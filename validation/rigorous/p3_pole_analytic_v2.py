#!/usr/bin/env python3
"""Exact rational audit of the analytic part of V3 on the frozen v2 box.

This audit intentionally stops before either missing global interface:

* the interval source-window-to-``x=10`` event tube; and
* an explicit regular-singular stable-fibre block with mixed two-jets.

The PASS atoms below are therefore conditional lemmas, not a PASS for either
``V3.SOURCE_TO_POLE`` or ``V3.POLE_TAIL`` in ``obligations.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
BOX_PATH = HERE / "config" / "vdp_box_v2.json"
THEOREM_PATH = REPOSITORY / "van-der-pol" / "POSITIVE_POLE_FINITE_PART.md"
DEFAULT_OUTPUT = HERE / "results" / "vdp_box_v2_p3_pole_analytic.json"


def _fraction(item: dict[str, str]) -> Fraction:
    return Fraction(int(item["numerator"]), int(item["denominator"]))


def _q(value: Fraction) -> dict[str, str]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "decimal": format(float(value), ".17g"),
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def build_certificate() -> dict[str, Any]:
    box = json.loads(BOX_PATH.read_text(encoding="utf-8"))
    _assert(box["box_id"] == "vdp-positive-box-v2", "wrong target box")
    variables = box["variables"]
    r_lo = _fraction(variables["r"]["lower"])
    r_hi = _fraction(variables["r"]["upper"])
    a2_lo = _fraction(variables["a2"]["lower"])
    a2_hi = _fraction(variables["a2"]["upper"])
    eps_lo = _fraction(variables["epsilon"]["lower"])
    eps_hi = _fraction(variables["epsilon"]["upper"])

    _assert((r_lo, r_hi) == (Fraction(1, 100), Fraction(1, 50)),
            "unexpected v2 r interval")
    _assert((a2_lo, a2_hi) == (Fraction(-1, 4), Fraction(1, 4)),
            "unexpected v2 a2 interval")
    _assert((eps_lo, eps_hi) == (Fraction(4, 5), Fraction(6, 5)),
            "unexpected v2 epsilon interval")

    # Exact rational square-root brackets.  No floating-point decision is
    # used in any PASS below.
    sqrt_eps_lo = Fraction(8, 9)
    sqrt_eps_hi = Fraction(11, 10)
    sqrt6_lo = Fraction(12, 5)
    sqrt6_hi = Fraction(5, 2)
    _assert(sqrt_eps_lo**2 <= eps_lo, "invalid lower sqrt(epsilon) bound")
    _assert(sqrt_eps_hi**2 >= eps_hi, "invalid upper sqrt(epsilon) bound")
    _assert(sqrt6_lo**2 <= 6, "invalid lower sqrt(6) bound")
    _assert(sqrt6_hi**2 >= 6, "invalid upper sqrt(6) bound")

    A = max(abs(a2_lo), abs(a2_hi))
    r_p = r_hi
    delta_lo = r_lo**2
    delta_hi = r_hi**2

    # V3 (1): the two only explicit small-radius hypotheses.
    radius_lhs_1 = sqrt_eps_hi * A * r_p**3
    radius_lhs_2 = 2 * A * r_p + sqrt_eps_hi * A**2 * r_p**4
    radius_margin_1 = Fraction(1, 4) - radius_lhs_1
    radius_margin_2 = 1 - radius_lhs_2
    _assert(radius_margin_1 > 0 and radius_margin_2 > 0,
            "the explicit V3 radius hypotheses do not close")

    parameter_perturbation = radius_lhs_1
    a_lower = 1 - parameter_perturbation
    a_upper = 1 + parameter_perturbation
    B_minus_half_lower = Fraction(1, 2) - parameter_perturbation
    c_abs_upper = radius_lhs_2
    b_lower = sqrt_eps_lo * r_lo**2 / 3
    b_upper = sqrt_eps_hi * r_hi**2 / 3
    ell_lower = sqrt6_lo * delta_lo
    ell_upper = sqrt6_hi * delta_hi
    _assert(a_lower > 0, "physical a lower bound is not positive")
    _assert(B_minus_half_lower >= Fraction(1, 4), "B >= 3/4 not proved")
    _assert(c_abs_upper <= 1, "|c| <= 1 not proved")
    _assert(b_lower > 0, "b lower bound is not positive")

    # The coarse cone inequalities printed in (14), sharpened only by the
    # positive b lower bound.  Monotonicity of the bracket in x makes x=10
    # the exact worst boundary point for x >= 10.
    x_gate = Fraction(10)
    cone_yprime_lower = (
        Fraction(1, 4) * x_gate**2 - x_gate + b_lower * x_gate**3
    )
    cone_kprime_lower = x_gate * cone_yprime_lower - x_gate
    cone_yprime_bound_derivative_lower = (
        Fraction(1, 2) * x_gate - 1 + 3 * b_lower * x_gate**2
    )
    cone_kprime_bound_derivative_lower = (
        Fraction(3, 4) * x_gate**2 - 2 * x_gate - 1
        + 4 * b_lower * x_gate**3
    )
    _assert(cone_yprime_lower > 0 and cone_kprime_lower > 0,
            "cone inward inequalities do not close")
    _assert(cone_yprime_bound_derivative_lower > 0,
            "the y' lower polynomial is not increasing from x=10")
    _assert(cone_kprime_bound_derivative_lower > 0,
            "the K' lower polynomial is not increasing from x=10")

    # If the missing event atlas supplies the state margins in V3 (16), the
    # actual v2 coefficient bounds alone retain the two derivative margins.
    entry_y = Fraction(13)
    entry_D = Fraction(26)
    entry_K = Fraction(131)
    actual_gate_yprime_lower = (
        entry_D
        + B_minus_half_lower * x_gate**2
        - c_abs_upper * x_gate
        + b_lower * x_gate**3
    )
    actual_gate_kprime_lower = (
        entry_y**2 + x_gate * actual_gate_yprime_lower - x_gate
    )
    _assert(entry_K > 0, "entry K antecedent must be interior")
    _assert(actual_gate_yprime_lower > 51,
            "the advertised gate y' margin is not retained")
    _assert(actual_gate_kprime_lower > 852,
            "the advertised gate K' margin is not retained")

    # Equation (17) then gives
    # y^2 >= x^4/67500 + 4559/27 > x^4/260^2.
    energy_offset = entry_y**2 - b_lower * x_gate**4 / 2
    _assert(energy_offset > 0, "finite-time tail offset is not positive")
    central_clock_constant = Fraction(260)
    _assert(Fraction(1, central_clock_constant**2) < b_lower / 2,
            "central blow-up time comparison is invalid")
    central_time_from_gate_upper = central_clock_constant / x_gate

    # epsilon^(-1/4) <= 16/15 follows by fourth powers on epsilon >= 4/5.
    eps_quarter_inverse_upper = Fraction(16, 15)
    _assert(Fraction(1, eps_quarter_inverse_upper**4) <= eps_lo,
            "epsilon^(-1/4) rational upper bound is invalid")
    physical_time_from_gate_upper = (
        r_hi * eps_quarter_inverse_upper * central_time_from_gate_upper
    )

    # Exact structural coefficients that do not require a label rectangle or
    # a numerical local stable-manifold chart.
    energy_c4_derivative_abs_lower = 30 * eps_lo * delta_lo**4
    coordinate_leading_determinant_lower = 30 * delta_lo**3
    _assert(energy_c4_derivative_abs_lower > 0,
            "energy/c4 transversality lower bound is not positive")
    _assert(coordinate_leading_determinant_lower > 0,
            "leading coordinate determinant lower bound is not positive")

    return {
        "schema_version": "rfsn-vdp-p3-pole-analytic-v2/1",
        "certificate_id": "vdp-box-v2-p3-pole-analytic",
        "status": "PARTIAL_ANALYTIC_PASS",
        "mathematical_status": "INCONCLUSIVE",
        "claim_bearing": False,
        "target": {
            "box_id": box["box_id"],
            "box_path": str(BOX_PATH.relative_to(REPOSITORY)),
            "box_sha256": _sha256(BOX_PATH),
            "theorem_path": str(THEOREM_PATH.relative_to(REPOSITORY)),
            "theorem_sha256": _sha256(THEOREM_PATH),
            "exact_identification": {
                "A": _q(A),
                "r_p": _q(r_p),
                "r_interval_equals_half_rp_to_rp": r_lo == r_p / 2,
            },
        },
        "rational_square_root_brackets": {
            "sqrt_epsilon": {"lower": _q(sqrt_eps_lo), "upper": _q(sqrt_eps_hi)},
            "sqrt_6": {"lower": _q(sqrt6_lo), "upper": _q(sqrt6_hi)},
        },
        "uniform_parameter_bounds": {
            "delta": {"lower": _q(delta_lo), "upper": _q(delta_hi)},
            "a_and_B": {"lower": _q(a_lower), "upper": _q(a_upper)},
            "B_minus_one_half_lower": _q(B_minus_half_lower),
            "abs_c_upper": _q(c_abs_upper),
            "b": {"lower": _q(b_lower), "upper": _q(b_upper)},
            "ell": {"lower": _q(ell_lower), "upper": _q(ell_upper)},
        },
        "local_lemma_atoms": [
            {
                "id": "V3.POLE.EXPLICIT_RADIUS",
                "status": "PASS",
                "scope": "UNCONDITIONAL_ON_THE_COMPLETE_V2_PARAMETER_BOX",
                "inequalities": {
                    "sqrt_epsilon_plus_A_rp_cubed_lhs": _q(radius_lhs_1),
                    "margin_to_one_quarter": _q(radius_margin_1),
                    "two_A_rp_plus_sqrt_epsilon_plus_A_squared_rp_fourth_lhs": _q(radius_lhs_2),
                    "margin_to_one": _q(radius_margin_2),
                },
            },
            {
                "id": "V3.POLE.CONE_INWARD",
                "status": "PASS",
                "scope": "UNCONDITIONAL_FOR_ALL_PARAMETERS_IN_V2_AND_ALL_STATES_IN_K_MU",
                "domain": "x>=10, y>0, D>=0, K>=0",
                "boundary_lower_bounds": {
                    "y_prime_at_D_zero": _q(cone_yprime_lower),
                    "K_prime_at_K_zero": _q(cone_kprime_lower),
                    "derivative_of_y_prime_lower_polynomial": _q(
                        cone_yprime_bound_derivative_lower
                    ),
                    "derivative_of_K_prime_lower_polynomial": _q(
                        cone_kprime_bound_derivative_lower
                    ),
                },
            },
            {
                "id": "V3.POLE.GATE_MARGIN_IMPLICATION",
                "status": "PASS",
                "scope": "CONDITIONAL_LEMMA_ONLY",
                "antecedent": {
                    "x": _q(x_gate),
                    "y_lower": _q(entry_y),
                    "D_lower": _q(entry_D),
                    "K_lower": _q(entry_K),
                },
                "consequent": {
                    "y_prime_lower": _q(actual_gate_yprime_lower),
                    "margin_above_51": _q(actual_gate_yprime_lower - 51),
                    "K_prime_lower": _q(actual_gate_kprime_lower),
                    "margin_above_852": _q(actual_gate_kprime_lower - 852),
                },
            },
            {
                "id": "V3.POLE.FINITE_TIME_TAIL_IMPLICATION",
                "status": "PASS",
                "scope": "CONDITIONAL_LEMMA_ONLY",
                "antecedent": "the same x=10,y>=13 cone entry",
                "bounds": {
                    "y_squared_offset": _q(energy_offset),
                    "y_lower_formula": "y(x)>x^2/260 for every x>=10",
                    "remaining_central_time_at_x": "xi_b-xi<260/x",
                    "remaining_central_time_from_gate_upper": _q(central_time_from_gate_upper),
                    "epsilon_minus_one_quarter_upper": _q(eps_quarter_inverse_upper),
                    "remaining_physical_time_from_gate_upper": _q(physical_time_from_gate_upper),
                },
            },
            {
                "id": "V3.POLE.REGULAR_SINGULAR_EXACT_STRUCTURE",
                "status": "PASS",
                "scope": "EXACT_FORMULA_LEVEL_ONLY_NOT_A_REMAINDER_ENCLOSURE",
                "normal_spectrum": ["-1", "-4", "1"],
                "label_spectrum": ["0", "0"],
                "admissible_power_roots": ["1", "4"],
                "abs_dG_dc4_lower": _q(energy_c4_derivative_abs_lower),
                "leading_coordinate_determinant_5ell2delta_lower": _q(
                    coordinate_leading_determinant_lower
                ),
            },
        ],
        "parent_obligations": [
            {
                "id": "V3.SOURCE_TO_POLE",
                "status": "INCONCLUSIVE",
                "reason": "No gap-free interval event tube yet carries the complete source phase window to its unique first x=10 hit and proves the entry antecedent.",
            },
            {
                "id": "V3.POLE_TAIL",
                "status": "INCONCLUSIVE",
                "reason": "The exact pole structure and conditional finite-time estimate pass, but no explicit label block, sigma0 contraction, stable-fibre enclosure, coordinate determinant remainder, or mixed-C2 action remainder is certified.",
            },
        ],
        "required_interfaces": [
            {
                "id": "P3.POLE_GATE_EVENT_TUBE",
                "required_output": [
                    "a gap-free cover of (r,a2,epsilon,phi) on v2 times [-0.2,0.2]",
                    "unique first-hit time and state intervals for g=x-10",
                    "strict pre-hit g<0 and hit-speed y>0 enclosures",
                    "gate lower bounds y>=13, D>=26, K>=131",
                    "state and parameter/phase mixed two-jet bounds at the gate",
                ],
            },
            {
                "id": "P3.POLE_LOCAL_END_BLOCK",
                "required_output": [
                    "one explicit downstream section x=M or sigma=sigma0 reached by the entire gate image",
                    "interval bounds for Z0,W0,c4 and a containing label rectangle",
                    "an explicit sigma0 and contraction/remainder constants through mixed external order two",
                    "a positive full coordinate-Jacobian lower bound after its remainder, not only its leading term",
                    "an integrable O_C2 density remainder constant and the resulting action-tail error",
                ],
            },
        ],
        "nonclaims": [
            "The conditional gate and blow-up lemmas do not show that any source orbit reaches the cone.",
            "The exact spectrum, transversality coefficient, and leading determinant do not enclose a local stable manifold or its remainder.",
            "The one-point floating pole scout is not used in any PASS decision.",
            "Neither V3 parent obligation is passed, and no V4--V6 claim follows.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true",
                        help="compare the computed certificate with --output")
    args = parser.parse_args()
    certificate = build_certificate()
    rendered = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("stored P3 pole analytic certificate is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(
        f"{certificate['status']}: V3.SOURCE_TO_POLE=INCONCLUSIVE, "
        "V3.POLE_TAIL=INCONCLUSIVE"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
