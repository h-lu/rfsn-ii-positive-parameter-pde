from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path


RIGOROUS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RIGOROUS))

import check_p2d_zero_energy as zero_energy  # noqa: E402


def as_fraction(record: dict[str, str]) -> Fraction:
    return Fraction(int(record["numerator"]), int(record["denominator"]))


class P2DZeroEnergyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = zero_energy.build_report()

    def test_local_atom_pass_and_parent_stays_open(self) -> None:
        report = self.report
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["mathematical_status"],
                         "LOCAL_MATHEMATICAL_PASS")
        self.assertEqual(
            report["local_chart_status"]["V2.CHART.ZERO_ENERGY"], "PASS")
        self.assertEqual(
            report["local_chart_status"]["V2.EXACT_CHART"], "OPEN")
        self.assertFalse(report["claim_bearing"])
        self.assertFalse(report["release_eligible"])
        self.assertEqual(report["independent_replay"], "1/2")

    def test_exact_action_krawczyk_and_orientation_constants(self) -> None:
        values = self.report["exact_values"]
        constants = values["constants"]
        self.assertEqual(
            as_fraction(constants["action_radius_s"]),
            Fraction(25, 2**50),
        )
        self.assertEqual(
            as_fraction(constants["normal_form_remainder_Mbar"]),
            Fraction(1, 3 * 2**62),
        )
        self.assertEqual(
            as_fraction(constants["remainder_I_derivative_L"]),
            Fraction(1, 153600),
        )
        self.assertEqual(
            as_fraction(constants["nu_star"]), Fraction(25, 2**54))
        self.assertGreater(
            as_fraction(constants["orientation_lower"]), Fraction(2, 3))
        self.assertLess(
            as_fraction(constants["krawczyk_image_radius"]),
            as_fraction(constants["krawczyk_radius_W"]),
        )
        self.assertLess(
            as_fraction(constants["source_lift_action_radius"]),
            as_fraction(constants["exact_source_action_radius"]),
        )
        self.assertTrue(all(values["checks"].values()))
        self.assertTrue(all(self.report["frame_hulls"]["checks"].values()))

    def test_mixed_jet_table_and_all_order_generator_are_exact(self) -> None:
        values = self.report["exact_values"]
        constants = values["constants"]
        gap = as_fraction(constants["nu_cauchy_gap"])
        q0 = as_fraction(constants["Q0"])
        q1 = as_fraction(constants["Q1"])
        table = values["mixed_jet_bounds_through_nu_order_3"]
        normalized = table["normalized_parameter_bounds"]
        self.assertEqual(
            as_fraction(normalized["parameter_order_0"][3]),
            6 * q0 / gap**3,
        )
        original = table["original_parameter_bounds"]
        self.assertEqual(
            as_fraction(original["D_r"][2]), 25 * 2 * q1 / gap**2)
        self.assertEqual(
            as_fraction(original["D_r_a2"][1]),
            100 * as_fraction(constants["Q2"]) / gap,
        )
        generator = values["all_finite_nu_order_generator"]
        self.assertIn("m>=0", generator["normalized_formula"])
        self.assertEqual(
            as_fraction(generator["cauchy_gap"]), gap)

    def test_mutated_mathematical_gates_fail_closed(self) -> None:
        oversized_remainder = zero_energy.compute_exact_bounds(
            m_bar=Fraction(1))
        self.assertFalse(
            oversized_remainder["checks"][
                "fiber_box_lies_in_inner_action_domain"])
        self.assertFalse(
            oversized_remainder["checks"][
                "orientation_has_strict_a_star_margin"])

        weak_alpha = zero_energy.compute_exact_bounds(
            alpha_lower=Fraction(1, 1000000))
        self.assertFalse(
            weak_alpha["checks"]["orientation_has_strict_a_star_margin"])
        self.assertFalse(
            weak_alpha["checks"]["krawczyk_contraction_is_strict"])

    def test_proof_digest_controls_only_the_local_atom_pass(self) -> None:
        self.assertTrue(self.report["proof_binding"]["matched"])
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "zero-energy.md"
            changed.write_bytes(zero_energy.PROOF_PATH.read_bytes() + b"\n")
            changed_report = zero_energy.build_report(proof_path=changed)
        self.assertEqual(changed_report["status"], "INCONCLUSIVE")
        self.assertEqual(changed_report["source_gate_status"], "PASS")
        self.assertEqual(
            changed_report["mathematical_status"],
            "INCONCLUSIVE",
        )
        self.assertEqual(changed_report["mathematical_pass_scope"], "NONE")
        self.assertEqual(
            changed_report["local_chart_status"]["V2.CHART.ZERO_ENERGY"],
            "OPEN",
        )

    def test_proof_mismatch_controls_process_exit_code(self) -> None:
        changed_report = dict(self.report)
        changed_report["status"] = "INCONCLUSIVE"
        output = io.StringIO()
        from unittest import mock
        with mock.patch.object(
                zero_energy, "build_report", return_value=changed_report), \
                contextlib.redirect_stdout(output):
            code = zero_energy.main([])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output.getvalue())["status"],
                         "INCONCLUSIVE")

    def test_low_order_result_cannot_be_injected(self) -> None:
        with self.assertRaises(TypeError):
            zero_energy.build_report(low_order_result={  # type: ignore[call-arg]
                "status": "PASS", "check_count": 26})

    def test_non_utf8_proof_is_rejected_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            invalid = Path(directory) / "zero-energy.md"
            invalid.write_bytes(b"\xff\xfe")
            with self.assertRaises(zero_energy.ZeroEnergyCheckError):
                zero_energy.proof_binding(invalid)

    def test_canonical_output_is_one_line_and_deterministic(self) -> None:
        first, second = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(first):
            zero_energy.emit(self.report)
        with contextlib.redirect_stdout(second):
            zero_energy.emit(self.report)
        self.assertEqual(first.getvalue(), second.getvalue())
        self.assertEqual(first.getvalue().count("\n"), 1)
        self.assertEqual(json.loads(first.getvalue()), self.report)


if __name__ == "__main__":
    unittest.main()
