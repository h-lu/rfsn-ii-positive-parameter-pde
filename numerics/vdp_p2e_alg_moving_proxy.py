"""Sampled floating root-chain proxy for the algebraic BVP.

The fixed V2 algebraic gate label and a possible V5 matched algebraic source
phase are different objects.  This small computation samples unidentified
finite-horizon algebraic BVP roots at the v2 center and at the corner where
the fixed-label interval cover is presently inconclusive.  It reuses the
energy-preserving central--K1--outer solve and checks its seam against a
separate finite-horizon V4 graph solve using the same exact outer-equation
implementation.

The two endpoints are joined by a predeclared 17-node parameter path.  Every
node uses a frozen data-informed phase formula and the existing BVP's default
state initialization; the expensive K1/V4 checks are performed only on the
retained endpoint solutions.  The result is a sampled root-chain candidate,
not a numerical continuation theorem, an identified V5 branch, or an interval
enclosure of the V5 incidence root or maximal V4 graph.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.interpolate import CubicSpline

from numerics.rfsn_numerics import vdp_hamiltonian
from numerics.vdp_matched_outer import (
    outer_seam_coordinates,
    resolved_k1_energy_root,
)
from numerics.vdp_outer import OuterParameters
from numerics.vdp_p2e_energy_matched import (
    _k1_to_central_full,
    compute_energy_matched_centerline,
)
from numerics.vdp_v4_future_graph_slice import (
    _load_configuration as _load_v4_configuration,
    _normal_values as _v4_normal_values,
    _solve_collocation_ladder as _solve_v4_collocation_ladder,
)


HERE = Path(__file__).resolve().parent
DEFAULT_RESULT = (
    HERE / "results/vdp_p2e_channel_scout_v2/alg_moving_proxy.json"
)
SCHEMA_VERSION = "ALG-MOVING-PROXY/1"
FIXED_V2_ALG_PHASE_MIDPOINT = 5.756691395749909
TARGET_U = -400.0 / 23.0
V4_HORIZONS = (40.0, 60.0, 80.0, 100.0)
ROUTE_SAMPLE_COUNT = 257
CONTINUATION_SEGMENTS = 16
LEGACY_SOURCE_PHASE_BOUNDS = (5.756691395749909, 5.75769139574991)
MAXIMUM_PHASE_STEP = 2.0e-3
AXIS_PHASE_DERIVATIVES = {
    "r": 0.010108358777483062,
    "a2": 0.08658683630287456,
    "epsilon": 3.810069138410199e-05,
}
EMPIRICAL_R_A2_SEED_COEFFICIENT = 5.76
POINTS = (
    {
        "id": "center",
        "parameter_point": {"r": "3/200", "a2": "0", "epsilon": "1"},
        "values": (3.0 / 200.0, 0.0, 1.0),
        "phase_seed": 5.756767223284979,
    },
    {
        "id": "fixed_phase_obstruction_corner",
        "parameter_point": {
            "r": "1/100",
            "a2": "-1/4",
            "epsilon": "4/5",
        },
        "values": (1.0 / 100.0, -1.0 / 4.0, 4.0 / 5.0),
    },
)
THRESHOLDS = {
    "matched_boundary_residual_inf_upper": 1.0e-9,
    "central_k1_seam_residual_inf_upper": 1.0e-8,
    "k1_outer_seam_residual_inf_upper": 1.0e-10,
    "same_section_residual_abs_upper": 1.0e-9,
    "target_u_residual_abs_upper": 1.0e-10,
    "route_energy_alignment_abs_upper": 1.0e-8,
    "v4_collocation_residual_upper": 3.0e-8,
    "v4_boundary_residual_upper": 1.0e-10,
    "v4_horizon_seam_spread_upper": 1.0e-12,
    "matched_v4_seam_alpha_difference_upper": 5.0e-10,
    "continuation_maximum_phase_step_upper": MAXIMUM_PHASE_STEP,
}


class MovingAlgebraicProxyError(RuntimeError):
    """The predeclared two-point proxy or one of its QA checks failed."""


def _k1_route(
    parameters: OuterParameters,
    report: dict[str, Any],
    arrays: dict[str, np.ndarray],
) -> dict[str, Any]:
    """Reconstruct the matched K1 orbit through the frozen ALG terminal U."""

    saved_r1 = np.asarray(arrays["k1_r1"], dtype=np.float64)
    saved_state = np.asarray(
        arrays["k1_state_Pi_Omega_q1"], dtype=np.float64
    )
    target_r1 = parameters.r * np.sqrt(
        parameters.r * parameters.a2 - TARGET_U
    )
    if not saved_r1[0] <= target_r1 <= saved_r1[-1]:
        raise MovingAlgebraicProxyError("the ALG terminal is outside the K1 leg")

    route_r1 = np.linspace(saved_r1[0], target_r1, ROUTE_SAMPLE_COUNT)
    pi_omega = CubicSpline(saved_r1, saved_state[:2], axis=1)(route_r1)
    q1 = resolved_k1_energy_root(
        route_r1,
        pi_omega[0],
        pi_omega[1],
        parameters,
        energy_h=float(report["energy_h"]),
    )
    central = _k1_to_central_full(
        route_r1, np.vstack((pi_omega, q1)), parameters
    )
    energy = vdp_hamiltonian(
        central, parameters.r, parameters.a2, parameters.epsilon
    )
    sigma = parameters.r / route_r1
    r1_speed = (
        0.5
        * np.sqrt(parameters.epsilon)
        * sigma**2
        * pi_omega[0]
        * route_r1
    )
    target = central[:, -1]
    return {
        "coordinate": (
            "resolved K1 r1; U=r*a2-(r1/r)^2 and "
            "dr1/dy1=(sqrt(epsilon)/2)*sigma^2*Pi*r1"
        ),
        "sample_count": ROUTE_SAMPLE_COUNT,
        "r1_start": float(route_r1[0]),
        "r1_target": float(target_r1),
        "target_U": TARGET_U,
        "target_state_U_P_V_Q": target.tolist(),
        "target_U_residual": float(target[0] - TARGET_U),
        "minimum_Pi": float(np.min(pi_omega[0])),
        "minimum_q1": float(np.min(q1)),
        "minimum_r1_speed": float(np.min(r1_speed)),
        "maximum_P": float(np.max(central[1])),
        "maximum_Q": float(np.max(central[3])),
        "energy_alignment_abs_max": float(
            np.max(np.abs(energy - float(report["energy_h"])))
        ),
        "interpretation": (
            "Positive Pi and q1 give P<0 and Q<0 on the sampled K1 route; "
            "positive r1 speed makes the displayed U level a first-hit proxy."
        ),
    }


def _v4_seam_ladder(
    parameters: OuterParameters,
    report: dict[str, Any],
    arrays: dict[str, np.ndarray],
    base_configuration: dict[str, Any],
) -> dict[str, Any]:
    """Compare the matched seam with exact-nullcline V4 graph proxies."""

    configuration = copy.deepcopy(base_configuration)
    _z_start, q_start = outer_seam_coordinates(parameters, outer_r1=2.0)
    configuration["matched_centerline_binding"]["seam_Q"] = q_start
    configuration["slice"]["collocation_Q_end_ladder"] = list(V4_HORIZONS)
    beta = float(arrays["outer_state_beta_alpha"][0, 0])
    matched_alpha = float(arrays["outer_state_beta_alpha"][1, 0])
    energy = (
        parameters.epsilon**2.5
        * parameters.r**6
        * float(report["energy_h"])
    )
    solutions, diagnostics = _solve_v4_collocation_ladder(
        configuration,
        parameters,
        np.array([beta], dtype=np.float64),
        energy=energy,
        evaluation_q=np.array([q_start], dtype=np.float64),
    )
    graph_alpha = []
    for horizon in V4_HORIZONS:
        value = _v4_normal_values(
            np.array([q_start], dtype=np.float64),
            solutions[(horizon, beta)].sol(
                np.array([q_start], dtype=np.float64)
            ),
            parameters,
            energy=energy,
        )[1]
        graph_alpha.append(float(value[0]))
    graph_alpha_array = np.asarray(graph_alpha, dtype=np.float64)
    return {
        "coordinate": "Q=z^-2, (eta,omega)=(log(pi/delta),w/delta)",
        "terminal_condition": "exact alpha_dot=0 normal nullcline",
        "Q_start": float(q_start),
        "Q_end_ladder": list(V4_HORIZONS),
        "matched_beta": beta,
        "matched_alpha": matched_alpha,
        "graph_alpha_at_seam": graph_alpha,
        "horizon_seam_spread": float(np.ptp(graph_alpha_array)),
        "matched_alpha_difference_abs_max": float(
            np.max(np.abs(graph_alpha_array - matched_alpha))
        ),
        "collocation_residual_max": float(
            max(item["solver_rms_residual_max"] for item in diagnostics)
        ),
        "boundary_residual_max": float(
            max(item["boundary_residual_inf"] for item in diagnostics)
        ),
        "minimum_pi": float(min(item["minimum_pi"] for item in diagnostics)),
        "interpretation": (
            "A finite-Q exact-nullcline ladder checks the same seam.  It is "
            "not the theorem's maximal future-staying graph."
        ),
    }


def _continuation_parameter_values(fraction: float) -> tuple[float, float, float]:
    start = POINTS[0]["values"]
    end = POINTS[-1]["values"]
    return tuple(
        float(start[index] + fraction * (end[index] - start[index]))
        for index in range(3)
    )  # type: ignore[return-value]


def _frozen_phase_predictor(parameters: OuterParameters) -> float:
    """Data-informed E1 seed frozen before the 17-node root-chain run."""

    center_r, center_a2, center_epsilon = POINTS[0]["values"]
    delta_r = parameters.r - center_r
    delta_a2 = parameters.a2 - center_a2
    delta_epsilon = parameters.epsilon - center_epsilon
    return float(
        POINTS[0]["phase_seed"]
        + AXIS_PHASE_DERIVATIVES["r"] * delta_r
        + AXIS_PHASE_DERIVATIVES["a2"] * delta_a2
        + AXIS_PHASE_DERIVATIVES["epsilon"] * delta_epsilon
        + EMPIRICAL_R_A2_SEED_COEFFICIENT * delta_r * parameters.a2
    )


def _compute_root_chain() -> tuple[
    dict[str, Any],
    dict[str, tuple[dict[str, Any], dict[str, np.ndarray]]],
]:
    """Solve the declared center-to-corner sampled floating root chain."""

    nodes: list[dict[str, Any]] = []
    endpoint_solutions: dict[
        str, tuple[dict[str, Any], dict[str, np.ndarray]]
    ] = {}
    previous_phase: float | None = None
    for index in range(CONTINUATION_SEGMENTS + 1):
        fraction = index / CONTINUATION_SEGMENTS
        if index == 0:
            values = POINTS[0]["values"]
        elif index == CONTINUATION_SEGMENTS:
            values = POINTS[-1]["values"]
        else:
            values = _continuation_parameter_values(fraction)
        parameters = OuterParameters(*values)
        phase_seed = _frozen_phase_predictor(parameters)
        try:
            matched, arrays = compute_energy_matched_centerline(
                parameters,
                initial_phase=phase_seed,
                raise_on_qa=False,
            )
        except Exception as error:
            raise MovingAlgebraicProxyError(
                f"sampled root node {index}/{CONTINUATION_SEGMENTS} "
                f"failed from phase predictor {phase_seed}: {error}"
            ) from error
        phase = float(matched["source_phase"])
        diagnostics = matched["diagnostics"]
        matched_qa = {
            name: bool(passed) for name, passed in matched["qa"].items()
        }
        all_matched_qa_passed = bool(
            matched["status"]
            == "ENERGY_PRESERVING_MATCHED_CENTERLINE_SUCCESS"
            and all(matched_qa.values())
        )
        legacy_inside = bool(
            LEGACY_SOURCE_PHASE_BOUNDS[0]
            <= phase
            <= LEGACY_SOURCE_PHASE_BOUNDS[1]
        )
        legacy_reported = bool(
            diagnostics["source_phase_in_center_scout_bracket"]
        )
        node = {
            "index": index,
            "continuation_fraction": f"{index}/{CONTINUATION_SEGMENTS}",
            "parameter_point": {
                "r": float(parameters.r),
                "a2": float(parameters.a2),
                "epsilon": float(parameters.epsilon),
            },
            "phase_predictor": float(phase_seed),
            "phase_predictor_kind": "FROZEN_DATA_INFORMED_E1_SEED",
            "default_bvp_state_initialization": True,
            "source_phase": phase,
            "phase_corrector_delta": float(phase - phase_seed),
            "root_step_from_previous_node": (
                None if previous_phase is None else float(phase - previous_phase)
            ),
            "central_flight_time_to_U_minus_4": float(
                matched["central_flight_time"]
            ),
            "energy_H": float(matched["energy_h"]),
            "matched_status": matched["status"],
            "matched_qa": matched_qa,
            "all_matched_qa_passed": all_matched_qa_passed,
            "legacy_center_initialization_bracket_diagnostic": {
                "bounds": list(LEGACY_SOURCE_PHASE_BOUNDS),
                "inside": legacy_inside,
                "solver_reported_inside": legacy_reported,
                "diagnostic_consistent": legacy_inside == legacy_reported,
                "acceptance_condition": False,
            },
        }
        nodes.append(node)
        if not all_matched_qa_passed:
            failed = [name for name, passed in matched_qa.items() if not passed]
            raise MovingAlgebraicProxyError(
                f"sampled root node {index} failed matched QA: {failed}"
            )
        if index == 0:
            endpoint_solutions[POINTS[0]["id"]] = (matched, arrays)
        elif index == CONTINUATION_SEGMENTS:
            endpoint_solutions[POINTS[-1]["id"]] = (matched, arrays)
        previous_phase = phase

    phase_steps = np.asarray(
        [node["root_step_from_previous_node"] for node in nodes[1:]],
        dtype=np.float64,
    )
    corrector_deltas = np.asarray(
        [node["phase_corrector_delta"] for node in nodes], dtype=np.float64
    )
    all_legacy_diagnostics_consistent = all(
        node["legacy_center_initialization_bracket_diagnostic"][
            "diagnostic_consistent"
        ]
        for node in nodes
    )
    maximum_phase_step = float(np.max(np.abs(phase_steps)))
    root_chain = {
        "path": (
            "mu(s)=(3/200,0,1)+s*((1/100,-1/4,4/5)-"
            "(3/200,0,1)), s=k/16"
        ),
        "method": (
            "17 independent floating BVP correctors on the declared path, "
            "each using the frozen data-informed phase formula and the "
            "solver's default BVP state initialization"
        ),
        "phase_predictor": {
            "formula": (
                "phi_c + phi_r*(r-0.015) + phi_a2*a2 + "
                "phi_epsilon*(epsilon-1) + 5.76*(r-0.015)*a2"
            ),
            "center_phase": float(POINTS[0]["phase_seed"]),
            "axis_derivatives": dict(AXIS_PHASE_DERIVATIVES),
            "r_a2_interaction_coefficient": EMPIRICAL_R_A2_SEED_COEFFICIENT,
            "provenance": (
                "The three axial coefficients are the centered finite-"
                "difference phase quotients archived in axis_continuation."
                "json.  The 5.76 cross term is an empirical convergence seed "
                "chosen during the corner scout; it is not a derived "
                "sensitivity and enters neither the BVP equations nor QA."
            ),
            "status": "FROZEN_EMPIRICAL_E1_SEED_NOT_A_BRANCH_MODEL",
        },
        "segment_count": CONTINUATION_SEGMENTS,
        "node_count": len(nodes),
        "nodes": nodes,
        "maximum_absolute_phase_step": maximum_phase_step,
        "maximum_absolute_corrector_delta": float(
            np.max(np.abs(corrector_deltas))
        ),
        "all_node_matched_qa_passed": bool(
            all(node["all_matched_qa_passed"] for node in nodes)
        ),
        "all_legacy_bracket_diagnostics_consistent": bool(
            all_legacy_diagnostics_consistent
        ),
        "legacy_bracket_is_acceptance_condition": False,
        "phase_step_passed": maximum_phase_step <= MAXIMUM_PHASE_STEP,
        "chain_status": "SAMPLED_FLOATING_ROOT_CHAIN_CANDIDATE",
        "nonclaim": (
            "The roots are separately corrected from a data-informed seed. "
            "Finite samples do not exclude a fold or root jump between "
            "nodes, do not identify one V5 branch, and are not a numerical "
            "continuation theorem."
        ),
    }
    return root_chain, endpoint_solutions


def _complete_endpoint(
    specification: dict[str, Any],
    matched: dict[str, Any],
    arrays: dict[str, np.ndarray],
    v4_configuration: dict[str, Any],
) -> dict[str, Any]:
    parameters = OuterParameters(*specification["values"])
    route = _k1_route(parameters, matched, arrays)
    graph = _v4_seam_ladder(parameters, matched, arrays, v4_configuration)
    diagnostics = matched["diagnostics"]
    cut = np.asarray(arrays["central_state"][:, -1], dtype=np.float64)
    qa = {
        "matched_centerline": bool(
            matched["status"] == "ENERGY_PRESERVING_MATCHED_CENTERLINE_SUCCESS"
            and all(matched["qa"].values())
        ),
        "matched_boundary": diagnostics["boundary_residual_inf"]
        <= THRESHOLDS["matched_boundary_residual_inf_upper"],
        "central_k1_seam": diagnostics["central_k1_state_seam_residual_inf"]
        <= THRESHOLDS["central_k1_seam_residual_inf_upper"],
        "k1_outer_seam": diagnostics["k1_outer_normal_seam_residual_inf"]
        <= THRESHOLDS["k1_outer_seam_residual_inf_upper"],
        "same_section": abs(diagnostics["same_section_root_residual"])
        <= THRESHOLDS["same_section_residual_abs_upper"],
        "algebraic_cut_orientation": bool(cut[1] < 0.0 and cut[3] < 0.0),
        "target_section": abs(route["target_U_residual"])
        <= THRESHOLDS["target_u_residual_abs_upper"],
        "k1_positive_branches": bool(
            route["minimum_Pi"] > 0.0 and route["minimum_q1"] > 0.0
        ),
        "k1_forward_coordinate": route["minimum_r1_speed"] > 0.0,
        "k1_algebraic_orientation": bool(
            route["maximum_P"] < 0.0 and route["maximum_Q"] < 0.0
        ),
        "k1_energy": route["energy_alignment_abs_max"]
        <= THRESHOLDS["route_energy_alignment_abs_upper"],
        "v4_collocation": graph["collocation_residual_max"]
        <= THRESHOLDS["v4_collocation_residual_upper"],
        "v4_boundary": graph["boundary_residual_max"]
        <= THRESHOLDS["v4_boundary_residual_upper"],
        "v4_horizon_insensitivity": graph["horizon_seam_spread"]
        <= THRESHOLDS["v4_horizon_seam_spread_upper"],
        "matched_v4_seam": graph["matched_alpha_difference_abs_max"]
        <= THRESHOLDS["matched_v4_seam_alpha_difference_upper"],
        "v4_positive_pi": graph["minimum_pi"] > 0.0,
    }
    return {
        "id": specification["id"],
        "parameter_point": specification["parameter_point"],
        "source_phase": float(matched["source_phase"]),
        "fixed_v2_alg_phase_midpoint": FIXED_V2_ALG_PHASE_MIDPOINT,
        "source_phase_minus_fixed_v2_label": float(
            matched["source_phase"] - FIXED_V2_ALG_PHASE_MIDPOINT
        ),
        "central_flight_time_to_U_minus_4": float(
            matched["central_flight_time"]
        ),
        "energy_H": float(matched["energy_h"]),
        "central_cut_state_U_P_V_Q": cut.tolist(),
        "matched_diagnostics": {
            "solver_residual_max": diagnostics["solver_rms_residual_max"],
            "boundary_residual_inf": diagnostics["boundary_residual_inf"],
            "central_k1_seam_residual_inf": diagnostics[
                "central_k1_state_seam_residual_inf"
            ],
            "k1_outer_seam_residual_inf": diagnostics[
                "k1_outer_normal_seam_residual_inf"
            ],
            "same_section_root_residual": diagnostics[
                "same_section_root_residual"
            ],
            "minimum_outer_pi": diagnostics["minimum_outer_pi"],
        },
        "k1_algebraic_route": route,
        "v4_graph_seam_ladder": graph,
        "qa": qa,
        "all_qa_passed": bool(all(qa.values())),
    }


def compute_alg_moving_proxy() -> dict[str, Any]:
    v4_configuration = _load_v4_configuration()
    root_chain, endpoint_solutions = _compute_root_chain()
    points = [
        _complete_endpoint(
            specification,
            *endpoint_solutions[specification["id"]],
            v4_configuration,
        )
        for specification in POINTS
    ]
    all_passed = bool(
        root_chain["all_node_matched_qa_passed"]
        and root_chain["all_legacy_bracket_diagnostics_consistent"]
        and root_chain["phase_step_passed"]
        and all(point["all_qa_passed"] for point in points)
    )
    report = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "COMPUTED/E1_QA_SAMPLED_FLOATING_ROOT_CHAIN_CANDIDATE"
            if all_passed
            else "COMPUTED/E1_QA_REJECTED"
        ),
        "evidence_status": "COMPUTED/E1",
        "mathematical_status": "INCONCLUSIVE",
        "claim_bearing": False,
        "strict_validation": False,
        "root_chain": root_chain,
        "point_order": [point["id"] for point in points],
        "points": points,
        "thresholds": THRESHOLDS,
        "equation_binding": {
            "source": "direct finite-horizon nonlinear W^u Kato provider",
            "central": "exact (U,P,V,Q) van der Pol Hamiltonian field",
            "matching_unknowns": "source phase and numerical energy H chart",
            "matching_rows": (
                "central-to-K1 (Pi,Omega,q1), K1-to-outer two-row seam, "
                "and finite-horizon outer terminal alpha=0"
            ),
            "separate_graph_check": (
                "positive-pi V4 equations with exact alpha_dot=0 terminal "
                "normal nullcline; shared outer-equation implementation"
            ),
            "algebraic_route": (
                "resolved K1 positive (Pi,q1) branch from U=-4 to "
                "U=-400/23"
            ),
        },
        "interpretation": (
            "Seventeen separately corrected finite-horizon algebraic BVP "
            "roots pass on the declared center-to-corner path; only the two "
            "endpoints receive the complete K1/V4 checks."
        ),
        "nonclaim": (
            "A sampled floating root chain is not a continuation proof and "
            "does not exclude a fold or root jump between nodes.  It does "
            "not identify a V5 branch, enclose the V5 incidence root, "
            "identify the maximal V4 graph, or validate Issue #7."
        ),
    }
    if not all_passed:
        failed = {
            point["id"]: [name for name, passed in point["qa"].items() if not passed]
            for point in points
            if not point["all_qa_passed"]
        }
        raise MovingAlgebraicProxyError(
            f"root-chain or endpoint proxy QA failed: {failed}"
        )
    return report


def main() -> None:
    report = compute_alg_moving_proxy()
    DEFAULT_RESULT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_RESULT.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(report["status"])
    print(
        "root_chain_nodes",
        report["root_chain"]["node_count"],
        "maximum_phase_step",
        report["root_chain"]["maximum_absolute_phase_step"],
    )
    for point in report["points"]:
        print(point["id"], point["source_phase"], point["all_qa_passed"])
    print(DEFAULT_RESULT)


if __name__ == "__main__":
    main()
