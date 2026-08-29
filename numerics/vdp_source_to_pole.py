"""Floating-point V2-source-to-V3-pole candidates for van der Pol.

The routines in this module close a numerical seam that is deliberately left
open by :mod:`numerics.vdp_pole`: they construct a finite-horizon
approximation of the *nonlinear unstable graph*, continue the frozen core
source as in V2 equations (27)--(28), and integrate one and the same physical
positive-parameter orbit from that source through the pole gate and into the
local pole chart.

This remains ``COMPUTED/E1`` evidence.  The finite-horizon boundary-value
problem is not an interval enclosure of the unstable graph, the exploratory
parameter is not certified to lie in the existential V3 box, and the fitted
entry into the local pole chart is not the deferred interval validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp
from scipy.optimize import root

from numerics.rfsn_numerics import (
    CORE_SOURCE_STATE,
    vdp_coefficients,
    vdp_field_point,
    vdp_hamiltonian,
)
from numerics.vdp_bridge import (
    BridgeParameters,
    central_to_physical,
    physical_to_central,
)
from numerics.vdp_pole import (
    PoleLabels,
    PoleParameters,
    PoleRealization,
    action_density,
    cubic_potential,
    divergent_action,
    fixed_source_energy_kappa,
    physical_field,
    physical_hamiltonian,
    physical_to_compact,
    pole_energy_from_labels,
    realize_local_pole,
)
Array = NDArray[np.float64]

SOURCE_TO_POLE_CANDIDATE_STATUS = "COMPUTED/E1_SOURCE_TO_POLE"
WINDOW_CANDIDATE_STATUS = "COMPUTED/E1_V2_SOURCE_WINDOW_TO_POLE_GATE"
KATO_DARBOUX_SECTION_STATUS = (
    "COMPUTED/E1_KATO_COMPATIBLE_DARBOUX_SECTION"
)
KATO_DARBOUX_INCONCLUSIVE_STATUS = (
    "INCONCLUSIVE/E1_KATO_COMPATIBLE_DARBOUX_SECTION"
)
THEOREM_VALIDATION_STATUS = "NOT_INTERVAL_VALIDATED (#7)"

# The physical coordinate order is (U,P,V,Q).  This is the matrix in
# CENTRAL_CONTINUATION.md, Section 5, so ``omega(v,w)=v.T@OMEGA@w``.
CENTRAL_SYMPLECTIC_MATRIX = np.array(
    [
        [0.0, -1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
        [0.0, 0.0, -1.0, 0.0],
    ],
    dtype=np.float64,
)
CENTRAL_REVERSER_MATRIX = np.diag([1.0, -1.0, 1.0, -1.0])

CORE_HOMOCLINIC_PHASE = 0.5 * (
    5.8615055856447817 + 5.8615055856450482
)


def _json_ready(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


@dataclass(frozen=True)
class SourceFrame:
    """Exact-formula algebraic and normalized-Kato saddle frames.

    ``unstable`` is the algebraic frame ``E`` used by the true unstable graph.
    ``kato_unstable`` is ``K=E C_AK``, where the matrix ``C_AK`` and its
    phase rotation are exactly the formulas audited in
    ``vdp_p2_kato_probe.cpp``.  Thus this is not the independently
    phase-fixed numerical eigenframe from :mod:`numerics.vdp_return_coding`.
    """

    unstable: Array
    stable: Array
    inverse: Array
    kato_unstable: Array
    kato_stable: Array
    kato_to_algebraic: Array
    phase_rotation: Array
    c: float
    alpha: float
    beta: float
    y: float
    chi: float
    radial_scale: float

    def coordinates(self, state: Array) -> Array:
        return self.inverse @ np.asarray(state, dtype=np.float64)

    def kato_phase_from_algebraic(self, coordinates: Array) -> float:
        """Invert the degree-one ``R_chi`` source-phase convention."""

        rotated = self.phase_rotation.T @ np.asarray(
            coordinates, dtype=np.float64
        )
        return float(np.arctan2(rotated[1], rotated[0]) % (2.0 * np.pi))


@dataclass(frozen=True)
class KatoSourceParameters:
    """Central source parameters, including the theorem's ``r=0`` face."""

    r: float
    a2: float
    epsilon: float

    def __post_init__(self) -> None:
        if not np.isfinite(self.r) or self.r < 0.0:
            raise ValueError("r must be finite and nonnegative")
        if not np.isfinite(self.a2):
            raise ValueError("a2 must be finite")
        if not np.isfinite(self.epsilon) or self.epsilon <= 0.0:
            raise ValueError("epsilon must be finite and positive")


def _as_kato_source_parameters(
    parameters: KatoSourceParameters | PoleParameters,
) -> KatoSourceParameters:
    return KatoSourceParameters(
        r=float(parameters.r),
        a2=float(parameters.a2),
        epsilon=float(parameters.epsilon),
    )


@dataclass(frozen=True)
class KatoDarbouxSourcePoint:
    """One finite-horizon, zero-energy Kato-compatible source point.

    The construction uses the exact Kato phase convention and a numerically
    canonical transverse coordinate along the computed nonlinear ``W^u``
    spine.  It is deliberately *not* identified with the paper's existential
    nonlinear Moser/Darboux chart; see ``raw_chart_identical``.
    """

    phase: float
    nu: float
    state: Array | None
    true_wu_state: Array | None
    status: str
    raw_chart_identical: bool
    diagnostics: dict[str, float | str | bool]


@dataclass(frozen=True)
class KatoDarbouxSourceCoordinates:
    """Numerical inverse coordinates on the Kato-compatible source section."""

    phase: float
    nu: float
    energy_correction_coordinate: float
    source_radius: float
    reconstructed_state: Array
    status: str
    raw_chart_identical: bool
    diagnostics: dict[str, float | str | bool]


@dataclass(frozen=True)
class V2SourceCandidate:
    parameters: PoleParameters
    phase: float
    source_radius: float
    flowback_tau: float
    graph_horizon: float
    core_state: Array
    b0: Array
    local_graph_state: Array
    source_state: Array
    diagnostics: dict[str, float | str | bool]

    def as_json_dict(self) -> dict[str, Any]:
        return _json_ready(
            {
                "parameters": {
                    "r": self.parameters.r,
                    "a2": self.parameters.a2,
                    "epsilon": self.parameters.epsilon,
                },
                "phase": self.phase,
                "source_radius": self.source_radius,
                "flowback_tau": self.flowback_tau,
                "graph_horizon": self.graph_horizon,
                "core_state": self.core_state,
                "b0": self.b0,
                "local_graph_state": self.local_graph_state,
                "source_state": self.source_state,
                "diagnostics": self.diagnostics,
            }
        )


@dataclass(frozen=True)
class PoleGateHit:
    phase: float
    physical_time: float
    central_time: float
    central_state: Array
    physical_state: Array
    cone: dict[str, float]
    diagnostics: dict[str, float | str | bool]

    def as_json_dict(self) -> dict[str, Any]:
        return _json_ready(
            {
                "phase": self.phase,
                "physical_time": self.physical_time,
                "central_time": self.central_time,
                "central_state": self.central_state,
                "physical_state": self.physical_state,
                "cone": self.cone,
                "diagnostics": self.diagnostics,
            }
        )


@dataclass(frozen=True)
class PoleEndFit:
    level_u: Array
    hit_x: Array
    hit_state: Array
    remaining_sigma: Array
    compact_state: Array
    blowup_estimate_ladder: Array
    z0_ladder: Array
    w0_ladder: Array
    labels: PoleLabels
    diagnostics: dict[str, float | str | bool]

    def as_json_dict(self) -> dict[str, Any]:
        return _json_ready(
            {
                "level_u": self.level_u,
                "hit_x": self.hit_x,
                "hit_state": self.hit_state,
                "remaining_sigma": self.remaining_sigma,
                "compact_state": self.compact_state,
                "blowup_estimate_ladder": self.blowup_estimate_ladder,
                "z0_ladder": self.z0_ladder,
                "w0_ladder": self.w0_ladder,
                "labels": {
                    "z0": self.labels.z0,
                    "w0": self.labels.w0,
                    "kappa": self.labels.kappa,
                },
                "diagnostics": self.diagnostics,
            }
        )


@dataclass(frozen=True)
class SameOrbitActionLadder:
    """Source-anchored V3 action subtraction on the connected physical IVP."""

    source_cut_x: float
    sigma: Array
    endpoint_x: Array
    raw_action: Array
    divergent_part: Array
    subtracted_action: Array
    density: Array
    diagnostics: dict[str, float | str | bool]

    def as_json_dict(self) -> dict[str, Any]:
        return _json_ready(
            {
                "status": "COMPUTED/E1_SAME_ORBIT_ACTION_FINITE_PART",
                "theorem_validation_status": THEOREM_VALIDATION_STATUS,
                "source_cut_x": self.source_cut_x,
                "sigma": self.sigma,
                "endpoint_x": self.endpoint_x,
                "raw_action": self.raw_action,
                "divergent_part": self.divergent_part,
                "subtracted_action": self.subtracted_action,
                "density": self.density,
                "diagnostics": self.diagnostics,
            }
        )


@dataclass
class SourceToPoleConnection:
    source: V2SourceCandidate
    gate: PoleGateHit
    end_fit: PoleEndFit
    action_ladder: SameOrbitActionLadder
    local_realization: PoleRealization
    physical_x: Array
    physical_state: Array
    physical_action: Array
    global_on_local_sigma: Array
    global_compact_on_local_sigma: Array
    diagnostics: dict[str, float | str | bool]
    dense_physical_solution: Any = field(repr=False)

    def as_json_dict(self) -> dict[str, Any]:
        return _json_ready(
            {
                "status": SOURCE_TO_POLE_CANDIDATE_STATUS,
                "theorem_validation_status": THEOREM_VALIDATION_STATUS,
                "source": self.source.as_json_dict(),
                "gate": self.gate.as_json_dict(),
                "end_fit": self.end_fit.as_json_dict(),
                "action_ladder": self.action_ladder.as_json_dict(),
                "local_realization_diagnostics": self.local_realization.diagnostics,
                "diagnostics": self.diagnostics,
            }
        )

    def as_npz_payload(self) -> dict[str, Array]:
        return {
            "physical_x": self.physical_x,
            "physical_state": self.physical_state,
            "physical_action": self.physical_action,
            "level_u": self.end_fit.level_u,
            "level_hit_x": self.end_fit.hit_x,
            "level_hit_state": self.end_fit.hit_state,
            "remaining_sigma": self.end_fit.remaining_sigma,
            "global_compact_level": self.end_fit.compact_state,
            "local_sigma": self.local_realization.sigma,
            "local_compact": self.local_realization.compact,
            "local_physical": self.local_realization.physical,
            "global_on_local_sigma": self.global_on_local_sigma,
            "global_compact_on_local_sigma": self.global_compact_on_local_sigma,
            "action_sigma": self.action_ladder.sigma,
            "action_endpoint_x": self.action_ladder.endpoint_x,
            "action_raw": self.action_ladder.raw_action,
            "action_divergent_part": self.action_ladder.divergent_part,
            "action_subtracted": self.action_ladder.subtracted_action,
            "action_density": self.action_ladder.density,
        }


@dataclass(frozen=True)
class PoleWindowCandidate:
    parameters: PoleParameters
    phases: Array
    source_states: Array
    gate_times_x: Array
    gate_times_xi: Array
    gate_states: Array
    cone_y: Array
    cone_d: Array
    cone_k: Array
    cone_y_prime: Array
    cone_k_prime: Array
    diagnostics: dict[str, float | str | bool]

    def as_json_dict(self) -> dict[str, Any]:
        return _json_ready(
            {
                "status": WINDOW_CANDIDATE_STATUS,
                "theorem_validation_status": THEOREM_VALIDATION_STATUS,
                "parameters": {
                    "r": self.parameters.r,
                    "a2": self.parameters.a2,
                    "epsilon": self.parameters.epsilon,
                },
                "phases": self.phases,
                "source_states": self.source_states,
                "gate_times_x": self.gate_times_x,
                "gate_times_xi": self.gate_times_xi,
                "gate_states": self.gate_states,
                "cone_y": self.cone_y,
                "cone_d": self.cone_d,
                "cone_k": self.cone_k,
                "cone_y_prime": self.cone_y_prime,
                "cone_k_prime": self.cone_k_prime,
                "diagnostics": self.diagnostics,
            }
        )

    def as_npz_payload(self) -> dict[str, Array]:
        return {
            "phase": self.phases,
            "source_state": self.source_states,
            "gate_time_x": self.gate_times_x,
            "gate_time_xi": self.gate_times_xi,
            "gate_state": self.gate_states,
            "cone_y": self.cone_y,
            "cone_D": self.cone_d,
            "cone_K": self.cone_k,
            "cone_y_prime": self.cone_y_prime,
            "cone_K_prime": self.cone_k_prime,
        }


def calibrated_source_frame(r: float, a2: float, epsilon: float) -> SourceFrame:
    """Evaluate the P2bK algebraic/Kato frame formulas in binary64.

    With ``c=2*r*a2+sqrt(epsilon)*r**4*a2**2``, this implements

    ``alpha=.5*sqrt(2+c)``, ``beta=.5*sqrt(2-c)``,
    ``chi=atan(y)``, and ``K=E C_AK``

    with the same sign and column order as
    ``validation/rigorous/src/vdp_p2_kato_probe.cpp``.  The matrix
    ``C_AK=sigma R_chi`` maps normalized Kato coordinates to algebraic
    unstable coordinates.  The source circle itself uses ``R_chi`` (without
    ``sigma``), exactly as equation (28) of ``CENTRAL_CONTINUATION.md``.
    """

    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    c, _quadratic, _cubic = vdp_coefficients(r, a2, epsilon)
    if abs(c) >= 2.0:
        raise ValueError("the Kato saddle-focus frame requires |c| < 2")
    alpha = 0.5 * np.sqrt(2.0 + c)
    beta = 0.5 * np.sqrt(2.0 - c)
    root_two = np.sqrt(2.0)
    y = -c / (
        np.sqrt(2.0 - c) * (root_two + np.sqrt(2.0 + c))
    )
    chi = float(np.arctan(y))
    normalizer = np.sqrt(
        6.0 * alpha * alpha - 4.0 * root_two * alpha + 3.0
    )
    rotation_denominator = np.sqrt(1.0 + y * y)
    phase_rotation = np.array(
        [[1.0, -y], [y, 1.0]], dtype=np.float64
    ) / rotation_denominator
    kato_to_algebraic = np.array(
        [[1.0, -y], [y, 1.0]], dtype=np.float64
    ) / normalizer
    radial_scale = float(rotation_denominator / normalizer)
    h = 2.0 * alpha * beta
    unstable = np.array(
        [
            [1.0, 0.0],
            [alpha, -beta],
            [0.5 * c, h],
            [alpha, beta],
        ],
        dtype=np.float64,
    )
    stable = CENTRAL_REVERSER_MATRIX @ unstable
    basis = np.column_stack((unstable, stable))
    inverse = np.linalg.inv(basis)
    kato_unstable = unstable @ kato_to_algebraic
    kato_stable = CENTRAL_REVERSER_MATRIX @ kato_unstable
    return SourceFrame(
        unstable=unstable,
        stable=stable,
        inverse=inverse,
        kato_unstable=kato_unstable,
        kato_stable=kato_stable,
        kato_to_algebraic=kato_to_algebraic,
        phase_rotation=phase_rotation,
        c=float(c),
        alpha=float(alpha),
        beta=float(beta),
        y=float(y),
        chi=chi,
        radial_scale=radial_scale,
    )


def _integrate_central(
    state: Array,
    span: tuple[float, float],
    *,
    r: float,
    a2: float,
    epsilon: float,
    rtol: float,
    atol: float,
    max_step: float,
) -> Any:
    integration = solve_ivp(
        lambda time, value: vdp_field_point(
            time, value, r=r, a2=a2, epsilon=epsilon
        ),
        span,
        np.asarray(state, dtype=np.float64),
        method="DOP853",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
        dense_output=True,
    )
    if not integration.success:
        raise RuntimeError(integration.message)
    return integration


def finite_horizon_unstable_graph_state(
    *,
    r: float,
    a2: float,
    epsilon: float,
    unstable_coordinates: Sequence[float],
    horizon: float = 10.0,
    initial_stable_coordinates: Sequence[float] = (0.0, 0.0),
    boundary_tolerance: float = 1.0e-8,
    rtol: float = 2.0e-11,
    atol: float = 2.0e-13,
    max_step: float = 0.03,
) -> tuple[Array, dict[str, float | str | bool]]:
    """Solve the finite-horizon nonlinear unstable-graph BVP.

    In the phase-calibrated saddle coordinates ``(u,s)``, the boundary
    conditions are

    ``u(0)=unstable_coordinates`` and ``s(-horizon)=0``.

    We solve the equivalent two-variable shooting problem: write
    ``z(0)=E_u u+E_s s_0`` and find ``s_0`` so that the backward endpoint has
    zero stable coordinates.  This approximates one point of the true
    nonlinear unstable graph; it is not the zero-energy linear-section proxy
    used by the finite V6 event atlas.
    """

    coordinates = np.asarray(unstable_coordinates, dtype=np.float64)
    if coordinates.shape != (2,) or not np.all(np.isfinite(coordinates)):
        raise ValueError("unstable_coordinates must be a finite two-vector")
    if horizon <= 0.0:
        raise ValueError("horizon must be positive")
    if boundary_tolerance <= 0.0:
        raise ValueError("boundary_tolerance must be positive")
    frame = calibrated_source_frame(r, a2, epsilon)

    evaluation_count = 0

    def backward_residual(stable_coordinates: Array) -> Array:
        nonlocal evaluation_count
        evaluation_count += 1
        endpoint = (
            frame.unstable @ coordinates
            + frame.stable @ np.asarray(stable_coordinates, dtype=np.float64)
        )
        integration = _integrate_central(
            endpoint,
            (0.0, -float(horizon)),
            r=r,
            a2=a2,
            epsilon=epsilon,
            rtol=rtol,
            atol=atol,
            max_step=max_step,
        )
        return frame.coordinates(integration.y[:, -1])[2:]

    solve = root(
        backward_residual,
        np.asarray(initial_stable_coordinates, dtype=np.float64),
        method="hybr",
        tol=min(1.0e-11, 0.1 * boundary_tolerance),
    )
    residual = np.asarray(backward_residual(solve.x), dtype=np.float64)
    residual_inf = float(np.max(np.abs(residual)))
    if residual_inf > boundary_tolerance:
        raise RuntimeError(
            "finite-horizon unstable-graph solve did not resolve its boundary "
            f"condition: {residual_inf:.3e}"
        )
    state = frame.unstable @ coordinates + frame.stable @ solve.x
    backward = _integrate_central(
        state,
        (0.0, -float(horizon)),
        r=r,
        a2=a2,
        epsilon=epsilon,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    endpoint_coordinates = frame.coordinates(backward.y[:, -1])
    state_coordinates = frame.coordinates(state)
    energy = float(vdp_hamiltonian(state[:, None], r, a2, epsilon)[0])
    return state, {
        "status": "COMPUTED/E1_FINITE_HORIZON_UNSTABLE_GRAPH_BVP",
        "solver_reported_success": bool(solve.success),
        "boundary_residual_inf": residual_inf,
        "boundary_residual_tolerance": float(boundary_tolerance),
        "boundary_residual_passed": bool(residual_inf <= boundary_tolerance),
        "source_coordinate_residual_inf": float(
            np.max(np.abs(state_coordinates[:2] - coordinates))
        ),
        "backward_endpoint_norm": float(np.linalg.norm(backward.y[:, -1])),
        "backward_endpoint_stable_norm": float(
            np.linalg.norm(endpoint_coordinates[2:])
        ),
        "stable_coordinate_norm": float(np.linalg.norm(solve.x)),
        "central_energy_abs": abs(energy),
        "root_function_evaluations": float(evaluation_count),
        "scope_note": (
            "Finite-horizon floating-point approximation of the nonlinear W^u "
            "graph; not an interval enclosure or a uniform graph theorem."
        ),
    }


def _wrapped_phase_difference(left: float, right: float) -> float:
    return float(((left - right + np.pi) % (2.0 * np.pi)) - np.pi)


def _vdp_hamiltonian_gradient(
    state: Array, *, r: float, a2: float, epsilon: float
) -> Array:
    """Gradient of the central Hamiltonian in ``(U,P,V,Q)`` order."""

    u, p, v, q = np.asarray(state, dtype=np.float64)
    c, quadratic, _cubic = vdp_coefficients(r, a2, epsilon)
    return np.array(
        [
            -v
            + c * u
            - quadratic * u * u
            + np.sqrt(epsilon) * r * r * u**3 / 3.0,
            -p,
            -u,
            q,
        ],
        dtype=np.float64,
    )


def _kato_true_wu_source_state(
    parameters: KatoSourceParameters,
    phase: float,
    *,
    source_radius: float,
    graph_horizon: float,
    graph_boundary_tolerance: float,
    rtol: float,
    atol: float,
    max_step: float,
) -> tuple[Array, SourceFrame, dict[str, float | str | bool]]:
    """Compute equation (28)'s direct finite-horizon true-``W^u`` source."""

    frame = calibrated_source_frame(
        parameters.r, parameters.a2, parameters.epsilon
    )
    phase_vector = np.array(
        [np.cos(phase), np.sin(phase)], dtype=np.float64
    )
    algebraic_unstable = (
        source_radius * frame.phase_rotation @ phase_vector
    )
    state, graph_diagnostics = finite_horizon_unstable_graph_state(
        r=parameters.r,
        a2=parameters.a2,
        epsilon=parameters.epsilon,
        unstable_coordinates=algebraic_unstable,
        horizon=graph_horizon,
        boundary_tolerance=graph_boundary_tolerance,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    state_coordinates = frame.coordinates(state)
    recovered_phase = frame.kato_phase_from_algebraic(
        state_coordinates[:2]
    )
    return state, frame, {
        "graph_boundary_residual_inf": float(
            graph_diagnostics["boundary_residual_inf"]
        ),
        "graph_source_coordinate_residual_inf": float(
            graph_diagnostics["source_coordinate_residual_inf"]
        ),
        "graph_backward_endpoint_norm": float(
            graph_diagnostics["backward_endpoint_norm"]
        ),
        "graph_energy_abs": float(graph_diagnostics["central_energy_abs"]),
        "algebraic_unstable_radius": float(
            np.linalg.norm(state_coordinates[:2])
        ),
        "source_radius_error": float(
            np.linalg.norm(state_coordinates[:2]) - source_radius
        ),
        "recovered_kato_phase": recovered_phase,
        "kato_phase_error": _wrapped_phase_difference(
            recovered_phase, phase
        ),
        "c": frame.c,
        "alpha": frame.alpha,
        "beta": frame.beta,
        "y": frame.y,
        "chi": frame.chi,
        "radial_scale_sigma": frame.radial_scale,
    }


def _kato_wu_section_geometry(
    parameters: KatoSourceParameters,
    phase: float,
    *,
    source_radius: float,
    graph_horizon: float,
    phase_difference_step: float,
    graph_boundary_tolerance: float,
    rtol: float,
    atol: float,
    max_step: float,
) -> tuple[
    Array,
    SourceFrame,
    Array,
    Array,
    Array,
    dict[str, float | str | bool],
]:
    """Return the true-``W^u`` spine and its canonical stable directions.

    If ``t=dS/dphi`` and ``E_s`` is the Kato stable plane, let
    ``g=t^T Omega E_s``.  We choose ``n`` and ``m`` in that plane so that

    ``omega(t,n)=1`` and ``omega(t,m)=0``.

    Hence ``nu=omega(t,z-S(phi))`` has the positive Kato orientation at the
    nonlinear unstable spine.  The second direction is reserved for the
    scalar zero-energy correction.
    """

    if phase_difference_step <= 0.0:
        raise ValueError("phase_difference_step must be positive")
    state, frame, diagnostics = _kato_true_wu_source_state(
        parameters,
        phase,
        source_radius=source_radius,
        graph_horizon=graph_horizon,
        graph_boundary_tolerance=graph_boundary_tolerance,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    plus, _plus_frame, plus_diagnostics = _kato_true_wu_source_state(
        parameters,
        phase + phase_difference_step,
        source_radius=source_radius,
        graph_horizon=graph_horizon,
        graph_boundary_tolerance=graph_boundary_tolerance,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    minus, _minus_frame, minus_diagnostics = _kato_true_wu_source_state(
        parameters,
        phase - phase_difference_step,
        source_radius=source_radius,
        graph_horizon=graph_horizon,
        graph_boundary_tolerance=graph_boundary_tolerance,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    phase_tangent = (plus - minus) / (2.0 * phase_difference_step)
    pairings = phase_tangent @ CENTRAL_SYMPLECTIC_MATRIX @ frame.kato_stable
    pairing_norm = float(np.linalg.norm(pairings))
    if not np.isfinite(pairing_norm) or pairing_norm <= 1.0e-12:
        raise RuntimeError(
            "Kato source tangent does not resolve a stable Darboux direction"
        )
    normal_direction = frame.kato_stable @ (
        pairings / (pairing_norm * pairing_norm)
    )
    kernel_direction = frame.kato_stable @ (
        np.array([-pairings[1], pairings[0]], dtype=np.float64)
        / pairing_norm
    )
    orientation_pairing = float(
        phase_tangent @ CENTRAL_SYMPLECTIC_MATRIX @ normal_direction
    )
    kernel_pairing = float(
        phase_tangent @ CENTRAL_SYMPLECTIC_MATRIX @ kernel_direction
    )
    diagnostics.update(
        {
            "phase_difference_step": float(phase_difference_step),
            "phase_tangent_norm": float(np.linalg.norm(phase_tangent)),
            "phase_tangent_symplectic_stable_pairing_norm": pairing_norm,
            "canonical_orientation_pairing": orientation_pairing,
            "energy_correction_kernel_pairing": kernel_pairing,
            "maximum_tangent_graph_boundary_residual_inf": float(
                max(
                    diagnostics["graph_boundary_residual_inf"],
                    plus_diagnostics["graph_boundary_residual_inf"],
                    minus_diagnostics["graph_boundary_residual_inf"],
                )
            ),
        }
    )
    return (
        state,
        frame,
        phase_tangent,
        normal_direction,
        kernel_direction,
        diagnostics,
    )


def compute_kato_darboux_source_point(
    parameters: KatoSourceParameters | PoleParameters,
    phase: float,
    nu: float,
    *,
    source_radius: float = 0.01,
    graph_horizon: float = 8.0,
    phase_difference_step: float = 2.0e-5,
    graph_boundary_tolerance: float = 2.0e-10,
    energy_tolerance: float = 2.0e-11,
    maximum_abs_nu: float | None = None,
    maximum_energy_correction: float = 0.1,
    rtol: float = 2.0e-11,
    atol: float = 2.0e-13,
    max_step: float = 0.03,
) -> KatoDarbouxSourcePoint:
    """Construct a minimal Kato-compatible numerical source section.

    ``nu=0`` is the direct finite-horizon nonlinear unstable graph from
    equation (28), not a linear zero-energy proxy.  For small nonzero ``nu``
    we move in the stable direction normalized by
    ``omega(dS/dphi,dz/dnu)=+1`` and solve one scalar equation in the
    symplectic-orthogonal stable direction to restore ``H=0``.

    This is a reproducible E1 section and inverse-coordinate convention.  It
    does not integrate or identify the paper's existential exact nonlinear
    Moser chart, so ``raw_chart_identical`` is always ``False``.  Failure of
    the local energy solve returns an explicit ``INCONCLUSIVE`` status.
    """

    parameters = _as_kato_source_parameters(parameters)
    if source_radius <= 0.0:
        raise ValueError("source_radius must be positive")
    if graph_horizon <= 0.0:
        raise ValueError("graph_horizon must be positive")
    if energy_tolerance <= 0.0:
        raise ValueError("energy_tolerance must be positive")
    phase = float(phase)
    nu = float(nu)
    if not np.isfinite(phase) or not np.isfinite(nu):
        raise ValueError("phase and nu must be finite")
    if maximum_abs_nu is None:
        maximum_abs_nu = 0.1 * source_radius * source_radius
    if maximum_abs_nu <= 0.0:
        raise ValueError("maximum_abs_nu must be positive")
    if abs(nu) > maximum_abs_nu:
        raise ValueError(
            f"|nu|={abs(nu):.3e} exceeds the local source bound "
            f"{maximum_abs_nu:.3e}"
        )

    try:
        (
            wu_state,
            frame,
            phase_tangent,
            normal_direction,
            kernel_direction,
            geometry_diagnostics,
        ) = _kato_wu_section_geometry(
            parameters,
            phase,
            source_radius=source_radius,
            graph_horizon=graph_horizon,
            phase_difference_step=phase_difference_step,
            graph_boundary_tolerance=graph_boundary_tolerance,
            rtol=rtol,
            atol=atol,
            max_step=max_step,
        )
    except RuntimeError as error:
        return KatoDarbouxSourcePoint(
            phase=phase,
            nu=nu,
            state=None,
            true_wu_state=None,
            status=KATO_DARBOUX_INCONCLUSIVE_STATUS,
            raw_chart_identical=False,
            diagnostics={
                "reason": str(error),
                "claim_bearing": False,
                "theorem_validation_status": THEOREM_VALIDATION_STATUS,
                "raw_chart_identical": False,
            },
        )

    correction = 0.0
    state = np.asarray(wu_state, dtype=np.float64).copy()
    newton_iterations = 0
    newton_reason = "nu_zero_true_Wu_spine"
    if nu != 0.0:
        base_state = wu_state + nu * normal_direction
        correction = 0.0
        newton_reason = "maximum_iterations_reached"
        for iteration in range(16):
            newton_iterations = iteration + 1
            state = base_state + correction * kernel_direction
            energy = float(
                vdp_hamiltonian(
                    state[:, None],
                    parameters.r,
                    parameters.a2,
                    parameters.epsilon,
                )[0]
            )
            if abs(energy) <= energy_tolerance:
                newton_reason = "energy_tolerance_reached"
                break
            derivative = float(
                _vdp_hamiltonian_gradient(
                    state,
                    r=parameters.r,
                    a2=parameters.a2,
                    epsilon=parameters.epsilon,
                )
                @ kernel_direction
            )
            if not np.isfinite(derivative) or abs(derivative) <= 1.0e-13:
                newton_reason = "energy_correction_derivative_unresolved"
                break
            correction -= energy / derivative
            if (
                not np.isfinite(correction)
                or abs(correction) > maximum_energy_correction
            ):
                newton_reason = "energy_correction_left_local_domain"
                break
        state = base_state + correction * kernel_direction

    energy = float(
        vdp_hamiltonian(
            state[:, None],
            parameters.r,
            parameters.a2,
            parameters.epsilon,
        )[0]
    )
    coordinates = frame.coordinates(state)
    expected_unstable = source_radius * frame.phase_rotation @ np.array(
        [np.cos(phase), np.sin(phase)], dtype=np.float64
    )
    unstable_coordinate_defect = float(
        np.linalg.norm(coordinates[:2] - expected_unstable)
    )
    recovered_nu = float(
        phase_tangent
        @ CENTRAL_SYMPLECTIC_MATRIX
        @ (state - wu_state)
    )
    local_correction_passed = bool(
        np.isfinite(correction)
        and abs(correction) <= maximum_energy_correction
        and newton_reason
        not in {
            "energy_correction_derivative_unresolved",
            "energy_correction_left_local_domain",
            "maximum_iterations_reached",
        }
    )
    gates_passed = bool(
        abs(energy) <= energy_tolerance
        and local_correction_passed
        and unstable_coordinate_defect <= 2.0e-11
        and abs(recovered_nu - nu) <= max(2.0e-13, 2.0e-8 * abs(nu))
        and geometry_diagnostics["graph_boundary_residual_inf"]
        <= graph_boundary_tolerance
        and geometry_diagnostics["canonical_orientation_pairing"] > 0.0
    )
    status = (
        KATO_DARBOUX_SECTION_STATUS
        if gates_passed
        else KATO_DARBOUX_INCONCLUSIVE_STATUS
    )
    diagnostics: dict[str, float | str | bool] = {
        **geometry_diagnostics,
        "status": status,
        "theorem_validation_status": THEOREM_VALIDATION_STATUS,
        "claim_bearing": False,
        "raw_chart_identical": False,
        "nu_zero_is_finite_horizon_nonlinear_Wu": bool(nu == 0.0),
        "central_energy_abs": abs(energy),
        "central_energy_tolerance": float(energy_tolerance),
        "energy_correction_coordinate": float(correction),
        "maximum_energy_correction": float(maximum_energy_correction),
        "local_energy_correction_passed": local_correction_passed,
        "energy_correction_newton_iterations": float(newton_iterations),
        "energy_correction_stop_reason": newton_reason,
        "unstable_coordinate_defect": unstable_coordinate_defect,
        "recovered_nu": recovered_nu,
        "nu_roundtrip_defect": float(recovered_nu - nu),
        "section_gates_passed": gates_passed,
        "coordinate_semantics": (
            "Kato phase from u=R R_chi e_phi; nu is the first-order "
            "Darboux coordinate omega(dS/dphi,z-S(phi)) on the computed "
            "finite-horizon nonlinear-Wu spine."
        ),
        "scope_note": (
            "Kato-compatible numerical zero-energy section; not the raw "
            "Moser chart, not an exact-action certificate, and not interval "
            "validation."
        ),
    }
    return KatoDarbouxSourcePoint(
        phase=phase,
        nu=nu,
        state=np.asarray(state, dtype=np.float64),
        true_wu_state=np.asarray(wu_state, dtype=np.float64),
        status=status,
        raw_chart_identical=False,
        diagnostics=diagnostics,
    )


def invert_kato_darboux_source_coordinates(
    state: Sequence[float],
    parameters: KatoSourceParameters | PoleParameters,
    *,
    source_radius: float = 0.01,
    graph_horizon: float = 8.0,
    phase_difference_step: float = 2.0e-5,
    graph_boundary_tolerance: float = 2.0e-10,
    energy_tolerance: float = 2.0e-11,
    rtol: float = 2.0e-11,
    atol: float = 2.0e-13,
    max_step: float = 0.03,
) -> KatoDarbouxSourceCoordinates:
    """Invert the numerical source section to common Kato ``(phi,nu)``.

    The unstable algebraic coordinate recovers ``phi`` through
    ``R_chi^{-1}``; the symplectic pairing with the finite-difference
    nonlinear-``W^u`` tangent recovers ``nu``.  The returned reconstruction
    defect checks, rather than assumes, membership in this numerical chart.
    """

    parameters = _as_kato_source_parameters(parameters)
    if energy_tolerance <= 0.0:
        raise ValueError("energy_tolerance must be positive")
    state_array = np.asarray(state, dtype=np.float64)
    if state_array.shape != (4,) or not np.all(np.isfinite(state_array)):
        raise ValueError("state must be a finite four-vector")
    frame = calibrated_source_frame(
        parameters.r, parameters.a2, parameters.epsilon
    )
    coordinates = frame.coordinates(state_array)
    rotated_unstable = frame.phase_rotation.T @ coordinates[:2]
    recovered_radius = float(np.linalg.norm(rotated_unstable))
    if recovered_radius <= 0.0:
        raise ValueError("state has zero unstable source radius")
    phase = float(
        np.arctan2(rotated_unstable[1], rotated_unstable[0])
        % (2.0 * np.pi)
    )
    (
        wu_state,
        _geometry_frame,
        phase_tangent,
        normal_direction,
        kernel_direction,
        geometry_diagnostics,
    ) = _kato_wu_section_geometry(
        parameters,
        phase,
        source_radius=source_radius,
        graph_horizon=graph_horizon,
        phase_difference_step=phase_difference_step,
        graph_boundary_tolerance=graph_boundary_tolerance,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    displacement = state_array - wu_state
    nu = float(
        phase_tangent @ CENTRAL_SYMPLECTIC_MATRIX @ displacement
    )
    stable_basis = np.column_stack((normal_direction, kernel_direction))
    stable_coefficients, _residuals, _rank, _singular = np.linalg.lstsq(
        stable_basis, displacement, rcond=None
    )
    correction = float(stable_coefficients[1])
    reconstructed = (
        wu_state + nu * normal_direction + correction * kernel_direction
    )
    reconstruction_defect = float(
        np.linalg.norm(reconstructed - state_array)
    )
    coefficient_nu_defect = float(stable_coefficients[0] - nu)
    energy_abs = abs(
        float(
            vdp_hamiltonian(
                state_array[:, None],
                parameters.r,
                parameters.a2,
                parameters.epsilon,
            )[0]
        )
    )
    radius_error = recovered_radius - source_radius
    gates_passed = bool(
        abs(radius_error) <= 2.0e-11
        and energy_abs <= energy_tolerance
        and reconstruction_defect <= 2.0e-10
        and abs(coefficient_nu_defect) <= 2.0e-10
        and geometry_diagnostics["canonical_orientation_pairing"] > 0.0
    )
    status = (
        KATO_DARBOUX_SECTION_STATUS
        if gates_passed
        else KATO_DARBOUX_INCONCLUSIVE_STATUS
    )
    return KatoDarbouxSourceCoordinates(
        phase=phase,
        nu=nu,
        energy_correction_coordinate=correction,
        source_radius=float(source_radius),
        reconstructed_state=np.asarray(reconstructed, dtype=np.float64),
        status=status,
        raw_chart_identical=False,
        diagnostics={
            **geometry_diagnostics,
            "status": status,
            "theorem_validation_status": THEOREM_VALIDATION_STATUS,
            "claim_bearing": False,
            "raw_chart_identical": False,
            "recovered_source_radius": recovered_radius,
            "source_radius_error": float(radius_error),
            "stable_plane_reconstruction_defect": reconstruction_defect,
            "stable_coefficient_nu_defect": coefficient_nu_defect,
            "central_energy_abs": energy_abs,
            "central_energy_tolerance": float(energy_tolerance),
            "inverse_gates_passed": gates_passed,
        },
    )


def _flow_central_state(
    state: Array,
    duration: float,
    *,
    r: float,
    a2: float,
    epsilon: float,
    rtol: float,
    atol: float,
    max_step: float,
) -> Array:
    return np.asarray(
        _integrate_central(
            state,
            (0.0, float(duration)),
            r=r,
            a2=a2,
            epsilon=epsilon,
            rtol=rtol,
            atol=atol,
            max_step=max_step,
        ).y[:, -1],
        dtype=np.float64,
    )


def compute_v2_source_candidate(
    parameters: PoleParameters,
    phase: float,
    *,
    source_radius: float = 0.01,
    flowback_tau: float = 2.0,
    graph_horizon: float = 10.0,
    comparison_horizon: float | None = None,
    graph_boundary_tolerance: float = 1.0e-8,
    rtol: float = 2.0e-11,
    atol: float = 2.0e-13,
    max_step: float = 0.03,
) -> V2SourceCandidate:
    """Compute the finite-horizon realization of V2 equations (27)--(28)."""

    if source_radius <= 0.0:
        raise ValueError("source_radius must be positive")
    if flowback_tau <= 0.0:
        raise ValueError("flowback_tau must be positive")
    phase = float(phase)
    core_coordinates = source_radius * np.array(
        [np.cos(phase), np.sin(phase)], dtype=np.float64
    )
    core_state, core_diagnostics = finite_horizon_unstable_graph_state(
        r=0.0,
        a2=0.0,
        epsilon=1.0,
        unstable_coordinates=core_coordinates,
        horizon=graph_horizon,
        boundary_tolerance=graph_boundary_tolerance,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    core_back = _flow_central_state(
        core_state,
        -flowback_tau,
        r=0.0,
        a2=0.0,
        epsilon=1.0,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    core_frame = calibrated_source_frame(0.0, 0.0, 1.0)
    b0 = core_frame.coordinates(core_back)[:2]
    local_graph_state, local_diagnostics = finite_horizon_unstable_graph_state(
        r=parameters.r,
        a2=parameters.a2,
        epsilon=parameters.epsilon,
        unstable_coordinates=b0,
        horizon=graph_horizon,
        boundary_tolerance=graph_boundary_tolerance,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    source_state = _flow_central_state(
        local_graph_state,
        flowback_tau,
        r=parameters.r,
        a2=parameters.a2,
        epsilon=parameters.epsilon,
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )

    horizon_defect: float | None = None
    if comparison_horizon is not None:
        comparison = compute_v2_source_candidate(
            parameters,
            phase,
            source_radius=source_radius,
            flowback_tau=flowback_tau,
            graph_horizon=float(comparison_horizon),
            comparison_horizon=None,
            graph_boundary_tolerance=graph_boundary_tolerance,
            rtol=rtol,
            atol=atol,
            max_step=max_step,
        )
        horizon_defect = float(np.linalg.norm(source_state - comparison.source_state))

    source_energy = float(
        vdp_hamiltonian(
            source_state[:, None],
            parameters.r,
            parameters.a2,
            parameters.epsilon,
        )[0]
    )
    core_anchor_defect: float | None = None
    if (
        abs(((phase - CORE_HOMOCLINIC_PHASE + np.pi) % (2.0 * np.pi)) - np.pi)
        < 1.0e-8
    ):
        core_anchor_defect = float(np.linalg.norm(core_state - CORE_SOURCE_STATE))
    diagnostics: dict[str, float | str | bool] = {
        "status": "COMPUTED/E1_V2_MOVING_SOURCE_CANDIDATE",
        "theorem_validation_status": THEOREM_VALIDATION_STATUS,
        "core_graph_boundary_residual_inf": float(
            core_diagnostics["boundary_residual_inf"]
        ),
        "positive_graph_boundary_residual_inf": float(
            local_diagnostics["boundary_residual_inf"]
        ),
        "graph_boundary_residual_tolerance": float(graph_boundary_tolerance),
        "graph_boundary_residuals_passed": bool(
            core_diagnostics["boundary_residual_passed"]
            and local_diagnostics["boundary_residual_passed"]
        ),
        "core_graph_energy_abs": float(core_diagnostics["central_energy_abs"]),
        "positive_graph_energy_abs": float(
            local_diagnostics["central_energy_abs"]
        ),
        "source_central_energy_abs": abs(source_energy),
        "horizon_source_defect": (
            horizon_defect if horizon_defect is not None else "NOT_COMPUTED"
        ),
        "core_anchor_defect": (
            core_anchor_defect if core_anchor_defect is not None else "NOT_APPLICABLE"
        ),
        "b0_norm": float(np.linalg.norm(b0)),
        "scope_note": (
            "Numerical realization of V2 (27)--(28) in a phase-calibrated "
            "finite-horizon graph; general-parameter Kato transport and interval "
            "validation remain unresolved."
        ),
    }
    return V2SourceCandidate(
        parameters=parameters,
        phase=phase,
        source_radius=float(source_radius),
        flowback_tau=float(flowback_tau),
        graph_horizon=float(graph_horizon),
        core_state=core_state,
        b0=np.asarray(b0, dtype=np.float64),
        local_graph_state=local_graph_state,
        source_state=source_state,
        diagnostics=diagnostics,
    )


def _gate_cone(central_state: Array, parameters: PoleParameters) -> dict[str, float]:
    u, p, v, q = (float(value) for value in central_state)
    x = -u
    y = -p
    z = -v
    zeta = -q
    d_value = 0.5 * x * x - z
    k_value = x * y - zeta
    sqrt_epsilon = float(np.sqrt(parameters.epsilon))
    coefficient_b = 1.0 + sqrt_epsilon * parameters.r**3 * parameters.a2
    coefficient_c = (
        2.0 * parameters.r * parameters.a2
        + sqrt_epsilon * parameters.r**4 * parameters.a2**2
    )
    coefficient_small_b = sqrt_epsilon * parameters.r**2 / 3.0
    y_prime = (
        d_value
        + (coefficient_b - 0.5) * x * x
        + coefficient_c * x
        + coefficient_small_b * x**3
    )
    k_prime = y * y + x * y_prime - x
    return {
        "x": x,
        "y": y,
        "z": z,
        "zeta": zeta,
        "D": d_value,
        "K": k_value,
        "x_prime": y,
        "y_prime": y_prime,
        "D_prime": k_value,
        "K_prime": k_prime,
    }


def _physical_gate_event(
    parameters: PoleParameters, gate_section_x: float = 10.0
) -> Any:
    if gate_section_x <= 0.0:
        raise ValueError("gate_section_x must be positive")
    threshold = (
        parameters.a
        + gate_section_x * np.sqrt(parameters.epsilon) * parameters.r**2
    )

    def event(_time: float, state: Array) -> float:
        return float(state[0] - threshold)

    event.direction = 1
    event.terminal = True
    return event


def _integrate_source_to_gate(
    source: V2SourceCandidate,
    *,
    gate_section_x: float = 10.0,
    maximum_x: float = 2.0,
    rtol: float = 2.0e-11,
    atol: float = 2.0e-13,
    max_step: float = 0.0016,
) -> PoleGateHit:
    parameters = source.parameters
    bridge = BridgeParameters(
        r=parameters.r, a2=parameters.a2, epsilon=parameters.epsilon
    )
    physical_source = central_to_physical(source.source_state, bridge)
    gate_event = _physical_gate_event(parameters, gate_section_x)
    integration = solve_ivp(
        lambda time, state: physical_field(time, state, parameters),
        (0.0, maximum_x),
        physical_source,
        method="DOP853",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
        events=gate_event,
        dense_output=True,
    )
    if not integration.success:
        raise RuntimeError(integration.message)
    if integration.t_events[0].size != 1:
        raise RuntimeError("source candidate did not have a unique recorded pole-gate hit")
    hit_x = float(integration.t_events[0][0])
    physical_hit = np.asarray(integration.y_events[0][0], dtype=np.float64)
    central_hit = physical_to_central(physical_hit, bridge)
    cone = _gate_cone(central_hit, parameters)
    target_energy = -parameters.epsilon * float(cubic_potential(parameters.a))
    energy = np.asarray(
        physical_hamiltonian(integration.y, parameters), dtype=np.float64
    )
    threshold = (
        parameters.a
        + gate_section_x * np.sqrt(parameters.epsilon) * parameters.r**2
    )
    pre_gate_values = integration.y[0, :-1] - threshold
    return PoleGateHit(
        phase=source.phase,
        physical_time=hit_x,
        central_time=hit_x * parameters.epsilon**0.25 / parameters.r,
        central_state=np.asarray(central_hit, dtype=np.float64),
        physical_state=physical_hit,
        cone=cone,
        diagnostics={
            "status": "COMPUTED/E1_PHYSICAL_FIRST_POLE_GATE_HIT",
            "solver_success": bool(integration.success),
            "gate_section_x": float(gate_section_x),
            "gate_residual": abs(cone["x"] - gate_section_x),
            "pre_gate_maximum_g": (
                float(np.max(pre_gate_values)) if pre_gate_values.size else float("nan")
            ),
            "source_to_gate_energy_drift": float(np.ptp(energy)),
            "gate_energy_defect": float(
                physical_hamiltonian(physical_hit, parameters) - target_energy
            ),
            "event_speed_physical": float(
                physical_field(hit_x, physical_hit, parameters)[0]
            ),
            "event_semantics": (
                f"First physical-ODE hit of the x=-U={gate_section_x:g} section from the "
                "finite-horizon V2 source candidate."
            ),
        },
    )


def _end_label_ladders(
    parameters: PoleParameters,
    hit_x: Array,
    hit_state: Array,
    level_u: Array,
    *,
    fit_indices: Array,
    iterations: int = 3,
) -> tuple[float, Array, Array, Array, Array, Array]:
    delta = parameters.delta
    ell = parameters.ell
    epsilon = parameters.epsilon
    x2 = 1.0 / (6.0 * delta**2)
    leading_sigma = ell / level_u
    blowup_ladder = hit_x + leading_sigma + x2 * leading_sigma**3
    blowup_x = float(blowup_ladder[-1])
    z0_ladder = np.zeros_like(level_u)
    w0_ladder = np.zeros_like(level_u)
    compact = np.zeros((4, level_u.size), dtype=np.float64)

    for _ in range(iterations):
        sigma = blowup_x - hit_x
        if np.any(sigma <= 0.0):
            raise RuntimeError("pole-time estimate does not lie beyond every level hit")
        compact = physical_to_compact(sigma, hit_state, parameters)
        _x_value, _y_value, w_value, z_value = compact
        z0_ladder = np.asarray(z_value, dtype=np.float64).copy()
        w0_ladder = np.asarray(w_value, dtype=np.float64).copy()
        for _coefficient_iteration in range(5):
            x3_ladder = z0_ladder / (4.0 * ell * delta**2)
            w0_ladder = (
                w_value
                - parameters.a * epsilon * sigma
                + 0.5 * ell * epsilon * x2 * sigma**2
                + ell * epsilon * x3_ladder * sigma**3 / 3.0
            )
            z0_ladder = (
                z_value
                + (w0_ladder + ell * epsilon) * sigma
                + 0.5 * parameters.a * epsilon * sigma**2
                - ell * epsilon * x2 * sigma**3 / 6.0
                - ell * epsilon * x3_ladder * sigma**4 / 12.0
            )
        z0 = float(np.median(z0_ladder[fit_indices]))
        x3 = z0 / (4.0 * ell * delta**2)
        blowup_ladder = (
            hit_x
            + leading_sigma
            + x2 * leading_sigma**3
            + x3 * leading_sigma**4
        )
        blowup_x = float(blowup_ladder[-1])

    sigma = blowup_x - hit_x
    compact = physical_to_compact(sigma, hit_state, parameters)
    _x_value, _y_value, w_value, z_value = compact
    z0_ladder = np.asarray(z_value, dtype=np.float64).copy()
    w0_ladder = np.asarray(w_value, dtype=np.float64).copy()
    for _coefficient_iteration in range(6):
        x3_ladder = z0_ladder / (4.0 * ell * delta**2)
        w0_ladder = (
            w_value
            - parameters.a * epsilon * sigma
            + 0.5 * ell * epsilon * x2 * sigma**2
            + ell * epsilon * x3_ladder * sigma**3 / 3.0
        )
        z0_ladder = (
            z_value
            + (w0_ladder + ell * epsilon) * sigma
            + 0.5 * parameters.a * epsilon * sigma**2
            - ell * epsilon * x2 * sigma**3 / 6.0
            - ell * epsilon * x3_ladder * sigma**4 / 12.0
        )
    return blowup_x, blowup_ladder, sigma, compact, z0_ladder, w0_ladder


def physical_action_density(
    state: Array, parameters: PoleParameters
) -> Array:
    """Evaluate the exact V3 physical action density (45).

    For the physical state order ``(u,p,v,q)``, the primitive
    ``epsilon*p*du-delta**(-1)*q*dv`` gives

    ``lambda_delta(partial_x)=(epsilon*p**2-q**2)/delta``.
    """

    physical = np.asarray(state, dtype=np.float64)
    if physical.shape[0] != 4:
        raise ValueError("state must have leading dimension four")
    p = physical[1]
    q = physical[3]
    return np.asarray(
        (parameters.epsilon * p**2 - q**2) / parameters.delta,
        dtype=np.float64,
    )


def _augmented_physical_field(
    physical_x: float, state_and_action: Array, parameters: PoleParameters
) -> Array:
    physical = np.asarray(state_and_action[:4], dtype=np.float64)
    return np.r_[
        physical_field(physical_x, physical, parameters),
        float(physical_action_density(physical, parameters)),
    ]


def _same_orbit_action_ladder(
    integration: Any,
    *,
    parameters: PoleParameters,
    labels: PoleLabels,
    blowup_x: float,
    gate_x: float,
    cutoff_sigmas: Sequence[float],
) -> SameOrbitActionLadder:
    cutoffs = np.asarray(tuple(float(value) for value in cutoff_sigmas))
    if cutoffs.ndim != 1 or cutoffs.size < 3:
        raise ValueError("action cutoff ladder must contain at least three values")
    cutoffs = np.sort(np.unique(cutoffs))[::-1]
    if np.any(cutoffs <= 0.0):
        raise ValueError("action cutoff sigmas must be positive")
    endpoint_x = blowup_x - cutoffs
    if endpoint_x[0] <= integration.t[0] or endpoint_x[-1] > integration.t[-1]:
        raise ValueError("action cutoff ladder lies outside the connected physical IVP")
    augmented = np.asarray(integration.sol(endpoint_x), dtype=np.float64)
    physical = augmented[:4]
    raw = augmented[4]
    divergence = divergent_action(cutoffs, parameters, labels.z0)
    subtracted = raw - divergence
    density = physical_action_density(physical, parameters)
    compact = physical_to_compact(cutoffs, physical, parameters)
    compact_density = action_density(cutoffs, compact, parameters)
    density_scale = np.maximum(1.0, np.abs(density))

    endpoint_sigma = float(cutoffs[-1])
    endpoint_action = float(raw[-1])
    gate_action = float(np.asarray(integration.sol(gate_x))[4])
    endpoint_divergence = float(divergence[-1])
    finite_part_source = endpoint_action - endpoint_divergence
    finite_part_gate = endpoint_action - gate_action - endpoint_divergence
    moving_cut_residual = finite_part_source - (gate_action + finite_part_gate)
    last_slice = slice(max(0, cutoffs.size - 3), cutoffs.size)
    return SameOrbitActionLadder(
        source_cut_x=0.0,
        sigma=cutoffs,
        endpoint_x=endpoint_x,
        raw_action=np.asarray(raw, dtype=np.float64),
        divergent_part=np.asarray(divergence, dtype=np.float64),
        subtracted_action=np.asarray(subtracted, dtype=np.float64),
        density=np.asarray(density, dtype=np.float64),
        diagnostics={
            "status": "COMPUTED/E1_SAME_ORBIT_ACTION_FINITE_PART",
            "theorem_validation_status": THEOREM_VALIDATION_STATUS,
            "action_definition": (
                "Integral from the numerical V2 source cut of "
                "(epsilon*p^2-q^2)/delta in physical x."
            ),
            "minimum_cutoff_sigma": endpoint_sigma,
            "last_three_subtracted_spread": float(
                np.ptp(subtracted[last_slice])
            ),
            "last_subtracted_value": float(subtracted[-1]),
            "moving_cut_at_gate_residual": float(moving_cut_residual),
            "source_to_gate_action": gate_action,
            "physical_compact_density_relative_defect_inf": float(
                np.max(np.abs(density - compact_density) / density_scale)
            ),
            "scope_note": (
                "Raw action and Laurent-log subtraction on the same floating-"
                "point source-to-pole IVP; no improper-limit or interval claim."
            ),
        },
    )


def compute_source_to_pole_connection(
    parameters: PoleParameters,
    phase: float = 0.0,
    *,
    source_radius: float = 0.01,
    flowback_tau: float = 2.0,
    graph_horizon: float = 10.0,
    comparison_horizon: float | None = 8.0,
    graph_boundary_tolerance: float = 1.0e-8,
    gate_section_x: float = 10.0,
    level_u: Sequence[float] = (20.0, 50.0, 100.0, 200.0, 500.0),
    label_fit_levels: Sequence[float] | None = None,
    maximum_x: float = 2.0,
    local_sigma_min: float = 5.0e-4,
    local_sigma_cut: float = 3.0e-3,
    local_points: int = 240,
    action_cutoff_sigmas: Sequence[float] = (
        2.55e-3,
        1.2e-3,
        5.5e-4,
        3.0e-4,
        1.6e-4,
        8.0e-5,
        5.0e-5,
    ),
    rtol: float = 2.0e-11,
    atol: float = 2.0e-13,
    max_step_x: float = 0.0016,
    max_step_xi: float = 0.03,
) -> SourceToPoleConnection:
    """Compute one physical V2-source-to-local-V3-pole candidate."""

    levels = np.asarray(level_u, dtype=np.float64)
    if levels.ndim != 1 or levels.size < 3 or np.any(np.diff(levels) <= 0.0):
        raise ValueError("level_u must contain at least three increasing values")
    requested_fit_levels = (
        levels[-3:]
        if label_fit_levels is None
        else np.asarray(label_fit_levels, dtype=np.float64)
    )
    if (
        requested_fit_levels.ndim != 1
        or requested_fit_levels.size < 3
        or np.unique(requested_fit_levels).size != requested_fit_levels.size
    ):
        raise ValueError("label_fit_levels must contain at least three unique levels")
    fit_indices_list: list[int] = []
    for fit_level in requested_fit_levels:
        matches = np.flatnonzero(np.isclose(levels, fit_level, rtol=0.0, atol=1.0e-12))
        if matches.size != 1:
            raise ValueError("every label_fit_level must occur in level_u exactly once")
        fit_indices_list.append(int(matches[0]))
    fit_indices = np.asarray(fit_indices_list, dtype=int)
    source = compute_v2_source_candidate(
        parameters,
        phase,
        source_radius=source_radius,
        flowback_tau=flowback_tau,
        graph_horizon=graph_horizon,
        comparison_horizon=comparison_horizon,
        graph_boundary_tolerance=graph_boundary_tolerance,
        rtol=rtol,
        atol=atol,
        max_step=max_step_xi,
    )
    bridge = BridgeParameters(
        r=parameters.r, a2=parameters.a2, epsilon=parameters.epsilon
    )
    physical_source = central_to_physical(source.source_state, bridge)
    gate_event = _physical_gate_event(parameters, gate_section_x)
    gate_event.terminal = False
    events: list[Any] = [gate_event]
    for index, level in enumerate(levels):

        def level_event(
            _time: float, state: Array, level: float = float(level)
        ) -> float:
            return float(state[0] - level)

        level_event.direction = 1
        level_event.terminal = index == levels.size - 1
        events.append(level_event)

    integration = solve_ivp(
        lambda time, state: _augmented_physical_field(time, state, parameters),
        (0.0, maximum_x),
        np.r_[physical_source, 0.0],
        method="DOP853",
        rtol=rtol,
        atol=atol,
        max_step=max_step_x,
        events=events,
        dense_output=True,
    )
    if not integration.success:
        raise RuntimeError(integration.message)
    if integration.t_events[0].size != 1:
        raise RuntimeError("physical source orbit did not have one pole-gate hit")
    if any(times.size != 1 for times in integration.t_events[1:]):
        raise RuntimeError("physical source orbit did not hit every requested u level")

    gate_x = float(integration.t_events[0][0])
    gate_physical = np.asarray(integration.y_events[0][0][:4], dtype=np.float64)
    gate_central = physical_to_central(gate_physical, bridge)
    cone = _gate_cone(gate_central, parameters)
    target_energy = -parameters.epsilon * float(cubic_potential(parameters.a))
    pre_gate = integration.t <= gate_x + 1.0e-14
    pre_gate_energy = np.asarray(
        physical_hamiltonian(integration.y[:4, pre_gate], parameters),
        dtype=np.float64,
    )
    gate = PoleGateHit(
        phase=source.phase,
        physical_time=gate_x,
        central_time=gate_x * parameters.epsilon**0.25 / parameters.r,
        central_state=np.asarray(gate_central, dtype=np.float64),
        physical_state=gate_physical,
        cone=cone,
        diagnostics={
            "status": "COMPUTED/E1_PHYSICAL_FIRST_POLE_GATE_HIT",
            "solver_success": bool(integration.success),
            "gate_section_x": float(gate_section_x),
            "gate_residual": abs(cone["x"] - gate_section_x),
            "source_to_gate_energy_drift": float(np.ptp(pre_gate_energy)),
            "gate_energy_defect": float(
                physical_hamiltonian(gate_physical, parameters) - target_energy
            ),
            "event_speed_physical": float(
                physical_field(gate_x, gate_physical, parameters)[0]
            ),
            "event_semantics": (
                f"First hit of x=-U={gate_section_x:g} on the same physical "
                "source-to-pole IVP."
            ),
        },
    )
    hit_x = np.asarray(
        [times[0] for times in integration.t_events[1:]], dtype=np.float64
    )
    hit_state = np.stack(
        [states[0][:4] for states in integration.y_events[1:]], axis=1
    )
    (
        blowup_x,
        blowup_ladder,
        sigma,
        compact,
        z0_ladder,
        w0_ladder,
    ) = _end_label_ladders(
        parameters,
        hit_x,
        hit_state,
        levels,
        fit_indices=fit_indices,
    )
    z0 = float(np.median(z0_ladder[fit_indices]))
    w0 = float(np.median(w0_ladder[fit_indices]))
    kappa = fixed_source_energy_kappa(parameters, z0, w0)
    labels = PoleLabels(z0=z0, w0=w0, kappa=kappa)
    pole_time_spread = float(np.ptp(blowup_ladder[fit_indices]))
    z0_spread = float(np.ptp(z0_ladder[fit_indices]))
    w0_spread = float(np.ptp(w0_ladder[fit_indices]))
    end_fit = PoleEndFit(
        level_u=levels,
        hit_x=hit_x,
        hit_state=hit_state,
        remaining_sigma=sigma,
        compact_state=compact,
        blowup_estimate_ladder=blowup_ladder,
        z0_ladder=z0_ladder,
        w0_ladder=w0_ladder,
        labels=labels,
        diagnostics={
            "status": "COMPUTED/E1_POLE_TIME_AND_END_LABEL_FIT",
            "blowup_position_x": blowup_x,
            "remaining_distance_at_gate": blowup_x - gate_x,
            "pole_time_last_three_spread": pole_time_spread,
            "z0_last_three_spread": z0_spread,
            "w0_last_three_spread": w0_spread,
            "label_fit_levels": requested_fit_levels.tolist(),
            "minimum_X": float(np.min(compact[0])),
            "maximum_abs_X_minus_one": float(np.max(np.abs(compact[0] - 1.0))),
            "maximum_abs_Y_minus_one": float(np.max(np.abs(compact[1] - 1.0))),
            "label_energy_defect": float(
                pole_energy_from_labels(parameters, labels) - target_energy
            ),
            "kappa_extraction_note": (
                "kappa is imposed by the exact fixed-source energy identity; "
                "direct sigma^-4 subtraction is intentionally not used."
            ),
        },
    )
    action_ladder = _same_orbit_action_ladder(
        integration,
        parameters=parameters,
        labels=labels,
        blowup_x=blowup_x,
        gate_x=gate_x,
        cutoff_sigmas=action_cutoff_sigmas,
    )

    local = realize_local_pole(
        parameters,
        labels,
        sigma_min=local_sigma_min,
        sigma_cut=local_sigma_cut,
        points=local_points,
        rtol=rtol,
        atol=atol,
        physical_crosscheck=True,
    )
    comparison_x = blowup_x - local.sigma
    if np.min(comparison_x) < integration.t[0] or np.max(comparison_x) > integration.t[-1]:
        raise RuntimeError("local pole overlap lies outside the physical source orbit")
    global_physical = np.asarray(
        integration.sol(comparison_x)[:4], dtype=np.float64
    )
    global_compact = physical_to_compact(local.sigma, global_physical, parameters)
    physical_scale = np.maximum(1.0, np.abs(global_physical))
    physical_relative_defect = float(
        np.max(np.abs(global_physical - local.physical) / physical_scale)
    )
    compact_scale = np.maximum(1.0, np.abs(global_compact))
    compact_relative_defect = float(
        np.max(np.abs(global_compact - local.compact) / compact_scale)
    )
    diagnostics: dict[str, float | str | bool] = {
        "status": SOURCE_TO_POLE_CANDIDATE_STATUS,
        "theorem_validation_status": THEOREM_VALIDATION_STATUS,
        "same_physical_ivp_source_to_last_level": True,
        "solver_success": bool(integration.success),
        "global_local_physical_relative_defect_inf": physical_relative_defect,
        "global_local_compact_relative_defect_inf": compact_relative_defect,
        "scope_note": (
            "A complete floating-point candidate from a finite-horizon W^u "
            "source to the local pole chart; not a certified parameter box, "
            "uniform source window, or interval basin-entry proof."
        ),
    }
    return SourceToPoleConnection(
        source=source,
        gate=gate,
        end_fit=end_fit,
        action_ladder=action_ladder,
        local_realization=local,
        physical_x=np.asarray(integration.t, dtype=np.float64),
        physical_state=np.asarray(integration.y[:4], dtype=np.float64),
        physical_action=np.asarray(integration.y[4], dtype=np.float64),
        global_on_local_sigma=global_physical,
        global_compact_on_local_sigma=global_compact,
        diagnostics=diagnostics,
        dense_physical_solution=integration.sol,
    )


def same_orbit_moving_cut_balance(
    connection: SourceToPoleConnection,
    *,
    earlier_cut_x: float,
    later_cut_x: float,
    endpoint_sigma: float,
) -> dict[str, float | str]:
    """Check V3 equation (50) using the connected IVP action coordinate.

    The two finite-part candidates use the same terminal point and the same
    Laurent--log subtraction.  The finite segment between cuts is read from
    the action component integrated together with the physical state.
    """

    blowup_x = float(connection.end_fit.diagnostics["blowup_position_x"])
    endpoint_x = blowup_x - float(endpoint_sigma)
    if not (
        connection.physical_x[0]
        <= earlier_cut_x
        < later_cut_x
        < endpoint_x
        <= connection.physical_x[-1]
    ):
        raise ValueError(
            "require source <= earlier_cut_x < later_cut_x < endpoint_x"
        )
    values = np.asarray(
        connection.dense_physical_solution(
            np.array([earlier_cut_x, later_cut_x, endpoint_x])
        ),
        dtype=np.float64,
    )[4]
    action_earlier, action_later, action_endpoint = (
        float(value) for value in values
    )
    subtraction = float(
        divergent_action(
            endpoint_sigma,
            connection.source.parameters,
            connection.end_fit.labels.z0,
        )
    )
    finite_part_earlier = action_endpoint - action_earlier - subtraction
    finite_part_later = action_endpoint - action_later - subtraction
    finite_segment = action_later - action_earlier
    residual = finite_part_earlier - (finite_segment + finite_part_later)
    return {
        "status": "COMPUTED/QA_SAME_ORBIT_MOVING_CUT",
        "finite_part_earlier_cut": finite_part_earlier,
        "finite_part_later_cut": finite_part_later,
        "finite_segment_action": finite_segment,
        "moving_cut_additivity_residual": residual,
        "endpoint_sigma": float(endpoint_sigma),
    }


def compute_pole_window_candidate(
    parameters: PoleParameters,
    phases: Iterable[float] = (-0.2, -0.1, 0.0, 0.1, 0.2),
    *,
    source_radius: float = 0.01,
    flowback_tau: float = 2.0,
    graph_horizon: float = 10.0,
    graph_boundary_tolerance: float = 1.0e-8,
    gate_section_x: float = 10.0,
    maximum_x: float = 2.0,
    rtol: float = 2.0e-11,
    atol: float = 2.0e-13,
    max_step_x: float = 0.0016,
    max_step_xi: float = 0.03,
) -> PoleWindowCandidate:
    """Sample the whole closed V3 phase window with true-graph candidates."""

    phase_values = np.asarray(tuple(float(value) for value in phases), dtype=np.float64)
    if phase_values.ndim != 1 or phase_values.size == 0:
        raise ValueError("phases must be nonempty")
    sources: list[V2SourceCandidate] = []
    gates: list[PoleGateHit] = []
    for phase in phase_values:
        source = compute_v2_source_candidate(
            parameters,
            float(phase),
            source_radius=source_radius,
            flowback_tau=flowback_tau,
            graph_horizon=graph_horizon,
            comparison_horizon=None,
            graph_boundary_tolerance=graph_boundary_tolerance,
            rtol=rtol,
            atol=atol,
            max_step=max_step_xi,
        )
        gate = _integrate_source_to_gate(
            source,
            gate_section_x=gate_section_x,
            maximum_x=maximum_x,
            rtol=rtol,
            atol=atol,
            max_step=max_step_x,
        )
        sources.append(source)
        gates.append(gate)
    cone_y = np.array([gate.cone["y"] for gate in gates])
    cone_d = np.array([gate.cone["D"] for gate in gates])
    cone_k = np.array([gate.cone["K"] for gate in gates])
    cone_y_prime = np.array([gate.cone["y_prime"] for gate in gates])
    cone_k_prime = np.array([gate.cone["K_prime"] for gate in gates])
    return PoleWindowCandidate(
        parameters=parameters,
        phases=phase_values,
        source_states=np.stack([source.source_state for source in sources]),
        gate_times_x=np.array([gate.physical_time for gate in gates]),
        gate_times_xi=np.array([gate.central_time for gate in gates]),
        gate_states=np.stack([gate.central_state for gate in gates]),
        cone_y=cone_y,
        cone_d=cone_d,
        cone_k=cone_k,
        cone_y_prime=cone_y_prime,
        cone_k_prime=cone_k_prime,
        diagnostics={
            "status": WINDOW_CANDIDATE_STATUS,
            "theorem_validation_status": THEOREM_VALIDATION_STATUS,
            "sample_count": float(phase_values.size),
            "minimum_y": float(np.min(cone_y)),
            "minimum_D": float(np.min(cone_d)),
            "minimum_K": float(np.min(cone_k)),
            "minimum_y_prime": float(np.min(cone_y_prime)),
            "minimum_K_prime": float(np.min(cone_k_prime)),
            "maximum_gate_residual": float(
                max(float(gate.diagnostics["gate_residual"]) for gate in gates)
            ),
            "maximum_source_energy_abs": float(
                max(
                    float(source.diagnostics["source_central_energy_abs"])
                    for source in sources
                )
            ),
            "scope_note": (
                "Finite phase samples on the V3 closed arc; not an exhaustive "
                "interval proof over phase or the existential parameter box."
            ),
        },
    )


__all__ = [
    "CENTRAL_SYMPLECTIC_MATRIX",
    "CORE_HOMOCLINIC_PHASE",
    "KATO_DARBOUX_INCONCLUSIVE_STATUS",
    "KATO_DARBOUX_SECTION_STATUS",
    "KatoDarbouxSourceCoordinates",
    "KatoDarbouxSourcePoint",
    "KatoSourceParameters",
    "PoleEndFit",
    "PoleGateHit",
    "PoleWindowCandidate",
    "SameOrbitActionLadder",
    "SOURCE_TO_POLE_CANDIDATE_STATUS",
    "SourceFrame",
    "SourceToPoleConnection",
    "THEOREM_VALIDATION_STATUS",
    "V2SourceCandidate",
    "WINDOW_CANDIDATE_STATUS",
    "calibrated_source_frame",
    "compute_pole_window_candidate",
    "compute_source_to_pole_connection",
    "compute_kato_darboux_source_point",
    "compute_v2_source_candidate",
    "finite_horizon_unstable_graph_state",
    "invert_kato_darboux_source_coordinates",
    "physical_action_density",
    "same_orbit_moving_cut_balance",
]
