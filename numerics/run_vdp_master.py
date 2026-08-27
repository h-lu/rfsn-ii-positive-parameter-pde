#!/usr/bin/env python3
"""Run the V1--V7 van der Pol numerical reproduction atlas.

This is a floating-point explanatory computation.  It deliberately preserves
the stop-rule statuses for theorem objects whose defining constants or graph
data are non-explicit; see ``VAN_DER_POL_COVERAGE_MATRIX.md``.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import scipy

# Support both ``python3 numerics/run_vdp_master.py`` and module execution.
_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))

from numerics.rfsn_numerics import (
    common_slope_fit,
    compute_periodic_orbit,
    reflected_profile,
    solve_homoclinic,
)
from numerics.vdp_bridge import (
    BridgeParameters,
    bridge_diagnostics,
    bridge_refinement_diagnostics,
    central_to_physical,
)
from numerics.vdp_central import (
    compute_homoclinic_continuation,
    json_ready,
    local_passage_log_law,
    saddle_focus_spectrum,
    symbolic_hamiltonian_checks,
    transversality_proxy,
)
from numerics.vdp_outer import (
    FiniteHorizonOuterTail,
    OuterParameters,
    OuterTailPair,
    central_section_to_k1,
    energy_equation_residual,
    finite_horizon_tail_pair,
    gauge_composition_balance,
    k1_to_outer,
    normal_outer_state,
    numerical_cut_balance,
    outer_physical_densities,
    outer_asymptotic_diagnostics,
    reference_change_balance,
    reference_subtracted_integrals,
    v5_matching_status,
)
from numerics.vdp_pole import (
    PoleParameters,
)
from numerics.vdp_source_to_pole import (
    compute_pole_window_candidate,
    compute_source_to_pole_connection,
    same_orbit_moving_cut_balance,
)
from numerics.vdp_matched_outer import (
    MatchedOuterConfig,
    compute_matched_outer_candidate,
    finite_horizon_gamma_continuation,
    true_wu_source_state_provider,
)
from numerics.vdp_complete_branches import integrate_complete_return_branch
from numerics.vdp_return_coding import (
    event_sample_record,
    finite_window_approximants,
    homoclinic_source_anchor,
    integrate_first_event,
    periodic_profile_diagnostics,
    periodic_source_anchor,
    solve_symmetric_multipulse,
)
from validation.build_vdp_candidate_contract import build_vdp_candidate_contract
from validation.check_candidate_contract import validate_contract


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "numerics" / "config" / "vdp_v1_v7.json"
DEFAULT_OUTPUT = ROOT / "numerics" / "results" / "vdp_v1_v7"

FROZEN_INTERFACE_KEYS = {
    "source_manifold": {
        "phase_convention",
        "source_radius",
        "flowback_tau",
        "graph_horizon_ladder",
        "graph_boundary_tolerance",
    },
    "pole_connection": {
        "phase_window",
        "phase_samples",
        "representative_phase",
        "gate_x",
        "blowup_u_levels",
        "label_fit_levels",
        "local_sigma_min",
        "local_sigma_cut",
        "local_points",
        "action_cutoff_sigmas",
    },
    "matched_outer": {
        "core_algebraic_phase_midpoint",
        "central_section_m",
        "source_phase_offset_bracket",
        "source_phase_seed",
        "beta_grid",
        "candidate_q_end",
        "gamma_horizon_ladder",
        "seam_r1",
        "label_q",
        "scaled_beta_collar",
        "mesh_points",
        "output_points",
        "finite_part_output_ladder",
        "coupled_bvp_tolerance",
        "boundary_tolerance",
        "same_section_root_residual_tolerance",
    },
    "events": {
        "phase_samples",
        "nu_samples",
        "nu_range",
        "maximum_xi",
        "local_return_radius",
        "terminal_u",
        "escape_norm",
        "uncertain_margin",
    },
    "acceptance": {
        "energy_drift",
        "closure_residual",
        "independent_difference",
        "finite_part_grid_difference",
        "event_hit_residual",
        "matched_bvp_rms_residual_factor",
        "complete_return_min_abs_event_speed",
        "complete_return_action_quadrature_difference",
        "multipulse_solver_rms_residual_factor",
        "multipulse_boundary_residual",
        "multipulse_tail_norm",
        "multipulse_hamiltonian_drift",
        "multipulse_physical_fd_residual",
    },
}


def validate_frozen_config_interface(config: dict[str, Any]) -> None:
    """Reject stale or silently ignored fields in the claim-candidate interface."""

    obsolete_sections = {"pole", "cutoff_ladders"}.intersection(config)
    if obsolete_sections:
        raise ValueError(
            "obsolete duplicate configuration sections are forbidden: "
            f"{sorted(obsolete_sections)}"
        )
    for section, expected in FROZEN_INTERFACE_KEYS.items():
        if section not in config or not isinstance(config[section], dict):
            raise ValueError(f"missing frozen configuration section: {section}")
        actual = set(config[section])
        if actual != expected:
            missing = sorted(expected - actual)
            unknown = sorted(actual - expected)
            raise ValueError(
                f"frozen configuration drift in {section}: "
                f"missing={missing}, unknown={unknown}"
            )


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(json_ready(value), indent=2, sort_keys=True, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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


def parameter_slice_sample(result: Any) -> dict[str, Any]:
    proxy = transversality_proxy(result)
    return {
        "r": result.r,
        "a2": result.a2,
        "epsilon": result.epsilon,
        "spectrum": saddle_focus_spectrum(
            result.r, result.a2, result.epsilon
        ).as_json_dict(),
        "diagnostics": result.diagnostics,
        "transversality": proxy.as_json_dict(),
        "center": result.solution.sol(0.0),
        "tail": result.solution.sol(result.domain),
    }


def periodic_payload(orbits: list[Any]) -> dict[str, np.ndarray]:
    payload: dict[str, np.ndarray] = {}
    for orbit in orbits:
        stem = f"{orbit.family}{orbit.relative_winding}"
        payload[f"{stem}_xi"] = orbit.xi
        payload[f"{stem}_state"] = orbit.state
        payload[f"{stem}_physical_x"] = orbit.physical_x
        payload[f"{stem}_physical_u"] = orbit.physical_u
        payload[f"{stem}_physical_v"] = orbit.physical_v
    return payload


def multipulse_payload(orbits: list[Any]) -> dict[str, np.ndarray]:
    payload: dict[str, np.ndarray] = {}
    for orbit in orbits:
        stem = f"pulse_{orbit.pulse_count_requested}"
        payload[f"{stem}_xi"] = orbit.xi
        payload[f"{stem}_state"] = orbit.state
        payload[f"{stem}_physical_x"] = orbit.physical_x
        payload[f"{stem}_physical_u"] = orbit.physical_u
        payload[f"{stem}_physical_v"] = orbit.physical_v
    return payload


def matched_candidate_report(candidate: Any) -> dict[str, Any]:
    """Return the compact JSON record for one coupled V4--V5 candidate."""

    return {
        "status": candidate.evidence_status,
        "validation_status": candidate.validation_status,
        "claim_bearing": False,
        "parameters": asdict(candidate.parameters),
        "configuration": asdict(candidate.config),
        "source_phase": candidate.source_phase,
        "central_flight_time": candidate.central_flight_time,
        "diagnostics": candidate.diagnostics,
        "scope": (
            "One floating-point nonlinear-Wu -> central -> resolved-K1 -> "
            "finite-horizon outer candidate.  It is not the uniform V4 graph, "
            "the V5 adjoint/exchange proof, or Issue #7 interval validation."
        ),
    }


def matched_candidate_payload(candidate: Any) -> dict[str, np.ndarray]:
    return {
        "normalized_grid": candidate.normalized_grid,
        "central_state": candidate.central_state,
        "k1_r1": candidate.k1_r1,
        "k1_state": candidate.k1_state,
        "compact_q": candidate.compact_q,
        "outer_beta": candidate.outer_state[0],
        "outer_alpha": candidate.outer_state[1],
        "source_phase": np.array([candidate.source_phase]),
        "central_flight_time": np.array([candidate.central_flight_time]),
    }


def matched_outer_tail_pair(candidate: Any) -> OuterTailPair:
    """Attach V5A same-Q densities to the computed V4--V5 candidate."""

    parameters = candidate.parameters
    q_start = float(candidate.compact_q[0])
    q_end = float(candidate.compact_q[-1])
    reference_sample = finite_horizon_gamma_continuation(
        parameters,
        (0.0,),
        q_start=q_start,
        q_end=q_end,
        points=int(candidate.config.output_points),
        tolerance=min(2.0e-8, 0.1 * candidate.config.tolerance),
        max_nodes=int(candidate.config.max_nodes),
    ).samples[0]
    common_q = reference_sample.compact_q
    neighboring_beta = np.interp(
        common_q, candidate.compact_q, candidate.outer_state[0]
    )
    neighboring_alpha = np.interp(
        common_q, candidate.compact_q, candidate.outer_state[1]
    )

    def build_tail(
        beta: np.ndarray,
        alpha: np.ndarray,
        *,
        beta0: float,
        source: str,
    ) -> FiniteHorizonOuterTail:
        z = common_q ** (-0.5)
        length_density, action_density, chi, pi, w = outer_physical_densities(
            common_q, beta, alpha, parameters
        )
        energy_residual = energy_equation_residual(
            z, beta, alpha, chi, parameters, energy=0.0
        )
        return FiniteHorizonOuterTail(
            parameters=parameters,
            beta0=float(beta0),
            compact_q=common_q,
            z=z,
            beta=np.asarray(beta),
            alpha=np.asarray(alpha),
            chi=chi,
            pi=pi,
            w=w,
            length_density=length_density,
            action_density=action_density,
            diagnostics={
                "solver_success": True,
                "boundary_residual_inf": float(
                    max(abs(beta[0] - beta0), abs(alpha[-1]))
                ),
                "energy_residual_inf": float(np.max(np.abs(energy_residual))),
                "minimum_pi": float(np.min(pi)),
                "terminal_condition": "alpha(Q_end)=0 finite-horizon candidate",
                "matching_status": candidate.evidence_status,
                "source": source,
            },
            evidence_status=candidate.evidence_status,
        )

    reference = build_tail(
        reference_sample.beta,
        reference_sample.alpha,
        beta0=0.0,
        source="independent beta=0 finite-horizon reference",
    )
    neighboring = build_tail(
        neighboring_beta,
        neighboring_alpha,
        beta0=float(candidate.seam_beta),
        source="same coupled central-K1-outer candidate",
    )
    return OuterTailPair(reference=reference, neighboring=neighboring)


def complete_branches_payload(branches: list[Any]) -> dict[str, np.ndarray]:
    payload: dict[str, np.ndarray] = {}
    for branch in branches:
        prefix = branch.branch_id.replace("-", "_")
        for name, values in branch.as_npz_payload().items():
            payload[f"{prefix}_{name}"] = np.asarray(values)
    return payload


def main() -> None:
    config_path = DEFAULT_CONFIG
    output = DEFAULT_OUTPUT
    output.mkdir(parents=True, exist_ok=True)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    validate_frozen_config_interface(config)
    primary = config["parameters"]["primary"]
    r = float(primary["r"])
    a2 = float(primary["a2"])
    epsilon = float(primary["epsilon"])
    central_config = config["central"]
    acceptance = config["acceptance"]

    print("[V1/V2] exact identities, coordinate bridge, and central slices", flush=True)
    symbolic = symbolic_hamiltonian_checks()
    continuation = compute_homoclinic_continuation(
        config["parameters"]["r_slice"],
        a2=a2,
        epsilon=epsilon,
        domain=float(central_config["homoclinic_domain_xi"]),
        tolerance=float(central_config["homoclinic_tolerance"]),
    )
    primary_index = int(
        np.argmin([abs(result.r - r) for result in continuation.results])
    )
    primary_homoclinic = continuation.results[primary_index]
    primary_xi, primary_state = reflected_profile(primary_homoclinic, points=8001)
    bridge_parameters = BridgeParameters(r=r, a2=a2, epsilon=epsilon)
    bridge = bridge_diagnostics(primary_xi, primary_state, bridge_parameters)
    refinement_initial = np.asarray(primary_homoclinic.solution.sol(3.0))
    refinement_initial = np.array(
        [
            refinement_initial[0],
            -refinement_initial[1],
            refinement_initial[2],
            -refinement_initial[3],
        ]
    )
    bridge_refinement = bridge_refinement_diagnostics(
        refinement_initial,
        bridge_parameters,
        xi_span=(-3.0, 3.0),
    )
    physical_state = central_to_physical(primary_state, bridge_parameters)

    # Continue laterally from the already selected primary orbit.  This avoids
    # asking a one-shot core-to-endpoint BVP to choose a distant branch.
    a2_results: list[Any] = []
    for direction in (-1.0, 1.0):
        previous = primary_homoclinic
        for target in sorted(
            [float(value) for value in config["parameters"]["a2_slice"] if direction * float(value) > 0.0],
            key=abs,
        ):
            previous = solve_homoclinic(
                "vdp",
                r,
                a2=target,
                epsilon=epsilon,
                domain=float(central_config["homoclinic_domain_xi"]),
                tolerance=float(central_config["homoclinic_tolerance"]),
                previous=previous,
            )
            a2_results.append(previous)
    epsilon_results: list[Any] = []
    for target in config["parameters"]["epsilon_slice"]:
        target = float(target)
        if abs(target - epsilon) < 1.0e-14:
            continue
        epsilon_results.append(
            solve_homoclinic(
                "vdp",
                r,
                a2=a2,
                epsilon=target,
                domain=float(central_config["homoclinic_domain_xi"]),
                tolerance=float(central_config["homoclinic_tolerance"]),
                previous=primary_homoclinic,
            )
        )
    parameter_slices = {
        "r_slice": continuation.as_json_dict(),
        "a2_slice_at_primary_r": [
            parameter_slice_sample(result)
            for result in sorted(
                a2_results + [primary_homoclinic], key=lambda item: item.a2
            )
        ],
        "epsilon_slice_at_primary_r": [
            parameter_slice_sample(result)
            for result in sorted(
                epsilon_results + [primary_homoclinic],
                key=lambda item: item.epsilon,
            )
        ],
    }
    passage = local_passage_log_law(
        primary_homoclinic,
        central_config["passage_nu"],
        incoming_stable_radius=float(central_config["passage_radius"]),
        outgoing_difference_radius=0.015,
    )
    v1_report = {
        "status": "EXACT/DERIVED plus COMPUTED/QA",
        "symbolic": symbolic.as_json_dict(),
        "bridge": bridge,
        "independent_refinement": bridge_refinement,
    }
    v2_report = {
        "status": "COMPUTED/E1 finite slices and passage proxy",
        "scope": (
            "The exact transported V2 phase/action chart and exhaustive clean-event "
            "arrangement remain NOT_NUMERICALLY_RESOLVED."
        ),
        "parameter_slices": parameter_slices,
        "passage": passage.as_json_dict(),
    }
    write_json(output / "v1_structure.json", v1_report)
    write_json(output / "v2_central.json", v2_report)
    np.savez_compressed(
        output / "v1_bridge.npz",
        xi=primary_xi,
        central_state=primary_state,
        physical_state=physical_state,
        physical_x=bridge_parameters.x_per_xi * primary_xi,
        fast_y=(bridge_parameters.x_per_xi * primary_xi)
        / bridge_parameters.delta,
        central_y2=primary_xi / epsilon**0.25,
        refinement_tolerance=np.array(
            [row["tolerance"] for row in bridge_refinement["rows"]]
        ),
        refinement_state_defect=np.array(
            [
                row["trajectory_state_defect_inf"]
                for row in bridge_refinement["rows"]
            ]
        ),
        refinement_energy_defect=np.array(
            [row["energy_scaling_defect_inf"] for row in bridge_refinement["rows"]]
        ),
        refinement_action_defect=np.array(
            [row["action_endpoint_defect"] for row in bridge_refinement["rows"]]
        ),
    )
    np.savez_compressed(
        output / "v2_homoclinics.npz", **continuation.as_npz_payload(points=2001)
    )
    np.savez_compressed(output / "v2_passage.npz", **passage.as_npz_payload())

    print("[V3] nonlinear-Wu source window, connected pole, and action", flush=True)
    source_config = config["source_manifold"]
    connection_config = config["pole_connection"]
    pole_parameters = PoleParameters(r=r, a2=a2, epsilon=epsilon)
    window_phases = np.linspace(
        float(connection_config["phase_window"][0]),
        float(connection_config["phase_window"][1]),
        int(connection_config["phase_samples"]),
    )
    pole_window = compute_pole_window_candidate(
        pole_parameters,
        phases=window_phases,
        source_radius=float(source_config["source_radius"]),
        flowback_tau=float(source_config["flowback_tau"]),
        graph_horizon=float(source_config["graph_horizon_ladder"][-1]),
        graph_boundary_tolerance=float(
            source_config["graph_boundary_tolerance"]
        ),
        gate_section_x=float(connection_config["gate_x"]),
        rtol=float(config["solver"]["rtol"]),
        atol=float(config["solver"]["atol"]),
        max_step_x=float(config["solver"]["max_step"] * r),
        max_step_xi=float(config["solver"]["max_step"]),
    )
    pole_connection = compute_source_to_pole_connection(
        pole_parameters,
        phase=float(connection_config["representative_phase"]),
        source_radius=float(source_config["source_radius"]),
        flowback_tau=float(source_config["flowback_tau"]),
        graph_horizon=float(source_config["graph_horizon_ladder"][-1]),
        comparison_horizon=float(source_config["graph_horizon_ladder"][-2]),
        graph_boundary_tolerance=float(
            source_config["graph_boundary_tolerance"]
        ),
        gate_section_x=float(connection_config["gate_x"]),
        level_u=connection_config["blowup_u_levels"],
        label_fit_levels=connection_config["label_fit_levels"],
        local_sigma_min=float(connection_config["local_sigma_min"]),
        local_sigma_cut=float(connection_config["local_sigma_cut"]),
        local_points=int(connection_config["local_points"]),
        action_cutoff_sigmas=connection_config["action_cutoff_sigmas"],
        rtol=float(config["solver"]["rtol"]),
        atol=float(config["solver"]["atol"]),
        max_step_x=float(config["solver"]["max_step"] * r),
        max_step_xi=float(config["solver"]["max_step"]),
    )
    pole = pole_connection.local_realization
    pole_labels = pole_connection.end_fit.labels
    pole_ladder = pole_connection.action_ladder
    pole_cut_balance = same_orbit_moving_cut_balance(
        pole_connection,
        earlier_cut_x=0.0,
        later_cut_x=float(pole_connection.gate.physical_time),
        endpoint_sigma=float(pole_ladder.sigma[-1]),
    )
    v3_report = {
        "status": pole_connection.diagnostics["status"],
        "validation_status": pole_connection.diagnostics[
            "theorem_validation_status"
        ],
        "claim_bearing": False,
        "source_configuration_provenance": source_config,
        "pole_connection_configuration_provenance": connection_config,
        "global_source_window_status": pole_window.diagnostics["status"],
        "source_window": pole_window.as_json_dict(),
        "connection": pole_connection.as_json_dict(),
        "diagnostics": pole_connection.diagnostics,
        "local_diagnostics": pole.diagnostics,
        "labels": {
            "z0": pole_labels.z0,
            "w0": pole_labels.w0,
            "kappa": pole_labels.kappa,
        },
        "action_cutoff": pole_ladder.as_json_dict(),
        "moving_cut": pole_cut_balance,
        "scope": (
            "The source window, gate, local pole overlap, labels, and finite-cut "
            "action are connected floating-point candidates.  Uniformity on a "
            "certified parameter box and the improper limit remain unvalidated."
        ),
    }
    write_json(output / "v3_pole.json", v3_report)
    v3_payload = pole_connection.as_npz_payload()
    v3_payload.update(
        {
            f"window_{name}": values
            for name, values in pole_window.as_npz_payload().items()
        }
    )
    # Backward-compatible aliases used by the figure layer.
    v3_payload.update(
        {
            "sigma": pole.sigma,
            "compact": pole.compact,
            "physical": pole.physical,
            "cutoff_sigma": pole_ladder.sigma,
            "raw_action": pole_ladder.raw_action,
            "divergent_part": pole_ladder.divergent_part,
            "subtracted_action": pole_ladder.subtracted_action,
        }
    )
    np.savez_compressed(
        output / "v3_pole.npz",
        **v3_payload,
    )

    print("[V4/V5/V5A] coupled nonlinear-Wu/K1/outer candidate", flush=True)
    outer_config = config["outer"]
    matched_config_data = config["matched_outer"]
    outer_parameters = OuterParameters(r=r, a2=a2, epsilon=epsilon)
    # Retain an independent outer-only horizon ladder as a terminal-condition
    # sensitivity diagnostic.  The connected floating-point candidate below
    # is solved separately and reaches back to the nonlinear Wu source; it is
    # not a claim-bearing interval validation.
    outer_convergence: list[dict[str, Any]] = []
    proxy_pair = None
    for q_end in outer_config["q_end_ladder"]:
        q_end = float(q_end)
        points = max(
            int(outer_config["minimum_points"]),
            int(outer_config["points_per_q_unit"] * (q_end - float(outer_config["q_start"]))) + 1,
        )
        pair = finite_horizon_tail_pair(
            outer_parameters,
            float(outer_config["neighboring_beta0"]),
            q_start=float(outer_config["q_start"]),
            q_end=q_end,
            points=points,
            tolerance=float(outer_config["tolerance"]),
        )
        outer_convergence.append(outer_asymptotic_diagnostics(pair))
        proxy_pair = pair
    assert proxy_pair is not None

    matched_config = MatchedOuterConfig(
        section_m=float(matched_config_data["central_section_m"]),
        outer_r1=float(matched_config_data["seam_r1"]),
        q_label=float(matched_config_data["label_q"]),
        q_end=float(matched_config_data["candidate_q_end"]),
        source_radius=float(source_config["source_radius"]),
        source_phase_seed=float(matched_config_data["source_phase_seed"]),
        source_phase_reference_midpoint=float(
            matched_config_data["core_algebraic_phase_midpoint"]
        ),
        source_phase_offset_bracket=tuple(
            float(value)
            for value in matched_config_data["source_phase_offset_bracket"]
        ),
        source_flowback_tau=float(source_config["flowback_tau"]),
        source_graph_horizon=float(source_config["graph_horizon_ladder"][-1]),
        source_graph_boundary_tolerance=float(
            source_config["graph_boundary_tolerance"]
        ),
        seam_beta_bracket=(
            float(matched_config_data["beta_grid"][0]),
            float(matched_config_data["beta_grid"][1]),
        ),
        scaled_beta_collar=float(matched_config_data["scaled_beta_collar"]),
        mesh_points=int(matched_config_data["mesh_points"]),
        output_points=int(matched_config_data["output_points"]),
        tolerance=float(matched_config_data["coupled_bvp_tolerance"]),
        boundary_tolerance=float(matched_config_data["boundary_tolerance"]),
        same_section_root_tolerance=float(
            matched_config_data["same_section_root_residual_tolerance"]
        ),
        max_nodes=int(config["solver"]["bvp_max_nodes"]),
    )
    source_provider = true_wu_source_state_provider(
        outer_parameters,
        source_radius=matched_config.source_radius,
        flowback_tau=matched_config.source_flowback_tau,
        graph_horizon=matched_config.source_graph_horizon,
        graph_boundary_tolerance=matched_config.source_graph_boundary_tolerance,
    )
    finite_part_refinement: list[dict[str, float]] = []
    matched_candidate = None
    matched_pair = None
    finite_parts = None
    for output_points in matched_config_data["finite_part_output_ladder"]:
        candidate_on_grid = compute_matched_outer_candidate(
            outer_parameters,
            replace(matched_config, output_points=int(output_points)),
            source_state_provider=source_provider,
        )
        pair_on_grid = matched_outer_tail_pair(candidate_on_grid)
        arrays_on_grid = reference_subtracted_integrals(pair_on_grid)
        diagnostics_on_grid = outer_asymptotic_diagnostics(pair_on_grid)
        finite_part_refinement.append(
            {
                "output_points": float(output_points),
                "relative_length": float(
                    arrays_on_grid.reference_subtracted_length[-1]
                ),
                "relative_action": float(
                    arrays_on_grid.reference_subtracted_action[-1]
                ),
                "relative_length_tail_change": float(
                    diagnostics_on_grid["renormalized_length_tail_change"]
                ),
                "relative_action_tail_change": float(
                    diagnostics_on_grid["renormalized_action_tail_change"]
                ),
            }
        )
        matched_candidate = candidate_on_grid
        matched_pair = pair_on_grid
        finite_parts = arrays_on_grid
    assert matched_candidate is not None
    assert matched_pair is not None
    assert finite_parts is not None
    beta_grid_lower = float(matched_config_data["beta_grid"][0])
    beta_grid_upper = float(matched_config_data["beta_grid"][1])
    beta_grid_count = int(matched_config_data["beta_grid"][2])
    if beta_grid_count < 3 or not beta_grid_lower < beta_grid_upper:
        raise ValueError("matched_outer.beta_grid must be [lower, upper, count>=3]")
    gamma_beta0 = np.linspace(beta_grid_lower, beta_grid_upper, beta_grid_count)
    gamma_points = max(
        301, min(801, int(matched_config_data["output_points"]) // 8)
    )
    gamma_tolerance = min(
        2.0e-8, 0.1 * float(matched_config_data["coupled_bvp_tolerance"])
    )
    gamma_grid = finite_horizon_gamma_continuation(
        outer_parameters,
        gamma_beta0,
        q_start=float(matched_candidate.diagnostics["q_r"]),
        q_end=float(matched_config_data["candidate_q_end"]),
        points=gamma_points,
        tolerance=gamma_tolerance,
        max_nodes=int(config["solver"]["bvp_max_nodes"]),
    )
    gamma_alpha0 = np.asarray(
        [sample.gamma for sample in gamma_grid.samples], dtype=np.float64
    )
    gamma_solver_rms = np.asarray(
        [
            float(sample.diagnostics["solver_rms_residual_max"])
            for sample in gamma_grid.samples
        ],
        dtype=np.float64,
    )
    gamma_boundary_residual = np.asarray(
        [
            float(sample.diagnostics["boundary_residual_inf"])
            for sample in gamma_grid.samples
        ],
        dtype=np.float64,
    )
    gamma_energy_residual = np.asarray(
        [
            float(sample.diagnostics["energy_residual_inf"])
            for sample in gamma_grid.samples
        ],
        dtype=np.float64,
    )
    gamma_horizon_q_end = np.asarray(
        matched_config_data["gamma_horizon_ladder"], dtype=np.float64
    )
    if (
        gamma_horizon_q_end.ndim != 1
        or gamma_horizon_q_end.size < 2
        or np.any(np.diff(gamma_horizon_q_end) <= 0.0)
        or np.any(gamma_horizon_q_end <= float(matched_candidate.diagnostics["q_r"]))
    ):
        raise ValueError("gamma_horizon_ladder must be increasing beyond Q_R")
    gamma_horizon_at_seam = np.asarray(
        [
            finite_horizon_gamma_continuation(
                outer_parameters,
                (matched_candidate.seam_beta,),
                q_start=float(matched_candidate.diagnostics["q_r"]),
                q_end=float(q_end),
                points=gamma_points,
                tolerance=gamma_tolerance,
                max_nodes=int(config["solver"]["bvp_max_nodes"]),
            ).samples[0].gamma
            for q_end in gamma_horizon_q_end
        ],
        dtype=np.float64,
    )
    candidate_gamma = float(
        matched_candidate.diagnostics["same_section_root_gamma"]
    )
    gamma_horizon_difference = gamma_horizon_at_seam - candidate_gamma
    gamma_grid_report = {
        "status": "COMPUTED/E1_FINITE_HORIZON_GAMMA_BETA_GRID",
        "validation_status": "NOT_INTERVAL_VALIDATED",
        "claim_bearing": False,
        "beta_grid": [beta_grid_lower, beta_grid_upper, beta_grid_count],
        "candidate_q_end": float(matched_config_data["candidate_q_end"]),
        "horizon_q_end": gamma_horizon_q_end,
        "horizon_gamma_at_candidate_seam_beta": gamma_horizon_at_seam,
        "horizon_difference_from_candidate": gamma_horizon_difference,
        "solver_tolerance": gamma_tolerance,
        "maximum_solver_rms_residual": float(np.max(gamma_solver_rms)),
        "maximum_boundary_residual": float(np.max(gamma_boundary_residual)),
        "maximum_energy_residual": float(np.max(gamma_energy_residual)),
        "scope": (
            "A frozen finite beta grid and finite-Q horizon sensitivity, not "
            "a continuous or infinite-horizon V4 graph theorem."
        ),
    }
    outer_diagnostics = outer_asymptotic_diagnostics(matched_pair)
    outer_diagnostics["evidence_status"] = matched_candidate.evidence_status
    outer_diagnostics["validation_status"] = matched_candidate.validation_status
    q_grid = matched_pair.reference.compact_q
    length_difference = (
        matched_pair.neighboring.length_density
        - matched_pair.reference.length_density
    )
    action_difference = (
        matched_pair.neighboring.action_density
        - matched_pair.reference.action_density
    )
    synthetic_reference = matched_pair.reference.action_density + 0.02 * np.exp(
        -(q_grid - q_grid[0])
    )
    v5a_balances = {
        "length_cut_balance": numerical_cut_balance(
            q_grid, length_difference, q_grid.size // 2
        ),
        "action_cut_balance": numerical_cut_balance(
            q_grid, action_difference, q_grid.size // 2
        ),
        "synthetic_reference_change_balance": reference_change_balance(
            q_grid,
            matched_pair.neighboring.action_density,
            matched_pair.reference.action_density,
            synthetic_reference,
        ),
        "exact_gauge_composition_balance": gauge_composition_balance(
            2.0, -0.7, 0.4, -1.2, 3.1
        ),
        "scope": (
            "Finite-grid algebra on the coupled source-K1-outer candidate.  "
            "The same saved outer segment is used, but no infinite-tail, "
            "uniform-parameter, or interval conclusion is claimed."
        ),
    }
    chart = central_section_to_k1(
        outer_parameters, **outer_config["chart_probe"]
    )
    chart_outer = k1_to_outer(
        r1=chart["r1"],
        delta1=chart["delta1"],
        p1=chart["p1"],
        v1=chart["v1"],
        q1=chart["q1"],
        epsilon=epsilon,
    )
    matching = v5_matching_status(outer_parameters)
    matched_report = matched_candidate_report(matched_candidate)
    matched_report["independent_gamma_grid"] = gamma_grid_report
    v4_v5_report = {
        "v4_status": "COMPUTED/E1_FINITE_HORIZON_GRAPH_CANDIDATE",
        "v4_uniform_graph_validation_status": "NOT_INTERVAL_VALIDATED",
        "v5_status": matched_candidate.evidence_status,
        "v5_validation_status": matched_candidate.validation_status,
        "claim_bearing": False,
        "matched_candidate": matched_report,
        "outer_diagnostics": outer_diagnostics,
        "independent_outer_q_end_convergence": outer_convergence,
        "chart_crosswalk": {"central_to_k1": chart, "k1_to_outer": chart_outer},
        "v5_analytic_nonexplicit_objects": matching,
        "scope": (
            "The exact three-piece BVP supplies a reproducible V5 candidate.  "
            "The theorem's uniform graph tube, endpoint adjoint/exchange, "
            "uniqueness, and parameter derivatives remain analytic or future #7 work."
        ),
    }
    v5a_report = {
        "status": "COMPUTED/E1_MATCHED_FINITE_HORIZON_SAME_Q_SUBTRACTION",
        "validation_status": "NOT_INTERVAL_VALIDATED",
        "claim_bearing": False,
        "matched_tail_status": matched_candidate.evidence_status,
        "diagnostics": outer_diagnostics,
        "finite_part_output_refinement": finite_part_refinement,
        "balances": v5a_balances,
        "scope": (
            "The neighboring tail is the actual saved outer segment of the "
            "coupled candidate.  Finite Q does not validate V5A's improper "
            "limits, mixed jets, or uniform reference covariance."
        ),
    }
    write_json(output / "v4_v5_outer_matching.json", v4_v5_report)
    write_json(output / "v4_v5_matched_candidate.json", matched_report)
    write_json(output / "v5a_outer_finite_part.json", v5a_report)
    np.savez_compressed(
        output / "v4_v5_matched_candidate.npz",
        **matched_candidate_payload(matched_candidate),
        gamma_beta0=gamma_beta0,
        gamma_alpha0=gamma_alpha0,
        gamma_solver_rms_residual=gamma_solver_rms,
        gamma_boundary_residual=gamma_boundary_residual,
        gamma_energy_residual=gamma_energy_residual,
        gamma_horizon_q_end=gamma_horizon_q_end,
        gamma_horizon_at_seam=gamma_horizon_at_seam,
        gamma_horizon_difference_from_candidate=gamma_horizon_difference,
    )
    np.savez_compressed(
        output / "v4_v5a_outer.npz",
        compact_q=q_grid,
        reference_z=matched_pair.reference.z,
        reference_beta=matched_pair.reference.beta,
        reference_alpha=matched_pair.reference.alpha,
        reference_chi=matched_pair.reference.chi,
        reference_pi=matched_pair.reference.pi,
        neighbor_beta=matched_pair.neighboring.beta,
        neighbor_alpha=matched_pair.neighboring.alpha,
        counterterm_length=finite_parts.counterterm_length,
        counterterm_action=finite_parts.counterterm_action,
        relative_length=finite_parts.reference_subtracted_length,
        relative_action=finite_parts.reference_subtracted_action,
        q_end=np.array([row["q_end"] for row in outer_convergence]),
        q_end_relative_length=np.array(
            [row["renormalized_length_at_q_end"] for row in outer_convergence]
        ),
        q_end_relative_action=np.array(
            [row["renormalized_action_at_q_end"] for row in outer_convergence]
        ),
        finite_part_output_points=np.array(
            [row["output_points"] for row in finite_part_refinement]
        ),
        finite_part_refined_length=np.array(
            [row["relative_length"] for row in finite_part_refinement]
        ),
        finite_part_refined_action=np.array(
            [row["relative_action"] for row in finite_part_refinement]
        ),
    )

    print("[V7] actual periodic and symmetric multipulse full-ODE profiles", flush=True)
    center_u = float(primary_homoclinic.solution.sol(0.0)[0])
    periodic_orbits = []
    periodic_reports = []
    for specification in config["periodic_orbits"]:
        orbit = compute_periodic_orbit(
            family=specification["family"],
            relative_winding=int(specification["relative_winding"]),
            bracket=tuple(float(value) for value in specification["bracket"]),
            event_index=int(specification["event_index"]),
            event_component=int(specification["event_component"]),
            residual_component=int(specification["residual_component"]),
            center_u=center_u,
            r=r,
            a2=a2,
            epsilon=epsilon,
        )
        periodic_orbits.append(orbit)
        periodic_reports.append(
            {
                "family": orbit.family,
                "relative_winding": orbit.relative_winding,
                "initial_offset": orbit.initial_offset,
                "central_action": orbit.central_action,
                "physical_action": orbit.physical_action,
                "diagnostics": periodic_profile_diagnostics(
                    orbit, r=r, a2=a2, epsilon=epsilon
                ),
            }
    )
    slope_fit = common_slope_fit(periodic_orbits)
    multipulse_tolerance = 2.0e-6
    multipulse_acceptance = {
        "solver_rms_residual": multipulse_tolerance
        * float(acceptance["multipulse_solver_rms_residual_factor"]),
        "boundary_residual": float(acceptance["multipulse_boundary_residual"]),
        "tail_norm": float(acceptance["multipulse_tail_norm"]),
        "hamiltonian_drift": float(
            acceptance["multipulse_hamiltonian_drift"]
        ),
        "physical_stationary_residual": float(
            acceptance["multipulse_physical_fd_residual"]
        ),
    }
    multipulses = [
        solve_symmetric_multipulse(
            primary_homoclinic,
            int(count),
            separation=18.0,
            padding=28.0,
            tolerance=multipulse_tolerance,
            max_nodes=int(config["solver"]["bvp_max_nodes"]) + 60_000,
            acceptance_thresholds=multipulse_acceptance,
        )
        for count in config["coded_patterns"]["multipulse_target_counts"]
    ]
    multipulse_reports = [
        {
            "pulse_count_requested": orbit.pulse_count_requested,
            "pulse_count_observed": orbit.pulse_count_observed,
            "diagnostics": orbit.diagnostics,
        }
        for orbit in multipulses
    ]
    finite_windows = finite_window_approximants(
        multipulses, config["coded_patterns"]["aperiodic_word"]
    )

    print("[V6] numerical source section and adaptive finite first-event atlas", flush=True)
    source_radius = float(central_config["source_radius"])
    homoclinic_anchor = homoclinic_source_anchor(
        primary_homoclinic, source_radius=source_radius
    )
    anchors = []
    for orbit in periodic_orbits:
        anchor = periodic_source_anchor(
            orbit,
            r=r,
            a2=a2,
            epsilon=epsilon,
            source_radius=source_radius,
        )
        anchors.append(
            {
                "family": orbit.family,
                "relative_winding": orbit.relative_winding,
                **anchor,
            }
        )

    event_config = config["events"]
    complete_branches: list[Any] = []
    complete_branch_failures: list[dict[str, str | int]] = []
    selected_complete_keys = {("B", 1), ("A", 2)}
    for anchor in anchors:
        key = (str(anchor["family"]), int(anchor["relative_winding"]))
        if key not in selected_complete_keys or not str(anchor["status"]).startswith(
            "COMPUTED"
        ):
            continue
        branch_id = f"vdp-{key[0]}{key[1]}-complete-return-candidate-v3"
        try:
            branch = integrate_complete_return_branch(
                source_state=np.asarray(anchor["state"], dtype=np.float64),
                branch_id=branch_id,
                r=r,
                a2=a2,
                epsilon=epsilon,
                source_radius=source_radius,
                local_return_radius=float(event_config["local_return_radius"]),
                uncertain_margin=float(event_config["uncertain_margin"]),
                maximum_time=float(event_config["maximum_xi"]),
                terminal_u=float(event_config["terminal_u"]),
                escape_norm=float(event_config["escape_norm"]),
                rtol=float(config["solver"]["rtol"]),
                atol=float(config["solver"]["atol"]),
                max_step=float(config["solver"]["max_step"]),
                provenance={
                    "source": "periodic_source_anchor from current master run",
                    "family": key[0],
                    "relative_winding_metadata": key[1],
                    "relative_winding_is_not_V6_label": True,
                    "configuration_version": config["configuration_version"],
                },
            )
        except RuntimeError as error:
            complete_branch_failures.append(
                {"family": key[0], "relative_winding": key[1], "error": str(error)}
            )
        else:
            complete_branches.append(branch)

    requests: list[tuple[float, float, str]] = []
    for phase in np.linspace(0.0, 2.0 * np.pi, int(event_config["phase_samples"]), endpoint=False):
        requests.append((float(phase), 0.0, "full_phase_grid_transverse_zero"))
    nu_values = np.linspace(
        float(event_config["nu_range"][0]),
        float(event_config["nu_range"][1]),
        int(event_config["nu_samples"]),
    )
    nu_phases = np.linspace(
        0.0, 2.0 * np.pi, int(event_config["nu_samples"]), endpoint=False
    )
    for phase, transverse in zip(nu_phases, nu_values):
        requests.append(
            (float(phase), float(transverse), "frozen_phase_transverse_diagonal")
        )
    computed_anchors = [
        anchor for anchor in anchors if str(anchor["status"]).startswith("COMPUTED")
    ]
    for anchor in computed_anchors:
        phase0 = float(anchor["phase"])
        transverse0 = float(anchor["transverse_coordinate"])
        for phase_delta in (-2.0e-5, 0.0, 2.0e-5):
            for transverse_delta in (-2.0e-5, 0.0, 2.0e-5):
                requests.append(
                    (
                        float((phase0 + phase_delta) % (2.0 * np.pi)),
                        transverse0 + transverse_delta,
                        f"adaptive_{anchor['family']}{anchor['relative_winding']}",
                    )
                )
    requests.append(
        (
            float(homoclinic_anchor["phase"]),
            float(homoclinic_anchor["transverse_coordinate"]),
            "homoclinic_anchor",
        )
    )
    samples = []
    tags = []
    for index, (phase, transverse, tag) in enumerate(requests, start=1):
        if index % 50 == 0:
            print(f"  first-event samples {index}/{len(requests)}", flush=True)
        samples.append(
            integrate_first_event(
                phase=phase,
                transverse_coordinate=transverse,
                r=r,
                a2=a2,
                epsilon=epsilon,
                source_radius=source_radius,
                local_return_radius=float(event_config["local_return_radius"]),
                maximum_time=float(event_config["maximum_xi"]),
                terminal_u=float(event_config["terminal_u"]),
                escape_norm=float(event_config["escape_norm"]),
                rtol=float(config["solver"]["rtol"]),
                atol=float(config["solver"]["atol"]),
                max_step=float(config["solver"]["max_step"]),
            )
        )
        tags.append(tag)
    refinement_indices = sorted(
        set(
            [
                0,
                len(samples) // 4,
                len(samples) // 2,
                3 * len(samples) // 4,
                len(samples) - 1,
            ]
            + [
                index
                for index, sample in enumerate(samples)
                if sample.event.startswith("return")
                or sample.event == "stable_cut_proxy"
            ]
        )
    )
    refinement = []
    for index in refinement_indices:
        base = samples[index]
        refined = integrate_first_event(
            phase=base.phase,
            transverse_coordinate=base.transverse_coordinate,
            r=r,
            a2=a2,
            epsilon=epsilon,
            source_radius=source_radius,
            local_return_radius=float(event_config["local_return_radius"]),
            maximum_time=float(event_config["maximum_xi"]),
            terminal_u=float(event_config["terminal_u"]),
            escape_norm=float(event_config["escape_norm"]),
            rtol=0.2 * float(config["solver"]["rtol"]),
            atol=0.2 * float(config["solver"]["atol"]),
            max_step=0.5 * float(config["solver"]["max_step"]),
        )
        refinement.append(
            {
                "index": index,
                "base_event": base.event,
                "refined_event": refined.event,
                "label_stable": base.event == refined.event,
                "event_time_difference": abs(
                    base.event_time_xi - refined.event_time_xi
                ),
            }
        )
    event_counts = Counter(sample.event for sample in samples)
    v6_report = {
        "status": "COMPUTED/E1 finite numerical source section and first-event samples",
        "theorem_atlas_validation_status": "NOT_INTERVAL_VALIDATED",
        "coordinate_scope": (
            "one exploratory local numerical presentation; not a construction "
            "of T2G and not an overlap-recoding check for the analytic marked atlas"
        ),
        "homoclinic_anchor": homoclinic_anchor,
        "periodic_anchors": anchors,
        "sample_count": len(samples),
        "sampling_configuration_provenance": event_config,
        "sampling_design": (
            "phase_samples points at nu=0, nu_samples paired phase/nu points "
            "across nu_range, plus adaptive periodic and homoclinic anchors"
        ),
        "event_counts": dict(event_counts),
        "refinement": refinement,
        "samples": [
            {"sample_tag": tag, **event_sample_record(sample)}
            for tag, sample in zip(tags, samples)
        ],
        "complete_return_branches": [
            branch.as_candidate_record() for branch in complete_branches
        ],
        "complete_return_failures": complete_branch_failures,
        "branch_action_status": (
            "COMPUTED/E1 for the saved B1 and A2 finite returns: both segments "
            "share one physical IVP and augmented length/action.  This is not an "
            "exhaustive V6 branch cocycle or an interval validation."
        ),
    }
    write_json(output / "v6_events.json", v6_report)
    event_names = sorted(event_counts)
    event_code = {name: index for index, name in enumerate(event_names)}
    np.savez_compressed(
        output / "v6_events.npz",
        phase=np.array([sample.phase for sample in samples]),
        transverse_coordinate=np.array(
            [sample.transverse_coordinate for sample in samples]
        ),
        event_name=np.array([sample.event for sample in samples]),
        event_code=np.array([event_code[sample.event] for sample in samples]),
        sample_tag=np.array(tags),
        event_time_xi=np.array([sample.event_time_xi for sample in samples]),
        event_speed=np.array([sample.event_speed for sample in samples]),
        winding_proxy=np.array([sample.winding_proxy for sample in samples]),
        energy_drift=np.array(
            [float(sample.diagnostics["energy_drift"]) for sample in samples]
        ),
        source_state=np.stack([sample.source_state for sample in samples]),
        event_state=np.stack([sample.event_state for sample in samples]),
    )
    complete_arrays_path = output / "v6_complete_branches.npz"
    np.savez_compressed(
        complete_arrays_path,
        **complete_branches_payload(complete_branches),
    )
    complete_record_paths: list[Path] = []
    for branch in complete_branches:
        record_path = output / f"v6_complete_{branch.branch_id}.json"
        write_json(record_path, branch.as_candidate_record())
        complete_record_paths.append(record_path)

    contract_path = output / "v6_candidate_contract.json"
    contract = build_vdp_candidate_contract(
        repository_root=ROOT,
        output_path=contract_path,
        branches=[
            {
                "branch_id": branch.branch_id,
                "type": "finite_return",
                "record": record_path,
                "arrays": complete_arrays_path,
            }
            for branch, record_path in zip(complete_branches, complete_record_paths)
        ],
        candidate_evidence_paths=[
            output / "v3_pole.json",
            output / "v4_v5_matched_candidate.json",
            output / "v5a_outer_finite_part.json",
            output / "v6_events.json",
        ],
        parameter_point=primary,
        configuration_path=config_path,
        generator_source_paths=[
            ROOT / "numerics" / "rfsn_numerics.py",
            ROOT / "numerics" / "vdp_return_coding.py",
            ROOT / "numerics" / "vdp_complete_branches.py",
            Path(__file__),
        ],
        contract_id="vdp-v6-b1-a2-candidate-v3",
        created_at="2026-08-27T00:00:00+08:00",
    )
    contract_failures = validate_contract(contract_path, repository_root=ROOT)
    if contract_failures:
        raise RuntimeError(
            "candidate contract failed post-write validation: "
            + "; ".join(contract_failures)
        )

    expected_period_slope = float(
        2.0 * np.pi * r / (epsilon**0.25 * passage.beta)
    )
    v7_report = {
        "status": "COMPUTED/E1 actual stationary full-ODE profiles",
        "itinerary_status": "NOT_NUMERICALLY_RESOLVED",
        "periodic_orbits": periodic_reports,
        "period_fit": slope_fit,
        "expected_period_slope": expected_period_slope,
        "period_slope_relative_error": abs(
            float(slope_fit["slope"]) / expected_period_slope - 1.0
        ),
        "multipulses": multipulse_reports,
        "finite_window_approximants": finite_windows,
        "bi_infinite_orbit_status": "NOT_NUMERICALLY_RESOLVED",
    }
    write_json(output / "v7_patterns.json", v7_report)
    np.savez_compressed(output / "v7_periodic.npz", **periodic_payload(periodic_orbits))
    np.savez_compressed(output / "v7_multipulses.npz", **multipulse_payload(multipulses))

    qa_checks = {
        "v1_symbolic_exact": bool(symbolic.passed),
        "v1_bridge_roundtrip": bridge["roundtrip_state_defect_inf"] < 1.0e-9,
        "v1_bridge_action": bridge["action_scaling_endpoint_defect"] < 1.0e-12,
        "v1_independent_clock_refinement": bridge_refinement["rows"][-1][
            "trajectory_state_defect_inf"
        ]
        < float(acceptance["independent_difference"]),
        "v2_all_slice_solvers": all(
            bool(sample["diagnostics"]["solver_success"])
            for sample in (
                [parameter_slice_sample(result) for result in continuation.results]
                + parameter_slices["a2_slice_at_primary_r"]
                + parameter_slices["epsilon_slice_at_primary_r"]
            )
        ),
        "v2_passage_time_slopes": max(
            abs(value - passage.expected_time_slope)
            for value in passage.fitted_time_slopes.values()
        )
        < 0.02,
        "v2_passage_phase_slopes": max(
            abs(value - passage.expected_phase_slope)
            for value in passage.fitted_phase_slopes.values()
        )
        < 0.02,
        "v3_field_crosscheck": pole.diagnostics[
            "max_physical_compact_field_relative_defect"
        ]
        < 1.0e-11,
        "v3_independent_orbit": pole.diagnostics[
            "independent_physical_compact_defect_inf"
        ]
        < float(acceptance["independent_difference"]),
        "v3_source_window_cone_margins": bool(
            pole_window.diagnostics["minimum_y"] > 20.0
            and pole_window.diagnostics["minimum_D"] > 40.0
            and pole_window.diagnostics["minimum_K"] > 200.0
            and pole_window.diagnostics["minimum_y_prime"] > 80.0
            and pole_window.diagnostics["minimum_K_prime"] > 1000.0
        ),
        "v3_source_graph_boundary_residuals": bool(
            pole_connection.source.diagnostics[
                "graph_boundary_residuals_passed"
            ]
            and max(
                float(
                    pole_connection.source.diagnostics[
                        "core_graph_boundary_residual_inf"
                    ]
                ),
                float(
                    pole_connection.source.diagnostics[
                        "positive_graph_boundary_residual_inf"
                    ]
                ),
            )
            <= float(source_config["graph_boundary_tolerance"])
        ),
        "v3_gate_event_and_energy": bool(
            float(pole_connection.gate.diagnostics["gate_residual"])
            <= float(acceptance["event_hit_residual"])
            and float(
                pole_connection.gate.diagnostics["source_to_gate_energy_drift"]
            )
            <= float(acceptance["energy_drift"])
            and float(pole_connection.gate.diagnostics["event_speed_physical"])
            > float(acceptance["complete_return_min_abs_event_speed"])
        ),
        "v3_same_orbit_global_local_overlap": max(
            float(
                pole_connection.diagnostics[
                    "global_local_physical_relative_defect_inf"
                ]
            ),
            float(
                pole_connection.diagnostics[
                    "global_local_compact_relative_defect_inf"
                ]
            ),
        )
        < float(acceptance["independent_difference"]),
        "v3_moving_cut": abs(pole_cut_balance["moving_cut_additivity_residual"])
        < 2.0e-7,
        "v3_action_density_crosscheck": float(
            pole_ladder.diagnostics[
                "physical_compact_density_relative_defect_inf"
            ]
        )
        < 1.0e-10,
        "v4_energy_equation": max(
            matched_pair.reference.diagnostics["energy_residual_inf"],
            matched_pair.neighboring.diagnostics["energy_residual_inf"],
        )
        < 1.0e-11,
        "v4_independent_gamma_grid_residuals": bool(
            np.max(gamma_solver_rms) <= gamma_tolerance
            and np.max(gamma_boundary_residual)
            <= float(matched_config.boundary_tolerance)
            and np.max(gamma_energy_residual) < 1.0e-11
        ),
        "v5_exact_chart_identity": abs(chart_outer["h_identity_residual"])
        < 1.0e-12,
        "v5_coupled_candidate_interfaces": max(
            abs(
                float(
                    matched_candidate.diagnostics[
                        "boundary_and_interface_residual_inf"
                    ]
                )
            ),
            abs(
                float(
                    matched_candidate.diagnostics[
                        "central_k1_q1_interface_residual"
                    ]
                )
            ),
        )
        < 1.0e-7,
        "v5_coupled_bvp_rms_residual": bool(
            float(matched_candidate.diagnostics["solver_rms_residual_max"])
            <= float(matched_config.tolerance)
            * float(acceptance["matched_bvp_rms_residual_factor"])
        ),
        "v5_frozen_phase_and_beta_brackets": bool(
            matched_candidate.diagnostics["source_phase_in_bracket"]
            and matched_candidate.diagnostics["seam_beta_in_bracket"]
        ),
        "v5_same_section_root_residual": bool(
            matched_candidate.diagnostics["same_section_root_passed"]
            and abs(
                float(
                    matched_candidate.diagnostics["same_section_root_residual"]
                )
            )
            <= float(matched_config.same_section_root_tolerance)
        ),
        "v5_coupled_candidate_energy": max(
            float(matched_candidate.diagnostics["central_energy_residual_inf"]),
            float(matched_candidate.diagnostics["k1_energy_residual_inf"]),
            float(matched_candidate.diagnostics["outer_energy_residual_inf"]),
        )
        < 1.0e-6,
        "v5_arrival_margins": bool(
            matched_candidate.diagnostics["scaled_arrival_margin_passed"]
            and matched_candidate.diagnostics["unscaled_arrival_margin_passed"]
        ),
        "v5_uniform_theorem_objects_not_interval_validated": bool(
            matched_candidate.validation_status == "NOT_INTERVAL_VALIDATED"
            and matching["status"] == "NOT_NUMERICALLY_RESOLVED"
        ),
        "v5a_cut_reference_gauge_balances": max(
            abs(float(v5a_balances[key]))
            for key in (
                "length_cut_balance",
                "action_cut_balance",
                "synthetic_reference_change_balance",
                "exact_gauge_composition_balance",
            )
        )
        < 1.0e-8,
        "v5a_endpoint_grid_refinement": max(
            abs(
                finite_part_refinement[-1]["relative_length"]
                - finite_part_refinement[-2]["relative_length"]
            ),
            abs(
                finite_part_refinement[-1]["relative_action"]
                - finite_part_refinement[-2]["relative_action"]
            ),
        )
        < float(acceptance["finite_part_grid_difference"]),
        "v6_refined_labels_stable": all(row["label_stable"] for row in refinement),
        "v6_complete_return_both_target_signs": {
            branch.target_sign_proxy for branch in complete_branches
        }
        == {"positive", "negative"},
        "v6_complete_return_composition": all(
            abs(float(branch.diagnostics["segment_length_composition_residual"]))
            < 1.0e-12
            and abs(
                float(branch.diagnostics["segment_action_composition_residual"])
            )
            < 1.0e-14
            for branch in complete_branches
        ),
        "v6_complete_return_face_residuals": bool(
            len(complete_branches) == 2
            and all(
                max(
                    float(branch.diagnostics["source_face_residual"]),
                    float(branch.diagnostics["incoming_face_residual"]),
                    float(branch.diagnostics["target_face_residual"]),
                )
                <= float(acceptance["event_hit_residual"])
                and bool(
                    branch.diagnostics["local_return_equals_source_radius"]
                )
                for branch in complete_branches
            )
        ),
        "v6_complete_return_event_transversality": bool(
            len(complete_branches) == 2
            and all(
                float(branch.diagnostics["incoming_event_speed"])
                < -float(acceptance["complete_return_min_abs_event_speed"])
                and float(branch.diagnostics["target_event_speed"])
                > float(acceptance["complete_return_min_abs_event_speed"])
                for branch in complete_branches
            )
        ),
        "v6_complete_return_energy": bool(
            len(complete_branches) == 2
            and all(
                max(
                    float(branch.diagnostics["energy_drift"]),
                    float(branch.diagnostics["energy_abs_max"]),
                )
                <= float(acceptance["energy_drift"])
                for branch in complete_branches
            )
        ),
        "v6_complete_return_action_quadrature": bool(
            len(complete_branches) == 2
            and all(
                abs(
                    float(branch.diagnostics["resampled_action_difference"])
                )
                <= float(
                    acceptance["complete_return_action_quadrature_difference"]
                )
                for branch in complete_branches
            )
        ),
        "v6_candidate_contract_hash_bound_not_run": bool(
            contract["claim_bearing"] is False
            and contract["final_status"] == "NOT_RUN"
            and not contract_failures
        ),
        "v6_finite_sampling_not_called_exhaustive": True,
        "frozen_configuration_interface_consumed": True,
        "v7_periodic_closure": max(
            report["diagnostics"]["closure_residual"] for report in periodic_reports
        )
        < float(acceptance["closure_residual"]),
        "v7_multipulse_residual_gates": all(
            bool(orbit.diagnostics.get("residual_gate_passed", True))
            for orbit in multipulses
        ),
        "v7_biinfinite_orbit_not_claimed": True,
    }

    def qa_metric(
        measured: float, threshold: float, comparator: str
    ) -> dict[str, float | str | bool | None]:
        if comparator == "<=":
            passed = measured <= threshold
        elif comparator == ">=":
            passed = measured >= threshold
        else:  # pragma: no cover - fixed internal schema
            raise ValueError(f"unsupported QA comparator: {comparator}")
        return {
            "measured": float(measured),
            "threshold": float(threshold),
            "comparator": comparator,
            "ratio": (
                float(measured / threshold) if threshold != 0.0 else None
            ),
            "passed": bool(passed),
        }

    maximum_complete_face_residual = max(
        (
            max(
                float(branch.diagnostics["source_face_residual"]),
                float(branch.diagnostics["incoming_face_residual"]),
                float(branch.diagnostics["target_face_residual"]),
            )
            for branch in complete_branches
        ),
        default=float(np.finfo(np.float64).max),
    )
    minimum_complete_event_speed = min(
        (
            min(
                abs(float(branch.diagnostics["incoming_event_speed"])),
                abs(float(branch.diagnostics["target_event_speed"])),
            )
            for branch in complete_branches
        ),
        default=0.0,
    )
    maximum_complete_energy_defect = max(
        (
            max(
                float(branch.diagnostics["energy_drift"]),
                float(branch.diagnostics["energy_abs_max"]),
            )
            for branch in complete_branches
        ),
        default=float(np.finfo(np.float64).max),
    )
    maximum_complete_quadrature_difference = max(
        (
            abs(float(branch.diagnostics["resampled_action_difference"]))
            for branch in complete_branches
        ),
        default=float(np.finfo(np.float64).max),
    )
    endpoint_grid_difference = max(
        abs(
            finite_part_refinement[-1]["relative_length"]
            - finite_part_refinement[-2]["relative_length"]
        ),
        abs(
            finite_part_refinement[-1]["relative_action"]
            - finite_part_refinement[-2]["relative_action"]
        ),
    )
    qa_metrics = {
        "v3_source_graph_boundary_residual": qa_metric(
            max(
                float(
                    pole_connection.source.diagnostics[
                        "core_graph_boundary_residual_inf"
                    ]
                ),
                float(
                    pole_connection.source.diagnostics[
                        "positive_graph_boundary_residual_inf"
                    ]
                ),
            ),
            float(source_config["graph_boundary_tolerance"]),
            "<=",
        ),
        "v3_gate_residual": qa_metric(
            float(pole_connection.gate.diagnostics["gate_residual"]),
            float(acceptance["event_hit_residual"]),
            "<=",
        ),
        "v3_gate_energy_drift": qa_metric(
            float(
                pole_connection.gate.diagnostics["source_to_gate_energy_drift"]
            ),
            float(acceptance["energy_drift"]),
            "<=",
        ),
        "v4_gamma_solver_rms_residual": qa_metric(
            float(np.max(gamma_solver_rms)), gamma_tolerance, "<="
        ),
        "v4_gamma_boundary_residual": qa_metric(
            float(np.max(gamma_boundary_residual)),
            float(matched_config.boundary_tolerance),
            "<=",
        ),
        "v4_gamma_energy_residual": qa_metric(
            float(np.max(gamma_energy_residual)), 1.0e-11, "<="
        ),
        "v5_coupled_bvp_rms_residual": qa_metric(
            float(matched_candidate.diagnostics["solver_rms_residual_max"]),
            float(matched_config.tolerance)
            * float(acceptance["matched_bvp_rms_residual_factor"]),
            "<=",
        ),
        "v5_same_section_root_residual": qa_metric(
            abs(
                float(
                    matched_candidate.diagnostics["same_section_root_residual"]
                )
            ),
            float(matched_config.same_section_root_tolerance),
            "<=",
        ),
        "v5_phase_bracket_margin": qa_metric(
            float(matched_candidate.diagnostics["source_phase_bracket_margin"]),
            0.0,
            ">=",
        ),
        "v5_beta_bracket_margin": qa_metric(
            float(matched_candidate.diagnostics["seam_beta_bracket_margin"]),
            0.0,
            ">=",
        ),
        "v6_complete_face_residual": qa_metric(
            maximum_complete_face_residual,
            float(acceptance["event_hit_residual"]),
            "<=",
        ),
        "v6_complete_min_abs_event_speed": qa_metric(
            minimum_complete_event_speed,
            float(acceptance["complete_return_min_abs_event_speed"]),
            ">=",
        ),
        "v6_complete_energy_defect": qa_metric(
            maximum_complete_energy_defect,
            float(acceptance["energy_drift"]),
            "<=",
        ),
        "v6_complete_action_quadrature_difference": qa_metric(
            maximum_complete_quadrature_difference,
            float(
                acceptance["complete_return_action_quadrature_difference"]
            ),
            "<=",
        ),
        "v5a_endpoint_grid_difference": qa_metric(
            endpoint_grid_difference,
            float(acceptance["finite_part_grid_difference"]),
            "<=",
        ),
    }
    qa = {
        "status": (
            "PASS_WITH_EXPLICIT_UNRESOLVED_THEOREM_OBJECTS"
            if all(qa_checks.values())
            else "FAIL_OR_INCONCLUSIVE"
        ),
        "checks": qa_checks,
        "metrics": qa_metrics,
        "frozen_configuration_interface": {
            section: sorted(keys)
            for section, keys in FROZEN_INTERFACE_KEYS.items()
        },
        "unresolved_are_not_failures_of_the_paper": [
            "V3 certified uniform parameter box and improper-limit enclosure",
            "V4 infinite future-staying graph and uniform cocycle/bunching bounds",
            "V5 uniform tube, adjoint/exchange, uniqueness, and parameter derivatives",
            "V6 exhaustive theorem-coordinate cells, cross forms, and all-winding bounds",
            "V7 theorem-edge itineraries and a bi-infinite numerical orbit",
        ],
    }
    write_json(output / "qa.json", qa)

    source_files = [
        config_path,
        ROOT / "numerics" / "rfsn_numerics.py",
        ROOT / "numerics" / "vdp_bridge.py",
        ROOT / "numerics" / "vdp_central.py",
        ROOT / "numerics" / "vdp_pole.py",
        ROOT / "numerics" / "vdp_source_to_pole.py",
        ROOT / "numerics" / "vdp_outer.py",
        ROOT / "numerics" / "vdp_matched_outer.py",
        ROOT / "numerics" / "vdp_return_coding.py",
        ROOT / "numerics" / "vdp_complete_branches.py",
        ROOT / "validation" / "candidate_contract.schema.json",
        ROOT / "validation" / "environment.lock.json",
        ROOT / "validation" / "check_candidate_contract.py",
        ROOT / "validation" / "build_vdp_candidate_contract.py",
        Path(__file__),
        ROOT / "numerics" / "render_vdp_figures.py",
        ROOT / "numerics" / "check_vdp_master.py",
    ]

    def build_manifest(result_files: list[Path]) -> dict[str, Any]:
        return {
            "evidence_status": config["evidence_status"],
            "configuration_version": config["configuration_version"],
            "qa_status": qa["status"],
            "repository_commit": git_text("rev-parse", "HEAD"),
            "repository_dirty": bool(git_text("status", "--porcelain")),
            "environment": {
                "python": sys.version,
                "platform": platform.platform(),
                "numpy": np.__version__,
                "scipy": scipy.__version__,
                "matplotlib": matplotlib.__version__,
            },
            "parameters": config["parameters"],
            "nonclaims": config["nonclaims"],
            "source_hashes": {
                str(path.relative_to(ROOT)): sha256(path) for path in source_files
            },
            "result_hashes": {
                path.name: sha256(path) for path in result_files if path.is_file()
            },
            "result_files": [
                path.name for path in result_files if path.is_file()
            ],
        }

    # Figure 9 displays configuration and raw-result provenance.  Write a
    # pre-render manifest that excludes figures, render against that current
    # metadata, and then replace it with the final manifest including the new
    # figure hashes.  This prevents a rerun from silently displaying the
    # previous configuration's manifest while still avoiding a figure/manifest
    # hash cycle.
    pre_render_result_files = sorted(
        path
        for path in output.iterdir()
        if path.name != "manifest.json" and not path.name.startswith("figure_")
    )
    write_json(output / "manifest.json", build_manifest(pre_render_result_files))

    print("[FIGURES] rendering nine contract-driven figures", flush=True)
    from numerics.render_vdp_figures import render_all

    render_all(output)

    result_files = sorted(
        path for path in output.iterdir() if path.name != "manifest.json"
    )
    manifest = build_manifest(result_files)
    write_json(output / "manifest.json", manifest)
    print(f"done: {output}", flush=True)
    print(f"QA: {qa['status']}", flush=True)


if __name__ == "__main__":
    main()
