"""Temporal Fourier/Turing prescreen for the van der Pol reaction--diffusion PDE.

The PDE convention is the one frozen in ``van-der-pol/README.md``::

    u_t = v - f(u) + d u_xx,
    v_t = epsilon (a-u) + v_xx,
    f(u) = u**3/3 - u,

with ``d=r**4`` and ``a=1+sqrt(epsilon)*r**3*a2``.  The homogeneous
equilibrium is ``(a, f(a))``.  A Fourier mode ``exp(lambda*t+i*k*x)`` has
the exact symbol

    L(k) = [[-alpha-d*k**2, 1], [-epsilon, -k**2]],
    alpha = f'(a) = a**2-1.

Consequently

    trace L = -alpha-(d+1)q,
    det L   = d*q**2+alpha*q+epsilon,       q=k**2.

These identities expose an important obstruction: homogeneous asymptotic
stability requires ``alpha>0``, whereas a positive-wavenumber stationary
zero requires ``alpha <= -2*sqrt(d*epsilon)``.  Thus this PDE has no
classical stationary Turing instability from a stable homogeneous state.
For ``alpha<0`` it can have a finite-wavenumber stationary-real unstable
band, but the zero mode is already unstable; this module labels that case as
long-wave instability and never as diffusion-driven mode selection.

The formulas above are exact derivations.  Parameter scans and eigenvalue
evaluations are ordinary double-precision ``COMPUTED/E1`` evidence.  They do
not establish nonlinear branches, selection, stability of nonconstant
patterns, canards, or the outward-rounded validation requested in issue #7.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]

EVIDENCE_STATUS = "DERIVED_FORMULAS+COMPUTED/E1_LINEAR_PRESCREEN"
SCHEMA_VERSION = "vdp-temporal-linear-prescreen-v1"

STABLE_ALL_K = "STABLE_ALL_K"
HOPF_BOUNDARY_K0 = "HOPF_BOUNDARY_K0"
LONG_WAVE_OSCILLATORY = "LONG_WAVE_OSCILLATORY_UNSTABLE"
LONG_WAVE_REAL = "LONG_WAVE_REAL_UNSTABLE"


@dataclass(frozen=True)
class TemporalParameters:
    """Physical parameters for the time-dependent PDE linearization."""

    r: float
    a2: float = 0.0
    epsilon: float = 1.0

    def __post_init__(self) -> None:
        if not np.isfinite(self.r) or self.r <= 0.0:
            raise ValueError("r must be finite and positive")
        if not np.isfinite(self.a2):
            raise ValueError("a2 must be finite")
        if not np.isfinite(self.epsilon) or self.epsilon <= 0.0:
            raise ValueError("epsilon must be finite and positive")

    @property
    def d(self) -> float:
        return self.r**4

    @property
    def a(self) -> float:
        return 1.0 + np.sqrt(self.epsilon) * self.r**3 * self.a2

    @property
    def alpha(self) -> float:
        """The reaction slope f'(a)=a^2-1."""

        return self.a * self.a - 1.0

    def as_dict(self) -> dict[str, float]:
        return {
            "r": float(self.r),
            "a2": float(self.a2),
            "epsilon": float(self.epsilon),
            "d": float(self.d),
            "a": float(self.a),
            "alpha_fprime_a": float(self.alpha),
        }


def cubic_f(u: ArrayLike) -> FloatArray:
    """Return f(u)=u^3/3-u using the paper's convention."""

    value = np.asarray(u, dtype=np.float64)
    return value**3 / 3.0 - value


def homogeneous_equilibrium(parameters: TemporalParameters) -> FloatArray:
    """Return the unique homogeneous equilibrium ``(a,f(a))``."""

    a = parameters.a
    return np.array([a, float(cubic_f(a))], dtype=np.float64)


def reaction_residual(
    state: ArrayLike, parameters: TemporalParameters
) -> FloatArray:
    """Evaluate the reaction terms, excluding spatial diffusion."""

    state_array = np.asarray(state, dtype=np.float64)
    if state_array.shape != (2,):
        raise ValueError("state must have shape (2,)")
    u, v = state_array
    return np.array(
        [v - float(cubic_f(u)), parameters.epsilon * (parameters.a - u)],
        dtype=np.float64,
    )


def _finite_wavenumbers(wavenumber: ArrayLike) -> FloatArray:
    values = np.asarray(wavenumber, dtype=np.float64)
    if np.any(~np.isfinite(values)):
        raise ValueError("wavenumbers must be finite")
    return values


def fourier_symbol(
    parameters: TemporalParameters, wavenumber: ArrayLike
) -> FloatArray:
    """Return the exact 2x2 temporal Fourier symbol.

    A scalar ``wavenumber`` returns shape ``(2,2)``.  An array of shape
    ``S`` returns shape ``S+(2,2)``.  Negative and positive wavenumbers are
    equivalent because the symbol depends on ``k^2``.
    """

    k = _finite_wavenumbers(wavenumber)
    q = k * k
    result = np.empty(q.shape + (2, 2), dtype=np.float64)
    result[..., 0, 0] = -parameters.alpha - parameters.d * q
    result[..., 0, 1] = 1.0
    result[..., 1, 0] = -parameters.epsilon
    result[..., 1, 1] = -q
    return result


def symbol_trace_determinant(
    parameters: TemporalParameters, wavenumber: ArrayLike
) -> tuple[FloatArray, FloatArray]:
    """Return the analytic trace and determinant of the Fourier symbol."""

    k = _finite_wavenumbers(wavenumber)
    q = k * k
    trace = -parameters.alpha - (parameters.d + 1.0) * q
    determinant = parameters.d * q * q + parameters.alpha * q + parameters.epsilon
    return np.asarray(trace), np.asarray(determinant)


def dispersion_eigenvalues(
    parameters: TemporalParameters, wavenumber: ArrayLike
) -> ComplexArray:
    """Return the two exact quadratic-formula dispersion branches.

    The final axis has length two and the plus-square-root branch is first.
    Complex arithmetic is retained at Hopf/oscillatory modes.
    """

    trace, determinant = symbol_trace_determinant(parameters, wavenumber)
    discriminant = np.asarray(trace * trace - 4.0 * determinant, dtype=np.complex128)
    root = np.sqrt(discriminant)
    return np.stack(((trace + root) / 2.0, (trace - root) / 2.0), axis=-1)


def spectral_abscissa(
    parameters: TemporalParameters, wavenumber: ArrayLike
) -> FloatArray:
    """Return ``max_j Re lambda_j(k)``."""

    return np.max(dispersion_eigenvalues(parameters, wavenumber).real, axis=-1)


def _scaled_tolerance(values: Iterable[float], absolute_tolerance: float) -> float:
    return absolute_tolerance * max(1.0, *(abs(float(value)) for value in values))


def homogeneous_status(
    parameters: TemporalParameters, *, absolute_tolerance: float = 1.0e-12
) -> str:
    """Classify the spatially homogeneous (k=0) temporal spectrum."""

    alpha = parameters.alpha
    tolerance = _scaled_tolerance((alpha,), absolute_tolerance)
    if alpha > tolerance:
        return STABLE_ALL_K
    if abs(alpha) <= tolerance:
        return HOPF_BOUNDARY_K0
    reaction_discriminant = alpha * alpha - 4.0 * parameters.epsilon
    discriminant_tolerance = _scaled_tolerance(
        (alpha * alpha, 4.0 * parameters.epsilon), absolute_tolerance
    )
    if reaction_discriminant <= discriminant_tolerance:
        return LONG_WAVE_OSCILLATORY
    return LONG_WAVE_REAL


def stationary_turing_diagnostics(
    parameters: TemporalParameters, *, absolute_tolerance: float = 1.0e-12
) -> dict[str, Any]:
    """Diagnose stationary finite-wavenumber zeros and the Turing obstruction.

    ``det L(k)=0`` is a quadratic in ``q=k^2``.  If it has two positive
    roots, ``det L<0`` between them and hence one real temporal eigenvalue is
    positive there.  That band can occur only for ``alpha<0``, when the
    homogeneous equilibrium is already unstable.
    """

    d = parameters.d
    epsilon = parameters.epsilon
    alpha = parameters.alpha
    stationary_discriminant = alpha * alpha - 4.0 * d * epsilon
    discriminant_tolerance = _scaled_tolerance(
        (alpha * alpha, 4.0 * d * epsilon), absolute_tolerance
    )
    threshold_alpha = -2.0 * np.sqrt(d * epsilon)
    q_critical = np.sqrt(epsilon / d)
    k_critical = np.sqrt(q_critical)

    if alpha < 0.0:
        q_minimum = -alpha / (2.0 * d)
        determinant_minimum = epsilon - alpha * alpha / (4.0 * d)
    else:
        q_minimum = 0.0
        determinant_minimum = epsilon

    q_roots: list[float] = []
    zero_status = "NONE"
    has_open_band = False
    if alpha < 0.0 and stationary_discriminant > discriminant_tolerance:
        root = np.sqrt(stationary_discriminant)
        q_roots = [
            float((-alpha - root) / (2.0 * d)),
            float((-alpha + root) / (2.0 * d)),
        ]
        zero_status = "TWO_POSITIVE_ZEROS"
        has_open_band = True
    elif alpha < 0.0 and abs(stationary_discriminant) <= discriminant_tolerance:
        q_roots = [float(-alpha / (2.0 * d))]
        zero_status = "DOUBLE_POSITIVE_ZERO"

    k_roots = [float(np.sqrt(q)) for q in q_roots]
    wavelengths = [float(2.0 * np.pi / k) for k in k_roots]
    homogeneous_stable = bool(
        alpha > _scaled_tolerance((alpha,), absolute_tolerance)
    )
    classical_turing = bool(homogeneous_stable and has_open_band)

    return {
        "stationary_zero_status": zero_status,
        "has_stationary_real_unstable_band": has_open_band,
        "classical_stationary_turing_from_stable_homogeneous_state": classical_turing,
        "stationary_discriminant": float(stationary_discriminant),
        "threshold_alpha": float(threshold_alpha),
        "threshold_margin_alpha_minus_threshold": float(alpha - threshold_alpha),
        "q_minimum_determinant": float(q_minimum),
        "minimum_determinant": float(determinant_minimum),
        "q_roots": q_roots,
        "k_roots": k_roots,
        "wavelengths_at_roots": wavelengths,
        "onset_q_critical": float(q_critical),
        "onset_k_critical": float(k_critical),
        "onset_wavelength": float(2.0 * np.pi / k_critical),
        "obstruction": (
            "homogeneous stability requires alpha>0, while a positive-k "
            "stationary zero requires alpha<=-2*sqrt(d*epsilon)"
        ),
    }


def temporal_regime(
    parameters: TemporalParameters, *, absolute_tolerance: float = 1.0e-12
) -> str:
    """Return a label that keeps Hopf, long-wave, and stationary bands apart."""

    homogeneous = homogeneous_status(parameters, absolute_tolerance=absolute_tolerance)
    stationary = stationary_turing_diagnostics(
        parameters, absolute_tolerance=absolute_tolerance
    )
    suffix = ""
    if stationary["stationary_zero_status"] == "DOUBLE_POSITIVE_ZERO":
        suffix = "+FINITE_K_STATIONARY_DOUBLE_ZERO"
    elif stationary["has_stationary_real_unstable_band"]:
        suffix = "+FINITE_K_STATIONARY_REAL_UNSTABLE_BAND"
    return homogeneous + suffix


def parameter_diagnostics(
    parameters: TemporalParameters, *, absolute_tolerance: float = 1.0e-12
) -> dict[str, Any]:
    """Return a compact JSON-safe analytic/numeric diagnosis of one point."""

    zero_eigenvalues = dispersion_eigenvalues(parameters, 0.0)
    stationary = stationary_turing_diagnostics(
        parameters, absolute_tolerance=absolute_tolerance
    )
    homogeneous = homogeneous_status(parameters, absolute_tolerance=absolute_tolerance)
    return {
        "parameters": parameters.as_dict(),
        "homogeneous_equilibrium": homogeneous_equilibrium(parameters).tolist(),
        "homogeneous_status": homogeneous,
        "temporal_regime": temporal_regime(
            parameters, absolute_tolerance=absolute_tolerance
        ),
        "zero_mode_trace": float(-parameters.alpha),
        "zero_mode_determinant": float(parameters.epsilon),
        "zero_mode_eigenvalues": [
            {"real": float(value.real), "imag": float(value.imag)}
            for value in zero_eigenvalues
        ],
        "zero_mode_spectral_abscissa": float(np.max(zero_eigenvalues.real)),
        "all_fourier_modes_asymptotically_stable": homogeneous == STABLE_ALL_K,
        "stationary": stationary,
        "interpretation": _interpretation(homogeneous, stationary),
    }


def _interpretation(homogeneous: str, stationary: Mapping[str, Any]) -> str:
    if homogeneous == STABLE_ALL_K:
        return "stable homogeneous state; analytic determinant monotonicity excludes Turing"
    if homogeneous == HOPF_BOUNDARY_K0:
        return "neutral Hopf pair at k=0; every k>0 is damped; no Turing band"
    if stationary["has_stationary_real_unstable_band"]:
        return (
            "zero mode is already unstable; a finite-k stationary-real band also exists, "
            "but it is not classical diffusion-driven Turing selection"
        )
    if stationary["stationary_zero_status"] == "DOUBLE_POSITIVE_ZERO":
        return (
            "zero mode is already unstable and a finite-k stationary double zero occurs; "
            "this is not onset from a stable homogeneous state"
        )
    return "long-wave homogeneous instability with no stationary finite-k zero"


def stationary_band_a2_interval(
    r: float, epsilon: float
) -> tuple[float, float] | None:
    """Return the exact open ``a2`` interval supporting a stationary band.

    It solves ``a^2-1 < -2*r^2*sqrt(epsilon)``.  The returned endpoints are
    ordered.  ``None`` means that the threshold is inaccessible because the
    minimum possible reaction slope ``alpha=-1`` is not negative enough.
    The interval still lies entirely in a homogeneous-unstable regime.
    """

    probe = TemporalParameters(r=r, a2=0.0, epsilon=epsilon)
    radicand = 1.0 - 2.0 * probe.r**2 * np.sqrt(probe.epsilon)
    # The defining inequality is strict.  At radicand == 0 the two
    # endpoints coincide, so there is no open stationary-band interval.
    if radicand <= 0.0:
        return None
    root = np.sqrt(radicand)
    scale = np.sqrt(probe.epsilon) * probe.r**3
    lower = (-root - 1.0) / scale
    upper = (root - 1.0) / scale
    return float(lower), float(upper)


def dispersion_curve(
    parameters: TemporalParameters, wavenumbers: ArrayLike
) -> dict[str, list[float]]:
    """Return plot-ready dispersion quantities without making a figure."""

    k = _finite_wavenumbers(wavenumbers)
    if k.ndim != 1:
        raise ValueError("dispersion_curve requires a one-dimensional k grid")
    eigenvalues = dispersion_eigenvalues(parameters, k)
    trace, determinant = symbol_trace_determinant(parameters, k)
    return {
        "k": k.tolist(),
        "leading_growth_rate": np.max(eigenvalues.real, axis=-1).tolist(),
        "lambda_plus_real": eigenvalues[:, 0].real.tolist(),
        "lambda_plus_imag": eigenvalues[:, 0].imag.tolist(),
        "lambda_minus_real": eigenvalues[:, 1].real.tolist(),
        "lambda_minus_imag": eigenvalues[:, 1].imag.tolist(),
        "trace": np.asarray(trace).tolist(),
        "determinant": np.asarray(determinant).tolist(),
    }


def threshold_curve(r_values: ArrayLike, epsilon: float) -> dict[str, list[float]]:
    """Return plot-ready near-``a=1`` stationary thresholds versus ``r``."""

    r_array = np.asarray(r_values, dtype=np.float64)
    if r_array.ndim != 1 or np.any(~np.isfinite(r_array)) or np.any(r_array <= 0.0):
        raise ValueError("r_values must be a finite positive one-dimensional grid")
    if not np.isfinite(epsilon) or epsilon <= 0.0:
        raise ValueError("epsilon must be finite and positive")
    near_plus: list[float] = []
    k_critical: list[float] = []
    accessible: list[float] = []
    for r in r_array:
        interval = stationary_band_a2_interval(float(r), float(epsilon))
        near_plus.append(float("nan") if interval is None else interval[1])
        k_critical.append(float(epsilon**0.25 / r))
        accessible.append(0.0 if interval is None else 1.0)
    return {
        "r": r_array.tolist(),
        "near_a_equals_one_a2_threshold": near_plus,
        "onset_k_critical": k_critical,
        "threshold_accessible": accessible,
    }


def scan_parameter_grid(
    r_values: Sequence[float],
    a2_values: Sequence[float],
    epsilon_values: Sequence[float],
    *,
    include_records: bool = True,
) -> dict[str, Any]:
    """Scan a Cartesian parameter grid using the analytic classification."""

    counts: Counter[str] = Counter()
    records: list[dict[str, Any]] = []
    first_stationary_band: dict[str, Any] | None = None
    closest_threshold: dict[str, Any] | None = None
    closest_absolute_margin = np.inf
    classical_turing_count = 0
    total = 0
    for r in r_values:
        for a2 in a2_values:
            for epsilon in epsilon_values:
                parameters = TemporalParameters(float(r), float(a2), float(epsilon))
                diagnosis = parameter_diagnostics(parameters)
                regime = str(diagnosis["temporal_regime"])
                counts[regime] += 1
                total += 1
                stationary = diagnosis["stationary"]
                classical_turing_count += int(
                    stationary[
                        "classical_stationary_turing_from_stable_homogeneous_state"
                    ]
                )
                if stationary["has_stationary_real_unstable_band"]:
                    if first_stationary_band is None:
                        first_stationary_band = diagnosis
                margin = abs(float(stationary["threshold_margin_alpha_minus_threshold"]))
                if margin < closest_absolute_margin:
                    closest_absolute_margin = margin
                    closest_threshold = diagnosis
                if include_records:
                    records.append(diagnosis)
    result: dict[str, Any] = {
        "shape": [len(r_values), len(a2_values), len(epsilon_values)],
        "point_count": total,
        "regime_counts": dict(sorted(counts.items())),
        "classical_stationary_turing_point_count": classical_turing_count,
        "first_stationary_band_witness": first_stationary_band,
        "closest_sample_to_stationary_threshold": closest_threshold,
    }
    if include_records:
        result["records"] = records
    return result


def _configured_grid(
    specification: Sequence[float | int], *, name: str, logarithmic: bool = False
) -> FloatArray:
    """Build one explicitly configured three-entry diagnostic grid."""

    if len(specification) != 3:
        raise ValueError(f"{name} must be [lower,upper,count]")
    lower, upper, count_value = specification
    count = int(count_value)
    if count < 2 or float(count_value) != count:
        raise ValueError(f"{name} count must be an integer at least two")
    lower_value = float(lower)
    upper_value = float(upper)
    if (
        not np.isfinite(lower_value)
        or not np.isfinite(upper_value)
        or upper_value <= lower_value
    ):
        raise ValueError(f"{name} endpoints must be finite and increasing")
    if logarithmic and lower_value <= 0.0:
        raise ValueError(f"{name} logarithmic endpoints must be positive")
    constructor = np.geomspace if logarithmic else np.linspace
    return np.asarray(constructor(lower_value, upper_value, count), dtype=np.float64)


def build_prescreen_report(configuration: Mapping[str, Any]) -> dict[str, Any]:
    """Build the frozen-slice and wider diagnostic prescreen report.

    ``configuration`` is the dynamics-screening configuration itself.  This
    keeps the report and the plot arrays on the same frozen parameter source.
    """

    primary_values = configuration["primary_parameters"]
    turing_configuration = configuration["turing"]
    frozen_slices = turing_configuration["frozen_parameter_slices"]
    primary = TemporalParameters(
        r=float(primary_values["r"]),
        a2=float(primary_values["a2"]),
        epsilon=float(primary_values["epsilon"]),
    )
    frozen_scan = scan_parameter_grid(
        frozen_slices["r"],
        frozen_slices["a2"],
        frozen_slices["epsilon"],
        include_records=True,
    )

    wide_r = _configured_grid(
        turing_configuration["wide_r_grid"], name="wide_r_grid"
    )
    wide_a2 = _configured_grid(
        turing_configuration["wide_a2_grid"], name="wide_a2_grid"
    )
    wide_epsilon = _configured_grid(
        turing_configuration["wide_epsilon_log_grid"],
        name="wide_epsilon_log_grid",
        logarithmic=True,
    )
    wide_scan = scan_parameter_grid(
        wide_r, wide_a2, wide_epsilon, include_records=False
    )

    primary_threshold_interval = stationary_band_a2_interval(
        primary.r, primary.epsilon
    )
    diagnostic_a2 = float(turing_configuration["remote_nonclassical_a2"])
    diagnostic_witness = TemporalParameters(
        r=primary.r, a2=diagnostic_a2, epsilon=primary.epsilon
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "evidence_status": EVIDENCE_STATUS,
        "model": {
            "equations": [
                "u_t = v - (u^3/3-u) + r^4 u_xx",
                "v_t = epsilon(a-u) + v_xx",
                "a = 1 + sqrt(epsilon) r^3 a2",
            ],
            "homogeneous_equilibrium": "(a, a^3/3-a)",
            "fourier_symbol": "[[-alpha-r^4 k^2,1],[-epsilon,-k^2]]",
            "alpha": "a^2-1",
            "trace": "-alpha-(r^4+1)k^2",
            "determinant": "r^4 k^4+alpha k^2+epsilon",
        },
        "claim_boundary": [
            "linear temporal Fourier prescreen only",
            "no nonlinear Turing branch or mode-selection claim",
            "no stability claim for nonconstant stationary profiles",
            "no nonlinear time-evolution conclusion",
            "no canard identification",
            "not outward-rounded issue #7 validation",
        ],
        "primary": parameter_diagnostics(primary),
        "primary_near_a_equals_one_stationary_band_a2_interval": (
            None
            if primary_threshold_interval is None
            else list(primary_threshold_interval)
        ),
        "frozen_cartesian_slice_scan": frozen_scan,
        "wide_diagnostic_domain": {
            "r": [float(wide_r[0]), float(wide_r[-1]), int(wide_r.size)],
            "a2": [float(wide_a2[0]), float(wide_a2[-1]), int(wide_a2.size)],
            "epsilon_log_grid": [
                float(wide_epsilon[0]),
                float(wide_epsilon[-1]),
                int(wide_epsilon.size),
            ],
            "scan": wide_scan,
        },
        "wide_stationary_band_witness_at_primary_r_epsilon": parameter_diagnostics(
            diagnostic_witness
        ),
        "recommended_figure_quantities": {
            "dispersion_panel": [
                "k",
                "leading_growth_rate",
                "lambda_plus/minus real and imaginary parts",
                "trace",
                "determinant",
            ],
            "threshold_panel": [
                "near-a=1 a2 threshold versus r",
                "onset k_critical=epsilon^(1/4)/r",
            ],
            "mandatory_labels": [
                "Hopf boundary k=0",
                "long-wave instability",
                "finite-k stationary-real band (not classical Turing)",
                "COMPUTED/E1 linear prescreen",
            ],
        },
    }


def _default_configuration_path() -> Path:
    return Path(__file__).resolve().parent / "config" / "vdp_dynamics_screening.json"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=_default_configuration_path())
    parser.add_argument(
        "--output",
        type=Path,
        help="optional JSON output path; stdout is always a concise summary",
    )
    arguments = parser.parse_args(argv)
    configuration = json.loads(arguments.config.read_text(encoding="utf-8"))
    report = build_prescreen_report(configuration)
    if arguments.output is not None:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    concise = {
        "schema_version": report["schema_version"],
        "evidence_status": report["evidence_status"],
        "primary": report["primary"],
        "frozen_slice_regime_counts": report["frozen_cartesian_slice_scan"][
            "regime_counts"
        ],
        "wide_scan_regime_counts": report["wide_diagnostic_domain"]["scan"][
            "regime_counts"
        ],
    }
    print(json.dumps(concise, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
