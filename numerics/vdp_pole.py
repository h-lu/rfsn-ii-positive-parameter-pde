"""Local numerical realization of the positive-parameter van der Pol pole.

This module implements the *physical* stationary equations, exact
regular-singular compactification, normalized polyhomogeneous jet, and
Laurent--log action subtraction from
``van-der-pol/POSITIVE_POLE_FINITE_PART.md`` (Theorem V3, equations
(3)--(8), (25)--(28), (33)--(39), and (45)--(50)).

The theorem's source circle and the constants defining its positive parameter
box are existential rather than numerical.  Consequently this module does not
claim to shoot from the V2 source window.  ``realize_local_pole`` instead
starts from the theorem's normalized local jet at a small positive remaining
distance and integrates the exact compactified field.  It is honest
``COMPUTED/E1`` local evidence, not interval validation and not a numerical
realization of the global source-window statement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import quad, solve_ivp


Array = NDArray[np.float64]

LOCAL_REALIZATION_STATUS = "COMPUTED/E1_LOCAL_ASYMPTOTIC_SEED"
SOURCE_WINDOW_STATUS = "NOT_NUMERICALLY_RESOLVED"
SOURCE_WINDOW_REASON = (
    "Theorem V3 proves the V2 source window on an existential compact box, "
    "but the constants r_p, A, epsilon_-/epsilon_+ and the continued source "
    "map S_mu(phi) are not supplied as explicit numerical data."
)


@dataclass(frozen=True)
class PoleParameters:
    """Positive parameters in Theorem V3, with ``delta=r**2``."""

    r: float
    a2: float
    epsilon: float

    def __post_init__(self) -> None:
        if not np.isfinite(self.r) or self.r <= 0.0:
            raise ValueError("r must be finite and positive")
        if not np.isfinite(self.a2):
            raise ValueError("a2 must be finite")
        if not np.isfinite(self.epsilon) or self.epsilon <= 0.0:
            raise ValueError("epsilon must be finite and positive")

    @property
    def delta(self) -> float:
        return self.r * self.r

    @property
    def a(self) -> float:
        return 1.0 + np.sqrt(self.epsilon) * self.r**3 * self.a2

    @property
    def ell(self) -> float:
        return np.sqrt(6.0) * self.delta


@dataclass(frozen=True)
class PoleLabels:
    """The normalized local labels ``(Z_0, W_0, kappa)`` from V3."""

    z0: float
    w0: float
    kappa: float

    def __post_init__(self) -> None:
        if not all(np.isfinite(value) for value in (self.z0, self.w0, self.kappa)):
            raise ValueError("all pole labels must be finite")


@dataclass
class PoleRealization:
    """A finite exact-field orbit seeded by the normalized local pole jet."""

    parameters: PoleParameters
    labels: PoleLabels
    sigma: Array
    compact: Array
    physical: Array
    diagnostics: dict[str, float | str | bool]
    dense_solution: Any = field(repr=False)


@dataclass(frozen=True)
class ActionCutoffLadder:
    """Raw and Laurent--log-subtracted actions for decreasing cutoffs."""

    cut_sigma: float
    sigma: Array
    raw_action: Array
    divergent_part: Array
    subtracted_action: Array
    density: Array
    regularized_density: Array


def cubic_f(u: Array | float) -> Array | float:
    """The physical nonlinearity ``f(u)=u^3/3-u``."""

    return np.asarray(u) ** 3 / 3.0 - np.asarray(u)


def cubic_potential(u: Array | float) -> Array | float:
    """The fixed primitive ``F'(u)=f(u)`` used by the Hamiltonian."""

    return np.asarray(u) ** 4 / 12.0 - np.asarray(u) ** 2 / 2.0


def physical_field(
    _physical_x: float, state: Array, parameters: PoleParameters
) -> Array:
    """Exact physical stationary field, V3 equation (27).

    State order is ``(u,p,v,q)`` and the independent variable is the physical
    spatial coordinate ``mathsf{x}``.
    """

    u, p, v, q = np.asarray(state)
    delta = parameters.delta
    return np.asarray(
        (
            p / delta,
            (u**3 / 3.0 - u - v) / delta,
            q,
            parameters.epsilon * (u - parameters.a),
        ),
        dtype=np.float64,
    )


def physical_hamiltonian(state: Array, parameters: PoleParameters) -> Array:
    """The exact first integral ``G_delta`` in physical variables."""

    u, p, v, q = np.asarray(state)
    epsilon = parameters.epsilon
    return (
        0.5 * (epsilon * p * p - q * q)
        - epsilon * (cubic_potential(u) + (parameters.a - u) * v)
    )


def compact_tau_field(
    _tau: float, state: Array, parameters: PoleParameters
) -> Array:
    """Exact compactified field (28) in order ``(sigma,X,Y,W,Z)``."""

    sigma, x_normalized, y_normalized, w_normalized, z_normalized = np.asarray(state)
    if sigma <= 0.0:
        raise ValueError("the exact logarithmic chart requires sigma>0")
    delta = parameters.delta
    ell = parameters.ell
    epsilon = parameters.epsilon
    log_sigma = np.log(sigma)
    return np.array(
        (
            -sigma,
            -x_normalized + y_normalized,
            -2.0 * y_normalized
            + 2.0 * x_normalized**3
            - sigma**2 * x_normalized / delta**2
            - sigma**3 * z_normalized / (ell * delta**2)
            - epsilon * sigma**4 * log_sigma / delta**2,
            ell * epsilon * (x_normalized - 1.0)
            - parameters.a * epsilon * sigma,
            sigma * (w_normalized + ell * epsilon),
        ),
        dtype=np.float64,
    )


def compact_sigma_field(
    sigma: float, state: Array, parameters: PoleParameters
) -> Array:
    """Exact compactified field with physical remaining distance as clock.

    Since ``d sigma / d mathsf{x}=-1`` and ``dot=sigma*d/dmathsf{x}``, this
    is precisely ``d(X,Y,W,Z)/d sigma`` along the same physical orbit.
    """

    if sigma <= 0.0:
        raise ValueError("sigma must be positive")
    augmented = np.r_[sigma, np.asarray(state, dtype=np.float64)]
    return -compact_tau_field(0.0, augmented, parameters)[1:] / sigma


def compact_to_physical(
    sigma: Array | float, state: Array, parameters: PoleParameters
) -> Array:
    """Exact inverse (42), from ``(X,Y,W,Z)`` to ``(u,p,v,q)``."""

    sigma_array = np.asarray(sigma, dtype=np.float64)
    if np.any(sigma_array <= 0.0):
        raise ValueError("sigma must be positive")
    x_normalized, y_normalized, w_normalized, z_normalized = np.asarray(state)
    ell = parameters.ell
    delta = parameters.delta
    epsilon = parameters.epsilon
    log_sigma = np.log(sigma_array)
    return np.asarray(
        (
            ell * x_normalized / sigma_array,
            ell * delta * y_normalized / sigma_array**2,
            z_normalized + ell * epsilon * sigma_array * log_sigma,
            w_normalized - ell * epsilon * log_sigma,
        ),
        dtype=np.float64,
    )


def physical_to_compact(
    sigma: Array | float, state: Array, parameters: PoleParameters
) -> Array:
    """Exact transformation (25), from ``(u,p,v,q)`` to ``(X,Y,W,Z)``."""

    sigma_array = np.asarray(sigma, dtype=np.float64)
    if np.any(sigma_array <= 0.0):
        raise ValueError("sigma must be positive")
    u, p, v, q = np.asarray(state)
    ell = parameters.ell
    delta = parameters.delta
    epsilon = parameters.epsilon
    log_sigma = np.log(sigma_array)
    return np.asarray(
        (
            sigma_array * u / ell,
            sigma_array**2 * p / (ell * delta),
            q + ell * epsilon * log_sigma,
            v - ell * epsilon * sigma_array * log_sigma,
        ),
        dtype=np.float64,
    )


def jet_coefficients(
    parameters: PoleParameters, labels: PoleLabels
) -> dict[str, float]:
    """Coefficients (34) of the normalized resonant pole jet."""

    delta = parameters.delta
    ell = parameters.ell
    epsilon = parameters.epsilon
    return {
        "x2": 1.0 / (6.0 * delta**2),
        "x3": labels.z0 / (4.0 * ell * delta**2),
        "m2": -epsilon / (10.0 * delta**2),
        "m1": labels.w0 / (5.0 * ell * delta**2)
        + 6.0 * epsilon / (25.0 * delta**2),
    }


def normalized_jet(
    sigma: Array | float, parameters: PoleParameters, labels: PoleLabels
) -> Array:
    """The displayed terms of V3 expansions (36)--(39).

    State order is ``(X,Y,W,Z)``.  Omitted terms retain exactly the theorem's
    stated orders; no fitted or invented coefficients are inserted.
    """

    sigma_array = np.asarray(sigma, dtype=np.float64)
    if np.any(sigma_array <= 0.0):
        raise ValueError("sigma must be positive")
    coefficients = jet_coefficients(parameters, labels)
    x2 = coefficients["x2"]
    x3 = coefficients["x3"]
    m2 = coefficients["m2"]
    m1 = coefficients["m1"]
    log_sigma = np.log(sigma_array)
    g = m2 * log_sigma**2 + m1 * log_sigma + labels.kappa
    g_prime = 2.0 * m2 * log_sigma + m1
    x_normalized = 1.0 + x2 * sigma_array**2 + x3 * sigma_array**3 + sigma_array**4 * g
    y_normalized = (
        1.0
        - x2 * sigma_array**2
        - 2.0 * x3 * sigma_array**3
        + sigma_array**4 * (-3.0 * g - g_prime)
    )
    w_normalized = (
        labels.w0
        + parameters.a * parameters.epsilon * sigma_array
        - parameters.ell * parameters.epsilon * x2 * sigma_array**2 / 2.0
        - parameters.ell * parameters.epsilon * x3 * sigma_array**3 / 3.0
    )
    z_normalized = (
        labels.z0
        - (labels.w0 + parameters.ell * parameters.epsilon) * sigma_array
        - parameters.a * parameters.epsilon * sigma_array**2 / 2.0
        + parameters.ell * parameters.epsilon * x2 * sigma_array**3 / 6.0
        + parameters.ell * parameters.epsilon * x3 * sigma_array**4 / 12.0
    )
    return np.asarray(
        (x_normalized, y_normalized, w_normalized, z_normalized),
        dtype=np.float64,
    )


def resonance_identity_residuals(
    parameters: PoleParameters, labels: PoleLabels
) -> dict[str, float]:
    """Algebraic residuals for the nonresonant and root-four cancellations."""

    coefficient = jet_coefficients(parameters, labels)
    delta = parameters.delta
    ell = parameters.ell
    epsilon = parameters.epsilon
    return {
        "x2_nonresonant": 6.0 * coefficient["x2"] - 1.0 / delta**2,
        "x3_nonresonant": 4.0 * coefficient["x3"]
        - labels.z0 / (ell * delta**2),
        "root4_log_squared": 10.0 * coefficient["m2"] + epsilon / delta**2,
        "root4_log": 2.0 * coefficient["m2"]
        + 5.0 * coefficient["m1"]
        - (labels.w0 + ell * epsilon) / (ell * delta**2),
        "order2_constant_cancellation": 6.0 * coefficient["x2"] ** 2
        - coefficient["x2"] / delta**2,
    }


def indicial_spectra() -> dict[str, tuple[float, ...]]:
    """Return the exact spectra stated in V3 equations (5) and (31)."""

    return {
        "compact_flow": (-4.0, -1.0, 0.0, 0.0, 1.0),
        "normalized_power": (-1.0, 0.0, 0.0, 1.0, 4.0),
        "scalar_indicial_roots": (-1.0, 4.0),
    }


def scalar_indicial_residual(
    sigma: Array | float, parameters: PoleParameters, labels: PoleLabels
) -> Array:
    """Residual of the exact scalar Fuchsian equation (33) for the shown jet."""

    sigma_array = np.asarray(sigma, dtype=np.float64)
    if np.any(sigma_array <= 0.0):
        raise ValueError("sigma must be positive")
    coefficient = jet_coefficients(parameters, labels)
    x2 = coefficient["x2"]
    x3 = coefficient["x3"]
    m2 = coefficient["m2"]
    m1 = coefficient["m1"]
    log_sigma = np.log(sigma_array)
    g = m2 * log_sigma**2 + m1 * log_sigma + labels.kappa
    g_prime = 2.0 * m2 * log_sigma + m1
    g_second = 2.0 * m2
    h = x2 * sigma_array**2 + x3 * sigma_array**3 + sigma_array**4 * g
    d_h = (
        2.0 * x2 * sigma_array**2
        + 3.0 * x3 * sigma_array**3
        + sigma_array**4 * (4.0 * g + g_prime)
    )
    d2_h = (
        4.0 * x2 * sigma_array**2
        + 9.0 * x3 * sigma_array**3
        + sigma_array**4 * (16.0 * g + 8.0 * g_prime + g_second)
    )
    operator_h = d2_h - 3.0 * d_h - 4.0 * h
    z_normalized = normalized_jet(sigma_array, parameters, labels)[3]
    right_hand_side = (
        6.0 * h**2
        + 2.0 * h**3
        - sigma_array**2 * (1.0 + h) / parameters.delta**2
        - sigma_array**3 * z_normalized / (parameters.ell * parameters.delta**2)
        - parameters.epsilon
        * sigma_array**4
        * log_sigma
        / parameters.delta**2
    )
    return np.asarray(operator_h - right_hand_side, dtype=np.float64)


def normalized_indicial_residual(
    sigma: Array | float, parameters: PoleParameters, labels: PoleLabels
) -> Array:
    """Equation-(33) residual divided by its proved remainder weight."""

    sigma_array = np.asarray(sigma, dtype=np.float64)
    weight = sigma_array**5 * (1.0 + np.abs(np.log(sigma_array))) ** 2
    return scalar_indicial_residual(sigma_array, parameters, labels) / weight


def jet_vector_residual(
    sigma: float, parameters: PoleParameters, labels: PoleLabels
) -> Array:
    """Derivative defect of the displayed jet in the exact sigma field.

    This is the finite initialization defect used by ``realize_local_pole``;
    it must not be confused with an interval enclosure of the omitted terms.
    """

    if sigma <= 0.0:
        raise ValueError("sigma must be positive")
    coefficient = jet_coefficients(parameters, labels)
    x2 = coefficient["x2"]
    x3 = coefficient["x3"]
    m2 = coefficient["m2"]
    m1 = coefficient["m1"]
    log_sigma = np.log(sigma)
    g = m2 * log_sigma**2 + m1 * log_sigma + labels.kappa
    g_prime = 2.0 * m2 * log_sigma + m1
    g_second = 2.0 * m2
    y_root4 = -3.0 * g - g_prime
    y_root4_prime = -3.0 * g_prime - g_second
    displayed_derivative = np.array(
        (
            2.0 * x2 * sigma
            + 3.0 * x3 * sigma**2
            + sigma**3 * (4.0 * g + g_prime),
            -2.0 * x2 * sigma
            - 6.0 * x3 * sigma**2
            + sigma**3 * (4.0 * y_root4 + y_root4_prime),
            parameters.a * parameters.epsilon
            - parameters.ell * parameters.epsilon * x2 * sigma
            - parameters.ell * parameters.epsilon * x3 * sigma**2,
            -(labels.w0 + parameters.ell * parameters.epsilon)
            - parameters.a * parameters.epsilon * sigma
            + parameters.ell * parameters.epsilon * x2 * sigma**2 / 2.0
            + parameters.ell * parameters.epsilon * x3 * sigma**3 / 3.0,
        ),
        dtype=np.float64,
    )
    exact_derivative = compact_sigma_field(
        sigma, normalized_jet(sigma, parameters, labels), parameters
    )
    return displayed_derivative - exact_derivative


def pole_energy_from_labels(
    parameters: PoleParameters, labels: PoleLabels
) -> float:
    """The finite conserved-energy identity immediately before V3 equation (41)."""

    epsilon = parameters.epsilon
    delta = parameters.delta
    ell = parameters.ell
    return float(
        7.0 * epsilon / 12.0
        - 186.0 * epsilon**2 * delta**2 / 25.0
        - 30.0 * epsilon * delta**4 * labels.kappa
        - epsilon * parameters.a * labels.z0
        - 6.0 * ell * epsilon * labels.w0 / 5.0
        - 0.5 * labels.w0**2
    )


def fixed_source_energy_kappa(
    parameters: PoleParameters, z0: float, w0: float
) -> float:
    """Solve the V3 finite energy identity for ``kappa``.

    This places the *local labels* on the homogeneous-equilibrium energy level
    ``G(O)=-epsilon*F(a)``.  It does not show that those labels are reached by
    the unresolved global source window.
    """

    zero_kappa = PoleLabels(float(z0), float(w0), 0.0)
    base_energy = pole_energy_from_labels(parameters, zero_kappa)
    target = -parameters.epsilon * float(cubic_potential(parameters.a))
    return float(
        (base_energy - target)
        / (30.0 * parameters.epsilon * parameters.delta**4)
    )


def energy_projected_jet(
    sigma: float, parameters: PoleParameters, labels: PoleLabels
) -> Array:
    """Project the displayed jet onto its exact V3 conserved-energy level.

    Equations (36)--(39) omit a controlled remainder, so their finite truncation
    does not conserve the limiting identity exactly.  Keeping ``X,W,Z`` fixed,
    this function selects the positive ``p`` (and hence ``Y``) root for the
    exact physical Hamiltonian value determined by the labels.  The adjustment
    is recorded by ``realize_local_pole`` and does not assert global source
    entry.
    """

    compact = normalized_jet(sigma, parameters, labels).copy()
    physical = compact_to_physical(sigma, compact, parameters)
    u, _p, v, q = physical
    target = pole_energy_from_labels(parameters, labels)
    epsilon = parameters.epsilon
    p_squared = (
        2.0
        / epsilon
        * (
            target
            + 0.5 * q * q
            + epsilon
            * (cubic_potential(u) + (parameters.a - u) * v)
        )
    )
    if not np.isfinite(p_squared) or p_squared <= 0.0:
        raise RuntimeError("the local jet has no positive real energy projection")
    p = float(np.sqrt(p_squared))
    compact[1] = sigma**2 * p / (parameters.ell * parameters.delta)
    return compact


def field_crosscheck(
    sigma: float, compact_state: Array, parameters: PoleParameters
) -> dict[str, float]:
    """Cross-check (27) against (28) through the exact change of variables."""

    compact_state = np.asarray(compact_state, dtype=np.float64)
    x_normalized, y_normalized, w_normalized, z_normalized = compact_state
    compact_derivative = compact_sigma_field(sigma, compact_state, parameters)
    dx_ds, dy_ds, dw_ds, dz_ds = compact_derivative
    ell = parameters.ell
    delta = parameters.delta
    epsilon = parameters.epsilon
    log_sigma = np.log(sigma)
    physical = compact_to_physical(sigma, compact_state, parameters)
    transformed_sigma_derivative = np.array(
        (
            ell * (dx_ds / sigma - x_normalized / sigma**2),
            ell
            * delta
            * (dy_ds / sigma**2 - 2.0 * y_normalized / sigma**3),
            dz_ds + ell * epsilon * (log_sigma + 1.0),
            dw_ds - ell * epsilon / sigma,
        )
    )
    expected_sigma_derivative = -physical_field(0.0, physical, parameters)
    defect = transformed_sigma_derivative - expected_sigma_derivative
    scale = np.maximum(1.0, np.abs(expected_sigma_derivative))
    roundtrip = physical_to_compact(sigma, physical, parameters) - compact_state
    return {
        "physical_compact_field_defect_inf": float(np.max(np.abs(defect))),
        "physical_compact_field_relative_defect_inf": float(
            np.max(np.abs(defect) / scale)
        ),
        "coordinate_roundtrip_defect_inf": float(np.max(np.abs(roundtrip))),
    }


def realize_local_pole(
    parameters: PoleParameters,
    labels: PoleLabels,
    *,
    sigma_min: float = 1.0e-4,
    sigma_cut: float = 3.0e-3,
    points: int = 240,
    rtol: float = 2.0e-11,
    atol: float = 2.0e-13,
    physical_crosscheck: bool = False,
) -> PoleRealization:
    """Integrate an exact local pole segment from a theorem-jet seed.

    Integration proceeds from small to larger ``sigma`` because this suppresses
    contamination by the excluded ``sigma**(-1)`` mode.  The returned segment
    solves the exact compactified field after its finite, explicitly reported
    jet initialization error.
    """

    if not 0.0 < sigma_min < sigma_cut:
        raise ValueError("require 0 < sigma_min < sigma_cut")
    if points < 12:
        raise ValueError("points must be at least 12")
    sigma_grid = np.geomspace(sigma_min, sigma_cut, points)
    displayed_initial = normalized_jet(sigma_min, parameters, labels)
    initial = energy_projected_jet(sigma_min, parameters, labels)
    solution = solve_ivp(
        lambda sigma, state: compact_sigma_field(sigma, state, parameters),
        (sigma_min, sigma_cut),
        initial,
        method="DOP853",
        t_eval=sigma_grid,
        dense_output=True,
        rtol=rtol,
        atol=atol,
        max_step=(sigma_cut - sigma_min) / 180.0,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    compact = np.asarray(solution.y, dtype=np.float64)
    physical = compact_to_physical(sigma_grid, compact, parameters)
    energy = np.asarray(physical_hamiltonian(physical, parameters), dtype=np.float64)
    energy_scale = max(1.0, float(np.max(np.abs(energy))))
    sample_indices = np.linspace(0, points - 1, min(points, 24), dtype=int)
    field_defects = [
        field_crosscheck(
            float(sigma_grid[index]), compact[:, index], parameters
        )["physical_compact_field_relative_defect_inf"]
        for index in sample_indices
    ]
    raw_residual = float(abs(scalar_indicial_residual(sigma_min, parameters, labels)))
    normalized_residual = float(
        abs(normalized_indicial_residual(sigma_min, parameters, labels))
    )
    vector_residual = jet_vector_residual(sigma_min, parameters, labels)
    diagnostics: dict[str, float | str | bool] = {
        "evidence_status": LOCAL_REALIZATION_STATUS,
        "source_window_status": SOURCE_WINDOW_STATUS,
        "source_window_reason": SOURCE_WINDOW_REASON,
        "solver_success": bool(solution.success),
        "sigma_min": float(sigma_min),
        "sigma_cut": float(sigma_cut),
        "initial_scalar_indicial_residual": raw_residual,
        "initial_normalized_indicial_residual": normalized_residual,
        "initial_jet_vector_residual_inf": float(np.max(np.abs(vector_residual))),
        "initial_energy_projection_delta_Y": float(initial[1] - displayed_initial[1]),
        "initial_energy_identity_defect": float(
            physical_hamiltonian(
                compact_to_physical(sigma_min, initial, parameters), parameters
            )
            - pole_energy_from_labels(parameters, labels)
        ),
        "hamiltonian_drift": float(np.ptp(energy)),
        "hamiltonian_relative_drift": float(np.ptp(energy) / energy_scale),
        "max_physical_compact_field_relative_defect": float(max(field_defects)),
        "minimum_physical_u": float(np.min(physical[0])),
        "maximum_physical_u": float(np.max(physical[0])),
        "small_sigma_X_minus_one": float(compact[0, 0] - 1.0),
        "small_sigma_Y_minus_one": float(compact[1, 0] - 1.0),
        "small_sigma_W_minus_W0": float(compact[2, 0] - labels.w0),
        "small_sigma_Z_minus_Z0": float(compact[3, 0] - labels.z0),
    }
    realization = PoleRealization(
        parameters=parameters,
        labels=labels,
        sigma=sigma_grid,
        compact=compact,
        physical=physical,
        diagnostics=diagnostics,
        dense_solution=solution.sol,
    )
    if physical_crosscheck:
        diagnostics.update(independent_physical_crosscheck(realization))
    return realization


def independent_physical_crosscheck(
    realization: PoleRealization,
    *,
    rtol: float = 2.0e-10,
    atol: float = 2.0e-12,
) -> dict[str, float | bool]:
    """Integrate (27) independently and compare in normalized coordinates."""

    sigma_descending = realization.sigma[::-1]
    sigma_cut = float(sigma_descending[0])
    physical_x = sigma_cut - sigma_descending
    initial = realization.physical[:, -1]
    span = float(physical_x[-1])
    integration = solve_ivp(
        lambda physical_x_value, state: physical_field(
            physical_x_value, state, realization.parameters
        ),
        (0.0, span),
        initial,
        method="DOP853",
        t_eval=physical_x,
        rtol=rtol,
        atol=atol,
        max_step=span / 300.0,
    )
    if not integration.success:
        raise RuntimeError(integration.message)
    compact_from_physical = physical_to_compact(
        sigma_descending, integration.y, realization.parameters
    )
    compact_reference = realization.compact[:, ::-1]
    defect = compact_from_physical - compact_reference
    energy = np.asarray(
        physical_hamiltonian(integration.y, realization.parameters), dtype=np.float64
    )
    return {
        "independent_physical_solver_success": bool(integration.success),
        "independent_physical_compact_defect_inf": float(
            np.max(np.abs(defect))
        ),
        "independent_physical_hamiltonian_drift": float(np.ptp(energy)),
    }


def action_density(
    sigma: Array | float, compact_state: Array, parameters: PoleParameters
) -> Array:
    """Exact physical action density, V3 equation (45)."""

    sigma_array = np.asarray(sigma, dtype=np.float64)
    _x_normalized, y_normalized, w_normalized, _z_normalized = np.asarray(
        compact_state
    )
    q = w_normalized - parameters.ell * parameters.epsilon * np.log(sigma_array)
    return np.asarray(
        6.0
        * parameters.epsilon
        * parameters.delta**3
        * y_normalized**2
        / sigma_array**4
        - q**2 / parameters.delta,
        dtype=np.float64,
    )


def divergent_action(
    sigma: Array | float, parameters: PoleParameters, z0: float
) -> Array:
    """The forced Laurent--log divergence ``F_div`` in equation (48)."""

    sigma_array = np.asarray(sigma, dtype=np.float64)
    return np.asarray(
        2.0 * parameters.epsilon * parameters.delta**3 / sigma_array**3
        - 2.0 * parameters.epsilon * parameters.delta / sigma_array
        + np.sqrt(6.0) * parameters.epsilon * z0 * np.log(sigma_array),
        dtype=np.float64,
    )


def divergent_action_derivative(
    sigma: Array | float, parameters: PoleParameters, z0: float
) -> Array:
    """Derivative of ``F_div``; its negative is the singular density."""

    sigma_array = np.asarray(sigma, dtype=np.float64)
    return np.asarray(
        -6.0 * parameters.epsilon * parameters.delta**3 / sigma_array**4
        + 2.0 * parameters.epsilon * parameters.delta / sigma_array**2
        + np.sqrt(6.0) * parameters.epsilon * z0 / sigma_array,
        dtype=np.float64,
    )


def regularized_action_density(
    sigma: Array | float,
    compact_state: Array,
    parameters: PoleParameters,
    z0: float,
) -> Array:
    """The integrable density ``lambda(partial_x)+F_div'`` from (49)."""

    return action_density(sigma, compact_state, parameters) + divergent_action_derivative(
        sigma, parameters, z0
    )


def _integrate_density(
    realization: PoleRealization, lower_sigma: float, upper_sigma: float
) -> tuple[float, float]:
    """Integrate the exact density and return value plus quadrature error."""

    if not realization.sigma[0] <= lower_sigma <= upper_sigma <= realization.sigma[-1]:
        raise ValueError("integration limits must lie inside the realized segment")

    def integrand(sigma: float) -> float:
        state = realization.dense_solution(sigma)
        return float(action_density(sigma, state, realization.parameters))

    value, error = quad(
        integrand,
        lower_sigma,
        upper_sigma,
        epsabs=2.0e-9,
        epsrel=2.0e-11,
        limit=250,
    )
    return float(value), float(error)


def action_cutoff_ladder(
    realization: PoleRealization,
    *,
    cut_sigma: float | None = None,
    cutoff_sigmas: Iterable[float] | None = None,
    count: int = 8,
) -> ActionCutoffLadder:
    """Compute raw and subtracted actions along a cutoff ladder.

    The cut is the earlier point (larger ``sigma``).  Each raw action is
    ``integral_sigma^cut density(t) dt``, exactly equivalent to the oriented
    physical line integral because ``d mathsf{x}=-d sigma``.
    """

    lower = float(realization.sigma[0])
    upper = float(realization.sigma[-1])
    cut = upper if cut_sigma is None else float(cut_sigma)
    if not lower < cut <= upper:
        raise ValueError("cut_sigma must lie above sigma_min in the realized segment")
    if cutoff_sigmas is None:
        if count < 2:
            raise ValueError("count must be at least two")
        cutoffs = np.geomspace(0.85 * cut, lower, count)
    else:
        cutoffs = np.array(tuple(float(value) for value in cutoff_sigmas))
        if cutoffs.size == 0:
            raise ValueError("cutoff_sigmas must not be empty")
        cutoffs = np.sort(np.unique(cutoffs))[::-1]
    if np.any(cutoffs < lower) or np.any(cutoffs >= cut):
        raise ValueError("every cutoff must satisfy sigma_min <= sigma < cut_sigma")
    raw = np.array(
        [_integrate_density(realization, float(sigma), cut)[0] for sigma in cutoffs]
    )
    states = np.column_stack(
        [realization.dense_solution(float(sigma)) for sigma in cutoffs]
    )
    divergence = divergent_action(
        cutoffs, realization.parameters, realization.labels.z0
    )
    density = action_density(cutoffs, states, realization.parameters)
    regularized = regularized_action_density(
        cutoffs, states, realization.parameters, realization.labels.z0
    )
    return ActionCutoffLadder(
        cut_sigma=cut,
        sigma=cutoffs,
        raw_action=raw,
        divergent_part=divergence,
        subtracted_action=raw - divergence,
        density=density,
        regularized_density=regularized,
    )


def moving_cut_additivity(
    realization: PoleRealization,
    *,
    earlier_cut_sigma: float,
    later_cut_sigma: float,
    endpoint_sigma: float | None = None,
) -> dict[str, float]:
    """Numerically check the exact moving-cut identity (50).

    Earlier in physical time means larger remaining distance, hence
    ``earlier_cut_sigma > later_cut_sigma > endpoint_sigma``.
    """

    endpoint = (
        float(realization.sigma[0])
        if endpoint_sigma is None
        else float(endpoint_sigma)
    )
    if not endpoint < later_cut_sigma < earlier_cut_sigma <= realization.sigma[-1]:
        raise ValueError(
            "require endpoint_sigma < later_cut_sigma < earlier_cut_sigma"
        )
    action_earlier, error_earlier = _integrate_density(
        realization, endpoint, earlier_cut_sigma
    )
    action_later, error_later = _integrate_density(
        realization, endpoint, later_cut_sigma
    )
    finite_segment, error_segment = _integrate_density(
        realization, later_cut_sigma, earlier_cut_sigma
    )
    subtraction = float(
        divergent_action(endpoint, realization.parameters, realization.labels.z0)
    )
    finite_part_earlier = action_earlier - subtraction
    finite_part_later = action_later - subtraction
    residual = finite_part_earlier - (finite_segment + finite_part_later)
    return {
        "finite_part_earlier_cut": float(finite_part_earlier),
        "finite_part_later_cut": float(finite_part_later),
        "finite_segment_action": float(finite_segment),
        "moving_cut_additivity_residual": float(residual),
        "quadrature_error_bound_sum": float(
            error_earlier + error_later + error_segment
        ),
    }


__all__ = [
    "ActionCutoffLadder",
    "LOCAL_REALIZATION_STATUS",
    "PoleLabels",
    "PoleParameters",
    "PoleRealization",
    "SOURCE_WINDOW_REASON",
    "SOURCE_WINDOW_STATUS",
    "action_cutoff_ladder",
    "action_density",
    "compact_sigma_field",
    "compact_tau_field",
    "compact_to_physical",
    "cubic_f",
    "cubic_potential",
    "divergent_action",
    "divergent_action_derivative",
    "energy_projected_jet",
    "field_crosscheck",
    "fixed_source_energy_kappa",
    "independent_physical_crosscheck",
    "indicial_spectra",
    "jet_coefficients",
    "jet_vector_residual",
    "moving_cut_additivity",
    "normalized_indicial_residual",
    "normalized_jet",
    "physical_field",
    "physical_hamiltonian",
    "physical_to_compact",
    "pole_energy_from_labels",
    "realize_local_pole",
    "regularized_action_density",
    "resonance_identity_residuals",
    "scalar_indicial_residual",
]
