#!/usr/bin/env python3
"""Design-only algebraic composition for the P2c homoclinic tails.

This scout consumes archived P2b/P2bK binary64 upper endpoints and a small
root-jet summary.  It performs no ODE integration and is not a certificate or
an independent replay.  Every arithmetic bound below is a nonnegative exact
Fraction; decimal values in the output are labelled as approximations only.

Expected root-summary schema::

  {
    "schema_version": "rfsn-vdp-p2c-root-jet-summary/1",
    "bound_semantics": "componentwise-absolute-upper-binary64-hex",
    "ordered_normalized_parameters":
      ["theta_r", "theta_a", "theta_epsilon"],
    "ordered_symmetric_pairs": [
      ["theta_r", "theta_r"],
      ["theta_r", "theta_a"],
      ["theta_r", "theta_epsilon"],
      ["theta_a", "theta_a"],
      ["theta_a", "theta_epsilon"],
      ["theta_epsilon", "theta_epsilon"]
    ],
    "half_time_upper_hex": "0x...p...",
    "phase_first_abs_upper_hex": ["0x...p...", "...", "..."],
    "time_first_abs_upper_hex": ["0x...p...", "...", "..."],
    "phase_second_abs_upper_hex": ["0x...p...", "... six entries ..."],
    "time_second_abs_upper_hex": ["0x...p...", "... six entries ..."]
  }

The component bounds are aggregated by exact squared-norm comparisons against
short rational Euclidean/Frobenius upper bounds.  No floating square root is
used in a proof gate.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT_SCHEMA = "rfsn-vdp-p2c-root-jet-summary/1"
OUTPUT_SCHEMA = "rfsn-vdp-p2c-tail-composition-scout/1"
BOUND_SEMANTICS = "componentwise-absolute-upper-binary64-hex"
PARAMETERS = ["theta_r", "theta_a", "theta_epsilon"]
SYMMETRIC_PAIRS = [
    ["theta_r", "theta_r"],
    ["theta_r", "theta_a"],
    ["theta_r", "theta_epsilon"],
    ["theta_a", "theta_a"],
    ["theta_a", "theta_epsilon"],
    ["theta_epsilon", "theta_epsilon"],
]

RADIUS = Fraction(1, 100)
LOCAL_WEIGHT = Fraction(1, 4)
TAIL_WEIGHT = Fraction(1, 5)
TAIL_CUT = Fraction(11)
TIME_GAP = Fraction(1)
DECAY_FACTOR = Fraction(4, 5)
SHIFT_EXPONENTIAL_UPPER = Fraction(27)
FIRST_ORIGINAL_PARAMETER_SCALE = Fraction(25)
SECOND_ORIGINAL_PARAMETER_SCALE = Fraction(625)
PHASE_FIRST_NORM_UPPER = Fraction(621, 500)
TIME_FIRST_NORM_UPPER = Fraction(206, 125)
PHASE_SECOND_NORM_UPPER = Fraction(39059, 1000)
TIME_SECOND_NORM_UPPER = Fraction(109163, 1000)
ROOT_REPOSITORY_COMMIT = "0f35363264d29a8b4b3b39ab10317273aff35fab"
ROOT_SOURCE_SHA256 = "d3fe590fd64da02e18941d32e8d43a3b50e018f37d59513e37a41d1d32cf7a2f"
ROOT_LOG_SHA256 = "b503e777183e6a5f759978b081828b70119bbfb95f48e643649857a89cace969"


class InputError(ValueError):
    """The input does not satisfy the scout's explicit interface."""


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise InputError(f"top-level JSON value in {path} must be an object")
    return value


def nested(value: dict[str, Any], dotted_path: str) -> Any:
    current: Any = value
    for key in dotted_path.split("."):
        if not isinstance(current, dict) or key not in current:
            raise InputError(f"missing required field {dotted_path}")
        current = current[key]
    return current


def fraction_from_hex(text: Any, label: str) -> Fraction:
    if not isinstance(text, str):
        raise InputError(f"{label} must be a binary64 hexadecimal string")
    try:
        value = float.fromhex(text)
    except ValueError as exc:
        raise InputError(f"invalid binary64 hexadecimal value for {label}") from exc
    if not math.isfinite(value) or value < 0.0:
        raise InputError(f"{label} must be finite and nonnegative")
    return Fraction.from_float(value)


def archived_upper(value: dict[str, Any], dotted_path: str) -> Fraction:
    enclosure = nested(value, dotted_path)
    if not isinstance(enclosure, dict):
        raise InputError(f"{dotted_path} must be an enclosure object")
    if enclosure.get("endpoint_format") != "IEEE754_BINARY64_HEX":
        raise InputError(f"{dotted_path} has an unsupported endpoint format")
    return fraction_from_hex(enclosure.get("upper_hex"), dotted_path + ".upper_hex")


def archived_contains(
    value: dict[str, Any], dotted_path: str, exact: Fraction
) -> bool:
    enclosure = nested(value, dotted_path)
    if not isinstance(enclosure, dict):
        raise InputError(f"{dotted_path} must be an enclosure object")
    if enclosure.get("endpoint_format") != "IEEE754_BINARY64_HEX":
        raise InputError(f"{dotted_path} has an unsupported endpoint format")
    lower = fraction_from_hex(enclosure.get("lower_hex"), dotted_path + ".lower_hex")
    upper = fraction_from_hex(enclosure.get("upper_hex"), dotted_path + ".upper_hex")
    return lower <= exact <= upper


def root_hex_list(summary: dict[str, Any], key: str, length: int) -> list[Fraction]:
    values = summary.get(key)
    if not isinstance(values, list) or len(values) != length:
        raise InputError(f"{key} must contain exactly {length} entries")
    return [fraction_from_hex(value, f"{key}[{index}]") for index, value in enumerate(values)]


def first_norm_squared_upper(values: list[Fraction]) -> Fraction:
    return sum((value * value for value in values), Fraction(0))


def second_frobenius_squared_upper(values: list[Fraction]) -> Fraction:
    # Pair order is rr, ra, re, aa, ae, ee.  The full ordered Hessian has
    # both copies of each off-diagonal entry.
    return (
        values[0] * values[0]
        + 2 * values[1] * values[1]
        + 2 * values[2] * values[2]
        + values[3] * values[3]
        + 2 * values[4] * values[4]
        + values[5] * values[5]
    )


def require_norm_contracts(p2b: dict[str, Any], p2bk: dict[str, Any]) -> None:
    expected_p2b = {
        "jet_tensor_norm": "labelled-multilinear-operator",
        "moving_state_norm": "max-of-two-euclidean-blocks",
        "physical_state_norm": "euclidean",
    }
    p2b_norm = nested(p2b, "raw_probe.coordinate_composition")
    if not isinstance(p2b_norm, dict):
        raise InputError("P2b coordinate_composition must be an object")
    for key, expected in expected_p2b.items():
        if p2b_norm.get(key) != expected:
            raise InputError(
                f"incompatible P2b norm contract {key}: "
                f"expected {expected!r}, found {p2b_norm.get(key)!r}"
            )

    expected_p2bk = {
        "scalar_first_parameter_norm": "euclidean-on-R3",
        "scalar_second_parameter_norm": "full-3x3-frobenius",
        "matrix_first_parameter_norm": "output-parameter-hilbert-schmidt",
        "matrix_second_parameter_norm": "output-full-ordered-parameter-hilbert-schmidt",
        "true_source_jet_norm": "physical-output-labelled-multilinear-hilbert-schmidt",
    }
    p2bk_norm = nested(p2bk, "raw_probe.norm_contract")
    if not isinstance(p2bk_norm, dict):
        raise InputError("P2bK norm_contract must be an object")
    for key, expected in expected_p2bk.items():
        if p2bk_norm.get(key) != expected:
            raise InputError(
                f"incompatible P2bK norm contract {key}: "
                f"expected {expected!r}, found {p2bk_norm.get(key)!r}"
            )


def require_root_contract(summary: dict[str, Any]) -> None:
    if summary.get("schema_version") != ROOT_SCHEMA:
        raise InputError(f"root summary schema_version must be {ROOT_SCHEMA!r}")
    if summary.get("status") != "PASS":
        raise InputError("root summary status is not PASS")
    if summary.get("bound_semantics") != BOUND_SEMANTICS:
        raise InputError(f"root summary bound_semantics must be {BOUND_SEMANTICS!r}")
    if summary.get("ordered_normalized_parameters") != PARAMETERS:
        raise InputError("root summary normalized-parameter order is incompatible")
    if summary.get("ordered_symmetric_pairs") != SYMMETRIC_PAIRS:
        raise InputError("root summary symmetric-pair order is incompatible")
    grid = summary.get("grid")
    if not isinstance(grid, dict):
        raise InputError("root summary grid must be an object")
    if grid.get("subdivisions") != [32, 128, 4]:
        raise InputError("root summary does not cover the frozen 32x128x4 grid")
    if grid.get("passed_cells") != 16384 or grid.get("total_cells") != 16384:
        raise InputError("root summary does not record 16384/16384 passing cells")
    provenance = summary.get("provenance")
    if not isinstance(provenance, dict):
        raise InputError("root summary provenance must be an object")
    expected_provenance = {
        "repository_commit": ROOT_REPOSITORY_COMMIT,
        "source_sha256": ROOT_SOURCE_SHA256,
        "fixed_numeric_order_log_concatenation_sha256": ROOT_LOG_SHA256,
    }
    for key, expected in expected_provenance.items():
        if provenance.get(key) != expected:
            raise InputError(
                f"root summary provenance {key} does not match the strict run"
            )


def fraction_json(value: Fraction) -> dict[str, str]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "decimal_approx": format(float(value), ".17g"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compose design-level P2c weight-1/5 tail bounds from archived "
            "P2b/P2bK endpoints and a strict root-jet summary."
        )
    )
    parser.add_argument("root_summary", type=Path)
    args = parser.parse_args()

    rigorous_dir = Path(__file__).resolve().parents[1]
    p2b_path = rigorous_dir / "results" / "vdp_bridge_v1_p2b_jets.json"
    p2bk_path = rigorous_dir / "results" / "vdp_bridge_v1_p2b_kato.json"
    p2b = read_json(p2b_path)
    p2bk = read_json(p2bk_path)
    root = read_json(args.root_summary)

    require_norm_contracts(p2b, p2bk)
    require_root_contract(root)

    if p2b.get("mathematical_status") != "PASS":
        raise InputError("archived P2b mathematical_status is not PASS")
    if p2bk.get("mathematical_status") != "PASS":
        raise InputError("archived P2bK mathematical_status is not PASS")

    frozen_constants_match = all(
        [
            archived_contains(p2b, "raw_probe.parameter_enclosures.R", RADIUS),
            archived_contains(p2b, "raw_probe.parameter_enclosures.omega", LOCAL_WEIGHT),
            archived_contains(p2b, "raw_probe.parameter_enclosures.hom_weight", TAIL_WEIGHT),
            archived_contains(p2bk, "raw_probe.parameter_enclosures.R", RADIUS),
        ]
    )
    if not frozen_constants_match:
        raise InputError("archived enclosures do not contain the frozen R/weight constants")

    half_time_upper = fraction_from_hex(root.get("half_time_upper_hex"), "half_time_upper_hex")
    phase_first = root_hex_list(root, "phase_first_abs_upper_hex", 3)
    time_first = root_hex_list(root, "time_first_abs_upper_hex", 3)
    phase_second = root_hex_list(root, "phase_second_abs_upper_hex", 6)
    time_second = root_hex_list(root, "time_second_abs_upper_hex", 6)

    p1_squared = first_norm_squared_upper(phase_first)
    t1_squared = first_norm_squared_upper(time_first)
    p2_squared = second_frobenius_squared_upper(phase_second)
    t2_squared = second_frobenius_squared_upper(time_second)
    p1 = PHASE_FIRST_NORM_UPPER
    t1 = TIME_FIRST_NORM_UPPER
    p2 = PHASE_SECOND_NORM_UPPER
    t2 = TIME_SECOND_NORM_UPPER

    time_margin = TAIL_CUT - TIME_GAP - half_time_upper
    weight_margin = LOCAL_WEIGHT - TAIL_WEIGHT
    # For x>0, exp(x)>1+x; hence exp(-1/4)<1/(1+1/4)=4/5.
    decay_exponential_gate = DECAY_FACTOR * (1 + LOCAL_WEIGHT) == 1
    # For 0<x<1, exp(x)<sum_{n>=0}x^n=1/(1-x).  At x=1/5 this gives
    # exp(1/5)<5/4, so exp(11/5)<(5/4)^11<27.  The final comparison is
    # checked below using integers only.
    shift_exponential_gate = 5**11 < SHIFT_EXPONENTIAL_UPPER * 4**11
    preliminary_gates = {
        "phase_first_euclidean_bound": p1 * p1 >= p1_squared,
        "time_first_euclidean_bound": t1 * t1 >= t1_squared,
        "phase_second_frobenius_bound": p2 * p2 >= p2_squared,
        "time_second_frobenius_bound": t2 * t2 >= t2_squared,
        "decay_exponential_comparison": decay_exponential_gate,
        "shift_exponential_comparison": shift_exponential_gate,
        "half_time_plus_one_below_tail_cut": time_margin > 0,
        "tail_weight_below_local_weight": weight_margin > 0,
    }
    if not all(preliminary_gates.values()):
        output = {
            "schema_version": OUTPUT_SCHEMA,
            "status": "INCONCLUSIVE",
            "scope": "design-only algebraic tail composition; not a certificate",
            "gates": preliminary_gates,
            "margins": {
                "phase_first_squared_norm_margin": fraction_json(
                    p1 * p1 - p1_squared
                ),
                "time_first_squared_norm_margin": fraction_json(
                    t1 * t1 - t1_squared
                ),
                "phase_second_squared_norm_margin": fraction_json(
                    p2 * p2 - p2_squared
                ),
                "time_second_squared_norm_margin": fraction_json(
                    t2 * t2 - t2_squared
                ),
                "tail_cut_minus_one_minus_half_time_upper": fraction_json(time_margin),
                "local_weight_minus_tail_weight": fraction_json(weight_margin),
            },
        }
        print(json.dumps(output, indent=2, sort_keys=True))
        return 2

    source_b1 = archived_upper(
        p2bk, "raw_probe.source_coordinate_jet_enclosures.B_1"
    )
    source_b2 = archived_upper(
        p2bk, "raw_probe.source_coordinate_jet_enclosures.B_2"
    )
    source_total_b1 = source_b1 + RADIUS * p1
    source_total_b2 = (
        source_b2
        + 2 * source_b1 * p1
        + RADIUS * (p1 * p1 + p2)
    )

    moving: dict[tuple[int, int], Fraction] = {}
    physical: dict[tuple[int, int], Fraction] = {}
    for state_order, parameter_order in [
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 1),
        (2, 0),
    ]:
        name = f"Z_{state_order}_{parameter_order}"
        moving[state_order, parameter_order] = archived_upper(
            p2b, f"raw_probe.weighted_jet_enclosures.{name}"
        )
        physical[state_order, parameter_order] = archived_upper(
            p2b, f"raw_probe.physical_weighted_jet_enclosures.{name}"
        )

    a = {index: DECAY_FACTOR * value for index, value in moving.items()}
    l10 = archived_upper(p2b, "raw_probe.lyapunov_perron_coefficients.L_1_0")
    l11 = archived_upper(p2b, "raw_probe.lyapunov_perron_coefficients.L_1_1")
    full_field_first = 1 + l10
    field_value = full_field_first * a[0, 0]
    time_parameter = l11 * a[0, 0] + full_field_first * a[0, 1]
    time_state = full_field_first * a[1, 0]
    time_time = full_field_first * field_value

    bminus0 = a[0, 0]
    bminus1 = a[0, 1] + a[1, 0] * source_total_b1 + field_value * t1
    bminus2 = (
        a[0, 2]
        + 2 * a[1, 1] * source_total_b1
        + a[2, 0] * source_total_b1 * source_total_b1
        + a[1, 0] * source_total_b2
        + 2 * (time_parameter + time_state * source_total_b1) * t1
        + time_time * t1 * t1
        + field_value * t2
    )

    interior_margin = RADIUS - bminus0
    all_gates = {
        **preliminary_gates,
        "bminus_strictly_inside_source_disk": interior_margin > 0,
    }
    if not all(all_gates.values()):
        output = {
            "schema_version": OUTPUT_SCHEMA,
            "status": "INCONCLUSIVE",
            "scope": "design-only algebraic tail composition; not a certificate",
            "gates": all_gates,
            "margins": {
                "tail_cut_minus_one_minus_half_time_upper": fraction_json(time_margin),
                "local_weight_minus_tail_weight": fraction_json(weight_margin),
                "source_radius_minus_bminus0": fraction_json(interior_margin),
            },
        }
        print(json.dumps(output, indent=2, sort_keys=True))
        return 2

    k0 = physical[0, 0]
    k1 = physical[0, 1] + physical[1, 0] * bminus1
    k2 = (
        physical[0, 2]
        + 2 * physical[1, 1] * bminus1
        + physical[2, 0] * bminus1 * bminus1
        + physical[1, 0] * bminus2
    )
    normalized_c = [
        SHIFT_EXPONENTIAL_UPPER * k0,
        SHIFT_EXPONENTIAL_UPPER * k1,
        SHIFT_EXPONENTIAL_UPPER * k2,
    ]
    original_c = [
        normalized_c[0],
        FIRST_ORIGINAL_PARAMETER_SCALE * normalized_c[1],
        SECOND_ORIGINAL_PARAMETER_SCALE * normalized_c[2],
    ]
    normalized_common_c = max(normalized_c)
    original_common_c = max(original_c)

    output = {
        "schema_version": OUTPUT_SCHEMA,
        "status": "PASS",
        "scope": "design-only algebraic tail composition; not a certificate",
        "method": {
            "finite_time_ode_integration": False,
            "tail_cut": fraction_json(TAIL_CUT),
            "local_weight": fraction_json(LOCAL_WEIGHT),
            "tail_weight": fraction_json(TAIL_WEIGHT),
            "decay_factor_upper": fraction_json(DECAY_FACTOR),
            "shift_exponential_upper": fraction_json(SHIFT_EXPONENTIAL_UPPER),
            "decay_exponential_proof": (
                "exp(1/4)>1+1/4=5/4, hence exp(-1/4)<4/5"
            ),
            "shift_exponential_proof": (
                "exp(1/5)<1/(1-1/5)=5/4 and 5^11<27*4^11, "
                "hence exp(11/5)<27"
            ),
        },
        "norm_contract": {
            "root_first_aggregation": (
                "exact rational Euclidean upper bound, checked after squaring"
            ),
            "root_second_aggregation": (
                "exact rational full-3x3 Frobenius upper bound, checked after "
                "squaring with off-diagonal symmetric entries counted twice"
            ),
            "moving_state": "max-of-two-euclidean-blocks",
            "physical_state": "euclidean",
            "parameter_derivatives": (
                "Euclidean/Frobenius bounds dominating labelled operator norms"
            ),
        },
        "gates": all_gates,
        "margins": {
            "phase_first_squared_norm_margin": fraction_json(
                p1 * p1 - p1_squared
            ),
            "time_first_squared_norm_margin": fraction_json(
                t1 * t1 - t1_squared
            ),
            "phase_second_squared_norm_margin": fraction_json(
                p2 * p2 - p2_squared
            ),
            "time_second_squared_norm_margin": fraction_json(
                t2 * t2 - t2_squared
            ),
            "tail_cut_minus_one_minus_half_time_upper": fraction_json(time_margin),
            "local_weight_minus_tail_weight": fraction_json(weight_margin),
            "source_radius_minus_bminus0": fraction_json(interior_margin),
        },
        "root_jet_aggregates": {
            "phase_first_euclidean": fraction_json(p1),
            "phase_second_frobenius": fraction_json(p2),
            "time_first_euclidean": fraction_json(t1),
            "time_second_frobenius": fraction_json(t2),
        },
        "source_coordinate_aggregates": {
            "B1": fraction_json(source_total_b1),
            "B2": fraction_json(source_total_b2),
        },
        "bminus_normalized_parameter_bounds": {
            "Bminus0": fraction_json(bminus0),
            "Bminus1": fraction_json(bminus1),
            "Bminus2": fraction_json(bminus2),
        },
        "tail_fixed_shift_bounds": {
            "K0": fraction_json(k0),
            "K1": fraction_json(k1),
            "K2": fraction_json(k2),
        },
        "tail_weight_one_fifth_constants": {
            "normalized_parameters": {
                "C0": fraction_json(normalized_c[0]),
                "C1": fraction_json(normalized_c[1]),
                "C2": fraction_json(normalized_c[2]),
                "common_C": fraction_json(normalized_common_c),
            },
            "original_parameters_coarse_25_625": {
                "C0": fraction_json(original_c[0]),
                "C1": fraction_json(original_c[1]),
                "C2": fraction_json(original_c[2]),
                "common_C": fraction_json(original_common_c),
            },
            "negative_and_positive_tails_use_same_constants": True,
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except InputError as exc:
        raise SystemExit(f"input error: {exc}") from exc
