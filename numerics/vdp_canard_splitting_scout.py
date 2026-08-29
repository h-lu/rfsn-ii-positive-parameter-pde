"""Fixed-parameter surrogate splitting scout for the van der Pol canard.

This module tests whether the reversible splitting proposed in Issue #13 is
numerically usable at ``(r, epsilon)=(0.08, 1)``.  It deliberately does not
construct a finite-parameter saddle slow manifold.

The central-chart field is

    u' = p,
    p' = u**2 - v + r**2*u**3/3,
    v' = q,
    q' = u - r*a2.

Appendix C of the published Vo--Doelman--Kaper paper (Appendix E in arXiv v1)
gives a formal perturbation of its algebraic canard.  We set the free formal
phase parameters to zero, truncate that jet,
and project only its q-coordinate onto the exact zero-energy surface.  Starting
at ``y=-Y``, we integrate the exact field to the first increasing ``p=0`` hit
and record ``S=q`` there.  A zero of this *surrogate* splitting is a useful
candidate for a later invariant-manifold BVP.  It is not a maximal-canard
certificate because the projected formal entry is not known to lie on the
finite-r saddle slow manifold.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp
from scipy.optimize import brentq


Array = NDArray[np.float64]

EVIDENCE_STATUS = "COMPUTED/E1_SURROGATE_SPLITTING_SCOUT"
BRANCH_STATUS = "GO_FOR_CANDIDATE_GENERATION_ONLY"
CANARD_STATUS = "INCONCLUSIVE_MISSING_INVARIANT_SLOW_MANIFOLD_ENTRY"
C4_STATUS = "INCONCLUSIVE_EXACT_HIGH_WINDING_EDGE_UNAVAILABLE"


@dataclass(frozen=True)
class ScoutConfiguration:
    r: float = 0.08
    epsilon: float = 1.0
    a2_min: float = -1.0 / 80.0
    a2_max: float = 0.0
    comparison_times: tuple[float, ...] = (1.0, 2.0, 3.0, 4.0)
    truncation_orders: tuple[int, ...] = (2, 3)
    derivative_step: float = 1.0e-5
    rtol: float = 1.0e-11
    atol: float = 1.0e-13
    max_step: float = 1.0e-2

    @property
    def leading_a2(self) -> float:
        return -5.0 * np.sqrt(self.epsilon) * self.r / 48.0


def central_field(state: Array, *, r: float, a2: float) -> Array:
    """Exact epsilon=1 central-chart vector field."""

    u, p, v, q = np.asarray(state, dtype=np.float64)
    return np.asarray(
        [p, u * u - v + (r * r / 3.0) * u**3, q, u - r * a2],
        dtype=np.float64,
    )


def central_hamiltonian(state: Array, *, r: float, a2: float) -> float:
    """Exact shifted central Hamiltonian H2 for epsilon=1."""

    u, p, v, q = np.asarray(state, dtype=np.float64)
    return float(
        0.5 * (p * p - q * q)
        + (u - r * a2) * v
        - u**3 / 3.0
        - r * r * u**4 / 12.0
    )


def formal_canard_jet(
    y: float, *, r: float, a2: float, order: int
) -> Array:
    """Return the published Appendix-C formal canard through order r**``order``.

    The free coefficients ``chi_21``, ``chi_22``, and ``chi_23`` are set to
    zero as a formal phase convention; this does not turn the truncated series
    into an invariant manifold.
    """

    if order not in (0, 1, 2, 3):
        raise ValueError("formal truncation order must be 0, 1, 2, or 3")
    y2 = y * y
    u = y2 / 12.0
    p = y / 6.0
    v = y2 * y2 / 144.0 - 1.0 / 6.0
    q = y2 * y / 36.0

    if order >= 1:
        u += r * (3.0 * a2 / 2.0)
        v += r * (a2 * y2 / 4.0)
        q += r * (a2 * y / 2.0)
    if order >= 2:
        u += r**2 * (5.0 / 96.0 - 5.0 * y2 * y2 / 3456.0)
        p += r**2 * (-5.0 * y2 * y / 864.0)
        v += r**2 * (
            9.0 * a2 * a2 / 4.0
            + 5.0 * y2 / 192.0
            - y2**3 / 20736.0
        )
        q += r**2 * (5.0 * y / 96.0 - y2 * y2 * y / 3456.0)
    if order >= 3:
        u += r**3 * (-7.0 * a2 * y2 / 96.0)
        p += r**3 * (-7.0 * a2 * y / 48.0)
        v += r**3 * (29.0 * a2 / 96.0 - 7.0 * a2 * y2 * y2 / 1152.0)
        q += r**3 * (-7.0 * a2 * y2 * y / 288.0)
    return np.asarray([u, p, v, q], dtype=np.float64)


def zero_energy_projected_entry(
    y: float, *, r: float, a2: float, order: int
) -> Array:
    """Project the formal entry to H2=0 by changing q only.

    The sign is selected to agree with the negative-y half of the algebraic
    canard.  This projection is an explicit scout convention, not an invariant
    slow-manifold construction.
    """

    state = formal_canard_jet(y, r=r, a2=a2, order=order)
    u, p, v, _q = state
    radicand = (
        p * p
        + 2.0 * (u - r * a2) * v
        - 2.0 * u**3 / 3.0
        - r * r * u**4 / 6.0
    )
    if not np.isfinite(radicand) or radicand <= 0.0:
        raise ValueError(f"zero-energy q radicand is not positive: {radicand}")
    state[3] = float(np.copysign(np.sqrt(radicand), y))
    return state


@dataclass(frozen=True)
class SplittingEvaluation:
    a2: float
    comparison_time: float
    order: int
    splitting: float
    event_time: float
    event_state: tuple[float, float, float, float]
    event_p_derivative: float
    entry_state: tuple[float, float, float, float]
    entry_hamiltonian_abs: float
    hamiltonian_drift: float
    entry_curve_defect_inf: float


def _entry_curve_defect(
    y: float, *, r: float, a2: float, order: int
) -> float:
    step = 1.0e-6
    left = zero_energy_projected_entry(
        y - step, r=r, a2=a2, order=order
    )
    right = zero_energy_projected_entry(
        y + step, r=r, a2=a2, order=order
    )
    derivative = (right - left) / (2.0 * step)
    field = central_field(
        zero_energy_projected_entry(y, r=r, a2=a2, order=order),
        r=r,
        a2=a2,
    )
    return float(np.max(np.abs(derivative - field)))


def evaluate_splitting(
    a2: float,
    *,
    comparison_time: float,
    order: int,
    configuration: ScoutConfiguration,
) -> SplittingEvaluation:
    """Integrate to the first increasing p=0 hit and return S=q."""

    if configuration.epsilon != 1.0:
        raise ValueError("the v1 scout is frozen to epsilon=1")
    if comparison_time <= 0.0:
        raise ValueError("comparison_time must be positive")
    entry_y = -float(comparison_time)
    initial = zero_energy_projected_entry(
        entry_y, r=configuration.r, a2=a2, order=order
    )

    def event(_time: float, state: Array) -> float:
        return float(state[1])

    event.direction = 1.0  # type: ignore[attr-defined]
    event.terminal = True  # type: ignore[attr-defined]
    integration = solve_ivp(
        lambda _time, state: central_field(
            state, r=configuration.r, a2=a2
        ),
        (0.0, 2.0 * comparison_time + 5.0),
        initial,
        events=event,
        method="DOP853",
        rtol=configuration.rtol,
        atol=configuration.atol,
        max_step=configuration.max_step,
    )
    if not integration.success:
        raise RuntimeError(integration.message)
    if integration.t_events[0].size != 1:
        raise RuntimeError("the increasing p=0 first hit was not found uniquely")
    event_time = float(integration.t_events[0][0])
    endpoint = np.asarray(integration.y_events[0][0], dtype=np.float64)
    endpoint_field = central_field(endpoint, r=configuration.r, a2=a2)
    if endpoint_field[1] <= 0.0:
        raise RuntimeError("p=0 event lacks the required positive crossing speed")
    energies = np.asarray(
        [
            central_hamiltonian(column, r=configuration.r, a2=a2)
            for column in integration.y.T
        ]
    )
    return SplittingEvaluation(
        a2=float(a2),
        comparison_time=float(comparison_time),
        order=int(order),
        splitting=float(endpoint[3]),
        event_time=event_time,
        event_state=tuple(float(value) for value in endpoint),
        event_p_derivative=float(endpoint_field[1]),
        entry_state=tuple(float(value) for value in initial),
        entry_hamiltonian_abs=abs(
            central_hamiltonian(initial, r=configuration.r, a2=a2)
        ),
        hamiltonian_drift=float(np.ptp(energies)),
        entry_curve_defect_inf=_entry_curve_defect(
            entry_y, r=configuration.r, a2=a2, order=order
        ),
    )


def _evaluation_record(evaluation: SplittingEvaluation) -> dict[str, Any]:
    return {
        "a2": evaluation.a2,
        "comparison_time_Y": evaluation.comparison_time,
        "formal_truncation_order": evaluation.order,
        "surrogate_splitting_q_at_first_p_zero": evaluation.splitting,
        "event_time": evaluation.event_time,
        "event_state": list(evaluation.event_state),
        "event_p_derivative": evaluation.event_p_derivative,
        "entry_state": list(evaluation.entry_state),
        "entry_hamiltonian_abs": evaluation.entry_hamiltonian_abs,
        "hamiltonian_drift": evaluation.hamiltonian_drift,
        "entry_curve_defect_inf": evaluation.entry_curve_defect_inf,
    }


def _root_row(
    *,
    comparison_time: float,
    order: int,
    configuration: ScoutConfiguration,
) -> dict[str, Any]:
    left = evaluate_splitting(
        configuration.a2_min,
        comparison_time=comparison_time,
        order=order,
        configuration=configuration,
    )
    right = evaluate_splitting(
        configuration.a2_max,
        comparison_time=comparison_time,
        order=order,
        configuration=configuration,
    )
    row: dict[str, Any] = {
        "comparison_time_Y": comparison_time,
        "formal_truncation_order": order,
        "left_endpoint": _evaluation_record(left),
        "right_endpoint": _evaluation_record(right),
        "sign_change_on_frozen_a2_interval": bool(
            left.splitting * right.splitting < 0.0
        ),
        "root": None,
    }
    if not row["sign_change_on_frozen_a2_interval"]:
        return row

    def scalar(value: float) -> float:
        return evaluate_splitting(
            value,
            comparison_time=comparison_time,
            order=order,
            configuration=configuration,
        ).splitting

    root = float(
        brentq(
            scalar,
            configuration.a2_min,
            configuration.a2_max,
            xtol=2.0e-13,
            rtol=2.0e-13,
        )
    )
    root_evaluation = evaluate_splitting(
        root,
        comparison_time=comparison_time,
        order=order,
        configuration=configuration,
    )
    step = configuration.derivative_step
    derivative = (scalar(root + step) - scalar(root - step)) / (2.0 * step)
    row["root"] = {
        **_evaluation_record(root_evaluation),
        "centered_parameter_derivative": float(derivative),
        "offset_from_published_leading_a2": float(
            root - configuration.leading_a2
        ),
    }
    return row


def build_report(
    configuration: ScoutConfiguration | None = None,
) -> dict[str, Any]:
    """Run the fixed-r scout and return a JSON-safe evidence record."""

    config = configuration or ScoutConfiguration()
    rows = [
        _root_row(
            comparison_time=comparison_time,
            order=order,
            configuration=config,
        )
        for comparison_time in config.comparison_times
        for order in config.truncation_orders
    ]
    core_order_three = [
        float(row["root"]["a2"])
        for row in rows
        if row["formal_truncation_order"] == 3
        and row["comparison_time_Y"] in (1.0, 2.0, 3.0)
        and row["root"] is not None
    ]
    order_pairs: list[dict[str, float]] = []
    for comparison_time in config.comparison_times:
        roots = {
            int(row["formal_truncation_order"]): float(row["root"]["a2"])
            for row in rows
            if row["comparison_time_Y"] == comparison_time
            and row["root"] is not None
        }
        if 2 in roots and 3 in roots:
            order_pairs.append(
                {
                    "comparison_time_Y": comparison_time,
                    "order_2_root": roots[2],
                    "order_3_root": roots[3],
                    "absolute_order_shift": abs(roots[3] - roots[2]),
                }
            )

    cluster = {
        "definition": (
            "descriptive post-scout range of order-3 surrogate roots at "
            "Y=1,2,3; not an enclosure"
        ),
        "minimum": min(core_order_three),
        "maximum": max(core_order_three),
        "width": max(core_order_three) - min(core_order_three),
        "midpoint": 0.5 * (max(core_order_three) + min(core_order_three)),
    }
    return {
        "schema_version": "vdp-canard-splitting-scout/1",
        "evidence_status": EVIDENCE_STATUS,
        "claim_bearing": False,
        "parameters": {
            "r": config.r,
            "epsilon": config.epsilon,
            "a2_interval": [config.a2_min, config.a2_max],
        },
        "published_leading_a2": config.leading_a2,
        "splitting_definition": (
            "S_Y^[m](a2)=q at the first increasing p=0 hit, starting from "
            "the order-m formal jet from published Appendix C (Appendix E "
            "in arXiv v1) at y=-Y after q-only exact "
            "zero-energy projection"
        ),
        "rows": rows,
        "descriptive_order_3_core_cluster": cluster,
        "truncation_sensitivity": order_pairs,
        "decision": {
            "branch_construction_status": BRANCH_STATUS,
            "finite_parameter_maximal_canard_status": CANARD_STATUS,
            "current_sample_a2_zero_classification": "INCONCLUSIVE",
            "high_winding_connection_status": C4_STATUS,
            "reason": (
                "The exact flow, first-hit event, energy level, and scalar root "
                "are numerically well posed, but the initial point is a "
                "projected finite formal jet rather than a point on a computed "
                "finite-r invariant saddle slow manifold. Root drift under Y "
                "and truncation changes therefore cannot be promoted to a "
                "finite-parameter coincidence graph."
            ),
            "next_mathematical_object": (
                "A branch-identified finite-r saddle-slow zero-energy trace on "
                "a fixed normally hyperbolic entry section, with parameter "
                "derivatives; then evaluate the same first-hit splitting."
            ),
        },
        "nonclaims": [
            "The descriptive root range is not an error bar or interval enclosure.",
            "The projected formal entry is not a validated invariant slow manifold.",
            "A surrogate zero does not identify a maximal canard.",
            "No classification of (r,a2,epsilon)=(0.08,0,1) is proved.",
            "No exact (+,2,+) high-winding branch is identified or connected.",
            "No interval arithmetic is used.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent
        / "results"
        / "vdp_canard_splitting_scout"
        / "fixed_r_report.json",
    )
    arguments = parser.parse_args()
    report = build_report()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report["decision"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
