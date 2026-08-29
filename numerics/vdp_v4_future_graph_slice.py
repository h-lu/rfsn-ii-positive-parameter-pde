"""One floating-point V4 future-staying graph slice at the v2 center.

The selected object is the zero-energy slice ``alpha=Gamma(z,beta)`` at
``(r,a2,epsilon)=(3/200,0,1)`` through the previously computed matched
centerline seam.  Two independent numerical formulations are compared:

* positive-``pi`` horizon collocation on a frozen ``Q_end`` ladder; and
* positive-``pi`` initial-alpha shooting across a short, stiff outer window.

Both formulations use the exact normal nullcline ``alpha_dot=0`` as an
asymptotically compatible terminal condition.  This removes the older
artificial condition ``alpha(Q_end)=0``, but it does not turn a finite floating
calculation into the maximal V4 graph or an Issue #7 interval proof.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_bvp, solve_ivp
from scipy.optimize import brentq

from numerics.vdp_matched_outer import _positive_pi_bvp_grid
from numerics.vdp_outer import (
    OuterParameters,
    energy_equation_residual,
    normal_to_positive_pi_state,
    normal_outer_state,
    positive_pi_outer_rhs_q,
    positive_pi_outer_state,
)


Array = NDArray[np.float64]
HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent
DEFAULT_CONFIG = HERE / "config/vdp_v4_future_graph_slice_v2.json"
DEFAULT_RESULT = HERE / "results/vdp_v4_future_graph_slice_v2/result.json"
DEFAULT_DATA = HERE / "results/vdp_v4_future_graph_slice_v2/slice.npz"


class GraphSliceError(RuntimeError):
    """The frozen floating-point construction or its QA failed."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_configuration(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    binding = data["matched_centerline_binding"]
    for path_key, hash_key in (
        ("report_path", "report_sha256"),
        ("data_path", "data_sha256"),
    ):
        bound_path = REPOSITORY / binding[path_key]
        actual = _sha256(bound_path)
        if actual != binding[hash_key]:
            raise GraphSliceError(
                f"matched-centerline binding changed: {binding[path_key]}"
            )
    archive = np.load(REPOSITORY / binding["data_path"])
    seam_q = float(archive["outer_Q"][0])
    seam_beta = float(archive["outer_state_beta_alpha"][0, 0])
    if not np.isclose(
        seam_q, float(binding["seam_Q"]), rtol=0.0, atol=8.0 * np.spacing(25.0)
    ):
        raise GraphSliceError("bound seam Q does not match the raw centerline")
    if seam_beta != float(binding["seam_beta_center"]):
        raise GraphSliceError("bound seam beta does not match the raw centerline")
    return data


def _tau_field(
    state: Array,
    parameters: OuterParameters,
    *,
    energy: float,
) -> Array:
    """Exact fixed-energy V4 field in state order ``(z,beta,alpha)``."""

    z, beta, alpha = (float(value) for value in state)
    chi, pi, w = normal_outer_state(
        np.array([z]),
        np.array([beta]),
        np.array([alpha]),
        parameters,
        energy=energy,
    )
    chi_value = float(chi[0])
    pi_value = float(pi[0])
    w_value = float(w[0])
    delta = parameters.delta
    common = (
        -delta * delta * parameters.epsilon * (1.0 - parameters.a * z)
        + 2.0 * delta * chi_value * pi_value
    )
    z_dot = -pi_value * z**3
    beta_dot = -beta + 0.5 * z * z * (
        common + pi_value + pi_value * w_value
    )
    alpha_dot = alpha + 0.5 * z * z * (
        common - pi_value - pi_value * w_value
    )
    return np.array([z_dot, beta_dot, alpha_dot], dtype=np.float64)


def normal_nullcline_alpha(
    compact_q: float,
    beta: float,
    parameters: OuterParameters,
    *,
    energy: float,
    alpha_half_width: float,
) -> float:
    """Root of the exact normal equation ``alpha_dot=0`` in a fixed collar."""

    z = float(compact_q) ** -0.5

    def residual(alpha: float) -> float:
        return float(
            _tau_field(
                np.array([z, beta, alpha], dtype=np.float64),
                parameters,
                energy=energy,
            )[2]
        )

    lower = -float(alpha_half_width)
    upper = float(alpha_half_width)
    lower_value = residual(lower)
    upper_value = residual(upper)
    if not lower_value < 0.0 < upper_value:
        raise GraphSliceError(
            "the exact normal nullcline is not bracketed in the frozen collar"
        )
    return float(
        brentq(
            residual,
            lower,
            upper,
            xtol=1.0e-18,
            rtol=1.0e-14,
            maxiter=80,
        )
    )


def _normal_values(
    compact_q: Array,
    positive_state: Array,
    parameters: OuterParameters,
    *,
    energy: float,
) -> tuple[Array, Array, Array, Array]:
    beta, alpha, chi, pi, _w = positive_pi_outer_state(
        compact_q, positive_state, parameters, energy=energy
    )
    return (
        np.asarray(beta, dtype=np.float64),
        np.asarray(alpha, dtype=np.float64),
        np.asarray(chi, dtype=np.float64),
        np.asarray(pi, dtype=np.float64),
    )


def _solve_collocation_ladder(
    configuration: dict[str, Any],
    parameters: OuterParameters,
    beta_values: Array,
    *,
    energy: float,
    evaluation_q: Array,
) -> tuple[dict[tuple[float, float], Any], list[dict[str, Any]]]:
    q_start = float(configuration["matched_centerline_binding"]["seam_Q"])
    options = configuration["collocation_construction"]
    alpha_half_width = float(
        configuration["sampled_corridor"]["alpha_half_width"]
    )
    solutions: dict[tuple[float, float], Any] = {}
    diagnostics: list[dict[str, Any]] = []
    for q_end_raw in configuration["slice"]["collocation_Q_end_ladder"]:
        q_end = float(q_end_raw)
        mesh = _positive_pi_bvp_grid(
            q_start,
            q_end,
            int(options["mesh_base_points"]),
            parameters.delta,
        )
        previous = None
        previous_beta = 0.0
        for beta0_raw in beta_values:
            beta0 = float(beta0_raw)
            if previous is None:
                beta_guess = beta0 * np.exp(
                    np.maximum(
                        parameters.stable_rate_q * (mesh - q_start), -700.0
                    )
                )
                alpha_guess = np.array(
                    [
                        normal_nullcline_alpha(
                            float(q),
                            float(beta),
                            parameters,
                            energy=energy,
                            alpha_half_width=alpha_half_width,
                        )
                        for q, beta in zip(mesh, beta_guess, strict=True)
                    ],
                    dtype=np.float64,
                )
                predictor_normal = np.vstack((beta_guess, alpha_guess))
            else:
                previous_normal = positive_pi_outer_state(
                    mesh, previous.sol(mesh), parameters, energy=energy
                )[:2]
                predictor_normal = np.vstack(previous_normal)
                predictor_normal[0] += (beta0 - previous_beta) * np.exp(
                    np.maximum(
                        parameters.stable_rate_q * (mesh - q_start), -700.0
                    )
                )
            predictor = normal_to_positive_pi_state(
                mesh, predictor_normal, parameters, energy=energy
            )

            def boundary(left: Array, right: Array) -> Array:
                left_beta = float(
                    positive_pi_outer_state(
                        q_start, left, parameters, energy=energy
                    )[0]
                )
                right_beta, right_alpha = positive_pi_outer_state(
                    q_end, right, parameters, energy=energy
                )[:2]
                terminal = normal_nullcline_alpha(
                    q_end,
                    float(right_beta),
                    parameters,
                    energy=energy,
                    alpha_half_width=alpha_half_width,
                )
                return np.array(
                    [
                        (left_beta - beta0) / parameters.delta,
                        (float(right_alpha) - terminal) / parameters.delta,
                    ],
                    dtype=np.float64,
                )

            solution = solve_bvp(
                lambda coordinate, state: positive_pi_outer_rhs_q(
                    coordinate, state, parameters, energy=energy
                ),
                boundary,
                mesh,
                predictor,
                tol=float(options["tolerance"]),
                bc_tol=float(options["boundary_tolerance"]),
                max_nodes=int(options["maximum_nodes"]),
                verbose=0,
            )
            if not solution.success:
                raise GraphSliceError(
                    f"collocation failed at Q_end={q_end}, beta0={beta0}: "
                    f"{solution.message}"
                )
            # Audit the complete adaptive collocation mesh, not only the
            # near-seam cuts used for comparison with short-window shooting.
            check_q = np.asarray(solution.x, dtype=np.float64)
            beta, alpha, chi, pi = _normal_values(
                check_q, solution.sol(check_q), parameters, energy=energy
            )
            energy_residual = energy_equation_residual(
                check_q**-0.5,
                beta,
                alpha,
                chi,
                parameters,
                energy=energy,
            )
            boundary_residual = boundary(
                solution.sol(q_start), solution.sol(q_end)
            )
            terminal_beta, terminal_alpha = positive_pi_outer_state(
                q_end, solution.sol(q_end), parameters, energy=energy
            )[:2]
            terminal_nullcline = normal_nullcline_alpha(
                q_end,
                float(terminal_beta),
                parameters,
                energy=energy,
                alpha_half_width=alpha_half_width,
            )
            diagnostics.append(
                {
                    "Q_end": q_end,
                    "beta0": beta0,
                    "solver_nodes": int(solution.x.size),
                    "solver_rms_residual_max": float(
                        np.max(solution.rms_residuals)
                    ),
                    "boundary_residual_inf": float(
                        np.max(np.abs(boundary_residual))
                    ),
                    "energy_residual_inf": float(
                        np.max(np.abs(energy_residual))
                    ),
                    "minimum_pi": float(np.min(pi)),
                    "terminal_beta": float(terminal_beta),
                    "terminal_alpha": float(terminal_alpha),
                    "terminal_nullcline_alpha": terminal_nullcline,
                    "terminal_nullcline_residual": float(
                        terminal_alpha - terminal_nullcline
                    ),
                }
            )
            solutions[(q_end, beta0)] = solution
            previous = solution
            previous_beta = beta0
    return solutions, diagnostics


def _shoot_one(
    configuration: dict[str, Any],
    parameters: OuterParameters,
    beta0: float,
    *,
    energy: float,
    evaluation_q: Array,
) -> tuple[Any, float, dict[str, Any]]:
    q_start = float(configuration["matched_centerline_binding"]["seam_Q"])
    options = configuration["shooting_construction"]
    q_end = float(options["Q_end"])
    alpha_half_width = float(
        configuration["sampled_corridor"]["alpha_half_width"]
    )
    nullcline_start = normal_nullcline_alpha(
        q_start,
        beta0,
        parameters,
        energy=energy,
        alpha_half_width=alpha_half_width,
    )

    def integrate(alpha0: float, dense_output: bool) -> Any:
        initial = normal_to_positive_pi_state(
            q_start,
            np.array([beta0, alpha0], dtype=np.float64),
            parameters,
            energy=energy,
        )
        integration = solve_ivp(
            lambda coordinate, state: positive_pi_outer_rhs_q(
                np.array([coordinate]),
                state.reshape(2, 1),
                parameters,
                energy=energy,
            )[:, 0],
            (q_start, q_end),
            initial,
            method=str(options["integrator"]),
            rtol=float(options["rtol"]),
            atol=float(options["atol"]),
            max_step=float(options["maximum_Q_step"]),
            dense_output=dense_output,
        )
        if not integration.success:
            raise GraphSliceError(
                f"shooting IVP failed at beta0={beta0}: {integration.message}"
            )
        return integration

    evaluations = 0

    def terminal_residual(alpha0: float) -> float:
        nonlocal evaluations
        evaluations += 1
        integration = integrate(alpha0, False)
        beta_end, alpha_end = positive_pi_outer_state(
            q_end, integration.y[:, -1], parameters, energy=energy
        )[:2]
        target = normal_nullcline_alpha(
            q_end,
            float(beta_end),
            parameters,
            energy=energy,
            alpha_half_width=alpha_half_width,
        )
        return float(alpha_end) - target

    half_width = float(options["initial_alpha_bracket_about_nullcline"])
    lower = nullcline_start - half_width
    upper = nullcline_start + half_width
    lower_residual = terminal_residual(lower)
    upper_residual = terminal_residual(upper)
    if not lower_residual < 0.0 < upper_residual:
        raise GraphSliceError(
            f"frozen shooting bracket failed at beta0={beta0}: "
            f"({lower_residual}, {upper_residual})"
        )
    alpha0 = float(
        brentq(
            terminal_residual,
            lower,
            upper,
            xtol=float(options["root_xtol"]),
            rtol=float(options["root_rtol"]),
            maxiter=int(options["root_maximum_iterations"]),
        )
    )
    final = integrate(alpha0, True)
    if final.sol is None:
        raise GraphSliceError("shooting dense output is unavailable")
    beta, alpha, chi, pi = _normal_values(
        evaluation_q, final.sol(evaluation_q), parameters, energy=energy
    )
    terminal = terminal_residual(alpha0)
    energy_residual = energy_equation_residual(
        evaluation_q**-0.5,
        beta,
        alpha,
        chi,
        parameters,
        energy=energy,
    )
    diagnostics = {
        "beta0": beta0,
        "alpha0": alpha0,
        "initial_nullcline_alpha": nullcline_start,
        "initial_alpha_minus_nullcline": alpha0 - nullcline_start,
        "bracket_lower_residual": lower_residual,
        "bracket_upper_residual": upper_residual,
        "terminal_residual": terminal,
        "root_residual_evaluations": evaluations,
        "integrator_steps": int(final.t.size),
        "minimum_pi": float(np.min(pi)),
        "energy_residual_inf": float(np.max(np.abs(energy_residual))),
    }
    return final, alpha0, diagnostics


def _slice_value_at_fixed_beta(
    beta: Array, alpha: Array, target_beta: float
) -> tuple[float, float]:
    centered = beta - target_beta
    coefficients = np.polyfit(centered, alpha, 2)
    return float(coefficients[2]), float(coefficients[1])


def _jacobian(
    state: Array,
    parameters: OuterParameters,
    *,
    energy: float,
    steps: Array,
) -> Array:
    jacobian = np.empty((3, 3), dtype=np.float64)
    for column, step in enumerate(steps):
        plus = state.copy()
        minus = state.copy()
        plus[column] += step
        minus[column] -= step
        jacobian[:, column] = (
            _tau_field(plus, parameters, energy=energy)
            - _tau_field(minus, parameters, energy=energy)
        ) / (2.0 * step)
    return jacobian


def _rate_proxies(
    configuration: dict[str, Any],
    parameters: OuterParameters,
    beta_values: Array,
    selected_solutions: list[Any],
    *,
    energy: float,
) -> dict[str, Array]:
    cuts = np.asarray(configuration["slice"]["rate_Q_cuts"], dtype=np.float64)
    q_step = float(configuration["slice"]["rate_Q_difference_step"])
    step_data = configuration["slice"]["jacobian_central_difference_steps"]
    jacobian_steps = np.array(
        [step_data["z"], step_data["beta"], step_data["alpha"]],
        dtype=np.float64,
    )
    gamma_beta_values = []
    gamma_z_values = []
    invariance_values = []
    tangent_values = []
    normal_values = []
    bunching_values = []
    beta_separation_values = []
    for compact_q in cuts:
        center_beta, center_alpha = _normal_values(
            np.array([compact_q]),
            selected_solutions[1].sol(np.array([compact_q])),
            parameters,
            energy=energy,
        )[:2]
        target_beta = float(center_beta[0])
        alpha_center = float(center_alpha[0])
        beta_at_cut = []
        alpha_at_cut = []
        for solution in selected_solutions:
            beta, alpha = _normal_values(
                np.array([compact_q]),
                solution.sol(np.array([compact_q])),
                parameters,
                energy=energy,
            )[:2]
            beta_at_cut.append(float(beta[0]))
            alpha_at_cut.append(float(alpha[0]))
        beta_array = np.asarray(beta_at_cut, dtype=np.float64)
        alpha_array = np.asarray(alpha_at_cut, dtype=np.float64)
        _gamma, gamma_beta = _slice_value_at_fixed_beta(
            beta_array, alpha_array, target_beta
        )
        fixed_beta_gamma = []
        for shifted_q in (compact_q - q_step, compact_q + q_step):
            shifted_beta = []
            shifted_alpha = []
            for solution in selected_solutions:
                beta, alpha = _normal_values(
                    np.array([shifted_q]),
                    solution.sol(np.array([shifted_q])),
                    parameters,
                    energy=energy,
                )[:2]
                shifted_beta.append(float(beta[0]))
                shifted_alpha.append(float(alpha[0]))
            gamma_value, _slope = _slice_value_at_fixed_beta(
                np.asarray(shifted_beta),
                np.asarray(shifted_alpha),
                target_beta,
            )
            fixed_beta_gamma.append(gamma_value)
        gamma_q = (fixed_beta_gamma[1] - fixed_beta_gamma[0]) / (2.0 * q_step)
        z = float(compact_q**-0.5)
        gamma_z = -2.0 * compact_q**1.5 * gamma_q
        state = np.array([z, target_beta, alpha_center], dtype=np.float64)
        field = _tau_field(state, parameters, energy=energy)
        invariance = field[2] - gamma_z * field[0] - gamma_beta * field[1]
        jacobian = _jacobian(
            state,
            parameters,
            energy=energy,
            steps=jacobian_steps,
        )
        tangent = np.array(
            [[1.0, 0.0], [0.0, 1.0], [gamma_z, gamma_beta]],
            dtype=np.float64,
        )
        orthonormal_tangent, _upper = np.linalg.qr(tangent)
        normal = np.cross(
            orthonormal_tangent[:, 0], orthonormal_tangent[:, 1]
        )
        normal /= np.linalg.norm(normal)
        if normal[2] < 0.0:
            normal *= -1.0
        symmetric = 0.5 * (jacobian + jacobian.T)
        tangent_rate = float(
            np.max(
                np.linalg.eigvalsh(
                    orthonormal_tangent.T
                    @ symmetric
                    @ orthonormal_tangent
                )
            )
        )
        normal_rate = float(normal @ jacobian @ normal)
        bunching = np.array(
            [normal_rate - order * tangent_rate for order in range(4)],
            dtype=np.float64,
        )
        gamma_beta_values.append(gamma_beta)
        gamma_z_values.append(gamma_z)
        invariance_values.append(invariance)
        tangent_values.append(tangent_rate)
        normal_values.append(normal_rate)
        bunching_values.append(bunching)
        beta_separation_values.append(float(np.ptp(beta_array)))
    return {
        "rate_Q": cuts,
        "rate_gamma_beta": np.asarray(gamma_beta_values),
        "rate_gamma_z": np.asarray(gamma_z_values),
        "rate_invariance_residual": np.asarray(invariance_values),
        "rate_tangent_log_norm": np.asarray(tangent_values),
        "rate_normal_quotient": np.asarray(normal_values),
        "rate_bunching_gamma_j": np.asarray(bunching_values),
        "rate_beta_slice_separation": np.asarray(beta_separation_values),
    }


def _sampled_face_margins(
    configuration: dict[str, Any],
    parameters: OuterParameters,
    *,
    energy: float,
) -> dict[str, float]:
    corridor = configuration["sampled_corridor"]
    z_values = [float(value) for value in corridor["z_values"]]
    cross_values = [float(value) for value in corridor["cross_values"]]
    beta_face = float(corridor["beta_half_width"])
    alpha_face = float(corridor["alpha_half_width"])
    margins: dict[str, list[float]] = {
        "beta_upper_inward": [],
        "beta_lower_inward": [],
        "alpha_upper_exit": [],
        "alpha_lower_exit": [],
        "z_outer_inward": [],
        "positive_pi": [],
    }
    energy_residuals = []
    for z in z_values:
        for cross in cross_values:
            upper_beta = np.array([z, beta_face, cross], dtype=np.float64)
            lower_beta = np.array([z, -beta_face, cross], dtype=np.float64)
            upper_alpha = np.array([z, cross, alpha_face], dtype=np.float64)
            lower_alpha = np.array([z, cross, -alpha_face], dtype=np.float64)
            margins["beta_upper_inward"].append(
                -float(_tau_field(upper_beta, parameters, energy=energy)[1])
            )
            margins["beta_lower_inward"].append(
                float(_tau_field(lower_beta, parameters, energy=energy)[1])
            )
            margins["alpha_upper_exit"].append(
                float(_tau_field(upper_alpha, parameters, energy=energy)[2])
            )
            margins["alpha_lower_exit"].append(
                -float(_tau_field(lower_alpha, parameters, energy=energy)[2])
            )
        for beta in cross_values:
            for alpha in cross_values:
                chi, pi, _w = normal_outer_state(
                    np.array([z]),
                    np.array([beta]),
                    np.array([alpha]),
                    parameters,
                    energy=energy,
                )
                margins["positive_pi"].append(float(pi[0]))
                residual = energy_equation_residual(
                    np.array([z]),
                    np.array([beta]),
                    np.array([alpha]),
                    chi,
                    parameters,
                    energy=energy,
                )
                energy_residuals.append(abs(float(residual[0])))
                if z == max(z_values):
                    margins["z_outer_inward"].append(
                        -float(
                            _tau_field(
                                np.array([z, beta, alpha], dtype=np.float64),
                                parameters,
                                energy=energy,
                            )[0]
                        )
                    )
    result = {key: float(min(values)) for key, values in margins.items()}
    result["energy_equation_residual_inf"] = float(max(energy_residuals))
    result["minimum_oriented_face_margin"] = min(
        result["beta_upper_inward"],
        result["beta_lower_inward"],
        result["alpha_upper_exit"],
        result["alpha_lower_exit"],
        result["z_outer_inward"],
    )
    return result


def compute_graph_slice(
    configuration_path: Path = DEFAULT_CONFIG,
) -> tuple[dict[str, Any], dict[str, Array]]:
    configuration = _load_configuration(configuration_path)
    binding = configuration["matched_centerline_binding"]
    parameters = OuterParameters(r=3.0 / 200.0, a2=0.0, epsilon=1.0)
    energy_h = float(binding["energy_H"])
    energy = parameters.epsilon**2.5 * parameters.r**6 * energy_h
    beta_center = float(binding["seam_beta_center"])
    beta_values = beta_center + np.asarray(
        configuration["slice"]["beta_offsets"], dtype=np.float64
    )
    common_q = np.asarray(
        configuration["slice"]["common_Q_cuts"], dtype=np.float64
    )
    rate_q = np.asarray(
        configuration["slice"]["rate_Q_cuts"], dtype=np.float64
    )
    rate_step = float(configuration["slice"]["rate_Q_difference_step"])
    evaluation_q = np.unique(
        np.concatenate((common_q, rate_q - rate_step, rate_q, rate_q + rate_step))
    )
    solutions, collocation_diagnostics = _solve_collocation_ladder(
        configuration,
        parameters,
        beta_values,
        energy=energy,
        evaluation_q=evaluation_q,
    )
    horizons = np.asarray(
        configuration["slice"]["collocation_Q_end_ladder"],
        dtype=np.float64,
    )
    collocation_beta = np.empty(
        (horizons.size, beta_values.size, common_q.size), dtype=np.float64
    )
    collocation_alpha = np.empty_like(collocation_beta)
    collocation_chi = np.empty_like(collocation_beta)
    collocation_pi = np.empty_like(collocation_beta)
    for horizon_index, q_end in enumerate(horizons):
        for beta_index, beta0 in enumerate(beta_values):
            values = _normal_values(
                common_q,
                solutions[(float(q_end), float(beta0))].sol(common_q),
                parameters,
                energy=energy,
            )
            (
                collocation_beta[horizon_index, beta_index],
                collocation_alpha[horizon_index, beta_index],
                collocation_chi[horizon_index, beta_index],
                collocation_pi[horizon_index, beta_index],
            ) = values

    shooting_q_end = float(configuration["shooting_construction"]["Q_end"])
    shooting_q = common_q[common_q <= shooting_q_end]
    shooting_beta = np.empty(
        (beta_values.size, shooting_q.size), dtype=np.float64
    )
    shooting_alpha = np.empty_like(shooting_beta)
    shooting_chi = np.empty_like(shooting_beta)
    shooting_pi = np.empty_like(shooting_beta)
    shooting_diagnostics = []
    for beta_index, beta0 in enumerate(beta_values):
        integration, _alpha0, diagnostics = _shoot_one(
            configuration,
            parameters,
            float(beta0),
            energy=energy,
            evaluation_q=shooting_q,
        )
        if integration.sol is None:
            raise GraphSliceError("shooting dense output unexpectedly missing")
        values = _normal_values(
            shooting_q,
            integration.sol(shooting_q),
            parameters,
            energy=energy,
        )
        (
            shooting_beta[beta_index],
            shooting_alpha[beta_index],
            shooting_chi[beta_index],
            shooting_pi[beta_index],
        ) = values
        shooting_diagnostics.append(diagnostics)

    selected_solutions = [
        solutions[(float(horizons[-1]), float(beta0))]
        for beta0 in beta_values
    ]
    rates = _rate_proxies(
        configuration,
        parameters,
        beta_values,
        selected_solutions,
        energy=energy,
    )
    face_margins = _sampled_face_margins(
        configuration, parameters, energy=energy
    )
    horizon_seam_gamma = collocation_alpha[:, :, 0]
    horizon_spread = np.ptp(horizon_seam_gamma, axis=0)
    selected_beta = collocation_beta[-1]
    selected_alpha = collocation_alpha[-1]
    method_beta_difference = selected_beta[:, : shooting_q.size] - shooting_beta
    method_alpha_difference = selected_alpha[:, : shooting_q.size] - shooting_alpha
    method_state_difference = np.maximum(
        np.abs(method_beta_difference), np.abs(method_alpha_difference)
    )
    corridor = configuration["sampled_corridor"]
    graph_face_clearance = min(
        float(corridor["beta_half_width"])
        - float(np.max(np.abs(selected_beta))),
        float(corridor["alpha_half_width"])
        - float(np.max(np.abs(selected_alpha))),
    )
    thresholds = configuration["qa_thresholds"]
    max_collocation_residual = max(
        item["solver_rms_residual_max"] for item in collocation_diagnostics
    )
    max_collocation_boundary = max(
        item["boundary_residual_inf"] for item in collocation_diagnostics
    )
    max_energy_residual = max(
        max(item["energy_residual_inf"] for item in collocation_diagnostics),
        max(item["energy_residual_inf"] for item in shooting_diagnostics),
        face_margins["energy_equation_residual_inf"],
    )
    minimum_pi = min(
        min(item["minimum_pi"] for item in collocation_diagnostics),
        min(item["minimum_pi"] for item in shooting_diagnostics),
        face_margins["positive_pi"],
    )
    diagnostics = {
        "outer_energy": energy,
        "collocation": collocation_diagnostics,
        "shooting": shooting_diagnostics,
        "horizon_seam_gamma_spread": horizon_spread.tolist(),
        "horizon_seam_gamma_spread_max": float(np.max(horizon_spread)),
        "method_seam_gamma_difference": (
            selected_alpha[:, 0] - shooting_alpha[:, 0]
        ).tolist(),
        "method_seam_gamma_difference_abs_max": float(
            np.max(np.abs(selected_alpha[:, 0] - shooting_alpha[:, 0]))
        ),
        "method_common_state_difference_inf": float(
            np.max(method_state_difference)
        ),
        "energy_residual_inf": float(max_energy_residual),
        "minimum_pi": float(minimum_pi),
        "graph_face_clearance": float(graph_face_clearance),
        "sampled_face_margins": face_margins,
        "invariance_residual_inf": float(
            np.max(np.abs(rates["rate_invariance_residual"]))
        ),
        "tangent_log_norm_max": float(
            np.max(rates["rate_tangent_log_norm"])
        ),
        "normal_quotient_rate_min": float(
            np.min(rates["rate_normal_quotient"])
        ),
        "third_order_bunching_rate_min": float(
            np.min(rates["rate_bunching_gamma_j"][:, 3])
        ),
        "rate_beta_slice_separation_min": float(
            np.min(rates["rate_beta_slice_separation"])
        ),
    }
    qa = {
        "collocation_residual": max_collocation_residual
        <= float(thresholds["collocation_rms_residual_upper"]),
        "collocation_boundary": max_collocation_boundary
        <= float(thresholds["collocation_boundary_residual_upper"]),
        "horizon_convergence": diagnostics["horizon_seam_gamma_spread_max"]
        <= float(thresholds["horizon_seam_gamma_spread_upper"]),
        "shooting_terminal": max(
            abs(item["terminal_residual"]) for item in shooting_diagnostics
        )
        <= float(thresholds["shooting_terminal_residual_upper"]),
        "independent_seam_agreement": diagnostics[
            "method_seam_gamma_difference_abs_max"
        ]
        <= float(thresholds["method_seam_gamma_difference_upper"]),
        "independent_common_state_agreement": diagnostics[
            "method_common_state_difference_inf"
        ]
        <= float(thresholds["method_common_state_difference_upper"]),
        "energy": max_energy_residual
        <= float(thresholds["energy_residual_upper"]),
        "positive_pi": minimum_pi >= float(thresholds["minimum_pi_lower"]),
        "graph_inside_sampled_faces": graph_face_clearance
        >= float(thresholds["graph_face_clearance_lower"]),
        "sampled_face_orientation": face_margins[
            "minimum_oriented_face_margin"
        ]
        >= float(thresholds["sampled_oriented_face_margin_lower"]),
        "invariance": diagnostics["invariance_residual_inf"]
        <= float(thresholds["invariance_residual_upper"]),
        "third_order_bunching_proxy": diagnostics[
            "third_order_bunching_rate_min"
        ]
        >= float(thresholds["third_order_bunching_rate_lower"]),
    }
    all_passed = all(qa.values())
    superseded = configuration["superseded_slice_reference"]
    metric_names = tuple(superseded["headline_metrics"])
    metric_old = np.asarray(
        [float(superseded["headline_metrics"][name]) for name in metric_names],
        dtype=np.float64,
    )
    metric_current = np.asarray(
        [float(diagnostics[name]) for name in metric_names], dtype=np.float64
    )
    binding_update = {
        "reason": configuration["binding_update"]["reason"],
        "frozen_design_unchanged": configuration["binding_update"][
            "frozen_design_unchanged"
        ],
        "source_commits_on_integration": configuration["binding_update"][
            "current_input_commits_on_integration"
        ],
        "report_sha256": {
            "superseded": configuration["binding_update"][
                "superseded_report_sha256"
            ],
            "current": binding["report_sha256"],
        },
        "data_sha256": {
            "superseded": configuration["binding_update"][
                "superseded_data_sha256"
            ],
            "current": binding["data_sha256"],
        },
        "energy_H": {
            "superseded": float(
                configuration["binding_update"]["superseded_energy_H"]
            ),
            "current": energy_h,
            "difference": energy_h
            - float(configuration["binding_update"]["superseded_energy_H"]),
        },
        "outer_energy": {
            "superseded": float(superseded["fixed_energy"]),
            "current": energy,
            "difference": energy - float(superseded["fixed_energy"]),
        },
        "seam_beta_center": {
            "superseded": float(
                configuration["binding_update"][
                    "superseded_seam_beta_center"
                ]
            ),
            "current": beta_center,
            "difference": beta_center
            - float(
                configuration["binding_update"][
                    "superseded_seam_beta_center"
                ]
            ),
        },
        "superseded_slice_git_object": superseded["git_object"],
        "superseded_slice_result_sha256": superseded["result_sha256"],
        "headline_metric_order": list(metric_names),
        "headline_metrics": {
            name: {
                "superseded": float(metric_old[index]),
                "current": float(metric_current[index]),
                "difference": float(metric_current[index] - metric_old[index]),
            }
            for index, name in enumerate(metric_names)
        },
        "qa_status_changed": bool(
            bool(superseded["all_qa_passed"]) != all_passed
        ),
    }
    report = {
        "schema_version": "rfsn-vdp-v4-future-graph-slice-v2/1",
        "status": (
            "V4_FUTURE_GRAPH_SLICE_COMPUTED"
            if all_passed
            else "V4_FUTURE_GRAPH_SLICE_QA_REJECTED"
        ),
        "evidence_status": "COMPUTED/E1_NON_RIGOROUS_WITH_QA",
        "mathematical_status": "INCONCLUSIVE",
        "claim_bearing": False,
        "parameter_point": configuration["parameter_point"],
        "fixed_energy": energy,
        "beta_values": beta_values.tolist(),
        "Q_start": float(binding["seam_Q"]),
        "collocation_Q_end_ladder": horizons.tolist(),
        "shooting_Q_end": shooting_q_end,
        "binding_update": binding_update,
        "terminal_model": (
            "Exact alpha_dot=0 normal nullcline; asymptotically compatible "
            "but not the exact finite-Q V4 graph."
        ),
        "diagnostics": diagnostics,
        "thresholds": thresholds,
        "qa": qa,
        "nonclaim": (
            "This is one fixed-parameter, fixed-energy, three-beta floating "
            "slice.  It does not prove the maximal future-staying graph, "
            "uniform corridor faces, uniqueness, regularity, parameter jets, "
            "or the Issue #7 parameter-box theorem."
        ),
    }
    arrays = {
        "beta_initial": beta_values,
        "common_Q": common_q,
        "collocation_Q_end": horizons,
        "collocation_beta": collocation_beta,
        "collocation_alpha": collocation_alpha,
        "collocation_chi": collocation_chi,
        "collocation_pi": collocation_pi,
        "shooting_Q": shooting_q,
        "shooting_beta": shooting_beta,
        "shooting_alpha": shooting_alpha,
        "shooting_chi": shooting_chi,
        "shooting_pi": shooting_pi,
        "method_beta_difference": method_beta_difference,
        "method_alpha_difference": method_alpha_difference,
        "binding_energy_H_superseded_current": np.array(
            [binding_update["energy_H"]["superseded"], energy_h],
            dtype=np.float64,
        ),
        "binding_outer_energy_superseded_current": np.array(
            [binding_update["outer_energy"]["superseded"], energy],
            dtype=np.float64,
        ),
        "binding_seam_beta_superseded_current": np.array(
            [binding_update["seam_beta_center"]["superseded"], beta_center],
            dtype=np.float64,
        ),
        "binding_headline_metrics_superseded_current": np.column_stack(
            (metric_old, metric_current)
        ),
        "binding_headline_metrics_difference": metric_current - metric_old,
        **rates,
    }
    if not all_passed:
        raise GraphSliceError(
            "predeclared graph-slice QA failed: "
            + ", ".join(key for key, passed in qa.items() if not passed)
        )
    return report, arrays


def _write_failure(error: Exception, configuration_path: Path) -> None:
    DEFAULT_RESULT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "rfsn-vdp-v4-future-graph-slice-v2/1",
        "status": "V4_FUTURE_GRAPH_SLICE_FAILED",
        "evidence_status": "COMPUTED/E1_FAILED",
        "mathematical_status": "INCONCLUSIVE",
        "claim_bearing": False,
        "configuration_path": str(configuration_path.relative_to(REPOSITORY)),
        "failure_type": type(error).__name__,
        "failure_reason": str(error),
    }
    DEFAULT_RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    try:
        report, arrays = compute_graph_slice(DEFAULT_CONFIG)
    except Exception as error:
        _write_failure(error, DEFAULT_CONFIG)
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
