"""Floating V5 endpoint adjoint, exchange, and matching Jacobian.

The computation is tied to the energy-preserving matched centerline and the
finite-horizon V4 graph proxy at ``(r,a2,epsilon)=(3/200,0,1)``.  It adds the
linearized energy BVP to the archived three-beta slice and uses the
normalizations and clocks of V5(37), V5(51)--(58).  The result is one E1/QA
object, never a maximal-graph identification, uniform exchange, or nonlinear
uniqueness proof.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_bvp, solve_ivp
from scipy.interpolate import CubicSpline
from scipy.special import gamma

from numerics.rfsn_numerics import vdp_field
from numerics.vdp_matched_outer import (
    resolved_k1_energy_root,
    resolved_k1_rhs_r1,
    resolved_k1_to_outer_normal,
)
from numerics.vdp_outer import (
    OuterParameters,
    positive_pi_outer_rhs_q,
    positive_pi_outer_state,
    shifted_energy_polynomial,
)
from numerics.vdp_p2e_channel_scout import _direct_kato_provider
from numerics.vdp_v4_future_graph_slice import (
    _load_configuration as _load_v4_configuration,
    _normal_values as _v4_normal_values,
    _solve_collocation_ladder as _solve_v4_collocation_ladder,
)


Array = NDArray[np.float64]
HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent
DEFAULT_CONFIG = HERE / "config/vdp_v5_endpoint_exchange_v2.json"
DEFAULT_RESULT = HERE / "results/vdp_v5_endpoint_exchange_v2/result.json"
DEFAULT_DATA = HERE / "results/vdp_v5_endpoint_exchange_v2/adjoint.npz"


class EndpointExchangeError(RuntimeError):
    """The frozen endpoint calculation or a predeclared QA check failed."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_configuration(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    configuration = json.loads(path.read_text(encoding="utf-8"))
    if configuration.get("schema_version") != (
        "rfsn-vdp-v5-endpoint-exchange-v2-config/1"
    ):
        raise EndpointExchangeError("unexpected endpoint-exchange schema")
    for binding in configuration["input_bindings"]:
        source = REPOSITORY / binding["path"]
        if not source.is_file() or _sha256(source) != binding["sha256"]:
            raise EndpointExchangeError(
                f"input binding changed: {binding['role']}"
            )
    return configuration


def _bound_path(configuration: dict[str, Any], role: str) -> Path:
    for binding in configuration["input_bindings"]:
        if binding["role"] == role:
            return REPOSITORY / binding["path"]
    raise EndpointExchangeError(f"missing input role {role}")


def _central_jacobian(state: Array, parameters: OuterParameters) -> Array:
    u = float(state[0])
    sqrt_epsilon = np.sqrt(parameters.epsilon)
    c = 2.0 * parameters.r * parameters.a2 + (
        sqrt_epsilon * parameters.r**4 * parameters.a2**2
    )
    quadratic = 1.0 + sqrt_epsilon * parameters.r**3 * parameters.a2
    cubic = sqrt_epsilon * parameters.r**2 / 3.0
    return np.array(
        [
            [0.0, 1.0, 0.0, 0.0],
            [c - 2.0 * quadratic * u + 3.0 * cubic * u * u, 0.0, -1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )


def _jost_basis(
    configuration: dict[str, Any], *, section_m: float
) -> tuple[dict[str, float], dict[str, Array]]:
    options = configuration["integration"]
    b2 = float(gamma(0.75) * 96.0**0.625 / (8.0 * np.sqrt(np.pi)))
    b3 = float(gamma(0.25) * 96.0**0.875 / (16.0 * np.sqrt(np.pi)))
    k0 = float(
        np.sqrt(np.pi)
        * gamma(0.25)
        / (4.0 * np.sqrt(6.0) * gamma(0.75))
    )
    t_c = float(2.0 * np.sqrt(3.0 * section_m))
    recessive_initial = np.array(
        [0.0, -12.0 * b2 * k0, -2.0 * b3, 6.0 * b2],
        dtype=np.float64,
    )
    growing_initial = np.array(
        [0.0, 12.0 * b2 * k0, -2.0 * b3, -6.0 * b2],
        dtype=np.float64,
    )

    def matrix(time: float) -> Array:
        return np.array(
            [
                [0.0, 1.0, 0.0, 0.0],
                [time * time / 6.0, 0.0, -1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [1.0, 0.0, 0.0, 0.0],
            ],
            dtype=np.float64,
        )

    integration = solve_ivp(
        lambda time, state: np.concatenate(
            (matrix(time) @ state[:4], matrix(time) @ state[4:])
        ),
        (0.0, t_c),
        np.concatenate((recessive_initial, growing_initial)),
        method=str(options["method"]),
        rtol=float(options["Jost_rtol"]),
        atol=float(options["Jost_atol"]),
        max_step=float(options["Jost_max_step"]),
        dense_output=True,
    )
    if not integration.success or integration.sol is None:
        raise EndpointExchangeError(
            f"frozen Jost integration failed: {integration.message}"
        )
    time = np.linspace(0.0, t_c, 401)
    state = np.asarray(integration.sol(time), dtype=np.float64)
    recessive = state[:4]
    growing = state[4:]
    # With lambda=P dU-Q dV, omega(s,v) has this row in (U,P,V,Q).
    symplectic_row = np.vstack(
        (recessive[1], -recessive[0], -recessive[3], recessive[2])
    )
    pairing = np.sum(symplectic_row * growing, axis=0)
    constants = {
        "B2": b2,
        "B3": b3,
        "B2B3": b2 * b3,
        "k0": k0,
        "t_c": t_c,
        "frozen_exchange_formula": 24.0 * b2 * b3,
        "frozen_exchange_target": 144.0 * np.sqrt(3.0),
        "pairing_drift": float(np.ptp(pairing)),
    }
    arrays = {
        "jost_t": time,
        "jost_recessive": recessive,
        "jost_growing": growing,
        "jost_symplectic_pairing": pairing,
    }
    return constants, arrays


def _outer_graph_energy_sensitivity(
    configuration: dict[str, Any],
    parameters: OuterParameters,
    *,
    beta_center: float,
    energy_h: float,
) -> tuple[dict[str, float], dict[str, Array]]:
    """Differentiate the finite-horizon V4 graph with respect to ``H``.

    The base graph is represented in the positive-``pi`` variables
    ``(eta,omega)``.  A linear two-point BVP differentiates both the exact
    outer ODE and its terminal normal-nullcline equation while fixing beta
    on the seam.  This supplies the energy component omitted by a fixed-H
    graph slice.
    """

    extension = configuration["full_energy_extension"]
    v4_configuration = copy.deepcopy(
        _load_v4_configuration(
            _bound_path(configuration, "V4_GRAPH_SLICE_CONFIGURATION")
        )
    )
    q_start = float(
        v4_configuration["matched_centerline_binding"]["seam_Q"]
    )
    q_end = float(extension["graph_horizon_Q_end"])
    v4_configuration["slice"]["collocation_Q_end_ladder"] = [q_end]
    energy_scale = parameters.epsilon**2.5 * parameters.r**6
    energy = energy_scale * energy_h
    solutions, _diagnostics = _solve_v4_collocation_ladder(
        v4_configuration,
        parameters,
        np.array([beta_center], dtype=np.float64),
        energy=energy,
        evaluation_q=np.array([q_start], dtype=np.float64),
    )
    base = solutions[(q_end, beta_center)]
    mesh = np.asarray(base.x, dtype=np.float64)
    delta = parameters.delta
    epsilon = parameters.epsilon
    shifted = shifted_energy_polynomial(parameters.a)

    def components(
        coordinate: float, state: Array
    ) -> tuple[Array, Array, float, float, Array, float]:
        eta, omega = (float(value) for value in state)
        scaled_pi = np.exp(eta)
        pi = delta * scaled_pi
        w = delta * omega
        z = coordinate**-0.5
        radicand = (
            epsilon / 2.0
            - 2.0 * parameters.a * epsilon * z / 3.0
            - epsilon * (2.0 * w + 1.0) * z**2
            + 2.0 * parameters.a * epsilon * (w + 1.0) * z**3
            + (epsilon * pi * pi + 2.0 * energy + 2.0 * epsilon * shifted)
            * z**4
        )
        chi = np.sqrt(radicand)
        chi_h = energy_scale * z**4 / chi
        chi_eta = epsilon * pi * pi * z**4 / chi
        chi_omega = (
            delta
            * epsilon
            * (-z**2 + parameters.a * z**3)
            / chi
        )
        beta_derivative = np.array(
            [
                0.5 * (pi - delta * chi_eta),
                0.5 * (-delta * chi_omega - delta),
            ],
            dtype=np.float64,
        )
        alpha_derivative = np.array(
            [
                0.5 * (pi - delta * chi_eta),
                0.5 * (-delta * chi_omega + delta),
            ],
            dtype=np.float64,
        )
        beta_h = -0.5 * delta * chi_h
        alpha_h = beta_h

        def terminal_equation(candidate: Array) -> float:
            beta, alpha, chi_value, pi_value, w_value = (
                positive_pi_outer_state(
                    coordinate, candidate, parameters, energy=energy
                )
            )
            common = (
                -delta * delta * epsilon * (1.0 - parameters.a * z)
                + 2.0 * delta * float(chi_value) * float(pi_value)
            )
            return float(
                alpha
                + 0.5
                * z**2
                * (common - float(pi_value) - float(pi_value) * float(w_value))
            )

        steps = extension["graph_state_jacobian_steps"]
        terminal_gradient = np.empty(2, dtype=np.float64)
        for column, step in enumerate(
            (float(steps["eta"]), float(steps["omega"]))
        ):
            direction = np.zeros(2, dtype=np.float64)
            direction[column] = step
            terminal_gradient[column] = (
                terminal_equation(state + direction)
                - terminal_equation(state - direction)
            ) / (2.0 * step)
        terminal_h = alpha_h + delta * pi * chi_h * z**2
        return (
            beta_derivative,
            alpha_derivative,
            beta_h,
            alpha_h,
            terminal_gradient,
            terminal_h,
        )

    state_steps = extension["graph_state_jacobian_steps"]
    state_step_array = np.array(
        [state_steps["eta"], state_steps["omega"]], dtype=np.float64
    )

    def sensitivity_rhs(coordinate: Array, sensitivity: Array) -> Array:
        output = np.empty_like(sensitivity)
        for index, value in enumerate(coordinate):
            base_state = np.asarray(base.sol(float(value)), dtype=np.float64)
            jacobian = _central_difference_jacobian(
                lambda candidate: positive_pi_outer_rhs_q(
                    np.array([float(value)]),
                    candidate.reshape(2, 1),
                    parameters,
                    energy=energy,
                )[:, 0],
                base_state,
                state_step_array,
            )
            eta = float(base_state[0])
            z = float(value) ** -0.5
            chi = float(
                positive_pi_outer_state(
                    float(value), base_state, parameters, energy=energy
                )[2]
            )
            chi_h = energy_scale * z**4 / chi
            forcing = np.array(
                [0.0, -chi_h / (2.0 * delta * np.exp(eta))],
                dtype=np.float64,
            )
            output[:, index] = jacobian @ sensitivity[:, index] + forcing
        return output

    left_state = np.asarray(base.sol(q_start), dtype=np.float64)
    right_state = np.asarray(base.sol(q_end), dtype=np.float64)
    left_components = components(q_start, left_state)
    right_components = components(q_end, right_state)

    def sensitivity_boundary(left: Array, right: Array) -> Array:
        return np.array(
            [
                float(left_components[0] @ left + left_components[2]),
                float(right_components[4] @ right + right_components[5]),
            ],
            dtype=np.float64,
        )

    sensitivity = solve_bvp(
        sensitivity_rhs,
        sensitivity_boundary,
        mesh,
        np.zeros((2, mesh.size), dtype=np.float64),
        tol=float(extension["graph_sensitivity_tolerance"]),
        bc_tol=float(extension["graph_sensitivity_boundary_tolerance"]),
        max_nodes=int(extension["graph_sensitivity_maximum_nodes"]),
        verbose=0,
    )
    if not sensitivity.success:
        raise EndpointExchangeError(
            f"outer graph energy sensitivity failed: {sensitivity.message}"
        )
    left_sensitivity = np.asarray(sensitivity.sol(q_start), dtype=np.float64)
    alpha_h = float(
        left_components[1] @ left_sensitivity + left_components[3]
    )
    beta_h = float(
        left_components[0] @ left_sensitivity + left_components[2]
    )
    gamma_h = alpha_h / delta

    finite_step = float(extension["graph_finite_difference_H_step"])
    finite_values: list[float] = []
    for shifted_h in (energy_h - finite_step, energy_h + finite_step):
        shifted_solutions, _shifted_diagnostics = _solve_v4_collocation_ladder(
            v4_configuration,
            parameters,
            np.array([beta_center], dtype=np.float64),
            energy=energy_scale * shifted_h,
            evaluation_q=np.array([q_start], dtype=np.float64),
        )
        shifted_alpha = _v4_normal_values(
            np.array([q_start], dtype=np.float64),
            shifted_solutions[(q_end, beta_center)].sol(
                np.array([q_start], dtype=np.float64)
            ),
            parameters,
            energy=energy_scale * shifted_h,
        )[1]
        finite_values.append(float(shifted_alpha[0]))
    gamma_h_finite_difference = (
        finite_values[1] - finite_values[0]
    ) / (2.0 * finite_step * delta)
    relative_crosscheck = abs(gamma_h - gamma_h_finite_difference) / max(
        abs(gamma_h), abs(gamma_h_finite_difference), np.finfo(float).tiny
    )
    boundary_residual = sensitivity_boundary(
        sensitivity.y[:, 0], sensitivity.y[:, -1]
    )
    diagnostics = {
        "Gamma_H": gamma_h,
        "Gamma_H_large_step_finite_difference": gamma_h_finite_difference,
        "Gamma_H_finite_difference_relative": relative_crosscheck,
        "fixed_beta_residual": beta_h,
        "sensitivity_boundary_residual_inf": float(
            np.max(np.abs(boundary_residual))
        ),
        "sensitivity_rms_residual_max": float(
            np.max(sensitivity.rms_residuals)
        ),
        "base_solver_rms_residual_max": float(np.max(base.rms_residuals)),
        "base_solver_nodes": int(base.x.size),
        "sensitivity_solver_nodes": int(sensitivity.x.size),
    }
    arrays = {
        "outer_energy_sensitivity_Q": np.asarray(
            sensitivity.x, dtype=np.float64
        ),
        "outer_energy_sensitivity_eta_omega": np.asarray(
            sensitivity.y, dtype=np.float64
        ),
        "outer_energy_finite_difference_H": np.array(
            [energy_h - finite_step, energy_h + finite_step], dtype=np.float64
        ),
        "outer_energy_finite_difference_alpha": np.asarray(
            finite_values, dtype=np.float64
        ),
    }
    return diagnostics, arrays


def _outer_map_jacobian_exact(
    state: Array,
    parameters: OuterParameters,
    *,
    outer_r1: float,
    q1: float,
) -> Array:
    pi_scaled, _omega_scaled = (float(value) for value in state)
    sigma = parameters.r / outer_r1
    sqrt_epsilon = np.sqrt(parameters.epsilon)
    z = 1.0 / (1.0 + sqrt_epsilon * outer_r1**2)
    chi_factor = z**2 * parameters.epsilon**1.5 * outer_r1**3
    dq1_d_pi = pi_scaled * sigma**4 / q1
    dq1_d_omega = -sigma**2 / (sqrt_epsilon * q1)
    dc_d_pi = parameters.epsilon * outer_r1 - chi_factor * dq1_d_pi
    dc_d_omega = -chi_factor * dq1_d_omega
    dd_d_omega = parameters.epsilon * z * outer_r1**2
    return 0.5 * parameters.delta * np.array(
        [
            [dc_d_pi, dc_d_omega - dd_d_omega],
            [dc_d_pi, dc_d_omega + dd_d_omega],
        ],
        dtype=np.float64,
    )


def _outer_map_jacobian_full_exact(
    state: Array,
    parameters: OuterParameters,
    *,
    outer_r1: float,
    q1: float,
) -> Array:
    """Derivative of ``(beta,alpha,H)`` with respect to ``(Pi,Omega,H)``."""

    fixed_energy = _outer_map_jacobian_exact(
        state[:2], parameters, outer_r1=outer_r1, q1=q1
    )
    sigma = parameters.r / outer_r1
    sqrt_epsilon = np.sqrt(parameters.epsilon)
    z = 1.0 / (1.0 + sqrt_epsilon * outer_r1**2)
    dq1_d_h = sigma**6 / (sqrt_epsilon * q1)
    dchi_d_h = (
        z**2
        * parameters.epsilon**1.5
        * outer_r1**3
        * dq1_d_h
    )
    derivative = np.zeros((3, 3), dtype=np.float64)
    derivative[:2, :2] = fixed_energy
    derivative[:2, 2] = -0.5 * parameters.delta * dchi_d_h
    derivative[2, 2] = 1.0
    return derivative


def _central_difference_jacobian(
    function: Callable[[Array], Array], state: Array, steps: Array
) -> Array:
    value = np.asarray(function(state), dtype=np.float64)
    jacobian = np.empty((value.size, state.size), dtype=np.float64)
    for column, step in enumerate(steps):
        direction = np.zeros_like(state)
        direction[column] = step
        jacobian[:, column] = (
            np.asarray(function(state + direction), dtype=np.float64)
            - np.asarray(function(state - direction), dtype=np.float64)
        ) / (2.0 * step)
    return jacobian


def _k1_full_jacobian_spline(
    r1: Array,
    state: Array,
    parameters: OuterParameters,
    *,
    energy_h: float,
    state_steps: Array,
    energy_step: float,
    energy_half_step: float,
) -> tuple[CubicSpline, Array, float, float]:
    """Linearization of the resolved ``(Pi,Omega,H)`` flow."""

    full_state = np.vstack(
        (state, np.full(r1.size, energy_h, dtype=np.float64))
    )
    state_spline = CubicSpline(r1, state, axis=1)

    def rhs(coordinate: float, value: Array) -> Array:
        return np.concatenate(
            (
                resolved_k1_rhs_r1(
                    np.array([coordinate]),
                    value[:2].reshape(2, 1),
                    parameters,
                    energy_h=float(value[2]),
                )[:, 0],
                np.array([0.0], dtype=np.float64),
            )
        )

    jacobian = np.zeros((r1.size, 3, 3), dtype=np.float64)
    energy_columns_finite = np.empty((r1.size, 3), dtype=np.float64)
    energy_columns_half = np.empty_like(energy_columns_finite)
    base_residual: list[float] = []
    for index, coordinate in enumerate(r1):
        value = full_state[:, index]
        jacobian[index, :, :2] = _central_difference_jacobian(
            lambda candidate: rhs(
                float(coordinate),
                np.array([candidate[0], candidate[1], energy_h]),
            ),
            value[:2],
            state_steps,
        )
        sigma = parameters.r / float(coordinate)
        sqrt_epsilon = np.sqrt(parameters.epsilon)
        q1 = float(
            resolved_k1_energy_root(
                np.array([coordinate]),
                np.array([value[0]]),
                np.array([value[1]]),
                parameters,
                energy_h=energy_h,
            )[0]
        )
        speed = (
            0.5
            * sqrt_epsilon
            * sigma**2
            * value[0]
            * float(coordinate)
        )
        jacobian[index, :, 2] = np.array(
            [0.0, -sigma**6 / (q1 * speed), 0.0], dtype=np.float64
        )
        for target, step in (
            (energy_columns_finite, energy_step),
            (energy_columns_half, energy_half_step),
        ):
            direction = np.array([0.0, 0.0, step], dtype=np.float64)
            target[index] = (
                rhs(float(coordinate), value + direction)
                - rhs(float(coordinate), value - direction)
            ) / (2.0 * step)
        base_residual.append(
            float(
                np.linalg.norm(
                    state_spline(float(coordinate), 1)
                    - rhs(float(coordinate), value)[:2],
                    ord=np.inf,
                )
            )
        )
    energy_scale = float(np.max(np.abs(jacobian[:, :, 2])))
    energy_column_error = float(
        max(
            np.max(np.abs(energy_columns_finite - jacobian[:, :, 2])),
            np.max(np.abs(energy_columns_half - jacobian[:, :, 2])),
            np.max(np.abs(energy_columns_finite - energy_columns_half)),
        )
        / max(energy_scale, np.finfo(float).tiny)
    )
    return (
        CubicSpline(r1, jacobian, axis=0),
        jacobian,
        float(max(base_residual)),
        energy_column_error,
    )


def _projective_adjoint_full(
    configuration: dict[str, Any],
    r1: Array,
    endpoint_row: Array,
    jacobian_spline: CubicSpline,
) -> tuple[dict[str, float], dict[str, Array]]:
    """Backward three-dimensional adjoint in norm and ratio charts."""

    options = configuration["integration"]
    reference = int(
        configuration["full_energy_extension"][
            "projective_ratio_reference_component"
        ]
    )
    if reference != 0:
        raise EndpointExchangeError("only the frozen Pi ratio chart is supported")
    norm = float(np.linalg.norm(endpoint_row))
    initial_direction = endpoint_row / norm

    def normalized_rhs(coordinate: float, value: Array) -> Array:
        direction = value[:3]
        raw = -direction @ jacobian_spline(coordinate)
        rate = float(direction @ raw)
        return np.concatenate(
            (raw - rate * direction, np.array([rate], dtype=np.float64))
        )

    normalized = solve_ivp(
        normalized_rhs,
        (float(r1[-1]), float(r1[0])),
        np.concatenate((initial_direction, np.array([np.log(norm)]))),
        method=str(options["method"]),
        rtol=float(options["K1_rtol"]),
        atol=float(options["K1_atol"]),
        max_step=float(options["K1_max_step"]),
        dense_output=True,
    )
    if not normalized.success or normalized.sol is None:
        raise EndpointExchangeError(
            f"normalized full adjoint failed: {normalized.message}"
        )
    if abs(endpoint_row[reference]) <= np.finfo(float).tiny:
        raise EndpointExchangeError("endpoint row misses the frozen ratio chart")
    initial_ratios = endpoint_row[1:] / endpoint_row[0]

    def ratio_rhs(coordinate: float, value: Array) -> Array:
        ratio_1, ratio_2 = (float(item) for item in value[:2])
        row = np.array([1.0, ratio_1, ratio_2], dtype=np.float64)
        raw = -row @ jacobian_spline(coordinate)
        reference_rate = float(raw[0])
        return np.array(
            [
                raw[1] - ratio_1 * reference_rate,
                raw[2] - ratio_2 * reference_rate,
                reference_rate,
            ],
            dtype=np.float64,
        )

    ratio = solve_ivp(
        ratio_rhs,
        (float(r1[-1]), float(r1[0])),
        np.array(
            [
                initial_ratios[0],
                initial_ratios[1],
                np.log(abs(float(endpoint_row[0]))),
            ],
            dtype=np.float64,
        ),
        method=str(options["method"]),
        rtol=float(options["K1_rtol"]),
        atol=float(options["K1_atol"]),
        max_step=float(options["K1_max_step"]),
        dense_output=True,
    )
    if not ratio.success or ratio.sol is None:
        raise EndpointExchangeError(
            f"ratio-chart full adjoint failed: {ratio.message}"
        )
    descending = r1[::-1]
    normalized_values = np.asarray(normalized.sol(descending), dtype=np.float64)
    ratio_values = np.asarray(ratio.sol(descending), dtype=np.float64)
    ratio_rows = np.vstack(
        (np.ones(descending.size), ratio_values[0], ratio_values[1])
    )
    ratio_norms = np.linalg.norm(ratio_rows, axis=0)
    ratio_direction = ratio_rows / ratio_norms
    if endpoint_row[0] < 0.0:
        ratio_direction *= -1.0
    dot = np.sum(normalized_values[:3] * ratio_direction, axis=0)
    ratio_direction *= np.where(dot < 0.0, -1.0, 1.0)
    ratio_log_norm = ratio_values[2] + np.log(ratio_norms)
    direction_difference = np.linalg.norm(
        normalized_values[:3] - ratio_direction, axis=0
    )
    diagnostics = {
        "normalized_solver_evaluations": int(normalized.nfev),
        "ratio_solver_evaluations": int(ratio.nfev),
        "direction_crosscheck_max": float(np.max(direction_difference)),
        "log_scale_crosscheck_max": float(
            np.max(np.abs(normalized_values[3] - ratio_log_norm))
        ),
        "central_log_raw_row_norm": float(normalized_values[3, -1]),
        "central_direction_norm_defect": float(
            abs(np.linalg.norm(normalized_values[:3, -1]) - 1.0)
        ),
        "ratio_coordinate_abs_max": float(np.max(np.abs(ratio_values[:2]))),
    }
    arrays = {
        "adjoint_r1_descending": descending,
        "adjoint_unit_row": normalized_values[:3],
        "adjoint_log_raw_norm": normalized_values[3],
        "adjoint_ratio_unit_row": ratio_direction,
        "adjoint_ratio_log_raw_norm": ratio_log_norm,
    }
    return diagnostics, arrays


def _source_tangents(
    configuration: dict[str, Any],
    parameters: OuterParameters,
    *,
    phase: float,
    flight_time: float,
    source_configuration: dict[str, Any],
) -> tuple[dict[str, float], dict[str, Array]]:
    source = source_configuration["common_source_convention"]
    provider = _direct_kato_provider(
        r=parameters.r,
        a2=parameters.a2,
        epsilon=parameters.epsilon,
        source_radius=float(source["source_radius"]),
        graph_horizon=float(source["graph_horizon"]),
        graph_boundary_tolerance=float(source["graph_boundary_tolerance"]),
    )
    differentiation = configuration["differentiation"]
    integration_options = configuration["integration"]
    step = float(differentiation["source_phase_step"])
    half_step = float(differentiation["source_phase_half_step"])
    field = vdp_field(parameters.r, parameters.a2, parameters.epsilon)

    def flow(initial: Array, end_time: float, *, dense: bool = False) -> Any:
        result = solve_ivp(
            lambda time, state: field(
                np.array([time]), state.reshape(4, 1)
            )[:, 0],
            (0.0, end_time),
            initial,
            method=str(integration_options["method"]),
            rtol=float(integration_options["central_rtol"]),
            atol=float(integration_options["central_atol"]),
            max_step=float(integration_options["central_max_step"]),
            dense_output=dense,
        )
        if not result.success:
            raise EndpointExchangeError(
                f"central source flow failed: {result.message}"
            )
        return result

    source_center = provider(phase)
    source_minus = provider(phase - step)
    source_plus = provider(phase + step)
    source_half_minus = provider(phase - half_step)
    source_half_plus = provider(phase + half_step)
    source_tangent_step = (source_plus - source_minus) / (2.0 * step)
    source_tangent_half = (
        source_half_plus - source_half_minus
    ) / (2.0 * half_step)
    source_tangent_richardson = (
        4.0 * source_tangent_half - source_tangent_step
    ) / 3.0

    endpoint_minus = flow(source_minus, flight_time).y[:, -1]
    endpoint_plus = flow(source_plus, flight_time).y[:, -1]
    endpoint_half_minus = flow(source_half_minus, flight_time).y[:, -1]
    endpoint_half_plus = flow(source_half_plus, flight_time).y[:, -1]
    endpoint_tangent_step = (endpoint_plus - endpoint_minus) / (2.0 * step)
    endpoint_tangent_half = (
        endpoint_half_plus - endpoint_half_minus
    ) / (2.0 * half_step)
    endpoint_tangent_richardson = (
        4.0 * endpoint_tangent_half - endpoint_tangent_step
    ) / 3.0

    def combined_rhs(time: float, state: Array) -> Array:
        base = state[:4]
        base_field = field(np.array([time]), base.reshape(4, 1))[:, 0]
        tangent = _central_jacobian(base, parameters) @ state[4:]
        return np.concatenate((base_field, tangent))

    variational = solve_ivp(
        combined_rhs,
        (0.0, flight_time),
        np.concatenate((source_center, source_tangent_richardson)),
        method=str(integration_options["method"]),
        rtol=float(integration_options["central_rtol"]),
        atol=float(integration_options["central_atol"]),
        max_step=float(integration_options["central_max_step"]),
    )
    if not variational.success:
        raise EndpointExchangeError(
            f"central variational flow failed: {variational.message}"
        )
    endpoint_center = variational.y[:4, -1]
    endpoint_tangent_variational = variational.y[4:, -1]

    time_step = float(differentiation["time_step"])
    time_flow = flow(source_center, flight_time + time_step, dense=True)
    if time_flow.sol is None:
        raise EndpointExchangeError("central time dense output is unavailable")
    time_tangent_fd = (
        time_flow.sol(flight_time + time_step)
        - time_flow.sol(flight_time - time_step)
    ) / (2.0 * time_step)
    time_tangent_exact = field(
        np.array([flight_time]), endpoint_center.reshape(4, 1)
    )[:, 0]
    diagnostics = {
        "source_provider_unique_evaluations": int(
            getattr(provider, "unique_evaluations", 0)
        ),
        "phase_tangent_crosscheck_relative": float(
            np.linalg.norm(
                endpoint_tangent_variational - endpoint_tangent_richardson
            )
            / np.linalg.norm(endpoint_tangent_richardson)
        ),
        "phase_finite_difference_refinement_relative": float(
            np.linalg.norm(endpoint_tangent_half - endpoint_tangent_step)
            / np.linalg.norm(endpoint_tangent_richardson)
        ),
        "time_tangent_crosscheck_relative": float(
            np.linalg.norm(time_tangent_exact - time_tangent_fd)
            / np.linalg.norm(time_tangent_exact)
        ),
    }
    arrays = {
        "source_state": source_center,
        "source_phase_tangent_initial": source_tangent_richardson,
        "central_endpoint_recomputed": endpoint_center,
        "source_phase_tangent_variational": endpoint_tangent_variational,
        "source_phase_tangent_finite_difference": endpoint_tangent_richardson,
        "time_tangent_exact": time_tangent_exact,
        "time_tangent_finite_difference": time_tangent_fd,
    }
    return diagnostics, arrays


def compute_endpoint_exchange(
    configuration_path: Path = DEFAULT_CONFIG,
) -> tuple[dict[str, Any], dict[str, Array]]:
    configuration = _load_configuration(configuration_path)
    parameters = OuterParameters(r=3.0 / 200.0, a2=0.0, epsilon=1.0)
    centerline_report = json.loads(
        _bound_path(
            configuration, "ENERGY_PRESERVING_MATCHED_CENTERLINE_REPORT"
        ).read_text(encoding="utf-8")
    )
    graph_report = json.loads(
        _bound_path(configuration, "V4_GRAPH_SLICE_REPORT").read_text(
            encoding="utf-8"
        )
    )
    if centerline_report["status"] != (
        "ENERGY_PRESERVING_MATCHED_CENTERLINE_SUCCESS"
    ) or graph_report["status"] != "V4_FUTURE_GRAPH_SLICE_COMPUTED":
        raise EndpointExchangeError("bound numerical inputs are not QA successes")
    centerline = np.load(
        _bound_path(configuration, "ENERGY_PRESERVING_MATCHED_CENTERLINE_DATA")
    )
    graph = np.load(_bound_path(configuration, "V4_GRAPH_SLICE_DATA"))
    source_configuration = json.loads(
        _bound_path(configuration, "P2E_SOURCE_CONVENTION").read_text(
            encoding="utf-8"
        )
    )
    sections = configuration["sections_and_clocks"]
    section_m = float(sections["M"])
    outer_r1 = float(sections["outer_r1"])
    energy_h = float(centerline_report["energy_h"])

    beta = np.asarray(graph["collocation_beta"][-1, :, 0], dtype=np.float64)
    alpha = np.asarray(graph["collocation_alpha"][-1, :, 0], dtype=np.float64)
    center_index = int(configuration["endpoint_row"]["center_beta_index"])
    polynomial = np.polyfit(beta - beta[center_index], alpha, 2)
    gamma_beta = float(polynomial[1])
    energy_diagnostics, energy_arrays = _outer_graph_energy_sensitivity(
        configuration,
        parameters,
        beta_center=float(beta[center_index]),
        energy_h=energy_h,
    )
    gamma_h = float(energy_diagnostics["Gamma_H"])
    outer_row = np.array(
        [
            -gamma_beta / parameters.delta,
            1.0 / parameters.delta,
            -gamma_h,
        ],
        dtype=np.float64,
    )
    graph_beta_tangent = np.array(
        [1.0, gamma_beta, 0.0], dtype=np.float64
    )
    graph_energy_tangent = np.array(
        [0.0, parameters.delta * gamma_h, 1.0], dtype=np.float64
    )

    # V5(49)--(50): this six-dimensional endpoint pairing is a separate
    # compatibility check.  In particular, it must not be substituted for
    # the directed Jost exchange computed below.
    q_plus = 2.0 / (np.sqrt(3.0) * parameters.epsilon**0.25)
    ell_plus = np.array(
        [
            0.0,
            -np.sqrt(2.0 / 3.0),
            np.sqrt(2.0) * parameters.epsilon**0.25,
            -1.0,
            0.0,
            0.0,
        ],
        dtype=np.float64,
    )
    incoming_tangent_plus = np.array(
        [0.0, 1.0, q_plus / 2.0, 0.0, 0.0, 0.0], dtype=np.float64
    )
    endpoint_compatibility = float(ell_plus @ incoming_tangent_plus)

    k1_r1 = np.asarray(centerline["k1_r1"], dtype=np.float64)
    k1_state = np.asarray(
        centerline["k1_state_Pi_Omega_q1"][:2], dtype=np.float64
    )
    q1_endpoint = float(centerline["k1_state_Pi_Omega_q1"][2, -1])
    outer_jacobian = _outer_map_jacobian_full_exact(
        np.array([k1_state[0, -1], k1_state[1, -1], energy_h]),
        parameters,
        outer_r1=outer_r1,
        q1=q1_endpoint,
    )
    outer_steps_data = configuration["differentiation"]["outer_map_steps"]
    outer_steps = np.array(
        [outer_steps_data["Pi"], outer_steps_data["Omega"]], dtype=np.float64
    )
    outer_jacobian_fd_fixed_energy = _central_difference_jacobian(
        lambda state: resolved_k1_to_outer_normal(
            state, parameters, outer_r1=outer_r1, energy_h=energy_h
        ),
        k1_state[:, -1],
        outer_steps,
    )
    outer_jacobian_fd = np.array(outer_jacobian, copy=True)
    outer_jacobian_fd[:2, :2] = outer_jacobian_fd_fixed_energy
    outer_energy_step = float(
        configuration["full_energy_extension"][
            "graph_finite_difference_H_step"
        ]
    )
    outer_plus = resolved_k1_to_outer_normal(
        k1_state[:, -1],
        parameters,
        outer_r1=outer_r1,
        energy_h=energy_h + outer_energy_step,
    )
    outer_minus = resolved_k1_to_outer_normal(
        k1_state[:, -1],
        parameters,
        outer_r1=outer_r1,
        energy_h=energy_h - outer_energy_step,
    )
    outer_jacobian_fd[:2, 2] = (
        outer_plus - outer_minus
    ) / (2.0 * outer_energy_step)
    k1_endpoint_row = outer_row @ outer_jacobian

    k1_steps_data = configuration["differentiation"]["K1_rhs_steps"]
    k1_steps = np.array(
        [k1_steps_data["Pi"], k1_steps_data["Omega"]], dtype=np.float64
    )
    extension = configuration["full_energy_extension"]
    (
        jacobian_spline,
        jacobian_samples,
        k1_base_residual,
        k1_energy_column_error,
    ) = _k1_full_jacobian_spline(
        k1_r1,
        k1_state,
        parameters,
        energy_h=energy_h,
        state_steps=k1_steps,
        energy_step=float(extension["K1_H_jacobian_step"]),
        energy_half_step=float(extension["K1_H_jacobian_half_step"]),
    )
    adjoint_diagnostics, adjoint_arrays = _projective_adjoint_full(
        configuration, k1_r1, k1_endpoint_row, jacobian_spline
    )
    k1_central_unit_row = adjoint_arrays["adjoint_unit_row"][:, -1]

    # Exact fixed-U derivative of V5(38), augmented by dH from V5(28).
    sigma_c = section_m**-0.5
    central_section_jacobian = np.zeros((3, 4), dtype=np.float64)
    central_section_jacobian[0, 1] = (
        -sigma_c * parameters.epsilon ** (-0.25)
    )
    central_section_jacobian[1, 2] = sigma_c**2
    central_endpoint = np.asarray(centerline["central_state"][:, -1])
    central_u, central_p, central_v, central_q = (
        float(value) for value in central_endpoint
    )
    sqrt_epsilon = np.sqrt(parameters.epsilon)
    c_parameter = 2.0 * parameters.r * parameters.a2 + (
        sqrt_epsilon * parameters.r**4 * parameters.a2**2
    )
    quadratic = 1.0 + sqrt_epsilon * parameters.r**3 * parameters.a2
    central_section_jacobian[2] = np.array(
        [
            -central_v
            + c_parameter * central_u
            - quadratic * central_u**2
            + sqrt_epsilon * parameters.r**2 * central_u**3 / 3.0,
            -central_p,
            -central_u,
            central_q,
        ],
        dtype=np.float64,
    )
    central_extension_row = k1_central_unit_row @ central_section_jacobian
    central_field = vdp_field(
        parameters.r, parameters.a2, parameters.epsilon
    )(
        np.array([float(centerline_report["central_flight_time"])]),
        central_endpoint.reshape(4, 1),
    )[:, 0]
    section_speed = float(central_field[0])
    dh = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
    central_intrinsic_unit_row = central_extension_row - (
        float(central_extension_row @ central_field) / section_speed
    ) * dh

    jost_constants, jost_arrays = _jost_basis(
        configuration, section_m=section_m
    )
    frozen_recessive = jost_arrays["jost_recessive"][:, -1]
    frozen_growing = jost_arrays["jost_growing"][:, -1]
    frozen_psi = np.array(
        [
            frozen_recessive[1],
            -frozen_recessive[0],
            -frozen_recessive[3],
            frozen_recessive[2],
        ],
        dtype=np.float64,
    )
    section_psi_vector = frozen_psi.copy()
    section_psi_vector[0] = 0.0
    jost_section_normal = section_psi_vector / float(
        frozen_psi @ section_psi_vector
    )
    normalization_denominator = float(
        central_intrinsic_unit_row @ jost_section_normal
    )
    if normalization_denominator == 0.0:
        raise EndpointExchangeError("endpoint row misses the frozen Jost normal")
    central_jost_row = central_intrinsic_unit_row / normalization_denominator
    positive_exchange = float(central_jost_row @ frozen_growing)
    frozen_exchange = float(jost_constants["frozen_exchange_target"])

    source_diagnostics, source_arrays = _source_tangents(
        configuration,
        parameters,
        phase=float(centerline_report["source_phase"]),
        flight_time=float(centerline_report["central_flight_time"]),
        source_configuration=source_configuration,
    )
    phase_tangent = source_arrays["source_phase_tangent_variational"]
    time_tangent = source_arrays["time_tangent_exact"]
    source_incidence = float(central_jost_row @ phase_tangent)
    phase_section_derivative = float(phase_tangent[0])
    matching_jacobian = np.array(
        [
            [source_incidence, 0.0],
            [phase_section_derivative, section_speed],
        ],
        dtype=np.float64,
    )
    matching_jacobian_fd = np.array(
        [
            [
                float(
                    central_jost_row
                    @ source_arrays["source_phase_tangent_finite_difference"]
                ),
                0.0,
            ],
            [
                float(
                    source_arrays["source_phase_tangent_finite_difference"][0]
                ),
                float(source_arrays["time_tangent_finite_difference"][0]),
            ],
        ],
        dtype=np.float64,
    )
    singular_values = np.linalg.svd(matching_jacobian, compute_uv=False)
    determinant = float(np.linalg.det(matching_jacobian))
    determinant_factor = float(section_speed * source_incidence)
    determinant_relative = abs(determinant - determinant_factor) / max(
        1.0, abs(determinant_factor)
    )
    flow_pairing_relative = abs(float(central_jost_row @ central_field)) / (
        np.linalg.norm(central_jost_row) * np.linalg.norm(central_field)
    )
    frozen_b2b3_error = abs(jost_constants["B2B3"] - 6.0 * np.sqrt(3.0))
    frozen_exchange_error = abs(
        jost_constants["frozen_exchange_formula"] - frozen_exchange
    )
    positive_exchange_relative = abs(positive_exchange - frozen_exchange) / (
        abs(frozen_exchange)
    )
    outer_jacobian_error = float(
        np.max(np.abs(outer_jacobian - outer_jacobian_fd))
    )
    endpoint_graph_pairing = abs(float(outer_row @ graph_beta_tangent))
    endpoint_graph_energy_pairing = abs(
        float(outer_row @ graph_energy_tangent)
    )
    central_endpoint_recompute_error = float(
        np.linalg.norm(
            source_arrays["central_endpoint_recomputed"] - central_endpoint,
            ord=np.inf,
        )
    )
    condition_number = float(singular_values[0] / singular_values[-1])
    thresholds = configuration["qa_thresholds"]
    qa = {
        "frozen_B2B3_identity": frozen_b2b3_error
        <= float(thresholds["frozen_B2B3_identity_abs_upper"]),
        "frozen_exchange_identity": frozen_exchange_error
        <= float(thresholds["frozen_exchange_identity_abs_upper"]),
        "Jost_pairing_conservation": jost_constants["pairing_drift"]
        <= float(thresholds["Jost_pairing_drift_abs_upper"]),
        "outer_map_jacobian_crosscheck": outer_jacobian_error
        <= float(thresholds["outer_map_jacobian_crosscheck_inf_upper"]),
        "graph_energy_sensitivity_boundary": energy_diagnostics[
            "sensitivity_boundary_residual_inf"
        ]
        <= float(
            thresholds["graph_energy_sensitivity_boundary_residual_upper"]
        ),
        "graph_energy_sensitivity_ode": energy_diagnostics[
            "sensitivity_rms_residual_max"
        ]
        <= float(thresholds["graph_energy_sensitivity_ode_residual_upper"]),
        "graph_energy_sensitivity_finite_difference": energy_diagnostics[
            "Gamma_H_finite_difference_relative"
        ]
        <= float(
            thresholds[
                "graph_energy_sensitivity_finite_difference_relative_upper"
            ]
        ),
        "K1_full_jacobian_energy_column": k1_energy_column_error
        <= float(
            thresholds["K1_full_jacobian_energy_column_relative_upper"]
        ),
        "endpoint_graph_tangent_annihilation": endpoint_graph_pairing
        <= float(thresholds["endpoint_graph_tangent_pairing_abs_upper"]),
        "endpoint_graph_energy_tangent_annihilation": (
            endpoint_graph_energy_pairing
            <= float(thresholds["endpoint_graph_tangent_pairing_abs_upper"])
        ),
        "adjoint_projective_crosscheck": adjoint_diagnostics[
            "direction_crosscheck_max"
        ]
        <= float(
            thresholds["full_adjoint_projective_ratio_difference_upper"]
        ),
        "intrinsic_row_annihilates_flow": flow_pairing_relative
        <= float(thresholds["intrinsic_flow_pairing_relative_upper"]),
        "positive_exchange": positive_exchange
        >= float(thresholds["positive_exchange_lower"]),
        "exchange_near_frozen_comparison": positive_exchange_relative
        <= float(
            thresholds["positive_exchange_relative_deviation_from_frozen_upper"]
        ),
        "source_tangent_crosscheck": source_diagnostics[
            "phase_tangent_crosscheck_relative"
        ]
        <= float(thresholds["source_tangent_crosscheck_relative_upper"]),
        "time_tangent_crosscheck": source_diagnostics[
            "time_tangent_crosscheck_relative"
        ]
        <= float(thresholds["time_tangent_crosscheck_relative_upper"]),
        "source_phase_incidence_nonzero": abs(source_incidence)
        >= float(thresholds["source_phase_incidence_abs_lower"]),
        "central_section_transverse": abs(section_speed)
        >= float(thresholds["central_section_speed_abs_lower"]),
        "determinant_factorization": determinant_relative
        <= float(thresholds["determinant_factorization_relative_upper"]),
        "matching_sigma_min": singular_values[-1]
        >= float(thresholds["matching_sigma_min_lower"]),
        "matching_condition_number": condition_number
        <= float(thresholds["matching_condition_number_upper"]),
    }
    qa = {key: bool(value) for key, value in qa.items()}
    all_passed = all(qa.values())
    diagnostics = {
        "gamma_beta_at_outer_seam": gamma_beta,
        "gamma_H_at_outer_seam": gamma_h,
        "outer_graph_energy_sensitivity": energy_diagnostics,
        "endpoint_graph_tangent_pairing_abs": endpoint_graph_pairing,
        "endpoint_graph_energy_tangent_pairing_abs": (
            endpoint_graph_energy_pairing
        ),
        "outer_map_jacobian_crosscheck_inf": outer_jacobian_error,
        "K1_saved_base_invariance_residual_inf": k1_base_residual,
        "K1_full_jacobian_energy_column_relative_error": (
            k1_energy_column_error
        ),
        "adjoint": adjoint_diagnostics,
        "central_intrinsic_flow_pairing_relative": flow_pairing_relative,
        "Jost_normalization_denominator": normalization_denominator,
        "Jost_row_on_section_normal": float(
            central_jost_row @ jost_section_normal
        ),
        "Jost_row_frozen_row_cosine": float(
            central_jost_row
            @ frozen_psi
            / (np.linalg.norm(central_jost_row) * np.linalg.norm(frozen_psi))
        ),
        "frozen_B2B3_identity_error": frozen_b2b3_error,
        "frozen_exchange_identity_error": frozen_exchange_error,
        "frozen_Jost_pairing_drift": jost_constants["pairing_drift"],
        "frozen_exchange": frozen_exchange,
        "positive_exchange": positive_exchange,
        "positive_exchange_relative_deviation": positive_exchange_relative,
        "source": source_diagnostics,
        "central_endpoint_recompute_residual_inf": central_endpoint_recompute_error,
        "source_phase_incidence": source_incidence,
        "central_section_speed": section_speed,
        "phase_section_derivative": phase_section_derivative,
        "matching_determinant": determinant,
        "matching_section_speed_times_incidence": determinant_factor,
        "determinant_factorization_relative": determinant_relative,
        "matching_singular_values": singular_values.tolist(),
        "matching_condition_number": condition_number,
        "matching_jacobian_crosscheck_inf": float(
            np.max(np.abs(matching_jacobian - matching_jacobian_fd))
        ),
        "endpoint_compatibility_ell_plus_T_plus": endpoint_compatibility,
        "endpoint_compatibility_interpretation": (
            "The vanishing V5(50) is checked separately and is not the "
            "exchange coefficient."
        ),
    }
    report = {
        "schema_version": "rfsn-vdp-v5-endpoint-exchange-v2/1",
        "status": (
            "V5_ENDPOINT_EXCHANGE_COMPUTED"
            if all_passed
            else "V5_ENDPOINT_EXCHANGE_QA_REJECTED"
        ),
        "evidence_status": "COMPUTED/E1_NON_RIGOROUS_WITH_QA",
        "mathematical_status": "INCONCLUSIVE",
        "claim_bearing": False,
        "parameter_point": configuration["parameter_point"],
        "source_phase": float(centerline_report["source_phase"]),
        "central_flight_time": float(centerline_report["central_flight_time"]),
        "energy_H": energy_h,
        "normalization": configuration["jost_normalization"],
        "sections_and_clocks": sections,
        "diagnostics": diagnostics,
        "thresholds": thresholds,
        "qa": qa,
        "nonclaim": (
            "One full-energy endpoint-anchored adjoint line for the finite-"
            "Q graph proxy, one Jost-normalized exchange candidate, and one "
            "two-by-two matching derivative at the center do not prove a "
            "uniform positive exchange, operator inverse bound, maximal-graph "
            "identification, matched-tube uniqueness, or the Issue #7 "
            "parameter-box theorem."
        ),
    }
    arrays = {
        "outer_seam_beta": beta,
        "outer_seam_alpha": alpha,
        "outer_graph_tangent": graph_beta_tangent,
        "outer_graph_beta_tangent": graph_beta_tangent,
        "outer_graph_energy_tangent": graph_energy_tangent,
        "outer_raw_row_beta_alpha_H": outer_row,
        "endpoint_left_row_ell_plus": ell_plus,
        "endpoint_incoming_tangent_T_plus": incoming_tangent_plus,
        "outer_map_jacobian_exact": outer_jacobian,
        "outer_map_jacobian_finite_difference": outer_jacobian_fd,
        "K1_endpoint_raw_row": k1_endpoint_row,
        "K1_r1": k1_r1,
        "K1_state_Pi_Omega": k1_state,
        "K1_jacobian_samples": jacobian_samples,
        "central_section_jacobian": central_section_jacobian,
        "central_intrinsic_unit_row": central_intrinsic_unit_row,
        "frozen_Jost_row": frozen_psi,
        "frozen_growing_complement": frozen_growing,
        "Jost_section_normal": jost_section_normal,
        "positive_Jost_row": central_jost_row,
        "matching_jacobian": matching_jacobian,
        "matching_jacobian_finite_difference": matching_jacobian_fd,
        "matching_singular_values": singular_values,
        **energy_arrays,
        **adjoint_arrays,
        **jost_arrays,
        **source_arrays,
    }
    if not all_passed:
        raise EndpointExchangeError(
            "predeclared endpoint-exchange QA failed: "
            + ", ".join(key for key, passed in qa.items() if not passed)
        )
    return report, arrays


def _write_failure(error: Exception) -> None:
    DEFAULT_RESULT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_RESULT.write_text(
        json.dumps(
            {
                "schema_version": "rfsn-vdp-v5-endpoint-exchange-v2/1",
                "status": "V5_ENDPOINT_EXCHANGE_FAILED",
                "evidence_status": "COMPUTED/E1_FAILED",
                "mathematical_status": "INCONCLUSIVE",
                "claim_bearing": False,
                "failure_type": type(error).__name__,
                "failure_reason": str(error),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    try:
        report, arrays = compute_endpoint_exchange(DEFAULT_CONFIG)
    except Exception as error:
        _write_failure(error)
        raise
    DEFAULT_RESULT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(DEFAULT_DATA, **arrays)
    report["configuration_path"] = str(DEFAULT_CONFIG.relative_to(REPOSITORY))
    report["data_path"] = str(DEFAULT_DATA.relative_to(REPOSITORY))
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
