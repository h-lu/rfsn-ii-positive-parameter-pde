"""Floating-point probes for the positive-parameter van der Pol outer end.

This module implements only formulas that are explicit in the analytic notes:

* V4 equations (14), (17), and (19) for the exact outer compactification;
* V5 equations (16)--(22), (51), and (58) for exact chart crosswalks and
  algebraic matching proxies; and
* V5A equations (9)--(14), (38)--(47) for the physical length/action weights
  and their composition laws.

The V4 future-staying graph ``alpha = Gamma(z, E, beta)`` and the full V5
K2--K1 matching tube are theorem-constructed objects, not closed formulas.
Accordingly, :func:`finite_horizon_outer_tail` computes an explicitly labelled
finite-horizon graph proxy: it solves the exact zero-energy outer equations with
``beta(Q_start)=beta0`` and the artificial terminal condition
``alpha(Q_end)=0``.  It must not be presented as a numerical proof of V4 or V5.

All routines are deterministic and side-effect free.  The evidence level is
ordinary floating-point ``COMPUTED/E1``; it is not task #7 interval validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import cumulative_trapezoid, solve_bvp, trapezoid


FloatArray = NDArray[np.float64]

COMPUTED_E1 = "COMPUTED/E1_FINITE_HORIZON_GRAPH_PROXY"
NOT_NUMERICALLY_RESOLVED = "NOT_NUMERICALLY_RESOLVED"


@dataclass(frozen=True)
class OuterParameters:
    """Positive parameters and the exact derived V4/V5A quantities."""

    r: float
    a2: float = 0.0
    epsilon: float = 1.0

    def __post_init__(self) -> None:
        if not np.isfinite(self.r) or self.r <= 0.0:
            raise ValueError("r must be finite and positive")
        if not np.isfinite(self.epsilon) or self.epsilon <= 0.0:
            raise ValueError("epsilon must be finite and positive")
        if not np.isfinite(self.a2):
            raise ValueError("a2 must be finite")

    @property
    def delta(self) -> float:
        return self.r * self.r

    @property
    def a(self) -> float:
        return 1.0 + np.sqrt(self.epsilon) * self.r**3 * self.a2

    @property
    def q_star(self) -> float:
        return float(np.sqrt(self.epsilon / 2.0))

    @property
    def stable_rate_q(self) -> float:
        """V5A boundary rate ell_infinity in the Q=z^{-2} coordinate."""

        return -1.0 / (2.0 * self.delta * self.q_star)


@dataclass(frozen=True)
class FiniteHorizonOuterTail:
    """One exact zero-energy outer orbit on a finite Q interval.

    The orbit equations and energy relation are exact.  The approximation is
    solely the terminal graph condition ``alpha(Q_end)=0`` at finite Q_end.
    """

    parameters: OuterParameters
    beta0: float
    compact_q: FloatArray
    z: FloatArray
    beta: FloatArray
    alpha: FloatArray
    chi: FloatArray
    pi: FloatArray
    w: FloatArray
    length_density: FloatArray
    action_density: FloatArray
    diagnostics: Mapping[str, float | str | bool]
    evidence_status: str = COMPUTED_E1


@dataclass(frozen=True)
class OuterTailPair:
    """V5A reference tail (beta0=0) and a neighboring same-Q tail."""

    reference: FiniteHorizonOuterTail
    neighboring: FiniteHorizonOuterTail

    def __post_init__(self) -> None:
        if self.reference.parameters != self.neighboring.parameters:
            raise ValueError("reference and neighboring tails need common parameters")
        if not np.array_equal(self.reference.compact_q, self.neighboring.compact_q):
            raise ValueError("reference and neighboring tails need a common Q grid")
        if self.reference.beta0 != 0.0:
            raise ValueError("the V5A reference normalization requires beta0=0")


@dataclass(frozen=True)
class FinitePartArrays:
    """V5A cutoff integrals evaluated on a common finite Q grid."""

    compact_q: FloatArray
    counterterm_length: FloatArray
    counterterm_action: FloatArray
    neighboring_raw_length: FloatArray
    neighboring_raw_action: FloatArray
    reference_subtracted_length: FloatArray
    reference_subtracted_action: FloatArray


def _as_float_array(value: ArrayLike) -> FloatArray:
    return np.asarray(value, dtype=np.float64)


def shifted_energy_polynomial(a: float) -> float:
    """Return F(a)=a^4/12-a^2/2 from V4 equation (18)."""

    return a**4 / 12.0 - 0.5 * a * a


def positive_energy_root(
    z: ArrayLike,
    beta: ArrayLike,
    alpha: ArrayLike,
    parameters: OuterParameters,
    *,
    energy: float = 0.0,
) -> FloatArray:
    """Solve the exact V4 energy equation (19) for its positive chi root.

    ``pi = delta*chi + alpha + beta`` makes (19) a scalar quadratic in chi.
    No asymptotic truncation is used here.
    """

    z_array, beta_array, alpha_array = np.broadcast_arrays(
        _as_float_array(z), _as_float_array(beta), _as_float_array(alpha)
    )
    delta = parameters.delta
    epsilon = parameters.epsilon
    a = parameters.a
    stable_sum = alpha_array + beta_array
    w = alpha_array - beta_array
    z2 = z_array * z_array
    z3 = z2 * z_array
    z4 = z2 * z2

    coefficient_2 = 1.0 - epsilon * delta * delta * z4
    coefficient_1 = -2.0 * epsilon * delta * stable_sum * z4
    constant = -(
        epsilon / 2.0
        - 2.0 * a * epsilon * z_array / 3.0
        - epsilon * (2.0 * w + 1.0) * z2
        + 2.0 * a * epsilon * (w + 1.0) * z3
        + (
            epsilon * stable_sum * stable_sum
            + 2.0 * energy
            + 2.0 * epsilon * shifted_energy_polynomial(a)
        )
        * z4
    )
    discriminant = coefficient_1 * coefficient_1 - 4.0 * coefficient_2 * constant
    if np.any(coefficient_2 <= 0.0):
        raise ValueError("the requested state lies outside the regular positive-root chart")
    if np.any(discriminant <= 0.0):
        raise ValueError("the V4 energy equation has no regular positive root")
    return (-coefficient_1 + np.sqrt(discriminant)) / (2.0 * coefficient_2)


def energy_equation_residual(
    z: ArrayLike,
    beta: ArrayLike,
    alpha: ArrayLike,
    chi: ArrayLike,
    parameters: OuterParameters,
    *,
    energy: float = 0.0,
) -> FloatArray:
    """Residual of V4 equation (19), left side minus right side."""

    z_array, beta_array, alpha_array, chi_array = np.broadcast_arrays(
        _as_float_array(z),
        _as_float_array(beta),
        _as_float_array(alpha),
        _as_float_array(chi),
    )
    delta = parameters.delta
    epsilon = parameters.epsilon
    a = parameters.a
    pi = delta * chi_array + alpha_array + beta_array
    w = alpha_array - beta_array
    right = (
        epsilon / 2.0
        - 2.0 * a * epsilon * z_array / 3.0
        - epsilon * (2.0 * w + 1.0) * z_array**2
        + 2.0 * a * epsilon * (w + 1.0) * z_array**3
        + (
            epsilon * pi * pi
            + 2.0 * energy
            + 2.0 * epsilon * shifted_energy_polynomial(a)
        )
        * z_array**4
    )
    return chi_array * chi_array - right


def compactified_outer_rhs_tau(
    state: ArrayLike, parameters: OuterParameters
) -> FloatArray:
    """Exact V4 outer field (14) in state order (z, pi, w, chi)."""

    values = _as_float_array(state)
    if values.shape[0] != 4:
        raise ValueError("state must have leading dimension four")
    z, pi, w, chi = values
    delta = parameters.delta
    epsilon = parameters.epsilon
    a = parameters.a
    return np.asarray(
        [
            -pi * z**3,
            w,
            (1.0 - z * z) * pi - delta * chi - pi * w * z * z,
            z * z * (epsilon * delta * (1.0 - a * z) - 2.0 * pi * chi),
        ],
        dtype=np.float64,
    )


def normal_outer_state(
    z: ArrayLike,
    beta: ArrayLike,
    alpha: ArrayLike,
    parameters: OuterParameters,
    *,
    energy: float = 0.0,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Return (chi, pi, w) using exact V4 equations (16) and (19)."""

    beta_array, alpha_array = np.broadcast_arrays(
        _as_float_array(beta), _as_float_array(alpha)
    )
    chi = positive_energy_root(
        z, beta_array, alpha_array, parameters, energy=energy
    )
    pi = parameters.delta * chi + alpha_array + beta_array
    w = alpha_array - beta_array
    return chi, pi, w


def normal_outer_rhs_q(
    compact_q: ArrayLike,
    state: ArrayLike,
    parameters: OuterParameters,
    *,
    energy: float = 0.0,
) -> FloatArray:
    """Exact V5A reduced orbit equations in Q=z^{-2}.

    The state order is ``(beta, alpha)``.  Both components are obtained from
    V4 equation (17) divided by the exact clock ``dQ/dtau=2*pi``.
    The restriction to a finite-horizon graph proxy is imposed only through
    boundary conditions in :func:`finite_horizon_outer_tail`.
    """

    compact_q_array = _as_float_array(compact_q)
    if np.any(compact_q_array <= 0.0):
        raise ValueError("Q must be positive")
    values = _as_float_array(state)
    if values.shape[0] != 2:
        raise ValueError("state must have leading dimension two: (beta, alpha)")
    beta, alpha = values
    z = compact_q_array ** (-0.5)
    chi, pi, w = normal_outer_state(
        z, beta, alpha, parameters, energy=energy
    )
    if np.any(pi <= 0.0):
        raise ValueError("Q is not a forward coordinate when pi is nonpositive")
    delta = parameters.delta
    epsilon = parameters.epsilon
    a = parameters.a
    common = -delta * delta * epsilon * (1.0 - a * z) + 2.0 * delta * chi * pi
    beta_dot = -beta + 0.5 * z * z * (common + pi + pi * w)
    alpha_dot = alpha + 0.5 * z * z * (common - pi - pi * w)
    return np.vstack((beta_dot / (2.0 * pi), alpha_dot / (2.0 * pi)))


def outer_physical_densities(
    compact_q: ArrayLike,
    beta: ArrayLike,
    alpha: ArrayLike,
    parameters: OuterParameters,
) -> tuple[FloatArray, FloatArray, FloatArray, FloatArray, FloatArray]:
    """Return exact V5A (T, A, chi, pi, w) densities from equations (9)--(10)."""

    compact_q_array = _as_float_array(compact_q)
    z = compact_q_array ** (-0.5)
    chi, pi, w = normal_outer_state(z, beta, alpha, parameters, energy=0.0)
    if np.any(pi <= 0.0):
        raise ValueError("the V5A common coordinate requires pi>0")
    length_density = (
        parameters.delta / (2.0 * pi) * compact_q_array ** (-0.5)
    )
    action_density = (
        -(chi * chi) / (2.0 * pi) * compact_q_array ** 1.5
        + parameters.epsilon * pi / 2.0 * compact_q_array ** (-0.5)
    )
    return length_density, action_density, chi, pi, w


def _endpoint_clustered_grid(start: float, end: float, points: int) -> FloatArray:
    if not (0.0 < start < end):
        raise ValueError("require 0 < Q_start < Q_end")
    if points < 41:
        raise ValueError("points must be at least 41")
    phase = np.linspace(0.0, 1.0, points)
    return start + 0.5 * (end - start) * (1.0 - np.cos(np.pi * phase))


def finite_horizon_outer_tail(
    parameters: OuterParameters,
    beta0: float,
    *,
    q_start: float = 25.0,
    q_end: float = 65.0,
    points: int = 801,
    tolerance: float = 2.0e-7,
    max_nodes: int = 50_000,
) -> FiniteHorizonOuterTail:
    """Compute a finite-horizon proxy for one zero-energy V4 graph orbit.

    The exact equations are solved with the V5A initial label
    ``beta(Q_start)=beta0``.  Because the theorem-constructed graph Gamma is
    not an explicit formula, ``alpha(Q_end)=0`` is used as a transparent
    finite-horizon terminal condition.  Convergence in ``q_end`` must be
    checked before using the result as explanatory evidence.
    """

    if not np.isfinite(beta0):
        raise ValueError("beta0 must be finite")
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    mesh = _endpoint_clustered_grid(q_start, q_end, max(121, points // 2))
    rate = parameters.stable_rate_q
    beta_guess = beta0 * np.exp(np.maximum(rate * (mesh - q_start), -700.0))
    alpha_guess = np.zeros_like(mesh)
    guess = np.vstack((beta_guess, alpha_guess))

    def boundary(left: FloatArray, right: FloatArray) -> FloatArray:
        return np.array([left[0] - beta0, right[1]], dtype=np.float64)

    solution = solve_bvp(
        lambda coordinate, state: normal_outer_rhs_q(
            coordinate, state, parameters
        ),
        boundary,
        mesh,
        guess,
        tol=tolerance,
        bc_tol=min(1.0e-9, 0.1 * tolerance),
        max_nodes=max_nodes,
        verbose=0,
    )
    if not solution.success:
        raise RuntimeError(f"outer finite-horizon BVP failed: {solution.message}")

    compact_q = _endpoint_clustered_grid(q_start, q_end, points)
    beta, alpha = solution.sol(compact_q)
    z = compact_q ** (-0.5)
    length_density, action_density, chi, pi, w = outer_physical_densities(
        compact_q, beta, alpha, parameters
    )
    energy_residual = energy_equation_residual(
        z, beta, alpha, chi, parameters, energy=0.0
    )
    diagnostics: dict[str, float | str | bool] = {
        "solver_success": bool(solution.success),
        "solver_nodes": float(solution.x.size),
        "solver_rms_residual_max": float(np.max(solution.rms_residuals)),
        "boundary_residual_inf": float(max(abs(beta[0] - beta0), abs(alpha[-1]))),
        "energy_residual_inf": float(np.max(np.abs(energy_residual))),
        "minimum_pi": float(np.min(pi)),
        "terminal_condition": "alpha(Q_end)=0 finite-horizon proxy",
        "matching_status": NOT_NUMERICALLY_RESOLVED,
    }
    return FiniteHorizonOuterTail(
        parameters=parameters,
        beta0=float(beta0),
        compact_q=compact_q,
        z=z,
        beta=beta,
        alpha=alpha,
        chi=chi,
        pi=pi,
        w=w,
        length_density=length_density,
        action_density=action_density,
        diagnostics=diagnostics,
    )


def finite_horizon_tail_pair(
    parameters: OuterParameters,
    neighboring_beta0: float,
    **solver_options: float | int,
) -> OuterTailPair:
    """Compute the V5A reference normalization and one neighboring same-Q tail."""

    if neighboring_beta0 == 0.0:
        raise ValueError("neighboring_beta0 must be nonzero")
    reference = finite_horizon_outer_tail(parameters, 0.0, **solver_options)
    neighboring = finite_horizon_outer_tail(
        parameters, neighboring_beta0, **solver_options
    )
    return OuterTailPair(reference=reference, neighboring=neighboring)


def reference_subtracted_integrals(pair: OuterTailPair) -> FinitePartArrays:
    """Evaluate the exact V5A cutoff definitions (11) and (13)."""

    q = pair.reference.compact_q
    reference = pair.reference
    neighboring = pair.neighboring
    counterterm_length = cumulative_trapezoid(
        reference.length_density, q, initial=0.0
    )
    counterterm_action = cumulative_trapezoid(
        reference.action_density, q, initial=0.0
    )
    neighboring_raw_length = cumulative_trapezoid(
        neighboring.length_density, q, initial=0.0
    )
    neighboring_raw_action = cumulative_trapezoid(
        neighboring.action_density, q, initial=0.0
    )
    # Integrate the density differences directly.  Subtracting the two raw
    # cumulative integrals loses many digits because the V5A counterterms are
    # algebraically large while the relative finite parts are small.  The raw
    # arrays are retained for plotting the divergence, but they are not used
    # to form the numerically stable candidate-level relative quantities.
    relative_length = cumulative_trapezoid(
        neighboring.length_density - reference.length_density, q, initial=0.0
    )
    relative_action = cumulative_trapezoid(
        neighboring.action_density - reference.action_density, q, initial=0.0
    )
    return FinitePartArrays(
        compact_q=q,
        counterterm_length=counterterm_length,
        counterterm_action=counterterm_action,
        neighboring_raw_length=neighboring_raw_length,
        neighboring_raw_action=neighboring_raw_action,
        reference_subtracted_length=relative_length,
        reference_subtracted_action=relative_action,
    )


def leading_counterterm_differences(
    compact_q: ArrayLike, parameters: OuterParameters, *, q_start: float
) -> tuple[FloatArray, FloatArray]:
    """Leading V5A equation (14) terms with their Q_start constants removed."""

    q = _as_float_array(compact_q)
    if np.any(q < q_start):
        raise ValueError("all cutoffs must be at or after q_start")
    leading_length = (np.sqrt(q) - np.sqrt(q_start)) / parameters.q_star
    leading_action = -parameters.q_star / (5.0 * parameters.delta) * (
        q**2.5 - q_start**2.5
    )
    return leading_length, leading_action


def outer_asymptotic_diagnostics(
    pair: OuterTailPair, *, tail_fraction: float = 0.1
) -> dict[str, float | str | bool]:
    """Summarize V4/V5A asymptotics without upgrading the evidence status."""

    if not (0.0 < tail_fraction < 1.0):
        raise ValueError("tail_fraction must lie in (0,1)")
    reference = pair.reference
    neighboring = pair.neighboring
    parameters = reference.parameters
    arrays = reference_subtracted_integrals(pair)
    q = reference.compact_q
    endpoint = -1
    tail_index = max(1, int((1.0 - tail_fraction) * (q.size - 1)))
    u = np.sqrt(q)
    f_u = u**3 / 3.0 - u
    physical_q = reference.chi * q
    physical_v = f_u - reference.w * u
    u_x = reference.pi / parameters.delta
    return {
        "evidence_status": COMPUTED_E1,
        "matching_status": NOT_NUMERICALLY_RESOLVED,
        "q_end": float(q[endpoint]),
        "minimum_pi": float(min(np.min(reference.pi), np.min(neighboring.pi))),
        "reference_energy_residual_inf": float(
            reference.diagnostics["energy_residual_inf"]
        ),
        "neighbor_energy_residual_inf": float(
            neighboring.diagnostics["energy_residual_inf"]
        ),
        "length_counterterm_at_q_end": float(arrays.counterterm_length[endpoint]),
        "action_counterterm_at_q_end": float(arrays.counterterm_action[endpoint]),
        "length_density_scaled": float(
            reference.length_density[endpoint] * np.sqrt(q[endpoint])
        ),
        "length_density_scaled_limit": 1.0 / (2.0 * parameters.q_star),
        "action_density_scaled": float(
            reference.action_density[endpoint] / q[endpoint] ** 1.5
        ),
        "action_density_scaled_limit": -parameters.q_star
        / (2.0 * parameters.delta),
        "u_x_minus_q_star": float(u_x[endpoint] - parameters.q_star),
        "q_over_u_squared_minus_q_star": float(
            physical_q[endpoint] / u[endpoint] ** 2 - parameters.q_star
        ),
        "u_times_v_minus_f": float(
            u[endpoint] * (physical_v[endpoint] - f_u[endpoint])
        ),
        "u_times_p_minus_delta_q_star": float(
            u[endpoint]
            * (reference.pi[endpoint] - parameters.delta * parameters.q_star)
        ),
        "same_q_beta_gap_initial": float(
            neighboring.beta[0] - reference.beta[0]
        ),
        "same_q_beta_gap_terminal": float(
            neighboring.beta[endpoint] - reference.beta[endpoint]
        ),
        "renormalized_length_at_q_end": float(
            arrays.reference_subtracted_length[endpoint]
        ),
        "renormalized_action_at_q_end": float(
            arrays.reference_subtracted_action[endpoint]
        ),
        "renormalized_length_tail_change": float(
            arrays.reference_subtracted_length[endpoint]
            - arrays.reference_subtracted_length[tail_index]
        ),
        "renormalized_action_tail_change": float(
            arrays.reference_subtracted_action[endpoint]
            - arrays.reference_subtracted_action[tail_index]
        ),
        "physical_distance_increases": bool(
            np.all(np.diff(arrays.counterterm_length) > 0.0)
            and arrays.counterterm_length[endpoint] > 0.0
        ),
        "counterterm_action_diverges_negative": bool(
            arrays.counterterm_action[endpoint] < arrays.counterterm_action[tail_index]
        ),
    }


def numerical_cut_balance(
    compact_q: ArrayLike,
    density: ArrayLike,
    cut_index: int,
) -> float:
    """Residual of V4/V5A finite-cut additivity at one interior cut."""

    q = _as_float_array(compact_q)
    values = _as_float_array(density)
    if q.ndim != 1 or values.shape != q.shape:
        raise ValueError("compact_q and density must be one-dimensional peers")
    if not 0 < cut_index < q.size - 1:
        raise ValueError("cut_index must be interior")
    whole = trapezoid(values, q)
    prefix = trapezoid(values[: cut_index + 1], q[: cut_index + 1])
    suffix = trapezoid(values[cut_index:], q[cut_index:])
    return float(whole - prefix - suffix)


def reference_change_balance(
    compact_q: ArrayLike,
    actual_density: ArrayLike,
    reference0_density: ArrayLike,
    reference1_density: ArrayLike,
) -> float:
    """Residual of changing the V5A reference on one common physical Q grid.

    The identity is
    ``int(actual-ref0) = int(actual-ref1) + int(ref1-ref0)``.
    It is a finite-cut algebraic check, not a proof of the improper limits.
    """

    q = _as_float_array(compact_q)
    actual = _as_float_array(actual_density)
    reference0 = _as_float_array(reference0_density)
    reference1 = _as_float_array(reference1_density)
    if not (actual.shape == reference0.shape == reference1.shape == q.shape):
        raise ValueError("all densities must share the one-dimensional Q grid")
    normalized0 = trapezoid(actual - reference0, q)
    normalized1 = trapezoid(actual - reference1, q)
    reference_transfer = trapezoid(reference1 - reference0, q)
    return float(normalized0 - normalized1 - reference_transfer)


def gauge_composition_balance(
    first_action: float,
    second_action: float,
    psi_initial: float,
    psi_join: float,
    psi_terminal: float,
) -> float:
    """Endpoint-coboundary residual for V5A equations (42) and (45)."""

    transformed_whole = (
        first_action
        + second_action
        + psi_terminal
        - psi_initial
    )
    transformed_parts = (
        first_action
        + psi_join
        - psi_initial
        + second_action
        + psi_terminal
        - psi_join
    )
    return float(transformed_whole - transformed_parts)


def terminal_potential_transfer(
    old_potential: float,
    slide_integral_or_time: float,
    end_transfer_constant: float,
) -> float:
    """V5A equation (47): new terminal potential after a section slide."""

    return float(old_potential - slide_integral_or_time + end_transfer_constant)


def central_section_to_k1(
    parameters: OuterParameters,
    *,
    section_m: float,
    p2: float,
    v2: float,
    q2: float,
) -> dict[str, float]:
    """Exact V5 central-section embedding, equations (16)--(17)."""

    denominator = section_m + parameters.r * parameters.a2
    if denominator <= 0.0:
        raise ValueError("M+r*a2 must be positive on the selected section")
    sigma = denominator ** (-0.5)
    r1 = parameters.r * np.sqrt(denominator)
    return {
        "sigma": float(sigma),
        "r1": float(r1),
        "delta1": float(sigma * sigma),
        "a1": float(sigma**3 * parameters.a2),
        "p1": float(sigma**3 * p2),
        "v1": float(sigma**4 * v2),
        "q1": float(sigma**3 * q2),
    }


def k1_to_outer(
    *,
    r1: float,
    delta1: float,
    p1: float,
    v1: float,
    q1: float,
    epsilon: float,
) -> dict[str, float]:
    """Exact V5 K1-to-outer crosswalk, equation (21)."""

    if r1 <= 0.0 or delta1 <= 0.0 or epsilon <= 0.0:
        raise ValueError("r1, delta1, and epsilon must be positive")
    sqrt_epsilon = np.sqrt(epsilon)
    z = 1.0 / (1.0 + sqrt_epsilon * r1 * r1)
    pi = epsilon * r1**3 * p1
    w = z * epsilon * r1**4 * (
        1.0 - v1 + sqrt_epsilon * r1 * r1 / 3.0
    )
    chi = z * z * epsilon**1.5 * r1**3 * q1
    h = epsilon * r1**3 * (
        p1 - sqrt_epsilon * r1 * r1 * delta1 * z * z * q1
    )
    alpha = 0.5 * (h + w)
    beta = 0.5 * (h - w)
    physical_delta = r1 * r1 * delta1
    return {
        "z": float(z),
        "pi": float(pi),
        "w": float(w),
        "chi": float(chi),
        "h": float(h),
        "alpha": float(alpha),
        "beta": float(beta),
        "physical_delta": float(physical_delta),
        "h_identity_residual": float(h - (pi - physical_delta * chi)),
    }


def frozen_exchange_pairing(b2b3: float = 6.0 * np.sqrt(3.0)) -> float:
    """The computable frozen Jost formula 24*B2*B3 from V5 equation (51)."""

    return float(24.0 * b2b3)


def matching_determinant_proxy(
    section_speed: float, source_phase_incidence: float
) -> float:
    """Algebraic factorization det(D M)=s*chi from V5 equation (58).

    The caller supplies both factors.  This routine does not compute the V5
    target row, source circle, or matching connection.
    """

    return float(section_speed * source_phase_incidence)


def v5_matching_status(parameters: OuterParameters) -> dict[str, float | str | None]:
    """Report the honest numerical status of the non-explicit V5 construction."""

    return {
        "status": NOT_NUMERICALLY_RESOLVED,
        "reason": (
            "the theorem-constructed K2-K1 graph tube, endpoint-anchored row, "
            "and source-phase incidence are not explicit numerical inputs"
        ),
        "frozen_exchange_pairing": frozen_exchange_pairing(),
        "positive_parameter_formula": "144*sqrt(3) + O(r)",
        "analytic_lower_bound_after_theorem_shrink": float(72.0 * np.sqrt(3.0)),
        "r": float(parameters.r),
        "computed_positive_parameter_exchange": None,
        "computed_matching_determinant": None,
    }


__all__ = [
    "COMPUTED_E1",
    "NOT_NUMERICALLY_RESOLVED",
    "FiniteHorizonOuterTail",
    "FinitePartArrays",
    "OuterParameters",
    "OuterTailPair",
    "central_section_to_k1",
    "compactified_outer_rhs_tau",
    "energy_equation_residual",
    "finite_horizon_outer_tail",
    "finite_horizon_tail_pair",
    "frozen_exchange_pairing",
    "gauge_composition_balance",
    "k1_to_outer",
    "leading_counterterm_differences",
    "matching_determinant_proxy",
    "normal_outer_rhs_q",
    "normal_outer_state",
    "numerical_cut_balance",
    "outer_asymptotic_diagnostics",
    "outer_physical_densities",
    "positive_energy_root",
    "reference_change_balance",
    "reference_subtracted_integrals",
    "shifted_energy_polynomial",
    "terminal_potential_transfer",
    "v5_matching_status",
]
