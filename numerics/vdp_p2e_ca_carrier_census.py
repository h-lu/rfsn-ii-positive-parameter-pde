"""Two-gate phase census around the v2 algebraic matched phase.

This is a floating-point carrier scout, not a V2 event atlas.  It integrates
the true central ODE from the same finite-horizon nonlinear-Wu/Kato source
provider used by the P2e channel work.  The only classified physical carriers
are the oriented algebraic seam and the frozen pole carrier ``x=-U=10``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

from numerics.rfsn_numerics import (
    vdp_coefficients,
    vdp_field_point,
    vdp_hamiltonian,
)
from numerics.vdp_p2e_channel_scout import (
    DEFAULT_CONFIG,
    _direct_kato_provider,
    _load_config,
)
from numerics.vdp_return_coding import _pole_gate_coordinates


Array = NDArray[np.float64]
HERE = Path(__file__).resolve().parent
CENTER_RESULT = (
    HERE / "results/vdp_p2e_channel_scout_v2/energy_matched_centerline.json"
)
DEFAULT_RESULT = (
    HERE / "results/vdp_p2e_channel_scout_v2/ca_carrier_census.json"
)

OFFSETS = (-0.04, -0.02, -0.01, 0.0, 0.01, 0.02, 0.04)
OFFSET_EXACT = {
    -0.04: "-1/25",
    -0.02: "-1/50",
    -0.01: "-1/100",
    0.0: "0",
    0.01: "1/100",
    0.02: "1/50",
    0.04: "1/25",
}
PARAMETER_POINT_EXACT = {"r": "3/200", "a2": "0", "epsilon": "1"}
ALGEBRAIC_CENTRAL_U = -4.0
POLE_CENTRAL_U = -10.0
SOURCE_PHASE_DIFFERENCE_STEP = 2.0e-5
MAXIMUM_CENTRAL_TIME = 40.0
INTEGRATION_GUARD_NORM = 60.0
ENERGY_SAMPLES = 801


class CarrierCensusError(RuntimeError):
    """The fixed two-gate census could not be completed."""


def _central_jacobian(
    state: Array, *, r: float, a2: float, epsilon: float
) -> Array:
    c, quadratic, cubic = vdp_coefficients(r, a2, epsilon)
    u = float(state[0])
    return np.array(
        [
            [0.0, 1.0, 0.0, 0.0],
            [c - 2.0 * quadratic * u + 3.0 * cubic * u * u, 0.0, -1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )


def _source_tangent(
    provider: Callable[[float], Array], phase: float
) -> Array:
    step = SOURCE_PHASE_DIFFERENCE_STEP
    return (provider(phase + step) - provider(phase - step)) / (2.0 * step)


def _crossing_record(time: float, augmented: Array) -> dict[str, Any]:
    state = np.asarray(augmented[:4], dtype=np.float64)
    return {
        "time": float(time),
        "state": state.tolist(),
        "central_U_speed": float(state[1]),
        "algebraic_orientation_P_negative": bool(state[1] < 0.0),
        "algebraic_orientation_Q_negative": bool(state[3] < 0.0),
    }


def _integrate_phase(
    *,
    phase: float,
    offset: float,
    provider: Callable[[float], Array],
    r: float,
    a2: float,
    epsilon: float,
    rtol: float,
    atol: float,
    max_step: float,
) -> dict[str, Any]:
    source = provider(phase)
    tangent = _source_tangent(provider, phase)

    def augmented_field(time: float, augmented: Array) -> Array:
        state = augmented[:4]
        variation = augmented[4:]
        field = vdp_field_point(
            time, state, r=r, a2=a2, epsilon=epsilon
        )
        return np.concatenate((
            field,
            _central_jacobian(
                state, r=r, a2=a2, epsilon=epsilon
            ) @ variation,
        ))

    def algebraic_carrier(_time: float, augmented: Array) -> float:
        return float(augmented[0] - ALGEBRAIC_CENTRAL_U)

    algebraic_carrier.direction = -1.0  # type: ignore[attr-defined]
    algebraic_carrier.terminal = False  # type: ignore[attr-defined]

    def pole_carrier(_time: float, augmented: Array) -> float:
        return float(augmented[0] - POLE_CENTRAL_U)

    pole_carrier.direction = -1.0  # type: ignore[attr-defined]
    pole_carrier.terminal = False  # type: ignore[attr-defined]

    def integration_guard(_time: float, augmented: Array) -> float:
        return float(np.linalg.norm(augmented[:4]) - INTEGRATION_GUARD_NORM)

    integration_guard.direction = 1.0  # type: ignore[attr-defined]
    integration_guard.terminal = True  # type: ignore[attr-defined]

    integration = solve_ivp(
        augmented_field,
        (0.0, MAXIMUM_CENTRAL_TIME),
        np.concatenate((source, tangent)),
        method="DOP853",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
        events=(algebraic_carrier, pole_carrier, integration_guard),
        dense_output=True,
    )
    if not integration.success or integration.sol is None:
        raise CarrierCensusError(
            f"central variational integration failed: {integration.message}"
        )

    algebraic_crossings = [
        _crossing_record(time, augmented)
        for time, augmented in zip(
            integration.t_events[0], integration.y_events[0]
        )
    ]
    pole_crossings = [
        _crossing_record(time, augmented)
        for time, augmented in zip(
            integration.t_events[1], integration.y_events[1]
        )
    ]
    candidates: list[tuple[float, str, Array]] = []
    for time, augmented in zip(
        integration.t_events[0], integration.y_events[0]
    ):
        state = augmented[:4]
        if state[1] < 0.0 and state[3] < 0.0:
            candidates.append((float(time), "algebraic", augmented))
    candidates.extend(
        (float(time), "pole_x10_carrier", augmented)
        for time, augmented in zip(
            integration.t_events[1], integration.y_events[1]
        )
    )
    if not candidates:
        raise CarrierCensusError(
            "neither qualifying carrier was reached before the integration guard"
        )
    hit_time, event, hit_augmented = min(candidates, key=lambda item: item[0])
    hit_state = np.asarray(hit_augmented[:4], dtype=np.float64)
    fixed_time_variation = np.asarray(hit_augmented[4:], dtype=np.float64)
    hit_field = vdp_field_point(
        hit_time, hit_state, r=r, a2=a2, epsilon=epsilon
    )
    if hit_field[0] >= 0.0:
        raise CarrierCensusError("selected carrier does not have negative U speed")
    hit_time_derivative = float(-fixed_time_variation[0] / hit_field[0])
    hit_state_derivative = (
        fixed_time_variation + hit_field * hit_time_derivative
    )
    sample_time = np.linspace(0.0, hit_time, ENERGY_SAMPLES)
    sample_state = np.asarray(
        integration.sol(sample_time)[:4], dtype=np.float64
    )
    energy = vdp_hamiltonian(sample_state, r, a2, epsilon)
    source_energy = float(vdp_hamiltonian(source[:, None], r, a2, epsilon)[0])

    rejected_algebraic = [
        crossing for crossing in algebraic_crossings
        if not (
            crossing["algebraic_orientation_P_negative"]
            and crossing["algebraic_orientation_Q_negative"]
        )
        and crossing["time"] < hit_time
    ]
    later_pole = [
        crossing for crossing in pole_crossings
        if crossing["time"] > hit_time
    ]
    inactive_time_record: dict[str, Any]
    if event == "algebraic" and later_pole:
        inactive_time_record = {
            "kind": "later_pole_surface_crossing",
            "gap": float(later_pole[0]["time"] - hit_time),
        }
    elif event == "pole_x10_carrier" and rejected_algebraic:
        inactive_time_record = {
            "kind": "prior_Q_positive_algebraic_surface_pass",
            "gap": float(hit_time - rejected_algebraic[-1]["time"]),
        }
    else:
        inactive_time_record = {"kind": "not_observed", "gap": None}

    result: dict[str, Any] = {
        "offset": float(offset),
        "offset_exact": OFFSET_EXACT[float(offset)],
        "phase": float(phase),
        "source_state": source.tolist(),
        "source_energy_abs": abs(source_energy),
        "source_phase_tangent": {
            "method": (
                "centered finite difference of the same nonlinear-Wu/Kato "
                "provider, followed by the analytic central variational ODE"
            ),
            "difference_step": SOURCE_PHASE_DIFFERENCE_STEP,
            "norm": float(np.linalg.norm(tangent)),
        },
        "first_qualifying_event": event,
        "classification": (
            "ALGEBRAIC_ORIENTED_FIRST"
            if event == "algebraic"
            else "POLE_X10_CARRIER_AFTER_Q_POSITIVE_U_MINUS4_PASS"
        ),
        "hit_time": hit_time,
        "hit_state": hit_state.tolist(),
        "hit_function_residual_abs": float(
            abs(
                hit_state[0]
                - (
                    ALGEBRAIC_CENTRAL_U
                    if event == "algebraic"
                    else POLE_CENTRAL_U
                )
            )
        ),
        "hit_speed": {
            "central_dU_dxi": float(hit_field[0]),
            "cooriented_minus_dU_dxi": float(-hit_field[0]),
        },
        "inactive_carrier_gap_at_hit": {
            "kind": (
                "abs(U-pole_U)" if event == "algebraic"
                else "abs(U-algebraic_U)"
            ),
            "value": float(
                abs(
                    hit_state[0]
                    - (
                        POLE_CENTRAL_U
                        if event == "algebraic"
                        else ALGEBRAIC_CENTRAL_U
                    )
                )
            ),
        },
        "inactive_event_time_gap": inactive_time_record,
        "hamiltonian": {
            "sampled_abs_max_to_first_event": float(
                np.max(np.abs(energy))
            ),
            "sampled_drift_to_first_event": float(np.ptp(energy)),
        },
        "variational_hit_derivative": {
            "d_hit_time_d_phase": hit_time_derivative,
            "d_hit_state_d_phase": hit_state_derivative.tolist(),
            "fixed_surface_tangency_residual_abs": float(
                abs(hit_state_derivative[0])
            ),
            "d_P_hit_d_phase": float(hit_state_derivative[1]),
            "d_V_hit_d_phase": float(hit_state_derivative[2]),
            "d_Q_hit_d_phase": float(hit_state_derivative[3]),
        },
        "algebraic_surface_crossings": algebraic_crossings,
        "rejected_algebraic_crossings_before_first_event": rejected_algebraic,
        "solver": {
            "success": bool(integration.success),
            "steps": int(integration.t.size),
            "integration_guard_reached": bool(len(integration.t_events[2])),
        },
    }
    if event == "pole_x10_carrier":
        result["pole_x10_coordinates"] = _pole_gate_coordinates(hit_state)
    return result


def _strictly_monotone(values: list[float], direction: int) -> bool:
    differences = np.diff(np.asarray(values, dtype=np.float64))
    return bool(np.all(direction * differences > 0.0))


def compute_ca_carrier_census() -> dict[str, Any]:
    center = json.loads(CENTER_RESULT.read_text(encoding="utf-8"))
    if center.get("parameter_point_exact") != PARAMETER_POINT_EXACT:
        raise CarrierCensusError("center result lost its exact v2 parameter label")
    if center.get("status") != "ENERGY_PRESERVING_MATCHED_CENTERLINE_SUCCESS":
        raise CarrierCensusError("energy-preserving algebraic center is unavailable")
    selected_phase = float(center["source_phase"])
    frozen = _load_config(DEFAULT_CONFIG)
    if float(frozen["pole"]["central_gate_U"]) != POLE_CENTRAL_U:
        raise CarrierCensusError(
            "frozen pole binding is not x=-U=10 / central U=-10"
        )
    source = frozen["common_source_convention"]
    integration_choices = frozen["homoclinic"]
    r, a2, epsilon = 3.0 / 200.0, 0.0, 1.0
    provider = _direct_kato_provider(
        r=r,
        a2=a2,
        epsilon=epsilon,
        source_radius=float(source["source_radius"]),
        graph_horizon=float(source["graph_horizon"]),
        graph_boundary_tolerance=float(source["graph_boundary_tolerance"]),
    )
    rows = [
        _integrate_phase(
            phase=selected_phase + offset,
            offset=offset,
            provider=provider,
            r=r,
            a2=a2,
            epsilon=epsilon,
            rtol=float(integration_choices["rtol"]),
            atol=float(integration_choices["atol"]),
            max_step=float(integration_choices["max_step"]),
        )
        for offset in OFFSETS
    ]
    algebraic = [
        row for row in rows if row["first_qualifying_event"] == "algebraic"
    ]
    pole = [
        row for row in rows
        if row["first_qualifying_event"] == "pole_x10_carrier"
    ]
    algebraic_monotonicity = {
        "sampled_hit_time_strictly_increases_with_phase": _strictly_monotone(
            [row["hit_time"] for row in algebraic], 1
        ),
        "sampled_Q_hit_strictly_decreases_with_phase": _strictly_monotone(
            [row["hit_state"][3] for row in algebraic], -1
        ),
        "sampled_P_hit_strictly_increases_with_phase": _strictly_monotone(
            [row["hit_state"][1] for row in algebraic], 1
        ),
        "variational_d_hit_time_d_phase_positive_at_every_sample": all(
            row["variational_hit_derivative"]["d_hit_time_d_phase"] > 0.0
            for row in algebraic
        ),
        "variational_d_Q_hit_d_phase_negative_at_every_sample": all(
            row["variational_hit_derivative"]["d_Q_hit_d_phase"] < 0.0
            for row in algebraic
        ),
        "scope": (
            "Pointwise and sampled E1 monotonicity on four phases; not a "
            "uniform derivative enclosure on the intervening phase interval."
        ),
    }
    pole_monotonicity = {
        "sampled_hit_time_strictly_decreases_with_phase": _strictly_monotone(
            [row["hit_time"] for row in pole], -1
        ),
        "variational_d_hit_time_has_one_sign_at_every_sample": bool(
            len({
                np.sign(
                    row["variational_hit_derivative"]["d_hit_time_d_phase"]
                )
                for row in pole
            }) == 1
        ),
        "scope": (
            "The sampled pole hit times are ordered, but the pointwise "
            "variational derivatives do not retain one sign."
        ),
    }
    return {
        "schema_version": "rfsn-vdp-p2e-ca-two-gate-census/1",
        "status": "TWO_GATE_CENSUS_COMPLETE_CA_APERTURE_PARTIAL",
        "evidence_status": "COMPUTED/E1_QA_NON_RIGOROUS",
        "claim_bearing": False,
        "parameter_point": {"r": r, "a2": a2, "epsilon": epsilon},
        "parameter_point_exact": PARAMETER_POINT_EXACT,
        "selected_algebraic_phase": selected_phase,
        "predeclared_offsets": list(OFFSETS),
        "predeclared_offsets_exact": [OFFSET_EXACT[item] for item in OFFSETS],
        "source_binding": {
            "provider": (
                "direct finite-horizon nonlinear W^u in the P2bK algebraic "
                "frame with R_chi"
            ),
            "source_radius": float(source["source_radius"]),
            "graph_horizon": float(source["graph_horizon"]),
            "graph_boundary_tolerance": float(
                source["graph_boundary_tolerance"]
            ),
            "unique_provider_evaluations": int(
                getattr(provider, "unique_evaluations", 0)
            ),
        },
        "event_definitions": {
            "algebraic": {
                "carrier": "U=-4",
                "coorientation": "dU/dxi=P<0",
                "required_sign_stratum": "P<0 and Q<0",
                "warning": (
                    "This current numerical seam is not a frozen V2 theorem face."
                ),
            },
            "pole": {
                "carrier": "x=-U=10, equivalently central U=-10",
                "coorientation": "d(x-10)/dxi=-P>0",
                "binding": (
                    "vdp_p2e_channel_scout_v2.json pole.central_gate_U=-10; "
                    "CENTRAL_CORE_IMPORT.md equations (13)-(14)"
                ),
                "sign_correction": (
                    "The task shorthand U=+10 was corrected to the repository's "
                    "frozen physical definition x=-U=10."
                ),
            },
            "return_or_stable_cut": {
                "status": "OMITTED_NO_COMPATIBLE_ACTUAL_DEFINITION",
                "unique_missing_object": (
                    "An application-owned physical B.RET return-section and "
                    "stable-cut embedding pulled back to this same nonlinear-"
                    "Wu/Kato source convention."
                ),
                "why_existing_code_is_not_reused": (
                    "vdp_return_coding.integrate_first_event uses an independent "
                    "linear numerical zero-energy source section and explicitly "
                    "labels its deep cut stable_cut_proxy; substituting it would "
                    "change the source/event definition."
                ),
            },
            "integration_guard": {
                "state_norm": INTEGRATION_GUARD_NORM,
                "maximum_time": MAXIMUM_CENTRAL_TIME,
                "role": "numerical stop only; never classified as an event",
            },
        },
        "points": rows,
        "event_counts": {
            "algebraic": len(algebraic),
            "pole_x10_carrier": len(pole),
        },
        "phase_monotonicity": {
            "algebraic": algebraic_monotonicity,
            "pole": pole_monotonicity,
        },
        "ca_carrier_candidate": {
            "selected_phase_is_oriented_algebraic_hit": bool(
                next(row for row in rows if row["offset"] == 0.0)[
                    "first_qualifying_event"
                ] == "algebraic"
            ),
            "sampled_oriented_algebraic_offset_span": [-0.04, 0.0],
            "first_sampled_competing_pole_offset": 0.01,
            "outcome_transition_bracket_in_offset": [0.0, 0.01],
            "left_sampled_same_outcome_buffer": 0.04,
            "right_sampled_same_outcome_buffer": 0.0,
            "two_sided_sampled_aperture_certified": False,
            "verdict": (
                "The selected phase supports a transverse C.A carrier germ and "
                "a one-sided sampled algebraic trace, but this fixed stencil "
                "does not supply a two-sided same-outcome aperture."
            ),
        },
        "qa": {
            "all_seven_classified_by_a_physical_gate": len(rows) == len(OFFSETS),
            "selected_phase_hits_oriented_algebraic_carrier": bool(
                next(row for row in rows if row["offset"] == 0.0)[
                    "first_qualifying_event"
                ] == "algebraic"
            ),
            "positive_offsets_pass_Q_positive_stratum_before_pole": all(
                row["first_qualifying_event"] == "pole_x10_carrier"
                and len(row["rejected_algebraic_crossings_before_first_event"])
                == 1
                and row["rejected_algebraic_crossings_before_first_event"][0][
                    "state"
                ][3] > 0.0
                for row in rows if row["offset"] > 0.0
            ),
            "all_hit_speeds_transverse": all(
                row["hit_speed"]["cooriented_minus_dU_dxi"] > 0.0
                for row in rows
            ),
            "all_variational_surface_residuals_below_1e_minus_8": all(
                row["variational_hit_derivative"][
                    "fixed_surface_tangency_residual_abs"
                ] < 1.0e-8
                for row in rows
            ),
        },
        "nonclaim": (
            "Seven floating-point source phases and two competing carriers do "
            "not freeze C.A, validate a two-sided aperture, materialize the "
            "return block, or constitute V2.EVENT_ATLAS."
        ),
    }


def main() -> None:
    report = compute_ca_carrier_census()
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
