"""Direct-IVP splitting and parameter-variation check for two finite boundaries."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp

try:
    from numerics.vdp_canard_slow_trace import critical_graph
    from numerics.vdp_canard_splitting_scout import central_hamiltonian
except ModuleNotFoundError:  # Direct ``python numerics/<script>.py`` execution.
    from vdp_canard_slow_trace import critical_graph  # type: ignore[no-redef]
    from vdp_canard_splitting_scout import (  # type: ignore[no-redef]
        central_hamiltonian,
    )


HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config" / "vdp_canard_boundary_convergence_v1.json"
FAMILY_PATH = (
    HERE / "results" / "vdp_canard_boundary_convergence" / "report.json"
)
RESULT_PATH = HERE / "results" / "vdp_canard_direct_splitting" / "report.json"


class DirectSplittingError(ValueError):
    pass


def _load_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    families = json.loads(FAMILY_PATH.read_text(encoding="utf-8"))
    if config.get("freeze_status") != "FROZEN_BEFORE_FIRST_THREE_BOUNDARY_RUN":
        raise DirectSplittingError("boundary/step configuration is not frozen")
    if config["finite_boundary_splitting_derivative"]["a2_steps"] != [
        2e-05,
        1e-05,
    ]:
        raise DirectSplittingError("the predeclared a2 steps changed")
    successful = [
        row
        for row in families["slices"]
        if row["status"] == "COMPUTED/E1_FINITE_BOUNDARY_A3_CANDIDATE"
    ]
    if [row["outer_q2"] for row in successful] != [-80.0, -100.0]:
        raise DirectSplittingError("the two successful boundary families changed")
    return config, families


def _initial_state_and_tangent(
    *, u: float, q: float, a2: float, r: float
) -> tuple[np.ndarray, np.ndarray, float]:
    v = float(critical_graph(u, r=r))
    radicand = (
        q * q
        - 2.0 * (u - r * a2) * v
        + 2.0 * u**3 / 3.0
        + r * r * u**4 / 6.0
    )
    if not math.isfinite(radicand) or radicand <= 0.0:
        raise DirectSplittingError(f"invalid negative-root radicand {radicand}")
    p = -math.sqrt(radicand)
    state = np.asarray([u, p, v, q], dtype=np.float64)
    # d/da2 of the unique negative H2=0 root with (u,v,q) fixed.
    tangent = np.asarray([0.0, r * v / p, 0.0, 0.0], dtype=np.float64)
    return state, tangent, central_hamiltonian(state, r=r, a2=a2)


def integrate_first_event(
    *,
    u: float,
    q: float,
    a2: float,
    r: float,
    maximum_time: float,
    rtol: float,
    atol: float,
    max_step: float,
) -> dict[str, Any]:
    state, tangent, initial_hamiltonian = _initial_state_and_tangent(
        u=u, q=q, a2=a2, r=r
    )
    initial_p2 = float(state[1])
    initial = np.concatenate((state, tangent))

    def augmented_field(_time: float, value: np.ndarray) -> np.ndarray:
        current = value[:4]
        variation = value[4:]
        current_u, current_p, current_v, current_q = current
        field = np.asarray(
            [
                current_p,
                current_u**2
                - current_v
                + r * r * current_u**3 / 3.0,
                current_q,
                current_u - r * a2,
            ]
        )
        jacobian = np.asarray(
            [
                [0.0, 1.0, 0.0, 0.0],
                [2.0 * current_u + r * r * current_u**2, 0.0, -1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [1.0, 0.0, 0.0, 0.0],
            ]
        )
        forcing = np.asarray([0.0, 0.0, 0.0, -r])
        return np.concatenate((field, jacobian @ variation + forcing))

    def p_zero(_time: float, value: np.ndarray) -> float:
        return float(value[1])

    p_zero.terminal = True  # type: ignore[attr-defined]
    p_zero.direction = 0.0  # type: ignore[attr-defined]
    solution = solve_ivp(
        augmented_field,
        (0.0, maximum_time),
        initial,
        method="DOP853",
        events=p_zero,
        dense_output=True,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    if not solution.success or not solution.t_events[0].size:
        return {
            "success": False,
            "message": solution.message,
            "event_found": bool(solution.t_events[0].size),
        }

    event_time = float(solution.t_events[0][0])
    event_augmented = np.asarray(solution.y_events[0][0], dtype=np.float64)
    event_state = event_augmented[:4]
    fixed_time_tangent = event_augmented[4:]
    field = augmented_field(event_time, event_augmented)[:4]
    p_prime = float(field[1])
    if p_prime == 0.0:
        return {
            "success": False,
            "message": "p2=0 event is non-transverse",
            "event_found": True,
        }
    event_time_tangent = -float(fixed_time_tangent[1]) / p_prime
    event_tangent = fixed_time_tangent + field * event_time_tangent

    sample_time = np.linspace(0.0, event_time, 4001)
    sample = np.asarray(solution.sol(sample_time)[:4], dtype=np.float64)
    energies = np.asarray(
        [
            central_hamiltonian(sample[:, index], r=r, a2=a2)
            for index in range(sample.shape[1])
        ]
    )
    open_sample = sample[:, :-1]
    first_event_verified = bool(np.max(open_sample[1]) < 0.0)
    no_loop = bool(first_event_verified and np.max(open_sample[3]) < 0.0)
    return {
        "success": True,
        "event_found": True,
        "initial_p2": initial_p2,
        "event_time": event_time,
        "event_u2": float(event_state[0]),
        "event_p2": float(event_state[1]),
        "event_v2": float(event_state[2]),
        "splitting_S": float(event_state[3]),
        "event_p2_prime": p_prime,
        "event_orientation": "INCREASING" if p_prime > 0.0 else "DECREASING",
        "first_event_verified": first_event_verified,
        "no_loop_to_first_event": no_loop,
        "open_max_p2": float(np.max(open_sample[1])),
        "open_max_q2": float(np.max(open_sample[3])),
        "initial_hamiltonian": initial_hamiltonian,
        "hamiltonian_drift": float(np.ptp(energies)),
        "hamiltonian_max_abs": float(np.max(np.abs(energies))),
        "dS_da2_variational": float(event_tangent[3]),
        "event_section_tangent_p2_residual": float(event_tangent[1]),
        "function_evaluations": int(solution.nfev),
    }


def _resolution_settings(config: dict[str, Any]) -> list[dict[str, float | str]]:
    section = config["common_section"]
    return [
        {
            "id": "frozen_high_accuracy",
            "rtol": float(section["extension_rtol"]),
            "atol": float(section["extension_atol"]),
            "max_step": float(section["extension_max_step"]),
        },
        {
            "id": "tight_step_halved_QA",
            "rtol": 2.5e-14,
            "atol": 1e-15,
            "max_step": 0.5 * float(section["extension_max_step"]),
        },
    ]


def compute_family(
    family: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    r = float(config["parameters"]["r"])
    center = float(family["a2_candidate"])
    outer = family["outer_entry_pair"]
    steps = [
        float(value)
        for value in config["finite_boundary_splitting_derivative"]["a2_steps"]
    ]
    offsets = [-steps[0], -steps[1], 0.0, steps[1], steps[0]]
    settings = _resolution_settings(config)
    resolutions: list[dict[str, Any]] = []
    for setting in settings:
        rows = [
            {
                "a2_offset": offset,
                "a2": center + offset,
                **integrate_first_event(
                    u=float(outer["u_star"]),
                    q=float(outer["q_star"]),
                    a2=center + offset,
                    r=r,
                    maximum_time=float(family["half_flight_time"]) + 1.0,
                    rtol=float(setting["rtol"]),
                    atol=float(setting["atol"]),
                    max_step=float(setting["max_step"]),
                ),
            }
            for offset in offsets
        ]
        by_offset = {float(row["a2_offset"]): row for row in rows}
        center_row = by_offset[0.0]
        finite_differences: list[dict[str, Any]] = []
        if all(row["success"] for row in rows):
            for step in steps:
                derivative = (
                    float(by_offset[step]["splitting_S"])
                    - float(by_offset[-step]["splitting_S"])
                ) / (2.0 * step)
                variational = float(center_row["dS_da2_variational"])
                finite_differences.append(
                    {
                        "a2_step": step,
                        "symmetric_difference": derivative,
                        "variational_at_center": variational,
                        "absolute_mismatch": abs(derivative - variational),
                        "relative_mismatch": abs(derivative - variational)
                        / max(abs(derivative), abs(variational), 1.0),
                    }
                )
        resolutions.append(
            {
                "settings": setting,
                "samples": rows,
                "finite_difference_cross_checks": finite_differences,
            }
        )

    primary_center = resolutions[0]["samples"][2]
    tight_center = resolutions[1]["samples"][2]
    all_samples = [
        sample
        for resolution in resolutions
        for sample in resolution["samples"]
    ]
    event_checks_pass = all(
        sample["success"]
        and sample["first_event_verified"]
        and sample["no_loop_to_first_event"]
        and sample["event_orientation"] == "INCREASING"
        for sample in all_samples
    )
    cross_checks = [
        check
        for resolution in resolutions
        for check in resolution["finite_difference_cross_checks"]
    ]
    derivative_cross_check_pass = bool(
        cross_checks
        and all(check["relative_mismatch"] < 0.1 for check in cross_checks)
    )
    center_is_zero_candidate = bool(
        primary_center["success"]
        and tight_center["success"]
        and abs(float(primary_center["splitting_S"])) < 1e-5
        and abs(float(tight_center["splitting_S"])) < 1e-5
    )
    center_resolution_difference = None
    if primary_center["success"] and tight_center["success"]:
        center_resolution_difference = {
            "event_time_abs": abs(
                float(primary_center["event_time"])
                - float(tight_center["event_time"])
            ),
            "splitting_abs": abs(
                float(primary_center["splitting_S"])
                - float(tight_center["splitting_S"])
            ),
            "variational_derivative_abs": abs(
                float(primary_center["dS_da2_variational"])
                - float(tight_center["dS_da2_variational"])
            ),
        }
    return {
        "outer_q2": family["outer_q2"],
        "outer_entry_pair": outer,
        "boundary_selected_a2_candidate": center,
        "resolutions": resolutions,
        "center_resolution_difference": center_resolution_difference,
        "event_checks_pass": event_checks_pass,
        "center_is_zero_candidate": center_is_zero_candidate,
        "derivative_cross_check_pass": derivative_cross_check_pass,
        "simple_zero_status": (
            "COMPUTED/E1_QA_BOUNDARY_SELECTED_SIMPLE_ZERO_CANDIDATE"
            if event_checks_pass
            and center_is_zero_candidate
            and derivative_cross_check_pass
            else "NOT_COMPUTED_DIRECT_IVP_DID_NOT_SHADOW_BVP_ZERO"
        ),
    }


def build_report() -> dict[str, Any]:
    config, families = _load_inputs()
    successful = [
        family
        for family in families["slices"]
        if family["status"] == "COMPUTED/E1_FINITE_BOUNDARY_A3_CANDIDATE"
    ]
    rows = [compute_family(family, config) for family in successful]
    return {
        "schema_version": "vdp-canard-direct-splitting-report/1",
        "evidence_status": "COMPUTED/QA_DIRECT_IVP_NONSHADOWING_RESULT",
        "claim_bearing": False,
        "definition": (
            "At fixed (u_star,q0,a2), choose the unique negative H2=0 p2 "
            "root and integrate to the first p2=0 event; S=q2 at the hit."
        ),
        "a2_steps": config["finite_boundary_splitting_derivative"]["a2_steps"],
        "families": rows,
        "decision": {
            "status": "DIRECT_IVP_DID_NOT_SHADOW_BOUNDARY_BVP_CANDIDATES",
            "boundary_selected_simple_zero": "NOT_ESTABLISHED",
            "intrinsic_maximal_canard": "NOT_CLAIMED",
            "reason": (
                "First-event and energy checks pass, but the saved BVP a2 "
                "values do not give S near zero under direct IVP, the tight "
                "replays differ, and variational derivatives disagree with "
                "both predeclared symmetric differences."
            ),
        },
        "nonclaims": [
            "This does not prove that a finite-boundary or intrinsic canard is absent.",
            "The large variational values are not promoted to simple-zero derivatives.",
            "No rigorous, C1, C2, intrinsic, or high-winding claim is closed.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=RESULT_PATH)
    arguments = parser.parse_args()
    try:
        report = build_report()
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report["decision"], indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, DirectSplittingError) as error:
        print(f"DIRECT SPLITTING REJECTED: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
