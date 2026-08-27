"""Exact V1 physical/fast/central coordinate and clock cross-checks.

The formulas are the direct substitutions in
``van-der-pol/MODEL_AND_CENTRAL_CHART.md``.  They are kept separate from the
end compactifications: this module concerns only the full stationary system,
its fixed-equilibrium central chart, and the physical action normalization.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import cumulative_trapezoid
from scipy.integrate import solve_ivp

from numerics.rfsn_numerics import vdp_field, vdp_hamiltonian


Array = NDArray[np.float64]


def cubic_f(u: Array | float) -> Array:
    values = np.asarray(u, dtype=float)
    return values**3 / 3.0 - values


def cubic_F(u: Array | float) -> Array:
    values = np.asarray(u, dtype=float)
    return values**4 / 12.0 - values**2 / 2.0


@dataclass(frozen=True)
class BridgeParameters:
    r: float
    a2: float
    epsilon: float

    def __post_init__(self) -> None:
        if not np.isfinite(self.r) or self.r <= 0.0:
            raise ValueError("r must be positive")
        if not np.isfinite(self.epsilon) or self.epsilon <= 0.0:
            raise ValueError("epsilon must be positive")
        if not np.isfinite(self.a2):
            raise ValueError("a2 must be finite")

    @property
    def delta(self) -> float:
        return self.r**2

    @property
    def d(self) -> float:
        return self.r**4

    @property
    def a(self) -> float:
        return float(1.0 + np.sqrt(self.epsilon) * self.r**3 * self.a2)

    @property
    def action_scale(self) -> float:
        return float(self.epsilon ** 2.25 * self.r**5)

    @property
    def energy_scale(self) -> float:
        return float(self.epsilon ** 2.5 * self.r**6)

    @property
    def x_per_xi(self) -> float:
        return float(self.r * self.epsilon ** -0.25)


def central_to_physical(state: Array, parameters: BridgeParameters) -> Array:
    """Apply the exact fixed-equilibrium change (23), columnwise."""

    central = np.asarray(state, dtype=float)
    if central.shape[0] != 4:
        raise ValueError("state must have leading dimension four")
    u, p, v, q = central
    epsilon = parameters.epsilon
    r = parameters.r
    a = parameters.a
    return np.asarray(
        [
            a - np.sqrt(epsilon) * r**2 * u,
            -epsilon**0.75 * r**3 * p,
            cubic_f(a) - epsilon * r**4 * v,
            -epsilon**1.25 * r**3 * q,
        ],
        dtype=float,
    )


def physical_to_central(state: Array, parameters: BridgeParameters) -> Array:
    """Invert the exact fixed-equilibrium change (23), columnwise."""

    physical = np.asarray(state, dtype=float)
    if physical.shape[0] != 4:
        raise ValueError("state must have leading dimension four")
    u, p, v, q = physical
    epsilon = parameters.epsilon
    r = parameters.r
    a = parameters.a
    return np.asarray(
        [
            (a - u) / (np.sqrt(epsilon) * r**2),
            -p / (epsilon**0.75 * r**3),
            (cubic_f(a) - v) / (epsilon * r**4),
            -q / (epsilon**1.25 * r**3),
        ],
        dtype=float,
    )


def physical_field_x(state: Array, parameters: BridgeParameters) -> Array:
    """Physical-x stationary field (6), evaluated columnwise."""

    u, p, v, q = np.asarray(state, dtype=float)
    delta = parameters.delta
    return np.asarray(
        [
            p / delta,
            (cubic_f(u) - v) / delta,
            q,
            parameters.epsilon * (u - parameters.a),
        ],
        dtype=float,
    )


def fast_field_y(state: Array, parameters: BridgeParameters) -> Array:
    """Fast-y stationary field (7), evaluated columnwise."""

    u, p, v, q = np.asarray(state, dtype=float)
    delta = parameters.delta
    return np.asarray(
        [p, cubic_f(u) - v, delta * q, parameters.epsilon * delta * (u - parameters.a)],
        dtype=float,
    )


def physical_first_integral(state: Array, parameters: BridgeParameters) -> Array:
    u, p, v, q = np.asarray(state, dtype=float)
    return np.asarray(
        0.5 * (parameters.epsilon * p**2 - q**2)
        - parameters.epsilon * (cubic_F(u) + (parameters.a - u) * v),
        dtype=float,
    )


def bridge_diagnostics(
    xi: Array, central_state: Array, parameters: BridgeParameters
) -> dict[str, Any]:
    """Compare clocks, vector fields, energy, and action on one orbit sample."""

    xi = np.asarray(xi, dtype=float)
    state = np.asarray(central_state, dtype=float)
    if xi.ndim != 1 or state.shape != (4, xi.size):
        raise ValueError("expected xi.shape=(N,) and state.shape=(4,N)")
    physical = central_to_physical(state, parameters)
    roundtrip = physical_to_central(physical, parameters)

    central_rhs = vdp_field(
        parameters.r, parameters.a2, parameters.epsilon
    )(xi, state)
    scale = np.asarray(
        [
            -np.sqrt(parameters.epsilon) * parameters.r**2,
            -parameters.epsilon**0.75 * parameters.r**3,
            -parameters.epsilon * parameters.r**4,
            -parameters.epsilon**1.25 * parameters.r**3,
        ]
    )[:, None]
    pushed_rhs = scale * central_rhs
    physical_rhs_in_xi = (
        physical_field_x(physical, parameters) * parameters.x_per_xi
    )
    fast_rhs_in_xi = (
        fast_field_y(physical, parameters)
        * (parameters.x_per_xi / parameters.delta)
    )

    central_energy = vdp_hamiltonian(
        state, parameters.r, parameters.a2, parameters.epsilon
    )
    physical_energy = physical_first_integral(physical, parameters)
    equilibrium_energy = -parameters.epsilon * float(cubic_F(parameters.a))
    physical_shifted = -physical_energy + equilibrium_energy

    central_density = state[1] * central_rhs[0] - state[3] * central_rhs[2]
    physical_density_x = (
        parameters.epsilon * physical[1] * physical_field_x(physical, parameters)[0]
        - physical[3] * physical_field_x(physical, parameters)[2] / parameters.delta
    )
    central_action = cumulative_trapezoid(central_density, xi, initial=0.0)
    physical_x = parameters.x_per_xi * xi
    physical_action = cumulative_trapezoid(
        physical_density_x, physical_x, initial=0.0
    )
    scaled_central_action = parameters.action_scale * central_action

    return {
        "evidence_status": "EXACT/DERIVED formulas with COMPUTED/QA orbit evaluation",
        "roundtrip_state_defect_inf": float(np.max(np.abs(roundtrip - state))),
        "physical_pushforward_defect_inf": float(
            np.max(np.abs(pushed_rhs - physical_rhs_in_xi))
        ),
        "fast_clock_pushforward_defect_inf": float(
            np.max(np.abs(pushed_rhs - fast_rhs_in_xi))
        ),
        "energy_scaling_defect_inf": float(
            np.max(
                np.abs(
                    physical_shifted
                    - parameters.energy_scale * central_energy
                )
            )
        ),
        "central_energy_drift": float(np.ptp(central_energy)),
        "physical_energy_drift": float(np.ptp(physical_energy)),
        "action_scaling_endpoint_defect": float(
            abs(physical_action[-1] - scaled_central_action[-1])
        ),
        "central_action_endpoint": float(central_action[-1]),
        "physical_action_endpoint": float(physical_action[-1]),
        "scaled_central_action_endpoint": float(scaled_central_action[-1]),
        "clock_relations": {
            "delta": parameters.delta,
            "x_per_y": parameters.delta,
            "x_per_xi": parameters.x_per_xi,
            "xi_per_x": 1.0 / parameters.x_per_xi,
        },
    }


def bridge_refinement_diagnostics(
    initial_central_state: Array,
    parameters: BridgeParameters,
    *,
    xi_span: tuple[float, float] = (-3.0, 3.0),
    tolerances: tuple[float, ...] = (1.0e-5, 1.0e-7, 1.0e-9, 1.0e-11),
    points: int = 1601,
) -> dict[str, Any]:
    """Independently integrate the central and physical clocks on a ladder."""

    initial = np.asarray(initial_central_state, dtype=float)
    if initial.shape != (4,):
        raise ValueError("initial_central_state must have shape (4,)")
    if points < 101:
        raise ValueError("points must be at least 101")
    xi = np.linspace(float(xi_span[0]), float(xi_span[1]), points)
    physical_x = parameters.x_per_xi * xi
    initial_physical = central_to_physical(initial, parameters)
    rows: list[dict[str, float | bool]] = []

    for level, tolerance in enumerate(tolerances):
        max_step_xi = 0.5 / (2.0**level)
        central_integration = solve_ivp(
            lambda time, state: vdp_field(
                parameters.r, parameters.a2, parameters.epsilon
            )(np.array([time]), state[:, None])[:, 0],
            xi_span,
            initial,
            t_eval=xi,
            method="DOP853",
            rtol=tolerance,
            atol=0.01 * tolerance,
            max_step=max_step_xi,
        )
        physical_integration = solve_ivp(
            lambda _time, state: physical_field_x(state, parameters),
            (float(physical_x[0]), float(physical_x[-1])),
            initial_physical,
            t_eval=physical_x,
            method="DOP853",
            rtol=tolerance,
            atol=0.01 * tolerance,
            max_step=max_step_xi * parameters.x_per_xi,
        )
        if not central_integration.success or not physical_integration.success:
            raise RuntimeError("independent V1 bridge integration failed")
        central_from_physical = physical_to_central(
            physical_integration.y, parameters
        )
        state_defect = central_from_physical - central_integration.y
        central_report = bridge_diagnostics(
            xi, central_integration.y, parameters
        )

        physical_rhs = physical_field_x(physical_integration.y, parameters)
        physical_density = (
            parameters.epsilon
            * physical_integration.y[1]
            * physical_rhs[0]
            - physical_integration.y[3] * physical_rhs[2] / parameters.delta
        )
        physical_action = cumulative_trapezoid(
            physical_density, physical_x, initial=0.0
        )
        central_rhs = vdp_field(
            parameters.r, parameters.a2, parameters.epsilon
        )(xi, central_integration.y)
        central_density = (
            central_integration.y[1] * central_rhs[0]
            - central_integration.y[3] * central_rhs[2]
        )
        central_action = cumulative_trapezoid(
            central_density, xi, initial=0.0
        )
        rows.append(
            {
                "tolerance": float(tolerance),
                "max_step_xi": float(max_step_xi),
                "central_solver_success": bool(central_integration.success),
                "physical_solver_success": bool(physical_integration.success),
                "trajectory_state_defect_inf": float(
                    np.max(np.abs(state_defect))
                ),
                "endpoint_state_defect_inf": float(
                    np.max(np.abs(state_defect[:, -1]))
                ),
                "energy_scaling_defect_inf": float(
                    central_report["energy_scaling_defect_inf"]
                ),
                "action_endpoint_defect": float(
                    abs(
                        physical_action[-1]
                        - parameters.action_scale * central_action[-1]
                    )
                ),
            }
        )
    return {
        "evidence_status": "COMPUTED/QA independent physical/central integrations",
        "xi_span": [float(xi_span[0]), float(xi_span[1])],
        "rows": rows,
    }


__all__ = [
    "BridgeParameters",
    "bridge_diagnostics",
    "bridge_refinement_diagnostics",
    "central_to_physical",
    "cubic_F",
    "cubic_f",
    "fast_field_y",
    "physical_field_x",
    "physical_first_integral",
    "physical_to_central",
]
