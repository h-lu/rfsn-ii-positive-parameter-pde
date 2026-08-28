from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest import mock


RIGOROUS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RIGOROUS))

import check_p2d_physical_slides as physical  # noqa: E402


def as_fraction(record: dict[str, str]) -> Fraction:
    return Fraction(int(record["numerator"]), int(record["denominator"]))


class P2DPhysicalSlidesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.weighted_report = physical.weighted.build_report()
        cls.proof_sha = hashlib.sha256(
            physical.PROOF_PATH.read_bytes()).hexdigest()
        if physical.PROOF_SHA256 != cls.proof_sha:
            raise AssertionError("the production physical-slides proof is unbound")
        with mock.patch.object(
                physical.weighted, "build_report",
                return_value=cls.weighted_report), \
                mock.patch.object(
                    physical, "PROOF_SHA256", cls.proof_sha):
            cls.report = physical.build_report()

    def build_bound_report(self, **kwargs: object) -> dict[str, object]:
        with mock.patch.object(
                physical.weighted, "build_report",
                return_value=self.weighted_report), \
                mock.patch.object(
                    physical, "PROOF_SHA256", self.proof_sha):
            return physical.build_report(**kwargs)

    def test_local_atom_passes_but_parent_and_p2e_stay_open(self) -> None:
        report = self.report
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["mathematical_status"],
                         "LOCAL_MATHEMATICAL_PASS")
        self.assertEqual(report["mathematical_pass_scope"],
                         "LOCAL_PHYSICAL_SLIDES_ATOM")
        self.assertEqual(report["local_chart_status"][
            "V2.CHART.PHYSICAL_SLIDES"], "PASS")
        self.assertEqual(report["local_chart_status"][
            "V2.CHART.OVERLAPS"], "OPEN")
        self.assertEqual(report["local_chart_status"]["V2.EXACT_CHART"],
                         "OPEN")
        boundary = report["claim_boundary"]
        self.assertEqual(boundary["V2_EVENT_ATLAS_P2e"], "OPEN")
        self.assertEqual(boundary[
            "physical_winding_residence_comparison"],
            {"status": "PASS", "C": "7"})
        self.assertFalse(report["claim_bearing"])
        self.assertFalse(report["release_eligible"])

    def test_physical_face_and_authenticated_source_intervals_are_locked(self) -> None:
        exact = self.report["exact_values"]
        constants = exact["constants"]
        self.assertEqual(as_fraction(constants["physical_face_radius"]),
                         Fraction(1, 100))
        self.assertEqual(as_fraction(constants["section_radius_rho"]),
                         Fraction(5, 2**26))
        self.assertEqual(as_fraction(constants["weighted_radius_nu_p"]),
                         Fraction(25, 2**58))
        self.assertEqual(as_fraction(constants["frame_scale_lower"]),
                         Fraction(21, 32))
        self.assertEqual(as_fraction(constants["frame_scale_upper"]),
                         Fraction(195, 256))
        intervals = exact["authenticated_intervals"]
        self.assertGreater(as_fraction(intervals["P2a_gamma0"]["lower"]),
                           Fraction(2, 3))
        self.assertGreater(as_fraction(intervals[
            "P2a_difference_cone_margin"]["lower"]), 1)
        sigma = intervals["P2bK_sigma"]
        self.assertGreater(as_fraction(sigma["lower"]), Fraction(2, 3))
        self.assertLess(as_fraction(sigma["upper"]), Fraction(3, 4))
        kappa = intervals["P2d_kappa_inverse_sqrt"]
        self.assertGreater(as_fraction(kappa["lower"]), Fraction(63, 64))
        self.assertLess(as_fraction(kappa["upper"]), Fraction(65, 64))
        self.assertTrue(all(exact["checks"].values()))

    def test_initial_cone_time_hit_speed_and_D12_are_explicit(self) -> None:
        exact = self.report["exact_values"]
        cone = exact["initial_cone"]
        unstable_lower = as_fraction(cone[
            "unstable_physical_radius_lower"])
        unstable_upper = as_fraction(cone[
            "unstable_physical_radius_upper"])
        stable_upper = as_fraction(cone["stable_physical_radius_upper"])
        self.assertGreater(unstable_lower, Fraction(1, 2**25))
        self.assertLess(unstable_upper, Fraction(1, 2**24))
        self.assertLess(stable_upper, unstable_lower / 32)
        self.assertGreater(as_fraction(cone["no_auxiliary_recross_margin"]), 0)
        slide = exact["slide_bounds"]
        self.assertEqual(slide["incoming_time_strict_upper"], "19")
        self.assertEqual(slide["outgoing_time_strict_upper"], "19")
        self.assertGreater(as_fraction(slide["time_gate_margin"]), 0)
        self.assertEqual(as_fraction(
            slide["squared_face_hit_speed_strict_lower"]),
            Fraction(1, 7500))
        self.assertEqual(as_fraction(
            slide["D12_physical_comparison_upper"]), Fraction(27, 4))
        self.assertLess(as_fraction(
            slide["D12_physical_comparison_upper"]), 7)

    def test_complete_four_by_three_jet_rectangle_and_original_table(self) -> None:
        mixed = self.report["exact_values"]["mixed_jet_bounds"]
        normalized = mixed["normalized_4_by_3_rectangle"]
        self.assertEqual(set(normalized), {
            "state_order_0", "state_order_1",
            "state_order_2", "state_order_3"})
        self.assertTrue(all(len(row) == 3 for row in normalized.values()))
        self.assertTrue(all(
            int(value["endpoint_power_of_two_exponent"]) >= 0
            and int(value["hit_time_power_of_two_exponent"]) >= 0
            for row in normalized.values() for value in row))
        original = mixed["original_parameter_rectangle"]
        self.assertEqual(set(original), {
            "value", "D_r", "D_a2", "D_epsilon",
            "D_r_r", "D_r_a2", "D_r_epsilon",
            "D_a2_a2", "D_a2_epsilon", "D_epsilon_epsilon"})
        self.assertTrue(all(len(records) == 4
                            for records in original.values()))
        corner = normalized["state_order_3"][2]
        self.assertEqual(corner["parameter_order"], 2)
        self.assertEqual(corner["endpoint_power_of_two_exponent"],
                         "46518415")
        self.assertEqual(corner["hit_time_power_of_two_exponent"],
                         "9180027")
        value = normalized["state_order_0"][0]
        self.assertEqual(value["hit_time_power_of_two_exponent"], "5")
        self.assertEqual(value["endpoint_power_of_two_exponent"], "0")
        self.assertLess(
            physical.conservative_mixed_jet_exponent(0, 0),
            physical.conservative_mixed_jet_exponent(3, 2))

    def test_source_formula_and_terminal_frame_budgets_are_reconstructed(self) -> None:
        exact = self.report["exact_values"]
        source = exact["source_jet_budget"]
        self.assertEqual(
            [layer["id"] for layer in source["source_formula_layers"]],
            [
                "zero_energy_radial_section", "Moser_forward_map",
                "Kato_C_AK_change", "P2d_kappa_rotation_completion",
            ],
        )
        self.assertEqual(source["maximum_product_factor_count"], "19")
        self.assertIn("P2d_kappa_rotation_jets",
                      source["required_source_objects"])
        zero = source["zero_energy_source_rectangle"]
        self.assertEqual(zero["nu_derivative_orders"], [0, 1, 2, 3])
        self.assertEqual(zero["normalized_parameter_orders"], [0, 1, 2])
        self.assertTrue(all(len(row) == 4
                            for row in zero["q_mixed_bounds"].values()))
        self.assertEqual(
            zero["maximum_q_mixed_bound_strict_power_of_two_exponent"],
            "103")
        self.assertTrue(zero["maximum_q_mixed_bound_is_below_2_pow_103"])
        self.assertLess(
            int(source["derived_source_jet_power_of_two_exponent"]), 4096)
        self.assertTrue(all(source["checks"].values()))

        terminal = exact["terminal_frame_budget"]
        self.assertEqual(set(terminal["normalized_operator_upper_bounds"]),
                         {"T_0", "T_1", "T_2"})
        self.assertEqual(terminal["operator_power_of_two_exponent"], "3")
        self.assertEqual(terminal["parameter_Leibniz_allocation_count"], "4")
        self.assertEqual(
            terminal["full_endpoint_overhead_power_of_two_exponent"], "12")
        self.assertTrue(all(terminal["checks"].values()))

    def test_missing_q_or_terminal_T_jet_is_rejected(self) -> None:
        incomplete_q = physical.weighted.zero_energy.compute_exact_bounds()
        del incomplete_q["mixed_jet_bounds_through_nu_order_3"][
            "normalized_parameter_bounds"]["parameter_order_2"]
        with mock.patch.object(
                physical.weighted.zero_energy, "compute_exact_bounds",
                return_value=incomplete_q), \
                self.assertRaises(physical.PhysicalSlidesCheckError):
            self.build_bound_report()

        _, p2b_jets, _, _, _, _ = physical.authenticate_sources(
            physical.P2A_PATH, physical.P2B_JETS_PATH, physical.KATO_PATH,
            physical.FRAME_PATH, physical.MOSER_PATH,
            physical.CONFIG_PATH, physical.P2C_CONFIG_PATH)
        incomplete_T = copy.deepcopy(p2b_jets)
        del incomplete_T["certificate"]["raw_probe"][
            "frame_derivative_enclosures"]["T_2"]
        with self.assertRaises(physical.PhysicalSlidesCheckError):
            physical._terminal_frame_budget(incomplete_T)

    def test_weighted_chain_and_seven_frozen_hashes_are_bound(self) -> None:
        source = self.report["source_authentication"]
        self.assertTrue(source["weighted_local_pass"])
        self.assertTrue(source["seven_frozen_source_hashes_matched"])
        self.assertEqual(source[physical.P2A_RELATIVE], physical.P2A_SHA256)
        self.assertEqual(source[physical.P2B_JETS_RELATIVE],
                         physical.P2B_JETS_SHA256)
        self.assertEqual(source[physical.KATO_RELATIVE], physical.KATO_SHA256)
        self.assertEqual(source[physical.FRAME_RELATIVE], physical.FRAME_SHA256)
        self.assertEqual(source[physical.MOSER_RELATIVE], physical.MOSER_SHA256)
        self.assertEqual(source[physical.CONFIG_RELATIVE],
                         physical.CONFIG_SHA256)
        self.assertEqual(source[physical.P2C_CONFIG_RELATIVE],
                         physical.P2C_CONFIG_SHA256)
        self.assertEqual(source["local_event_support_restriction"], "EMPTY")

    def test_production_binding_and_proof_mismatch_are_fail_closed(self) -> None:
        with mock.patch.object(
                physical.weighted, "build_report",
                return_value=self.weighted_report):
            production = physical.build_report()
        self.assertEqual(production["status"], "PASS")
        self.assertEqual(production["source_gate_status"], "PASS")
        self.assertEqual(production["local_chart_status"][
            "V2.CHART.PHYSICAL_SLIDES"], "PASS")

        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "physical-slides.md"
            changed.write_bytes(physical.PROOF_PATH.read_bytes() + b"\n")
            changed_report = self.build_bound_report(proof_path=changed)
        self.assertEqual(changed_report["status"], "INCONCLUSIVE")
        self.assertEqual(changed_report["source_gate_status"], "PASS")
        self.assertEqual(changed_report["claim_boundary"][
            "physical_winding_residence_comparison"]["status"], "OPEN")
        with mock.patch.object(
                physical, "build_report", return_value=changed_report), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(physical.main([]), 1)

    def test_upstream_mismatch_remains_inconclusive(self) -> None:
        changed = copy.deepcopy(self.weighted_report)
        changed["status"] = "INCONCLUSIVE"
        changed["mathematical_status"] = "INCONCLUSIVE"
        changed["proof_binding"]["matched"] = False
        changed["local_chart_status"]["V2.CHART.WEIGHTED_PASSAGE"] = "OPEN"
        with mock.patch.object(
                physical.weighted, "build_report", return_value=changed), \
                mock.patch.object(
                    physical, "PROOF_SHA256", self.proof_sha):
            report = physical.build_report()
        self.assertEqual(report["status"], "INCONCLUSIVE")
        self.assertEqual(report["source_gate_status"], "PASS")
        self.assertFalse(report["source_authentication"]["weighted_local_pass"])
        self.assertEqual(report["local_chart_status"][
            "V2.CHART.PHYSICAL_SLIDES"], "OPEN")

    def test_failed_rational_gate_is_FAIL_not_a_local_pass(self) -> None:
        changed_exact = copy.deepcopy(self.report["exact_values"])
        changed_exact["checks"][
            "each_slide_time_is_strictly_below_19"] = False
        with mock.patch.object(
                physical.weighted, "build_report",
                return_value=self.weighted_report), \
                mock.patch.object(
                    physical, "PROOF_SHA256", self.proof_sha), \
                mock.patch.object(
                    physical, "compute_physical_bounds",
                    return_value=changed_exact):
            report = physical.build_report()
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["source_gate_status"], "FAIL")
        self.assertEqual(report["local_chart_status"][
            "V2.CHART.PHYSICAL_SLIDES"], "OPEN")

    def test_source_mutation_and_input_error_are_rejected_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "p2a.json"
            changed.write_bytes(physical.P2A_PATH.read_bytes() + b"\n")
            with self.assertRaises(physical.PhysicalSlidesCheckError):
                physical.authenticate_sources(
                    changed, physical.P2B_JETS_PATH, physical.KATO_PATH,
                    physical.FRAME_PATH, physical.MOSER_PATH,
                    physical.CONFIG_PATH, physical.P2C_CONFIG_PATH)

        output = io.StringIO()
        with mock.patch.object(
                physical, "build_report",
                side_effect=physical.PhysicalSlidesCheckError("bad source")), \
                contextlib.redirect_stdout(output):
            code = physical.main([])
        self.assertEqual(code, 2)
        rejected = json.loads(output.getvalue())
        self.assertEqual(rejected["status"], "INPUT_REJECTED")
        self.assertEqual(rejected["local_chart_status"][
            "V2.CHART.PHYSICAL_SLIDES"], "OPEN")
        self.assertEqual(rejected["claim_boundary"][
            "V2_EVENT_ATLAS_P2e"], "OPEN")

    def test_exact_hex_decoder_and_canonical_output(self) -> None:
        self.assertEqual(physical.hex_fraction("0x1.8p+1", "x"), 3)
        self.assertEqual(physical.hex_fraction("-0x1p-3", "x"),
                         Fraction(-1, 8))
        with self.assertRaises(physical.PhysicalSlidesCheckError):
            physical.hex_fraction("1.5", "bad")
        first, second = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(first):
            physical.emit(self.report)
        with contextlib.redirect_stdout(second):
            physical.emit(self.report)
        self.assertEqual(first.getvalue(), second.getvalue())
        self.assertEqual(first.getvalue().count("\n"), 1)
        self.assertEqual(json.loads(first.getvalue()), self.report)


if __name__ == "__main__":
    unittest.main()
