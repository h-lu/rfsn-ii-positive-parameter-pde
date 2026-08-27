#!/usr/bin/env python3
"""Check a staged rigorous certificate without upgrading an inconclusive run."""

from __future__ import annotations

import argparse
import json
import math
import os
import shlex
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import jsonschema

from rigorous_common import (
    box_arguments,
    combine_verdicts,
    fraction,
    git_output,
    load_json,
    p2_jets_arguments,
    safe_repository_path,
    sha256_bytes,
    sha256_file,
    validate_exact_bridge,
    validate_exact_box,
    validate_h10_c01_configuration,
    validate_local_graph_configuration,
    validate_p2_jets_configuration,
    validate_p2b0_true_tube_implication,
)

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
P0_IDS = {
    "ENV.SOURCE_BINDING",
    "ENV.CAPD_BINDING",
    "ENV.ROUNDING",
    "BOX.FROZEN",
}
KERNEL_IDS = P0_IDS | {
    "V1.REVERSIBILITY",
    "V1.HAMILTONIAN",
    "V2.1.WEDGE",
    "V2.1.POSITIVITY",
    "V2.1.SADDLE_FOCUS",
}
LOCAL_GRAPH_P0_IDS = P0_IDS | {
    "BRIDGE.FROZEN",
    "P2.LOCAL_GRAPH_CONFIG_FROZEN",
}
LOCAL_GRAPH_IDS = LOCAL_GRAPH_P0_IDS | {
    "V2.WU.FRAME_BLOCK",
    "V2.WU.COARSE_GRAPH",
}
H10_C01_P0_IDS = LOCAL_GRAPH_P0_IDS | {
    "P2.P2A_PREREQUISITE",
    "P2.H10_C01_CONFIG_FROZEN",
    "P2.H10_CENTER_EXACT",
}
H10_C01_IDS = H10_C01_P0_IDS | {
    "V2.WU.H10_C0_TUBE",
    "V2.WU.H10_C1_TUBE",
}
P2_JETS_P0_IDS = LOCAL_GRAPH_P0_IDS | {
    "P2.P2A_PREREQUISITE",
    "P2.P2B0_PREREQUISITE",
    "P2.JETS_CONFIG_FROZEN",
}
P2_JETS_IDS = P2_JETS_P0_IDS | {
    "P2.JETS.COEFFICIENTS",
    "V2.WU.STATE_C23",
    "V2.WU.MIXED_JETS",
    "V2.WU.WEIGHTED_HALF_ORBITS",
    "V2.WU.JETS",
    "V2.WU_GRAPH",
}
BASE_REQUIRED_BINDINGS = {
    "RESEARCH_CONTRACT.md",
    "theory/BASELINE.md",
    "van-der-pol/HAMILTONIAN_CHECK.md",
    "van-der-pol/MODEL_AND_CENTRAL_CHART.md",
    "van-der-pol/CENTRAL_CONTINUATION.md",
    "validation/rigorous/README.md",
    "validation/rigorous/certificate.schema.json",
    "validation/rigorous/parameter_box.schema.json",
    "validation/rigorous/config/vdp_box_v1.json",
    "validation/rigorous/dependency.lock.json",
    "validation/rigorous/flagship_import.lock.json",
    "validation/rigorous/obligations.json",
    "validation/rigorous/include/verdict.hpp",
    "validation/rigorous/include/interval_io.hpp",
    "validation/rigorous/include/rounding_self_test.hpp",
    "validation/rigorous/include/exact_polynomial.hpp",
    "validation/rigorous/src/rounding_self_test.cpp",
    "validation/rigorous/src/vdp_parameter_box_probe.cpp",
    "validation/rigorous/rigorous_common.py",
    "validation/rigorous/run_validation.py",
    "validation/rigorous/check_certificate.py",
}
LOCAL_GRAPH_REQUIRED_BINDINGS = BASE_REQUIRED_BINDINGS | {
    "validation/rigorous/P2_VALIDATION_CONTRACT.md",
    "validation/rigorous/continuation_bridge.schema.json",
    "validation/rigorous/p2_local_graph.schema.json",
    "validation/rigorous/config/vdp_bridge_v1.json",
    "validation/rigorous/config/vdp_p2_local_graph_v1.json",
    "validation/rigorous/src/vdp_local_graph_probe.cpp",
}
H10_C01_REQUIRED_BINDINGS = LOCAL_GRAPH_REQUIRED_BINDINGS | {
    "validation/rigorous/p2_h10_c01.schema.json",
    "validation/rigorous/config/vdp_p2_h10_c01_v1.json",
    "validation/rigorous/audit_h10_center.py",
    "validation/rigorous/src/vdp_h10_c01_probe.cpp",
    "validation/rigorous/results/vdp_bridge_v1_p2a_local_graph.json",
}
P2_JETS_REQUIRED_BINDINGS = H10_C01_REQUIRED_BINDINGS | {
    "validation/rigorous/p2_jets.schema.json",
    "validation/rigorous/config/vdp_p2_jets_v1.json",
    "validation/rigorous/src/vdp_p2_jets_probe.cpp",
    "validation/rigorous/results/vdp_bridge_v1_p2b_h10_c01.json",
    "validation/rigorous/design/README.md",
    "validation/rigorous/design/p2b_jets_scout.cpp",
}
LOCAL_FRAME_ENCLOSURES = {
    "four_minus_c_squared",
    "two_plus_c",
    "two_minus_c",
    "alpha",
    "beta",
    "unstable_face_outward_margin",
    "stable_face_inward_margin",
    "difference_cone_margin",
}
LOCAL_GRAPH_ENCLOSURES = {
    "gamma0",
    "one_minus_first_quadratic_coefficient",
    "gamma1",
    "one_quarter_minus_refined_quadratic_coefficient",
    "gamma1_minus_two_thirds",
}
H10_C0_ENCLOSURES = {
    "h10_euclidean_reference_margin",
    "dh10_frobenius_reference_margin",
    "core_defect_euclidean_reference_margin",
    "absolute_a_minus_one_parameter_margin",
    "b_parameter_margin",
    "absolute_c_parameter_margin",
    "alpha_parameter_margin",
    "q_norm_parameter_margin",
    "delta_block_operator_parameter_margin",
    "delta_q_norm_parameter_margin",
    "center_residual_euclidean_margin",
    "weighted_nonlinear_lipschitz_margin",
    "normal_contraction_margin",
    "c0_inward_margin_margin",
}
H10_C1_ENCLOSURES = {
    "d2h10_frobenius_reference_margin",
    "core_defect_derivative_frobenius_reference_margin",
    "center_residual_derivative_frobenius_margin",
    "weighted_nonlinear_second_margin",
    "c1_cone_margin_margin",
}
H10_PARAMETER_ENCLOSURES = {
    "r",
    "a2",
    "epsilon",
    "radius",
    "rho",
    "eta",
    "a",
    "b",
    "c",
    "alpha",
    "beta",
    "q_norm",
    "absolute_a_minus_one",
    "absolute_c",
    "delta_block_operator",
    "delta_q_norm",
}
H10_CENTER_ENCLOSURES = {
    "h10_component_1_abs",
    "h10_component_2_abs",
    "h10_euclidean",
    "dh10_frobenius",
    "d2h10_frobenius",
    "core_defect_euclidean",
    "core_defect_derivative_frobenius",
    "X0",
    "X",
    "Cq",
    "delta_G",
    "delta_G_prime",
    "E0",
    "E1",
    "ell",
    "m",
    "kappa",
    "Gu",
    "c0_inward_margin",
    "c1_cone_margin",
}
H10_REFERENCE_MARGINS = {
    "h10_euclidean_reference_margin",
    "dh10_frobenius_reference_margin",
    "d2h10_frobenius_reference_margin",
    "core_defect_euclidean_reference_margin",
    "core_defect_derivative_frobenius_reference_margin",
}
H10_PARAMETER_MARGINS = {
    "absolute_a_minus_one_parameter_margin",
    "b_parameter_margin",
    "absolute_c_parameter_margin",
    "alpha_parameter_margin",
    "q_norm_parameter_margin",
    "delta_block_operator_parameter_margin",
    "delta_q_norm_parameter_margin",
}
H10_ACCEPTANCE_MARGINS = {
    "center_residual_euclidean_margin",
    "center_residual_derivative_frobenius_margin",
    "weighted_nonlinear_lipschitz_margin",
    "weighted_nonlinear_second_margin",
    "normal_contraction_margin",
    "c0_inward_margin_margin",
    "c1_cone_margin_margin",
}
P2_JETS_PARAMETER_ENCLOSURES = {
    "r", "a2", "epsilon", "R", "Xstar", "Dstar", "omega",
    "hom_weight", "sigma2", "sigma3",
    "original_first_derivative_scale",
    "original_second_derivative_scale",
}
P2_JETS_COEFFICIENT_ENCLOSURES = {
    f"{prefix}_{order}"
    for prefix in ("B", "h", "ell", "m", "t")
    for order in range(3)
}
P2_JETS_COEFFICIENT_MARGINS = {
    f"{name}_upper_margin" for name in P2_JETS_COEFFICIENT_ENCLOSURES
}
P2_JETS_LP_COEFFICIENTS = {
    f"L_{state_order}_{parameter_order}"
    for state_order in range(4)
    for parameter_order in range(3)
}
P2_JETS_LP_ENCLOSURES = {
    "fixed_core_rate", "local_tail_weight",
    "final_homoclinic_weight_reserved", "core_rate_minus_local_weight",
    "local_minus_reserved_weight", "green_operator",
    "linearized_contraction", "one_minus_linearized_contraction",
    "resolvent",
}
P2_JETS_LP_MARGINS = {
    "alpha_lower_margin", "core_rate_minus_local_weight",
    "local_minus_reserved_weight", "green_operator_upper_margin",
    "linearized_contraction_upper_margin", "resolvent_upper_margin",
}
P2_JETS_STATE_ENCLOSURES = {
    "alpha", "kappa_bar", "M_2", "M_3",
    "state_second_no_first_exit_margin",
    "state_third_no_first_exit_margin", "origin_second_margin",
    "origin_third_margin",
}
P2_JETS_STATE_MARGINS = {
    "state_normal_gap_lower_margin",
    "state_second_no_first_exit_gate_margin",
    "state_third_no_first_exit_gate_margin",
    "origin_second_gate_margin", "origin_third_gate_margin",
}
P2_JETS_WEIGHTED_ENCLOSURES = {
    f"Z_{state_order}_{parameter_order}"
    for state_order in range(4)
    for parameter_order in range(3)
}
P2_JETS_WEIGHTED_MARGINS = {
    f"{name}_upper_margin" for name in P2_JETS_WEIGHTED_ENCLOSURES
}
P2_JETS_FRAME_ENCLOSURES = {"T_0", "T_1", "T_2"}
P2_JETS_STRUCTURE_CHECKS = {
    "gap_free_exact_rational_grid",
    "bridge_matches_parameter_normalization",
    "subdivisions_match_frozen_contract",
    "parameter_ad_hessians_symmetric",
    "algebraic_identities_contain_zero",
    "state_degree_at_most_three",
    "complete_parameter_multiindex_coverage",
    "original_parameter_scales_match_frozen_contract",
    "all_inputs_strictly_positive",
    "homoclinic_weight_below_local_weight",
    "parameter_grid_nonempty",
    "recurrence_complete",
}
P2_JETS_TERM_COUNTS = {
    "Z_0_0": 0, "Z_0_1": 1, "Z_0_2": 4,
    "Z_1_0": 0, "Z_1_1": 2, "Z_1_2": 9,
    "Z_2_0": 1, "Z_2_1": 6, "Z_2_2": 25,
    "Z_3_0": 4, "Z_3_1": 18, "Z_3_2": 73,
}
P2_JETS_FIRST_MULTIINDICES = ["theta_r", "theta_a", "theta_epsilon"]
P2_JETS_SECOND_MULTIINDICES = [
    "theta_r,theta_r", "theta_r,theta_a", "theta_r,theta_epsilon",
    "theta_a,theta_a", "theta_a,theta_epsilon",
    "theta_epsilon,theta_epsilon",
]
P2_JETS_RAW_FIELDS = {
    "schema_version", "status", "mathematical_status", "structure_status",
    "structure_checks", "rounding_self_test", "grid",
    "parameter_enclosures", "coefficient_upper_gates", "acceptance_gates",
    "normalized_weighted_jet_upper_gates", "coefficient_enclosures",
    "coefficient_gate_margins", "lyapunov_perron_coefficients",
    "lyapunov_perron_enclosures", "lyapunov_perron_gate_margins",
    "state_tensor_enclosures", "state_tensor_gate_margins",
    "weighted_jet_enclosures",
    "original_parameter_weighted_jet_enclosures",
    "frame_derivative_enclosures", "physical_weighted_jet_enclosures",
    "original_parameter_physical_weighted_jet_enclosures",
    "coordinate_composition", "linearization_contract",
    "weighted_jet_gate_margins", "recurrence", "obligations",
}
P2_JETS_SCOPE_NONCLAIM = (
    "The P2 mixed-jet kernel proves the local graph and weighted half-orbit "
    "obligations in the P2a algebraic frame; normalized Kato source phase, "
    "the selected homoclinic, exact charts, event atlas, V3--V6, temporal "
    "stability, Turing selection, and canard identification remain outside "
    "its scope."
)
COMMON_NONCLAIMS = [
    "A local mathematical PASS is not an aggregate theorem certificate.",
    "Independent-machine replay is pending and this certificate is not claim-bearing.",
]
PHASE1_SCOPE_NONCLAIM = (
    "Phase 1 does not validate V2 continuation beyond item (1), V3--V6, "
    "temporal stability, Turing selection, or canard identification."
)
LOCAL_GRAPH_SCOPE_NONCLAIM = (
    "The local-graph kernel proves only its two P2a subobligations; "
    "V2.WU_GRAPH mixed jets, the homoclinic, exact charts, event atlas, "
    "V3--V6, temporal stability, Turing selection, and canard identification "
    "remain outside its scope."
)
H10_C01_SCOPE_NONCLAIM = (
    "The H10 C0/C1 kernel proves only its two P2b0 tube subobligations; "
    "V2.WU.JETS and V2.WU_GRAPH mixed jets and weighted tails, the "
    "homoclinic, exact charts, event atlas, V3--V6, temporal stability, "
    "Turing selection, and canard identification remain outside its scope."
)
ROUNDING_IDS = {
    "ROUND.IEEE754_BINARY64",
    "ROUND.NO_FAST_MATH",
    "ROUND.CAPD_MODES",
    "ROUND.CAPD_LEGACY_SELF_TEST",
    "ROUND.DIRECTED_ADDITION",
    "ROUND.RATIONAL_DIVISION",
    "ROUND.NEGATIVE_RATIONAL_DIVISION",
    "ROUND.SQRT",
    "ROUND.DEPENDENCY_SQUARE",
    "ROUND.POLYNOMIAL_CONTAINMENT",
    "ROUND.HEX_SERIALIZATION",
    "ROUND.SUBNORMAL_MODE",
    "ROUND.RESTORE_NEAREST",
}


def schema_errors(certificate: dict[str, Any]) -> list[str]:
    schema = load_json(HERE / "certificate.schema.json")
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker())
    return [
        f"schema {'.'.join(str(part) for part in error.absolute_path) or '<root>'}: "
        f"{error.message}"
        for error in sorted(
            validator.iter_errors(certificate),
            key=lambda item: tuple(str(part) for part in item.path))
    ]


def _check_hex_interval(name: str, value: Any, errors: list[str]) -> None:
    expected_fields = {"lower_hex", "upper_hex", "endpoint_format"}
    if not isinstance(value, dict) or not {"lower_hex", "upper_hex"} <= set(value):
        errors.append(f"{name} is not a serialized interval")
        return
    if set(value) != expected_fields:
        errors.append(f"{name} serialized-interval fields changed")
    if value.get("endpoint_format") != "IEEE754_BINARY64_HEX":
        errors.append(f"{name} endpoint format changed")
    try:
        lower = float.fromhex(value["lower_hex"])
        upper = float.fromhex(value["upper_hex"])
    except (TypeError, ValueError) as error:
        errors.append(f"{name} has an invalid hexadecimal endpoint: {error}")
        return
    if not math.isfinite(lower) or not math.isfinite(upper):
        errors.append(f"{name} has a non-finite endpoint")
        return
    if lower > upper:
        errors.append(f"{name} has reversed endpoints")


def _strict_positive_interval_verdict(value: Any) -> str | None:
    try:
        lower = float.fromhex(value["lower_hex"])
        upper = float.fromhex(value["upper_hex"])
    except (KeyError, TypeError, ValueError):
        return None
    if lower > upper:
        return None
    if lower > 0.0:
        return "PASS"
    if upper <= 0.0:
        return "FAIL"
    return "INCONCLUSIVE"


def _sufficient_positive_interval_verdict(value: Any) -> str | None:
    """Reduce a sufficient-condition margin without inventing a counterexample."""

    try:
        lower = float.fromhex(value["lower_hex"])
        upper = float.fromhex(value["upper_hex"])
    except (KeyError, TypeError, ValueError):
        return None
    if lower > upper:
        return None
    return "PASS" if lower > 0.0 else "INCONCLUSIVE"


def _contains_exact_interval(value: Any, lower: Fraction,
                             upper: Fraction) -> bool:
    try:
        observed_lower = Fraction.from_float(float.fromhex(value["lower_hex"]))
        observed_upper = Fraction.from_float(float.fromhex(value["upper_hex"]))
    except (KeyError, TypeError, ValueError):
        return False
    return observed_lower <= lower <= upper <= observed_upper


def _check_interval_mapping(name: str, value: Any, expected: set[str],
                            errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{name} is not an interval mapping")
        return {}
    if set(value) != expected:
        errors.append(
            f"{name} field set changed: observed={sorted(value)}, "
            f"expected={sorted(expected)}")
    for field, enclosure in value.items():
        _check_hex_interval(f"{name}.{field}", enclosure, errors)
    return value


FractionInterval = tuple[Fraction, Fraction]


def _fraction_interval(value: Any) -> FractionInterval | None:
    try:
        lower_float = float.fromhex(value["lower_hex"])
        upper_float = float.fromhex(value["upper_hex"])
    except (KeyError, TypeError, ValueError):
        return None
    if not math.isfinite(lower_float) or not math.isfinite(upper_float):
        return None
    lower = Fraction.from_float(lower_float)
    upper = Fraction.from_float(upper_float)
    if lower > upper:
        return None
    return lower, upper


def _fi_add(left: FractionInterval,
            right: FractionInterval) -> FractionInterval:
    return left[0] + right[0], left[1] + right[1]


def _fi_neg(value: FractionInterval) -> FractionInterval:
    return -value[1], -value[0]


def _fi_sub(left: FractionInterval,
            right: FractionInterval) -> FractionInterval:
    return _fi_add(left, _fi_neg(right))


def _fi_mul(left: FractionInterval,
            right: FractionInterval) -> FractionInterval:
    products = (
        left[0] * right[0], left[0] * right[1],
        left[1] * right[0], left[1] * right[1],
    )
    return min(products), max(products)


def _fi_integer(value: int) -> FractionInterval:
    exact = Fraction(value)
    return exact, exact


def _fi_sum(values: list[FractionInterval]) -> FractionInterval:
    result = _fi_integer(0)
    for value in values:
        result = _fi_add(result, value)
    return result


def _fi_power(value: FractionInterval, exponent: int) -> FractionInterval:
    result = _fi_integer(1)
    for _ in range(exponent):
        result = _fi_mul(result, value)
    return result


def _fi_reciprocal(value: FractionInterval) -> FractionInterval | None:
    if value[0] <= 0 <= value[1]:
        return None
    return Fraction(1, 1) / value[1], Fraction(1, 1) / value[0]


def _check_contains_fraction_interval(
        name: str, observed: Any, expected: FractionInterval | None,
        errors: list[str]) -> None:
    actual = _fraction_interval(observed)
    if actual is None or expected is None:
        errors.append(f"{name} cannot be checked as a finite interval")
    elif not (actual[0] <= expected[0] <= expected[1] <= actual[1]):
        errors.append(f"{name} does not enclose its independently recomputed value")


def _check_difference_enclosure(
        name: str, observed: Any, left: Any, right: Any,
        errors: list[str]) -> None:
    left_interval = _fraction_interval(left)
    right_interval = _fraction_interval(right)
    expected = None if left_interval is None or right_interval is None else \
        _fi_sub(left_interval, right_interval)
    _check_contains_fraction_interval(name, observed, expected, errors)


def _check_product_enclosure(
        name: str, observed: Any, left: Any, right: Any,
        errors: list[str]) -> None:
    left_interval = _fraction_interval(left)
    right_interval = _fraction_interval(right)
    expected = None if left_interval is None or right_interval is None else \
        _fi_mul(left_interval, right_interval)
    _check_contains_fraction_interval(name, observed, expected, errors)


def _p2_partitions(labels: list[bool], maximum_blocks: int) -> list[list[list[int]]]:
    """Enumerate labelled set partitions independently of the C++ probe."""

    output: list[list[list[int]]] = []
    blocks: list[list[int]] = []

    def visit(position: int) -> None:
        if position == len(labels):
            if blocks and len(blocks) <= maximum_blocks:
                output.append([block.copy() for block in blocks])
            return
        existing = len(blocks)
        for block_index in range(existing):
            blocks[block_index].append(position)
            visit(position + 1)
            blocks[block_index].pop()
        if len(blocks) < maximum_blocks:
            blocks.append([position])
            visit(position + 1)
            blocks.pop()

    visit(0)
    return output


def _recompute_p2_weighted_jets(
        coefficient_values: dict[str, Any], green_value: Any,
        resolvent_value: Any, radius_value: Any,
        errors: list[str]) -> tuple[dict[str, FractionInterval], dict[str, int]]:
    """Rebuild the complete labelled Faà di Bruno rectangle from raw bounds."""

    try:
        coefficients = {
            (state_order, parameter_order):
                _fraction_interval(coefficient_values[
                    f"L_{state_order}_{parameter_order}"])
            for state_order in range(4)
            for parameter_order in range(3)
        }
        green = _fraction_interval(green_value)
        resolvent = _fraction_interval(resolvent_value)
        radius = _fraction_interval(radius_value)
    except KeyError as error:
        errors.append(f"P2 recurrence input is missing: {error}")
        return {}, {}
    if green is None or resolvent is None or radius is None or \
            any(value is None for value in coefficients.values()):
        errors.append("P2 recurrence input contains a malformed interval")
        return {}, {}

    typed_coefficients = {
        key: value for key, value in coefficients.items() if value is not None}
    jets: dict[tuple[int, int], FractionInterval] = {(0, 0): radius}
    counts: dict[str, int] = {"Z_0_0": 0}
    for total_order in range(1, 6):
        for state_order in range(4):
            for parameter_order in range(3):
                if state_order + parameter_order != total_order:
                    continue
                labels = [False] * state_order + [True] * parameter_order
                terms: list[FractionInterval] = []
                term_count = 0
                for mask in range(1 << len(labels)):
                    if any(
                            (mask >> index) & 1 and not labels[index]
                            for index in range(len(labels))):
                        continue
                    explicit_order = sum(
                        1 for index in range(len(labels))
                        if (mask >> index) & 1)
                    if explicit_order > 2:
                        continue
                    remaining = [
                        index for index in range(len(labels))
                        if not ((mask >> index) & 1)]
                    if not remaining:
                        if state_order == 0:
                            terms.append(typed_coefficients[(0, explicit_order)])
                            term_count += 1
                        continue
                    remaining_labels = [labels[index] for index in remaining]
                    for local_partition in _p2_partitions(
                            remaining_labels, 3):
                        if explicit_order == 0 and len(local_partition) == 1 \
                                and len(local_partition[0]) == len(labels):
                            continue
                        term = typed_coefficients[
                            (len(local_partition), explicit_order)]
                        for block in local_partition:
                            block_state = sum(
                                1 for index in block
                                if not remaining_labels[index])
                            block_parameter = len(block) - block_state
                            block_key = (block_state, block_parameter)
                            if block_key not in jets:
                                errors.append(
                                    "independent P2 recurrence is not triangular: "
                                    f"target=({state_order},{parameter_order}), "
                                    f"block={block_key}")
                                return {}, {}
                            term = _fi_mul(term, jets[block_key])
                        terms.append(term)
                        term_count += 1
                direct = _fi_integer(
                    1 if (state_order, parameter_order) == (1, 0) else 0)
                remainder = _fi_sum(terms)
                jets[(state_order, parameter_order)] = _fi_mul(
                    resolvent, _fi_add(direct, _fi_mul(green, remainder)))
                counts[f"Z_{state_order}_{parameter_order}"] = term_count
    return {
        f"Z_{state_order}_{parameter_order}": value
        for (state_order, parameter_order), value in jets.items()
    }, counts


def _h10_audit_status(audit: Any, configuration: dict[str, Any],
                      flagship_repository: Any,
                      errors: list[str]) -> str:
    """Recompute the exact-center audit verdict from its bound evidence."""

    if not isinstance(audit, dict):
        errors.append("H10 exact-center audit is not an object")
        return "INCONCLUSIVE"
    center = configuration.get("imported_core_center", {})
    protocol = configuration.get("exact_center_audit", {})
    if audit.get("schema_version") != "rfsn-vdp-h10-center-audit/1":
        errors.append("H10 exact-center audit schema version changed")
    if audit.get("commit") != center.get("commit"):
        errors.append("H10 exact-center audit commit differs from the frozen center")
    if audit.get("flagship_repository") != flagship_repository:
        errors.append(
            "H10 exact-center audit repository differs from the bound flagship")

    failures = audit.get("failures")
    reasons = audit.get("inconclusive_reasons")
    if not isinstance(failures, list) or not all(
            isinstance(item, str) for item in failures):
        errors.append("H10 exact-center audit failures are malformed")
        failures = []
    if not isinstance(reasons, list) or not all(
            isinstance(item, str) for item in reasons):
        errors.append("H10 exact-center audit inconclusive reasons are malformed")
        reasons = []

    exact_failure = False
    execution_inconclusive = False
    frozen_objects = audit.get("frozen_objects")
    if not isinstance(frozen_objects, dict):
        errors.append("H10 exact-center audit frozen_objects is malformed")
        frozen_objects = {}
        execution_inconclusive = True
    for name in ("generator", "term_table"):
        expected = center.get(name, {})
        record = frozen_objects.get(name, {})
        if not isinstance(record, dict):
            errors.append(f"H10 exact-center {name} record is malformed")
            execution_inconclusive = True
            continue
        if record.get("path") != expected.get("path") or \
                record.get("expected_sha256") != expected.get("sha256"):
            errors.append(f"H10 exact-center {name} binding changed")
        git_show = record.get("git_show", {})
        if not isinstance(git_show, dict):
            errors.append(f"H10 exact-center {name} git-show record is malformed")
            execution_inconclusive = True
        elif git_show.get("exit_code") != 0:
            execution_inconclusive = True
        else:
            argv = git_show.get("argv")
            expected_spec = f"{center.get('commit')}:{expected.get('path')}"
            expected_argv = [
                "git", "-C", flagship_repository, "show", expected_spec]
            if argv != expected_argv:
                errors.append(f"H10 exact-center {name} git-show argv changed")
            if git_show.get("stdout_sha256") != record.get("observed_sha256"):
                errors.append(
                    f"H10 exact-center {name} stdout hash is internally inconsistent")
            if git_show.get("stderr_sha256") != sha256_bytes(b""):
                errors.append(
                    f"H10 exact-center {name} git-show stderr is not empty")
        observed = record.get("observed_sha256")
        if isinstance(observed, str):
            matches = observed == expected.get("sha256")
            if record.get("hash_matches") is not matches:
                errors.append(f"H10 exact-center {name} hash_matches is inconsistent")
            exact_failure = exact_failure or not matches
        elif not execution_inconclusive:
            errors.append(f"H10 exact-center {name} observed hash is missing")
            execution_inconclusive = True

    regeneration = audit.get("regeneration")
    if not isinstance(regeneration, dict):
        errors.append("H10 exact-center regeneration record is malformed")
        regeneration = {}
        execution_inconclusive = True
    regeneration_exit = regeneration.get("exit_code")
    if regeneration_exit != 0:
        execution_inconclusive = True
    elif regeneration.get("output_exists") is not True:
        execution_inconclusive = True
    else:
        expected_header_hash = center.get("term_table", {}).get("sha256")
        if regeneration.get("frozen_sha256") != expected_header_hash:
            errors.append("H10 exact-center regeneration frozen hash changed")
        regenerated_hash = regeneration.get("regenerated_sha256")
        byte_identical = regeneration.get("byte_identical")
        if byte_identical is not (regenerated_hash == expected_header_hash):
            errors.append("H10 exact-center byte-identical flag is inconsistent")
        exact_failure = exact_failure or byte_identical is not True
        regeneration_argv = regeneration.get("argv")
        if not isinstance(regeneration_argv, list) or \
                len(regeneration_argv) != 5 or \
                regeneration_argv[1] != "-B" or \
                Path(regeneration_argv[2]).name != \
                Path(center.get("generator", {}).get("path", "")).name or \
                regeneration_argv[3] != "--output" or \
                Path(regeneration_argv[4]).name != "unstable_graph_terms.hpp":
            errors.append("H10 exact-center regeneration argv is malformed")
        if regeneration.get("stdout_sha256") != sha256_bytes(b"") or \
                regeneration.get("stderr_sha256") != sha256_bytes(b""):
            errors.append("H10 exact-center regeneration emitted unexpected output")

    table_audit = audit.get("term_table_audit")
    if not isinstance(table_audit, dict):
        errors.append("H10 exact-center term-table audit is malformed")
        table_audit = {}
        execution_inconclusive = True
    expected_names = {
        "kH1Terms", "kH2Terms", "kDefect1Terms", "kDefect2Terms"}
    if table_audit:
        if set(table_audit.get("expected_array_names", [])) != expected_names:
            errors.append("H10 exact-center expected array names changed")
        observed_names = table_audit.get("observed_array_names", [])
        if not isinstance(observed_names, list):
            errors.append("H10 exact-center observed array names are malformed")
            exact_failure = True
        else:
            exact_failure = exact_failure or \
                len(observed_names) != len(set(observed_names)) or \
                set(observed_names) != expected_names
        arrays = table_audit.get("arrays", {})
        if not isinstance(arrays, dict):
            errors.append("H10 exact-center array audit records are malformed")
            arrays = {}
            exact_failure = True
        specifications = {
            "kH1Terms": (
                protocol.get("h1_term_count"),
                protocol.get("center_minimum_total_degree"),
                protocol.get("center_maximum_total_degree"), False),
            "kH2Terms": (
                protocol.get("h2_term_count"),
                protocol.get("center_minimum_total_degree"),
                protocol.get("center_maximum_total_degree"), False),
            "kDefect1Terms": (
                protocol.get("defect1_term_count"),
                protocol.get("defect_minimum_total_degree"),
                protocol.get("defect_maximum_total_degree"), True),
            "kDefect2Terms": (
                protocol.get("defect2_term_count"),
                protocol.get("defect_minimum_total_degree"),
                protocol.get("defect_maximum_total_degree"), True),
        }
        for name, (count, minimum, maximum, sqrt_flag) in specifications.items():
            record = arrays.get(name, {})
            if not isinstance(record, dict):
                exact_failure = True
                continue
            expected_degrees = list(range(minimum, maximum + 1)) \
                if isinstance(minimum, int) and isinstance(maximum, int) else []
            fixed_fields = {
                "expected_term_count": count,
                "expected_total_degree_range": [minimum, maximum],
                "expected_times_sqrt_two": sqrt_flag,
            }
            for field, expected_value in fixed_fields.items():
                if record.get(field) != expected_value:
                    errors.append(
                        f"H10 exact-center {name}.{field} changed")
            exact_failure = exact_failure or any((
                record.get("observed_term_count") != count,
                record.get("observed_total_degrees") != expected_degrees,
                bool(record.get("duplicate_monomials")),
                bool(record.get("nonpositive_denominator_monomials")),
                bool(record.get("incorrect_sqrt_flag_monomials")),
            ))
    elif not execution_inconclusive:
        execution_inconclusive = True

    if failures or exact_failure:
        expected_status = "FAIL"
    elif reasons or execution_inconclusive:
        expected_status = "INCONCLUSIVE"
    else:
        expected_status = "PASS"
    if audit.get("status") != expected_status:
        errors.append(
            "H10 exact-center audit status is not its evidence aggregate")
    return expected_status


def _recorded_blob(repository: Path, commit: str, relative: str) -> bytes:
    """Read a repository-relative blob from the certificate's frozen commit."""

    path = Path(relative)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise ValueError(f"unsafe recorded source path: {relative}")
    return subprocess.run(
        ["git", "-C", str(repository), "cat-file", "blob", f"{commit}:{path.as_posix()}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def _replay_p2_probe(
        certificate: dict[str, Any], repository: Path,
        recorded_commit: str, recorded_dirty: bool) -> list[str]:
    """Recompile and replay the bound P2 probe on this same machine."""

    errors: list[str] = []
    toolchain = certificate.get("toolchain", {})
    build = toolchain.get("probe_build", {})
    logs = certificate.get("logs", {})
    compile_argv = build.get("compile_argv")
    probe_argv = build.get("probe_argv")
    if not isinstance(compile_argv, list) or not compile_argv or not all(
            isinstance(item, str) for item in compile_argv):
        return ["P2 replay compile argv is malformed"]
    if not isinstance(probe_argv, list) or not probe_argv or not all(
            isinstance(item, str) for item in probe_argv):
        return ["P2 replay probe argv is malformed"]
    expected_compile_hash = sha256_bytes(json.dumps(
        compile_argv, separators=(",", ":")).encode())
    if build.get("compile_argv_sha256") != expected_compile_hash:
        errors.append("P2 compile argv hash is internally inconsistent")
        return errors

    try:
        dependency_bytes = (
            safe_repository_path(
                repository,
                "validation/rigorous/dependency.lock.json").read_bytes()
            if recorded_dirty else
            _recorded_blob(
                repository, recorded_commit,
                "validation/rigorous/dependency.lock.json"))
        dependency = json.loads(dependency_bytes)
        compiler_lock = dependency["compiler"]
        capd_lock = dependency["capd"]
        compiler_record = toolchain["compiler"]
        capd_record = toolchain["capd"]
    except (OSError, ValueError, KeyError, TypeError,
            json.JSONDecodeError, subprocess.SubprocessError) as error:
        return [f"P2 replay dependency evidence is unavailable: {error}"]

    expected_compiler_record = {
        "path": compiler_lock.get("executable"),
        "version_first_line": compiler_lock.get("first_line"),
        "sha256": compiler_lock.get("sha256"),
    }
    if compiler_record != expected_compiler_record:
        errors.append("P2 replay compiler record differs from the frozen lock")
    compiler_path = Path(str(compiler_lock.get("executable", "")))
    try:
        if sha256_file(compiler_path) != compiler_lock.get("sha256"):
            errors.append("P2 replay compiler executable hash mismatch")
        compiler_version = subprocess.run(
            [str(compiler_path), "--version"], check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=30).stdout.splitlines()[0]
        if compiler_version != compiler_lock.get("first_line"):
            errors.append("P2 replay compiler version mismatch")
    except (OSError, IndexError, subprocess.SubprocessError) as error:
        errors.append(f"P2 replay compiler is unavailable: {error}")

    capd_source = Path(str(capd_record.get("source_path", "")))
    capd_config = Path(str(capd_record.get("config_path", "")))
    build_directory = capd_config.parent.parent
    expected_capd_fields = {
        "source_commit": capd_lock.get("source_commit"),
        "source_tree": capd_lock.get("source_tree"),
        "source_dirty": False,
        "config_version": capd_lock.get("capd_config_reported_version"),
    }
    for name, expected in expected_capd_fields.items():
        if capd_record.get(name) != expected:
            errors.append(f"P2 replay CAPD {name} differs from the frozen lock")
    try:
        if git_output(capd_source, "rev-parse", "HEAD") != \
                capd_lock.get("source_commit"):
            errors.append("P2 replay CAPD checkout commit mismatch")
        if git_output(capd_source, "rev-parse", "HEAD^{tree}") != \
                capd_lock.get("source_tree"):
            errors.append("P2 replay CAPD checkout tree mismatch")
        if git_output(capd_source, "status", "--porcelain"):
            errors.append("P2 replay CAPD checkout is dirty")
        if capd_source != capd_config and capd_source not in capd_config.parents:
            errors.append("P2 replay capd-config escapes the pinned checkout")
        queried_version = subprocess.run(
            [str(capd_config), "--version"], check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=30).stdout.strip()
        queried_cflags = shlex.split(subprocess.run(
            [str(capd_config), "--cflags"], check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=30).stdout.strip())
        queried_libs = shlex.split(subprocess.run(
            [str(capd_config), "--libs"], check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=30).stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        errors.append(f"P2 replay CAPD toolchain is unavailable: {error}")
        queried_version = ""
        queried_cflags = []
        queried_libs = []

    expected_cflags = [
        f"-I{capd_source / 'capdDynSys' / 'include'}",
        f"-I{capd_source / 'capdAlg' / 'include'}",
        f"-I{capd_source / 'capdAux' / 'include'}",
        f"-I{capd_source / 'capdExt' / 'include'}",
        f"-I{capd_source / 'capdExt' / 'filibsrc'}",
        "-std=c++17", "-O2", "-frounding-math", "-D__USE_FILIB__",
        "-O2", "-frounding-math", "-DFILIB_EXTENDED",
        "-DFILIB_HAVE_SSE",
    ]
    expected_libs = [
        f"-L{build_directory}",
        f"-L{build_directory / 'capdExt' / 'filibsrc'}",
        "-lcapd", "-lfilib",
    ]
    if queried_version != capd_lock.get("capd_config_reported_version"):
        errors.append("P2 replay capd-config version mismatch")
    if queried_cflags != expected_cflags or capd_record.get("cflags") != \
            expected_cflags:
        errors.append("P2 replay CAPD cflags differ from the frozen command")
    if queried_libs != expected_libs or capd_record.get("libs") != expected_libs:
        errors.append("P2 replay CAPD libs differ from the frozen command")
    expected_release_flags = shlex.split(
        capd_lock.get("cmake_configuration", {}).get(
            "CMAKE_CXX_FLAGS_RELEASE", ""))
    if capd_record.get("cmake_release_flags") != expected_release_flags:
        errors.append("P2 replay CMake release flags differ from the frozen lock")
    strict_flags = compiler_lock.get("required_probe_flags", [])
    if expected_release_flags != strict_flags:
        errors.append("P2 replay strict probe/library flags are not identical")
    if toolchain.get("fatal_errors") != [] or \
            toolchain.get("incomplete_checks") != []:
        errors.append("P2 replay toolchain records unresolved checks")

    library_records = capd_record.get("linked_archives", {})
    expected_library_paths = {
        "libcapd.a": build_directory / "libcapd.a",
        "libfilib.a": (
            build_directory / "capdExt" / "filibsrc" / "libfilib.a"),
    }
    if not isinstance(library_records, dict) or \
            set(library_records) != set(expected_library_paths):
        errors.append("P2 replay linked-archive records are malformed")
    else:
        for name, path in expected_library_paths.items():
            record = library_records.get(name, {})
            try:
                observed_hash = sha256_file(path)
            except OSError as error:
                errors.append(f"P2 replay linked archive is unavailable ({name}): {error}")
                continue
            if Path(str(record.get("path", ""))).resolve() != path.resolve():
                errors.append(f"P2 replay linked archive path mismatch: {name}")
            if record.get("sha256") != observed_hash:
                errors.append(f"P2 replay linked archive hash mismatch: {name}")
            reference_config = Path(str(
                capd_lock.get("reference_capd_config", "")))
            reference_hash = capd_lock.get(
                "reference_libraries", {}).get(name)
            if capd_config.resolve() == reference_config.resolve() and \
                    observed_hash != reference_hash:
                errors.append(f"P2 replay reference archive hash mismatch: {name}")

    normalized_compile: list[str] = []
    index = 0
    include_count = 0
    source_count = 0
    output_count = 0
    while index < len(compile_argv):
        item = compile_argv[index]
        if item == "-o" and index + 1 < len(compile_argv):
            normalized_compile.extend(["-o", "<OUTPUT>"])
            output_count += 1
            index += 2
            continue
        if item.startswith("-I") and Path(item[2:]).parts[-3:] == \
                ("validation", "rigorous", "include"):
            normalized_compile.append("<LOCAL_INCLUDE>")
            include_count += 1
        elif Path(item).parts[-4:] == (
                "validation", "rigorous", "src",
                "vdp_p2_jets_probe.cpp"):
            normalized_compile.append("<SOURCE>")
            source_count += 1
        else:
            normalized_compile.append(item)
        index += 1
    expected_compile = [
        str(compiler_path), "-std=c++17", "<LOCAL_INCLUDE>",
        *expected_cflags, *strict_flags, "<SOURCE>", "-o", "<OUTPUT>",
        *expected_libs,
    ]
    if (include_count, source_count, output_count) != (1, 1, 1) or \
            normalized_compile != expected_compile:
        errors.append("P2 replay compile argv differs from the frozen command")
    if errors:
        return errors

    replay_files = [
        "validation/rigorous/src/vdp_p2_jets_probe.cpp",
        "validation/rigorous/include/interval_io.hpp",
        "validation/rigorous/include/rounding_self_test.hpp",
        "validation/rigorous/include/verdict.hpp",
    ]
    contents: dict[str, bytes] = {}
    for relative in replay_files:
        try:
            contents[relative] = (
                safe_repository_path(repository, relative).read_bytes()
                if recorded_dirty else
                _recorded_blob(repository, recorded_commit, relative))
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            errors.append(f"P2 replay source is unavailable ({relative}): {error}")
    if errors:
        return errors

    try:
        with tempfile.TemporaryDirectory(prefix="rfsn-p2-checker-replay-") \
                as temporary:
            root = Path(temporary)
            include_dir = root / "include"
            include_dir.mkdir()
            source = root / "vdp_p2_jets_probe.cpp"
            source.write_bytes(contents[replay_files[0]])
            for relative in replay_files[1:]:
                (include_dir / Path(relative).name).write_bytes(contents[relative])
            binary = root / "probe"

            replay_compile: list[str] = []
            index = 0
            source_replaced = False
            include_replaced = False
            output_replaced = False
            while index < len(compile_argv):
                item = compile_argv[index]
                if item == "-o" and index + 1 < len(compile_argv):
                    replay_compile.extend(["-o", str(binary)])
                    output_replaced = True
                    index += 2
                    continue
                if item.startswith("-I") and Path(item[2:]).name == "include" \
                        and Path(item[2:]).parent.name == "rigorous":
                    replay_compile.append(f"-I{include_dir}")
                    include_replaced = True
                elif Path(item).name == "vdp_p2_jets_probe.cpp":
                    replay_compile.append(str(source))
                    source_replaced = True
                else:
                    replay_compile.append(item)
                index += 1
            if not (source_replaced and include_replaced and output_replaced):
                return ["P2 replay could not reconstruct the compile command"]

            environment = os.environ.copy()
            environment.update({
                "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                "LC_ALL": "C.UTF-8",
            })
            compiled = subprocess.run(
                replay_compile, text=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, env=environment, timeout=180)
            if compiled.returncode != 0:
                errors.append(
                    "P2 checker replay compilation failed: " +
                    compiled.stderr)
                return errors
            for name, output in (
                    ("compile_stdout_sha256", compiled.stdout),
                    ("compile_stderr_sha256", compiled.stderr)):
                if sha256_bytes(output.encode()) != logs.get(name):
                    errors.append(f"P2 replay {name} differs from the formal run")

            replay_probe = [str(binary), *probe_argv[1:]]
            executed = subprocess.run(
                replay_probe, text=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, env=environment, timeout=120)
            if executed.returncode != build.get("probe_exit_code"):
                errors.append("P2 replay exit code differs from the formal run")
            if executed.stdout != build.get("probe_stdout"):
                errors.append("P2 replay stdout differs from the formal run")
            if sha256_bytes(executed.stdout.encode()) != logs.get(
                    "probe_stdout_sha256"):
                errors.append("P2 replay stdout hash differs from the formal run")
            if sha256_bytes(executed.stderr.encode()) != logs.get(
                    "probe_stderr_sha256"):
                errors.append("P2 replay stderr differs from the formal run")
    except (OSError, subprocess.SubprocessError) as error:
        errors.append(f"P2 checker replay could not execute: {error}")
    return errors


def semantic_errors(certificate: dict[str, Any],
                    repository: Path = REPOSITORY) -> list[str]:
    errors: list[str] = []
    box_path = HERE / "config" / "vdp_box_v1.json"
    box = load_json(box_path)
    box_schema = load_json(HERE / "parameter_box.schema.json")
    try:
        jsonschema.validate(box, box_schema,
                            format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as error:
        errors.append(f"frozen box schema: {error.message}")
    errors.extend(validate_exact_box(box))

    parameter_box = certificate.get("parameter_box", {})
    if parameter_box.get("path") != "validation/rigorous/config/vdp_box_v1.json":
        errors.append("certificate does not bind the canonical phase-1 box path")
    if parameter_box.get("sha256") != sha256_file(box_path):
        errors.append("certificate parameter-box hash does not match the frozen box")
    if parameter_box.get("variables") != box.get("variables"):
        errors.append("certificate parameter endpoints differ from the frozen box")

    scope = certificate.get("scope")
    bridge: dict[str, Any] = {}
    configuration: dict[str, Any] = {}
    h10_configuration: dict[str, Any] = {}
    p2_jets_configuration: dict[str, Any] = {}
    expected_h10_audit_status: str | None = None
    bridge_scopes = {
        "V2_LOCAL_GRAPH_KERNEL", "V2_H10_C01_KERNEL",
        "V2_P2_JETS_KERNEL"}
    if scope in bridge_scopes:
        bridge_path = HERE / "config" / "vdp_bridge_v1.json"
        bridge = load_json(bridge_path)
        try:
            jsonschema.validate(
                bridge,
                load_json(HERE / "continuation_bridge.schema.json"),
                format_checker=jsonschema.FormatChecker(),
            )
        except jsonschema.ValidationError as error:
            errors.append(f"frozen continuation bridge schema: {error.message}")
        errors.extend(validate_exact_bridge(bridge))
        recorded_bridge = certificate.get("continuation_bridge", {})
        if recorded_bridge.get("path") != \
                "validation/rigorous/config/vdp_bridge_v1.json":
            errors.append("local-graph certificate does not bind the canonical bridge path")
        if recorded_bridge.get("sha256") != sha256_file(bridge_path):
            errors.append("certificate continuation-bridge hash mismatch")
        if recorded_bridge.get("variables") != bridge.get("variables"):
            errors.append("certificate bridge endpoints differ from the frozen bridge")

        configuration_path = HERE / "config" / "vdp_p2_local_graph_v1.json"
        configuration = load_json(configuration_path)
        try:
            jsonschema.validate(
                configuration,
                load_json(HERE / "p2_local_graph.schema.json"),
                format_checker=jsonschema.FormatChecker(),
            )
        except jsonschema.ValidationError as error:
            errors.append(f"local-graph configuration schema: {error.message}")
        errors.extend(validate_local_graph_configuration(configuration))
        recorded_configuration = certificate.get("validation_configuration", {})
        if recorded_configuration.get("path") != \
                "validation/rigorous/config/vdp_p2_local_graph_v1.json":
            errors.append("local-graph certificate does not bind the canonical configuration")
        if recorded_configuration.get("sha256") != sha256_file(configuration_path):
            errors.append("certificate local-graph configuration hash mismatch")
        selected_bridge = configuration.get("selection_basis", {}).get(
            "continuation_bridge", {})
        if selected_bridge.get("sha256") != sha256_file(bridge_path):
            errors.append("local-graph configuration does not bind the frozen bridge")

        if scope == "V2_H10_C01_KERNEL":
            h10_path = HERE / "config" / "vdp_p2_h10_c01_v1.json"
            h10_configuration = load_json(h10_path)
            try:
                jsonschema.validate(
                    h10_configuration,
                    load_json(HERE / "p2_h10_c01.schema.json"),
                    format_checker=jsonschema.FormatChecker(),
                )
            except jsonschema.ValidationError as error:
                errors.append(f"H10 C0/C1 configuration schema: {error.message}")
            errors.extend(validate_h10_c01_configuration(h10_configuration))
            recorded_h10 = certificate.get("h10_c01_configuration", {})
            if recorded_h10.get("path") != \
                    "validation/rigorous/config/vdp_p2_h10_c01_v1.json":
                errors.append(
                    "H10 C0/C1 certificate does not bind the canonical configuration")
            if recorded_h10.get("sha256") != sha256_file(h10_path):
                errors.append("certificate H10 C0/C1 configuration hash mismatch")
            if recorded_h10.get("configuration_id") != \
                    h10_configuration.get("configuration_id"):
                errors.append("certificate H10 C0/C1 configuration id mismatch")

            basis = h10_configuration.get("selection_basis", {})
            selected_files = {
                "continuation_bridge": bridge_path,
                "p2a_configuration":
                    HERE / "config" / "vdp_p2_local_graph_v1.json",
                "p2a_certificate":
                    HERE / "results" / "vdp_bridge_v1_p2a_local_graph.json",
            }
            for name, path in selected_files.items():
                selected = basis.get(name, {})
                expected_relative = str(path.relative_to(REPOSITORY))
                if selected.get("path") != expected_relative or \
                        selected.get("sha256") != sha256_file(path):
                    errors.append(f"H10 C0/C1 selection {name} binding mismatch")
            try:
                selected_commit = git_output(
                    repository, "rev-parse",
                    f"{basis.get('repository_tag', '')}^{{commit}}")
                if selected_commit != basis.get("repository_commit"):
                    errors.append(
                        "H10 C0/C1 selection tag does not resolve to its commit")
            except (OSError, subprocess.SubprocessError) as error:
                errors.append(f"cannot resolve H10 C0/C1 selection tag: {error}")

            flagship_lock = load_json(HERE / "flagship_import.lock.json")
            center = h10_configuration.get("imported_core_center", {})
            if center.get("commit") != flagship_lock.get("commit"):
                errors.append("H10 center commit differs from the flagship lock")
            for name in ("generator", "term_table", "reference_probe",
                         "reference_readme", "source_certificate"):
                item = center.get(name, {})
                if flagship_lock.get("files", {}).get(item.get("path")) != \
                        item.get("sha256"):
                    errors.append(f"H10 center {name} differs from the flagship lock")

            p2a_path = HERE / "results" / "vdp_bridge_v1_p2a_local_graph.json"
            p2a_certificate = load_json(p2a_path)
            nested_p2a_errors = schema_errors(p2a_certificate) + \
                semantic_errors(p2a_certificate, repository)
            if nested_p2a_errors:
                errors.append(
                    "bound P2a prerequisite certificate is invalid: " +
                    "; ".join(nested_p2a_errors))
            prerequisite = certificate.get("p2a_prerequisite", {})
            expected_prerequisite = {
                "configuration_path":
                    "validation/rigorous/config/vdp_p2_local_graph_v1.json",
                "configuration_sha256": sha256_file(
                    HERE / "config" / "vdp_p2_local_graph_v1.json"),
                "certificate_path":
                    "validation/rigorous/results/vdp_bridge_v1_p2a_local_graph.json",
                "certificate_sha256": sha256_file(p2a_path),
                "certificate_scope": p2a_certificate.get("scope"),
                "source_commit": p2a_certificate.get(
                    "source_revision", {}).get("commit"),
                "integrity_status": p2a_certificate.get("integrity_status"),
                "mathematical_status": p2a_certificate.get("mathematical_status"),
                "final_status": p2a_certificate.get("final_status"),
                "claim_bearing": p2a_certificate.get("claim_bearing"),
            }
            if prerequisite != expected_prerequisite:
                errors.append("certificate P2a prerequisite record changed")
            p2a_by_id = {
                item.get("id"): item.get("status")
                for item in p2a_certificate.get("obligations", [])
                if isinstance(item, dict)
            }
            if not (
                p2a_certificate.get("scope") == "V2_LOCAL_GRAPH_KERNEL" and
                p2a_certificate.get("integrity_status") == "PASS" and
                p2a_certificate.get("mathematical_status") == "PASS" and
                p2a_certificate.get("final_status") == "INCONCLUSIVE" and
                p2a_certificate.get("claim_bearing") is False and
                p2a_by_id.get("V2.WU.FRAME_BLOCK") == "PASS" and
                p2a_by_id.get("V2.WU.COARSE_GRAPH") == "PASS"
            ):
                errors.append("bound P2a prerequisite does not establish P2a PASS")

            expected_h10_audit_status = _h10_audit_status(
                certificate.get("h10_exact_center_audit"),
                h10_configuration,
                certificate.get("toolchain", {}).get(
                    "flagship_import", {}).get("repository_path"),
                errors)
        if scope == "V2_P2_JETS_KERNEL":
            p2_jets_path = HERE / "config" / "vdp_p2_jets_v1.json"
            p2_jets_configuration = load_json(p2_jets_path)
            try:
                jsonschema.validate(
                    p2_jets_configuration,
                    load_json(HERE / "p2_jets.schema.json"),
                    format_checker=jsonschema.FormatChecker(),
                )
            except jsonschema.ValidationError as error:
                errors.append(f"P2 jets configuration schema: {error.message}")
            errors.extend(validate_p2_jets_configuration(
                p2_jets_configuration))
            recorded_jets = certificate.get("p2_jets_configuration", {})
            if recorded_jets.get("path") != \
                    "validation/rigorous/config/vdp_p2_jets_v1.json":
                errors.append(
                    "P2 jets certificate does not bind the canonical configuration")
            if recorded_jets.get("sha256") != sha256_file(p2_jets_path):
                errors.append("certificate P2 jets configuration hash mismatch")
            if recorded_jets.get("configuration_id") != \
                    p2_jets_configuration.get("configuration_id"):
                errors.append("certificate P2 jets configuration id mismatch")

            basis = p2_jets_configuration.get("selection_basis", {})
            selected_files = {
                "continuation_bridge": HERE / "config" / "vdp_bridge_v1.json",
                "p2a_configuration":
                    HERE / "config" / "vdp_p2_local_graph_v1.json",
                "p2a_certificate":
                    HERE / "results" / "vdp_bridge_v1_p2a_local_graph.json",
                "p2b0_configuration":
                    HERE / "config" / "vdp_p2_h10_c01_v1.json",
                "p2b0_certificate":
                    HERE / "results" / "vdp_bridge_v1_p2b_h10_c01.json",
                "design_scout": HERE / "design" / "p2b_jets_scout.cpp",
            }
            for name, path in selected_files.items():
                selected = basis.get(name, {})
                expected_relative = str(path.relative_to(REPOSITORY))
                if selected.get("path") != expected_relative or \
                        selected.get("sha256") != sha256_file(path):
                    errors.append(f"P2 jets selection {name} binding mismatch")
                try:
                    frozen_blob = _recorded_blob(
                        repository, str(basis.get("repository_commit", "")),
                        expected_relative)
                except (OSError, ValueError,
                        subprocess.SubprocessError) as error:
                    errors.append(
                        f"P2 jets frozen selection {name} is unavailable: {error}")
                else:
                    if selected.get("sha256") != sha256_bytes(frozen_blob):
                        errors.append(
                            f"P2 jets frozen selection {name} hash mismatch")
            try:
                selected_commit = git_output(
                    repository, "rev-parse",
                    f"{basis.get('repository_tag', '')}^{{commit}}")
                if selected_commit != basis.get("repository_commit"):
                    errors.append(
                        "P2 jets selection tag does not resolve to its commit")
            except (OSError, subprocess.SubprocessError) as error:
                errors.append(f"cannot resolve P2 jets selection tag: {error}")

            p2a_path = HERE / "results" / "vdp_bridge_v1_p2a_local_graph.json"
            p2a_certificate = load_json(p2a_path)
            nested_p2a_errors = schema_errors(p2a_certificate) + \
                semantic_errors(p2a_certificate, repository)
            if nested_p2a_errors:
                errors.append(
                    "bound P2a prerequisite certificate is invalid: " +
                    "; ".join(nested_p2a_errors))
            expected_p2a = {
                "configuration_path":
                    "validation/rigorous/config/vdp_p2_local_graph_v1.json",
                "configuration_sha256": sha256_file(
                    HERE / "config" / "vdp_p2_local_graph_v1.json"),
                "certificate_path":
                    "validation/rigorous/results/vdp_bridge_v1_p2a_local_graph.json",
                "certificate_sha256": sha256_file(p2a_path),
                "certificate_scope": p2a_certificate.get("scope"),
                "source_commit": p2a_certificate.get(
                    "source_revision", {}).get("commit"),
                "integrity_status": p2a_certificate.get("integrity_status"),
                "mathematical_status": p2a_certificate.get("mathematical_status"),
                "final_status": p2a_certificate.get("final_status"),
                "claim_bearing": p2a_certificate.get("claim_bearing"),
            }
            if certificate.get("p2a_prerequisite") != expected_p2a:
                errors.append("certificate P2a prerequisite record changed")
            p2a_by_id = {
                item.get("id"): item.get("status")
                for item in p2a_certificate.get("obligations", [])
                if isinstance(item, dict)
            }
            if not (
                p2a_certificate.get("scope") == "V2_LOCAL_GRAPH_KERNEL" and
                p2a_certificate.get("integrity_status") == "PASS" and
                p2a_certificate.get("mathematical_status") == "PASS" and
                p2a_certificate.get("final_status") == "INCONCLUSIVE" and
                p2a_certificate.get("claim_bearing") is False and
                p2a_by_id.get("V2.WU.FRAME_BLOCK") == "PASS" and
                p2a_by_id.get("V2.WU.COARSE_GRAPH") == "PASS"
            ):
                errors.append("bound P2a prerequisite does not establish P2a PASS")

            p2b0_path = HERE / "results" / "vdp_bridge_v1_p2b_h10_c01.json"
            p2b0_certificate = load_json(p2b0_path)
            nested_p2b0_errors = schema_errors(p2b0_certificate) + \
                semantic_errors(p2b0_certificate, repository)
            if nested_p2b0_errors:
                errors.append(
                    "bound P2b0 prerequisite certificate is invalid: " +
                    "; ".join(nested_p2b0_errors))
            expected_p2b0 = {
                "configuration_path":
                    "validation/rigorous/config/vdp_p2_h10_c01_v1.json",
                "configuration_sha256": sha256_file(
                    HERE / "config" / "vdp_p2_h10_c01_v1.json"),
                "certificate_path":
                    "validation/rigorous/results/vdp_bridge_v1_p2b_h10_c01.json",
                "certificate_sha256": sha256_file(p2b0_path),
                "certificate_scope": p2b0_certificate.get("scope"),
                "source_commit": p2b0_certificate.get(
                    "source_revision", {}).get("commit"),
                "integrity_status": p2b0_certificate.get("integrity_status"),
                "mathematical_status": p2b0_certificate.get("mathematical_status"),
                "final_status": p2b0_certificate.get("final_status"),
                "claim_bearing": p2b0_certificate.get("claim_bearing"),
            }
            if certificate.get("p2b0_prerequisite") != expected_p2b0:
                errors.append("certificate P2b0 prerequisite record changed")
            p2b0_by_id = {
                item.get("id"): item.get("status")
                for item in p2b0_certificate.get("obligations", [])
                if isinstance(item, dict)
            }
            if not (
                p2b0_certificate.get("scope") == "V2_H10_C01_KERNEL" and
                p2b0_certificate.get("integrity_status") == "PASS" and
                p2b0_certificate.get("mathematical_status") == "PASS" and
                p2b0_certificate.get("final_status") == "INCONCLUSIVE" and
                p2b0_certificate.get("claim_bearing") is False and
                p2b0_by_id.get("V2.WU.H10_C0_TUBE") == "PASS" and
                p2b0_by_id.get("V2.WU.H10_C1_TUBE") == "PASS"
            ):
                errors.append("bound P2b0 prerequisite does not establish P2b0 PASS")
            errors.extend(validate_p2b0_true_tube_implication(
                p2_jets_configuration, p2b0_certificate))
    elif "continuation_bridge" in certificate or \
            "validation_configuration" in certificate:
        errors.append("non-P2 certificate unexpectedly records P2 configuration data")
    if scope != "V2_H10_C01_KERNEL" and any(
            name in certificate for name in (
                "h10_c01_configuration", "h10_exact_center_audit")):
        errors.append("non-H10 certificate unexpectedly records H10 configuration data")
    if scope not in {"V2_H10_C01_KERNEL", "V2_P2_JETS_KERNEL"} and \
            "p2a_prerequisite" in certificate:
        errors.append("certificate unexpectedly records a P2a prerequisite")
    if scope != "V2_P2_JETS_KERNEL" and any(
            name in certificate for name in (
                "p2_jets_configuration", "p2b0_prerequisite")):
        errors.append("non-P2-jets certificate records P2-jets data")

    source_revision = certificate.get("source_revision", {})
    try:
        git_output(
            repository, "cat-file", "-e",
            f"{source_revision.get('commit', '')}^{{commit}}")
    except (OSError, subprocess.SubprocessError) as error:
        errors.append(f"recorded source commit is unavailable: {error}")

    recorded_commit = str(source_revision.get("commit", ""))
    recorded_dirty = bool(source_revision.get("repository_dirty", True))
    allow_dirty = bool(source_revision.get("allow_dirty_development", False))
    if recorded_dirty and not allow_dirty:
        errors.append("a dirty source certificate must record allow_dirty_development=true")

    seen_paths: set[str] = set()
    for binding in certificate.get("source_bindings", []):
        relative = binding.get("path")
        if not isinstance(relative, str):
            continue
        if relative in seen_paths:
            errors.append(f"duplicate source-binding path: {relative}")
            continue
        seen_paths.add(relative)
        try:
            path = safe_repository_path(repository, relative)
        except ValueError as error:
            errors.append(str(error))
            continue
        if recorded_dirty:
            # A dirty development certificate cannot be reconstructed from its
            # base commit.  It remains non-claim-bearing and is checked against
            # the explicitly hash-bound working-tree inputs.
            if not path.is_file():
                errors.append(f"source-binding file is missing: {relative}")
            elif binding.get("sha256") != sha256_file(path):
                errors.append(f"dirty source-binding hash mismatch: {relative}")
        else:
            # A clean certificate is historical evidence.  Verify the exact
            # Git blobs at the recorded commit so later checker evolution does
            # not invalidate an otherwise immutable certificate.
            try:
                blob = _recorded_blob(repository, recorded_commit, relative)
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                errors.append(f"recorded source blob is unavailable ({relative}): {error}")
            else:
                if binding.get("sha256") != sha256_bytes(blob):
                    errors.append(f"recorded source-blob hash mismatch: {relative}")

    required_bindings_by_scope = {
        "V2_LOCAL_GRAPH_KERNEL": LOCAL_GRAPH_REQUIRED_BINDINGS,
        "V2_H10_C01_KERNEL": H10_C01_REQUIRED_BINDINGS,
        "V2_P2_JETS_KERNEL": P2_JETS_REQUIRED_BINDINGS,
    }
    required_bindings = required_bindings_by_scope.get(
        scope, BASE_REQUIRED_BINDINGS)
    missing_bindings = required_bindings - seen_paths
    if missing_bindings:
        errors.append(f"required source bindings missing: {sorted(missing_bindings)}")

    obligations = certificate.get("obligations", [])
    by_id: dict[str, dict[str, Any]] = {}
    for obligation in obligations:
        identifier = obligation.get("id")
        if identifier in by_id:
            errors.append(f"duplicate obligation id: {identifier}")
        elif isinstance(identifier, str):
            by_id[identifier] = obligation
        for name, enclosure in obligation.get("enclosures", {}).items():
            _check_hex_interval(f"{identifier}.{name}", enclosure, errors)

    try:
        if recorded_dirty:
            obligation_manifest = load_json(HERE / "obligations.json")
        else:
            obligation_manifest = json.loads(_recorded_blob(
                repository, recorded_commit,
                "validation/rigorous/obligations.json"))
        manifest_predicates = {
            item["id"]: item["predicate"]
            for phase in obligation_manifest["phases"]
            for item in phase["obligations"]
        }
        for identifier, obligation in by_id.items():
            if identifier not in manifest_predicates:
                errors.append(f"obligation is absent from its bound manifest: {identifier}")
            elif obligation.get("predicate") != manifest_predicates[identifier]:
                errors.append(f"obligation predicate differs from its bound manifest: {identifier}")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError,
            OSError, subprocess.SubprocessError) as error:
        errors.append(f"cannot reconstruct bound obligation predicates: {error}")

    required_by_scope = {
        "PREFLIGHT": P0_IDS,
        "V1_V2_1_KERNEL": KERNEL_IDS,
        "V2_LOCAL_GRAPH_KERNEL": LOCAL_GRAPH_IDS,
        "V2_H10_C01_KERNEL": H10_C01_IDS,
        "V2_P2_JETS_KERNEL": P2_JETS_IDS,
    }
    required = required_by_scope.get(scope, set())
    missing = required - set(by_id)
    extra = set(by_id) - required
    if missing:
        errors.append(f"missing obligations: {sorted(missing)}")
    if extra:
        errors.append(f"unexpected obligations for {scope}: {sorted(extra)}")

    scope_nonclaims = {
        "V2_LOCAL_GRAPH_KERNEL": LOCAL_GRAPH_SCOPE_NONCLAIM,
        "V2_H10_C01_KERNEL": H10_C01_SCOPE_NONCLAIM,
        "V2_P2_JETS_KERNEL": P2_JETS_SCOPE_NONCLAIM,
    }
    expected_nonclaims = COMMON_NONCLAIMS + [
        scope_nonclaims.get(scope, PHASE1_SCOPE_NONCLAIM)]
    if certificate.get("nonclaims") != expected_nonclaims:
        errors.append("certificate nonclaims differ from the frozen scope boundary")

    if scope == "V2_H10_C01_KERNEL":
        if by_id.get("P2.P2A_PREREQUISITE", {}).get("status") != "PASS":
            errors.append("P2.P2A_PREREQUISITE must bind the verified P2a PASS")
        if by_id.get("P2.H10_C01_CONFIG_FROZEN", {}).get("status") != "PASS":
            errors.append("P2.H10_C01_CONFIG_FROZEN must bind the frozen configuration")
        if expected_h10_audit_status is not None and \
                by_id.get("P2.H10_CENTER_EXACT", {}).get("status") != \
                expected_h10_audit_status:
            errors.append(
                "P2.H10_CENTER_EXACT differs from the recomputed audit verdict")
    if scope == "V2_P2_JETS_KERNEL":
        for identifier in (
                "P2.P2A_PREREQUISITE", "P2.P2B0_PREREQUISITE",
                "P2.JETS_CONFIG_FROZEN"):
            if by_id.get(identifier, {}).get("status") != "PASS":
                errors.append(f"{identifier} must bind its verified PASS input")
        atomic_ids = (
            "P2.JETS.COEFFICIENTS", "V2.WU.STATE_C23",
            "V2.WU.MIXED_JETS", "V2.WU.WEIGHTED_HALF_ORBITS")
        if all(identifier in by_id for identifier in atomic_ids):
            expected_parent = combine_verdicts(
                by_id[identifier]["status"] for identifier in atomic_ids)
            for identifier in ("V2.WU.JETS", "V2.WU_GRAPH"):
                if by_id.get(identifier, {}).get("status") != expected_parent:
                    errors.append(
                        f"{identifier} is not the P2 jets atomic aggregate")

    integrity_ids = {
        "V2_LOCAL_GRAPH_KERNEL": LOCAL_GRAPH_P0_IDS,
        "V2_H10_C01_KERNEL": H10_C01_P0_IDS,
        "V2_P2_JETS_KERNEL": P2_JETS_P0_IDS,
    }.get(scope, P0_IDS)
    p0_status = combine_verdicts(
        by_id[item]["status"] for item in integrity_ids if item in by_id)
    if len(integrity_ids & set(by_id)) == len(integrity_ids) and \
            certificate.get("integrity_status") != p0_status:
        errors.append("integrity_status is not the aggregate P0 verdict")

    if scope == "PREFLIGHT":
        expected_math = "PASS"
    else:
        mathematical_ids = required - integrity_ids
        expected_math = combine_verdicts(
            by_id[item]["status"] for item in mathematical_ids if item in by_id)
    if required <= set(by_id) and certificate.get("mathematical_status") != expected_math:
        errors.append("mathematical_status is not the mathematical-obligation aggregate")

    raw_probe = certificate.get("raw_probe", {})
    if scope != "PREFLIGHT":
        raw_obligations = raw_probe.get("obligations", [])
        raw_by_id: dict[str, dict[str, Any]] = {}
        if not isinstance(raw_obligations, list):
            errors.append("raw_probe.obligations is not a list")
            raw_obligations = []
        for item in raw_obligations:
            if not isinstance(item, dict) or not isinstance(item.get("id"), str):
                errors.append("raw probe has an invalid obligation record")
                continue
            identifier = item["id"]
            if identifier in raw_by_id:
                errors.append(f"duplicate raw-probe obligation id: {identifier}")
            raw_by_id[identifier] = item
        expected_raw_ids = (
            {"P2.JETS.COEFFICIENTS", "V2.WU.STATE_C23",
             "V2.WU.MIXED_JETS", "V2.WU.WEIGHTED_HALF_ORBITS"}
            if scope == "V2_P2_JETS_KERNEL" else required - integrity_ids)
        if set(raw_by_id) != expected_raw_ids:
            errors.append(
                "raw-probe mathematical obligations differ from the scoped set: "
                f"observed={sorted(raw_by_id)}, expected={sorted(expected_raw_ids)}")
        for identifier in expected_raw_ids & set(raw_by_id) & set(by_id):
            if raw_by_id[identifier].get("status") != by_id[identifier].get("status"):
                errors.append(f"raw/top-level status mismatch: {identifier}")
            if raw_by_id[identifier].get("enclosures", {}) != \
                    by_id[identifier].get("enclosures", {}):
                errors.append(f"raw/top-level enclosure mismatch: {identifier}")
        expected_raw_math = combine_verdicts(
            raw_by_id[identifier].get("status", "INCONCLUSIVE")
            for identifier in expected_raw_ids if identifier in raw_by_id)
        if len(expected_raw_ids & set(raw_by_id)) == len(expected_raw_ids) and \
                raw_probe.get("mathematical_status") != expected_raw_math:
            errors.append("raw-probe mathematical_status differs from its obligations")

    if scope == "V1_V2_1_KERNEL":
        if raw_probe.get("exact_characteristic_polynomial") is not True:
            errors.append("kernel does not record the exact characteristic-polynomial identity")
    if scope == "V2_LOCAL_GRAPH_KERNEL":
        if raw_probe.get("exact_frame_derivation") is not True:
            errors.append("local-graph kernel does not bind the exact frame derivation")
        expected_enclosures = {
            "V2.WU.FRAME_BLOCK": LOCAL_FRAME_ENCLOSURES,
            "V2.WU.COARSE_GRAPH": LOCAL_GRAPH_ENCLOSURES,
        }
        for identifier, expected_names in expected_enclosures.items():
            observed = by_id.get(identifier, {}).get("enclosures", {})
            if set(observed) != expected_names:
                errors.append(
                    f"{identifier} enclosure set changed: "
                    f"observed={sorted(observed)}, expected={sorted(expected_names)}")
            margin_verdicts: list[str] = []
            for name, enclosure in observed.items():
                verdict = _strict_positive_interval_verdict(enclosure)
                if verdict is None:
                    errors.append(
                        f"{identifier}.{name} cannot be reduced to a margin verdict")
                else:
                    margin_verdicts.append(verdict)
            if len(margin_verdicts) == len(expected_names):
                recomputed = combine_verdicts(margin_verdicts)
                if by_id.get(identifier, {}).get("status") != recomputed:
                    errors.append(
                        f"{identifier} status is not its strict-margin aggregate")

        raw_parameters = raw_probe.get("parameter_enclosures", {})
        bridge_variables = bridge.get("variables", {})
        for name in ("r", "a2", "epsilon"):
            try:
                exact_lower = fraction(bridge_variables[name]["lower"])
                exact_upper = fraction(bridge_variables[name]["upper"])
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                continue
            if not _contains_exact_interval(
                    raw_parameters.get(name), exact_lower, exact_upper):
                errors.append(
                    f"raw local-graph parameter enclosure does not contain "
                    f"the exact bridge interval: {name}")
        exact_radius = Fraction(1, 100)
        if not _contains_exact_interval(
                raw_parameters.get("radius"), exact_radius, exact_radius):
            errors.append("raw local-graph radius does not contain the frozen 1/100")

    if scope == "V2_H10_C01_KERNEL":
        if raw_probe.get("materialized_center_structure") not in (True, False):
            errors.append("H10 probe materialized_center_structure is not boolean")
        raw_parameters = _check_interval_mapping(
            "raw_probe.parameter_enclosures",
            raw_probe.get("parameter_enclosures"),
            H10_PARAMETER_ENCLOSURES, errors)
        _check_interval_mapping(
            "raw_probe.center_enclosures",
            raw_probe.get("center_enclosures"),
            H10_CENTER_ENCLOSURES, errors)
        reference_margins = _check_interval_mapping(
            "raw_probe.reference_gate_margins",
            raw_probe.get("reference_gate_margins"),
            H10_REFERENCE_MARGINS, errors)
        parameter_margins = _check_interval_mapping(
            "raw_probe.parameter_gate_margins",
            raw_probe.get("parameter_gate_margins"),
            H10_PARAMETER_MARGINS, errors)
        acceptance_margins = _check_interval_mapping(
            "raw_probe.acceptance_gate_margins",
            raw_probe.get("acceptance_gate_margins"),
            H10_ACCEPTANCE_MARGINS, errors)

        bridge_variables = bridge.get("variables", {})
        for name in ("r", "a2", "epsilon"):
            try:
                exact_lower = fraction(bridge_variables[name]["lower"])
                exact_upper = fraction(bridge_variables[name]["upper"])
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                continue
            if not _contains_exact_interval(
                    raw_parameters.get(name), exact_lower, exact_upper):
                errors.append(
                    f"raw H10 parameter enclosure does not contain the exact "
                    f"bridge interval: {name}")
        frozen_scalar_inputs = {
            "radius": h10_configuration.get(
                "coordinate_domain", {}).get("unstable_radius"),
            "rho": h10_configuration.get(
                "tube_radii", {}).get("value_euclidean"),
            "eta": h10_configuration.get(
                "tube_radii", {}).get("first_derivative_frobenius"),
        }
        for name, rational in frozen_scalar_inputs.items():
            try:
                exact = fraction(rational)
            except (TypeError, ValueError, ZeroDivisionError):
                continue
            if not _contains_exact_interval(
                    raw_parameters.get(name), exact, exact):
                errors.append(
                    f"raw H10 {name} does not contain its frozen rational value")

        expected_enclosures = {
            "V2.WU.H10_C0_TUBE": H10_C0_ENCLOSURES,
            "V2.WU.H10_C1_TUBE": H10_C1_ENCLOSURES,
        }
        all_margin_maps = {
            **reference_margins,
            **parameter_margins,
            **acceptance_margins,
        }
        observed_by_id: dict[str, dict[str, Any]] = {}
        for identifier, expected_names in expected_enclosures.items():
            observed = by_id.get(identifier, {}).get("enclosures", {})
            if not isinstance(observed, dict):
                observed = {}
            observed_by_id[identifier] = observed
            if set(observed) != expected_names:
                errors.append(
                    f"{identifier} enclosure set changed: "
                    f"observed={sorted(observed)}, "
                    f"expected={sorted(expected_names)}")
            for name in expected_names & set(observed):
                if observed[name] != all_margin_maps.get(name):
                    errors.append(
                        f"{identifier}.{name} differs from its raw gate margin")

        c0_margin_verdicts: list[str] = []
        c0_observed = observed_by_id.get("V2.WU.H10_C0_TUBE", {})
        for name in H10_C0_ENCLOSURES & set(c0_observed):
            verdict = _sufficient_positive_interval_verdict(c0_observed[name])
            if verdict is None:
                errors.append(
                    f"V2.WU.H10_C0_TUBE.{name} cannot be reduced to a "
                    "sufficient-margin verdict")
            else:
                c0_margin_verdicts.append(verdict)
        c0_status: str | None = None
        if len(c0_margin_verdicts) == len(H10_C0_ENCLOSURES):
            if raw_probe.get("materialized_center_structure") is False:
                c0_status = "FAIL"
            elif raw_probe.get("materialized_center_structure") is True:
                c0_status = combine_verdicts(c0_margin_verdicts)
            if c0_status is not None and \
                    by_id.get("V2.WU.H10_C0_TUBE", {}).get("status") != c0_status:
                errors.append(
                    "V2.WU.H10_C0_TUBE status is not its sufficient-margin "
                    "and structure aggregate")

        c1_margin_verdicts: list[str] = []
        c1_observed = observed_by_id.get("V2.WU.H10_C1_TUBE", {})
        for name in H10_C1_ENCLOSURES & set(c1_observed):
            verdict = _sufficient_positive_interval_verdict(c1_observed[name])
            if verdict is None:
                errors.append(
                    f"V2.WU.H10_C1_TUBE.{name} cannot be reduced to a "
                    "sufficient-margin verdict")
            else:
                c1_margin_verdicts.append(verdict)
        if c0_status is not None and \
                len(c1_margin_verdicts) == len(H10_C1_ENCLOSURES):
            c1_status = combine_verdicts(
                [c0_status, *c1_margin_verdicts])
            if by_id.get("V2.WU.H10_C1_TUBE", {}).get("status") != c1_status:
                errors.append(
                    "V2.WU.H10_C1_TUBE status is not the C0 prerequisite/C1 "
                    "sufficient-margin aggregate")

    if scope == "V2_P2_JETS_KERNEL":
        if raw_probe.get("schema_version") != "rfsn-vdp-p2-jets-probe/1":
            errors.append("raw P2 probe schema version changed")
        if set(raw_probe) != P2_JETS_RAW_FIELDS:
            errors.append(
                "raw P2 top-level field set changed: "
                f"observed={sorted(raw_probe)}, "
                f"expected={sorted(P2_JETS_RAW_FIELDS)}")
        structure_checks = raw_probe.get("structure_checks")
        if not isinstance(structure_checks, dict):
            errors.append("raw P2 structure_checks is not an object")
            structure_checks = {}
        if set(structure_checks) != P2_JETS_STRUCTURE_CHECKS:
            errors.append(
                "raw P2 structure-check set changed: "
                f"observed={sorted(structure_checks)}, "
                f"expected={sorted(P2_JETS_STRUCTURE_CHECKS)}")
        if not all(isinstance(value, bool)
                   for value in structure_checks.values()):
            errors.append("raw P2 structure checks are not all boolean")

        expected_grid = {
            "ordered_axes": ["theta_r", "theta_a", "theta_epsilon", "x"],
            "subdivisions": [16, 8, 4, 2],
            "cell_count": 1024,
            "parameter_derivatives_taken_at_fixed_x": True,
        }
        grid_record = raw_probe.get("grid")
        if grid_record != expected_grid:
            errors.append("raw P2 grid record differs from the frozen exact cover")

        expected_recurrence = {
            "complete": True,
            "target_count": 12,
            "maximum_state_order": 3,
            "maximum_parameter_order": 2,
            "normalized_parameter_dimension": 3,
            "first_parameter_multiindices": P2_JETS_FIRST_MULTIINDICES,
            "second_symmetric_parameter_multiindices":
                P2_JETS_SECOND_MULTIINDICES,
            "term_counts": P2_JETS_TERM_COUNTS,
        }
        recurrence_record = raw_probe.get("recurrence")
        if recurrence_record != expected_recurrence:
            errors.append(
                "raw P2 recurrence does not enumerate the complete frozen "
                "C2_mu(C3_b) rectangle")

        structure_ok = (
            set(structure_checks) == P2_JETS_STRUCTURE_CHECKS and
            all(value is True for value in structure_checks.values()) and
            grid_record == expected_grid and
            recurrence_record == expected_recurrence
        )
        expected_structure_status = "PASS" if structure_ok else "FAIL"
        if raw_probe.get("structure_status") != expected_structure_status:
            errors.append(
                "raw P2 structure_status is not its exact-structure aggregate")

        parameter_enclosures = _check_interval_mapping(
            "raw_probe.parameter_enclosures",
            raw_probe.get("parameter_enclosures"),
            P2_JETS_PARAMETER_ENCLOSURES, errors)
        coefficient_enclosures = _check_interval_mapping(
            "raw_probe.coefficient_enclosures",
            raw_probe.get("coefficient_enclosures"),
            P2_JETS_COEFFICIENT_ENCLOSURES, errors)
        coefficient_margins = _check_interval_mapping(
            "raw_probe.coefficient_gate_margins",
            raw_probe.get("coefficient_gate_margins"),
            P2_JETS_COEFFICIENT_MARGINS, errors)
        lp_coefficients = _check_interval_mapping(
            "raw_probe.lyapunov_perron_coefficients",
            raw_probe.get("lyapunov_perron_coefficients"),
            P2_JETS_LP_COEFFICIENTS, errors)
        lp_enclosures = _check_interval_mapping(
            "raw_probe.lyapunov_perron_enclosures",
            raw_probe.get("lyapunov_perron_enclosures"),
            P2_JETS_LP_ENCLOSURES, errors)
        lp_margins = _check_interval_mapping(
            "raw_probe.lyapunov_perron_gate_margins",
            raw_probe.get("lyapunov_perron_gate_margins"),
            P2_JETS_LP_MARGINS, errors)
        state_enclosures = _check_interval_mapping(
            "raw_probe.state_tensor_enclosures",
            raw_probe.get("state_tensor_enclosures"),
            P2_JETS_STATE_ENCLOSURES, errors)
        state_margins = _check_interval_mapping(
            "raw_probe.state_tensor_gate_margins",
            raw_probe.get("state_tensor_gate_margins"),
            P2_JETS_STATE_MARGINS, errors)
        weighted_enclosures = _check_interval_mapping(
            "raw_probe.weighted_jet_enclosures",
            raw_probe.get("weighted_jet_enclosures"),
            P2_JETS_WEIGHTED_ENCLOSURES, errors)
        original_weighted_enclosures = _check_interval_mapping(
            "raw_probe.original_parameter_weighted_jet_enclosures",
            raw_probe.get("original_parameter_weighted_jet_enclosures"),
            P2_JETS_WEIGHTED_ENCLOSURES, errors)
        frame_enclosures = _check_interval_mapping(
            "raw_probe.frame_derivative_enclosures",
            raw_probe.get("frame_derivative_enclosures"),
            P2_JETS_FRAME_ENCLOSURES, errors)
        physical_weighted_enclosures = _check_interval_mapping(
            "raw_probe.physical_weighted_jet_enclosures",
            raw_probe.get("physical_weighted_jet_enclosures"),
            P2_JETS_WEIGHTED_ENCLOSURES, errors)
        original_physical_weighted_enclosures = _check_interval_mapping(
            "raw_probe.original_parameter_physical_weighted_jet_enclosures",
            raw_probe.get(
                "original_parameter_physical_weighted_jet_enclosures"),
            P2_JETS_WEIGHTED_ENCLOSURES, errors)
        expected_coordinate_composition = {
            "moving_state_norm": "max-of-two-euclidean-blocks",
            "physical_state_norm": "euclidean",
            "jet_tensor_norm": "labelled-multilinear-operator",
            "pure_graph_state_tensor_norm": "hilbert-schmidt",
            "frame_bound_method":
                "sqrt(2)-times-parameter-HS-Frobenius",
            "complete_leibniz_composition": True,
        }
        if raw_probe.get("coordinate_composition") != \
                expected_coordinate_composition:
            errors.append("raw P2 coordinate-composition contract changed")
        expected_linearization_contract = {
            "actual_family_source":
                "analytic-unstable-manifold-plus-P2a-cone-continuation",
            "coefficient_domain": "P2b0-true-orbit-sharpened-x-tube",
            "inverse_mode": "along-true-orbit-Neumann",
            "full_product_ball_contraction_claimed": False,
        }
        if raw_probe.get("linearization_contract") != \
                expected_linearization_contract:
            errors.append("raw P2 linearization-domain contract changed")
        weighted_margins = _check_interval_mapping(
            "raw_probe.weighted_jet_gate_margins",
            raw_probe.get("weighted_jet_gate_margins"),
            P2_JETS_WEIGHTED_MARGINS, errors)

        coefficient_gate_names = {
            f"{name}_gate" for name in P2_JETS_COEFFICIENT_ENCLOSURES}
        coefficient_gates = _check_interval_mapping(
            "raw_probe.coefficient_upper_gates",
            raw_probe.get("coefficient_upper_gates"),
            coefficient_gate_names, errors)
        acceptance_name_map = {
            "alpha_lower": "alpha_lower_gate",
            "green_operator_upper": "green_operator_upper_gate",
            "linearized_contraction_upper":
                "linearized_contraction_upper_gate",
            "resolvent_upper": "resolvent_upper_gate",
            "state_normal_gap_lower": "state_normal_gap_lower_gate",
            "state_second_no_first_exit_margin_lower":
                "state_second_no_first_exit_margin_lower_gate",
            "state_third_no_first_exit_margin_lower":
                "state_third_no_first_exit_margin_lower_gate",
            "origin_second_margin_lower": "origin_second_margin_lower_gate",
            "origin_third_margin_lower": "origin_third_margin_lower_gate",
        }
        acceptance_gates = _check_interval_mapping(
            "raw_probe.acceptance_gates", raw_probe.get("acceptance_gates"),
            set(acceptance_name_map.values()), errors)
        weighted_gate_names = {
            f"{name}_gate" for name in P2_JETS_WEIGHTED_ENCLOSURES}
        weighted_gates = _check_interval_mapping(
            "raw_probe.normalized_weighted_jet_upper_gates",
            raw_probe.get("normalized_weighted_jet_upper_gates"),
            weighted_gate_names, errors)

        positive_input_values = [
            parameter_enclosures.get(name) for name in (
                "R", "Xstar", "Dstar", "omega", "hom_weight", "sigma2",
                "sigma3", "original_first_derivative_scale",
                "original_second_derivative_scale")
        ] + list(coefficient_gates.values()) + \
            list(acceptance_gates.values()) + list(weighted_gates.values())
        parsed_positive_inputs = [
            _fraction_interval(value) for value in positive_input_values]
        all_inputs_strictly_positive = (
            len(parsed_positive_inputs) == 45 and
            all(value is not None and value[0] > 0
                for value in parsed_positive_inputs)
        )
        if not all_inputs_strictly_positive:
            errors.append(
                "raw P2 rational inputs are not all strictly positive despite "
                "the frozen positive argv")
        if structure_checks.get("all_inputs_strictly_positive") is not \
                all_inputs_strictly_positive:
            errors.append(
                "raw P2 all-inputs-positive check differs from its enclosures")
        local_weight_for_structure = _fraction_interval(
            parameter_enclosures.get("omega"))
        reserved_weight_for_structure = _fraction_interval(
            parameter_enclosures.get("hom_weight"))
        weight_ordered = (
            local_weight_for_structure is not None and
            reserved_weight_for_structure is not None and
            reserved_weight_for_structure[1] <
            local_weight_for_structure[0]
        )
        if structure_checks.get("homoclinic_weight_below_local_weight") is not \
                weight_ordered:
            errors.append(
                "raw P2 weight-ordering check differs from its enclosures")
        if structure_checks.get("recurrence_complete") is not (
                recurrence_record == expected_recurrence):
            errors.append(
                "raw P2 recurrence-complete flag differs from its record")
        grid_nonempty = (
            isinstance(grid_record, dict) and
            isinstance(grid_record.get("cell_count"), int) and
            grid_record.get("cell_count", 0) > 0)
        if structure_checks.get("parameter_grid_nonempty") is not grid_nonempty:
            errors.append("raw P2 nonempty-grid flag differs from its grid")

        bridge_variables = bridge.get("variables", {})
        for name in ("r", "a2", "epsilon"):
            try:
                exact_lower = fraction(bridge_variables[name]["lower"])
                exact_upper = fraction(bridge_variables[name]["upper"])
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                continue
            if not _contains_exact_interval(
                    parameter_enclosures.get(name), exact_lower, exact_upper):
                errors.append(
                    f"raw P2 parameter enclosure does not contain the exact "
                    f"bridge interval: {name}")

        domain = p2_jets_configuration.get("coordinate_domain", {})
        lp_contract = p2_jets_configuration.get(
            "lyapunov_perron_contract", {})
        tensor_contract = p2_jets_configuration.get(
            "state_tensor_contract", {})
        scale_contract = p2_jets_configuration.get(
            "parameter_normalization", {}).get(
                "original_from_normalized_derivative_scale", {})
        frozen_parameter_values = {
            "R": domain.get("unstable_radius"),
            "Xstar": domain.get("true_graph_x_absolute_upper"),
            "Dstar": domain.get("true_graph_first_derivative_upper"),
            "omega": lp_contract.get("local_tail_weight"),
            "hom_weight": lp_contract.get(
                "final_homoclinic_weight_reserved_for_p2c"),
            "sigma2": tensor_contract.get("sigma_2"),
            "sigma3": tensor_contract.get("sigma_3"),
            "original_first_derivative_scale":
                scale_contract.get("order_1_operator"),
            "original_second_derivative_scale":
                scale_contract.get("order_2_operator"),
        }
        for name, rational in frozen_parameter_values.items():
            try:
                exact = fraction(rational)
            except (TypeError, ValueError, ZeroDivisionError):
                continue
            if not _contains_exact_interval(
                    parameter_enclosures.get(name), exact, exact):
                errors.append(
                    f"raw P2 {name} does not contain its frozen rational value")

        frozen_coefficient_gates = p2_jets_configuration.get(
            "coefficient_upper_gates", {})
        for name in P2_JETS_COEFFICIENT_ENCLOSURES:
            gate_name = f"{name}_gate"
            try:
                exact = fraction(frozen_coefficient_gates[name])
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                continue
            if not _contains_exact_interval(
                    coefficient_gates.get(gate_name), exact, exact):
                errors.append(f"raw P2 coefficient gate changed: {name}")
            _check_difference_enclosure(
                f"raw P2 coefficient margin {name}",
                coefficient_margins.get(f"{name}_upper_margin"),
                coefficient_gates.get(gate_name),
                coefficient_enclosures.get(name), errors)

        frozen_acceptance_gates = p2_jets_configuration.get(
            "acceptance_gates", {})
        for config_name, raw_name in acceptance_name_map.items():
            try:
                exact = fraction(frozen_acceptance_gates[config_name])
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                continue
            if not _contains_exact_interval(
                    acceptance_gates.get(raw_name), exact, exact):
                errors.append(f"raw P2 acceptance gate changed: {config_name}")

        frozen_weighted_gates = p2_jets_configuration.get(
            "normalized_weighted_jet_upper_gates", {})
        for name in P2_JETS_WEIGHTED_ENCLOSURES:
            gate_name = f"{name}_gate"
            try:
                exact = fraction(frozen_weighted_gates[name])
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                continue
            if not _contains_exact_interval(
                    weighted_gates.get(gate_name), exact, exact):
                errors.append(f"raw P2 weighted-jet gate changed: {name}")
            _check_difference_enclosure(
                f"raw P2 weighted margin {name}",
                weighted_margins.get(f"{name}_upper_margin"),
                weighted_gates.get(gate_name), weighted_enclosures.get(name),
                errors)

        # Independently reconstruct the coefficient identities consumed by
        # the labelled recurrence.  The checker uses exact rational arithmetic
        # on the serialized binary endpoints; the probe's outward intervals
        # must contain these exact interval operations.
        radius_interval = _fraction_interval(parameter_enclosures.get("R"))
        for parameter_order in range(3):
            b_value = _fraction_interval(
                coefficient_enclosures.get(f"B_{parameter_order}"))
            ell_value = _fraction_interval(
                coefficient_enclosures.get(f"ell_{parameter_order}"))
            m_value = _fraction_interval(
                coefficient_enclosures.get(f"m_{parameter_order}"))
            t_value = _fraction_interval(
                coefficient_enclosures.get(f"t_{parameter_order}"))
            if any(value is None for value in (
                    b_value, ell_value, m_value, t_value, radius_interval)):
                errors.append(
                    f"P2 L-coefficient order {parameter_order} cannot be "
                    "independently reconstructed")
                continue
            assert b_value is not None and ell_value is not None
            assert m_value is not None and t_value is not None
            assert radius_interval is not None
            expected_l1 = _fi_add(
                b_value, _fi_mul(_fi_integer(2), ell_value))
            expected_l2 = _fi_mul(_fi_integer(4), m_value)
            expected_l3 = _fi_mul(_fi_integer(8), t_value)
            _check_contains_fraction_interval(
                f"raw P2 L_1_{parameter_order}",
                lp_coefficients.get(f"L_1_{parameter_order}"),
                expected_l1, errors)
            _check_contains_fraction_interval(
                f"raw P2 L_2_{parameter_order}",
                lp_coefficients.get(f"L_2_{parameter_order}"),
                expected_l2, errors)
            _check_contains_fraction_interval(
                f"raw P2 L_3_{parameter_order}",
                lp_coefficients.get(f"L_3_{parameter_order}"),
                expected_l3, errors)
            serialized_l1 = _fraction_interval(
                lp_coefficients.get(f"L_1_{parameter_order}"))
            expected_l0 = None if serialized_l1 is None else _fi_mul(
                serialized_l1, radius_interval)
            _check_contains_fraction_interval(
                f"raw P2 L_0_{parameter_order}",
                lp_coefficients.get(f"L_0_{parameter_order}"),
                expected_l0, errors)

        fixed_rate = _fraction_interval(
            lp_enclosures.get("fixed_core_rate"))
        local_weight = _fraction_interval(
            lp_enclosures.get("local_tail_weight"))
        reserved_weight = _fraction_interval(
            lp_enclosures.get("final_homoclinic_weight_reserved"))
        if fixed_rate is not None:
            fixed_rate_square = _fi_mul(fixed_rate, fixed_rate)
            if fixed_rate[0] <= 0 or not (
                    fixed_rate_square[0] <= Fraction(1, 2) <=
                    fixed_rate_square[1]):
                errors.append("raw P2 fixed core rate does not enclose 1/sqrt(2)")
        if fixed_rate is not None and local_weight is not None:
            _check_contains_fraction_interval(
                "raw P2 core-rate/weight gap",
                lp_enclosures.get("core_rate_minus_local_weight"),
                _fi_sub(fixed_rate, local_weight), errors)
        if local_weight is not None and reserved_weight is not None:
            _check_contains_fraction_interval(
                "raw P2 local/reserved weight gap",
                lp_enclosures.get("local_minus_reserved_weight"),
                _fi_sub(local_weight, reserved_weight), errors)

        gap_interval = _fraction_interval(
            lp_enclosures.get("core_rate_minus_local_weight"))
        green_interval = _fraction_interval(
            lp_enclosures.get("green_operator"))
        expected_green = None if gap_interval is None or gap_interval[0] <= 0 \
            else _fi_reciprocal(gap_interval)
        if gap_interval is not None and gap_interval[0] <= 0:
            errors.append("raw P2 Green-operator denominator is not positive")
        _check_contains_fraction_interval(
            "raw P2 Green operator", lp_enclosures.get("green_operator"),
            expected_green, errors)
        l10_interval = _fraction_interval(lp_coefficients.get("L_1_0"))
        if green_interval is not None and l10_interval is not None:
            _check_contains_fraction_interval(
                "raw P2 linearized contraction",
                lp_enclosures.get("linearized_contraction"),
                _fi_mul(green_interval, l10_interval), errors)
        contraction_interval = _fraction_interval(
            lp_enclosures.get("linearized_contraction"))
        if contraction_interval is not None:
            _check_contains_fraction_interval(
                "raw P2 one-minus-contraction",
                lp_enclosures.get("one_minus_linearized_contraction"),
                _fi_sub(_fi_integer(1), contraction_interval), errors)
        denominator_interval = _fraction_interval(
            lp_enclosures.get("one_minus_linearized_contraction"))
        resolvent_interval = _fraction_interval(
            lp_enclosures.get("resolvent"))
        expected_resolvent = None if denominator_interval is None or \
            denominator_interval[0] <= 0 else \
            _fi_reciprocal(denominator_interval)
        if denominator_interval is not None and denominator_interval[0] <= 0:
            errors.append("raw P2 resolvent denominator is not positive")
        _check_contains_fraction_interval(
            "raw P2 resolvent", lp_enclosures.get("resolvent"),
            expected_resolvent, errors)

        alpha_interval = _fraction_interval(state_enclosures.get("alpha"))
        derivative_interval = _fraction_interval(
            parameter_enclosures.get("Dstar"))
        ell0_interval = _fraction_interval(
            coefficient_enclosures.get("ell_0"))
        m0_interval = _fraction_interval(
            coefficient_enclosures.get("m_0"))
        t0_interval = _fraction_interval(
            coefficient_enclosures.get("t_0"))
        sigma2_interval = _fraction_interval(
            parameter_enclosures.get("sigma2"))
        sigma3_interval = _fraction_interval(
            parameter_enclosures.get("sigma3"))
        state_formula_inputs = (
            alpha_interval, derivative_interval, ell0_interval, m0_interval,
            t0_interval, sigma2_interval, sigma3_interval)
        if any(value is None for value in state_formula_inputs):
            errors.append("raw P2 state-tensor formulas cannot be reconstructed")
        else:
            assert alpha_interval is not None
            assert derivative_interval is not None
            assert ell0_interval is not None and m0_interval is not None
            assert t0_interval is not None and sigma2_interval is not None
            assert sigma3_interval is not None
            one_plus_d = _fi_add(_fi_integer(1), derivative_interval)
            expected_kappa = _fi_sub(
                alpha_interval, _fi_mul(one_plus_d, ell0_interval))
            expected_m2 = _fi_mul(m0_interval, _fi_power(one_plus_d, 3))
            expected_m3 = _fi_add(
                _fi_mul(one_plus_d, _fi_add(
                    _fi_mul(t0_interval, _fi_power(one_plus_d, 3)),
                    _fi_mul(_fi_integer(3), _fi_mul(
                        m0_interval, _fi_mul(sigma2_interval, one_plus_d))))),
                _fi_mul(_fi_integer(3), _fi_mul(
                    sigma2_interval, _fi_add(
                        _fi_mul(m0_interval, _fi_power(one_plus_d, 2)),
                        _fi_mul(ell0_interval, sigma2_interval)))))
            _check_contains_fraction_interval(
                "raw P2 kappa_bar", state_enclosures.get("kappa_bar"),
                expected_kappa, errors)
            _check_contains_fraction_interval(
                "raw P2 M_2", state_enclosures.get("M_2"),
                expected_m2, errors)
            _check_contains_fraction_interval(
                "raw P2 M_3", state_enclosures.get("M_3"),
                expected_m3, errors)
            kappa_interval = _fraction_interval(
                state_enclosures.get("kappa_bar"))
            m2_interval = _fraction_interval(state_enclosures.get("M_2"))
            m3_interval = _fraction_interval(state_enclosures.get("M_3"))
            if kappa_interval is not None and m2_interval is not None:
                _check_contains_fraction_interval(
                    "raw P2 state second no-first-exit margin",
                    state_enclosures.get(
                        "state_second_no_first_exit_margin"),
                    _fi_sub(_fi_mul(
                        _fi_integer(3), _fi_mul(
                            kappa_interval, sigma2_interval)), m2_interval),
                    errors)
            if kappa_interval is not None and m3_interval is not None:
                _check_contains_fraction_interval(
                    "raw P2 state third no-first-exit margin",
                    state_enclosures.get(
                        "state_third_no_first_exit_margin"),
                    _fi_sub(_fi_mul(
                        _fi_integer(4), _fi_mul(
                            kappa_interval, sigma3_interval)), m3_interval),
                    errors)
            _check_contains_fraction_interval(
                "raw P2 origin second margin",
                state_enclosures.get("origin_second_margin"),
                _fi_sub(_fi_mul(
                    _fi_integer(3), _fi_mul(
                        alpha_interval, sigma2_interval)), m0_interval),
                errors)
            _check_contains_fraction_interval(
                "raw P2 origin third margin",
                state_enclosures.get("origin_third_margin"),
                _fi_sub(_fi_mul(
                    _fi_integer(4), _fi_mul(
                        alpha_interval, sigma3_interval)),
                    _fi_add(t0_interval, _fi_mul(
                        _fi_integer(6), _fi_mul(
                            m0_interval, sigma2_interval)))), errors)

        lp_margin_relations = {
            "alpha_lower_margin": (
                state_enclosures.get("alpha"),
                acceptance_gates.get("alpha_lower_gate")),
            "green_operator_upper_margin": (
                acceptance_gates.get("green_operator_upper_gate"),
                lp_enclosures.get("green_operator")),
            "linearized_contraction_upper_margin": (
                acceptance_gates.get("linearized_contraction_upper_gate"),
                lp_enclosures.get("linearized_contraction")),
            "resolvent_upper_margin": (
                acceptance_gates.get("resolvent_upper_gate"),
                lp_enclosures.get("resolvent")),
        }
        for name, (left, right) in lp_margin_relations.items():
            _check_difference_enclosure(
                f"raw P2 LP margin {name}", lp_margins.get(name),
                left, right, errors)
        for name in ("core_rate_minus_local_weight",
                     "local_minus_reserved_weight"):
            if lp_margins.get(name) != lp_enclosures.get(name):
                errors.append(f"raw P2 LP margin {name} changed from its gap")

        state_margin_relations = {
            "state_normal_gap_lower_margin": (
                "kappa_bar", "state_normal_gap_lower_gate"),
            "state_second_no_first_exit_gate_margin": (
                "state_second_no_first_exit_margin",
                "state_second_no_first_exit_margin_lower_gate"),
            "state_third_no_first_exit_gate_margin": (
                "state_third_no_first_exit_margin",
                "state_third_no_first_exit_margin_lower_gate"),
            "origin_second_gate_margin": (
                "origin_second_margin", "origin_second_margin_lower_gate"),
            "origin_third_gate_margin": (
                "origin_third_margin", "origin_third_margin_lower_gate"),
        }
        for margin_name, (value_name, gate_name) in \
                state_margin_relations.items():
            _check_difference_enclosure(
                f"raw P2 state margin {margin_name}",
                state_margins.get(margin_name),
                state_enclosures.get(value_name),
                acceptance_gates.get(gate_name), errors)

        recomputed_jets, recomputed_counts = _recompute_p2_weighted_jets(
            lp_coefficients, lp_enclosures.get("green_operator"),
            lp_enclosures.get("resolvent"), parameter_enclosures.get("R"),
            errors)
        if recomputed_counts and recomputed_counts != P2_JETS_TERM_COUNTS:
            errors.append(
                "independent P2 labelled recurrence term counts changed")
        for name, expected in recomputed_jets.items():
            _check_contains_fraction_interval(
                f"raw P2 weighted jet {name}",
                weighted_enclosures.get(name), expected, errors)

        first_scale = parameter_enclosures.get(
            "original_first_derivative_scale")
        second_scale = parameter_enclosures.get(
            "original_second_derivative_scale")
        for state_order in range(4):
            for parameter_order in range(3):
                name = f"Z_{state_order}_{parameter_order}"
                scale = ({0: {
                    "lower_hex": "0x1p+0", "upper_hex": "0x1p+0",
                    "endpoint_format": "IEEE754_BINARY64_HEX"},
                    1: first_scale, 2: second_scale})[parameter_order]
                _check_product_enclosure(
                    f"raw P2 original-parameter jet {name}",
                    original_weighted_enclosures.get(name),
                    scale, weighted_enclosures.get(name), errors)
                physical_terms: list[FractionInterval] = []
                for frame_order in range(parameter_order + 1):
                    frame_interval = _fraction_interval(
                        frame_enclosures.get(f"T_{frame_order}"))
                    moving_interval = _fraction_interval(
                        weighted_enclosures.get(
                            f"Z_{state_order}_{parameter_order-frame_order}"))
                    if frame_interval is None or moving_interval is None:
                        physical_terms = []
                        break
                    physical_terms.append(_fi_mul(
                        _fi_integer(math.comb(parameter_order, frame_order)),
                        _fi_mul(frame_interval, moving_interval)))
                expected_physical = _fi_sum(physical_terms) \
                    if len(physical_terms) == parameter_order + 1 else None
                _check_contains_fraction_interval(
                    f"raw P2 physical jet {name}",
                    physical_weighted_enclosures.get(name),
                    expected_physical, errors)
                _check_product_enclosure(
                    f"raw P2 original-parameter physical jet {name}",
                    original_physical_weighted_enclosures.get(name),
                    scale, physical_weighted_enclosures.get(name), errors)

        expected_obligation_enclosures = {
            "P2.JETS.COEFFICIENTS": coefficient_margins,
            "V2.WU.STATE_C23": state_margins,
            "V2.WU.MIXED_JETS": weighted_margins,
            "V2.WU.WEIGHTED_HALF_ORBITS": {
                **lp_margins, **weighted_margins},
        }
        for identifier, expected in expected_obligation_enclosures.items():
            if by_id.get(identifier, {}).get("enclosures", {}) != expected:
                errors.append(
                    f"{identifier} enclosures differ from the raw P2 margins")

        def sufficient_aggregate(
                values: dict[str, Any], expected_names: set[str]) -> str | None:
            verdicts: list[str] = []
            for name in expected_names & set(values):
                verdict = _sufficient_positive_interval_verdict(values[name])
                if verdict is None:
                    errors.append(
                        f"raw P2 margin {name} cannot be reduced to a verdict")
                else:
                    verdicts.append(verdict)
            return combine_verdicts(verdicts) \
                if len(verdicts) == len(expected_names) else None

        coefficient_own = sufficient_aggregate(
            coefficient_margins, P2_JETS_COEFFICIENT_MARGINS)
        state_own = sufficient_aggregate(
            state_margins, P2_JETS_STATE_MARGINS)
        lp_own = sufficient_aggregate(lp_margins, P2_JETS_LP_MARGINS)
        weighted_own = sufficient_aggregate(
            weighted_margins, P2_JETS_WEIGHTED_MARGINS)
        if None not in (coefficient_own, state_own, lp_own, weighted_own):
            assert coefficient_own is not None and state_own is not None
            assert lp_own is not None and weighted_own is not None
            coefficient_status = combine_verdicts(
                [expected_structure_status, coefficient_own])
            state_status = combine_verdicts(
                [expected_structure_status, coefficient_status, state_own])
            mixed_own = combine_verdicts([lp_own, weighted_own])
            mixed_status = combine_verdicts([
                expected_structure_status, state_status,
                coefficient_status, mixed_own])
            weighted_status = combine_verdicts([
                expected_structure_status, coefficient_status, mixed_own])
            expected_atomic_statuses = {
                "P2.JETS.COEFFICIENTS": coefficient_status,
                "V2.WU.STATE_C23": state_status,
                "V2.WU.MIXED_JETS": mixed_status,
                "V2.WU.WEIGHTED_HALF_ORBITS": weighted_status,
            }
            for identifier, expected in expected_atomic_statuses.items():
                if by_id.get(identifier, {}).get("status") != expected:
                    errors.append(
                        f"{identifier} status is not its independently "
                        "reduced P2 aggregate")

    rounding = certificate.get("rounding_self_test", {})
    rounding_tests = {item.get("id"): item for item in rounding.get("tests", [])}
    if not ROUNDING_IDS <= set(rounding_tests):
        errors.append(f"rounding tests missing: {sorted(ROUNDING_IDS - set(rounding_tests))}")
    expected_rounding = combine_verdicts(
        item.get("status", "INCONCLUSIVE") for item in rounding.get("tests", []))
    if rounding.get("status") != expected_rounding:
        errors.append("rounding_self_test.status is not its test aggregate")
    if raw_probe.get("rounding_self_test") != rounding:
        errors.append("raw-probe rounding report differs from the certificate report")
    if scope != "PREFLIGHT":
        expected_raw_status = combine_verdicts(
            [expected_rounding,
             raw_probe.get("mathematical_status", "INCONCLUSIVE")])
        if raw_probe.get("status") != expected_raw_status:
            errors.append("raw-probe status is not its rounding/mathematical aggregate")
    if "ENV.ROUNDING" in by_id and by_id["ENV.ROUNDING"].get("status") != rounding.get("status"):
        errors.append("ENV.ROUNDING differs from rounding_self_test.status")

    toolchain = certificate.get("toolchain", {})
    logs = certificate.get("logs", {})
    bound_hashes = {
        item.get("path"): item.get("sha256")
        for item in certificate.get("source_bindings", [])
        if isinstance(item, dict)
    }
    flagship_import = toolchain.get("flagship_import", {})
    flagship_lock = load_json(HERE / "flagship_import.lock.json")
    expected_flagship_fields = {
        "lock_sha256": bound_hashes.get(
            "validation/rigorous/flagship_import.lock.json"),
        "commit": flagship_lock.get("commit"),
        "tree": flagship_lock.get("tree"),
        "access": "git-object-read-only",
    }
    if not isinstance(flagship_import, dict):
        errors.append("toolchain flagship-import record is malformed")
        expected_source_status = "INCONCLUSIVE"
    else:
        for name, expected_value in expected_flagship_fields.items():
            if flagship_import.get(name) != expected_value:
                errors.append(f"toolchain flagship-import {name} mismatch")
        flagship_errors = flagship_import.get("errors")
        if isinstance(flagship_errors, list):
            expected_source_status = "FAIL" if flagship_errors else "PASS"
        elif "reason" in flagship_import and \
                "repository_path" not in flagship_import:
            expected_source_status = "INCONCLUSIVE"
        else:
            errors.append("toolchain flagship-import verdict evidence is malformed")
            expected_source_status = "INCONCLUSIVE"
    if "ENV.SOURCE_BINDING" in by_id and \
            by_id["ENV.SOURCE_BINDING"].get("status") != expected_source_status:
        errors.append("ENV.SOURCE_BINDING differs from flagship-import evidence")
    if toolchain.get("dependency_lock_sha256") != bound_hashes.get(
            "validation/rigorous/dependency.lock.json"):
        errors.append("toolchain dependency-lock hash does not match its source binding")
    probe_source_by_scope = {
        "PREFLIGHT": "validation/rigorous/src/rounding_self_test.cpp",
        "V1_V2_1_KERNEL": "validation/rigorous/src/vdp_parameter_box_probe.cpp",
        "V2_LOCAL_GRAPH_KERNEL": "validation/rigorous/src/vdp_local_graph_probe.cpp",
        "V2_H10_C01_KERNEL": "validation/rigorous/src/vdp_h10_c01_probe.cpp",
        "V2_P2_JETS_KERNEL": "validation/rigorous/src/vdp_p2_jets_probe.cpp",
    }
    probe_source = probe_source_by_scope.get(scope)
    probe_build = toolchain.get("probe_build", {})
    if probe_source is not None and probe_build.get("source_sha256") != \
            bound_hashes.get(probe_source):
        errors.append("compiled probe source hash differs from its source binding")
    if scope == "V2_P2_JETS_KERNEL":
        probe_stdout = probe_build.get("probe_stdout")
        if not isinstance(probe_stdout, str):
            errors.append("P2 probe exact stdout evidence is missing")
        else:
            if sha256_bytes(probe_stdout.encode()) != logs.get(
                    "probe_stdout_sha256"):
                errors.append("P2 probe stdout hash differs from its exact evidence")
            try:
                parsed_stdout = json.loads(probe_stdout)
            except json.JSONDecodeError as error:
                errors.append(f"P2 probe stdout evidence is invalid JSON: {error}")
            else:
                if parsed_stdout != raw_probe:
                    errors.append(
                        "P2 parsed raw_probe differs from its exact stdout evidence")
        for name in ("compile_stdout_sha256", "compile_stderr_sha256",
                     "probe_stderr_sha256"):
            if logs.get(name) != sha256_bytes(b""):
                errors.append(f"P2 strict execution emitted unexpected {name}")
    expected_probe_arguments: list[str] = []
    if scope == "V1_V2_1_KERNEL":
        expected_probe_arguments = box_arguments(box)
    elif scope == "V2_LOCAL_GRAPH_KERNEL":
        expected_probe_arguments = box_arguments(bridge)
        radius = configuration.get("coordinate_block", {}).get(
            "unstable_radius", {})
        try:
            expected_probe_arguments.extend(
                [radius["numerator"], radius["denominator"]])
        except KeyError:
            pass
    elif scope == "V2_H10_C01_KERNEL":
        expected_probe_arguments = box_arguments(bridge)
        frozen_probe_inputs = [
            h10_configuration.get("coordinate_domain", {}).get(
                "unstable_radius", {}),
            h10_configuration.get("tube_radii", {}).get(
                "value_euclidean", {}),
            h10_configuration.get("tube_radii", {}).get(
                "first_derivative_frobenius", {}),
        ]
        try:
            for value in frozen_probe_inputs:
                expected_probe_arguments.extend(
                    [value["numerator"], value["denominator"]])
        except KeyError:
            pass
    elif scope == "V2_P2_JETS_KERNEL":
        try:
            expected_probe_arguments = p2_jets_arguments(
                bridge, p2_jets_configuration)
        except (KeyError, TypeError, ValueError) as error:
            errors.append(f"cannot reconstruct P2 jets probe arguments: {error}")
    recorded_probe_argv = probe_build.get("probe_argv")
    if not isinstance(recorded_probe_argv, list) or not recorded_probe_argv:
        errors.append("probe argv is missing")
    elif recorded_probe_argv[1:] != expected_probe_arguments:
        errors.append("probe argv does not match the frozen scope inputs")
    if scope == "V2_P2_JETS_KERNEL" and not errors:
        errors.extend(_replay_p2_probe(
            certificate, repository, recorded_commit, recorded_dirty))
    raw_status_for_exit = rounding.get("status") if scope == "PREFLIGHT" \
        else raw_probe.get("status")
    expected_probe_exit = {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 2}.get(
        raw_status_for_exit)
    if expected_probe_exit is not None and \
            probe_build.get("probe_exit_code") != expected_probe_exit:
        errors.append("probe exit code differs from the raw probe verdict")
    if scope == "V2_H10_C01_KERNEL":
        center = h10_configuration.get("imported_core_center", {})
        term_table = center.get("term_table", {})
        imported_header = probe_build.get("imported_header", {})
        expected_header = {
            "repository_commit": center.get("commit"),
            "repository_path": term_table.get("path"),
            "expected_sha256": term_table.get("sha256"),
            "materialized_sha256": term_table.get("sha256"),
            "git_show_stdout_sha256": term_table.get("sha256"),
            "compiler_include_mode": "absolute-forced-include",
        }
        if not isinstance(imported_header, dict):
            errors.append("H10 probe imported-header record is malformed")
        else:
            for name, expected_value in expected_header.items():
                if imported_header.get(name) != expected_value:
                    errors.append(f"H10 probe imported-header {name} mismatch")
            stderr_hash = imported_header.get("git_show_stderr_sha256")
            if not isinstance(stderr_hash, str) or len(stderr_hash) != 64:
                errors.append("H10 probe imported-header stderr hash is malformed")
            include_argument = imported_header.get("compiler_include_argument")
            if not isinstance(include_argument, str) or \
                    not Path(include_argument).is_absolute() or \
                    Path(include_argument).name != "unstable_graph_terms.hpp":
                errors.append(
                    "H10 probe imported-header forced-include path is invalid")
            compile_argv = probe_build.get("compile_argv", [])
            include_pairs = [
                compile_argv[index + 1]
                for index, item in enumerate(compile_argv[:-1])
                if item == "-include"
            ] if isinstance(compile_argv, list) else []
            if include_pairs != [include_argument]:
                errors.append(
                    "H10 probe compile argv does not force exactly the recorded header")

        audit_execution = toolchain.get("h10_exact_center_audit_execution", {})
        if not isinstance(audit_execution, dict):
            errors.append("H10 exact-center audit execution record is malformed")
        else:
            if audit_execution.get("audit_source_sha256") != bound_hashes.get(
                    "validation/rigorous/audit_h10_center.py"):
                errors.append(
                    "H10 exact-center audit source hash differs from its binding")
            audit = certificate.get("h10_exact_center_audit", {})
            expected_audit_exit = {
                "PASS": 0, "FAIL": 1, "INCONCLUSIVE": 2}.get(
                    audit.get("status"))
            if audit_execution.get("audit_exit_code") != expected_audit_exit:
                errors.append("H10 exact-center audit exit code differs from its verdict")
            expected_audit_stdout = (
                json.dumps(audit, indent=2, sort_keys=True) + "\n").encode()
            if logs.get("h10_audit_stdout_sha256") != sha256_bytes(
                    expected_audit_stdout):
                errors.append(
                    "H10 exact-center audit stdout hash differs from its report")
            if logs.get("h10_audit_stderr_sha256") != sha256_bytes(b""):
                errors.append("H10 exact-center audit stderr is not empty")
            audit_argv = audit_execution.get("audit_argv")
            if not isinstance(audit_argv, list) or len(audit_argv) < 4:
                errors.append("H10 exact-center audit argv is missing")
            else:
                protocol = h10_configuration.get("exact_center_audit", {})
                flagship_path = toolchain.get(
                    "flagship_import", {}).get("repository_path")
                expected_audit_tail = [
                    "--flagship-repository", flagship_path,
                    "--commit", center.get("commit"),
                    "--generator-path", center.get("generator", {}).get("path"),
                    "--generator-sha256", center.get("generator", {}).get("sha256"),
                    "--header-path", term_table.get("path"),
                    "--header-sha256", term_table.get("sha256"),
                    "--h1-term-count", str(protocol.get("h1_term_count")),
                    "--h2-term-count", str(protocol.get("h2_term_count")),
                    "--defect1-term-count", str(protocol.get("defect1_term_count")),
                    "--defect2-term-count", str(protocol.get("defect2_term_count")),
                    "--h-min-degree", str(
                        protocol.get("center_minimum_total_degree")),
                    "--h-max-degree", str(
                        protocol.get("center_maximum_total_degree")),
                    "--defect-min-degree", str(
                        protocol.get("defect_minimum_total_degree")),
                    "--defect-max-degree", str(
                        protocol.get("defect_maximum_total_degree")),
                    "--timeout-seconds", "900",
                ]
                if audit_argv[3:] != expected_audit_tail:
                    errors.append("H10 exact-center audit argv differs from frozen inputs")
                expected_argv_hash = sha256_bytes(json.dumps(
                    audit_argv, separators=(",", ":")).encode())
                if audit_execution.get("audit_argv_sha256") != expected_argv_hash:
                    errors.append("H10 exact-center audit argv hash is inconsistent")
    if "ENV.CAPD_BINDING" in by_id and \
            by_id["ENV.CAPD_BINDING"].get("status") != toolchain.get("status"):
        errors.append("ENV.CAPD_BINDING differs from toolchain.status")
    if toolchain.get("status") == "PASS":
        if toolchain.get("strict_library_build_status") != "PASS":
            errors.append("a PASS toolchain must record a strict CAPD/FILIB build PASS")
        scan = toolchain.get("capd", {}).get("compile_commands_scan", {})
        if scan.get("entry_count", 0) <= 0 or \
                scan.get("entries_with_all_strict_flags") != scan.get("entry_count"):
            errors.append("PASS toolchain does not bind an all-entry strict compile scan")
        if not toolchain.get("capd", {}).get("compile_commands_sha256"):
            errors.append("PASS toolchain does not hash compile_commands.json")

    replay = certificate.get("independent_replay", {})
    if replay.get("status") != "PENDING_REQUIRED":
        errors.append(
            "the local checker accepts only PENDING_REQUIRED; independent replay "
            "must be aggregated by a future evidence-bearing schema")
    if replay.get("required_distinct_machines") != 2:
        errors.append("rigorous replay policy requires exactly two distinct machines")
    if replay.get("observed_distinct_machines") != 1:
        errors.append("a local certificate must record exactly one observed machine")
    integrity = certificate.get("integrity_status")
    mathematical = certificate.get("mathematical_status")
    if integrity == "FAIL" or mathematical == "FAIL" or replay.get("status") == "FAIL":
        expected_final = "FAIL"
    elif replay.get("status") != "PASS":
        expected_final = "INCONCLUSIVE"
    elif integrity == mathematical == "PASS":
        expected_final = "PASS"
    else:
        expected_final = "INCONCLUSIVE"
    if certificate.get("final_status") != expected_final:
        errors.append(f"final_status must be {expected_final} under the recorded verdicts")

    enough_machines = replay.get("observed_distinct_machines", 0) >= \
        replay.get("required_distinct_machines", 2)
    clean_release = not recorded_dirty and not allow_dirty
    strict_build = toolchain.get("strict_library_build_status") == "PASS"
    eligible = expected_final == "PASS" and enough_machines and clean_release and strict_build
    if certificate.get("claim_bearing") != eligible:
        errors.append("claim_bearing is inconsistent with replay/clean/strict requirements")
    if certificate.get("release_eligible") != eligible:
        errors.append("release_eligible is inconsistent with replay/clean/strict requirements")
    if replay.get("status") == "PENDING_REQUIRED" and (
            certificate.get("claim_bearing") or certificate.get("release_eligible")):
        errors.append("pending independent replay cannot be claim-bearing")
    return errors


def check_certificate(path: Path, repository: Path = REPOSITORY) -> list[str]:
    certificate = load_json(path)
    return schema_errors(certificate) + semantic_errors(certificate, repository)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--repository", type=Path, default=REPOSITORY)
    arguments = parser.parse_args()
    try:
        certificate = load_json(arguments.certificate)
        errors = schema_errors(certificate) + semantic_errors(
            certificate, arguments.repository.resolve())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"INVALID: {error}", file=sys.stderr)
        return 1
    print(
        "VALID: certificate is internally consistent; "
        f"final_status={certificate['final_status']}; "
        f"claim_bearing={str(certificate['claim_bearing']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
