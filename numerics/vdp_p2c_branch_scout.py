"""Floating direct-source branch scout for the van der Pol P2c problem.

The P2c shooting map is

``M(mu, phi, T) = (P, Q)(Phi_mu^T(S_mu(phi)))``.

Here ``S_mu`` uses the *direct* radius-``.01`` source from the P2bK
contract: the radius is measured in the algebraic unstable coordinates and
the Kato phase is converted with ``R_chi``.  This is deliberately separate
from :func:`numerics.vdp_return_coding.homoclinic_source_anchor`, whose
historical numerical section uses a unit-normalized eigenframe and therefore
has a different radius normalization.

This module is a small, deterministic floating-point scout.  Its
finite-horizon unstable graph, shooting roots, finite-difference columns, and
sampled first-hit margins are ``COMPUTED/FLOAT`` evidence only.  They are
candidate centers and gates for an outward-rounded P2c implementation, not a
proof of a parameter-uniform homoclinic branch or a first-hit theorem.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from math import atan, ceil, cos, sin, sqrt
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp
from scipy.optimize import root

from numerics.rfsn_numerics import (
    vdp_coefficients,
    vdp_field_point,
    vdp_hamiltonian,
)


Array = NDArray[np.float64]
REVERSER_MATRIX = np.diag([1.0, -1.0, 1.0, -1.0])
COMPONENT_INDEX = {"U": 0, "P": 1, "V": 2, "Q": 3}

EVIDENCE_STATUS = (
    "COMPUTED/FLOAT_DIRECT_SOURCE_BRANCH_SCOUT -- not interval validation"
)
SCHEMA_VERSION = "rfsn-vdp-p2c-direct-source-branch-scout/1"
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent
    / "results"
    / "vdp_p2c_direct_source_branch_scout.json"
)

CORE_SEED = (5.861505585644915, 9.63744206789648)
PRIMARY_PARAMETERS = (0.08, 0.0, 1.0)


@dataclass(frozen=True)
class P2CParameters:
    """Parameters of the fixed-equilibrium central van der Pol system."""

    r: float
    a2: float
    epsilon: float


@dataclass(frozen=True)
class P2CScoutConfiguration:
    """Numerical choices for one reproducible floating branch scout."""

    source_radius: float = 0.01
    graph_horizon: float = 10.0
    graph_boundary_tolerance: float = 1.0e-9
    rtol: float = 1.0e-11
    atol: float = 1.0e-13
    graph_max_step: float = 0.04
    flight_max_step: float = 0.015
    shooting_root_tolerance: float = 3.0e-10
    phase_difference_step: float = 1.0e-5
    first_hit_sample_step: float = 5.0e-4
    pre_endpoint_gap: float = 0.02


@dataclass(frozen=True)
class P2BKAlgebraicFrame:
    """Exact-formula P2bK algebraic frame evaluated in binary64."""

    c: float
    alpha: float
    beta: float
    h: float
    y: float
    chi: float
    unstable: Array
    stable: Array
    inverse: Array
    rotation: Array


@dataclass(frozen=True)
class DirectSourceEvaluation:
    """One finite-horizon approximation to the P2bK direct true source."""

    state: Array
    algebraic_coordinates: Array
    graph_stable_coordinates: Array
    graph_boundary_residual_inf: float
    backward_endpoint_norm: float
    graph_solver_reported_success: bool
    graph_root_function_evaluations: int


@dataclass(frozen=True)
class FirstHitSegmentDiagnostic:
    """One sampled signed margin in the common candidate time partition."""

    label: str
    component: str
    relation: str
    time_interval: tuple[float, float]
    sampled_signed_margin: float
    time_of_sampled_minimum: float
    sample_count: int


@dataclass(frozen=True)
class DirectSourceBranchResult:
    """JSON-ready output for one positive-time direct-source shooting root."""

    parameters: P2CParameters
    initial_seed: tuple[float, float]
    phase: float
    half_time: float
    source_state: tuple[float, ...]
    source_algebraic_coordinates: tuple[float, ...]
    source_algebraic_unstable_radius: float
    source_radius_error: float
    source_energy_abs: float
    graph_boundary_residual_inf: float
    graph_backward_endpoint_norm: float
    graph_solver_reported_success: bool
    graph_root_function_evaluations: int
    endpoint_state: tuple[float, ...]
    shooting_residual: tuple[float, float]
    shooting_residual_inf: float
    endpoint_phase_column: tuple[float, ...]
    endpoint_time_column: tuple[float, ...]
    shooting_phase_column: tuple[float, float]
    shooting_time_column: tuple[float, float]
    shooting_determinant: float
    phase_difference_step: float
    shooting_solver_reported_success: bool
    shooting_root_function_evaluations: int
    first_hit_segments: tuple[FirstHitSegmentDiagnostic, ...]
    first_hit_common_segments_passed: bool
    minimum_pq_norm_before_endpoint_window: float
    time_of_minimum_pq_norm_before_endpoint_window: float
    endpoint_pq_speed: float
    evidence_status: str = EVIDENCE_STATUS

    def as_json_dict(self) -> dict[str, Any]:
        return _json_ready(asdict(self))


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


def p2bk_algebraic_frame(parameters: P2CParameters) -> P2BKAlgebraicFrame:
    """Evaluate the P2bK formulas ``E``, ``R_chi``, and the reversible frame.

    The unstable columns are exactly the algebraic columns frozen in
    ``validation/rigorous/config/vdp_p2_kato_v1.json``.  In particular, they
    are not normalized independently.
    """

    if parameters.epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    c, _quadratic, _cubic = vdp_coefficients(
        parameters.r, parameters.a2, parameters.epsilon
    )
    if abs(c) >= 2.0:
        raise ValueError("P2bK saddle-focus frame requires |c| < 2")
    alpha = 0.5 * sqrt(2.0 + c)
    beta = 0.5 * sqrt(2.0 - c)
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
    stable = REVERSER_MATRIX @ unstable
    full_frame = np.column_stack((unstable, stable))
    inverse = np.linalg.inv(full_frame)
    alpha0 = 1.0 / sqrt(2.0)
    y = (alpha0 - alpha) / beta
    rotation_denominator = sqrt(1.0 + y * y)
    rotation = np.array(
        [[1.0, -y], [y, 1.0]], dtype=np.float64
    ) / rotation_denominator
    return P2BKAlgebraicFrame(
        c=float(c),
        alpha=float(alpha),
        beta=float(beta),
        h=float(h),
        y=float(y),
        chi=float(atan(y)),
        unstable=unstable,
        stable=stable,
        inverse=inverse,
        rotation=rotation,
    )


class _DirectSourceShooter:
    """Cached nested graph and flight solves for one parameter point."""

    def __init__(
        self, parameters: P2CParameters, configuration: P2CScoutConfiguration
    ) -> None:
        self.parameters = parameters
        self.configuration = configuration
        self.frame = p2bk_algebraic_frame(parameters)
        self._source_cache: dict[str, DirectSourceEvaluation] = {}

    def _field(self, time: float, state: Array) -> Array:
        return vdp_field_point(
            time,
            state,
            r=self.parameters.r,
            a2=self.parameters.a2,
            epsilon=self.parameters.epsilon,
        )

    def direct_source(self, phase: float) -> DirectSourceEvaluation:
        key = float(phase).hex()
        cached = self._source_cache.get(key)
        if cached is not None:
            return cached

        config = self.configuration
        kato_coordinates = np.array([cos(phase), sin(phase)], dtype=np.float64)
        algebraic_unstable = (
            config.source_radius * self.frame.rotation @ kato_coordinates
        )

        def backward_residual(stable_coordinates: Array) -> Array:
            state = (
                self.frame.unstable @ algebraic_unstable
                + self.frame.stable
                @ np.asarray(stable_coordinates, dtype=np.float64)
            )
            integration = solve_ivp(
                self._field,
                (0.0, -config.graph_horizon),
                state,
                method="DOP853",
                rtol=config.rtol,
                atol=config.atol,
                max_step=config.graph_max_step,
            )
            if not integration.success:
                raise RuntimeError(integration.message)
            return (self.frame.inverse @ integration.y[:, -1])[2:]

        graph_root = root(
            backward_residual,
            np.zeros(2, dtype=np.float64),
            method="hybr",
            tol=min(1.0e-10, 0.1 * config.graph_boundary_tolerance),
            options={"maxfev": 80},
        )
        stable_coordinates = np.asarray(graph_root.x, dtype=np.float64)
        graph_residual = np.asarray(
            backward_residual(stable_coordinates), dtype=np.float64
        )
        residual_inf = float(np.max(np.abs(graph_residual)))
        if residual_inf > config.graph_boundary_tolerance:
            raise RuntimeError(
                "finite-horizon direct-source graph solve failed: "
                f"residual {residual_inf:.3e}"
            )
        state = (
            self.frame.unstable @ algebraic_unstable
            + self.frame.stable @ stable_coordinates
        )
        backward = solve_ivp(
            self._field,
            (0.0, -config.graph_horizon),
            state,
            method="DOP853",
            rtol=config.rtol,
            atol=config.atol,
            max_step=config.graph_max_step,
        )
        if not backward.success:
            raise RuntimeError(backward.message)
        evaluation = DirectSourceEvaluation(
            state=np.asarray(state, dtype=np.float64),
            algebraic_coordinates=self.frame.inverse @ state,
            graph_stable_coordinates=stable_coordinates,
            graph_boundary_residual_inf=residual_inf,
            backward_endpoint_norm=float(np.linalg.norm(backward.y[:, -1])),
            graph_solver_reported_success=bool(graph_root.success),
            graph_root_function_evaluations=int(graph_root.nfev),
        )
        self._source_cache[key] = evaluation
        return evaluation

    def flight(self, phase: float, half_time: float, *, dense: bool) -> Any:
        if half_time <= 0.0:
            raise ValueError("half_time must be positive")
        integration = solve_ivp(
            self._field,
            (0.0, float(half_time)),
            self.direct_source(float(phase)).state,
            method="DOP853",
            rtol=self.configuration.rtol,
            atol=self.configuration.atol,
            max_step=self.configuration.flight_max_step,
            dense_output=dense,
        )
        if not integration.success:
            raise RuntimeError(integration.message)
        return integration

    def shooting_map(self, unknown: Sequence[float]) -> Array:
        phase, half_time = (float(value) for value in unknown)
        if half_time <= 0.0:
            # Keep the root solver on the requested positive-time branch.
            return np.array([1.0e3 - half_time, 1.0e3 - half_time])
        endpoint = self.flight(phase, half_time, dense=False).y[:, -1]
        return np.asarray(endpoint[[1, 3]], dtype=np.float64)


def _sample_segment(
    dense_solution: Any,
    *,
    label: str,
    component: str,
    sign: float,
    lower: float,
    upper: float,
    sample_step: float,
) -> FirstHitSegmentDiagnostic:
    if not 0.0 <= lower < upper:
        raise ValueError(f"invalid first-hit segment [{lower}, {upper}]")
    count = max(2, int(ceil((upper - lower) / sample_step)) + 1)
    times = np.linspace(lower, upper, count)
    values = sign * dense_solution.sol(times)[COMPONENT_INDEX[component]]
    minimum_index = int(np.argmin(values))
    return FirstHitSegmentDiagnostic(
        label=label,
        component=component,
        relation=">0" if sign > 0.0 else "<0",
        time_interval=(float(lower), float(upper)),
        sampled_signed_margin=float(values[minimum_index]),
        time_of_sampled_minimum=float(times[minimum_index]),
        sample_count=count,
    )


def _first_hit_diagnostics(
    dense_solution: Any,
    half_time: float,
    configuration: P2CScoutConfiguration,
) -> tuple[
    tuple[FirstHitSegmentDiagnostic, ...], bool, float, float
]:
    if half_time <= 9.55:
        raise RuntimeError("candidate half-time does not reach the common final tube")
    segments = (
        _sample_segment(
            dense_solution,
            label="P_positive_0_to_1_55",
            component="P",
            sign=1.0,
            lower=0.0,
            upper=1.55,
            sample_step=configuration.first_hit_sample_step,
        ),
        _sample_segment(
            dense_solution,
            label="Q_positive_1_55_to_1_90",
            component="Q",
            sign=1.0,
            lower=1.55,
            upper=1.90,
            sample_step=configuration.first_hit_sample_step,
        ),
        _sample_segment(
            dense_solution,
            label="P_negative_1_90_to_7_35",
            component="P",
            sign=-1.0,
            lower=1.90,
            upper=7.35,
            sample_step=configuration.first_hit_sample_step,
        ),
        _sample_segment(
            dense_solution,
            label="Q_negative_7_35_to_9_55",
            component="Q",
            sign=-1.0,
            lower=7.35,
            upper=9.55,
            sample_step=configuration.first_hit_sample_step,
        ),
        _sample_segment(
            dense_solution,
            label="U_positive_9_55_to_endpoint",
            component="U",
            sign=1.0,
            lower=9.55,
            upper=half_time,
            sample_step=configuration.first_hit_sample_step,
        ),
    )
    common_segments_passed = all(
        segment.sampled_signed_margin > 0.0 for segment in segments
    )

    pre_endpoint = half_time - configuration.pre_endpoint_gap
    count = max(
        2,
        int(ceil(pre_endpoint / configuration.first_hit_sample_step)) + 1,
    )
    times = np.linspace(0.0, pre_endpoint, count)
    states = dense_solution.sol(times)
    pq_norm = np.hypot(states[1], states[3])
    minimum_index = int(np.argmin(pq_norm))
    return (
        segments,
        common_segments_passed,
        float(pq_norm[minimum_index]),
        float(times[minimum_index]),
    )


def solve_direct_source_branch(
    parameters: P2CParameters,
    seed: Sequence[float],
    *,
    configuration: P2CScoutConfiguration | None = None,
) -> DirectSourceBranchResult:
    """Solve the floating P2c direct-source shooting pair at one parameter."""

    config = configuration or P2CScoutConfiguration()
    seed_values = tuple(float(value) for value in seed)
    if len(seed_values) != 2:
        raise ValueError("seed must contain (phase, half_time)")
    initial_seed = (seed_values[0], seed_values[1])
    if initial_seed[1] <= 0.0:
        raise ValueError("the seed half_time must be positive")
    shooter = _DirectSourceShooter(parameters, config)
    shooting_root = root(
        shooter.shooting_map,
        np.asarray(initial_seed, dtype=np.float64),
        method="hybr",
        tol=config.shooting_root_tolerance,
        options={"maxfev": 50},
    )
    phase, half_time = (float(value) for value in shooting_root.x)
    residual = shooter.shooting_map((phase, half_time))
    residual_inf = float(np.max(np.abs(residual)))
    if half_time <= 0.0 or residual_inf > 1.0e-8:
        raise RuntimeError(
            "direct-source shooting solve failed: "
            f"success={shooting_root.success}, residual={residual_inf:.3e}, "
            f"root=({phase:.16g}, {half_time:.16g})"
        )

    source = shooter.direct_source(phase)
    flight = shooter.flight(phase, half_time, dense=True)
    endpoint = np.asarray(flight.y[:, -1], dtype=np.float64)
    difference_step = config.phase_difference_step
    endpoint_plus = shooter.flight(
        phase + difference_step, half_time, dense=False
    ).y[:, -1]
    endpoint_minus = shooter.flight(
        phase - difference_step, half_time, dense=False
    ).y[:, -1]
    endpoint_phase_column = np.asarray(
        (endpoint_plus - endpoint_minus) / (2.0 * difference_step),
        dtype=np.float64,
    )
    endpoint_time_column = shooter._field(half_time, endpoint)
    shooting_phase_column = endpoint_phase_column[[1, 3]]
    shooting_time_column = endpoint_time_column[[1, 3]]
    determinant = float(
        np.linalg.det(
            np.column_stack((shooting_phase_column, shooting_time_column))
        )
    )
    (
        first_hit_segments,
        first_hit_passed,
        minimum_pq_norm,
        minimum_pq_time,
    ) = _first_hit_diagnostics(flight, half_time, config)

    algebraic_unstable_radius = float(
        np.linalg.norm(source.algebraic_coordinates[:2])
    )
    source_energy = float(
        vdp_hamiltonian(
            source.state[:, None],
            parameters.r,
            parameters.a2,
            parameters.epsilon,
        )[0]
    )
    return DirectSourceBranchResult(
        parameters=parameters,
        initial_seed=initial_seed,
        phase=phase,
        half_time=half_time,
        source_state=tuple(float(value) for value in source.state),
        source_algebraic_coordinates=tuple(
            float(value) for value in source.algebraic_coordinates
        ),
        source_algebraic_unstable_radius=algebraic_unstable_radius,
        source_radius_error=abs(algebraic_unstable_radius - config.source_radius),
        source_energy_abs=abs(source_energy),
        graph_boundary_residual_inf=source.graph_boundary_residual_inf,
        graph_backward_endpoint_norm=source.backward_endpoint_norm,
        graph_solver_reported_success=source.graph_solver_reported_success,
        graph_root_function_evaluations=source.graph_root_function_evaluations,
        endpoint_state=tuple(float(value) for value in endpoint),
        shooting_residual=(float(residual[0]), float(residual[1])),
        shooting_residual_inf=residual_inf,
        endpoint_phase_column=tuple(
            float(value) for value in endpoint_phase_column
        ),
        endpoint_time_column=tuple(float(value) for value in endpoint_time_column),
        shooting_phase_column=(
            float(shooting_phase_column[0]),
            float(shooting_phase_column[1]),
        ),
        shooting_time_column=(
            float(shooting_time_column[0]),
            float(shooting_time_column[1]),
        ),
        shooting_determinant=determinant,
        phase_difference_step=difference_step,
        shooting_solver_reported_success=bool(shooting_root.success),
        shooting_root_function_evaluations=int(shooting_root.nfev),
        first_hit_segments=first_hit_segments,
        first_hit_common_segments_passed=first_hit_passed,
        minimum_pq_norm_before_endpoint_window=minimum_pq_norm,
        time_of_minimum_pq_norm_before_endpoint_window=minimum_pq_time,
        endpoint_pq_speed=float(np.linalg.norm(shooting_time_column)),
    )


def build_default_scout() -> dict[str, Any]:
    """Compute the core anchor and the primary positive-parameter candidate."""

    configuration = P2CScoutConfiguration()
    core = solve_direct_source_branch(
        P2CParameters(r=0.0, a2=0.0, epsilon=1.0),
        CORE_SEED,
        configuration=configuration,
    )
    primary = solve_direct_source_branch(
        P2CParameters(*PRIMARY_PARAMETERS),
        (core.phase, core.half_time),
        configuration=configuration,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "theorem_validation_status": "NOT_INTERVAL_VALIDATED",
        "claim_bearing": False,
        "source_contract": {
            "source_radius": configuration.source_radius,
            "algebraic_frame_formula": (
                "E=[[1,0],[alpha,-beta],[c/2,2*alpha*beta],"
                "[alpha,beta]]"
            ),
            "phase_rotation_formula": (
                "b(phi)=R*R_chi*(cos(phi),sin(phi)); "
                "R_chi=[[1,-y],[y,1]]/sqrt(1+y^2); "
                "y=(1/sqrt(2)-alpha)/beta"
            ),
            "true_graph_model": (
                "finite-horizon floating approximation with b fixed in the "
                "P2bK algebraic coordinates"
            ),
            "historical_normalized_eigenframe_anchor_reused": False,
        },
        "configuration": _json_ready(asdict(configuration)),
        "common_first_hit_partition": [
            ["P>0", 0.0, 1.55],
            ["Q>0", 1.55, 1.90],
            ["P<0", 1.90, 7.35],
            ["Q<0", 7.35, 9.55],
            ["U>0", 9.55, "T"],
        ],
        "samples": {
            "core": core.as_json_dict(),
            "primary_r_0p08_a2_0_epsilon_1": primary.as_json_dict(),
        },
        "nonclaims": [
            "The finite-horizon source is not an interval enclosure of the true graph.",
            "The shooting root and finite-difference columns are ordinary binary64 computations.",
            "Sampled sign margins do not prove a first-hit statement "
            "between samples or uniformly in parameter.",
            "Only the core and one positive parameter point are emitted; "
            "there is no gap-free parameter cover.",
            "This scout does not prove homoclinic uniqueness, weighted tails, "
            "exact charts, or event atlases.",
        ],
    }


def write_default_scout(path: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    """Compute and write the deterministic two-sample scout JSON."""

    result = build_default_scout()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> None:
    result = write_default_scout()
    core = result["samples"]["core"]
    primary = result["samples"]["primary_r_0p08_a2_0_epsilon_1"]
    print(
        "P2c direct-source scout: "
        f"core det={core['shooting_determinant']:.12g}, "
        f"primary (phi,T)=({primary['phase']:.12g},"
        f"{primary['half_time']:.12g}), "
        f"det={primary['shooting_determinant']:.12g}"
    )
    print(DEFAULT_OUTPUT)


if __name__ == "__main__":
    main()


__all__ = [
    "CORE_SEED",
    "DEFAULT_OUTPUT",
    "DirectSourceBranchResult",
    "EVIDENCE_STATUS",
    "FirstHitSegmentDiagnostic",
    "P2BKAlgebraicFrame",
    "P2CParameters",
    "P2CScoutConfiguration",
    "PRIMARY_PARAMETERS",
    "SCHEMA_VERSION",
    "build_default_scout",
    "p2bk_algebraic_frame",
    "solve_direct_source_branch",
    "write_default_scout",
]
