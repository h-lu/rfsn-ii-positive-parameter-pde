#!/usr/bin/env python3
"""Check the saved non-rigorous van der Pol dynamics-screening package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from numerics.run_vdp_dynamics_screening import (  # noqa: E402
    DEVELOPMENT_RUN_MODE,
    OFFICIAL_RUN_MODE,
    baseline_git_blob_hashes,
    git_blob_sha256,
    git_text,
    resolve_candidate_baseline,
    source_files_for,
    validate_config,
    verify_baseline_git_blobs,
)

DEFAULT_CONFIG = ROOT / "numerics/config/vdp_dynamics_screening.json"
DEFAULT_OUTPUT = ROOT / "numerics/results/vdp_dynamics_screening"

FIGURE_STEMS = (
    "figure_d1_turing_obstruction",
    "figure_d2_periodic_bloch_screen",
    "figure_d3_multipulse_temporal_screen",
    "figure_d4_canard_stop_rule",
)
DATA_FILES = (
    "turing_report.json",
    "turing_arrays.npz",
    "bloch_report.json",
    "bloch_arrays.npz",
    "pulse_temporal_report.json",
    "canard_report.json",
    "screening_profiles.npz",
    "qa.json",
    "decision.json",
    "render_contract.json",
    "manifest.json",
)

REQUIRED_QA_CHECKS = {
    "bloch.constant_profile_dispersion_crosscheck",
    "bloch.bloch_conjugacy_crosscheck",
    "bloch.translation_vector_residual",
    "bloch.grid_refinement_matching_defect",
    "pulse.homogeneous_fourier_crosscheck",
    "pulse.leading_mode_eigenpair_residual",
    "pulse.zero_perturbation_invariance",
    "pulse.spectral_grid_abscissa_sensitivity",
    "pulse.spectral_boundary_abscissa_sensitivity",
    "pulse.time_step_final_state_sensitivity",
    "pulse.grid_final_state_sensitivity",
    "pulse.boundary_final_state_sensitivity",
    "pulse.leading_mode_envelope_amplification_sensitivity",
    "turing.primary_classification",
    "turing.classical_obstruction_scan",
    "canard.stop_rule_preserved",
    "canard.outer_fold_exclusion",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def check_source_files(
    contract: dict[str, Any], config_path: Path, config: dict[str, Any]
) -> list[str]:
    """Strictly verify the exact source census and every recorded SHA-256."""

    failures: list[str] = []
    try:
        expected_paths = source_files_for(config_path, config)
    except (KeyError, OSError, ValueError) as exc:
        return [f"cannot construct expected source census: {exc}"]
    expected = {str(path.relative_to(ROOT)): path for path in expected_paths}
    recorded = contract.get("source_files")
    if not isinstance(recorded, dict):
        return ["source_files must be a repository-relative SHA-256 mapping"]
    if set(recorded) != set(expected):
        failures.append(
            "source file census mismatch: "
            f"missing={sorted(set(expected) - set(recorded))}, "
            f"unexpected={sorted(set(recorded) - set(expected))}"
        )
    for relative in sorted(set(recorded) & set(expected)):
        digest = recorded[relative]
        if not isinstance(digest, str) or len(digest) != 64:
            failures.append(f"invalid source SHA-256 record: {relative}")
            continue
        current = sha256(expected[relative])
        if digest != current:
            failures.append(f"source SHA-256 mismatch: {relative}")
    return failures


def check_run_provenance(
    contract: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    allow_development_artifact: bool = False,
) -> list[str]:
    """Verify clean official-source semantics and the frozen baseline blobs."""

    failures: list[str] = []
    run_mode = contract.get("run_mode")
    dirty_at_start = contract.get("source_dirty_at_run_start")
    if run_mode == OFFICIAL_RUN_MODE:
        if dirty_at_start is not False:
            failures.append("official artifact did not start from a clean repository")
    elif run_mode == DEVELOPMENT_RUN_MODE:
        if not allow_development_artifact:
            failures.append(
                "development-only dirty-source artifact rejected by official checker"
            )
    else:
        failures.append(f"unknown dynamics screening run mode: {run_mode}")

    start_revision = contract.get("source_revision_at_run_start")
    end_revision = contract.get("source_revision_at_run_end")
    if (
        not isinstance(start_revision, str)
        or len(start_revision) != 40
        or git_text("cat-file", "-t", start_revision) != "commit"
    ):
        failures.append("source revision at run start is not a resolvable commit")
    if end_revision != start_revision:
        failures.append("source revision changed during dynamics screening")

    recorded_source_hashes = contract.get("source_files")
    recorded_commit_blobs = contract.get("source_revision_git_blobs")
    if run_mode == OFFICIAL_RUN_MODE and isinstance(start_revision, str):
        if not isinstance(recorded_source_hashes, dict):
            failures.append("official artifact lacks a source-file hash census")
        else:
            try:
                expected_commit_blobs = {
                    relative: git_blob_sha256(start_revision, relative)
                    for relative in recorded_source_hashes
                }
            except RuntimeError as exc:
                failures.append(
                    f"cannot bind official source census to source commit: {exc}"
                )
            else:
                if recorded_commit_blobs != expected_commit_blobs:
                    failures.append(
                        "recorded source-revision Git blobs differ from source commit"
                    )
                if recorded_source_hashes != expected_commit_blobs:
                    failures.append(
                        "official source hashes differ from source-revision Git blobs"
                    )
    elif run_mode == DEVELOPMENT_RUN_MODE:
        if recorded_commit_blobs is not None:
            failures.append(
                "development artifact must not claim clean source-revision Git blobs"
            )

    try:
        resolved_tag = resolve_candidate_baseline(config)
        expected_blobs = baseline_git_blob_hashes(
            config, resolved_revision=resolved_tag
        )
        verify_baseline_git_blobs(config, resolved_revision=resolved_tag)
    except (KeyError, OSError, RuntimeError, ValueError) as exc:
        failures.append(f"cannot verify frozen candidate baseline Git blobs: {exc}")
        return failures
    if contract.get("candidate_tag_resolved") != resolved_tag:
        failures.append("candidate baseline tag resolution changed")
    recorded_blobs = contract.get("candidate_baseline_git_blobs")
    if recorded_blobs != expected_blobs:
        failures.append("candidate baseline Git-blob binding differs from frozen tag")
    return failures


def _finite_max(values: Any) -> float:
    array = np.asarray(values, dtype=np.float64)
    finite = array[np.isfinite(array)]
    return float(np.max(finite)) if finite.size else float("inf")


def _numeric_gate(value: float, limit: float) -> dict[str, Any]:
    return {
        "value": float(value),
        "limit": float(limit),
        "passed": bool(np.isfinite(value) and value <= limit),
    }


def recompute_qa_checks(
    output: Path, config: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    """Independently reconstruct every QA row from saved data and config."""

    limits = config["qa"]
    bloch_report = load_json(output / "bloch_report.json")
    with np.load(output / "bloch_arrays.npz", allow_pickle=False) as archive:
        bloch_conjugacy = _finite_max(archive["conjugacy_defects"])
        bloch_translation = _finite_max(archive["translation_residuals"])
        bloch_refinement = _finite_max(archive["refinement_defects"])
        constant_dispersion = float(np.asarray(archive["constant_dispersion_defect"])[0])
    if constant_dispersion != float(
        bloch_report["constant_profile_dispersion_matching_defect"]
    ):
        raise ValueError("Bloch report/array constant-dispersion value differs")

    pulse_report = load_json(output / "pulse_temporal_report.json")
    homogeneous_rows = pulse_report["homogeneous_fourier_validation"][
        "finite_volume_matrix_vs_analytic_discrete_modes"
    ]
    homogeneous_defect = max(
        float(row["maximum_eigenvalue_matching_error"])
        for row in homogeneous_rows.values()
    )
    profiles = pulse_report["profiles"]
    eigenpair_residual = max(
        float(profile["sensitivity"]["leading_mode_complex_eigenpair_relative_residual"])
        for profile in profiles
    )
    zero_defect = max(
        float(run["zero_perturbation_defect_inf"])
        for profile in profiles
        for run in profile["short_time_runs"].values()
    )
    pulse_metrics = {
        "spectral_grid_abscissa_sensitivity": max(
            float(profile["sensitivity"]["spectral_grid_abscissa_difference"])
            for profile in profiles
        ),
        "spectral_boundary_abscissa_sensitivity": max(
            float(profile["sensitivity"]["spectral_boundary_abscissa_difference"])
            for profile in profiles
        ),
        "time_step_final_state_sensitivity": max(
            float(
                profile["sensitivity"][
                    "time_step_final_state_difference_over_initial_rms"
                ]
            )
            for profile in profiles
        ),
        "grid_final_state_sensitivity": max(
            float(
                profile["sensitivity"][
                    "grid_final_state_difference_over_initial_rms"
                ]
            )
            for profile in profiles
        ),
        "boundary_final_state_sensitivity": max(
            float(
                profile["sensitivity"][
                    "boundary_final_state_difference_over_initial_rms"
                ]
            )
            for profile in profiles
        ),
        "leading_mode_envelope_amplification_sensitivity": max(
            abs(
                float(
                    profile["sensitivity"][
                        "leading_mode_observed_nonlinear_amplification"
                    ]
                )
                - float(
                    profile["sensitivity"][
                        "leading_mode_expected_linear_envelope_amplification"
                    ]
                )
            )
            for profile in profiles
        ),
    }

    turing_report = load_json(output / "turing_report.json")
    canard_report = load_json(output / "canard_report.json")
    checks: dict[str, dict[str, Any]] = {
        "bloch.constant_profile_dispersion_crosscheck": _numeric_gate(
            constant_dispersion,
            float(limits["bloch_constant_dispersion_defect_max"]),
        ),
        "bloch.bloch_conjugacy_crosscheck": _numeric_gate(
            bloch_conjugacy, float(limits["bloch_conjugacy_defect_max"])
        ),
        "bloch.translation_vector_residual": _numeric_gate(
            bloch_translation,
            float(limits["bloch_translation_vector_residual_max"]),
        ),
        "bloch.grid_refinement_matching_defect": _numeric_gate(
            bloch_refinement, float(limits["bloch_refinement_defect_max"])
        ),
        "pulse.homogeneous_fourier_crosscheck": _numeric_gate(
            homogeneous_defect,
            float(limits["pulse_homogeneous_fourier_defect_max"]),
        ),
        "pulse.leading_mode_eigenpair_residual": _numeric_gate(
            eigenpair_residual,
            float(limits["pulse_leading_mode_eigenpair_residual_max"]),
        ),
        "pulse.zero_perturbation_invariance": _numeric_gate(
            zero_defect,
            float(limits["pulse_zero_perturbation_defect_max"]),
        ),
    }
    pulse_limit_names = {
        "spectral_grid_abscissa_sensitivity": (
            "pulse_spectral_grid_abscissa_difference_max"
        ),
        "spectral_boundary_abscissa_sensitivity": (
            "pulse_spectral_boundary_abscissa_difference_max"
        ),
        "time_step_final_state_sensitivity": (
            "pulse_time_step_final_state_difference_max"
        ),
        "grid_final_state_sensitivity": "pulse_grid_final_state_difference_max",
        "boundary_final_state_sensitivity": (
            "pulse_boundary_final_state_difference_max"
        ),
        "leading_mode_envelope_amplification_sensitivity": (
            "pulse_leading_mode_envelope_amplification_difference_max"
        ),
    }
    for suffix, limit_name in pulse_limit_names.items():
        checks[f"pulse.{suffix}"] = _numeric_gate(
            pulse_metrics[suffix], float(limits[limit_name])
        )

    turing_status = turing_report["primary"]["homogeneous_status"]
    turing_count = turing_report["wide_diagnostic_domain"]["scan"][
        "classical_stationary_turing_point_count"
    ]
    canard_status = canard_report["canard_identification_status"]
    outer_crossing = canard_report["outer_diagnostics"]["crosses_a_fold"]
    checks.update(
        {
            "turing.primary_classification": {
                "value": turing_status,
                "expected": "HOPF_BOUNDARY_K0",
                "passed": turing_status == "HOPF_BOUNDARY_K0",
            },
            "turing.classical_obstruction_scan": {
                "value": turing_count,
                "expected": 0,
                "passed": turing_count == 0,
            },
            "canard.stop_rule_preserved": {
                "value": canard_status,
                "expected": "NO_CANARD_IDENTIFICATION_FROM_CURRENT_DATA",
                "passed": canard_status
                == "NO_CANARD_IDENTIFICATION_FROM_CURRENT_DATA",
            },
            "canard.outer_fold_exclusion": {
                "value": outer_crossing,
                "expected": False,
                "passed": outer_crossing is False,
            },
        }
    )
    return checks


def check_qa_record(
    qa: Mapping[str, Any], recomputed: Mapping[str, Mapping[str, Any]]
) -> list[str]:
    """Reject stale limits, forged pass flags, values, statuses, and counts."""

    failures: list[str] = []
    required_top_level = {
        "schema_version",
        "status",
        "claim_bearing",
        "checks",
        "passed_count",
        "check_count",
    }
    if set(qa) != required_top_level:
        failures.append("QA top-level schema changed")
    if qa.get("schema_version") != "vdp-dynamics-screening-qa/1":
        failures.append("QA schema version changed")
    if qa.get("claim_bearing") is not False:
        failures.append("QA record must remain non-claim-bearing")
    checks = qa.get("checks")
    if not isinstance(checks, dict) or set(checks) != set(recomputed):
        failures.append("computational QA gate census changed")
        return failures
    for name in sorted(recomputed):
        if checks.get(name) != recomputed[name]:
            failures.append(f"QA row differs from independent recomputation: {name}")
    passed_count = sum(bool(row["passed"]) for row in recomputed.values())
    expected_status = (
        "PASS_COMPUTATIONAL_QA_NOT_A_THEOREM"
        if passed_count == len(recomputed)
        else "FAIL_COMPUTATIONAL_QA"
    )
    if qa.get("passed_count") != passed_count:
        failures.append("QA passed count differs from independent recomputation")
    if qa.get("check_count") != len(recomputed):
        failures.append("QA check count differs from independent recomputation")
    if qa.get("status") != expected_status:
        failures.append("QA status differs from independent recomputation")
    if expected_status != "PASS_COMPUTATIONAL_QA_NOT_A_THEOREM":
        failures.append(f"computational QA did not pass: {expected_status}")
    return failures


def check_manifest_decision_consistency(
    manifest: Mapping[str, Any],
    render_contract: Mapping[str, Any],
    qa: Mapping[str, Any],
    decision: Mapping[str, Any],
) -> list[str]:
    """Cross-bind the summary fields rather than trusting manifest prose."""

    failures: list[str] = []
    if render_contract.get("qa_status") != qa.get("status"):
        failures.append("render-contract QA status differs from QA record")
    if manifest.get("final_status") != qa.get("status"):
        failures.append("manifest final status differs from QA record")
    if manifest.get("screening_decision") != decision.get("conclusions"):
        failures.append("manifest screening decision differs from decision record")
    return failures


def check(
    output: Path,
    config_path: Path,
    *,
    allow_development_artifact: bool = False,
) -> list[str]:
    failures: list[str] = []
    required = [*DATA_FILES]
    required.extend(
        f"{stem}.{suffix}"
        for stem in FIGURE_STEMS
        for suffix in ("pdf", "svg", "png")
    )
    for filename in required:
        path = output / filename
        if not path.is_file():
            failures.append(f"missing output file: {filename}")
        elif path.stat().st_size == 0:
            failures.append(f"empty output file: {filename}")
    if failures:
        return failures

    config = load_json(config_path)
    try:
        validate_config(config)
    except (KeyError, TypeError, ValueError) as exc:
        failures.append(f"invalid frozen dynamics configuration: {exc}")
        return failures
    manifest = load_json(output / "manifest.json")
    render_contract = load_json(output / "render_contract.json")
    if manifest.get("claim_bearing") is not False:
        failures.append("manifest must remain non-claim-bearing")
    if manifest.get("configuration_version") != config.get("configuration_version"):
        failures.append("configuration version mismatch")
    if manifest.get("configuration_sha256") != sha256(config_path):
        failures.append("configuration hash mismatch")
    for key, value in render_contract.items():
        if manifest.get(key) != value:
            failures.append(f"manifest/render-contract mismatch: {key}")
    failures.extend(check_source_files(render_contract, config_path, config))
    failures.extend(
        check_run_provenance(
            render_contract,
            config,
            allow_development_artifact=allow_development_artifact,
        )
    )
    baseline = config["source_candidate_baseline"]
    if render_contract.get("candidate_baseline") != baseline:
        failures.append("candidate baseline differs from frozen configuration")
    for filename, record in manifest.get("output_files", {}).items():
        path = output / filename
        if not path.is_file():
            failures.append(f"manifest-bound file missing: {filename}")
            continue
        if record.get("sha256") != sha256(path):
            failures.append(f"manifest SHA-256 mismatch: {filename}")
        if record.get("bytes") != path.stat().st_size:
            failures.append(f"manifest byte count mismatch: {filename}")
    expected_manifest_files = set(required) - {"manifest.json"}
    if set(manifest.get("output_files", {})) != expected_manifest_files:
        failures.append("manifest output file census differs from required package")

    qa = load_json(output / "qa.json")
    try:
        recomputed_qa = recompute_qa_checks(output, config)
    except (KeyError, OSError, TypeError, ValueError) as exc:
        failures.append(f"cannot independently recompute computational QA: {exc}")
        recomputed_qa = {}
    if set(recomputed_qa) != REQUIRED_QA_CHECKS:
        failures.append("independently recomputed QA gate census changed")
    else:
        failures.extend(check_qa_record(qa, recomputed_qa))

    turing = load_json(output / "turing_report.json")
    if turing["primary"]["homogeneous_status"] != "HOPF_BOUNDARY_K0":
        failures.append("primary Turing classification changed")
    if (
        turing["wide_diagnostic_domain"]["scan"]
        ["classical_stationary_turing_point_count"]
        != 0
    ):
        failures.append("classical stationary Turing obstruction was not preserved")

    bloch = load_json(output / "bloch_report.json")
    if bloch.get("claim_bearing") is not False:
        failures.append("Bloch report must remain non-claim-bearing")
    for row in bloch.get("profiles", []):
        if row.get("co_periodic_outcome") != "SAMPLED_COPERIODIC_INSTABILITY_DETECTED":
            failures.append(f"{row.get('label')} lost its sampled co-periodic signal")
        if float(row.get("co_periodic_max_real_part", 0.0)) <= 0.0:
            failures.append(f"{row.get('label')} co-periodic growth is not positive")
    with np.load(output / "bloch_arrays.npz", allow_pickle=False) as archive:
        if archive["spectral_abscissa"].shape[0] != 5:
            failures.append("Bloch array profile count changed")
        if not np.all(np.isfinite(archive["spectral_abscissa"])):
            failures.append("Bloch spectral abscissa contains nonfinite values")

    pulses = load_json(output / "pulse_temporal_report.json")
    if pulses.get("claim_bearing") is not False:
        failures.append("pulse report must remain non-claim-bearing")
    if pulses.get("profile_count") != 4:
        failures.append("pulse report must contain four profiles")
    for row in pulses.get("profiles", []):
        if row.get("screen_signal") != (
            "POSITIVE_GROWTH_CANDIDATE_ACROSS_GRID_AND_BOUNDARY_CHECKS"
        ):
            failures.append(f"{row.get('profile')} lost its positive-growth candidate")
        if "refined_real_axis_spectra" not in row:
            failures.append(f"{row.get('profile')} lacks the refined real-axis screen")

    canard = load_json(output / "canard_report.json")
    if canard.get("canard_identification_status") != (
        "NO_CANARD_IDENTIFICATION_FROM_CURRENT_DATA"
    ):
        failures.append("canard stop rule was not preserved")
    if canard["outer_diagnostics"].get("crosses_a_fold"):
        failures.append("saved outer leg unexpectedly reaches a fold")
    if canard.get("screened_fold") != config["canard"]["positive_fold"]:
        failures.append("canard screened fold differs from frozen configuration")
    if canard.get("fold_collar") != config["canard"]["fold_collar"]:
        failures.append("canard fold collar differs from frozen configuration")
    if (
        canard.get("reference_curve_configuration")
        != config["canard"]["reference_curve"]
    ):
        failures.append("canard reference curve differs from frozen configuration")

    decision = load_json(output / "decision.json")
    if decision.get("claim_bearing") is not False:
        failures.append("decision record must remain non-claim-bearing")
    if decision["conclusions"]["issue_7"]["status"] != (
        "PROCEED_WITH_EXISTENCE_VALIDATION_ON_PRESELECTED_BOX"
    ):
        failures.append("Issue #7 ordering decision changed")
    if decision["issue_7_preselected_box"] != config["issue_7_preselected_box"]:
        failures.append("preselected Issue #7 box differs from frozen config")
    if decision.get("nonclaims") != config["nonclaims"]:
        failures.append("decision nonclaims differ from frozen config")
    failures.extend(
        check_manifest_decision_consistency(
            manifest, render_contract, qa, decision
        )
    )
    return failures


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--allow-development-artifact",
        action="store_true",
        help=(
            "accept an artifact explicitly marked DEVELOPMENT_ALLOW_DIRTY_SOURCE; "
            "the default official checker rejects it"
        ),
    )
    arguments = parser.parse_args(argv)
    failures = check(
        arguments.output.resolve(),
        arguments.config.resolve(),
        allow_development_artifact=arguments.allow_development_artifact,
    )
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(
        "PASS: dynamics-screening artifacts and computational QA are internally "
        "consistent; this is not temporal-stability, canard, or Issue #7 interval validation"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
