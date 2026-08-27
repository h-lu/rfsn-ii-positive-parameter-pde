#!/usr/bin/env python3
"""Compile, run, and certify staged CAPD/FILIB validation probes."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import jsonschema

from check_certificate import schema_errors, semantic_errors
from rigorous_common import (
    box_arguments,
    combine_verdicts,
    git_output,
    load_json,
    observe_exact_symbolic_backend,
    p2_jets_arguments,
    p2_kato_arguments,
    run_checked,
    safe_repository_path,
    sha256_bytes,
    sha256_file,
    validate_exact_bridge,
    validate_exact_box,
    validate_h10_c01_configuration,
    validate_local_graph_configuration,
    validate_p2_jets_configuration,
    validate_p2_kato_configuration,
    validate_p2b0_true_tube_implication,
)

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
BOX_PATH = HERE / "config" / "vdp_box_v1.json"
BRIDGE_PATH = HERE / "config" / "vdp_bridge_v1.json"
LOCAL_GRAPH_CONFIG_PATH = HERE / "config" / "vdp_p2_local_graph_v1.json"
H10_C01_CONFIG_PATH = HERE / "config" / "vdp_p2_h10_c01_v1.json"
P2_JETS_CONFIG_PATH = HERE / "config" / "vdp_p2_jets_v1.json"
P2_KATO_CONFIG_PATH = HERE / "config" / "vdp_p2_kato_v1.json"
P2A_CERTIFICATE_PATH = HERE / "results" / "vdp_bridge_v1_p2a_local_graph.json"
P2B0_CERTIFICATE_PATH = HERE / "results" / "vdp_bridge_v1_p2b_h10_c01.json"
P2B_JETS_CERTIFICATE_PATH = HERE / "results" / "vdp_bridge_v1_p2b_jets.json"
DEPENDENCY_LOCK_PATH = HERE / "dependency.lock.json"
FLAGSHIP_LOCK_PATH = HERE / "flagship_import.lock.json"

P2_JETS_SCOPE_NONCLAIM = (
    "The P2 mixed-jet kernel proves the local graph and weighted half-orbit "
    "obligations in the P2a algebraic frame; normalized Kato source phase, "
    "the selected homoclinic, exact charts, event atlas, V3--V6, temporal "
    "stability, Turing selection, and canard identification remain outside "
    "its scope."
)

P2_KATO_SCOPE_NONCLAIM = (
    "The P2 Kato kernel proves only the normalized expanding-frame and "
    "total-order-three true-source phase interface; the selected homoclinic, "
    "positive radial symplectic completion, exact charts, event atlas, "
    "V3--V6, temporal stability, Turing selection, and canard identification "
    "remain outside its scope."
)

BOUND_SOURCES = (
    "RESEARCH_CONTRACT.md",
    "theory/BASELINE.md",
    "van-der-pol/HAMILTONIAN_CHECK.md",
    "van-der-pol/MODEL_AND_CENTRAL_CHART.md",
    "van-der-pol/CENTRAL_CORE_IMPORT.md",
    "van-der-pol/CENTRAL_CONTINUATION.md",
    "validation/rigorous/README.md",
    "validation/rigorous/P2_VALIDATION_CONTRACT.md",
    "validation/rigorous/certificate.schema.json",
    "validation/rigorous/continuation_bridge.schema.json",
    "validation/rigorous/parameter_box.schema.json",
    "validation/rigorous/p2_local_graph.schema.json",
    "validation/rigorous/p2_h10_c01.schema.json",
    "validation/rigorous/p2_jets.schema.json",
    "validation/rigorous/p2_kato.schema.json",
    "validation/rigorous/config/vdp_bridge_v1.json",
    "validation/rigorous/config/vdp_box_v1.json",
    "validation/rigorous/config/vdp_p2_local_graph_v1.json",
    "validation/rigorous/config/vdp_p2_h10_c01_v1.json",
    "validation/rigorous/config/vdp_p2_jets_v1.json",
    "validation/rigorous/config/vdp_p2_kato_v1.json",
    "validation/rigorous/dependency.lock.json",
    "validation/rigorous/flagship_import.lock.json",
    "validation/rigorous/obligations.json",
    "validation/rigorous/include/verdict.hpp",
    "validation/rigorous/include/interval_io.hpp",
    "validation/rigorous/include/rounding_self_test.hpp",
    "validation/rigorous/include/exact_polynomial.hpp",
    "validation/rigorous/src/rounding_self_test.cpp",
    "validation/rigorous/src/vdp_local_graph_probe.cpp",
    "validation/rigorous/src/vdp_h10_c01_probe.cpp",
    "validation/rigorous/src/vdp_p2_jets_probe.cpp",
    "validation/rigorous/src/vdp_p2_kato_probe.cpp",
    "validation/rigorous/src/vdp_parameter_box_probe.cpp",
    "validation/rigorous/audit_h10_center.py",
    "validation/rigorous/audit_kato_exact.py",
    "validation/rigorous/results/vdp_bridge_v1_p2a_local_graph.json",
    "validation/rigorous/results/vdp_bridge_v1_p2b_h10_c01.json",
    "validation/rigorous/results/vdp_bridge_v1_p2b_jets.json",
    "validation/rigorous/design/README.md",
    "validation/rigorous/design/p2b_jets_scout.cpp",
    "validation/rigorous/design/p2b_kato_scout.cpp",
    "validation/rigorous/rigorous_common.py",
    "validation/rigorous/run_validation.py",
    "validation/rigorous/check_certificate.py",
)


def obligation_predicates() -> dict[str, str]:
    manifest = load_json(HERE / "obligations.json")
    return {
        item["id"]: item["predicate"]
        for phase in manifest["phases"]
        for item in phase["obligations"]
    }


def verify_box(box: dict[str, Any]) -> tuple[str, list[str]]:
    errors = validate_exact_box(box)
    try:
        jsonschema.validate(
            box,
            load_json(HERE / "parameter_box.schema.json"),
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as error:
        errors.append(f"schema: {error.message}")
    basis = box.get("selection_basis", {})
    floating = basis.get("floating_configuration", {})
    try:
        floating_path = safe_repository_path(REPOSITORY, floating["path"])
        if sha256_file(floating_path) != floating["sha256"]:
            errors.append("floating configuration hash changed")
        tag_commit = git_output(
            REPOSITORY, "rev-parse", f"{basis['repository_tag']}^{{commit}}")
        if tag_commit != basis["repository_commit"]:
            errors.append("selection tag does not resolve to the frozen selection commit")
        frozen_blob = subprocess.run(
            ["git", "-C", str(REPOSITORY), "show",
             f"{basis['repository_commit']}:{floating['path']}"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        if sha256_bytes(frozen_blob) != floating["sha256"]:
            errors.append("frozen selection-commit blob hash mismatch")
    except (KeyError, OSError, subprocess.SubprocessError) as error:
        errors.append(f"selection-basis verification failed: {error}")
    return ("PASS" if not errors else "FAIL", errors)


def verify_bridge(bridge: dict[str, Any], box: dict[str, Any]) -> tuple[str, list[str]]:
    errors = validate_exact_bridge(bridge)
    try:
        jsonschema.validate(
            bridge,
            load_json(HERE / "continuation_bridge.schema.json"),
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as error:
        errors.append(f"schema: {error.message}")
    try:
        basis = bridge["selection_basis"]
        target = basis["target_box"]
        target_path = safe_repository_path(REPOSITORY, target["path"])
        if target_path != BOX_PATH.resolve():
            errors.append("bridge target is not the canonical positive box")
        if target["sha256"] != sha256_file(BOX_PATH):
            errors.append("bridge target-box hash mismatch")
        if target["box_id"] != box["box_id"]:
            errors.append("bridge target-box identifier mismatch")
        tag_commit = git_output(
            REPOSITORY, "rev-parse", f"{basis['repository_tag']}^{{commit}}")
        if tag_commit != basis["repository_commit"]:
            errors.append("bridge selection tag does not resolve to its frozen commit")
        frozen_target = subprocess.run(
            ["git", "-C", str(REPOSITORY), "show",
             f"{basis['repository_commit']}:{target['path']}"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        if sha256_bytes(frozen_target) != target["sha256"]:
            errors.append("bridge selection-commit target-box blob hash mismatch")
    except (KeyError, OSError, subprocess.SubprocessError) as error:
        errors.append(f"bridge selection-basis verification failed: {error}")
    return ("PASS" if not errors else "FAIL", errors)


def verify_local_graph_configuration(
        configuration: dict[str, Any], bridge: dict[str, Any]) -> tuple[str, list[str]]:
    errors = validate_local_graph_configuration(configuration)
    try:
        jsonschema.validate(
            configuration,
            load_json(HERE / "p2_local_graph.schema.json"),
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as error:
        errors.append(f"schema: {error.message}")
    try:
        basis = configuration["selection_basis"]
        selected_bridge = basis["continuation_bridge"]
        bridge_path = safe_repository_path(REPOSITORY, selected_bridge["path"])
        if bridge_path != BRIDGE_PATH.resolve():
            errors.append("local-graph configuration does not use the canonical bridge")
        if selected_bridge["sha256"] != sha256_file(BRIDGE_PATH):
            errors.append("local-graph configuration bridge hash mismatch")
        tag_commit = git_output(
            REPOSITORY, "rev-parse", f"{basis['repository_tag']}^{{commit}}")
        if tag_commit != basis["repository_commit"]:
            errors.append(
                "local-graph selection tag does not resolve to its frozen commit")
        if bridge.get("bridge_id") != "vdp-core-to-positive-bridge-v1":
            errors.append("unexpected continuation bridge identifier")
    except (KeyError, OSError, subprocess.SubprocessError) as error:
        errors.append(f"local-graph configuration verification failed: {error}")
    return ("PASS" if not errors else "FAIL", errors)


def verify_p2a_prerequisite(
        certificate: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    errors = schema_errors(certificate) + semantic_errors(certificate, REPOSITORY)
    by_id = {
        item.get("id"): item.get("status")
        for item in certificate.get("obligations", [])
        if isinstance(item, dict)
    }
    expected = {
        "scope": "V2_LOCAL_GRAPH_KERNEL",
        "integrity_status": "PASS",
        "mathematical_status": "PASS",
        "final_status": "INCONCLUSIVE",
        "claim_bearing": False,
    }
    for key, value in expected.items():
        if certificate.get(key) != value:
            errors.append(
                f"P2a prerequisite {key}={certificate.get(key)!r}, expected {value!r}")
    for identifier in ("V2.WU.FRAME_BLOCK", "V2.WU.COARSE_GRAPH"):
        if by_id.get(identifier) != "PASS":
            errors.append(f"P2a prerequisite {identifier} is not PASS")
    detail = {
        "configuration_path":
            "validation/rigorous/config/vdp_p2_local_graph_v1.json",
        "configuration_sha256": sha256_file(LOCAL_GRAPH_CONFIG_PATH),
        "certificate_path":
            "validation/rigorous/results/vdp_bridge_v1_p2a_local_graph.json",
        "certificate_sha256": sha256_file(P2A_CERTIFICATE_PATH),
        "certificate_scope": certificate.get("scope"),
        "source_commit": certificate.get("source_revision", {}).get("commit"),
        "integrity_status": certificate.get("integrity_status"),
        "mathematical_status": certificate.get("mathematical_status"),
        "final_status": certificate.get("final_status"),
        "claim_bearing": certificate.get("claim_bearing"),
    }
    return ("PASS" if not errors else "FAIL", errors, detail)


def verify_p2b0_prerequisite(
        certificate: dict[str, Any],
        p2_jets_configuration: dict[str, Any]) -> \
        tuple[str, list[str], dict[str, Any]]:
    errors = schema_errors(certificate) + semantic_errors(certificate, REPOSITORY)
    by_id = {
        item.get("id"): item.get("status")
        for item in certificate.get("obligations", [])
        if isinstance(item, dict)
    }
    expected = {
        "scope": "V2_H10_C01_KERNEL",
        "integrity_status": "PASS",
        "mathematical_status": "PASS",
        "final_status": "INCONCLUSIVE",
        "claim_bearing": False,
    }
    for key, value in expected.items():
        if certificate.get(key) != value:
            errors.append(
                f"P2b0 prerequisite {key}={certificate.get(key)!r}, "
                f"expected {value!r}")
    for identifier in ("V2.WU.H10_C0_TUBE", "V2.WU.H10_C1_TUBE"):
        if by_id.get(identifier) != "PASS":
            errors.append(f"P2b0 prerequisite {identifier} is not PASS")
    errors.extend(validate_p2b0_true_tube_implication(
        p2_jets_configuration, certificate))
    detail = {
        "configuration_path":
            "validation/rigorous/config/vdp_p2_h10_c01_v1.json",
        "configuration_sha256": sha256_file(H10_C01_CONFIG_PATH),
        "certificate_path":
            "validation/rigorous/results/vdp_bridge_v1_p2b_h10_c01.json",
        "certificate_sha256": sha256_file(P2B0_CERTIFICATE_PATH),
        "certificate_scope": certificate.get("scope"),
        "source_commit": certificate.get("source_revision", {}).get("commit"),
        "integrity_status": certificate.get("integrity_status"),
        "mathematical_status": certificate.get("mathematical_status"),
        "final_status": certificate.get("final_status"),
        "claim_bearing": certificate.get("claim_bearing"),
    }
    return ("PASS" if not errors else "FAIL", errors, detail)


def verify_p2_jets_configuration(
        configuration: dict[str, Any], bridge: dict[str, Any],
        p2a_configuration: dict[str, Any], p2a_certificate: dict[str, Any],
        p2b0_configuration: dict[str, Any],
        p2b0_certificate: dict[str, Any]) -> tuple[str, list[str]]:
    errors = validate_p2_jets_configuration(configuration)
    try:
        jsonschema.validate(
            configuration,
            load_json(HERE / "p2_jets.schema.json"),
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as error:
        errors.append(f"schema: {error.message}")
    try:
        basis = configuration["selection_basis"]
        tag_commit = git_output(
            REPOSITORY, "rev-parse", f"{basis['repository_tag']}^{{commit}}")
        if tag_commit != basis["repository_commit"]:
            errors.append("P2 jets selection tag does not resolve to its commit")
        canonical = {
            "continuation_bridge": BRIDGE_PATH,
            "p2a_configuration": LOCAL_GRAPH_CONFIG_PATH,
            "p2a_certificate": P2A_CERTIFICATE_PATH,
            "p2b0_configuration": H10_C01_CONFIG_PATH,
            "p2b0_certificate": P2B0_CERTIFICATE_PATH,
            "design_scout": HERE / "design" / "p2b_jets_scout.cpp",
        }
        for name, path in canonical.items():
            selected = basis[name]
            if safe_repository_path(REPOSITORY, selected["path"]) != path.resolve():
                errors.append(f"P2 jets {name} is not canonical")
            if selected["sha256"] != sha256_file(path):
                errors.append(f"P2 jets current {name} hash mismatch")
            frozen_blob = subprocess.run(
                ["git", "-C", str(REPOSITORY), "show",
                 f"{basis['repository_commit']}:{selected['path']}"],
                check=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).stdout
            if selected["sha256"] != sha256_bytes(frozen_blob):
                errors.append(f"P2 jets frozen {name} blob hash mismatch")
        if bridge.get("bridge_id") != "vdp-core-to-positive-bridge-v1":
            errors.append("P2 jets bridge identifier changed")
        if p2a_configuration.get("configuration_id") != \
                "vdp-p2-local-graph-v1":
            errors.append("P2 jets P2a configuration identifier changed")
        if p2a_certificate.get("scope") != "V2_LOCAL_GRAPH_KERNEL":
            errors.append("P2 jets P2a prerequisite certificate scope changed")
        if p2b0_configuration.get("configuration_id") != \
                "vdp-p2-h10-c01-v1":
            errors.append("P2 jets P2b0 configuration identifier changed")
        if p2b0_certificate.get("scope") != "V2_H10_C01_KERNEL":
            errors.append("P2 jets P2b0 prerequisite certificate scope changed")
    except (KeyError, OSError, subprocess.SubprocessError) as error:
        errors.append(f"P2 jets configuration verification failed: {error}")
    return ("PASS" if not errors else "FAIL", errors)


def verify_p2_kato_configuration(
        configuration: dict[str, Any], bridge: dict[str, Any],
        p2b_certificate: dict[str, Any],
        flagship_repository: Path | None) -> tuple[str, list[str]]:
    """Verify the frozen local and read-only flagship inputs for P2bK."""

    errors = validate_p2_kato_configuration(configuration)
    try:
        jsonschema.validate(
            configuration,
            load_json(HERE / "p2_kato.schema.json"),
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as error:
        errors.append(f"schema: {error.message}")

    try:
        basis = configuration["selection_basis"]
        tag_commit = git_output(
            REPOSITORY, "rev-parse", f"{basis['repository_tag']}^{{commit}}")
        if tag_commit != basis["repository_commit"]:
            errors.append("P2 Kato selection tag does not resolve to its commit")

        local_inputs = {
            "continuation_bridge": BRIDGE_PATH,
            "p2a_configuration": LOCAL_GRAPH_CONFIG_PATH,
            "p2a_certificate": P2A_CERTIFICATE_PATH,
            "p2b_configuration": P2_JETS_CONFIG_PATH,
            "p2b_certificate": P2B_JETS_CERTIFICATE_PATH,
            "core_source_import": REPOSITORY / "van-der-pol" /
                "CENTRAL_CORE_IMPORT.md",
            "v2_source_definition": REPOSITORY / "van-der-pol" /
                "CENTRAL_CONTINUATION.md",
            "design_scout": HERE / "design" / "p2b_kato_scout.cpp",
        }
        for name, path in local_inputs.items():
            selected = basis[name]
            expected_path = path.resolve()
            expected_relative = str(expected_path.relative_to(REPOSITORY.resolve()))
            if safe_repository_path(REPOSITORY, selected["path"]) != expected_path:
                errors.append(f"P2 Kato {name} is not canonical")
            if selected["path"] != expected_relative:
                errors.append(f"P2 Kato {name} path spelling changed")
            if selected["sha256"] != sha256_file(expected_path):
                errors.append(f"P2 Kato current {name} hash mismatch")
            frozen_blob = subprocess.run(
                ["git", "-C", str(REPOSITORY), "show",
                 f"{basis['repository_commit']}:{selected['path']}"],
                check=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).stdout
            if selected["sha256"] != sha256_bytes(frozen_blob):
                errors.append(f"P2 Kato frozen {name} blob hash mismatch")

        if bridge.get("bridge_id") != "vdp-core-to-positive-bridge-v1":
            errors.append("P2 Kato bridge identifier changed")
        if p2b_certificate.get("scope") != "V2_P2_JETS_KERNEL":
            errors.append("P2 Kato P2b prerequisite certificate scope changed")

        flagship_lock = load_json(FLAGSHIP_LOCK_PATH)
        if flagship_repository is None:
            errors.append(
                "P2 Kato validation requires the frozen flagship repository")
        else:
            flagship_repository = flagship_repository.resolve()
            for name in ("flagship_core_manuscript",
                         "flagship_core_certificate"):
                selected = basis[name]
                if selected["commit"] != flagship_lock["commit"]:
                    errors.append(f"P2 Kato {name} commit differs from flagship lock")
                if flagship_lock["files"].get(selected["path"]) != \
                        selected["sha256"]:
                    errors.append(f"P2 Kato {name} differs from flagship lock")
                frozen_blob = subprocess.run(
                    ["git", "-C", str(flagship_repository), "show",
                     f"{selected['commit']}:{selected['path']}"],
                    check=True, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE).stdout
                if selected["sha256"] != sha256_bytes(frozen_blob):
                    errors.append(
                        f"P2 Kato read-only flagship {name} hash mismatch")
    except (KeyError, OSError, ValueError,
            subprocess.SubprocessError) as error:
        errors.append(f"P2 Kato configuration verification failed: {error}")
    return ("PASS" if not errors else "FAIL", errors)


def verify_p2b_jets_prerequisite(
        certificate: dict[str, Any]) -> tuple[
            str, list[str], dict[str, Any]]:
    """Recursively verify the immutable P2b mixed-jet certificate."""

    errors = schema_errors(certificate) + semantic_errors(certificate, REPOSITORY)
    by_id = {
        item.get("id"): item.get("status")
        for item in certificate.get("obligations", [])
        if isinstance(item, dict)
    }
    expected = {
        "scope": "V2_P2_JETS_KERNEL",
        "integrity_status": "PASS",
        "mathematical_status": "PASS",
        "final_status": "INCONCLUSIVE",
        "claim_bearing": False,
    }
    for key, value in expected.items():
        if certificate.get(key) != value:
            errors.append(
                f"P2b jets prerequisite {key}={certificate.get(key)!r}, "
                f"expected {value!r}")
    required_obligations = (
        "P2.JETS.COEFFICIENTS",
        "V2.WU.STATE_C23",
        "V2.WU.MIXED_JETS",
        "V2.WU.WEIGHTED_HALF_ORBITS",
        "V2.WU.JETS",
        "V2.WU_GRAPH",
    )
    for identifier in required_obligations:
        if by_id.get(identifier) != "PASS":
            errors.append(
                f"P2b jets prerequisite {identifier} is not PASS")
    expected_replay = {
        "status": "PENDING_REQUIRED",
        "required_distinct_machines": 2,
        "observed_distinct_machines": 1,
    }
    if certificate.get("independent_replay") != expected_replay:
        errors.append(
            "P2b jets prerequisite independent-replay record changed")
    if certificate.get("continuation_bridge", {}).get("variables") != \
            load_json(BRIDGE_PATH).get("variables"):
        errors.append("P2b jets prerequisite uses a different bridge")
    expected_configuration = {
        "path": "validation/rigorous/config/vdp_p2_jets_v1.json",
        "sha256": sha256_file(P2_JETS_CONFIG_PATH),
        "configuration_id": "vdp-p2-jets-v1",
    }
    if certificate.get("p2_jets_configuration") != expected_configuration:
        errors.append("P2b jets prerequisite configuration record changed")
    detail = {
        "configuration_path":
            "validation/rigorous/config/vdp_p2_jets_v1.json",
        "configuration_sha256": sha256_file(P2_JETS_CONFIG_PATH),
        "certificate_path":
            "validation/rigorous/results/vdp_bridge_v1_p2b_jets.json",
        "certificate_sha256": sha256_file(P2B_JETS_CERTIFICATE_PATH),
        "certificate_scope": certificate.get("scope"),
        "source_commit": certificate.get("source_revision", {}).get("commit"),
        "integrity_status": certificate.get("integrity_status"),
        "mathematical_status": certificate.get("mathematical_status"),
        "final_status": certificate.get("final_status"),
        "claim_bearing": certificate.get("claim_bearing"),
    }
    return ("PASS" if not errors else "FAIL", errors, detail)


def verify_h10_c01_configuration(
        configuration: dict[str, Any], bridge: dict[str, Any],
        p2a_configuration: dict[str, Any], p2a_certificate: dict[str, Any],
        flagship_lock: dict[str, Any]) -> tuple[str, list[str]]:
    errors = validate_h10_c01_configuration(configuration)
    try:
        jsonschema.validate(
            configuration,
            load_json(HERE / "p2_h10_c01.schema.json"),
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as error:
        errors.append(f"schema: {error.message}")
    try:
        basis = configuration["selection_basis"]
        tag_commit = git_output(
            REPOSITORY, "rev-parse", f"{basis['repository_tag']}^{{commit}}")
        if tag_commit != basis["repository_commit"]:
            errors.append("H10 C0/C1 selection tag does not resolve to its commit")
        canonical = {
            "continuation_bridge": BRIDGE_PATH,
            "p2a_configuration": LOCAL_GRAPH_CONFIG_PATH,
            "p2a_certificate": P2A_CERTIFICATE_PATH,
        }
        for name, path in canonical.items():
            selected = basis[name]
            if safe_repository_path(REPOSITORY, selected["path"]) != path.resolve():
                errors.append(f"H10 C0/C1 {name} is not canonical")
            if selected["sha256"] != sha256_file(path):
                errors.append(f"H10 C0/C1 current {name} hash mismatch")
            frozen_blob = subprocess.run(
                ["git", "-C", str(REPOSITORY), "show",
                 f"{basis['repository_commit']}:{selected['path']}"],
                check=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).stdout
            if selected["sha256"] != sha256_bytes(frozen_blob):
                errors.append(f"H10 C0/C1 frozen {name} blob hash mismatch")
        if bridge.get("bridge_id") != "vdp-core-to-positive-bridge-v1":
            errors.append("H10 C0/C1 bridge identifier changed")
        if p2a_configuration.get("configuration_id") != \
                "vdp-p2-local-graph-v1":
            errors.append("H10 C0/C1 P2a configuration identifier changed")
        if p2a_certificate.get("scope") != "V2_LOCAL_GRAPH_KERNEL":
            errors.append("H10 C0/C1 prerequisite certificate scope changed")

        center = configuration["imported_core_center"]
        if center["commit"] != flagship_lock["commit"]:
            errors.append("H10 C0/C1 center commit differs from flagship lock")
        for name in ("generator", "term_table", "reference_probe",
                     "reference_readme", "source_certificate"):
            item = center[name]
            if flagship_lock["files"].get(item["path"]) != item["sha256"]:
                errors.append(
                    f"H10 C0/C1 imported {name} differs from flagship lock")
    except (KeyError, OSError, subprocess.SubprocessError) as error:
        errors.append(f"H10 C0/C1 configuration verification failed: {error}")
    return ("PASS" if not errors else "FAIL", errors)


def verify_flagship(repository: Path | None) -> tuple[str, dict[str, Any]]:
    lock = load_json(FLAGSHIP_LOCK_PATH)
    detail: dict[str, Any] = {
        "lock_sha256": sha256_file(FLAGSHIP_LOCK_PATH),
        "commit": lock["commit"],
        "tree": lock["tree"],
        "access": "git-object-read-only",
    }
    if repository is None:
        detail["reason"] = "--flagship-repository was not supplied"
        return "INCONCLUSIVE", detail
    repository = repository.resolve()
    errors: list[str] = []
    try:
        observed_tree = git_output(repository, "rev-parse", f"{lock['commit']}^{{tree}}")
        if observed_tree != lock["tree"]:
            errors.append("frozen flagship tree mismatch")
        for relative, expected_hash in lock["files"].items():
            result = subprocess.run(
                ["git", "-C", str(repository), "show", f"{lock['commit']}:{relative}"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if sha256_bytes(result.stdout) != expected_hash:
                errors.append(f"frozen flagship object hash mismatch: {relative}")
    except (OSError, subprocess.SubprocessError) as error:
        errors.append(f"cannot read frozen flagship objects: {error}")
    detail["repository_path"] = str(repository)
    detail["errors"] = errors
    return ("PASS" if not errors else "FAIL", detail)


def run_h10_center_audit(
        flagship_repository: Path,
        configuration: dict[str, Any]) -> tuple[
            dict[str, Any], dict[str, str], dict[str, Any]]:
    center = configuration["imported_core_center"]
    protocol = configuration["exact_center_audit"]
    command = [
        sys.executable, "-B", str(HERE / "audit_h10_center.py"),
        "--flagship-repository", str(flagship_repository.resolve()),
        "--commit", center["commit"],
        "--generator-path", center["generator"]["path"],
        "--generator-sha256", center["generator"]["sha256"],
        "--header-path", center["term_table"]["path"],
        "--header-sha256", center["term_table"]["sha256"],
        "--h1-term-count", str(protocol["h1_term_count"]),
        "--h2-term-count", str(protocol["h2_term_count"]),
        "--defect1-term-count", str(protocol["defect1_term_count"]),
        "--defect2-term-count", str(protocol["defect2_term_count"]),
        "--h-min-degree", str(protocol["center_minimum_total_degree"]),
        "--h-max-degree", str(protocol["center_maximum_total_degree"]),
        "--defect-min-degree", str(protocol["defect_minimum_total_degree"]),
        "--defect-max-degree", str(protocol["defect_maximum_total_degree"]),
        "--timeout-seconds", "900",
    ]
    environment = os.environ.copy()
    environment.update({
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "LC_ALL": "C.UTF-8",
    })
    executed = subprocess.run(
        command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env=environment, timeout=960)
    if executed.returncode not in (0, 1, 2):
        raise RuntimeError(
            f"H10 exact-center audit terminated with unexpected code "
            f"{executed.returncode}:\n{executed.stderr}")
    try:
        audit = json.loads(executed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"H10 exact-center audit emitted invalid JSON: {error}") from error
    expected_exit = {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 2}.get(
        audit.get("status"))
    if expected_exit != executed.returncode:
        raise RuntimeError("H10 exact-center audit status/exit mismatch")
    if audit.get("commit") != center["commit"]:
        raise RuntimeError("H10 exact-center audit commit mismatch")
    logs = {
        "h10_audit_stdout_sha256": sha256_bytes(executed.stdout.encode()),
        "h10_audit_stderr_sha256": sha256_bytes(executed.stderr.encode()),
    }
    execution = {
        "audit_argv": command,
        "audit_argv_sha256": sha256_bytes(
            json.dumps(command, separators=(",", ":")).encode()),
        "audit_exit_code": executed.returncode,
        "audit_source_sha256": sha256_file(HERE / "audit_h10_center.py"),
    }
    return audit, logs, execution


def run_kato_exact_audit() -> tuple[
        dict[str, Any], dict[str, str], dict[str, Any]]:
    """Run and preserve the deterministic exact-symbolic P2bK audit."""

    command = [sys.executable, "-B", str(HERE / "audit_kato_exact.py")]
    environment = os.environ.copy()
    environment.update({
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "LC_ALL": "C.UTF-8",
        "PYTHONHASHSEED": "0",
    })
    with tempfile.TemporaryDirectory(
            prefix="rfsn-kato-empty-pycache-") as pycache:
        # The SymPy tree hash intentionally excludes bytecode.  Redirecting
        # cache lookup to a fresh empty tree makes the audit consume the
        # hash-bound sources instead of a pre-existing package __pycache__.
        environment["PYTHONPYCACHEPREFIX"] = pycache
        executed = subprocess.run(
            command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=environment, timeout=960)
    if executed.returncode not in (0, 1):
        raise RuntimeError(
            "P2 Kato exact audit terminated with unexpected code "
            f"{executed.returncode}:\n{executed.stderr}")
    try:
        audit = json.loads(executed.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"P2 Kato exact audit emitted invalid JSON: {error}") from error
    if not isinstance(audit, dict):
        raise RuntimeError("P2 Kato exact audit did not emit a JSON object")
    expected_exit = {"PASS": 0, "FAIL": 1}.get(audit.get("status"))
    if expected_exit != executed.returncode:
        raise RuntimeError("P2 Kato exact audit status/exit mismatch")
    if audit.get("schema_version") != \
            "rfsn-vdp-p2-kato-exact-audit/1":
        raise RuntimeError("P2 Kato exact audit schema version mismatch")
    backend = audit.get("backend")
    if not isinstance(backend, dict) or backend.get("name") != "sympy":
        raise RuntimeError("P2 Kato exact audit backend record changed")
    checks = audit.get("checks")
    if not isinstance(checks, dict) or not checks or not all(
            isinstance(name, str) and isinstance(value, bool)
            for name, value in checks.items()):
        raise RuntimeError("P2 Kato exact audit check map is invalid")
    if audit.get("status") == "PASS":
        if audit.get("method") != "exact-symbolic-identities-no-sampling":
            raise RuntimeError("P2 Kato exact audit method changed")
        if not all(checks.values()):
            raise RuntimeError("P2 Kato exact audit PASS contains a false check")
    logs = {
        "kato_audit_stdout_sha256": sha256_bytes(executed.stdout.encode()),
        "kato_audit_stderr_sha256": sha256_bytes(executed.stderr.encode()),
    }
    execution = {
        "audit_source_sha256": sha256_file(HERE / "audit_kato_exact.py"),
        "audit_argv": command,
        "audit_argv_sha256": sha256_bytes(
            json.dumps(command, separators=(",", ":")).encode()),
        "audit_exit_code": executed.returncode,
        "audit_stdout": executed.stdout,
    }
    return audit, logs, execution


def verify_exact_symbolic_backend(
        dependency: dict[str, Any]) -> tuple[str, dict[str, Any], list[str]]:
    """Verify the Python executable and cache-free SymPy source tree."""

    errors: list[str] = []
    try:
        frozen = dependency["exact_symbolic_backend"]
        observed = observe_exact_symbolic_backend()
        expected_observation = {
            "python": frozen["python"],
            "sympy": {
                "version": frozen["sympy"]["version"],
                "source_tree": frozen["sympy"]["source_tree"],
            },
            "bytecode_policy": frozen["bytecode_policy"],
        }
        comparable_observation = {
            "python": observed["python"],
            "sympy": {
                "version": observed["sympy"]["version"],
                "source_tree": observed["sympy"]["source_tree"],
            },
            "bytecode_policy": observed["bytecode_policy"],
        }
        if comparable_observation != expected_observation:
            errors.append(
                "exact symbolic Python/SymPy backend differs from the frozen lock")
        detail = {
            **observed,
            "lock_scope": frozen.get("scope"),
            "status": "PASS" if not errors else "FAIL",
            "errors": errors,
        }
    except (ImportError, KeyError, OSError, ValueError,
            subprocess.SubprocessError) as error:
        errors.append(f"exact symbolic backend query failed: {error}")
        detail = {"status": "FAIL", "errors": errors}
    return detail["status"], detail, errors


def parse_cache(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line or line.startswith(("#", "//")) or "=" not in line:
            continue
        key_with_type, value = line.split("=", 1)
        key = key_with_type.split(":", 1)[0]
        values[key] = value
    return values


def resolve_libraries(tokens: list[str]) -> dict[str, Path]:
    directories = [Path(token[2:]).resolve() for token in tokens if token.startswith("-L")]
    names = [token[2:] for token in tokens if token.startswith("-l")]
    result: dict[str, Path] = {}
    for name in names:
        for directory in directories:
            candidate = directory / f"lib{name}.a"
            if candidate.is_file():
                result[f"lib{name}.a"] = candidate
                break
    return result


def verify_toolchain(capd_source: Path, capd_config: Path,
                     dependency: dict[str, Any]) -> tuple[str, dict[str, Any], list[str], list[str]]:
    capd_source = capd_source.resolve()
    capd_config = capd_config.resolve()
    compiler = Path(dependency["compiler"]["executable"])
    fatal: list[str] = []
    incomplete: list[str] = []
    try:
        compiler_hash = sha256_file(compiler)
        compiler_version = run_checked([str(compiler), "--version"]).stdout.splitlines()[0]
        if compiler_hash != dependency["compiler"]["sha256"]:
            fatal.append("compiler hash mismatch")
        if compiler_version != dependency["compiler"]["first_line"]:
            fatal.append("compiler version mismatch")
        capd_head = git_output(capd_source, "rev-parse", "HEAD")
        capd_tree = git_output(capd_source, "rev-parse", "HEAD^{tree}")
        capd_dirty = bool(git_output(capd_source, "status", "--porcelain"))
        if capd_head != dependency["capd"]["source_commit"]:
            fatal.append("CAPD source commit mismatch")
        if capd_tree != dependency["capd"]["source_tree"]:
            fatal.append("CAPD source tree mismatch")
        if capd_dirty:
            fatal.append("CAPD source checkout is dirty")
        cflags_text = run_checked([str(capd_config), "--cflags"]).stdout.strip()
        libs_text = run_checked([str(capd_config), "--libs"]).stdout.strip()
        config_version = run_checked([str(capd_config), "--version"]).stdout.strip()
        if config_version != dependency["capd"]["capd_config_reported_version"]:
            fatal.append("capd-config reported-version mismatch")
    except (OSError, subprocess.SubprocessError, IndexError) as error:
        fatal.append(f"toolchain query failed: {error}")
        compiler_hash = ""
        compiler_version = ""
        capd_head = ""
        capd_tree = ""
        capd_dirty = True
        cflags_text = ""
        libs_text = ""
        config_version = ""

    cflags = shlex.split(cflags_text)
    libs = shlex.split(libs_text)
    libraries = resolve_libraries(libs)
    if "-D__USE_FILIB__" not in cflags:
        fatal.append("capd-config does not select the FILIB backend")
    forbidden_flags = dependency["compiler"]["forbidden_flags"]
    for forbidden in forbidden_flags:
        if forbidden in cflags:
            fatal.append(f"forbidden CAPD flag present: {forbidden}")
    for required in ("libcapd.a", "libfilib.a"):
        if required not in libraries:
            fatal.append(f"linked archive not resolved: {required}")

    build_directory = capd_config.resolve().parents[1]
    if capd_source not in capd_config.parents:
        fatal.append("capd-config is not inside the pinned CAPD source/build tree")
    cache_path = build_directory / "CMakeCache.txt"
    cache = parse_cache(cache_path)
    release_flags = shlex.split(cache.get("CMAKE_CXX_FLAGS_RELEASE", ""))
    strict_flags = dependency["compiler"]["required_probe_flags"]
    for forbidden in forbidden_flags:
        if forbidden in release_flags:
            fatal.append(f"forbidden CMake release flag present: {forbidden}")
    missing_library_flags = [flag for flag in strict_flags if flag not in release_flags]
    if missing_library_flags:
        incomplete.append(
            "CAPD/FILIB archives were not built with all strict flags: " +
            ", ".join(missing_library_flags))
    expected_cache = {
        "CMAKE_BUILD_TYPE": "Release",
        "CAPD_INTERVAL_TYPE": "FILIB",
        "CAPD_ENABLE_MULTIPRECISION": "OFF",
        "CAPD_BUILD_TESTS": "OFF",
        "CAPD_BUILD_EXAMPLES": "OFF",
        "CMAKE_EXPORT_COMPILE_COMMANDS": "ON",
    }
    for key, expected in expected_cache.items():
        if cache.get(key) != expected:
            fatal.append(f"CMake cache mismatch: {key}={cache.get(key)!r}, expected {expected!r}")
    cache_compiler = Path(cache.get("CMAKE_CXX_COMPILER", "/missing"))
    try:
        if cache_compiler.resolve() != compiler.resolve():
            fatal.append("CMake CXX compiler does not resolve to the locked compiler")
    except OSError as error:
        fatal.append(f"cannot resolve CMake CXX compiler: {error}")
    cmake_path = Path(cache.get("CMAKE_COMMAND", "/missing"))
    make_path = Path(cache.get("CMAKE_MAKE_PROGRAM", "/missing"))
    build_programs: dict[str, Any] = {}
    for name, path, expected_hash in (
            ("cmake", cmake_path, dependency["cmake"]["reference_sha256"]),
            ("make", make_path, dependency["build_tool"]["sha256"])):
        try:
            observed_hash = sha256_file(path)
            build_programs[name] = {
                "path": str(path.resolve()), "sha256": observed_hash}
            if observed_hash != expected_hash:
                fatal.append(f"{name} executable hash mismatch")
        except OSError as error:
            fatal.append(f"cannot hash {name} executable: {error}")
    try:
        cmake_version_line = run_checked([str(cmake_path), "--version"]).stdout.splitlines()[0]
        build_programs.setdefault("cmake", {})["version_first_line"] = cmake_version_line
        if cmake_version_line != f"cmake version {dependency['cmake']['reference_version']}":
            fatal.append("CMake version mismatch")
    except (OSError, subprocess.SubprocessError, IndexError) as error:
        fatal.append(f"cannot query CMake version: {error}")

    compile_commands_path = build_directory / "compile_commands.json"
    compile_commands_hash: str | None = None
    compile_command_summary: dict[str, Any] = {
        "entry_count": 0,
        "entries_with_all_strict_flags": 0,
        "entries_with_filib_selector": 0,
        "compiler_paths": [],
    }
    if not compile_commands_path.is_file():
        incomplete.append("compile_commands.json is missing")
    else:
        compile_commands_hash = sha256_file(compile_commands_path)
        try:
            entries = json.loads(compile_commands_path.read_text(encoding="utf-8"))
            if not isinstance(entries, list) or not entries:
                raise ValueError("compile command list is empty")
            compiler_paths: set[str] = set()
            strict_count = 0
            filib_count = 0
            for index, entry in enumerate(entries):
                tokens = entry.get("arguments")
                if tokens is None:
                    tokens = shlex.split(entry["command"])
                if not isinstance(tokens, list) or not tokens:
                    raise ValueError(f"entry {index} has no compiler argv")
                entry_compiler = Path(tokens[0]).resolve()
                compiler_paths.add(str(entry_compiler))
                if entry_compiler != compiler.resolve():
                    fatal.append(f"compile_commands entry {index} uses an unlocked compiler")
                if all(flag in tokens for flag in strict_flags):
                    strict_count += 1
                else:
                    missing = [flag for flag in strict_flags if flag not in tokens]
                    incomplete.append(
                        f"compile_commands entry {index} lacks strict flags: {', '.join(missing)}")
                present_forbidden = [flag for flag in forbidden_flags if flag in tokens]
                if present_forbidden:
                    fatal.append(
                        f"compile_commands entry {index} has forbidden flags: " +
                        ", ".join(present_forbidden))
                if "-D__USE_FILIB__" in tokens:
                    filib_count += 1
                source_file = Path(entry["file"]).resolve()
                if capd_source != source_file and capd_source not in source_file.parents:
                    fatal.append(f"compile_commands entry {index} source escapes pinned tree")
                entry_directory = Path(entry["directory"]).resolve()
                if build_directory != entry_directory and build_directory not in entry_directory.parents:
                    fatal.append(f"compile_commands entry {index} directory escapes build tree")
            compile_command_summary = {
                "entry_count": len(entries),
                "entries_with_all_strict_flags": strict_count,
                "entries_with_filib_selector": filib_count,
                "compiler_paths": sorted(compiler_paths),
            }
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            fatal.append(f"invalid compile_commands.json: {error}")

    for name, path in libraries.items():
        if build_directory != path and build_directory not in path.parents:
            fatal.append(f"linked archive escapes the bound build tree: {name}")
    reference_config = Path(dependency["capd"]["reference_capd_config"])
    if capd_config == reference_config.resolve():
        for name, expected_hash in dependency["capd"]["reference_libraries"].items():
            if name in libraries and sha256_file(libraries[name]) != expected_hash:
                fatal.append(f"reference archive hash mismatch: {name}")
    strict_status = "PASS" if not fatal and not incomplete else (
        "FAIL" if fatal else "INCONCLUSIVE")
    overall = "FAIL" if fatal else ("INCONCLUSIVE" if incomplete else "PASS")
    library_records = {
        name: {"path": str(path), "sha256": sha256_file(path)}
        for name, path in libraries.items()
    }
    detail = {
        "status": overall,
        "strict_library_build_status": strict_status,
        "dependency_lock_sha256": sha256_file(DEPENDENCY_LOCK_PATH),
        "compiler": {
            "path": str(compiler),
            "version_first_line": compiler_version,
            "sha256": compiler_hash,
        },
        "build_programs": build_programs,
        "capd": {
            "source_path": str(capd_source.resolve()),
            "source_commit": capd_head,
            "source_tree": capd_tree,
            "source_dirty": capd_dirty,
            "config_path": str(capd_config.resolve()),
            "config_version": config_version,
            "cflags": cflags,
            "libs": shlex.split(libs_text),
            "cmake_cache_sha256": sha256_file(cache_path) if cache_path.is_file() else None,
            "cmake_release_flags": release_flags,
            "cmake_configuration": {
                key: cache.get(key) for key in (*expected_cache, "CMAKE_CXX_COMPILER")
            },
            "compile_commands_sha256": compile_commands_hash,
            "compile_commands_scan": compile_command_summary,
            "linked_archives": library_records,
        },
        "fatal_errors": fatal,
        "incomplete_checks": incomplete,
    }
    return overall, detail, cflags, libs


def compile_and_run(
        scope: str, cflags: list[str], libs: list[str],
        dependency: dict[str, Any], box: dict[str, Any],
        bridge: dict[str, Any] | None = None,
        local_graph_configuration: dict[str, Any] | None = None,
        h10_c01_configuration: dict[str, Any] | None = None,
        p2_jets_configuration: dict[str, Any] | None = None,
        p2_kato_configuration: dict[str, Any] | None = None,
        p2b_jets_certificate: dict[str, Any] | None = None,
        flagship_repository: Path | None = None,
        ) -> tuple[dict[str, Any], dict[str, str], dict[str, Any]]:
    source_names = {
        "preflight": "rounding_self_test.cpp",
        "kernel": "vdp_parameter_box_probe.cpp",
        "local-graph": "vdp_local_graph_probe.cpp",
        "h10-c01": "vdp_h10_c01_probe.cpp",
        "p2-jets": "vdp_p2_jets_probe.cpp",
        "p2-kato": "vdp_p2_kato_probe.cpp",
    }
    source = HERE / "src" / source_names[scope]
    compiler = dependency["compiler"]["executable"]
    strict_flags = dependency["compiler"]["required_probe_flags"]
    environment = os.environ.copy()
    environment.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "LC_ALL": "C.UTF-8"})
    with tempfile.TemporaryDirectory(prefix="rfsn-rigorous-") as temporary:
        binary = Path(temporary) / "probe"
        extra_compile_arguments: list[str] = []
        imported_header: dict[str, Any] | None = None
        if scope == "h10-c01":
            if h10_c01_configuration is None or flagship_repository is None:
                raise RuntimeError("H10 C0/C1 scope lacks its frozen inputs")
            center = h10_c01_configuration["imported_core_center"]
            term_table = center["term_table"]
            result = subprocess.run(
                ["git", "-C", str(flagship_repository.resolve()), "show",
                 f"{center['commit']}:{term_table['path']}"],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            observed_hash = sha256_bytes(result.stdout)
            if observed_hash != term_table["sha256"]:
                raise RuntimeError("materialized H10 term-table hash mismatch")
            header = Path(temporary) / "unstable_graph_terms.hpp"
            header.write_bytes(result.stdout)
            extra_compile_arguments.extend(["-include", str(header.resolve())])
            imported_header = {
                "repository_commit": center["commit"],
                "repository_path": term_table["path"],
                "expected_sha256": term_table["sha256"],
                "materialized_sha256": sha256_file(header),
                "git_show_stdout_sha256": observed_hash,
                "git_show_stderr_sha256": sha256_bytes(result.stderr),
                "compiler_include_mode": "absolute-forced-include",
                "compiler_include_argument": str(header.resolve()),
            }
        command = [
            compiler,
            "-std=c++17",
            f"-I{HERE / 'include'}",
            *extra_compile_arguments,
            *cflags,
            *strict_flags,
            str(source),
            "-o",
            str(binary),
            *libs,
        ]
        compiled = subprocess.run(
            command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=environment, timeout=180)
        if compiled.returncode != 0:
            raise RuntimeError(
                f"probe compilation failed ({compiled.returncode}):\n{compiled.stderr}")
        run_command = [str(binary)]
        if scope == "kernel":
            run_command.extend(box_arguments(box))
        elif scope == "local-graph":
            if bridge is None or local_graph_configuration is None:
                raise RuntimeError("local-graph scope lacks its frozen inputs")
            run_command.extend(box_arguments(bridge))
            radius = local_graph_configuration["coordinate_block"][
                "unstable_radius"]
            run_command.extend([radius["numerator"], radius["denominator"]])
        elif scope == "h10-c01":
            if bridge is None or h10_c01_configuration is None:
                raise RuntimeError("H10 C0/C1 scope lacks its rational inputs")
            run_command.extend(box_arguments(bridge))
            radius = h10_c01_configuration["coordinate_domain"][
                "unstable_radius"]
            rho = h10_c01_configuration["tube_radii"]["value_euclidean"]
            eta = h10_c01_configuration["tube_radii"][
                "first_derivative_frobenius"]
            for value in (radius, rho, eta):
                run_command.extend([value["numerator"], value["denominator"]])
        elif scope == "p2-jets":
            if bridge is None or p2_jets_configuration is None:
                raise RuntimeError("P2 jets scope lacks its frozen inputs")
            run_command.extend(p2_jets_arguments(
                bridge, p2_jets_configuration))
        elif scope == "p2-kato":
            if bridge is None or p2_kato_configuration is None or \
                    p2b_jets_certificate is None:
                raise RuntimeError("P2 Kato scope lacks its frozen inputs")
            run_command.extend(p2_kato_arguments(
                bridge, p2_kato_configuration, p2b_jets_certificate))
        executed = subprocess.run(
            run_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=environment, timeout=120)
        if executed.returncode not in (0, 1, 2):
            raise RuntimeError(
                f"probe terminated with unexpected code {executed.returncode}:\n"
                f"{executed.stderr}")
        try:
            raw = json.loads(executed.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"probe emitted invalid JSON: {error}") from error
        logs = {
            "compile_stdout_sha256": sha256_bytes(compiled.stdout.encode()),
            "compile_stderr_sha256": sha256_bytes(compiled.stderr.encode()),
            "probe_stdout_sha256": sha256_bytes(executed.stdout.encode()),
            "probe_stderr_sha256": sha256_bytes(executed.stderr.encode()),
        }
        build = {
            "compile_argv": command,
            "compile_argv_sha256": sha256_bytes(
                json.dumps(command, separators=(",", ":")).encode()),
            "source_sha256": sha256_file(source),
            "binary_sha256": sha256_file(binary),
            "probe_argv": run_command,
            "probe_exit_code": executed.returncode,
        }
        if scope in ("p2-jets", "p2-kato"):
            # Preserve the exact machine output for a byte-level hash check.
            # The parsed raw_probe remains the semantic representation.
            build["probe_stdout"] = executed.stdout
        if imported_header is not None:
            build["imported_header"] = imported_header
        return raw, logs, build


def source_bindings() -> list[dict[str, str]]:
    bindings: list[dict[str, str]] = []
    for relative in BOUND_SOURCES:
        path = safe_repository_path(REPOSITORY, relative)
        if not path.is_file():
            raise FileNotFoundError(f"bound source is missing: {relative}")
        bindings.append({"path": relative, "sha256": sha256_file(path), "role": "rigorous-input"})
    return bindings


def make_obligation(identifier: str, status: str,
                    predicates: dict[str, str], **extra: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "id": identifier,
        "status": status,
        "predicate": predicates[identifier],
    }
    value.update(extra)
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scope", choices=(
            "preflight", "kernel", "local-graph", "h10-c01", "p2-jets",
            "p2-kato"))
    parser.add_argument("--capd-source", type=Path, required=True)
    parser.add_argument("--capd-config", type=Path, required=True)
    parser.add_argument("--flagship-repository", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--allow-dirty", action="store_true",
                        help="permit a hash-bound dirty development checkout")
    arguments = parser.parse_args()

    try:
        dependency = load_json(DEPENDENCY_LOCK_PATH)
        box = load_json(BOX_PATH)
        box_status, box_errors = verify_box(box)
        bridge: dict[str, Any] | None = None
        local_graph_configuration: dict[str, Any] | None = None
        h10_c01_configuration: dict[str, Any] | None = None
        p2_jets_configuration: dict[str, Any] | None = None
        p2_kato_configuration: dict[str, Any] | None = None
        p2a_certificate: dict[str, Any] | None = None
        p2b0_certificate: dict[str, Any] | None = None
        p2b_jets_certificate: dict[str, Any] | None = None
        bridge_status = "PASS"
        bridge_errors: list[str] = []
        local_graph_configuration_status = "PASS"
        local_graph_configuration_errors: list[str] = []
        h10_c01_configuration_status = "PASS"
        h10_c01_configuration_errors: list[str] = []
        p2_jets_configuration_status = "PASS"
        p2_jets_configuration_errors: list[str] = []
        p2_kato_configuration_status = "PASS"
        p2_kato_configuration_errors: list[str] = []
        p2a_prerequisite_status = "PASS"
        p2a_prerequisite_errors: list[str] = []
        p2a_prerequisite: dict[str, Any] | None = None
        p2b0_prerequisite_status = "PASS"
        p2b0_prerequisite_errors: list[str] = []
        p2b0_prerequisite: dict[str, Any] | None = None
        p2b_jets_prerequisite_status = "PASS"
        p2b_jets_prerequisite_errors: list[str] = []
        p2b_jets_prerequisite: dict[str, Any] | None = None
        if arguments.scope in (
                "local-graph", "h10-c01", "p2-jets", "p2-kato"):
            bridge = load_json(BRIDGE_PATH)
            local_graph_configuration = load_json(LOCAL_GRAPH_CONFIG_PATH)
            bridge_status, bridge_errors = verify_bridge(bridge, box)
            local_graph_configuration_status, \
                local_graph_configuration_errors = \
                verify_local_graph_configuration(
                    local_graph_configuration, bridge)
        if arguments.scope in ("h10-c01", "p2-jets"):
            h10_c01_configuration = load_json(H10_C01_CONFIG_PATH)
            p2a_certificate = load_json(P2A_CERTIFICATE_PATH)
            p2a_prerequisite_status, p2a_prerequisite_errors, \
                p2a_prerequisite = verify_p2a_prerequisite(p2a_certificate)
            if arguments.scope == "h10-c01":
                h10_c01_configuration_status, h10_c01_configuration_errors = \
                    verify_h10_c01_configuration(
                        h10_c01_configuration, bridge,
                        local_graph_configuration, p2a_certificate,
                        load_json(FLAGSHIP_LOCK_PATH))
        if arguments.scope == "p2-jets":
            assert bridge is not None
            assert local_graph_configuration is not None
            assert h10_c01_configuration is not None
            assert p2a_certificate is not None
            p2_jets_configuration = load_json(P2_JETS_CONFIG_PATH)
            p2b0_certificate = load_json(P2B0_CERTIFICATE_PATH)
            p2b0_prerequisite_status, p2b0_prerequisite_errors, \
                p2b0_prerequisite = verify_p2b0_prerequisite(
                    p2b0_certificate, p2_jets_configuration)
            p2_jets_configuration_status, p2_jets_configuration_errors = \
                verify_p2_jets_configuration(
                    p2_jets_configuration, bridge,
                    local_graph_configuration, p2a_certificate,
                    h10_c01_configuration, p2b0_certificate)
        if arguments.scope == "p2-kato":
            assert bridge is not None
            p2_kato_configuration = load_json(P2_KATO_CONFIG_PATH)
            p2b_jets_certificate = load_json(P2B_JETS_CERTIFICATE_PATH)
            p2b_jets_prerequisite_status, \
                p2b_jets_prerequisite_errors, p2b_jets_prerequisite = \
                verify_p2b_jets_prerequisite(p2b_jets_certificate)
            p2_kato_configuration_status, p2_kato_configuration_errors = \
                verify_p2_kato_configuration(
                    p2_kato_configuration, bridge, p2b_jets_certificate,
                    arguments.flagship_repository)
        head = git_output(REPOSITORY, "rev-parse", "HEAD")
        dirty = bool(git_output(REPOSITORY, "status", "--porcelain"))
        if dirty and not arguments.allow_dirty:
            raise RuntimeError(
                "repository is dirty; use --allow-dirty only for a non-release development run")
        if arguments.scope in ("h10-c01", "p2-kato") and \
                arguments.flagship_repository is None:
            raise RuntimeError(
                f"{arguments.scope} validation requires --flagship-repository for "
                "frozen-object regeneration")
        flagship_status, flagship = verify_flagship(arguments.flagship_repository)
        capd_status, toolchain, cflags, libs = verify_toolchain(
            arguments.capd_source.resolve(), arguments.capd_config.resolve(), dependency)
        toolchain["flagship_import"] = flagship
        exact_symbolic_backend_status = "PASS"
        exact_symbolic_backend_errors: list[str] = []
        if arguments.scope == "p2-kato":
            exact_symbolic_backend_status, exact_symbolic_backend, \
                exact_symbolic_backend_errors = \
                verify_exact_symbolic_backend(dependency)
            toolchain["exact_symbolic_backend"] = exact_symbolic_backend
        exact_center_audit: dict[str, Any] | None = None
        exact_center_audit_logs: dict[str, str] = {}
        kato_exact_algebra_audit: dict[str, Any] | None = None
        kato_exact_audit_logs: dict[str, str] = {}
        if arguments.scope == "h10-c01":
            assert arguments.flagship_repository is not None
            assert h10_c01_configuration is not None
            exact_center_audit, exact_center_audit_logs, audit_execution = \
                run_h10_center_audit(
                    arguments.flagship_repository, h10_c01_configuration)
            toolchain["h10_exact_center_audit_execution"] = audit_execution
        if arguments.scope == "p2-kato":
            kato_exact_algebra_audit, kato_exact_audit_logs, \
                kato_audit_execution = run_kato_exact_audit()
            toolchain["kato_exact_algebra_audit_execution"] = \
                kato_audit_execution
        raw, logs, build = compile_and_run(
            arguments.scope, cflags, libs, dependency, box,
            bridge, local_graph_configuration, h10_c01_configuration,
            p2_jets_configuration,
            p2_kato_configuration, p2b_jets_certificate,
            arguments.flagship_repository)
        p2_parent_status: str | None = None
        p2_kato_atomic_statuses: dict[str, str] | None = None
        p2_kato_true_source_status: str | None = None
        p2_kato_parent_status: str | None = None
        if arguments.scope == "p2-jets":
            raw_items = raw.get("obligations", [])
            if not isinstance(raw_items, list):
                raise RuntimeError("P2 jets probe obligations are not a list")
            raw_statuses = {
                item.get("id"): item.get("status")
                for item in raw_items if isinstance(item, dict)
            }
            atomic_ids = (
                "P2.JETS.COEFFICIENTS", "V2.WU.STATE_C23",
                "V2.WU.MIXED_JETS", "V2.WU.WEIGHTED_HALF_ORBITS")
            if set(raw_statuses) != set(atomic_ids):
                raise RuntimeError(
                    "P2 jets probe emitted an unexpected atomic obligation set")
            p2_parent_status = combine_verdicts(
                raw_statuses[identifier] for identifier in atomic_ids)
            if raw.get("mathematical_status") != p2_parent_status:
                raise RuntimeError(
                    "P2 jets probe mathematical status is not its atomic aggregate")
        if arguments.scope == "p2-kato":
            assert kato_exact_algebra_audit is not None
            raw_items = raw.get("obligations", [])
            if not isinstance(raw_items, list):
                raise RuntimeError("P2 Kato probe obligations are not a list")
            raw_statuses = {
                item.get("id"): item.get("status")
                for item in raw_items if isinstance(item, dict)
            }
            atomic_ids = (
                "P2.KATO.RIESZ_TRANSPORT",
                "P2.KATO.FRAME_CHANGE",
                "P2.KATO.C2_LIFT",
                "P2.KATO.SOURCE_PARAMETERIZATION",
            )
            if set(raw_statuses) != set(atomic_ids):
                raise RuntimeError(
                    "P2 Kato probe emitted an unexpected atomic obligation set")
            raw_parent_status = combine_verdicts(
                raw_statuses[identifier] for identifier in atomic_ids)
            if raw.get("mathematical_status") != raw_parent_status:
                raise RuntimeError(
                    "P2 Kato probe mathematical status is not its raw "
                    "atomic aggregate")
            exact_status = kato_exact_algebra_audit["status"]
            p2_kato_atomic_statuses = {
                identifier: combine_verdicts(
                    (raw_statuses[identifier], exact_status))
                for identifier in atomic_ids
            }
            p2_kato_atomic_statuses[
                "P2.KATO.SOURCE_PARAMETERIZATION"] = combine_verdicts((
                    p2_kato_atomic_statuses[
                        "P2.KATO.SOURCE_PARAMETERIZATION"],
                    p2b_jets_prerequisite_status,
                ))
            p2_kato_true_source_status = combine_verdicts((
                p2b_jets_prerequisite_status,
                p2_kato_atomic_statuses["P2.KATO.C2_LIFT"],
                p2_kato_atomic_statuses[
                    "P2.KATO.SOURCE_PARAMETERIZATION"],
            ))
            p2_kato_parent_status = combine_verdicts((
                *(p2_kato_atomic_statuses[identifier]
                  for identifier in atomic_ids),
                p2_kato_true_source_status,
            ))
        logs.update(exact_center_audit_logs)
        logs.update(kato_exact_audit_logs)
        toolchain["probe_build"] = build
        report_resolved = arguments.report.resolve()
        try:
            report_location = str(report_resolved.relative_to(REPOSITORY.resolve()))
            report_inside_repository = True
        except ValueError:
            report_location = str(report_resolved)
            report_inside_repository = False
        toolchain["report_output"] = {
            "path": report_location,
            "inside_repository": report_inside_repository,
            "excluded_from_prewrite_source_observation": True,
        }

        predicates = obligation_predicates()
        source_status = flagship_status
        rounding = raw["rounding_self_test"]
        p0 = [
            make_obligation("ENV.SOURCE_BINDING", source_status, predicates),
            make_obligation("ENV.CAPD_BINDING", capd_status, predicates),
            make_obligation("ENV.ROUNDING", rounding["status"], predicates),
            make_obligation("BOX.FROZEN", box_status, predicates,
                            diagnostics=box_errors),
        ]
        if arguments.scope in (
                "local-graph", "h10-c01", "p2-jets", "p2-kato"):
            p0.extend([
                make_obligation(
                    "BRIDGE.FROZEN", bridge_status, predicates,
                    diagnostics=bridge_errors),
                make_obligation(
                    "P2.LOCAL_GRAPH_CONFIG_FROZEN",
                    local_graph_configuration_status, predicates,
                    diagnostics=local_graph_configuration_errors),
            ])
        if arguments.scope == "h10-c01":
            assert exact_center_audit is not None
            p0.extend([
                make_obligation(
                    "P2.P2A_PREREQUISITE", p2a_prerequisite_status,
                    predicates, diagnostics=p2a_prerequisite_errors),
                make_obligation(
                    "P2.H10_C01_CONFIG_FROZEN",
                    h10_c01_configuration_status, predicates,
                    diagnostics=h10_c01_configuration_errors),
                make_obligation(
                    "P2.H10_CENTER_EXACT",
                    exact_center_audit["status"], predicates,
                    diagnostics=(exact_center_audit.get("failures", []) +
                                 exact_center_audit.get(
                                     "inconclusive_reasons", []))),
            ])
        if arguments.scope == "p2-jets":
            p0.extend([
                make_obligation(
                    "P2.P2A_PREREQUISITE", p2a_prerequisite_status,
                    predicates, diagnostics=p2a_prerequisite_errors),
                make_obligation(
                    "P2.P2B0_PREREQUISITE", p2b0_prerequisite_status,
                    predicates, diagnostics=p2b0_prerequisite_errors),
                make_obligation(
                    "P2.JETS_CONFIG_FROZEN", p2_jets_configuration_status,
                    predicates, diagnostics=p2_jets_configuration_errors),
            ])
        if arguments.scope == "p2-kato":
            assert kato_exact_algebra_audit is not None
            audit_diagnostics = list(
                kato_exact_algebra_audit.get("failed_checks", []))
            if "error" in kato_exact_algebra_audit:
                audit_diagnostics.append(
                    str(kato_exact_algebra_audit["error"]))
            p0.extend([
                make_obligation(
                    "ENV.EXACT_SYMBOLIC_BACKEND",
                    exact_symbolic_backend_status, predicates,
                    diagnostics=exact_symbolic_backend_errors),
                make_obligation(
                    "P2.P2B_JETS_PREREQUISITE",
                    p2b_jets_prerequisite_status, predicates,
                    diagnostics=p2b_jets_prerequisite_errors),
                make_obligation(
                    "P2.KATO_CONFIG_FROZEN", p2_kato_configuration_status,
                    predicates, diagnostics=p2_kato_configuration_errors),
                make_obligation(
                    "P2.KATO.EXACT_ALGEBRA",
                    kato_exact_algebra_audit["status"], predicates,
                    diagnostics=audit_diagnostics),
            ])
        mathematical: list[dict[str, Any]] = []
        if arguments.scope != "preflight":
            for item in raw["obligations"]:
                identifier = item["id"]
                item_status = item["status"]
                if arguments.scope == "p2-kato":
                    assert p2_kato_atomic_statuses is not None
                    item_status = p2_kato_atomic_statuses[identifier]
                mathematical.append(make_obligation(
                    identifier, item_status, predicates,
                    **({"enclosures": item["enclosures"]}
                       if "enclosures" in item else {})))
        if arguments.scope == "p2-jets":
            assert p2_parent_status is not None
            for identifier in ("V2.WU.JETS", "V2.WU_GRAPH"):
                mathematical.append(make_obligation(
                    identifier, p2_parent_status, predicates))
        if arguments.scope == "p2-kato":
            assert p2_kato_true_source_status is not None
            assert p2_kato_parent_status is not None
            mathematical.extend([
                make_obligation(
                    "V2.PHASE.TRUE_SOURCE", p2_kato_true_source_status,
                    predicates),
                make_obligation(
                    "V2.PHASE.KATO_INTERFACE", p2_kato_parent_status,
                    predicates),
            ])
        integrity_status = combine_verdicts(item["status"] for item in p0)
        mathematical_status = combine_verdicts(
            item["status"] for item in mathematical) if mathematical else "PASS"
        final_status = "FAIL" if "FAIL" in (integrity_status, mathematical_status) \
            else "INCONCLUSIVE"
        now = dt.datetime.now(dt.timezone.utc)
        scope_name = {
            "preflight": "PREFLIGHT",
            "kernel": "V1_V2_1_KERNEL",
            "local-graph": "V2_LOCAL_GRAPH_KERNEL",
            "h10-c01": "V2_H10_C01_KERNEL",
            "p2-jets": "V2_P2_JETS_KERNEL",
            "p2-kato": "V2_P2_KATO_KERNEL",
        }[arguments.scope]
        certificate = {
            "schema_version": "rfsn-rigorous-run-certificate/1",
            "certificate_id": (
                f"vdp-{arguments.scope}-{now.strftime('%Y%m%dt%H%M%Sz').lower()}-"
                f"{head[:12]}"),
            "scope": scope_name,
            "created_at": now.isoformat(),
            "source_revision": {
                "repository": "h-lu/rfsn-ii-positive-parameter-pde",
                "commit": head,
                "repository_dirty": dirty,
                "allow_dirty_development": arguments.allow_dirty,
                "working_tree_observation": "BEFORE_REPORT_WRITE",
                "report_output_excluded_from_observation": True,
            },
            "source_bindings": source_bindings(),
            "parameter_box": {
                "path": "validation/rigorous/config/vdp_box_v1.json",
                "sha256": sha256_file(BOX_PATH),
                "box_id": box["box_id"],
                "variables": box["variables"],
            },
            "toolchain": toolchain,
            "rounding_self_test": rounding,
            "obligations": p0 + mathematical,
            "integrity_status": integrity_status,
            "mathematical_status": mathematical_status,
            "independent_replay": {
                "status": "PENDING_REQUIRED",
                "required_distinct_machines": dependency["independent_replay"]["minimum_distinct_machines"],
                "observed_distinct_machines": 1,
            },
            "final_status": final_status,
            "claim_bearing": False,
            "release_eligible": False,
            "raw_probe": raw,
            "logs": logs,
            "nonclaims": [
                "A local mathematical PASS is not an aggregate theorem certificate.",
                "Independent-machine replay is pending and this certificate is not claim-bearing.",
                (
                    "The local-graph kernel proves only its two P2a subobligations; "
                    "V2.WU_GRAPH mixed jets, the homoclinic, exact charts, event "
                    "atlas, V3--V6, temporal stability, Turing selection, and "
                    "canard identification remain outside its scope."
                    if arguments.scope == "local-graph" else
                    "The H10 C0/C1 kernel proves only its two P2b0 tube "
                    "subobligations; V2.WU.JETS and V2.WU_GRAPH mixed jets "
                    "and weighted tails, the homoclinic, exact charts, event "
                    "atlas, V3--V6, temporal stability, Turing selection, "
                    "and canard identification remain outside its scope."
                    if arguments.scope == "h10-c01" else
                    P2_JETS_SCOPE_NONCLAIM
                    if arguments.scope == "p2-jets" else
                    P2_KATO_SCOPE_NONCLAIM
                    if arguments.scope == "p2-kato" else
                    "Phase 1 does not validate V2 continuation beyond item (1), "
                    "V3--V6, temporal stability, Turing selection, or canard identification."
                ),
            ],
        }
        if arguments.scope in (
                "local-graph", "h10-c01", "p2-jets", "p2-kato"):
            assert bridge is not None
            assert local_graph_configuration is not None
            certificate["continuation_bridge"] = {
                "path": "validation/rigorous/config/vdp_bridge_v1.json",
                "sha256": sha256_file(BRIDGE_PATH),
                "bridge_id": bridge["bridge_id"],
                "variables": bridge["variables"],
            }
            certificate["validation_configuration"] = {
                "path": "validation/rigorous/config/vdp_p2_local_graph_v1.json",
                "sha256": sha256_file(LOCAL_GRAPH_CONFIG_PATH),
                "configuration_id": local_graph_configuration[
                    "configuration_id"],
            }
        if arguments.scope == "h10-c01":
            assert h10_c01_configuration is not None
            assert p2a_prerequisite is not None
            assert exact_center_audit is not None
            certificate["h10_c01_configuration"] = {
                "path": "validation/rigorous/config/vdp_p2_h10_c01_v1.json",
                "sha256": sha256_file(H10_C01_CONFIG_PATH),
                "configuration_id": h10_c01_configuration[
                    "configuration_id"],
            }
            certificate["p2a_prerequisite"] = p2a_prerequisite
            certificate["h10_exact_center_audit"] = exact_center_audit
        if arguments.scope == "p2-jets":
            assert p2_jets_configuration is not None
            assert p2a_prerequisite is not None
            assert p2b0_prerequisite is not None
            certificate["p2_jets_configuration"] = {
                "path": "validation/rigorous/config/vdp_p2_jets_v1.json",
                "sha256": sha256_file(P2_JETS_CONFIG_PATH),
                "configuration_id": p2_jets_configuration[
                    "configuration_id"],
            }
            certificate["p2a_prerequisite"] = p2a_prerequisite
            certificate["p2b0_prerequisite"] = p2b0_prerequisite
        if arguments.scope == "p2-kato":
            assert p2_kato_configuration is not None
            assert p2b_jets_prerequisite is not None
            assert kato_exact_algebra_audit is not None
            certificate["p2_kato_configuration"] = {
                "path": "validation/rigorous/config/vdp_p2_kato_v1.json",
                "sha256": sha256_file(P2_KATO_CONFIG_PATH),
                "configuration_id": p2_kato_configuration[
                    "configuration_id"],
            }
            certificate["p2b_jets_prerequisite"] = p2b_jets_prerequisite
            certificate["kato_exact_algebra_audit"] = \
                kato_exact_algebra_audit
        errors = schema_errors(certificate) + semantic_errors(certificate, REPOSITORY)
        if errors:
            raise RuntimeError("generated certificate failed self-check:\n" + "\n".join(errors))
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        print(
            f"wrote {arguments.report}: mathematical_status={mathematical_status}, "
            f"integrity_status={integrity_status}, final_status={final_status}, "
            "claim_bearing=false")
        return 1 if final_status == "FAIL" else 0
    except (OSError, KeyError, ValueError, RuntimeError,
            subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"validation runner error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
