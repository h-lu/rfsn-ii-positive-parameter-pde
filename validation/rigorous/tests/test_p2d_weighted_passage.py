from __future__ import annotations

import contextlib
import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest import mock


RIGOROUS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RIGOROUS))

import check_p2d_weighted_passage as weighted  # noqa: E402


def as_fraction(record: dict[str, str]) -> Fraction:
    return Fraction(int(record["numerator"]), int(record["denominator"]))


class P2DWeightedPassageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = weighted.build_report()

    def test_local_atom_pass_and_parent_stays_open(self) -> None:
        report = self.report
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["mathematical_status"],
                         "LOCAL_MATHEMATICAL_PASS")
        self.assertEqual(
            report["local_chart_status"]["V2.CHART.WEIGHTED_PASSAGE"],
            "PASS",
        )
        self.assertEqual(
            report["local_chart_status"]["V2.CHART.PHYSICAL_SLIDES"],
            "OPEN",
        )
        self.assertEqual(
            report["local_chart_status"]["V2.EXACT_CHART"], "OPEN")
        self.assertFalse(report["claim_bearing"])
        self.assertFalse(report["release_eligible"])

    def test_exact_branch_clock_and_winding_constants(self) -> None:
        exact = self.report["exact_values"]
        constants = exact["constants"]
        self.assertTrue(all(exact["checks"].values()))
        self.assertEqual(
            as_fraction(constants["weighted_analytic_radius"]),
            Fraction(25, 2**57),
        )
        self.assertEqual(
            as_fraction(constants["weighted_passage_radius"]),
            Fraction(25, 2**58),
        )
        self.assertEqual(
            as_fraction(constants["p_branch_variation"]),
            Fraction(79, 1152),
        )
        self.assertEqual(
            as_fraction(constants["c_star"]), Fraction(35, 2**53))
        self.assertEqual(
            as_fraction(constants["root_n2_over_passage_radius"]),
            Fraction(12, 61),
        )
        self.assertLess(
            as_fraction(constants["clock_contraction"]), Fraction(1, 16))
        self.assertEqual(
            as_fraction(
                constants["local_winding_residence_comparison_upper"]),
            Fraction(2),
        )
        deck = exact["argument_deck"]
        self.assertEqual(
            deck["positive_action_limit"],
            "-pi+arctan(alpha_mu/beta_mu)",
        )
        self.assertEqual(
            deck["negative_action_limit"],
            "arctan(alpha_mu/beta_mu)",
        )
        self.assertLess(as_fraction(deck["real_slice_p_upper"]), 0)
        self.assertTrue(
            exact["sharp_weighted_log_method"]["not_a_uniform_log_bound"])

    def test_all_finite_order_generator_and_rectangular_parameter_table(self) -> None:
        exact = self.report["exact_values"]
        table = exact["mixed_bounds_through_log_order_3"]
        self.assertEqual(table["lambda_m"], ["1", "2", "6", "26"])
        witness = exact["all_finite_log_order_generator"]["witness_orders"]
        self.assertEqual(witness["7"]["lambda_m"], "94586")
        self.assertGreater(
            as_fraction(witness["7"]["C_m_original_parameters"]), 0)
        original = table["original_parameter_bounds"]
        self.assertEqual(
            set(original),
            {
                "value", "D_r", "D_a2", "D_epsilon",
                "D_r_r", "D_r_a2", "D_r_epsilon",
                "D_a2_a2", "D_a2_epsilon", "D_epsilon_epsilon",
            },
        )
        self.assertTrue(all(len(records) == 4
                            for records in original.values()))

    def test_centered_generator_coefficients_are_locked(self) -> None:
        values = (
            Fraction(2),
            (Fraction(1), Fraction(2), Fraction(3)),
            (Fraction(4), Fraction(5), Fraction(6)),
            (Fraction(7), Fraction(8), Fraction(9)),
            (Fraction(10), Fraction(11), Fraction(12)),
            (Fraction(13), Fraction(14), Fraction(15)),
        )
        time_zero, phase_zero, weight_zero = weighted._weighted_generator(
            0, *values)
        self.assertEqual(time_zero, (Fraction(5), Fraction(7), Fraction(9)))
        self.assertEqual(
            phase_zero,
            (Fraction(47, 2), Fraction(33), Fraction(36)),
        )
        self.assertEqual(weight_zero, 1)
        time_one, phase_one, weight_one = weighted._weighted_generator(
            1, *values)
        self.assertEqual(
            time_one, (Fraction(11), Fraction(16), Fraction(21)))
        self.assertEqual(
            phase_one, (Fraction(54), Fraction(74), Fraction(81)))
        self.assertEqual(weight_one, 2)

    def test_clock_root_and_downstream_kato_dictionary(self) -> None:
        exact = self.report["exact_values"]
        root = exact["clock_root_generator"]
        residual = exact["downstream_residual"]
        self.assertEqual(root["uniform_winding_threshold"], 2)
        self.assertEqual(root["signs"], ["+", "-"])
        self.assertTrue(root["u_first_derivative_polynomial_coefficients"])
        self.assertTrue(root["u_second_derivative_polynomial_coefficients"])
        self.assertEqual(
            residual["b_tilde_K"], "b_K-beta_mu*t_K=gamma_mu_sigma")
        self.assertEqual(
            residual["finite_matching_row"],
            "psi-phi-theta-b_tilde_K-varrho_K=0",
        )
        self.assertGreater(as_fraction(residual["C_varrho"]), 0)
        boundary = self.report["claim_boundary"]
        self.assertEqual(boundary["radial_winding_residence_comparison"],
                         "PASS")
        self.assertIn("OPEN", boundary[
            "physical_winding_residence_comparison"])

    def test_required_weighted_kato_identities_are_authenticated(self) -> None:
        audit = self.report["exact_audit"]
        self.assertEqual(
            set(audit["required_checks"]),
            set(weighted.REQUIRED_WEIGHTED_AUDIT_CHECKS),
        )
        self.assertTrue(all(audit["required_checks"].values()))
        characteristic = audit["characteristic_identity"]
        self.assertEqual(
            characteristic["formula"], "alpha_mu^2+beta_mu^2=1")
        self.assertEqual(
            characteristic["check"], "alpha_beta_spectral_relations")
        self.assertTrue(characteristic["passed"])
        self.assertEqual(
            characteristic["source_sha256"],
            "c67cce575caa396eba5b4388e8ba9a0c9d73fd702f69911d64c878f57f27bff3",
        )

    def test_own_proof_mismatch_is_inconclusive_and_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "weighted.md"
            changed.write_bytes(weighted.PROOF_PATH.read_bytes() + b"\n")
            report = weighted.build_report(proof_path=changed)
        self.assertEqual(report["status"], "INCONCLUSIVE")
        self.assertEqual(report["source_gate_status"], "PASS")
        self.assertEqual(
            report["local_chart_status"]["V2.CHART.WEIGHTED_PASSAGE"],
            "OPEN",
        )
        self.assertEqual(
            report["claim_boundary"][
                "radial_winding_residence_comparison"],
            "OPEN",
        )
        with mock.patch.object(
                weighted, "build_report", return_value=report), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(weighted.main([]), 1)

    def test_upstream_proof_mismatch_stays_inconclusive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "exact-sections.md"
            changed.write_bytes(
                weighted.exact_sections.PROOF_PATH.read_bytes() + b"\n")
            report = weighted.build_report(
                exact_sections_proof_path=changed)
        self.assertEqual(report["status"], "INCONCLUSIVE")
        self.assertEqual(report["source_gate_status"], "PASS")
        self.assertFalse(report["source_authentication"][
            "exact_sections_local_pass"])
        self.assertEqual(
            report["local_chart_status"]["V2.CHART.EXACT_SECTIONS"],
            "OPEN",
        )
        self.assertEqual(
            report["local_chart_status"]["V2.CHART.WEIGHTED_PASSAGE"],
            "OPEN",
        )
        self.assertEqual(
            report["claim_boundary"][
                "radial_winding_residence_comparison"],
            "OPEN",
        )

    def test_zero_energy_proof_mismatch_stays_inconclusive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "zero-energy.md"
            changed.write_bytes(
                weighted.zero_energy.PROOF_PATH.read_bytes() + b"\n")
            report = weighted.build_report(zero_energy_proof_path=changed)
        self.assertEqual(report["status"], "INCONCLUSIVE")
        self.assertEqual(report["source_gate_status"], "PASS")
        self.assertFalse(report["source_authentication"][
            "exact_sections_local_pass"])
        self.assertEqual(
            report["local_chart_status"]["V2.CHART.ZERO_ENERGY"],
            "OPEN",
        )
        self.assertEqual(
            report["local_chart_status"]["V2.CHART.WEIGHTED_PASSAGE"],
            "OPEN",
        )
        self.assertEqual(
            report["claim_boundary"][
                "radial_winding_residence_comparison"],
            "OPEN",
        )
        with mock.patch.object(
                weighted, "build_report", return_value=report), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(weighted.main([]), 1)

    def test_exact_audit_source_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "audit_p2d_exact_chart.py"
            changed.write_bytes(
                weighted.exact_sections.AUDIT_PATH.read_bytes() + b"\n")
            with mock.patch.object(
                    weighted.exact_sections, "AUDIT_PATH", changed), \
                    self.assertRaises(
                        weighted.exact_sections.ExactSectionsCheckError):
                weighted.build_report()

        certificate, _ = (
            weighted.zero_energy.normal_form.scout.load_frame_certificate(
                weighted.zero_energy.normal_form.scout.FRAME_PATH))
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "vdp_bridge_v1_p2b_kato.json"
            changed.write_bytes(
                weighted.KATO_CERTIFICATE_PATH.read_bytes() + b"\n")
            with mock.patch.object(
                    weighted, "KATO_CERTIFICATE_PATH", changed), \
                    self.assertRaises(weighted.WeightedPassageCheckError):
                weighted.weighted_audit_gates(certificate)

    def test_audit_mutation_and_failed_bound_gate_fail_closed(self) -> None:
        certificate, _ = (
            weighted.zero_energy.normal_form.scout.load_frame_certificate(
                weighted.zero_energy.normal_form.scout.FRAME_PATH))
        changed_certificate = copy.deepcopy(certificate)
        changed_certificate["exact_audit"]["report"]["checks"][
            weighted.REQUIRED_WEIGHTED_AUDIT_CHECKS[0]] = False
        with self.assertRaises((weighted.WeightedPassageCheckError,
                                weighted.exact_sections.ExactSectionsCheckError)):
            weighted.weighted_audit_gates(changed_certificate)

        changed_bounds = copy.deepcopy(self.report["exact_values"])
        changed_bounds["checks"][
            "clock_contraction_is_below_one_sixteenth"] = False
        with mock.patch.object(
                weighted, "compute_weighted_bounds",
                return_value=changed_bounds):
            report = weighted.build_report()
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["source_gate_status"], "FAIL")
        self.assertEqual(
            report["local_chart_status"]["V2.CHART.WEIGHTED_PASSAGE"],
            "OPEN",
        )
        self.assertEqual(
            report["claim_boundary"][
                "radial_winding_residence_comparison"],
            "OPEN",
        )

    def test_subprocess_error_and_non_utf8_proof_are_rejected_cleanly(self) -> None:
        output = io.StringIO()
        with mock.patch.object(
                weighted.exact_sections, "build_report",
                side_effect=subprocess.TimeoutExpired("audit", 1)), \
                contextlib.redirect_stdout(output):
            code = weighted.main([])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["status"],
                         "INPUT_REJECTED")

        with tempfile.TemporaryDirectory() as directory:
            invalid = Path(directory) / "weighted.md"
            invalid.write_bytes(b"\xff\xfe")
            with self.assertRaises(weighted.WeightedPassageCheckError):
                weighted.proof_binding(invalid)

    def test_canonical_output_is_one_line_and_deterministic(self) -> None:
        first, second = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(first):
            weighted.emit(self.report)
        with contextlib.redirect_stdout(second):
            weighted.emit(self.report)
        self.assertEqual(first.getvalue(), second.getvalue())
        self.assertEqual(first.getvalue().count("\n"), 1)
        self.assertEqual(json.loads(first.getvalue()), self.report)


if __name__ == "__main__":
    unittest.main()
