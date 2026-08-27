"""Finite floating-point realizations of the V6--V7 van der Pol mechanisms.

The analytic V6 source section is defined by exact saddle coordinates and
continued physical event faces.  Several constants that select that section
are existential in the paper rather than numerical.  This module therefore
uses a phase-fixed linear reversible saddle frame and labels its section
coordinates ``numerical_canonical_eigenplane_phase`` and
``numerical_transverse_coordinate``.
It computes actual zero-energy trajectories of the positive-parameter central
ODE, but a finite grid is not an exhaustive V6 component census.

The multipulse routine solves the full positive-parameter ODE by collocation.
Its superposed homoclinics are only initial guesses; every returned profile is
reported as computed only when the collocation and independent residual gates
pass.  No finite-window calculation is called an infinite aperiodic orbit.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, pi
from typing import Iterable, Mapping

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_bvp, solve_ivp
from scipy.interpolate import CubicSpline
from scipy.optimize import root_scalar
from scipy.signal import find_peaks

from numerics.rfsn_numerics import (
    HomoclinicResult,
    PeriodicOrbit,
    REVERSER,
    origin_matrix,
    reflected_profile,
    stable_complement,
    vdp_coefficients,
    vdp_field,
    vdp_field_point,
    vdp_hamiltonian,
)


Array = NDArray[np.float64]


@dataclass(frozen=True)
class SaddleFrame:
    unstable: Array
    stable: Array
    inverse: Array
    alpha: float
    beta: float

    def coordinates(self, state: Array) -> Array:
        return self.inverse @ np.asarray(state, dtype=float)


@dataclass
class FirstEventSample:
    phase: float
    transverse_coordinate: float
    source_state: Array
    event: str
    event_time_xi: float
    event_state: Array
    event_speed: float
    winding_proxy: float
    diagnostics: dict[str, float | str | bool]
    sample_time_xi: Array
    sample_state: Array


@dataclass
class MultipulseOrbit:
    pulse_count_requested: int
    pulse_count_observed: int
    xi: Array
    state: Array
    physical_x: Array
    physical_u: Array
    physical_v: Array
    diagnostics: dict[str, float | int | str | bool]


def _canonical_real_pair(
    matrix: Array, vector: Array, alpha: float, beta: float
) -> Array:
    """Return a phase-fixed real basis for a complex invariant plane.

    A complex eigenvector has an arbitrary unit-modulus factor, so merely
    orienting its real and imaginary columns does not define a reproducible
    absolute phase.  We instead form the invariant-plane projector, project a
    fixed coordinate axis with maximal norm, and obtain the second vector from
    ``(A-alpha I)/beta``.  This removes the LAPACK eigenvector phase ambiguity.
    """

    raw = np.column_stack((np.real(vector), np.imag(vector)))
    orthonormal, _ = np.linalg.qr(raw)
    projector = orthonormal @ orthonormal.T
    diagonal = np.diag(projector)
    anchor_index = int(np.flatnonzero(diagonal >= np.max(diagonal) - 1.0e-14)[0])
    first = projector[:, anchor_index]
    first /= np.linalg.norm(first)
    if first[anchor_index] < 0.0:
        first *= -1.0
    second = (matrix @ first - alpha * first) / beta
    second /= np.linalg.norm(second)
    pair = np.column_stack((first, second))
    if np.linalg.matrix_rank(pair) != 2:
        raise RuntimeError("failed to construct the real eigenspace frame")
    return pair


def reversible_saddle_frame(r: float, a2: float, epsilon: float) -> SaddleFrame:
    """Construct a deterministic reversible linear saddle-focus frame.

    The phase is fixed by projection of a coordinate axis into the numerical
    eigenspace; it is not the transported absolute phase fixed by Theorem V2.
    """

    matrix = origin_matrix("vdp", r, a2, epsilon)
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    candidates = [
        index
        for index, value in enumerate(eigenvalues)
        if value.real > 0.0 and value.imag > 0.0
    ]
    if len(candidates) != 1:
        raise RuntimeError(f"expected one expanding complex eigenvalue, got {eigenvalues}")
    index = candidates[0]
    value = eigenvalues[index]
    unstable = _canonical_real_pair(
        matrix, eigenvectors[:, index], float(value.real), float(value.imag)
    )
    stable = REVERSER[:, None] * unstable
    basis = np.column_stack((unstable, stable))
    inverse = np.linalg.inv(basis)
    invariance_u = np.linalg.norm(matrix @ unstable - unstable @ (inverse[:2] @ matrix @ unstable))
    invariance_s = np.linalg.norm(matrix @ stable - stable @ (inverse[2:] @ matrix @ stable))
    if max(invariance_u, invariance_s) > 1.0e-10:
        raise RuntimeError("reversible eigenframe does not resolve the invariant splitting")
    return SaddleFrame(
        unstable=unstable,
        stable=stable,
        inverse=inverse,
        alpha=float(value.real),
        beta=float(value.imag),
    )


def vdp_hamiltonian_gradient(
    state: Array, r: float, a2: float, epsilon: float
) -> Array:
    u, p, v, q = np.asarray(state, dtype=float)
    c, quadratic, _cubic = vdp_coefficients(r, a2, epsilon)
    return np.array(
        [
            -v + c * u - quadratic * u * u + np.sqrt(epsilon) * r * r * u**3 / 3.0,
            -p,
            -u,
            q,
        ],
        dtype=float,
    )


def zero_energy_source_state(
    *,
    frame: SaddleFrame,
    phase: float,
    transverse_coordinate: float,
    radius: float,
    r: float,
    a2: float,
    epsilon: float,
) -> tuple[Array, dict[str, float | str]]:
    """Parameterize a local numerical zero-energy outgoing section.

    For each unstable phase, the energy gradient selects the stable direction
    used to solve the scalar zero-energy equation.  The orthogonal stable
    direction is the finite transverse coordinate.  This is a deterministic
    numerical section, not the theorem's transported exact action coordinate.
    """

    unstable_coordinates = radius * np.array([np.cos(phase), np.sin(phase)])
    unstable_state = frame.unstable @ unstable_coordinates
    stable_gradient = frame.stable.T @ vdp_hamiltonian_gradient(
        unstable_state, r, a2, epsilon
    )
    gradient_norm = float(np.linalg.norm(stable_gradient))
    if gradient_norm < 1.0e-12:
        raise RuntimeError("energy surface is tangent to the chosen stable fiber")
    solve_direction = stable_gradient / gradient_norm
    transverse_direction = np.array([-solve_direction[1], solve_direction[0]])

    def state_at(tau: float) -> Array:
        stable_coordinates = (
            transverse_coordinate * transverse_direction + tau * solve_direction
        )
        return unstable_state + frame.stable @ stable_coordinates

    def energy(tau: float) -> float:
        state = state_at(tau).reshape(4, 1)
        return float(vdp_hamiltonian(state, r, a2, epsilon)[0])

    def derivative(tau: float) -> float:
        return float(
            vdp_hamiltonian_gradient(state_at(tau), r, a2, epsilon)
            @ (frame.stable @ solve_direction)
        )

    initial_derivative = derivative(0.0)
    initial_tau = -energy(0.0) / initial_derivative
    solution = root_scalar(
        energy,
        x0=float(initial_tau),
        fprime=derivative,
        method="newton",
        xtol=2.0e-14,
        maxiter=40,
    )
    if not solution.converged:
        raise RuntimeError("zero-energy source solve did not converge")
    state = state_at(float(solution.root))
    residual = abs(energy(float(solution.root)))
    return state, {
        "coordinate_status": "COMPUTED/E1 numerical reversible eigenframe",
        "phase_name": "numerical_canonical_eigenplane_phase",
        "transverse_name": "numerical_transverse_coordinate_not_exact_action",
        "energy_residual": residual,
        "solved_stable_coordinate": float(solution.root),
        "stable_energy_gradient_norm": gradient_norm,
    }


def homoclinic_source_anchor(
    homoclinic: HomoclinicResult, *, source_radius: float = 0.01
) -> dict[str, float | Array | str]:
    """Locate the continued homoclinic on the numerical outgoing section.

    The half-line BVP is stored from its symmetry point toward the stable tail.
    Reversibility maps that tail to the outgoing branch.  The returned phase
    and transverse coordinate are expressed in this module's deterministic
    numerical frame, not in the transported absolute phase of V2.
    """

    if homoclinic.model != "vdp":
        raise ValueError("expected a van der Pol homoclinic")
    r, a2, epsilon = homoclinic.r, homoclinic.a2, homoclinic.epsilon
    frame = reversible_saddle_frame(r, a2, epsilon)

    def unstable_radius(time: float) -> float:
        outgoing = REVERSER * homoclinic.solution.sol(time)
        return float(np.linalg.norm(frame.coordinates(outgoing)[:2]))

    grid = np.linspace(0.0, homoclinic.domain, 2001)
    values = np.array([unstable_radius(float(time)) - source_radius for time in grid])
    crossings = np.flatnonzero(values[:-1] * values[1:] <= 0.0)
    if crossings.size == 0:
        raise RuntimeError("continued homoclinic does not cross the numerical source radius")
    # The tail-most crossing is the local outgoing section; earlier crossings
    # can occur during the global excursion.
    index = int(crossings[-1])
    root = root_scalar(
        lambda time: unstable_radius(float(time)) - source_radius,
        bracket=(float(grid[index]), float(grid[index + 1])),
        xtol=2.0e-13,
        rtol=2.0e-13,
    )
    time = float(root.root)
    state = REVERSER * homoclinic.solution.sol(time)
    coordinates = frame.coordinates(state)
    phase = float(atan2(coordinates[1], coordinates[0]) % (2.0 * pi))
    unstable_state = frame.unstable @ coordinates[:2]
    stable_gradient = frame.stable.T @ vdp_hamiltonian_gradient(
        unstable_state, r, a2, epsilon
    )
    solve_direction = stable_gradient / np.linalg.norm(stable_gradient)
    transverse_direction = np.array([-solve_direction[1], solve_direction[0]])
    transverse_coordinate = float(coordinates[2:] @ transverse_direction)
    reconstructed, reconstruction = zero_energy_source_state(
        frame=frame,
        phase=phase,
        transverse_coordinate=transverse_coordinate,
        radius=source_radius,
        r=r,
        a2=a2,
        epsilon=epsilon,
    )
    return {
        "status": "COMPUTED/E1 continued homoclinic anchor in numerical section",
        "phase": phase,
        "transverse_coordinate": transverse_coordinate,
        "tail_time_from_symmetry": time,
        "state": state,
        "reconstruction_defect": float(np.linalg.norm(reconstructed - state)),
        "energy_residual": float(
            abs(vdp_hamiltonian(state.reshape(4, 1), r, a2, epsilon)[0])
        ),
        "solved_stable_coordinate": float(reconstruction["solved_stable_coordinate"]),
    }


def numerical_source_coordinates(
    state: Array,
    *,
    frame: SaddleFrame,
    r: float,
    a2: float,
    epsilon: float,
) -> dict[str, float | Array]:
    coordinates = frame.coordinates(state)
    radius = float(np.linalg.norm(coordinates[:2]))
    phase = float(atan2(coordinates[1], coordinates[0]) % (2.0 * pi))
    unstable_state = frame.unstable @ coordinates[:2]
    stable_gradient = frame.stable.T @ vdp_hamiltonian_gradient(
        unstable_state, r, a2, epsilon
    )
    solve_direction = stable_gradient / np.linalg.norm(stable_gradient)
    transverse_direction = np.array([-solve_direction[1], solve_direction[0]])
    transverse_coordinate = float(coordinates[2:] @ transverse_direction)
    reconstructed, _ = zero_energy_source_state(
        frame=frame,
        phase=phase,
        transverse_coordinate=transverse_coordinate,
        radius=radius,
        r=r,
        a2=a2,
        epsilon=epsilon,
    )
    return {
        "phase": phase,
        "transverse_coordinate": transverse_coordinate,
        "radius": radius,
        "linear_coordinates": coordinates,
        "reconstruction_defect": float(np.linalg.norm(reconstructed - state)),
    }


def periodic_source_anchor(
    orbit: PeriodicOrbit,
    *,
    r: float,
    a2: float,
    epsilon: float,
    source_radius: float = 0.01,
) -> dict[str, float | Array | str]:
    """Locate a computed periodic orbit on the numerical outgoing section."""

    frame = reversible_saddle_frame(r, a2, epsilon)
    splines = [CubicSpline(orbit.xi, orbit.state[index]) for index in range(4)]

    def state(time: float) -> Array:
        return np.array([spline(time) for spline in splines])

    def section(time: float) -> float:
        return float(np.linalg.norm(frame.coordinates(state(time))[:2]) - source_radius)

    values = np.array([section(float(time)) for time in orbit.xi])
    crossings = np.flatnonzero((values[:-1] < 0.0) & (values[1:] >= 0.0))
    if crossings.size == 0:
        return {
            "status": "NOT_NUMERICALLY_RESOLVED",
            "reason": "periodic sample does not enter the chosen local source radius",
            "minimum_unstable_radius": float(
                np.min(
                    np.linalg.norm(frame.inverse[:2] @ orbit.state, axis=0)
                )
            ),
        }
    index = int(crossings[-1])
    crossing = root_scalar(
        section,
        bracket=(float(orbit.xi[index]), float(orbit.xi[index + 1])),
        xtol=2.0e-13,
        rtol=2.0e-13,
    )
    time = float(crossing.root)
    crossing_state = state(time)
    coordinates = numerical_source_coordinates(
        crossing_state,
        frame=frame,
        r=r,
        a2=a2,
        epsilon=epsilon,
    )
    return {
        "status": "COMPUTED/E1 periodic outgoing-section anchor",
        "orbit_family": orbit.family,
        "relative_winding": int(orbit.relative_winding),
        "crossing_time_xi": time,
        "state": crossing_state,
        **coordinates,
    }


def _pole_gate_coordinates(state: Array) -> dict[str, float]:
    u, p, v, q = (float(value) for value in state)
    x = -u
    y = -p
    pole_q = -q
    w = -v
    return {
        "x": x,
        "y": y,
        "q": pole_q,
        "w": w,
        "D": 0.5 * x * x - w,
        "H": x * y - pole_q,
    }


def integrate_first_event(
    *,
    phase: float,
    transverse_coordinate: float,
    r: float,
    a2: float,
    epsilon: float,
    source_radius: float = 0.01,
    local_return_radius: float | None = None,
    maximum_time: float = 80.0,
    terminal_u: float = -10.0,
    escape_norm: float = 60.0,
    rtol: float = 1.0e-10,
    atol: float = 1.0e-12,
    max_step: float = 0.03,
) -> FirstEventSample:
    """Integrate one actual central-ODE sample to a finite numerical event.

    A return is completed through two legs: outgoing source to the incoming
    local sphere, then the local saddle passage to the next outgoing sphere.
    The exact homoclinic instead approaches the stable cut and will time out on
    the second leg.  Terminal U/escape events remain active on both legs.
    """

    return_radius = (
        float(source_radius)
        if local_return_radius is None
        else float(local_return_radius)
    )
    if return_radius <= 0.0:
        raise ValueError("local_return_radius must be positive")
    frame = reversible_saddle_frame(r, a2, epsilon)
    source, source_diagnostics = zero_energy_source_state(
        frame=frame,
        phase=phase,
        transverse_coordinate=transverse_coordinate,
        radius=source_radius,
        r=r,
        a2=a2,
        epsilon=epsilon,
    )

    def incoming_sphere(_time: float, state: Array) -> float:
        return float(np.linalg.norm(frame.coordinates(state)) - return_radius)

    incoming_sphere.direction = -1
    incoming_sphere.terminal = True

    def terminal_section(_time: float, state: Array) -> float:
        return float(state[0] - terminal_u)

    terminal_section.direction = -1
    terminal_section.terminal = True

    def escape_section(_time: float, state: Array) -> float:
        return float(np.linalg.norm(state) - escape_norm)

    escape_section.direction = 1
    escape_section.terminal = True

    integration = solve_ivp(
        lambda time, state: vdp_field_point(
            time, state, r=r, a2=a2, epsilon=epsilon
        ),
        (0.0, maximum_time),
        source,
        method="DOP853",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
        events=(incoming_sphere, terminal_section, escape_section),
        dense_output=True,
    )
    event_index = next(
        (index for index, times in enumerate(integration.t_events) if len(times)),
        None,
    )
    integrations = [integration]
    if event_index is None:
        event = "time_limit_unresolved"
        event_time = float(integration.t[-1])
        event_state = integration.y[:, -1].copy()
        event_speed = 0.0
    elif event_index == 0:
        incoming_time = float(integration.t_events[0][0])
        incoming_state = integration.y_events[0][0].copy()

        def outgoing_sphere(_time: float, state: Array) -> float:
            # The numerical source section is defined by the unstable radius,
            # not by the full four-dimensional norm.  Using the same equation
            # at the target is essential before a returned segment can be
            # composed with another branch.
            return float(
                np.linalg.norm(frame.coordinates(state)[:2]) - return_radius
            )

        outgoing_sphere.direction = 1
        outgoing_sphere.terminal = True

        def deep_stable_cut(_time: float, state: Array) -> float:
            return float(
                np.linalg.norm(frame.coordinates(state)) - return_radius * 5.0e-2
            )

        deep_stable_cut.direction = -1
        deep_stable_cut.terminal = True
        second = solve_ivp(
            lambda time, state: vdp_field_point(
                time, state, r=r, a2=a2, epsilon=epsilon
            ),
            (incoming_time, maximum_time),
            incoming_state,
            method="DOP853",
            rtol=rtol,
            atol=atol,
            max_step=max_step,
            events=(outgoing_sphere, deep_stable_cut, terminal_section, escape_section),
            dense_output=True,
        )
        integrations.append(second)
        second_index = next(
            (index for index, times in enumerate(second.t_events) if len(times)),
            None,
        )
        if second_index is None:
            event = "time_limit_unresolved"
            event_time = float(second.t[-1])
            event_state = second.y[:, -1].copy()
            event_speed = 0.0
        else:
            event_time = float(second.t_events[second_index][0])
            event_state = second.y_events[second_index][0].copy()
            vector = vdp_field_point(
                event_time, event_state, r=r, a2=a2, epsilon=epsilon
            )
            if second_index == 0:
                coordinates = frame.coordinates(event_state)
                target_coordinates = numerical_source_coordinates(
                    event_state,
                    frame=frame,
                    r=r,
                    a2=a2,
                    epsilon=epsilon,
                )
                target_transverse = float(
                    target_coordinates["transverse_coordinate"]
                )
                event = "return+" if target_transverse >= 0.0 else "return-"
                coordinate_velocity = frame.inverse @ vector
                event_speed = float(
                    coordinates[:2]
                    @ coordinate_velocity[:2]
                    / np.linalg.norm(coordinates[:2])
                )
            elif second_index == 1:
                event = "stable_cut_proxy"
                coordinate_velocity = frame.inverse @ vector
                coordinates = frame.coordinates(event_state)
                event_speed = float(
                    coordinates @ coordinate_velocity / np.linalg.norm(coordinates)
                )
            elif second_index == 2:
                gate = _pole_gate_coordinates(event_state)
                if gate["y"] > 0.0 and gate["D"] > 0.0 and gate["H"] > 0.0:
                    event = "pole_gate_proxy"
                else:
                    event = "algebraic_gate_proxy"
                event_speed = float(vector[0])
            else:
                event = "escape_unresolved"
                event_speed = float(event_state @ vector / np.linalg.norm(event_state))
    else:
        event_time = float(integration.t_events[event_index][0])
        event_state = integration.y_events[event_index][0].copy()
        vector = vdp_field_point(
            event_time, event_state, r=r, a2=a2, epsilon=epsilon
        )
        if event_index == 1:
            gate = _pole_gate_coordinates(event_state)
            if gate["y"] > 0.0 and gate["D"] > 0.0 and gate["H"] > 0.0:
                event = "pole_gate_proxy"
            else:
                event = "algebraic_gate_proxy"
            event_speed = float(vector[0])
        else:
            event = "escape_unresolved"
            event_speed = float(event_state @ vector / np.linalg.norm(event_state))

    sampled_time_parts = []
    sampled_state_parts = []
    for part_index, part in enumerate(integrations):
        part_end = min(event_time, float(part.t[-1]))
        if part_end <= float(part.t[0]):
            continue
        part_times = np.linspace(
            float(part.t[0]),
            part_end,
            max(30, int(80 * (part_end - float(part.t[0]))) + 1),
        )
        if part_index:
            part_times = part_times[1:]
        sampled_time_parts.append(part_times)
        sampled_state_parts.append(part.sol(part_times))
    sample_times = np.concatenate(sampled_time_parts)
    sample_state = np.concatenate(sampled_state_parts, axis=1)
    angle = np.unwrap(np.arctan2(sample_state[2], sample_state[0]))
    whole_excursion_winding = float(
        np.sum(np.abs(np.diff(angle))) / (2.0 * pi)
    )
    if len(sampled_state_parts) > 1 and sampled_state_parts[1].shape[1] > 1:
        local_angle = np.unwrap(
            np.arctan2(sampled_state_parts[1][2], sampled_state_parts[1][0])
        )
        local_winding = float(
            np.sum(np.abs(np.diff(local_angle))) / (2.0 * pi)
        )
    else:
        local_winding = whole_excursion_winding
    energy = vdp_hamiltonian(sample_state, r, a2, epsilon)
    gate_diagnostics = _pole_gate_coordinates(event_state)
    coordinates = frame.coordinates(event_state)
    diagnostics: dict[str, float | str | bool] = {
        **source_diagnostics,
        "solver_success": bool(all(part.success for part in integrations)),
        "energy_drift": float(np.ptp(energy)),
        "energy_abs_max": float(np.max(np.abs(energy))),
        "terminal_state_norm": float(np.linalg.norm(event_state)),
        "terminal_unstable_radius": float(np.linalg.norm(coordinates[:2])),
        "terminal_stable_radius": float(np.linalg.norm(coordinates[2:])),
        "source_radius": float(source_radius),
        "local_return_radius": return_radius,
        "whole_excursion_absolute_angular_variation_turns": (
            whole_excursion_winding
        ),
        "local_passage_absolute_angular_variation_turns": local_winding,
        "event_semantics": (
            "actual first hit among the finite numerical completed return, stable-cut "
            "proxy, U gate, and escape sphere; not the exhaustive V6 face arrangement"
        ),
        **{f"pole_{key}": value for key, value in gate_diagnostics.items()},
    }
    if event.startswith("return"):
        target_coordinates = numerical_source_coordinates(
            event_state,
            frame=frame,
            r=r,
            a2=a2,
            epsilon=epsilon,
        )
        diagnostics.update(
            {
                "return_section": "same_numerical_unstable_radius_as_source",
                "return_target_phase": float(target_coordinates["phase"]),
                "return_target_transverse_coordinate": float(
                    target_coordinates["transverse_coordinate"]
                ),
                "return_target_radius": float(target_coordinates["radius"]),
                "return_target_reconstruction_defect": float(
                    target_coordinates["reconstruction_defect"]
                ),
                "return_sign_semantics": (
                    "sign of numerical target transverse coordinate"
                ),
            }
        )
    return FirstEventSample(
        phase=float(phase),
        transverse_coordinate=float(transverse_coordinate),
        source_state=source,
        event=event,
        event_time_xi=event_time,
        event_state=event_state,
        event_speed=event_speed,
        winding_proxy=local_winding,
        diagnostics=diagnostics,
        sample_time_xi=sample_times,
        sample_state=sample_state,
    )


def sample_first_event_atlas(
    phases: Iterable[float],
    transverse_coordinates: Iterable[float],
    *,
    r: float,
    a2: float,
    epsilon: float,
    source_radius: float = 0.01,
    local_return_radius: float | None = None,
    maximum_time: float = 80.0,
    terminal_u: float = -10.0,
    escape_norm: float = 60.0,
) -> list[FirstEventSample]:
    samples = []
    for transverse_coordinate in transverse_coordinates:
        for phase in phases:
            samples.append(
                integrate_first_event(
                    phase=float(phase),
                    transverse_coordinate=float(transverse_coordinate),
                    r=r,
                    a2=a2,
                    epsilon=epsilon,
                    source_radius=source_radius,
                    local_return_radius=local_return_radius,
                    maximum_time=maximum_time,
                    terminal_u=terminal_u,
                    escape_norm=escape_norm,
                )
            )
    return samples


def _full_homoclinic_value(result: HomoclinicResult, coordinate: Array) -> Array:
    coordinate = np.asarray(coordinate, dtype=float)
    values = np.empty((4, coordinate.size), dtype=float)
    positive = coordinate >= 0.0
    positive_coordinate = np.minimum(coordinate[positive], result.domain)
    negative_coordinate = np.minimum(-coordinate[~positive], result.domain)
    values[:, positive] = result.solution.sol(positive_coordinate)
    values[:, ~positive] = REVERSER[:, None] * result.solution.sol(negative_coordinate)
    return values


def _vdp_field_jacobian(
    state: Array, r: float, a2: float, epsilon: float
) -> Array:
    c, quadratic, cubic = vdp_coefficients(r, a2, epsilon)
    state = np.asarray(state)
    u = state[0]
    count = u.size if u.ndim else 1
    jacobian = np.zeros((4, 4, count), dtype=float)
    jacobian[0, 1] = 1.0
    jacobian[1, 0] = c - 2.0 * quadratic * u + 3.0 * cubic * u * u
    jacobian[1, 2] = -1.0
    jacobian[2, 3] = 1.0
    jacobian[3, 0] = 1.0
    return jacobian


def _physical_profile(
    xi: Array, state: Array, r: float, a2: float, epsilon: float
) -> tuple[Array, Array, Array]:
    a = 1.0 + np.sqrt(epsilon) * r**3 * a2
    physical_x = r * epsilon ** (-0.25) * xi
    physical_u = a - np.sqrt(epsilon) * r * r * state[0]
    physical_v = a**3 / 3.0 - a - epsilon * r**4 * state[2]
    return physical_x, physical_u, physical_v


def stationary_pde_residual(
    xi: Array, state: Array, r: float, a2: float, epsilon: float
) -> dict[str, float]:
    """Independent finite-difference residual in the physical x coordinate."""

    physical_x, physical_u, physical_v = _physical_profile(
        xi, state, r, a2, epsilon
    )
    edge_order = 2
    ux = np.gradient(physical_u, physical_x, edge_order=edge_order)
    uxx = np.gradient(ux, physical_x, edge_order=edge_order)
    vx = np.gradient(physical_v, physical_x, edge_order=edge_order)
    vxx = np.gradient(vx, physical_x, edge_order=edge_order)
    a = 1.0 + np.sqrt(epsilon) * r**3 * a2
    f_u = physical_u**3 / 3.0 - physical_u
    residual_u = physical_v - f_u + r**4 * uxx
    residual_v = epsilon * (a - physical_u) + vxx
    trim = max(4, xi.size // 500)
    interior = slice(trim, -trim)
    return {
        "physical_stationary_u_residual_inf": float(np.max(np.abs(residual_u[interior]))),
        "physical_stationary_v_residual_inf": float(np.max(np.abs(residual_v[interior]))),
        "finite_difference_trim_points": float(trim),
    }


def solve_symmetric_multipulse(
    homoclinic: HomoclinicResult,
    pulse_count: int,
    *,
    separation: float = 18.0,
    padding: float = 28.0,
    tolerance: float = 1.2e-6,
    max_nodes: int = 180_000,
    acceptance_thresholds: Mapping[str, float] | None = None,
) -> MultipulseOrbit:
    """Compute a symmetric positive-parameter multipulse by collocation."""

    if homoclinic.model != "vdp":
        raise ValueError("expected a van der Pol homoclinic")
    if pulse_count < 1:
        raise ValueError("pulse_count must be positive")
    thresholds = {
        "solver_rms_residual": float(tolerance),
        "boundary_residual": 1.0e-7,
        "tail_norm": 1.0e-5,
        "hamiltonian_drift": 5.0e-6,
        "physical_stationary_residual": 2.0e-6,
    }
    if acceptance_thresholds is not None:
        unknown = set(acceptance_thresholds) - set(thresholds)
        if unknown:
            raise ValueError(f"unknown multipulse acceptance keys: {sorted(unknown)}")
        thresholds.update(
            {key: float(value) for key, value in acceptance_thresholds.items()}
        )
    if any(value <= 0.0 for value in thresholds.values()):
        raise ValueError("multipulse acceptance thresholds must be positive")
    r, a2, epsilon = homoclinic.r, homoclinic.a2, homoclinic.epsilon
    if pulse_count == 1:
        xi, state = reflected_profile(homoclinic, points=12_001)
        physical_x, physical_u, physical_v = _physical_profile(
            xi, state, r, a2, epsilon
        )
        central_action = float(np.trapezoid(state[1] ** 2 - state[3] ** 2, xi))
        physical_action = float(epsilon**2.25 * r**5 * central_action)
        physical_residual = stationary_pde_residual(xi, state, r, a2, epsilon)
        primary_gate_passed = bool(
            float(homoclinic.diagnostics["normalized_ode_residual_inf"])
            <= thresholds["solver_rms_residual"]
            and float(homoclinic.diagnostics["boundary_residual_inf"])
            <= thresholds["boundary_residual"]
            and float(homoclinic.diagnostics["tail_norm"])
            <= thresholds["tail_norm"]
            and float(homoclinic.diagnostics["hamiltonian_drift"])
            <= thresholds["hamiltonian_drift"]
            and max(
                physical_residual["physical_stationary_u_residual_inf"],
                physical_residual["physical_stationary_v_residual_inf"],
            )
            <= thresholds["physical_stationary_residual"]
        )
        diagnostics: dict[str, float | int | str | bool] = {
            "solver_success": True,
            "evidence_status": "COMPUTED/E1 continued primary homoclinic",
            "residual_gate_passed": primary_gate_passed,
            "acceptance_thresholds": thresholds,
            "normalized_ode_residual_inf": float(
                homoclinic.diagnostics["normalized_ode_residual_inf"]
            ),
            "boundary_residual_inf": float(homoclinic.diagnostics["boundary_residual_inf"]),
            "tail_norm": float(homoclinic.diagnostics["tail_norm"]),
            "hamiltonian_drift": float(homoclinic.diagnostics["hamiltonian_drift"]),
            "truncated_physical_domain_length": float(
                physical_x[-1] - physical_x[0]
            ),
            "central_action": central_action,
            "physical_action": physical_action,
            **physical_residual,
        }
        return MultipulseOrbit(
            pulse_count_requested=1,
            pulse_count_observed=1,
            xi=xi,
            state=state,
            physical_x=physical_x,
            physical_u=physical_u,
            physical_v=physical_v,
            diagnostics=diagnostics,
        )

    positions = separation * (
        np.arange(pulse_count, dtype=float) - 0.5 * (pulse_count - 1)
    )
    domain = float(np.max(np.abs(positions)) + padding)
    mesh = np.linspace(0.0, domain, int(30 * domain) + 1)
    guess = sum(
        (_full_homoclinic_value(homoclinic, mesh - position) for position in positions),
        start=np.zeros((4, mesh.size), dtype=float),
    )
    complement = stable_complement(origin_matrix("vdp", r, a2, epsilon))
    field = vdp_field(r, a2, epsilon)

    def boundary(left: Array, right: Array) -> Array:
        return np.r_[left[1], left[3], complement @ right]

    solution = solve_bvp(
        field,
        boundary,
        mesh,
        guess,
        fun_jac=lambda _time, state: _vdp_field_jacobian(
            state, r, a2, epsilon
        ),
        tol=tolerance,
        bc_tol=min(2.0e-8, tolerance * 0.05),
        max_nodes=max_nodes,
        verbose=0,
    )
    half_xi = np.linspace(0.0, domain, max(6001, int(180 * domain) + 1))
    half_state = solution.sol(half_xi)
    xi = np.concatenate((-half_xi[:0:-1], half_xi))
    state = np.concatenate(
        (REVERSER[:, None] * half_state[:, :0:-1], half_state), axis=1
    )
    derivative = solution.sol(half_xi, 1)
    ode_residual = float(np.max(np.abs(derivative - field(half_xi, half_state))))
    boundary_residual = float(
        max(
            abs(half_state[1, 0]),
            abs(half_state[3, 0]),
            np.max(np.abs(complement @ half_state[:, -1])),
        )
    )
    peaks, _ = find_peaks(state[0], height=2.0, prominence=2.0)
    observed = int(peaks.size)
    energy = vdp_hamiltonian(state, r, a2, epsilon)
    physical_x, physical_u, physical_v = _physical_profile(
        xi, state, r, a2, epsilon
    )
    central_action = float(np.trapezoid(state[1] ** 2 - state[3] ** 2, xi))
    physical_action = float(epsilon**2.25 * r**5 * central_action)
    solver_rms_residual = float(np.max(solution.rms_residuals))
    physical_residual = stationary_pde_residual(xi, state, r, a2, epsilon)
    residual_gate_passed = bool(
        solution.success
        and observed == pulse_count
        and solver_rms_residual <= thresholds["solver_rms_residual"]
        and boundary_residual <= thresholds["boundary_residual"]
        and float(np.linalg.norm(half_state[:, -1]))
        <= thresholds["tail_norm"]
        and float(np.ptp(energy)) <= thresholds["hamiltonian_drift"]
        and max(
            physical_residual["physical_stationary_u_residual_inf"],
            physical_residual["physical_stationary_v_residual_inf"],
        )
        <= thresholds["physical_stationary_residual"]
    )
    diagnostics = {
        "solver_success": bool(solution.success),
        "solver_message": str(solution.message),
        "evidence_status": (
            "COMPUTED/E1 actual full-ODE multipulse"
            if residual_gate_passed
            else "INCONCLUSIVE multipulse collocation"
        ),
        "residual_gate_passed": residual_gate_passed,
        "acceptance_thresholds": thresholds,
        "nodes": int(solution.x.size),
        "solver_rms_residual_max": solver_rms_residual,
        "domain_half_xi": domain,
        "initial_guess_separation_xi": separation,
        "normalized_ode_residual_inf": ode_residual,
        "boundary_residual_inf": boundary_residual,
        "tail_norm": float(np.linalg.norm(half_state[:, -1])),
        "hamiltonian_drift": float(np.ptp(energy)),
        "hamiltonian_abs_max": float(np.max(np.abs(energy))),
        "truncated_physical_domain_length": float(
            physical_x[-1] - physical_x[0]
        ),
        "central_action": central_action,
        "physical_action": physical_action,
        **physical_residual,
    }
    return MultipulseOrbit(
        pulse_count_requested=pulse_count,
        pulse_count_observed=observed,
        xi=xi,
        state=state,
        physical_x=physical_x,
        physical_u=physical_u,
        physical_v=physical_v,
        diagnostics=diagnostics,
    )


def periodic_profile_diagnostics(
    orbit: PeriodicOrbit, *, r: float, a2: float, epsilon: float
) -> dict[str, float | str]:
    residual = stationary_pde_residual(
        orbit.xi, orbit.state, r, a2, epsilon
    )
    return {
        "evidence_status": "COMPUTED/E1 actual reversible periodic orbit",
        "closure_residual": float(orbit.diagnostics["closure_residual"]),
        "hamiltonian_drift": float(orbit.diagnostics["hamiltonian_drift"]),
        "physical_period": float(orbit.diagnostics["physical_period"]),
        "physical_action": float(orbit.physical_action),
        **residual,
    }


def finite_window_approximants(
    multipulses: list[MultipulseOrbit], word: list[str]
) -> list[dict[str, object]]:
    """Package nested finite-word computations without claiming an infinite orbit.

    The computed multipulses are actual ODE solutions.  Their symbolic labels
    are requested finite-word metadata unless a separate V6 itinerary checker
    has identified every return branch.  The distinction is explicit in each
    record.
    """

    records: list[dict[str, object]] = []
    center = len(word) // 2
    for level, orbit in enumerate(multipulses, start=1):
        half_width = min(center, level)
        requested_word = word[center - half_width : center + half_width + 1]
        records.append(
            {
                "level": level,
                "requested_finite_word": requested_word,
                "pulse_count": orbit.pulse_count_observed,
                "solver_success": bool(orbit.diagnostics["solver_success"]),
                "status": "COMPUTED/E1 finite-window homoclinic approximant",
                "coding_status": (
                    "word metadata only; a full numerical V6 branch-itinerary "
                    "identification is not yet resolved"
                ),
                "central_window_x": float(
                    min(abs(orbit.physical_x[0]), abs(orbit.physical_x[-1])) / 3.0
                ),
            }
        )
    return records


def event_sample_record(sample: FirstEventSample) -> dict[str, object]:
    return {
        "phase": sample.phase,
        "transverse_coordinate": sample.transverse_coordinate,
        "event": sample.event,
        "event_time_xi": sample.event_time_xi,
        "event_speed": sample.event_speed,
        "winding_proxy": sample.winding_proxy,
        "source_state": sample.source_state.tolist(),
        "event_state": sample.event_state.tolist(),
        "diagnostics": sample.diagnostics,
    }
