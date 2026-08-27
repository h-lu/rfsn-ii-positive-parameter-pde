"""Floating-point V1--V2 diagnostics for the van der Pol spatial system.

This module implements reproducible numerical *illustrations* of the exact
Hamiltonian bridge and the compact central continuation theorem.  Nothing in
this file validates a theorem box.  In particular, the local-passage and
finite-event routines are explicitly labelled proxies: the exact V2
action--angle charts and the certified compact event atlas are analytic
objects that are not reconstructed here.

The public conversion helpers return JSON-ready dictionaries or arrays that
can be passed directly to ``numpy.savez_compressed``.  They do not write files.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from itertools import permutations
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp
from scipy.linalg import schur
from scipy.optimize import brentq

from numerics.rfsn_numerics import (
    HomoclinicResult,
    continue_homoclinics,
    origin_matrix,
    vdp_coefficients,
    vdp_field_point,
    vdp_hamiltonian,
)


Array = NDArray[np.float64]
REVERSER_MATRIX = np.diag([1.0, -1.0, 1.0, -1.0])

FLOAT_EVIDENCE = "COMPUTED/FLOAT -- explanatory evidence, not theorem validation"
PROXY_EVIDENCE = (
    "COMPUTED/FLOAT_PROXY -- not the exact V2 saddle chart or certified event atlas"
)


def json_ready(value: Any) -> Any:
    """Recursively convert diagnostics to objects accepted by ``json.dumps``."""

    if is_dataclass(value):
        return json_ready(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, np.ndarray):
        return json_ready(value.tolist())
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, complex):
        return {"real": float(value.real), "imag": float(value.imag)}
    if isinstance(value, np.generic):
        return value.item()
    return value


@dataclass(frozen=True)
class SymbolicCheckReport:
    """Exact symbolic residuals for the V1 and central Hamiltonian formulas."""

    residuals: dict[str, str]
    passed: bool
    evidence_status: str = "EXACT/DERIVED symbolic identities"

    def as_json_dict(self) -> dict[str, Any]:
        return json_ready(self)


def symbolic_hamiltonian_checks() -> SymbolicCheckReport:
    """Return exact SymPy checks of Hamiltonian, primitive, and reverser signs.

    Both the physical fast-space V1 convention and the fixed-equilibrium
    central convention are checked.  Residuals are stored as strings so that
    the result is stable and immediately JSON serializable.
    """

    import sympy as sp

    u, p, v, q = sp.symbols("u p v q", real=True)
    a, delta, epsilon = sp.symbols(
        "a delta epsilon", positive=True, finite=True, real=True
    )
    coordinates = sp.Matrix([u, p, v, q])
    f = u**3 / 3 - u
    primitive_f = u**4 / 12 - u**2 / 2
    field = sp.Matrix([p, f - v, delta * q, epsilon * delta * (u - a)])
    first_integral = (
        (epsilon * p**2 - q**2) / 2
        - epsilon * (primitive_f + (a - u) * v)
    )
    hamiltonian = -first_integral
    primitive_coefficients = sp.Matrix([epsilon * p, 0, -q / delta, 0])
    omega = sp.Matrix(
        4,
        4,
        lambda i, j: sp.diff(primitive_coefficients[j], coordinates[i])
        - sp.diff(primitive_coefficients[i], coordinates[j]),
    )
    reverser = sp.diag(1, -1, 1, -1)
    reverse_substitution = {p: -p, q: -q}
    reversed_field = field.subs(reverse_substitution, simultaneous=True)
    reversed_primitive = primitive_coefficients.subs(
        reverse_substitution, simultaneous=True
    )
    reversed_omega = omega.subs(reverse_substitution, simultaneous=True)

    residual_expressions: dict[str, Any] = {
        "physical_first_integral": sp.diff(first_integral, u) * field[0]
        + sp.diff(first_integral, p) * field[1]
        + sp.diff(first_integral, v) * field[2]
        + sp.diff(first_integral, q) * field[3],
        "physical_hamiltonian_contraction": -(omega * field)
        - sp.Matrix([sp.diff(hamiltonian, item) for item in coordinates]),
        "physical_reverser_vector_field": reverser * field + reversed_field,
        "physical_reverser_primitive": reverser.T * reversed_primitive
        + primitive_coefficients,
        "physical_reverser_two_form": reverser.T * reversed_omega * reverser
        + omega,
    }

    U, P, V, Q = sp.symbols("U P V Q", real=True)
    r, a2 = sp.symbols("r a2", real=True)
    sqrt_epsilon = sp.sqrt(epsilon)
    central_coordinates = sp.Matrix([U, P, V, Q])
    c = 2 * r * a2 + sqrt_epsilon * r**4 * a2**2
    quadratic = 1 + sqrt_epsilon * r**3 * a2
    central_field = sp.Matrix(
        [
            P,
            c * U - V - quadratic * U**2 + sqrt_epsilon * r**2 * U**3 / 3,
            Q,
            U,
        ]
    )
    central_hamiltonian = (
        (Q**2 - P**2) / 2
        - U * V
        + c * U**2 / 2
        - quadratic * U**3 / 3
        + sqrt_epsilon * r**2 * U**4 / 12
    )
    central_primitive = sp.Matrix([P, 0, -Q, 0])
    central_omega = sp.Matrix(
        4,
        4,
        lambda i, j: sp.diff(central_primitive[j], central_coordinates[i])
        - sp.diff(central_primitive[i], central_coordinates[j]),
    )
    central_reverse_substitution = {P: -P, Q: -Q}
    central_reversed_field = central_field.subs(
        central_reverse_substitution, simultaneous=True
    )
    central_reversed_primitive = central_primitive.subs(
        central_reverse_substitution, simultaneous=True
    )
    residual_expressions.update(
        {
            "central_hamiltonian_contraction": -(central_omega * central_field)
            - sp.Matrix(
                [
                    sp.diff(central_hamiltonian, item)
                    for item in central_coordinates
                ]
            ),
            "central_reverser_vector_field": reverser * central_field
            + central_reversed_field,
            "central_reverser_primitive": reverser.T * central_reversed_primitive
            + central_primitive,
            "central_energy_reversibility": central_hamiltonian.subs(
                central_reverse_substitution, simultaneous=True
            )
            - central_hamiltonian,
        }
    )

    simplified: dict[str, str] = {}
    passed = True
    for name, expression in residual_expressions.items():
        if isinstance(expression, sp.MatrixBase):
            entries = [sp.simplify(entry) for entry in expression]
            is_zero = all(entry == 0 for entry in entries)
            simplified[name] = "0" if is_zero else str(sp.Matrix(expression.shape[0], expression.shape[1], entries))
        else:
            reduced = sp.simplify(expression)
            is_zero = reduced == 0
            simplified[name] = str(reduced)
        passed = passed and bool(is_zero)
    return SymbolicCheckReport(residuals=simplified, passed=passed)


@dataclass(frozen=True)
class SaddleFocusSpectrum:
    r: float
    a2: float
    epsilon: float
    c: float
    alpha: float
    beta: float
    eigenvalues: tuple[complex, ...]
    characteristic_residual_inf: float
    quartet_match_error: float
    is_saddle_focus: bool
    evidence_status: str = FLOAT_EVIDENCE

    def as_json_dict(self) -> dict[str, Any]:
        return json_ready(self)


def saddle_focus_spectrum(
    r: float, a2: float = 0.0, epsilon: float = 1.0
) -> SaddleFocusSpectrum:
    """Compute the V2 saddle-focus quartet and compare it with the formula."""

    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    c, _quadratic, _cubic = vdp_coefficients(r, a2, epsilon)
    is_saddle_focus = bool(abs(c) < 2.0)
    if not is_saddle_focus:
        alpha = float("nan")
        beta = float("nan")
        expected: tuple[complex, ...] = ()
    else:
        alpha = 0.5 * float(np.sqrt(2.0 + c))
        beta = 0.5 * float(np.sqrt(2.0 - c))
        expected = (
            alpha + 1j * beta,
            alpha - 1j * beta,
            -alpha + 1j * beta,
            -alpha - 1j * beta,
        )
    eigenvalues = tuple(
        complex(value)
        for value in np.linalg.eigvals(origin_matrix("vdp", r, a2, epsilon))
    )
    characteristic_residual = float(
        max(abs(value**4 - c * value**2 + 1.0) for value in eigenvalues)
    )
    if expected:
        quartet_match_error = float(
            min(
                max(abs(eigenvalues[index] - candidate[index]) for index in range(4))
                for candidate in permutations(expected)
            )
        )
    else:
        quartet_match_error = float("nan")
    return SaddleFocusSpectrum(
        r=float(r),
        a2=float(a2),
        epsilon=float(epsilon),
        c=float(c),
        alpha=alpha,
        beta=beta,
        eigenvalues=eigenvalues,
        characteristic_residual_inf=characteristic_residual,
        quartet_match_error=quartet_match_error,
        is_saddle_focus=is_saddle_focus,
    )


def vdp_jacobian(state: Sequence[float], r: float, a2: float, epsilon: float) -> Array:
    """Jacobian of the exact fixed-equilibrium central vector field."""

    u = float(state[0])
    c, quadratic, cubic = vdp_coefficients(r, a2, epsilon)
    return np.array(
        [
            [0.0, 1.0, 0.0, 0.0],
            [c - 2.0 * quadratic * u + 3.0 * cubic * u * u, 0.0, -1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )


def vdp_energy_gradient(
    state: Sequence[float], r: float, a2: float, epsilon: float
) -> Array:
    """Gradient of the shifted central Hamiltonian ``widehat H``."""

    u, p, v, q = (float(item) for item in state)
    c, quadratic, cubic = vdp_coefficients(r, a2, epsilon)
    return np.array(
        [
            -v + c * u - quadratic * u * u + cubic * u**3,
            -p,
            -u,
            q,
        ],
        dtype=np.float64,
    )


@dataclass(frozen=True)
class TransversalityProxy:
    quotient_sine: float
    rank_three_singular_value: float
    rank_defect_singular_value: float
    stable_energy_tangency_defect: float
    unstable_energy_tangency_defect: float
    flow_to_stable_distance: float
    flow_to_unstable_distance: float
    fundamental_condition_number: float
    evidence_status: str = PROXY_EVIDENCE
    scope_note: str = (
        "Finite-tail variational proxy for transversality modulo flow; "
        "not an interval lower bound and not the V2 shooting certificate."
    )

    def as_json_dict(self) -> dict[str, Any]:
        return json_ready(self)


def _projected_quotient_direction(basis: Array, flow: Array, gradient: Array) -> Array:
    gradient_unit = gradient / np.linalg.norm(gradient)
    flow_tangent = flow - gradient_unit * float(np.dot(gradient_unit, flow))
    flow_unit = flow_tangent / np.linalg.norm(flow_tangent)
    projector = (
        np.eye(4)
        - np.outer(gradient_unit, gradient_unit)
        - np.outer(flow_unit, flow_unit)
    )
    projected = projector @ basis
    left_vectors, singular_values, _right_vectors = np.linalg.svd(
        projected, full_matrices=False
    )
    if singular_values[0] <= 1.0e-14:
        raise RuntimeError("tangent plane has no resolved quotient direction")
    return left_vectors[:, 0]


def transversality_proxy(
    result: HomoclinicResult,
    *,
    rtol: float = 2.0e-10,
    atol: float = 2.0e-12,
    max_step: float = 0.03,
) -> TransversalityProxy:
    """Compute a reproducible finite-tail proxy for V2 homoclinic transversality.

    The linear stable plane is transported backward from the BVP tail to the
    symmetry point.  Reflecting the transported plane gives
    approximations of the two tangent planes at the symmetry point.  Their
    angle after quotienting the common flow direction is the reported proxy.
    """

    if result.model != "vdp":
        raise ValueError("transversality_proxy expects a van der Pol homoclinic")
    r, a2, epsilon = result.r, result.a2, result.epsilon

    _triangular, schur_vectors, stable_dimension = schur(
        origin_matrix("vdp", r, a2, epsilon),
        output="real",
        sort=lambda real, imag: real < 0.0,
    )
    if stable_dimension != 2:
        raise RuntimeError(f"expected stable dimension two, got {stable_dimension}")
    tail_stable_basis = schur_vectors[:, :stable_dimension]

    # Transport only the two-dimensional stable plane backward from the BVP
    # tail.  Forming a full forward fundamental matrix and explicitly solving
    # through it loses rank once exp((alpha_u-alpha_s)L) approaches machine
    # precision on the longer production domains.
    def subspace_rhs(time: float, flattened: Array) -> Array:
        state = result.solution.sol(time)
        basis = flattened.reshape(4, 2)
        return (vdp_jacobian(state, r, a2, epsilon) @ basis).ravel()

    integration = solve_ivp(
        subspace_rhs,
        (result.domain, 0.0),
        tail_stable_basis.ravel(),
        method="DOP853",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    if not integration.success:
        raise RuntimeError(integration.message)
    center_stable_raw = integration.y[:, -1].reshape(4, 2)
    center_stable, _triangular_factor = np.linalg.qr(center_stable_raw)
    center_stable = center_stable[:, :2]
    center_unstable = REVERSER_MATRIX @ center_stable

    center = np.asarray(result.solution.sol(0.0), dtype=np.float64)
    flow = vdp_field_point(0.0, center, r=r, a2=a2, epsilon=epsilon)
    flow_unit = flow / np.linalg.norm(flow)
    gradient = vdp_energy_gradient(center, r, a2, epsilon)
    gradient_norm = np.linalg.norm(gradient)
    stable_direction = _projected_quotient_direction(
        center_stable, flow, gradient
    )
    unstable_direction = _projected_quotient_direction(
        center_unstable, flow, gradient
    )
    quotient_dot = float(np.clip(abs(np.dot(stable_direction, unstable_direction)), 0.0, 1.0))
    quotient_sine = float(np.sqrt(max(0.0, 1.0 - quotient_dot**2)))
    combined = np.column_stack((center_stable, center_unstable))
    singular_values = np.linalg.svd(combined, compute_uv=False)
    return TransversalityProxy(
        quotient_sine=quotient_sine,
        rank_three_singular_value=float(singular_values[2]),
        rank_defect_singular_value=float(singular_values[3]),
        stable_energy_tangency_defect=float(
            np.max(np.abs(gradient @ center_stable)) / gradient_norm
        ),
        unstable_energy_tangency_defect=float(
            np.max(np.abs(gradient @ center_unstable)) / gradient_norm
        ),
        flow_to_stable_distance=float(
            np.linalg.norm(flow_unit - center_stable @ (center_stable.T @ flow_unit))
        ),
        flow_to_unstable_distance=float(
            np.linalg.norm(flow_unit - center_unstable @ (center_unstable.T @ flow_unit))
        ),
        fundamental_condition_number=float(np.linalg.cond(center_stable_raw)),
    )


@dataclass(frozen=True)
class HomoclinicSliceSample:
    r: float
    a2: float
    epsilon: float
    spectrum: SaddleFocusSpectrum
    center: tuple[float, ...]
    tail: tuple[float, ...]
    diagnostics: dict[str, float | bool]
    transversality: TransversalityProxy


@dataclass(frozen=True)
class HomoclinicSliceReport:
    samples: tuple[HomoclinicSliceSample, ...]
    domain_xi: float
    bvp_tolerance: float
    evidence_status: str = FLOAT_EVIDENCE
    scope_note: str = (
        "Exploratory one-dimensional continuation slice; it is not an explicit "
        "V2 theorem wedge or a uniform validation."
    )

    def as_json_dict(self) -> dict[str, Any]:
        return json_ready(self)


@dataclass
class HomoclinicContinuation:
    """Serializable report together with non-serializable collocation objects."""

    report: HomoclinicSliceReport
    results: tuple[HomoclinicResult, ...]

    def as_json_dict(self) -> dict[str, Any]:
        return self.report.as_json_dict()

    def as_npz_payload(self, points: int = 1201) -> dict[str, Array]:
        return homoclinic_npz_payload(self, points=points)


def compute_homoclinic_continuation(
    r_values: Iterable[float],
    *,
    a2: float = 0.0,
    epsilon: float = 1.0,
    domain: float = 16.0,
    tolerance: float = 2.0e-7,
    transversality_rtol: float = 2.0e-10,
    transversality_atol: float = 2.0e-12,
    transversality_max_step: float = 0.03,
) -> HomoclinicContinuation:
    """Continue the selected numerical homoclinic along an exploratory r-slice."""

    values = tuple(float(value) for value in r_values)
    if not values:
        raise ValueError("r_values must be nonempty")
    results = tuple(
        continue_homoclinics(
            "vdp",
            values,
            a2=a2,
            epsilon=epsilon,
            domain=domain,
            tolerance=tolerance,
        )
    )
    samples: list[HomoclinicSliceSample] = []
    for result in results:
        proxy = transversality_proxy(
            result,
            rtol=transversality_rtol,
            atol=transversality_atol,
            max_step=transversality_max_step,
        )
        samples.append(
            HomoclinicSliceSample(
                r=result.r,
                a2=result.a2,
                epsilon=result.epsilon,
                spectrum=saddle_focus_spectrum(
                    result.r, result.a2, result.epsilon
                ),
                center=tuple(float(item) for item in result.solution.sol(0.0)),
                tail=tuple(
                    float(item) for item in result.solution.sol(result.domain)
                ),
                diagnostics=dict(result.diagnostics),
                transversality=proxy,
            )
        )
    return HomoclinicContinuation(
        report=HomoclinicSliceReport(
            samples=tuple(samples),
            domain_xi=float(domain),
            bvp_tolerance=float(tolerance),
        ),
        results=results,
    )


def homoclinic_npz_payload(
    continuation: HomoclinicContinuation, *, points: int = 1201
) -> dict[str, Array]:
    """Return a dense, homogeneous array payload for ``numpy.savez``."""

    if points < 3:
        raise ValueError("points must be at least three")
    domain = min(result.domain for result in continuation.results)
    xi = np.linspace(0.0, domain, points)
    states = np.stack([result.solution.sol(xi) for result in continuation.results])
    samples = continuation.report.samples
    return {
        "r": np.array([sample.r for sample in samples], dtype=np.float64),
        "a2": np.array([sample.a2 for sample in samples], dtype=np.float64),
        "epsilon": np.array(
            [sample.epsilon for sample in samples], dtype=np.float64
        ),
        "xi_half": xi,
        "state_half": states,
        "center": np.array([sample.center for sample in samples]),
        "tail": np.array([sample.tail for sample in samples]),
        "alpha": np.array([sample.spectrum.alpha for sample in samples]),
        "beta": np.array([sample.spectrum.beta for sample in samples]),
        "quotient_sine_proxy": np.array(
            [sample.transversality.quotient_sine for sample in samples]
        ),
        "rank_three_singular_value_proxy": np.array(
            [
                sample.transversality.rank_three_singular_value
                for sample in samples
            ]
        ),
        "ode_residual_inf": np.array(
            [sample.diagnostics["normalized_ode_residual_inf"] for sample in samples]
        ),
        "tail_norm": np.array(
            [sample.diagnostics["tail_norm"] for sample in samples]
        ),
    }


def _complex_eigenframe(
    r: float, a2: float, epsilon: float
) -> tuple[Array, Array, float]:
    matrix = origin_matrix("vdp", r, a2, epsilon)
    eigenvalues, eigenvectors = np.linalg.eig(matrix)

    def select(real_sign: int) -> int:
        candidates = [
            index
            for index, value in enumerate(eigenvalues)
            if real_sign * value.real > 0.0 and value.imag > 0.0
        ]
        if len(candidates) != 1:
            raise RuntimeError("could not select a unique saddle-focus eigenvector")
        return candidates[0]

    unstable = eigenvectors[:, select(+1)]
    stable = eigenvectors[:, select(-1)]
    frame = np.column_stack(
        (unstable.real, unstable.imag, stable.real, stable.imag)
    ).astype(np.float64)
    condition = float(np.linalg.cond(frame))
    if not np.isfinite(condition) or condition > 1.0e8:
        raise RuntimeError(f"ill-conditioned eigenframe: {condition:.3e}")
    return frame, np.linalg.inv(frame), condition


def _find_stable_section_point(
    result: HomoclinicResult, inverse_frame: Array, section_radius: float
) -> tuple[float, Array]:
    grid = np.linspace(0.0, result.domain, 2001)
    states = result.solution.sol(grid)
    stable_radius = np.linalg.norm(inverse_frame[2:, :] @ states, axis=0)
    shifted = stable_radius - section_radius
    crossings = np.flatnonzero(shifted[:-1] * shifted[1:] <= 0.0)
    if crossings.size == 0:
        raise RuntimeError(
            f"stable radius {section_radius:g} is not crossed on the BVP half-orbit"
        )
    index = int(crossings[-1])
    entry_time = float(
        brentq(
            lambda time: np.linalg.norm(
                inverse_frame[2:, :] @ result.solution.sol(time)
            )
            - section_radius,
            float(grid[index]),
            float(grid[index + 1]),
            xtol=1.0e-13,
            rtol=1.0e-13,
        )
    )
    return entry_time, np.asarray(result.solution.sol(entry_time), dtype=np.float64)


def _energy_matched_perturbation(
    base: Array,
    nu_proxy: float,
    unstable_frame: Array,
    r: float,
    a2: float,
    epsilon: float,
) -> tuple[Array, float]:
    gradient = vdp_energy_gradient(base, r, a2, epsilon)
    unstable_gradient = unstable_frame.T @ gradient
    norm = float(np.linalg.norm(unstable_gradient))
    if norm <= 1.0e-12:
        raise RuntimeError("energy gradient does not resolve an unstable adjustment")
    adjust_coordinates = unstable_gradient / norm
    primary_coordinates = np.array(
        [-adjust_coordinates[1], adjust_coordinates[0]], dtype=np.float64
    )
    adjust_direction = unstable_frame @ adjust_coordinates
    primary_direction = unstable_frame @ primary_coordinates
    base_energy = float(vdp_hamiltonian(base[:, None], r, a2, epsilon)[0])

    def mismatch(adjustment: float) -> float:
        state = base + nu_proxy * primary_direction + adjustment * adjust_direction
        return float(vdp_hamiltonian(state[:, None], r, a2, epsilon)[0]) - base_energy

    span = max(4.0 * abs(nu_proxy), 1.0e-10)
    left, right = -span, span
    left_value, right_value = mismatch(left), mismatch(right)
    for _attempt in range(20):
        if left_value == 0.0:
            adjustment = left
            break
        if right_value == 0.0:
            adjustment = right
            break
        if left_value * right_value < 0.0:
            adjustment = float(
                brentq(mismatch, left, right, xtol=1.0e-14, rtol=1.0e-13)
            )
            break
        span *= 2.0
        left, right = -span, span
        left_value, right_value = mismatch(left), mismatch(right)
    else:
        raise RuntimeError("failed to energy-match the local perturbation")
    perturbed = base + nu_proxy * primary_direction + adjustment * adjust_direction
    return perturbed, adjustment


@dataclass(frozen=True)
class LocalPassageSample:
    nu_proxy: float
    sign: int
    passage_time_xi: float
    oriented_phase_change: float
    initial_adjustment: float
    event_residual: float
    base_energy_abs_max: float
    perturbed_energy_abs_max: float
    energy_difference_drift: float
    integration_steps: int


@dataclass(frozen=True)
class LocalPassageReport:
    r: float
    a2: float
    epsilon: float
    alpha: float
    beta: float
    incoming_stable_radius: float
    outgoing_difference_radius: float
    eigenframe_condition_number: float
    expected_time_slope: float
    expected_phase_slope: float
    fitted_time_slopes: dict[str, float]
    fitted_phase_slopes: dict[str, float]
    samples: tuple[LocalPassageSample, ...]
    evidence_status: str = PROXY_EVIDENCE
    scope_note: str = (
        "Paired-orbit experiment around the numerical homoclinic using a raw "
        "linear eigen-coordinate amplitude nu_proxy.  It tests the leading "
        "time/phase slopes only; nu_proxy is not the exact V2 action coordinate."
    )

    def as_json_dict(self) -> dict[str, Any]:
        return json_ready(self)

    def as_npz_payload(self) -> dict[str, Array]:
        return local_passage_npz_payload(self)


def local_passage_log_law(
    result: HomoclinicResult,
    nu_magnitudes: Sequence[float],
    *,
    signs: Sequence[int] = (-1, 1),
    incoming_stable_radius: float = 0.06,
    outgoing_difference_radius: float = 0.015,
    rtol: float = 3.0e-10,
    atol: float = 3.0e-12,
    max_step: float = 0.04,
) -> LocalPassageReport:
    """Measure leading saddle-focus time/phase log laws with paired trajectories.

    The base trajectory starts on the numerical stable half-homoclinic.  A
    small energy-matched perturbation is applied in the linear unstable plane,
    and base and perturbed trajectories are integrated together until their
    unstable-coordinate separation reaches a fixed radius.  This is a useful
    floating-point proxy, not the exact local-passage chart from Theorem V2.
    """

    if result.model != "vdp":
        raise ValueError("local_passage_log_law expects a van der Pol homoclinic")
    magnitudes = np.asarray(nu_magnitudes, dtype=np.float64)
    if magnitudes.ndim != 1 or magnitudes.size < 2 or np.any(magnitudes <= 0.0):
        raise ValueError("nu_magnitudes must contain at least two positive values")
    sign_values = tuple(int(sign) for sign in signs)
    if not sign_values or any(sign not in (-1, 1) for sign in sign_values):
        raise ValueError("signs must be a nonempty subset of {-1, 1}")
    if outgoing_difference_radius <= float(np.max(magnitudes)):
        raise ValueError("outgoing_difference_radius must exceed every nu magnitude")

    r, a2, epsilon = result.r, result.a2, result.epsilon
    spectrum = saddle_focus_spectrum(r, a2, epsilon)
    if not spectrum.is_saddle_focus:
        raise ValueError("parameters are outside the saddle-focus regime")
    frame, inverse_frame, frame_condition = _complex_eigenframe(r, a2, epsilon)
    _entry_time, base_initial = _find_stable_section_point(
        result, inverse_frame, incoming_stable_radius
    )
    unstable_frame = frame[:, :2]
    minimum_nu = float(np.min(magnitudes))
    maximum_time = max(
        8.0,
        (-np.log(minimum_nu / outgoing_difference_radius) + 6.0)
        / spectrum.alpha,
    )
    samples: list[LocalPassageSample] = []

    for sign in sign_values:
        for magnitude in sorted(float(value) for value in magnitudes)[::-1]:
            nu_proxy = sign * magnitude
            perturbed_initial, adjustment = _energy_matched_perturbation(
                base_initial,
                nu_proxy,
                unstable_frame,
                r,
                a2,
                epsilon,
            )

            def pair_field(time: float, pair: Array) -> Array:
                return np.concatenate(
                    (
                        vdp_field_point(
                            time, pair[:4], r=r, a2=a2, epsilon=epsilon
                        ),
                        vdp_field_point(
                            time, pair[4:], r=r, a2=a2, epsilon=epsilon
                        ),
                    )
                )

            def separation_event(_time: float, pair: Array) -> float:
                difference_coordinates = inverse_frame[:2, :] @ (
                    pair[4:] - pair[:4]
                )
                return float(np.linalg.norm(difference_coordinates)) - outgoing_difference_radius

            separation_event.direction = 1
            separation_event.terminal = True
            integration = solve_ivp(
                pair_field,
                (0.0, maximum_time),
                np.concatenate((base_initial, perturbed_initial)),
                method="DOP853",
                rtol=rtol,
                atol=atol,
                max_step=max_step,
                events=separation_event,
            )
            if not integration.success or integration.t_events[0].size != 1:
                raise RuntimeError(
                    f"local passage proxy did not reach its outgoing section for nu={nu_proxy:g}"
                )
            event_time = float(integration.t_events[0][0])
            differences = integration.y[4:, :] - integration.y[:4, :]
            unstable_coordinates = inverse_frame[:2, :] @ differences
            phase = np.unwrap(
                np.arctan2(unstable_coordinates[1], unstable_coordinates[0])
            )
            phase_change = float(phase[-1] - phase[0])
            base_energy = vdp_hamiltonian(integration.y[:4, :], r, a2, epsilon)
            perturbed_energy = vdp_hamiltonian(
                integration.y[4:, :], r, a2, epsilon
            )
            energy_difference = perturbed_energy - base_energy
            final_pair = integration.y_events[0][0]
            final_radius = float(
                np.linalg.norm(
                    inverse_frame[:2, :] @ (final_pair[4:] - final_pair[:4])
                )
            )
            samples.append(
                LocalPassageSample(
                    nu_proxy=nu_proxy,
                    sign=sign,
                    passage_time_xi=event_time,
                    oriented_phase_change=phase_change,
                    initial_adjustment=float(adjustment),
                    event_residual=abs(final_radius - outgoing_difference_radius),
                    base_energy_abs_max=float(np.max(np.abs(base_energy))),
                    perturbed_energy_abs_max=float(
                        np.max(np.abs(perturbed_energy))
                    ),
                    energy_difference_drift=float(np.ptp(energy_difference)),
                    integration_steps=int(integration.t.size),
                )
            )

    fitted_time: dict[str, float] = {}
    fitted_phase: dict[str, float] = {}
    for sign in sign_values:
        selected = [sample for sample in samples if sample.sign == sign]
        log_nu = np.log(np.abs([sample.nu_proxy for sample in selected]))
        fitted_time[str(sign)] = float(
            np.polyfit(log_nu, [sample.passage_time_xi for sample in selected], 1)[0]
        )
        fitted_phase[str(sign)] = float(
            np.polyfit(
                log_nu,
                [sample.oriented_phase_change for sample in selected],
                1,
            )[0]
        )
    return LocalPassageReport(
        r=r,
        a2=a2,
        epsilon=epsilon,
        alpha=spectrum.alpha,
        beta=spectrum.beta,
        incoming_stable_radius=float(incoming_stable_radius),
        outgoing_difference_radius=float(outgoing_difference_radius),
        eigenframe_condition_number=frame_condition,
        expected_time_slope=-1.0 / spectrum.alpha,
        expected_phase_slope=spectrum.beta / spectrum.alpha,
        fitted_time_slopes=fitted_time,
        fitted_phase_slopes=fitted_phase,
        samples=tuple(samples),
    )


def local_passage_npz_payload(report: LocalPassageReport) -> dict[str, Array]:
    samples = report.samples
    return {
        "nu_proxy": np.array([sample.nu_proxy for sample in samples]),
        "sign": np.array([sample.sign for sample in samples], dtype=np.int64),
        "passage_time_xi": np.array(
            [sample.passage_time_xi for sample in samples]
        ),
        "oriented_phase_change": np.array(
            [sample.oriented_phase_change for sample in samples]
        ),
        "initial_adjustment": np.array(
            [sample.initial_adjustment for sample in samples]
        ),
        "event_residual": np.array([sample.event_residual for sample in samples]),
        "base_energy_abs_max": np.array(
            [sample.base_energy_abs_max for sample in samples]
        ),
        "perturbed_energy_abs_max": np.array(
            [sample.perturbed_energy_abs_max for sample in samples]
        ),
        "energy_difference_drift": np.array(
            [sample.energy_difference_drift for sample in samples]
        ),
    }


@dataclass(frozen=True)
class AffineEventProxy:
    """User-defined affine event surface, never a certified V2 event face."""

    label: str
    normal: tuple[float, float, float, float]
    offset: float
    direction: int = 0

    def __post_init__(self) -> None:
        if not self.label:
            raise ValueError("event label must be nonempty")
        if len(self.normal) != 4 or np.linalg.norm(self.normal) == 0.0:
            raise ValueError("event normal must be a nonzero four-vector")
        if self.direction not in (-1, 0, 1):
            raise ValueError("event direction must be -1, 0, or 1")


@dataclass(frozen=True)
class FiniteEventProxyResult:
    r: float
    a2: float
    epsilon: float
    selected_label: str | None
    hit_time_xi: float | None
    hit_state: tuple[float, ...] | None
    hit_speed: float | None
    competing_time_gap: float | None
    first_hit_times: dict[str, float | None]
    evidence_status: str = PROXY_EVIDENCE
    scope_note: str = (
        "First hit of user-supplied affine proxy surfaces only.  The labels are "
        "not the V2 clean event faces, not a complete gate atlas, and not pole "
        "or algebraic end certification."
    )

    def as_json_dict(self) -> dict[str, Any]:
        return json_ready(self)

    def as_npz_payload(self) -> dict[str, Array]:
        state = (
            np.full(4, np.nan)
            if self.hit_state is None
            else np.asarray(self.hit_state, dtype=np.float64)
        )
        return {
            "hit_time_xi": np.array(
                np.nan if self.hit_time_xi is None else self.hit_time_xi
            ),
            "hit_state": state,
            "hit_speed": np.array(
                np.nan if self.hit_speed is None else self.hit_speed
            ),
            "competing_time_gap": np.array(
                np.nan
                if self.competing_time_gap is None
                else self.competing_time_gap
            ),
        }


def trace_affine_event_proxies(
    initial_state: Sequence[float],
    events: Sequence[AffineEventProxy],
    *,
    r: float,
    a2: float = 0.0,
    epsilon: float = 1.0,
    maximum_time: float = 20.0,
    minimum_time: float = 1.0e-8,
    rtol: float = 2.0e-10,
    atol: float = 2.0e-12,
    max_step: float = 0.03,
) -> FiniteEventProxyResult:
    """Trace the first hit among explicitly user-defined affine proxy faces."""

    if not events:
        raise ValueError("at least one proxy event is required")
    initial = np.asarray(initial_state, dtype=np.float64)
    if initial.shape != (4,):
        raise ValueError("initial_state must be a four-vector")

    event_functions = []
    for specification in events:
        normal = np.asarray(specification.normal, dtype=np.float64)
        offset = float(specification.offset)

        def event_function(
            _time: float,
            state: Array,
            normal: Array = normal,
            offset: float = offset,
        ) -> float:
            return float(np.dot(normal, state) - offset)

        event_function.direction = specification.direction
        event_function.terminal = False
        event_functions.append(event_function)

    integration = solve_ivp(
        lambda time, state: vdp_field_point(
            time, state, r=r, a2=a2, epsilon=epsilon
        ),
        (0.0, maximum_time),
        initial,
        method="DOP853",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
        events=event_functions,
        dense_output=True,
    )
    if not integration.success:
        raise RuntimeError(integration.message)

    candidates: list[tuple[float, int]] = []
    first_hit_times: dict[str, float | None] = {}
    for index, (specification, times) in enumerate(zip(events, integration.t_events)):
        eligible = [float(time) for time in times if time >= minimum_time]
        first = min(eligible) if eligible else None
        first_hit_times[specification.label] = first
        if first is not None:
            candidates.append((first, index))
    candidates.sort()
    if not candidates:
        return FiniteEventProxyResult(
            r=float(r),
            a2=float(a2),
            epsilon=float(epsilon),
            selected_label=None,
            hit_time_xi=None,
            hit_state=None,
            hit_speed=None,
            competing_time_gap=None,
            first_hit_times=first_hit_times,
        )

    hit_time, event_index = candidates[0]
    specification = events[event_index]
    hit_state = np.asarray(integration.sol(hit_time), dtype=np.float64)
    field = vdp_field_point(
        hit_time, hit_state, r=r, a2=a2, epsilon=epsilon
    )
    speed = abs(float(np.dot(np.asarray(specification.normal), field)))
    gap = candidates[1][0] - hit_time if len(candidates) > 1 else None
    return FiniteEventProxyResult(
        r=float(r),
        a2=float(a2),
        epsilon=float(epsilon),
        selected_label=specification.label,
        hit_time_xi=hit_time,
        hit_state=tuple(float(item) for item in hit_state),
        hit_speed=speed,
        competing_time_gap=None if gap is None else float(gap),
        first_hit_times=first_hit_times,
    )


__all__ = [
    "AffineEventProxy",
    "FiniteEventProxyResult",
    "HomoclinicContinuation",
    "HomoclinicSliceReport",
    "HomoclinicSliceSample",
    "LocalPassageReport",
    "LocalPassageSample",
    "SaddleFocusSpectrum",
    "SymbolicCheckReport",
    "TransversalityProxy",
    "compute_homoclinic_continuation",
    "homoclinic_npz_payload",
    "json_ready",
    "local_passage_log_law",
    "local_passage_npz_payload",
    "saddle_focus_spectrum",
    "symbolic_hamiltonian_checks",
    "trace_affine_event_proxies",
    "transversality_proxy",
    "vdp_energy_gradient",
    "vdp_jacobian",
]
