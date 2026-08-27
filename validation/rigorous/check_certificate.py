#!/usr/bin/env python3
"""Check a staged rigorous certificate without upgrading an inconclusive run."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import jsonschema

from rigorous_common import (
    box_arguments,
    combine_verdicts,
    fraction,
    git_output,
    load_json,
    safe_repository_path,
    sha256_bytes,
    sha256_file,
    validate_exact_bridge,
    validate_exact_box,
    validate_local_graph_configuration,
)

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
P0_IDS = {
    "ENV.SOURCE_BINDING",
    "ENV.CAPD_BINDING",
    "ENV.ROUNDING",
    "BOX.FROZEN",
}
KERNEL_IDS = P0_IDS | {
    "V1.REVERSIBILITY",
    "V1.HAMILTONIAN",
    "V2.1.WEDGE",
    "V2.1.POSITIVITY",
    "V2.1.SADDLE_FOCUS",
}
LOCAL_GRAPH_P0_IDS = P0_IDS | {
    "BRIDGE.FROZEN",
    "P2.LOCAL_GRAPH_CONFIG_FROZEN",
}
LOCAL_GRAPH_IDS = LOCAL_GRAPH_P0_IDS | {
    "V2.WU.FRAME_BLOCK",
    "V2.WU.COARSE_GRAPH",
}
BASE_REQUIRED_BINDINGS = {
    "RESEARCH_CONTRACT.md",
    "theory/BASELINE.md",
    "van-der-pol/HAMILTONIAN_CHECK.md",
    "van-der-pol/MODEL_AND_CENTRAL_CHART.md",
    "van-der-pol/CENTRAL_CONTINUATION.md",
    "validation/rigorous/README.md",
    "validation/rigorous/certificate.schema.json",
    "validation/rigorous/parameter_box.schema.json",
    "validation/rigorous/config/vdp_box_v1.json",
    "validation/rigorous/dependency.lock.json",
    "validation/rigorous/flagship_import.lock.json",
    "validation/rigorous/obligations.json",
    "validation/rigorous/include/verdict.hpp",
    "validation/rigorous/include/interval_io.hpp",
    "validation/rigorous/include/rounding_self_test.hpp",
    "validation/rigorous/include/exact_polynomial.hpp",
    "validation/rigorous/src/rounding_self_test.cpp",
    "validation/rigorous/src/vdp_parameter_box_probe.cpp",
    "validation/rigorous/rigorous_common.py",
    "validation/rigorous/run_validation.py",
    "validation/rigorous/check_certificate.py",
}
LOCAL_GRAPH_REQUIRED_BINDINGS = BASE_REQUIRED_BINDINGS | {
    "validation/rigorous/P2_VALIDATION_CONTRACT.md",
    "validation/rigorous/continuation_bridge.schema.json",
    "validation/rigorous/p2_local_graph.schema.json",
    "validation/rigorous/config/vdp_bridge_v1.json",
    "validation/rigorous/config/vdp_p2_local_graph_v1.json",
    "validation/rigorous/src/vdp_local_graph_probe.cpp",
}
LOCAL_FRAME_ENCLOSURES = {
    "four_minus_c_squared",
    "two_plus_c",
    "two_minus_c",
    "alpha",
    "beta",
    "unstable_face_outward_margin",
    "stable_face_inward_margin",
    "difference_cone_margin",
}
LOCAL_GRAPH_ENCLOSURES = {
    "gamma0",
    "one_minus_first_quadratic_coefficient",
    "gamma1",
    "one_quarter_minus_refined_quadratic_coefficient",
    "gamma1_minus_two_thirds",
}
COMMON_NONCLAIMS = [
    "A local mathematical PASS is not an aggregate theorem certificate.",
    "Independent-machine replay is pending and this certificate is not claim-bearing.",
]
PHASE1_SCOPE_NONCLAIM = (
    "Phase 1 does not validate V2 continuation beyond item (1), V3--V6, "
    "temporal stability, Turing selection, or canard identification."
)
LOCAL_GRAPH_SCOPE_NONCLAIM = (
    "The local-graph kernel proves only its two P2a subobligations; "
    "V2.WU_GRAPH mixed jets, the homoclinic, exact charts, event atlas, "
    "V3--V6, temporal stability, Turing selection, and canard identification "
    "remain outside its scope."
)
ROUNDING_IDS = {
    "ROUND.IEEE754_BINARY64",
    "ROUND.NO_FAST_MATH",
    "ROUND.CAPD_MODES",
    "ROUND.CAPD_LEGACY_SELF_TEST",
    "ROUND.DIRECTED_ADDITION",
    "ROUND.RATIONAL_DIVISION",
    "ROUND.NEGATIVE_RATIONAL_DIVISION",
    "ROUND.SQRT",
    "ROUND.DEPENDENCY_SQUARE",
    "ROUND.POLYNOMIAL_CONTAINMENT",
    "ROUND.HEX_SERIALIZATION",
    "ROUND.SUBNORMAL_MODE",
    "ROUND.RESTORE_NEAREST",
}


def schema_errors(certificate: dict[str, Any]) -> list[str]:
    schema = load_json(HERE / "certificate.schema.json")
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker())
    return [
        f"schema {'.'.join(str(part) for part in error.absolute_path) or '<root>'}: "
        f"{error.message}"
        for error in sorted(
            validator.iter_errors(certificate),
            key=lambda item: tuple(str(part) for part in item.path))
    ]


def _check_hex_interval(name: str, value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict) or not {"lower_hex", "upper_hex"} <= set(value):
        errors.append(f"{name} is not a serialized interval")
        return
    try:
        lower = float.fromhex(value["lower_hex"])
        upper = float.fromhex(value["upper_hex"])
    except (TypeError, ValueError) as error:
        errors.append(f"{name} has an invalid hexadecimal endpoint: {error}")
        return
    if lower > upper:
        errors.append(f"{name} has reversed endpoints")


def _strict_positive_interval_verdict(value: Any) -> str | None:
    try:
        lower = float.fromhex(value["lower_hex"])
        upper = float.fromhex(value["upper_hex"])
    except (KeyError, TypeError, ValueError):
        return None
    if lower > upper:
        return None
    if lower > 0.0:
        return "PASS"
    if upper <= 0.0:
        return "FAIL"
    return "INCONCLUSIVE"


def _contains_exact_interval(value: Any, lower: Fraction,
                             upper: Fraction) -> bool:
    try:
        observed_lower = Fraction.from_float(float.fromhex(value["lower_hex"]))
        observed_upper = Fraction.from_float(float.fromhex(value["upper_hex"]))
    except (KeyError, TypeError, ValueError):
        return False
    return observed_lower <= lower <= upper <= observed_upper


def _recorded_blob(repository: Path, commit: str, relative: str) -> bytes:
    """Read a repository-relative blob from the certificate's frozen commit."""

    path = Path(relative)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"unsafe recorded source path: {relative}")
    return subprocess.run(
        ["git", "-C", str(repository), "cat-file", "blob", f"{commit}:{path.as_posix()}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def semantic_errors(certificate: dict[str, Any],
                    repository: Path = REPOSITORY) -> list[str]:
    errors: list[str] = []
    box_path = HERE / "config" / "vdp_box_v1.json"
    box = load_json(box_path)
    box_schema = load_json(HERE / "parameter_box.schema.json")
    try:
        jsonschema.validate(box, box_schema,
                            format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as error:
        errors.append(f"frozen box schema: {error.message}")
    errors.extend(validate_exact_box(box))

    parameter_box = certificate.get("parameter_box", {})
    if parameter_box.get("path") != "validation/rigorous/config/vdp_box_v1.json":
        errors.append("certificate does not bind the canonical phase-1 box path")
    if parameter_box.get("sha256") != sha256_file(box_path):
        errors.append("certificate parameter-box hash does not match the frozen box")
    if parameter_box.get("variables") != box.get("variables"):
        errors.append("certificate parameter endpoints differ from the frozen box")

    scope = certificate.get("scope")
    if scope == "V2_LOCAL_GRAPH_KERNEL":
        bridge_path = HERE / "config" / "vdp_bridge_v1.json"
        bridge = load_json(bridge_path)
        try:
            jsonschema.validate(
                bridge,
                load_json(HERE / "continuation_bridge.schema.json"),
                format_checker=jsonschema.FormatChecker(),
            )
        except jsonschema.ValidationError as error:
            errors.append(f"frozen continuation bridge schema: {error.message}")
        errors.extend(validate_exact_bridge(bridge))
        recorded_bridge = certificate.get("continuation_bridge", {})
        if recorded_bridge.get("path") != \
                "validation/rigorous/config/vdp_bridge_v1.json":
            errors.append("local-graph certificate does not bind the canonical bridge path")
        if recorded_bridge.get("sha256") != sha256_file(bridge_path):
            errors.append("certificate continuation-bridge hash mismatch")
        if recorded_bridge.get("variables") != bridge.get("variables"):
            errors.append("certificate bridge endpoints differ from the frozen bridge")

        configuration_path = HERE / "config" / "vdp_p2_local_graph_v1.json"
        configuration = load_json(configuration_path)
        try:
            jsonschema.validate(
                configuration,
                load_json(HERE / "p2_local_graph.schema.json"),
                format_checker=jsonschema.FormatChecker(),
            )
        except jsonschema.ValidationError as error:
            errors.append(f"local-graph configuration schema: {error.message}")
        errors.extend(validate_local_graph_configuration(configuration))
        recorded_configuration = certificate.get("validation_configuration", {})
        if recorded_configuration.get("path") != \
                "validation/rigorous/config/vdp_p2_local_graph_v1.json":
            errors.append("local-graph certificate does not bind the canonical configuration")
        if recorded_configuration.get("sha256") != sha256_file(configuration_path):
            errors.append("certificate local-graph configuration hash mismatch")
        selected_bridge = configuration.get("selection_basis", {}).get(
            "continuation_bridge", {})
        if selected_bridge.get("sha256") != sha256_file(bridge_path):
            errors.append("local-graph configuration does not bind the frozen bridge")
    elif "continuation_bridge" in certificate or \
            "validation_configuration" in certificate:
        errors.append("non-P2 certificate unexpectedly records P2 configuration data")

    source_revision = certificate.get("source_revision", {})
    try:
        git_output(
            repository, "cat-file", "-e",
            f"{source_revision.get('commit', '')}^{{commit}}")
    except (OSError, subprocess.SubprocessError) as error:
        errors.append(f"recorded source commit is unavailable: {error}")

    recorded_commit = str(source_revision.get("commit", ""))
    recorded_dirty = bool(source_revision.get("repository_dirty", True))
    allow_dirty = bool(source_revision.get("allow_dirty_development", False))
    if recorded_dirty and not allow_dirty:
        errors.append("a dirty source certificate must record allow_dirty_development=true")

    seen_paths: set[str] = set()
    for binding in certificate.get("source_bindings", []):
        relative = binding.get("path")
        if not isinstance(relative, str):
            continue
        if relative in seen_paths:
            errors.append(f"duplicate source-binding path: {relative}")
            continue
        seen_paths.add(relative)
        try:
            path = safe_repository_path(repository, relative)
        except ValueError as error:
            errors.append(str(error))
            continue
        if recorded_dirty:
            # A dirty development certificate cannot be reconstructed from its
            # base commit.  It remains non-claim-bearing and is checked against
            # the explicitly hash-bound working-tree inputs.
            if not path.is_file():
                errors.append(f"source-binding file is missing: {relative}")
            elif binding.get("sha256") != sha256_file(path):
                errors.append(f"dirty source-binding hash mismatch: {relative}")
        else:
            # A clean certificate is historical evidence.  Verify the exact
            # Git blobs at the recorded commit so later checker evolution does
            # not invalidate an otherwise immutable certificate.
            try:
                blob = _recorded_blob(repository, recorded_commit, relative)
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                errors.append(f"recorded source blob is unavailable ({relative}): {error}")
            else:
                if binding.get("sha256") != sha256_bytes(blob):
                    errors.append(f"recorded source-blob hash mismatch: {relative}")

    required_bindings = LOCAL_GRAPH_REQUIRED_BINDINGS \
        if scope == "V2_LOCAL_GRAPH_KERNEL" else BASE_REQUIRED_BINDINGS
    missing_bindings = required_bindings - seen_paths
    if missing_bindings:
        errors.append(f"required source bindings missing: {sorted(missing_bindings)}")

    obligations = certificate.get("obligations", [])
    by_id: dict[str, dict[str, Any]] = {}
    for obligation in obligations:
        identifier = obligation.get("id")
        if identifier in by_id:
            errors.append(f"duplicate obligation id: {identifier}")
        elif isinstance(identifier, str):
            by_id[identifier] = obligation
        for name, enclosure in obligation.get("enclosures", {}).items():
            _check_hex_interval(f"{identifier}.{name}", enclosure, errors)

    try:
        if recorded_dirty:
            obligation_manifest = load_json(HERE / "obligations.json")
        else:
            obligation_manifest = json.loads(_recorded_blob(
                repository, recorded_commit,
                "validation/rigorous/obligations.json"))
        manifest_predicates = {
            item["id"]: item["predicate"]
            for phase in obligation_manifest["phases"]
            for item in phase["obligations"]
        }
        for identifier, obligation in by_id.items():
            if identifier not in manifest_predicates:
                errors.append(f"obligation is absent from its bound manifest: {identifier}")
            elif obligation.get("predicate") != manifest_predicates[identifier]:
                errors.append(f"obligation predicate differs from its bound manifest: {identifier}")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError,
            OSError, subprocess.SubprocessError) as error:
        errors.append(f"cannot reconstruct bound obligation predicates: {error}")

    required_by_scope = {
        "PREFLIGHT": P0_IDS,
        "V1_V2_1_KERNEL": KERNEL_IDS,
        "V2_LOCAL_GRAPH_KERNEL": LOCAL_GRAPH_IDS,
    }
    required = required_by_scope.get(scope, set())
    missing = required - set(by_id)
    extra = set(by_id) - required
    if missing:
        errors.append(f"missing obligations: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected obligations for {scope}: {sorted(extra)}")

    expected_nonclaims = COMMON_NONCLAIMS + [
        LOCAL_GRAPH_SCOPE_NONCLAIM
        if scope == "V2_LOCAL_GRAPH_KERNEL" else PHASE1_SCOPE_NONCLAIM
    ]
    if certificate.get("nonclaims") != expected_nonclaims:
        errors.append("certificate nonclaims differ from the frozen scope boundary")

    integrity_ids = LOCAL_GRAPH_P0_IDS if scope == "V2_LOCAL_GRAPH_KERNEL" \
        else P0_IDS
    p0_status = combine_verdicts(
        by_id[item]["status"] for item in integrity_ids if item in by_id)
    if len(integrity_ids & set(by_id)) == len(integrity_ids) and \
            certificate.get("integrity_status") != p0_status:
        errors.append("integrity_status is not the aggregate P0 verdict")

    if scope == "PREFLIGHT":
        expected_math = "PASS"
    else:
        mathematical_ids = required - integrity_ids
        expected_math = combine_verdicts(
            by_id[item]["status"] for item in mathematical_ids if item in by_id)
    if required <= set(by_id) and certificate.get("mathematical_status") != expected_math:
        errors.append("mathematical_status is not the mathematical-obligation aggregate")

    raw_probe = certificate.get("raw_probe", {})
    if scope != "PREFLIGHT":
        raw_obligations = raw_probe.get("obligations", [])
        raw_by_id: dict[str, dict[str, Any]] = {}
        if not isinstance(raw_obligations, list):
            errors.append("raw_probe.obligations is not a list")
            raw_obligations = []
        for item in raw_obligations:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                errors.append("raw probe has an invalid obligation record")
                continue
            identifier = item["id"]
            if identifier in raw_by_id:
                errors.append(f"duplicate raw-probe obligation id: {identifier}")
            raw_by_id[identifier] = item
        expected_raw_ids = required - integrity_ids
        if set(raw_by_id) != expected_raw_ids:
            errors.append(
                "raw-probe mathematical obligations differ from the scoped set: "
                f"observed={sorted(raw_by_id)}, expected={sorted(expected_raw_ids)}")
        for identifier in expected_raw_ids & set(raw_by_id) & set(by_id):
            if raw_by_id[identifier].get("status") != by_id[identifier].get("status"):
                errors.append(f"raw/top-level status mismatch: {identifier}")
            if raw_by_id[identifier].get("enclosures", {}) != \
                    by_id[identifier].get("enclosures", {}):
                errors.append(f"raw/top-level enclosure mismatch: {identifier}")
        if raw_probe.get("mathematical_status") != expected_math:
            errors.append("raw-probe mathematical_status differs from its obligations")

    if scope == "V1_V2_1_KERNEL":
        if raw_probe.get("exact_characteristic_polynomial") is not True:
            errors.append("kernel does not record the exact characteristic-polynomial identity")
    if scope == "V2_LOCAL_GRAPH_KERNEL":
        if raw_probe.get("exact_frame_derivation") is not True:
            errors.append("local-graph kernel does not bind the exact frame derivation")
        expected_enclosures = {
            "V2.WU.FRAME_BLOCK": LOCAL_FRAME_ENCLOSURES,
            "V2.WU.COARSE_GRAPH": LOCAL_GRAPH_ENCLOSURES,
        }
        for identifier, expected_names in expected_enclosures.items():
            observed = by_id.get(identifier, {}).get("enclosures", {})
            if set(observed) != expected_names:
                errors.append(
                    f"{identifier} enclosure set changed: "
                    f"observed={sorted(observed)}, expected={sorted(expected_names)}")
            margin_verdicts: list[str] = []
            for name, enclosure in observed.items():
                verdict = _strict_positive_interval_verdict(enclosure)
                if verdict is None:
                    errors.append(
                        f"{identifier}.{name} cannot be reduced to a margin verdict")
                else:
                    margin_verdicts.append(verdict)
            if len(margin_verdicts) == len(expected_names):
                recomputed = combine_verdicts(margin_verdicts)
                if by_id.get(identifier, {}).get("status") != recomputed:
                    errors.append(
                        f"{identifier} status is not its strict-margin aggregate")

        raw_parameters = raw_probe.get("parameter_enclosures", {})
        bridge_variables = bridge.get("variables", {})
        for name in ("r", "a2", "epsilon"):
            try:
                exact_lower = fraction(bridge_variables[name]["lower"])
                exact_upper = fraction(bridge_variables[name]["upper"])
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                continue
            if not _contains_exact_interval(
                    raw_parameters.get(name), exact_lower, exact_upper):
                errors.append(
                    f"raw local-graph parameter enclosure does not contain "
                    f"the exact bridge interval: {name}")
        exact_radius = Fraction(1, 100)
        if not _contains_exact_interval(
                raw_parameters.get("radius"), exact_radius, exact_radius):
            errors.append("raw local-graph radius does not contain the frozen 1/100")

    rounding = certificate.get("rounding_self_test", {})
    rounding_tests = {item.get("id"): item for item in rounding.get("tests", [])}
    if not ROUNDING_IDS <= set(rounding_tests):
        errors.append(f"rounding tests missing: {sorted(ROUNDING_IDS - set(rounding_tests))}")
    expected_rounding = combine_verdicts(
        item.get("status", "INCONCLUSIVE") for item in rounding.get("tests", []))
    if rounding.get("status") != expected_rounding:
        errors.append("rounding_self_test.status is not its test aggregate")
    if raw_probe.get("rounding_self_test") != rounding:
        errors.append("raw-probe rounding report differs from the certificate report")
    if scope != "PREFLIGHT":
        expected_raw_status = combine_verdicts(
            [expected_rounding,
             raw_probe.get("mathematical_status", "INCONCLUSIVE")])
        if raw_probe.get("status") != expected_raw_status:
            errors.append("raw-probe status is not its rounding/mathematical aggregate")
    if "ENV.ROUNDING" in by_id and by_id["ENV.ROUNDING"].get("status") != rounding.get("status"):
        errors.append("ENV.ROUNDING differs from rounding_self_test.status")

    toolchain = certificate.get("toolchain", {})
    bound_hashes = {
        item.get("path"): item.get("sha256")
        for item in certificate.get("source_bindings", [])
        if isinstance(item, dict)
    }
    if toolchain.get("dependency_lock_sha256") != bound_hashes.get(
            "validation/rigorous/dependency.lock.json"):
        errors.append("toolchain dependency-lock hash does not match its source binding")
    probe_source_by_scope = {
        "PREFLIGHT": "validation/rigorous/src/rounding_self_test.cpp",
        "V1_V2_1_KERNEL": "validation/rigorous/src/vdp_parameter_box_probe.cpp",
        "V2_LOCAL_GRAPH_KERNEL": "validation/rigorous/src/vdp_local_graph_probe.cpp",
    }
    probe_source = probe_source_by_scope.get(scope)
    probe_build = toolchain.get("probe_build", {})
    if probe_source is not None and probe_build.get("source_sha256") != \
            bound_hashes.get(probe_source):
        errors.append("compiled probe source hash differs from its source binding")
    expected_probe_arguments: list[str] = []
    if scope == "V1_V2_1_KERNEL":
        expected_probe_arguments = box_arguments(box)
    elif scope == "V2_LOCAL_GRAPH_KERNEL":
        expected_probe_arguments = box_arguments(bridge)
        radius = configuration.get("coordinate_block", {}).get(
            "unstable_radius", {})
        try:
            expected_probe_arguments.extend(
                [radius["numerator"], radius["denominator"]])
        except KeyError:
            pass
    recorded_probe_argv = probe_build.get("probe_argv")
    if not isinstance(recorded_probe_argv, list) or not recorded_probe_argv:
        errors.append("probe argv is missing")
    elif recorded_probe_argv[1:] != expected_probe_arguments:
        errors.append("probe argv does not match the frozen scope inputs")
    raw_status_for_exit = rounding.get("status") if scope == "PREFLIGHT" \
        else raw_probe.get("status")
    expected_probe_exit = {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 2}.get(
        raw_status_for_exit)
    if expected_probe_exit is not None and \
            probe_build.get("probe_exit_code") != expected_probe_exit:
        errors.append("probe exit code differs from the raw probe verdict")
    if "ENV.CAPD_BINDING" in by_id and \
            by_id["ENV.CAPD_BINDING"].get("status") != toolchain.get("status"):
        errors.append("ENV.CAPD_BINDING differs from toolchain.status")
    if toolchain.get("status") == "PASS":
        if toolchain.get("strict_library_build_status") != "PASS":
            errors.append("a PASS toolchain must record a strict CAPD/FILIB build PASS")
        scan = toolchain.get("capd", {}).get("compile_commands_scan", {})
        if scan.get("entry_count", 0) <= 0 or \
                scan.get("entries_with_all_strict_flags") != scan.get("entry_count"):
            errors.append("PASS toolchain does not bind an all-entry strict compile scan")
        if not toolchain.get("capd", {}).get("compile_commands_sha256"):
            errors.append("PASS toolchain does not hash compile_commands.json")

    replay = certificate.get("independent_replay", {})
    if replay.get("status") != "PENDING_REQUIRED":
        errors.append(
            "the local checker accepts only PENDING_REQUIRED; independent replay "
            "must be aggregated by a future evidence-bearing schema")
    if replay.get("required_distinct_machines") != 2:
        errors.append("rigorous replay policy requires exactly two distinct machines")
    if replay.get("observed_distinct_machines") != 1:
        errors.append("a local certificate must record exactly one observed machine")
    integrity = certificate.get("integrity_status")
    mathematical = certificate.get("mathematical_status")
    if integrity == "FAIL" or mathematical == "FAIL" or replay.get("status") == "FAIL":
        expected_final = "FAIL"
    elif replay.get("status") != "PASS":
        expected_final = "INCONCLUSIVE"
    elif integrity == mathematical == "PASS":
        expected_final = "PASS"
    else:
        expected_final = "INCONCLUSIVE"
    if certificate.get("final_status") != expected_final:
        errors.append(f"final_status must be {expected_final} under the recorded verdicts")

    enough_machines = replay.get("observed_distinct_machines", 0) >= \
        replay.get("required_distinct_machines", 2)
    clean_release = not recorded_dirty and not allow_dirty
    strict_build = toolchain.get("strict_library_build_status") == "PASS"
    eligible = expected_final == "PASS" and enough_machines and clean_release and strict_build
    if certificate.get("claim_bearing") != eligible:
        errors.append("claim_bearing is inconsistent with replay/clean/strict requirements")
    if certificate.get("release_eligible") != eligible:
        errors.append("release_eligible is inconsistent with replay/clean/strict requirements")
    if replay.get("status") == "PENDING_REQUIRED" and (
            certificate.get("claim_bearing") or certificate.get("release_eligible")):
        errors.append("pending independent replay cannot be claim-bearing")
    return errors


def check_certificate(path: Path, repository: Path = REPOSITORY) -> list[str]:
    certificate = load_json(path)
    return schema_errors(certificate) + semantic_errors(certificate, repository)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--repository", type=Path, default=REPOSITORY)
    arguments = parser.parse_args()
    try:
        certificate = load_json(arguments.certificate)
        errors = schema_errors(certificate) + semantic_errors(
            certificate, arguments.repository.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(
        "VALID: certificate is internally consistent; "
        f"final_status={certificate['final_status']}; "
        f"claim_bearing={str(certificate['claim_bearing']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
