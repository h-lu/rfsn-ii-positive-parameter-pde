#!/usr/bin/env python3
"""Check the nonlinear P2d exact radial sections with exact rational gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
sys.path.insert(0, str(HERE))

import check_p2d_zero_energy as zero_energy  # noqa: E402


SCHEMA_VERSION = "rfsn-vdp-p2d-exact-sections-source-check/1"
SCOPE = "V2_CHART_EXACT_SECTIONS_LOCAL_RATIONAL_AND_IDENTITY_GATES"
PROOF_CONTRACT = "rfsn-vdp-p2d-explicit-exact-radial-sections/1"
PROOF_RELATIVE = "theory/EXPLICIT_EXACT_RADIAL_SECTIONS.md"
PROOF_PATH = REPOSITORY / PROOF_RELATIVE
PROOF_SHA256 = (
    "df3ff1e0c23871ffc050183e941c63a9"
    "d93d57179eecb38efa3db8dd161a6d55"
)

AUDIT_RELATIVE = "validation/rigorous/audit_p2d_exact_chart.py"
AUDIT_PATH = REPOSITORY / AUDIT_RELATIVE
AUDIT_SHA256 = (
    "050cfd00d49412e9404c17b0eed680bf"
    "17e88798bfce48d0e1ec0920770c52d1"
)
AUDIT_SCHEMA = "rfsn-vdp-p2d-exact-chart-audit/2"
AUDIT_METHOD = "exact-symbolic-identities-no-sampling-no-file-inputs"
REQUIRED_AUDIT_CHECKS = (
    "actual_completion_L_is_exact_symplectic",
    "actual_linear_symplectic_frame_preserves_symmetric_primitive",
    "FK_dictionary_T_preserves_I1",
    "FK_dictionary_T_sends_I2F_to_I2K_without_action_flip",
    "FK_dictionary_C0_sends_phase_phi_to_minus_phi",
    "incoming_scout_stable_radius_is_rho",
    "incoming_scout_I1_is_tau",
    "incoming_scout_I2K_is_nu",
    "incoming_scout_primitive_is_minus_nu_dphi_minus_half_dq",
    "incoming_scout_pullback_is_dphi_wedge_dnu",
    "outgoing_scout_I1_is_tau",
    "outgoing_scout_I2K_is_nu",
    "outgoing_scout_expanding_radius_is_rho",
    "outgoing_scout_primitive_is_minus_nu_dphi_plus_half_dq",
    "outgoing_scout_pullback_is_dphi_wedge_dnu",
    "physical_primitive_gauge_is_exact",
    "quadratic_hamiltonian_uses_I2K",
    "reverser_maps_expanding_to_stable",
)

SECTION_RADIUS = Fraction(5, 2**26)


class ExactSectionsCheckError(ValueError):
    """A required proof, source binding, or exact gate is malformed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ExactSectionsCheckError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def rational(value: Fraction) -> dict[str, str]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
    }


def as_fraction(record: Any, label: str) -> Fraction:
    require(isinstance(record, dict), f"{label} is not a rational record")
    try:
        return Fraction(int(record["numerator"]), int(record["denominator"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        raise ExactSectionsCheckError(
            f"{label} is not a valid rational record: {error}") from error


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def proof_binding(path: Path) -> dict[str, Any]:
    source = path.read_bytes()
    digest = sha256_bytes(source)
    try:
        text = source.decode("utf-8")
    except UnicodeError as error:
        raise ExactSectionsCheckError(
            f"exact-sections proof is not UTF-8: {error}") from error
    contract_present = PROOF_CONTRACT in text
    return {
        "path": PROOF_RELATIVE,
        "expected_sha256": PROOF_SHA256,
        "observed_sha256": digest,
        "proof_contract": PROOF_CONTRACT,
        "proof_contract_present": contract_present,
        "matched": digest == PROOF_SHA256 and contract_present,
    }


def exact_audit_gates(certificate: dict[str, Any]) -> dict[str, Any]:
    source = AUDIT_PATH.read_bytes()
    observed_source_sha256 = sha256_bytes(source)
    require(observed_source_sha256 == AUDIT_SHA256,
            "exact-chart audit source SHA-256 changed")
    try:
        audit = certificate["exact_audit"]
        report = audit["report"]
        checks = report["checks"]
        execution = audit["execution"]
    except (KeyError, TypeError) as error:
        raise ExactSectionsCheckError(
            f"archived exact-chart audit is incomplete: {error}") from error
    require(audit.get("path") == AUDIT_RELATIVE,
            "archived exact-chart audit path changed")
    require(audit.get("sha256") == AUDIT_SHA256,
            "archived exact-chart audit source binding changed")
    source_bindings = certificate.get("source_bindings")
    require(isinstance(source_bindings, list),
            "frame source bindings are missing")
    matching_bindings = [
        item for item in source_bindings
        if isinstance(item, dict) and item.get("path") == AUDIT_RELATIVE
    ]
    require(matching_bindings == [{
        "path": AUDIT_RELATIVE,
        "role": "p2d-frame-input",
        "sha256": AUDIT_SHA256,
    }], "exact-chart audit source binding is not unique and exact")
    require(report.get("schema_version") == AUDIT_SCHEMA,
            "archived exact-chart audit schema changed")
    require(report.get("method") == AUDIT_METHOD,
            "archived exact-chart audit method changed")
    require(report.get("status") == "PASS",
            "archived exact-chart audit is not PASS")
    require(isinstance(checks, dict),
            "archived exact-chart checks are not a dictionary")
    require(len(checks) == 59 and all(value is True for value in checks.values()),
            "archived exact-chart audit is not the complete 59-check PASS")
    require(isinstance(execution, dict),
            "archived exact-chart execution record is missing")
    stdout = execution.get("stdout")
    require(isinstance(stdout, str),
            "archived exact-chart stdout is missing")
    stdout_bytes = stdout.encode("utf-8")
    require(execution.get("exit_code") == 0,
            "archived exact-chart audit exit code is not zero")
    require(execution.get("stderr_sha256") == sha256_bytes(b""),
            "archived exact-chart audit stderr is not empty")
    require(execution.get("stdout_sha256") == sha256_bytes(stdout_bytes),
            "archived exact-chart stdout digest changed")
    require(stdout == canonical_json(report),
            "archived exact-chart stdout is not canonical report JSON")
    required = {name: checks.get(name) is True for name in REQUIRED_AUDIT_CHECKS}
    require(all(required.values()),
            "a required exact radial-section identity is not PASS")
    return {
        "path": AUDIT_RELATIVE,
        "source_sha256": observed_source_sha256,
        "schema_version": AUDIT_SCHEMA,
        "method": AUDIT_METHOD,
        "archived_check_count": len(checks),
        "all_archived_checks_pass": True,
        "required_checks": required,
    }


def compute_section_bounds(zero_report: dict[str, Any]) -> dict[str, Any]:
    try:
        constants = zero_report["exact_values"]["constants"]
        q0 = as_fraction(constants["Q0"], "Q0")
        nu_star = as_fraction(constants["nu_star"], "nu_star")
        source_action_radius = as_fraction(
            constants["exact_source_action_radius"],
            "exact_source_action_radius",
        )
        orientation_lower = as_fraction(
            constants["orientation_lower"], "orientation_lower")
    except (KeyError, TypeError) as error:
        raise ExactSectionsCheckError(
            f"zero-energy constants are incomplete: {error}") from error

    source_radius = zero_energy.EPSILON_NF * zero_energy.R_SOURCE
    complementary_numerator = q0 + nu_star
    complementary_radius = complementary_numerator / SECTION_RADIUS
    checks = {
        "section_radius_is_frozen_positive": (
            SECTION_RADIUS == Fraction(5, 2**26)),
        "section_interval_is_frozen_two_sided_nonzero": (
            nu_star == Fraction(25, 2**54)),
        "source_radius_matches_exact_chart": (
            source_radius**2 == source_action_radius),
        "fixed_radial_factor_lies_strictly_in_source_chart": (
            SECTION_RADIUS < source_radius),
        "complementary_factor_lies_strictly_in_source_chart": (
            complementary_radius < source_radius),
        "incoming_expanding_radius_is_strictly_below_outgoing_radius": (
            complementary_numerator < SECTION_RADIUS**2),
        "complete_passage_tube_lies_in_exact_source_chart": (
            SECTION_RADIUS < source_radius),
        "real_time_orientation_is_strictly_positive": (
            orientation_lower > Fraction(2, 3)),
    }
    return {
        "constants": {
            "section_radius_rho": rational(SECTION_RADIUS),
            "exact_source_state_radius": rational(source_radius),
            "section_nu_star": rational(nu_star),
            "zero_energy_Q0": rational(q0),
            "Q0_plus_nu_star": rational(complementary_numerator),
            "complementary_radial_factor_upper": rational(
                complementary_radius),
            "rho_over_source_radius": rational(
                SECTION_RADIUS / source_radius),
            "positive_flight_ratio": rational(
                complementary_numerator / SECTION_RADIUS**2),
            "source_inclusion_ratio": rational(
                complementary_radius / source_radius),
            "complete_passage_state_radius_buffer": rational(
                source_radius - SECTION_RADIUS),
            "orientation_lower": rational(orientation_lower),
        },
        "checks": checks,
    }


def build_report(
        frame_path: Path = zero_energy.normal_form.scout.FRAME_PATH,
        normal_form_theory_path: Path = zero_energy.normal_form.THEORY_PATH,
        zero_energy_proof_path: Path = zero_energy.PROOF_PATH,
        proof_path: Path = PROOF_PATH,
        ) -> dict[str, Any]:
    zero_report = zero_energy.build_report(
        frame_path, normal_form_theory_path, zero_energy_proof_path)
    require(zero_report.get("schema_version") == zero_energy.SCHEMA_VERSION,
            "zero-energy checker schema changed")
    require(zero_report.get("scope") == zero_energy.SCOPE,
            "zero-energy checker scope changed")
    require(zero_report.get("status") in {"PASS", "INCONCLUSIVE", "FAIL"},
            "zero-energy checker status is malformed")
    require(zero_report.get("local_chart_status", {}).get(
            "V2.EXACT_CHART") == "OPEN",
            "zero-energy prerequisite changed the parent boundary")
    zero_source_pass = zero_report.get("source_gate_status") == "PASS"
    zero_local_pass = (
        zero_report.get("status") == "PASS"
        and zero_report.get("mathematical_status") ==
        "LOCAL_MATHEMATICAL_PASS"
        and zero_report.get("proof_binding", {}).get("matched") is True
        and
        zero_report.get("local_chart_status", {}).get(
            "V2.CHART.ZERO_ENERGY") == "PASS"
    )
    certificate, frame_digest = (
        zero_energy.normal_form.scout.load_frame_certificate(frame_path))
    require(frame_digest == zero_report["source_authentication"][
        "frame_certificate_sha256"],
        "exact-sections and zero-energy frame digests differ")
    audit = exact_audit_gates(certificate)
    bounds = compute_section_bounds(zero_report)
    binding = proof_binding(proof_path)

    all_source_checks_pass = (
        zero_source_pass
        and all(audit["required_checks"].values())
        and all(bounds["checks"].values())
    )
    local_atom_pass = (
        all_source_checks_pass and zero_local_pass and binding["matched"])
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
            "LOCAL_EXACT_RADIAL_SECTIONS_ATOM" if local_atom_pass else "NONE"
        ),
        "claim_bearing": False,
        "release_eligible": False,
        "independent_replay": "1/2",
        "source_authentication": {
            "frame_certificate_sha256": frame_digest,
            "zero_energy_checker_schema": zero_report["schema_version"],
            "zero_energy_status": zero_report["status"],
            "zero_energy_local_pass": zero_local_pass,
            "zero_energy_proof_sha256": zero_report[
                "proof_binding"]["observed_sha256"],
            "exact_chart_audit_source_sha256": audit["source_sha256"],
        },
        "proof_binding": binding,
        "exact_audit": audit,
        "exact_values": bounds,
        "section_identities": {
            "incoming_actions": "I1=q_mu(nu), I2K=nu",
            "outgoing_actions": "I1=q_mu(nu), I2K=nu",
            "incoming_form": "pullback(omega0)=dphi wedge dnu",
            "outgoing_form": "pullback(omega0)=dpsi wedge dnu",
            "incoming_gauge": "G_in=f_mu o s_in-q_mu/2",
            "outgoing_gauge": "G_out=f_mu o s_out+q_mu/2",
            "passage_action": "nu_out=I2K=nu_in exactly",
        },
        "local_chart_status": {
            "V2.CHART.SYMPLECTIC_FRAME": "PASS",
            "V2.CHART.ANALYTIC_NORMAL_FORM": "PASS",
            "V2.CHART.ZERO_ENERGY": "PASS" if zero_local_pass else "OPEN",
            "V2.CHART.EXACT_SECTIONS": "PASS" if local_atom_pass else "OPEN",
            "V2.CHART.WEIGHTED_PASSAGE": "OPEN",
            "V2.CHART.PHYSICAL_SLIDES": "OPEN",
            "V2.CHART.OVERLAPS": "OPEN",
            "V2.EXACT_CHART": "OPEN",
        },
        "claim_boundary": {
            "local_child_only": True,
            "claim_bearing": False,
            "V2_EXACT_CHART": "OPEN",
            "excluded": [
                "weighted logarithmic time and Kato phase bounds",
                "physical event-face slides",
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
    parser.add_argument("--proof", type=Path, default=PROOF_PATH)
    arguments = parser.parse_args(argv)
    try:
        report = build_report(
            arguments.frame_certificate.resolve(),
            arguments.normal_form_theory.resolve(),
            arguments.zero_energy_proof.resolve(),
            arguments.proof.resolve(),
        )
    except (OSError, UnicodeError, ExactSectionsCheckError,
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
                "V2.CHART.EXACT_SECTIONS": "OPEN",
                "V2.EXACT_CHART": "OPEN",
            },
        })
        return 2
    emit(report)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
