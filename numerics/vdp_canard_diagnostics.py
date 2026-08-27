"""Candidate-level slow--fast diagnostics for the stationary van der Pol PDE.

The physical stationary equations, in fast spatial time ``y=x/delta``, are

``u_y=p, p_y=f(u)-v, v_y=delta*q, q_y=epsilon*delta*(u-a)``.

At ``delta=0`` the critical manifold is ``p=0, v=f(u)`` and loses normal
hyperbolicity at ``u=+/-1``.  These routines measure how the already-computed
finite-parameter profiles meet that geometry.  They do *not* identify a
canard: that would additionally require finite-parameter slow manifolds,
branch tracking through a fold, and parameter-sensitivity evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import numpy as np
from numpy.typing import ArrayLike, NDArray

from numerics.vdp_bridge import BridgeParameters, central_to_physical
from numerics.vdp_outer import OuterParameters, normal_outer_state
from numerics.vdp_pole import cubic_f


FloatArray = NDArray[np.float64]

CANARD_STOP_STATUS = "NO_CANARD_IDENTIFICATION_FROM_CURRENT_DATA"
FOLD_PASSAGE_STATUS = "COMPUTED/E1_FOLD_PASSAGE_DIAGNOSTIC"
OUTER_STATUS = "COMPUTED/E1_OUTER_SEGMENT_EXCLUDES_FOLD"


@dataclass(frozen=True)
class FoldCrossing:
    """Linearly interpolated crossing of one critical-manifold fold level."""

    fold: float
    physical_x: float
    p: float
    v_minus_f: float
    q: float
    direction: int

    def as_dict(self) -> dict[str, float | int]:
        return {
            "fold": self.fold,
            "physical_x": self.physical_x,
            "p": self.p,
            "v_minus_f": self.v_minus_f,
            "q": self.q,
            "direction": self.direction,
        }


def critical_manifold_v(u: ArrayLike) -> FloatArray:
    """Critical-manifold graph ``v=f(u)``."""

    return np.asarray(cubic_f(np.asarray(u, dtype=np.float64)), dtype=np.float64)


def fast_normal_eigenvalue_squared(u: ArrayLike) -> FloatArray:
    """Squared nonzero fast eigenvalue ``f'(u)=u^2-1`` along the critical set."""

    values = np.asarray(u, dtype=np.float64)
    return values * values - 1.0


def desingularized_reduced_field(
    u: ArrayLike, q: ArrayLike, *, a: float, epsilon: float
) -> FloatArray:
    """Reduced fold field in desingularized time: ``(u_s,q_s)``.

    The physical slow equations satisfy ``f'(u) u_x=q`` and
    ``q_x=epsilon*(u-a)``.  Multiplication by ``f'(u)`` gives the displayed
    field.  Its time orientation reverses where ``f'(u)<0``.
    """

    u_values, q_values = np.broadcast_arrays(
        np.asarray(u, dtype=np.float64), np.asarray(q, dtype=np.float64)
    )
    return np.asarray(
        [q_values, epsilon * (u_values - a) * fast_normal_eigenvalue_squared(u_values)],
        dtype=np.float64,
    )


def folded_linear_product(*, fold: float, a: float, epsilon: float) -> float:
    """Return the product controlling the desingularized fold linearization.

    At ``(u,q)=(fold,0)``, with ``fold=+/-1``, the nonzero off-diagonal
    product is ``2*epsilon*fold*(fold-a)``.  Zero is the degenerate FSN case;
    its sign alone is only a singular reduced-flow classification.
    """

    if fold not in (-1.0, 1.0):
        raise ValueError("fold must be +1 or -1")
    if epsilon <= 0.0 or not np.isfinite(epsilon):
        raise ValueError("epsilon must be finite and positive")
    return float(2.0 * epsilon * fold * (fold - a))


def folded_singularity_classification(
    *, fold: float, a: float, epsilon: float, tolerance: float = 1.0e-12
) -> str:
    """Classify only the two-dimensional desingularized reduced linearization.

    This label is deliberately narrower than a finite-parameter canard label.
    The squared reduced eigenvalue equals :func:`folded_linear_product`.
    """

    product = folded_linear_product(fold=fold, a=a, epsilon=epsilon)
    if tolerance < 0.0 or not np.isfinite(tolerance):
        raise ValueError("tolerance must be finite and nonnegative")
    if abs(product) <= tolerance:
        return "FSN_DEGENERATE_SINGULAR_LIMIT"
    if product > 0.0:
        return "DESINGULARIZED_REDUCED_SADDLE"
    return "DESINGULARIZED_REDUCED_CENTER"


def maximal_canard_leading_parameter(*, r: float, epsilon: float) -> dict[str, float | str]:
    """Return the published leading maximal-canard coincidence curve.

    Lemma 6.4 of Vo--Doelman--Kaper gives, in physical parameters,

    ``a_c = 1 - (5*epsilon/48)*delta**2 + O(delta**3)``.

    With the repository conventions ``delta=r**2`` and
    ``a=1+sqrt(epsilon)*r**3*a2``, this becomes

    ``a2_c = -(5*sqrt(epsilon)/48)*r + O(r**3)``.

    Only the displayed leading term is returned.  It is a reference curve,
    not a finite-parameter enclosure or an identification test.
    """

    if not np.isfinite(r) or r <= 0.0:
        raise ValueError("r must be finite and positive")
    if not np.isfinite(epsilon) or epsilon <= 0.0:
        raise ValueError("epsilon must be finite and positive")
    delta = r * r
    physical_a_leading = 1.0 - (5.0 * epsilon / 48.0) * delta * delta
    a2_leading = -(5.0 * np.sqrt(epsilon) / 48.0) * r
    return {
        "source": "Vo--Doelman--Kaper (2025), Lemma 6.4",
        "physical_a_leading": float(physical_a_leading),
        "blowup_a2_leading": float(a2_leading),
        "physical_remainder_order": "O(delta^3)=O(r^6)",
        "blowup_a2_remainder_order": "O(r^3)",
    }


def _fold_crossings(
    physical_x: FloatArray,
    physical: FloatArray,
    *,
    fold: float,
) -> tuple[FoldCrossing, ...]:
    u, p, v, q = physical
    signed = u - fold
    indices = np.flatnonzero(signed[:-1] * signed[1:] <= 0.0)
    crossings: list[FoldCrossing] = []
    for index in indices:
        left = signed[index]
        right = signed[index + 1]
        if left == 0.0 and index > 0 and signed[index - 1] * right <= 0.0:
            continue
        denominator = right - left
        weight = 0.0 if denominator == 0.0 else -left / denominator
        weight = float(np.clip(weight, 0.0, 1.0))

        def interpolate(values: FloatArray) -> float:
            return float((1.0 - weight) * values[index] + weight * values[index + 1])

        crossing_v = interpolate(v)
        direction = int(np.sign(right - left))
        crossings.append(
            FoldCrossing(
                fold=fold,
                physical_x=interpolate(physical_x),
                p=interpolate(p),
                v_minus_f=float(crossing_v - cubic_f(fold)),
                q=interpolate(q),
                direction=direction,
            )
        )
    return tuple(crossings)


def profile_fold_diagnostics(
    physical_x: ArrayLike,
    central_state: ArrayLike,
    parameters: BridgeParameters,
    *,
    fold: float = 1.0,
    fold_collar: float = 2.0e-3,
) -> dict[str, Any]:
    """Measure a saved central profile against the singular fold geometry."""

    coordinate = np.asarray(physical_x, dtype=np.float64)
    central = np.asarray(central_state, dtype=np.float64)
    if central.ndim != 2 or central.shape[0] != 4:
        raise ValueError("central_state must have shape (4,N)")
    if coordinate.ndim != 1 or coordinate.size != central.shape[1]:
        raise ValueError("physical_x and central_state grid sizes must agree")
    if coordinate.size < 3 or np.any(np.diff(coordinate) <= 0.0):
        raise ValueError("physical_x must be a strictly increasing grid")
    if fold not in (-1.0, 1.0):
        raise ValueError("fold must be +1 or -1")
    if fold_collar <= 0.0:
        raise ValueError("fold_collar must be positive")

    physical = np.asarray(central_to_physical(central, parameters), dtype=np.float64)
    u, p, v, q = physical
    v_minus_f = v - critical_manifold_v(u)
    crossings = _fold_crossings(coordinate, physical, fold=fold)
    natural_p_scale = parameters.epsilon**0.75 * parameters.r**3
    natural_v_scale = parameters.epsilon * parameters.r**4
    natural_q_scale = parameters.epsilon**1.25 * parameters.r**3
    collar_mask = np.abs(u - fold) <= fold_collar
    # Hyperbolic/elliptic is determined by the fast normal square u^2-1,
    # not by whether a sample lies to the right/left of the selected fold.
    # The latter convention reverses the labels at the negative fold.
    fast_normal_square = fast_normal_eigenvalue_squared(u)
    hyperbolic_side = fast_normal_square > 0.0
    elliptic_side = fast_normal_square < 0.0
    return {
        "status": FOLD_PASSAGE_STATUS,
        "canard_identification_status": CANARD_STOP_STATUS,
        "fold": fold,
        "fold_collar": fold_collar,
        "crossing_count": len(crossings),
        "crossings": [crossing.as_dict() for crossing in crossings],
        "minimum_abs_u_minus_fold": float(np.min(np.abs(u - fold))),
        "physical_x_in_fold_collar": float(
            np.trapezoid(collar_mask.astype(np.float64), coordinate)
        ),
        "samples_on_hyperbolic_side": int(np.count_nonzero(hyperbolic_side)),
        "samples_on_elliptic_side": int(np.count_nonzero(elliptic_side)),
        "maximum_abs_p": float(np.max(np.abs(p))),
        "maximum_abs_v_minus_f": float(np.max(np.abs(v_minus_f))),
        "maximum_abs_q": float(np.max(np.abs(q))),
        "maximum_scaled_p": float(np.max(np.abs(p)) / natural_p_scale),
        "maximum_scaled_v_minus_f": float(
            np.max(np.abs(v_minus_f)) / natural_v_scale
        ),
        "maximum_scaled_q": float(np.max(np.abs(q)) / natural_q_scale),
        "minimum_abs_fast_normal_eigenvalue_squared": float(
            np.min(np.abs(fast_normal_square))
        ),
        "folded_linear_product": folded_linear_product(
            fold=fold, a=parameters.a, epsilon=parameters.epsilon
        ),
        "singular_reduced_classification": folded_singularity_classification(
            fold=fold, a=parameters.a, epsilon=parameters.epsilon
        ),
        "scope": (
            "An actual finite-parameter orbit crosses a neighborhood of the "
            "singular fold.  No attracting/repelling finite-parameter slow "
            "manifolds, maximal-canard intersection, or exponentially small "
            "parameter window has been computed."
        ),
    }


def _crosses_fold_levels(u: ArrayLike) -> bool:
    """Return whether a connected sampled segment spans either fold level."""

    values = np.asarray(u, dtype=np.float64)
    if values.size == 0 or np.any(~np.isfinite(values)):
        raise ValueError("u must contain finite samples")
    minimum = float(np.min(values))
    maximum = float(np.max(values))
    return any(minimum <= fold <= maximum for fold in (-1.0, 1.0))


def outer_fold_exclusion_diagnostics(
    compact_q: ArrayLike,
    beta: ArrayLike,
    alpha: ArrayLike,
    parameters: OuterParameters,
) -> dict[str, Any]:
    """Show whether the saved finite outer segment even reaches a fold collar."""

    q_coordinate, beta_values, alpha_values = np.broadcast_arrays(
        np.asarray(compact_q, dtype=np.float64),
        np.asarray(beta, dtype=np.float64),
        np.asarray(alpha, dtype=np.float64),
    )
    if np.any(q_coordinate <= 0.0):
        raise ValueError("compact_q must be positive")
    u = np.sqrt(q_coordinate)
    z = 1.0 / u
    chi, pi, w = normal_outer_state(z, beta_values, alpha_values, parameters)
    v_minus_f = -w * u
    distance_to_fold_set = np.minimum(np.abs(u - 1.0), np.abs(u + 1.0))
    return {
        "status": OUTER_STATUS,
        "canard_identification_status": CANARD_STOP_STATUS,
        "minimum_u": float(np.min(u)),
        "maximum_u": float(np.max(u)),
        "minimum_distance_to_fold_set": float(np.min(distance_to_fold_set)),
        "maximum_abs_p": float(np.max(np.abs(pi))),
        "maximum_abs_v_minus_f": float(np.max(np.abs(v_minus_f))),
        "minimum_q": float(np.min(chi * q_coordinate)),
        # The saved arrays sample a connected outer segment.  A continuous
        # fold crossing need not place a floating-point node exactly at u=+/-1.
        "crosses_a_fold": _crosses_fold_levels(u),
        "scope": (
            "The saved outer leg is an actual finite-horizon candidate in the "
            "outer chart.  Exclusion of both folds shows that this leg alone "
            "cannot demonstrate a fold canard."
        ),
    }


def screen_saved_profiles(
    result_directory: str | Path,
    *,
    r: float = 0.08,
    a2: float = 0.0,
    epsilon: float = 1.0,
    fold: float = 1.0,
    fold_collar: float = 2.0e-3,
    reference_curve: str = (
        "Vo--Doelman--Kaper (2025), Lemma 6.4 leading term only"
    ),
) -> dict[str, Any]:
    """Screen the saved V7 profiles and matched outer leg without recomputation."""

    if fold not in (-1.0, 1.0):
        raise ValueError("fold must be +1 or -1")
    if not np.isfinite(fold_collar) or fold_collar <= 0.0:
        raise ValueError("fold_collar must be finite and positive")
    if not isinstance(reference_curve, str) or not reference_curve.strip():
        raise ValueError("reference_curve must be a nonempty string")
    directory = Path(result_directory)
    bridge_parameters = BridgeParameters(r=r, a2=a2, epsilon=epsilon)
    outer_parameters = OuterParameters(r=r, a2=a2, epsilon=epsilon)
    canard_curve = maximal_canard_leading_parameter(r=r, epsilon=epsilon)
    profile_reports: dict[str, Mapping[str, Any]] = {}
    for filename in ("v7_periodic.npz", "v7_multipulses.npz"):
        with np.load(directory / filename, allow_pickle=False) as archive:
            prefixes = sorted(
                key.removesuffix("_state")
                for key in archive.files
                if key.endswith("_state")
            )
            for prefix in prefixes:
                profile_reports[prefix] = profile_fold_diagnostics(
                    archive[f"{prefix}_physical_x"],
                    archive[f"{prefix}_state"],
                    bridge_parameters,
                    fold=fold,
                    fold_collar=fold_collar,
                )
    with np.load(directory / "v4_v5_matched_candidate.npz", allow_pickle=False) as archive:
        outer_report = outer_fold_exclusion_diagnostics(
            archive["compact_q"],
            archive["outer_beta"],
            archive["outer_alpha"],
            outer_parameters,
        )
    return {
        "status": "COMPUTED/E1_SLOW_FAST_GEOMETRY_SCREEN",
        "canard_identification_status": CANARD_STOP_STATUS,
        "parameters": {"r": r, "a2": a2, "epsilon": epsilon},
        "screened_fold": fold,
        "fold_collar": fold_collar,
        "reference_curve_configuration": reference_curve,
        "maximal_canard_reference": {
            **canard_curve,
            "configured_reference_curve": reference_curve,
            "sample_minus_leading_a2": float(
                a2 - float(canard_curve["blowup_a2_leading"])
            ),
            "interpretation": (
                "The sample is compared only with the published leading "
                "coincidence curve.  The unbounded O(r^3) remainder and the "
                "absence of finite-parameter slow-manifold continuation "
                "prevent a canard identification."
            ),
        },
        "critical_manifold": "p=0, v=f(u)",
        "folds": [-1.0, 1.0],
        "screened_fold_singular_reduced_classification": (
            folded_singularity_classification(
                fold=fold, a=bridge_parameters.a, epsilon=epsilon
            )
        ),
        "positive_fold_singular_reduced_classification": (
            folded_singularity_classification(
                fold=1.0, a=bridge_parameters.a, epsilon=epsilon
            )
        ),
        "profile_diagnostics": profile_reports,
        "outer_diagnostics": outer_report,
        "required_before_canard_claim": [
            "compute the relevant finite-parameter slow manifolds in the spatial problem",
            "continue their fold passage or intersection in a parameter family",
            "separate singular, desingularized, and physical spatial time",
            "enclose or resolve the remainder in the maximal-canard parameter curve",
            "measure parameter sensitivity and numerical refinement",
        ],
    }


__all__ = [
    "CANARD_STOP_STATUS",
    "FOLD_PASSAGE_STATUS",
    "OUTER_STATUS",
    "FoldCrossing",
    "critical_manifold_v",
    "desingularized_reduced_field",
    "fast_normal_eigenvalue_squared",
    "folded_linear_product",
    "folded_singularity_classification",
    "maximal_canard_leading_parameter",
    "outer_fold_exclusion_diagnostics",
    "profile_fold_diagnostics",
    "screen_saved_profiles",
]
