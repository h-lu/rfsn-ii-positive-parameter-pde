"""Deterministic floating V5 seed grid on the frozen v2 parameter box.

This module steps from the v2 centre to a ``5 x 9 x 5`` tensor grid by a
fixed nearest-neighbour tree.  At each node it recomputes the existing
energy-preserving central--K1--outer BVP and retains only endpoint data needed
to seed a later interval incidence calculation.  It deliberately saves no
orbit arrays.

The calculation is COMPUTED/E1 evidence.  Finite sampled roots, even when all
of their residual QA passes, neither exclude a fold or root jump between
nodes nor identify or validate the V5 branch.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from numerics.vdp_matched_outer import (
    k1_center_graph_leading_guess,
    outer_seam_coordinates,
)
from numerics.vdp_outer import OuterParameters
from numerics.vdp_p2e_energy_matched import (
    compute_energy_matched_centerline,
)


HERE = Path(__file__).resolve().parent
DEFAULT_RESULT = HERE / "results/vdp_v5_v2_predictor_grid/result.json"

FULL_R = tuple(Fraction(1, 100) + index * Fraction(1, 400) for index in range(5))
FULL_A2 = tuple(Fraction(-1, 4) + index * Fraction(1, 16) for index in range(9))
FULL_EPSILON = tuple(Fraction(4, 5) + index * Fraction(1, 10) for index in range(5))

CENTRAL_PATCH = {
    "Pi": (Fraction(1, 2), Fraction(2, 3)),
    "Omega": (Fraction(1, 32), Fraction(1, 16)),
}
V4_COLLAR = {
    "energy_E_half_width": Fraction(1, 1000),
    "z_upper": Fraction(2, 9),
    "alpha_half_width": Fraction(1, 100_000),
    "beta_half_width": Fraction(1, 100_000),
}
K1_SPECTRAL_CORRIDOR_CANDIDATE = {
    "b_half_width": Fraction(1, 100_000),
    "n_half_width": Fraction(1, 200_000),
}


class PredictorGridError(RuntimeError):
    """A prescribed grid solve failed before producing an accepted seed."""


@dataclass(frozen=True)
class GridSpecification:
    """Exact tensor levels and their centre indices."""

    name: str
    r: tuple[Fraction, ...]
    a2: tuple[Fraction, ...]
    epsilon: tuple[Fraction, ...]

    @property
    def centre(self) -> tuple[int, int, int]:
        return (
            self.r.index(Fraction(3, 200)),
            self.a2.index(Fraction(0)),
            self.epsilon.index(Fraction(1)),
        )

    @property
    def point_count(self) -> int:
        return len(self.r) * len(self.a2) * len(self.epsilon)


FULL_GRID = GridSpecification(
    name="full_5x9x5",
    r=FULL_R,
    a2=FULL_A2,
    epsilon=FULL_EPSILON,
)
COARSE_GRID = GridSpecification(
    name="coarse_3x3x3",
    r=tuple(FULL_R[index] for index in (0, 2, 4)),
    a2=tuple(FULL_A2[index] for index in (0, 4, 8)),
    epsilon=tuple(FULL_EPSILON[index] for index in (0, 2, 4)),
)


def _fraction_label(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _point_id(indices: tuple[int, int, int]) -> str:
    r_index, a2_index, epsilon_index = indices
    return f"r{r_index:02d}_a{a2_index:02d}_e{epsilon_index:02d}"


def _axis_order(size: int, centre: int) -> tuple[int, ...]:
    """Centre, increasing side, then decreasing side."""

    return tuple(
        [centre]
        + list(range(centre + 1, size))
        + list(range(centre - 1, -1, -1))
    )


def deterministic_point_order(
    specification: GridSpecification = FULL_GRID,
) -> tuple[tuple[int, int, int], ...]:
    """Return the fixed neighbour-tree traversal used by the computation."""

    r_centre, a2_centre, epsilon_centre = specification.centre
    order: list[tuple[int, int, int]] = []
    for epsilon_index in _axis_order(len(specification.epsilon), epsilon_centre):
        for r_index in _axis_order(len(specification.r), r_centre):
            for a2_index in _axis_order(len(specification.a2), a2_centre):
                order.append((r_index, a2_index, epsilon_index))
    return tuple(order)


def _axis_predictor(
    *,
    target: int,
    centre: int,
    fixed_indices: tuple[int, int],
    axis: str,
    phases: dict[tuple[int, int, int], float],
) -> tuple[float, tuple[int, int, int], str, list[tuple[int, int, int]]]:
    """Predict along one already constructed coordinate line."""

    def indices(axis_index: int) -> tuple[int, int, int]:
        if axis == "epsilon":
            return fixed_indices[0], fixed_indices[1], axis_index
        if axis == "r":
            return axis_index, fixed_indices[0], fixed_indices[1]
        if axis == "a2":
            return fixed_indices[0], axis_index, fixed_indices[1]
        raise ValueError(f"unknown predictor axis {axis!r}")

    centre_point = indices(centre)
    if target > centre:
        predecessor = indices(target - 1)
        if target == centre + 1:
            return (
                phases[predecessor],
                predecessor,
                "nearest_neighbour",
                [predecessor],
            )
        secondary = indices(target - 2)
        return (
            2.0 * phases[predecessor] - phases[secondary],
            predecessor,
            "two_neighbour_secant",
            [predecessor, secondary],
        )

    predecessor = indices(target + 1)
    if target == centre - 1:
        positive = indices(centre + 1)
        return (
            2.0 * phases[centre_point] - phases[positive],
            predecessor,
            "centre_reflection_from_positive_neighbour",
            [centre_point, positive],
        )
    secondary = indices(target + 2)
    return (
        2.0 * phases[predecessor] - phases[secondary],
        predecessor,
        "two_neighbour_secant",
        [predecessor, secondary],
    )


def _prediction_for_point(
    indices: tuple[int, int, int],
    specification: GridSpecification,
    phases: dict[tuple[int, int, int], float],
) -> tuple[float | None, tuple[int, int, int] | None, str, list[tuple[int, int, int]]]:
    r_index, a2_index, epsilon_index = indices
    r_centre, a2_centre, epsilon_centre = specification.centre
    if indices == specification.centre:
        return None, None, "frozen_center_seed", []
    if a2_index != a2_centre:
        return _axis_predictor(
            target=a2_index,
            centre=a2_centre,
            fixed_indices=(r_index, epsilon_index),
            axis="a2",
            phases=phases,
        )
    if r_index != r_centre:
        return _axis_predictor(
            target=r_index,
            centre=r_centre,
            fixed_indices=(a2_centre, epsilon_index),
            axis="r",
            phases=phases,
        )
    return _axis_predictor(
        target=epsilon_index,
        centre=epsilon_centre,
        fixed_indices=(r_centre, a2_centre),
        axis="epsilon",
        phases=phases,
    )


def _signed_interval_margin(value: float, lower: Fraction, upper: Fraction) -> float:
    return min(value - float(lower), float(upper) - value)


def _summarize_point(
    *,
    indices: tuple[int, int, int],
    specification: GridSpecification,
    result: dict[str, Any],
    arrays: dict[str, np.ndarray],
    phase_predictor: float | None,
    predecessor: tuple[int, int, int] | None,
    predictor_method: str,
    predictor_support: Iterable[tuple[int, int, int]],
) -> dict[str, Any]:
    r_index, a2_index, epsilon_index = indices
    exact_r = specification.r[r_index]
    exact_a2 = specification.a2[a2_index]
    exact_epsilon = specification.epsilon[epsilon_index]
    parameters = OuterParameters(
        r=float(exact_r),
        a2=float(exact_a2),
        epsilon=float(exact_epsilon),
    )
    k1_state = arrays["k1_state_Pi_Omega_q1"]
    outer_state = arrays["outer_state_beta_alpha"]
    central_pi = float(k1_state[0, 0])
    central_omega = float(k1_state[1, 0])
    outer_pi_scaled = float(k1_state[0, -1])
    outer_omega_scaled = float(k1_state[1, -1])
    outer_beta = float(outer_state[0, 0])
    outer_alpha = float(outer_state[1, 0])
    r1_central = float(
        parameters.r * np.sqrt(4.0 + parameters.r * parameters.a2)
    )
    leading = k1_center_graph_leading_guess(
        np.array([r1_central], dtype=np.float64), parameters
    )[:, 0]
    reference_pi = float(leading[0])
    reference_omega = float(leading[1])
    spectral_lambda = float(
        np.sqrt(
            np.sqrt(parameters.epsilon)
            * (2.0 + np.sqrt(parameters.epsilon) * r1_central**2)
        )
    )
    spectral_b = 0.5 * (
        (central_pi - reference_pi)
        - (central_omega - reference_omega) / spectral_lambda
    )
    spectral_n = 0.5 * (
        (central_pi - reference_pi)
        + (central_omega - reference_omega) / spectral_lambda
    )
    energy_h = float(result["energy_h"])
    energy_e = float(
        parameters.epsilon**2.5 * parameters.r**6 * energy_h
    )
    z_r, q_r = outer_seam_coordinates(parameters, outer_r1=2.0)
    patch_margins = {
        "Pi": _signed_interval_margin(
            central_pi, *CENTRAL_PATCH["Pi"]
        ),
        "Omega": _signed_interval_margin(
            central_omega, *CENTRAL_PATCH["Omega"]
        ),
    }
    collar_margins = {
        "energy_E": float(V4_COLLAR["energy_E_half_width"]) - abs(energy_e),
        "z_upper": float(V4_COLLAR["z_upper"]) - z_r,
        "alpha": float(V4_COLLAR["alpha_half_width"]) - abs(outer_alpha),
        "beta": float(V4_COLLAR["beta_half_width"]) - abs(outer_beta),
    }
    diagnostics = result["diagnostics"]
    return {
        "point_id": _point_id(indices),
        "grid_indices": {
            "r": r_index,
            "a2": a2_index,
            "epsilon": epsilon_index,
        },
        "parameters_exact": {
            "r": _fraction_label(exact_r),
            "a2": _fraction_label(exact_a2),
            "epsilon": _fraction_label(exact_epsilon),
        },
        "parameters": {
            "r": parameters.r,
            "a2": parameters.a2,
            "epsilon": parameters.epsilon,
        },
        "continuation": {
            "predecessor": None if predecessor is None else _point_id(predecessor),
            "phase_predictor": (
                float(result["initial_phase_predictor"])
                if phase_predictor is None
                else float(phase_predictor)
            ),
            "method": predictor_method,
            "support": [_point_id(point) for point in predictor_support],
        },
        "source_phase": float(result["source_phase"]),
        "energy_H": energy_h,
        "energy_E": energy_e,
        "central_U_minus_4": {
            "r1": r1_central,
            "Pi": central_pi,
            "Omega": central_omega,
            "leading_reference": {
                "Pi": reference_pi,
                "Omega": reference_omega,
            },
            "spectral_coordinates": {
                "lambda": spectral_lambda,
                "b": spectral_b,
                "n": spectral_n,
            },
        },
        "outer_R_2": {
            "z": z_r,
            "Q": q_r,
            "Pi": outer_pi_scaled,
            "Omega": outer_omega_scaled,
            "alpha": outer_alpha,
            "beta": outer_beta,
        },
        "signed_margins": {
            "central_patch": {
                **patch_margins,
                "minimum": min(patch_margins.values()),
            },
            "V4_outer_collar": {
                **collar_margins,
                "minimum": min(collar_margins.values()),
            },
        },
        "qa": dict(result["qa"]),
        "qa_diagnostics": {
            "solver_rms_residual_max": float(
                diagnostics["solver_rms_residual_max"]
            ),
            "boundary_residual_inf": float(diagnostics["boundary_residual_inf"]),
            "central_energy_abs_max": float(
                diagnostics["central_energy_abs_max"]
            ),
            "central_k1_state_seam_residual_inf": float(
                diagnostics["central_k1_state_seam_residual_inf"]
            ),
            "k1_outer_normal_seam_residual_inf": float(
                diagnostics["k1_outer_normal_seam_residual_inf"]
            ),
            "same_section_root_residual_abs": abs(
                float(diagnostics["same_section_root_residual"])
            ),
            "minimum_k1_Pi": float(diagnostics["minimum_k1_pi_scaled"]),
            "minimum_k1_q1": float(diagnostics["minimum_k1_q1"]),
            "minimum_outer_pi": float(diagnostics["minimum_outer_pi"]),
        },
    }


def _hull(values: Iterable[float]) -> list[float]:
    data = tuple(float(value) for value in values)
    return [min(data), max(data)]


def _aggregate(points: list[dict[str, Any]]) -> dict[str, Any]:
    b_hull = _hull(
        point["central_U_minus_4"]["spectral_coordinates"]["b"]
        for point in points
    )
    n_hull = _hull(
        point["central_U_minus_4"]["spectral_coordinates"]["n"]
        for point in points
    )
    return {
        "all_existing_qa_pass": all(all(point["qa"].values()) for point in points),
        "source_phase_hull": _hull(point["source_phase"] for point in points),
        "energy_H_hull": _hull(point["energy_H"] for point in points),
        "energy_E_hull": _hull(point["energy_E"] for point in points),
        "central_U_minus_4": {
            "Pi_hull": _hull(point["central_U_minus_4"]["Pi"] for point in points),
            "Omega_hull": _hull(
                point["central_U_minus_4"]["Omega"] for point in points
            ),
            "lambda_hull": _hull(
                point["central_U_minus_4"]["spectral_coordinates"]["lambda"]
                for point in points
            ),
            "b_hull": b_hull,
            "n_hull": n_hull,
            "sampled_symmetric_half_widths": {
                "b": max(abs(b_hull[0]), abs(b_hull[1])),
                "n": max(abs(n_hull[0]), abs(n_hull[1])),
                "interpretation": (
                    "sampled design lower bounds only; strict K1 corridor half-widths "
                    "must include interval and inter-node allowances"
                ),
            },
            "next_strict_corridor_candidate": {
                "b_half_width_exact": _fraction_label(
                    K1_SPECTRAL_CORRIDOR_CANDIDATE["b_half_width"]
                ),
                "n_half_width_exact": _fraction_label(
                    K1_SPECTRAL_CORRIDOR_CANDIDATE["n_half_width"]
                ),
                "sampled_b_margin": float(
                    K1_SPECTRAL_CORRIDOR_CANDIDATE["b_half_width"]
                ) - max(abs(b_hull[0]), abs(b_hull[1])),
                "sampled_n_margin": float(
                    K1_SPECTRAL_CORRIDOR_CANDIDATE["n_half_width"]
                ) - max(abs(n_hull[0]), abs(n_hull[1])),
                "status": "DESIGN_CANDIDATE_NOT_INTERVAL_VALIDATED",
            },
        },
        "outer_R_2": {
            key + "_hull": _hull(point["outer_R_2"][key] for point in points)
            for key in ("Pi", "Omega", "alpha", "beta", "z", "Q")
        },
        "minimum_signed_central_patch_margin": min(
            point["signed_margins"]["central_patch"]["minimum"]
            for point in points
        ),
        "minimum_signed_V4_outer_collar_margin": min(
            point["signed_margins"]["V4_outer_collar"]["minimum"]
            for point in points
        ),
        "minimum_individual_margins": {
            family: {
                coordinate: min(
                    point["signed_margins"][family][coordinate]
                    for point in points
                )
                for coordinate in point0["signed_margins"][family]
                if coordinate != "minimum"
            }
            for family, point0 in (
                ("central_patch", points[0]),
                ("V4_outer_collar", points[0]),
            )
        },
        "max_qa_diagnostics": {
            key: max(point["qa_diagnostics"][key] for point in points)
            for key in (
                "solver_rms_residual_max",
                "boundary_residual_inf",
                "central_energy_abs_max",
                "central_k1_state_seam_residual_inf",
                "k1_outer_normal_seam_residual_inf",
                "same_section_root_residual_abs",
            )
        },
    }


def compute_predictor_grid(
    specification: GridSpecification = FULL_GRID,
) -> dict[str, Any]:
    """Compute the prescribed grid and return its JSON-ready report."""

    phases: dict[tuple[int, int, int], float] = {}
    points: list[dict[str, Any]] = []
    order = deterministic_point_order(specification)
    for ordinal, indices in enumerate(order, start=1):
        phase_predictor, predecessor, method, support = _prediction_for_point(
            indices, specification, phases
        )
        r_index, a2_index, epsilon_index = indices
        parameters = OuterParameters(
            r=float(specification.r[r_index]),
            a2=float(specification.a2[a2_index]),
            epsilon=float(specification.epsilon[epsilon_index]),
        )
        try:
            result, arrays = compute_energy_matched_centerline(
                parameters,
                initial_phase=phase_predictor,
                raise_on_qa=False,
            )
        except Exception as error:
            raise PredictorGridError(
                f"{_point_id(indices)} failed from {method}: "
                f"{type(error).__name__}: {error}"
            ) from error
        if not result["status"].endswith("SUCCESS") or not all(result["qa"].values()):
            failed = [name for name, passed in result["qa"].items() if not passed]
            raise PredictorGridError(
                f"{_point_id(indices)} failed existing QA: {', '.join(failed)}"
            )
        point = _summarize_point(
            indices=indices,
            specification=specification,
            result=result,
            arrays=arrays,
            phase_predictor=phase_predictor,
            predecessor=predecessor,
            predictor_method=method,
            predictor_support=support,
        )
        phases[indices] = point["source_phase"]
        points.append(point)
        print(
            f"[{ordinal:03d}/{len(order):03d}] {point['point_id']} "
            f"phi={point['source_phase']:.12f} H={point['energy_H']:.3e}",
            flush=True,
        )

    aggregate = _aggregate(points)
    return {
        "schema_version": "rfsn-vdp-v5-v2-predictor-grid/1",
        "status": "V2_V5_PREDICTOR_GRID_COMPUTED",
        "evidence_status": "COMPUTED/E1_NON_RIGOROUS",
        "claim_bearing": False,
        "grid": {
            "name": specification.name,
            "shape": [len(specification.r), len(specification.a2), len(specification.epsilon)],
            "point_count": specification.point_count,
            "levels_exact": {
                "r": [_fraction_label(value) for value in specification.r],
                "a2": [_fraction_label(value) for value in specification.a2],
                "epsilon": [
                    _fraction_label(value) for value in specification.epsilon
                ],
            },
            "traversal": (
                "epsilon centre/positive/negative; within each layer r "
                "centre/positive/negative; within each line a2 "
                "centre/positive/negative"
            ),
            "continuation_policy": (
                "nearest-neighbour first step, two-neighbour secant thereafter, "
                "and centre reflection for each first negative step"
            ),
        },
        "fixed_sections": {
            "central": "U=-4",
            "outer": "resolved K1 R=2",
        },
        "central_patch": {
            key: [_fraction_label(bound) for bound in bounds]
            for key, bounds in CENTRAL_PATCH.items()
        },
        "V4_outer_collar": {
            key: _fraction_label(value) for key, value in V4_COLLAR.items()
        },
        "spectral_coordinate_definition": {
            "lambda": "sqrt(sqrt(epsilon)*(2+sqrt(epsilon)*r1^2))",
            "b": "0.5*((Pi-Pi_ref)-(Omega-Omega_ref)/lambda)",
            "n": "0.5*((Pi-Pi_ref)+(Omega-Omega_ref)/lambda)",
            "reference": "k1_center_graph_leading_guess at the U=-4 r1 value",
        },
        "aggregate": aggregate,
        "point_order": [point["point_id"] for point in points],
        "points": points,
        "saved_orbit_arrays": False,
        "reproduction": "python3 -m numerics.vdp_v5_v2_predictor_grid",
        "nonclaim": (
            "This finite sampled root grid is only a deterministic seed set. "
            "It cannot exclude an interior parameter fold or root jump, identify "
            "one global V5 branch, enclose the V5 incidence root, or prove V5."
        ),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--coarse27",
        action="store_true",
        help="run only the endpoint/centre 3 x 3 x 3 diagnostic grid",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RESULT,
        help="JSON result path",
    )
    return parser.parse_args()


def main() -> None:
    arguments = _parse_args()
    specification = COARSE_GRID if arguments.coarse27 else FULL_GRID
    report = compute_predictor_grid(specification)
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(report["status"])
    print(arguments.output)


if __name__ == "__main__":
    main()
