#!/usr/bin/env python3
"""Check the P2d nonlinear zero-energy fiber with exact rational gates.

The checker reuses the authenticated P2d frame and analytic-normal-form
source report.  It adds no new floating-point or CAPD lane: every new gate is
an exact rational consequence of the already proved all-orders majorant.  A
local pass is not claim-bearing and does not close ``V2.EXACT_CHART``.
"""

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

import check_p2d_normal_form_source_bounds as normal_form  # noqa: E402


SCHEMA_VERSION = "rfsn-vdp-p2d-zero-energy-source-check/1"
SCOPE = "V2_CHART_ZERO_ENERGY_LOCAL_RATIONAL_GATES"
PROOF_CONTRACT = "rfsn-vdp-p2d-explicit-zero-energy-fiber/1"
PROOF_RELATIVE = "theory/EXPLICIT_ZERO_ENERGY_FIBER.md"
PROOF_PATH = REPOSITORY / PROOF_RELATIVE
PROOF_SHA256 = (
    "ac1cac62e56acf59e2ae2bfb79ae1073"
    "0756673bf86775d50c8196d47c2c3342"
)

EPSILON_NF = Fraction(1, 2**22)
R_INFINITY = Fraction(5, 8)
R_SOURCE = Fraction(3, 8)
ACTION_RADIUS = (EPSILON_NF * R_INFINITY) ** 2
SOURCE_ACTION_RADIUS = (EPSILON_NF * R_SOURCE) ** 2
M_BAR = Fraction(1, 3 * 2**62)
ALPHA_LOWER_GATE = Fraction(7, 10)
BETA_UPPER_GATE = Fraction(18, 25)
PARAMETER_DERIVATIVE_GATE = Fraction(1, 100)
A_STAR = Fraction(2, 3)

NORMALIZED_AXES = ("theta_r", "theta_a", "theta_epsilon")
ORIGINAL_SCALES = {"r": 25, "a2": 4, "epsilon": 5}
SECOND_PARAMETER_PAIRS = (
    ("r", "r"),
    ("r", "a2"),
    ("r", "epsilon"),
    ("a2", "a2"),
    ("a2", "epsilon"),
    ("epsilon", "epsilon"),
)


class ZeroEnergyCheckError(ValueError):
    """A required source, proof binding, or exact gate is malformed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ZeroEnergyCheckError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def rational(value: Fraction) -> dict[str, str]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
    }


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def proof_binding(path: Path) -> dict[str, Any]:
    source = path.read_bytes()
    digest = sha256_bytes(source)
    try:
        text = source.decode("utf-8")
    except UnicodeError as error:
        raise ZeroEnergyCheckError(
            f"zero-energy proof is not UTF-8: {error}") from error
    contract_present = PROOF_CONTRACT in text
    return {
        "path": PROOF_RELATIVE,
        "expected_sha256": PROOF_SHA256,
        "observed_sha256": digest,
        "proof_contract": PROOF_CONTRACT,
        "proof_contract_present": contract_present,
        "matched": digest == PROOF_SHA256 and contract_present,
    }


def _jet_hulls(certificate: dict[str, Any], name: str) -> dict[str, Fraction]:
    try:
        normalized = certificate["raw_probe"]["scalar_jets"][name][
            "normalized"
        ]
    except (KeyError, TypeError) as error:
        raise ZeroEnergyCheckError(f"missing {name} normalized jet: {error}") \
            from error
    lower, upper = normal_form.scout.interval_endpoints(
        normalized["value"], f"{name}.value")
    d1 = max(
        normal_form.scout.interval_abs_upper(item, f"{name}.D1[{index}]")
        for index, item in enumerate(normalized["D1"])
    )
    d2 = max(
        normal_form.scout.interval_abs_upper(item, f"{name}.D2[{index}]")
        for index, item in enumerate(normalized["D2_symmetric"])
    )
    return {
        "lower": lower,
        "upper": upper,
        "absolute_upper": max(abs(lower), abs(upper)),
        "D1_absolute_upper": d1,
        "D2_absolute_upper": d2,
    }


def frame_gates(certificate: dict[str, Any]) -> dict[str, Any]:
    alpha = _jet_hulls(certificate, "alpha")
    beta = _jet_hulls(certificate, "beta")
    checks = {
        "alpha_uniform_lower_bound": alpha["lower"] >= ALPHA_LOWER_GATE,
        "beta_uniform_absolute_upper_bound": (
            beta["absolute_upper"] <= BETA_UPPER_GATE),
        "alpha_normalized_D1_bound": (
            alpha["D1_absolute_upper"] <= PARAMETER_DERIVATIVE_GATE),
        "alpha_normalized_D2_bound": (
            alpha["D2_absolute_upper"] <= PARAMETER_DERIVATIVE_GATE),
        "beta_normalized_D1_bound": (
            beta["D1_absolute_upper"] <= PARAMETER_DERIVATIVE_GATE),
        "beta_normalized_D2_bound": (
            beta["D2_absolute_upper"] <= PARAMETER_DERIVATIVE_GATE),
    }
    return {
        "alpha": {key: rational(value) for key, value in alpha.items()},
        "beta": {key: rational(value) for key, value in beta.items()},
        "gates": {
            "alpha_lower": rational(ALPHA_LOWER_GATE),
            "beta_absolute_upper": rational(BETA_UPPER_GATE),
            "normalized_parameter_D1_D2_absolute_upper": rational(
                PARAMETER_DERIVATIVE_GATE),
        },
        "checks": checks,
    }


def _jet_bound_table(
        q_bounds: tuple[Fraction, Fraction, Fraction],
        cauchy_gap: Fraction,
        max_nu_order: int = 3,
        ) -> dict[str, Any]:
    normalized: dict[str, list[dict[str, str]]] = {}
    for parameter_order, q_bound in enumerate(q_bounds):
        normalized[f"parameter_order_{parameter_order}"] = [
            rational(Fraction(math.factorial(order)) * q_bound /
                     cauchy_gap**order)
            for order in range(max_nu_order + 1)
        ]

    original: dict[str, list[dict[str, str]]] = {
        "value": normalized["parameter_order_0"],
    }
    for axis, scale in ORIGINAL_SCALES.items():
        original[f"D_{axis}"] = [
            rational(scale * Fraction(math.factorial(order)) * q_bounds[1] /
                     cauchy_gap**order)
            for order in range(max_nu_order + 1)
        ]
    for first, second in SECOND_PARAMETER_PAIRS:
        scale = ORIGINAL_SCALES[first] * ORIGINAL_SCALES[second]
        original[f"D_{first}_{second}"] = [
            rational(scale * Fraction(math.factorial(order)) * q_bounds[2] /
                     cauchy_gap**order)
            for order in range(max_nu_order + 1)
        ]
    return {
        "nu_derivative_order": list(range(max_nu_order + 1)),
        "normalized_parameter_bounds": normalized,
        "original_parameter_bounds": original,
    }


def compute_exact_bounds(
        m_bar: Fraction = M_BAR,
        action_radius: Fraction = ACTION_RADIUS,
        alpha_lower: Fraction = ALPHA_LOWER_GATE,
        beta_upper: Fraction = BETA_UPPER_GATE,
        parameter_derivative_upper: Fraction = PARAMETER_DERIVATIVE_GATE,
        a_star: Fraction = A_STAR,
        ) -> dict[str, Any]:
    require(m_bar > 0, "the remainder majorant must be positive")
    require(action_radius > 0, "the action radius must be positive")
    require(alpha_lower > 0, "the alpha lower bound must be positive")
    require(beta_upper >= 0, "the beta upper bound must be nonnegative")
    require(parameter_derivative_upper >= 0,
            "the parameter derivative bound must be nonnegative")
    require(a_star > 0, "the orientation target must be positive")

    inner_radius = action_radius / 2
    action_gap = action_radius - inner_radius
    first_state_remainder = m_bar / action_gap
    second_state_remainder = 2 * m_bar / action_gap**2
    orientation_lower = alpha_lower - first_state_remainder

    nu_outer = action_radius / 8
    nu_star = action_radius / 16
    cauchy_gap = nu_outer - nu_star
    center_ratio = beta_upper / alpha_lower
    krawczyk_radius = 2 * m_bar / alpha_lower
    contraction = first_state_remainder / alpha_lower
    krawczyk_image_radius = (
        m_bar / alpha_lower + contraction * krawczyk_radius)
    fiber_action_radius = center_ratio * nu_outer + krawczyk_radius
    source_lift_action_radius = (fiber_action_radius + nu_outer) / 2

    q0 = fiber_action_radius
    q1 = (
        parameter_derivative_upper * (q0 + nu_outer) + m_bar
    ) / a_star
    q2 = (
        parameter_derivative_upper * (q0 + nu_outer)
        + 2 * m_bar
        + second_state_remainder * q1**2
        + 2 * (parameter_derivative_upper + first_state_remainder) * q1
    ) / a_star

    checks = {
        "action_radius_matches_analytic_majorant_domain": (
            action_radius == Fraction(25, 2**50)),
        "exact_source_action_radius_matches_chart_domain": (
            SOURCE_ACTION_RADIUS == Fraction(9, 2**50)),
        "majorant_matches_normal_form_envelope": (
            m_bar == Fraction(1, 3 * 2**62)),
        "inner_action_domain_is_nonempty": inner_radius > 0,
        "common_two_sided_outer_interval_is_nonempty": nu_outer > 0,
        "common_two_sided_final_interval_is_nonempty": nu_star > 0,
        "cauchy_gap_is_positive": cauchy_gap > 0,
        "fiber_box_lies_in_inner_action_domain": (
            fiber_action_radius < inner_radius),
        "fiber_box_lifts_strictly_to_exact_source_chart": (
            source_lift_action_radius < SOURCE_ACTION_RADIUS),
        "remainder_I_derivative_gate": (
            first_state_remainder == Fraction(1, 153600)),
        "orientation_has_strict_a_star_margin": orientation_lower > a_star,
        "krawczyk_contraction_is_strict": contraction < 1,
        "krawczyk_image_is_strictly_interior": (
            krawczyk_image_radius < krawczyk_radius),
        "parameter_Q0_is_finite_positive": q0 > 0,
        "parameter_Q1_is_finite_positive": q1 > 0,
        "parameter_Q2_is_finite_positive": q2 > 0,
    }

    return {
        "constants": {
            "epsilon_nf": rational(EPSILON_NF),
            "R_infinity": rational(R_INFINITY),
            "R_source": rational(R_SOURCE),
            "action_radius_s": rational(action_radius),
            "exact_source_action_radius": rational(SOURCE_ACTION_RADIUS),
            "inner_action_radius_d": rational(inner_radius),
            "action_cauchy_gap": rational(action_gap),
            "normal_form_remainder_Mbar": rational(m_bar),
            "remainder_I_derivative_L": rational(first_state_remainder),
            "remainder_II_derivative_L2": rational(second_state_remainder),
            "alpha_lower": rational(alpha_lower),
            "beta_absolute_upper": rational(beta_upper),
            "parameter_derivative_upper": rational(
                parameter_derivative_upper),
            "a_star": rational(a_star),
            "orientation_lower": rational(orientation_lower),
            "nu_outer": rational(nu_outer),
            "nu_star": rational(nu_star),
            "nu_cauchy_gap": rational(cauchy_gap),
            "linear_center_ratio": rational(center_ratio),
            "krawczyk_radius_W": rational(krawczyk_radius),
            "krawczyk_contraction": rational(contraction),
            "krawczyk_image_radius": rational(krawczyk_image_radius),
            "fiber_action_radius": rational(fiber_action_radius),
            "source_lift_action_radius": rational(
                source_lift_action_radius),
            "Q0": rational(q0),
            "Q1": rational(q1),
            "Q2": rational(q2),
        },
        "checks": checks,
        "mixed_jet_bounds_through_nu_order_3": _jet_bound_table(
            (q0, q1, q2), cauchy_gap),
        "all_finite_nu_order_generator": {
            "normalized_formula": (
                "|D_theta^gamma D_nu^m q| <= "
                "m! * Q_|gamma| / (nu_outer-nu_star)^m, "
                "|gamma|<=2, m>=0"
            ),
            "original_parameter_factor": (
                "25^gamma_r * 4^gamma_a2 * 5^gamma_epsilon"
            ),
            "Q_by_parameter_order": {
                "0": rational(q0), "1": rational(q1), "2": rational(q2),
            },
            "nu_outer": rational(nu_outer),
            "nu_star": rational(nu_star),
            "cauchy_gap": rational(cauchy_gap),
        },
    }


def build_report(
        frame_path: Path = normal_form.scout.FRAME_PATH,
        normal_form_theory_path: Path = normal_form.THEORY_PATH,
        proof_path: Path = PROOF_PATH,
        ) -> dict[str, Any]:
    # Deliberately run this authenticated prerequisite here.  Accepting an
    # injected summary would let a library caller forge the low-order gate.
    low_order = normal_form.run_low_order_audit()
    prerequisite = normal_form.build_report(
        frame_path, normal_form_theory_path, low_order_result=low_order)
    require(prerequisite.get("status") == "PASS",
            "analytic normal-form source gates are not PASS")
    require(
        prerequisite.get("local_chart_status", {}).get(
            "V2.CHART.ANALYTIC_NORMAL_FORM") == "PASS",
        "analytic normal-form mathematical prerequisite is not PASS",
    )

    certificate, frame_digest = normal_form.scout.load_frame_certificate(
        frame_path)
    hulls = frame_gates(certificate)
    exact = compute_exact_bounds()
    binding = proof_binding(proof_path)

    all_source_checks_pass = all(hulls["checks"].values()) and all(
        exact["checks"].values())
    local_atom_pass = all_source_checks_pass and binding["matched"]

    analytic_binding = prerequisite["proof_bindings"]["analytic_majorant"]
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
            "LOCAL_ZERO_ENERGY_FIBER_ATOM" if local_atom_pass else
            "NONE"
        ),
        "claim_bearing": False,
        "release_eligible": False,
        "independent_replay": "1/2",
        "source_authentication": {
            "frame_certificate_sha256": frame_digest,
            "normal_form_checker_schema": prerequisite["schema_version"],
            "normal_form_status": prerequisite["mathematical_status"],
            "normal_form_proof_sha256": analytic_binding[
                "observed_sha256"],
            "low_order_exact_audit_status": low_order["status"],
            "low_order_exact_check_count": low_order["check_count"],
        },
        "proof_binding": binding,
        "frame_hulls": hulls,
        "exact_values": exact,
        "local_chart_status": {
            "V2.CHART.SYMPLECTIC_FRAME": "PASS",
            "V2.CHART.ANALYTIC_NORMAL_FORM": "PASS",
            "V2.CHART.ZERO_ENERGY": "PASS" if local_atom_pass else "OPEN",
            "V2.CHART.EXACT_SECTIONS": "OPEN",
            "V2.CHART.WEIGHTED_PASSAGE": "OPEN",
            "V2.CHART.PHYSICAL_SLIDES": "OPEN",
            "V2.CHART.OVERLAPS": "OPEN",
            "V2.EXACT_CHART": "OPEN",
        },
        "proved_fiber": {
            "equation": "h_mu(q_mu(nu),nu)=0",
            "two_sided_interval": "|nu|<=25/2^54",
            "origin": "q_mu(0)=0",
            "origin_slope": "q_mu'(0)=-beta_mu/alpha_mu",
            "orientation": "partial_I1 h_mu(q_mu(nu),nu)>2/3",
            "regularity": (
                "analytic in nu; normalized-parameter C2 with an explicit "
                "all-finite-nu-order Cauchy generator"
            ),
        },
        "claim_boundary": {
            "local_child_only": True,
            "claim_bearing": False,
            "V2_EXACT_CHART": "OPEN",
            "excluded": [
                "exact nonlinear radial sections",
                "weighted time and Kato phase passage",
                "physical slides and overlap atlas",
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
                        default=normal_form.scout.FRAME_PATH)
    parser.add_argument("--normal-form-theory", type=Path,
                        default=normal_form.THEORY_PATH)
    parser.add_argument("--proof", type=Path, default=PROOF_PATH)
    arguments = parser.parse_args(argv)
    try:
        report = build_report(
            arguments.frame_certificate.resolve(),
            arguments.normal_form_theory.resolve(),
            arguments.proof.resolve(),
        )
    except (OSError, UnicodeError, ZeroEnergyCheckError,
            normal_form.SourceCheckError,
            normal_form.scout.ScoutInputError, KeyError, TypeError,
            subprocess.SubprocessError) as error:
        emit({
            "schema_version": SCHEMA_VERSION,
            "scope": SCOPE,
            "status": "INPUT_REJECTED",
            "mathematical_status": "INCONCLUSIVE",
            "error": str(error),
            "claim_bearing": False,
            "local_chart_status": {
                "V2.CHART.ZERO_ENERGY": "OPEN",
                "V2.EXACT_CHART": "OPEN",
            },
        })
        return 2
    emit(report)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
