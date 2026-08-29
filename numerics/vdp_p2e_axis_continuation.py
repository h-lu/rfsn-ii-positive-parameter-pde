"""Seven-point v2 axis continuation of the energy-preserving centerline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from numerics.vdp_outer import OuterParameters
from numerics.vdp_p2c_branch_scout import (
    P2CParameters,
    P2CScoutConfiguration,
    solve_direct_source_branch,
)
from numerics.vdp_p2e_channel_scout import DEFAULT_CONFIG, _load_config
from numerics.vdp_p2e_energy_matched import (
    compute_energy_matched_centerline,
)


HERE = Path(__file__).resolve().parent
DEFAULT_RESULT = (
    HERE / "results/vdp_p2e_channel_scout_v2/axis_continuation.json"
)
DEFAULT_DATA = (
    HERE / "results/vdp_p2e_channel_scout_v2/axis_continuation.npz"
)
POINTS = (
    ("center", 3.0 / 200.0, 0.0, 1.0),
    ("r_lower", 1.0 / 100.0, 0.0, 1.0),
    ("r_upper", 1.0 / 50.0, 0.0, 1.0),
    ("a2_upper", 3.0 / 200.0, 1.0 / 4.0, 1.0),
    ("a2_lower", 3.0 / 200.0, -1.0 / 4.0, 1.0),
    ("epsilon_lower", 3.0 / 200.0, 0.0, 4.0 / 5.0),
    ("epsilon_upper", 3.0 / 200.0, 0.0, 6.0 / 5.0),
)
POINT_PARAMETER_EXACT = {
    "center": {"r": "3/200", "a2": "0", "epsilon": "1"},
    "r_lower": {"r": "1/100", "a2": "0", "epsilon": "1"},
    "r_upper": {"r": "1/50", "a2": "0", "epsilon": "1"},
    "a2_upper": {"r": "3/200", "a2": "1/4", "epsilon": "1"},
    "a2_lower": {"r": "3/200", "a2": "-1/4", "epsilon": "1"},
    "epsilon_lower": {"r": "3/200", "a2": "0", "epsilon": "4/5"},
    "epsilon_upper": {"r": "3/200", "a2": "0", "epsilon": "6/5"},
}


def _homoclinic_configuration(config: dict[str, Any]) -> P2CScoutConfiguration:
    source = config["common_source_convention"]
    choices = config["homoclinic"]
    return P2CScoutConfiguration(
        source_radius=float(source["source_radius"]),
        graph_horizon=float(source["graph_horizon"]),
        graph_boundary_tolerance=float(source["graph_boundary_tolerance"]),
        rtol=float(choices["rtol"]),
        atol=float(choices["atol"]),
        flight_max_step=float(choices["max_step"]),
    )


def _paired_difference(
    rows: dict[str, dict[str, Any]],
    lower: str,
    upper: str,
    denominator: float,
) -> dict[str, Any]:
    if not all(rows[name]["status"] == "SUCCESS" for name in (lower, upper)):
        return {"status": "INCOMPLETE_DUE_TO_ENDPOINT_FAIL"}
    return {
        "status": "COMPUTED/E1_QA",
        "d_source_phase": (
            rows[upper]["source_phase"] - rows[lower]["source_phase"]
        ) / denominator,
        "d_energy_h": (
            rows[upper]["energy_h"] - rows[lower]["energy_h"]
        ) / denominator,
        "d_central_flight_time": (
            rows[upper]["central_flight_time"]
            - rows[lower]["central_flight_time"]
        ) / denominator,
    }


def compute_axis_continuation() -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    frozen = _load_config(DEFAULT_CONFIG)
    hom_config = _homoclinic_configuration(frozen)
    hom_choices = frozen["homoclinic"]
    core_hom = solve_direct_source_branch(
        P2CParameters(0.0, 0.0, 1.0),
        hom_choices["core_seed"],
        configuration=hom_config,
    )
    rows: dict[str, dict[str, Any]] = {}
    arrays: dict[str, np.ndarray] = {}
    center_phase_predictor: float | None = None
    center_hom_predictor = (core_hom.phase, core_hom.half_time)
    two_pi = float(2.0 * np.pi)
    pole_left_cover_lift = two_pi - 0.2

    for point_id, r, a2, epsilon in POINTS:
        parameters = OuterParameters(r=r, a2=a2, epsilon=epsilon)
        phase_predictor = center_phase_predictor
        if (
            point_id == "a2_lower"
            and center_phase_predictor is not None
            and rows.get("a2_upper", {}).get("status") == "SUCCESS"
        ):
            phase_predictor = (
                2.0 * center_phase_predictor
                - float(rows["a2_upper"]["source_phase"])
            )
        try:
            result, point_arrays = compute_energy_matched_centerline(
                parameters,
                initial_phase=phase_predictor,
                raise_on_qa=False,
            )
        except Exception as error:
            rows[point_id] = {
                "status": "FAIL",
                "parameter_point": {"r": r, "a2": a2, "epsilon": epsilon},
                "parameter_point_exact": dict(POINT_PARAMETER_EXACT[point_id]),
                "failure": {
                    "exception_type": type(error).__name__,
                    "message": str(error),
                },
            }
            continue
        if point_id == "center" and result["status"].endswith("SUCCESS"):
            center_phase_predictor = float(result["source_phase"])
        try:
            hom = solve_direct_source_branch(
                P2CParameters(r, a2, epsilon),
                center_hom_predictor,
                configuration=hom_config,
            )
            hom_record: dict[str, Any] = {
                "status": "SUCCESS",
                "phase": float(hom.phase),
                "shooting_residual_inf": float(hom.shooting_residual_inf),
            }
        except Exception as error:
            hom_record = {
                "status": "FAIL",
                "exception_type": type(error).__name__,
                "message": str(error),
            }
        diagnostics = result["diagnostics"]
        algebraic_phase = float(result["source_phase"])
        phase_order = {
            "algebraic_phase": algebraic_phase,
            "homoclinic": hom_record,
            "pole_phase_zero_lift_scalar": two_pi,
            "pole_certified_cover_left_lift_proxy": pole_left_cover_lift,
            "diagnostic_order_passed": bool(
                hom_record["status"] == "SUCCESS"
                and algebraic_phase < hom_record["phase"]
                and hom_record["phase"] < pole_left_cover_lift
            ),
            "nonclaim": (
                "Scalar phase ordering at one sampled point is not an event "
                "atlas, event-face separation, or uniform phase enclosure."
            ),
        }
        if hom_record["status"] == "SUCCESS":
            phase_order["algebraic_to_homoclinic_gap"] = (
                hom_record["phase"] - algebraic_phase
            )
            phase_order["homoclinic_to_pole_left_proxy_gap"] = (
                pole_left_cover_lift - hom_record["phase"]
            )
        success = bool(
            result["status"].endswith("SUCCESS")
            and phase_order["diagnostic_order_passed"]
        )
        rows[point_id] = {
            "status": "SUCCESS" if success else "FAIL",
            "centerline_status": result["status"],
            "parameter_point": {"r": r, "a2": a2, "epsilon": epsilon},
            "parameter_point_exact": dict(POINT_PARAMETER_EXACT[point_id]),
            "source_phase": algebraic_phase,
            "initial_phase_predictor": result["initial_phase_predictor"],
            "source_phase_in_center_scout_bracket": diagnostics[
                "source_phase_in_center_scout_bracket"
            ],
            "energy_h": float(result["energy_h"]),
            "central_flight_time": float(result["central_flight_time"]),
            "solver": {
                "success": diagnostics["solver_success"],
                "nodes": diagnostics["solver_nodes"],
                "rms_residual_max": diagnostics["solver_rms_residual_max"],
            },
            "energy_residuals": {
                "central_abs_max": diagnostics["central_energy_abs_max"],
                "k1_equation_inf": diagnostics[
                    "resolved_k1_energy_equation_residual_inf"
                ],
                "outer_equation_inf": diagnostics[
                    "outer_energy_equation_residual_inf"
                ],
            },
            "six_row_and_seam_residuals": {
                "boundary_inf": diagnostics["boundary_residual_inf"],
                "central_k1_full_state_inf": diagnostics[
                    "central_k1_state_seam_residual_inf"
                ],
                "k1_outer_normal_inf": diagnostics[
                    "k1_outer_normal_seam_residual_inf"
                ],
                "independent_same_section_abs": abs(
                    diagnostics["same_section_root_residual"]
                ),
            },
            "positive_branch_margins": {
                "minimum_k1_Pi": diagnostics["minimum_k1_pi_scaled"],
                "minimum_k1_q1": diagnostics["minimum_k1_q1"],
                "minimum_outer_pi": diagnostics["minimum_outer_pi"],
            },
            "qa": result["qa"],
            "phase_order_diagnostic": phase_order,
        }
        for name, values in point_arrays.items():
            arrays[f"{point_id}__{name}"] = values

    successful = [name for name, row in rows.items() if row["status"] == "SUCCESS"]
    sensitivities = {
        "method": "paired endpoint centered finite differences; COMPUTED/E1/QA",
        "energy_h_caution": (
            "The solved H values are near the floating energy noise floor; "
            "their endpoint quotients are recorded but not interpreted."
        ),
        "r": _paired_difference(rows, "r_lower", "r_upper", 1.0 / 100.0),
        "a2": _paired_difference(rows, "a2_lower", "a2_upper", 1.0 / 2.0),
        "epsilon": _paired_difference(
            rows, "epsilon_lower", "epsilon_upper", 2.0 / 5.0
        ),
        "nonclaim": (
            "These endpoint quotients are sampled sensitivities, not "
            "derivative enclosures or C2 parameter validation."
        ),
    }
    report = {
        "schema_version": "rfsn-vdp-p2e-seven-axis-continuation/1",
        "status": (
            "ALL_SEVEN_CENTERLINES_SUCCESS"
            if len(successful) == len(POINTS)
            else "AXIS_CONTINUATION_HAS_FAILS"
        ),
        "evidence_status": "COMPUTED/E1_QA_NON_RIGOROUS",
        "claim_bearing": False,
        "fixed_geometry": {
            "section_m": 4.0,
            "outer_r1": 2.0,
            "q_label": 100.0,
            "q_end": 200.0,
            "equations": (
                "identical to the center solve up to exact positive-pi and "
                "positive-Pi coordinate conjugacies"
            ),
            "residual_and_branch_thresholds": "identical to center solve",
            "center_phase_bracket_policy": (
                "recorded at every point but not used as an axis acceptance "
                "test: phase is a solved output, and the bracket froze only "
                "the center scout's Newton initialization"
            ),
            "predictor_policy": (
                "center phase for every axial endpoint; the negative a2 "
                "endpoint uses the symmetric secant phase from center and "
                "the already successful positive a2 endpoint"
            ),
        },
        "point_order": [item[0] for item in POINTS],
        "successful_points": successful,
        "points": rows,
        "centered_finite_differences": sensitivities,
        "nonclaim": (
            "Seven axial floating-point centerlines and scalar phase order "
            "do not form a box cover, channel tube, or V2 event atlas."
        ),
    }
    return report, arrays


def main() -> None:
    report, arrays = compute_axis_continuation()
    DEFAULT_RESULT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(DEFAULT_DATA, **arrays)
    report["data_path"] = str(DEFAULT_DATA.relative_to(HERE.parent))
    report["saved_array_count"] = len(arrays)
    DEFAULT_RESULT.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(report["status"])
    print(report["successful_points"])
    print(DEFAULT_RESULT)


if __name__ == "__main__":
    main()
