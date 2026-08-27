"""Non-rigorous Bloch spectral screening of the computed V7 profiles.

For a physical stationary profile ``(u_*(x), v_*(x))`` of period ``L``, the
temporal linearization of

    u_t = v - f(u) + d u_xx,
    v_t = epsilon * (a - u) + v_xx,
    f(u) = u**3 / 3 - u,

is sampled with a Fourier--Bloch collocation method.  The Bloch phase
``theta`` is dimensionless and uses the convention

    z(x + L) = exp(1j * theta) z(x),       -pi <= theta <= pi.

Writing ``z = exp(1j * theta * x / L) w`` with periodic ``w`` replaces each
spatial derivative by ``D_theta = d/dx + 1j * theta / L``.  On Fourier mode
``exp(2*pi*1j*k*x/L)``, ``D_theta**2`` therefore has multiplier
``-((2*pi*k + theta)/L)**2``.

All eigenvalues returned here are finite-dimensional floating-point samples.
They can detect an instability on the sampled grid, but absence of a sampled
positive real part is not a proof of spectral or nonlinear stability.  In
particular, this module is not an Evans-function calculation and performs no
outward-rounded interval validation for issue #7.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import CubicSpline
from scipy.linalg import eigvals
from scipy.optimize import linear_sum_assignment


RealArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]

DEFAULT_PROFILE_LABELS = ("A0", "B0", "A1", "B1", "A2")
EVIDENCE_STATUS = "COMPUTED/E1 NONRIGOROUS_FINITE_FOURIER_BLOCH_SCREEN"
SAMPLED_INSTABILITY = "SAMPLED_BLOCH_INSTABILITY_DETECTED"
NO_SAMPLED_INSTABILITY = "NO_SAMPLED_POSITIVE_REAL_PART_DETECTED"
NONCLAIMS = (
    "Finite Fourier collocation is not an interval enclosure of the Bloch spectrum.",
    "A finite Bloch-phase grid cannot prove stability between sampled phases.",
    "No sampled positive real part is not a proof of spectral or nonlinear stability.",
    "A sampled positive real part is numerical instability evidence, not a rigorous theorem.",
    "This screen does not identify a Turing branch or prove dynamical pattern selection.",
)


@dataclass(frozen=True)
class PhysicalPeriodicProfile:
    """A closed physical profile loaded from ``v7_periodic.npz``."""

    label: str
    x: RealArray
    u: RealArray
    v: RealArray

    @property
    def period(self) -> float:
        return float(self.x[-1] - self.x[0])


@dataclass(frozen=True)
class BlochScreeningResult:
    """Machine-readable output of a finite Bloch-grid screening run."""

    labels: tuple[str, ...]
    theta: RealArray
    periods: RealArray
    grid_points: int
    coarse_grid_points: int
    leading_eigenvalues: ComplexArray
    spectral_abscissa: RealArray
    co_periodic_spectral_abscissa: RealArray
    translation_eigenvalues: ComplexArray
    translation_residuals: RealArray
    refinement_theta: RealArray
    refinement_defects: RealArray
    conjugacy_defects: RealArray
    constant_dispersion_defect: float
    d: float
    epsilon: float
    homogeneous_u: float
    instability_tolerance: float

    @property
    def screening_outcomes(self) -> tuple[str, ...]:
        return tuple(
            SAMPLED_INSTABILITY
            if float(np.max(row)) > self.instability_tolerance
            else NO_SAMPLED_INSTABILITY
            for row in self.spectral_abscissa
        )

    @property
    def status(self) -> str:
        return EVIDENCE_STATUS

    @property
    def claim_bearing(self) -> bool:
        return False

    def as_npz_payload(self) -> dict[str, RealArray]:
        """Return arrays without object dtype, ready for ``np.savez``."""

        label_width = max((len(label) for label in self.labels), default=1)
        return {
            "labels": np.asarray(self.labels, dtype=f"<U{label_width}"),
            "theta": self.theta.copy(),
            "periods": self.periods.copy(),
            "leading_eigenvalues_real": self.leading_eigenvalues.real.copy(),
            "leading_eigenvalues_imag": self.leading_eigenvalues.imag.copy(),
            "spectral_abscissa": self.spectral_abscissa.copy(),
            "co_periodic_spectral_abscissa": (
                self.co_periodic_spectral_abscissa.copy()
            ),
            "translation_eigenvalues_real": self.translation_eigenvalues.real.copy(),
            "translation_eigenvalues_imag": self.translation_eigenvalues.imag.copy(),
            "translation_residuals": self.translation_residuals.copy(),
            "refinement_theta": self.refinement_theta.copy(),
            "refinement_defects": self.refinement_defects.copy(),
            "conjugacy_defects": self.conjugacy_defects.copy(),
            "constant_dispersion_defect": np.asarray(
                [self.constant_dispersion_defect], dtype=np.float64
            ),
            "grid_points": np.asarray([self.grid_points], dtype=np.int64),
            "coarse_grid_points": np.asarray(
                [self.coarse_grid_points], dtype=np.int64
            ),
            "d": np.asarray([self.d], dtype=np.float64),
            "epsilon": np.asarray([self.epsilon], dtype=np.float64),
            "homogeneous_u": np.asarray([self.homogeneous_u], dtype=np.float64),
        }

    def as_report(self) -> dict[str, object]:
        """Return a JSON-safe report that preserves the evidence boundary."""

        profiles: list[dict[str, object]] = []
        outcomes = self.screening_outcomes
        for index, label in enumerate(self.labels):
            maximum_index = int(np.argmax(self.spectral_abscissa[index]))
            maximum_theta = float(self.theta[maximum_index])
            nonzero_mask = np.abs(self.theta) > 1.0e-13
            nonzero_maximum = (
                float(np.max(self.spectral_abscissa[index, nonzero_mask]))
                if np.any(nonzero_mask)
                else None
            )
            refinement = self.refinement_defects[index]
            finite_refinement = refinement[np.isfinite(refinement)]
            conjugacy = float(self.conjugacy_defects[index])
            profiles.append(
                {
                    "label": label,
                    "period": float(self.periods[index]),
                    "screening_outcome": outcomes[index],
                    "sampled_max_real_part": float(
                        self.spectral_abscissa[index, maximum_index]
                    ),
                    "theta_at_sampled_max": maximum_theta,
                    "bloch_wavenumber_at_sampled_max": (
                        maximum_theta / float(self.periods[index])
                    ),
                    "floquet_multiplier_at_sampled_max": _complex_record(
                        np.exp(1j * maximum_theta)
                    ),
                    "co_periodic_max_real_part": float(
                        self.co_periodic_spectral_abscissa[index]
                    ),
                    "co_periodic_outcome": (
                        "SAMPLED_COPERIODIC_INSTABILITY_DETECTED"
                        if self.co_periodic_spectral_abscissa[index]
                        > self.instability_tolerance
                        else "NO_SAMPLED_COPERIODIC_INSTABILITY_DETECTED"
                    ),
                    "sampled_nonzero_bloch_max_real_part": nonzero_maximum,
                    "sampled_nonzero_bloch_outcome": (
                        "SAMPLED_NONZERO_BLOCH_INSTABILITY_DETECTED"
                        if nonzero_maximum is not None
                        and nonzero_maximum > self.instability_tolerance
                        else "NO_SAMPLED_NONZERO_BLOCH_INSTABILITY_DETECTED"
                    ),
                    "sideband_stability_status": (
                        "NOT_PROVED; only finitely many Bloch phases were sampled"
                    ),
                    "sampled_positive_phase_count": int(
                        np.count_nonzero(
                            self.spectral_abscissa[index]
                            > self.instability_tolerance
                        )
                    ),
                    "translation_eigenvalue_at_theta_zero": _complex_record(
                        self.translation_eigenvalues[index]
                    ),
                    "translation_eigenvalue_modulus": float(
                        abs(self.translation_eigenvalues[index])
                    ),
                    "translation_vector_relative_residual": float(
                        self.translation_residuals[index]
                    ),
                    "grid_refinement_max_matching_defect": (
                        float(np.max(finite_refinement))
                        if finite_refinement.size
                        else None
                    ),
                    "bloch_conjugacy_matching_defect": (
                        conjugacy if np.isfinite(conjugacy) else None
                    ),
                }
            )
        return {
            "status": self.status,
            "claim_bearing": self.claim_bearing,
            "screening_outcome": (
                SAMPLED_INSTABILITY
                if SAMPLED_INSTABILITY in outcomes
                else NO_SAMPLED_INSTABILITY
            ),
            "method": {
                "discretization": "dense odd Fourier collocation",
                "grid_points": self.grid_points,
                "coarse_grid_points": self.coarse_grid_points,
                "bloch_phase_convention": (
                    "z(x+L)=exp(i*theta)z(x), periodic factor derivative "
                    "D_theta=d/dx+i*theta/L"
                ),
                "theta_interval": "[-pi, pi]",
                "leading_eigenvalue_sort": "decreasing real part, then imaginary part",
            },
            "parameters": {
                "d": self.d,
                "epsilon": self.epsilon,
                "homogeneous_u": self.homogeneous_u,
                "instability_tolerance": self.instability_tolerance,
            },
            "theta": self.theta.tolist(),
            "refinement_theta": self.refinement_theta.tolist(),
            "constant_profile_dispersion_matching_defect": float(
                self.constant_dispersion_defect
            ),
            "interpretation": {
                "bloch_spectrum": (
                    "finite-dimensional candidate spectra at the listed phases"
                ),
                "co_periodic_spectrum": "theta=0 on the same Fourier grid",
                "sideband_stability": (
                    "not established: no continuum-in-theta enclosure was performed"
                ),
                "proof_status": "NOT_A_PROOF / NOT_INTERVAL_VALIDATED",
            },
            "profiles": profiles,
            "nonclaims": list(NONCLAIMS),
        }


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(np.real(value)), "imag": float(np.imag(value))}


def _validate_odd_grid_points(grid_points: int, *, name: str) -> int:
    points = int(grid_points)
    if points < 7:
        raise ValueError(f"{name} must be at least 7")
    if points % 2 == 0:
        raise ValueError(
            f"{name} must be odd; this avoids the unpaired Fourier Nyquist mode"
        )
    return points


def load_physical_periodic_profiles(
    npz_path: str | Path,
    labels: Sequence[str] = DEFAULT_PROFILE_LABELS,
    *,
    closure_tolerance: float = 1.0e-8,
) -> tuple[PhysicalPeriodicProfile, ...]:
    """Load and validate the saved physical V7 periodic arrays.

    The saved grids include both endpoints.  Endpoint agreement is checked
    here; Fourier collocation later omits the duplicate right endpoint.
    """

    path = Path(npz_path)
    profiles: list[PhysicalPeriodicProfile] = []
    with np.load(path, allow_pickle=False) as archive:
        available = set(archive.files)
        for label in labels:
            keys = tuple(
                f"{label}_{suffix}"
                for suffix in ("physical_x", "physical_u", "physical_v")
            )
            missing = [key for key in keys if key not in available]
            if missing:
                raise KeyError(f"{path}: missing arrays {missing}")
            x = np.asarray(archive[keys[0]], dtype=np.float64)
            u = np.asarray(archive[keys[1]], dtype=np.float64)
            v = np.asarray(archive[keys[2]], dtype=np.float64)
            if x.ndim != 1 or u.shape != x.shape or v.shape != x.shape:
                raise ValueError(f"{label}: physical arrays must be equal-length vectors")
            if x.size < 8 or not np.all(np.isfinite(x)):
                raise ValueError(f"{label}: invalid physical grid")
            if not np.all(np.diff(x) > 0.0):
                raise ValueError(f"{label}: physical grid must be strictly increasing")
            if not np.all(np.isfinite(u)) or not np.all(np.isfinite(v)):
                raise ValueError(f"{label}: profile contains a non-finite value")
            closure_defect = max(abs(float(u[-1] - u[0])), abs(float(v[-1] - v[0])))
            profile_scale = max(1.0, float(np.max(np.abs(u))), float(np.max(np.abs(v))))
            if closure_defect > closure_tolerance * profile_scale:
                raise ValueError(
                    f"{label}: endpoint closure defect {closure_defect:.3e} exceeds tolerance"
                )
            # Make periodic interpolation exact even when an admissible input
            # differs at the last few floating-point bits.
            u = u.copy()
            v = v.copy()
            u[[0, -1]] = 0.5 * (u[0] + u[-1])
            v[[0, -1]] = 0.5 * (v[0] + v[-1])
            profiles.append(PhysicalPeriodicProfile(str(label), x.copy(), u, v))
    return tuple(profiles)


def resample_periodic_profile(
    profile: PhysicalPeriodicProfile, grid_points: int
) -> tuple[RealArray, RealArray, RealArray]:
    """Interpolate a closed saved profile onto an endpoint-free uniform grid."""

    points = _validate_odd_grid_points(grid_points, name="grid_points")
    grid = profile.x[0] + profile.period * np.arange(points, dtype=float) / points
    u = CubicSpline(profile.x, profile.u, bc_type="periodic")(grid)
    v = CubicSpline(profile.x, profile.v, bc_type="periodic")(grid)
    return grid, np.asarray(u, dtype=np.float64), np.asarray(v, dtype=np.float64)


def fourier_bloch_second_derivative_matrix(
    period: float, grid_points: int, theta: float
) -> ComplexArray:
    """Return the collocation matrix for ``(d/dx+i*theta/L)^2``."""

    points = _validate_odd_grid_points(grid_points, name="grid_points")
    if not np.isfinite(period) or period <= 0.0:
        raise ValueError("period must be finite and positive")
    if not np.isfinite(theta):
        raise ValueError("theta must be finite")
    base_wavenumbers = 2.0 * np.pi * np.fft.fftfreq(
        points, d=float(period) / points
    )
    bloch_wavenumbers = base_wavenumbers + float(theta) / float(period)
    identity = np.eye(points, dtype=np.complex128)
    transformed = np.fft.fft(identity, axis=0)
    return np.asarray(
        np.fft.ifft(-(bloch_wavenumbers[:, None] ** 2) * transformed, axis=0),
        dtype=np.complex128,
    )


def fourier_first_derivative(values: RealArray, period: float) -> ComplexArray:
    """Differentiate endpoint-free periodic samples by an FFT multiplier."""

    samples = np.asarray(values)
    if samples.ndim != 1:
        raise ValueError("values must be a vector")
    _validate_odd_grid_points(samples.size, name="number of samples")
    wavenumbers = 2.0 * np.pi * np.fft.fftfreq(
        samples.size, d=float(period) / samples.size
    )
    return np.asarray(
        np.fft.ifft(1j * wavenumbers * np.fft.fft(samples)),
        dtype=np.complex128,
    )


def assemble_bloch_operator(
    u: RealArray,
    *,
    period: float,
    theta: float,
    d: float,
    epsilon: float,
) -> ComplexArray:
    """Assemble the two-component temporal Bloch linearization."""

    u_samples = np.asarray(u, dtype=np.float64)
    if u_samples.ndim != 1 or not np.all(np.isfinite(u_samples)):
        raise ValueError("u must be a finite vector")
    points = _validate_odd_grid_points(u_samples.size, name="number of u samples")
    if not np.isfinite(d) or d <= 0.0:
        raise ValueError("d must be finite and positive")
    if not np.isfinite(epsilon) or epsilon <= 0.0:
        raise ValueError("epsilon must be finite and positive")
    second = fourier_bloch_second_derivative_matrix(period, points, theta)
    identity = np.eye(points, dtype=np.complex128)
    reaction_derivative = u_samples * u_samples - 1.0
    return np.block(
        [
            [d * second - np.diag(reaction_derivative), identity],
            [-epsilon * identity, second],
        ]
    )


def sort_eigenvalues(values: Iterable[complex]) -> ComplexArray:
    """Sort by decreasing real part and then decreasing imaginary part."""

    array = np.asarray(tuple(values), dtype=np.complex128)
    if array.ndim != 1:
        raise ValueError("eigenvalues must be a vector")
    indices = np.lexsort((-array.imag, -array.real))
    return array[indices]


def bloch_eigenvalues(
    u: RealArray,
    *,
    period: float,
    theta: float,
    d: float,
    epsilon: float,
    leading_count: int | None = None,
) -> ComplexArray:
    """Compute the dense finite Fourier spectrum at one Bloch phase."""

    operator = assemble_bloch_operator(
        u, period=period, theta=theta, d=d, epsilon=epsilon
    )
    values = sort_eigenvalues(
        eigvals(operator, overwrite_a=True, check_finite=False)
    )
    if leading_count is None:
        return values
    count = int(leading_count)
    if count < 1 or count > values.size:
        raise ValueError("leading_count must lie between 1 and the matrix dimension")
    return values[:count]


def eigenvalue_set_matching_defect(first: ComplexArray, second: ComplexArray) -> float:
    """Return the optimal maximum pairwise distance between equal-size sets."""

    left = np.asarray(first, dtype=np.complex128).reshape(-1)
    right = np.asarray(second, dtype=np.complex128).reshape(-1)
    if left.size != right.size or left.size == 0:
        raise ValueError("eigenvalue sets must have the same nonzero size")
    rows, columns = linear_sum_assignment(np.abs(left[:, None] - right[None, :]))
    return float(np.max(np.abs(left[rows] - right[columns])))


def analytic_constant_profile_dispersion(
    *,
    period: float,
    grid_points: int,
    theta: float,
    d: float,
    epsilon: float,
    homogeneous_u: float,
) -> ComplexArray:
    """Return the exact modal eigenvalues for a constant physical profile."""

    points = _validate_odd_grid_points(grid_points, name="grid_points")
    base_wavenumbers = 2.0 * np.pi * np.fft.fftfreq(
        points, d=float(period) / points
    )
    derivative = homogeneous_u * homogeneous_u - 1.0
    values: list[complex] = []
    for wavenumber in base_wavenumbers + float(theta) / float(period):
        modal_matrix = np.array(
            [
                [-d * wavenumber * wavenumber - derivative, 1.0],
                [-epsilon, -wavenumber * wavenumber],
            ],
            dtype=np.complex128,
        )
        values.extend(np.linalg.eigvals(modal_matrix))
    return sort_eigenvalues(values)


def constant_profile_dispersion_crosscheck(
    *,
    period: float = 1.0,
    grid_points: int = 15,
    theta: float = 0.731,
    d: float = 0.08**4,
    epsilon: float = 1.0,
    homogeneous_u: float = 1.0,
) -> float:
    """Compare the assembled constant operator with its modal dispersion law."""

    points = _validate_odd_grid_points(grid_points, name="grid_points")
    numerical = bloch_eigenvalues(
        np.full(points, homogeneous_u, dtype=np.float64),
        period=period,
        theta=theta,
        d=d,
        epsilon=epsilon,
    )
    analytic = analytic_constant_profile_dispersion(
        period=period,
        grid_points=points,
        theta=theta,
        d=d,
        epsilon=epsilon,
        homogeneous_u=homogeneous_u,
    )
    return eigenvalue_set_matching_defect(numerical, analytic)


def translation_mode_diagnostic(
    u: RealArray,
    v: RealArray,
    *,
    period: float,
    d: float,
    epsilon: float,
    theta_zero_spectrum: ComplexArray | None = None,
) -> tuple[complex, float]:
    """Measure the neutral translation eigenvalue and eigenvector residual."""

    u_samples = np.asarray(u, dtype=np.float64)
    v_samples = np.asarray(v, dtype=np.float64)
    if u_samples.shape != v_samples.shape or u_samples.ndim != 1:
        raise ValueError("u and v must be equal-length vectors")
    derivative_u = fourier_first_derivative(u_samples, period)
    derivative_v = fourier_first_derivative(v_samples, period)
    translation_vector = np.concatenate((derivative_u, derivative_v))
    operator = assemble_bloch_operator(
        u_samples, period=period, theta=0.0, d=d, epsilon=epsilon
    )
    denominator = float(np.linalg.norm(translation_vector))
    if denominator == 0.0:
        raise ValueError("constant profiles have no nonzero translation vector")
    residual = float(np.linalg.norm(operator @ translation_vector) / denominator)
    spectrum = (
        bloch_eigenvalues(
            u_samples,
            period=period,
            theta=0.0,
            d=d,
            epsilon=epsilon,
        )
        if theta_zero_spectrum is None
        else np.asarray(theta_zero_spectrum, dtype=np.complex128)
    )
    translation_eigenvalue = complex(spectrum[int(np.argmin(np.abs(spectrum)))])
    return translation_eigenvalue, residual


def _phase_index(theta: RealArray, target: float, *, tolerance: float = 2.0e-13) -> int | None:
    differences = np.abs(theta - target)
    index = int(np.argmin(differences))
    return index if differences[index] <= tolerance else None


def screen_saved_periodic_profiles(
    npz_path: str | Path,
    *,
    labels: Sequence[str] = DEFAULT_PROFILE_LABELS,
    theta: Sequence[float] | RealArray | None = None,
    grid_points: int = 127,
    coarse_grid_points: int = 95,
    leading_count: int = 10,
    refinement_theta: Sequence[float] = (-np.pi / 2.0, 0.0, np.pi / 2.0),
    d: float = 0.08**4,
    epsilon: float = 1.0,
    homogeneous_u: float = 1.0,
    instability_tolerance: float = 1.0e-6,
) -> BlochScreeningResult:
    """Screen all saved V7 profiles on a finite Bloch-phase grid.

    Odd Fourier grids are required so that the truncated mode set has no
    unpaired Nyquist mode.  This makes the finite-dimensional relation
    ``sigma(L_-theta) = conjugate(sigma(L_theta))`` directly testable.
    """

    fine_points = _validate_odd_grid_points(grid_points, name="grid_points")
    coarse_points = _validate_odd_grid_points(
        coarse_grid_points, name="coarse_grid_points"
    )
    if coarse_points >= fine_points:
        raise ValueError("coarse_grid_points must be smaller than grid_points")
    phases = np.asarray(
        np.linspace(-np.pi, np.pi, 13) if theta is None else theta,
        dtype=np.float64,
    )
    if phases.ndim != 1 or phases.size == 0 or not np.all(np.isfinite(phases)):
        raise ValueError("theta must be a nonempty finite vector")
    if np.max(np.abs(phases)) > np.pi + 1.0e-12:
        raise ValueError("theta must lie in the fundamental interval [-pi, pi]")
    refinement_phases = np.asarray(refinement_theta, dtype=np.float64)
    if (
        refinement_phases.ndim != 1
        or not np.all(np.isfinite(refinement_phases))
        or np.max(np.abs(refinement_phases), initial=0.0) > np.pi + 1.0e-12
    ):
        raise ValueError("refinement_theta must be a finite vector in [-pi, pi]")
    count = int(leading_count)
    if count < 1 or count > 2 * coarse_points:
        raise ValueError("leading_count exceeds the coarse operator dimension")
    if not np.isfinite(instability_tolerance) or instability_tolerance < 0.0:
        raise ValueError("instability_tolerance must be finite and nonnegative")

    profiles = load_physical_periodic_profiles(npz_path, labels)
    profile_count = len(profiles)
    leading = np.empty((profile_count, phases.size, count), dtype=np.complex128)
    abscissa = np.empty((profile_count, phases.size), dtype=np.float64)
    translation_eigenvalues = np.empty(profile_count, dtype=np.complex128)
    translation_residuals = np.empty(profile_count, dtype=np.float64)
    co_periodic_abscissa = np.empty(profile_count, dtype=np.float64)
    refinement_defects = np.full(
        (profile_count, refinement_phases.size), np.nan, dtype=np.float64
    )
    conjugacy_defects = np.full(profile_count, np.nan, dtype=np.float64)

    for profile_index, profile in enumerate(profiles):
        _fine_x, fine_u, fine_v = resample_periodic_profile(profile, fine_points)
        fine_spectra: dict[float, ComplexArray] = {}
        for phase_index, phase in enumerate(phases):
            full_spectrum = bloch_eigenvalues(
                fine_u,
                period=profile.period,
                theta=float(phase),
                d=d,
                epsilon=epsilon,
            )
            fine_spectra[float(phase)] = full_spectrum
            leading[profile_index, phase_index] = full_spectrum[:count]
            abscissa[profile_index, phase_index] = float(full_spectrum[0].real)

        zero_index = _phase_index(phases, 0.0)
        zero_spectrum = (
            fine_spectra[float(phases[zero_index])]
            if zero_index is not None
            else bloch_eigenvalues(
                fine_u,
                period=profile.period,
                theta=0.0,
                d=d,
                epsilon=epsilon,
            )
        )
        co_periodic_abscissa[profile_index] = float(zero_spectrum[0].real)
        (
            translation_eigenvalues[profile_index],
            translation_residuals[profile_index],
        ) = translation_mode_diagnostic(
            fine_u,
            fine_v,
            period=profile.period,
            d=d,
            epsilon=epsilon,
            theta_zero_spectrum=zero_spectrum,
        )

        pair_defects: list[float] = []
        for phase in phases:
            if phase <= 1.0e-13:
                continue
            negative_index = _phase_index(phases, -float(phase))
            positive_index = _phase_index(phases, float(phase))
            if negative_index is None or positive_index is None:
                continue
            pair_defects.append(
                eigenvalue_set_matching_defect(
                    leading[profile_index, negative_index],
                    np.conjugate(leading[profile_index, positive_index]),
                )
            )
        if pair_defects:
            conjugacy_defects[profile_index] = max(pair_defects)

        _coarse_x, coarse_u, _coarse_v = resample_periodic_profile(
            profile, coarse_points
        )
        for refinement_index, phase in enumerate(refinement_phases):
            phase_index = _phase_index(phases, float(phase))
            fine_values = (
                leading[profile_index, phase_index]
                if phase_index is not None
                else bloch_eigenvalues(
                    fine_u,
                    period=profile.period,
                    theta=float(phase),
                    d=d,
                    epsilon=epsilon,
                    leading_count=count,
                )
            )
            coarse_values = bloch_eigenvalues(
                coarse_u,
                period=profile.period,
                theta=float(phase),
                d=d,
                epsilon=epsilon,
                leading_count=count,
            )
            refinement_defects[profile_index, refinement_index] = (
                eigenvalue_set_matching_defect(fine_values, coarse_values)
            )

    constant_defect = constant_profile_dispersion_crosscheck(
        d=d,
        epsilon=epsilon,
        homogeneous_u=homogeneous_u,
    )
    return BlochScreeningResult(
        labels=tuple(profile.label for profile in profiles),
        theta=phases.copy(),
        periods=np.asarray([profile.period for profile in profiles]),
        grid_points=fine_points,
        coarse_grid_points=coarse_points,
        leading_eigenvalues=leading,
        spectral_abscissa=abscissa,
        co_periodic_spectral_abscissa=co_periodic_abscissa,
        translation_eigenvalues=translation_eigenvalues,
        translation_residuals=translation_residuals,
        refinement_theta=refinement_phases.copy(),
        refinement_defects=refinement_defects,
        conjugacy_defects=conjugacy_defects,
        constant_dispersion_defect=constant_defect,
        d=float(d),
        epsilon=float(epsilon),
        homogeneous_u=float(homogeneous_u),
        instability_tolerance=float(instability_tolerance),
    )


def write_screening_outputs(
    result: BlochScreeningResult,
    *,
    npz_path: str | Path,
    json_path: str | Path,
) -> None:
    """Write the array payload and nonclaim-preserving JSON report."""

    array_path = Path(npz_path)
    report_path = Path(json_path)
    array_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(array_path, **result.as_npz_payload())
    report_path.write_text(
        json.dumps(result.as_report(), indent=2, sort_keys=True, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


__all__ = [
    "BlochScreeningResult",
    "DEFAULT_PROFILE_LABELS",
    "EVIDENCE_STATUS",
    "NO_SAMPLED_INSTABILITY",
    "NONCLAIMS",
    "PhysicalPeriodicProfile",
    "SAMPLED_INSTABILITY",
    "analytic_constant_profile_dispersion",
    "assemble_bloch_operator",
    "bloch_eigenvalues",
    "constant_profile_dispersion_crosscheck",
    "eigenvalue_set_matching_defect",
    "fourier_bloch_second_derivative_matrix",
    "fourier_first_derivative",
    "load_physical_periodic_profiles",
    "resample_periodic_profile",
    "screen_saved_periodic_profiles",
    "sort_eigenvalues",
    "translation_mode_diagnostic",
    "write_screening_outputs",
]
