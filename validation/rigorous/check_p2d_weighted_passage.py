#!/usr/bin/env python3
"""Check the P2d weighted Kato passage with exact rational gates."""

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

import check_p2d_exact_sections as exact_sections  # noqa: E402


zero_energy = exact_sections.zero_energy

SCHEMA_VERSION = "rfsn-vdp-p2d-weighted-kato-passage-check/1"
SCOPE = "V2_CHART_WEIGHTED_PASSAGE_LOCAL_EXACT_RATIONAL_GATES"
PROOF_CONTRACT = "rfsn-vdp-p2d-explicit-weighted-kato-passage/1"
PROOF_RELATIVE = "theory/EXPLICIT_WEIGHTED_KATO_PASSAGE.md"
PROOF_PATH = REPOSITORY / PROOF_RELATIVE
PROOF_SHA256 = (
    "78023f2c1511b2037b07ad9fa6a70504"
    "abb8734ee9f73103a00634c91f315f1c"
)
KATO_CERTIFICATE_RELATIVE = (
    "validation/rigorous/results/vdp_bridge_v1_p2b_kato.json"
)
KATO_CERTIFICATE_PATH = REPOSITORY / KATO_CERTIFICATE_RELATIVE
KATO_AUDIT_SCHEMA = "rfsn-vdp-p2-kato-exact-audit/1"

REQUIRED_WEIGHTED_AUDIT_CHECKS = (
    "quadratic_hamiltonian_uses_I2K",
    "linear_zero_energy_q_is_minus_beta_over_alpha_nu",
    "linear_incoming_expanding_radius_squared_is_nu_squared_over_alpha_squared_rho_squared",
    "linear_positive_flight_domain_is_zero_less_abs_nu_less_alpha_rho_squared",
    "linear_reach_time_hits_rho_and_has_Dlog_minus_one_over_alpha",
    "kato_expanding_phase_speed_is_plus_beta",
    "linear_phase_Dlog_from_plus_beta_speed_is_minus_beta_over_alpha",
)

ALPHA_BETA_LOWER = Fraction(2, 3)
ALPHA_BETA_UPPER = Fraction(3, 4)
PARAMETER_JET_UPPER = Fraction(1, 100)
PASSAGE_OUTER_RATIO = Fraction(1, 16)
PASSAGE_FINAL_RATIO = Fraction(1, 2)
LOG_FINAL_UPPER = 58
ONE_PLUS_LOG_FINAL_UPPER = 59
ARGUMENT_ABSOLUTE_UPPER = Fraction(4)
PI_RATIONAL_UPPER = Fraction(22, 7)
NORMALIZED_TO_ORIGINAL_MAX = (1, 25, 625)
ORIGINAL_SCALES = {"r": 25, "a2": 4, "epsilon": 5}
SECOND_PARAMETER_PAIRS = (
    ("r", "r"),
    ("r", "a2"),
    ("r", "epsilon"),
    ("a2", "a2"),
    ("a2", "epsilon"),
    ("epsilon", "epsilon"),
)


class WeightedPassageCheckError(ValueError):
    """A required proof, source binding, or exact gate is malformed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise WeightedPassageCheckError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def rational(value: Fraction | int) -> dict[str, str]:
    value = Fraction(value)
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
    }


def as_fraction(record: Any, label: str) -> Fraction:
    require(isinstance(record, dict), f"{label} is not a rational record")
    try:
        return Fraction(int(record["numerator"]), int(record["denominator"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        raise WeightedPassageCheckError(
            f"{label} is not a valid rational record: {error}") from error


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def proof_binding(path: Path) -> dict[str, Any]:
    source = path.read_bytes()
    digest = sha256_bytes(source)
    try:
        text = source.decode("utf-8")
    except UnicodeError as error:
        raise WeightedPassageCheckError(
            f"weighted-passage proof is not UTF-8: {error}") from error
    contract_present = PROOF_CONTRACT in text
    return {
        "path": PROOF_RELATIVE,
        "expected_sha256": PROOF_SHA256,
        "observed_sha256": digest,
        "proof_contract": PROOF_CONTRACT,
        "proof_contract_present": contract_present,
        "matched": digest == PROOF_SHA256 and contract_present,
    }


def stirling_second(order: int, blocks: int) -> int:
    require(order >= 0 and blocks >= 0,
            "Stirling indices must be nonnegative")
    if order == 0:
        return 1 if blocks == 0 else 0
    if blocks == 0 or blocks > order:
        return 0
    table = [[0] * (order + 1) for _ in range(order + 1)]
    table[0][0] = 1
    for n in range(1, order + 1):
        for k in range(1, n + 1):
            table[n][k] = table[n - 1][k - 1] + k * table[n - 1][k]
    return table[order][blocks]


def logarithmic_cauchy_weight(order: int) -> int:
    """Return Lambda_m in the all-finite-order proof."""
    require(order >= 0, "logarithmic derivative order must be nonnegative")
    total = 0
    for j in range(order + 1):
        inner = sum(
            stirling_second(j, k) * math.factorial(k)
            for k in range(j + 1)
        )
        total += math.comb(order, j) * inner
    return total


def _poly_add(*values: list[Fraction]) -> list[Fraction]:
    size = max((len(value) for value in values), default=0)
    result = [Fraction(0) for _ in range(size)]
    for value in values:
        for index, coefficient in enumerate(value):
            result[index] += coefficient
    return result


def _poly_scale(value: list[Fraction], factor: Fraction) -> list[Fraction]:
    return [factor * coefficient for coefficient in value]


def _poly_multiply(
        left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    result = [Fraction(0) for _ in range(len(left) + len(right) - 1)]
    for i, left_coefficient in enumerate(left):
        for j, right_coefficient in enumerate(right):
            result[i + j] += left_coefficient * right_coefficient
    return result


def weighted_audit_gates(certificate: dict[str, Any]) -> dict[str, Any]:
    authenticated = exact_sections.exact_audit_gates(certificate)
    try:
        checks = certificate["exact_audit"]["report"]["checks"]
    except (KeyError, TypeError) as error:
        raise WeightedPassageCheckError(
            f"weighted exact-audit checks are missing: {error}") from error
    required = {
        name: checks.get(name) is True
        for name in REQUIRED_WEIGHTED_AUDIT_CHECKS
    }
    require(all(required.values()),
            "a required weighted Kato identity is not PASS")
    prerequisite = certificate.get("p2bk_prerequisite")
    require(isinstance(prerequisite, dict),
            "the P2bK prerequisite record is missing")
    require(prerequisite.get("path") == KATO_CERTIFICATE_RELATIVE,
            "the P2bK prerequisite path changed")
    matching_bindings = [
        item for item in certificate.get("source_bindings", [])
        if isinstance(item, dict)
        and item.get("path") == KATO_CERTIFICATE_RELATIVE
    ]
    require(matching_bindings == [{
        "path": KATO_CERTIFICATE_RELATIVE,
        "role": "p2d-frame-input",
        "sha256": prerequisite.get("sha256"),
    }], "the P2bK source binding is not unique and exact")
    try:
        kato_source = KATO_CERTIFICATE_PATH.read_bytes()
        kato_certificate = json.loads(kato_source)
        kato_audit = kato_certificate["kato_exact_algebra_audit"]
        kato_checks = kato_audit["checks"]
    except (OSError, UnicodeError, json.JSONDecodeError,
            KeyError, TypeError) as error:
        raise WeightedPassageCheckError(
            f"the P2bK characteristic source is malformed: {error}") \
            from error
    kato_digest = sha256_bytes(kato_source)
    require(kato_digest == prerequisite.get("sha256"),
            "the P2bK characteristic source SHA-256 changed")
    require(kato_certificate.get("mathematical_status") == "PASS",
            "the P2bK mathematical prerequisite is not PASS")
    require(kato_audit.get("schema_version") == KATO_AUDIT_SCHEMA,
            "the P2bK exact-audit schema changed")
    require(kato_audit.get("status") == "PASS",
            "the P2bK exact algebra audit is not PASS")
    require(kato_checks.get("alpha_beta_spectral_relations") is True,
            "alpha^2+beta^2=1 is not an authenticated P2bK identity")
    return {
        "source_sha256": authenticated["source_sha256"],
        "schema_version": authenticated["schema_version"],
        "archived_check_count": authenticated["archived_check_count"],
        "all_archived_checks_pass": authenticated["all_archived_checks_pass"],
        "required_checks": required,
        "characteristic_identity": {
            "formula": "alpha_mu^2+beta_mu^2=1",
            "check": "alpha_beta_spectral_relations",
            "passed": True,
            "source_path": KATO_CERTIFICATE_RELATIVE,
            "source_sha256": kato_digest,
            "audit_schema": KATO_AUDIT_SCHEMA,
        },
    }


def _parameter_product_bounds(
        left: tuple[Fraction, Fraction, Fraction],
        right: tuple[Fraction, Fraction, Fraction],
        ) -> tuple[Fraction, Fraction, Fraction]:
    return (
        left[0] * right[0],
        left[1] * right[0] + left[0] * right[1],
        left[2] * right[0]
        + 2 * left[1] * right[1]
        + left[0] * right[2],
    )


def _weighted_generator(
        order: int,
        analytic_radius: Fraction,
        a_bounds: tuple[Fraction, Fraction, Fraction],
        b_bounds: tuple[Fraction, Fraction, Fraction],
        omega_bounds: tuple[Fraction, Fraction, Fraction],
        e_bounds: tuple[Fraction, Fraction, Fraction],
        argument_bounds: tuple[Fraction, Fraction, Fraction],
        ) -> tuple[tuple[Fraction, ...], tuple[Fraction, ...], int]:
    weight = logarithmic_cauchy_weight(order)
    previous = logarithmic_cauchy_weight(order - 1) if order else 0
    log_weight = weight + order * previous
    centered_a = tuple(2 * value for value in a_bounds)
    centered_b = tuple(2 * value for value in b_bounds)
    centered_omega = tuple(2 * value for value in omega_bounds)
    centered_e = tuple(2 * value for value in e_bounds)
    centered_argument = (
        argument_bounds[0],
        2 * argument_bounds[1],
        2 * argument_bounds[2],
    )
    time = tuple(
        (centered_a[j] * log_weight + centered_b[j] * weight)
        / analytic_radius
        for j in range(3)
    )
    phase = tuple(
        (centered_omega[j] * log_weight
         + (centered_e[j] + centered_argument[j]) * weight)
        / analytic_radius
        for j in range(3)
    )
    return time, phase, weight


def _original_parameter_table(
        normalized: dict[int, tuple[tuple[Fraction, ...],
                                    tuple[Fraction, ...]]],
        max_order: int,
        ) -> dict[str, list[dict[str, Any]]]:
    def records(parameter_order: int, scale: int) -> list[dict[str, Any]]:
        return [
            {
                "time": rational(scale * normalized[m][0][parameter_order]),
                "phase": rational(scale * normalized[m][1][parameter_order]),
                "sum": rational(scale * (
                    normalized[m][0][parameter_order]
                    + normalized[m][1][parameter_order])),
            }
            for m in range(max_order + 1)
        ]

    result = {"value": records(0, 1)}
    for axis, scale in ORIGINAL_SCALES.items():
        result[f"D_{axis}"] = records(1, scale)
    for first, second in SECOND_PARAMETER_PAIRS:
        result[f"D_{first}_{second}"] = records(
            2, ORIGINAL_SCALES[first] * ORIGINAL_SCALES[second])
    return result


def compute_weighted_bounds(
        exact_report: dict[str, Any],
        certificate: dict[str, Any],
        max_log_order: int = 3,
        ) -> dict[str, Any]:
    require(max_log_order >= 3,
            "the machine table must include log orders zero through three")
    zero_exact = zero_energy.compute_exact_bounds()
    frame = zero_energy.frame_gates(certificate)
    require(all(frame["checks"].values()), "frame hull gates are not PASS")

    alpha_lower = as_fraction(frame["alpha"]["lower"], "alpha.lower")
    alpha_upper = as_fraction(frame["alpha"]["upper"], "alpha.upper")
    beta_lower = as_fraction(frame["beta"]["lower"], "beta.lower")
    beta_upper = as_fraction(frame["beta"]["upper"], "beta.upper")
    alpha_d1 = as_fraction(
        frame["alpha"]["D1_absolute_upper"], "alpha.D1")
    alpha_d2 = as_fraction(
        frame["alpha"]["D2_absolute_upper"], "alpha.D2")
    beta_d1 = as_fraction(
        frame["beta"]["D1_absolute_upper"], "beta.D1")
    beta_d2 = as_fraction(
        frame["beta"]["D2_absolute_upper"], "beta.D2")

    constants = zero_exact["constants"]
    q0 = as_fraction(constants["Q0"], "Q0")
    q1 = as_fraction(constants["Q1"], "Q1")
    q2 = as_fraction(constants["Q2"], "Q2")
    q_radius = as_fraction(constants["nu_outer"], "nu_outer")
    action_radius = as_fraction(constants["action_radius_s"], "action_radius")
    action_gap = as_fraction(constants["action_cauchy_gap"], "action_gap")
    m_bar = as_fraction(
        constants["normal_form_remainder_Mbar"], "Mbar")
    a_star = as_fraction(constants["a_star"], "a_star")
    section_radius = as_fraction(
        exact_report["exact_values"]["constants"]["section_radius_rho"],
        "section_radius_rho",
    )
    section_interval = as_fraction(
        exact_report["exact_values"]["constants"]["section_nu_star"],
        "section_nu_star",
    )

    analytic_radius = q_radius * PASSAGE_OUTER_RATIO
    passage_radius = analytic_radius * PASSAGE_FINAL_RATIO
    p_bounds = (q0 / q_radius, q1 / q_radius, q2 / q_radius)
    p_zero_lower = ALPHA_BETA_LOWER / ALPHA_BETA_UPPER
    p_zero_upper = ALPHA_BETA_UPPER / ALPHA_BETA_LOWER
    outer_x = analytic_radius / q_radius
    p_variation = p_bounds[0] * outer_x / (1 - outer_x)
    p_absolute = p_zero_upper + p_variation
    real_slice_p_upper = -p_zero_lower + p_variation
    z_zero_lower = 1 + p_zero_lower**2
    z_relative_variation = (
        p_variation * (2 * p_zero_upper + p_variation) / z_zero_lower)
    branch_margin = 1 - p_variation

    m1 = m_bar / action_gap
    m2 = 2 * m_bar / action_gap**2
    m3 = 6 * m_bar / action_gap**3
    h0 = ALPHA_BETA_UPPER + m1
    h1 = PARAMETER_JET_UPPER + m1 + m2 * q1
    h2 = (
        PARAMETER_JET_UPPER + 2 * m1 + 2 * m2 * q1
        + m3 * q1**2 + m2 * q2
    )
    a_bounds = (
        1 / a_star,
        h1 / a_star**2,
        2 * h1**2 / a_star**3 + h2 / a_star**2,
    )
    omega_bounds = (
        h0 * a_bounds[0],
        h1 * a_bounds[0] + h0 * a_bounds[1],
        h2 * a_bounds[0]
        + 2 * h1 * a_bounds[1]
        + h0 * a_bounds[2],
    )

    z_inverse = Fraction(64, 49)
    c_bounds = (
        Fraction(54),
        Fraction(5, 4) * p_bounds[1] * z_inverse,
        (p_bounds[1]**2 + Fraction(5, 4) * p_bounds[2]) * z_inverse
        + 2 * Fraction(5, 4)**2 * p_bounds[1]**2 * z_inverse**2,
    )
    argument_bounds = (
        Fraction(1, 7),
        Fraction(8, 7) * p_bounds[1],
        Fraction(8, 7) * p_bounds[2]
        + Fraction(64, 49) * p_bounds[1]**2,
    )
    b_bounds = _parameter_product_bounds(a_bounds, c_bounds)
    e_bounds = _parameter_product_bounds(omega_bounds, c_bounds)

    normalized: dict[int, tuple[tuple[Fraction, ...],
                                tuple[Fraction, ...]]] = {}
    weights: dict[int, int] = {}
    for order in range(max_log_order + 1):
        time, phase, weight = _weighted_generator(
            order, analytic_radius, a_bounds, b_bounds,
            omega_bounds, e_bounds, argument_bounds)
        normalized[order] = (time, phase)
        weights[order] = weight

    all_order_witness = {}
    for order in (0, 1, 2, 3, 7):
        time, phase, weight = _weighted_generator(
            order, analytic_radius, a_bounds, b_bounds,
            omega_bounds, e_bounds, argument_bounds)
        c_m = max(
            NORMALIZED_TO_ORIGINAL_MAX[j] * (time[j] + phase[j])
            for j in range(3)
        )
        all_order_witness[str(order)] = {
            "lambda_m": str(weight),
            "nu_star_m": rational(passage_radius),
            "C_m_original_parameters": rational(c_m),
        }

    # Sharp order-zero and first-log bounds used only for clock inversion.
    final_x = passage_radius / q_radius
    p_final_variation = p_bounds[0] * final_x / (1 - final_x)
    p_final_absolute = p_zero_upper + p_final_variation
    final_z_relative = (
        p_final_variation
        * (2 * p_zero_upper + p_final_variation)
        / z_zero_lower
    )
    c_final_variation = (
        Fraction(1, 2) * final_z_relative / (1 - final_z_relative))
    a_difference = m2 * passage_radius * (p_final_absolute + 1)
    inverse_a_difference = a_difference / (
        ALPHA_BETA_LOWER * a_star)
    ac_difference = (
        inverse_a_difference * c_bounds[0]
        + a_bounds[0] * c_final_variation
    )
    sharp_tau = (
        inverse_a_difference * LOG_FINAL_UPPER + ac_difference)

    dlog_p = p_bounds[0] * final_x / (1 - final_x)**2
    dlog_q = passage_radius * (p_final_absolute + dlog_p)
    dlog_a = m2 * (dlog_q + passage_radius)
    dlog_inverse_a = dlog_a / a_star**2
    final_z_lower = (1 - p_final_variation)**2
    dlog_c = p_final_absolute * dlog_p / final_z_lower
    dlog_ac = dlog_inverse_a * c_bounds[0] + a_bounds[0] * dlog_c
    sharp_dlog_tau = (
        dlog_inverse_a * LOG_FINAL_UPPER
        + inverse_a_difference + dlog_ac
    )
    clock_contraction = ALPHA_BETA_UPPER * sharp_dlog_tau

    rho_squared = section_radius**2
    c_star = Fraction(7, 10) * rho_squared
    c_upper = ALPHA_BETA_UPPER * rho_squared
    exponential_remainder_factor = Fraction(64, 61)
    root_prefactor = c_upper * exponential_remainder_factor
    root_n2_ratio = root_prefactor * Fraction(1, 16**2) / passage_radius

    # Parameter/phase derivative generator for the logarithmic root.
    weighted_at_final: dict[tuple[int, int], Fraction] = {}
    for parameter_order in range(3):
        for log_order in range(3):
            weighted_at_final[(parameter_order, log_order)] = (
                normalized[log_order][0][parameter_order]
                * passage_radius * ONE_PLUS_LOG_FINAL_UPPER
            )
    weighted_at_final[(0, 0)] = sharp_tau
    weighted_at_final[(0, 1)] = sharp_dlog_tau

    alpha0 = ALPHA_BETA_UPPER
    alpha1 = PARAMETER_JET_UPPER
    alpha2 = PARAMETER_JET_UPPER
    residual_parameter_one = (
        alpha1 * weighted_at_final[(0, 0)]
        + alpha0 * weighted_at_final[(1, 0)]
    )
    residual_parameter_two = (
        alpha2 * weighted_at_final[(0, 0)]
        + 2 * alpha1 * weighted_at_final[(1, 0)]
        + alpha0 * weighted_at_final[(2, 0)]
    )
    residual_u_parameter = (
        alpha1 * weighted_at_final[(0, 1)]
        + alpha0 * weighted_at_final[(1, 1)]
    )
    residual_uu = alpha0 * weighted_at_final[(0, 2)]

    beta_inverse = (
        1 / ALPHA_BETA_LOWER,
        PARAMETER_JET_UPPER / ALPHA_BETA_LOWER**2,
        2 * PARAMETER_JET_UPPER**2 / ALPHA_BETA_LOWER**3
        + PARAMETER_JET_UPPER / ALPHA_BETA_LOWER**2,
    )
    alpha_jets = (
        ALPHA_BETA_UPPER, PARAMETER_JET_UPPER, PARAMETER_JET_UPPER)
    alpha_over_beta = _parameter_product_bounds(alpha_jets, beta_inverse)
    log_c_one = PARAMETER_JET_UPPER / ALPHA_BETA_LOWER
    log_c_two = (
        PARAMETER_JET_UPPER / ALPHA_BETA_LOWER
        + PARAMETER_JET_UPPER**2 / ALPHA_BETA_LOWER**2
    )
    u_source_one = max(
        alpha_over_beta[0], 8 * alpha_over_beta[1] + log_c_one)
    u_source_two = max(
        alpha_over_beta[1], 8 * alpha_over_beta[2] + log_c_two)
    inverse_implicit_margin = Fraction(16, 15)
    u1_polynomial = _poly_scale([
        u_source_one + residual_parameter_one,
        u_source_one,
    ], inverse_implicit_margin)
    u2_source = [
        u_source_two + residual_parameter_two,
        u_source_two,
    ]
    u2_polynomial = _poly_scale(
        _poly_add(
            u2_source,
            _poly_scale(u1_polynomial, 2 * residual_u_parameter),
            _poly_scale(
                _poly_multiply(u1_polynomial, u1_polynomial),
                residual_uu,
            ),
        ),
        inverse_implicit_margin,
    )

    # Exact residual-composition generator through two derivatives.
    residual_weighted: dict[tuple[int, int], Fraction] = {}
    for log_order in range(3):
        time = tuple(
            normalized[log_order][0][j] for j in range(3))
        phase = tuple(
            normalized[log_order][1][j] for j in range(3))
        residual_weighted[(0, log_order)] = (
            phase[0] + ALPHA_BETA_UPPER * time[0])
        residual_weighted[(1, log_order)] = (
            phase[1] + PARAMETER_JET_UPPER * time[0]
            + ALPHA_BETA_UPPER * time[1])
        residual_weighted[(2, log_order)] = (
            phase[2] + PARAMETER_JET_UPPER * time[0]
            + 2 * PARAMETER_JET_UPPER * time[1]
            + ALPHA_BETA_UPPER * time[2])

    value_poly = [residual_weighted[(0, 0)]]
    first_poly = _poly_add(
        [residual_weighted[(1, 0)]],
        _poly_scale(u1_polynomial, residual_weighted[(0, 1)]),
    )
    second_poly = _poly_add(
        [residual_weighted[(2, 0)]],
        _poly_scale(u1_polynomial, 2 * residual_weighted[(1, 1)]),
        _poly_scale(
            _poly_multiply(u1_polynomial, u1_polynomial),
            residual_weighted[(0, 2)],
        ),
        _poly_scale(u2_polynomial, residual_weighted[(0, 1)]),
    )
    residual_polynomials = (value_poly, first_poly, second_poly)
    residual_coefficient = (
        root_prefactor * 64 * NORMALIZED_TO_ORIGINAL_MAX[2]
        * max(sum(polynomial) for polynomial in residual_polynomials)
    )

    local_phase_time_difference = (
        a_difference * (a_bounds[0] * LOG_FINAL_UPPER + b_bounds[0])
        + ARGUMENT_ABSOLUTE_UPPER
    )

    checks = {
        "section_radius_matches_exact_sections": (
            section_radius == Fraction(5, 2**26)),
        "section_interval_contains_passage_collar": (
            passage_radius < section_interval),
        "action_radius_matches_zero_energy_contract": (
            action_radius == Fraction(25, 2**50)),
        "analytic_radius_is_frozen": (
            analytic_radius == Fraction(25, 2**57)),
        "passage_radius_is_frozen": (
            passage_radius == Fraction(25, 2**58)),
        "alpha_lower_positive_clock_gate": alpha_lower >= Fraction(7, 10),
        "alpha_upper_gate": alpha_upper <= ALPHA_BETA_UPPER,
        "beta_lower_positive_clock_gate": beta_lower >= ALPHA_BETA_LOWER,
        "beta_upper_gate": beta_upper <= ALPHA_BETA_UPPER,
        "alpha_first_parameter_jet_gate": alpha_d1 <= PARAMETER_JET_UPPER,
        "alpha_second_parameter_jet_gate": alpha_d2 <= PARAMETER_JET_UPPER,
        "beta_first_parameter_jet_gate": beta_d1 <= PARAMETER_JET_UPPER,
        "beta_second_parameter_jet_gate": beta_d2 <= PARAMETER_JET_UPPER,
        "complex_orientation_gate": a_star == Fraction(2, 3),
        "p_branch_variation_is_below_one_eighth": (
            p_variation < Fraction(1, 8)),
        "p_absolute_bound_is_below_five_fourths": (
            p_absolute < Fraction(5, 4)),
        "one_plus_p_squared_relative_variation_is_below_one_tenth": (
            z_relative_variation < Fraction(1, 10)),
        "both_argument_factors_have_positive_margin": branch_margin > 0,
        "frozen_argument_deck_stays_on_negative_real_p_branch": (
            real_slice_p_upper < 0),
        "argument_rational_pi_upper_is_below_four": (
            PI_RATIONAL_UPPER < ARGUMENT_ABSOLUTE_UPPER),
        "log_generator_first_four_weights": (
            [weights[index] for index in range(4)] == [1, 2, 6, 26]),
        "sharp_log_endpoint_exceeds_two_to_minus_fifty_eight": (
            passage_radius > Fraction(1, 2**LOG_FINAL_UPPER)),
        "sharp_weighted_log_monotonicity_domain": (
            passage_radius < Fraction(1, 4)),
        "sharp_time_remainder_is_below_one_sixteenth": (
            sharp_tau < Fraction(1, 16)),
        "clock_contraction_is_below_one_sixteenth": (
            clock_contraction < Fraction(1, 16)),
        "clock_constant_has_strict_positive_lower_bound": c_star > 0,
        "clock_n_two_root_is_strictly_inside_passage_collar": (
            root_n2_ratio == Fraction(12, 61)),
        "clock_exponent_per_winding_exceeds_four": Fraction(16, 3) > 4,
        "clock_residual_log_factor_dominates_proved_bound": 64 > 28,
        "local_phase_time_difference_is_below_five": (
            local_phase_time_difference < 5),
        "clock_root_derivative_generator_is_finite": (
            all(value >= 0 for value in u1_polynomial + u2_polynomial)),
        "finite_clock_residual_generator_is_positive": (
            residual_coefficient > 0),
    }

    normalized_table = {}
    for parameter_order in range(3):
        normalized_table[f"parameter_order_{parameter_order}"] = [
            {
                "time": rational(normalized[order][0][parameter_order]),
                "phase": rational(normalized[order][1][parameter_order]),
                "sum": rational(
                    normalized[order][0][parameter_order]
                    + normalized[order][1][parameter_order]),
            }
            for order in range(max_log_order + 1)
        ]

    return {
        "constants": {
            "q_analytic_radius": rational(q_radius),
            "weighted_analytic_radius": rational(analytic_radius),
            "weighted_passage_radius": rational(passage_radius),
            "section_radius_rho": rational(section_radius),
            "Q0": rational(q0),
            "Q1": rational(q1),
            "Q2": rational(q2),
            "P0": rational(p_bounds[0]),
            "P1": rational(p_bounds[1]),
            "P2": rational(p_bounds[2]),
            "p_branch_variation": rational(p_variation),
            "real_slice_p_upper": rational(real_slice_p_upper),
            "p_argument_branch_margin": rational(branch_margin),
            "one_plus_p_squared_relative_variation": rational(
                z_relative_variation),
            "M1": rational(m1),
            "M2": rational(m2),
            "M3": rational(m3),
            "H0": rational(h0),
            "H1": rational(h1),
            "H2": rational(h2),
            "sharp_tau_absolute_upper": rational(sharp_tau),
            "sharp_Dlog_tau_absolute_upper": rational(sharp_dlog_tau),
            "clock_contraction": rational(clock_contraction),
            "c_star": rational(c_star),
            "c_upper": rational(c_upper),
            "root_prefactor": rational(root_prefactor),
            "root_n2_over_passage_radius": rational(root_n2_ratio),
            "local_phase_time_difference_upper": rational(
                local_phase_time_difference),
            "local_winding_residence_comparison_upper": rational(2),
        },
        "checks": checks,
        "argument_deck": {
            "positive_action_limit": (
                "-pi+arctan(alpha_mu/beta_mu)"
            ),
            "negative_action_limit": "arctan(alpha_mu/beta_mu)",
            "continuation": "unique continuous positive-Kato lift",
            "real_slice_p_upper": rational(real_slice_p_upper),
            "absolute_argument_upper": rational(
                ARGUMENT_ABSOLUTE_UPPER),
            "turn_count_anchor": (
                "Delta_K=2*pi*n_K+vartheta, 0<=vartheta<2*pi"
            ),
        },
        "sharp_weighted_log_method": {
            "centered_factor_bound": "|F(nu)|<=K*|nu|",
            "endpoint_log_upper": LOG_FINAL_UPPER,
            "endpoint_one_plus_log_upper": ONE_PLUS_LOG_FINAL_UPPER,
            "monotonicity": (
                "x*|log(x)| and x*(1+|log(x)|) increase on collar"
            ),
            "not_a_uniform_log_bound": True,
        },
        "constant_parameter_bounds": {
            "t_K_normalized_parameter_order_0_1_2": [
                rational(value) for value in b_bounds],
            "b_K_normalized_parameter_order_0_1_2": [
                rational(value) for value in (
                    e_bounds[0] + ARGUMENT_ABSOLUTE_UPPER,
                    e_bounds[1] + argument_bounds[1],
                    e_bounds[2] + argument_bounds[2],
                )],
            "b_tilde_K_equals": "gamma_mu_sigma exactly",
            "c_K_equals": "alpha_mu * rho^2 exactly",
            "c_K_normalized_parameter_order_0_1_2": [
                {
                    "lower": rational(c_star),
                    "upper": rational(c_upper),
                },
                {"absolute_upper": rational(rho_squared / 100)},
                {"absolute_upper": rational(rho_squared / 100)},
            ],
        },
        "mixed_bounds_through_log_order_3": {
            "log_derivative_order": list(range(max_log_order + 1)),
            "lambda_m": [str(weights[index])
                         for index in range(max_log_order + 1)],
            "normalized_parameter_bounds": normalized_table,
            "original_parameter_bounds": _original_parameter_table(
                normalized, max_log_order),
        },
        "all_finite_log_order_generator": {
            "nu_star_m": rational(passage_radius),
            "lambda_formula": (
                "Lambda_m=sum_{j=0}^m binom(m,j) "
                "sum_{k=0}^j Stirling2(j,k) k!"
            ),
            "time_formula": (
                "(2*A_j*(Lambda_m+m*Lambda_(m-1))"
                "+2*B_j*Lambda_m)/R"
            ),
            "phase_formula": (
                "(2*W_j*(Lambda_m+m*Lambda_(m-1))"
                "+(2*E_j+Dhat_j)*Lambda_m)/R, "
                "Dhat=(D0,2*D1,2*D2)"
            ),
            "original_parameter_factor": (
                "25^gamma_r * 4^gamma_a2 * 5^gamma_epsilon"
            ),
            "witness_orders": all_order_witness,
        },
        "clock_root_generator": {
            "clock_equation": "beta_mu*T=2*pi*n+theta",
            "signs": ["+", "-"],
            "theta_interval": (
                "0<=theta<2*pi; estimates also hold at theta=2*pi"
            ),
            "uniform_winding_threshold": 2,
            "root_absolute_upper": (
                "root_prefactor * 16^(-n)"
            ),
            "exponential_reason": (
                "alpha/beta>=8/9, 2*pi>6, exp(16/3)>16"
            ),
            "u_first_derivative_polynomial_coefficients": [
                rational(value) for value in u1_polynomial],
            "u_second_derivative_polynomial_coefficients": [
                rational(value) for value in u2_polynomial],
            "root_first_derivative_bound": (
                "root_prefactor*16^(-n)*u1(n)"
            ),
            "root_second_derivative_bound": (
                "root_prefactor*16^(-n)*(u1(n)^2+u2(n))"
            ),
            "original_parameter_factor": (
                "25^gamma_r * 4^gamma_a2 * 5^gamma_epsilon"
            ),
        },
        "downstream_residual": {
            "b_tilde_K": "b_K-beta_mu*t_K=gamma_mu_sigma",
            "varrho_K": "rho_K(nu_n)-beta_mu*tau_K(nu_n)",
            "limiting_phase": "phi+theta+b_tilde_K",
            "finite_matching_row": (
                "psi-phi-theta-b_tilde_K-varrho_K=0"
            ),
            "original_parameter_C2_exponential_bound": (
                "C_varrho*(n+1)^3*16^(-n)"
            ),
            "C_varrho": rational(residual_coefficient),
            "log_weight_reason": (
                "1+|log|nu_n||<28*(n+1)<64*(n+1)"
            ),
        },
    }


def build_report(
        frame_path: Path = zero_energy.normal_form.scout.FRAME_PATH,
        normal_form_theory_path: Path = zero_energy.normal_form.THEORY_PATH,
        zero_energy_proof_path: Path = zero_energy.PROOF_PATH,
        exact_sections_proof_path: Path = exact_sections.PROOF_PATH,
        proof_path: Path = PROOF_PATH,
        ) -> dict[str, Any]:
    prerequisite = exact_sections.build_report(
        frame_path,
        normal_form_theory_path,
        zero_energy_proof_path,
        exact_sections_proof_path,
    )
    require(prerequisite.get("schema_version") == exact_sections.SCHEMA_VERSION,
            "exact-sections checker schema changed")
    require(prerequisite.get("scope") == exact_sections.SCOPE,
            "exact-sections checker scope changed")
    require(prerequisite.get("status") in {"PASS", "INCONCLUSIVE", "FAIL"},
            "exact-sections checker status is malformed")
    require(prerequisite.get("local_chart_status", {}).get(
            "V2.EXACT_CHART") == "OPEN",
            "exact-sections prerequisite changed the parent boundary")

    prerequisite_source_pass = (
        prerequisite.get("source_gate_status") == "PASS")
    prerequisite_local_pass = (
        prerequisite.get("status") == "PASS"
        and prerequisite.get("mathematical_status") ==
        "LOCAL_MATHEMATICAL_PASS"
        and prerequisite.get("proof_binding", {}).get("matched") is True
        and prerequisite.get("source_authentication", {}).get(
            "zero_energy_local_pass") is True
        and prerequisite.get("local_chart_status", {}).get(
            "V2.CHART.EXACT_SECTIONS") == "PASS"
    )

    certificate, frame_digest = (
        zero_energy.normal_form.scout.load_frame_certificate(frame_path))
    require(frame_digest == prerequisite["source_authentication"][
        "frame_certificate_sha256"],
        "weighted-passage and exact-sections frame digests differ")
    audit = weighted_audit_gates(certificate)
    require(audit["source_sha256"] == prerequisite[
        "source_authentication"]["exact_chart_audit_source_sha256"],
        "weighted and exact-sections audit sources differ")
    exact = compute_weighted_bounds(prerequisite, certificate)
    binding = proof_binding(proof_path)

    all_source_checks_pass = (
        prerequisite_source_pass
        and all(audit["required_checks"].values())
        and all(exact["checks"].values())
    )
    local_atom_pass = (
        all_source_checks_pass
        and prerequisite_local_pass
        and binding["matched"]
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "status": (
            "PASS" if local_atom_pass else
            "INCONCLUSIVE" if all_source_checks_pass else "FAIL"
        ),
        "source_gate_status": "PASS" if all_source_checks_pass else "FAIL",
        "mathematical_status": (
            "LOCAL_MATHEMATICAL_PASS" if local_atom_pass else
            "INCONCLUSIVE" if all_source_checks_pass else "FAIL"
        ),
        "mathematical_pass_scope": (
            "LOCAL_WEIGHTED_KATO_PASSAGE_ATOM" if local_atom_pass else "NONE"
        ),
        "claim_bearing": False,
        "release_eligible": False,
        "independent_replay": "1/2",
        "source_authentication": {
            "frame_certificate_sha256": frame_digest,
            "exact_sections_checker_schema": prerequisite["schema_version"],
            "exact_sections_status": prerequisite["status"],
            "exact_sections_local_pass": prerequisite_local_pass,
            "exact_sections_proof_sha256": prerequisite[
                "proof_binding"]["observed_sha256"],
            "zero_energy_proof_sha256": prerequisite[
                "source_authentication"]["zero_energy_proof_sha256"],
            "exact_chart_audit_source_sha256": audit["source_sha256"],
        },
        "proof_binding": binding,
        "exact_audit": audit,
        "exact_values": exact,
        "passage_laws": {
            "time": "-alpha_mu^(-1)*log|nu|+t_K+tau_K(nu)",
            "positive_Kato_phase": (
                "-(beta_mu/alpha_mu)*log|nu|+b_K+rho_K(nu)"
            ),
            "action": "nu_out=I2K=nu_in with the same sign",
        },
        "local_chart_status": {
            "V2.CHART.SYMPLECTIC_FRAME": "PASS",
            "V2.CHART.ANALYTIC_NORMAL_FORM": "PASS",
            "V2.CHART.ZERO_ENERGY": (
                "PASS" if prerequisite.get("source_authentication", {}).get(
                    "zero_energy_local_pass") is True else "OPEN"),
            "V2.CHART.EXACT_SECTIONS": (
                "PASS" if prerequisite_local_pass else "OPEN"),
            "V2.CHART.WEIGHTED_PASSAGE": (
                "PASS" if local_atom_pass else "OPEN"),
            "V2.CHART.PHYSICAL_SLIDES": "OPEN",
            "V2.CHART.OVERLAPS": "OPEN",
            "V2.EXACT_CHART": "OPEN",
        },
        "claim_boundary": {
            "local_child_only": True,
            "claim_bearing": False,
            "V2_EXACT_CHART": "OPEN",
            "radial_winding_residence_comparison": (
                "PASS" if local_atom_pass else "OPEN"),
            "physical_winding_residence_comparison": (
                "OPEN until V2.CHART.PHYSICAL_SLIDES"
            ),
            "excluded": [
                "physical event-face slides and their bounded flight times",
                "finite chart overlap atlas",
                "event atlas and later positive-end obligations",
                "temporal stability, Turing selection, and canard identification",
            ],
        },
    }


def emit(value: dict[str, Any]) -> None:
    sys.stdout.write(canonical_json(value))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame-certificate", type=Path,
                        default=zero_energy.normal_form.scout.FRAME_PATH)
    parser.add_argument("--normal-form-theory", type=Path,
                        default=zero_energy.normal_form.THEORY_PATH)
    parser.add_argument("--zero-energy-proof", type=Path,
                        default=zero_energy.PROOF_PATH)
    parser.add_argument("--exact-sections-proof", type=Path,
                        default=exact_sections.PROOF_PATH)
    parser.add_argument("--proof", type=Path, default=PROOF_PATH)
    arguments = parser.parse_args(argv)
    try:
        report = build_report(
            arguments.frame_certificate.resolve(),
            arguments.normal_form_theory.resolve(),
            arguments.zero_energy_proof.resolve(),
            arguments.exact_sections_proof.resolve(),
            arguments.proof.resolve(),
        )
    except (OSError, UnicodeError, WeightedPassageCheckError,
            exact_sections.ExactSectionsCheckError,
            zero_energy.ZeroEnergyCheckError,
            zero_energy.normal_form.SourceCheckError,
            zero_energy.normal_form.scout.ScoutInputError,
            subprocess.SubprocessError, KeyError, TypeError) as error:
        emit({
            "schema_version": SCHEMA_VERSION,
            "scope": SCOPE,
            "status": "INPUT_REJECTED",
            "mathematical_status": "INCONCLUSIVE",
            "error": str(error),
            "claim_bearing": False,
            "local_chart_status": {
                "V2.CHART.WEIGHTED_PASSAGE": "OPEN",
                "V2.EXACT_CHART": "OPEN",
            },
        })
        return 2
    emit(report)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
