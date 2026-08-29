from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULT = HERE / "results/vdp_p2e_channel_scout_v2/axis_continuation.json"
DATA = HERE / "results/vdp_p2e_channel_scout_v2/axis_continuation.npz"
EXPECTED = {
    "center",
    "r_lower",
    "r_upper",
    "a2_lower",
    "a2_upper",
    "epsilon_lower",
    "epsilon_upper",
}


class SevenPointAxisContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.data = np.load(DATA)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.data.close()

    def test_exactly_the_seven_predeclared_points_succeed(self) -> None:
        self.assertEqual(self.result["status"], "ALL_SEVEN_CENTERLINES_SUCCESS")
        self.assertEqual(set(self.result["points"]), EXPECTED)
        self.assertEqual(set(self.result["successful_points"]), EXPECTED)
        self.assertFalse(self.result["claim_bearing"])

    def test_every_point_passes_fixed_residual_and_positive_branch_qa(self) -> None:
        for row in self.result["points"].values():
            self.assertEqual(row["status"], "SUCCESS")
            self.assertTrue(row["solver"]["success"])
            self.assertLessEqual(row["solver"]["rms_residual_max"], 1.0e-6)
            self.assertTrue(all(row["qa"].values()))
            self.assertLess(row["energy_residuals"]["central_abs_max"], 1.0e-10)
            self.assertLess(row["energy_residuals"]["k1_equation_inf"], 1.0e-12)
            self.assertLess(row["energy_residuals"]["outer_equation_inf"], 1.0e-12)
            self.assertLess(
                row["six_row_and_seam_residuals"]["boundary_inf"], 1.0e-9
            )
            self.assertGreater(row["positive_branch_margins"]["minimum_k1_Pi"], 0.0)
            self.assertGreater(row["positive_branch_margins"]["minimum_k1_q1"], 0.0)
            self.assertGreater(row["positive_branch_margins"]["minimum_outer_pi"], 0.0)

    def test_scalar_phase_order_is_diagnostic_only_and_passes_at_each_point(self) -> None:
        for row in self.result["points"].values():
            phase = row["phase_order_diagnostic"]
            self.assertTrue(phase["diagnostic_order_passed"])
            self.assertGreater(phase["algebraic_to_homoclinic_gap"], 0.0)
            self.assertGreater(phase["homoclinic_to_pole_left_proxy_gap"], 0.0)
            self.assertIn("not an event atlas", phase["nonclaim"])

    def test_three_paired_centered_differences_are_finite_qa_values(self) -> None:
        differences = self.result["centered_finite_differences"]
        for parameter in ("r", "a2", "epsilon"):
            row = differences[parameter]
            self.assertEqual(row["status"], "COMPUTED/E1_QA")
            for key in (
                "d_source_phase", "d_energy_h", "d_central_flight_time"
            ):
                self.assertTrue(np.isfinite(row[key]))

    def test_npz_contains_all_three_segments_for_every_point(self) -> None:
        self.assertEqual(self.result["saved_array_count"], 8 * len(EXPECTED))
        for point in EXPECTED:
            self.assertEqual(self.data[f"{point}__central_state"].shape, (4, 401))
            self.assertEqual(
                self.data[f"{point}__k1_state_Pi_Omega_q1"].shape,
                (3, 401),
            )
            self.assertEqual(
                self.data[f"{point}__outer_state_beta_alpha"].shape,
                (2, 401),
            )


if __name__ == "__main__":
    unittest.main()
