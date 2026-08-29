"""Floating V5 endpoint adjoint, exchange, and matching Jacobian.

The computation is tied to the energy-preserving matched centerline and the
three-beta V4 graph slice at ``(r,a2,epsilon)=(3/200,0,1)``.  It uses the
normalizations and clocks of V5(37), V5(51)--(58).  The result is one E1/QA
object, never a uniform exchange or nonlinear uniqueness proof.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline
from scipy.special import gamma

from numerics.rfsn_numerics import vdp_field
from numerics.vdp_matched_outer import (
    resolved_k1_rhs_r1,
    resolved_k1_to_outer_normal,
)
from numerics.vdp_outer import OuterParameters
from numerics.vdp_p2e_channel_scout import _direct_kato_provider


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


def _k1_jacobian_spline(
    r1: Array,
    state: Array,
    parameters: OuterParameters,
    *,
    energy_h: float,
    steps: Array,
) -> tuple[CubicSpline, Array, float]:
    state_spline = CubicSpline(r1, state, axis=1)

    def rhs(coordinate: float, value: Array) -> Array:
        return resolved_k1_rhs_r1(
            np.array([coordinate]),
            value.reshape(2, 1),
            parameters,
            energy_h=energy_h,
        )[:, 0]

    jacobian = np.empty((r1.size, 2, 2), dtype=np.float64)
    base_residual = []
    for index, coordinate in enumerate(r1):
        value = state[:, index]
        jacobian[index] = _central_difference_jacobian(
            lambda candidate: rhs(float(coordinate), candidate), value, steps
        )
        base_residual.append(
            np.linalg.norm(
                state_spline(float(coordinate), 1)
                - rhs(float(coordinate), value),
                ord=np.inf,
            )
        )
    return (
        CubicSpline(r1, jacobian, axis=0),
        jacobian,
        float(max(base_residual)),
    )


def _projective_adjoint(
    configuration: dict[str, Any],
    r1: Array,
    endpoint_row: Array,
    jacobian_spline: CubicSpline,
) -> tuple[dict[str, float], dict[str, Array]]:
    options = configuration["integration"]
    norm = float(np.linalg.norm(endpoint_row))
    initial_direction = endpoint_row / norm

    def normalized_rhs(coordinate: float, state: Array) -> Array:
        direction = state[:2]
        raw = -direction @ jacobian_spline(coordinate)
        rate = float(direction @ raw)
        return np.array(
            [raw[0] - rate * direction[0], raw[1] - rate * direction[1], rate],
            dtype=np.float64,
        )

    normalized = solve_ivp(
        normalized_rhs,
        (float(r1[-1]), float(r1[0])),
        np.array(
            [initial_direction[0], initial_direction[1], np.log(norm)],
            dtype=np.float64,
        ),
        method=str(options["method"]),
        rtol=float(options["K1_rtol"]),
        atol=float(options["K1_atol"]),
        max_step=float(options["K1_max_step"]),
        dense_output=True,
    )
    if not normalized.success or normalized.sol is None:
        raise EndpointExchangeError(
            f"normalized backward adjoint failed: {normalized.message}"
        )

    initial_angle = float(
        np.arctan2(initial_direction[1], initial_direction[0])
    )

    def angle_rhs(coordinate: float, state: Array) -> Array:
        angle = float(state[0])
        direction = np.array([np.cos(angle), np.sin(angle)], dtype=np.float64)
        perpendicular = np.array(
            [-direction[1], direction[0]], dtype=np.float64
        )
        raw = -direction @ jacobian_spline(coordinate)
        return np.array(
            [perpendicular @ raw, direction @ raw], dtype=np.float64
        )

    angle = solve_ivp(
        angle_rhs,
        (float(r1[-1]), float(r1[0])),
        np.array([initial_angle, np.log(norm)], dtype=np.float64),
        method=str(options["method"]),
        rtol=float(options["K1_rtol"]),
        atol=float(options["K1_atol"]),
        max_step=float(options["K1_max_step"]),
        dense_output=True,
    )
    if not angle.success or angle.sol is None:
        raise EndpointExchangeError(
            f"angle backward adjoint failed: {angle.message}"
        )
    reversed_r1 = r1[::-1]
    normalized_values = np.asarray(normalized.sol(reversed_r1), dtype=np.float64)
    angle_values = np.asarray(angle.sol(reversed_r1), dtype=np.float64)
    angle_direction = np.vstack(
        (np.cos(angle_values[0]), np.sin(angle_values[0]))
    )
    dot = np.sum(normalized_values[:2] * angle_direction, axis=0)
    signs = np.where(dot < 0.0, -1.0, 1.0)
    angle_direction *= signs
    direction_difference = np.linalg.norm(
        normalized_values[:2] - angle_direction, axis=0
    )
    diagnostics = {
        "normalized_solver_evaluations": int(normalized.nfev),
        "angle_solver_evaluations": int(angle.nfev),
        "direction_crosscheck_max": float(np.max(direction_difference)),
        "log_scale_crosscheck_max": float(
            np.max(np.abs(normalized_values[2] - angle_values[1]))
        ),
        "central_log_raw_row_norm": float(normalized_values[2, -1]),
        "central_direction_norm_defect": float(
            abs(np.linalg.norm(normalized_values[:2, -1]) - 1.0)
        ),
    }
    arrays = {
        "adjoint_r1_descending": reversed_r1,
        "adjoint_unit_row": normalized_values[:2],
        "adjoint_log_raw_norm": normalized_values[2],
        "adjoint_angle_unit_row": angle_direction,
        "adjoint_angle_log_raw_norm": angle_values[1],
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
    outer_row = np.array(
        [-gamma_beta / parameters.delta, 1.0 / parameters.delta],
        dtype=np.float64,
    )
    graph_tangent = np.array([1.0, gamma_beta], dtype=np.float64)

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
    outer_jacobian = _outer_map_jacobian_exact(
        k1_state[:, -1],
        parameters,
        outer_r1=outer_r1,
        q1=q1_endpoint,
    )
    outer_steps_data = configuration["differentiation"]["outer_map_steps"]
    outer_steps = np.array(
        [outer_steps_data["Pi"], outer_steps_data["Omega"]], dtype=np.float64
    )
    outer_jacobian_fd = _central_difference_jacobian(
        lambda state: resolved_k1_to_outer_normal(
            state,
            parameters,
            outer_r1=outer_r1,
            energy_h=energy_h,
        ),
        k1_state[:, -1],
        outer_steps,
    )
    k1_endpoint_row = outer_row @ outer_jacobian

    k1_steps_data = configuration["differentiation"]["K1_rhs_steps"]
    k1_steps = np.array(
        [k1_steps_data["Pi"], k1_steps_data["Omega"]], dtype=np.float64
    )
    jacobian_spline, jacobian_samples, k1_base_residual = _k1_jacobian_spline(
        k1_r1,
        k1_state,
        parameters,
        energy_h=energy_h,
        steps=k1_steps,
    )
    adjoint_diagnostics, adjoint_arrays = _projective_adjoint(
        configuration, k1_r1, k1_endpoint_row, jacobian_spline
    )
    k1_central_unit_row = adjoint_arrays["adjoint_unit_row"][:, -1]

    # Exact fixed-U derivative of V5(38) at U=-M, epsilon=1.
    sigma_c = section_m**-0.5
    central_section_jacobian = np.zeros((2, 4), dtype=np.float64)
    central_section_jacobian[0, 1] = (
        -sigma_c * parameters.epsilon ** (-0.25)
    )
    central_section_jacobian[1, 2] = sigma_c**2
    central_extension_row = k1_central_unit_row @ central_section_jacobian
    central_endpoint = np.asarray(centerline["central_state"][:, -1])
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
    endpoint_graph_pairing = abs(float(outer_row @ graph_tangent))
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
        "endpoint_graph_tangent_annihilation": endpoint_graph_pairing
        <= float(thresholds["endpoint_graph_tangent_pairing_abs_upper"]),
        "adjoint_projective_crosscheck": adjoint_diagnostics[
            "direction_crosscheck_max"
        ]
        <= float(thresholds["adjoint_projective_angle_difference_upper"]),
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
        "endpoint_graph_tangent_pairing_abs": endpoint_graph_pairing,
        "outer_map_jacobian_crosscheck_inf": outer_jacobian_error,
        "K1_saved_base_invariance_residual_inf": k1_base_residual,
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
            "One endpoint-anchored adjoint line, Jost-normalized exchange, "
            "and two-by-two matching derivative at the center do not prove "
            "a uniform positive exchange, operator inverse bound, matched-tube "
            "uniqueness, or the Issue #7 parameter-box theorem."
        ),
    }
    arrays = {
        "outer_seam_beta": beta,
        "outer_seam_alpha": alpha,
        "outer_graph_tangent": graph_tangent,
        "outer_raw_row_beta_alpha": outer_row,
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
