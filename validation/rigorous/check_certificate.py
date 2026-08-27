#!/usr/bin/env python3
"""Check a phase-1 certificate without upgrading an inconclusive run."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema

from rigorous_common import (
    combine_verdicts,
    git_output,
    load_json,
    safe_repository_path,
    sha256_bytes,
    sha256_file,
    validate_exact_box,
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

    scope = certificate.get("scope")
    required = P0_IDS if scope == "PREFLIGHT" else KERNEL_IDS
    missing = required - set(by_id)
    extra = set(by_id) - required
    if missing:
        errors.append(f"missing obligations: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected obligations for {scope}: {sorted(extra)}")

    p0_status = combine_verdicts(
        by_id[item]["status"] for item in P0_IDS if item in by_id)
    if len(P0_IDS & set(by_id)) == len(P0_IDS) and \
            certificate.get("integrity_status") != p0_status:
        errors.append("integrity_status is not the aggregate P0 verdict")

    if scope == "PREFLIGHT":
        expected_math = "PASS"
    else:
        mathematical_ids = required - P0_IDS
        expected_math = combine_verdicts(
            by_id[item]["status"] for item in mathematical_ids if item in by_id)
    if required <= set(by_id) and certificate.get("mathematical_status") != expected_math:
        errors.append("mathematical_status is not the mathematical-obligation aggregate")
    if scope == "V1_V2_1_KERNEL":
        if certificate.get("raw_probe", {}).get("exact_characteristic_polynomial") is not True:
            errors.append("kernel does not record the exact characteristic-polynomial identity")

    rounding = certificate.get("rounding_self_test", {})
    rounding_tests = {item.get("id"): item for item in rounding.get("tests", [])}
    if not ROUNDING_IDS <= set(rounding_tests):
        errors.append(f"rounding tests missing: {sorted(ROUNDING_IDS - set(rounding_tests))}")
    expected_rounding = combine_verdicts(
        item.get("status", "INCONCLUSIVE") for item in rounding.get("tests", []))
    if rounding.get("status") != expected_rounding:
        errors.append("rounding_self_test.status is not its test aggregate")
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
            "phase-1 checker accepts only PENDING_REQUIRED; independent replay "
            "must be aggregated by a future evidence-bearing schema")
    if replay.get("required_distinct_machines") != 2:
        errors.append("phase-1 policy requires exactly two distinct machines")
    if replay.get("observed_distinct_machines") != 1:
        errors.append("a phase-1 local certificate must record exactly one observed machine")
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
