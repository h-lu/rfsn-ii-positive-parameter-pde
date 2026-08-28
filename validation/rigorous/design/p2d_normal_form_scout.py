#!/usr/bin/env python3
"""Design-only scalar majorants for the P2d analytic normal form.

This scout consumes the archived, source-bound P2d symplectic-frame
certificate and evaluates the candidate gates in
``theory/EXPLICIT_GLOBAL_MOSER_MAJORANT.md``.  It deliberately does not run
interval arithmetic, prove that proposed amendment, freeze a configuration,
or discharge ``V2.CHART.ANALYTIC_NORMAL_FORM``.

The arithmetic which combines archived binary64 interval endpoints is exact:
each hexadecimal endpoint is converted to its exact rational value before
addition and multiplication; square roots are replaced by explicit dyadic
rational upper bounds.  That fact does not turn the proposed majorant theorem
into a proof.  A later formal probe must independently implement it with
outward-rounded arithmetic on the complete parameter cover.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
RIGOROUS = HERE.parent
REPOSITORY = RIGOROUS.parents[1]

FRAME_RELATIVE = (
    "validation/rigorous/results/"
    "vdp_bridge_v1_p2d_symplectic_frame.json"
)
FRAME_PATH = REPOSITORY / FRAME_RELATIVE
FRAME_SHA256 = (
    "5fabbcf01dc9b2f818f34525010332c76"
    "ff40190ea9a3d5ab166072397397847"
)
FRAME_SCHEMA = "rfsn-vdp-p2d-frame-certificate/1"
FRAME_CERTIFICATE_ID = "vdp-p2d-frame-c80e11ed5065"
FRAME_SOURCE_COMMIT = "c80e11ed5065c86161d6b3ad482a76db613e9983"
FRAME_SCOPE = "V2_P2D_SYMPLECTIC_FRAME_KERNEL"

SCHEMA_VERSION = "rfsn-vdp-p2d-normal-form-scout/1"
SYMMETRIC_D2_WEIGHTS = (1, 2, 2, 1, 2, 1)
EXPECTED_D1_ORDER = ("theta_r", "theta_a", "theta_epsilon")
EXPECTED_D2_ORDER = (
    "theta_r,theta_r",
    "theta_r,theta_a",
    "theta_r,theta_epsilon",
    "theta_a,theta_a",
    "theta_a,theta_epsilon",
    "theta_epsilon,theta_epsilon",
)


class ScoutInputError(ValueError):
    """The archived frame input is absent, altered, or semantically wrong."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ScoutInputError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def rational_record(value: Fraction) -> dict[str, str]:
    with localcontext() as context:
        context.prec = 20
        decimal = Decimal(value.numerator) / Decimal(value.denominator)
    numerator = str(value.numerator)
    denominator = str(value.denominator)
    record = {"decimal": format(decimal, ".16g")}
    # Exact tail-series fractions quickly acquire thousands of digits.  The
    # formula and all exact inputs are already in the report, so suppressing
    # those expansions keeps the JSON useful to a human reader.
    if len(numerator) + len(denominator) <= 120:
        record.update({"numerator": numerator, "denominator": denominator})
    else:
        record.update({
            "exact_fraction_omitted": "recompute-from-authenticated-inputs",
            "numerator_digits": str(len(numerator.lstrip("-"))),
            "denominator_digits": str(len(denominator)),
        })
    return record


def binary64_fraction(text: Any, label: str) -> Fraction:
    require(isinstance(text, str), f"{label} is not a hexadecimal string")
    try:
        value = float.fromhex(text)
    except ValueError as error:
        raise ScoutInputError(f"{label} is not valid hexadecimal: {error}") \
            from error
    require(math.isfinite(value), f"{label} is not finite")
    numerator, denominator = value.as_integer_ratio()
    return Fraction(numerator, denominator)


def interval_endpoints(interval: Any, label: str) -> tuple[Fraction, Fraction]:
    require(isinstance(interval, dict), f"{label} is not an interval object")
    require(interval.get("endpoint_format") == "IEEE754_BINARY64_HEX",
            f"{label} does not use hexadecimal binary64 endpoints")
    lower = binary64_fraction(interval.get("lower_hex"), f"{label}.lower")
    upper = binary64_fraction(interval.get("upper_hex"), f"{label}.upper")
    require(lower <= upper, f"{label} has reversed endpoints")
    return lower, upper


def interval_abs_upper(interval: Any, label: str) -> Fraction:
    lower, upper = interval_endpoints(interval, label)
    return max(abs(lower), abs(upper))


def authenticate_frame_certificate(
        certificate: Any, observed_sha256: str) -> dict[str, Any]:
    require(observed_sha256 == FRAME_SHA256,
            "archived P2d frame certificate SHA-256 changed")
    require(isinstance(certificate, dict),
            "archived P2d frame certificate is not a JSON object")
    require(certificate.get("schema_version") == FRAME_SCHEMA,
            "archived P2d frame schema changed")
    require(certificate.get("certificate_id") == FRAME_CERTIFICATE_ID,
            "archived P2d frame certificate id changed")
    require(certificate.get("scope") == FRAME_SCOPE,
            "archived P2d frame scope changed")

    revision = certificate.get("source_revision")
    require(isinstance(revision, dict), "frame source revision is missing")
    require(revision.get("repository") ==
            "h-lu/rfsn-ii-positive-parameter-pde",
            "frame source repository changed")
    require(revision.get("commit") == FRAME_SOURCE_COMMIT,
            "frame source commit changed")
    require(revision.get("repository_dirty") is False,
            "frame certificate was not built from a clean source revision")

    chart_status = certificate.get("chart_status")
    require(isinstance(chart_status, dict), "frame chart status is missing")
    require(chart_status.get("V2.CHART.SYMPLECTIC_FRAME") == "PASS",
            "V2.CHART.SYMPLECTIC_FRAME prerequisite is not PASS")
    require(chart_status.get("V2.CHART.ANALYTIC_NORMAL_FORM") == "OPEN",
            "archived frame certificate changed the normal-form boundary")
    require(chart_status.get("V2.EXACT_CHART") == "OPEN",
            "archived frame certificate changed the parent boundary")
    require(certificate.get("integrity_status") == "PASS",
            "archived frame integrity status is not PASS")
    require(certificate.get("mathematical_status") == "PASS",
            "archived frame mathematical status is not PASS")
    require(certificate.get("final_status") == "INCONCLUSIVE",
            "archived frame aggregate status changed")
    require(certificate.get("claim_bearing") is False,
            "archived frame unexpectedly became claim-bearing")

    raw = certificate.get("raw_probe")
    require(isinstance(raw, dict), "archived frame raw probe is missing")
    require(raw.get("schema_version") ==
            "rfsn-vdp-p2d-symplectic-frame-probe/1",
            "archived frame raw-probe schema changed")
    require(raw.get("status") == "PASS" and
            raw.get("mathematical_status") == "PASS" and
            raw.get("structure_status") == "PASS",
            "archived frame raw probe is not PASS")
    binding = raw.get("input_binding", {})
    require(tuple(binding.get("normalized_D1_order", ())) ==
            EXPECTED_D1_ORDER,
            "normalized first-parameter order changed")
    require(tuple(binding.get("normalized_D2_symmetric_order", ())) ==
            EXPECTED_D2_ORDER,
            "normalized second-parameter order changed")
    return raw


def load_frame_certificate(path: Path = FRAME_PATH) -> tuple[dict[str, Any], str]:
    try:
        source = path.read_bytes()
    except OSError as error:
        raise ScoutInputError(f"cannot read archived frame certificate: {error}") \
            from error
    digest = sha256_bytes(source)
    try:
        certificate = json.loads(source)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ScoutInputError(f"cannot parse archived frame certificate: {error}") \
            from error
    authenticate_frame_certificate(certificate, digest)
    return certificate, digest


def normalized_jet_components(jet: Any, label: str) -> dict[str, Any]:
    require(isinstance(jet, dict), f"{label} jet is missing")
    normalized = jet.get("normalized")
    require(isinstance(normalized, dict), f"{label}.normalized is missing")
    d1_raw = normalized.get("D1")
    d2_raw = normalized.get("D2_symmetric")
    require(isinstance(d1_raw, list) and len(d1_raw) == 3,
            f"{label} normalized D1 is incomplete")
    require(isinstance(d2_raw, list) and len(d2_raw) == 6,
            f"{label} normalized D2 is incomplete")
    lower, upper = interval_endpoints(
        normalized.get("value"), f"{label}.value")
    return {
        "lower": lower,
        "upper": upper,
        "value_abs": max(abs(lower), abs(upper)),
        "D1_abs": [
            interval_abs_upper(item, f"{label}.D1[{index}]")
            for index, item in enumerate(d1_raw)
        ],
        "D2_abs": [
            interval_abs_upper(item, f"{label}.D2_symmetric[{index}]")
            for index, item in enumerate(d2_raw)
        ],
    }


def matrix_entry_jet(
        matrix: Any, row: int, column: int, label: str) -> dict[str, Any]:
    require(isinstance(matrix, dict), "L_jets is missing")
    require(matrix.get("rows") == 4 and matrix.get("columns") == 4,
            "L_jets is not a 4 by 4 matrix")
    entries = matrix.get("entries")
    require(isinstance(entries, list) and len(entries) == 4,
            "L_jets entries are incomplete")
    require(isinstance(entries[row], list) and len(entries[row]) == 4,
            f"L row {row} is incomplete")
    return normalized_jet_components(entries[row][column], label)


def rational_sqrt_upper(value: Fraction, bits: int = 96) -> Fraction:
    """Return a dyadic rational provably no smaller than sqrt(value)."""

    require(value >= 0, "cannot take the square root of a negative bound")
    require(bits > 0, "square-root precision must be positive")
    if value == 0:
        return Fraction()
    scale = 1 << bits
    scaled_numerator = value.numerator * scale * scale
    target_ceiling = (
        scaled_numerator + value.denominator - 1) // value.denominator
    root = math.isqrt(target_ceiling)
    if root * root < target_ceiling:
        root += 1
    result = Fraction(root, scale)
    require(result * result >= value,
            "internal rational square-root enclosure failed")
    return result


def complex_u_coefficient_jet(matrix: Any) -> dict[str, Any]:
    """Equation (5) coefficient norm from p=L[0,0], q=-L[0,1]."""

    p = matrix_entry_jet(matrix, 0, 0, "p=L[0,0]")
    q_source = matrix_entry_jet(matrix, 0, 1, "q=-L[0,1]")
    q = dict(q_source)
    q["lower"], q["upper"] = -q_source["upper"], -q_source["lower"]

    def coefficient_bound(p_bound: Fraction, q_bound: Fraction) -> Fraction:
        # There are four complex coefficients of modulus
        # sqrt((p^2+q^2)/2).
        return 4 * rational_sqrt_upper(
            (p_bound * p_bound + q_bound * q_bound) / 2)

    value = coefficient_bound(p["value_abs"], q["value_abs"])
    d1 = [
        coefficient_bound(p_bound, q_bound)
        for p_bound, q_bound in zip(p["D1_abs"], q["D1_abs"])
    ]
    d2 = [
        coefficient_bound(p_bound, q_bound)
        for p_bound, q_bound in zip(p["D2_abs"], q["D2_abs"])
    ]
    ordered_d2 = sum(
        (weight * bound for weight, bound in
         zip(SYMMETRIC_D2_WEIGHTS, d2)), Fraction())
    j2 = value + sum(d1, Fraction()) + ordered_d2 / 2
    return {"p": p, "q": q, "value": value, "D1": d1, "D2": d2,
            "ordered_D2": ordered_d2, "J2": j2}


def j2_bound(value: Fraction, d1: list[Fraction],
             d2: list[Fraction]) -> Fraction:
    ordered_d2 = sum(
        (weight * bound for weight, bound in
         zip(SYMMETRIC_D2_WEIGHTS, d2)), Fraction())
    return value + sum(d1, Fraction()) + ordered_d2 / 2


def model_coefficient_jets() -> dict[str, Any]:
    """Bounds for gamma=A and D in equations (6)--(7), in theta variables."""

    r = Fraction(2, 25)
    a = Fraction(1, 4)
    dr = Fraction(1, 25)
    da = Fraction(1, 4)
    # Rational bounds valid on epsilon in [4/5,6/5].
    sqrt_e = Fraction(11, 10)
    ds = Fraction(9, 80)
    d2s = Fraction(729, 51200)

    gamma_value = 1 + sqrt_e * r**3 * a
    gamma_d1 = [
        sqrt_e * 3 * r**2 * dr * a,
        sqrt_e * r**3 * da,
        ds * r**3 * a,
    ]
    gamma_d2 = [
        sqrt_e * 6 * r * dr**2 * a,
        sqrt_e * 3 * r**2 * dr * da,
        ds * 3 * r**2 * dr * a,
        Fraction(),
        ds * r**3 * da,
        d2s * r**3 * a,
    ]

    D_value = sqrt_e * r**2 / 12
    D_d1 = [
        sqrt_e * 2 * r * dr / 12,
        Fraction(),
        ds * r**2 / 12,
    ]
    D_d2 = [
        sqrt_e * 2 * dr**2 / 12,
        Fraction(),
        ds * 2 * r * dr / 12,
        Fraction(),
        Fraction(),
        d2s * r**2 / 12,
    ]
    return {
        "gamma": {
            "value": gamma_value, "D1": gamma_d1, "D2": gamma_d2,
            "J2": j2_bound(gamma_value, gamma_d1, gamma_d2),
        },
        "D": {
            "value": D_value, "D1": D_d1, "D2": D_d2,
            "J2": j2_bound(D_value, D_d1, D_d2),
        },
    }


def component_jet_record(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "value_abs_upper": rational_record(value["value_abs"]),
        "value_lower": rational_record(value["lower"]),
        "D1_abs_upper": [rational_record(item) for item in value["D1_abs"]],
        "D2_symmetric_abs_upper": [
            rational_record(item) for item in value["D2_abs"]],
    }


def model_jet_record(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "value_abs_upper": rational_record(value["value"]),
        "D1_abs_upper": [rational_record(item) for item in value["D1"]],
        "D2_symmetric_abs_upper": [
            rational_record(item) for item in value["D2"]],
        "J2_upper": rational_record(value["J2"]),
    }


def divisor_jet_majorant(alpha: dict[str, Any],
                         beta: dict[str, Any]) -> dict[str, Any]:
    """Evaluate equation (17) term by term."""

    m = min(alpha["lower"], beta["lower"])
    require(m > 0, "the archived divisor lower bound is not positive")
    M = [a + b for a, b in zip(alpha["D1_abs"], beta["D1_abs"])]
    N = [a + b for a, b in zip(alpha["D2_abs"], beta["D2_abs"])]
    diagonal = ((0, 0), (1, 3), (2, 5))
    mixed = ((0, 1, 1), (0, 2, 2), (1, 2, 4))
    value_term = 1 / m
    first_terms = [item / m**2 for item in M]
    diagonal_terms = [
        (2 * M[index]**2 / m**3 + N[d2_index] / m**2) / 2
        for index, d2_index in diagonal
    ]
    mixed_terms = [
        2 * M[i] * M[j] / m**3 + N[d2_index] / m**2
        for i, j, d2_index in mixed
    ]
    kappa = (
        value_term + sum(first_terms, Fraction())
        + sum(diagonal_terms, Fraction())
        + sum(mixed_terms, Fraction()))
    return {
        "m": m, "M": M, "N": N, "value_term": value_term,
        "first_terms": first_terms, "diagonal_terms": diagonal_terms,
        "mixed_terms": mixed_terms, "kappa_J": kappa,
    }


def build_report(path: Path = FRAME_PATH) -> dict[str, Any]:
    """Build a report only from certificate bytes authenticated by the loader."""

    certificate, digest = load_frame_certificate(path)
    raw = certificate["raw_probe"]
    scalars = raw.get("scalar_jets")
    require(isinstance(scalars, dict), "frame scalar jets are missing")
    alpha = normalized_jet_components(scalars.get("alpha"), "alpha")
    beta = normalized_jet_components(scalars.get("beta"), "beta")
    U = complex_u_coefficient_jet(raw.get("L_jets"))
    coefficients = model_coefficient_jets()
    divisor = divisor_jet_majorant(alpha, beta)

    gamma_J = coefficients["gamma"]["J2"]
    D_J = coefficients["D"]["J2"]
    U_J = U["J2"]
    cubic_J = gamma_J * U_J**3 / 3
    quartic_J = D_J * U_J**4
    E = cubic_J
    h_in = quartic_J / E
    kappa_J = divisor["kappa_J"]

    input_gates = {
        "E_le_4": E <= 4,
        "h_in_le_1_over_64": h_in <= Fraction(1, 64),
        "kappa_J_le_5_over_3": kappa_J <= Fraction(5, 3),
    }

    Bbar = Fraction(2**20)
    Gbar = Fraction(8)
    epsilon_nf = Fraction(1, 2**22)
    theta = Bbar * epsilon_nf
    equation_38_lhs = Fraction(128, 5) * Gbar * epsilon_nf
    S0_upper = Fraction(512, 9) * epsilon_nf**2
    B_z = (
        Fraction(64, 25) * Gbar * epsilon_nf
        * 2 * (theta**2 - 3 * theta + 3) / (1 - theta)**3)
    A_z = 1 / (1 - B_z)
    forward_displacement = A_z * S0_upper
    physical_preimage_radius = Fraction(2, 7) * epsilon_nf + S0_upper
    domain_gates = {
        "equation_38_all_orders_domain": equation_38_lhs < 1,
        "equation_39_total_displacement": S0_upper < epsilon_nf / 8,
        "equation_39b_forward_lipschitz": B_z < Fraction(1, 16384),
        "equation_40b_forward_displacement": (
            forward_displacement < epsilon_nf / 8),
        "equation_44a_physical_preimage_in_source": (
            physical_preimage_radius < 3 * epsilon_nf / 8),
    }

    prefix_order = 2
    inverse_coordinate_tail = (
        Fraction(8, 5) * Gbar * epsilon_nf**2 * theta**prefix_order
        * ((prefix_order + 3) - (prefix_order + 2) * theta)
        / (1 - theta)**2)
    forward_coordinate_tail = A_z * inverse_coordinate_tail

    return {
        "schema_version": SCHEMA_VERSION,
        "status": "DESIGN_CANDIDATE_ONLY",
        "numerical_status": (
            "EXACT_RATIONAL_DESIGN_EVALUATION_ALIGNED_WITH_"
            "EXPLICIT_GLOBAL_MOSER_MAJORANT"
        ),
        "mathematical_status": "INCONCLUSIVE",
        "input_authentication": {
            "path": FRAME_RELATIVE,
            "sha256": digest,
            "schema_version": FRAME_SCHEMA,
            "certificate_id": FRAME_CERTIFICATE_ID,
            "source_commit": FRAME_SOURCE_COMMIT,
            "integrity_status": certificate["integrity_status"],
            "mathematical_status": certificate["mathematical_status"],
            "frame_atom": "PASS",
            "frame_final_status": certificate["final_status"],
            "frame_claim_bearing": certificate["claim_bearing"],
        },
        "theory_alignment": {
            "path": "theory/EXPLICIT_GLOBAL_MOSER_MAJORANT.md",
            "complex_coordinate_equation": 2,
            "J2_norm_equation": 11,
            "divisor_jet_equation": 17,
            "input_gate_equations": [18, 19],
            "fixed_schedule_equation": 35,
            "domain_gate_equations": [38, 39, "39b", "40b", "44a"],
            "forward_lipschitz_equations": ["39a", "39b", "39c"],
            "forward_displacement_equation": "40b",
            "coordinate_tail_equations": [47, "47a"],
        },
        "coordinate_convention": {
            "real_state_order": ["x1", "x2", "y1", "y2"],
            "complex_roles": "z_from_x__w_from_y",
            "poisson_coordinate_bracket": "{z_j,w_k}=-delta_jk",
            "U_coefficient_formula": (
                "four coefficients, each of modulus "
                "sqrt((p^2+q^2)/2), p=L[0,0], q=-L[0,1]"
            ),
        },
        "archived_normalized_jet_bounds": {
            "parameter_D1_order": list(EXPECTED_D1_ORDER),
            "parameter_D2_symmetric_order": list(EXPECTED_D2_ORDER),
            "alpha": component_jet_record(alpha),
            "beta": component_jet_record(beta),
            "p_equals_L_0_0": component_jet_record(U["p"]),
            "q_equals_minus_L_0_1": component_jet_record(U["q"]),
            "complex_U_coefficient_norm": {
                "sqrt_upper_dyadic_bits": 96,
                "value_upper": rational_record(U["value"]),
                "D1_upper": [rational_record(item) for item in U["D1"]],
                "D2_symmetric_upper": [
                    rational_record(item) for item in U["D2"]],
                "ordered_D2_upper": rational_record(U["ordered_D2"]),
                "J2_upper": rational_record(U_J),
            },
        },
        "model_coefficient_bounds": {
            "formulas": {
                "gamma": "1+sqrt(epsilon)*r^3*a2",
                "D": "sqrt(epsilon)*r^2/12",
                "nonlinear_part": "-gamma*U^3/3+D*U^4",
            },
            "gamma": model_jet_record(coefficients["gamma"]),
            "D": model_jet_record(coefficients["D"]),
        },
        "candidate_majorants": {
            "J2_definition": (
                "value+sum(D1)+one_half*full_ordered_sum(D2)"
            ),
            "gamma_J": rational_record(gamma_J),
            "D_J": rational_record(D_J),
            "U_J": rational_record(U_J),
            "cubic_J_formula": "gamma_J*U_J^3/3",
            "cubic_J": rational_record(cubic_J),
            "quartic_J_formula": "D_J*U_J^4",
            "quartic_J": rational_record(quartic_J),
            "E": rational_record(E),
            "h_in_formula": "quartic_J/E",
            "h_in": rational_record(h_in),
            "divisor": {
                "m": rational_record(divisor["m"]),
                "M_i": [rational_record(item) for item in divisor["M"]],
                "N_ij_symmetric": [
                    rational_record(item) for item in divisor["N"]],
                "equation_17_terms": {
                    "inverse_m": rational_record(divisor["value_term"]),
                    "first": [rational_record(item) for item in
                              divisor["first_terms"]],
                    "diagonal_second": [rational_record(item) for item in
                                         divisor["diagonal_terms"]],
                    "mixed_second": [rational_record(item) for item in
                                      divisor["mixed_terms"]],
                },
            },
            "kappa_J_formula": "theory equation (17), term by term",
            "kappa_J": rational_record(kappa_J),
        },
        "candidate_gates": {
            "thresholds": {
                "E_upper": rational_record(Fraction(4)),
                "h_in_upper": rational_record(Fraction(1, 64)),
                "kappa_J_upper": rational_record(Fraction(5, 3)),
            },
            "input": input_gates,
            "all_input_gates_pass": all(input_gates.values()),
        },
        "fixed_theory_schedule": {
            "Bbar": rational_record(Bbar),
            "Gbar": rational_record(Gbar),
            "epsilon_nf": rational_record(epsilon_nf),
            "theta": rational_record(theta),
            "domain_radii": {
                "D_infinity": rational_record(5 * epsilon_nf / 8),
                "D_inverse": rational_record(epsilon_nf / 2),
                "D_source": rational_record(3 * epsilon_nf / 8),
                "D_physical": rational_record(epsilon_nf / 8),
            },
            "equation_38": {
                "lhs_128_over_5_Gbar_epsilon": rational_record(
                    equation_38_lhs),
                "rhs": rational_record(Fraction(1)),
            },
            "equation_39": {
                "S0_upper_512_over_9_epsilon_squared": rational_record(
                    S0_upper),
                "epsilon_over_8": rational_record(epsilon_nf / 8),
            },
            "equations_39a_to_39c": {
                "B_z_formula": (
                    "(64/25)*Gbar*epsilon_nf*"
                    "2*(theta^2-3*theta+3)/(1-theta)^3"
                ),
                "B_z": rational_record(B_z),
                "B_z_upper_gate": rational_record(Fraction(1, 16384)),
                "A_z_formula": "1/(1-B_z)",
                "A_z": rational_record(A_z),
                "A_z_theory_upper": rational_record(
                    Fraction(16384, 16383)),
            },
            "equation_40b": {
                "forward_displacement_A_z_times_S0": rational_record(
                    forward_displacement),
                "epsilon_over_8": rational_record(epsilon_nf / 8),
            },
            "equation_44a": {
                "physical_preimage_radius_2epsilon_over_7_plus_S0": (
                    rational_record(physical_preimage_radius)
                ),
                "source_radius_3epsilon_over_8": rational_record(
                    3 * epsilon_nf / 8
                ),
            },
            "domain_gates": domain_gates,
            "all_domain_gates_pass": all(domain_gates.values()),
            "coordinate_tails_q2": {
                "prefix_order": prefix_order,
                "inverse_raw_equation_47": rational_record(
                    inverse_coordinate_tail),
                "forward_equation_47a": rational_record(
                    forward_coordinate_tail),
                "forward_amplification": "A_z",
            },
        },
        "claim_boundary": {
            "design_output_is_certificate_evidence": False,
            "outward_rounded_formal_probe_run": False,
            "proposed_local_amendment_proved": False,
            "finite_Lie_prefix_constructed": False,
            "exact_symplectic_limit_constructed": False,
            "parameter_two_jet_limit_proved": False,
            "claim_bearing": False,
            "closed_obligations": [],
            "V2_CHART_ANALYTIC_NORMAL_FORM": "OPEN",
            "V2_EXACT_CHART": "OPEN",
        },
        "next_formal_step": (
            "Prove the proposed parameter-jet majorant, freeze the three "
            "input gates and fixed schedule, and independently validate "
            "equations (17)--(19) and (38)--(58) with an outward-rounded "
            "source-bound checker."
        ),
    }


def emit(payload: dict[str, Any], pretty: bool) -> None:
    if pretty:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame-certificate", type=Path, default=FRAME_PATH)
    parser.add_argument("--pretty", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        report = build_report(arguments.frame_certificate.resolve())
    except (OSError, ScoutInputError, KeyError, TypeError) as error:
        emit({
            "schema_version": SCHEMA_VERSION,
            "status": "INPUT_REJECTED",
            "mathematical_status": "INCONCLUSIVE",
            "error": str(error),
            "claim_boundary": {
                "claim_bearing": False,
                "closed_obligations": [],
                "V2_CHART_ANALYTIC_NORMAL_FORM": "OPEN",
                "V2_EXACT_CHART": "OPEN",
            },
        }, arguments.pretty)
        return 2
    emit(report, arguments.pretty)
    return 0


if __name__ == "__main__":
    sys.exit(main())
