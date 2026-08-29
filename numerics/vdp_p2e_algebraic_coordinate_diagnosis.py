"""Diagnose the v2 algebraic scout in an exact positive-``pi`` chart.

This is a floating-point, non-claim-bearing diagnostic.  It deliberately
leaves the frozen one-attempt scout unchanged and asks only whether that
attempt stopped because its collocation iterates could leave the coordinate
domain ``pi>0``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from numerics.vdp_matched_outer import (
    MatchedOuterConfig,
    compute_matched_outer_candidate,
)
from numerics.vdp_outer import OuterParameters
from numerics.vdp_p2e_channel_scout import (
    DEFAULT_CONFIG,
    _direct_kato_provider,
    _load_config,
)


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = (
    HERE / "results/vdp_p2e_channel_scout_v2/algebraic_coordinate_diagnosis.json"
)


def _candidate_config(config: dict[str, Any]) -> MatchedOuterConfig:
    source = config["common_source_convention"]
    choices = config["algebraic_matched_single_attempt"]
    midpoint = float(choices["core_phase_midpoint"])
    return MatchedOuterConfig(
        section_m=float(choices["central_section_m"]),
        outer_r1=float(choices["outer_r1"]),
        q_label=float(choices["q_label"]),
        q_end=float(choices["q_end"]),
        source_radius=float(source["source_radius"]),
        source_phase_seed=(
            midpoint + float(choices["source_phase_seed_offset"])
        ),
        source_phase_reference_midpoint=midpoint,
        source_phase_offset_bracket=tuple(
            float(value) for value in choices["source_phase_offset_bracket"]
        ),
        source_flowback_tau=2.0,
        source_graph_horizon=float(source["graph_horizon"]),
        source_graph_boundary_tolerance=float(
            source["graph_boundary_tolerance"]
        ),
        seam_beta_bracket=tuple(
            float(value) for value in choices["seam_beta_bracket"]
        ),
        scaled_beta_collar=float(choices["scaled_beta_collar"]),
        mesh_points=int(choices["mesh_points"]),
        output_points=int(choices["output_points"]),
        tolerance=float(choices["tolerance"]),
        boundary_tolerance=float(choices["boundary_tolerance"]),
        same_section_root_tolerance=float(
            choices["same_section_root_tolerance"]
        ),
        max_nodes=int(choices["max_nodes"]),
    )


def build_diagnosis() -> dict[str, Any]:
    config = _load_config(DEFAULT_CONFIG)
    source = config["common_source_convention"]
    r = 3.0 / 200.0
    provider = _direct_kato_provider(
        r=r,
        a2=0.0,
        epsilon=1.0,
        source_radius=float(source["source_radius"]),
        graph_horizon=float(source["graph_horizon"]),
        graph_boundary_tolerance=float(source["graph_boundary_tolerance"]),
    )
    candidate = compute_matched_outer_candidate(
        OuterParameters(r=r, a2=0.0, epsilon=1.0),
        _candidate_config(config),
        source_state_provider=provider,
        positive_pi_outer=True,
    )
    diagnostics = dict(candidate.diagnostics)
    outer_coordinate_pass = bool(
        diagnostics["solver_success"]
        and diagnostics["solver_rms_residual_passed"]
        and diagnostics["minimum_outer_pi"] > 0.0
        and diagnostics["same_section_root_passed"]
        and abs(float(diagnostics["outer_energy_residual_inf"])) <= 1.0e-12
    )
    central_k1_pass = bool(
        abs(float(diagnostics["central_energy_residual_inf"])) <= 1.0e-7
        and abs(float(diagnostics["k1_energy_residual_inf"])) <= 1.0e-6
        and abs(float(diagnostics["central_k1_q1_interface_residual"]))
        <= 1.0e-8
    )
    return {
        "schema_version": "rfsn-vdp-p2e-algebraic-coordinate-diagnosis/1",
        "status": (
            "OUTER_COORDINATE_REPAIRED_MATCHED_CANDIDATE_REJECTED"
            if outer_coordinate_pass and not central_k1_pass
            else "DIAGNOSIS_DID_NOT_REACH_EXPECTED_VERDICT"
        ),
        "evidence_status": "COMPUTED/E1_NON_EVIDENTIARY",
        "claim_bearing": False,
        "parameter_point": {"r": "3/200", "a2": "0", "epsilon": "1"},
        "coordinate_diagnosis": {
            "old_failure_is_a_newton_domain_escape": outer_coordinate_pass,
            "chart": "eta=log(pi/delta), omega=w/delta",
            "exact_coordinate_change_only": True,
            "minimum_outer_pi": diagnostics["minimum_outer_pi"],
            "outer_energy_residual_inf": diagnostics[
                "outer_energy_residual_inf"
            ],
        },
        "candidate": {
            "source_phase": candidate.source_phase,
            "central_flight_time": candidate.central_flight_time,
            "solver_nodes": diagnostics["solver_nodes"],
            "solver_rms_residual_max": diagnostics[
                "solver_rms_residual_max"
            ],
            "boundary_and_interface_residual_inf": diagnostics[
                "boundary_and_interface_residual_inf"
            ],
            "same_section_root_residual": diagnostics[
                "same_section_root_residual"
            ],
            "central_energy_residual_inf": diagnostics[
                "central_energy_residual_inf"
            ],
            "k1_energy_residual_inf": diagnostics["k1_energy_residual_inf"],
            "central_k1_q1_interface_residual": diagnostics[
                "central_k1_q1_interface_residual"
            ],
            "accepted_as_matched_channel": central_k1_pass,
        },
        "next_missing_object": (
            "An energy-preserving, scaled central--K1 coupling that includes "
            "the q1 seam equation; the current two-coordinate seam lets the "
            "small-r collocation residual amplify into an O(1) q1 defect."
        ),
        "nonclaim": (
            "The positive-pi outer solve removes the recorded coordinate "
            "exception, but the rejected central--K1 seam is not an "
            "algebraic centerline, matched orbit, V5 connection, or V2 atlas."
        ),
    }


def main() -> None:
    result = build_diagnosis()
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(result["status"])
    print(DEFAULT_OUTPUT)


if __name__ == "__main__":
    main()
