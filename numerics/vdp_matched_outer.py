"""Finite-horizon V4/V5 matched candidates for the van der Pol example.

The analytic V4 graph is normally expanding in forward outer time.  A
one-way shooting calculation is consequently ill-conditioned: a tiny normal
error at the central cut becomes enormous before the outer cut.  This module
instead solves the central, resolved-``K1``, and outer pieces simultaneously
as one collocation problem.  Its terminal condition is still the finite-
horizon condition ``alpha(Q_end)=0``.  The output is therefore ordinary
floating-point evidence, never an interval proof of V4 or V5.

The default source curve is the finite-horizon nonlinear ``W^u`` realization
from :mod:`numerics.vdp_source_to_pole`.  The older zero-energy linear-section
proxy remains available explicitly for fast regression tests.  This
separation is intentional: a zero-energy linear-eigenplane section must not be
silently renamed the theorem's true ``W^u`` source circle.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Iterable, Mapping

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import cumulative_trapezoid, solve_bvp, solve_ivp
from scipy.interpolate import CubicSpline

from numerics.rfsn_numerics import vdp_field, vdp_hamiltonian
from numerics.vdp_bridge import BridgeParameters, central_to_physical, cubic_f
from numerics.vdp_outer import (
    OuterParameters,
    energy_equation_residual,
    normal_to_positive_pi_state,
    normal_outer_rhs_q,
    normal_outer_state,
    outer_physical_densities,
    positive_pi_outer_rhs_q,
    positive_pi_outer_state,
)
from numerics.vdp_pole import PoleParameters
from numerics.vdp_return_coding import (
    SaddleFrame,
    reversible_saddle_frame,
    zero_energy_source_state,
)
from numerics.vdp_source_to_pole import compute_v2_source_candidate


FloatArray = NDArray[np.float64]
SourceStateProvider = Callable[[float], FloatArray]

COMPUTED_E1_MATCHED_CANDIDATE = "COMPUTED/E1_MATCHED_CANDIDATE"
NOT_INTERVAL_VALIDATED = "NOT_INTERVAL_VALIDATED"


@dataclass(frozen=True)
class MatchedOuterConfig:
    """Frozen finite-horizon choices for one positive-parameter candidate."""

    section_m: float = 4.0
    outer_r1: float = 2.0
    q_label: float = 100.0
    q_end: float = 200.0
    source_radius: float = 0.01
    source_phase_seed: float = 5.4109
    source_phase_reference_midpoint: float = 5.4088
    source_phase_offset_bracket: tuple[float, float] = (0.002, 0.0022)
    source_flowback_tau: float = 2.0
    source_graph_horizon: float = 8.0
    source_graph_boundary_tolerance: float = 1.0e-8
    seam_beta_bracket: tuple[float, float] = (0.0, 4.0e-4)
    scaled_beta_collar: float = 0.25
    mesh_points: int = 401
    output_points: int = 801
    tolerance: float = 2.0e-5
    boundary_tolerance: float = 1.0e-8
    same_section_root_tolerance: float = 2.0e-12
    max_nodes: int = 60_000

    def __post_init__(self) -> None:
        if self.section_m <= 0.0:
            raise ValueError("section_m must be positive")
        if self.outer_r1 <= 0.0:
            raise ValueError("outer_r1 must be positive")
        if self.source_radius <= 0.0:
            raise ValueError("source_radius must be positive")
        if self.source_flowback_tau <= 0.0:
            raise ValueError("source_flowback_tau must be positive")
        if self.source_graph_horizon <= 0.0:
            raise ValueError("source_graph_horizon must be positive")
        if self.source_graph_boundary_tolerance <= 0.0:
            raise ValueError("source_graph_boundary_tolerance must be positive")
        phase_lower, phase_upper = self.source_phase_bounds
        if not phase_lower < phase_upper:
            raise ValueError("source_phase_offset_bracket must be increasing")
        if not phase_lower <= self.source_phase_seed <= phase_upper:
            raise ValueError("source_phase_seed must lie in the frozen phase bracket")
        beta_lower, beta_upper = self.seam_beta_bracket
        if not beta_lower < beta_upper:
            raise ValueError("seam_beta_bracket must be increasing")
        if self.scaled_beta_collar <= 0.0:
            raise ValueError("scaled_beta_collar must be positive")
        if self.mesh_points < 81 or self.output_points < 81:
            raise ValueError("mesh_points and output_points must be at least 81")
        if (
            self.tolerance <= 0.0
            or self.boundary_tolerance <= 0.0
            or self.same_section_root_tolerance <= 0.0
        ):
            raise ValueError("solver tolerances must be positive")

    @property
    def source_phase_bounds(self) -> tuple[float, float]:
        return (
            self.source_phase_reference_midpoint
            + float(self.source_phase_offset_bracket[0]),
            self.source_phase_reference_midpoint
            + float(self.source_phase_offset_bracket[1]),
        )


@dataclass(frozen=True)
class FiniteHorizonGammaSample:
    """One point of the finite-horizon graph ``alpha=Gamma(beta)``."""

    beta0: float
    compact_q: FloatArray
    beta: FloatArray
    alpha: FloatArray
    diagnostics: Mapping[str, float | bool]
    evidence_status: str = COMPUTED_E1_MATCHED_CANDIDATE
    validation_status: str = NOT_INTERVAL_VALIDATED

    @property
    def gamma(self) -> float:
        return float(self.alpha[0])


@dataclass(frozen=True)
class FiniteHorizonGammaContinuation:
    """Continuation samples at a common outer section and horizon."""

    q_start: float
    q_end: float
    samples: tuple[FiniteHorizonGammaSample, ...]
    evidence_status: str = COMPUTED_E1_MATCHED_CANDIDATE
    validation_status: str = NOT_INTERVAL_VALIDATED

    def gamma_at(self, beta0: float) -> float:
        for sample in self.samples:
            if sample.beta0 == beta0:
                return sample.gamma
        raise KeyError(f"beta0={beta0!r} is not in this continuation")


@dataclass(frozen=True)
class MatchedOuterCandidate:
    """One same-orbit central--K1--outer finite-horizon candidate."""

    parameters: OuterParameters
    config: MatchedOuterConfig
    source_phase: float
    central_flight_time: float
    normalized_grid: FloatArray
    central_state: FloatArray
    k1_r1: FloatArray
    k1_state: FloatArray
    compact_q: FloatArray
    outer_state: FloatArray
    diagnostics: Mapping[str, float | bool | str]
    evidence_status: str = COMPUTED_E1_MATCHED_CANDIDATE
    validation_status: str = NOT_INTERVAL_VALIDATED

    @property
    def seam_beta(self) -> float:
        return float(self.outer_state[0, 0])

    @property
    def seam_alpha(self) -> float:
        return float(self.outer_state[1, 0])


@dataclass(frozen=True)
class MatchedOuterRefinement:
    """Full matched solves on a predeclared outer-horizon ladder."""

    q_end: FloatArray
    source_phase: FloatArray
    central_flight_time: FloatArray
    seam_beta: FloatArray
    seam_alpha: FloatArray
    label_beta: FloatArray
    consecutive_state_difference: FloatArray
    candidates: tuple[MatchedOuterCandidate, ...]
    evidence_status: str = COMPUTED_E1_MATCHED_CANDIDATE
    validation_status: str = NOT_INTERVAL_VALIDATED


@dataclass(frozen=True)
class MatchedActionDecomposition:
    """Finite V5 action/length split on one computed matched orbit.

    The three cumulative arrays end at the fixed V5A normalization cut.
    They realize V5(61)--(62) and the exact outer density on one floating-
    point candidate; they are not an improper finite part or a uniform
    parameter statement.
    """

    central_xi: FloatArray
    central_action: FloatArray
    central_length: FloatArray
    k1_r1: FloatArray
    k1_action: FloatArray
    k1_action_central_pullback: FloatArray
    k1_length: FloatArray
    outer_q: FloatArray
    outer_action: FloatArray
    outer_length: FloatArray
    diagnostics: Mapping[str, float | bool | str]
    evidence_status: str = "COMPUTED/E1_V5_FINITE_ACTION_DECOMPOSITION"
    validation_status: str = NOT_INTERVAL_VALIDATED

    @property
    def total_action(self) -> float:
        return float(
            self.central_action[-1]
            + self.k1_action[-1]
            + self.outer_action[-1]
        )

    @property
    def total_length(self) -> float:
        return float(
            self.central_length[-1]
            + self.k1_length[-1]
            + self.outer_length[-1]
        )

    def as_json_dict(self) -> dict[str, object]:
        return {
            "status": self.evidence_status,
            "validation_status": self.validation_status,
            "claim_bearing": False,
            "cuts": {
                "central_start_xi": float(self.central_xi[0]),
                "central_k1_xi": float(self.central_xi[-1]),
                "k1_start_r1": float(self.k1_r1[0]),
                "k1_outer_r1": float(self.k1_r1[-1]),
                "outer_start_q_r": float(self.outer_q[0]),
                "terminal_q_star": float(self.outer_q[-1]),
            },
            "action": {
                "central": float(self.central_action[-1]),
                "resolved_k1": float(self.k1_action[-1]),
                "outer_qr_to_qstar": float(self.outer_action[-1]),
                "truncated_total_to_qstar": self.total_action,
            },
            "physical_length": {
                "central": float(self.central_length[-1]),
                "resolved_k1": float(self.k1_length[-1]),
                "outer_qr_to_qstar": float(self.outer_length[-1]),
                "truncated_total_to_qstar": self.total_length,
            },
            "diagnostics": dict(self.diagnostics),
            "scope": (
                "Finite central--K1--outer action and length on one matched "
                "candidate, ending at Q_*.  No endpoint adjoint, uniform "
                "matching theorem, or infinite-tail finite part is claimed."
            ),
        }

    def as_npz_payload(self) -> dict[str, FloatArray]:
        return {
            "v5_central_xi": self.central_xi,
            "v5_central_action": self.central_action,
            "v5_central_length": self.central_length,
            "v5_k1_r1": self.k1_r1,
            "v5_k1_action": self.k1_action,
            "v5_k1_action_central_pullback": self.k1_action_central_pullback,
            "v5_k1_length": self.k1_length,
            "v5_outer_q": self.outer_q,
            "v5_outer_action": self.outer_action,
            "v5_outer_length": self.outer_length,
        }


def _as_float_array(value: ArrayLike) -> FloatArray:
    return np.asarray(value, dtype=np.float64)


def outer_seam_coordinates(
    parameters: OuterParameters, *, outer_r1: float
) -> tuple[float, float]:
    """Return ``(z_R,Q_R)`` for the physical ``K1`` cut ``r1=R``."""

    if outer_r1 <= 0.0:
        raise ValueError("outer_r1 must be positive")
    z_r = 1.0 / (1.0 + np.sqrt(parameters.epsilon) * outer_r1**2)
    return float(z_r), float(z_r**-2)


def resolved_k1_energy_root(
    r1: ArrayLike,
    pi_scaled: ArrayLike,
    omega_scaled: ArrayLike,
    parameters: OuterParameters,
    *,
    energy_h: float = 0.0,
) -> FloatArray:
    """Positive ``q1`` root in V5 equation (34)."""

    r1_array, pi_array, omega_array = np.broadcast_arrays(
        _as_float_array(r1),
        _as_float_array(pi_scaled),
        _as_float_array(omega_scaled),
    )
    if np.any(r1_array <= 0.0):
        raise ValueError("r1 must be positive on a fixed positive leaf")
    sigma = parameters.r / r1_array
    sqrt_epsilon = np.sqrt(parameters.epsilon)
    a2 = parameters.a2
    numerator = (
        8.0
        + 3.0 * sqrt_epsilon * r1_array**2
        - 12.0 * omega_array * sigma**2
        - (
            4.0 * sqrt_epsilon * a2 * r1_array**3
            + 12.0 * a2 * r1_array
        )
        * sigma**3
        + 6.0 * sqrt_epsilon * pi_array**2 * sigma**4
        + 12.0 * omega_array * a2 * r1_array * sigma**5
        + 12.0 * energy_h * sigma**6
        + 4.0 * a2**3 * r1_array**3 * sigma**9
        + sqrt_epsilon * a2**4 * r1_array**6 * sigma**12
    )
    radicand = numerator / (6.0 * sqrt_epsilon)
    if np.any(radicand <= 0.0):
        raise ValueError("resolved K1 energy root lost its positive branch")
    return np.sqrt(radicand)


def resolved_k1_energy_equation_residual(
    r1: ArrayLike,
    pi_scaled: ArrayLike,
    omega_scaled: ArrayLike,
    q1: ArrayLike,
    parameters: OuterParameters,
    *,
    energy_h: float = 0.0,
) -> FloatArray:
    """Residual of the exact resolved-``K1`` energy equation V5(34)."""

    r1_array, pi_array, omega_array, q1_array = np.broadcast_arrays(
        _as_float_array(r1),
        _as_float_array(pi_scaled),
        _as_float_array(omega_scaled),
        _as_float_array(q1),
    )
    sigma = parameters.r / r1_array
    sqrt_epsilon = np.sqrt(parameters.epsilon)
    a2 = parameters.a2
    right = (
        8.0
        + 3.0 * sqrt_epsilon * r1_array**2
        - 12.0 * omega_array * sigma**2
        - (
            4.0 * sqrt_epsilon * a2 * r1_array**3
            + 12.0 * a2 * r1_array
        )
        * sigma**3
        + 6.0 * sqrt_epsilon * pi_array**2 * sigma**4
        + 12.0 * omega_array * a2 * r1_array * sigma**5
        + 12.0 * energy_h * sigma**6
        + 4.0 * a2**3 * r1_array**3 * sigma**9
        + sqrt_epsilon * a2**4 * r1_array**6 * sigma**12
    )
    return 6.0 * sqrt_epsilon * q1_array**2 - right


def resolved_k1_rhs_r1(
    r1: ArrayLike,
    state: ArrayLike,
    parameters: OuterParameters,
    *,
    energy_h: float = 0.0,
) -> FloatArray:
    """Resolved V5 ``K1`` equations with ``r1`` as independent variable."""

    r1_array = _as_float_array(r1)
    values = _as_float_array(state)
    if values.shape[0] != 2:
        raise ValueError("resolved K1 state order is (Pi,Omega)")
    pi_scaled, omega_scaled = values
    sigma = parameters.r / r1_array
    sqrt_epsilon = np.sqrt(parameters.epsilon)
    q1 = resolved_k1_energy_root(
        r1_array,
        pi_scaled,
        omega_scaled,
        parameters,
        energy_h=energy_h,
    )
    r1_speed = (
        0.5 * sqrt_epsilon * sigma**2 * pi_scaled * r1_array
    )
    if np.any(r1_speed <= 0.0):
        raise ValueError("r1 is not a forward coordinate when its speed is nonpositive")
    pi_rhs = omega_scaled - 0.5 * sqrt_epsilon * sigma**2 * pi_scaled**2
    omega_rhs = (
        (2.0 * sqrt_epsilon + parameters.epsilon * r1_array**2) * pi_scaled
        - sqrt_epsilon * q1
        - sqrt_epsilon * sigma**2 * pi_scaled * omega_scaled
    )
    return np.vstack((pi_rhs / r1_speed, omega_rhs / r1_speed))


def k1_center_graph_leading_guess(
    r1: ArrayLike, parameters: OuterParameters
) -> FloatArray:
    """The explicit leading center-graph expansion from V5(719)--(727)."""

    r1_array = _as_float_array(r1)
    sigma = parameters.r / r1_array
    sqrt_epsilon = np.sqrt(parameters.epsilon)
    x = sqrt_epsilon * r1_array**2
    q0 = np.sqrt((8.0 + 3.0 * x) / (6.0 * sqrt_epsilon))
    pi_scaled = q0 / (2.0 + x)
    if parameters.a2 != 0.0:
        pi_scaled = pi_scaled - sigma**3 * (
            parameters.a2
            * r1_array
            * (x + 3.0)
            / (3.0 * sqrt_epsilon * q0 * (2.0 + x))
        )
    omega_scaled = sigma**2 * (x + 4.0) / (3.0 * (x + 2.0) ** 3)
    return np.vstack((pi_scaled, omega_scaled))


def central_to_resolved_k1(
    central_state: ArrayLike, parameters: OuterParameters
) -> FloatArray:
    """Exact central-to-resolved-``K1`` map on the positive overlap."""

    values = _as_float_array(central_state)
    if values.shape[0] != 4:
        raise ValueError("central state order is (U,P,V,Q)")
    u, p, v, _q = values
    u2 = parameters.r * parameters.a2 - u
    if np.any(u2 <= 0.0):
        raise ValueError("central-to-K1 overlap requires u2>0")
    sigma = u2 ** (-0.5)
    r1 = parameters.r * np.sqrt(u2)
    sqrt_epsilon = np.sqrt(parameters.epsilon)
    p2 = -parameters.epsilon ** (-0.25) * p
    v2 = (
        parameters.r**2 * parameters.a2**2
        + sqrt_epsilon * parameters.r**5 * parameters.a2**3 / 3.0
        - v
    )
    pi_scaled = sigma * p2
    omega_scaled = (
        1.0 - sigma**4 * v2 + sqrt_epsilon * r1**2 / 3.0
    ) / sigma**2
    return np.vstack((pi_scaled, omega_scaled)) if values.ndim > 1 else np.array(
        [float(pi_scaled), float(omega_scaled)], dtype=np.float64
    )


def resolved_k1_to_outer_normal(
    state: ArrayLike,
    parameters: OuterParameters,
    *,
    outer_r1: float,
    energy_h: float = 0.0,
) -> FloatArray:
    """Map ``(Pi,Omega)`` at ``r1=R`` to unscaled ``(beta,alpha)``."""

    values = _as_float_array(state)
    if values.shape[0] != 2:
        raise ValueError("resolved K1 state order is (Pi,Omega)")
    pi_scaled, omega_scaled = values
    z_r, _q_r = outer_seam_coordinates(parameters, outer_r1=outer_r1)
    q1 = resolved_k1_energy_root(
        outer_r1,
        pi_scaled,
        omega_scaled,
        parameters,
        energy_h=energy_h,
    )
    chi = (
        z_r**2
        * parameters.epsilon**1.5
        * outer_r1**3
        * q1
    )
    c_sum = parameters.epsilon * outer_r1 * pi_scaled - chi
    d_difference = (
        parameters.epsilon * z_r * outer_r1**2 * omega_scaled
    )
    scaled_a = 0.5 * (c_sum + d_difference)
    scaled_b = 0.5 * (c_sum - d_difference)
    beta = parameters.delta * scaled_b
    alpha = parameters.delta * scaled_a
    return np.vstack((beta, alpha)) if values.ndim > 1 else np.array(
        [float(beta), float(alpha)], dtype=np.float64
    )


def _endpoint_clustered_grid(start: float, end: float, points: int) -> FloatArray:
    if not 0.0 < start < end:
        raise ValueError("require 0 < start < end")
    phase = np.linspace(0.0, 1.0, points)
    return start + 0.5 * (end - start) * (1.0 - np.cos(np.pi * phase))


def _positive_pi_bvp_grid(
    start: float,
    end: float,
    points: int,
    layer_width: float,
) -> FloatArray:
    """Resolve the two ``O(delta)`` end layers without roundoff-scale cells."""

    if not start < end:
        raise ValueError("require start < end")
    phase = np.linspace(0.0, 1.0, points)
    base = start + 0.5 * (end - start) * (1.0 - np.cos(np.pi * phase))
    layer = layer_width * np.logspace(-2.0, 2.0, 48)
    layer = layer[layer < end - start]
    return np.unique(np.concatenate((base, start + layer, end - layer)))


def finite_horizon_gamma_continuation(
    parameters: OuterParameters,
    beta_values: Iterable[float],
    *,
    q_start: float,
    q_end: float,
    points: int = 601,
    tolerance: float = 2.0e-8,
    max_nodes: int = 50_000,
    positive_pi: bool = False,
    energy: float = 0.0,
) -> FiniteHorizonGammaContinuation:
    """Continue the artificial finite-horizon graph over initial ``beta``.

    Every member solves the exact outer equations with
    ``beta(Q_start)=beta0`` and ``alpha(Q_end)=0``.  The previous collocation
    solution supplies the next predictor, so this is a genuine beta
    continuation rather than a collection of unrelated shooting orbits.
    The opt-in positive-``pi`` chart changes only the collocation coordinates;
    the default keeps archived replay behavior unchanged.
    """

    requested = tuple(float(value) for value in beta_values)
    if not requested:
        raise ValueError("beta_values must be nonempty")
    if any(not np.isfinite(value) for value in requested):
        raise ValueError("beta continuation values must be finite")
    mesh = (
        _positive_pi_bvp_grid(
            q_start, q_end, max(121, points // 2), parameters.delta
        )
        if positive_pi
        else _endpoint_clustered_grid(q_start, q_end, max(121, points // 2))
    )
    output_q = _endpoint_clustered_grid(q_start, q_end, points)
    previous_solution = None
    previous_beta = 0.0
    samples: list[FiniteHorizonGammaSample] = []
    for beta0 in requested:
        if previous_solution is None:
            predictor_beta = beta0 * np.exp(
                np.maximum(parameters.stable_rate_q * (mesh - q_start), -700.0)
            )
            predictor_normal = np.vstack((predictor_beta, np.zeros_like(mesh)))
        else:
            if positive_pi:
                previous_normal = positive_pi_outer_state(
                    mesh,
                    previous_solution.sol(mesh),
                    parameters,
                    energy=energy,
                )[:2]
                predictor_normal = np.vstack(previous_normal)
            else:
                predictor_normal = previous_solution.sol(mesh)
            predictor_normal[0] += (beta0 - previous_beta) * np.exp(
                np.maximum(parameters.stable_rate_q * (mesh - q_start), -700.0)
            )
        predictor = (
            normal_to_positive_pi_state(
                mesh, predictor_normal, parameters, energy=energy
            )
            if positive_pi
            else predictor_normal
        )

        def boundary(left: FloatArray, right: FloatArray) -> FloatArray:
            if not positive_pi:
                return np.array([left[0] - beta0, right[1]], dtype=np.float64)
            left_beta = positive_pi_outer_state(
                q_start, left, parameters, energy=energy
            )[0]
            right_alpha = positive_pi_outer_state(
                q_end, right, parameters, energy=energy
            )[1]
            return np.array(
                [left_beta / parameters.delta - beta0 / parameters.delta,
                 right_alpha / parameters.delta],
                dtype=np.float64,
            )

        solution = solve_bvp(
            lambda coordinate, state: (
                positive_pi_outer_rhs_q(
                    coordinate, state, parameters, energy=energy
                )
                if positive_pi
                else normal_outer_rhs_q(
                    coordinate, state, parameters, energy=energy
                )
            ),
            boundary,
            mesh,
            predictor,
            tol=tolerance,
            bc_tol=min(1.0e-10, 0.1 * tolerance),
            max_nodes=max_nodes,
            verbose=0,
        )
        if not solution.success:
            raise RuntimeError(
                f"finite-horizon beta continuation failed at {beta0}: "
                f"{solution.message}"
            )
        if positive_pi:
            beta, alpha, chi, pi, _w = positive_pi_outer_state(
                output_q, solution.sol(output_q), parameters, energy=energy
            )
        else:
            beta, alpha = solution.sol(output_q)
            chi, pi, _w = normal_outer_state(
                output_q ** (-0.5), beta, alpha, parameters, energy=energy
            )
        energy_residual = energy_equation_residual(
            output_q ** (-0.5), beta, alpha, chi, parameters, energy=energy
        )
        samples.append(
            FiniteHorizonGammaSample(
                beta0=beta0,
                compact_q=output_q,
                beta=beta,
                alpha=alpha,
                diagnostics={
                    "solver_success": bool(solution.success),
                    "solver_nodes": float(solution.x.size),
                    "solver_rms_residual_max": float(
                        np.max(solution.rms_residuals)
                    ),
                    "boundary_residual_inf": float(
                        max(abs(beta[0] - beta0), abs(alpha[-1]))
                    ),
                    "energy_residual_inf": float(
                        np.max(np.abs(energy_residual))
                    ),
                    "minimum_pi": float(np.min(pi)),
                    "outer_coordinate_chart": (
                        "eta=log(pi/delta), omega=w/delta"
                        if positive_pi
                        else "normal (beta,alpha)"
                    ),
                },
            )
        )
        previous_solution = solution
        previous_beta = beta0
    return FiniteHorizonGammaContinuation(
        q_start=float(q_start), q_end=float(q_end), samples=tuple(samples)
    )


def zero_energy_source_proxy_provider(
    parameters: OuterParameters,
    *,
    source_radius: float,
    frame: SaddleFrame | None = None,
) -> SourceStateProvider:
    """Return the legacy zero-energy linear-section source proxy."""

    selected_frame = frame or reversible_saddle_frame(
        parameters.r, parameters.a2, parameters.epsilon
    )

    def provider(phase: float) -> FloatArray:
        state, _diagnostics = zero_energy_source_state(
            frame=selected_frame,
            phase=float(phase),
            transverse_coordinate=0.0,
            radius=source_radius,
            r=parameters.r,
            a2=parameters.a2,
            epsilon=parameters.epsilon,
        )
        return np.asarray(state, dtype=np.float64)

    provider.source_model = (  # type: ignore[attr-defined]
        "zero-energy eigenplane source proxy; not the theorem true W^u circle"
    )
    provider.unique_evaluations = 0  # type: ignore[attr-defined]
    return provider


def true_wu_source_state_provider(
    parameters: OuterParameters,
    *,
    source_radius: float,
    flowback_tau: float = 2.0,
    graph_horizon: float = 8.0,
    graph_boundary_tolerance: float = 1.0e-8,
) -> SourceStateProvider:
    """Return a cached finite-horizon nonlinear-``W^u`` source provider.

    Each new phase is resolved by ``compute_v2_source_candidate``.  Exact
    repeated phase requests are cached because ``solve_bvp`` evaluates its
    boundary map repeatedly.  This remains a floating-point finite-horizon
    graph, not an interval enclosure of the theorem's source circle.
    """

    pole_parameters = PoleParameters(
        r=parameters.r, a2=parameters.a2, epsilon=parameters.epsilon
    )
    cache: dict[float, FloatArray] = {}

    def provider(phase: float) -> FloatArray:
        key = float(phase)
        if key not in cache:
            source = compute_v2_source_candidate(
                pole_parameters,
                key,
                source_radius=source_radius,
                flowback_tau=flowback_tau,
                graph_horizon=graph_horizon,
                comparison_horizon=None,
                graph_boundary_tolerance=graph_boundary_tolerance,
            )
            cache[key] = np.asarray(source.source_state, dtype=np.float64)
            provider.unique_evaluations = len(cache)  # type: ignore[attr-defined]
        return cache[key].copy()

    provider.source_model = (  # type: ignore[attr-defined]
        "finite-horizon nonlinear W^u source from vdp_source_to_pole; "
        "not interval validated"
    )
    provider.unique_evaluations = 0  # type: ignore[attr-defined]
    provider.graph_horizon = float(graph_horizon)  # type: ignore[attr-defined]
    provider.flowback_tau = float(flowback_tau)  # type: ignore[attr-defined]
    provider.graph_boundary_tolerance = float(  # type: ignore[attr-defined]
        graph_boundary_tolerance
    )
    return provider


def default_source_state_provider(
    parameters: OuterParameters,
    *,
    source_radius: float,
    flowback_tau: float = 2.0,
    graph_horizon: float = 8.0,
    graph_boundary_tolerance: float = 1.0e-8,
) -> SourceStateProvider:
    """Return the finite-horizon nonlinear-``W^u`` provider used by default."""

    return true_wu_source_state_provider(
        parameters,
        source_radius=source_radius,
        flowback_tau=flowback_tau,
        graph_horizon=graph_horizon,
        graph_boundary_tolerance=graph_boundary_tolerance,
    )


def _central_seed_orbit(
    parameters: OuterParameters,
    config: MatchedOuterConfig,
    source_state_provider: SourceStateProvider,
) -> tuple[object, float]:
    initial = source_state_provider(config.source_phase_seed)

    def section_event(_time: float, state: FloatArray) -> float:
        return float(state[0] + config.section_m)

    section_event.direction = -1.0  # type: ignore[attr-defined]
    section_event.terminal = True  # type: ignore[attr-defined]
    integration = solve_ivp(
        lambda time, state: vdp_field(
            parameters.r, parameters.a2, parameters.epsilon
        )(np.array([time]), state.reshape(4, 1))[:, 0],
        (0.0, 40.0),
        initial,
        events=section_event,
        rtol=2.0e-11,
        atol=2.0e-13,
        max_step=0.02,
        dense_output=True,
    )
    if not integration.success or not len(integration.t_events[0]):
        raise RuntimeError("source phase seed did not reach the central U=-M cut")
    return integration, float(integration.t_events[0][0])


def _k1_to_central_state(
    r1: FloatArray, state: FloatArray, parameters: OuterParameters
) -> FloatArray:
    """Blow down a resolved K1 orbit to universal central coordinates."""

    pi_scaled, omega_scaled = state
    sigma = parameters.r / r1
    sqrt_epsilon = np.sqrt(parameters.epsilon)
    q1 = resolved_k1_energy_root(r1, pi_scaled, omega_scaled, parameters)
    p2 = pi_scaled / sigma
    v1 = 1.0 + sqrt_epsilon * r1**2 / 3.0 - sigma**2 * omega_scaled
    v2 = v1 / sigma**4
    q2 = q1 / sigma**3
    u = parameters.r * parameters.a2 - sigma**-2
    p = -parameters.epsilon**0.25 * p2
    v = (
        parameters.r**2 * parameters.a2**2
        + sqrt_epsilon * parameters.r**5 * parameters.a2**3 / 3.0
        - v2
    )
    q = -parameters.epsilon**0.25 * q2
    return np.vstack((u, p, v, q))


def compute_matched_outer_candidate(
    parameters: OuterParameters = OuterParameters(r=0.08, a2=0.0, epsilon=1.0),
    config: MatchedOuterConfig = MatchedOuterConfig(),
    *,
    source_state_provider: SourceStateProvider | None = None,
    positive_pi_outer: bool = False,
) -> MatchedOuterCandidate:
    """Solve one coupled central--K1--outer finite-horizon candidate.

    ``positive_pi_outer`` is opt-in so archived calculations retain their
    original replay path.  It changes only the two outer unknowns and mesh.
    """

    z_r, q_r = outer_seam_coordinates(
        parameters, outer_r1=config.outer_r1
    )
    if not q_r < config.q_label < config.q_end:
        raise ValueError("require Q_R < Q_label < Q_end")
    u2_cut = config.section_m + parameters.r * parameters.a2
    if u2_cut <= 0.0:
        raise ValueError("M+r*a2 must be positive at the central cut")
    r1_cut = parameters.r * np.sqrt(u2_cut)
    if not r1_cut < config.outer_r1:
        raise ValueError("central K1 cut must precede the outer r1 cut")

    provider = source_state_provider or default_source_state_provider(
        parameters,
        source_radius=config.source_radius,
        flowback_tau=config.source_flowback_tau,
        graph_horizon=config.source_graph_horizon,
        graph_boundary_tolerance=config.source_graph_boundary_tolerance,
    )
    source_model = str(
        getattr(
            provider,
            "source_model",
            "injected source provider with unspecified graph construction",
        )
    )
    central_seed, central_time_seed = _central_seed_orbit(
        parameters, config, provider
    )
    mesh = (
        _positive_pi_bvp_grid(
            0.0,
            1.0,
            config.mesh_points,
            parameters.delta / (config.q_end - q_r),
        )
        if positive_pi_outer
        else np.linspace(0.0, 1.0, config.mesh_points)
    )
    central_guess = central_seed.sol(mesh * central_time_seed)
    k1_r1_mesh = r1_cut + (config.outer_r1 - r1_cut) * mesh
    k1_guess = k1_center_graph_leading_guess(k1_r1_mesh, parameters)
    leading_outer = resolved_k1_to_outer_normal(
        k1_guess[:, -1], parameters, outer_r1=config.outer_r1
    )
    leading_beta = float(leading_outer[0])
    leading_alpha = float(leading_outer[1])
    leading_gamma = finite_horizon_gamma_continuation(
        parameters,
        (0.0, leading_beta),
        q_start=q_r,
        q_end=config.q_end,
        points=max(301, config.output_points // 2),
        tolerance=min(2.0e-8, 0.1 * config.tolerance),
        max_nodes=config.max_nodes,
        positive_pi=positive_pi_outer,
    )
    leading_gamma_alpha = leading_gamma.samples[-1].gamma
    outer_seed = leading_gamma.samples[-1]
    q_mesh = q_r + (config.q_end - q_r) * mesh
    outer_normal_guess = np.vstack(
        (
            np.interp(q_mesh, outer_seed.compact_q, outer_seed.beta),
            np.interp(q_mesh, outer_seed.compact_q, outer_seed.alpha),
        )
    )
    outer_guess = (
        normal_to_positive_pi_state(q_mesh, outer_normal_guess, parameters)
        if positive_pi_outer
        else outer_normal_guess
    )
    initial_guess = np.vstack((central_guess, k1_guess, outer_guess))

    central_field = vdp_field(
        parameters.r, parameters.a2, parameters.epsilon
    )

    def field(
        normalized: FloatArray, state: FloatArray, unknown: FloatArray
    ) -> FloatArray:
        central_time = np.exp(unknown[1])
        r1 = r1_cut + (config.outer_r1 - r1_cut) * normalized
        compact_q = q_r + (config.q_end - q_r) * normalized
        return np.vstack(
            (
                central_time * central_field(normalized, state[:4]),
                (config.outer_r1 - r1_cut)
                * resolved_k1_rhs_r1(r1, state[4:6], parameters),
                (config.q_end - q_r)
                * (
                    positive_pi_outer_rhs_q(
                        compact_q, state[6:8], parameters
                    )
                    if positive_pi_outer
                    else normal_outer_rhs_q(
                        compact_q, state[6:8], parameters
                    )
                ),
            )
        )

    def boundary(
        left: FloatArray, right: FloatArray, unknown: FloatArray
    ) -> FloatArray:
        source = provider(float(unknown[0]))
        outer_left_normal = resolved_k1_to_outer_normal(
            right[4:6], parameters, outer_r1=config.outer_r1
        )
        outer_left = (
            normal_to_positive_pi_state(
                q_r, outer_left_normal, parameters
            )
            if positive_pi_outer
            else outer_left_normal
        )
        outer_right_alpha = (
            positive_pi_outer_state(
                config.q_end, right[6:8], parameters
            )[1]
            if positive_pi_outer
            else right[7]
        )
        return np.concatenate(
            (
                left[:4] - source,
                np.array([right[0] + config.section_m]),
                left[4:6] - central_to_resolved_k1(right[:4], parameters),
                left[6:8] - outer_left,
                np.array([
                    outer_right_alpha / parameters.delta
                    if positive_pi_outer
                    else outer_right_alpha
                ]),
            )
        )

    initial_unknown = np.array(
        [config.source_phase_seed, np.log(central_time_seed)], dtype=np.float64
    )
    solution = solve_bvp(
        field,
        boundary,
        mesh,
        initial_guess,
        p=initial_unknown,
        tol=config.tolerance,
        bc_tol=config.boundary_tolerance,
        max_nodes=config.max_nodes,
        verbose=0,
    )
    if not solution.success:
        raise RuntimeError(f"coupled V4/V5 BVP failed: {solution.message}")

    # The outer stable rate is O(delta^{-1}), so the physical same-Q density
    # difference contains an extremely thin layer at Q=Q_R.  A uniform output
    # grid can solve the collocation problem correctly yet badly alias the
    # subsequent V5A quadrature.  Use the same cosine clustering as the
    # independent Gamma continuation at both interfaces.
    output_phase = np.linspace(0.0, 1.0, config.output_points)
    normalized = 0.5 * (1.0 - np.cos(np.pi * output_phase))
    state = solution.sol(normalized)
    central_state = state[:4]
    k1_state = state[4:6]
    k1_r1 = r1_cut + (config.outer_r1 - r1_cut) * normalized
    compact_q = q_r + (config.q_end - q_r) * normalized
    outer_state = (
        np.vstack(
            positive_pi_outer_state(
                compact_q, state[6:8], parameters
            )[:2]
        )
        if positive_pi_outer
        else state[6:8]
    )
    source_phase = float(solution.p[0])
    central_flight_time = float(np.exp(solution.p[1]))
    boundary_residual = boundary(state[:, 0], state[:, -1], solution.p)

    seam_beta = float(outer_state[0, 0])
    seam_alpha = float(outer_state[1, 0])
    root_gamma = finite_horizon_gamma_continuation(
        parameters,
        (0.0, seam_beta),
        q_start=q_r,
        q_end=config.q_end,
        points=max(301, config.output_points // 2),
        tolerance=min(2.0e-8, 0.1 * config.tolerance),
        max_nodes=config.max_nodes,
        positive_pi=positive_pi_outer,
    )
    independent_gamma = root_gamma.samples[-1].gamma
    short_horizon = max(q_r + 20.0, 0.5 * (q_r + config.q_end))
    if short_horizon >= config.q_end:
        short_horizon = q_r + 0.75 * (config.q_end - q_r)
    short_gamma = finite_horizon_gamma_continuation(
        parameters,
        (seam_beta,),
        q_start=q_r,
        q_end=short_horizon,
        points=max(241, config.output_points // 3),
        tolerance=min(4.0e-8, 0.2 * config.tolerance),
        max_nodes=config.max_nodes,
        positive_pi=positive_pi_outer,
    ).samples[0].gamma

    label_beta = float(np.interp(config.q_label, compact_q, outer_state[0]))
    label_alpha = float(np.interp(config.q_label, compact_q, outer_state[1]))
    label_b = label_beta / parameters.delta
    delta_minus = (parameters.r / 2.0) ** 2
    b_star = delta_minus * config.scaled_beta_collar
    scaled_arrival_ok = abs(label_b) <= config.scaled_beta_collar / 8.0
    unscaled_arrival_ok = abs(label_beta) <= b_star / 2.0

    central_energy = vdp_hamiltonian(
        central_state, parameters.r, parameters.a2, parameters.epsilon
    )
    k1_as_central = _k1_to_central_state(k1_r1, k1_state, parameters)
    k1_energy = vdp_hamiltonian(
        k1_as_central, parameters.r, parameters.a2, parameters.epsilon
    )
    outer_chi, outer_pi, _outer_w = normal_outer_state(
        compact_q ** (-0.5), outer_state[0], outer_state[1], parameters
    )
    outer_energy = energy_equation_residual(
        compact_q ** (-0.5),
        outer_state[0],
        outer_state[1],
        outer_chi,
        parameters,
    )
    central_endpoint = central_state[:, -1]
    sigma_cut = parameters.r / r1_cut
    central_q1 = (
        sigma_cut**3
        * (-parameters.epsilon ** (-0.25) * central_endpoint[3])
    )
    k1_q1 = float(
        resolved_k1_energy_root(
            r1_cut, k1_state[0, 0], k1_state[1, 0], parameters
        )
    )
    diagnostics: dict[str, float | bool | str] = {
        "solver_success": bool(solution.success),
        "solver_nodes": float(solution.x.size),
        "solver_rms_residual_max": float(np.max(solution.rms_residuals)),
        "solver_rms_residual_tolerance": float(config.tolerance),
        "solver_rms_residual_passed": bool(
            np.max(solution.rms_residuals) <= config.tolerance
        ),
        "boundary_and_interface_residual_inf": float(
            np.max(np.abs(boundary_residual))
        ),
        "source_model": source_model,
        "source_provider_unique_evaluations": float(
            getattr(provider, "unique_evaluations", np.nan)
        ),
        "same_section_root_residual": float(seam_alpha - independent_gamma),
        "same_section_root_tolerance": float(
            config.same_section_root_tolerance
        ),
        "same_section_root_passed": bool(
            abs(seam_alpha - independent_gamma)
            <= config.same_section_root_tolerance
        ),
        "same_section_root_gamma": float(independent_gamma),
        "gamma_horizon_difference_at_seam": float(
            independent_gamma - short_gamma
        ),
        "gamma_short_horizon": float(short_horizon),
        "central_energy_residual_inf": float(np.max(np.abs(central_energy))),
        "k1_energy_residual_inf": float(np.max(np.abs(k1_energy))),
        "outer_energy_residual_inf": float(np.max(np.abs(outer_energy))),
        "central_k1_q1_interface_residual": float(central_q1 - k1_q1),
        "minimum_outer_pi": float(np.min(outer_pi)),
        "minimum_k1_pi_scaled": float(np.min(k1_state[0])),
        "k1_leaf_invariant_residual_inf": float(
            np.max(np.abs(k1_r1 * (parameters.r / k1_r1) - parameters.r))
        ),
        "leading_guess_beta": leading_beta,
        "leading_guess_alpha": leading_alpha,
        "leading_guess_gamma": leading_gamma_alpha,
        "k1_seam_leading_guess_residual": float(
            leading_alpha - leading_gamma_alpha
        ),
        "z_r": z_r,
        "q_r": q_r,
        "q_label": float(config.q_label),
        "q_end": float(config.q_end),
        "q_r_q_label_separated": bool(q_r < config.q_label < config.q_end),
        "seam_beta": seam_beta,
        "seam_alpha": seam_alpha,
        "source_phase_bracket_lower": float(config.source_phase_bounds[0]),
        "source_phase_bracket_upper": float(config.source_phase_bounds[1]),
        "source_phase_bracket_margin": float(
            min(
                source_phase - config.source_phase_bounds[0],
                config.source_phase_bounds[1] - source_phase,
            )
        ),
        "source_phase_in_bracket": bool(
            config.source_phase_bounds[0]
            <= source_phase
            <= config.source_phase_bounds[1]
        ),
        "seam_beta_bracket_lower": float(config.seam_beta_bracket[0]),
        "seam_beta_bracket_upper": float(config.seam_beta_bracket[1]),
        "seam_beta_bracket_margin": float(
            min(
                seam_beta - config.seam_beta_bracket[0],
                config.seam_beta_bracket[1] - seam_beta,
            )
        ),
        "seam_beta_in_bracket": bool(
            config.seam_beta_bracket[0]
            <= seam_beta
            <= config.seam_beta_bracket[1]
        ),
        "label_beta": label_beta,
        "label_alpha": label_alpha,
        "label_scaled_b": float(label_b),
        "scaled_beta_collar": float(config.scaled_beta_collar),
        "b_star": float(b_star),
        "beta_equals_delta_b_residual": float(
            label_beta - parameters.delta * label_b
        ),
        "scaled_arrival_margin_passed": bool(scaled_arrival_ok),
        "unscaled_arrival_margin_passed": bool(unscaled_arrival_ok),
        "finite_horizon_only": True,
        "outer_coordinate_chart": (
            "eta=log(pi/delta), omega=w/delta"
            if positive_pi_outer
            else "normal (beta,alpha)"
        ),
    }
    return MatchedOuterCandidate(
        parameters=parameters,
        config=config,
        source_phase=source_phase,
        central_flight_time=central_flight_time,
        normalized_grid=normalized,
        central_state=central_state,
        k1_r1=k1_r1,
        k1_state=k1_state,
        compact_q=compact_q,
        outer_state=outer_state,
        diagnostics=diagnostics,
    )


def matched_action_decomposition(
    candidate: MatchedOuterCandidate, *, terminal_q: float | None = None
) -> MatchedActionDecomposition:
    """Compute the finite V5 central--``K1``--outer observables.

    The default terminal cut is the fixed V5A normalization
    ``Q_*=candidate.config.q_label``.  In particular, this function does not
    integrate the V5 segment to the artificial finite-horizon condition at
    ``Q_end``.
    """

    parameters = candidate.parameters
    q_star = float(candidate.config.q_label if terminal_q is None else terminal_q)
    q_r = float(candidate.compact_q[0])
    q_end = float(candidate.compact_q[-1])
    if not q_r < q_star < q_end:
        raise ValueError("V5 action decomposition requires Q_R < Q_* < Q_end")

    normalized = np.asarray(candidate.normalized_grid, dtype=np.float64)
    central = np.asarray(candidate.central_state, dtype=np.float64)
    central_xi = candidate.central_flight_time * normalized
    action_scale = float(parameters.epsilon**2.25 * parameters.r**5)
    central_action_density = action_scale * (
        central[1] ** 2 - central[3] ** 2
    )
    central_action = cumulative_trapezoid(
        central_action_density, x=central_xi, initial=0.0
    )
    central_length = (
        parameters.r * parameters.epsilon ** (-0.25) * central_xi
    )

    r1 = np.asarray(candidate.k1_r1, dtype=np.float64)
    pi_scaled, omega_scaled = np.asarray(candidate.k1_state, dtype=np.float64)
    sigma = parameters.r / r1
    delta1 = sigma**2
    sqrt_epsilon = np.sqrt(parameters.epsilon)
    q1 = resolved_k1_energy_root(
        r1, pi_scaled, omega_scaled, parameters
    )
    p1 = delta1 * pi_scaled
    v1 = 1.0 + sqrt_epsilon * r1**2 / 3.0 - delta1 * omega_scaled
    omega_r1 = resolved_k1_rhs_r1(
        r1, candidate.k1_state, parameters
    )[1]
    v1_r1 = (
        2.0 * sqrt_epsilon * r1 / 3.0
        + 2.0 * delta1 * omega_scaled / r1
        - delta1 * omega_r1
    )
    k1_action_density = parameters.epsilon**2.5 * r1**4 * (
        2.0 * p1
        - 4.0 * q1 * v1 / delta1
        - r1 * q1 * v1_r1 / delta1
    )
    k1_action = cumulative_trapezoid(
        k1_action_density, x=r1, initial=0.0
    )
    k1_length_density = 2.0 / (sqrt_epsilon * pi_scaled)
    k1_length = cumulative_trapezoid(
        k1_length_density, x=r1, initial=0.0
    )

    k1_central = _k1_to_central_state(r1, candidate.k1_state, parameters)
    k1_action_central_pullback = action_scale * (
        cumulative_trapezoid(k1_central[1], x=k1_central[0], initial=0.0)
        - cumulative_trapezoid(k1_central[3], x=k1_central[2], initial=0.0)
    )

    full_q = np.asarray(candidate.compact_q, dtype=np.float64)
    lower = full_q < q_star
    outer_q = np.concatenate((full_q[lower], np.array([q_star])))
    outer_beta = np.interp(outer_q, full_q, candidate.outer_state[0])
    outer_alpha = np.interp(outer_q, full_q, candidate.outer_state[1])
    outer_length_density, outer_action_density, outer_chi, outer_pi, outer_w = (
        outer_physical_densities(
            outer_q, outer_beta, outer_alpha, parameters
        )
    )
    outer_action = cumulative_trapezoid(
        outer_action_density, x=outer_q, initial=0.0
    )
    outer_length = cumulative_trapezoid(
        outer_length_density, x=outer_q, initial=0.0
    )

    # Independent pullback checks use spline derivatives of the saved state,
    # rather than the densities just integrated above.
    central_u_s = CubicSpline(normalized, central[0]).derivative()(normalized)
    central_v_s = CubicSpline(normalized, central[2]).derivative()(normalized)
    central_pullback_density = action_scale * (
        central[1] * central_u_s - central[3] * central_v_s
    )
    k1_u_r = CubicSpline(r1, k1_central[0]).derivative()(r1)
    k1_v_r = CubicSpline(r1, k1_central[2]).derivative()(r1)
    k1_pullback_density = action_scale * (
        k1_central[1] * k1_u_r - k1_central[3] * k1_v_r
    )
    outer_z = outer_q ** (-0.5)
    outer_u = 1.0 / outer_z
    outer_v = cubic_f(outer_u) - outer_w / outer_z
    outer_q_physical = outer_chi / outer_z**2
    outer_physical_density = (
        parameters.epsilon
        * outer_pi
        * CubicSpline(outer_q, outer_u).derivative()(outer_q)
        - parameters.delta**-1
        * outer_q_physical
        * CubicSpline(outer_q, outer_v).derivative()(outer_q)
    )

    def scaled_density_defect(first: FloatArray, second: FloatArray) -> float:
        scale = max(float(np.max(np.abs(first))), float(np.max(np.abs(second))))
        return float(np.max(np.abs(first - second)) / max(scale, np.finfo(float).tiny))

    bridge = BridgeParameters(
        r=parameters.r, a2=parameters.a2, epsilon=parameters.epsilon
    )
    central_k1_interface = float(
        np.max(
            np.abs(
                central_to_physical(central[:, -1], bridge)
                - central_to_physical(k1_central[:, 0], bridge)
            )
        )
    )
    k1_physical_end = central_to_physical(k1_central[:, -1], bridge)
    outer_physical_start = np.array(
        [
            outer_u[0],
            outer_pi[0],
            outer_v[0],
            outer_q_physical[0],
        ],
        dtype=np.float64,
    )
    k1_outer_interface = float(
        np.max(np.abs(k1_physical_end - outer_physical_start))
    )

    diagnostics: dict[str, float | bool | str] = {
        "q_r": q_r,
        "q_star": q_star,
        "q_end_not_integrated_by_v5": q_end,
        "central_density_pullback_relative_defect": scaled_density_defect(
            candidate.central_flight_time * central_action_density,
            central_pullback_density,
        ),
        "k1_density_pullback_relative_defect": scaled_density_defect(
            k1_action_density, k1_pullback_density
        ),
        "outer_density_physical_relative_defect": scaled_density_defect(
            outer_action_density, outer_physical_density
        ),
        "k1_action_direct_vs_central_pullback_absolute_defect": float(
            k1_action[-1] - k1_action_central_pullback[-1]
        ),
        "k1_action_direct_vs_central_pullback_relative_defect": float(
            abs(k1_action[-1] - k1_action_central_pullback[-1])
            / max(abs(float(k1_action[-1])), np.finfo(float).tiny)
        ),
        "central_k1_physical_interface_defect_inf": central_k1_interface,
        "k1_outer_physical_interface_defect_inf": k1_outer_interface,
        "terminal_is_fixed_v5a_normalization_cut": bool(
            abs(q_star - candidate.config.q_label) <= 1.0e-12
        ),
        "finite_horizon_only": True,
    }
    return MatchedActionDecomposition(
        central_xi=np.asarray(central_xi),
        central_action=np.asarray(central_action),
        central_length=np.asarray(central_length),
        k1_r1=r1,
        k1_action=np.asarray(k1_action),
        k1_action_central_pullback=np.asarray(k1_action_central_pullback),
        k1_length=np.asarray(k1_length),
        outer_q=np.asarray(outer_q),
        outer_action=np.asarray(outer_action),
        outer_length=np.asarray(outer_length),
        diagnostics=diagnostics,
    )


def matched_outer_refinement(
    q_end_values: Iterable[float],
    parameters: OuterParameters = OuterParameters(r=0.08, a2=0.0, epsilon=1.0),
    config: MatchedOuterConfig = MatchedOuterConfig(),
    *,
    source_state_provider: SourceStateProvider | None = None,
) -> MatchedOuterRefinement:
    """Re-solve the full coupled problem on an outer-horizon ladder."""

    horizons = tuple(float(value) for value in q_end_values)
    if not horizons:
        raise ValueError("q_end_values must be nonempty")
    if any(value <= config.q_label for value in horizons):
        raise ValueError("every refinement horizon must exceed Q_label")
    selected_provider = source_state_provider or default_source_state_provider(
        parameters,
        source_radius=config.source_radius,
        flowback_tau=config.source_flowback_tau,
        graph_horizon=config.source_graph_horizon,
        graph_boundary_tolerance=config.source_graph_boundary_tolerance,
    )
    candidates = tuple(
        compute_matched_outer_candidate(
            parameters,
            replace(config, q_end=value),
            source_state_provider=selected_provider,
        )
        for value in horizons
    )
    differences = np.full(len(candidates), np.nan, dtype=np.float64)
    for index in range(1, len(candidates)):
        previous = candidates[index - 1]
        current = candidates[index]
        # Compare on the fixed physical observation interval, not at the
        # shorter member's artificial terminal boundary.  Including that
        # terminal layer would measure the deliberately changed condition
        # alpha(Q_end)=0 rather than convergence of the matched candidate.
        common_q_end = min(
            previous.config.q_label,
            current.config.q_label,
            previous.config.q_end,
            current.config.q_end,
        )
        common_q = np.linspace(
            max(previous.diagnostics["q_r"], current.diagnostics["q_r"]),
            common_q_end,
            301,
        )
        previous_state = np.vstack(
            (
                np.interp(common_q, previous.compact_q, previous.outer_state[0]),
                np.interp(common_q, previous.compact_q, previous.outer_state[1]),
            )
        )
        current_state = np.vstack(
            (
                np.interp(common_q, current.compact_q, current.outer_state[0]),
                np.interp(common_q, current.compact_q, current.outer_state[1]),
            )
        )
        differences[index] = float(np.max(np.abs(current_state - previous_state)))
    return MatchedOuterRefinement(
        q_end=np.asarray(horizons, dtype=np.float64),
        source_phase=np.asarray(
            [candidate.source_phase for candidate in candidates], dtype=np.float64
        ),
        central_flight_time=np.asarray(
            [candidate.central_flight_time for candidate in candidates],
            dtype=np.float64,
        ),
        seam_beta=np.asarray(
            [candidate.seam_beta for candidate in candidates], dtype=np.float64
        ),
        seam_alpha=np.asarray(
            [candidate.seam_alpha for candidate in candidates], dtype=np.float64
        ),
        label_beta=np.asarray(
            [float(candidate.diagnostics["label_beta"]) for candidate in candidates],
            dtype=np.float64,
        ),
        consecutive_state_difference=differences,
        candidates=candidates,
    )


__all__ = [
    "COMPUTED_E1_MATCHED_CANDIDATE",
    "NOT_INTERVAL_VALIDATED",
    "FiniteHorizonGammaContinuation",
    "FiniteHorizonGammaSample",
    "MatchedActionDecomposition",
    "MatchedOuterCandidate",
    "MatchedOuterConfig",
    "MatchedOuterRefinement",
    "SourceStateProvider",
    "central_to_resolved_k1",
    "compute_matched_outer_candidate",
    "default_source_state_provider",
    "finite_horizon_gamma_continuation",
    "k1_center_graph_leading_guess",
    "matched_action_decomposition",
    "matched_outer_refinement",
    "outer_seam_coordinates",
    "resolved_k1_energy_root",
    "resolved_k1_energy_equation_residual",
    "resolved_k1_rhs_r1",
    "resolved_k1_to_outer_normal",
    "true_wu_source_state_provider",
    "zero_energy_source_proxy_provider",
]
