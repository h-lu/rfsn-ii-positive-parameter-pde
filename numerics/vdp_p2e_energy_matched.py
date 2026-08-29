"""Energy-preserving small-r central--K1--outer matched centerline.

This floating-point solve removes the central collocation leg.  A true central
IVP supplies the common cut, while the reduced K1 and positive-pi outer BVP
solves simultaneously for source phase and energy.  The missing q1 seam
equation is an explicit boundary condition.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_bvp, solve_ivp

from numerics.rfsn_numerics import vdp_field, vdp_hamiltonian
from numerics.vdp_matched_outer import (
    _positive_pi_bvp_grid,
    central_to_resolved_k1,
    finite_horizon_gamma_continuation,
    k1_center_graph_leading_guess,
    outer_seam_coordinates,
    resolved_k1_energy_equation_residual,
    resolved_k1_energy_root,
    resolved_k1_rhs_r1,
    resolved_k1_to_outer_normal,
)
from numerics.vdp_outer import (
    OuterParameters,
    energy_equation_residual,
    normal_to_positive_pi_state,
    positive_pi_outer_rhs_q,
    positive_pi_outer_state,
)
from numerics.vdp_p2e_algebraic_coordinate_diagnosis import _candidate_config
from numerics.vdp_p2e_channel_scout import (
    DEFAULT_CONFIG,
    _direct_kato_provider,
    _load_config,
)


Array = NDArray[np.float64]
HERE = Path(__file__).resolve().parent
DEFAULT_RESULT = (
    HERE / "results/vdp_p2e_channel_scout_v2/energy_matched_centerline.json"
)
DEFAULT_DATA = (
    HERE / "results/vdp_p2e_channel_scout_v2/energy_matched_centerline.npz"
)
ENERGY_H_HALF_WIDTH = 1.0
SOLVER_TOLERANCE = 1.0e-6
THRESHOLDS = {
    "boundary_residual_inf": 1.0e-9,
    "central_energy_abs": 1.0e-10,
    "central_energy_alignment_abs": 1.0e-10,
    "k1_energy_equation_residual_inf": 1.0e-12,
    "outer_energy_equation_residual_inf": 1.0e-12,
    "central_k1_state_seam_residual_inf": 1.0e-9,
    "k1_outer_normal_seam_residual_inf": 1.0e-11,
    "same_section_root_residual_abs": 1.0e-10,
}


class EnergyMatchedError(RuntimeError):
    """The predeclared energy-preserving solve or its QA failed."""


def _central_to_k1_full(
    state: Array, parameters: OuterParameters, r1_cut: float
) -> Array:
    pi_omega = central_to_resolved_k1(state, parameters)
    sigma = parameters.r / r1_cut
    q1 = -parameters.epsilon ** (-0.25) * sigma**3 * state[3]
    return np.array([pi_omega[0], pi_omega[1], q1], dtype=np.float64)


def _k1_to_central_full(
    r1: Array, state: Array, parameters: OuterParameters
) -> Array:
    pi_scaled, omega_scaled, q1 = state
    sigma = parameters.r / r1
    sqrt_epsilon = np.sqrt(parameters.epsilon)
    u = parameters.r * parameters.a2 - sigma**-2
    p = -parameters.epsilon**0.25 * sigma**-1 * pi_scaled
    q = -parameters.epsilon**0.25 * sigma**-3 * q1
    v = (
        parameters.r**2 * parameters.a2**2
        + sqrt_epsilon * parameters.r**5 * parameters.a2**3 / 3.0
        - sigma**-4
        * (1.0 + sqrt_epsilon * r1**2 / 3.0 - sigma**2 * omega_scaled)
    )
    return np.vstack((u, p, v, q))


def _central_section_provider(
    parameters: OuterParameters,
    section_m: float,
    source_provider: Callable[[float], Array],
) -> Callable[[float], tuple[Any, float]]:
    cache: dict[float, tuple[Any, float]] = {}
    field = vdp_field(parameters.r, parameters.a2, parameters.epsilon)

    def section(phase: float) -> tuple[Any, float]:
        key = float(phase)
        if key not in cache:
            initial = source_provider(key)

            def event(_time: float, state: Array) -> float:
                return float(state[0] + section_m)

            event.direction = -1.0  # type: ignore[attr-defined]
            event.terminal = True  # type: ignore[attr-defined]
            integration = solve_ivp(
                lambda time, state: field(
                    np.array([time]), state.reshape(4, 1)
                )[:, 0],
                (0.0, 40.0),
                initial,
                method="DOP853",
                events=event,
                rtol=2.0e-11,
                atol=2.0e-13,
                max_step=0.02,
                dense_output=True,
            )
            if (
                not integration.success
                or integration.sol is None
                or not len(integration.t_events[0])
            ):
                raise EnergyMatchedError("source orbit did not reach U=-M")
            cache[key] = (integration, float(integration.t_events[0][0]))
        return cache[key]

    section.unique_evaluations = lambda: len(cache)  # type: ignore[attr-defined]
    return section


def compute_energy_matched_centerline() -> tuple[dict[str, Any], dict[str, Array]]:
    frozen = _load_config(DEFAULT_CONFIG)
    config = _candidate_config(frozen)
    source = frozen["common_source_convention"]
    choices = frozen["algebraic_matched_single_attempt"]
    parameters = OuterParameters(r=3.0 / 200.0, a2=0.0, epsilon=1.0)
    provider = _direct_kato_provider(
        r=parameters.r,
        a2=parameters.a2,
        epsilon=parameters.epsilon,
        source_radius=float(source["source_radius"]),
        graph_horizon=float(source["graph_horizon"]),
        graph_boundary_tolerance=float(source["graph_boundary_tolerance"]),
    )
    central_section = _central_section_provider(
        parameters, config.section_m, provider
    )
    _z_r, q_r = outer_seam_coordinates(
        parameters, outer_r1=config.outer_r1
    )
    r1_cut = parameters.r * np.sqrt(
        config.section_m + parameters.r * parameters.a2
    )
    r1_span = config.outer_r1 - r1_cut
    q_span = config.q_end - q_r
    mesh = _positive_pi_bvp_grid(
        0.0,
        1.0,
        config.mesh_points,
        parameters.delta / q_span,
    )
    r1_mesh = r1_cut + r1_span * mesh
    q_mesh = q_r + q_span * mesh
    k1_guess = k1_center_graph_leading_guess(r1_mesh, parameters)
    outer_leading = resolved_k1_to_outer_normal(
        k1_guess[:, -1], parameters, outer_r1=config.outer_r1
    )
    gamma_seed = finite_horizon_gamma_continuation(
        parameters,
        (0.0, float(outer_leading[0])),
        q_start=q_r,
        q_end=config.q_end,
        points=max(301, config.output_points // 2),
        tolerance=2.0e-8,
        max_nodes=config.max_nodes,
        positive_pi=True,
    ).samples[-1]
    outer_normal_guess = np.vstack((
        np.interp(q_mesh, gamma_seed.compact_q, gamma_seed.beta),
        np.interp(q_mesh, gamma_seed.compact_q, gamma_seed.alpha),
    ))
    outer_guess = normal_to_positive_pi_state(
        q_mesh, outer_normal_guess, parameters
    )
    initial_guess = np.vstack((k1_guess, outer_guess))
    energy_scale = parameters.epsilon**2.5 * parameters.r**6

    def energy_h(unknown: Array) -> float:
        return float(ENERGY_H_HALF_WIDTH * np.tanh(unknown[1]))

    def field(normalized: Array, state: Array, unknown: Array) -> Array:
        h_value = energy_h(unknown)
        r1 = r1_cut + r1_span * normalized
        compact_q = q_r + q_span * normalized
        return np.vstack((
            r1_span
            * resolved_k1_rhs_r1(
                r1, state[:2], parameters, energy_h=h_value
            ),
            q_span
            * positive_pi_outer_rhs_q(
                compact_q,
                state[2:4],
                parameters,
                energy=energy_scale * h_value,
            ),
        ))

    def boundary(left: Array, right: Array, unknown: Array) -> Array:
        phase = float(unknown[0])
        h_value = energy_h(unknown)
        central_integration, central_time = central_section(phase)
        central_cut = np.asarray(
            central_integration.sol(central_time), dtype=np.float64
        )
        k1_target = _central_to_k1_full(
            central_cut, parameters, r1_cut
        )
        q1_left = float(resolved_k1_energy_root(
            r1_cut,
            left[0],
            left[1],
            parameters,
            energy_h=h_value,
        ))
        outer_target = resolved_k1_to_outer_normal(
            right[:2],
            parameters,
            outer_r1=config.outer_r1,
            energy_h=h_value,
        )
        positive_outer_target = normal_to_positive_pi_state(
            q_r,
            outer_target,
            parameters,
            energy=energy_scale * h_value,
        )
        terminal_alpha = positive_pi_outer_state(
            config.q_end,
            right[2:4],
            parameters,
            energy=energy_scale * h_value,
        )[1]
        return np.concatenate((
            left[:2] - k1_target[:2],
            np.array([q1_left - k1_target[2]]),
            left[2:4] - positive_outer_target,
            np.array([terminal_alpha / parameters.delta]),
        ))

    initial_phase = float(choices["core_phase_midpoint"])
    solution = solve_bvp(
        field,
        boundary,
        mesh,
        initial_guess,
        p=np.array([initial_phase, 0.0], dtype=np.float64),
        tol=SOLVER_TOLERANCE,
        bc_tol=1.0e-10,
        max_nodes=config.max_nodes,
        verbose=0,
    )
    if not solution.success:
        raise EnergyMatchedError(
            f"energy-preserving coupled BVP failed: {solution.message}"
        )

    phase = float(solution.p[0])
    h_value = energy_h(solution.p)
    outer_energy = energy_scale * h_value
    output_phase = np.linspace(0.0, 1.0, config.output_points)
    normalized = 0.5 * (1.0 - np.cos(np.pi * output_phase))
    state = np.asarray(solution.sol(normalized), dtype=np.float64)
    r1 = r1_cut + r1_span * normalized
    compact_q = q_r + q_span * normalized
    pi_scaled, omega_scaled = state[:2]
    q1 = resolved_k1_energy_root(
        r1,
        pi_scaled,
        omega_scaled,
        parameters,
        energy_h=h_value,
    )
    k1_state = np.vstack((pi_scaled, omega_scaled, q1))
    outer_beta, outer_alpha, outer_chi, outer_pi, _outer_w = (
        positive_pi_outer_state(
            compact_q, state[2:4], parameters, energy=outer_energy
        )
    )
    outer_state = np.vstack((outer_beta, outer_alpha))
    central_integration, central_time = central_section(phase)
    central_xi = central_time * normalized
    central_state = np.asarray(
        central_integration.sol(central_xi), dtype=np.float64
    )
    boundary_residual = boundary(
        state[:, 0], state[:, -1], solution.p
    )
    central_energy = vdp_hamiltonian(
        central_state,
        parameters.r,
        parameters.a2,
        parameters.epsilon,
    )
    k1_energy_residual = resolved_k1_energy_equation_residual(
        r1,
        pi_scaled,
        omega_scaled,
        q1,
        parameters,
        energy_h=h_value,
    )
    outer_energy_residual = energy_equation_residual(
        compact_q ** (-0.5),
        outer_beta,
        outer_alpha,
        outer_chi,
        parameters,
        energy=outer_energy,
    )
    k1_central_start = _k1_to_central_full(
        np.array([r1[0]]), k1_state[:, :1], parameters
    )[:, 0]
    central_k1_seam = float(
        np.max(np.abs(central_state[:, -1] - k1_central_start))
    )
    expected_outer_start = resolved_k1_to_outer_normal(
        k1_state[:2, -1],
        parameters,
        outer_r1=config.outer_r1,
        energy_h=h_value,
    )
    k1_outer_seam = float(
        np.max(np.abs(outer_state[:, 0] - expected_outer_start))
    )
    independent_gamma = finite_horizon_gamma_continuation(
        parameters,
        (0.0, float(outer_state[0, 0])),
        q_start=q_r,
        q_end=config.q_end,
        points=max(301, config.output_points // 2),
        tolerance=2.0e-8,
        max_nodes=config.max_nodes,
        positive_pi=True,
        energy=outer_energy,
    ).samples[-1].gamma
    same_section_residual = float(
        outer_state[1, 0] - independent_gamma
    )
    phase_bounds = config.source_phase_bounds
    diagnostics = {
        "solver_success": True,
        "solver_nodes": int(solution.x.size),
        "solver_rms_residual_max": float(np.max(solution.rms_residuals)),
        "solver_tolerance": SOLVER_TOLERANCE,
        "boundary_residual_inf": float(np.max(np.abs(boundary_residual))),
        "central_energy_abs_max": float(np.max(np.abs(central_energy))),
        "central_energy_drift": float(np.ptp(central_energy)),
        "resolved_k1_energy_equation_residual_inf": float(
            np.max(np.abs(k1_energy_residual))
        ),
        "outer_energy_equation_residual_inf": float(
            np.max(np.abs(outer_energy_residual))
        ),
        "central_k1_state_seam_residual_inf": central_k1_seam,
        "k1_outer_normal_seam_residual_inf": k1_outer_seam,
        "same_section_root_residual": same_section_residual,
        "minimum_k1_pi_scaled": float(np.min(pi_scaled)),
        "minimum_k1_q1": float(np.min(q1)),
        "minimum_outer_pi": float(np.min(outer_pi)),
        "energy_h": h_value,
        "energy_h_minus_central_endpoint": float(
            h_value - central_energy[-1]
        ),
        "source_phase": phase,
        "source_phase_in_frozen_bracket": bool(
            phase_bounds[0] <= phase <= phase_bounds[1]
        ),
        "central_cut_P": float(central_state[1, -1]),
        "central_cut_Q": float(central_state[3, -1]),
        "central_cut_algebraic_orientation": bool(
            central_state[1, -1] < 0.0 and central_state[3, -1] < 0.0
        ),
        "source_provider_unique_evaluations": int(
            getattr(provider, "unique_evaluations", 0)
        ),
        "central_section_unique_evaluations": int(
            central_section.unique_evaluations()  # type: ignore[attr-defined]
        ),
    }
    qa = {
        "solver_residual": diagnostics["solver_rms_residual_max"]
        <= SOLVER_TOLERANCE,
        "boundary_residual": diagnostics["boundary_residual_inf"]
        <= THRESHOLDS["boundary_residual_inf"],
        "central_energy": diagnostics["central_energy_abs_max"]
        <= THRESHOLDS["central_energy_abs"],
        "central_energy_alignment": abs(
            diagnostics["energy_h_minus_central_endpoint"]
        ) <= THRESHOLDS["central_energy_alignment_abs"],
        "k1_energy": diagnostics[
            "resolved_k1_energy_equation_residual_inf"
        ] <= THRESHOLDS["k1_energy_equation_residual_inf"],
        "outer_energy": diagnostics["outer_energy_equation_residual_inf"]
        <= THRESHOLDS["outer_energy_equation_residual_inf"],
        "central_k1_seam": central_k1_seam
        <= THRESHOLDS["central_k1_state_seam_residual_inf"],
        "k1_outer_seam": k1_outer_seam
        <= THRESHOLDS["k1_outer_normal_seam_residual_inf"],
        "same_section": abs(same_section_residual)
        <= THRESHOLDS["same_section_root_residual_abs"],
        "positive_branches": bool(
            np.min(pi_scaled) > 0.0
            and np.min(q1) > 0.0
            and np.min(outer_pi) > 0.0
        ),
        "phase_and_orientation": bool(
            diagnostics["source_phase_in_frozen_bracket"]
            and diagnostics["central_cut_algebraic_orientation"]
        ),
    }
    all_passed = all(qa.values())
    report = {
        "schema_version": "rfsn-vdp-p2e-energy-matched-centerline/1",
        "status": (
            "ENERGY_PRESERVING_MATCHED_CENTERLINE_SUCCESS"
            if all_passed
            else "ENERGY_PRESERVING_MATCHED_CENTERLINE_REJECTED"
        ),
        "evidence_status": "COMPUTED/E1_NON_RIGOROUS",
        "claim_bearing": False,
        "parameter_point": {"r": "3/200", "a2": "0", "epsilon": "1"},
        "source_phase": phase,
        "central_flight_time": central_time,
        "energy_h": h_value,
        "equation_count": {
            "state_unknowns": 4,
            "scalar_parameters": ["source_phase", "energy_h_chart"],
            "boundary_equations": 6,
            "rows": [
                "central_to_K1_Pi",
                "central_to_K1_Omega",
                "central_to_K1_q1",
                "K1_to_outer_eta",
                "K1_to_outer_omega",
                "outer_terminal_alpha",
            ],
        },
        "diagnostics": diagnostics,
        "thresholds": THRESHOLDS,
        "qa": qa,
        "nonclaim": (
            "One finite-horizon three-segment floating-point centerline is "
            "not a parameter-box channel, V5 theorem validation, or V2 atlas."
        ),
    }
    arrays = {
        "central_xi": central_xi,
        "central_state": central_state,
        "k1_r1": r1,
        "k1_state_Pi_Omega_q1": k1_state,
        "outer_Q": compact_q,
        "outer_state_beta_alpha": outer_state,
        "outer_chi": outer_chi,
        "outer_pi": outer_pi,
    }
    if not all_passed:
        raise EnergyMatchedError(
            "energy-preserving candidate failed predeclared QA: "
            + ", ".join(key for key, passed in qa.items() if not passed)
        )
    return report, arrays


def main() -> None:
    report, arrays = compute_energy_matched_centerline()
    DEFAULT_RESULT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(DEFAULT_DATA, **arrays)
    report["data_path"] = str(DEFAULT_DATA.relative_to(HERE.parent))
    report["array_shapes"] = {
        key: list(value.shape) for key, value in arrays.items()
    }
    DEFAULT_RESULT.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(report["status"])
    print(DEFAULT_RESULT)


if __name__ == "__main__":
    main()
