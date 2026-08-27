"""Complete floating-point return-branch records for the van der Pol model.

The first-event atlas in :mod:`numerics.vdp_return_coding` is an exploratory
endpoint sampler.  This module has a narrower purpose: it follows one selected
source state from the numerical outgoing face

``rho_u = ||(x_u,y_u)|| = source_radius``

through the global excursion, the incoming face ``rho_s = source_radius``,
and the local saddle passage back to the *same* outgoing face.  Physical
length and action are integrated as augmented ODE variables, so the two stored
segments form one composable finite branch rather than disconnected endpoint
data.

All coordinates and signs here belong to the deterministic linear reversible
eigenframe.  In particular, ``positive`` and ``negative`` below mean the sign
of ``numerical_transverse_coordinate_not_exact_action``.  They are candidate
labels, not the exact V2 action signs or V6 winding labels.  The computation is
ordinary floating point ``COMPUTED/E1`` and is not Issue #7 interval evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Any, Mapping

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp, trapezoid

from numerics.rfsn_numerics import (
    vdp_field_point,
    vdp_hamiltonian,
)
from numerics.vdp_return_coding import (
    SaddleFrame,
    numerical_source_coordinates,
    reversible_saddle_frame,
)


Array = NDArray[np.float64]

EVIDENCE_STATUS = "COMPUTED/E1_NONRIGOROUS_COMPLETE_RETURN_CANDIDATE"
COORDINATE_STATUS = "numerical_linear_reversible_eigenframe_not_exact_V2_chart"
WINDING_STATUS = "PROXY_ONLY_UNCALIBRATED_NO_INTEGER_V6_LABEL"


@dataclass(frozen=True)
class CompleteBranchSegment:
    """One contiguous piece of a sampled physical return branch.

    The two observable arrays are cumulative from the source of the *whole*
    branch.  Their endpoint differences give the contribution of this segment.
    """

    name: str
    start_face: str
    end_face: str
    xi: Array
    central_state: Array
    cumulative_physical_length: Array
    cumulative_physical_action: Array

    @property
    def xi_duration(self) -> float:
        return float(self.xi[-1] - self.xi[0])

    @property
    def physical_length(self) -> float:
        return float(
            self.cumulative_physical_length[-1]
            - self.cumulative_physical_length[0]
        )

    @property
    def physical_action(self) -> float:
        return float(
            self.cumulative_physical_action[-1]
            - self.cumulative_physical_action[0]
        )

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "start_face": self.start_face,
            "end_face": self.end_face,
            "xi_start": float(self.xi[0]),
            "xi_end": float(self.xi[-1]),
            "xi_duration": self.xi_duration,
            "physical_length": self.physical_length,
            "physical_action": self.physical_action,
            "start_state": self.central_state[:, 0].tolist(),
            "end_state": self.central_state[:, -1].tolist(),
        }


@dataclass(frozen=True)
class CompleteReturnBranch:
    """A two-segment source-to-source return candidate."""

    branch_id: str
    r: float
    a2: float
    epsilon: float
    source_radius: float
    local_return_radius: float
    source_state: Array
    incoming_state: Array
    target_state: Array
    source_coordinates: Mapping[str, Any]
    target_coordinates: Mapping[str, Any]
    source_sign_proxy: str
    target_sign_proxy: str
    incoming_time_xi: float
    return_time_xi: float
    segments: tuple[CompleteBranchSegment, CompleteBranchSegment]
    diagnostics: Mapping[str, Any]
    provenance: Mapping[str, Any]

    @property
    def physical_length(self) -> float:
        return float(sum(segment.physical_length for segment in self.segments))

    @property
    def physical_action(self) -> float:
        return float(sum(segment.physical_action for segment in self.segments))

    @property
    def local_residence_turns_proxy(self) -> float:
        return float(self.diagnostics["local_residence_turns_proxy"])

    def as_candidate_record(self) -> dict[str, Any]:
        """Return a JSON-ready non-rigorous branch summary.

        Dense arrays are deliberately kept out of this record; use
        :meth:`as_npz_payload` for replayable sampled trajectories.
        """

        def parameter(value: float) -> dict[str, str]:
            return {"decimal": repr(float(value)), "binary64_hex": float(value).hex()}

        source_linear = np.asarray(
            self.source_coordinates["linear_coordinates"], dtype=float
        )
        target_linear = np.asarray(
            self.target_coordinates["linear_coordinates"], dtype=float
        )
        return {
            "schema_version": "rfsn-vdp-sampled-branch/1",
            "branch_id": self.branch_id,
            "model": "van_der_pol_stationary_central_ode",
            "branch_type": "finite_return",
            "evidence_status": EVIDENCE_STATUS,
            "claim_bearing": False,
            "parameters": {
                "r": parameter(self.r),
                "a2": parameter(self.a2),
                "epsilon": parameter(self.epsilon),
            },
            "chart": {
                "coordinate_status": COORDINATE_STATUS,
                "source_face": "unstable_radius_equals_source_radius",
                "incoming_face": "stable_radius_equals_source_radius",
                "source_radius": self.source_radius,
                "local_return_radius": self.local_return_radius,
                "phase_name": "numerical_canonical_eigenplane_phase",
                "transverse_name": (
                    "numerical_transverse_coordinate_not_exact_action"
                ),
            },
            "source": {
                "state": self.source_state.tolist(),
                "linear_coordinates": source_linear.tolist(),
                "phase": float(self.source_coordinates["phase"]),
                "transverse_coordinate_proxy": float(
                    self.source_coordinates["transverse_coordinate"]
                ),
                "sign_proxy": self.source_sign_proxy,
                "unstable_radius": float(self.source_coordinates["radius"]),
                "stable_radius": float(np.linalg.norm(source_linear[2:])),
            },
            "target": {
                "state": self.target_state.tolist(),
                "linear_coordinates": target_linear.tolist(),
                "phase": float(self.target_coordinates["phase"]),
                "transverse_coordinate_proxy": float(
                    self.target_coordinates["transverse_coordinate"]
                ),
                "sign_proxy": self.target_sign_proxy,
                "unstable_radius": float(self.target_coordinates["radius"]),
                "stable_radius": float(np.linalg.norm(target_linear[2:])),
            },
            "event": {
                "physical_event": "return",
                "target_sign_semantics": (
                    "sign of target numerical transverse coordinate; not the "
                    "sign of the first unstable eigen-coordinate"
                ),
                "incoming_time_xi": self.incoming_time_xi,
                "return_time_xi": self.return_time_xi,
                "local_residence_turns_proxy": self.local_residence_turns_proxy,
                "winding_status": WINDING_STATUS,
            },
            "segments": [segment.summary() for segment in self.segments],
            "observables": {
                "physical_length": self.physical_length,
                "physical_action": self.physical_action,
                "length_counterterm": 0.0,
                "action_counterterm": 0.0,
                "normalization": "ordinary finite return branch",
            },
            "diagnostics": dict(self.diagnostics),
            "provenance": dict(self.provenance),
            "nonclaims": [
                "This is a floating-point candidate, not outward-rounded validation.",
                "The transverse signs are not the exact V2 action signs.",
                "No integer V6 winding label or exhaustive return cell is certified.",
                "A single return trajectory does not validate a V6 cross form.",
            ],
        }

    def as_npz_payload(self) -> dict[str, Array]:
        """Return dense numeric arrays without object dtype."""

        payload: dict[str, Array] = {}
        for index, segment in enumerate(self.segments):
            prefix = f"segment_{index}_{segment.name}"
            payload[f"{prefix}_xi"] = segment.xi
            payload[f"{prefix}_central_state"] = segment.central_state
            payload[f"{prefix}_physical_length"] = (
                segment.cumulative_physical_length
            )
            payload[f"{prefix}_physical_action"] = (
                segment.cumulative_physical_action
            )
        payload["source_state"] = self.source_state
        payload["incoming_state"] = self.incoming_state
        payload["target_state"] = self.target_state
        return payload


def _transverse_sign(value: float, uncertain_margin: float) -> str:
    if value > uncertain_margin:
        return "positive"
    if value < -uncertain_margin:
        return "negative"
    return "cut_band"


def _radial_speed(frame: SaddleFrame, state: Array, *, unstable: bool,
                  r: float, a2: float, epsilon: float) -> float:
    coordinates = frame.coordinates(state)
    velocity = frame.inverse @ vdp_field_point(
        0.0, state, r=r, a2=a2, epsilon=epsilon
    )
    block = slice(0, 2) if unstable else slice(2, 4)
    radius = float(np.linalg.norm(coordinates[block]))
    if radius == 0.0:
        raise RuntimeError("radial event speed is undefined at zero radius")
    return float(coordinates[block] @ velocity[block] / radius)


def _sample_segment(
    integration: Any,
    *,
    name: str,
    start_face: str,
    end_face: str,
    samples_per_xi: int,
) -> CompleteBranchSegment:
    start = float(integration.t[0])
    end = float(integration.t[-1])
    count = max(65, int(np.ceil(samples_per_xi * (end - start))) + 1)
    xi = np.linspace(start, end, count)
    augmented = np.asarray(integration.sol(xi), dtype=float)
    return CompleteBranchSegment(
        name=name,
        start_face=start_face,
        end_face=end_face,
        xi=xi,
        central_state=augmented[:4],
        cumulative_physical_length=augmented[4],
        cumulative_physical_action=augmented[5],
    )


def integrate_complete_return_branch(
    *,
    source_state: Array,
    branch_id: str,
    r: float,
    a2: float,
    epsilon: float,
    source_radius: float = 0.01,
    local_return_radius: float | None = None,
    source_stable_width: float | None = None,
    uncertain_margin: float = 1.0e-6,
    maximum_time: float = 80.0,
    terminal_u: float = -10.0,
    escape_norm: float = 60.0,
    deep_cut_fraction: float = 5.0e-2,
    rtol: float = 1.0e-11,
    atol: float = 1.0e-13,
    max_step: float = 0.02,
    samples_per_xi: int = 100,
    provenance: Mapping[str, Any] | None = None,
) -> CompleteReturnBranch:
    """Integrate one complete return on a common numerical source face.

    ``source_state`` is used directly.  It is not reconstructed from its
    phase/transverse coordinates, because exponentially sensitive return
    candidates can move visibly under a tiny reconstruction perturbation.
    The routine raises :class:`RuntimeError` if a gate, deep cut, escape, or
    time limit occurs before the return.
    """

    return_radius = (
        float(source_radius)
        if local_return_radius is None
        else float(local_return_radius)
    )
    if not (
        r > 0.0
        and epsilon > 0.0
        and source_radius > 0.0
        and return_radius > 0.0
    ):
        raise ValueError("r, epsilon, and source_radius must be positive")
    if uncertain_margin < 0.0:
        raise ValueError("uncertain_margin must be nonnegative")
    if not (0.0 < deep_cut_fraction < 1.0):
        raise ValueError("deep_cut_fraction must lie in (0,1)")
    if samples_per_xi < 2:
        raise ValueError("samples_per_xi must be at least two")

    state0 = np.asarray(source_state, dtype=float)
    if state0.shape != (4,) or not np.all(np.isfinite(state0)):
        raise ValueError("source_state must be one finite four-vector")
    frame = reversible_saddle_frame(r, a2, epsilon)
    initial_coordinates = frame.coordinates(state0)
    initial_unstable_radius = float(np.linalg.norm(initial_coordinates[:2]))
    initial_stable_radius = float(np.linalg.norm(initial_coordinates[2:]))
    face_tolerance = max(2.0e-11, 20.0 * atol)
    if abs(return_radius - source_radius) > face_tolerance:
        raise ValueError(
            "a composable complete branch requires local_return_radius "
            "to equal source_radius"
        )
    if abs(initial_unstable_radius - source_radius) > face_tolerance:
        raise ValueError(
            "source_state is not on the outgoing unstable-radius face: "
            f"rho_u={initial_unstable_radius}, expected {source_radius}"
        )
    stable_width = source_radius if source_stable_width is None else source_stable_width
    if initial_stable_radius > stable_width:
        raise ValueError(
            "source_state lies outside the declared local stable width: "
            f"rho_s={initial_stable_radius}, width={stable_width}"
        )

    length_scale = float(r * epsilon ** (-0.25))
    action_scale = float(epsilon**2.25 * r**5)

    def augmented_field(time: float, augmented: Array) -> Array:
        state = augmented[:4]
        vector = vdp_field_point(time, state, r=r, a2=a2, epsilon=epsilon)
        action_density = float(state[1] ** 2 - state[3] ** 2)
        return np.r_[vector, length_scale, action_scale * action_density]

    def incoming_face(_time: float, augmented: Array) -> float:
        return float(
            np.linalg.norm(frame.coordinates(augmented[:4])[2:]) - return_radius
        )

    incoming_face.direction = -1
    incoming_face.terminal = True

    def terminal_gate(_time: float, augmented: Array) -> float:
        return float(augmented[0] - terminal_u)

    terminal_gate.direction = -1
    terminal_gate.terminal = True

    def escape_gate(_time: float, augmented: Array) -> float:
        return float(np.linalg.norm(augmented[:4]) - escape_norm)

    escape_gate.direction = 1
    escape_gate.terminal = True

    initial_augmented = np.r_[state0, 0.0, 0.0]
    first = solve_ivp(
        augmented_field,
        (0.0, maximum_time),
        initial_augmented,
        method="DOP853",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
        events=(incoming_face, terminal_gate, escape_gate),
        dense_output=True,
    )
    first_event = next(
        (index for index, values in enumerate(first.t_events) if len(values)), None
    )
    if first_event != 0:
        label = {
            None: "time_limit_unresolved",
            1: "terminal_gate_before_incoming_face",
            2: "escape_before_incoming_face",
        }[first_event]
        raise RuntimeError(f"complete return failed on global leg: {label}")

    incoming_time = float(first.t_events[0][0])
    incoming_augmented = np.asarray(first.y_events[0][0], dtype=float)

    def outgoing_face(_time: float, augmented: Array) -> float:
        return float(
            np.linalg.norm(frame.coordinates(augmented[:4])[:2]) - return_radius
        )

    outgoing_face.direction = 1
    outgoing_face.terminal = True

    def deep_cut(_time: float, augmented: Array) -> float:
        return float(
            np.linalg.norm(frame.coordinates(augmented[:4]))
            - return_radius * deep_cut_fraction
        )

    deep_cut.direction = -1
    deep_cut.terminal = True

    second = solve_ivp(
        augmented_field,
        (incoming_time, maximum_time),
        incoming_augmented,
        method="DOP853",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
        events=(outgoing_face, deep_cut, terminal_gate, escape_gate),
        dense_output=True,
    )
    second_event = next(
        (index for index, values in enumerate(second.t_events) if len(values)), None
    )
    if second_event != 0:
        label = {
            None: "time_limit_unresolved",
            1: "deep_stable_cut_before_return",
            2: "terminal_gate_before_return",
            3: "escape_before_return",
        }[second_event]
        raise RuntimeError(f"complete return failed on local leg: {label}")

    return_time = float(second.t_events[0][0])
    target_augmented = np.asarray(second.y_events[0][0], dtype=float)
    incoming_state = incoming_augmented[:4]
    target_state = target_augmented[:4]

    global_segment = _sample_segment(
        first,
        name="global_excursion",
        start_face="outgoing_unstable_radius",
        end_face="incoming_stable_radius",
        samples_per_xi=samples_per_xi,
    )
    local_segment = _sample_segment(
        second,
        name="local_saddle_passage",
        start_face="incoming_stable_radius",
        end_face="outgoing_unstable_radius",
        samples_per_xi=samples_per_xi,
    )
    segments = (global_segment, local_segment)

    source_coordinates = numerical_source_coordinates(
        state0, frame=frame, r=r, a2=a2, epsilon=epsilon
    )
    target_coordinates = numerical_source_coordinates(
        target_state, frame=frame, r=r, a2=a2, epsilon=epsilon
    )
    source_sign = _transverse_sign(
        float(source_coordinates["transverse_coordinate"]), uncertain_margin
    )
    target_sign = _transverse_sign(
        float(target_coordinates["transverse_coordinate"]), uncertain_margin
    )

    all_state = np.concatenate(
        (global_segment.central_state, local_segment.central_state[:, 1:]), axis=1
    )
    all_xi = np.concatenate((global_segment.xi, local_segment.xi[1:]))
    energy = vdp_hamiltonian(all_state, r, a2, epsilon)
    quadrature_action = float(
        action_scale
        * trapezoid(all_state[1] ** 2 - all_state[3] ** 2, x=all_xi)
    )
    total_length = float(sum(segment.physical_length for segment in segments))
    total_action = float(sum(segment.physical_action for segment in segments))
    direct_augmented_length = float(target_augmented[4])
    direct_augmented_action = float(target_augmented[5])
    target_linear = frame.coordinates(target_state)
    incoming_linear = frame.coordinates(incoming_state)
    coordinate_velocity_target = frame.inverse @ vdp_field_point(
        return_time, target_state, r=r, a2=a2, epsilon=epsilon
    )

    diagnostics: dict[str, Any] = {
        "solver_success": bool(first.success and second.success),
        "solver_method": "DOP853",
        "solver_rtol": float(rtol),
        "solver_atol": float(atol),
        "solver_max_step": float(max_step),
        "source_face_residual": abs(initial_unstable_radius - source_radius),
        "incoming_face_residual": abs(
            float(np.linalg.norm(incoming_linear[2:])) - return_radius
        ),
        "target_face_residual": abs(
            float(np.linalg.norm(target_linear[:2])) - return_radius
        ),
        "configured_local_return_radius": return_radius,
        "local_return_equals_source_radius": bool(
            abs(return_radius - source_radius) <= face_tolerance
        ),
        "source_stable_radius": initial_stable_radius,
        "incoming_unstable_radius": float(np.linalg.norm(incoming_linear[:2])),
        "target_stable_radius": float(np.linalg.norm(target_linear[2:])),
        "incoming_event_speed": _radial_speed(
            frame,
            incoming_state,
            unstable=False,
            r=r,
            a2=a2,
            epsilon=epsilon,
        ),
        "target_event_speed": float(
            target_linear[:2] @ coordinate_velocity_target[:2]
            / np.linalg.norm(target_linear[:2])
        ),
        "energy_drift": float(np.ptp(energy)),
        "energy_abs_max": float(np.max(np.abs(energy))),
        "minimum_terminal_gate_margin": float(np.min(all_state[0] - terminal_u)),
        "minimum_escape_margin": float(
            np.min(escape_norm - np.linalg.norm(all_state, axis=0))
        ),
        "local_residence_time_xi": float(return_time - incoming_time),
        "local_residence_turns_proxy": float(
            frame.beta * (return_time - incoming_time) / (2.0 * pi)
        ),
        "winding_status": WINDING_STATUS,
        "length_scale_dx_dxi": length_scale,
        "action_scale": action_scale,
        "physical_length_augmented": direct_augmented_length,
        "physical_action_augmented": direct_augmented_action,
        "physical_action_resampled_quadrature": quadrature_action,
        "resampled_action_difference": float(
            quadrature_action - direct_augmented_action
        ),
        "segment_length_composition_residual": float(
            total_length - direct_augmented_length
        ),
        "segment_action_composition_residual": float(
            total_action - direct_augmented_action
        ),
        "source_reconstruction_defect": float(
            source_coordinates["reconstruction_defect"]
        ),
        "target_reconstruction_defect": float(
            target_coordinates["reconstruction_defect"]
        ),
        "source_target_state_defect_inf": float(
            np.max(np.abs(target_state - state0))
        ),
        "target_unstable_first_coordinate": float(target_linear[0]),
        "target_sign_is_not_unstable_first_coordinate_sign": True,
    }
    return CompleteReturnBranch(
        branch_id=branch_id,
        r=float(r),
        a2=float(a2),
        epsilon=float(epsilon),
        source_radius=float(source_radius),
        local_return_radius=return_radius,
        source_state=state0,
        incoming_state=incoming_state,
        target_state=target_state,
        source_coordinates=source_coordinates,
        target_coordinates=target_coordinates,
        source_sign_proxy=source_sign,
        target_sign_proxy=target_sign,
        incoming_time_xi=incoming_time,
        return_time_xi=return_time,
        segments=segments,
        diagnostics=diagnostics,
        provenance={} if provenance is None else dict(provenance),
    )


# This source point is the A2 periodic outgoing-section anchor saved by the
# configuration-v2 exploratory master run.  It lies in the declared
# [-2e-4,2e-4] numerical transverse range.  It is a seed, not a certificate.
A2_SOURCE_SEED = np.array(
    [
        0.005115571304121211,
        0.0070663619333089156,
        -0.004889117632353183,
        0.0000381700305840751,
    ],
    dtype=float,
)

A2_REFERENCE_PHYSICAL_PERIOD = 2.159661039071366
A2_REFERENCE_PHYSICAL_ACTION = 4.790930094305982e-05


def compute_a2_complete_return_candidate(**overrides: Any) -> CompleteReturnBranch:
    """Compute the first contract-ready A2 floating-point return candidate."""

    options: dict[str, Any] = {
        "source_state": A2_SOURCE_SEED,
        "branch_id": "vdp-A2-rhou-1e-2-candidate-v1",
        "r": 0.08,
        "a2": 0.0,
        "epsilon": 1.0,
        "source_radius": 0.01,
        "source_stable_width": 0.01,
        "uncertain_margin": 1.0e-6,
        "maximum_time": 80.0,
        "terminal_u": -10.0,
        "escape_norm": 60.0,
        "rtol": 1.0e-11,
        "atol": 1.0e-13,
        "max_step": 0.02,
        "provenance": {
            "seed_status": "exploratory A2 periodic outgoing-section anchor",
            "seed_artifact": "numerics/results/vdp_v1_v7/v6_events.json",
            "configuration_version": 2,
            "family": "A",
            "relative_winding_metadata": 2,
            "relative_winding_is_not_V6_label": True,
            "reference_physical_period": A2_REFERENCE_PHYSICAL_PERIOD,
            "reference_physical_action": A2_REFERENCE_PHYSICAL_ACTION,
        },
    }
    options.update(overrides)
    return integrate_complete_return_branch(**options)


__all__ = [
    "A2_REFERENCE_PHYSICAL_ACTION",
    "A2_REFERENCE_PHYSICAL_PERIOD",
    "A2_SOURCE_SEED",
    "COORDINATE_STATUS",
    "CompleteBranchSegment",
    "CompleteReturnBranch",
    "EVIDENCE_STATUS",
    "WINDING_STATUS",
    "compute_a2_complete_return_candidate",
    "integrate_complete_return_branch",
]
