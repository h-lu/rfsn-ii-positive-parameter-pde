#!/usr/bin/env python3
"""Build or check the local P2d reversible-symplectic-frame certificate.

The certificate is deliberately local and non-claim-bearing.  It combines
three logically separate inputs: the archived P2bK local mathematical PASS,
the deterministic exact-symbolic P2d audit, and one strict outward-rounded
interval probe.  Their aggregate discharges only
``V2.CHART.SYMPLECTIC_FRAME``.  The other six chart atoms and the
``V2.EXACT_CHART`` parent remain OPEN.

This module does not implement independent-machine replay and does not alter
or upgrade any historical certificate.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

import jsonschema

from check_certificate import (
    schema_errors as historical_schema_errors,
    semantic_errors as historical_semantic_errors,
)
from rigorous_common import (
    box_arguments,
    git_output,
    load_json,
    safe_repository_path,
    sha256_bytes,
    sha256_file,
    validate_exact_bridge,
)
from run_validation import verify_exact_symbolic_backend, verify_toolchain


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]

SCHEMA_VERSION = "rfsn-vdp-p2d-frame-certificate/1"
SCOPE = "V2_P2D_SYMPLECTIC_FRAME_KERNEL"
CONFIGURATION_ID = "vdp-p2d-symplectic-frame-v1"

BRIDGE_RELATIVE = "validation/rigorous/config/vdp_bridge_v1.json"
CONFIG_RELATIVE = (
    "validation/rigorous/config/vdp_p2d_symplectic_frame_v1.json")
CONFIG_SCHEMA_RELATIVE = (
    "validation/rigorous/p2d_symplectic_frame_config.schema.json")
RAW_SCHEMA_RELATIVE = (
    "validation/rigorous/p2d_symplectic_frame_probe.schema.json")
PROBE_RELATIVE = (
    "validation/rigorous/src/vdp_p2d_symplectic_frame_probe.cpp")
AUDIT_RELATIVE = "validation/rigorous/audit_p2d_exact_chart.py"
P2BK_RELATIVE = (
    "validation/rigorous/results/vdp_bridge_v1_p2b_kato.json")
CERTIFICATE_SCHEMA_RELATIVE = (
    "validation/rigorous/p2d_frame_certificate.schema.json")
CERTIFICATE_SOURCE_RELATIVE = (
    "validation/rigorous/p2d_frame_certificate.py")
DEPENDENCY_RELATIVE = "validation/rigorous/dependency.lock.json"
OBLIGATIONS_RELATIVE = "validation/rigorous/obligations.json"

BRIDGE_PATH = REPOSITORY / BRIDGE_RELATIVE
CONFIG_PATH = REPOSITORY / CONFIG_RELATIVE
CONFIG_SCHEMA_PATH = REPOSITORY / CONFIG_SCHEMA_RELATIVE
RAW_SCHEMA_PATH = REPOSITORY / RAW_SCHEMA_RELATIVE
PROBE_PATH = REPOSITORY / PROBE_RELATIVE
AUDIT_PATH = REPOSITORY / AUDIT_RELATIVE
P2BK_PATH = REPOSITORY / P2BK_RELATIVE
CERTIFICATE_SCHEMA_PATH = REPOSITORY / CERTIFICATE_SCHEMA_RELATIVE
DEPENDENCY_PATH = REPOSITORY / DEPENDENCY_RELATIVE

GATE_ORDER = (
    "d_positive_lower",
    "minus_e_positive_lower",
    "kappa_lower",
    "kappa_upper",
    "kappa_plus_d_lower",
    "half_denominator_lower",
    "cos_theta_lower",
    "abs_sin_theta_upper",
    "radial_scale_lower",
    "radial_scale_upper",
    "abs_theta_upper",
    "anchor_deviation_upper",
    "normalized_L_D1_upper",
    "normalized_L_D2_upper",
    "normalized_L_inverse_D1_upper",
    "normalized_L_inverse_D2_upper",
    "original_L_D1_upper",
    "original_L_D2_upper",
    "original_L_inverse_D1_upper",
    "original_L_inverse_D2_upper",
)

OPEN_ATOMS = (
    "V2.CHART.ANALYTIC_NORMAL_FORM",
    "V2.CHART.ZERO_ENERGY",
    "V2.CHART.EXACT_SECTIONS",
    "V2.CHART.WEIGHTED_PASSAGE",
    "V2.CHART.PHYSICAL_SLIDES",
    "V2.CHART.OVERLAPS",
)

CHART_STATUS = {
    "V2.CHART.SYMPLECTIC_FRAME": "PASS",
    **{identifier: "OPEN" for identifier in OPEN_ATOMS},
    "V2.EXACT_CHART": "OPEN",
}

NONCLAIMS = [
    "A local mathematical PASS is not an aggregate theorem certificate.",
    "Independent-machine replay is pending and this certificate is not claim-bearing.",
    "The exact-symbolic audit alone leaves every V2 chart atom OPEN; only its combination with the archived P2bK prerequisite and the strict interval frame probe discharges V2.CHART.SYMPLECTIC_FRAME.",
    "V2.CHART.ANALYTIC_NORMAL_FORM, V2.CHART.ZERO_ENERGY, V2.CHART.EXACT_SECTIONS, V2.CHART.WEIGHTED_PASSAGE, V2.CHART.PHYSICAL_SLIDES, V2.CHART.OVERLAPS, and V2.EXACT_CHART remain OPEN.",
    "The interval residuals are diagnostics and are not used as substitutes for the exact symplectic, inverse, reverser, action-sign, or quadratic-conjugacy identities.",
    "This certificate does not prove temporal stability, dynamic Turing-pattern selection, or finite-parameter canard identification.",
]

SOURCE_BINDING_PATHS = (
    "RESEARCH_CONTRACT.md",
    "van-der-pol/CENTRAL_CONTINUATION.md",
    "validation/rigorous/P2_VALIDATION_CONTRACT.md",
    "validation/rigorous/README.md",
    OBLIGATIONS_RELATIVE,
    DEPENDENCY_RELATIVE,
    "validation/rigorous/flagship_import.lock.json",
    BRIDGE_RELATIVE,
    "validation/rigorous/continuation_bridge.schema.json",
    CONFIG_RELATIVE,
    CONFIG_SCHEMA_RELATIVE,
    RAW_SCHEMA_RELATIVE,
    "validation/rigorous/config/vdp_p2_kato_v1.json",
    PROBE_RELATIVE,
    AUDIT_RELATIVE,
    P2BK_RELATIVE,
    CERTIFICATE_SCHEMA_RELATIVE,
    CERTIFICATE_SOURCE_RELATIVE,
    "validation/rigorous/certificate.schema.json",
    "validation/rigorous/check_certificate.py",
    "validation/rigorous/rigorous_common.py",
    "validation/rigorous/run_validation.py",
    "validation/rigorous/include/interval_io.hpp",
    "validation/rigorous/include/rounding_self_test.hpp",
    "validation/rigorous/include/verdict.hpp",
    "validation/rigorous/design/p2d_symplectic_frame_scout.cpp",
    "validation/rigorous/tests/test_p2d_frame_certificate.py",
)

EXPECTED_SELECTION_PATHS = {
    "continuation_bridge": BRIDGE_RELATIVE,
    "p2bK_configuration":
        "validation/rigorous/config/vdp_p2_kato_v1.json",
    "p2bK_archived_certificate": P2BK_RELATIVE,
    "exact_audit": AUDIT_RELATIVE,
    "design_scout":
        "validation/rigorous/design/p2d_symplectic_frame_scout.cpp",
    "formal_probe": PROBE_RELATIVE,
}


class EvidenceError(ValueError):
    """A frozen P2d-frame evidence object is missing or inconsistent."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def argv_sha256(arguments: list[str]) -> str:
    return sha256_bytes(
        json.dumps(arguments, separators=(",", ":")).encode("utf-8"))


def json_object_bytes(value: bytes, label: str) -> dict[str, Any]:
    try:
        result = json.loads(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvidenceError(f"cannot parse {label}: {error}") from error
    require(isinstance(result, dict), f"{label} is not a JSON object")
    return result


def validate_schema(instance: Any, schema: dict[str, Any],
                    label: str) -> list[str]:
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker())
    return [
        f"{label} schema "
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: "
        f"{error.message}"
        for error in sorted(
            validator.iter_errors(instance),
            key=lambda item: tuple(str(part) for part in item.path))
    ]


def certificate_schema_errors(certificate: dict[str, Any]) -> list[str]:
    return validate_schema(
        certificate, load_json(CERTIFICATE_SCHEMA_PATH), "certificate")


def git_blob(repository: Path, commit: str, relative: str) -> bytes:
    require(len(commit) == 40 and all(char in "0123456789abcdef" for char in commit),
            f"invalid Git commit: {commit!r}")
    safe_repository_path(repository, relative)
    completed = subprocess.run(
        ["git", "-C", str(repository), "show", f"{commit}:{relative}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
    if completed.returncode != 0:
        detail = completed.stderr.decode(errors="replace").strip()
        raise EvidenceError(
            f"cannot materialize {commit}:{relative}: {detail}")
    return completed.stdout


def source_bindings() -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for relative in SOURCE_BINDING_PATHS:
        path = safe_repository_path(REPOSITORY, relative)
        require(path.is_file(), f"bound source is missing: {relative}")
        result.append({
            "path": relative,
            "sha256": sha256_file(path),
            "role": "p2d-frame-input",
        })
    return result


def binding_map(certificate: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in certificate.get("source_bindings", []):
        if not isinstance(item, dict):
            continue
        relative, digest = item.get("path"), item.get("sha256")
        if isinstance(relative, str) and isinstance(digest, str):
            if relative in result:
                raise EvidenceError(f"duplicate source binding: {relative}")
            result[relative] = digest
    return result


def bound_bytes(certificate: dict[str, Any], relative: str) -> bytes:
    revision = certificate.get("source_revision", {})
    if revision.get("repository_dirty") is True:
        return safe_repository_path(REPOSITORY, relative).read_bytes()
    return git_blob(REPOSITORY, str(revision.get("commit", "")), relative)


def exact_interval(value: Any, label: str) -> tuple[float, float]:
    require(isinstance(value, dict), f"{label} is not an interval object")
    require(set(value) == {"lower_hex", "upper_hex", "endpoint_format"},
            f"{label} interval fields changed")
    require(value.get("endpoint_format") == "IEEE754_BINARY64_HEX",
            f"{label} endpoint format changed")
    try:
        lower = float.fromhex(value["lower_hex"])
        upper = float.fromhex(value["upper_hex"])
    except (TypeError, ValueError) as error:
        raise EvidenceError(f"{label} has invalid hex endpoints: {error}") \
            from error
    require(math.isfinite(lower) and math.isfinite(upper),
            f"{label} has non-finite endpoints")
    require(lower <= upper, f"{label} has reversed endpoints")
    return lower, upper


def rational_arguments(value: Any, label: str) -> list[str]:
    require(isinstance(value, dict), f"{label} is not a rational object")
    numerator = value.get("numerator")
    denominator = value.get("denominator")
    require(isinstance(numerator, str) and isinstance(denominator, str),
            f"{label} rational fields are not strings")
    try:
        parsed_denominator = int(denominator)
        int(numerator)
    except ValueError as error:
        raise EvidenceError(f"{label} is not an integer rational") from error
    require(parsed_denominator > 0, f"{label} denominator is not positive")
    return [numerator, denominator]


def _configuration_grid(configuration: dict[str, Any]) -> dict[str, Any]:
    domain = configuration.get("parameter_domain")
    grid = (
        domain.get("parameter_grid")
        if isinstance(domain, dict) else None)
    if grid is None:
        grid = configuration.get("parameter_grid", configuration.get("grid"))
    require(isinstance(grid, dict), "frame configuration lacks its grid")
    return grid


def _configuration_gates(configuration: dict[str, Any]) -> dict[str, Any]:
    gates = configuration.get(
        "acceptance_gates", configuration.get("gates"))
    require(isinstance(gates, dict),
            "frame configuration lacks acceptance gates")
    return gates


def validate_configuration_semantics(
        configuration: dict[str, Any],
        available_hashes: dict[str, str] | None = None) -> list[str]:
    errors = validate_schema(
        configuration, load_json(CONFIG_SCHEMA_PATH), "frame configuration")
    try:
        require(configuration.get("configuration_id") == CONFIGURATION_ID,
                "frame configuration id changed")
        grid = _configuration_grid(configuration)
        require(grid.get("subdivisions") == [16, 8, 4],
                "frame grid subdivisions changed")
        gates = _configuration_gates(configuration)
        require(set(gates) == set(GATE_ORDER),
                "frame acceptance-gate set changed")
        for name in GATE_ORDER:
            rational_arguments(gates[name], f"acceptance_gates.{name}")

        selection = configuration.get("selection_basis")
        require(isinstance(selection, dict),
                "frame configuration lacks selection_basis")
        for name, expected_path in EXPECTED_SELECTION_PATHS.items():
            item = selection.get(name)
            require(isinstance(item, dict),
                    f"frame selection lacks {name}")
            require(item.get("path") == expected_path,
                    f"frame selection {name} path changed")
            expected_hash = (
                available_hashes.get(expected_path)
                if available_hashes is not None else
                sha256_file(REPOSITORY / expected_path))
            require(item.get("sha256") == expected_hash,
                    f"frame selection {name} hash mismatch")
    except (EvidenceError, OSError) as error:
        errors.append(str(error))
    return errors


def probe_arguments(bridge: dict[str, Any],
                    configuration: dict[str, Any]) -> list[str]:
    arguments = box_arguments(bridge)
    grid = _configuration_grid(configuration)
    subdivisions = grid.get("subdivisions")
    require(subdivisions == [16, 8, 4],
            "frame probe grid is not the frozen 16x8x4 grid")
    arguments.extend(str(value) for value in subdivisions)
    gates = _configuration_gates(configuration)
    for name in GATE_ORDER:
        arguments.extend(rational_arguments(
            gates.get(name), f"acceptance_gates.{name}"))
    require(len(arguments) == 55,
            f"frame probe expects 55 arguments, observed {len(arguments)}")
    return arguments


def prerequisite_record(certificate: dict[str, Any]) -> dict[str, Any]:
    errors = historical_schema_errors(certificate) + \
        historical_semantic_errors(certificate, REPOSITORY)
    if errors:
        raise EvidenceError(
            "archived P2bK certificate is invalid: " + "; ".join(errors))
    by_id = {
        item.get("id"): item.get("status")
        for item in certificate.get("obligations", [])
        if isinstance(item, dict)
    }
    expected_atoms = {
        "V2.PHASE.TRUE_SOURCE": "PASS",
        "V2.PHASE.KATO_INTERFACE": "PASS",
    }
    require(certificate.get("scope") == "V2_P2_KATO_KERNEL",
            "archived P2bK scope changed")
    require(certificate.get("integrity_status") == "PASS",
            "archived P2bK integrity status is not PASS")
    require(certificate.get("mathematical_status") == "PASS",
            "archived P2bK mathematical status is not PASS")
    require(certificate.get("final_status") == "INCONCLUSIVE",
            "archived P2bK final status changed")
    require(certificate.get("claim_bearing") is False,
            "archived P2bK unexpectedly became claim-bearing")
    require(all(by_id.get(name) == status
                for name, status in expected_atoms.items()),
            "archived P2bK phase atoms do not both PASS")
    bridge = load_json(BRIDGE_PATH)
    recorded_bridge = certificate.get("continuation_bridge", {})
    require(recorded_bridge.get("sha256") == sha256_file(BRIDGE_PATH),
            "archived P2bK bridge hash differs from the frozen bridge")
    require(recorded_bridge.get("variables") == bridge.get("variables"),
            "archived P2bK bridge endpoints changed")
    return {
        "path": P2BK_RELATIVE,
        "sha256": sha256_file(P2BK_PATH),
        "scope": certificate["scope"],
        "source_commit": certificate["source_revision"]["commit"],
        "integrity_status": certificate["integrity_status"],
        "mathematical_status": certificate["mathematical_status"],
        "final_status": certificate["final_status"],
        "claim_bearing": certificate["claim_bearing"],
        "required_atoms": expected_atoms,
    }


def validate_exact_audit_report(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        require(report.get("schema_version") ==
                "rfsn-vdp-p2d-exact-chart-audit/2",
                "P2d exact-audit schema version changed")
        require(report.get("status") == "PASS",
                "P2d exact audit did not PASS")
        require(report.get("method") ==
                "exact-symbolic-identities-no-sampling-no-file-inputs",
                "P2d exact-audit method changed")
        checks = report.get("checks")
        require(isinstance(checks, dict) and len(checks) == 59,
                "P2d exact audit does not expose the frozen 59 checks")
        require(all(value is True for value in checks.values()),
                "P2d exact audit contains a failed identity")
        policy = report.get("input_policy")
        require(policy == {
            "external_files": [], "floating_point": False,
            "sampling": False},
            "P2d exact-audit input policy changed")
        boundary = report.get("claim_boundary")
        require(isinstance(boundary, dict),
                "P2d exact audit lacks its claim boundary")
        atoms = boundary.get("v2_chart_atoms")
        require(isinstance(atoms, dict),
                "P2d exact audit lacks the seven-atom status map")
        require(set(atoms) == {
            "V2.CHART.SYMPLECTIC_FRAME", *OPEN_ATOMS},
            "P2d exact-audit atom set changed")
        require(set(atoms.values()) == {"OPEN"},
                "P2d exact audit alone must leave every chart atom OPEN")
        require(boundary.get("parent_obligation") ==
                "V2.EXACT_CHART remains OPEN",
                "P2d exact audit changed the parent boundary")
        require(boundary.get("claim_bearing") is False,
                "P2d exact audit unexpectedly became claim-bearing")
    except EvidenceError as error:
        errors.append(str(error))
    return errors


def run_exact_audit(path: Path = AUDIT_PATH) -> dict[str, Any]:
    python = str(Path(sys.executable).resolve())
    arguments = [python, "-B", str(path.resolve())]
    environment = os.environ.copy()
    environment.update({
        "LC_ALL": "C.UTF-8",
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    completed = subprocess.run(
        arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=environment, timeout=120)
    require(completed.returncode in (0, 1),
            f"P2d exact audit returned {completed.returncode}")
    require(completed.stderr == b"", "P2d exact audit emitted stderr")
    require(completed.stdout.count(b"\n") == 1,
            "P2d exact audit did not emit exactly one JSON line")
    report = json_object_bytes(completed.stdout, "P2d exact audit")
    errors = validate_exact_audit_report(report)
    require(not errors, "; ".join(errors))
    stdout = completed.stdout.decode("utf-8")
    require(stdout == canonical_json(report),
            "P2d exact-audit stdout is not canonical JSON")
    return {
        "path": AUDIT_RELATIVE,
        "sha256": sha256_file(path),
        "report": report,
        "execution": {
            "python_executable": python,
            "argv": arguments,
            "argv_sha256": argv_sha256(arguments),
            "exit_code": completed.returncode,
            "stdout": stdout,
            "stdout_sha256": sha256_bytes(completed.stdout),
            "stderr_sha256": sha256_bytes(completed.stderr),
        },
    }


def replay_bound_exact_audit(certificate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    exact = certificate.get("exact_audit", {})
    execution = exact.get("execution", {}) if isinstance(exact, dict) else {}
    report = exact.get("report", {}) if isinstance(exact, dict) else {}
    try:
        source = bound_bytes(certificate, AUDIT_RELATIVE)
        require(exact.get("sha256") == sha256_bytes(source),
                "bound exact-audit source hash changed")
        require(execution.get("stdout") == canonical_json(report),
                "recorded exact-audit stdout differs from canonical report")
        require(execution.get("stdout_sha256") == sha256_bytes(
            str(execution.get("stdout", "")).encode("utf-8")),
            "recorded exact-audit stdout hash changed")
        require(execution.get("stderr_sha256") == sha256_bytes(b""),
                "recorded exact-audit stderr hash is not empty")
        arguments = execution.get("argv")
        require(isinstance(arguments, list) and len(arguments) == 3,
                "recorded exact-audit argv is malformed")
        require(execution.get("argv_sha256") == argv_sha256(arguments),
                "recorded exact-audit argv hash changed")
        python = str(Path(sys.executable).resolve())
        require(Path(str(execution.get("python_executable", ""))).resolve() ==
                Path(python),
                "recorded exact-audit Python differs from this checker")
        require(Path(arguments[0]).resolve() == Path(python) and
                arguments[1] == "-B" and
                Path(arguments[2]).parts[-2:] ==
                ("rigorous", "audit_p2d_exact_chart.py"),
                "recorded exact-audit command changed")
        errors.extend(validate_exact_audit_report(report))
        if errors:
            return errors
        with tempfile.TemporaryDirectory(
                prefix="rfsn-p2d-audit-replay-") as temporary:
            audit_path = Path(temporary) / "audit_p2d_exact_chart.py"
            audit_path.write_bytes(source)
            replayed = run_exact_audit(audit_path)
        require(replayed["execution"]["stdout"] == execution.get("stdout"),
                "P2d exact-audit replay changed bytewise")
        require(replayed["execution"]["exit_code"] ==
                execution.get("exit_code"),
                "P2d exact-audit replay exit code changed")
    except (EvidenceError, OSError, subprocess.SubprocessError) as error:
        errors.append(str(error))
    return errors


def derive_capd_source(capd_config: Path) -> Path:
    completed = subprocess.run(
        [str(capd_config.resolve()), "--cflags"], check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
    candidates: list[Path] = []
    for token in shlex.split(completed.stdout):
        if token.startswith("-I"):
            include = Path(token[2:]).resolve()
            if include.parts[-2:] == ("capdDynSys", "include"):
                candidates.append(include.parents[1])
    require(len(candidates) == 1,
            "capd-config does not identify one CAPD source root")
    return candidates[0]


def run_formal_probe(
        capd_config: Path, bridge: dict[str, Any],
        configuration: dict[str, Any], dependency: dict[str, Any],
        ) -> tuple[dict[str, Any], dict[str, Any]]:
    required_config = Path(
        dependency["capd"]["reference_capd_config"]).resolve()
    require(capd_config.resolve() == required_config,
            "formal P2d-frame runs must use dependency.lock's reference "
            f"capd-config: {required_config}")
    capd_source = derive_capd_source(capd_config)
    toolchain_status, toolchain, cflags, libraries = verify_toolchain(
        capd_source, capd_config.resolve(), dependency)
    require(toolchain_status == "PASS",
            "strict CAPD/FILIB toolchain did not PASS: " +
            "; ".join(toolchain.get("fatal_errors", []) +
                      toolchain.get("incomplete_checks", [])))
    exact_status, exact_backend, exact_errors = \
        verify_exact_symbolic_backend(dependency)
    require(exact_status == "PASS",
            "exact symbolic backend did not PASS: " +
            "; ".join(exact_errors))

    compiler = dependency["compiler"]["executable"]
    strict_flags = dependency["compiler"]["required_probe_flags"]
    probe_inputs = probe_arguments(bridge, configuration)
    environment = os.environ.copy()
    environment.update({
        "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
    })
    with tempfile.TemporaryDirectory(
            prefix="rfsn-p2d-frame-build-") as temporary:
        binary = Path(temporary) / "probe"
        command = [
            compiler, "-std=c++17", f"-I{HERE / 'include'}",
            *cflags, *strict_flags, str(PROBE_PATH), "-o", str(binary),
            *libraries,
        ]
        compiled = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=environment, timeout=180)
        require(compiled.returncode == 0,
                "formal frame probe compilation failed: " +
                compiled.stderr.decode(errors="replace"))
        run_command = [str(binary), *probe_inputs]
        executed = subprocess.run(
            run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=environment, timeout=120)
        require(executed.returncode in (0, 1, 2),
                f"formal frame probe returned {executed.returncode}")
        require(compiled.stdout == b"" and compiled.stderr == b"",
                "strict formal frame compilation emitted output")
        require(executed.stderr == b"",
                "strict formal frame probe emitted stderr")
        raw = json_object_bytes(executed.stdout, "formal frame probe")
        normalized_compile = [
            *command[:command.index("-o") + 1], "<TEMPORARY_OUTPUT>",
            *command[command.index("-o") + 2:],
        ]
        probe_build = {
            "source_path": PROBE_RELATIVE,
            "source_sha256": sha256_file(PROBE_PATH),
            "compile_argv_template": normalized_compile,
            "compile_argv_sha256": argv_sha256(normalized_compile),
            "binary_sha256": sha256_file(binary),
            "probe_arguments": probe_inputs,
            "probe_exit_code": executed.returncode,
            "probe_stdout": executed.stdout.decode("utf-8"),
            "compile_stdout_sha256": sha256_bytes(compiled.stdout),
            "compile_stderr_sha256": sha256_bytes(compiled.stderr),
            "probe_stdout_sha256": sha256_bytes(executed.stdout),
            "probe_stderr_sha256": sha256_bytes(executed.stderr),
        }
    toolchain["exact_symbolic_backend"] = exact_backend
    toolchain["probe_build"] = probe_build
    return raw, toolchain


def validate_raw_probe(
        raw: dict[str, Any], configuration: dict[str, Any]) -> list[str]:
    errors = validate_schema(
        raw, load_json(RAW_SCHEMA_PATH), "formal frame probe")
    try:
        require(raw.get("schema_version") ==
                "rfsn-vdp-p2d-symplectic-frame-probe/1",
                "formal frame probe schema version changed")
        require(raw.get("status") == "PASS",
                "formal frame aggregate did not PASS on the reference build")
        require(raw.get("mathematical_status") == "PASS",
                "formal frame mathematical component did not PASS")
        require(raw.get("structure_status") == "PASS",
                "formal frame structure checks did not PASS")
        rounding = raw.get("rounding_self_test")
        require(isinstance(rounding, dict) and
                rounding.get("status") == "PASS",
                "formal frame rounding self-test did not PASS")
        rounding_tests = {
            item.get("id"): item.get("status")
            for item in rounding.get("tests", [])
            if isinstance(item, dict)
        }
        require(rounding_tests and
                all(status == "PASS" for status in rounding_tests.values()),
                "a formal frame rounding test is not PASS")
        grid = raw.get("grid")
        require(isinstance(grid, dict) and
                grid.get("subdivisions") == [16, 8, 4] and
                grid.get("cell_count", grid.get("cells")) == 512,
                "formal frame raw grid changed")
        margins = raw.get("gate_margins")
        require(isinstance(margins, dict) and
                set(margins) == set(GATE_ORDER),
                "formal frame gate-margin set changed")
        for name in GATE_ORDER:
            lower, _ = exact_interval(margins[name],
                                      f"gate_margins.{name}")
            require(lower > 0.0,
                    f"gate_margins.{name} is not strictly positive")
        obligations = raw.get("obligations")
        require(isinstance(obligations, list) and len(obligations) == 1,
                "formal frame probe must expose one interval obligation")
        obligation = obligations[0]
        require(obligation.get("id") == "V2.CHART.SYMPLECTIC_FRAME" and
                obligation.get("component") == "interval_component_only" and
                obligation.get("status") == "PASS",
                "formal frame interval obligation changed")
        boundary = raw.get("claim_boundary")
        require(isinstance(boundary, dict),
                "formal frame probe lacks its claim boundary")
        require(boundary.get("claim_bearing") is False and
                boundary.get("raw_pass_scope") ==
                "interval_frame_predicate_only" and
                boundary.get("exact_audit_included_in_raw_status") is False and
                boundary.get("P2bK_prerequisite_included_in_raw_status") is False and
                boundary.get(
                    "V2_CHART_SYMPLECTIC_FRAME_closed_by_raw_probe") is False and
                boundary.get("V2_EXACT_CHART_closed") is False,
                "formal interval probe overclaims its component")
        require(probe_arguments(load_json(BRIDGE_PATH), configuration),
                "formal frame probe has no frozen arguments")
    except EvidenceError as error:
        errors.append(str(error))
    return errors


def predicates_from_manifest(manifest: dict[str, Any]) -> dict[str, str]:
    return {
        item["id"]: item["predicate"]
        for phase in manifest["phases"]
        for item in phase["obligations"]
    }


def expected_obligations(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    predicates = predicates_from_manifest(manifest)
    return [
        {
            "id": "P2.P2BK_PREREQUISITE",
            "predicate": predicates["P2.P2BK_PREREQUISITE"],
            "status": "PASS",
            "components": {"archived_p2bk_local_certificate": "PASS"},
        },
        {
            "id": "V2.CHART.SYMPLECTIC_FRAME",
            "predicate": predicates["V2.CHART.SYMPLECTIC_FRAME"],
            "status": "PASS",
            "components": {
                "p2bk_prerequisite": "PASS",
                "exact_symbolic_audit": "PASS",
                "outward_interval_frame": "PASS",
            },
        },
    ]


def _toolchain_semantic_errors(
        certificate: dict[str, Any], dependency: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    recorded = certificate.get("toolchain")
    if not isinstance(recorded, dict):
        return ["certificate toolchain is not an object"]
    try:
        capd = recorded.get("capd")
        require(isinstance(capd, dict), "certificate lacks CAPD toolchain data")
        capd_source = Path(str(capd.get("source_path", "")))
        capd_config = Path(str(capd.get("config_path", "")))
        status, observed, _, _ = verify_toolchain(
            capd_source, capd_config, dependency)
        observed["dependency_lock_sha256"] = sha256_bytes(
            bound_bytes(certificate, DEPENDENCY_RELATIVE))
        require(status == "PASS", "recomputed strict toolchain did not PASS")
        exact_status, exact_backend, exact_errors = \
            verify_exact_symbolic_backend(dependency)
        require(exact_status == "PASS" and not exact_errors,
                "recomputed exact symbolic backend did not PASS")
        observed["exact_symbolic_backend"] = exact_backend
        observed["probe_build"] = recorded.get("probe_build")
        require(recorded == observed,
                "recorded toolchain differs from its local recomputation")
    except (EvidenceError, OSError, KeyError, subprocess.SubprocessError) as error:
        errors.append(str(error))
    return errors


def _probe_build_semantic_errors(
        certificate: dict[str, Any], bridge: dict[str, Any],
        configuration: dict[str, Any], dependency: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        toolchain = certificate.get("toolchain", {})
        build = toolchain.get("probe_build")
        require(isinstance(build, dict),
                "certificate lacks its formal probe build")
        bindings = binding_map(certificate)
        require(build.get("source_path") == PROBE_RELATIVE,
                "formal probe source path changed")
        require(build.get("source_sha256") == bindings.get(PROBE_RELATIVE),
                "formal probe source hash differs from its binding")
        arguments = probe_arguments(bridge, configuration)
        require(build.get("probe_arguments") == arguments,
                "formal probe arguments differ from the frozen inputs")
        template = build.get("compile_argv_template")
        require(isinstance(template, list) and
                build.get("compile_argv_sha256") == argv_sha256(template),
                "formal probe compile template hash changed")
        require(template.count("<TEMPORARY_OUTPUT>") == 1,
                "formal probe compile template has no unique output marker")
        capd_record = toolchain.get("capd")
        compiler_record = toolchain.get("compiler")
        require(isinstance(capd_record, dict) and
                isinstance(compiler_record, dict),
                "formal probe toolchain records are malformed")
        expected_template = [
            dependency["compiler"]["executable"],
            "-std=c++17", f"-I{HERE / 'include'}",
            *capd_record["cflags"],
            *dependency["compiler"]["required_probe_flags"],
            str(PROBE_PATH), "-o", "<TEMPORARY_OUTPUT>",
            *capd_record["libs"],
        ]
        require(template == expected_template,
                "formal probe compile template differs from the frozen "
                "compiler/CAPD command")
        stdout = build.get("probe_stdout")
        require(isinstance(stdout, str),
                "formal probe exact stdout is missing")
        require(build.get("probe_stdout_sha256") ==
                sha256_bytes(stdout.encode("utf-8")),
                "formal probe stdout hash changed")
        raw = json.loads(stdout)
        require(raw == certificate.get("raw_probe"),
                "formal probe stdout differs from raw_probe")
        empty_hash = sha256_bytes(b"")
        for name in (
                "compile_stdout_sha256", "compile_stderr_sha256",
                "probe_stderr_sha256"):
            require(build.get(name) == empty_hash,
                    f"strict formal probe emitted {name}")
        expected_exit = {"PASS": 0, "FAIL": 1,
                         "INCONCLUSIVE": 2}.get(raw.get("status"))
        require(build.get("probe_exit_code") == expected_exit,
                "formal probe exit code differs from its raw status")
    except (EvidenceError, TypeError, json.JSONDecodeError) as error:
        errors.append(str(error))
    return errors


def _replay_bound_probe(
        certificate: dict[str, Any], bridge: dict[str, Any],
        configuration: dict[str, Any], dependency: dict[str, Any]) -> list[str]:
    """Recompile and rerun the bound probe on this same local machine.

    This closes certificate-local coordinated edits of ``raw_probe`` and its
    stored hashes.  It is not the independent second-machine replay required
    for a claim-bearing release.
    """

    errors: list[str] = []
    try:
        toolchain = certificate.get("toolchain", {})
        build = toolchain.get("probe_build", {})
        capd = toolchain.get("capd", {})
        compiler = dependency["compiler"]["executable"]
        required_config = Path(
            dependency["capd"]["reference_capd_config"]).resolve()
        require(Path(str(capd.get("config_path", ""))).resolve() ==
                required_config,
                "bound formal probe did not use the reference capd-config")
        source_bytes = bound_bytes(certificate, PROBE_RELATIVE)
        header_relatives = (
            "validation/rigorous/include/interval_io.hpp",
            "validation/rigorous/include/rounding_self_test.hpp",
            "validation/rigorous/include/verdict.hpp",
        )
        probe_inputs = probe_arguments(bridge, configuration)
        environment = os.environ.copy()
        environment.update({
            "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
        })
        with tempfile.TemporaryDirectory(
                prefix="rfsn-p2d-frame-check-") as temporary:
            root = Path(temporary)
            include = root / "include"
            include.mkdir()
            source = root / Path(PROBE_RELATIVE).name
            source.write_bytes(source_bytes)
            for relative in header_relatives:
                (include / Path(relative).name).write_bytes(
                    bound_bytes(certificate, relative))
            binary = root / "probe"
            command = [
                compiler, "-std=c++17", f"-I{include}",
                *capd["cflags"],
                *dependency["compiler"]["required_probe_flags"],
                str(source), "-o", str(binary), *capd["libs"],
            ]
            compiled = subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=environment, timeout=180)
            require(compiled.returncode == 0,
                    "local formal-probe replay compilation failed: " +
                    compiled.stderr.decode(errors="replace"))
            require(sha256_bytes(compiled.stdout) ==
                    build.get("compile_stdout_sha256"),
                    "formal-probe replay compile stdout changed")
            require(sha256_bytes(compiled.stderr) ==
                    build.get("compile_stderr_sha256"),
                    "formal-probe replay compile stderr changed")
            executed = subprocess.run(
                [str(binary), *probe_inputs], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, env=environment, timeout=120)
            require(executed.returncode == build.get("probe_exit_code"),
                    "formal-probe replay exit code changed")
            require(executed.stdout.decode("utf-8") ==
                    build.get("probe_stdout"),
                    "formal-probe replay stdout changed bytewise")
            require(sha256_bytes(executed.stdout) ==
                    build.get("probe_stdout_sha256"),
                    "formal-probe replay stdout hash changed")
            require(sha256_bytes(executed.stderr) ==
                    build.get("probe_stderr_sha256"),
                    "formal-probe replay stderr changed")
    except (EvidenceError, OSError, KeyError,
            subprocess.SubprocessError) as error:
        errors.append(str(error))
    return errors


def semantic_errors(certificate: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    revision = certificate.get("source_revision", {})
    try:
        commit = str(revision.get("commit", ""))
        git_output(REPOSITORY, "cat-file", "-e", f"{commit}^{{commit}}")
        dirty = revision.get("repository_dirty") is True
        allow_dirty = revision.get("allow_dirty_development") is True
        require(not dirty or allow_dirty,
                "dirty development certificate lacks --allow-dirty")
        bindings = binding_map(certificate)
        require(set(bindings) == set(SOURCE_BINDING_PATHS),
                "P2d-frame source-binding set changed")
        for relative, digest in bindings.items():
            observed = bound_bytes(certificate, relative)
            require(digest == sha256_bytes(observed),
                    f"source binding hash mismatch: {relative}")
    except (EvidenceError, OSError, subprocess.SubprocessError) as error:
        errors.append(str(error))
        return errors

    try:
        bridge = json_object_bytes(
            bound_bytes(certificate, BRIDGE_RELATIVE), "bound bridge")
        errors.extend(validate_exact_bridge(bridge))
        recorded_bridge = certificate.get("continuation_bridge", {})
        require(recorded_bridge == {
            "path": BRIDGE_RELATIVE,
            "sha256": bindings[BRIDGE_RELATIVE],
            "bridge_id": bridge["bridge_id"],
            "variables": bridge["variables"],
        }, "certificate continuation bridge changed")

        configuration = json_object_bytes(
            bound_bytes(certificate, CONFIG_RELATIVE),
            "bound frame configuration")
        # The schema itself is source-bound.  The current development checker
        # uses the same bytes; a clean historical check first verifies the
        # recorded schema binding above.
        errors.extend(validate_configuration_semantics(
            configuration, bindings))
        require(certificate.get("configuration") == {
            "path": CONFIG_RELATIVE,
            "sha256": bindings[CONFIG_RELATIVE],
            "configuration_id": configuration["configuration_id"],
        }, "certificate frame-configuration record changed")

        p2bk = json_object_bytes(
            bound_bytes(certificate, P2BK_RELATIVE), "bound P2bK certificate")
        expected_p2bk = prerequisite_record(p2bk)
        expected_p2bk["sha256"] = bindings[P2BK_RELATIVE]
        require(certificate.get("p2bk_prerequisite") == expected_p2bk,
                "certificate P2bK prerequisite record changed")

        exact_errors = replay_bound_exact_audit(certificate)
        errors.extend(exact_errors)

        dependency = json_object_bytes(
            bound_bytes(certificate, DEPENDENCY_RELATIVE),
            "bound dependency lock")

        raw = certificate.get("raw_probe")
        require(isinstance(raw, dict), "certificate raw_probe is not an object")
        errors.extend(validate_raw_probe(raw, configuration))
        errors.extend(_probe_build_semantic_errors(
            certificate, bridge, configuration, dependency))
        errors.extend(_toolchain_semantic_errors(certificate, dependency))
        if not errors:
            errors.extend(_replay_bound_probe(
                certificate, bridge, configuration, dependency))

        manifest = json_object_bytes(
            bound_bytes(certificate, OBLIGATIONS_RELATIVE),
            "bound obligation manifest")
        require(certificate.get("obligations") ==
                expected_obligations(manifest),
                "certificate obligation aggregation changed")
        require(certificate.get("chart_status") == CHART_STATUS,
                "certificate chart-status boundary changed")
        require(certificate.get("integrity_status") == "PASS",
                "P2d-frame integrity status is not PASS")
        require(certificate.get("mathematical_status") == "PASS",
                "P2d-frame local mathematical status is not PASS")
        require(certificate.get("independent_replay") == {
            "status": "PENDING_REQUIRED",
            "required_distinct_machines": 2,
            "observed_distinct_machines": 1,
        }, "P2d-frame replay boundary changed")
        require(certificate.get("final_status") == "INCONCLUSIVE",
                "P2d-frame final status must remain INCONCLUSIVE")
        require(certificate.get("claim_bearing") is False and
                certificate.get("release_eligible") is False,
                "local P2d-frame certificate cannot be claim-bearing")
        require(certificate.get("nonclaims") == NONCLAIMS,
                "P2d-frame nonclaims changed")
    except (EvidenceError, KeyError, OSError, subprocess.SubprocessError) as error:
        errors.append(str(error))
    return errors


def build_certificate(output: Path, capd_config: Path,
                      allow_dirty: bool) -> dict[str, Any]:
    require(CERTIFICATE_SCHEMA_PATH.is_file(),
            "P2d-frame certificate schema is missing")
    for path in (CONFIG_PATH, CONFIG_SCHEMA_PATH, RAW_SCHEMA_PATH,
                 PROBE_PATH, AUDIT_PATH, P2BK_PATH):
        require(path.is_file(), f"required P2d-frame input is missing: {path}")
    bridge = load_json(BRIDGE_PATH)
    bridge_errors = validate_exact_bridge(bridge)
    require(not bridge_errors, "; ".join(bridge_errors))
    configuration = load_json(CONFIG_PATH)
    config_errors = validate_configuration_semantics(configuration)
    require(not config_errors, "; ".join(config_errors))
    p2bk = load_json(P2BK_PATH)
    prerequisite = prerequisite_record(p2bk)
    exact_audit = run_exact_audit()
    dependency = load_json(DEPENDENCY_PATH)
    raw, toolchain = run_formal_probe(
        capd_config, bridge, configuration, dependency)
    raw_errors = validate_raw_probe(raw, configuration)
    require(not raw_errors, "; ".join(raw_errors))

    head = git_output(REPOSITORY, "rev-parse", "HEAD")
    dirty = bool(git_output(REPOSITORY, "status", "--porcelain"))
    require(not dirty or allow_dirty,
            "repository is dirty; use --allow-dirty only for a local development certificate")
    bindings = source_bindings()
    manifest = load_json(REPOSITORY / OBLIGATIONS_RELATIVE)
    now = dt.datetime.now(dt.timezone.utc)
    certificate = {
        "schema_version": SCHEMA_VERSION,
        "certificate_id": f"vdp-p2d-frame-{head[:12]}",
        "scope": SCOPE,
        "created_at": now.isoformat(),
        "source_revision": {
            "repository": "h-lu/rfsn-ii-positive-parameter-pde",
            "commit": head,
            "repository_dirty": dirty,
            "allow_dirty_development": allow_dirty,
            "working_tree_observation": "BEFORE_REPORT_WRITE",
            "report_output_excluded_from_observation": True,
        },
        "source_bindings": bindings,
        "configuration": {
            "path": CONFIG_RELATIVE,
            "sha256": sha256_file(CONFIG_PATH),
            "configuration_id": configuration["configuration_id"],
        },
        "continuation_bridge": {
            "path": BRIDGE_RELATIVE,
            "sha256": sha256_file(BRIDGE_PATH),
            "bridge_id": bridge["bridge_id"],
            "variables": bridge["variables"],
        },
        "p2bk_prerequisite": prerequisite,
        "exact_audit": exact_audit,
        "toolchain": toolchain,
        "raw_probe": raw,
        "obligations": expected_obligations(manifest),
        "chart_status": CHART_STATUS,
        "integrity_status": "PASS",
        "mathematical_status": "PASS",
        "independent_replay": {
            "status": "PENDING_REQUIRED",
            "required_distinct_machines": 2,
            "observed_distinct_machines": 1,
        },
        "final_status": "INCONCLUSIVE",
        "claim_bearing": False,
        "release_eligible": False,
        "nonclaims": NONCLAIMS,
    }
    errors = certificate_schema_errors(certificate) + \
        semantic_errors(certificate)
    require(not errors, "generated certificate failed self-check: " +
            "; ".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(certificate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    return certificate


def check_certificate(path: Path) -> list[str]:
    try:
        certificate = load_json(path)
    except (OSError, json.JSONDecodeError) as error:
        return [f"cannot read certificate: {error}"]
    return certificate_schema_errors(certificate) + semantic_errors(certificate)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser(
        "build", help="build one local non-claim-bearing frame certificate")
    build.add_argument("output", type=Path)
    build.add_argument("--capd-config", type=Path, required=True)
    build.add_argument("--allow-dirty", action="store_true")
    check = subparsers.add_parser("check", help="check one frame certificate")
    check.add_argument("file", type=Path)
    return parser


def main(arguments: Iterable[str] | None = None) -> int:
    parsed = make_parser().parse_args(arguments)
    try:
        if parsed.command == "build":
            certificate = build_certificate(
                parsed.output.resolve(), parsed.capd_config.resolve(),
                parsed.allow_dirty)
            print(
                f"wrote {parsed.output}: "
                f"mathematical_status={certificate['mathematical_status']}, "
                f"final_status={certificate['final_status']}, "
                "claim_bearing=false")
            return 0
        errors = check_certificate(parsed.file.resolve())
        if errors:
            for error in errors:
                print(f"INVALID: {error}", file=sys.stderr)
            return 1
        certificate = load_json(parsed.file.resolve())
        print(
            "VALID: local V2.CHART.SYMPLECTIC_FRAME mathematical PASS; "
            "six chart atoms and V2.EXACT_CHART remain OPEN; "
            f"final_status={certificate['final_status']}; "
            "claim_bearing=false")
        return 0
    except (EvidenceError, OSError, KeyError, ValueError,
            subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"P2d frame certificate error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
