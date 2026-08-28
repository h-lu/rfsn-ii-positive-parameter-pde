from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


RIGOROUS = Path(__file__).resolve().parents[1]
REPOSITORY = RIGOROUS.parents[1]
AUDIT = RIGOROUS / "audit_p2d_normal_form_exact.py"

EXPECTED_CHECKS = {
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


def execute() -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", str(AUDIT)],
        cwd=REPOSITORY,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )


class P2DNormalFormExactAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = execute()
        cls.second = execute()

    def test_sparse_check_set_is_true_and_byte_deterministic(self) -> None:
        self.assertEqual(self.first.returncode, 0, self.first.stderr.decode())
        self.assertEqual(self.second.returncode, 0, self.second.stderr.decode())
        self.assertEqual(self.first.stdout, self.second.stdout)
        self.assertEqual(self.first.stderr, b"")
        self.assertEqual(self.first.stdout.count(b"\n"), 1)

        report = json.loads(self.first.stdout)
        self.assertEqual(
            report["schema_version"],
            "rfsn-vdp-p2d-normal-form-exact-audit/1",
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(
            report["method"],
            "exact-sparse-homological-algebra-no-sampling-no-file-inputs",
        )
        self.assertEqual(set(report["checks"]), EXPECTED_CHECKS)
        self.assertTrue(all(report["checks"].values()))
        self.assertEqual(report["sparse_counts"], {
            "cubic_generator_monomials": 20,
            "cubic_input_monomials": 20,
            "quartic_generator_monomials": 32,
            "quartic_input_monomials": 35,
            "quartic_resonant_monomials": 3,
        })
        self.assertEqual(report["input_policy"], {
            "external_files": [],
            "floating_point": False,
            "sampling": False,
        })

    def test_core_formula_does_not_close_analytic_normal_form(self) -> None:
        self.assertEqual(self.first.returncode, 0, self.first.stderr.decode())
        report = json.loads(self.first.stdout)
        self.assertEqual(report["exact_formulas"]["core_anchor"], {
            "K02": "-1/60",
            "K11": "0",
            "K20": "-1/60",
            "Z4": "((I2K)^2-I1^2)/120",
            "alpha": "1/sqrt(2)",
            "beta": "1/sqrt(2)",
            "eta": "0",
            "gamma": "1",
            "p": "sqrt(4+2*sqrt(2))/4",
            "q": "sqrt(4-2*sqrt(2))/4",
        })
        self.assertEqual(
            report["exact_formulas"][
                "core_conditional_formal_zero_energy_coefficient"
            ],
            {
                "conditional_coefficient": "c2=0",
                "formal_ansatz": "I1=-nu+c2*nu^2+...",
                "linear_branch": "I1=-I2K",
                "quartic_value_on_linear_branch": "0",
                "scope": (
                    "conditional formal coefficient comparison through "
                    "action degree two only; no formal or analytic branch "
                    "is constructed"
                ),
            },
        )
        boundary = report["claim_boundary"]
        self.assertFalse(boundary["claim_bearing"])
        self.assertFalse(boundary["low_order_audit_closes_atom"])
        self.assertIn(
            "constructs neither a formal nor an analytic branch",
            boundary["conditional_formal_coefficient_only"],
        )
        self.assertIn(
            "nonlinear zero-energy branch existence uniqueness and uniformity",
            boundary["open_scope"],
        )
        self.assertEqual(
            boundary["local_obligation"],
            "V2.CHART.ANALYTIC_NORMAL_FORM remains OPEN",
        )
        self.assertEqual(
            boundary["parent_obligation"], "V2.EXACT_CHART remains OPEN"
        )


if __name__ == "__main__":
    unittest.main()
