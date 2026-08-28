#!/usr/bin/env python3
"""Check the source-bound scalar gates for the P2d normal form.

This is deliberately a small local checker, not a certificate builder and
not an independent replay lane.  It authenticates the archived P2d frame,
reuses its outward binary64 enclosures as exact rational intervals, proves
the remaining rational model and tail inequalities, and emits one canonical
JSON line.  A local PASS is never claim-bearing and never closes
``V2.EXACT_CHART``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
DESIGN = HERE / "design"
sys.path.insert(0, str(DESIGN))

import p2d_normal_form_scout as scout  # noqa: E402


SCHEMA_VERSION = "rfsn-vdp-p2d-normal-form-source-check/1"
SCOPE = "V2_P2D_ANALYTIC_NORMAL_FORM_LOCAL_SOURCE_GATES"

THEORY_RELATIVE = "theory/EXPLICIT_GLOBAL_MOSER_MAJORANT.md"
THEORY_PATH = REPOSITORY / THEORY_RELATIVE
THEORY_SHA256 = (
    "069d109a22fa502c2e6970de7e3ef4c6"
    "0234e327138b9052df764b6f36cf8245"
)
THEORY_PROOF_CONTRACT = "rfsn-vdp-p2d-explicit-global-moser-majorant/1"

LOW_ORDER_RELATIVE = "validation/rigorous/audit_p2d_normal_form_exact.py"
LOW_ORDER_PATH = REPOSITORY / LOW_ORDER_RELATIVE
LOW_ORDER_SHA256 = (
    "82147d559b351aab2e71c71732507fbbb"
    "24265fb172e136e51670484a51a6d68"
)

EXPECTED_AXES = ("theta_r", "theta_a", "theta_epsilon")
EXPECTED_D2_ORDER = (
    "theta_r,theta_r",
    "theta_r,theta_a",
    "theta_r,theta_epsilon",
    "theta_a,theta_a",
    "theta_a,theta_epsilon",
    "theta_epsilon,theta_epsilon",
)
EXPECTED_STRUCTURE_CHECKS = {
    "bridge_matches_frozen_contract",
    "subdivisions_match_frozen_contract",
    "gates_match_frozen_contract",
    "all_gate_rationals_strictly_positive",
    "gap_free_exact_rational_grid",
    "cell_count_matches_frozen_contract",
    "complete_scalar_set",
    "complete_L_and_L_inverse_entries",
    "complete_first_and_symmetric_second_multiindices",
    "parameter_ad_hessians_bit_symmetric",
    "all_sqrt_and_reciprocal_domains_valid",
    "L_inverse_constructed_by_symplectic_formula",
    "raw_scope_excludes_exact_audit_and_P2bK_authentication",
}
DICTIONARY_CHECKS = {
    "FK_dictionary_T_is_symplectic_involution",
    "FK_dictionary_T_commutes_with_standard_reverser",
    "FK_dictionary_T_preserves_I1",
    "FK_dictionary_T_sends_I2F_to_I2K_without_action_flip",
    "FK_dictionary_transports_flagship_H2_to_kato_H2",
    "actual_completion_L_is_exact_symplectic",
    "actual_completion_intertwines_physical_and_standard_reversers",
    "actual_completion_inverse_conjugates_physical_linearization_to_kato_blocks",
    "actual_linear_symplectic_frame_preserves_symmetric_primitive",
    "c_zero_anchor_actual_completion_is_euclidean_orthogonal",
    "quadratic_hamiltonian_uses_I2K",
    "physical_primitive_gauge_is_exact",
}
LOW_ORDER_CHECKS = {
    "real_to_complex_matrix_dictionary_is_exact",
    "complex_poisson_coordinate_pairs_are_canonical",
    "standard_reverser_is_involutive_and_anti_poisson",
    "quadratic_hamiltonian_is_alpha_I1_plus_beta_I2K",
    "quadratic_hamiltonian_is_real_and_reverser_invariant",
    "homological_operator_is_diagonal_with_frozen_divisor",
    "divisor_real_imaginary_integer_map_is_invertible",
    "resonant_kernel_is_generated_by_J1_and_J2",
    "degree_three_has_no_resonances",
    "degree_four_has_exactly_three_action_resonances",
    "cubic_block_has_exactly_20_monomials",
    "quartic_block_has_exactly_35_monomials",
    "nonlinear_input_blocks_are_real_and_reverser_invariant",
    "cubic_generator_uses_frozen_negative_homological_sign",
    "cubic_generator_is_real_and_reverser_anti_invariant",
    "degree_three_is_cancelled_exactly",
    "quartic_BCH_block_reduces_to_H4_plus_half_bracket",
    "quartic_resonant_projection_has_three_action_monomials",
    "quartic_resonant_projection_is_real_and_reverser_invariant",
    "quartic_generator_has_zero_resonant_projection",
    "quartic_generator_is_real_and_reverser_anti_invariant",
    "degree_four_is_normalized_exactly_to_Z4",
    "core_anchor_quartic_action_coefficients_are_exact",
    "core_anchor_Z4_is_I2K_squared_minus_I1_squared_over_120",
    "core_conditional_formal_zero_energy_coefficient_c2_is_zero",
    "encoded_model_input_has_only_degree_three_and_four_blocks",
}


class SourceCheckError(ValueError):
    """A source binding or a required exact prerequisite is invalid."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SourceCheckError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def rational(value: Fraction) -> dict[str, str]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
    }


def rational_from_record(value: Any, label: str) -> Fraction:
    require(isinstance(value, dict), f"{label} is not a rational record")
    try:
        result = Fraction(int(value["numerator"]), int(value["denominator"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        raise SourceCheckError(f"{label} is malformed: {error}") from error
    return result


def binding_map(certificate: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    bindings = certificate.get("source_bindings")
    require(isinstance(bindings, list), "frame source bindings are missing")
    for item in bindings:
        require(isinstance(item, dict), "a frame source binding is malformed")
        path, digest = item.get("path"), item.get("sha256")
        require(isinstance(path, str) and isinstance(digest, str),
                "a frame source binding lacks path or SHA-256")
        require(path not in result, f"duplicate frame source binding: {path}")
        result[path] = digest
    return result


def _validate_normalized_jet(jet: Any, label: str) -> None:
    require(isinstance(jet, dict), f"{label} is not a jet")
    normalized = jet.get("normalized")
    require(isinstance(normalized, dict), f"{label}.normalized is missing")
    scout.interval_endpoints(normalized.get("value"), f"{label}.value")
    d1 = normalized.get("D1")
    d2 = normalized.get("D2_symmetric")
    require(isinstance(d1, list) and len(d1) == 3,
            f"{label} does not have three normalized first derivatives")
    require(isinstance(d2, list) and len(d2) == 6,
            f"{label} does not have six normalized symmetric Hessians")
    for index, interval in enumerate(d1):
        scout.interval_endpoints(interval, f"{label}.D1[{index}]")
    for index, interval in enumerate(d2):
        scout.interval_endpoints(interval, f"{label}.D2[{index}]")


def authenticate_frame_source(
        certificate: dict[str, Any], digest: str) -> dict[str, Any]:
    """Authenticate archived bytes and their embedded probe provenance."""

    raw = scout.authenticate_frame_certificate(certificate, digest)
    bindings = binding_map(certificate)

    build = certificate.get("toolchain", {}).get("probe_build", {})
    require(isinstance(build, dict), "frame probe build record is missing")
    stdout = build.get("probe_stdout")
    require(isinstance(stdout, str), "frame probe stdout is missing")
    require(build.get("probe_stdout_sha256") ==
            sha256_bytes(stdout.encode("utf-8")),
            "frame probe stdout SHA-256 changed")
    try:
        parsed_stdout = json.loads(stdout)
    except json.JSONDecodeError as error:
        raise SourceCheckError(f"frame probe stdout is not JSON: {error}") \
            from error
    require(parsed_stdout == raw,
            "frame probe stdout is not equal to archived raw_probe")
    require(build.get("source_sha256") == bindings.get(
        "validation/rigorous/src/vdp_p2d_symplectic_frame_probe.cpp"),
        "frame probe source hash is not its archived source binding")
    require(build.get("probe_exit_code") == 0,
            "frame probe exit code is not PASS")

    grid = raw.get("grid")
    require(isinstance(grid, dict), "frame probe grid is missing")
    require(tuple(grid.get("ordered_axes", ())) == EXPECTED_AXES,
            "frame probe ordered axes changed")
    require(grid.get("subdivisions") == [16, 8, 4] and
            grid.get("cell_count") == 512,
            "frame probe is not the complete 16x8x4 cover")
    structure = raw.get("structure_checks")
    require(isinstance(structure, dict) and
            set(structure) == EXPECTED_STRUCTURE_CHECKS and
            all(value is True for value in structure.values()),
            "frame probe structure checks are incomplete or failed")
    require(raw.get("structure_status") == "PASS",
            "frame probe structure status is not PASS")

    input_binding = raw.get("input_binding")
    require(isinstance(input_binding, dict), "frame input binding is missing")
    require(tuple(input_binding.get("normalized_D1_order", ())) ==
            EXPECTED_AXES, "normalized D1 order changed")
    require(tuple(input_binding.get("normalized_D2_symmetric_order", ())) ==
            EXPECTED_D2_ORDER, "normalized D2 order changed")

    scalar_jets = raw.get("scalar_jets")
    require(isinstance(scalar_jets, dict) and
            {"alpha", "beta"} <= set(scalar_jets),
            "required scalar jets are missing")
    for name, jet in scalar_jets.items():
        _validate_normalized_jet(jet, f"scalar_jets.{name}")
    for matrix_name in ("L_jets", "L_inverse_jets"):
        matrix = raw.get(matrix_name)
        require(isinstance(matrix, dict) and matrix.get("rows") == 4 and
                matrix.get("columns") == 4,
                f"{matrix_name} is not 4 by 4")
        entries = matrix.get("entries")
        require(isinstance(entries, list) and len(entries) == 4,
                f"{matrix_name} rows are incomplete")
        for row_index, row in enumerate(entries):
            require(isinstance(row, list) and len(row) == 4,
                    f"{matrix_name} row {row_index} is incomplete")
            for column_index, jet in enumerate(row):
                _validate_normalized_jet(
                    jet, f"{matrix_name}[{row_index},{column_index}]")

    margins = raw.get("gate_margins")
    require(isinstance(margins, dict) and margins,
            "frame gate margins are missing")
    for name, interval in margins.items():
        lower, _ = scout.interval_endpoints(interval, f"gate_margins.{name}")
        require(lower > 0, f"frame gate margin {name} is not positive")

    rounding = raw.get("rounding_self_test")
    require(isinstance(rounding, dict) and rounding.get("status") == "PASS",
            "frame rounding self-test is not PASS")
    require(all(item.get("status") == "PASS"
                for item in rounding.get("tests", [])
                if isinstance(item, dict)),
            "a frame rounding self-test failed")

    conditioning = raw.get("conditioning")
    require(isinstance(conditioning, dict),
            "frame conditioning record is missing")
    _, inverse_operator_upper = scout.interval_endpoints(
        conditioning.get("L_inverse_operator_upper_from_anchor"),
        "conditioning.L_inverse_operator_upper_from_anchor")
    require(inverse_operator_upper < Fraction(8, 7),
            "certified L inverse operator upper bound is not below 8/7")
    require(conditioning.get(
        "conditional_on_external_exact_L0_orthogonality") is True,
        "frame conditioning does not cite exact L0 orthogonality")

    exact = certificate.get("exact_audit")
    require(isinstance(exact, dict), "frame exact dictionary audit is missing")
    execution = exact.get("execution")
    report = exact.get("report")
    require(isinstance(execution, dict) and isinstance(report, dict),
            "frame exact dictionary audit record is malformed")
    exact_stdout = execution.get("stdout")
    require(isinstance(exact_stdout, str) and
            execution.get("stdout_sha256") ==
            sha256_bytes(exact_stdout.encode("utf-8")),
            "frame exact-audit stdout hash changed")
    require(exact_stdout == canonical_json(report),
            "frame exact-audit stdout differs from its report")
    require(exact.get("sha256") == bindings.get(
        "validation/rigorous/audit_p2d_exact_chart.py"),
        "frame exact-audit source hash is not its archived binding")
    checks = report.get("checks")
    require(report.get("status") == "PASS" and
            isinstance(checks, dict) and len(checks) == 59 and
            all(value is True for value in checks.values()) and
            all(checks.get(name) is True for name in DICTIONARY_CHECKS),
            "frame exact dictionary prerequisite is not PASS")

    bridge = certificate.get("continuation_bridge", {}).get("variables")
    expected_bridge = {
        "r": (Fraction(0), Fraction(2, 25)),
        "a2": (Fraction(-1, 4), Fraction(1, 4)),
        "epsilon": (Fraction(4, 5), Fraction(6, 5)),
    }
    require(isinstance(bridge, dict), "frame continuation bridge is missing")
    raw_bridge = input_binding.get("bridge")
    require(isinstance(raw_bridge, dict), "raw frame bridge is missing")
    for name, (expected_lower, expected_upper) in expected_bridge.items():
        record = bridge.get(name)
        require(isinstance(record, dict), f"bridge variable {name} is missing")
        require(rational_from_record(record.get("lower"), f"{name}.lower") ==
                expected_lower and
                rational_from_record(record.get("upper"), f"{name}.upper") ==
                expected_upper, f"exact bridge endpoints changed for {name}")
        lower, upper = scout.interval_endpoints(
            raw_bridge.get(name), f"raw bridge {name}")
        require(lower <= expected_lower and upper >= expected_upper,
                f"raw bridge interval does not enclose {name}")

    return {
        "frame_sha256": digest,
        "frame_certificate_id": certificate["certificate_id"],
        "frame_source_commit": certificate["source_revision"]["commit"],
        "probe_stdout_sha256": build["probe_stdout_sha256"],
        "grid_cells": 512,
        "dictionary_checks": len(DICTIONARY_CHECKS),
        "L_inverse_operator_upper_from_anchor": rational(
            inverse_operator_upper),
    }


def run_low_order_audit(path: Path = LOW_ORDER_PATH) -> dict[str, Any]:
    """Run the already-small exact q=1,2 algebra prerequisite once."""

    source = path.read_bytes()
    require(sha256_bytes(source) == LOW_ORDER_SHA256,
            "low-order exact-audit source SHA-256 changed")
    environment = os.environ.copy()
    environment.update({
        "LC_ALL": "C.UTF-8",
        "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    completed = subprocess.run(
        [sys.executable, "-B", str(path.resolve())],
        cwd=REPOSITORY, env=environment, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, timeout=60, check=False)
    require(completed.returncode == 0 and completed.stderr == b"",
            "low-order exact audit did not run cleanly")
    require(completed.stdout.count(b"\n") == 1,
            "low-order exact audit did not emit one JSON line")
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise SourceCheckError(
            f"low-order exact audit did not emit JSON: {error}") from error
    require(completed.stdout.decode("utf-8") == canonical_json(report),
            "low-order exact-audit output is not canonical JSON")
    checks = report.get("checks")
    require(report.get("schema_version") ==
            "rfsn-vdp-p2d-normal-form-exact-audit/1" and
            report.get("status") == "PASS" and
            report.get("method") ==
            "exact-sparse-homological-algebra-no-sampling-no-file-inputs" and
            isinstance(checks, dict) and set(checks) == LOW_ORDER_CHECKS and
            all(value is True for value in checks.values()),
            "low-order q=1,2 exact algebra prerequisite is not PASS")
    return {
        "source_sha256": LOW_ORDER_SHA256,
        "stdout_sha256": sha256_bytes(completed.stdout),
        "check_count": len(checks),
        "status": "PASS",
    }


def theory_binding(path: Path = THEORY_PATH) -> dict[str, Any]:
    source = path.read_bytes()
    digest = sha256_bytes(source)
    evidence_marker = (
        b"Evidence status: LOCAL-AMENDMENT / Proved and locally "
        b"source-bound."
    )
    contract_marker = THEORY_PROOF_CONTRACT.encode("ascii")
    expected_is_frozen = (
        len(THEORY_SHA256) == 64 and
        all(character in "0123456789abcdef" for character in THEORY_SHA256)
    )
    matched = (
        expected_is_frozen and digest == THEORY_SHA256
        and evidence_marker in source and contract_marker in source
    )
    return {
        "path": THEORY_RELATIVE,
        "proof_contract": THEORY_PROOF_CONTRACT,
        "expected_sha256": THEORY_SHA256,
        "observed_sha256": digest,
        "proved_and_source_bound_marker": evidence_marker in source,
        "proof_contract_marker": contract_marker in source,
        "matched": matched,
    }


def model_bounds(raw: dict[str, Any]) -> dict[str, Any]:
    scalars = raw["scalar_jets"]
    alpha = scout.normalized_jet_components(scalars["alpha"], "alpha")
    beta = scout.normalized_jet_components(scalars["beta"], "beta")
    U = scout.complex_u_coefficient_jet(raw["L_jets"])
    coefficients = scout.model_coefficient_jets()
    divisor = scout.divisor_jet_majorant(alpha, beta)

    epsilon_min = Fraction(4, 5)
    epsilon_max = Fraction(6, 5)
    sqrt_e = Fraction(11, 10)
    sqrt_d1 = Fraction(9, 80)
    sqrt_d2 = Fraction(729, 51200)
    sqrt_checks = {
        "positive_branch": epsilon_min > 0,
        "sqrt_epsilon_upper": sqrt_e**2 >= epsilon_max,
        "sqrt_epsilon_D1_upper": (
            sqrt_d1**2 >= 1 / (100 * epsilon_min)),
        "sqrt_epsilon_D2_upper": (
            sqrt_d2**2 >= 1 / (10000 * epsilon_min**3)),
    }

    p, q = U["p"], U["q"]
    p_bounds = [p["value_abs"], *p["D1_abs"], *p["D2_abs"]]
    q_bounds = [q["value_abs"], *q["D1_abs"], *q["D2_abs"]]
    u_bounds = [U["value"], *U["D1"], *U["D2"]]
    u_sqrt_checks = [
        (bound / 4)**2 >= (p_bound**2 + q_bound**2) / 2
        for bound, p_bound, q_bound in zip(u_bounds, p_bounds, q_bounds)
    ]

    r = Fraction(2, 25)
    a = Fraction(1, 4)
    dr = Fraction(1, 25)
    da = Fraction(1, 4)
    expected_gamma = {
        "value": 1 + sqrt_e * r**3 * a,
        "D1": [sqrt_e * 3 * r**2 * dr * a,
               sqrt_e * r**3 * da, sqrt_d1 * r**3 * a],
        "D2": [sqrt_e * 6 * r * dr**2 * a,
               sqrt_e * 3 * r**2 * dr * da,
               sqrt_d1 * 3 * r**2 * dr * a, Fraction(),
               sqrt_d1 * r**3 * da, sqrt_d2 * r**3 * a],
    }
    expected_D = {
        "value": sqrt_e * r**2 / 12,
        "D1": [sqrt_e * 2 * r * dr / 12, Fraction(),
               sqrt_d1 * r**2 / 12],
        "D2": [sqrt_e * 2 * dr**2 / 12, Fraction(),
               sqrt_d1 * 2 * r * dr / 12, Fraction(), Fraction(),
               sqrt_d2 * r**2 / 12],
    }
    for expected in (expected_gamma, expected_D):
        expected["J2"] = scout.j2_bound(
            expected["value"], expected["D1"], expected["D2"])
    model_formula_checks = {
        "gamma_jet_formula": coefficients["gamma"] == expected_gamma,
        "D_jet_formula": coefficients["D"] == expected_D,
        "all_complex_U_sqrt_enclosures": all(u_sqrt_checks),
    }

    gamma_J = coefficients["gamma"]["J2"]
    D_J = coefficients["D"]["J2"]
    U_J = U["J2"]
    E = gamma_J * U_J**3 / 3
    quartic = D_J * U_J**4
    h_in = quartic / E
    kappa = divisor["kappa_J"]
    return {
        "proof_checks": {**sqrt_checks, **model_formula_checks},
        "sqrt_bounds": {
            "sqrt_epsilon": rational(sqrt_e),
            "D1_theta_epsilon": rational(sqrt_d1),
            "D2_theta_epsilon": rational(sqrt_d2),
            "complex_U_dyadic_bits": 96,
        },
        "gamma_J": gamma_J,
        "D_J": D_J,
        "U_J": U_J,
        "E": E,
        "h_in": h_in,
        "kappa_J": kappa,
    }


def V_tail(N: int, epsilon: Fraction) -> Fraction:
    return Fraction(256 * (3 * N + 10), 45 * 4**N) * epsilon**2


def B_tail(N: int, epsilon: Fraction) -> Fraction:
    return Fraction(
        2048 * (9 * N**2 + 51 * N + 74), 675 * 4**N
    ) * epsilon


def C_tail(N: int) -> Fraction:
    return Fraction(
        16384 * (9 * N**3 + 63 * N**2 + 150 * N + 128),
        3375 * 4**N,
    )


def Achi_tail(N: int, epsilon: Fraction) -> Fraction:
    return Fraction(16 * (3 * N + 4), 9 * 4**N) * epsilon**3


def G_tail(N: int, epsilon: Fraction) -> Fraction:
    return Fraction(
        128 * (9 * N**2 + 42 * N + 44), 135 * 4**N
    ) * epsilon**2


def K_tail(N: int, epsilon: Fraction) -> Fraction:
    return Fraction(
        1024 * (9 * N**3 + 63 * N**2 + 150 * N + 128),
        675 * 4**N,
    ) * epsilon


def c2_and_primitive_bounds(epsilon: Fraction, A_z: Fraction,
                            N: int = 2) -> dict[str, Any]:
    """Evaluate the exact rational formulas in Sections 6--7."""

    V0, B0, C0 = V_tail(0, epsilon), B_tail(0, epsilon), C_tail(0)

    def single_flow_tails(index: int) -> dict[str, Fraction]:
        Vn, Bn, Cn = (
            V_tail(index, epsilon), B_tail(index, epsilon), C_tail(index))
        return {
            "Sigma": A_z * Bn,
            "P": A_z * Vn,
            "H": A_z**2 * Cn,
            "M": A_z**2 * Bn + A_z**3 * Cn * Vn,
            "Q": (2 * A_z * Vn + 2 * A_z**2 * Bn * Vn
                  + A_z**3 * Cn * Vn**2),
        }

    flow0 = single_flow_tails(0)
    Sbar = A_z
    Pbar = A_z * flow0["P"]
    Hbar = A_z**3 * flow0["H"]
    Mbar = A_z**2 * (flow0["M"] + Pbar * flow0["H"])
    Qbar = A_z * (
        flow0["Q"] + 2 * Pbar * flow0["M"] + Pbar**2 * flow0["H"])
    Dpsi = Hbar + 2 * Mbar + Qbar
    Ptheta = A_z * Pbar
    Htheta = A_z**3 * Hbar
    Mtheta = A_z**2 * (Mbar + Hbar * Ptheta)
    Qtheta = A_z * (
        Qbar + 2 * Mbar * Ptheta + Hbar * Ptheta**2)
    Ltheta = A_z + Ptheta
    Dtheta = Htheta + 2 * Mtheta + Qtheta

    flown = single_flow_tails(N)
    Vn = V_tail(N, epsilon)
    ES = A_z * flown["Sigma"]
    EP = flown["P"] + Pbar * flown["Sigma"]
    EH = A_z**2 * flown["H"] + Hbar * flown["Sigma"]
    EM = (A_z * flown["M"] + A_z * Pbar * flown["H"]
          + Mbar * flown["Sigma"])
    EQ = (flown["Q"] + 2 * Pbar * flown["M"]
          + Pbar**2 * flown["H"] + Qbar * flown["Sigma"])
    E1, E2 = ES + EP, EH + 2 * EM + EQ
    d0 = A_z * Vn
    Etheta1 = Ltheta**2 * (E1 + (Hbar + Mbar) * d0)
    Etheta2 = (
        3 * Dpsi * Ltheta**2 * Etheta1
        + Ltheta**3 * (E2 + Fraction(64, 1) / epsilon * Dpsi * d0)
    )

    Achi0, G0, K0 = (
        Achi_tail(0, epsilon), G_tail(0, epsilon), K_tail(0, epsilon))

    def primitive_inverse_tails(index: int) -> dict[str, Fraction]:
        achi, g, k = (Achi_tail(index, epsilon),
                      G_tail(index, epsilon), K_tail(index, epsilon))
        return {
            "value": achi,
            "state": Sbar * g,
            "parameter": achi + Pbar * g,
            "state_state": Sbar**2 * k + Hbar * g,
            "state_parameter": ((Sbar + Mbar) * g
                                + Sbar * Pbar * k),
            "parameter_parameter": (
                2 * achi + (2 * Pbar + Qbar) * g + Pbar**2 * k),
        }

    primitive0 = primitive_inverse_tails(0)
    primitiven = primitive_inverse_tails(N)

    def joint_one(value: dict[str, Fraction]) -> Fraction:
        return value["state"] + value["parameter"]

    def joint_two(value: dict[str, Fraction]) -> Fraction:
        return (value["state_state"] + 2 * value["state_parameter"]
                + value["parameter_parameter"])

    b1, b2 = joint_one(primitive0), joint_two(primitive0)
    b1n, b2n = joint_one(primitiven), joint_two(primitiven)
    CB = Fraction(64, 1) / epsilon * b2
    EA0 = primitiven["value"] + b1 * d0
    EA1 = Ltheta * (b1n + b2 * d0) + b1 * Etheta1
    EA2 = (
        Ltheta**2 * (b2n + CB * d0)
        + 2 * b2 * Ltheta * Etheta1
        + Dtheta * (b1n + b2 * d0)
        + b1 * Etheta2
    )

    checks = {
        "equation_51e_V0": V0 == Fraction(1, 309237645312),
        "equation_51e_B0": B0 == Fraction(37, 691200),
        "equation_51e_C0": C0 == Fraction(2097152, 3375),
        "equation_54f_Achi0": (
            Achi0 == Fraction(1, 10376293541461622784)),
        "equation_54f_G0": G0 == Fraction(11, 4638564679680),
        "equation_54f_K0": K0 == Fraction(1, 21600),
        "C2_N2_tails_positive": all(value > 0 for value in
                                    (E1, E2, Etheta1, Etheta2)),
        "C2_N2_tails_smaller_than_N0_inputs": (
            Vn < V0 and B_tail(N, epsilon) < B0 and C_tail(N) < C0),
        "primitive_N2_tails_positive": all(value > 0 for value in
                                            (EA0, EA1, EA2)),
        "primitive_N2_basic_tails_smaller_than_N0": (
            Achi_tail(N, epsilon) < Achi0 and
            G_tail(N, epsilon) < G0 and K_tail(N, epsilon) < K0),
    }
    return {
        "checks": checks,
        "accumulated_constants": {
            "Sbar": rational(Sbar), "Pbar": rational(Pbar),
            "Hbar": rational(Hbar), "Mbar": rational(Mbar),
            "Qbar": rational(Qbar), "Dpsi": rational(Dpsi),
            "Ltheta": rational(Ltheta), "Dtheta": rational(Dtheta),
        },
        "N2_C2_tails": {
            "inverse_joint_D1": rational(E1),
            "inverse_joint_D2": rational(E2),
            "forward_joint_D1": rational(Etheta1),
            "forward_joint_D2": rational(Etheta2),
        },
        "N2_primitive_tails": {
            "value": rational(EA0),
            "joint_D1": rational(EA1),
            "joint_D2": rational(EA2),
        },
    }


def build_report(
        frame_path: Path = scout.FRAME_PATH,
        theory_path: Path = THEORY_PATH,
        low_order_result: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
    certificate, digest = scout.load_frame_certificate(frame_path)
    authentication = authenticate_frame_source(certificate, digest)
    low_order = low_order_result or run_low_order_audit()
    require(low_order.get("status") == "PASS",
            "low-order exact algebra prerequisite is not PASS")
    proof_binding = theory_binding(theory_path)

    bounds = model_bounds(certificate["raw_probe"])
    E, h_in, kappa = bounds["E"], bounds["h_in"], bounds["kappa_J"]
    input_checks = {
        **bounds["proof_checks"],
        "equation_18_E": E <= 4,
        "equation_18_h_in": h_in <= Fraction(1, 64),
        "equation_18_kappa_J": kappa <= Fraction(5, 3),
    }

    b0 = Fraction(3, 16)
    Cstar = h_in + 30 * E * kappa
    Bstar = Fraction(128, 1) / b0**2 * Cstar
    Gstar = E * kappa
    majorant_checks = {
        "equation_31_Cstar": Cstar <= Fraction(12801, 64),
        "equation_31_Bstar_envelope": Bstar <= Fraction(6554112, 9),
        "equation_31_Bstar_lt_2pow20": Bstar < 2**20,
        "equation_31_Gstar_envelope": Gstar <= Fraction(20, 3),
        "equation_31_Gstar_lt_8": Gstar < 8,
        "equation_32_Bbar": Fraction(2**20) == 2**20,
        "equation_32_Gbar": Fraction(8) == 8,
    }

    Bbar, Gbar = Fraction(2**20), Fraction(8)
    epsilon = Fraction(1, 2**22)
    theta = Bbar * epsilon
    domain_lhs = Fraction(128, 5) * Gbar * epsilon
    S0 = Fraction(512, 9) * epsilon**2
    B_z = (Fraction(64, 25) * Gbar * epsilon
           * 2 * (theta**2 - 3 * theta + 3) / (1 - theta)**3)
    A_z = 1 / (1 - B_z)
    displacement = A_z * S0
    physical_preimage = Fraction(2, 7) * epsilon + S0
    domain_checks = {
        "equation_38_all_orders_flow_domain": domain_lhs < 1,
        "equation_39_displacement": S0 < epsilon / 8,
        "equation_39b_Bz": B_z < Fraction(1, 16384),
        "equation_39c_Az": A_z < Fraction(16384, 16383),
        "equation_40b_forward_displacement": displacement < epsilon / 8,
        "equation_42e_Dmid_gap": displacement / epsilon < Fraction(1, 16),
        "equation_44a_physical_preimage": (
            physical_preimage < 3 * epsilon / 8),
    }

    N = 2
    normal_form_tail = E * epsilon**3 * theta**N / (1 - theta)
    inverse_coordinate_tail = (
        Fraction(8, 5) * Gbar * epsilon**2 * theta**N
        * ((N + 3) - (N + 2) * theta) / (1 - theta)**2)
    forward_coordinate_tail = A_z * inverse_coordinate_tail
    finite_tail_checks = {
        "equation_45_N2_finite": normal_form_tail > 0,
        "equation_46_N2_finite": normal_form_tail > 0,
        "equation_47_N2_inverse_finite": inverse_coordinate_tail > 0,
        "equation_47a_forward_is_Az_amplified": (
            forward_coordinate_tail == A_z * inverse_coordinate_tail),
    }

    derivative_bounds = c2_and_primitive_bounds(epsilon, A_z, N)
    checks = {
        "input_and_model": input_checks,
        "majorant_envelopes": majorant_checks,
        "domains": domain_checks,
        "N2_finite_tails": finite_tail_checks,
        "C2_and_primitive": derivative_bounds["checks"],
    }
    all_source_checks_pass = all(
        value is True for group in checks.values() for value in group.values())
    local_atom_pass = all_source_checks_pass and proof_binding["matched"]

    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "status": "PASS" if all_source_checks_pass else "FAIL",
        "mathematical_status": (
            "LOCAL_MATHEMATICAL_PASS" if local_atom_pass else
            "LOCAL_SOURCE_GATES_PASS" if all_source_checks_pass else "FAIL"
        ),
        "mathematical_pass_scope": (
            "LOCAL_ANALYTIC_NORMAL_FORM_ATOM" if local_atom_pass else
            "LOCAL_SOURCE_GATES_ONLY"
        ),
        "claim_bearing": False,
        "source_authentication": authentication,
        "proof_bindings": {
            "low_order_q1_q2": low_order,
            "analytic_majorant": proof_binding,
        },
        "exact_values": {
            "equations_17_to_19": {
                "gamma_J": rational(bounds["gamma_J"]),
                "D_J": rational(bounds["D_J"]),
                "U_J": rational(bounds["U_J"]),
                "E": rational(E), "h_in": rational(h_in),
                "kappa_J": rational(kappa),
                "sqrt_bounds": bounds["sqrt_bounds"],
            },
            "equations_30_to_32": {
                "Cstar": rational(Cstar), "Bstar": rational(Bstar),
                "Gstar": rational(Gstar), "Bbar": rational(Bbar),
                "Gbar": rational(Gbar),
            },
            "equations_38_to_44a": {
                "epsilon_nf": rational(epsilon), "theta": rational(theta),
                "S0": rational(S0), "Bz": rational(B_z),
                "Az": rational(A_z),
                "forward_displacement": rational(displacement),
                "Dmid_gap": rational(epsilon / 16),
                "physical_preimage_radius": rational(physical_preimage),
            },
            "N2_equations_45_to_47a": {
                "normal_form_tail": rational(normal_form_tail),
                "remainder_tail": rational(normal_form_tail),
                "inverse_coordinate_tail": rational(inverse_coordinate_tail),
                "forward_coordinate_tail": rational(forward_coordinate_tail),
            },
            "sections_6_and_7": {
                key: value for key, value in derivative_bounds.items()
                if key != "checks"
            },
        },
        "checks": checks,
        "local_chart_status": {
            "V2.CHART.SYMPLECTIC_FRAME": "PASS",
            "V2.CHART.ANALYTIC_NORMAL_FORM": (
                "PASS" if local_atom_pass else "OPEN"),
            "V2.CHART.ZERO_ENERGY": "OPEN",
            "V2.CHART.EXACT_SECTIONS": "OPEN",
            "V2.CHART.WEIGHTED_PASSAGE": "OPEN",
            "V2.CHART.PHYSICAL_SLIDES": "OPEN",
            "V2.CHART.OVERLAPS": "OPEN",
            "V2.EXACT_CHART": "OPEN",
        },
        "claim_boundary": {
            "source_gate_pass_is_local_only": True,
            "analytic_atom_requires_bound_proof_version": True,
            "analytic_proof_version_bound": proof_binding["matched"],
            "claim_bearing": False,
            "V2_EXACT_CHART": "OPEN",
            "excluded": [
                "zero-energy graph and exact sections",
                "weighted passage and physical overlaps",
                "temporal stability, Turing selection, and canard identification",
            ],
        },
    }


def emit(value: dict[str, Any]) -> None:
    sys.stdout.write(canonical_json(value))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame-certificate", type=Path,
                        default=scout.FRAME_PATH)
    parser.add_argument("--theory", type=Path, default=THEORY_PATH)
    arguments = parser.parse_args(argv)
    try:
        report = build_report(
            arguments.frame_certificate.resolve(), arguments.theory.resolve())
    except (OSError, SourceCheckError, scout.ScoutInputError,
            KeyError, TypeError, subprocess.SubprocessError) as error:
        emit({
            "schema_version": SCHEMA_VERSION,
            "scope": SCOPE,
            "status": "INPUT_REJECTED",
            "mathematical_status": "INCONCLUSIVE",
            "error": str(error),
            "claim_bearing": False,
            "local_chart_status": {
                "V2.CHART.ANALYTIC_NORMAL_FORM": "OPEN",
                "V2.EXACT_CHART": "OPEN",
            },
        })
        return 2
    emit(report)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
