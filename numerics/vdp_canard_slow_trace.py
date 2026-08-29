"""Boundary-selected finite-r saddle-slow and coincidence candidates.

This module replaces the formal-entry projection used by
``vdp_canard_splitting_scout`` with solutions of the exact central-chart
vector field selected by the Appendix-A.2 boundary-value construction of
Vo--Doelman--Kaper.  It has two deliberately separate outputs.

1.  A primary finite-r saddle-slow representative is continued from the
    outside A.2 family to its reversible fold representative.  Its crossing
    of the fixed section ``u2=16`` is an actual point of the computed BVP
    orbit, not a projected formal jet.
2.  The endpoint family through that reversible representative is continued
    along its linearized family tangent by a weighted pseudo-arclength
    condition.  The boundary condition ``H2=0`` is then imposed in a
    collocation solve and the resulting first increasing ``p2=0`` hit is
    recorded.

The second object is a genuine *boundary-selected BVP coincidence candidate*.
It is not yet the intrinsic ``W^cu(P_-)=W^cs(P_+)`` coincidence required by
Issue #13: the A.2 boundary representative has not been proved independent
of its finite boundary, and the zero-energy BVP candidate found on the frozen
slice does not pass the frozen localization diagnostic for the published
algebraic RFSN-II canard.  These distinctions are part of the generated
report.
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

EVIDENCE_STATUS = "COMPUTED/E1_BOUNDARY_SELECTED_A2_COINCIDENCE_CANDIDATE"
ENTRY_STATUS = "COMPUTED/E1_BOUNDARY_SELECTED_FINITE_R_SADDLE_SLOW_ENTRY"
COINCIDENCE_STATUS = (
    "COMPUTED/E1_BOUNDARY_SELECTED_ZERO_ENERGY_BVP_CANDIDATE"
)
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


def _hamiltonian(state: Array, configuration: SlowTraceConfiguration) -> float:
    return central_hamiltonian(
        state, r=configuration.r, a2=configuration.a2
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


def compute_candidate(
    configuration: SlowTraceConfiguration | None = None,
) -> tuple[dict[str, Any], dict[str, Array]]:
    config = configuration or load_configuration()
    if config.epsilon != 1.0:
        raise ValueError("the v1 A.2 computation is frozen to epsilon=1")

    half = _outside_half(config)
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

    report: dict[str, Any] = {
        "schema_version": "vdp-canard-slow-trace/1",
        "evidence_status": EVIDENCE_STATUS,
        "claim_bearing": False,
        "parameters": {
            "epsilon": config.epsilon,
            "r": config.r,
            "a2": config.a2,
            "published_leading_a2": -5.0 * config.r / 48.0,
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
        "zero_energy_coincidence_candidate": {
            "status": COINCIDENCE_STATUS,
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
                "The formal projected entry has been replaced by collocation "
                "solutions of the exact finite-r field on a boundary-selected "
                "A.2 branch. An H2=0 condition is imposed in the candidate "
                "BVP, whose numerically observed reversibility does not yet "
                "identify the intrinsic Wcu/Wcs maximal-canard branch."
            ),
            "next_mathematical_object": (
                "Resolve the symmetry-breaking/slow-sheet direction "
                "independently of the endpoint family, transport its "
                "H2=0 trace to u2=16, and evaluate q2 at the first increasing "
                "p2=0 hit as a function of (r,a2)."
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
