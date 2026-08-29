from __future__ import annotations

import json
import unittest

from numerics.vdp_canard_boundary_convergence import (
    RESULT_PATH,
    build_report,
    load_configuration,
)


class CanardBoundaryConvergenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_configuration()
        cls.report = build_report()

    def test_the_three_boundaries_remain_predeclared(self) -> None:
        self.assertEqual(
            self.config["outer_q2_boundaries"], [-60.0, -80.0, -100.0]
        )
        self.assertFalse(self.config["claim_bearing"])

    def test_q60_failure_is_retained_without_retargeting(self) -> None:
        row = self.report["slices"][0]
        self.assertEqual(row["outer_q2"], -60.0)
        self.assertEqual(row["status"], "FAILED_A2_PRIMARY_BRANCH_CONTINUATION")
        self.assertIn("u2=14.0", row["failure"])
        self.assertIn("maximum number of mesh nodes", row["failure"].lower())
        self.assertIsNone(row["a2_candidate"])

    def test_q80_and_q100_candidates_keep_branch_and_localization_gates(self) -> None:
        for row in self.report["slices"][1:]:
            self.assertEqual(
                row["status"], "COMPUTED/E1_FINITE_BOUNDARY_A3_CANDIDATE"
            )
            self.assertTrue(row["primary_no_loop_sample_pass"])
            self.assertTrue(row["central_localization_pass"])
            self.assertAlmostEqual(row["common_section_entry"][0], 16.0, places=10)
            self.assertLess(abs(row["common_section_entry_hamiltonian"]), 1e-8)
            self.assertLess(row["boundary_residual_inf"], 2e-12)
            self.assertLess(row["max_interval_rms_relative_residual"], 2.1e-8)

    def test_only_one_boundary_difference_is_descriptive(self) -> None:
        comparison = self.report["comparison"]
        self.assertEqual(
            comparison["three_slice_convergence_status"],
            "NOT_TESTED_MISSING_SLICE",
        )
        self.assertEqual(len(comparison["successive_pairs"]), 1)
        pair = comparison["successive_pairs"][0]
        self.assertEqual((pair["from_q2"], pair["to_q2"]), (-80.0, -100.0))
        self.assertGreater(pair["entry_state_inf"], 0.02)
        self.assertLess(pair["a2_candidate_abs"], 2e-6)

    def test_splitting_derivative_stays_empty_after_collocation_failures(self) -> None:
        for row in self.report["slices"][1:]:
            derivative = row["splitting_a2_derivative"]
            self.assertEqual(
                derivative["status"],
                "NOT_COMPUTED_PERTURBED_COLLOCATION_FAILED",
            )
            self.assertEqual(derivative["derivative_candidates"], [])
            self.assertEqual(len(derivative["attempts"]), 4)
            self.assertTrue(all(not item["success"] for item in derivative["attempts"]))

    def test_saved_report_is_the_fresh_replay(self) -> None:
        saved = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(saved, self.report)


if __name__ == "__main__":
    unittest.main()
