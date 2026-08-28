#!/usr/bin/env python3
"""Check the proof-bound P2d slides to the inherited physical faces."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
sys.path.insert(0, str(HERE))

import check_p2d_weighted_passage as weighted  # noqa: E402


SCHEMA_VERSION = "rfsn-vdp-p2d-physical-slides-check/1"
SCOPE = "V2_CHART_PHYSICAL_SLIDES_LOCAL_PROOF_BOUND_GATES"
PROOF_CONTRACT = "rfsn-vdp-p2d-explicit-physical-slides/1"
PROOF_RELATIVE = "theory/EXPLICIT_PHYSICAL_SLIDES.md"
PROOF_PATH = REPOSITORY / PROOF_RELATIVE
PROOF_SHA256 = (
    "7fa2fc45827f7c8b41a0dabb3a2bd872f66088e61d3c26ed55d8c78bc80e187b")

P2A_RELATIVE = (
    "validation/rigorous/results/vdp_bridge_v1_p2a_local_graph.json")
P2A_PATH = REPOSITORY / P2A_RELATIVE
P2A_SHA256 = (
    "192b351c3f153080d82bc856fa3c667388dc16c7b4cf0cfa8568fa347bcaf6be")
P2B_JETS_RELATIVE = (
    "validation/rigorous/results/vdp_bridge_v1_p2b_jets.json")
P2B_JETS_PATH = REPOSITORY / P2B_JETS_RELATIVE
P2B_JETS_SHA256 = (
    "07b0949a3d403c0c0a85a4a157b86d7b32cce3ff0348aeffa1db474d441fca07")
KATO_RELATIVE = (
    "validation/rigorous/results/vdp_bridge_v1_p2b_kato.json")
KATO_PATH = REPOSITORY / KATO_RELATIVE
KATO_SHA256 = (
    "c67cce575caa396eba5b4388e8ba9a0c9d73fd702f69911d64c878f57f27bff3")
FRAME_RELATIVE = (
    "validation/rigorous/results/vdp_bridge_v1_p2d_symplectic_frame.json")
FRAME_PATH = REPOSITORY / FRAME_RELATIVE
FRAME_SHA256 = (
    "5fabbcf01dc9b2f818f34525010332c76ff40190ea9a3d5ab166072397397847")
MOSER_RELATIVE = "theory/EXPLICIT_GLOBAL_MOSER_MAJORANT.md"
MOSER_PATH = REPOSITORY / MOSER_RELATIVE
MOSER_SHA256 = (
    "069d109a22fa502c2e6970de7e3ef4c60234e327138b9052df764b6f36cf8245")
MOSER_CONTRACT = "rfsn-vdp-p2d-explicit-global-moser-majorant/1"
CONFIG_RELATIVE = (
    "validation/rigorous/config/vdp_p2d_physical_slides_v1.json")
CONFIG_PATH = REPOSITORY / CONFIG_RELATIVE
CONFIG_SHA256 = (
    "fa7daa1273b508951e081378d938342f985271722bf4871669a30f4ab44a8f16")
P2C_CONFIG_RELATIVE = "validation/rigorous/config/vdp_p2_homoclinic_v1.json"
P2C_CONFIG_PATH = REPOSITORY / P2C_CONFIG_RELATIVE
P2C_CONFIG_SHA256 = (
    "a1aca97d2fcf76f336dc06734c1ced25aeb9bd6b1bfa69b9dc8a6545846ce9ac")

PHYSICAL_RADIUS = Fraction(1, 100)
SECTION_RADIUS = Fraction(5, 2**26)
CHART_SOURCE_RADIUS = Fraction(3, 2**25)
WEIGHTED_RADIUS = Fraction(25, 2**58)
MOSER_FORWARD_DISPLACEMENT = Fraction(75, 23191581884416)
MOSER_TWO_SIDED_DISPLACEMENT = 2 * MOSER_FORWARD_DISPLACEMENT
SIGMA_LOWER = Fraction(2, 3)
SIGMA_UPPER = Fraction(3, 4)
BETA_UPPER = Fraction(3, 4)
KAPPA_INVERSE_SQRT_LOWER = Fraction(63, 64)
KAPPA_INVERSE_SQRT_UPPER = Fraction(65, 64)
FRAME_SCALE_LOWER = SIGMA_LOWER * KAPPA_INVERSE_SQRT_LOWER
FRAME_SCALE_UPPER = SIGMA_UPPER * KAPPA_INVERSE_SQRT_UPPER
WEIGHTED_P_UPPER = Fraction(5, 4)
ONE_PLUS_P_SQUARED_SQRT_UPPER = Fraction(13, 8)
SLIDE_TIME_UPPER = 19
TOTAL_SLIDE_TIME_UPPER = 38
RADIAL_SPEED_LOWER = Fraction(1, 150)
SQUARED_FACE_SPEED_LOWER = 2 * PHYSICAL_RADIUS * RADIAL_SPEED_LOWER
NORMALIZED_HIT_SPEED_LOWER = 10**4 * SQUARED_FACE_SPEED_LOWER
PHYSICAL_COMPARISON_CONSTANT = 7
NORMALIZED_FIELD_DERIVATIVE_UPPER = 16
SOURCE_JET_EXPONENT = 4096
FLOW_JET_EXPONENTS = (4704, 10033, 30725, 123527, 618263)
HIT_FUNCTION_EXPONENTS = (4726, 20089, 92199, 494133, 3091341)
HIT_TIME_EXPONENTS = (4726, 29559, 180895, 1217733, 9180027)
ENDPOINT_EXPONENTS = (9443, 69165, 573425, 4994475, 46518415)
ENDPOINT_VALUE_EXPONENT = 0
HIT_TIME_VALUE_EXPONENT = 5
ENDPOINT_VALUE_UPPER = Fraction(3, 25)
MAX_STATE_ORDER = 3
MAX_PARAMETER_ORDER = 2
MAX_TOTAL_ORDER = MAX_STATE_ORDER + MAX_PARAMETER_ORDER
ALGEBRAIC_ENDPOINT_OVERHEAD_EXPONENT = 7
TERMINAL_T_OPERATOR_CAP_EXPONENT = 3
TERMINAL_T_PARAMETER_ALLOCATION_COUNT = 2**MAX_PARAMETER_ORDER
TERMINAL_T_PARAMETER_ALLOCATION_EXPONENT = 2
ENDPOINT_OVERHEAD_EXPONENT = (
    ALGEBRAIC_ENDPOINT_OVERHEAD_EXPONENT
    + TERMINAL_T_OPERATOR_CAP_EXPONENT
    + TERMINAL_T_PARAMETER_ALLOCATION_EXPONENT)
ORIGINAL_PARAMETER_SCALES = {"r": 25, "a2": 4, "epsilon": 5}
SECOND_PARAMETER_PAIRS = (
    ("r", "r"), ("r", "a2"), ("r", "epsilon"),
    ("a2", "a2"), ("a2", "epsilon"), ("epsilon", "epsilon"),
)


class PhysicalSlidesCheckError(ValueError):
    """A required source, proof binding, or rational gate is malformed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PhysicalSlidesCheckError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def rational(value: Fraction | int) -> dict[str, str]:
    value = Fraction(value)
    return {"numerator": str(value.numerator),
            "denominator": str(value.denominator)}


def as_fraction(record: Any, label: str) -> Fraction:
    require(isinstance(record, dict), f"{label} is not a rational record")
    try:
        return Fraction(int(record["numerator"]), int(record["denominator"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        raise PhysicalSlidesCheckError(
            f"{label} is not a valid rational record: {error}") from error


def hex_fraction(value: Any, label: str) -> Fraction:
    """Decode an IEEE-754 hexadecimal endpoint as an exact Fraction."""
    require(isinstance(value, str), f"{label} is not a hexadecimal endpoint")
    sign = -1 if value.startswith("-") else 1
    unsigned = value[1:] if sign < 0 else value
    require(unsigned.startswith("0x") and "p" in unsigned,
            f"{label} has malformed hexadecimal syntax")
    mantissa, exponent_text = unsigned[2:].split("p", 1)
    require(mantissa.count(".") <= 1 and mantissa,
            f"{label} has malformed mantissa")
    integer_text, dot, fractional_text = mantissa.partition(".")
    digits = (integer_text or "0") + fractional_text
    try:
        coefficient = int(digits, 16)
        exponent = int(exponent_text)
    except ValueError as error:
        raise PhysicalSlidesCheckError(
            f"{label} is not an exact hexadecimal number: {error}") from error
    denominator = 16 ** len(fractional_text)
    result = Fraction(sign * coefficient, denominator)
    return result * (2 ** exponent) if exponent >= 0 else result / (2 ** -exponent)


def interval(record: Any, label: str) -> tuple[Fraction, Fraction]:
    require(isinstance(record, dict), f"{label} is not an interval record")
    require(record.get("endpoint_format") == "IEEE754_BINARY64_HEX",
            f"{label} endpoint format changed")
    lower = hex_fraction(record.get("lower_hex"), f"{label}.lower_hex")
    upper = hex_fraction(record.get("upper_hex"), f"{label}.upper_hex")
    require(lower <= upper, f"{label} has reversed endpoints")
    return lower, upper


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def _load_bound_json(
        path: Path, expected_sha256: str, relative: str,
        ) -> tuple[dict[str, Any], str]:
    source = path.read_bytes()
    digest = sha256_bytes(source)
    require(digest == expected_sha256,
            f"the frozen source SHA-256 changed: {relative}")
    try:
        value = json.loads(source)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise PhysicalSlidesCheckError(
            f"the frozen source is malformed ({relative}): {error}") from error
    require(isinstance(value, dict), f"the frozen source is not an object: {relative}")
    return value, digest


def _bound_text(
        path: Path, expected_sha256: str, relative: str, contract: str,
        ) -> dict[str, Any]:
    source = path.read_bytes()
    digest = sha256_bytes(source)
    try:
        text = source.decode("utf-8")
    except UnicodeError as error:
        raise PhysicalSlidesCheckError(
            f"the source proof is not UTF-8 ({relative}): {error}") from error
    contract_present = contract in text
    require(digest == expected_sha256,
            f"the frozen source SHA-256 changed: {relative}")
    require(contract_present, f"the proof contract changed: {relative}")
    return {"path": relative, "expected_sha256": expected_sha256,
            "observed_sha256": digest, "proof_contract": contract,
            "proof_contract_present": contract_present, "matched": True}


def proof_binding(path: Path) -> dict[str, Any]:
    source = path.read_bytes()
    digest = sha256_bytes(source)
    try:
        text = source.decode("utf-8")
    except UnicodeError as error:
        raise PhysicalSlidesCheckError(
            f"physical-slides proof is not UTF-8: {error}") from error
    contract_present = PROOF_CONTRACT in text
    return {
        "path": PROOF_RELATIVE,
        "expected_sha256": PROOF_SHA256,
        "observed_sha256": digest,
        "proof_contract": PROOF_CONTRACT,
        "proof_contract_present": contract_present,
        "matched": digest == PROOF_SHA256 and contract_present,
    }


def _obligation(certificate: dict[str, Any], identifier: str) -> dict[str, Any]:
    matches = [item for item in certificate.get("obligations", [])
               if isinstance(item, dict) and item.get("id") == identifier]
    require(len(matches) == 1, f"obligation {identifier} is not unique")
    require(matches[0].get("status") == "PASS",
            f"obligation {identifier} is not PASS")
    return matches[0]


def authenticate_sources(
        p2a_path: Path, p2b_jets_path: Path, kato_path: Path,
        frame_path: Path, moser_path: Path, config_path: Path,
        p2c_config_path: Path,
        ) -> tuple[
            dict[str, Any], dict[str, Any], dict[str, Any],
            dict[str, Any], dict[str, Any], dict[str, Any]]:
    p2a, p2a_digest = _load_bound_json(
        p2a_path, P2A_SHA256, P2A_RELATIVE)
    p2b_jets, p2b_jets_digest = _load_bound_json(
        p2b_jets_path, P2B_JETS_SHA256, P2B_JETS_RELATIVE)
    kato, kato_digest = _load_bound_json(
        kato_path, KATO_SHA256, KATO_RELATIVE)
    frame, frame_digest = _load_bound_json(
        frame_path, FRAME_SHA256, FRAME_RELATIVE)
    moser = _bound_text(
        moser_path, MOSER_SHA256, MOSER_RELATIVE, MOSER_CONTRACT)
    config, config_digest = _load_bound_json(
        config_path, CONFIG_SHA256, CONFIG_RELATIVE)
    _, p2c_config_digest = _load_bound_json(
        p2c_config_path, P2C_CONFIG_SHA256, P2C_CONFIG_RELATIVE)

    for value, scope, label in (
            (p2a, "V2_LOCAL_GRAPH_KERNEL", "P2a"),
            (p2b_jets, "V2_P2_JETS_KERNEL", "P2b jets"),
            (kato, "V2_P2_KATO_KERNEL", "P2bK"),
            (frame, "V2_P2D_SYMPLECTIC_FRAME_KERNEL", "P2d frame")):
        require(value.get("scope") == scope, f"{label} scope changed")
        require(value.get("integrity_status") == "PASS",
                f"{label} integrity status is not PASS")
        require(value.get("mathematical_status") == "PASS",
                f"{label} mathematical status is not PASS")

    frame_block = _obligation(p2a, "V2.WU.FRAME_BLOCK")
    coarse_graph = _obligation(p2a, "V2.WU.COARSE_GRAPH")
    _obligation(p2b_jets, "V2.WU.JETS")
    coefficient_gates = p2b_jets.get("raw_probe", {}).get(
        "coefficient_upper_gates")
    require(isinstance(coefficient_gates, dict),
            "the P2b coefficient gates are missing")
    sigma_record = kato.get("raw_probe", {}).get(
        "scalar_enclosures", {}).get("sigma")
    kato_audit = kato.get("kato_exact_algebra_audit", {})
    require(kato_audit.get("status") == "PASS",
            "the P2bK exact algebra audit is not PASS")
    require(kato_audit.get("checks", {}).get(
        "same_graph_boundary_normalized_C_AK_direction") is True,
        "the P2a-to-P2bK graph-boundary direction is not authenticated")
    require(kato_audit.get("checks", {}).get(
        "K_equals_E_times_C_AK") is True,
        "the Kato-to-algebraic C_AK identity is not authenticated")
    frame_audit = frame.get("exact_audit", {}).get("report", {})
    require(frame_audit.get("status") == "PASS",
            "the P2d exact audit is not PASS")
    require(frame_audit.get("checks", {}).get("kappa_positive_closed_form") is True,
            "kappa positivity is not authenticated")
    require(frame_audit.get("checks", {}).get(
        "kappa_squared_is_d_squared_plus_e_squared") is True,
        "the kappa/rotation normalization is not authenticated")
    require(frame_audit.get("checks", {}).get(
        "kato_frame_equals_algebraic_frame_times_change") is True,
        "the Kato/algebraic frame identity is not authenticated")

    require(config.get("schema_version") ==
            "rfsn-vdp-p2d-physical-slides-config/1",
            "the physical-slides configuration schema changed")
    require(config.get("status") == "FROZEN_PROOF_BOUND",
            "the physical-slides configuration is not frozen")
    physical_interface = config.get("physical_interface", {})
    require(as_fraction(physical_interface.get("physical_radius"),
                        "configured physical radius") == PHYSICAL_RADIUS,
            "the configured physical face is not radius 1/100")
    event_contract = config.get("local_event_support_contract", {})
    require(event_contract.get(
        "restriction_to_closed_physical_saddle_block") == "EMPTY",
        "the local event family is not empty on the closed saddle block")
    require(event_contract.get(
        "excluded_non_saddle_event_germ_ids_inside_block") == [],
        "a non-saddle event germ was placed inside the saddle block")
    require(event_contract.get(
        "p2e_extension_and_complete_census_status") == "OPEN",
        "the local support contract changed the P2e claim boundary")
    p2c_binding = config.get("p2c_source_interface", {})
    require(p2c_binding.get("path") == P2C_CONFIG_RELATIVE,
            "the P2c source-interface path changed")
    require(p2c_binding.get("sha256") == p2c_config_digest,
            "the P2c source-interface digest changed")

    return (
        {"certificate": p2a, "sha256": p2a_digest,
         "frame_block": frame_block, "coarse_graph": coarse_graph},
        {"certificate": p2b_jets, "sha256": p2b_jets_digest,
         "coefficient_gates": coefficient_gates},
        {"certificate": kato, "sha256": kato_digest,
         "sigma_record": sigma_record},
        {"certificate": frame, "sha256": frame_digest,
         "kappa_record": frame.get("raw_probe", {}).get(
             "scalar_jets", {}).get("kappa_inverse_sqrt", {}).get(
                 "normalized", {}).get("value")},
        moser,
        {"configuration": config, "sha256": config_digest,
         "p2c_config_sha256": p2c_config_digest,
         "event_contract": event_contract},
    )


def _ceil_log2(value: int) -> int:
    require(isinstance(value, int) and value > 0,
            "the logarithm input must be a positive integer")
    return (value - 1).bit_length()


def _strict_power_two_exponent(value: Fraction | int) -> int:
    """Return the least e with ``abs(value) < 2**e``."""
    value = abs(Fraction(value))
    require(value > 0, "a strict power-of-two budget must be positive")
    exponent = max(0, value.numerator.bit_length()
                   - value.denominator.bit_length())
    while value >= 2**exponent:
        exponent += 1
    while exponent > 0 and value < 2**(exponent - 1):
        exponent -= 1
    return exponent


def _bell_number(order: int) -> int:
    require(order >= 0, "the Bell-number order must be nonnegative")
    return sum(weighted.stirling_second(order, blocks)
               for blocks in range(order + 1))


def _flow_exponent_recurrence() -> tuple[int, ...]:
    values = [SOURCE_JET_EXPONENT + 608]
    for order in range(2, 6):
        values.append(
            609 + max(
                SOURCE_JET_EXPONENT,
                14 + order * (1 + values[-1]),
            )
        )
    return tuple(values)


def _hit_function_exponent_recurrence(
        flow: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        21 + order * (1 + flow[order - 1])
        for order in range(1, 6)
    )


def _hit_time_exponent_recurrence(
        hit_function: tuple[int, ...]) -> tuple[int, ...]:
    values = [hit_function[0]]
    for order in range(2, 6):
        values.append(
            16 + max(hit_function[:order])
            + order * (1 + values[-1])
        )
    return tuple(values)


def _endpoint_exponent_recurrence(
        flow: tuple[int, ...], hit_time: tuple[int, ...],
        ) -> tuple[int, ...]:
    return tuple(
        ENDPOINT_OVERHEAD_EXPONENT
        + flow[order - 1] + order * (1 + hit_time[order - 1])
        for order in range(1, 6)
    )


def conservative_mixed_jet_exponent(
        state_order: int, parameter_order: int,
        *, endpoint: bool = True, original_scale: int = 1) -> int:
    """Return a power-of-two exponent for a slide endpoint or hit time."""
    require(state_order in range(4), "state order must lie in 0..3")
    require(parameter_order in range(3), "parameter order must lie in 0..2")
    total_order = state_order + parameter_order
    require(original_scale > 0, "the original-parameter scale must be positive")
    if total_order == 0:
        value_exponent = (
            ENDPOINT_VALUE_EXPONENT if endpoint else HIT_TIME_VALUE_EXPONENT)
        return value_exponent + _ceil_log2(original_scale)
    table = ENDPOINT_EXPONENTS if endpoint else HIT_TIME_EXPONENTS
    return table[total_order - 1] + _ceil_log2(original_scale)


def _mixed_jet_rectangle() -> dict[str, Any]:
    normalized = {
        f"state_order_{state_order}": [
            {
                "parameter_order": parameter_order,
                "hit_time_power_of_two_exponent": str(
                    conservative_mixed_jet_exponent(
                        state_order, parameter_order, endpoint=False)),
                "endpoint_power_of_two_exponent": str(
                    conservative_mixed_jet_exponent(
                        state_order, parameter_order)),
            }
            for parameter_order in range(3)
        ]
        for state_order in range(4)
    }
    original: dict[str, list[dict[str, Any]]] = {}
    parameter_entries = [("value", 0, 1)]
    parameter_entries.extend(
        (f"D_{axis}", 1, scale)
        for axis, scale in ORIGINAL_PARAMETER_SCALES.items())
    parameter_entries.extend(
        (f"D_{left}_{right}", 2,
         ORIGINAL_PARAMETER_SCALES[left] * ORIGINAL_PARAMETER_SCALES[right])
        for left, right in SECOND_PARAMETER_PAIRS)
    for label, parameter_order, scale in parameter_entries:
        original[label] = [
            {"state_order": state_order,
             "hit_time_power_of_two_exponent": str(
                 conservative_mixed_jet_exponent(
                     state_order, parameter_order, endpoint=False,
                     original_scale=scale)),
             "endpoint_power_of_two_exponent": str(
                 conservative_mixed_jet_exponent(
                     state_order, parameter_order,
                     original_scale=scale))}
            for state_order in range(4)
        ]
    return {
        "state_orders": list(range(4)),
        "normalized_parameter_orders": list(range(3)),
        "normalized_4_by_3_rectangle": normalized,
        "original_parameter_rectangle": original,
        "generator": {
            "normalized_field_derivative_upper": str(
                NORMALIZED_FIELD_DERIVATIVE_UPPER),
            "source_jet_power_of_two_exponent": str(SOURCE_JET_EXPONENT),
            "flow_power_of_two_exponents": [str(value) for value in
                                                   FLOW_JET_EXPONENTS],
            "hit_function_power_of_two_exponents": [str(value) for value in
                                                           HIT_FUNCTION_EXPONENTS],
            "hit_time_power_of_two_exponents": [str(value) for value in
                                                       HIT_TIME_EXPONENTS],
            "endpoint_power_of_two_exponents": [str(value) for value in
                                                       ENDPOINT_EXPONENTS],
            "hit_time_value_strict_upper": str(SLIDE_TIME_UPPER),
            "hit_time_value_power_of_two_exponent": str(
                HIT_TIME_VALUE_EXPONENT),
            "endpoint_value_strict_upper": rational(ENDPOINT_VALUE_UPPER),
            "endpoint_value_power_of_two_exponent": str(
                ENDPOINT_VALUE_EXPONENT),
            "endpoint_overhead_power_of_two_exponent": str(
                ENDPOINT_OVERHEAD_EXPONENT),
            "normalized_hit_speed_lower": rational(
                NORMALIZED_HIT_SPEED_LOWER),
            "original_parameter_max_conversion_exponent": "10",
            "scope": (
                "complete uniform C_mu^2(C_state^3) rectangle for both "
                "endpoint maps and hit times"),
        },
    }


def _gate_upper(gates: dict[str, Any], name: str) -> Fraction:
    return interval(gates.get(name), f"P2b.{name}")[1]


def _field_derivative_budget(p2b_jets: dict[str, Any]) -> dict[str, Any]:
    gates = p2b_jets["coefficient_gates"]
    expected = {
        "B_0_gate": Fraction(101, 10000),
        "B_1_gate": Fraction(3, 250),
        "B_2_gate": Fraction(3, 400),
        "m_0_gate": Fraction(101, 100),
        "m_1_gate": Fraction(23, 2000),
        "m_2_gate": Fraction(3, 400),
        "t_0_gate": Fraction(3, 400),
        "t_1_gate": Fraction(3, 400),
        "t_2_gate": Fraction(3, 800),
    }
    gate_intervals = {
        name: interval(gates.get(name), f"P2b.{name}") for name in expected}
    uppers = dict(expected)
    exact_gate_checks = {
        name: gate_intervals[name][0] <= bound <= gate_intervals[name][1]
        for name, bound in expected.items()
    }
    x_star = interval(
        p2b_jets["certificate"].get("raw_probe", {}).get(
            "parameter_enclosures", {}).get("Xstar"),
        "P2b.Xstar",
    )
    require(x_star[0] >= PHYSICAL_RADIUS,
            "the P2b coefficient interval does not reach radius 1/100")

    derivative_bounds: dict[str, list[Fraction]] = {
        "state_order_0": [], "state_order_1": [],
        "state_order_2": [], "state_order_3": [],
    }
    for parameter_order in range(3):
        block = (
            1 + uppers["B_0_gate"] if parameter_order == 0
            else uppers[f"B_{parameter_order}_gate"]
        )
        third = uppers[f"t_{parameter_order}_gate"]
        second = (
            uppers[f"m_{parameter_order}_gate"]
            + PHYSICAL_RADIUS * third
        )
        derivative_bounds["state_order_0"].append(
            block * PHYSICAL_RADIUS
            + Fraction(1, 2) * (2 * PHYSICAL_RADIUS) ** 2 * second)
        derivative_bounds["state_order_1"].append(
            block + 4 * PHYSICAL_RADIUS * second)
        derivative_bounds["state_order_2"].append(4 * second)
        derivative_bounds["state_order_3"].append(8 * third)

    return {
        "P2b_gate_upper_bounds": {
            name: rational(value) for name, value in uppers.items()},
        "full_block_normalized_bounds": {
            key: [rational(value) for value in values]
            for key, values in derivative_bounds.items()
        },
        "uniform_upper": str(NORMALIZED_FIELD_DERIVATIVE_UPPER),
        "checks": {
            **exact_gate_checks,
            "Xstar_reaches_physical_radius": x_star[0] >= PHYSICAL_RADIUS,
            "complete_4_by_3_field_rectangle_below_16": all(
                value < NORMALIZED_FIELD_DERIVATIVE_UPPER
                for values in derivative_bounds.values() for value in values),
            "state_degree_is_at_most_three": (
                p2b_jets["certificate"].get("raw_probe", {}).get(
                    "structure_checks", {}).get(
                        "state_degree_at_most_three") is True),
        },
    }


def _iter_rational_magnitudes(value: Any):
    if isinstance(value, dict):
        if set(value) == {"numerator", "denominator"}:
            yield abs(as_fraction(value, "source accumulator"))
            return
        if value.get("endpoint_format") == "IEEE754_BINARY64_HEX":
            lower, upper = interval(value, "source interval")
            yield max(abs(lower), abs(upper))
            return
        for child in value.values():
            yield from _iter_rational_magnitudes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_rational_magnitudes(child)
    elif isinstance(value, Fraction):
        yield abs(value)


def _terminal_frame_budget(p2b_jets: dict[str, Any]) -> dict[str, Any]:
    records = p2b_jets["certificate"].get("raw_probe", {}).get(
        "frame_derivative_enclosures", {})
    required = tuple(f"T_{order}" for order in range(3))
    require(all(name in records for name in required),
            "the terminal algebraic-frame C2 operator bounds are incomplete")
    upper_bounds: dict[str, Fraction] = {}
    for name in required:
        lower, upper = interval(records[name], f"P2b.{name}")
        upper_bounds[name] = max(abs(lower), abs(upper))
    operator_exponent = max(
        _strict_power_two_exponent(value) for value in upper_bounds.values())
    allocation_count = 2**MAX_PARAMETER_ORDER
    allocation_exponent = _ceil_log2(allocation_count)
    terminal_product_exponent = operator_exponent + allocation_exponent
    endpoint_overhead = (
        ALGEBRAIC_ENDPOINT_OVERHEAD_EXPONENT + terminal_product_exponent)
    return {
        "normalized_operator_upper_bounds": {
            name: rational(value) for name, value in upper_bounds.items()},
        "operator_power_of_two_exponent": str(operator_exponent),
        "parameter_Leibniz_allocation_count": str(allocation_count),
        "parameter_Leibniz_power_of_two_exponent": str(
            allocation_exponent),
        "terminal_product_power_of_two_exponent": str(
            terminal_product_exponent),
        "algebraic_endpoint_overhead_power_of_two_exponent": str(
            ALGEBRAIC_ENDPOINT_OVERHEAD_EXPONENT),
        "full_endpoint_overhead_power_of_two_exponent": str(
            endpoint_overhead),
        "checks": {
            "complete_T_mu_C2_operator_table": set(required) <= set(records),
            "T_mu_orders_0_1_2_are_strictly_below_2_pow_3": all(
                value < 2**TERMINAL_T_OPERATOR_CAP_EXPONENT
                for value in upper_bounds.values()),
            "derived_T_mu_operator_exponent_is_at_most_3": (
                operator_exponent <= TERMINAL_T_OPERATOR_CAP_EXPONENT),
            "two_parameter_labels_give_at_most_four_Leibniz_allocations": (
                allocation_count == TERMINAL_T_PARAMETER_ALLOCATION_COUNT
                and allocation_exponent ==
                TERMINAL_T_PARAMETER_ALLOCATION_EXPONENT),
            "endpoint_overhead_matches_recurrence": (
                endpoint_overhead == ENDPOINT_OVERHEAD_EXPONENT),
            "endpoint_value_is_below_explicit_three_over_25": (
                upper_bounds["T_0"] * Fraction(3, 200)
                < ENDPOINT_VALUE_UPPER),
        },
    }


def _zero_energy_source_rectangle(
        prerequisite: dict[str, Any],
        ) -> tuple[dict[str, Any], dict[str, Any]]:
    zero_exact = weighted.zero_energy.compute_exact_bounds()
    require(all(zero_exact.get("checks", {}).values()),
            "the exact zero-energy source gates are not all PASS")
    table = zero_exact.get("mixed_jet_bounds_through_nu_order_3", {})
    require(table.get("nu_derivative_order") == list(range(4)),
            "the zero-energy q table does not cover nu orders 0..3")
    normalized = table.get("normalized_parameter_bounds", {})
    expected_rows = {f"parameter_order_{order}" for order in range(3)}
    require(set(normalized) == expected_rows,
            "the zero-energy q table does not cover parameter orders 0..2")
    q_bounds: dict[int, list[Fraction]] = {}
    for parameter_order in range(3):
        row = normalized[f"parameter_order_{parameter_order}"]
        require(isinstance(row, list) and len(row) == 4,
                "a zero-energy q mixed-jet row is not length four")
        q_bounds[parameter_order] = [
            as_fraction(value, "zero-energy q mixed jet") for value in row]

    weighted_constants = prerequisite.get("exact_values", {}).get(
        "constants", {})
    zero_constants = zero_exact.get("constants", {})
    q_matches = {
        f"Q{order}": as_fraction(
            zero_constants.get(f"Q{order}"), f"zero-energy Q{order}")
        == as_fraction(weighted_constants.get(f"Q{order}"),
                       f"weighted Q{order}")
        for order in range(3)
    }
    require(all(q_matches.values()),
            "the zero-energy and weighted q parameter bounds differ")
    maximum_q_bound = max(
        value for row in q_bounds.values() for value in row)

    rectangle: dict[str, list[dict[str, Any]]] = {}
    for state_order in range(4):
        row = []
        phase_product_count = 2**state_order
        for parameter_order in range(3):
            q_upper = max(q_bounds[parameter_order][:state_order + 1])
            nu_upper = Fraction(0)
            if parameter_order == 0:
                nu_upper = WEIGHTED_RADIUS if state_order == 0 else Fraction(1)
            # The radial block is rho*e_phase.  The complementary block is
            # rho^{-1}(q*e_phase +/- nu*J*e_phase); 2^i covers every
            # Leibniz allocation of the i labelled section derivatives.
            source_upper = (
                SECTION_RADIUS
                + Fraction(phase_product_count, SECTION_RADIUS)
                * (q_upper + nu_upper))
            row.append({
                "parameter_order": parameter_order,
                "absolute_upper": rational(source_upper),
            })
        rectangle[f"state_order_{state_order}"] = row
    return ({
        "nu_derivative_orders": list(range(4)),
        "normalized_parameter_orders": list(range(3)),
        "q_mixed_bounds": {
            f"parameter_order_{order}": [rational(value) for value in values]
            for order, values in q_bounds.items()},
        "maximum_q_mixed_bound": rational(maximum_q_bound),
        "maximum_q_mixed_bound_strict_power_of_two_exponent": str(
            _strict_power_two_exponent(maximum_q_bound)),
        "maximum_q_mixed_bound_is_below_2_pow_103": (
            maximum_q_bound < 2**103),
        "auxiliary_section_4_by_3_rectangle": rectangle,
        "Q_bounds_match_weighted_prerequisite": q_matches,
    }, zero_exact)


def _source_formula_factor_plan() -> tuple[list[dict[str, Any]], int]:
    """Derive the maximum factor count from the four source-map layers."""
    specifications = (
        {
            "id": "zero_energy_radial_section",
            "operation": "explicit_product",
            "primitive_factor_slots": 3,
            "required_sources": ["zero_energy_q_mixed_jets"],
        },
        {
            "id": "Moser_forward_map",
            "operation": "composition",
            "outer_tensor_slots": 1,
            "required_sources": ["Moser_forward_map_jets"],
        },
        {
            "id": "Kato_C_AK_change",
            "operation": "left_products",
            "new_factor_slots": 1,
            "required_sources": ["Kato_C_AK_jets"],
        },
        {
            "id": "P2d_kappa_rotation_completion",
            "operation": "left_products",
            "new_factor_slots": 2,
            "required_sources": ["P2d_kappa_rotation_jets"],
        },
    )
    factor_count = 0
    records: list[dict[str, Any]] = []
    for specification in specifications:
        incoming = factor_count
        operation = specification["operation"]
        if operation == "explicit_product":
            factor_count = int(specification["primitive_factor_slots"])
        elif operation == "composition":
            factor_count = (int(specification["outer_tensor_slots"])
                            + MAX_TOTAL_ORDER * factor_count)
        elif operation == "left_products":
            factor_count += int(specification["new_factor_slots"])
        else:  # pragma: no cover - the tuple above is closed and frozen.
            raise PhysicalSlidesCheckError(
                f"unknown source formula operation: {operation}")
        records.append({
            **specification,
            "incoming_max_factor_count": str(incoming),
            "outgoing_max_factor_count": str(factor_count),
        })
    return records, factor_count


def _source_jet_budget(
        prerequisite: dict[str, Any], p2a: dict[str, Any],
        p2b_jets: dict[str, Any],
        kato: dict[str, Any], frame: dict[str, Any]) -> dict[str, Any]:
    normal_form = weighted.zero_energy.normal_form
    normal_constants = normal_form.c2_and_primitive_bounds(
        Fraction(1, 2**22), Fraction(691200, 691163), 2)
    require(all(normal_constants.get("checks", {}).values()),
            "the Moser C2 source constants are not all PASS")
    zero_source, zero_exact = _zero_energy_source_rectangle(prerequisite)
    frame_probe = frame["certificate"].get("raw_probe", {})
    kato_probe = kato["certificate"].get("raw_probe", {})
    source_objects = {
        "zero_energy_q_mixed_jets": zero_source,
        "Moser_forward_map_jets": normal_constants,
        "Kato_C_AK_jets": {
            "value_operator_bound_sigma": kato_probe.get(
                "scalar_enclosures", {}).get("sigma", {}),
            "D1_operator_bound": kato_probe.get(
                "normalized_parameter_jet_enclosures", {}).get(
                    "C_AK_D1", {}),
            "D2_operator_bound": kato_probe.get(
                "normalized_parameter_jet_enclosures", {}).get(
                    "C_AK_D2", {}),
        },
        "P2d_kappa_rotation_jets": {
            "kappa_inverse_sqrt": frame_probe.get(
                "scalar_jets", {}).get("kappa_inverse_sqrt", {}),
            "cos_theta": frame_probe.get(
                "scalar_jets", {}).get("cos_theta", {}),
            "sin_theta": frame_probe.get(
                "scalar_jets", {}).get("sin_theta", {}),
        },
    }
    object_budgets: dict[str, dict[str, Any]] = {}
    object_exponents: list[int] = []
    for name, value in source_objects.items():
        magnitudes = list(_iter_rational_magnitudes(value))
        require(magnitudes, f"the required source-jet object is empty: {name}")
        maximum = max(magnitudes)
        exponent = _strict_power_two_exponent(maximum)
        object_exponents.append(exponent)
        object_budgets[name] = {
            "maximum_absolute_entry": rational(maximum),
            "strict_power_of_two_exponent": str(exponent),
        }

    individual_accumulator_exponent = max(object_exponents)
    layer_records, maximum_product_factor_count = (
        _source_formula_factor_plan())
    accumulator_product_exponent = (
        individual_accumulator_exponent * maximum_product_factor_count)
    state_cauchy_gap = as_fraction(
        zero_exact.get("constants", {}).get("epsilon_nf"),
        "normal-form state radius") / 16
    zero_energy_action_gap = as_fraction(
        zero_exact.get("constants", {}).get("nu_cauchy_gap"),
        "zero-energy nu Cauchy gap")
    weighted_constants = prerequisite.get("exact_values", {}).get(
        "constants", {})
    weighted_action_gap = (
        as_fraction(weighted_constants.get("weighted_analytic_radius"),
                    "weighted analytic radius")
        - as_fraction(weighted_constants.get("weighted_passage_radius"),
                      "weighted passage radius"))
    action_cauchy_gap = min(zero_energy_action_gap, weighted_action_gap)
    state_gap_inverse_exponent = _strict_power_two_exponent(
        1 / state_cauchy_gap)
    action_gap_inverse_exponent = _strict_power_two_exponent(
        1 / action_cauchy_gap)
    factorial_exponent = _strict_power_two_exponent(
        math.factorial(MAX_TOTAL_ORDER))
    cauchy_loss_exponent = (
        MAX_STATE_ORDER
        * (state_gap_inverse_exponent + action_gap_inverse_exponent)
        + factorial_exponent)
    bell_number = _bell_number(MAX_TOTAL_ORDER)
    bell_exponent = _strict_power_two_exponent(bell_number)
    formula_rule_count = len(layer_records)
    component_sum_exponent = _strict_power_two_exponent(
        4**MAX_TOTAL_ORDER)
    colored_allocation_exponent = _strict_power_two_exponent(
        (MAX_PARAMETER_ORDER + 1)**formula_rule_count)
    product_partition_exponent = (
        formula_rule_count * bell_exponent
        + component_sum_exponent + colored_allocation_exponent)
    derived_exponent = (
        accumulator_product_exponent + cauchy_loss_exponent
        + product_partition_exponent)
    return {
        "required_source_objects": object_budgets,
        "zero_energy_source_rectangle": zero_source,
        "source_formula_layers": layer_records,
        "state_Cauchy_gap": rational(state_cauchy_gap),
        "action_Cauchy_gap": rational(action_cauchy_gap),
        "zero_energy_q_Cauchy_gap": rational(zero_energy_action_gap),
        "weighted_passage_Cauchy_gap": rational(weighted_action_gap),
        "individual_accumulator_power_of_two_exponent": str(
            individual_accumulator_exponent),
        "maximum_product_factor_count": str(maximum_product_factor_count),
        "accumulator_product_power_of_two_exponent": str(
            accumulator_product_exponent),
        "Cauchy_loss_power_of_two_exponent": str(cauchy_loss_exponent),
        "Cauchy_loss_components": {
            "state_gap_inverse_exponent": str(state_gap_inverse_exponent),
            "action_gap_inverse_exponent": str(action_gap_inverse_exponent),
            "maximum_state_order": str(MAX_STATE_ORDER),
            "factorial_exponent": str(factorial_exponent),
        },
        "product_partition_power_of_two_exponent": str(
            product_partition_exponent),
        "partition_components": {
            "formula_rule_count": str(formula_rule_count),
            "Bell_5": str(bell_number),
            "Bell_5_exponent": str(bell_exponent),
            "component_sum_exponent": str(component_sum_exponent),
            "colored_allocation_exponent": str(colored_allocation_exponent),
        },
        "derived_source_jet_power_of_two_exponent": str(derived_exponent),
        "frozen_source_jet_power_of_two_exponent": str(SOURCE_JET_EXPONENT),
        "checks": {
            "zero_energy_q_mixed_table_is_complete_3_by_4": (
                zero_source["nu_derivative_orders"] == list(range(4))
                and zero_source["normalized_parameter_orders"] == list(range(3))
                and all(len(row) == 4 for row in
                    zero_source["q_mixed_bounds"].values())),
            "maximum_zero_energy_q_mixed_bound_is_below_2_pow_103": (
                zero_source["maximum_q_mixed_bound_is_below_2_pow_103"] is True),
            "zero_energy_Q_bounds_match_weighted_prerequisite": all(
                zero_source["Q_bounds_match_weighted_prerequisite"].values()),
            "auxiliary_section_rectangle_is_complete_4_by_3": (
                len(zero_source["auxiliary_section_4_by_3_rectangle"]) == 4
                and all(len(row) == 3 for row in zero_source[
                    "auxiliary_section_4_by_3_rectangle"].values())),
            "auxiliary_section_rectangle_is_below_2_pow_130": all(
                as_fraction(entry["absolute_upper"], "section source bound")
                < 2**130
                for row in zero_source[
                    "auxiliary_section_4_by_3_rectangle"].values()
                for entry in row),
            "all_required_source_objects_have_derived_budgets": (
                set(object_budgets) == set(source_objects)),
            "Kato_C_AK_value_D1_D2_jets_are_included": (
                bool(kato_probe.get("scalar_enclosures", {}).get("sigma"))
                and bool(kato_probe.get(
                    "normalized_parameter_jet_enclosures", {}).get(
                        "C_AK_D1"))
                and bool(kato_probe.get(
                    "normalized_parameter_jet_enclosures", {}).get(
                        "C_AK_D2"))),
            "P2d_kappa_and_rotation_value_D1_D2_jets_are_included": (
                bool(frame_probe.get("scalar_jets", {}).get(
                    "kappa_inverse_sqrt"))
                and bool(frame_probe.get("scalar_jets", {}).get("cos_theta"))
                and bool(frame_probe.get("scalar_jets", {}).get("sin_theta"))),
            "four_source_formula_layers_are_explicit": formula_rule_count == 4,
            "maximum_factor_count_is_program_derived": (
                maximum_product_factor_count
                == int(layer_records[-1]["outgoing_max_factor_count"])),
            "Cauchy_losses_are_derived_from_authenticated_gaps": (
                state_cauchy_gap > 0 and action_cauchy_gap > 0
                and state_cauchy_gap == Fraction(1, 2**26)
                and zero_energy_action_gap > action_cauchy_gap
                and weighted_action_gap == action_cauchy_gap
                and action_cauchy_gap == WEIGHTED_RADIUS
                and cauchy_loss_exponent > 0),
            "partition_cost_is_derived_from_Bell_5_and_four_layers": (
                bell_number == 52 and product_partition_exponent > 0),
            "augmented_external_parameter_identity_is_below_source_bound": (
                1 < 2**SOURCE_JET_EXPONENT),
            "derived_source_budget_is_below_frozen_2_pow_4096": (
                derived_exponent < SOURCE_JET_EXPONENT),
        },
    }


def compute_physical_bounds(
        prerequisite: dict[str, Any], p2a: dict[str, Any],
        p2b_jets: dict[str, Any], kato: dict[str, Any],
        frame: dict[str, Any],
        ) -> dict[str, Any]:
    weighted_exact = prerequisite.get("exact_values", {})
    weighted_constants = weighted_exact.get("constants", {})
    section_radius = as_fraction(
        weighted_constants.get("section_radius_rho"), "section_radius_rho")
    weighted_radius = as_fraction(
        weighted_constants.get("weighted_passage_radius"),
        "weighted_passage_radius")
    weighted_checks = weighted_exact.get("checks", {})
    require(isinstance(weighted_checks, dict), "weighted checks are missing")

    frame_enclosures = p2a["frame_block"].get("enclosures", {})
    coarse_enclosures = p2a["coarse_graph"].get("enclosures", {})
    gamma0 = interval(coarse_enclosures.get("gamma0"), "P2a.gamma0")
    difference_cone = interval(
        frame_enclosures.get("difference_cone_margin"),
        "P2a.difference_cone_margin")
    unstable_speed = interval(
        frame_enclosures.get("unstable_face_outward_margin"),
        "P2a.unstable_face_outward_margin")
    stable_speed = interval(
        frame_enclosures.get("stable_face_inward_margin"),
        "P2a.stable_face_inward_margin")
    sigma = interval(kato["sigma_record"], "P2bK.sigma")
    kappa_inverse_sqrt = interval(
        frame["kappa_record"], "P2d.kappa_inverse_sqrt")

    stable_normal_form_upper = (
        ONE_PLUS_P_SQUARED_SQRT_UPPER * weighted_radius / section_radius)
    unstable_initial_lower = FRAME_SCALE_LOWER * (
        section_radius - MOSER_TWO_SIDED_DISPLACEMENT)
    unstable_initial_upper = FRAME_SCALE_UPPER * (
        section_radius + MOSER_TWO_SIDED_DISPLACEMENT)
    stable_initial_upper = FRAME_SCALE_UPPER * (
        stable_normal_form_upper + MOSER_TWO_SIDED_DISPLACEMENT)
    chart_exit_unstable_lower = FRAME_SCALE_LOWER * (
        CHART_SOURCE_RADIUS - MOSER_TWO_SIDED_DISPLACEMENT)

    exponential_lower = Fraction(8, 3) ** 12 * Fraction(17, 9)
    time_margin = exponential_lower * unstable_initial_lower - PHYSICAL_RADIUS
    comparison_upper = (
        Fraction(2) + BETA_UPPER * Fraction(TOTAL_SLIDE_TIME_UPPER, 6))
    field_budget = _field_derivative_budget(p2b_jets)
    source_budget = _source_jet_budget(
        prerequisite, p2a, p2b_jets, kato, frame)
    terminal_frame_budget = _terminal_frame_budget(p2b_jets)
    rectangle = _mixed_jet_rectangle()
    flow_recurrence = _flow_exponent_recurrence()
    hit_function_recurrence = _hit_function_exponent_recurrence(
        flow_recurrence)
    hit_time_recurrence = _hit_time_exponent_recurrence(
        hit_function_recurrence)
    endpoint_recurrence = _endpoint_exponent_recurrence(
        flow_recurrence, hit_time_recurrence)

    checks = {
        "physical_face_is_inherited_radius_one_over_one_hundred": (
            PHYSICAL_RADIUS == Fraction(1, 100)),
        "section_radius_matches_weighted_prerequisite": (
            section_radius == SECTION_RADIUS),
        "weighted_radius_matches_weighted_prerequisite": (
            weighted_radius == WEIGHTED_RADIUS),
        "weighted_p_absolute_bound_is_authenticated": (
            weighted_checks.get("p_absolute_bound_is_below_five_fourths") is True),
        "P2a_gamma0_exceeds_two_thirds": gamma0[0] > SIGMA_LOWER,
        "P2a_difference_cone_exceeds_one": difference_cone[0] > 1,
        "P2a_unstable_face_speed_exceeds_one_over_150": (
            unstable_speed[0] > RADIAL_SPEED_LOWER),
        "P2a_stable_face_speed_exceeds_one_over_150": (
            stable_speed[0] > RADIAL_SPEED_LOWER),
        "P2bK_sigma_is_strictly_between_two_thirds_and_three_fourths": (
            sigma[0] > SIGMA_LOWER and sigma[1] < SIGMA_UPPER),
        "P2d_kappa_inverse_sqrt_is_strictly_between_63_64_and_65_64": (
            kappa_inverse_sqrt[0] > KAPPA_INVERSE_SQRT_LOWER
            and kappa_inverse_sqrt[1] < KAPPA_INVERSE_SQRT_UPPER),
        "Moser_displacement_is_smaller_than_section_radius": (
            MOSER_TWO_SIDED_DISPLACEMENT < section_radius),
        "initial_unstable_radius_exceeds_two_to_minus_25": (
            unstable_initial_lower > Fraction(1, 2**25)),
        "initial_unstable_radius_is_below_two_to_minus_24": (
            unstable_initial_upper < Fraction(1, 2**24)),
        "initial_stable_radius_is_below_one_32_unstable_radius": (
            stable_initial_upper < unstable_initial_lower / 32),
        "initial_radii_are_inside_physical_face": (
            unstable_initial_upper < PHYSICAL_RADIUS),
        "chart_exit_radius_exceeds_every_auxiliary_face_radius": (
            chart_exit_unstable_lower > unstable_initial_upper),
        "each_slide_time_is_strictly_below_19": time_margin > 0,
        "physical_face_squared_hit_speed_exceeds_one_over_7500": (
            SQUARED_FACE_SPEED_LOWER == Fraction(1, 7500)),
        "normalized_first_hit_speed_exceeds_four_thirds": (
            NORMALIZED_HIT_SPEED_LOWER == Fraction(4, 3)),
        "D12_comparison_is_strictly_below_7": (
            comparison_upper < PHYSICAL_COMPARISON_CONSTANT),
        "complete_Cmu2_Cstate3_rectangle_is_present": (
            len(rectangle["normalized_4_by_3_rectangle"]) == 4
            and all(len(row) == 3 for row in
                    rectangle["normalized_4_by_3_rectangle"].values())),
        "zero_order_hit_time_uses_19_below_2_pow_5": (
            SLIDE_TIME_UPPER < 2**HIT_TIME_VALUE_EXPONENT
            and conservative_mixed_jet_exponent(
                0, 0, endpoint=False) == HIT_TIME_VALUE_EXPONENT),
        "zero_order_endpoint_has_explicit_bound_below_one": (
            ENDPOINT_VALUE_UPPER < 1
            and conservative_mixed_jet_exponent(0, 0)
            == ENDPOINT_VALUE_EXPONENT),
        "P2b_field_derivative_budget_passes": all(
            field_budget["checks"].values()),
        "auxiliary_source_jet_budget_passes": all(
            source_budget["checks"].values()),
        "terminal_T_mu_budget_passes": all(
            terminal_frame_budget["checks"].values()),
        "flow_exponent_recurrence_matches_proof": (
            flow_recurrence == FLOW_JET_EXPONENTS),
        "hit_function_exponent_recurrence_matches_proof": (
            hit_function_recurrence == HIT_FUNCTION_EXPONENTS),
        "hit_time_exponent_recurrence_matches_proof": (
            hit_time_recurrence == HIT_TIME_EXPONENTS),
        "endpoint_exponent_recurrence_matches_proof": (
            endpoint_recurrence == ENDPOINT_EXPONENTS),
        "original_parameter_conversion_is_below_2_pow_10": (
            max(left * right for left in ORIGINAL_PARAMETER_SCALES.values()
                for right in ORIGINAL_PARAMETER_SCALES.values()) < 2**10),
    }

    return {
        "constants": {
            "physical_face_radius": rational(PHYSICAL_RADIUS),
            "section_radius_rho": rational(section_radius),
            "chart_source_radius_rho_src": rational(CHART_SOURCE_RADIUS),
            "weighted_radius_nu_p": rational(weighted_radius),
            "weighted_p_upper": rational(WEIGHTED_P_UPPER),
            "sqrt_one_plus_p_squared_upper": rational(
                ONE_PLUS_P_SQUARED_SQRT_UPPER),
            "Moser_forward_displacement": rational(
                MOSER_FORWARD_DISPLACEMENT),
            "Moser_two_sided_displacement": rational(
                MOSER_TWO_SIDED_DISPLACEMENT),
            "frame_scale_lower": rational(FRAME_SCALE_LOWER),
            "frame_scale_upper": rational(FRAME_SCALE_UPPER),
        },
        "authenticated_intervals": {
            "P2a_gamma0": {"lower": rational(gamma0[0]),
                            "upper": rational(gamma0[1])},
            "P2a_difference_cone_margin": {
                "lower": rational(difference_cone[0]),
                "upper": rational(difference_cone[1])},
            "P2a_unstable_face_outward_margin": {
                "lower": rational(unstable_speed[0]),
                "upper": rational(unstable_speed[1])},
            "P2a_stable_face_inward_margin": {
                "lower": rational(stable_speed[0]),
                "upper": rational(stable_speed[1])},
            "P2bK_sigma": {"lower": rational(sigma[0]),
                            "upper": rational(sigma[1])},
            "P2d_kappa_inverse_sqrt": {
                "lower": rational(kappa_inverse_sqrt[0]),
                "upper": rational(kappa_inverse_sqrt[1])},
        },
        "initial_cone": {
            "stable_normal_form_radius_upper": rational(
                stable_normal_form_upper),
            "unstable_physical_radius_lower": rational(
                unstable_initial_lower),
            "unstable_physical_radius_upper": rational(
                unstable_initial_upper),
            "stable_physical_radius_upper": rational(stable_initial_upper),
            "stable_to_unstable_ratio_upper": rational(
                stable_initial_upper / unstable_initial_lower),
            "chart_exit_unstable_radius_lower": rational(
                chart_exit_unstable_lower),
            "no_auxiliary_recross_margin": rational(
                chart_exit_unstable_lower - unstable_initial_upper),
        },
        "slide_bounds": {
            "incoming_time_strict_upper": str(SLIDE_TIME_UPPER),
            "outgoing_time_strict_upper": str(SLIDE_TIME_UPPER),
            "total_time_strict_upper": str(TOTAL_SLIDE_TIME_UPPER),
            "exp_38_over_3_rational_lower": rational(exponential_lower),
            "time_gate_margin": rational(time_margin),
            "radial_speed_strict_lower": rational(RADIAL_SPEED_LOWER),
            "squared_face_hit_speed_strict_lower": rational(
                SQUARED_FACE_SPEED_LOWER),
            "normalized_face_hit_speed_strict_lower": rational(
                NORMALIZED_HIT_SPEED_LOWER),
            "D12_radial_comparison_upper": rational(2),
            "D12_phase_slide_contribution_upper": rational(
                BETA_UPPER * Fraction(TOTAL_SLIDE_TIME_UPPER, 6)),
            "D12_physical_comparison_upper": rational(comparison_upper),
            "D12_frozen_integer_constant": str(PHYSICAL_COMPARISON_CONSTANT),
        },
        "field_derivative_budget": field_budget,
        "source_jet_budget": source_budget,
        "terminal_frame_budget": terminal_frame_budget,
        "mixed_jet_bounds": rectangle,
        "checks": checks,
    }


def build_report(
        frame_path: Path = FRAME_PATH,
        normal_form_theory_path: Path = weighted.zero_energy.normal_form.THEORY_PATH,
        zero_energy_proof_path: Path = weighted.zero_energy.PROOF_PATH,
        exact_sections_proof_path: Path = weighted.exact_sections.PROOF_PATH,
        weighted_proof_path: Path = weighted.PROOF_PATH,
        proof_path: Path = PROOF_PATH,
        p2a_path: Path = P2A_PATH,
        p2b_jets_path: Path = P2B_JETS_PATH,
        kato_path: Path = KATO_PATH,
        moser_path: Path = MOSER_PATH,
        config_path: Path = CONFIG_PATH,
        p2c_config_path: Path = P2C_CONFIG_PATH,
        ) -> dict[str, Any]:
    prerequisite = weighted.build_report(
        frame_path, normal_form_theory_path, zero_energy_proof_path,
        exact_sections_proof_path, weighted_proof_path)
    require(prerequisite.get("schema_version") == weighted.SCHEMA_VERSION,
            "weighted-passage checker schema changed")
    require(prerequisite.get("scope") == weighted.SCOPE,
            "weighted-passage checker scope changed")
    require(prerequisite.get("status") in {"PASS", "INCONCLUSIVE", "FAIL"},
            "weighted-passage checker status is malformed")
    require(prerequisite.get("local_chart_status", {}).get(
        "V2.EXACT_CHART") == "OPEN",
        "weighted-passage prerequisite changed the parent boundary")

    p2a, p2b_jets, kato, frame, moser, config = authenticate_sources(
        p2a_path, p2b_jets_path, kato_path, frame_path, moser_path,
        config_path, p2c_config_path)
    require(frame["sha256"] == prerequisite.get(
        "source_authentication", {}).get("frame_certificate_sha256"),
        "physical-slides and weighted-passage frame digests differ")

    exact = compute_physical_bounds(
        prerequisite, p2a, p2b_jets, kato, frame)
    binding = proof_binding(proof_path)
    prerequisite_source_pass = prerequisite.get("source_gate_status") == "PASS"
    prerequisite_local_pass = (
        prerequisite.get("status") == "PASS"
        and prerequisite.get("mathematical_status") == "LOCAL_MATHEMATICAL_PASS"
        and prerequisite.get("proof_binding", {}).get("matched") is True
        and prerequisite.get("local_chart_status", {}).get(
            "V2.CHART.WEIGHTED_PASSAGE") == "PASS")
    all_source_checks_pass = (
        prerequisite_source_pass and all(exact["checks"].values()))
    local_atom_pass = (
        all_source_checks_pass and prerequisite_local_pass and binding["matched"])

    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "status": ("PASS" if local_atom_pass else
                   "INCONCLUSIVE" if all_source_checks_pass else "FAIL"),
        "source_gate_status": "PASS" if all_source_checks_pass else "FAIL",
        "mathematical_status": (
            "LOCAL_MATHEMATICAL_PASS" if local_atom_pass else
            "INCONCLUSIVE" if all_source_checks_pass else "FAIL"),
        "mathematical_pass_scope": (
            "LOCAL_PHYSICAL_SLIDES_ATOM" if local_atom_pass else "NONE"),
        "claim_bearing": False,
        "release_eligible": False,
        "independent_replay": "1/2",
        "source_authentication": {
            "weighted_checker_schema": prerequisite["schema_version"],
            "weighted_status": prerequisite["status"],
            "weighted_local_pass": prerequisite_local_pass,
            "weighted_proof_sha256": prerequisite.get(
                "proof_binding", {}).get("observed_sha256"),
            P2A_RELATIVE: p2a["sha256"],
            P2B_JETS_RELATIVE: p2b_jets["sha256"],
            KATO_RELATIVE: kato["sha256"],
            FRAME_RELATIVE: frame["sha256"],
            MOSER_RELATIVE: moser["observed_sha256"],
            CONFIG_RELATIVE: config["sha256"],
            P2C_CONFIG_RELATIVE: config["p2c_config_sha256"],
            "seven_frozen_source_hashes_matched": True,
            "local_event_support_family": config["event_contract"][
                "family_id"],
            "local_event_support_restriction": config["event_contract"][
                "restriction_to_closed_physical_saddle_block"],
        },
        "proof_binding": binding,
        "exact_values": exact,
        "local_chart_status": {
            "V2.CHART.SYMPLECTIC_FRAME": "PASS",
            "V2.CHART.ANALYTIC_NORMAL_FORM": "PASS",
            "V2.CHART.ZERO_ENERGY": (
                prerequisite.get("local_chart_status", {}).get(
                    "V2.CHART.ZERO_ENERGY", "OPEN")),
            "V2.CHART.EXACT_SECTIONS": (
                prerequisite.get("local_chart_status", {}).get(
                    "V2.CHART.EXACT_SECTIONS", "OPEN")),
            "V2.CHART.WEIGHTED_PASSAGE": (
                "PASS" if prerequisite_local_pass else "OPEN"),
            "V2.CHART.PHYSICAL_SLIDES": (
                "PASS" if local_atom_pass else "OPEN"),
            "V2.CHART.OVERLAPS": "OPEN",
            "V2.EXACT_CHART": "OPEN",
        },
        "claim_boundary": {
            "local_child_only": True,
            "claim_bearing": False,
            "V2_EXACT_CHART": "OPEN",
            "physical_winding_residence_comparison": (
                {"status": "PASS", "C": str(PHYSICAL_COMPARISON_CONSTANT)}
                if local_atom_pass else {"status": "OPEN", "C": None}),
            "local_event_exclusion": (
                "PASS: flowbox event supports begin outside ||u||=1/100"
                if local_atom_pass else "OPEN"),
            "V2_EVENT_ATLAS_P2e": "OPEN",
            "excluded": [
                "finite chart overlap atlas",
                "complete physical event-cell census and continuation (P2e)",
                "later positive-end obligations",
                "temporal stability, Turing selection, and canard identification",
            ],
        },
    }


def emit(value: dict[str, Any]) -> None:
    sys.stdout.write(canonical_json(value))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame-certificate", type=Path, default=FRAME_PATH)
    parser.add_argument("--normal-form-theory", type=Path,
                        default=weighted.zero_energy.normal_form.THEORY_PATH)
    parser.add_argument("--zero-energy-proof", type=Path,
                        default=weighted.zero_energy.PROOF_PATH)
    parser.add_argument("--exact-sections-proof", type=Path,
                        default=weighted.exact_sections.PROOF_PATH)
    parser.add_argument("--weighted-proof", type=Path, default=weighted.PROOF_PATH)
    parser.add_argument("--proof", type=Path, default=PROOF_PATH)
    parser.add_argument("--p2a-certificate", type=Path, default=P2A_PATH)
    parser.add_argument("--p2b-jets-certificate", type=Path,
                        default=P2B_JETS_PATH)
    parser.add_argument("--kato-certificate", type=Path, default=KATO_PATH)
    parser.add_argument("--moser-proof", type=Path, default=MOSER_PATH)
    parser.add_argument("--configuration", type=Path, default=CONFIG_PATH)
    parser.add_argument("--p2c-configuration", type=Path,
                        default=P2C_CONFIG_PATH)
    arguments = parser.parse_args(argv)
    try:
        report = build_report(
            arguments.frame_certificate.resolve(),
            arguments.normal_form_theory.resolve(),
            arguments.zero_energy_proof.resolve(),
            arguments.exact_sections_proof.resolve(),
            arguments.weighted_proof.resolve(),
            arguments.proof.resolve(),
            arguments.p2a_certificate.resolve(),
            arguments.p2b_jets_certificate.resolve(),
            arguments.kato_certificate.resolve(),
            arguments.moser_proof.resolve(),
            arguments.configuration.resolve(),
            arguments.p2c_configuration.resolve(),
        )
    except (OSError, UnicodeError, json.JSONDecodeError,
            PhysicalSlidesCheckError, weighted.WeightedPassageCheckError,
            weighted.exact_sections.ExactSectionsCheckError,
            weighted.zero_energy.ZeroEnergyCheckError,
            weighted.zero_energy.normal_form.SourceCheckError,
            weighted.zero_energy.normal_form.scout.ScoutInputError,
            subprocess.SubprocessError, KeyError, TypeError) as error:
        emit({
            "schema_version": SCHEMA_VERSION,
            "scope": SCOPE,
            "status": "INPUT_REJECTED",
            "mathematical_status": "INCONCLUSIVE",
            "error": str(error),
            "claim_bearing": False,
            "local_chart_status": {
                "V2.CHART.PHYSICAL_SLIDES": "OPEN",
                "V2.CHART.OVERLAPS": "OPEN",
                "V2.EXACT_CHART": "OPEN",
            },
            "claim_boundary": {
                "physical_winding_residence_comparison": "OPEN",
                "V2_EVENT_ATLAS_P2e": "OPEN",
            },
        })
        return 2
    emit(report)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
