"""Reproducible floating-point numerics for the positive-parameter PDE notes.

The routines in this module are deliberately non-rigorous.  They continue the
certified universal-core homoclinic with SciPy collocation, compute concrete
PDE profiles, and locate several zero-energy reversible periodic orbits.  The
resulting curves are E1 numerical evidence, not interval certificates.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import simpson, solve_bvp, solve_ivp
from scipy.linalg import schur
from scipy.optimize import brentq, root


Array = NDArray[np.float64]
REVERSER = np.array([1.0, -1.0, 1.0, -1.0])

# Midpoint reconstruction of the immutable universal-core certificate.  The
# source lies on the radius-.01 degree-ten unstable graph.  Its provenance is
# recorded in numerics/README.md; no runtime dependency on the flagship repo is
# introduced.
CORE_SOURCE_STATE = np.array(
    [
        0.00913112278544689,
        0.00933320410678839,
        -0.00410366020134664,
        0.00356008447006408,
    ],
    dtype=np.float64,
)
CORE_HALF_TIME = 9.63744206789648


@dataclass
class HomoclinicResult:
    model: str
    r: float
    epsilon: float
    a2: float
    domain: float
    solution: object
    diagnostics: dict[str, float | bool]


@dataclass
class PeriodicOrbit:
    family: str
    relative_winding: int
    initial_offset: float
    half_period_xi: float
    xi: Array
    state: Array
    physical_x: Array
    physical_u: Array
    physical_v: Array
    central_action: float
    physical_action: float
    diagnostics: dict[str, float | int | str]


def core_field_point(_time: float, state: Array) -> Array:
    u, p, v, q = state
    return np.array([p, -u * u - v, q, u], dtype=np.float64)


def core_field(_time: Array, state: Array) -> Array:
    u, p, v, q = state
    return np.vstack((p, -u * u - v, q, u))


def brusselator_field(r: float) -> Callable[[Array, Array], Array]:
    r2 = r * r
    r4 = r2 * r2
    r6 = r4 * r2

    def field(_time: Array, state: Array) -> Array:
        u, p, v, q = state
        uv = u * v
        u2v = u * uv
        return np.vstack(
            (
                p,
                -u * u - v - 2.0 * r2 * uv - r4 * u2v,
                q,
                u + r2 * (u * u + v) + 2.0 * r4 * uv + r6 * u2v,
            )
        )

    return field


def vdp_coefficients(r: float, a2: float, epsilon: float) -> tuple[float, float, float]:
    sqrt_epsilon = float(np.sqrt(epsilon))
    c = 2.0 * r * a2 + sqrt_epsilon * r**4 * a2 * a2
    quadratic = 1.0 + sqrt_epsilon * r**3 * a2
    cubic = sqrt_epsilon * r * r / 3.0
    return c, quadratic, cubic


def vdp_field(
    r: float, a2: float = 0.0, epsilon: float = 1.0
) -> Callable[[Array, Array], Array]:
    c, quadratic, cubic = vdp_coefficients(r, a2, epsilon)

    def field(_time: Array, state: Array) -> Array:
        u, p, v, q = state
        return np.vstack((p, c * u - v - quadratic * u * u + cubic * u**3, q, u))

    return field


def vdp_field_point(
    time: float, state: Array, *, r: float, a2: float, epsilon: float
) -> Array:
    return vdp_field(r, a2, epsilon)(np.array([time]), state.reshape(4, 1))[:, 0]


def origin_matrix(model: str, r: float, a2: float, epsilon: float) -> Array:
    if model == "brusselator":
        r2 = r * r
        return np.array(
            [
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, -1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [1.0, 0.0, r2, 0.0],
            ],
            dtype=np.float64,
        )
    if model == "vdp":
        c, _quadratic, _cubic = vdp_coefficients(r, a2, epsilon)
        return np.array(
            [
                [0.0, 1.0, 0.0, 0.0],
                [c, 0.0, -1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [1.0, 0.0, 0.0, 0.0],
            ],
            dtype=np.float64,
        )
    if model == "core":
        return np.array(
            [
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, -1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [1.0, 0.0, 0.0, 0.0],
            ],
            dtype=np.float64,
        )
    raise ValueError(f"unknown model {model!r}")


def stable_complement(matrix: Array) -> Array:
    """Return two orthonormal rows that vanish on the stable Schur space."""

    _triangular, vectors, stable_dimension = schur(
        matrix, output="real", sort=lambda real, imag: real < 0.0
    )
    if stable_dimension != 2:
        raise RuntimeError(f"expected stable dimension two, got {stable_dimension}")
    return vectors[:, stable_dimension:].T.copy()


def field_for_model(
    model: str, r: float, a2: float, epsilon: float
) -> Callable[[Array, Array], Array]:
    if model == "core":
        return core_field
    if model == "brusselator":
        return brusselator_field(r)
    if model == "vdp":
        return vdp_field(r, a2, epsilon)
    raise ValueError(f"unknown model {model!r}")


def certified_core_center() -> tuple[Array, dict[str, float]]:
    integration = solve_ivp(
        core_field_point,
        (0.0, CORE_HALF_TIME),
        CORE_SOURCE_STATE,
        method="DOP853",
        rtol=3.0e-13,
        atol=3.0e-15,
        max_step=0.02,
        dense_output=True,
    )
    if not integration.success:
        raise RuntimeError(integration.message)
    center = integration.y[:, -1].copy()
    symmetry_residual = float(max(abs(center[1]), abs(center[3])))
    energy = core_hamiltonian(integration.y)
    diagnostics = {
        "certificate_midpoint_symmetry_residual": symmetry_residual,
        "certificate_midpoint_energy_drift": float(np.ptp(energy)),
    }
    # The certified root has exactly P=Q=0.  Projecting the floating midpoint
    # to Fix(R) prevents its 1e-13 integration error from contaminating a long
    # unstable initial guess.
    center[1] = 0.0
    center[3] = 0.0
    return center, diagnostics


def core_hamiltonian(state: Array) -> Array:
    u, p, v, q = state
    return 0.5 * (q * q - p * p) - u**3 / 3.0 - u * v


def vdp_hamiltonian(state: Array, r: float, a2: float, epsilon: float) -> Array:
    u, p, v, q = state
    c, quadratic, _cubic = vdp_coefficients(r, a2, epsilon)
    return (
        0.5 * (q * q - p * p)
        - u * v
        + 0.5 * c * u * u
        - quadratic * u**3 / 3.0
        + np.sqrt(epsilon) * r * r * u**4 / 12.0
    )


def _homoclinic_diagnostics(
    model: str,
    r: float,
    a2: float,
    epsilon: float,
    domain: float,
    solution: object,
    complement: Array,
) -> dict[str, float | bool]:
    grid = np.linspace(0.0, domain, 4001)
    state = solution.sol(grid)
    derivative = solution.sol(grid, 1)
    field = field_for_model(model, r, a2, epsilon)(grid, state)
    normalized_residual = float(np.max(np.abs(derivative - field)))
    boundary_residual = float(
        max(
            abs(state[1, 0]),
            abs(state[3, 0]),
            np.max(np.abs(complement @ state[:, -1])),
        )
    )
    diagnostics: dict[str, float | bool] = {
        "solver_success": bool(solution.success),
        "nodes": float(solution.x.size),
        "normalized_ode_residual_inf": normalized_residual,
        "boundary_residual_inf": boundary_residual,
        "tail_norm": float(np.linalg.norm(state[:, -1])),
        "center_amplitude": float(np.hypot(state[0, 0], state[2, 0])),
        "nontrivial_branch": bool(np.hypot(state[0, 0], state[2, 0]) > 1.0),
    }
    if model in {"core", "vdp"}:
        energy = (
            core_hamiltonian(state)
            if model == "core"
            else vdp_hamiltonian(state, r, a2, epsilon)
        )
        diagnostics["hamiltonian_drift"] = float(np.ptp(energy))
        diagnostics["hamiltonian_abs_max"] = float(np.max(np.abs(energy)))
    if model == "brusselator" and r > 0.0:
        physical_u = 1.0 + r * r * state[0]
        physical_v = 1.0 + r**4 * state[2]
        diagnostics["min_physical_u"] = float(np.min(physical_u))
        diagnostics["min_physical_v"] = float(np.min(physical_v))
    return diagnostics


def solve_homoclinic(
    model: str,
    r: float,
    *,
    a2: float = 0.0,
    epsilon: float = 1.0,
    domain: float = 20.0,
    tolerance: float = 1.0e-8,
    previous: HomoclinicResult | None = None,
) -> HomoclinicResult:
    field = field_for_model(model, r, a2, epsilon)
    complement = stable_complement(origin_matrix(model, r, a2, epsilon))

    def boundary(left: Array, right: Array) -> Array:
        return np.r_[left[1], left[3], complement @ right]

    mesh = np.linspace(0.0, domain, int(70 * domain) + 1)
    if previous is None:
        center, _diagnostics = certified_core_center()
        integration = solve_ivp(
            core_field_point,
            (0.0, domain),
            center,
            method="DOP853",
            rtol=2.0e-12,
            atol=2.0e-14,
            max_step=0.02,
            dense_output=True,
        )
        guess = integration.sol(mesh)
    else:
        old_domain = previous.domain
        old_time = np.minimum(mesh, old_domain)
        guess = previous.solution.sol(old_time)
        if domain > old_domain:
            tail_start = previous.solution.sol(old_domain)
            tail = solve_ivp(
                lambda time, state: field_for_model(
                    previous.model,
                    previous.r,
                    previous.a2,
                    previous.epsilon,
                )(np.array([time]), state.reshape(4, 1))[:, 0],
                (old_domain, domain),
                tail_start,
                method="DOP853",
                rtol=2.0e-11,
                atol=2.0e-13,
                max_step=0.02,
                dense_output=True,
            )
            mask = mesh > old_domain
            guess[:, mask] = tail.sol(mesh[mask])

    solution = solve_bvp(
        field,
        boundary,
        mesh,
        guess,
        tol=tolerance,
        bc_tol=min(1.0e-10, tolerance * 0.1),
        max_nodes=80000,
        verbose=0,
    )
    if not solution.success:
        raise RuntimeError(f"{model} r={r}: {solution.message}")
    diagnostics = _homoclinic_diagnostics(
        model, r, a2, epsilon, domain, solution, complement
    )
    if not diagnostics["nontrivial_branch"]:
        raise RuntimeError(f"{model} r={r}: collocation fell onto the equilibrium")
    return HomoclinicResult(
        model=model,
        r=r,
        epsilon=epsilon,
        a2=a2,
        domain=domain,
        solution=solution,
        diagnostics=diagnostics,
    )


def continue_homoclinics(
    model: str,
    r_values: Iterable[float],
    *,
    a2: float = 0.0,
    epsilon: float = 1.0,
    domain: float = 20.0,
    tolerance: float = 1.0e-8,
) -> list[HomoclinicResult]:
    core = solve_homoclinic(
        "core", 0.0, domain=domain, tolerance=min(tolerance, 2.0e-9)
    )
    results: list[HomoclinicResult] = []
    previous = core
    for r in sorted(float(value) for value in r_values):
        result = solve_homoclinic(
            model,
            r,
            a2=a2,
            epsilon=epsilon,
            domain=domain,
            tolerance=tolerance,
            previous=previous,
        )
        results.append(result)
        previous = result
    return results


def reflected_profile(result: HomoclinicResult, points: int = 6001) -> tuple[Array, Array]:
    half_time = np.linspace(0.0, result.domain, points // 2 + 1)
    half_state = result.solution.sol(half_time)
    full_time = np.concatenate((-half_time[:0:-1], half_time))
    left_state = REVERSER[:, None] * half_state[:, :0:-1]
    full_state = np.concatenate((left_state, half_state), axis=1)
    return full_time, full_state


def first_half_height(half_time: Array, values: Array) -> float:
    threshold = 0.5 * abs(float(values[0]))
    magnitude = np.abs(values)
    indices = np.flatnonzero(magnitude <= threshold)
    if indices.size == 0:
        raise RuntimeError("half-height crossing not found")
    index = int(indices[0])
    if index == 0:
        return 0.0
    x0, x1 = half_time[index - 1 : index + 1]
    y0, y1 = magnitude[index - 1 : index + 1]
    if y1 == y0:
        return float(x1)
    return float(x0 + (threshold - y0) * (x1 - x0) / (y1 - y0))


def collocation_half_height(solution: object, component: int, domain: float) -> float:
    """Locate the first half-height crossing using the collocation spline."""

    center = abs(float(solution.sol(0.0)[component]))
    threshold = 0.5 * center
    grid = np.linspace(0.0, domain, 2001)
    values = np.abs(solution.sol(grid)[component]) - threshold
    indices = np.flatnonzero(values <= 0.0)
    if indices.size == 0:
        raise RuntimeError("half-height crossing not found")
    index = int(indices[0])
    if index == 0:
        return 0.0
    return float(
        brentq(
            lambda coordinate: abs(float(solution.sol(coordinate)[component]))
            - threshold,
            float(grid[index - 1]),
            float(grid[index]),
            xtol=1.0e-13,
            rtol=1.0e-13,
        )
    )


def brusselator_observables(result: HomoclinicResult) -> dict[str, float]:
    if result.model != "brusselator":
        raise ValueError("expected a Brusselator result")
    half_time = np.linspace(0.0, result.domain, 8001)
    state = result.solution.sol(half_time)
    r = result.r
    return {
        "r": r,
        "d": r**4,
        "amplitude_u": r * r * float(np.max(np.abs(state[0]))),
        "amplitude_v": r**4 * float(np.max(np.abs(state[2]))),
        "width_u": 2.0 * r * collocation_half_height(
            result.solution, 0, result.domain
        ),
        "width_v": 2.0 * r * collocation_half_height(
            result.solution, 2, result.domain
        ),
        "scaled_amplitude_u": float(np.max(np.abs(state[0]))),
        "scaled_amplitude_v": float(np.max(np.abs(state[2]))),
    }


def vdp_fixr_zero_energy_v(u: float, r: float, a2: float, epsilon: float) -> float:
    c, quadratic, _cubic = vdp_coefficients(r, a2, epsilon)
    return float(
        0.5 * c * u
        - quadratic * u * u / 3.0
        + np.sqrt(epsilon) * r * r * u**3 / 12.0
    )


def _vdp_component_events(
    offset: float,
    *,
    event_component: int,
    center_u: float,
    r: float,
    a2: float,
    epsilon: float,
    maximum_time: float,
) -> tuple[object, list[tuple[float, Array]]]:
    if event_component not in (1, 3):
        raise ValueError("a reversible symmetry event must use P (1) or Q (3)")
    initial_u = center_u + offset
    initial = np.array(
        [
            initial_u,
            0.0,
            vdp_fixr_zero_energy_v(initial_u, r, a2, epsilon),
            0.0,
        ]
    )

    def event(_time: float, state: Array) -> float:
        return float(state[event_component])

    event.direction = 0
    event.terminal = False
    integration = solve_ivp(
        lambda time, state: vdp_field_point(
            time, state, r=r, a2=a2, epsilon=epsilon
        ),
        (0.0, maximum_time),
        initial,
        method="DOP853",
        rtol=2.0e-11,
        atol=2.0e-13,
        max_step=0.02,
        events=event,
        dense_output=True,
    )
    events = [
        (float(time), state.copy())
        for time, state in zip(integration.t_events[0], integration.y_events[0])
        if time > 0.05
    ]
    return integration, events


def periodic_event_residual(
    offset: float,
    *,
    event_index: int,
    event_component: int,
    residual_component: int,
    center_u: float,
    r: float,
    a2: float,
    epsilon: float,
    maximum_time: float = 36.0,
) -> float:
    if {event_component, residual_component} != {1, 3}:
        raise ValueError("event and residual components must be P (1) and Q (3)")
    _integration, events = _vdp_component_events(
        offset,
        event_component=event_component,
        center_u=center_u,
        r=r,
        a2=a2,
        epsilon=epsilon,
        maximum_time=maximum_time,
    )
    if len(events) <= event_index:
        raise RuntimeError(
            f"offset {offset:.3e}: requested component-{event_component} event "
            f"{event_index}, found {len(events)}"
        )
    return float(events[event_index][1][residual_component])


def compute_periodic_orbit(
    *,
    family: str,
    relative_winding: int,
    bracket: tuple[float, float],
    event_index: int,
    event_component: int,
    residual_component: int,
    center_u: float,
    r: float,
    a2: float = 0.0,
    epsilon: float = 1.0,
) -> PeriodicOrbit:
    residual = lambda offset: periodic_event_residual(
        offset,
        event_index=event_index,
        event_component=event_component,
        residual_component=residual_component,
        center_u=center_u,
        r=r,
        a2=a2,
        epsilon=epsilon,
    )
    left_value = residual(bracket[0])
    right_value = residual(bracket[1])
    if left_value * right_value >= 0.0:
        raise RuntimeError(
            f"periodic bracket {bracket} does not change sign: "
            f"{left_value}, {right_value}"
        )
    offset = float(
        brentq(
            residual,
            bracket[0],
            bracket[1],
            xtol=2.0e-14,
            rtol=2.0e-12,
            maxiter=100,
        )
    )
    _integration, events = _vdp_component_events(
        offset,
        event_component=event_component,
        center_u=center_u,
        r=r,
        a2=a2,
        epsilon=epsilon,
        maximum_time=36.0,
    )
    selection_time, selection_state = events[event_index]
    half_period = selection_time
    selection_field = vdp_field_point(
        selection_time,
        selection_state,
        r=r,
        a2=a2,
        epsilon=epsilon,
    )

    # The scalar transverse-event bracket is robust for branch selection, but
    # a second integration with tighter tolerances can move an exponentially
    # sensitive long orbit enough to leave a visible symmetry residual.  Refine
    # the selected branch with the full reversible shooting pair
    # (P(T), Q(T))=0 while retaining the exact zero-energy parametrization at
    # the initial point.
    offset_scale = max(0.2 * abs(offset), 1.0e-12)

    def shooting_pair(unknown: Array) -> Array:
        trial_offset = offset + offset_scale * float(unknown[0])
        trial_time = float(unknown[1])
        trial_u = center_u + trial_offset
        trial_initial = np.array(
            [
                trial_u,
                0.0,
                vdp_fixr_zero_energy_v(trial_u, r, a2, epsilon),
                0.0,
            ]
        )
        trial = solve_ivp(
            lambda time, state: vdp_field_point(
                time, state, r=r, a2=a2, epsilon=epsilon
            ),
            (0.0, trial_time),
            trial_initial,
            method="DOP853",
            rtol=1.0e-12,
            atol=1.0e-14,
            max_step=0.008,
        )
        return trial.y[[1, 3], -1]

    refinement = root(
        shooting_pair,
        np.array([0.0, half_period]),
        method="hybr",
        tol=1.0e-10,
    )
    refined_residual = shooting_pair(refinement.x)
    if np.max(np.abs(refined_residual)) > 5.0e-9:
        raise RuntimeError(
            f"periodic refinement failed for {family}{relative_winding}: "
            f"{refinement.message}; residual={refined_residual}"
        )
    offset += offset_scale * float(refinement.x[0])
    half_period = float(refinement.x[1])
    initial_u = center_u + offset
    initial = np.array(
        [initial_u, 0.0, vdp_fixr_zero_energy_v(initial_u, r, a2, epsilon), 0.0]
    )
    half = solve_ivp(
        lambda time, state: vdp_field_point(
            time, state, r=r, a2=a2, epsilon=epsilon
        ),
        (0.0, half_period),
        initial,
        method="DOP853",
        rtol=1.0e-12,
        atol=1.0e-14,
        max_step=0.008,
        dense_output=True,
    )
    independent = solve_ivp(
        lambda time, state: vdp_field_point(
            time, state, r=r, a2=a2, epsilon=epsilon
        ),
        (0.0, half_period),
        initial,
        method="DOP853",
        rtol=3.0e-13,
        atol=3.0e-15,
        max_step=0.004,
    )
    half_xi = np.linspace(0.0, half_period, 3001)
    half_state = half.sol(half_xi)
    xi = np.concatenate((half_xi, 2.0 * half_period - half_xi[-2::-1]))
    reflected = REVERSER[:, None] * half_state[:, -2::-1]
    state = np.concatenate((half_state, reflected), axis=1)
    physical_x = r * epsilon ** (-0.25) * xi
    a = 1.0 + np.sqrt(epsilon) * r**3 * a2
    physical_u = a - np.sqrt(epsilon) * r * r * state[0]
    f_a = a**3 / 3.0 - a
    physical_v = f_a - epsilon * r**4 * state[2]
    half_action = float(simpson(half_state[1] ** 2 - half_state[3] ** 2, x=half_xi))
    central_action = 2.0 * half_action
    physical_action = epsilon ** 2.25 * r**5 * central_action
    energy = vdp_hamiltonian(half_state, r, a2, epsilon)
    endpoint = half_state[:, -1]
    diagnostics = {
        "closure_residual": float(max(abs(endpoint[1]), abs(endpoint[3]))),
        "independent_step_halving_closure_residual": float(
            np.max(np.abs(independent.y[[1, 3], -1]))
        ),
        "endpoint_step_halving_difference": float(
            np.max(np.abs(independent.y[:, -1] - endpoint))
        ),
        "hamiltonian_drift": float(np.ptp(energy)),
        "hamiltonian_abs_max": float(np.max(np.abs(energy))),
        "initial_u": float(initial_u),
        "initial_v": float(initial[2]),
        "branch_selection_event_component": "P" if event_component == 1 else "Q",
        "branch_selection_residual_component": "P" if residual_component == 1 else "Q",
        "branch_selection_event_index": int(event_index),
        "branch_selection_event_count": int(len(events)),
        "branch_selection_event_time_xi": float(selection_time),
        "branch_selection_scalar_residual": float(selection_state[residual_component]),
        "branch_selection_transversality": float(abs(selection_field[event_component])),
        "full_period_xi": float(2.0 * half_period),
        "physical_period": float(2.0 * r * epsilon ** (-0.25) * half_period),
    }
    return PeriodicOrbit(
        family=family,
        relative_winding=relative_winding,
        initial_offset=offset,
        half_period_xi=half_period,
        xi=xi,
        state=state,
        physical_x=physical_x,
        physical_u=physical_u,
        physical_v=physical_v,
        central_action=central_action,
        physical_action=physical_action,
        diagnostics=diagnostics,
    )


def common_slope_fit(orbits: list[PeriodicOrbit]) -> dict[str, object]:
    families = sorted({orbit.family for orbit in orbits})
    design = []
    periods = []
    for orbit in orbits:
        row = [float(orbit.relative_winding)]
        row.extend(1.0 if orbit.family == family else 0.0 for family in families)
        design.append(row)
        periods.append(float(orbit.diagnostics["physical_period"]))
    matrix = np.asarray(design)
    values = np.asarray(periods)
    coefficients, *_ = np.linalg.lstsq(matrix, values, rcond=None)
    fitted = matrix @ coefficients
    return {
        "families": families,
        "slope": float(coefficients[0]),
        "intercepts": {
            family: float(value) for family, value in zip(families, coefficients[1:])
        },
        "residuals": (values - fitted).tolist(),
        "residual_inf": float(np.max(np.abs(values - fitted))),
    }
