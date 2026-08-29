"""Finite-Q V5A object on the current v2 energy-preserving centerline.

The saved centerline is the data-bearing object.  Its outer arrival label and
terminal condition determine an independent high-resolution solution of the
same exact outer boundary-value problem.  The independent solution is used
for quadrature because the archived 401-point output does not resolve the
terminal ``O(delta)`` layer; agreement is checked at every archived node.

Everything produced here is floating-point ``COMPUTED/E1`` evidence.  A
finite terminal condition at ``Q=200`` cannot prove the V5A improper limits,
their mixed derivatives, or uniform covariance on the parameter box.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import cumulative_trapezoid, trapezoid
from scipy.interpolate import CubicSpline

from numerics.vdp_matched_outer import finite_horizon_gamma_continuation
from numerics.vdp_outer import (
    OuterParameters,
    normal_outer_rhs_q,
    normal_outer_state,
)


Array = NDArray[np.float64]
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_CONFIG = HERE / "config/vdp_v5a_current_tail.json"
DEFAULT_RESULT = (
    HERE / "results/vdp_p2e_channel_scout_v2/v5a_current_tail.json"
)
DEFAULT_DATA = (
    HERE / "results/vdp_p2e_channel_scout_v2/v5a_current_tail.npz"
)


class CurrentTailError(RuntimeError):
    """The frozen input or finite-Q current-tail computation is invalid."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _endpoint_grid(q_start: float, q_end: float, points: int) -> Array:
    phase = np.linspace(0.0, 1.0, points)
    return q_start + 0.5 * (q_end - q_start) * (
        1.0 - np.cos(np.pi * phase)
    )


def quadrature_grid(
    q_start: float,
    q_end: float,
    points: int,
    start_layer_width: float,
    *,
    extra_points: Array | None = None,
) -> Array:
    """Return the frozen bulk-plus-inflow-layer physical-Q grid."""

    if not 0.0 < q_start < q_end:
        raise ValueError("require 0 < q_start < q_end")
    if points < 101:
        raise ValueError("points must be at least 101")
    if not 0.0 < start_layer_width < q_end - q_start:
        raise ValueError("start_layer_width must be inside the Q interval")
    bulk = _endpoint_grid(q_start, q_end, points)
    layer = np.linspace(q_start, q_start + start_layer_width, points)
    pieces = [bulk, layer]
    if extra_points is not None:
        pieces.append(np.asarray(extra_points, dtype=np.float64))
    return np.unique(np.concatenate(pieces))


def outer_densities(
    compact_q: Array,
    beta: Array,
    alpha: Array,
    parameters: OuterParameters,
    *,
    energy: float,
) -> tuple[Array, Array, Array, Array, Array]:
    """Evaluate the exact V5A length/action densities at one fixed energy."""

    q = np.asarray(compact_q, dtype=np.float64)
    chi, pi, w = normal_outer_state(
        q ** (-0.5), beta, alpha, parameters, energy=energy
    )
    if np.any(pi <= 0.0):
        raise CurrentTailError("the common physical Q coordinate lost pi>0")
    length = parameters.delta / (2.0 * pi) * q ** (-0.5)
    action = (
        -chi * chi / (2.0 * pi) * q**1.5
        + parameters.epsilon * pi / 2.0 * q ** (-0.5)
    )
    return length, action, chi, pi, w


def _state_splines(beta: Array, alpha: Array, q: Array) -> tuple[CubicSpline, CubicSpline]:
    return CubicSpline(q, beta), CubicSpline(q, alpha)


def _density_splines(
    length: Array, action: Array, q: Array
) -> tuple[CubicSpline, CubicSpline]:
    return CubicSpline(q, length), CubicSpline(q, action)


def _gauge_density(
    q: Array,
    beta: Array,
    alpha: Array,
    parameters: OuterParameters,
    *,
    energy: float,
    coefficient_z: float,
    coefficient_w: float,
) -> Array:
    rhs = normal_outer_rhs_q(
        q, np.vstack((beta, alpha)), parameters, energy=energy
    )
    z_q = -0.5 * q ** (-1.5)
    w_q = rhs[1] - rhs[0]
    return coefficient_z * z_q + coefficient_w * w_q


def _gauge_potential(
    q: Array | float,
    beta: Array | float,
    alpha: Array | float,
    *,
    coefficient_z: float,
    coefficient_w: float,
) -> Array:
    q_array = np.asarray(q, dtype=np.float64)
    return (
        coefficient_z * q_array ** (-0.5)
        + coefficient_w
        * (np.asarray(alpha, dtype=np.float64) - np.asarray(beta, dtype=np.float64))
    )


def _split_balance(q: Array, density: Array, cut: float) -> float:
    index = int(np.searchsorted(q, cut))
    if index >= q.size or q[index] != cut:
        raise CurrentTailError("split cut is not an exact quadrature node")
    whole = trapezoid(density, q)
    prefix = trapezoid(density[: index + 1], q[: index + 1])
    suffix = trapezoid(density[index:], q[index:])
    return float(whole - prefix - suffix)


def compute_current_tail(
    config_path: Path = DEFAULT_CONFIG,
) -> tuple[dict[str, Any], dict[str, Array]]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    input_config = config["input"]
    center_json_path = ROOT / input_config["centerline_json"]
    center_npz_path = ROOT / input_config["centerline_npz"]
    center_report = json.loads(center_json_path.read_text(encoding="utf-8"))
    if center_report.get("status") != input_config["required_status"]:
        raise CurrentTailError("the frozen current centerline is not accepted")

    parameter_data = center_report["parameter_point"]
    parameters = OuterParameters(
        r=float(parameter_data["r"]),
        a2=float(parameter_data["a2"]),
        epsilon=float(parameter_data["epsilon"]),
    )
    with np.load(center_npz_path) as archive:
        saved_q = np.asarray(archive["outer_Q"], dtype=np.float64)
        saved_state = np.asarray(
            archive["outer_state_beta_alpha"], dtype=np.float64
        )
        saved_chi = np.asarray(archive["outer_chi"], dtype=np.float64)
        saved_pi = np.asarray(archive["outer_pi"], dtype=np.float64)
    if saved_state.shape != (2, saved_q.size):
        raise CurrentTailError("unexpected saved outer-state shape")
    if not np.all(np.diff(saved_q) > 0.0):
        raise CurrentTailError("saved physical Q grid is not increasing")

    normalization = config["normalization"]
    target_q_star = float(normalization["target_q_star"])
    q_star_index = int(np.argmin(np.abs(saved_q - target_q_star)))
    q_star = float(saved_q[q_star_index])
    q_end = float(normalization["q_end"])
    if abs(float(saved_q[-1]) - q_end) > 1.0e-12:
        raise CurrentTailError("the frozen Q_end does not equal the saved endpoint")
    actual_beta0 = float(saved_state[0, q_star_index])
    alternate_beta0 = (
        float(normalization["alternate_reference_beta_factor"]) * actual_beta0
    )
    reference_beta0 = (
        float(normalization["reference_beta_factor"]) * actual_beta0
    )
    if reference_beta0 != 0.0:
        raise CurrentTailError("V5A reference normalization requires beta=0")

    energy_h = float(center_report["energy_h"])
    outer_energy = parameters.epsilon**2.5 * parameters.r**6 * energy_h
    solver = config["outer_bvp"]
    continuation = finite_horizon_gamma_continuation(
        parameters,
        (reference_beta0, alternate_beta0, actual_beta0),
        q_start=q_star,
        q_end=q_end,
        points=int(solver["output_points"]),
        tolerance=float(solver["tolerance"]),
        max_nodes=int(solver["max_nodes"]),
        positive_pi=True,
        energy=outer_energy,
    )
    reference, alternate, actual = continuation.samples
    output_q = actual.compact_q

    states = {
        "reference": (reference.beta, reference.alpha),
        "alternate_reference": (alternate.beta, alternate.alpha),
        "actual": (actual.beta, actual.alpha),
    }
    densities: dict[str, tuple[Array, Array, Array, Array, Array]] = {}
    for name, (beta, alpha) in states.items():
        densities[name] = outer_densities(
            output_q,
            beta,
            alpha,
            parameters,
            energy=outer_energy,
        )

    # Bind the reconstructed actual member to all archived nodes at and after
    # the selected normalization cut.  This is the critical current-centerline
    # check; it prevents a generic neighboring graph orbit being substituted.
    saved_mask = np.arange(saved_q.size) >= q_star_index
    bound_q = saved_q[saved_mask]
    actual_beta_spline, actual_alpha_spline = _state_splines(
        actual.beta, actual.alpha, output_q
    )
    reconstructed_state = np.vstack(
        (actual_beta_spline(bound_q), actual_alpha_spline(bound_q))
    )
    state_reconstruction = reconstructed_state - saved_state[:, saved_mask]
    reconstructed_chi_pi = np.vstack(
        (
            CubicSpline(output_q, densities["actual"][2])(bound_q),
            CubicSpline(output_q, densities["actual"][3])(bound_q),
        )
    )
    chi_pi_reconstruction = reconstructed_chi_pi - np.vstack(
        (saved_chi[saved_mask], saved_pi[saved_mask])
    )

    density_interpolants: dict[str, tuple[CubicSpline, CubicSpline]] = {
        name: _density_splines(value[0], value[1], output_q)
        for name, value in densities.items()
    }
    state_interpolants = {
        name: _state_splines(beta, alpha, output_q)
        for name, (beta, alpha) in states.items()
    }

    quadrature = config["quadrature"]
    grid_ladder: list[dict[str, float | int]] = []
    for points in quadrature["grid_ladder"]:
        grid = quadrature_grid(
            q_star,
            q_end,
            int(points),
            float(quadrature["start_layer_width"]),
        )
        delta_length = (
            density_interpolants["actual"][0](grid)
            - density_interpolants["reference"][0](grid)
        )
        delta_action = (
            density_interpolants["actual"][1](grid)
            - density_interpolants["reference"][1](grid)
        )
        grid_ladder.append(
            {
                "requested_points_per_component": int(points),
                "union_grid_points": int(grid.size),
                "relative_length_at_q_end": float(
                    trapezoid(delta_length, grid)
                ),
                "relative_action_at_q_end": float(
                    trapezoid(delta_action, grid)
                ),
            }
        )

    cutoff_values = [
        q_star + float(offset)
        for offset in config["cutoff_offsets"]
        if q_star + float(offset) < q_end
    ]
    cutoff_values.append(q_end)
    split_values = [
        q_star + float(offset)
        for offset in config["covariance"]["split_cut_offsets"]
        if q_star + float(offset) < q_end
    ]
    extra = np.asarray(cutoff_values + split_values, dtype=np.float64)
    integration_q = quadrature_grid(
        q_star,
        q_end,
        int(quadrature["grid_ladder"][-1]),
        float(quadrature["start_layer_width"]),
        extra_points=extra,
    )

    evaluated: dict[str, dict[str, Array]] = {}
    for name in states:
        beta = state_interpolants[name][0](integration_q)
        alpha = state_interpolants[name][1](integration_q)
        length = density_interpolants[name][0](integration_q)
        action = density_interpolants[name][1](integration_q)
        evaluated[name] = {
            "beta": beta,
            "alpha": alpha,
            "length": length,
            "action": action,
        }

    delta_length = evaluated["actual"]["length"] - evaluated["reference"]["length"]
    delta_action = evaluated["actual"]["action"] - evaluated["reference"]["action"]
    cumulative_relative_length = cumulative_trapezoid(
        delta_length, integration_q, initial=0.0
    )
    cumulative_relative_action = cumulative_trapezoid(
        delta_action, integration_q, initial=0.0
    )
    cumulative_reference_length = cumulative_trapezoid(
        evaluated["reference"]["length"], integration_q, initial=0.0
    )
    cumulative_reference_action = cumulative_trapezoid(
        evaluated["reference"]["action"], integration_q, initial=0.0
    )

    cutoff_ladder: list[dict[str, float]] = []
    shadowing_ladder: list[dict[str, float]] = []
    shadow_points = [q_star] + cutoff_values
    for cutoff in cutoff_values:
        relative_length = float(
            np.interp(cutoff, integration_q, cumulative_relative_length)
        )
        relative_action = float(
            np.interp(cutoff, integration_q, cumulative_relative_action)
        )
        cutoff_ladder.append(
            {
                "q_cut": cutoff,
                "relative_length": relative_length,
                "relative_action": relative_action,
            }
        )
    for cutoff in shadow_points:
        beta_gap = float(
            state_interpolants["actual"][0](cutoff)
            - state_interpolants["reference"][0](cutoff)
        )
        alpha_gap = float(
            state_interpolants["actual"][1](cutoff)
            - state_interpolants["reference"][1](cutoff)
        )
        shadowing_ladder.append(
            {
                "q": cutoff,
                "beta_gap": beta_gap,
                "alpha_gap": alpha_gap,
                "euclidean_normal_gap": float(np.hypot(beta_gap, alpha_gap)),
            }
        )

    cut_covariance = []
    for split in split_values:
        cut_covariance.append(
            {
                "q_cut": split,
                "length_balance_residual": _split_balance(
                    integration_q, delta_length, split
                ),
                "action_balance_residual": _split_balance(
                    integration_q, delta_action, split
                ),
            }
        )

    actual_minus_alternate_length = (
        evaluated["actual"]["length"]
        - evaluated["alternate_reference"]["length"]
    )
    alternate_minus_reference_length = (
        evaluated["alternate_reference"]["length"]
        - evaluated["reference"]["length"]
    )
    actual_minus_alternate_action = (
        evaluated["actual"]["action"]
        - evaluated["alternate_reference"]["action"]
    )
    alternate_minus_reference_action = (
        evaluated["alternate_reference"]["action"]
        - evaluated["reference"]["action"]
    )
    reference_covariance = {
        "alternate_reference_beta_at_q_star": alternate_beta0,
        "length_balance_residual": float(
            trapezoid(delta_length, integration_q)
            - trapezoid(actual_minus_alternate_length, integration_q)
            - trapezoid(alternate_minus_reference_length, integration_q)
        ),
        "action_balance_residual": float(
            trapezoid(delta_action, integration_q)
            - trapezoid(actual_minus_alternate_action, integration_q)
            - trapezoid(alternate_minus_reference_action, integration_q)
        ),
    }

    gauge_config = config["covariance"]["gauge"]
    coefficient_z = float(gauge_config["coefficient_z"])
    coefficient_w = float(gauge_config["coefficient_w"])
    gauge_densities: dict[str, Array] = {}
    gauge_potentials: dict[str, Array] = {}
    for name in ("actual", "reference"):
        beta = evaluated[name]["beta"]
        alpha = evaluated[name]["alpha"]
        gauge_densities[name] = _gauge_density(
            integration_q,
            beta,
            alpha,
            parameters,
            energy=outer_energy,
            coefficient_z=coefficient_z,
            coefficient_w=coefficient_w,
        )
        gauge_potentials[name] = _gauge_potential(
            integration_q,
            beta,
            alpha,
            coefficient_z=coefficient_z,
            coefficient_w=coefficient_w,
        )
    transformed_relative_action = float(
        trapezoid(
            (
                evaluated["actual"]["action"] + gauge_densities["actual"]
                - evaluated["reference"]["action"]
                - gauge_densities["reference"]
            ),
            integration_q,
        )
    )
    original_relative_action = float(trapezoid(delta_action, integration_q))
    gauge_endpoint_correction = float(
        gauge_potentials["actual"][-1]
        - gauge_potentials["actual"][0]
        - gauge_potentials["reference"][-1]
        + gauge_potentials["reference"][0]
    )
    gauge_covariance = {
        "gauge": str(gauge_config["formula"]),
        "coefficient_z": coefficient_z,
        "coefficient_w": coefficient_w,
        "original_relative_action": original_relative_action,
        "transformed_relative_action": transformed_relative_action,
        "endpoint_correction": gauge_endpoint_correction,
        "balance_residual": float(
            transformed_relative_action
            - original_relative_action
            - gauge_endpoint_correction
        ),
    }

    thresholds = config["qa_thresholds"]
    last_length_change = abs(
        float(grid_ladder[-1]["relative_length_at_q_end"])
        - float(grid_ladder[-2]["relative_length_at_q_end"])
    )
    last_action_change = abs(
        float(grid_ladder[-1]["relative_action_at_q_end"])
        - float(grid_ladder[-2]["relative_action_at_q_end"])
    )
    layer_cut = q_star + float(quadrature["start_layer_width"])
    post_layer_length_change = abs(
        float(cumulative_relative_length[-1])
        - float(np.interp(layer_cut, integration_q, cumulative_relative_length))
    )
    post_layer_action_change = abs(
        float(cumulative_relative_action[-1])
        - float(np.interp(layer_cut, integration_q, cumulative_relative_action))
    )
    max_solver_residual = max(
        float(sample.diagnostics["solver_rms_residual_max"])
        for sample in continuation.samples
    )
    max_boundary_residual = max(
        float(sample.diagnostics["boundary_residual_inf"])
        for sample in continuation.samples
    )
    max_energy_residual = max(
        float(sample.diagnostics["energy_residual_inf"])
        for sample in continuation.samples
    )
    minimum_pi = min(
        float(sample.diagnostics["minimum_pi"])
        for sample in continuation.samples
    )
    state_reconstruction_inf = float(np.max(np.abs(state_reconstruction)))
    chi_pi_reconstruction_inf = float(
        np.max(np.abs(chi_pi_reconstruction))
    )
    max_cut_length = max(
        abs(float(row["length_balance_residual"])) for row in cut_covariance
    )
    max_cut_action = max(
        abs(float(row["action_balance_residual"])) for row in cut_covariance
    )
    qa = {
        "input_status": True,
        "positive_pi": minimum_pi > 0.0,
        "solver_residual": max_solver_residual
        <= float(thresholds["solver_rms_residual_max"]),
        "boundary_residual": max_boundary_residual
        <= float(thresholds["boundary_residual_inf"]),
        "energy_residual": max_energy_residual
        <= float(thresholds["energy_residual_inf"]),
        "saved_node_state_reconstruction": state_reconstruction_inf
        <= float(thresholds["saved_node_state_reconstruction_inf"]),
        "saved_node_chi_pi_reconstruction": chi_pi_reconstruction_inf
        <= float(thresholds["saved_node_chi_pi_reconstruction_inf"]),
        "grid_length_change": last_length_change
        <= float(thresholds["last_grid_length_change_abs"]),
        "grid_action_change": last_action_change
        <= float(thresholds["last_grid_action_change_abs"]),
        "post_layer_length_change": post_layer_length_change
        <= float(thresholds["post_layer_length_change_abs"]),
        "post_layer_action_change": post_layer_action_change
        <= float(thresholds["post_layer_action_change_abs"]),
        "cut_length_covariance": max_cut_length
        <= float(thresholds["cut_balance_length_abs"]),
        "cut_action_covariance": max_cut_action
        <= float(thresholds["cut_balance_action_abs"]),
        "reference_length_covariance": abs(
            float(reference_covariance["length_balance_residual"])
        )
        <= float(thresholds["reference_balance_length_abs"]),
        "reference_action_covariance": abs(
            float(reference_covariance["action_balance_residual"])
        )
        <= float(thresholds["reference_balance_action_abs"]),
        "gauge_action_covariance": abs(
            float(gauge_covariance["balance_residual"])
        )
        <= float(thresholds["gauge_balance_action_abs"]),
    }
    all_qa = all(qa.values())

    report: dict[str, Any] = {
        "schema_version": "rfsn-vdp-v5a-current-tail/1",
        "status": (
            "CURRENT_CENTERLINE_V5A_FINITE_Q_OBJECT_COMPUTED"
            if all_qa
            else "CURRENT_CENTERLINE_V5A_FINITE_Q_OBJECT_QA_REJECTED"
        ),
        "evidence_status": "COMPUTED/E1_NON_RIGOROUS",
        "theorem_status": "INCONCLUSIVE",
        "claim_bearing": False,
        "parameter_point": dict(parameter_data),
        "parameter_point_exact": center_report.get("parameter_point_exact"),
        "input_binding": {
            "centerline_status": center_report["status"],
            "centerline_json": input_config["centerline_json"],
            "centerline_npz": input_config["centerline_npz"],
            "centerline_json_sha256": _sha256(center_json_path),
            "centerline_npz_sha256": _sha256(center_npz_path),
            "frozen_config": str(config_path.relative_to(ROOT)),
            "frozen_config_sha256": _sha256(config_path),
        },
        "normalization": {
            "target_q_star": target_q_star,
            "selected_saved_q_star_index": q_star_index,
            "selected_physical_q_star": q_star,
            "q_end": q_end,
            "actual_beta_at_q_star": actual_beta0,
            "actual_alpha_at_q_star_saved": float(
                saved_state[1, q_star_index]
            ),
            "reference_beta_at_q_star": reference_beta0,
            "alternate_reference_beta_at_q_star": alternate_beta0,
            "terminal_condition": solver["terminal_condition"],
            "outer_energy_from_current_centerline": outer_energy,
            "energy_h_chart": energy_h,
        },
        "solver_diagnostics": {
            "chart": solver["chart"],
            "maximum_rms_residual": max_solver_residual,
            "maximum_boundary_residual": max_boundary_residual,
            "maximum_energy_residual": max_energy_residual,
            "minimum_pi": minimum_pi,
            "samples": {
                name: dict(sample.diagnostics)
                for name, sample in zip(
                    ("reference", "alternate_reference", "actual"),
                    continuation.samples,
                )
            },
        },
        "current_centerline_reconstruction": {
            "saved_nodes_compared": int(bound_q.size),
            "state_beta_alpha_residual_inf": state_reconstruction_inf,
            "chi_pi_residual_inf": chi_pi_reconstruction_inf,
            "reason_for_reconstruction": (
                "The archived 401-node state binds the orbit but under-resolves "
                "the terminal O(delta) layer; quadrature uses the independently "
                "resolved exact BVP after agreement at every archived node."
            ),
        },
        "same_q_shadowing": {
            "status": "FINITE_HORIZON_SAME_Q_GAPS_COMPUTED",
            "ladder": shadowing_ladder,
            "nonclaim": (
                "Finite-Q decay to the common artificial terminal condition is "
                "not a proof of exponential flatness on the half-line."
            ),
        },
        "finite_cut_reference_subtraction": {
            "relative_length_at_q_end": float(
                cumulative_relative_length[-1]
            ),
            "relative_action_at_q_end": float(
                cumulative_relative_action[-1]
            ),
            "reference_raw_length_at_q_end": float(
                cumulative_reference_length[-1]
            ),
            "reference_raw_action_at_q_end": float(
                cumulative_reference_action[-1]
            ),
            "post_start_layer_length_change_abs": post_layer_length_change,
            "post_start_layer_action_change_abs": post_layer_action_change,
            "cutoff_ladder": cutoff_ladder,
            "grid_ladder": grid_ladder,
            "last_grid_length_change_abs": last_length_change,
            "last_grid_action_change_abs": last_action_change,
        },
        "finite_covariance": {
            "cut": cut_covariance,
            "reference": reference_covariance,
            "gauge": gauge_covariance,
            "coordinate": {
                "status": "NOT_COMPUTED",
                "reason": (
                    "No independent admissible compactifying-coordinate "
                    "realization is present in the current saved centerline."
                ),
            },
            "scope": (
                "These are finite-grid identities on actual computed tails, "
                "not covariance of an improper limit."
            ),
        },
        "thresholds": thresholds,
        "qa": qa,
        "strict_scope": {
            "resolved": (
                "One current-centerline outer member, one beta=0 reference, "
                "one real alternate reference, same-Q density differences, "
                "finite-cut integrals, and finite cut/reference/gauge balances."
            ),
            "unresolved": (
                "Q to infinity, removal of the artificial terminal condition, "
                "exponential flatness, mixed two-jets, uniform parameter-box "
                "bounds, and coordinate covariance."
            ),
            "conclusion": (
                "The actual V5A finite-Q numerical object now exists, while "
                "Theorem V5A remains numerically INCONCLUSIVE."
            ),
        },
    }

    arrays: dict[str, Array] = {
        "outer_Q": output_q,
        "actual_beta": actual.beta,
        "actual_alpha": actual.alpha,
        "actual_chi": densities["actual"][2],
        "actual_pi": densities["actual"][3],
        "actual_length_density": densities["actual"][0],
        "actual_action_density": densities["actual"][1],
        "reference_beta": reference.beta,
        "reference_alpha": reference.alpha,
        "reference_chi": densities["reference"][2],
        "reference_pi": densities["reference"][3],
        "reference_length_density": densities["reference"][0],
        "reference_action_density": densities["reference"][1],
        "alternate_reference_beta": alternate.beta,
        "alternate_reference_alpha": alternate.alpha,
        "alternate_reference_length_density": densities[
            "alternate_reference"
        ][0],
        "alternate_reference_action_density": densities[
            "alternate_reference"
        ][1],
        "integration_Q": integration_q,
        "integration_delta_length_density": delta_length,
        "integration_delta_action_density": delta_action,
        "cumulative_relative_length": cumulative_relative_length,
        "cumulative_relative_action": cumulative_relative_action,
        "cumulative_reference_length": cumulative_reference_length,
        "cumulative_reference_action": cumulative_reference_action,
        "gauge_actual_density": gauge_densities["actual"],
        "gauge_reference_density": gauge_densities["reference"],
        "saved_comparison_Q": bound_q,
        "saved_state_reconstruction_delta": state_reconstruction,
        "saved_chi_pi_reconstruction_delta": chi_pi_reconstruction,
        "grid_ladder_points": np.asarray(
            [row["requested_points_per_component"] for row in grid_ladder],
            dtype=np.float64,
        ),
        "grid_ladder_relative_length": np.asarray(
            [row["relative_length_at_q_end"] for row in grid_ladder],
            dtype=np.float64,
        ),
        "grid_ladder_relative_action": np.asarray(
            [row["relative_action_at_q_end"] for row in grid_ladder],
            dtype=np.float64,
        ),
        "cutoff_Q": np.asarray(cutoff_values, dtype=np.float64),
        "cutoff_relative_length": np.asarray(
            [row["relative_length"] for row in cutoff_ladder], dtype=np.float64
        ),
        "cutoff_relative_action": np.asarray(
            [row["relative_action"] for row in cutoff_ladder], dtype=np.float64
        ),
    }
    return report, arrays


def main() -> None:
    report, arrays = compute_current_tail()
    DEFAULT_RESULT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(DEFAULT_DATA, **arrays)
    report["data_path"] = str(DEFAULT_DATA.relative_to(ROOT))
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
