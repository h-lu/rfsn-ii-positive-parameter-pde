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
    validate_h10_c01_configuration,
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
H10_C01_P0_IDS = LOCAL_GRAPH_P0_IDS | {
    "P2.P2A_PREREQUISITE",
    "P2.H10_C01_CONFIG_FROZEN",
    "P2.H10_CENTER_EXACT",
}
H10_C01_IDS = H10_C01_P0_IDS | {
    "V2.WU.H10_C0_TUBE",
    "V2.WU.H10_C1_TUBE",
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
H10_C01_REQUIRED_BINDINGS = LOCAL_GRAPH_REQUIRED_BINDINGS | {
    "validation/rigorous/p2_h10_c01.schema.json",
    "validation/rigorous/config/vdp_p2_h10_c01_v1.json",
    "validation/rigorous/audit_h10_center.py",
    "validation/rigorous/src/vdp_h10_c01_probe.cpp",
    "validation/rigorous/results/vdp_bridge_v1_p2a_local_graph.json",
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
H10_C0_ENCLOSURES = {
    "h10_euclidean_reference_margin",
    "dh10_frobenius_reference_margin",
    "core_defect_euclidean_reference_margin",
    "absolute_a_minus_one_parameter_margin",
    "b_parameter_margin",
    "absolute_c_parameter_margin",
    "alpha_parameter_margin",
    "q_norm_parameter_margin",
    "delta_block_operator_parameter_margin",
    "delta_q_norm_parameter_margin",
    "center_residual_euclidean_margin",
    "weighted_nonlinear_lipschitz_margin",
    "normal_contraction_margin",
    "c0_inward_margin_margin",
}
H10_C1_ENCLOSURES = {
    "d2h10_frobenius_reference_margin",
    "core_defect_derivative_frobenius_reference_margin",
    "center_residual_derivative_frobenius_margin",
    "weighted_nonlinear_second_margin",
    "c1_cone_margin_margin",
}
H10_PARAMETER_ENCLOSURES = {
    "r",
    "a2",
    "epsilon",
    "radius",
    "rho",
    "eta",
    "a",
    "b",
    "c",
    "alpha",
    "beta",
    "q_norm",
    "absolute_a_minus_one",
    "absolute_c",
    "delta_block_operator",
    "delta_q_norm",
}
H10_CENTER_ENCLOSURES = {
    "h10_component_1_abs",
    "h10_component_2_abs",
    "h10_euclidean",
    "dh10_frobenius",
    "d2h10_frobenius",
    "core_defect_euclidean",
    "core_defect_derivative_frobenius",
    "X0",
    "X",
    "Cq",
    "delta_G",
    "delta_G_prime",
    "E0",
    "E1",
    "ell",
    "m",
    "kappa",
    "Gu",
    "c0_inward_margin",
    "c1_cone_margin",
}
H10_REFERENCE_MARGINS = {
    "h10_euclidean_reference_margin",
    "dh10_frobenius_reference_margin",
    "d2h10_frobenius_reference_margin",
    "core_defect_euclidean_reference_margin",
    "core_defect_derivative_frobenius_reference_margin",
}
H10_PARAMETER_MARGINS = {
    "absolute_a_minus_one_parameter_margin",
    "b_parameter_margin",
    "absolute_c_parameter_margin",
    "alpha_parameter_margin",
    "q_norm_parameter_margin",
    "delta_block_operator_parameter_margin",
    "delta_q_norm_parameter_margin",
}
H10_ACCEPTANCE_MARGINS = {
    "center_residual_euclidean_margin",
    "center_residual_derivative_frobenius_margin",
    "weighted_nonlinear_lipschitz_margin",
    "weighted_nonlinear_second_margin",
    "normal_contraction_margin",
    "c0_inward_margin_margin",
    "c1_cone_margin_margin",
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
H10_C01_SCOPE_NONCLAIM = (
    "The H10 C0/C1 kernel proves only its two P2b0 tube subobligations; "
    "V2.WU.JETS and V2.WU_GRAPH mixed jets and weighted tails, the "
    "homoclinic, exact charts, event atlas, V3--V6, temporal stability, "
    "Turing selection, and canard identification remain outside its scope."
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


def _sufficient_positive_interval_verdict(value: Any) -> str | None:
    """Reduce a sufficient-condition margin without inventing a counterexample."""

    try:
        lower = float.fromhex(value["lower_hex"])
        upper = float.fromhex(value["upper_hex"])
    except (KeyError, TypeError, ValueError):
        return None
    if lower > upper:
        return None
    return "PASS" if lower > 0.0 else "INCONCLUSIVE"


def _contains_exact_interval(value: Any, lower: Fraction,
                             upper: Fraction) -> bool:
    try:
        observed_lower = Fraction.from_float(float.fromhex(value["lower_hex"]))
        observed_upper = Fraction.from_float(float.fromhex(value["upper_hex"]))
    except (KeyError, TypeError, ValueError):
        return False
    return observed_lower <= lower <= upper <= observed_upper


def _check_interval_mapping(name: str, value: Any, expected: set[str],
                            errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{name} is not an interval mapping")
        return {}
    if set(value) != expected:
        errors.append(
            f"{name} field set changed: observed={sorted(value)}, "
            f"expected={sorted(expected)}")
    for field, enclosure in value.items():
        _check_hex_interval(f"{name}.{field}", enclosure, errors)
    return value


def _h10_audit_status(audit: Any, configuration: dict[str, Any],
                      flagship_repository: Any,
                      errors: list[str]) -> str:
    """Recompute the exact-center audit verdict from its bound evidence."""

    if not isinstance(audit, dict):
        errors.append("H10 exact-center audit is not an object")
        return "INCONCLUSIVE"
    center = configuration.get("imported_core_center", {})
    protocol = configuration.get("exact_center_audit", {})
    if audit.get("schema_version") != "rfsn-vdp-h10-center-audit/1":
        errors.append("H10 exact-center audit schema version changed")
    if audit.get("commit") != center.get("commit"):
        errors.append("H10 exact-center audit commit differs from the frozen center")
    if audit.get("flagship_repository") != flagship_repository:
        errors.append(
            "H10 exact-center audit repository differs from the bound flagship")

    failures = audit.get("failures")
    reasons = audit.get("inconclusive_reasons")
    if not isinstance(failures, list) or not all(
            isinstance(item, str) for item in failures):
        errors.append("H10 exact-center audit failures are malformed")
        failures = []
    if not isinstance(reasons, list) or not all(
            isinstance(item, str) for item in reasons):
        errors.append("H10 exact-center audit inconclusive reasons are malformed")
        reasons = []

    exact_failure = False
    execution_inconclusive = False
    frozen_objects = audit.get("frozen_objects")
    if not isinstance(frozen_objects, dict):
        errors.append("H10 exact-center audit frozen_objects is malformed")
        frozen_objects = {}
        execution_inconclusive = True
    for name in ("generator", "term_table"):
        expected = center.get(name, {})
        record = frozen_objects.get(name, {})
        if not isinstance(record, dict):
            errors.append(f"H10 exact-center {name} record is malformed")
            execution_inconclusive = True
            continue
        if record.get("path") != expected.get("path") or \
                record.get("expected_sha256") != expected.get("sha256"):
            errors.append(f"H10 exact-center {name} binding changed")
        git_show = record.get("git_show", {})
        if not isinstance(git_show, dict):
            errors.append(f"H10 exact-center {name} git-show record is malformed")
            execution_inconclusive = True
        elif git_show.get("exit_code") != 0:
            execution_inconclusive = True
        else:
            argv = git_show.get("argv")
            expected_spec = f"{center.get('commit')}:{expected.get('path')}"
            expected_argv = [
                "git", "-C", flagship_repository, "show", expected_spec]
            if argv != expected_argv:
                errors.append(f"H10 exact-center {name} git-show argv changed")
            if git_show.get("stdout_sha256") != record.get("observed_sha256"):
                errors.append(
                    f"H10 exact-center {name} stdout hash is internally inconsistent")
            if git_show.get("stderr_sha256") != sha256_bytes(b""):
                errors.append(
                    f"H10 exact-center {name} git-show stderr is not empty")
        observed = record.get("observed_sha256")
        if isinstance(observed, str):
            matches = observed == expected.get("sha256")
            if record.get("hash_matches") is not matches:
                errors.append(f"H10 exact-center {name} hash_matches is inconsistent")
            exact_failure = exact_failure or not matches
        elif not execution_inconclusive:
            errors.append(f"H10 exact-center {name} observed hash is missing")
            execution_inconclusive = True

    regeneration = audit.get("regeneration")
    if not isinstance(regeneration, dict):
        errors.append("H10 exact-center regeneration record is malformed")
        regeneration = {}
        execution_inconclusive = True
    regeneration_exit = regeneration.get("exit_code")
    if regeneration_exit != 0:
        execution_inconclusive = True
    elif regeneration.get("output_exists") is not True:
        execution_inconclusive = True
    else:
        expected_header_hash = center.get("term_table", {}).get("sha256")
        if regeneration.get("frozen_sha256") != expected_header_hash:
            errors.append("H10 exact-center regeneration frozen hash changed")
        regenerated_hash = regeneration.get("regenerated_sha256")
        byte_identical = regeneration.get("byte_identical")
        if byte_identical is not (regenerated_hash == expected_header_hash):
            errors.append("H10 exact-center byte-identical flag is inconsistent")
        exact_failure = exact_failure or byte_identical is not True
        regeneration_argv = regeneration.get("argv")
        if not isinstance(regeneration_argv, list) or \
                len(regeneration_argv) != 5 or \
                regeneration_argv[1] != "-B" or \
                Path(regeneration_argv[2]).name != \
                Path(center.get("generator", {}).get("path", "")).name or \
                regeneration_argv[3] != "--output" or \
                Path(regeneration_argv[4]).name != "unstable_graph_terms.hpp":
            errors.append("H10 exact-center regeneration argv is malformed")
        if regeneration.get("stdout_sha256") != sha256_bytes(b"") or \
                regeneration.get("stderr_sha256") != sha256_bytes(b""):
            errors.append("H10 exact-center regeneration emitted unexpected output")

    table_audit = audit.get("term_table_audit")
    if not isinstance(table_audit, dict):
        errors.append("H10 exact-center term-table audit is malformed")
        table_audit = {}
        execution_inconclusive = True
    expected_names = {
        "kH1Terms", "kH2Terms", "kDefect1Terms", "kDefect2Terms"}
    if table_audit:
        if set(table_audit.get("expected_array_names", [])) != expected_names:
            errors.append("H10 exact-center expected array names changed")
        observed_names = table_audit.get("observed_array_names", [])
        if not isinstance(observed_names, list):
            errors.append("H10 exact-center observed array names are malformed")
            exact_failure = True
        else:
            exact_failure = exact_failure or \
                len(observed_names) != len(set(observed_names)) or \
                set(observed_names) != expected_names
        arrays = table_audit.get("arrays", {})
        if not isinstance(arrays, dict):
            errors.append("H10 exact-center array audit records are malformed")
            arrays = {}
            exact_failure = True
        specifications = {
            "kH1Terms": (
                protocol.get("h1_term_count"),
                protocol.get("center_minimum_total_degree"),
                protocol.get("center_maximum_total_degree"), False),
            "kH2Terms": (
                protocol.get("h2_term_count"),
                protocol.get("center_minimum_total_degree"),
                protocol.get("center_maximum_total_degree"), False),
            "kDefect1Terms": (
                protocol.get("defect1_term_count"),
                protocol.get("defect_minimum_total_degree"),
                protocol.get("defect_maximum_total_degree"), True),
            "kDefect2Terms": (
                protocol.get("defect2_term_count"),
                protocol.get("defect_minimum_total_degree"),
                protocol.get("defect_maximum_total_degree"), True),
        }
        for name, (count, minimum, maximum, sqrt_flag) in specifications.items():
            record = arrays.get(name, {})
            if not isinstance(record, dict):
                exact_failure = True
                continue
            expected_degrees = list(range(minimum, maximum + 1)) \
                if isinstance(minimum, int) and isinstance(maximum, int) else []
            fixed_fields = {
                "expected_term_count": count,
                "expected_total_degree_range": [minimum, maximum],
                "expected_times_sqrt_two": sqrt_flag,
            }
            for field, expected_value in fixed_fields.items():
                if record.get(field) != expected_value:
                    errors.append(
                        f"H10 exact-center {name}.{field} changed")
            exact_failure = exact_failure or any((
                record.get("observed_term_count") != count,
                record.get("observed_total_degrees") != expected_degrees,
                bool(record.get("duplicate_monomials")),
                bool(record.get("nonpositive_denominator_monomials")),
                bool(record.get("incorrect_sqrt_flag_monomials")),
            ))
    elif not execution_inconclusive:
        execution_inconclusive = True

    if failures or exact_failure:
        expected_status = "FAIL"
    elif reasons or execution_inconclusive:
        expected_status = "INCONCLUSIVE"
    else:
        expected_status = "PASS"
    if audit.get("status") != expected_status:
        errors.append(
            "H10 exact-center audit status is not its evidence aggregate")
    return expected_status


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
    bridge: dict[str, Any] = {}
    configuration: dict[str, Any] = {}
    h10_configuration: dict[str, Any] = {}
    expected_h10_audit_status: str | None = None
    bridge_scopes = {"V2_LOCAL_GRAPH_KERNEL", "V2_H10_C01_KERNEL"}
    if scope in bridge_scopes:
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

        if scope == "V2_H10_C01_KERNEL":
            h10_path = HERE / "config" / "vdp_p2_h10_c01_v1.json"
            h10_configuration = load_json(h10_path)
            try:
                jsonschema.validate(
                    h10_configuration,
                    load_json(HERE / "p2_h10_c01.schema.json"),
                    format_checker=jsonschema.FormatChecker(),
                )
            except jsonschema.ValidationError as error:
                errors.append(f"H10 C0/C1 configuration schema: {error.message}")
            errors.extend(validate_h10_c01_configuration(h10_configuration))
            recorded_h10 = certificate.get("h10_c01_configuration", {})
            if recorded_h10.get("path") != \
                    "validation/rigorous/config/vdp_p2_h10_c01_v1.json":
                errors.append(
                    "H10 C0/C1 certificate does not bind the canonical configuration")
            if recorded_h10.get("sha256") != sha256_file(h10_path):
                errors.append("certificate H10 C0/C1 configuration hash mismatch")
            if recorded_h10.get("configuration_id") != \
                    h10_configuration.get("configuration_id"):
                errors.append("certificate H10 C0/C1 configuration id mismatch")

            basis = h10_configuration.get("selection_basis", {})
            selected_files = {
                "continuation_bridge": bridge_path,
                "p2a_configuration":
                    HERE / "config" / "vdp_p2_local_graph_v1.json",
                "p2a_certificate":
                    HERE / "results" / "vdp_bridge_v1_p2a_local_graph.json",
            }
            for name, path in selected_files.items():
                selected = basis.get(name, {})
                expected_relative = str(path.relative_to(REPOSITORY))
                if selected.get("path") != expected_relative or \
                        selected.get("sha256") != sha256_file(path):
                    errors.append(f"H10 C0/C1 selection {name} binding mismatch")
            try:
                selected_commit = git_output(
                    repository, "rev-parse",
                    f"{basis.get('repository_tag', '')}^{{commit}}")
                if selected_commit != basis.get("repository_commit"):
                    errors.append(
                        "H10 C0/C1 selection tag does not resolve to its commit")
            except (OSError, subprocess.SubprocessError) as error:
                errors.append(f"cannot resolve H10 C0/C1 selection tag: {error}")

            flagship_lock = load_json(HERE / "flagship_import.lock.json")
            center = h10_configuration.get("imported_core_center", {})
            if center.get("commit") != flagship_lock.get("commit"):
                errors.append("H10 center commit differs from the flagship lock")
            for name in ("generator", "term_table", "reference_probe",
                         "reference_readme", "source_certificate"):
                item = center.get(name, {})
                if flagship_lock.get("files", {}).get(item.get("path")) != \
                        item.get("sha256"):
                    errors.append(f"H10 center {name} differs from the flagship lock")

            p2a_path = HERE / "results" / "vdp_bridge_v1_p2a_local_graph.json"
            p2a_certificate = load_json(p2a_path)
            nested_p2a_errors = schema_errors(p2a_certificate) + \
                semantic_errors(p2a_certificate, repository)
            if nested_p2a_errors:
                errors.append(
                    "bound P2a prerequisite certificate is invalid: " +
                    "; ".join(nested_p2a_errors))
            prerequisite = certificate.get("p2a_prerequisite", {})
            expected_prerequisite = {
                "configuration_path":
                    "validation/rigorous/config/vdp_p2_local_graph_v1.json",
                "configuration_sha256": sha256_file(
                    HERE / "config" / "vdp_p2_local_graph_v1.json"),
                "certificate_path":
                    "validation/rigorous/results/vdp_bridge_v1_p2a_local_graph.json",
                "certificate_sha256": sha256_file(p2a_path),
                "certificate_scope": p2a_certificate.get("scope"),
                "source_commit": p2a_certificate.get(
                    "source_revision", {}).get("commit"),
                "integrity_status": p2a_certificate.get("integrity_status"),
                "mathematical_status": p2a_certificate.get("mathematical_status"),
                "final_status": p2a_certificate.get("final_status"),
                "claim_bearing": p2a_certificate.get("claim_bearing"),
            }
            if prerequisite != expected_prerequisite:
                errors.append("certificate P2a prerequisite record changed")
            p2a_by_id = {
                item.get("id"): item.get("status")
                for item in p2a_certificate.get("obligations", [])
                if isinstance(item, dict)
            }
            if not (
                p2a_certificate.get("scope") == "V2_LOCAL_GRAPH_KERNEL" and
                p2a_certificate.get("integrity_status") == "PASS" and
                p2a_certificate.get("mathematical_status") == "PASS" and
                p2a_certificate.get("final_status") == "INCONCLUSIVE" and
                p2a_certificate.get("claim_bearing") is False and
                p2a_by_id.get("V2.WU.FRAME_BLOCK") == "PASS" and
                p2a_by_id.get("V2.WU.COARSE_GRAPH") == "PASS"
            ):
                errors.append("bound P2a prerequisite does not establish P2a PASS")

            expected_h10_audit_status = _h10_audit_status(
                certificate.get("h10_exact_center_audit"),
                h10_configuration,
                certificate.get("toolchain", {}).get(
                    "flagship_import", {}).get("repository_path"),
                errors)
    elif "continuation_bridge" in certificate or \
            "validation_configuration" in certificate:
        errors.append("non-P2 certificate unexpectedly records P2 configuration data")
    if scope != "V2_H10_C01_KERNEL" and any(
            name in certificate for name in (
                "h10_c01_configuration", "p2a_prerequisite",
                "h10_exact_center_audit")):
        errors.append("non-H10 certificate unexpectedly records H10 configuration data")

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

    required_bindings_by_scope = {
        "V2_LOCAL_GRAPH_KERNEL": LOCAL_GRAPH_REQUIRED_BINDINGS,
        "V2_H10_C01_KERNEL": H10_C01_REQUIRED_BINDINGS,
    }
    required_bindings = required_bindings_by_scope.get(
        scope, BASE_REQUIRED_BINDINGS)
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
        "V2_H10_C01_KERNEL": H10_C01_IDS,
    }
    required = required_by_scope.get(scope, set())
    missing = required - set(by_id)
    extra = set(by_id) - required
    if missing:
        errors.append(f"missing obligations: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected obligations for {scope}: {sorted(extra)}")

    scope_nonclaims = {
        "V2_LOCAL_GRAPH_KERNEL": LOCAL_GRAPH_SCOPE_NONCLAIM,
        "V2_H10_C01_KERNEL": H10_C01_SCOPE_NONCLAIM,
    }
    expected_nonclaims = COMMON_NONCLAIMS + [
        scope_nonclaims.get(scope, PHASE1_SCOPE_NONCLAIM)]
    if certificate.get("nonclaims") != expected_nonclaims:
        errors.append("certificate nonclaims differ from the frozen scope boundary")

    if scope == "V2_H10_C01_KERNEL":
        if by_id.get("P2.P2A_PREREQUISITE", {}).get("status") != "PASS":
            errors.append("P2.P2A_PREREQUISITE must bind the verified P2a PASS")
        if by_id.get("P2.H10_C01_CONFIG_FROZEN", {}).get("status") != "PASS":
            errors.append("P2.H10_C01_CONFIG_FROZEN must bind the frozen configuration")
        if expected_h10_audit_status is not None and \
                by_id.get("P2.H10_CENTER_EXACT", {}).get("status") != \
                expected_h10_audit_status:
            errors.append(
                "P2.H10_CENTER_EXACT differs from the recomputed audit verdict")

    integrity_ids = {
        "V2_LOCAL_GRAPH_KERNEL": LOCAL_GRAPH_P0_IDS,
        "V2_H10_C01_KERNEL": H10_C01_P0_IDS,
    }.get(scope, P0_IDS)
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

    if scope == "V2_H10_C01_KERNEL":
        if raw_probe.get("materialized_center_structure") not in (True, False):
            errors.append("H10 probe materialized_center_structure is not boolean")
        raw_parameters = _check_interval_mapping(
            "raw_probe.parameter_enclosures",
            raw_probe.get("parameter_enclosures"),
            H10_PARAMETER_ENCLOSURES, errors)
        _check_interval_mapping(
            "raw_probe.center_enclosures",
            raw_probe.get("center_enclosures"),
            H10_CENTER_ENCLOSURES, errors)
        reference_margins = _check_interval_mapping(
            "raw_probe.reference_gate_margins",
            raw_probe.get("reference_gate_margins"),
            H10_REFERENCE_MARGINS, errors)
        parameter_margins = _check_interval_mapping(
            "raw_probe.parameter_gate_margins",
            raw_probe.get("parameter_gate_margins"),
            H10_PARAMETER_MARGINS, errors)
        acceptance_margins = _check_interval_mapping(
            "raw_probe.acceptance_gate_margins",
            raw_probe.get("acceptance_gate_margins"),
            H10_ACCEPTANCE_MARGINS, errors)

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
                    f"raw H10 parameter enclosure does not contain the exact "
                    f"bridge interval: {name}")
        frozen_scalar_inputs = {
            "radius": h10_configuration.get(
                "coordinate_domain", {}).get("unstable_radius"),
            "rho": h10_configuration.get(
                "tube_radii", {}).get("value_euclidean"),
            "eta": h10_configuration.get(
                "tube_radii", {}).get("first_derivative_frobenius"),
        }
        for name, rational in frozen_scalar_inputs.items():
            try:
                exact = fraction(rational)
            except (TypeError, ValueError, ZeroDivisionError):
                continue
            if not _contains_exact_interval(
                    raw_parameters.get(name), exact, exact):
                errors.append(
                    f"raw H10 {name} does not contain its frozen rational value")

        expected_enclosures = {
            "V2.WU.H10_C0_TUBE": H10_C0_ENCLOSURES,
            "V2.WU.H10_C1_TUBE": H10_C1_ENCLOSURES,
        }
        all_margin_maps = {
            **reference_margins,
            **parameter_margins,
            **acceptance_margins,
        }
        observed_by_id: dict[str, dict[str, Any]] = {}
        for identifier, expected_names in expected_enclosures.items():
            observed = by_id.get(identifier, {}).get("enclosures", {})
            if not isinstance(observed, dict):
                observed = {}
            observed_by_id[identifier] = observed
            if set(observed) != expected_names:
                errors.append(
                    f"{identifier} enclosure set changed: "
                    f"observed={sorted(observed)}, "
                    f"expected={sorted(expected_names)}")
            for name in expected_names & set(observed):
                if observed[name] != all_margin_maps.get(name):
                    errors.append(
                        f"{identifier}.{name} differs from its raw gate margin")

        c0_margin_verdicts: list[str] = []
        c0_observed = observed_by_id.get("V2.WU.H10_C0_TUBE", {})
        for name in H10_C0_ENCLOSURES & set(c0_observed):
            verdict = _sufficient_positive_interval_verdict(c0_observed[name])
            if verdict is None:
                errors.append(
                    f"V2.WU.H10_C0_TUBE.{name} cannot be reduced to a "
                    "sufficient-margin verdict")
            else:
                c0_margin_verdicts.append(verdict)
        c0_status: str | None = None
        if len(c0_margin_verdicts) == len(H10_C0_ENCLOSURES):
            if raw_probe.get("materialized_center_structure") is False:
                c0_status = "FAIL"
            elif raw_probe.get("materialized_center_structure") is True:
                c0_status = combine_verdicts(c0_margin_verdicts)
            if c0_status is not None and \
                    by_id.get("V2.WU.H10_C0_TUBE", {}).get("status") != c0_status:
                errors.append(
                    "V2.WU.H10_C0_TUBE status is not its sufficient-margin "
                    "and structure aggregate")

        c1_margin_verdicts: list[str] = []
        c1_observed = observed_by_id.get("V2.WU.H10_C1_TUBE", {})
        for name in H10_C1_ENCLOSURES & set(c1_observed):
            verdict = _sufficient_positive_interval_verdict(c1_observed[name])
            if verdict is None:
                errors.append(
                    f"V2.WU.H10_C1_TUBE.{name} cannot be reduced to a "
                    "sufficient-margin verdict")
            else:
                c1_margin_verdicts.append(verdict)
        if c0_status is not None and \
                len(c1_margin_verdicts) == len(H10_C1_ENCLOSURES):
            c1_status = combine_verdicts(
                [c0_status, *c1_margin_verdicts])
            if by_id.get("V2.WU.H10_C1_TUBE", {}).get("status") != c1_status:
                errors.append(
                    "V2.WU.H10_C1_TUBE status is not the C0 prerequisite/C1 "
                    "sufficient-margin aggregate")

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
    flagship_import = toolchain.get("flagship_import", {})
    flagship_lock = load_json(HERE / "flagship_import.lock.json")
    expected_flagship_fields = {
        "lock_sha256": bound_hashes.get(
            "validation/rigorous/flagship_import.lock.json"),
        "commit": flagship_lock.get("commit"),
        "tree": flagship_lock.get("tree"),
        "access": "git-object-read-only",
    }
    if not isinstance(flagship_import, dict):
        errors.append("toolchain flagship-import record is malformed")
        expected_source_status = "INCONCLUSIVE"
    else:
        for name, expected_value in expected_flagship_fields.items():
            if flagship_import.get(name) != expected_value:
                errors.append(f"toolchain flagship-import {name} mismatch")
        flagship_errors = flagship_import.get("errors")
        if isinstance(flagship_errors, list):
            expected_source_status = "FAIL" if flagship_errors else "PASS"
        elif "reason" in flagship_import and \
                "repository_path" not in flagship_import:
            expected_source_status = "INCONCLUSIVE"
        else:
            errors.append("toolchain flagship-import verdict evidence is malformed")
            expected_source_status = "INCONCLUSIVE"
    if "ENV.SOURCE_BINDING" in by_id and \
            by_id["ENV.SOURCE_BINDING"].get("status") != expected_source_status:
        errors.append("ENV.SOURCE_BINDING differs from flagship-import evidence")
    if toolchain.get("dependency_lock_sha256") != bound_hashes.get(
            "validation/rigorous/dependency.lock.json"):
        errors.append("toolchain dependency-lock hash does not match its source binding")
    probe_source_by_scope = {
        "PREFLIGHT": "validation/rigorous/src/rounding_self_test.cpp",
        "V1_V2_1_KERNEL": "validation/rigorous/src/vdp_parameter_box_probe.cpp",
        "V2_LOCAL_GRAPH_KERNEL": "validation/rigorous/src/vdp_local_graph_probe.cpp",
        "V2_H10_C01_KERNEL": "validation/rigorous/src/vdp_h10_c01_probe.cpp",
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
    elif scope == "V2_H10_C01_KERNEL":
        expected_probe_arguments = box_arguments(bridge)
        frozen_probe_inputs = [
            h10_configuration.get("coordinate_domain", {}).get(
                "unstable_radius", {}),
            h10_configuration.get("tube_radii", {}).get(
                "value_euclidean", {}),
            h10_configuration.get("tube_radii", {}).get(
                "first_derivative_frobenius", {}),
        ]
        try:
            for value in frozen_probe_inputs:
                expected_probe_arguments.extend(
                    [value["numerator"], value["denominator"]])
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
    if scope == "V2_H10_C01_KERNEL":
        center = h10_configuration.get("imported_core_center", {})
        term_table = center.get("term_table", {})
        imported_header = probe_build.get("imported_header", {})
        expected_header = {
            "repository_commit": center.get("commit"),
            "repository_path": term_table.get("path"),
            "expected_sha256": term_table.get("sha256"),
            "materialized_sha256": term_table.get("sha256"),
            "git_show_stdout_sha256": term_table.get("sha256"),
            "compiler_include_mode": "absolute-forced-include",
        }
        if not isinstance(imported_header, dict):
            errors.append("H10 probe imported-header record is malformed")
        else:
            for name, expected_value in expected_header.items():
                if imported_header.get(name) != expected_value:
                    errors.append(f"H10 probe imported-header {name} mismatch")
            stderr_hash = imported_header.get("git_show_stderr_sha256")
            if not isinstance(stderr_hash, str) or len(stderr_hash) != 64:
                errors.append("H10 probe imported-header stderr hash is malformed")
            include_argument = imported_header.get("compiler_include_argument")
            if not isinstance(include_argument, str) or \
                    not Path(include_argument).is_absolute() or \
                    Path(include_argument).name != "unstable_graph_terms.hpp":
                errors.append(
                    "H10 probe imported-header forced-include path is invalid")
            compile_argv = probe_build.get("compile_argv", [])
            include_pairs = [
                compile_argv[index + 1]
                for index, item in enumerate(compile_argv[:-1])
                if item == "-include"
            ] if isinstance(compile_argv, list) else []
            if include_pairs != [include_argument]:
                errors.append(
                    "H10 probe compile argv does not force exactly the recorded header")

        audit_execution = toolchain.get("h10_exact_center_audit_execution", {})
        if not isinstance(audit_execution, dict):
            errors.append("H10 exact-center audit execution record is malformed")
        else:
            if audit_execution.get("audit_source_sha256") != bound_hashes.get(
                    "validation/rigorous/audit_h10_center.py"):
                errors.append(
                    "H10 exact-center audit source hash differs from its binding")
            audit = certificate.get("h10_exact_center_audit", {})
            expected_audit_exit = {
                "PASS": 0, "FAIL": 1, "INCONCLUSIVE": 2}.get(
                    audit.get("status"))
            if audit_execution.get("audit_exit_code") != expected_audit_exit:
                errors.append("H10 exact-center audit exit code differs from its verdict")
            logs = certificate.get("logs", {})
            expected_audit_stdout = (
                json.dumps(audit, indent=2, sort_keys=True) + "\n").encode()
            if logs.get("h10_audit_stdout_sha256") != sha256_bytes(
                    expected_audit_stdout):
                errors.append(
                    "H10 exact-center audit stdout hash differs from its report")
            if logs.get("h10_audit_stderr_sha256") != sha256_bytes(b""):
                errors.append("H10 exact-center audit stderr is not empty")
            audit_argv = audit_execution.get("audit_argv")
            if not isinstance(audit_argv, list) or len(audit_argv) < 4:
                errors.append("H10 exact-center audit argv is missing")
            else:
                protocol = h10_configuration.get("exact_center_audit", {})
                flagship_path = toolchain.get(
                    "flagship_import", {}).get("repository_path")
                expected_audit_tail = [
                    "--flagship-repository", flagship_path,
                    "--commit", center.get("commit"),
                    "--generator-path", center.get("generator", {}).get("path"),
                    "--generator-sha256", center.get("generator", {}).get("sha256"),
                    "--header-path", term_table.get("path"),
                    "--header-sha256", term_table.get("sha256"),
                    "--h1-term-count", str(protocol.get("h1_term_count")),
                    "--h2-term-count", str(protocol.get("h2_term_count")),
                    "--defect1-term-count", str(protocol.get("defect1_term_count")),
                    "--defect2-term-count", str(protocol.get("defect2_term_count")),
                    "--h-min-degree", str(
                        protocol.get("center_minimum_total_degree")),
                    "--h-max-degree", str(
                        protocol.get("center_maximum_total_degree")),
                    "--defect-min-degree", str(
                        protocol.get("defect_minimum_total_degree")),
                    "--defect-max-degree", str(
                        protocol.get("defect_maximum_total_degree")),
                    "--timeout-seconds", "900",
                ]
                if audit_argv[3:] != expected_audit_tail:
                    errors.append("H10 exact-center audit argv differs from frozen inputs")
                expected_argv_hash = sha256_bytes(json.dumps(
                    audit_argv, separators=(",", ":")).encode())
                if audit_execution.get("audit_argv_sha256") != expected_argv_hash:
                    errors.append("H10 exact-center audit argv hash is inconsistent")
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
