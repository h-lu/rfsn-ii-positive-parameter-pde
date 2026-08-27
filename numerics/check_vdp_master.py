#!/usr/bin/env python3
"""Verify completeness and hashes of the saved V1--V7 atlas."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

# Support both ``python3 numerics/check_vdp_master.py`` and module execution.
_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))

from validation.check_candidate_contract import validate_contract
from numerics.run_vdp_master import validate_frozen_config_interface


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "numerics" / "results" / "vdp_v1_v7"
CONFIG = ROOT / "numerics" / "config" / "vdp_v1_v7.json"
ARCHIVED_SOURCE_TAG = "vdp-v4-screening-baseline"
ARCHIVED_SOURCE_COMMIT = "61ac68066599e3bf3c86c0f6d3a8615ac61d8538"

FIGURE_STEMS = (
    "figure_01_v1_structure",
    "figure_02_v2_central_passage",
    "figure_03_v3_pole_finite_part",
    "figure_04_v4_v5_outer_matching",
    "figure_05_v5a_algebraic_finite_part",
    "figure_06_v6_first_event_cells",
    "figure_07_v6_length_action",
    "figure_08_v7_patterns",
    "figure_09_numerical_qa",
)
RAW_FILES = (
    "v1_structure.json",
    "v1_bridge.npz",
    "v2_central.json",
    "v2_homoclinics.npz",
    "v2_passage.npz",
    "v3_pole.json",
    "v3_pole.npz",
    "v4_v5_outer_matching.json",
    "v4_v5_matched_candidate.json",
    "v4_v5_matched_candidate.npz",
    "v4_v5a_outer.npz",
    "v5a_outer_finite_part.json",
    "v6_events.json",
    "v6_events.npz",
    "v6_complete_branches.npz",
    "v6_candidate_contract.json",
    "v7_patterns.json",
    "v7_periodic.npz",
    "v7_multipulses.npz",
    "qa.json",
    "manifest.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def archived_source_sha256(relative: str) -> str | None:
    """Hash one source blob from the immutable v4 artifact snapshot.

    The original run recorded a dirty base commit because its newly added
    validation files did not yet exist at that commit.  Commit 61ac680 is the
    subsequent immutable snapshot containing the exact manifest, outputs, and
    source blobs.  Current source evolution must therefore be checked against
    that pinned snapshot, rather than making a historical artifact fail merely
    because a checker has advanced.
    """

    path = Path(relative)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        return None
    try:
        resolved = subprocess.run(
            ["git", "rev-list", "-n", "1", ARCHIVED_SOURCE_TAG],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if resolved != ARCHIVED_SOURCE_COMMIT:
            return None
        blob = subprocess.run(
            [
                "git",
                "cat-file",
                "blob",
                f"{ARCHIVED_SOURCE_COMMIT}:{path.as_posix()}",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return hashlib.sha256(blob).hexdigest()


def verify(output: Path = OUTPUT) -> list[str]:
    failures: list[str] = []
    required = [output / name for name in RAW_FILES]
    complete_record_paths = sorted(output.glob("v6_complete_*.json"))
    if len(complete_record_paths) != 2:
        failures.append(
            "expected exactly two v6_complete_*.json branch records, "
            f"found {len(complete_record_paths)}"
        )
    required.extend(complete_record_paths)
    required.extend(
        output / f"{stem}.{suffix}"
        for stem in FIGURE_STEMS
        for suffix in ("pdf", "svg", "png")
    )
    for path in required:
        if not path.is_file() or path.stat().st_size == 0:
            failures.append(f"missing or empty: {path}")
    if failures:
        return failures

    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    qa = json.loads((output / "qa.json").read_text(encoding="utf-8"))
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    try:
        validate_frozen_config_interface(config)
    except ValueError as error:
        failures.append(f"frozen configuration interface: {error}")
    if manifest.get("configuration_version") != config.get("configuration_version"):
        failures.append("manifest configuration version does not match frozen config")
    if manifest.get("qa_status") != qa.get("status"):
        failures.append("manifest QA status does not match qa.json")
    if not str(qa.get("status", "")).startswith("PASS_WITH_EXPLICIT_UNRESOLVED"):
        failures.append(f"unexpected QA status: {qa.get('status')}")
    if not all(bool(value) for value in qa.get("checks", {}).values()):
        failures.append("one or more qa.json checks are false")
    required_qa_checks = {
        "v3_source_graph_boundary_residuals",
        "v3_gate_event_and_energy",
        "v4_independent_gamma_grid_residuals",
        "v5_coupled_bvp_rms_residual",
        "v5_frozen_phase_and_beta_brackets",
        "v5_same_section_root_residual",
        "v6_complete_return_face_residuals",
        "v6_complete_return_event_transversality",
        "v6_complete_return_energy",
        "v6_complete_return_action_quadrature",
        "frozen_configuration_interface_consumed",
    }
    missing_checks = required_qa_checks - set(qa.get("checks", {}))
    if missing_checks:
        failures.append(f"missing substantive QA checks: {sorted(missing_checks)}")
    required_metrics = {
        "v3_source_graph_boundary_residual",
        "v3_gate_residual",
        "v3_gate_energy_drift",
        "v4_gamma_solver_rms_residual",
        "v4_gamma_boundary_residual",
        "v4_gamma_energy_residual",
        "v5_coupled_bvp_rms_residual",
        "v5_same_section_root_residual",
        "v5_phase_bracket_margin",
        "v5_beta_bracket_margin",
        "v6_complete_face_residual",
        "v6_complete_min_abs_event_speed",
        "v6_complete_energy_defect",
        "v6_complete_action_quadrature_difference",
        "v5a_endpoint_grid_difference",
    }
    metrics = qa.get("metrics", {})
    missing_metrics = required_metrics - set(metrics)
    if missing_metrics:
        failures.append(f"missing machine-readable QA metrics: {sorted(missing_metrics)}")
    for name in required_metrics.intersection(metrics):
        metric = metrics[name]
        if metric.get("passed") is not True:
            failures.append(f"QA metric did not pass: {name}")
        if metric.get("comparator") not in {"<=", ">="}:
            failures.append(f"QA metric comparator is invalid: {name}")

    result_hashes = manifest.get("result_hashes", {})
    result_files = set(manifest.get("result_files", []))
    for path in required:
        name = path.name
        if name == "manifest.json":
            continue
        if name not in result_hashes:
            failures.append(f"required result missing from manifest hashes: {name}")
        if name not in result_files:
            failures.append(f"required result missing from manifest file list: {name}")

    for name, expected in result_hashes.items():
        path = output / name
        if not path.is_file():
            failures.append(f"manifest result missing: {name}")
        elif sha256(path) != expected:
            failures.append(f"result hash mismatch: {name}")
    for relative, expected in manifest.get("source_hashes", {}).items():
        path = ROOT / relative
        current_matches = path.is_file() and sha256(path) == expected
        archived_matches = archived_source_sha256(relative) == expected
        if not current_matches and not archived_matches:
            failures.append(
                f"source hash is absent from both current worktree and frozen "
                f"{ARCHIVED_SOURCE_TAG}: {relative}"
            )

    for name in (item for item in RAW_FILES if item.endswith(".npz")):
        try:
            with np.load(output / name, allow_pickle=False) as archive:
                for key in archive.files:
                    array = archive[key]
                    if array.dtype == object:
                        failures.append(f"object array forbidden: {name}:{key}")
        except Exception as error:  # pragma: no cover - CLI diagnostic path
            failures.append(f"cannot read {name}: {error}")

    v3 = json.loads((output / "v3_pole.json").read_text(encoding="utf-8"))
    v4v5 = json.loads(
        (output / "v4_v5_outer_matching.json").read_text(encoding="utf-8")
    )
    matched = json.loads(
        (output / "v4_v5_matched_candidate.json").read_text(encoding="utf-8")
    )
    v6 = json.loads((output / "v6_events.json").read_text(encoding="utf-8"))
    v7 = json.loads((output / "v7_patterns.json").read_text(encoding="utf-8"))
    computed_expectations = {
        "V3 connected source-to-pole orbit": v3.get("status"),
        "V3 source window": v3.get("global_source_window_status"),
        "V4 finite-horizon graph candidate": v4v5.get("v4_status"),
        "V5 coupled matching candidate": v4v5.get("v5_status"),
        "V4/V5 standalone matched candidate": matched.get("status"),
    }
    for label, status in computed_expectations.items():
        if not str(status).startswith("COMPUTED/E1"):
            failures.append(f"{label} lost its COMPUTED/E1 status: {status}")

    validation_expectations = {
        "V3 connected orbit": v3.get("validation_status"),
        "V4 uniform graph": v4v5.get("v4_uniform_graph_validation_status"),
        "V5 matching": v4v5.get("v5_validation_status"),
        "V4/V5 standalone matched candidate": matched.get("validation_status"),
        "V6 theorem atlas": v6.get("theorem_atlas_validation_status"),
    }
    for label, status in validation_expectations.items():
        if not str(status).startswith("NOT_INTERVAL_VALIDATED"):
            failures.append(f"{label} lost its interval stop-rule status: {status}")
    matched_diagnostics = matched.get("diagnostics", {})
    for diagnostic in (
        "solver_rms_residual_passed",
        "same_section_root_passed",
        "source_phase_in_bracket",
        "seam_beta_in_bracket",
    ):
        if matched_diagnostics.get(diagnostic) is not True:
            failures.append(f"matched candidate diagnostic did not pass: {diagnostic}")
    gamma_report = matched.get("independent_gamma_grid", {})
    if not str(gamma_report.get("status", "")).startswith("COMPUTED/E1"):
        failures.append("independent Gamma(beta) grid lost its E1 status")
    if gamma_report.get("claim_bearing") is not False:
        failures.append("independent Gamma(beta) grid must be non-claim-bearing")

    with np.load(output / "v4_v5_matched_candidate.npz", allow_pickle=False) as archive:
        required_gamma_arrays = {
            "gamma_beta0",
            "gamma_alpha0",
            "gamma_solver_rms_residual",
            "gamma_boundary_residual",
            "gamma_energy_residual",
            "gamma_horizon_q_end",
            "gamma_horizon_at_seam",
            "gamma_horizon_difference_from_candidate",
        }
        missing_gamma_arrays = required_gamma_arrays - set(archive.files)
        if missing_gamma_arrays:
            failures.append(
                f"matched NPZ missing Gamma evidence: {sorted(missing_gamma_arrays)}"
            )
        elif archive["gamma_beta0"].size != int(
            config["matched_outer"]["beta_grid"][2]
        ):
            failures.append("Gamma beta grid size differs from frozen beta_grid")
        if (
            "gamma_horizon_q_end" in archive.files
            and archive["gamma_horizon_q_end"].size
            != len(config["matched_outer"]["gamma_horizon_ladder"])
        ):
            failures.append("Gamma horizon size differs from frozen ladder")

    unresolved_expectations = {
        "V7 itinerary": v7.get("itinerary_status"),
        "V7 bi-infinite orbit": v7.get("bi_infinite_orbit_status"),
    }
    for label, status in unresolved_expectations.items():
        if status != "NOT_NUMERICALLY_RESOLVED":
            failures.append(f"{label} lost its stop-rule status: {status}")
    if not any(name.startswith("return") for name in v6.get("event_counts", {})):
        failures.append("V6 atlas contains no completed numerical return sample")

    complete_records: list[dict[str, object]] = []
    for path in complete_record_paths:
        try:
            complete_records.append(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError) as error:
            failures.append(f"cannot read complete branch record {path.name}: {error}")
    complete_keys = {
        (
            str(record.get("provenance", {}).get("family")),
            record.get("provenance", {}).get("relative_winding_metadata"),
        )
        for record in complete_records
    }
    if complete_keys != {("B", 1), ("A", 2)}:
        failures.append(f"complete V6 branches are not exactly B1 and A2: {complete_keys}")
    target_signs = {
        record.get("target", {}).get("sign_proxy") for record in complete_records
    }
    if target_signs != {"positive", "negative"}:
        failures.append(
            "complete V6 branches do not realize both target signs: "
            f"{target_signs}"
        )
    for record in complete_records:
        branch_id = record.get("branch_id", "<missing branch_id>")
        if record.get("claim_bearing") is not False:
            failures.append(f"complete branch {branch_id} must be non-claim-bearing")
        if not str(record.get("evidence_status", "")).startswith(
            "COMPUTED/E1_NONRIGOROUS"
        ):
            failures.append(f"complete branch {branch_id} lost its E1 status")
        diagnostics = record.get("diagnostics", {})
        acceptance = config["acceptance"]
        if max(
            float(diagnostics.get("source_face_residual", float("inf"))),
            float(diagnostics.get("incoming_face_residual", float("inf"))),
            float(diagnostics.get("target_face_residual", float("inf"))),
        ) > float(acceptance["event_hit_residual"]):
            failures.append(f"complete branch {branch_id} failed face residual QA")
        if not (
            float(diagnostics.get("incoming_event_speed", 0.0))
            < -float(acceptance["complete_return_min_abs_event_speed"])
            and float(diagnostics.get("target_event_speed", 0.0))
            > float(acceptance["complete_return_min_abs_event_speed"])
        ):
            failures.append(f"complete branch {branch_id} failed transversality QA")
        if max(
            float(diagnostics.get("energy_drift", float("inf"))),
            float(diagnostics.get("energy_abs_max", float("inf"))),
        ) > float(acceptance["energy_drift"]):
            failures.append(f"complete branch {branch_id} failed energy QA")
        if abs(
            float(diagnostics.get("resampled_action_difference", float("inf")))
        ) > float(acceptance["complete_return_action_quadrature_difference"]):
            failures.append(f"complete branch {branch_id} failed quadrature QA")

    contract_path = output / "v6_candidate_contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract.get("claim_bearing") is not False:
        failures.append("V6 candidate contract must be non-claim-bearing")
    if contract.get("final_status") != "NOT_RUN":
        failures.append(
            "V6 candidate contract lost its NOT_RUN stop-rule status: "
            f"{contract.get('final_status')}"
        )
    record_branch_ids = {record.get("branch_id") for record in complete_records}
    contract_branch_ids = {
        branch.get("branch_id") for branch in contract.get("candidate_branches", [])
    }
    if contract_branch_ids != record_branch_ids:
        failures.append(
            "V6 candidate contract branch ids differ from the B1/A2 records: "
            f"{contract_branch_ids} != {record_branch_ids}"
        )
    failures.extend(
        f"V6 candidate contract: {failure}"
        for failure in validate_contract(contract_path, repository_root=ROOT)
    )

    if len(v7.get("periodic_orbits", [])) < 3:
        failures.append("fewer than three actual periodic profiles")
    if len(v7.get("multipulses", [])) < 4:
        failures.append("fewer than four increasing multipulse profiles")
    return failures


def main() -> None:
    failures = verify()
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)
    print(f"PASS: verified {OUTPUT}")


if __name__ == "__main__":
    main()
