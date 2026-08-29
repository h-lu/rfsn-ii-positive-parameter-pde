"""Boundary-selected finite-r saddle-slow and coincidence candidates.

This module replaces the formal-entry projection used by
``vdp_canard_splitting_scout`` with solutions of the exact central-chart
vector field selected by the Appendix-A.2 boundary-value construction of
Vo--Doelman--Kaper.  It has three deliberately separate outputs.

1.  A primary finite-r saddle-slow representative is continued from the
    outside A.2 family to its reversible fold representative.  Its crossing
    of the fixed section ``u2=16`` is an actual point of the computed BVP
    orbit, not a projected formal jet.
2.  A frozen-outer-boundary A.3-compatible half-orbit treats the flight time
    and ``a2`` as unknowns and imposes zero energy together with a central
    reverser endpoint.  This selects the central-localized primary candidate
    near the Appendix-C formal canard.
3.  The endpoint family through the reversible A.2 representative is
    continued
    along its linearized family tangent by a weighted pseudo-arclength
    condition.  The boundary condition ``H2=0`` is then imposed in a
    collocation solve and the resulting first increasing ``p2=0`` hit is
    recorded.

The second object is the strongest computed candidate, but it is still a
*finite-boundary* BVP object rather than the intrinsic
``W^cu(P_-)=W^cs(P_+)`` coincidence required by Issue #13.  The third object
is retained as a branch-selection warning: its zero-energy root is reversible
but misses the published central canard by an order-one amount.  These
distinctions are part of the generated report.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import cumulative_trapezoid, solve_bvp
from scipy.optimize import brentq

try:
    from numerics.vdp_canard_splitting_scout import (
        central_hamiltonian,
        formal_canard_jet,
    )
except ModuleNotFoundError:  # Direct ``python numerics/<script>.py`` execution.
    from vdp_canard_splitting_scout import (  # type: ignore[no-redef]
        central_hamiltonian,
        formal_canard_jet,
    )


Array = NDArray[np.float64]
CONFIG_PATH = (
    Path(__file__).resolve().parent
    / "config"
    / "vdp_canard_slow_trace_v1.json"
)

EVIDENCE_STATUS = (
    "COMPUTED/E1_FINITE_BOUNDARY_A3_COMPATIBLE_PRIMARY_CANDIDATE"
)
ENTRY_STATUS = "COMPUTED/E1_BOUNDARY_SELECTED_FINITE_R_SADDLE_SLOW_ENTRY"
COINCIDENCE_STATUS = (
    "COMPUTED/E1_BOUNDARY_SELECTED_ZERO_ENERGY_BVP_CANDIDATE"
)
A3_CANDIDATE_STATUS = EVIDENCE_STATUS
MAXIMAL_CANARD_STATUS = (
    "INCONCLUSIVE_INTRINSIC_SLOW_TRACE_AND_TARGET_BRANCH_NOT_VALIDATED"
)
C1_STATUS = "INCOMPLETE_BOUNDARY_SELECTED_REPRESENTATIVE_ONLY"
C2_STATUS = "INCOMPLETE_NO_SIMPLE_ZERO_GRAPH_IN_A2"


@dataclass(frozen=True)
class SlowTraceConfiguration:
    epsilon: float
    r: float
    a2: float
    outer_q_boundary: float
    a3_outer_u2_boundary: float
    a3_candidate_a2_interval: tuple[float, float]
    entry_section_u2: float
    natural_start_u2: float
    natural_geometric: tuple[float, float, int]
    natural_linear_middle: tuple[float, float, int]
    natural_linear_outer: tuple[float, float, int]
    terminal_q2_continuation: tuple[float, ...]
    half_mesh_points: int
    full_mesh_points: int
    continuation_tolerance: float
    kernel_tolerance: float
    root_tolerance: float
    max_nodes: int
    pseudo_arclength_step: float
    pseudo_arclength_max_steps: int
    central_localization_u2_tolerance: float
    central_localization_v2_tolerance: float

    @property
    def natural_u2_targets(self) -> Array:
        return np.concatenate(
            (
                np.geomspace(*self.natural_geometric),
                np.linspace(*self.natural_linear_middle),
                np.linspace(*self.natural_linear_outer),
            )
        )


def load_configuration(path: Path = CONFIG_PATH) -> SlowTraceConfiguration:
    data = json.loads(path.read_text(encoding="utf-8"))
    continuation = data["natural_u2_continuation"]

    def triple(values: list[float | int]) -> tuple[float, float, int]:
        return float(values[0]), float(values[1]), int(values[2])

    return SlowTraceConfiguration(
        epsilon=float(data["epsilon"]),
        r=float(data["r"]),
        a2=float(data["a2"]),
        outer_q_boundary=float(data["outer_q_boundary"]),
        a3_outer_u2_boundary=float(data["a3_outer_u2_boundary"]),
        a3_candidate_a2_interval=tuple(
            float(value) for value in data["a3_candidate_a2_interval"]
        ),
        entry_section_u2=float(data["entry_section_u2"]),
        natural_start_u2=float(data["natural_start_u2"]),
        natural_geometric=triple(continuation["geometric"]),
        natural_linear_middle=triple(continuation["linear_middle"]),
        natural_linear_outer=triple(continuation["linear_outer"]),
        terminal_q2_continuation=tuple(
            float(value) for value in data["terminal_q2_continuation"]
        ),
        half_mesh_points=int(data["half_mesh_points"]),
        full_mesh_points=int(data["full_mesh_points"]),
        continuation_tolerance=float(data["continuation_tolerance"]),
        kernel_tolerance=float(data["kernel_tolerance"]),
        root_tolerance=float(data["root_tolerance"]),
        max_nodes=int(data["max_nodes"]),
        pseudo_arclength_step=float(data["pseudo_arclength_step"]),
        pseudo_arclength_max_steps=int(
            data["pseudo_arclength_max_steps"]
        ),
        central_localization_u2_tolerance=float(
            data["central_localization_u2_tolerance"]
        ),
        central_localization_v2_tolerance=float(
            data["central_localization_v2_tolerance"]
        ),
    )


def critical_graph(u: Array | float, *, r: float) -> Array | float:
    """The translated K2 p-nullcline ``v2=u2^2+r^2 u2^3/3``."""

    return u * u + (r * r / 3.0) * u**3


def critical_graph_derivative(u: Array | float, *, r: float) -> Array | float:
    return 2.0 * u + r * r * u * u


def vectorized_central_field(
    state: Array, *, r: float, a2: float
) -> Array:
    u, p, v, q = state
    return np.vstack(
        (
            p,
            critical_graph(u, r=r) - v,
            q,
            u - r * a2,
        )
    )


def _hamiltonian(
    state: Array,
    configuration: SlowTraceConfiguration,
    *,
    a2: float | None = None,
) -> float:
    return central_hamiltonian(
        state,
        r=configuration.r,
        a2=configuration.a2 if a2 is None else a2,
    )


def _solve_or_raise(*args: Any, label: str, **kwargs: Any) -> Any:
    solution = solve_bvp(*args, **kwargs)
    if not solution.success:
        raise RuntimeError(f"{label}: {solution.message}")
    return solution


def _outside_half(configuration: SlowTraceConfiguration) -> Any:
    r = configuration.r
    a2 = configuration.a2
    q_boundary = configuration.outer_q_boundary
    mesh = np.linspace(0.0, 1.0, configuration.half_mesh_points)

    def field(_s: Array, state: Array, parameter: Array) -> Array:
        return parameter[0] * vectorized_central_field(state, r=r, a2=a2)

    def natural_boundary(u_start: float) -> Callable[[Array, Array, Array], Array]:
        def boundary(left: Array, right: Array, _parameter: Array) -> Array:
            return np.asarray(
                [
                    left[2] - critical_graph(left[0], r=r),
                    left[3] - q_boundary,
                    left[0] - u_start,
                    right[1],
                    right[0],
                ]
            )

        return boundary

    def terminal_q_boundary(
        q_terminal: float,
    ) -> Callable[[Array, Array, Array], Array]:
        def boundary(left: Array, right: Array, _parameter: Array) -> Array:
            return np.asarray(
                [
                    left[2] - critical_graph(left[0], r=r),
                    left[3] - q_boundary,
                    right[1],
                    right[0],
                    right[3] - q_terminal,
                ]
            )

        return boundary

    u_start = configuration.natural_start_u2
    u_guess = u_start * (1.0 - mesh)
    initial = np.vstack(
        (
            u_guess,
            -u_start * np.ones_like(mesh),
            critical_graph(u_guess, r=r),
            q_boundary * np.ones_like(mesh),
        )
    )
    solution = _solve_or_raise(
        field,
        natural_boundary(u_start),
        mesh,
        initial,
        p=[0.03],
        tol=configuration.continuation_tolerance,
        max_nodes=configuration.max_nodes,
        label="initial outside A.2 solve",
    )
    for target in configuration.natural_u2_targets:
        solution = _solve_or_raise(
            field,
            natural_boundary(float(target)),
            mesh,
            solution.sol(mesh),
            p=solution.p,
            tol=configuration.continuation_tolerance,
            max_nodes=configuration.max_nodes,
            label=f"outside A.2 natural continuation to u2={target}",
        )
    for target in configuration.terminal_q2_continuation:
        solution = _solve_or_raise(
            field,
            terminal_q_boundary(float(target)),
            mesh,
            solution.sol(mesh),
            p=solution.p,
            tol=configuration.continuation_tolerance,
            max_nodes=configuration.max_nodes,
            label=f"outside A.2 terminal-q continuation to q2={target}",
        )
    return solution


def _localized_a3_half(
    configuration: SlowTraceConfiguration, initialization_half: Any
) -> Any:
    """Solve the frozen-boundary A.3-compatible zero-energy half BVP."""

    r = configuration.r
    outer_u = configuration.a3_outer_u2_boundary
    outer_q = configuration.outer_q_boundary
    mesh = np.linspace(0.0, 1.0, configuration.half_mesh_points)

    def field(_s: Array, state: Array, parameter: Array) -> Array:
        flight_time, a2 = parameter
        return flight_time * vectorized_central_field(
            state, r=r, a2=float(a2)
        )

    def boundary(left: Array, right: Array, parameter: Array) -> Array:
        a2 = float(parameter[1])
        return np.asarray(
            [
                left[0] - outer_u,
                left[2] - critical_graph(left[0], r=r),
                left[3] - outer_q,
                right[1],
                right[3],
                central_hamiltonian(left, r=r, a2=a2),
            ]
        )

    solution = _solve_or_raise(
        field,
        boundary,
        mesh,
        initialization_half.sol(mesh),
        p=[float(initialization_half.p[0]), configuration.a2],
        tol=configuration.root_tolerance,
        max_nodes=configuration.max_nodes,
        label="frozen-boundary A.3-compatible half-orbit candidate",
    )
    a2_candidate = float(solution.p[1])
    lower, upper = configuration.a3_candidate_a2_interval
    if not lower <= a2_candidate <= upper:
        raise RuntimeError(
            "A.3-compatible candidate left its frozen posterior branch gate: "
            f"{a2_candidate} not in [{lower}, {upper}]"
        )
    return solution


def _fixed_section_state(solution: Any, section_u: float) -> tuple[float, Array]:
    sample = np.linspace(0.0, 1.0, 4001)
    values = solution.sol(sample)[0] - section_u
    crossings = np.flatnonzero((values[:-1] > 0.0) & (values[1:] <= 0.0))
    if crossings.size == 0:
        raise RuntimeError(f"no descending u2={section_u} section crossing")
    index = int(crossings[0])
    section_s = float(
        brentq(
            lambda value: float(solution.sol(value)[0] - section_u),
            float(sample[index]),
            float(sample[index + 1]),
        )
    )
    return section_s, np.asarray(solution.sol(section_s), dtype=np.float64)


def _reflected_primary(configuration: SlowTraceConfiguration, half: Any) -> Any:
    r = configuration.r
    a2 = configuration.a2
    left_u = float(half.y[0, 0])
    mesh = np.linspace(0.0, 1.0, configuration.full_mesh_points)
    reflected = np.empty((4, mesh.size))
    first = mesh <= 0.5
    reflected[:, first] = half.sol(2.0 * mesh[first])
    second = half.sol(2.0 * (1.0 - mesh[~first]))
    second[[1, 3]] *= -1.0
    reflected[:, ~first] = second

    def field(_s: Array, state: Array, parameter: Array) -> Array:
        return parameter[0] * vectorized_central_field(state, r=r, a2=a2)

    def boundary(left: Array, right: Array, _parameter: Array) -> Array:
        return np.asarray(
            [
                left[0] - left_u,
                left[2] - critical_graph(left[0], r=r),
                right[2] - critical_graph(right[0], r=r),
                left[3] + right[3],
                left[1] + right[1],
            ]
        )

    return _solve_or_raise(
        field,
        boundary,
        mesh,
        reflected,
        p=[2.0 * float(half.p[0])],
        tol=configuration.continuation_tolerance,
        max_nodes=configuration.max_nodes,
        label="reflected primary A.2 solve",
    )


@dataclass
class _Reference:
    period: float
    evaluate: Callable[[Array | float], Array]


def _reference(solution: Any) -> _Reference:
    return _Reference(
        period=float(solution.p[0]),
        evaluate=lambda value: np.asarray(solution.sol(value)[:4]),
    )


def _energy_kernel(
    configuration: SlowTraceConfiguration, primary: Any
) -> tuple[Callable[[Array | float], Array], float, dict[str, Any]]:
    """Return the normalized tangent of the endpoint family at the A.2 orbit."""

    r = configuration.r
    a2 = configuration.a2
    period = float(primary.p[0])
    left_u = float(primary.y[0, 0])
    mesh = np.linspace(0.0, 1.0, configuration.full_mesh_points)

    def linear_field(s: Array, tangent: Array, parameter: Array) -> Array:
        base = primary.sol(s)
        period_tangent = float(parameter[0])
        result = np.empty_like(tangent)
        for index, u_value in enumerate(base[0]):
            derivative = np.asarray(
                [
                    [0.0, 1.0, 0.0, 0.0],
                    [
                        critical_graph_derivative(u_value, r=r),
                        0.0,
                        -1.0,
                        0.0,
                    ],
                    [0.0, 0.0, 0.0, 1.0],
                    [1.0, 0.0, 0.0, 0.0],
                ]
            )
            result[:, index] = (
                period * derivative @ tangent[:, index]
                + period_tangent
                * vectorized_central_field(
                    base[:, index : index + 1], r=r, a2=a2
                )[:, 0]
            )
        return result

    def boundary(left: Array, right: Array, _parameter: Array) -> Array:
        return np.asarray(
            [
                left[0],
                left[2]
                - critical_graph_derivative(left_u, r=r) * left[0],
                right[2]
                - critical_graph_derivative(primary.y[0, -1], r=r)
                * right[0],
                left[3] + right[3],
                right[3] - left[3] - 1.0,
            ]
        )

    guess = np.zeros((4, mesh.size))
    guess[1] = 0.01
    guess[3] = mesh - 0.5
    tangent = _solve_or_raise(
        linear_field,
        boundary,
        mesh,
        guess,
        p=[0.0],
        tol=configuration.kernel_tolerance,
        max_nodes=configuration.max_nodes,
        label="A.2 endpoint-family tangent",
    )

    state_scales = np.asarray(
        [
            left_u,
            2.3,
            critical_graph(left_u, r=r),
            abs(configuration.outer_q_boundary),
        ]
    )
    state_weights = 1.0 / state_scales**2
    period_weight = 1.0 / period**2
    sample = np.linspace(0.0, 1.0, 2001)
    raw = tangent.sol(sample)
    raw_period = float(tangent.p[0])
    norm = float(
        np.sqrt(
            np.trapezoid(
                np.sum(state_weights[:, None] * raw * raw, axis=0), sample
            )
            + period_weight * raw_period**2
        )
    )
    return (
        lambda value: np.asarray(tangent.sol(value)) / norm,
        raw_period / norm,
        {
            "raw_period_component": raw_period,
            "weighted_norm": norm,
            "normalized_period_component": raw_period / norm,
            "normalization": "q2(1)-q2(0)=1 before weighted normalization",
            "state_scales": state_scales.tolist(),
            "max_abs_raw_state_components": np.max(
                np.abs(tangent.y), axis=1
            ).tolist(),
        },
    )


def _continue_to_zero_energy(
    configuration: SlowTraceConfiguration,
    primary: Any,
    tangent: Callable[[Array | float], Array],
    period_tangent: float,
) -> tuple[Any, list[dict[str, float]], tuple[_Reference, _Reference]]:
    r = configuration.r
    a2 = configuration.a2
    left_u = float(primary.y[0, 0])
    mesh = np.linspace(0.0, 1.0, configuration.full_mesh_points)
    sample = np.linspace(0.0, 1.0, 2001)
    state_scales = np.asarray(
        [
            left_u,
            2.3,
            critical_graph(left_u, r=r),
            abs(configuration.outer_q_boundary),
        ]
    )
    state_weights = 1.0 / state_scales**2
    period_weight = 1.0 / float(primary.p[0]) ** 2

    def boundary_four(left: Array, right: Array) -> Array:
        return np.asarray(
            [
                left[0] - left_u,
                left[2] - critical_graph(left[0], r=r),
                right[2] - critical_graph(right[0], r=r),
                left[3] + right[3],
            ]
        )

    def pseudo_step(
        reference: _Reference,
        tangent_function: Callable[[Array | float], Array],
        tangent_period: float,
    ) -> Any:
        step = configuration.pseudo_arclength_step
        tangent_mesh = tangent_function(mesh)
        reference_mesh = reference.evaluate(mesh)
        predicted = reference_mesh + step * tangent_mesh
        predicted_period = reference.period + step * tangent_period
        density = np.sum(
            state_weights[:, None]
            * (predicted - reference_mesh)
            * tangent_mesh,
            axis=0,
        )
        auxiliary = np.r_[0.0, cumulative_trapezoid(density, mesh)]
        initial = np.vstack((predicted, auxiliary))

        def field(s: Array, state: Array, parameter: Array) -> Array:
            orbit = state[:4]
            result = np.empty_like(state)
            result[:4] = parameter[0] * vectorized_central_field(
                orbit, r=r, a2=a2
            )
            result[4] = np.sum(
                state_weights[:, None]
                * (orbit - reference.evaluate(s))
                * tangent_function(s),
                axis=0,
            )
            return result

        def boundary(left: Array, right: Array, parameter: Array) -> Array:
            return np.r_[
                boundary_four(left[:4], right[:4]),
                left[4],
                right[4]
                + period_weight
                * (parameter[0] - reference.period)
                * tangent_period
                - step,
            ]

        return _solve_or_raise(
            field,
            boundary,
            mesh,
            initial,
            p=[predicted_period],
            tol=2.0e-5,
            max_nodes=configuration.max_nodes,
            label="A.2 pseudo-arclength step",
        )

    previous = _reference(primary)
    tangent_function = tangent
    tangent_period = period_tangent
    continuation: list[dict[str, float]] = []
    negative: _Reference | None = None
    positive: _Reference | None = None

    for index in range(1, configuration.pseudo_arclength_max_steps + 1):
        augmented = pseudo_step(previous, tangent_function, tangent_period)
        current = _reference(augmented)
        left = current.evaluate(0.0)
        energy = _hamiltonian(left, configuration)
        continuation.append(
            {
                "step": float(index),
                "period": current.period,
                "hamiltonian": energy,
                "left_q2": float(left[3]),
                "max_interval_rms_relative_residual": float(
                    np.max(augmented.rms_residuals)
                ),
            }
        )
        if energy < 0.0:
            negative = current
        elif negative is not None:
            positive = current
            break

        difference = current.evaluate(sample) - previous.evaluate(sample)
        period_difference = current.period - previous.period
        norm = float(
            np.sqrt(
                np.trapezoid(
                    np.sum(
                        state_weights[:, None] * difference * difference,
                        axis=0,
                    ),
                    sample,
                )
                + period_weight * period_difference**2
            )
        )
        old = previous
        tangent_function = (
            lambda value, current=current, old=old, norm=norm: (
                current.evaluate(value) - old.evaluate(value)
            )
            / norm
        )
        tangent_period = period_difference / norm
        previous = current

    if negative is None or positive is None:
        raise RuntimeError("pseudo-arclength continuation did not bracket H2=0")

    negative_energy = _hamiltonian(negative.evaluate(0.0), configuration)
    positive_energy = _hamiltonian(positive.evaluate(0.0), configuration)
    fraction = -negative_energy / (positive_energy - negative_energy)
    guess = (
        (1.0 - fraction) * negative.evaluate(mesh)
        + fraction * positive.evaluate(mesh)
    )
    period_guess = (
        (1.0 - fraction) * negative.period + fraction * positive.period
    )

    def root_field(_s: Array, state: Array, parameter: Array) -> Array:
        return parameter[0] * vectorized_central_field(state, r=r, a2=a2)

    def root_boundary(left: Array, right: Array, _parameter: Array) -> Array:
        return np.r_[
            boundary_four(left, right),
            _hamiltonian(left, configuration),
        ]

    root = _solve_or_raise(
        root_field,
        root_boundary,
        mesh,
        guess,
        p=[period_guess],
        tol=configuration.root_tolerance,
        max_nodes=configuration.max_nodes,
        label="A.2 H2=0 collocation candidate",
    )
    return root, continuation, (negative, positive)


def _first_increasing_p_hit(
    solution: Any, *, start_s: float
) -> tuple[float, Array]:
    sample = np.linspace(start_s, 1.0, 6001)
    p = solution.sol(sample)[1]
    crossings = np.flatnonzero((p[:-1] < 0.0) & (p[1:] >= 0.0))
    if crossings.size == 0:
        raise RuntimeError("no increasing p2=0 hit after the entry section")
    index = int(crossings[0])
    hit_s = float(
        brentq(
            lambda value: float(solution.sol(value)[1]),
            float(sample[index]),
            float(sample[index + 1]),
        )
    )
    return hit_s, np.asarray(solution.sol(hit_s), dtype=np.float64)


def _state_record(state: Array) -> list[float]:
    return [float(value) for value in state]


def _reflected_half_states(solution: Any, sample: Array) -> Array:
    """Reflect one half orbit into a full normalized reversible segment."""

    result = np.empty((4, sample.size), dtype=np.float64)
    first = sample <= 0.5
    result[:, first] = solution.sol(2.0 * sample[first])
    result[:, ~first] = solution.sol(2.0 * (1.0 - sample[~first]))
    result[1, ~first] *= -1.0
    result[3, ~first] *= -1.0
    return result


def compute_candidate(
    configuration: SlowTraceConfiguration | None = None,
) -> tuple[dict[str, Any], dict[str, Array]]:
    config = configuration or load_configuration()
    if config.epsilon != 1.0:
        raise ValueError("the v1 A.2 computation is frozen to epsilon=1")

    half = _outside_half(config)
    a3_half = _localized_a3_half(config, half)
    primary = _reflected_primary(config, half)
    half_entry_s, half_entry = _fixed_section_state(
        half, config.entry_section_u2
    )
    primary_entry_s, primary_entry = _fixed_section_state(
        primary, config.entry_section_u2
    )
    tangent, period_tangent, kernel_record = _energy_kernel(config, primary)
    root, continuation, bracket = _continue_to_zero_energy(
        config, primary, tangent, period_tangent
    )
    entry_s, entry = _fixed_section_state(root, config.entry_section_u2)
    hit_s, hit = _first_increasing_p_hit(root, start_s=entry_s)

    sample = np.linspace(0.0, 1.0, 4001)
    root_states = root.sol(sample)
    energies = np.asarray(
        [_hamiltonian(root_states[:, index], config) for index in range(sample.size)]
    )
    midpoint = np.asarray(root.sol(0.5), dtype=np.float64)
    formal_midpoint = formal_canard_jet(
        0.0, r=config.r, a2=config.a2, order=3
    )
    central_difference = midpoint - formal_midpoint
    localization_passes = bool(
        abs(central_difference[0])
        <= config.central_localization_u2_tolerance
        and abs(central_difference[2])
        <= config.central_localization_v2_tolerance
    )
    right = np.asarray(root.y[:, -1], dtype=np.float64)
    left = np.asarray(root.y[:, 0], dtype=np.float64)
    field_at_hit = vectorized_central_field(
        hit[:, None], r=config.r, a2=config.a2
    )[:, 0]
    negative, positive = bracket

    a3_a2 = float(a3_half.p[1])
    a3_half_time = float(a3_half.p[0])
    a3_sample = np.linspace(0.0, 1.0, 4001)
    a3_states = np.asarray(a3_half.sol(a3_sample), dtype=np.float64)
    a3_energies = np.asarray(
        [
            _hamiltonian(a3_states[:, index], config, a2=a3_a2)
            for index in range(a3_sample.size)
        ]
    )
    a3_left = np.asarray(a3_half.sol(0.0), dtype=np.float64)
    a3_right = np.asarray(a3_half.sol(1.0), dtype=np.float64)
    a3_boundary_residuals = {
        "left_u2_minus_frozen": float(
            a3_left[0] - config.a3_outer_u2_boundary
        ),
        "left_v2_minus_p_nullcline": float(
            a3_left[2] - critical_graph(a3_left[0], r=config.r)
        ),
        "left_q2_minus_outer": float(
            a3_left[3] - config.outer_q_boundary
        ),
        "right_p2": float(a3_right[1]),
        "right_q2": float(a3_right[3]),
        "left_hamiltonian": _hamiltonian(
            a3_left, config, a2=a3_a2
        ),
    }
    a3_boundary_residual_inf = max(
        abs(value) for value in a3_boundary_residuals.values()
    )
    a3_field_at_right = vectorized_central_field(
        a3_right[:, None], r=config.r, a2=a3_a2
    )[:, 0]
    a3_open = a3_states[:, 1:-1]
    a3_open_max_p = float(np.max(a3_open[1]))
    a3_open_max_q = float(np.max(a3_open[3]))
    a3_no_loop_sample_pass = bool(
        a3_open_max_p < 0.0 and a3_open_max_q < 0.0
    )
    a3_formal = formal_canard_jet(
        0.0, r=config.r, a2=a3_a2, order=3
    )
    a3_formal_difference = a3_right - a3_formal
    a3_localization_passes = bool(
        abs(a3_formal_difference[0])
        <= config.central_localization_u2_tolerance
        and abs(a3_formal_difference[2])
        <= config.central_localization_v2_tolerance
    )
    a3_full_sample = np.linspace(0.0, 1.0, 4001)
    a3_full_states = _reflected_half_states(a3_half, a3_full_sample)
    reverser = np.asarray([1.0, -1.0, 1.0, -1.0])[:, None]
    a3_full_parity_residual = float(
        np.max(np.abs(a3_full_states - reverser * a3_full_states[:, ::-1]))
    )
    a3_midpoint = a3_full_states[:, a3_full_sample.size // 2]
    a3_midpoint_fix_residual = float(
        np.max(np.abs(a3_midpoint[[1, 3]]))
    )
    a3_endpoint_reverser_residual = float(
        np.max(
            np.abs(
                a3_full_states[:, -1]
                - reverser[:, 0] * a3_full_states[:, 0]
            )
        )
    )
    published_leading = -5.0 * config.r / 48.0

    report: dict[str, Any] = {
        "schema_version": "vdp-canard-slow-trace/2",
        "evidence_status": EVIDENCE_STATUS,
        "claim_bearing": False,
        "parameters": {
            "epsilon": config.epsilon,
            "r": config.r,
            "a2": config.a2,
            "a2_initial_guess": config.a2,
            "a2_candidate": a3_a2,
            "published_leading_a2": published_leading,
        },
        "exact_k2_field": [
            "u2'=p2",
            "p2'=u2^2-v2+r^2*u2^3/3",
            "v2'=q2",
            "q2'=u2-r*a2",
        ],
        "boundary_selection": {
            "method": (
                "published Appendix A.2 outside BVP followed by "
                "full-orbit boundary continuation through a reversible "
                "representative"
            ),
            "outer_q2": config.outer_q_boundary,
            "p_nullcline": "v2=u2^2+r^2*u2^3/3",
            "outside_right_boundary": ["p2=0", "u2=0"],
            "fixed_entry_section": f"u2={config.entry_section_u2}, p2<0, q2<0",
        },
        "a3_boundary_selection": {
            "method": (
                "A.3-compatible half-orbit with frozen Appendix-A.2 outer "
                "u2 coordinate and unknown (flight_time,a2)"
            ),
            "frozen_outer_u2": config.a3_outer_u2_boundary,
            "frozen_outer_q2": config.outer_q_boundary,
            "boundary_conditions": [
                "u2(left)=frozen_outer_u2",
                "v2(left)=u2(left)^2+r^2*u2(left)^3/3",
                "q2(left)=frozen_outer_q2",
                "p2(right)=0",
                "q2(right)=0",
                "H2(left;r,a2)=0",
            ],
            "unknown_parameters": ["half_flight_time", "a2"],
            "interpretation": (
                "The outer u2 value is frozen, not recomputed along the a2 "
                "solve. This selects a finite-boundary candidate and does "
                "not define an intrinsic slow manifold."
            ),
        },
        "primary_saddle_slow_representative": {
            "status": ENTRY_STATUS,
            "half_period": float(half.p[0]),
            "full_reflected_period": float(primary.p[0]),
            "left_state": _state_record(half.y[:, 0]),
            "fold_state": _state_record(half.y[:, -1]),
            "half_orbit_entry_section_s": half_entry_s,
            "half_orbit_entry_state": _state_record(half_entry),
            "full_reflected_orbit_entry_section_s": primary_entry_s,
            "entry_state": _state_record(primary_entry),
            "entry_hamiltonian": _hamiltonian(primary_entry, config),
            "interpretation": (
                "This point lies on a collocation solution of the exact "
                "finite-r field for the frozen finite-boundary A.2 BVP "
                "branch. The two stored section coordinates refer to the "
                "normalized half orbit and full reflected orbit, respectively. "
                "It is not on H2=0 and is not itself the Issue-13 entry trace."
            ),
        },
        "endpoint_family_tangent": kernel_record,
        "finite_boundary_a3_compatible_half_candidate": {
            "status": A3_CANDIDATE_STATUS,
            "half_flight_time": a3_half_time,
            "a2_candidate": a3_a2,
            "left_state": _state_record(a3_left),
            "reverser_state": _state_record(a3_right),
            "boundary_residuals": a3_boundary_residuals,
            "boundary_residual_inf": a3_boundary_residual_inf,
            "max_interval_rms_relative_residual": float(
                np.max(a3_half.rms_residuals)
            ),
            "hamiltonian_abs_at_left": abs(
                _hamiltonian(a3_left, config, a2=a3_a2)
            ),
            "hamiltonian_drift": float(np.ptp(a3_energies)),
            "u2_minus_r_a2_at_reverser": float(
                a3_right[0] - config.r * a3_a2
            ),
            "v2_plus_one_sixth_at_reverser": float(
                a3_right[2] + 1.0 / 6.0
            ),
            "event_p2_derivative": float(a3_field_at_right[1]),
            "open_half_max_p2": a3_open_max_p,
            "open_half_max_q2": a3_open_max_q,
            "no_loop_sample_pass": a3_no_loop_sample_pass,
            "formal_order_3_reverser_state": _state_record(a3_formal),
            "candidate_minus_formal_reverser": _state_record(
                a3_formal_difference
            ),
            "central_localization_diagnostic": {
                "u2_tolerance": config.central_localization_u2_tolerance,
                "v2_tolerance": config.central_localization_v2_tolerance,
                "passes": a3_localization_passes,
                "status": (
                    "PASSES_SAMPLED_FORMAL_LOCALIZATION_DIAGNOSTIC"
                    if a3_localization_passes
                    else "DOES_NOT_PASS_SAMPLED_FORMAL_LOCALIZATION_DIAGNOSTIC"
                ),
            },
            "a2_minus_published_leading": a3_a2 - published_leading,
            "scaled_r3_remainder_candidate": (
                a3_a2 - published_leading
            ) / config.r**3,
            "interpretation": (
                "Central-localized, sampled no-loop solution of the exact "
                "finite-r field with the six frozen-boundary A.3-compatible "
                "conditions. It is not an intrinsic Wcu/Wcs trace, a "
                "simple-zero graph, or a uniqueness result."
            ),
        },
        "reflected_a3_full_segment": {
            "total_flight_time": 2.0 * a3_half_time,
            "midpoint_fix_reverser_residual_inf": a3_midpoint_fix_residual,
            "endpoint_reverser_residual_inf": a3_endpoint_reverser_residual,
            "sampled_parity_residual_inf": a3_full_parity_residual,
            "interpretation": (
                "Exact algebraic reflection of the computed half segment; "
                "this is not called a periodic orbit or a period."
            ),
        },
        "zero_energy_coincidence_candidate": {
            "status": COINCIDENCE_STATUS,
            "role": "LEGACY_A2_ENDPOINT_FAMILY_WRONG_BRANCH_DIAGNOSTIC",
            "period": float(root.p[0]),
            "left_state": _state_record(left),
            "right_state": _state_record(right),
            "midpoint_state": _state_record(midpoint),
            "entry_section_s": entry_s,
            "entry_state": _state_record(entry),
            "entry_hamiltonian": _hamiltonian(entry, config),
            "first_increasing_p_zero_s": hit_s,
            "first_increasing_p_zero_state": _state_record(hit),
            "splitting_q2": float(hit[3]),
            "event_p2_derivative": float(field_at_hit[1]),
            "flight_time_entry_to_hit": float(
                (hit_s - entry_s) * root.p[0]
            ),
            "hamiltonian_abs_at_left": abs(_hamiltonian(left, config)),
            "hamiltonian_drift": float(np.ptp(energies)),
            "max_interval_rms_relative_residual": float(
                np.max(root.rms_residuals)
            ),
            "reversibility_residual_inf": float(
                np.max(
                    np.abs(
                        np.asarray(
                            [
                                left[0] - right[0],
                                left[1] + right[1],
                                left[2] - right[2],
                                left[3] + right[3],
                            ]
                        )
                    )
                )
            ),
            "hamiltonian_bracket": {
                "negative": _hamiltonian(
                    negative.evaluate(0.0), config
                ),
                "positive": _hamiltonian(
                    positive.evaluate(0.0), config
                ),
                "negative_period": negative.period,
                "positive_period": positive.period,
            },
        },
        "target_branch_diagnostic": {
            "role": "LEGACY_A2_ENDPOINT_FAMILY_WRONG_BRANCH_DIAGNOSTIC",
            "published_order_3_formal_midpoint": _state_record(formal_midpoint),
            "candidate_minus_formal_midpoint": _state_record(central_difference),
            "frozen_u2_tolerance": config.central_localization_u2_tolerance,
            "frozen_v2_tolerance": config.central_localization_v2_tolerance,
            "passes": localization_passes,
            "status": (
                "PASSES_LOCALIZATION_DIAGNOSTIC"
                if localization_passes
                else "DOES_NOT_PASS_RFSNII_CENTRAL_LOCALIZATION_DIAGNOSTIC"
            ),
            "interpretation": (
                "Failure is a branch-discrimination warning, not a rigorous "
                "separation theorem: the formal midpoint is asymptotic rather "
                "than an interval enclosure."
            ),
        },
        "continuation": continuation,
        "decision": {
            "C1_finite_parameter_saddle_slow_manifolds": C1_STATUS,
            "C2_coincidence_curve": C2_STATUS,
            "finite_parameter_maximal_canard_status": MAXIMAL_CANARD_STATUS,
            "current_sample_a2_zero_classification": "INCONCLUSIVE",
            "surrogate_upgrade": (
                "A frozen-boundary A.3-compatible half BVP now solves for "
                "(T,a2), imposes H2=0 and p2=q2=0 at the reverser, and lands "
                "on the Appendix-C central branch. It remains a finite-"
                "boundary candidate rather than an intrinsic Wcu/Wcs trace."
            ),
            "next_mathematical_object": (
                "First promote the frozen-boundary root with a CAPD "
                "multiple-shooting/Poincare enclosure on p2=0. For intrinsic "
                "C1/C2, anchor a Wcu disk at the equator, transport its H2=0 "
                "trace through K1-K2, and validate the primary no-loop simple-"
                "zero tube as a function of (r,a2)."
            ),
        },
        "nonclaims": [
            (
                "The finite A.2 boundary representative is not a proved "
                "intrinsic saddle slow manifold."
            ),
            (
                "The zero-energy BVP candidate is not identified with the "
                "Lemma-6.4 maximal canard."
            ),
            (
                "The A.3-compatible candidate depends on one frozen outer "
                "boundary coordinate and is not a boundary-independent trace."
            ),
            "The localization diagnostic is not an interval separation result.",
            "No simple-zero a2,c(r) graph or parameter derivative is validated.",
            (
                "No classification of a2=0 or connection to the frozen "
                "high-winding edge is made."
            ),
            "No interval arithmetic is used.",
        ],
    }
    primary_sample = np.unique(np.r_[sample, primary_entry_s])
    arrays = {
        "s": sample,
        "zero_energy_states": root_states,
        "zero_energy_hamiltonian": energies,
        "primary_s": primary_sample,
        "primary_states": primary.sol(primary_sample),
        "continuation_period": np.asarray(
            [row["period"] for row in continuation]
        ),
        "continuation_hamiltonian": np.asarray(
            [row["hamiltonian"] for row in continuation]
        ),
        "a3_half_s": a3_sample,
        "a3_half_states": a3_states,
        "a3_half_hamiltonian": a3_energies,
        "a3_full_s": a3_full_sample,
        "a3_full_states": a3_full_states,
    }
    return report, arrays


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent
        / "results"
        / "vdp_canard_slow_trace"
        / "fixed_r_candidate.json",
    )
    parser.add_argument(
        "--arrays",
        type=Path,
        default=Path(__file__).resolve().parent
        / "results"
        / "vdp_canard_slow_trace"
        / "fixed_r_candidate.npz",
    )
    arguments = parser.parse_args()
    report, arrays = compute_candidate()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    arguments.arrays.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(arguments.arrays, **arrays)
    print(json.dumps(report["decision"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
