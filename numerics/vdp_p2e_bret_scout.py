"""Application-owned B.RET/stable-cut candidates on the nonlinear-Wu source."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

from numerics.rfsn_numerics import vdp_field_point, vdp_hamiltonian
from numerics.vdp_p2e_ca_carrier_census import _central_jacobian
from numerics.vdp_p2e_channel_scout import _direct_kato_provider
from numerics.vdp_source_to_pole import (
    CENTRAL_REVERSER_MATRIX,
    KatoSourceParameters,
    calibrated_source_frame,
    invert_kato_darboux_source_coordinates,
)


Array = NDArray[np.float64]
HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent
DEFAULT_CONFIG = HERE / "config/vdp_p2e_bret_scout_v2.json"
DEFAULT_RESULT = HERE / "results/vdp_p2e_channel_scout_v2/bret_census.json"


class BretScoutError(RuntimeError):
    """The prospectively frozen B.RET scout could not be completed."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bound_path(record: dict[str, str]) -> Path:
    path = (REPOSITORY / record["path"]).resolve()
    if not path.is_relative_to(REPOSITORY.resolve()):
        raise BretScoutError("binding escapes the repository")
    if _sha256(path) != record["sha256"]:
        raise BretScoutError(f"binding hash mismatch: {record['path']}")
    return path


def _load_frozen_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("schema_version") != "rfsn-vdp-p2e-bret-scout-config/1":
        raise BretScoutError("unexpected B.RET scout schema")
    if config.get("status") != "PREFROZEN_BEFORE_FIRST_RETAINED_BRET_STABLE_RUN":
        raise BretScoutError("B.RET scout is not in its prospectively frozen state")
    center_path = _bound_path(
        config["homoclinic_phase_center"]["floating_center_binding"]
    )
    _bound_path(config["homoclinic_phase_center"]["strict_branch_binding"])
    _bound_path(config["source"]["binding"])
    _bound_path(
        config["event_definitions"]["B.RET_candidate"][
            "physical_slide_binding"
        ]
    )
    center = json.loads(center_path.read_text(encoding="utf-8"))
    archived_phase = center["points"]["center"]["phase_order_diagnostic"][
        "homoclinic"
    ]["phase"]
    if float(archived_phase) != float(
        config["homoclinic_phase_center"]["value"]
    ):
        raise BretScoutError("frozen homoclinic center does not match its archive")
    return config


def _fraction(value: str) -> float:
    return float(Fraction(value))


def _radial_data(
    state: Array, field: Array, frame: Any, source_radius: float
) -> dict[str, Any]:
    coordinates = frame.coordinates(state)
    velocity = frame.inverse @ field
    stable = coordinates[2:]
    rho_u = float(np.linalg.norm(coordinates[:2]))
    rho_s = float(np.linalg.norm(stable))
    speed = float(stable @ velocity[2:] / rho_s)
    return {
        "rho_u": rho_u,
        "rho_s": rho_s,
        "rho_s_minus_source_radius": rho_s - source_radius,
        "rho_s_speed": speed,
        "inside_local_block": bool(rho_u <= source_radius),
        "algebraic_coordinates_u": coordinates[:2].tolist(),
        "algebraic_coordinates_s": stable.tolist(),
        "stable_kato_phase": frame.kato_phase_from_algebraic(stable),
    }


def _event_crossing(
    time: float,
    augmented: Array,
    *,
    frame: Any,
    source_radius: float,
    r: float,
    a2: float,
    epsilon: float,
) -> dict[str, Any]:
    state = np.asarray(augmented[:4], dtype=np.float64)
    field = vdp_field_point(time, state, r=r, a2=a2, epsilon=epsilon)
    radial = _radial_data(state, field, frame, source_radius)
    return {
        "time": float(time),
        "state": state.tolist(),
        "P_negative": bool(state[1] < 0.0),
        "Q_negative": bool(state[3] < 0.0),
        **radial,
    }


def _integrate_one(
    *,
    phase: float,
    offset_exact: str,
    provider: Callable[[float], Array],
    frame: Any,
    parameters: KatoSourceParameters,
    source_radius: float,
    config: dict[str, Any],
) -> dict[str, Any]:
    integration_config = config["integration"]
    phase_step = _fraction(integration_config["source_phase_difference_step"])
    source_state = provider(phase)
    source_tangent = (
        provider(phase + phase_step) - provider(phase - phase_step)
    ) / (2.0 * phase_step)
    r, a2, epsilon = parameters.r, parameters.a2, parameters.epsilon

    def field(time: float, augmented: Array) -> Array:
        state, variation = augmented[:4], augmented[4:]
        return np.concatenate((
            vdp_field_point(time, state, r=r, a2=a2, epsilon=epsilon),
            _central_jacobian(
                state, r=r, a2=a2, epsilon=epsilon
            ) @ variation,
        ))

    def incoming(_time: float, augmented: Array) -> float:
        return float(
            np.linalg.norm(frame.coordinates(augmented[:4])[2:])
            - source_radius
        )

    incoming.direction = -1.0  # type: ignore[attr-defined]
    incoming.terminal = False  # type: ignore[attr-defined]

    def algebraic(_time: float, augmented: Array) -> float:
        return float(augmented[0] + 4.0)

    algebraic.direction = -1.0  # type: ignore[attr-defined]
    algebraic.terminal = False  # type: ignore[attr-defined]

    def pole(_time: float, augmented: Array) -> float:
        return float(augmented[0] + 10.0)

    pole.direction = -1.0  # type: ignore[attr-defined]
    pole.terminal = False  # type: ignore[attr-defined]

    guard_norm = _fraction(integration_config["state_norm_guard"])

    def guard(_time: float, augmented: Array) -> float:
        return float(np.linalg.norm(augmented[:4]) - guard_norm)

    guard.direction = 1.0  # type: ignore[attr-defined]
    guard.terminal = True  # type: ignore[attr-defined]

    solution = solve_ivp(
        field,
        (0.0, _fraction(integration_config["maximum_central_time"])),
        np.concatenate((source_state, source_tangent)),
        method=integration_config["method"],
        rtol=float(integration_config["rtol"]),
        atol=float(integration_config["atol"]),
        max_step=_fraction(integration_config["max_step"]),
        events=(incoming, algebraic, pole, guard),
        dense_output=True,
    )
    if not solution.success or solution.sol is None:
        raise BretScoutError(f"central integration failed: {solution.message}")

    incoming_rows = [
        _event_crossing(
            time,
            value,
            frame=frame,
            source_radius=source_radius,
            r=r,
            a2=a2,
            epsilon=epsilon,
        )
        for time, value in zip(solution.t_events[0], solution.y_events[0])
    ]
    algebraic_rows = [
        _event_crossing(
            time,
            value,
            frame=frame,
            source_radius=source_radius,
            r=r,
            a2=a2,
            epsilon=epsilon,
        )
        for time, value in zip(solution.t_events[1], solution.y_events[1])
    ]
    pole_rows = [
        _event_crossing(
            time,
            value,
            frame=frame,
            source_radius=source_radius,
            r=r,
            a2=a2,
            epsilon=epsilon,
        )
        for time, value in zip(solution.t_events[2], solution.y_events[2])
    ]
    candidates: list[tuple[float, str, Array]] = []
    for time, value, row in zip(
        solution.t_events[0], solution.y_events[0], incoming_rows
    ):
        if row["inside_local_block"] and row["rho_s_speed"] < 0.0:
            candidates.append((float(time), "B.RET_candidate", value))
    for time, value, row in zip(
        solution.t_events[1], solution.y_events[1], algebraic_rows
    ):
        if row["P_negative"] and row["Q_negative"]:
            candidates.append((float(time), "algebraic", value))
    candidates.extend(
        (float(time), "pole_x10_carrier", value)
        for time, value in zip(solution.t_events[2], solution.y_events[2])
    )
    if not candidates:
        raise BretScoutError("no qualifying event before the frozen stop")
    hit_time, event, hit_augmented = min(candidates, key=lambda item: item[0])
    hit_state = np.asarray(hit_augmented[:4], dtype=np.float64)
    fixed_time_variation = np.asarray(hit_augmented[4:], dtype=np.float64)
    hit_field = vdp_field_point(
        hit_time, hit_state, r=r, a2=a2, epsilon=epsilon
    )
    radial = _radial_data(hit_state, hit_field, frame, source_radius)
    if event == "B.RET_candidate":
        stable = frame.coordinates(hit_state)[2:]
        event_gradient = frame.inverse[2:].T @ (stable / np.linalg.norm(stable))
        event_residual = radial["rho_s_minus_source_radius"]
    else:
        event_gradient = np.array([1.0, 0.0, 0.0, 0.0])
        event_residual = hit_state[0] + (4.0 if event == "algebraic" else 10.0)
    raw_speed = float(event_gradient @ hit_field)
    hit_time_derivative = float(
        -(event_gradient @ fixed_time_variation) / raw_speed
    )
    hit_state_derivative = (
        fixed_time_variation + hit_field * hit_time_derivative
    )
    tangency_residual = float(abs(event_gradient @ hit_state_derivative))
    sample_time = np.linspace(
        0.0, hit_time, int(integration_config["energy_samples"])
    )
    sample_state = np.asarray(solution.sol(sample_time)[:4], dtype=np.float64)
    energy = vdp_hamiltonian(sample_state, r, a2, epsilon)

    stable_cut: dict[str, Any] | None = None
    if event == "B.RET_candidate":
        reflected = CENTRAL_REVERSER_MATRIX @ hit_state
        inverse = invert_kato_darboux_source_coordinates(
            reflected,
            parameters,
            source_radius=source_radius,
            graph_horizon=_fraction(config["source"]["graph_horizon"]),
            phase_difference_step=phase_step,
            graph_boundary_tolerance=float(
                config["source"]["graph_boundary_tolerance"]
            ),
            energy_tolerance=2.0e-11,
            rtol=float(integration_config["rtol"]),
            atol=float(integration_config["atol"]),
            max_step=_fraction(integration_config["max_step"]),
        )
        stable_cut = {
            "definition": "c_stable=nu(R Z) on the B.RET candidate",
            "status": inverse.status,
            "incoming_kato_phase": float(inverse.phase),
            "nu_s": float(inverse.nu),
            "energy_correction_coordinate": float(
                inverse.energy_correction_coordinate
            ),
            "reflected_inverse_reconstruction_defect": float(
                np.linalg.norm(inverse.reconstructed_state - reflected)
            ),
            "raw_chart_identical": bool(inverse.raw_chart_identical),
        }

    return {
        "offset_exact": offset_exact,
        "offset": _fraction(offset_exact),
        "phase": float(phase),
        "first_qualifying_event": event,
        "hit_time": hit_time,
        "hit_state": hit_state.tolist(),
        "hit_function_residual_abs": abs(float(event_residual)),
        "hit_speed": {
            "raw_defining_function_speed": raw_speed,
            "cooriented_speed": -raw_speed,
        },
        "inactive_gaps_at_hit": {
            "B.RET_surface_abs": abs(float(radial["rho_s_minus_source_radius"])),
            "B.RET_local_block_excess": max(
                float(radial["rho_u"]) - source_radius, 0.0
            ),
            "algebraic_surface_abs": abs(float(hit_state[0] + 4.0)),
            "pole_x10_surface_abs": abs(float(hit_state[0] + 10.0)),
        },
        "kato_incoming_coordinates": radial,
        "stable_cut_candidate": stable_cut,
        "hamiltonian": {
            "sampled_abs_max_to_hit": float(np.max(np.abs(energy))),
            "sampled_drift_to_hit": float(np.ptp(energy)),
        },
        "variational_hit_derivative": {
            "source_tangent_method": (
                "centered nonlinear-Wu source difference followed by the "
                "analytic central variational ODE"
            ),
            "source_phase_difference_step": phase_step,
            "d_hit_time_d_phase": hit_time_derivative,
            "d_hit_state_d_phase": hit_state_derivative.tolist(),
            "surface_tangency_residual_abs": tangency_residual,
        },
        "rejected_incoming_projection_crossings_before_hit": [
            row for row in incoming_rows
            if row["time"] < hit_time and not row["inside_local_block"]
        ],
        "rejected_Q_positive_algebraic_crossings_before_hit": [
            row for row in algebraic_rows
            if row["time"] < hit_time and not row["Q_negative"]
        ],
        "solver": {
            "success": bool(solution.success),
            "integration_guard_reached": bool(len(solution.t_events[3])),
        },
    }


def _group_monotonicity(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(rows, key=lambda row: row["phase"])
    times = np.asarray([row["hit_time"] for row in ordered], dtype=np.float64)
    derivatives = np.asarray([
        row["variational_hit_derivative"]["d_hit_time_d_phase"]
        for row in ordered
    ])
    return {
        "sample_count": len(ordered),
        "sampled_hit_time_strictly_increasing": bool(
            len(times) > 1 and np.all(np.diff(times) > 0.0)
        ),
        "sampled_hit_time_strictly_decreasing": bool(
            len(times) > 1 and np.all(np.diff(times) < 0.0)
        ),
        "variational_time_derivative_has_one_nonzero_sign": bool(
            len(derivatives) > 1
            and (
                np.all(derivatives > 0.0)
                or np.all(derivatives < 0.0)
            )
        ),
        "single_sample_not_a_monotonicity_claim": len(ordered) <= 1,
    }


def compute_bret_census() -> dict[str, Any]:
    config = _load_frozen_config()
    parameters = KatoSourceParameters(
        _fraction(config["parameter_point"]["r"]),
        _fraction(config["parameter_point"]["a2"]),
        _fraction(config["parameter_point"]["epsilon"]),
    )
    source_radius = _fraction(config["source"]["source_radius"])
    center_phase = float(config["homoclinic_phase_center"]["value"])
    frame = calibrated_source_frame(
        parameters.r, parameters.a2, parameters.epsilon
    )
    provider = _direct_kato_provider(
        r=parameters.r,
        a2=parameters.a2,
        epsilon=parameters.epsilon,
        source_radius=source_radius,
        graph_horizon=_fraction(config["source"]["graph_horizon"]),
        graph_boundary_tolerance=float(
            config["source"]["graph_boundary_tolerance"]
        ),
    )
    rows = [
        _integrate_one(
            phase=center_phase + _fraction(offset),
            offset_exact=offset,
            provider=provider,
            frame=frame,
            parameters=parameters,
            source_radius=source_radius,
            config=config,
        )
        for offset in config["phase_offsets"]
    ]
    groups = {
        event: [row for row in rows if row["first_qualifying_event"] == event]
        for event in ("B.RET_candidate", "algebraic", "pole_x10_carrier")
    }
    thresholds = {
        key: float(value) for key, value in config["qa_thresholds"].items()
    }
    center = next(row for row in rows if row["offset_exact"] == "0")
    stable = center["stable_cut_candidate"]
    qa = {
        "all_seven_reach_a_qualifying_event": len(rows) == 7,
        "center_reaches_BRET": center["first_qualifying_event"] == "B.RET_candidate",
        "all_hit_residuals_pass": all(
            row["hit_function_residual_abs"]
            <= thresholds["event_hit_residual_abs_upper"] for row in rows
        ),
        "all_hit_speeds_pass": all(
            row["hit_speed"]["cooriented_speed"]
            >= thresholds["cooriented_event_speed_lower"] for row in rows
        ),
        "all_energy_drifts_pass": all(
            row["hamiltonian"]["sampled_drift_to_hit"]
            <= thresholds["sampled_hamiltonian_drift_upper"] for row in rows
        ),
        "all_variational_tangencies_pass": all(
            row["variational_hit_derivative"]["surface_tangency_residual_abs"]
            <= thresholds["variational_surface_tangency_residual_abs_upper"]
            for row in rows
        ),
        "center_stable_cut_inverse_passes": bool(
            stable is not None
            and stable["status"] == "COMPUTED/E1_KATO_COMPATIBLE_DARBOUX_SECTION"
            and abs(stable["nu_s"])
            <= thresholds["stable_cut_center_abs_upper"]
            and stable["reflected_inverse_reconstruction_defect"]
            <= thresholds["stable_inverse_reconstruction_defect_upper"]
        ),
    }
    return {
        "schema_version": "rfsn-vdp-p2e-bret-census/1",
        "status": "BRET_AND_STABLE_CUT_CENTER_CANDIDATES_NO_SAMPLED_APERTURE",
        "evidence_status": "COMPUTED/E1_QA_NON_RIGOROUS",
        "claim_bearing": False,
        "configuration": {
            "path": str(DEFAULT_CONFIG.relative_to(REPOSITORY)),
            "sha256": _sha256(DEFAULT_CONFIG),
            "status": config["status"],
            "design_run_disclosure": config["design_run_disclosure"],
        },
        "parameter_point_exact": config["parameter_point"],
        "homoclinic_phase_center": center_phase,
        "phase_offsets_exact": config["phase_offsets"],
        "source_provider_unique_evaluations": int(
            getattr(provider, "unique_evaluations", 0)
        ),
        "event_counts": {key: len(value) for key, value in groups.items()},
        "points": rows,
        "phase_monotonicity": {
            key: _group_monotonicity(value) for key, value in groups.items()
        },
        "carrier_conclusion": {
            "center_BRET_local_block_margin": float(
                source_radius - center["kato_incoming_coordinates"]["rho_u"]
            ),
            "center_stable_cut_nu_s": float(stable["nu_s"]),
            "nearest_left_sample_event": rows[2]["first_qualifying_event"],
            "nearest_right_sample_event": rows[4]["first_qualifying_event"],
            "two_sided_sampled_BRET_aperture": False,
            "verdict": (
                "The homoclinic center gives transverse application-owned "
                "B.RET and c_stable candidates, but the fixed nearest samples "
                "on both sides already have another first event."
            ),
        },
        "qa_thresholds": thresholds,
        "qa": qa,
        "nonclaim": (
            "The algebraic-frame numerical sphere and reverser/Kato stable "
            "label are not the exact-Moser theorem faces; one center hit and "
            "seven phases are not a return band or V2.EVENT_ATLAS."
        ),
    }


def main() -> None:
    report = compute_bret_census()
    DEFAULT_RESULT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_RESULT.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(report["status"])
    print(report["event_counts"])
    print(DEFAULT_RESULT)


if __name__ == "__main__":
    main()
