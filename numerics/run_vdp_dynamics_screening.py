#!/usr/bin/env python3
"""Run the frozen temporal/Turing/slow--fast prescreen after the V1--V7 atlas.

The run deliberately has two kinds of output: exact derived identities (most
notably the homogeneous stationary-Turing obstruction) and floating-point
``COMPUTED/E1`` diagnostics.  A QA ``PASS`` from this script means that the
finite computations satisfy their internal reproduction gates.  It is never
an Issue #7 interval-validation result or a temporal-stability theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

import matplotlib
import numpy as np
import scipy


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from numerics.vdp_bloch_stability import (  # noqa: E402
    SAMPLED_INSTABILITY,
    screen_saved_periodic_profiles,
    write_screening_outputs,
)
from numerics.vdp_canard_diagnostics import (  # noqa: E402
    CANARD_STOP_STATUS,
    screen_saved_profiles,
)
from numerics.vdp_temporal_screen import (  # noqa: E402
    TemporalParameters as PulseTemporalParameters,
    run_temporal_prescreen,
)
from numerics.vdp_turing import (  # noqa: E402
    HOPF_BOUNDARY_K0,
    TemporalParameters as TuringParameters,
    build_prescreen_report,
    dispersion_curve,
    threshold_curve,
)


DEFAULT_CONFIG = ROOT / "numerics" / "config" / "vdp_dynamics_screening.json"
DEFAULT_OUTPUT = ROOT / "numerics" / "results" / "vdp_dynamics_screening"
SCREENING_SCHEMA = "vdp-dynamics-screening-results/1"
FROZEN_CONFIG_V1_CANONICAL_SHA256 = (
    "fa97c4883bf2d073f8717d04e4eb3fc2236ef5b931f0ecaa9de56720ebd66f21"
)

SOURCE_RELATIVE_FILES = (
    "numerics/vdp_turing.py",
    "numerics/vdp_bloch_stability.py",
    "numerics/vdp_temporal_screen.py",
    "numerics/vdp_canard_diagnostics.py",
    "numerics/vdp_bridge.py",
    "numerics/vdp_outer.py",
    "numerics/vdp_pole.py",
    "numerics/rfsn_numerics.py",
    "numerics/run_vdp_dynamics_screening.py",
    "numerics/render_vdp_dynamics_figures.py",
    "numerics/check_vdp_dynamics_screening.py",
    "numerics/VDP_DYNAMICS_FIGURE_CONTRACTS.md",
)

BASELINE_INPUT_FILENAMES = (
    "v7_periodic.npz",
    "v7_multipulses.npz",
    "v4_v5_matched_candidate.npz",
)

OFFICIAL_RUN_MODE = "OFFICIAL_CLEAN_SOURCE"
DEVELOPMENT_RUN_MODE = "DEVELOPMENT_ALLOW_DIRTY_SOURCE"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_sha256(value: Any) -> str:
    """Hash JSON semantics independently of whitespace and key order."""

    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def source_files_for(
    config_path: Path, config: Mapping[str, Any]
) -> tuple[Path, ...]:
    """Return the exact code/config/contract/input census for one run."""

    source_directory = ROOT / config["source_candidate_baseline"][
        "results_directory"
    ]
    candidates = [
        config_path,
        *(ROOT / relative for relative in SOURCE_RELATIVE_FILES),
        *(source_directory / filename for filename in BASELINE_INPUT_FILENAMES),
    ]
    resolved: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        path = candidate.resolve()
        try:
            path.relative_to(ROOT)
        except ValueError as exc:
            raise ValueError(f"source file escapes repository root: {path}") from exc
        if path in seen:
            raise ValueError(f"duplicate source file in dynamics census: {path}")
        if not path.is_file():
            raise FileNotFoundError(f"dynamics source file is missing: {path}")
        seen.add(path)
        resolved.append(path)
    return tuple(resolved)


def source_file_hashes(
    config_path: Path, config: Mapping[str, Any]
) -> dict[str, str]:
    """Return repository-relative SHA-256 records for the exact source census."""

    return {
        str(path.relative_to(ROOT)): sha256(path)
        for path in source_files_for(config_path, config)
    }


def source_git_blob_hashes(
    config_path: Path,
    config: Mapping[str, Any],
    *,
    revision: str,
) -> dict[str, str]:
    """Hash every census file exactly as stored in one Git commit."""

    return {
        str(path.relative_to(ROOT)): git_blob_sha256(
            revision, str(path.relative_to(ROOT))
        )
        for path in source_files_for(config_path, config)
    }


def verify_source_commit_blobs(
    config_path: Path,
    config: Mapping[str, Any],
    *,
    revision: str,
    current_hashes: Mapping[str, str],
) -> dict[str, str]:
    """Require the official worktree census to equal its recorded commit."""

    blobs = source_git_blob_hashes(
        config_path, config, revision=revision
    )
    if dict(current_hashes) != blobs:
        changed = sorted(
            key
            for key in set(current_hashes) | set(blobs)
            if current_hashes.get(key) != blobs.get(key)
        )
        raise RuntimeError(
            "official source census differs from source revision Git blobs: "
            + ", ".join(changed)
        )
    return blobs


def baseline_input_paths(config: Mapping[str, Any]) -> tuple[Path, ...]:
    """Return the three frozen V1--V7 inputs consumed by this screen."""

    directory = (
        ROOT / config["source_candidate_baseline"]["results_directory"]
    ).resolve()
    try:
        directory.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(
            f"candidate baseline directory escapes repository root: {directory}"
        ) from exc
    paths = tuple(directory / filename for filename in BASELINE_INPUT_FILENAMES)
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(f"candidate baseline input is missing: {path}")
    return paths


def resolve_candidate_baseline(config: Mapping[str, Any]) -> str:
    """Resolve and validate the annotated baseline tag to its commit."""

    baseline = config["source_candidate_baseline"]
    resolved = git_text("rev-list", "-n", "1", str(baseline["tag"]))
    if resolved == "UNAVAILABLE" or len(resolved) != 40:
        raise RuntimeError("cannot resolve frozen candidate baseline tag to a commit")
    if not resolved.startswith(str(baseline["commit"])):
        raise RuntimeError("candidate baseline tag no longer resolves to frozen commit")
    return resolved


def git_blob_sha256(revision: str, relative_path: str) -> str:
    """Hash one exact Git blob without text decoding or worktree conversion."""

    try:
        result = subprocess.run(
            ["git", "show", f"{revision}:{relative_path}"],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(
            f"cannot read frozen Git blob {revision}:{relative_path}"
        ) from exc
    return hashlib.sha256(result.stdout).hexdigest()


def baseline_git_blob_hashes(
    config: Mapping[str, Any], *, resolved_revision: str | None = None
) -> dict[str, str]:
    """Bind every consumed baseline NPZ to the configured Git tag commit."""

    revision = resolved_revision or resolve_candidate_baseline(config)
    return {
        str(path.relative_to(ROOT)): git_blob_sha256(
            revision, str(path.relative_to(ROOT))
        )
        for path in baseline_input_paths(config)
    }


def verify_baseline_git_blobs(
    config: Mapping[str, Any], *, resolved_revision: str | None = None
) -> dict[str, str]:
    """Require the current baseline inputs to equal their frozen Git blobs."""

    recorded = baseline_git_blob_hashes(
        config, resolved_revision=resolved_revision
    )
    current = {
        str(path.relative_to(ROOT)): sha256(path)
        for path in baseline_input_paths(config)
    }
    mismatches = [
        relative
        for relative, digest in recorded.items()
        if current.get(relative) != digest
    ]
    if mismatches:
        raise RuntimeError(
            "candidate baseline input differs from frozen Git blob: "
            + ", ".join(sorted(mismatches))
        )
    return recorded


def verify_unchanged_source_snapshot(
    start_hashes: Mapping[str, str],
    end_hashes: Mapping[str, str],
    *,
    start_revision: str,
    end_revision: str,
    start_baseline_revision: str,
    end_baseline_revision: str,
) -> None:
    """Reject a run whose code, inputs, HEAD, or baseline tag moved in flight."""

    if start_revision != end_revision:
        raise RuntimeError("repository HEAD changed during dynamics screening")
    if start_baseline_revision != end_baseline_revision:
        raise RuntimeError("candidate baseline tag changed during dynamics screening")
    if dict(start_hashes) != dict(end_hashes):
        changed = sorted(
            key
            for key in set(start_hashes) | set(end_hashes)
            if start_hashes.get(key) != end_hashes.get(key)
        )
        raise RuntimeError(
            "dynamics source census changed during screening: "
            + ", ".join(changed)
        )


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def git_text(*arguments: str) -> str:
    try:
        return subprocess.run(
            ["git", *arguments],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNAVAILABLE"


def _grid(specification: Sequence[float | int], *, name: str) -> np.ndarray:
    if len(specification) != 3:
        raise ValueError(f"{name} must be [lower,upper,count]")
    lower, upper, count_value = specification
    count = int(count_value)
    if count < 2 or float(count_value) != count:
        raise ValueError(f"{name} count must be an integer at least two")
    if not np.isfinite(lower) or not np.isfinite(upper) or float(upper) <= float(lower):
        raise ValueError(f"{name} endpoints must be finite and increasing")
    return np.linspace(float(lower), float(upper), count)


def validate_config(config: Mapping[str, Any]) -> None:
    required = {
        "schema_version",
        "configuration_version",
        "frozen_before_issue_7_interval_run",
        "evidence_status",
        "source_candidate_baseline",
        "primary_parameters",
        "issue_7_preselected_box",
        "turing",
        "periodic_bloch",
        "multipulse_temporal",
        "canard",
        "qa",
        "nonclaims",
    }
    if set(config) != required:
        raise ValueError(
            "dynamics screening configuration drift: "
            f"missing={sorted(required - set(config))}, "
            f"unknown={sorted(set(config) - required)}"
        )
    if config["schema_version"] != "vdp-dynamics-screening-config/1":
        raise ValueError("unsupported dynamics screening configuration schema")
    if config["configuration_version"] != 1:
        raise ValueError("unsupported dynamics screening configuration version")
    if config["frozen_before_issue_7_interval_run"] != "2026-08-27":
        raise ValueError("the Issue #7 preregistration date changed")
    if config["evidence_status"] != (
        "DERIVED_FORMULAS + COMPUTED/E1 NONRIGOROUS_PRESCREEN"
    ):
        raise ValueError("the dynamics-screening evidence status changed")
    baseline = config["source_candidate_baseline"]
    if set(baseline) != {"commit", "tag", "results_directory"}:
        raise ValueError("source_candidate_baseline interface drift")
    if baseline != {
        "commit": "61ac680",
        "tag": "vdp-v4-screening-baseline",
        "results_directory": "numerics/results/vdp_v1_v7",
    }:
        raise ValueError("the frozen V1--V7 candidate baseline changed")
    primary = config["primary_parameters"]
    if set(primary) != {"r", "a2", "epsilon"}:
        raise ValueError("primary_parameters must contain exactly r,a2,epsilon")
    if float(primary["r"]) <= 0.0 or float(primary["epsilon"]) <= 0.0:
        raise ValueError("primary r and epsilon must be positive")
    box = config["issue_7_preselected_box"]
    if set(box) != {
        "selection_status",
        "selection_rule",
        "r",
        "a2",
        "epsilon",
        "immutability_rule",
    }:
        raise ValueError("issue_7_preselected_box interface drift")
    for variable in ("r", "a2", "epsilon"):
        endpoints = box[variable]
        if len(endpoints) != 2 or float(endpoints[1]) < float(endpoints[0]):
            raise ValueError(f"invalid preselected {variable} interval")
    if float(box["r"][0]) <= 0.0 or float(box["epsilon"][0]) <= 0.0:
        raise ValueError("preselected r and epsilon boxes must be positive")
    if box["selection_status"] != "PRESELECTED_BEFORE_FIRST_OUTWARD_ROUNDED_RUN":
        raise ValueError("the Issue #7 parameter-box selection status changed")
    frozen_box = {"r": [0.04, 0.08], "a2": [-0.25, 0.25], "epsilon": [0.8, 1.2]}
    if any(list(box[name]) != endpoints for name, endpoints in frozen_box.items()):
        raise ValueError("the preregistered Issue #7 parameter box changed")
    expected_nested_keys = {
        "turing": {
            "primary_k_grid",
            "remote_nonclassical_a2",
            "threshold_r_grid",
            "frozen_parameter_slices",
            "wide_r_grid",
            "wide_a2_grid",
            "wide_epsilon_log_grid",
        },
        "periodic_bloch": {
            "profile_labels",
            "theta_grid",
            "grid_points",
            "coarse_grid_points",
            "leading_count",
            "refinement_theta",
            "instability_tolerance",
        },
        "multipulse_temporal": {
            "pulse_counts",
            "grid_points",
            "coarse_grid_points",
            "refined_maximum_cell_width",
            "coarse_refined_maximum_cell_width",
            "final_time",
            "time_step",
            "perturbation_amplitude",
            "leading_count",
        },
        "canard": {"positive_fold", "fold_collar", "reference_curve"},
        "qa": {
            "bloch_constant_dispersion_defect_max",
            "bloch_conjugacy_defect_max",
            "bloch_translation_vector_residual_max",
            "bloch_refinement_defect_max",
            "pulse_homogeneous_fourier_defect_max",
            "pulse_leading_mode_eigenpair_residual_max",
            "pulse_zero_perturbation_defect_max",
            "pulse_spectral_grid_abscissa_difference_max",
            "pulse_spectral_boundary_abscissa_difference_max",
            "pulse_time_step_final_state_difference_max",
            "pulse_grid_final_state_difference_max",
            "pulse_boundary_final_state_difference_max",
            "pulse_leading_mode_envelope_amplification_difference_max",
        },
    }
    for section, keys in expected_nested_keys.items():
        if set(config[section]) != keys:
            raise ValueError(f"{section} interface drift")
    if tuple(config["periodic_bloch"]["profile_labels"]) != (
        "A0",
        "B0",
        "A1",
        "B1",
        "A2",
    ):
        raise ValueError("the frozen periodic-profile census changed")
    if tuple(config["multipulse_temporal"]["pulse_counts"]) != (1, 2, 3, 4):
        raise ValueError("the frozen multipulse-profile census changed")
    _grid(config["turing"]["primary_k_grid"], name="primary_k_grid")
    _grid(config["turing"]["threshold_r_grid"], name="threshold_r_grid")
    _grid(config["turing"]["wide_r_grid"], name="wide_r_grid")
    _grid(config["turing"]["wide_a2_grid"], name="wide_a2_grid")
    wide_epsilon_grid = _grid(
        config["turing"]["wide_epsilon_log_grid"],
        name="wide_epsilon_log_grid",
    )
    if float(wide_epsilon_grid[0]) <= 0.0:
        raise ValueError("wide_epsilon_log_grid must have positive endpoints")
    frozen_slices = config["turing"]["frozen_parameter_slices"]
    if set(frozen_slices) != {"r", "a2", "epsilon"}:
        raise ValueError("turing frozen_parameter_slices interface drift")
    _grid(config["periodic_bloch"]["theta_grid"], name="theta_grid")
    if canonical_json_sha256(config) != FROZEN_CONFIG_V1_CANONICAL_SHA256:
        raise ValueError(
            "frozen v1 configuration values changed; bump configuration version"
        )


def _copy_profile_arrays(source: Path, output: Path) -> None:
    payload: dict[str, np.ndarray] = {}
    with np.load(source / "v7_periodic.npz", allow_pickle=False) as archive:
        for label in ("A0", "A2"):
            for suffix in ("physical_x", "physical_u", "physical_v"):
                payload[f"periodic_{label}_{suffix}"] = np.asarray(
                    archive[f"{label}_{suffix}"]
                )
    with np.load(source / "v7_multipulses.npz", allow_pickle=False) as archive:
        for pulse_count in range(1, 5):
            for suffix in ("physical_x", "physical_u", "physical_v"):
                key = f"pulse_{pulse_count}_{suffix}"
                payload[key] = np.asarray(archive[key])
    with np.load(
        source / "v4_v5_matched_candidate.npz", allow_pickle=False
    ) as archive:
        compact_q = np.asarray(archive["compact_q"])
        payload["outer_compact_q"] = compact_q
        payload["outer_physical_u"] = np.sqrt(compact_q)
    np.savez_compressed(output, **payload)


def _pulse_qa(report: Mapping[str, Any], limits: Mapping[str, float]) -> dict[str, Any]:
    homogeneous_rows = report["homogeneous_fourier_validation"][
        "finite_volume_matrix_vs_analytic_discrete_modes"
    ]
    homogeneous_defect = max(
        float(row["maximum_eigenvalue_matching_error"])
        for row in homogeneous_rows.values()
    )
    eigenpair_residual = max(
        float(profile["sensitivity"]["leading_mode_complex_eigenpair_relative_residual"])
        for profile in report["profiles"]
    )
    zero_defect = max(
        float(run["zero_perturbation_defect_inf"])
        for profile in report["profiles"]
        for run in profile["short_time_runs"].values()
    )
    spectral_grid_difference = max(
        float(profile["sensitivity"]["spectral_grid_abscissa_difference"])
        for profile in report["profiles"]
    )
    spectral_boundary_difference = max(
        float(profile["sensitivity"]["spectral_boundary_abscissa_difference"])
        for profile in report["profiles"]
    )
    time_step_difference = max(
        float(
            profile["sensitivity"][
                "time_step_final_state_difference_over_initial_rms"
            ]
        )
        for profile in report["profiles"]
    )
    grid_difference = max(
        float(
            profile["sensitivity"]["grid_final_state_difference_over_initial_rms"]
        )
        for profile in report["profiles"]
    )
    boundary_difference = max(
        float(
            profile["sensitivity"][
                "boundary_final_state_difference_over_initial_rms"
            ]
        )
        for profile in report["profiles"]
    )
    envelope_difference = max(
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
        for profile in report["profiles"]
    )
    checks = {
        "homogeneous_fourier_crosscheck": {
            "value": homogeneous_defect,
            "limit": float(limits["pulse_homogeneous_fourier_defect_max"]),
            "passed": homogeneous_defect
            <= float(limits["pulse_homogeneous_fourier_defect_max"]),
        },
        "leading_mode_eigenpair_residual": {
            "value": eigenpair_residual,
            "limit": float(limits["pulse_leading_mode_eigenpair_residual_max"]),
            "passed": eigenpair_residual
            <= float(limits["pulse_leading_mode_eigenpair_residual_max"]),
        },
        "zero_perturbation_invariance": {
            "value": zero_defect,
            "limit": float(limits["pulse_zero_perturbation_defect_max"]),
            "passed": zero_defect
            <= float(limits["pulse_zero_perturbation_defect_max"]),
        },
        "spectral_grid_abscissa_sensitivity": {
            "value": spectral_grid_difference,
            "limit": float(
                limits["pulse_spectral_grid_abscissa_difference_max"]
            ),
            "passed": spectral_grid_difference
            <= float(limits["pulse_spectral_grid_abscissa_difference_max"]),
        },
        "spectral_boundary_abscissa_sensitivity": {
            "value": spectral_boundary_difference,
            "limit": float(
                limits["pulse_spectral_boundary_abscissa_difference_max"]
            ),
            "passed": spectral_boundary_difference
            <= float(limits["pulse_spectral_boundary_abscissa_difference_max"]),
        },
        "time_step_final_state_sensitivity": {
            "value": time_step_difference,
            "limit": float(limits["pulse_time_step_final_state_difference_max"]),
            "passed": time_step_difference
            <= float(limits["pulse_time_step_final_state_difference_max"]),
        },
        "grid_final_state_sensitivity": {
            "value": grid_difference,
            "limit": float(limits["pulse_grid_final_state_difference_max"]),
            "passed": grid_difference
            <= float(limits["pulse_grid_final_state_difference_max"]),
        },
        "boundary_final_state_sensitivity": {
            "value": boundary_difference,
            "limit": float(limits["pulse_boundary_final_state_difference_max"]),
            "passed": boundary_difference
            <= float(limits["pulse_boundary_final_state_difference_max"]),
        },
        "leading_mode_envelope_amplification_sensitivity": {
            "value": envelope_difference,
            "limit": float(
                limits[
                    "pulse_leading_mode_envelope_amplification_difference_max"
                ]
            ),
            "passed": envelope_difference
            <= float(
                limits[
                    "pulse_leading_mode_envelope_amplification_difference_max"
                ]
            ),
        },
    }
    return checks


def _bloch_qa(result: Any, limits: Mapping[str, float]) -> dict[str, Any]:
    finite_conjugacy = result.conjugacy_defects[np.isfinite(result.conjugacy_defects)]
    conjugacy = float(np.max(finite_conjugacy)) if finite_conjugacy.size else np.inf
    translation = float(np.max(result.translation_residuals))
    finite_refinement = result.refinement_defects[
        np.isfinite(result.refinement_defects)
    ]
    refinement = (
        float(np.max(finite_refinement)) if finite_refinement.size else np.inf
    )
    checks = {
        "constant_profile_dispersion_crosscheck": {
            "value": float(result.constant_dispersion_defect),
            "limit": float(limits["bloch_constant_dispersion_defect_max"]),
            "passed": float(result.constant_dispersion_defect)
            <= float(limits["bloch_constant_dispersion_defect_max"]),
        },
        "bloch_conjugacy_crosscheck": {
            "value": conjugacy,
            "limit": float(limits["bloch_conjugacy_defect_max"]),
            "passed": conjugacy <= float(limits["bloch_conjugacy_defect_max"]),
        },
        "translation_vector_residual": {
            "value": translation,
            "limit": float(limits["bloch_translation_vector_residual_max"]),
            "passed": translation
            <= float(limits["bloch_translation_vector_residual_max"]),
        },
        "grid_refinement_matching_defect": {
            "value": refinement,
            "limit": float(limits["bloch_refinement_defect_max"]),
            "passed": refinement <= float(limits["bloch_refinement_defect_max"]),
        },
    }
    return checks


def build_decision_record(
    config: Mapping[str, Any],
    turing_report: Mapping[str, Any],
    bloch_report: Mapping[str, Any],
    pulse_report: Mapping[str, Any],
    canard_report: Mapping[str, Any],
) -> dict[str, Any]:
    pulse_signals = {
        str(profile["profile"]): str(profile["screen_signal"])
        for profile in pulse_report["profiles"]
    }
    return {
        "schema_version": "vdp-dynamics-screening-decision/1",
        "evidence_status": config["evidence_status"],
        "claim_bearing": False,
        "issue_7_preselected_box": config["issue_7_preselected_box"],
        "conclusions": {
            "classical_stationary_turing": {
                "status": "ANALYTICALLY_EXCLUDED_FOR_THE_HOMOGENEOUS_STATE",
                "reason": turing_report["primary"]["stationary"]["obstruction"],
                "relation_to_v7": (
                    "V7 profiles arise from global stationary spatial dynamics; "
                    "their existence does not require a local Turing bifurcation."
                ),
            },
            "periodic_profile_temporal_screen": {
                "status": bloch_report["screening_outcome"],
                "profile_outcomes": {
                    str(row["label"]): str(row["screening_outcome"])
                    for row in bloch_report["profiles"]
                },
                "next_required": (
                    "Converged Evans/Bloch analysis and, only if spectrally viable, "
                    "nonlinear orbital stability."
                ),
            },
            "multipulse_temporal_screen": {
                "status": "FINITE_WINDOW_AND_SHORT_TIME_SIGNALS_RECORDED",
                "profile_signals": pulse_signals,
                "next_required": (
                    "Whole-line essential/point spectrum, Evans enclosures, and "
                    "nonlinear semigroup estimates."
                ),
            },
            "canard": {
                "status": canard_report["canard_identification_status"],
                "singular_reduced_classification": canard_report[
                    "positive_fold_singular_reduced_classification"
                ],
                "next_required": canard_report["required_before_canard_claim"],
            },
            "issue_7": {
                "status": "PROCEED_WITH_EXISTENCE_VALIDATION_ON_PRESELECTED_BOX",
                "scope": (
                    "The box targets the V2--V7 stationary spatial existence/coding "
                    "obligations.  It is deliberately not a temporal-stability box."
                ),
            },
        },
        "ordering": [
            "freeze this screening and parameter-box input",
            "run outward-rounded Issue #7 obligations",
            "retain PASS/FAIL/INCONCLUSIVE without moving the box",
            "then continue periodic/pulse dynamics and canard branches as separate research",
        ],
        "nonclaims": list(config["nonclaims"]),
    }


def run(
    config_path: Path,
    output: Path,
    *,
    allow_dirty_source: bool = False,
) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    validate_config(config)
    source_revision_at_start = git_text("rev-parse", "HEAD")
    if source_revision_at_start == "UNAVAILABLE" or len(source_revision_at_start) != 40:
        raise RuntimeError("cannot resolve repository HEAD before dynamics screening")
    source_status_at_start = git_text("status", "--porcelain", "--untracked-files=all")
    if source_status_at_start == "UNAVAILABLE":
        raise RuntimeError("cannot inspect repository cleanliness before screening")
    source_dirty_at_start = bool(source_status_at_start)
    if source_dirty_at_start and not allow_dirty_source:
        raise RuntimeError(
            "official dynamics screening requires a clean repository; "
            "use --allow-dirty-source only for an explicitly development-only artifact"
        )
    run_mode = DEVELOPMENT_RUN_MODE if allow_dirty_source else OFFICIAL_RUN_MODE
    candidate_revision_at_start = resolve_candidate_baseline(config)
    candidate_git_blobs_at_start = verify_baseline_git_blobs(
        config, resolved_revision=candidate_revision_at_start
    )
    source_hashes_at_start = source_file_hashes(config_path, config)
    source_revision_git_blobs = (
        None
        if allow_dirty_source
        else verify_source_commit_blobs(
            config_path,
            config,
            revision=source_revision_at_start,
            current_hashes=source_hashes_at_start,
        )
    )
    output.mkdir(parents=True, exist_ok=True)
    source = ROOT / config["source_candidate_baseline"]["results_directory"]
    if not source.is_dir():
        raise FileNotFoundError(f"frozen V1--V7 results are missing: {source}")

    primary_values = config["primary_parameters"]
    primary_turing = TuringParameters(**primary_values)
    primary_pulse = PulseTemporalParameters(**primary_values)

    turing_report = build_prescreen_report(config)
    write_json(output / "turing_report.json", turing_report)
    k = _grid(config["turing"]["primary_k_grid"], name="primary_k_grid")
    remote = TuringParameters(
        r=primary_turing.r,
        a2=float(config["turing"]["remote_nonclassical_a2"]),
        epsilon=primary_turing.epsilon,
    )
    primary_curve = dispersion_curve(primary_turing, k)
    remote_curve = dispersion_curve(remote, k)
    r_threshold = _grid(
        config["turing"]["threshold_r_grid"], name="threshold_r_grid"
    )
    thresholds = threshold_curve(r_threshold, primary_turing.epsilon)
    np.savez_compressed(
        output / "turing_arrays.npz",
        **{f"primary_{key}": np.asarray(value) for key, value in primary_curve.items()},
        **{f"remote_{key}": np.asarray(value) for key, value in remote_curve.items()},
        **{f"threshold_{key}": np.asarray(value) for key, value in thresholds.items()},
    )

    bloch_config = config["periodic_bloch"]
    theta = _grid(bloch_config["theta_grid"], name="theta_grid")
    bloch_result = screen_saved_periodic_profiles(
        source / "v7_periodic.npz",
        labels=tuple(bloch_config["profile_labels"]),
        theta=theta,
        grid_points=int(bloch_config["grid_points"]),
        coarse_grid_points=int(bloch_config["coarse_grid_points"]),
        leading_count=int(bloch_config["leading_count"]),
        refinement_theta=tuple(bloch_config["refinement_theta"]),
        d=primary_turing.d,
        epsilon=primary_turing.epsilon,
        homogeneous_u=primary_turing.a,
        instability_tolerance=float(bloch_config["instability_tolerance"]),
    )
    write_screening_outputs(
        bloch_result,
        npz_path=output / "bloch_arrays.npz",
        json_path=output / "bloch_report.json",
    )
    bloch_report = bloch_result.as_report()

    pulse_config = config["multipulse_temporal"]
    pulse_report = run_temporal_prescreen(
        source / "v7_multipulses.npz",
        parameters=primary_pulse,
        pulse_counts=tuple(int(value) for value in pulse_config["pulse_counts"]),
        grid_points=int(pulse_config["grid_points"]),
        coarse_grid_points=int(pulse_config["coarse_grid_points"]),
        final_time=float(pulse_config["final_time"]),
        dt=float(pulse_config["time_step"]),
        amplitude=float(pulse_config["perturbation_amplitude"]),
        leading_count=int(pulse_config["leading_count"]),
        refined_maximum_cell_width=float(
            pulse_config["refined_maximum_cell_width"]
        ),
        coarse_refined_maximum_cell_width=float(
            pulse_config["coarse_refined_maximum_cell_width"]
        ),
    )
    write_json(output / "pulse_temporal_report.json", pulse_report)

    canard_report = screen_saved_profiles(
        source,
        r=primary_turing.r,
        a2=primary_turing.a2,
        epsilon=primary_turing.epsilon,
        fold=float(config["canard"]["positive_fold"]),
        fold_collar=float(config["canard"]["fold_collar"]),
        reference_curve=str(config["canard"]["reference_curve"]),
    )
    write_json(output / "canard_report.json", canard_report)
    _copy_profile_arrays(source, output / "screening_profiles.npz")

    qa_checks = {
        **{f"bloch.{key}": value for key, value in _bloch_qa(bloch_result, config["qa"]).items()},
        **{f"pulse.{key}": value for key, value in _pulse_qa(pulse_report, config["qa"]).items()},
        "turing.primary_classification": {
            "value": turing_report["primary"]["homogeneous_status"],
            "expected": HOPF_BOUNDARY_K0,
            "passed": turing_report["primary"]["homogeneous_status"]
            == HOPF_BOUNDARY_K0,
        },
        "turing.classical_obstruction_scan": {
            "value": turing_report["wide_diagnostic_domain"]["scan"][
                "classical_stationary_turing_point_count"
            ],
            "expected": 0,
            "passed": turing_report["wide_diagnostic_domain"]["scan"][
                "classical_stationary_turing_point_count"
            ]
            == 0,
        },
        "canard.stop_rule_preserved": {
            "value": canard_report["canard_identification_status"],
            "expected": CANARD_STOP_STATUS,
            "passed": canard_report["canard_identification_status"]
            == CANARD_STOP_STATUS,
        },
        "canard.outer_fold_exclusion": {
            "value": canard_report["outer_diagnostics"]["crosses_a_fold"],
            "expected": False,
            "passed": not canard_report["outer_diagnostics"]["crosses_a_fold"],
        },
    }
    qa = {
        "schema_version": "vdp-dynamics-screening-qa/1",
        "status": (
            "PASS_COMPUTATIONAL_QA_NOT_A_THEOREM"
            if all(row["passed"] for row in qa_checks.values())
            else "FAIL_COMPUTATIONAL_QA"
        ),
        "claim_bearing": False,
        "checks": qa_checks,
        "passed_count": sum(bool(row["passed"]) for row in qa_checks.values()),
        "check_count": len(qa_checks),
    }
    write_json(output / "qa.json", qa)

    decision = build_decision_record(
        config, turing_report, bloch_report, pulse_report, canard_report
    )
    write_json(output / "decision.json", decision)

    source_revision_at_end = git_text("rev-parse", "HEAD")
    candidate_revision_at_end = resolve_candidate_baseline(config)
    candidate_git_blobs_at_end = verify_baseline_git_blobs(
        config, resolved_revision=candidate_revision_at_end
    )
    source_hashes_at_end = source_file_hashes(config_path, config)
    verify_unchanged_source_snapshot(
        source_hashes_at_start,
        source_hashes_at_end,
        start_revision=source_revision_at_start,
        end_revision=source_revision_at_end,
        start_baseline_revision=candidate_revision_at_start,
        end_baseline_revision=candidate_revision_at_end,
    )
    if candidate_git_blobs_at_start != candidate_git_blobs_at_end:
        raise RuntimeError("candidate baseline Git blobs changed during screening")

    render_contract = {
        "schema_version": SCREENING_SCHEMA,
        "configuration_version": config["configuration_version"],
        "configuration_sha256": sha256(config_path),
        "candidate_baseline": config["source_candidate_baseline"],
        "candidate_tag_resolved": candidate_revision_at_start,
        "candidate_baseline_git_blobs": candidate_git_blobs_at_start,
        "run_mode": run_mode,
        "source_revision_at_run_start": source_revision_at_start,
        "source_revision_at_run_end": source_revision_at_end,
        "source_revision_git_blobs": source_revision_git_blobs,
        "source_dirty_at_run_start": source_dirty_at_start,
        "source_files": source_hashes_at_start,
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "matplotlib": matplotlib.__version__,
            "platform": platform.platform(),
        },
        "qa_status": qa["status"],
        "claim_bearing": False,
    }
    write_json(output / "render_contract.json", render_contract)

    from numerics.render_vdp_dynamics_figures import render_all  # noqa: E402

    render_all(output, config_path=config_path)

    # The renderer consumes bound source too, so repeat the endpoint check
    # after every figure has been written and before the manifest is sealed.
    source_revision_after_render = git_text("rev-parse", "HEAD")
    candidate_revision_after_render = resolve_candidate_baseline(config)
    candidate_git_blobs_after_render = verify_baseline_git_blobs(
        config, resolved_revision=candidate_revision_after_render
    )
    source_hashes_after_render = source_file_hashes(config_path, config)
    verify_unchanged_source_snapshot(
        source_hashes_at_start,
        source_hashes_after_render,
        start_revision=source_revision_at_start,
        end_revision=source_revision_after_render,
        start_baseline_revision=candidate_revision_at_start,
        end_baseline_revision=candidate_revision_after_render,
    )
    if candidate_git_blobs_at_start != candidate_git_blobs_after_render:
        raise RuntimeError("candidate baseline Git blobs changed during rendering")

    generated_files = sorted(
        path for path in output.iterdir() if path.is_file() and path.name != "manifest.json"
    )
    manifest = {
        **render_contract,
        "output_files": {
            path.name: {"sha256": sha256(path), "bytes": path.stat().st_size}
            for path in generated_files
        },
        "screening_decision": decision["conclusions"],
        "final_status": qa["status"],
        "nonclaim": (
            "This manifest binds a non-rigorous dynamics prescreen. It is not "
            "outward-rounded Issue #7 validation or a stability/canard theorem."
        ),
    }
    write_json(output / "manifest.json", manifest)
    return {
        "qa": qa,
        "decision": decision,
        "bloch_sampled_instability": bloch_report["screening_outcome"]
        == SAMPLED_INSTABILITY,
        "output": str(output),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--allow-dirty-source",
        action="store_true",
        help=(
            "permit a dirty worktree only for an explicitly development-only "
            "artifact; the default official run refuses it"
        ),
    )
    arguments = parser.parse_args(argv)
    summary = run(
        arguments.config.resolve(),
        arguments.output.resolve(),
        allow_dirty_source=arguments.allow_dirty_source,
    )
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False))
    return 0 if summary["qa"]["status"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
