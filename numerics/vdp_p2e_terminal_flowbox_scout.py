"""Minimal terminal-centered P2e flowbox scout at one v2 point.

This calculation separates two objects that were conflated in the first
P2e draft: a relatively wide phase collar used only to separate the three
channels, and the much narrower entrance disc on which a physical flowbox is
continued to its terminal section.  All output is floating-point design
evidence; no interval or event-atlas claim is made.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

from numerics.rfsn_numerics import vdp_field_point, vdp_hamiltonian
from numerics.vdp_source_to_pole import (
    KATO_DARBOUX_SECTION_STATUS,
    KatoSourceParameters,
    calibrated_source_frame,
    compute_kato_darboux_source_point,
)


Array = NDArray[np.float64]
HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent
OUTPUT = (
    HERE / "results/vdp_p2e_channel_scout_v2/terminal_flowbox_scout.json"
)
HOM_RESULT = HERE / "results/vdp_p2e_channel_scout_v2/scout.json"
MATCHED_ALG_RESULT = (
    HERE / "results/vdp_p2e_channel_scout_v2/energy_matched_centerline.json"
)
PHASE_RESULT = (
    REPOSITORY
    / "validation/rigorous/results/vdp_box_v2_p2e_phase_order.json"
)

PARAMETERS = KatoSourceParameters(r=3.0 / 200.0, a2=0.0, epsilon=1.0)
PARAMETER_POINT_EXACT = {"r": "3/200", "a2": "0", "epsilon": "1"}
SOURCE_RADIUS = 0.01
GRAPH_HORIZON = 10.0
SOURCE_PHASE_DIFFERENCE_STEP = 2.0e-5
FINITE_DIFFERENCE_PHASE_STEP = 2.0e-6
FINITE_DIFFERENCE_ACTION_STEP = 1.0e-8
ENTRY_ACTION_RADIUS = 2.0**-55
ENTRY_PHASE_RADII = {
    "algebraic": 1.0e-6,
    "homoclinic": 1.0e-7,
    "pole": 1.0e-4,
}
TERMINAL_LEVELS = {
    "algebraic": 400.0 / 23.0,
    "pole": 10.0,
}


class FlowboxScoutError(RuntimeError):
    """A required floating source or terminal hit was not obtained."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_point(phase: float, action: float) -> tuple[Array, dict[str, Any]]:
    point = compute_kato_darboux_source_point(
        PARAMETERS,
        phase,
        action,
        source_radius=SOURCE_RADIUS,
        graph_horizon=GRAPH_HORIZON,
        phase_difference_step=SOURCE_PHASE_DIFFERENCE_STEP,
        graph_boundary_tolerance=1.0e-9,
        energy_tolerance=2.0e-11,
        rtol=2.0e-11,
        atol=2.0e-13,
        max_step=0.02,
    )
    if point.status != KATO_DARBOUX_SECTION_STATUS or point.state is None:
        raise FlowboxScoutError(
            f"source construction failed at phase={phase}, action={action}: "
            f"{point.status}"
        )
    return np.asarray(point.state, dtype=np.float64), point.diagnostics


def _fixed_u_hit(phase: float, action: float, level: float) -> dict[str, Any]:
    source, source_diagnostics = _source_point(phase, action)

    def event(_time: float, state: Array) -> float:
        return float(state[0] + level)

    event.direction = -1.0  # type: ignore[attr-defined]
    event.terminal = True  # type: ignore[attr-defined]
    integration = solve_ivp(
        lambda time, state: vdp_field_point(
            time,
            state,
            r=PARAMETERS.r,
            a2=PARAMETERS.a2,
            epsilon=PARAMETERS.epsilon,
        ),
        (0.0, 30.0),
        source,
        method="DOP853",
        rtol=2.0e-11,
        atol=2.0e-13,
        max_step=0.01,
        events=event,
        dense_output=True,
    )
    if (
        not integration.success
        or integration.sol is None
        or len(integration.t_events[0]) != 1
    ):
        raise FlowboxScoutError(f"no unique U=-{level:g} terminal hit")
    hit_time = float(integration.t_events[0][0])
    state = np.asarray(integration.y_events[0][0], dtype=np.float64)
    samples = np.asarray(
        integration.sol(np.linspace(0.0, hit_time, 401)), dtype=np.float64
    )
    energy = vdp_hamiltonian(
        samples, PARAMETERS.r, PARAMETERS.a2, PARAMETERS.epsilon
    )
    return {
        "time": hit_time,
        "state": state,
        "terminal_coordinates_V_Q": state[[2, 3]],
        "cooriented_speed": float(-state[1]),
        "section_residual_abs": float(abs(state[0] + level)),
        "source_energy_abs": float(source_diagnostics["central_energy_abs"]),
        "sampled_energy_abs_max": float(np.max(np.abs(energy))),
        "sampled_energy_drift": float(np.ptp(energy)),
    }


def _terminal_map_scout(
    channel: str, phase: float, level: float
) -> dict[str, Any]:
    center = _fixed_u_hit(phase, 0.0, level)
    phase_plus = _fixed_u_hit(
        phase + FINITE_DIFFERENCE_PHASE_STEP, 0.0, level
    )
    phase_minus = _fixed_u_hit(
        phase - FINITE_DIFFERENCE_PHASE_STEP, 0.0, level
    )
    action_plus = _fixed_u_hit(
        phase, FINITE_DIFFERENCE_ACTION_STEP, level
    )
    action_minus = _fixed_u_hit(
        phase, -FINITE_DIFFERENCE_ACTION_STEP, level
    )
    phase_column = (
        phase_plus["terminal_coordinates_V_Q"]
        - phase_minus["terminal_coordinates_V_Q"]
    ) / (2.0 * FINITE_DIFFERENCE_PHASE_STEP)
    action_column = (
        action_plus["terminal_coordinates_V_Q"]
        - action_minus["terminal_coordinates_V_Q"]
    ) / (2.0 * FINITE_DIFFERENCE_ACTION_STEP)
    raw_jacobian = np.column_stack((phase_column, action_column))
    scaled_jacobian = raw_jacobian @ np.diag(
        [ENTRY_PHASE_RADII[channel], ENTRY_ACTION_RADIUS]
    )
    raw_singular_values = np.linalg.svd(raw_jacobian, compute_uv=False)
    scaled_singular_values = np.linalg.svd(
        scaled_jacobian, compute_uv=False
    )
    return {
        "source_phase": phase,
        "terminal": {
            "definition": f"U=-{level:.17g}",
            "time": center["time"],
            "state": center["state"].tolist(),
            "cooriented_speed": center["cooriented_speed"],
            "section_residual_abs": center["section_residual_abs"],
        },
        "energy_qa": {
            "source_energy_abs": center["source_energy_abs"],
            "sampled_energy_abs_max": center["sampled_energy_abs_max"],
            "sampled_energy_drift": center["sampled_energy_drift"],
        },
        "finite_difference_terminal_map": {
            "terminal_coordinates": ["V", "Q"],
            "phase_step": FINITE_DIFFERENCE_PHASE_STEP,
            "action_step": FINITE_DIFFERENCE_ACTION_STEP,
            "raw_jacobian": raw_jacobian.tolist(),
            "raw_determinant": float(np.linalg.det(raw_jacobian)),
            "raw_singular_values": raw_singular_values.tolist(),
            "candidate_entry_phase_radius": ENTRY_PHASE_RADII[channel],
            "candidate_entry_action_radius": ENTRY_ACTION_RADIUS,
            "scaled_jacobian": scaled_jacobian.tolist(),
            "scaled_singular_values": scaled_singular_values.tolist(),
            "rank_scout_passed": bool(raw_singular_values[-1] > 1.0e-6),
            "scope": (
                "Centered binary64 differences at one parameter point; the "
                "action step is deliberately much larger than the candidate "
                "radius and supplies only a tangent-scale diagnostic."
            ),
        },
    }


def _homoclinic_return_probe(phase: float) -> dict[str, Any]:
    frame = calibrated_source_frame(
        PARAMETERS.r, PARAMETERS.a2, PARAMETERS.epsilon
    )
    rows: list[dict[str, float]] = []
    for offset in (-ENTRY_PHASE_RADII["homoclinic"],
                   ENTRY_PHASE_RADII["homoclinic"]):
        source, _diagnostics = _source_point(phase + offset, 0.0)

        def incoming(_time: float, state: Array) -> float:
            return float(
                np.linalg.norm(frame.coordinates(state)[2:]) - SOURCE_RADIUS
            )

        incoming.direction = -1.0  # type: ignore[attr-defined]
        incoming.terminal = False  # type: ignore[attr-defined]
        integration = solve_ivp(
            lambda time, state: vdp_field_point(
                time,
                state,
                r=PARAMETERS.r,
                a2=PARAMETERS.a2,
                epsilon=PARAMETERS.epsilon,
            ),
            (0.0, 24.0),
            source,
            method="DOP853",
            rtol=2.0e-11,
            atol=2.0e-13,
            max_step=0.01,
            events=incoming,
        )
        candidates: list[dict[str, float]] = []
        for time, state in zip(
            integration.t_events[0], integration.y_events[0]
        ):
            coordinates = frame.coordinates(state)
            coordinate_velocity = frame.inverse @ vdp_field_point(
                float(time),
                np.asarray(state),
                r=PARAMETERS.r,
                a2=PARAMETERS.a2,
                epsilon=PARAMETERS.epsilon,
            )
            stable_speed = float(
                coordinates[2:] @ coordinate_velocity[2:] / SOURCE_RADIUS
            )
            if time > 10.0 and stable_speed < 0.0:
                candidates.append(
                    {
                        "source_phase_offset": offset,
                        "incoming_time": float(time),
                        "incoming_unstable_radius": float(
                            np.linalg.norm(coordinates[:2])
                        ),
                        "incoming_stable_radial_speed": stable_speed,
                    }
                )
        if len(candidates) != 1:
            raise FlowboxScoutError(
                "homoclinic phase probe lacks a unique incoming radial hit"
            )
        rows.append(candidates[0])
    maximum_unstable = max(row["incoming_unstable_radius"] for row in rows)
    return {
        "source_phase": phase,
        "candidate_entry_phase_radius": ENTRY_PHASE_RADII["homoclinic"],
        "endpoint_probes": rows,
        "maximum_incoming_unstable_radius": maximum_unstable,
        "incoming_face_radius": SOURCE_RADIUS,
        "sampled_containment_margin": SOURCE_RADIUS - maximum_unstable,
        "sampled_containment_passed": maximum_unstable < SOURCE_RADIUS,
        "scope": (
            "Two phase endpoints at nu=0 only; this is not a transverse "
            "disc, interval tube, or uniform first-hit certificate."
        ),
    }


def build_scout() -> dict[str, Any]:
    phase_result = json.loads(PHASE_RESULT.read_text(encoding="utf-8"))
    hom_result = json.loads(HOM_RESULT.read_text(encoding="utf-8"))
    matched_result = json.loads(
        MATCHED_ALG_RESULT.read_text(encoding="utf-8")
    )
    algebraic_hull = phase_result["phase_hulls"]["algebraic"]
    algebraic_phase = 0.5 * sum(float(value) for value in algebraic_hull)
    homoclinic_phase = float(hom_result["homoclinic"]["source_phase"])
    matched_phase = float(matched_result["source_phase"])
    matched_displacement = matched_phase - algebraic_phase

    algebraic = _terminal_map_scout(
        "algebraic", algebraic_phase, TERMINAL_LEVELS["algebraic"]
    )
    pole = _terminal_map_scout(
        "pole", 2.0 * np.pi, TERMINAL_LEVELS["pole"]
    )
    homoclinic = _homoclinic_return_probe(homoclinic_phase)
    return {
        "schema_version": "rfsn-vdp-p2e-terminal-flowbox-scout/1",
        "status": "THREE_TERMINAL_CENTER_GERMS_SCOUTED",
        "evidence_status": "COMPUTED/E1_NON_EVIDENTIARY",
        "claim_bearing": False,
        "parameter_point_exact": PARAMETER_POINT_EXACT,
        "source_bindings": [
            {"path": str(PHASE_RESULT.relative_to(REPOSITORY)),
             "sha256": _sha256(PHASE_RESULT)},
            {"path": str(HOM_RESULT.relative_to(REPOSITORY)),
             "sha256": _sha256(HOM_RESULT)},
            {"path": str(MATCHED_ALG_RESULT.relative_to(REPOSITORY)),
             "sha256": _sha256(MATCHED_ALG_RESULT)},
        ],
        "design_correction": {
            "protected_phase_collars_are_not_flowbox_entry_discs": True,
            "flowbox_definition": (
                "Use a terminal transverse disc and its backward first-hit "
                "map to the outgoing band; use the wider phase collars only "
                "for channel separation and inactive-face margins."
            ),
            "candidate_entry_phase_radii": ENTRY_PHASE_RADII,
            "candidate_entry_action_radius": ENTRY_ACTION_RADIUS,
        },
        "algebraic": algebraic,
        "homoclinic": homoclinic,
        "pole": pole,
        "algebraic_interface": {
            "fixed_v2_gate_anchor_phase": algebraic_phase,
            "positive_outer_matched_candidate_phase": matched_phase,
            "phase_displacement": matched_displacement,
            "inside_protected_radius_1_over_100": bool(
                abs(matched_displacement) < 0.01
            ),
            "remaining_sampled_phase_margin": 0.01 - abs(matched_displacement),
            "interpretation": (
                "The finite V2 gate anchor and the later V4/V5 matched orbit "
                "are distinct objects; this sampled displacement shows only "
                "that the latter remains inside the proposed protected collar."
            ),
        },
        "qa": {
            "algebraic_terminal_rank_scout": algebraic[
                "finite_difference_terminal_map"
            ]["rank_scout_passed"],
            "pole_terminal_rank_scout": pole[
                "finite_difference_terminal_map"
            ]["rank_scout_passed"],
            "homoclinic_phase_endpoint_containment": homoclinic[
                "sampled_containment_passed"
            ],
            "matched_algebraic_candidate_inside_protected_collar": bool(
                abs(matched_displacement) < 0.01
            ),
        },
        "next_mathematical_step": (
            "Freeze terminal-disc charts and backward entrance maps with "
            "these separated scales, then validate their full v2 parameter "
            "cover by outward-rounded flow and variational enclosures."
        ),
        "nonclaims": [
            "No sampled derivative or endpoint is an interval enclosure.",
            "The action finite-difference step is not the final action radius.",
            "No carrier embedding, incidence census, numeric m0, or V2 event-atlas atom passes here.",
        ],
    }


def main() -> None:
    result = build_scout()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(result["status"])
    print(json.dumps(result["qa"], sort_keys=True))
    print(OUTPUT)


if __name__ == "__main__":
    main()
