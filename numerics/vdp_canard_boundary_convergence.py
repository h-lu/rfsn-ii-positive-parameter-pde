"""Three-boundary Appendix-A.2/A.3 finite-boundary canard scout."""

from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
from typing import Any
import warnings

import numpy as np
from scipy.integrate import solve_bvp, solve_ivp

try:
    from numerics.vdp_canard_slow_trace import (
        SlowTraceConfiguration,
        _fixed_section_state,
        _localized_a3_half,
        _outside_half,
        critical_graph,
        load_configuration as load_slow_configuration,
        vectorized_central_field,
    )
    from numerics.vdp_canard_splitting_scout import (
        central_hamiltonian,
        formal_canard_jet,
    )
except ModuleNotFoundError:  # Direct ``python numerics/<script>.py`` execution.
    from vdp_canard_slow_trace import (  # type: ignore[no-redef]
        SlowTraceConfiguration,
        _fixed_section_state,
        _localized_a3_half,
        _outside_half,
        critical_graph,
        load_configuration as load_slow_configuration,
        vectorized_central_field,
    )
    from vdp_canard_splitting_scout import (  # type: ignore[no-redef]
        central_hamiltonian,
        formal_canard_jet,
    )


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent
CONFIG_PATH = HERE / "config" / "vdp_canard_boundary_convergence_v1.json"
RESULT_PATH = (
    HERE / "results" / "vdp_canard_boundary_convergence" / "report.json"
)


class BoundaryConvergenceError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_configuration(path: Path = CONFIG_PATH) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("schema_version") != (
        "vdp-canard-boundary-convergence-config/1"
    ):
        raise BoundaryConvergenceError("configuration schema changed")
    if config.get("freeze_status") != "FROZEN_BEFORE_FIRST_THREE_BOUNDARY_RUN":
        raise BoundaryConvergenceError("configuration was not pre-run frozen")
    if config.get("outer_q2_boundaries") != [-60.0, -80.0, -100.0]:
        raise BoundaryConvergenceError("the three outer boundaries changed")
    if config.get("claim_bearing") is not False:
        raise BoundaryConvergenceError("scout cannot be claim-bearing")
    for binding in config["base_inputs"]:
        if _sha256(REPOSITORY / binding["path"]) != binding["sha256"]:
            raise BoundaryConvergenceError(
                f"base input changed: {binding['path']}"
            )
    return config


def _state(state: np.ndarray) -> list[float]:
    return [float(value) for value in state]


def _common_section_entry(
    solution: Any,
    configuration: SlowTraceConfiguration,
    scout: dict[str, Any],
) -> tuple[np.ndarray, str]:
    section = scout["common_section"]
    target = float(section["u2"])
    left = np.asarray(solution.sol(0.0), dtype=np.float64)
    if left[0] >= target:
        _, entry = _fixed_section_state(solution, target)
        return entry, "A3_HALF_BVP_INTERPOLANT"
    if not section["allow_exact_backward_ivp_extension"]:
        raise RuntimeError("outer boundary lies inside u2=16 and extension is disabled")

    def event(_time: float, state: np.ndarray) -> float:
        return float(state[0] - target)

    event.terminal = True  # type: ignore[attr-defined]
    event.direction = 0.0  # type: ignore[attr-defined]
    extension = solve_ivp(
        lambda _time, state: vectorized_central_field(
            state[:, None], r=configuration.r, a2=float(solution.p[1])
        )[:, 0],
        (0.0, -float(section["extension_max_time"])),
        left,
        events=event,
        rtol=float(section["extension_rtol"]),
        atol=float(section["extension_atol"]),
        max_step=float(section["extension_max_step"]),
    )
    if not extension.success or not extension.t_events[0].size:
        raise RuntimeError("exact backward IVP did not reach u2=16")
    return (
        np.asarray(extension.y_events[0][0], dtype=np.float64),
        "EXACT_FIELD_BACKWARD_IVP_EXTENSION",
    )


def _fixed_boundary_splitting_attempts(
    root: Any,
    configuration: SlowTraceConfiguration,
    scout: dict[str, Any],
    outer_u: float,
    outer_q: float,
) -> dict[str, Any]:
    derivative = scout["finite_boundary_splitting_derivative"]
    center = float(root.p[1])
    mesh = np.linspace(0.0, 1.0, configuration.half_mesh_points)
    attempts: list[dict[str, Any]] = []
    successful: dict[tuple[float, int], float] = {}

    for step in derivative["a2_steps"]:
        h = float(step)
        for sign in (-1, 1):
            a2 = center + sign * h

            def field(_s: np.ndarray, state: np.ndarray, parameter: np.ndarray) -> np.ndarray:
                return parameter[0] * vectorized_central_field(
                    state, r=configuration.r, a2=a2
                )

            def boundary(
                left: np.ndarray, right: np.ndarray, _parameter: np.ndarray
            ) -> np.ndarray:
                return np.asarray(
                    [
                        left[0] - outer_u,
                        left[2] - critical_graph(left[0], r=configuration.r),
                        left[3] - outer_q,
                        central_hamiltonian(left, r=configuration.r, a2=a2),
                        right[1],
                    ]
                )

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                solution = solve_bvp(
                    field,
                    boundary,
                    mesh,
                    root.sol(mesh),
                    p=[float(root.p[0])],
                    tol=configuration.root_tolerance,
                    max_nodes=configuration.max_nodes,
                )
            record: dict[str, Any] = {
                "a2_step": h,
                "sign": sign,
                "a2": a2,
                "success": bool(solution.success),
                "message": solution.message,
                "mesh_nodes": int(solution.x.size),
                "warnings": [str(item.message) for item in caught],
            }
            if solution.rms_residuals.size:
                residual = float(np.max(solution.rms_residuals))
                record["max_interval_rms_relative_residual"] = (
                    residual if math.isfinite(residual) else None
                )
            if solution.success:
                splitting = float(solution.y[3, -1])
                record["splitting_q2"] = splitting
                successful[(h, sign)] = splitting
            attempts.append(record)

    derivatives: list[dict[str, float]] = []
    for step in derivative["a2_steps"]:
        h = float(step)
        if (h, -1) in successful and (h, 1) in successful:
            derivatives.append(
                {
                    "a2_step": h,
                    "central_difference": (
                        successful[(h, 1)] - successful[(h, -1)]
                    )
                    / (2.0 * h),
                }
            )
    complete = len(successful) == 2 * len(derivative["a2_steps"])
    return {
        "definition": derivative["definition"],
        "attempts": attempts,
        "derivative_candidates": derivatives if complete else [],
        "status": (
            "COMPUTED/E1_SYMMETRIC_COLLOCATION_DERIVATIVE_CANDIDATE"
            if complete
            else "NOT_COMPUTED_PERTURBED_COLLOCATION_FAILED"
        ),
    }


def _successful_slice(
    q0: float,
    half: Any,
    root: Any,
    configuration: SlowTraceConfiguration,
    scout: dict[str, Any],
) -> dict[str, Any]:
    outer_u = float(half.y[0, 0])
    entry, entry_source = _common_section_entry(root, configuration, scout)
    a2 = float(root.p[1])
    sample = np.linspace(0.0, 1.0, 4001)
    states = np.asarray(root.sol(sample), dtype=np.float64)
    left, right = states[:, 0], states[:, -1]
    energies = np.asarray(
        [
            central_hamiltonian(states[:, index], r=configuration.r, a2=a2)
            for index in range(states.shape[1])
        ]
    )
    open_states = states[:, 1:-1]
    no_loop = bool(np.max(open_states[1]) < 0.0 and np.max(open_states[3]) < 0.0)
    formal = formal_canard_jet(0.0, r=configuration.r, a2=a2, order=3)
    localization_difference = right - formal
    localized = bool(
        abs(localization_difference[0])
        < configuration.central_localization_u2_tolerance
        and abs(localization_difference[2])
        < configuration.central_localization_v2_tolerance
    )
    boundary_residuals = [
        left[0] - outer_u,
        left[2] - critical_graph(left[0], r=configuration.r),
        left[3] - q0,
        right[1],
        right[3],
        central_hamiltonian(left, r=configuration.r, a2=a2),
    ]
    return {
        "outer_q2": q0,
        "status": "COMPUTED/E1_FINITE_BOUNDARY_A3_CANDIDATE",
        "outer_entry_pair": {"u_star": outer_u, "q_star": q0},
        "a2_candidate": a2,
        "half_flight_time": float(root.p[0]),
        "common_section_entry": _state(entry),
        "common_section_entry_source": entry_source,
        "common_section_entry_hamiltonian": central_hamiltonian(
            entry, r=configuration.r, a2=a2
        ),
        "reverser_endpoint": _state(right),
        "boundary_residual_inf": float(np.max(np.abs(boundary_residuals))),
        "max_interval_rms_relative_residual": float(
            np.max(root.rms_residuals)
        ),
        "hamiltonian_drift": float(np.ptp(energies)),
        "primary_no_loop_sample_pass": no_loop,
        "central_localization_pass": localized,
        "central_localization_difference_from_formal_diagnostic": _state(
            localization_difference
        ),
        "splitting_a2_derivative": _fixed_boundary_splitting_attempts(
            root, configuration, scout, outer_u, q0
        ),
    }


def compute_slice(
    q0: float,
    base: SlowTraceConfiguration,
    scout: dict[str, Any],
) -> dict[str, Any]:
    interval = scout["parameters"]["a2_candidate_interval"]
    configuration = replace(
        base,
        outer_q_boundary=q0,
        a3_candidate_a2_interval=(float(interval[0]), float(interval[1])),
    )
    try:
        half = _outside_half(configuration)
    except RuntimeError as error:
        return {
            "outer_q2": q0,
            "status": "FAILED_A2_PRIMARY_BRANCH_CONTINUATION",
            "failure": str(error),
            "outer_entry_pair": None,
            "a2_candidate": None,
            "common_section_entry": None,
            "reverser_endpoint": None,
            "splitting_a2_derivative": None,
        }
    outer_u = float(half.y[0, 0])
    configuration = replace(configuration, a3_outer_u2_boundary=outer_u)
    try:
        root = _localized_a3_half(configuration, half)
        return _successful_slice(q0, half, root, configuration, scout)
    except RuntimeError as error:
        return {
            "outer_q2": q0,
            "status": "FAILED_A3_ZERO_ENERGY_HALF_BVP",
            "failure": str(error),
            "outer_entry_pair": {"u_star": outer_u, "q_star": q0},
            "a2_candidate": None,
            "common_section_entry": None,
            "reverser_endpoint": None,
            "splitting_a2_derivative": None,
        }


def _comparisons(rows: list[dict[str, Any]]) -> dict[str, Any]:
    successful = [row for row in rows if row["a2_candidate"] is not None]
    pairs: list[dict[str, Any]] = []
    for previous, current in zip(successful, successful[1:]):
        entry_previous = np.asarray(previous["common_section_entry"])
        entry_current = np.asarray(current["common_section_entry"])
        endpoint_previous = np.asarray(previous["reverser_endpoint"])
        endpoint_current = np.asarray(current["reverser_endpoint"])
        pairs.append(
            {
                "from_q2": previous["outer_q2"],
                "to_q2": current["outer_q2"],
                "entry_state_inf": float(
                    np.max(np.abs(entry_current - entry_previous))
                ),
                "a2_candidate_abs": abs(
                    float(current["a2_candidate"])
                    - float(previous["a2_candidate"])
                ),
                "reverser_state_inf": float(
                    np.max(np.abs(endpoint_current - endpoint_previous))
                ),
            }
        )
    return {
        "successive_pairs": pairs,
        "three_slice_convergence_status": (
            "DESCRIPTIVE_ONLY_ALL_THREE_AVAILABLE"
            if len(successful) == 3
            else "NOT_TESTED_MISSING_SLICE"
        ),
    }


def build_report(config_path: Path = CONFIG_PATH) -> dict[str, Any]:
    scout = load_configuration(config_path)
    base = load_slow_configuration()
    rows = [
        compute_slice(float(q0), base, scout)
        for q0 in scout["outer_q2_boundaries"]
    ]
    return {
        "schema_version": "vdp-canard-boundary-convergence-report/1",
        "evidence_status": "COMPUTED/E1_PARTIAL_THREE_BOUNDARY_SCOUT",
        "claim_bearing": False,
        "configuration": {
            "path": str(config_path.relative_to(REPOSITORY)),
            "sha256": _sha256(config_path),
            "freeze_status": scout["freeze_status"],
        },
        "parameters": scout["parameters"],
        "slices": rows,
        "comparison": _comparisons(rows),
        "decision": {
            "status": "PARTIAL_Q60_A2_CONTINUATION_FAILED",
            "intrinsic_canard": "NOT_CLAIMED_FINITE_BOUNDARY_OBJECTS_ONLY",
            "splitting_derivative": (
                "NOT_COMPUTED_PERTURBED_COLLOCATION_FAILED"
            ),
        },
        "nonclaims": scout["nonclaims"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configuration", type=Path, default=CONFIG_PATH)
    parser.add_argument("--output", type=Path, default=RESULT_PATH)
    arguments = parser.parse_args()
    try:
        report = build_report(arguments.configuration.resolve())
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report["decision"], indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, BoundaryConvergenceError) as error:
        print(f"BOUNDARY CONVERGENCE SCOUT REJECTED: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
