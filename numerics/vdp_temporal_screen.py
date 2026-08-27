r"""Candidate-only temporal screening of the saved van der Pol multipulses.

The analytic V1--V7 results construct *stationary spatial* profiles.  This
module asks a deliberately separate numerical question: what do finite-window
linear spectra and short-time perturbation evolutions look like for the saved
physical profiles in ``v7_multipulses.npz``?

The physical time-dependent PDE is

.. math::

   u_t = v - (u^3/3-u) + r^4 u_{xx},\qquad
   v_t = \epsilon(a-u) + v_{xx}.

Every result here is ``COMPUTED/E1`` and ``CANDIDATE_ONLY``.  In particular,
finite-window eigenvalues and short trajectories are neither a nonlinear
stability proof nor evidence of dynamical pattern selection.  The boundary
condition is imposed on perturbations, not on the saved stationary profile.
To avoid turning the small collocation/interpolation residual of that profile
into artificial time drift, the nonlinear simulation evolves the residual-
subtracted frozen-profile perturbation equations.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Literal, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import eig, eigvals
from scipy.optimize import linear_sum_assignment
from scipy.sparse import bmat, csc_matrix, diags, eye
from scipy.sparse.linalg import eigs, factorized


Array = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]
BoundaryCondition = Literal["neumann", "periodic"]

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MULTIPULSE_ARCHIVE = (
    ROOT / "numerics" / "results" / "vdp_v1_v7" / "v7_multipulses.npz"
)

EVIDENCE_STATUS = "COMPUTED/E1 CANDIDATE_ONLY finite-window temporal screen"
NONCLAIMS = (
    "A finite-window spectrum is not a whole-line spectral-stability theorem.",
    "A short residual-subtracted perturbation evolution is not nonlinear stability.",
    "No observed growth or decay establishes Turing-branch selection or time-asymptotic pattern selection.",
    "No interval arithmetic, Evans-function enclosure, semigroup estimate, or nonlinear bootstrap is performed.",
)


def cubic_f(value: Array | float) -> Array:
    """The physical van der Pol cubic ``f(u)=u^3/3-u``."""

    array = np.asarray(value, dtype=float)
    return array**3 / 3.0 - array


@dataclass(frozen=True)
class TemporalParameters:
    """Physical PDE parameters in the repository's positive-parameter scale."""

    r: float = 0.08
    a2: float = 0.0
    epsilon: float = 1.0

    def __post_init__(self) -> None:
        if not np.isfinite(self.r) or self.r <= 0.0:
            raise ValueError("r must be finite and positive")
        if not np.isfinite(self.epsilon) or self.epsilon <= 0.0:
            raise ValueError("epsilon must be finite and positive")
        if not np.isfinite(self.a2):
            raise ValueError("a2 must be finite")

    @property
    def diffusion_u(self) -> float:
        return float(self.r**4)

    @property
    def a(self) -> float:
        return float(1.0 + np.sqrt(self.epsilon) * self.r**3 * self.a2)

    @property
    def equilibrium_v(self) -> float:
        return float(cubic_f(self.a))

    def as_record(self) -> dict[str, float]:
        return {
            "r": self.r,
            "a2": self.a2,
            "epsilon": self.epsilon,
            "a": self.a,
            "d": self.diffusion_u,
            "equilibrium_u": self.a,
            "equilibrium_v": self.equilibrium_v,
        }


@dataclass(frozen=True)
class PhysicalProfile:
    """One full, symmetric physical multipulse profile from the V7 archive."""

    pulse_count: int
    x: Array
    u: Array
    v: Array

    def __post_init__(self) -> None:
        x = np.asarray(self.x, dtype=float)
        u = np.asarray(self.u, dtype=float)
        v = np.asarray(self.v, dtype=float)
        if self.pulse_count < 1:
            raise ValueError("pulse_count must be positive")
        if x.ndim != 1 or u.shape != x.shape or v.shape != x.shape:
            raise ValueError("x, u, and v must be one-dimensional arrays of equal size")
        if x.size < 5 or not np.all(np.diff(x) > 0.0):
            raise ValueError("profile x grid must contain at least five increasing points")
        if not np.all(np.isfinite(x)) or not np.all(np.isfinite(u)) or not np.all(np.isfinite(v)):
            raise ValueError("profile arrays must be finite")

    @property
    def name(self) -> str:
        return f"pulse_{self.pulse_count}"

    @property
    def interval(self) -> tuple[float, float]:
        return float(self.x[0]), float(self.x[-1])


@dataclass(frozen=True)
class SpatialDiscretization:
    """Cell-centred finite-volume Laplacian on a frozen interval."""

    boundary_condition: BoundaryCondition
    x: Array
    dx: float
    laplacian: csc_matrix


@dataclass(frozen=True)
class SpectrumResult:
    """Full finite-dimensional spectrum and its leading subset."""

    boundary_condition: BoundaryCondition
    grid_points: int
    interval: tuple[float, float]
    dx: float
    eigenvalues: ComplexArray
    leading_eigenvalues: ComplexArray
    spectral_abscissa: float
    unstable_eigenvalue_count: int
    near_neutral_eigenvalue_count: int

    def as_record(self) -> dict[str, Any]:
        return {
            "evidence_status": EVIDENCE_STATUS,
            "boundary_condition_on_perturbations": self.boundary_condition,
            "frozen_interval": list(self.interval),
            "grid_points": self.grid_points,
            "cell_width": self.dx,
            "spectral_abscissa": self.spectral_abscissa,
            "unstable_eigenvalue_count_real_part_gt_1e-8": self.unstable_eigenvalue_count,
            "near_neutral_eigenvalue_count_abs_real_part_le_1e-8": self.near_neutral_eigenvalue_count,
            "leading_eigenvalues": [_complex_record(value) for value in self.leading_eigenvalues],
            "interpretation": "finite-window floating-point spectrum only",
        }


@dataclass(frozen=True)
class RealAxisSpectrumResult:
    """High-resolution real-axis candidates from an energy-bounded shift.

    The weighted energy identity bounds every spectral real part by
    ``max(0,max(1-U^2))``.  A real shift just to the right of that bound makes
    shift-invert efficient for the localized real modes seen in the complete
    coarse-grid spectrum.  This is a refinement of those real candidates, not
    an exhaustive computation of the high-resolution complex spectrum.
    """

    boundary_condition: BoundaryCondition
    x: Array
    dx: float
    energy_real_part_upper_bound: float
    shift: float
    candidate_eigenvalues: ComplexArray
    leading_eigenvalue: complex
    leading_eigenpair_residual_l2: float
    leading_u_mode: Array
    leading_v_mode: Array

    @property
    def grid_points(self) -> int:
        return int(self.x.size)

    @property
    def leading_real_axis_candidate(self) -> float:
        return float(np.real(self.leading_eigenvalue))

    def scaled_real_leading_mode(self, amplitude: float) -> tuple[Array, Array]:
        if amplitude <= 0.0 or not np.isfinite(amplitude):
            raise ValueError("amplitude must be finite and positive")
        return amplitude * self.leading_u_mode, amplitude * self.leading_v_mode

    def as_record(self) -> dict[str, Any]:
        return {
            "evidence_status": EVIDENCE_STATUS,
            "boundary_condition_on_perturbations": self.boundary_condition,
            "grid_points": self.grid_points,
            "cell_width": self.dx,
            "weighted_energy_real_part_upper_bound": self.energy_real_part_upper_bound,
            "real_shift": self.shift,
            "leading_real_axis_candidate": _complex_record(self.leading_eigenvalue),
            "leading_eigenpair_residual_l2": self.leading_eigenpair_residual_l2,
            "returned_shift_invert_candidates": [
                _complex_record(value) for value in self.candidate_eigenvalues
            ],
            "search_scope": "high-resolution real-axis refinement anchored by the weighted-energy upper bound",
            "nonclaim": "not an exhaustive high-resolution complex spectrum",
        }


@dataclass(frozen=True)
class EvolutionResult:
    """Short-time residual-subtracted perturbation evolution."""

    boundary_condition: BoundaryCondition
    x: Array
    dt: float
    requested_dt: float
    final_time: float
    initial_rms: float
    final_rms: float
    maximum_rms: float
    amplification: float
    effective_growth_rate: float
    zero_perturbation_defect_inf: float
    sample_times: Array
    sample_rms: Array
    final_u_perturbation: Array
    final_v_perturbation: Array

    def as_record(self) -> dict[str, Any]:
        return {
            "evidence_status": EVIDENCE_STATUS,
            "boundary_condition_on_perturbations": self.boundary_condition,
            "grid_points": int(self.x.size),
            "requested_dt": self.requested_dt,
            "actual_dt": self.dt,
            "final_time": self.final_time,
            "initial_perturbation_rms": self.initial_rms,
            "final_perturbation_rms": self.final_rms,
            "maximum_perturbation_rms": self.maximum_rms,
            "finite_time_amplification": self.amplification,
            "effective_log_growth_rate": self.effective_growth_rate,
            "zero_perturbation_defect_inf": self.zero_perturbation_defect_inf,
            "sample_times": self.sample_times.tolist(),
            "sample_rms": self.sample_rms.tolist(),
            "interpretation": "short residual-subtracted frozen-profile perturbation run only",
        }


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(np.real(value)), "imag": float(np.imag(value))}


def load_multipulse_profiles(
    archive: str | Path = DEFAULT_MULTIPULSE_ARCHIVE,
    *,
    pulse_counts: Iterable[int] | None = None,
) -> list[PhysicalProfile]:
    """Load the physical ``x,u,v`` arrays, never the central proxy alone."""

    path = Path(archive)
    if not path.exists():
        raise FileNotFoundError(f"multipulse archive not found: {path}")
    requested = tuple(range(1, 5) if pulse_counts is None else pulse_counts)
    if not requested or len(set(requested)) != len(requested):
        raise ValueError("pulse_counts must be a nonempty sequence without duplicates")
    profiles: list[PhysicalProfile] = []
    with np.load(path) as data:
        for count in requested:
            if count < 1:
                raise ValueError("pulse counts must be positive")
            stem = f"pulse_{count}_physical_"
            keys = (stem + "x", stem + "u", stem + "v")
            missing = [key for key in keys if key not in data]
            if missing:
                raise KeyError(f"archive is missing physical profile arrays: {missing}")
            profiles.append(
                PhysicalProfile(
                    pulse_count=int(count),
                    x=np.array(data[keys[0]], dtype=float, copy=True),
                    u=np.array(data[keys[1]], dtype=float, copy=True),
                    v=np.array(data[keys[2]], dtype=float, copy=True),
                )
            )
    return profiles


def finite_volume_laplacian(
    interval: tuple[float, float],
    grid_points: int,
    boundary_condition: BoundaryCondition,
) -> SpatialDiscretization:
    """Return a second-order cell-centred Laplacian.

    ``neumann`` uses zero face flux (the boundary diagonal is ``-1`` rather
    than ``-2``); ``periodic`` connects the first and last cells.  Both choices
    therefore act on the same cell-centred grid, making boundary comparisons
    direct.
    """

    left, right = map(float, interval)
    if not np.isfinite(left) or not np.isfinite(right) or right <= left:
        raise ValueError("interval must be finite and increasing")
    if grid_points < 5:
        raise ValueError("grid_points must be at least five")
    if boundary_condition not in ("neumann", "periodic"):
        raise ValueError("boundary_condition must be 'neumann' or 'periodic'")

    dx = (right - left) / grid_points
    x = left + (np.arange(grid_points, dtype=float) + 0.5) * dx
    main = -2.0 * np.ones(grid_points)
    off = np.ones(grid_points - 1)
    matrix = diags((off, main, off), offsets=(-1, 0, 1), format="lil")
    if boundary_condition == "neumann":
        matrix[0, 0] = -1.0
        matrix[-1, -1] = -1.0
    else:
        matrix[0, -1] = 1.0
        matrix[-1, 0] = 1.0
    return SpatialDiscretization(
        boundary_condition=boundary_condition,
        x=x,
        dx=float(dx),
        laplacian=(matrix.tocsc() / dx**2),
    )


def resample_profile(
    profile: PhysicalProfile, discretization: SpatialDiscretization
) -> tuple[Array, Array]:
    """Interpolate the physical profile to a screening grid."""

    x = discretization.x
    if x[0] < profile.x[0] or x[-1] > profile.x[-1]:
        raise ValueError("discretization lies outside the frozen profile interval")
    return np.interp(x, profile.x, profile.u), np.interp(x, profile.x, profile.v)


def analytic_fourier_growth_rates(
    wavenumber: float | Array, parameters: TemporalParameters
) -> ComplexArray:
    """Exact continuum dispersion roots at real Fourier wavenumber ``k``.

    For the homogeneous state ``(a,f(a))`` the modal matrix is

    ``[[-f'(a)-d*k^2, 1], [-epsilon, -k^2]]``.
    """

    k = np.asarray(wavenumber, dtype=float)
    if np.any(~np.isfinite(k)):
        raise ValueError("wavenumber must be finite")
    k2 = k * k
    f_prime = parameters.a**2 - 1.0
    entry_11 = -f_prime - parameters.diffusion_u * k2
    entry_22 = -k2
    trace = entry_11 + entry_22
    determinant = entry_11 * entry_22 + parameters.epsilon
    discriminant = trace.astype(complex) ** 2 - 4.0 * determinant
    root = np.lib.scimath.sqrt(discriminant)
    return np.stack(((trace + root) / 2.0, (trace - root) / 2.0), axis=-1)


def _growth_rates_from_laplacian_eigenvalue(
    laplacian_eigenvalue: Array, parameters: TemporalParameters
) -> ComplexArray:
    rho = np.asarray(laplacian_eigenvalue, dtype=float)
    f_prime = parameters.a**2 - 1.0
    entry_11 = -f_prime + parameters.diffusion_u * rho
    entry_22 = rho
    trace = entry_11 + entry_22
    determinant = entry_11 * entry_22 + parameters.epsilon
    root = np.lib.scimath.sqrt(trace.astype(complex) ** 2 - 4.0 * determinant)
    return np.stack(((trace + root) / 2.0, (trace - root) / 2.0), axis=-1)


def discrete_laplacian_eigenvalues(
    interval_length: float,
    grid_points: int,
    boundary_condition: BoundaryCondition,
) -> Array:
    """Analytic eigenvalues of :func:`finite_volume_laplacian`."""

    if interval_length <= 0.0 or not np.isfinite(interval_length):
        raise ValueError("interval_length must be finite and positive")
    if grid_points < 5:
        raise ValueError("grid_points must be at least five")
    dx = interval_length / grid_points
    modes = np.arange(grid_points, dtype=float)
    if boundary_condition == "neumann":
        angle = np.pi * modes / (2.0 * grid_points)
    elif boundary_condition == "periodic":
        angle = np.pi * modes / grid_points
    else:
        raise ValueError("boundary_condition must be 'neumann' or 'periodic'")
    return -4.0 * np.sin(angle) ** 2 / dx**2


def build_linearized_operator(
    base_u: Array,
    laplacian: csc_matrix,
    parameters: TemporalParameters,
) -> csc_matrix:
    """Linearize the time PDE around a sampled stationary profile."""

    base = np.asarray(base_u, dtype=float)
    if base.ndim != 1 or laplacian.shape != (base.size, base.size):
        raise ValueError("base_u and laplacian dimensions do not agree")
    if not np.all(np.isfinite(base)):
        raise ValueError("base_u must be finite")
    identity = eye(base.size, format="csc")
    f_prime = diags(base * base - 1.0, format="csc")
    return bmat(
        (
            (parameters.diffusion_u * laplacian - f_prime, identity),
            (-parameters.epsilon * identity, laplacian),
        ),
        format="csc",
    )


def _ordered_spectrum(values: ComplexArray) -> ComplexArray:
    return np.asarray(
        sorted(
            np.asarray(values, dtype=complex),
            key=lambda value: (-float(value.real), abs(float(value.imag)), float(value.imag)),
        ),
        dtype=complex,
    )


def finite_window_spectrum(
    profile: PhysicalProfile,
    parameters: TemporalParameters,
    *,
    grid_points: int = 161,
    boundary_condition: BoundaryCondition = "neumann",
    leading_count: int = 12,
) -> SpectrumResult:
    """Compute the dense finite-window spectrum for one physical profile."""

    if leading_count < 1:
        raise ValueError("leading_count must be positive")
    discretization = finite_volume_laplacian(
        profile.interval, grid_points, boundary_condition
    )
    base_u, _base_v = resample_profile(profile, discretization)
    operator = build_linearized_operator(base_u, discretization.laplacian, parameters)
    values = _ordered_spectrum(
        eigvals(operator.toarray(), overwrite_a=True, check_finite=False)
    )
    leading = values[: min(leading_count, values.size)]
    return SpectrumResult(
        boundary_condition=boundary_condition,
        grid_points=grid_points,
        interval=profile.interval,
        dx=discretization.dx,
        eigenvalues=values,
        leading_eigenvalues=leading,
        spectral_abscissa=float(values[0].real),
        unstable_eigenvalue_count=int(np.count_nonzero(values.real > 1.0e-8)),
        near_neutral_eigenvalue_count=int(np.count_nonzero(np.abs(values.real) <= 1.0e-8)),
    )


def refined_real_axis_spectrum(
    profile: PhysicalProfile,
    parameters: TemporalParameters,
    *,
    maximum_cell_width: float = 0.004,
    boundary_condition: BoundaryCondition = "neumann",
    candidate_count: int = 12,
    shift_margin: float = 0.01,
) -> RealAxisSpectrumResult:
    """Refine localized real eigenvalue candidates on a physical-spacing grid.

    The primary resolution control is a physical cell width, rather than a
    fixed point count, so a four-pulse interval does not silently receive four
    times fewer cells per pulse than a one-pulse interval.
    """

    if maximum_cell_width <= 0.0 or not np.isfinite(maximum_cell_width):
        raise ValueError("maximum_cell_width must be finite and positive")
    if candidate_count < 2:
        raise ValueError("candidate_count must be at least two")
    if shift_margin <= 0.0 or not np.isfinite(shift_margin):
        raise ValueError("shift_margin must be finite and positive")
    length = profile.interval[1] - profile.interval[0]
    grid_points = max(17, int(np.ceil(length / maximum_cell_width)))
    discretization = finite_volume_laplacian(
        profile.interval, grid_points, boundary_condition
    )
    base_u, _base_v = resample_profile(profile, discretization)
    operator = build_linearized_operator(base_u, discretization.laplacian, parameters)
    # In the epsilon-weighted norm the off-diagonal reaction coupling is
    # skew, while both diffusion blocks are nonpositive.  Hence this sampled
    # maximum is an upper bound on Re(lambda) for the matrix spectrum.
    real_part_bound = float(max(0.0, np.max(1.0 - base_u * base_u)))
    shift = real_part_bound + shift_margin
    count = min(candidate_count, operator.shape[0] - 2)
    values, vectors = eigs(
        operator,
        k=count,
        sigma=shift,
        which="LM",
        tol=1.0e-10,
        maxiter=10_000,
    )
    order = np.argsort(values.real)[::-1]
    values = np.asarray(values[order], dtype=complex)
    vectors = np.asarray(vectors[:, order], dtype=complex)
    real_indices = np.flatnonzero(np.abs(values.imag) <= 1.0e-7)
    if real_indices.size == 0:
        raise RuntimeError("real-axis refinement returned no resolved real candidate")
    leading_index = int(real_indices[np.argmax(values[real_indices].real)])
    leading_value = complex(values[leading_index])
    vector = vectors[:, leading_index]
    residual = operator @ vector - leading_value * vector
    residual_l2 = float(np.linalg.norm(residual) / np.linalg.norm(vector))
    pivot = int(np.argmax(np.abs(vector)))
    if abs(vector[pivot]) > 0.0:
        vector *= np.exp(-1j * np.angle(vector[pivot]))
    representative = vector.real
    if np.linalg.norm(vector.imag) > np.linalg.norm(representative):
        representative = vector.imag
    u_mode = np.asarray(representative[:grid_points], dtype=float)
    v_mode = np.asarray(representative[grid_points:], dtype=float)
    normalizer = _perturbation_rms(u_mode, v_mode)
    if normalizer <= np.finfo(float).tiny:
        raise RuntimeError("leading eigenvector has no usable real representative")
    return RealAxisSpectrumResult(
        boundary_condition=boundary_condition,
        x=discretization.x,
        dx=discretization.dx,
        energy_real_part_upper_bound=real_part_bound,
        shift=shift,
        candidate_eigenvalues=values,
        leading_eigenvalue=leading_value,
        leading_eigenpair_residual_l2=residual_l2,
        leading_u_mode=u_mode / normalizer,
        leading_v_mode=v_mode / normalizer,
    )


def dominant_linear_mode(
    profile: PhysicalProfile,
    parameters: TemporalParameters,
    *,
    grid_points: int = 161,
    boundary_condition: BoundaryCondition = "neumann",
    amplitude: float = 1.0e-5,
) -> tuple[complex, tuple[Array, Array], float]:
    """Return a real, normalized representative of the leading eigenmode.

    The complex eigenvector is phase-rotated so its largest component is real,
    after which the larger of its real and imaginary representatives is used.
    The returned residual is the relative complex eigenpair residual before
    taking that real representative.
    """

    if amplitude <= 0.0 or not np.isfinite(amplitude):
        raise ValueError("amplitude must be finite and positive")
    discretization = finite_volume_laplacian(
        profile.interval, grid_points, boundary_condition
    )
    base_u, _base_v = resample_profile(profile, discretization)
    operator = build_linearized_operator(base_u, discretization.laplacian, parameters)
    dense_operator = operator.toarray()
    values, vectors = eig(dense_operator, check_finite=False)
    index = int(np.argmax(values.real))
    value = complex(values[index])
    vector = np.asarray(vectors[:, index], dtype=complex)
    pivot = int(np.argmax(np.abs(vector)))
    if abs(vector[pivot]) > 0.0:
        vector *= np.exp(-1j * np.angle(vector[pivot]))
    residual = dense_operator @ vector - value * vector
    relative_residual = float(
        np.linalg.norm(residual)
        / max(np.linalg.norm(dense_operator) * np.linalg.norm(vector), np.finfo(float).tiny)
    )
    representative = vector.real
    if np.linalg.norm(vector.imag) > np.linalg.norm(representative):
        representative = vector.imag
    u_mode = np.asarray(representative[:grid_points], dtype=float)
    v_mode = np.asarray(representative[grid_points:], dtype=float)
    normalizer = _perturbation_rms(u_mode, v_mode)
    if normalizer <= np.finfo(float).tiny:
        raise RuntimeError("leading eigenvector has no usable real representative")
    return (
        value,
        (amplitude * u_mode / normalizer, amplitude * v_mode / normalizer),
        relative_residual,
    )


def homogeneous_fourier_validation(
    parameters: TemporalParameters,
    *,
    interval_length: float = 4.0,
    grid_points: int = 24,
) -> dict[str, Any]:
    """Cross-check matrix spectra against analytic modal growth rates."""

    if grid_points > 96:
        raise ValueError("the dense validation grid is intentionally limited to 96")
    rows: dict[str, Any] = {}
    for boundary in ("neumann", "periodic"):
        discretization = finite_volume_laplacian(
            (0.0, interval_length), grid_points, boundary
        )
        operator = build_linearized_operator(
            np.full(grid_points, parameters.a),
            discretization.laplacian,
            parameters,
        )
        numerical = eigvals(operator.toarray(), check_finite=False)
        rho = discrete_laplacian_eigenvalues(
            interval_length, grid_points, boundary
        )
        expected = _growth_rates_from_laplacian_eigenvalue(rho, parameters).reshape(-1)
        costs = np.abs(numerical[:, None] - expected[None, :])
        row_indices, column_indices = linear_sum_assignment(costs)
        matching_error = float(np.max(costs[row_indices, column_indices]))
        rows[boundary] = {
            "maximum_eigenvalue_matching_error": matching_error,
            "analytic_discrete_spectral_abscissa": float(np.max(expected.real)),
            "matrix_spectral_abscissa": float(np.max(numerical.real)),
        }

    sample_wavenumbers = np.asarray(
        [0.0, np.pi / interval_length, 2.0 * np.pi / interval_length]
    )
    continuum = analytic_fourier_growth_rates(sample_wavenumbers, parameters)
    return {
        "status": "PASS" if max(row["maximum_eigenvalue_matching_error"] for row in rows.values()) < 2.0e-10 else "FAIL",
        "parameters": parameters.as_record(),
        "finite_volume_matrix_vs_analytic_discrete_modes": rows,
        "continuum_fourier_samples": [
            {
                "wavenumber": float(wavenumber),
                "growth_rates": [_complex_record(value) for value in rates],
            }
            for wavenumber, rates in zip(sample_wavenumbers, continuum, strict=True)
        ],
    }


def _perturbation_rms(u_perturbation: Array, v_perturbation: Array) -> float:
    return float(
        np.sqrt(np.mean(u_perturbation * u_perturbation + v_perturbation * v_perturbation))
    )


def deterministic_initial_perturbation(
    x: Array, *, amplitude: float = 1.0e-5
) -> tuple[Array, Array]:
    """A smooth localized perturbation shared by every grid and boundary run."""

    coordinate = np.asarray(x, dtype=float)
    if coordinate.ndim != 1 or coordinate.size < 5 or not np.all(np.diff(coordinate) > 0.0):
        raise ValueError("x must be a one-dimensional increasing grid")
    if amplitude <= 0.0 or not np.isfinite(amplitude):
        raise ValueError("amplitude must be finite and positive")
    center = 0.5 * (coordinate[0] + coordinate[-1])
    length = coordinate[-1] - coordinate[0] + (coordinate[1] - coordinate[0])
    width = 0.16 * length
    envelope = np.exp(-((coordinate - center) / width) ** 2)
    u_perturbation = envelope * (
        1.0 + 0.2 * np.cos(2.0 * np.pi * (coordinate - center) / length)
    )
    v_perturbation = -0.35 * envelope
    normalizer = _perturbation_rms(u_perturbation, v_perturbation)
    return (
        amplitude * u_perturbation / normalizer,
        amplitude * v_perturbation / normalizer,
    )


def evolve_frozen_profile_perturbation(
    profile: PhysicalProfile,
    parameters: TemporalParameters,
    *,
    grid_points: int = 161,
    boundary_condition: BoundaryCondition = "neumann",
    final_time: float = 1.0,
    dt: float = 0.01,
    amplitude: float = 1.0e-5,
    initial_perturbation: tuple[Array, Array] | None = None,
    saved_samples: int = 21,
) -> EvolutionResult:
    """Run a first-order diffusion-implicit perturbation simulation.

    If ``(U,V)`` is the interpolated frozen profile and ``(p,q)`` its
    perturbation, this integrates

    ``p_t = q - (f(U+p)-f(U)) + d*p_xx`` and
    ``q_t = -epsilon*p + q_xx``.

    Thus ``(p,q)=(0,0)`` is preserved independently of the small finite-grid
    residual of ``(U,V)``.  Diffusion is backward Euler and reaction is forward
    Euler (IMEX Euler).
    """

    if final_time <= 0.0 or not np.isfinite(final_time):
        raise ValueError("final_time must be finite and positive")
    if dt <= 0.0 or not np.isfinite(dt):
        raise ValueError("dt must be finite and positive")
    if saved_samples < 2:
        raise ValueError("saved_samples must be at least two")
    discretization = finite_volume_laplacian(
        profile.interval, grid_points, boundary_condition
    )
    base_u, _base_v = resample_profile(profile, discretization)
    if initial_perturbation is None:
        u_perturbation, v_perturbation = deterministic_initial_perturbation(
            discretization.x, amplitude=amplitude
        )
    else:
        u_perturbation = np.asarray(initial_perturbation[0], dtype=float).copy()
        v_perturbation = np.asarray(initial_perturbation[1], dtype=float).copy()
        if u_perturbation.shape != (grid_points,) or v_perturbation.shape != (grid_points,):
            raise ValueError("initial perturbations must match grid_points")

    steps = int(np.ceil(final_time / dt))
    actual_dt = float(final_time / steps)
    identity = eye(grid_points, format="csc")
    solve_u = factorized(
        identity - actual_dt * parameters.diffusion_u * discretization.laplacian
    )
    solve_v = factorized(identity - actual_dt * discretization.laplacian)

    # This explicit zero-state check documents the residual-subtraction
    # invariant with the actual factorisations used by the run.
    zero_u = solve_u(np.zeros(grid_points))
    zero_v = solve_v(np.zeros(grid_points))
    zero_defect = float(max(np.max(np.abs(zero_u)), np.max(np.abs(zero_v))))

    initial_rms = _perturbation_rms(u_perturbation, v_perturbation)
    save_steps = np.unique(
        np.rint(np.linspace(0, steps, min(saved_samples, steps + 1))).astype(int)
    )
    sample_times: list[float] = [0.0]
    sample_norms: list[float] = [initial_rms]
    maximum_rms = initial_rms
    next_save_index = 1

    for step in range(1, steps + 1):
        nonlinear_increment = cubic_f(base_u + u_perturbation) - cubic_f(base_u)
        old_u = u_perturbation
        old_v = v_perturbation
        u_perturbation = solve_u(
            old_u + actual_dt * (old_v - nonlinear_increment)
        )
        v_perturbation = solve_v(
            old_v - actual_dt * parameters.epsilon * old_u
        )
        current_rms = _perturbation_rms(u_perturbation, v_perturbation)
        maximum_rms = max(maximum_rms, current_rms)
        if next_save_index < save_steps.size and step == save_steps[next_save_index]:
            sample_times.append(step * actual_dt)
            sample_norms.append(current_rms)
            next_save_index += 1

    final_rms = _perturbation_rms(u_perturbation, v_perturbation)
    amplification = float(final_rms / initial_rms) if initial_rms > 0.0 else 1.0
    effective_growth = float(np.log(amplification) / final_time) if amplification > 0.0 else float("-inf")
    return EvolutionResult(
        boundary_condition=boundary_condition,
        x=discretization.x,
        dt=actual_dt,
        requested_dt=float(dt),
        final_time=float(final_time),
        initial_rms=initial_rms,
        final_rms=final_rms,
        maximum_rms=maximum_rms,
        amplification=amplification,
        effective_growth_rate=effective_growth,
        zero_perturbation_defect_inf=zero_defect,
        sample_times=np.asarray(sample_times),
        sample_rms=np.asarray(sample_norms),
        final_u_perturbation=np.asarray(u_perturbation),
        final_v_perturbation=np.asarray(v_perturbation),
    )


def _normalized_state_difference(
    reference: EvolutionResult,
    comparison: EvolutionResult,
) -> float:
    if reference.boundary_condition != comparison.boundary_condition and reference.x.shape != comparison.x.shape:
        raise ValueError("different-boundary comparisons require the same grid")
    comparison_u = np.interp(
        reference.x, comparison.x, comparison.final_u_perturbation
    )
    comparison_v = np.interp(
        reference.x, comparison.x, comparison.final_v_perturbation
    )
    difference = _perturbation_rms(
        reference.final_u_perturbation - comparison_u,
        reference.final_v_perturbation - comparison_v,
    )
    return float(difference / reference.initial_rms)


def profile_tail_diagnostics(
    profile: PhysicalProfile, parameters: TemporalParameters
) -> dict[str, float]:
    """Quantify why both tail Neumann and periodic screens are worth comparing."""

    dx_left = profile.x[1] - profile.x[0]
    dx_right = profile.x[-1] - profile.x[-2]
    return {
        "left_u_minus_equilibrium": float(profile.u[0] - parameters.a),
        "right_u_minus_equilibrium": float(profile.u[-1] - parameters.a),
        "left_v_minus_equilibrium": float(profile.v[0] - parameters.equilibrium_v),
        "right_v_minus_equilibrium": float(profile.v[-1] - parameters.equilibrium_v),
        "periodic_endpoint_u_gap": float(profile.u[-1] - profile.u[0]),
        "periodic_endpoint_v_gap": float(profile.v[-1] - profile.v[0]),
        "left_one_sided_u_slope": float((profile.u[1] - profile.u[0]) / dx_left),
        "right_one_sided_u_slope": float((profile.u[-1] - profile.u[-2]) / dx_right),
        "left_one_sided_v_slope": float((profile.v[1] - profile.v[0]) / dx_left),
        "right_one_sided_v_slope": float((profile.v[-1] - profile.v[-2]) / dx_right),
    }


def _screen_signal(*spectral_abscissae: float) -> str:
    values = np.asarray(spectral_abscissae, dtype=float)
    if np.all(values > 1.0e-6):
        return "POSITIVE_GROWTH_CANDIDATE_ACROSS_GRID_AND_BOUNDARY_CHECKS"
    if np.all(values < -1.0e-6):
        return "NEGATIVE_GROWTH_CANDIDATE_ACROSS_GRID_AND_BOUNDARY_CHECKS"
    return "INCONCLUSIVE_OR_GRID_BOUNDARY_SENSITIVE"


def screen_profile(
    profile: PhysicalProfile,
    parameters: TemporalParameters,
    *,
    grid_points: int = 161,
    coarse_grid_points: int = 121,
    final_time: float = 1.0,
    dt: float = 0.01,
    amplitude: float = 1.0e-5,
    leading_count: int = 12,
    refined_maximum_cell_width: float = 0.004,
    coarse_refined_maximum_cell_width: float = 0.008,
) -> dict[str, Any]:
    """Run spectrum, time-step, grid, and boundary screens for one profile."""

    if coarse_grid_points >= grid_points:
        raise ValueError("coarse_grid_points must be smaller than grid_points")
    if coarse_refined_maximum_cell_width <= refined_maximum_cell_width:
        raise ValueError(
            "coarse_refined_maximum_cell_width must exceed refined_maximum_cell_width"
        )
    spectra = {
        "fine_neumann": finite_window_spectrum(
            profile,
            parameters,
            grid_points=grid_points,
            boundary_condition="neumann",
            leading_count=leading_count,
        ),
        "fine_periodic": finite_window_spectrum(
            profile,
            parameters,
            grid_points=grid_points,
            boundary_condition="periodic",
            leading_count=leading_count,
        ),
        "coarse_neumann": finite_window_spectrum(
            profile,
            parameters,
            grid_points=coarse_grid_points,
            boundary_condition="neumann",
            leading_count=leading_count,
        ),
    }

    refined_spectra = {
        "fine_neumann": refined_real_axis_spectrum(
            profile,
            parameters,
            maximum_cell_width=refined_maximum_cell_width,
            boundary_condition="neumann",
            candidate_count=leading_count,
        ),
        "fine_periodic": refined_real_axis_spectrum(
            profile,
            parameters,
            maximum_cell_width=refined_maximum_cell_width,
            boundary_condition="periodic",
            candidate_count=leading_count,
        ),
        "coarse_neumann": refined_real_axis_spectrum(
            profile,
            parameters,
            maximum_cell_width=coarse_refined_maximum_cell_width,
            boundary_condition="neumann",
            candidate_count=leading_count,
        ),
    }

    fine_points = refined_spectra["fine_neumann"].grid_points
    coarse_points = refined_spectra["coarse_neumann"].grid_points

    fine_dt = evolve_frozen_profile_perturbation(
        profile,
        parameters,
        grid_points=fine_points,
        boundary_condition="neumann",
        final_time=final_time,
        dt=dt,
        amplitude=amplitude,
    )
    fine_half_dt = evolve_frozen_profile_perturbation(
        profile,
        parameters,
        grid_points=fine_points,
        boundary_condition="neumann",
        final_time=final_time,
        dt=0.5 * dt,
        amplitude=amplitude,
    )
    periodic_half_dt = evolve_frozen_profile_perturbation(
        profile,
        parameters,
        grid_points=fine_points,
        boundary_condition="periodic",
        final_time=final_time,
        dt=0.5 * dt,
        amplitude=amplitude,
    )
    coarse_half_dt = evolve_frozen_profile_perturbation(
        profile,
        parameters,
        grid_points=coarse_points,
        boundary_condition="neumann",
        final_time=final_time,
        dt=0.5 * dt,
        amplitude=amplitude,
    )
    leading_value = refined_spectra["fine_neumann"].leading_eigenvalue
    leading_initial = refined_spectra["fine_neumann"].scaled_real_leading_mode(
        amplitude
    )
    leading_residual = refined_spectra[
        "fine_neumann"
    ].leading_eigenpair_residual_l2
    leading_mode_run = evolve_frozen_profile_perturbation(
        profile,
        parameters,
        grid_points=fine_points,
        boundary_condition="neumann",
        final_time=final_time,
        dt=0.5 * dt,
        amplitude=amplitude,
        initial_perturbation=leading_initial,
    )

    spectral_abscissae = [
        refined_spectra["fine_neumann"].leading_real_axis_candidate,
        refined_spectra["fine_periodic"].leading_real_axis_candidate,
        refined_spectra["coarse_neumann"].leading_real_axis_candidate,
    ]
    sensitivities = {
        "spectral_grid_abscissa_difference": float(
            abs(
                refined_spectra["fine_neumann"].leading_real_axis_candidate
                - refined_spectra["coarse_neumann"].leading_real_axis_candidate
            )
        ),
        "spectral_boundary_abscissa_difference": float(
            abs(
                refined_spectra["fine_neumann"].leading_real_axis_candidate
                - refined_spectra["fine_periodic"].leading_real_axis_candidate
            )
        ),
        "full_spectrum_audit_grid_abscissa_difference": float(
            abs(
                spectra["fine_neumann"].spectral_abscissa
                - spectra["coarse_neumann"].spectral_abscissa
            )
        ),
        "full_spectrum_audit_boundary_abscissa_difference": float(
            abs(
                spectra["fine_neumann"].spectral_abscissa
                - spectra["fine_periodic"].spectral_abscissa
            )
        ),
        "time_step_final_state_difference_over_initial_rms": _normalized_state_difference(
            fine_half_dt, fine_dt
        ),
        "grid_final_state_difference_over_initial_rms": _normalized_state_difference(
            coarse_half_dt, fine_half_dt
        ),
        "boundary_final_state_difference_over_initial_rms": _normalized_state_difference(
            fine_half_dt, periodic_half_dt
        ),
        "leading_mode_expected_linear_envelope_amplification": float(
            np.exp(leading_value.real * final_time)
        ),
        "leading_mode_observed_nonlinear_amplification": leading_mode_run.amplification,
        "leading_mode_complex_eigenpair_relative_residual": leading_residual,
        "spectral_sign_agrees_across_checks": bool(
            np.all(np.asarray(spectral_abscissae) > 0.0)
            or np.all(np.asarray(spectral_abscissae) < 0.0)
        ),
    }

    return {
        "evidence_status": EVIDENCE_STATUS,
        "claim_bearing": False,
        "profile": profile.name,
        "pulse_count": profile.pulse_count,
        "frozen_physical_interval": list(profile.interval),
        "source_archive_arrays": [
            f"{profile.name}_physical_x",
            f"{profile.name}_physical_u",
            f"{profile.name}_physical_v",
        ],
        "tail_diagnostics": profile_tail_diagnostics(profile, parameters),
        "linear_spectra": {name: result.as_record() for name, result in spectra.items()},
        "refined_real_axis_spectra": {
            name: result.as_record() for name, result in refined_spectra.items()
        },
        "short_time_runs": {
            "fine_neumann_dt": fine_dt.as_record(),
            "fine_neumann_half_dt": fine_half_dt.as_record(),
            "fine_periodic_half_dt": periodic_half_dt.as_record(),
            "coarse_neumann_half_dt": coarse_half_dt.as_record(),
            "fine_neumann_leading_mode_half_dt": {
                **leading_mode_run.as_record(),
                "initial_mode_eigenvalue": _complex_record(leading_value),
                "complex_eigenpair_relative_residual": leading_residual,
                "expected_linear_envelope_amplification": float(
                    np.exp(leading_value.real * final_time)
                ),
            },
        },
        "sensitivity": sensitivities,
        "screen_signal": _screen_signal(*spectral_abscissae),
        "nonclaim": "This signal prioritizes later analysis; it is not a temporal-stability conclusion.",
    }


def run_temporal_prescreen(
    archive: str | Path = DEFAULT_MULTIPULSE_ARCHIVE,
    *,
    parameters: TemporalParameters = TemporalParameters(),
    pulse_counts: Sequence[int] = (1, 2, 3, 4),
    grid_points: int = 161,
    coarse_grid_points: int = 121,
    final_time: float = 1.0,
    dt: float = 0.01,
    amplitude: float = 1.0e-5,
    leading_count: int = 12,
    refined_maximum_cell_width: float = 0.004,
    coarse_refined_maximum_cell_width: float = 0.008,
) -> dict[str, Any]:
    """Return a JSON-ready pre-screen record without writing repository results."""

    archive_path = Path(archive).resolve()
    profiles = load_multipulse_profiles(archive_path, pulse_counts=pulse_counts)
    screens = [
        screen_profile(
            profile,
            parameters,
            grid_points=grid_points,
            coarse_grid_points=coarse_grid_points,
            final_time=final_time,
            dt=dt,
            amplitude=amplitude,
            leading_count=leading_count,
            refined_maximum_cell_width=refined_maximum_cell_width,
            coarse_refined_maximum_cell_width=coarse_refined_maximum_cell_width,
        )
        for profile in profiles
    ]
    return {
        "evidence_status": EVIDENCE_STATUS,
        "claim_bearing": False,
        "final_status": "TEMPORAL_PRESCREEN_ONLY",
        "parameters": parameters.as_record(),
        "source_archive": str(archive_path),
        "profile_count": len(screens),
        "linearization": "physical PDE linearization on the frozen saved profile",
        "boundary_conditions_on_perturbations": ["neumann", "periodic"],
        "space_discretization": "second-order cell-centred finite-volume Laplacian",
        "time_discretization": "first-order diffusion-implicit/reaction-explicit IMEX Euler",
        "base_residual_treatment": "subtract the frozen profile residual so zero perturbation is invariant",
        "homogeneous_fourier_validation": homogeneous_fourier_validation(parameters),
        "profiles": screens,
        "nonclaims": list(NONCLAIMS),
    }


def _parse_pulse_counts(text: str) -> tuple[int, ...]:
    try:
        values = tuple(int(item.strip()) for item in text.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("pulse counts must be comma-separated integers") from exc
    if not values or any(value < 1 for value in values) or len(set(values)) != len(values):
        raise argparse.ArgumentTypeError("pulse counts must be distinct positive integers")
    return values


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_MULTIPULSE_ARCHIVE)
    parser.add_argument("--pulse-counts", type=_parse_pulse_counts, default=(1, 2, 3, 4))
    parser.add_argument("--grid-points", type=int, default=161)
    parser.add_argument("--coarse-grid-points", type=int, default=121)
    parser.add_argument("--final-time", type=float, default=1.0)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--amplitude", type=float, default=1.0e-5)
    parser.add_argument("--leading-count", type=int, default=12)
    parser.add_argument("--refined-maximum-cell-width", type=float, default=0.004)
    parser.add_argument("--coarse-refined-maximum-cell-width", type=float, default=0.008)
    arguments = parser.parse_args(argv)
    report = run_temporal_prescreen(
        arguments.archive,
        pulse_counts=arguments.pulse_counts,
        grid_points=arguments.grid_points,
        coarse_grid_points=arguments.coarse_grid_points,
        final_time=arguments.final_time,
        dt=arguments.dt,
        amplitude=arguments.amplitude,
        leading_count=arguments.leading_count,
        refined_maximum_cell_width=arguments.refined_maximum_cell_width,
        coarse_refined_maximum_cell_width=arguments.coarse_refined_maximum_cell_width,
    )
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
