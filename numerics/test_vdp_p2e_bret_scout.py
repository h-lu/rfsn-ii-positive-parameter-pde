from __future__ import annotations

import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT = HERE / "results/vdp_p2e_channel_scout_v2/bret_census.json"


class BretScoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_frozen_stencil_is_retained_without_retry(self) -> None:
        self.assertEqual(
            self.result["phase_offsets_exact"],
            ["-1/500", "-1/1000", "-1/2000", "0", "1/2000", "1/1000", "1/500"],
        )
        self.assertEqual(
            self.result["parameter_point_exact"],
            {"r": "3/200", "a2": "0", "epsilon": "1"},
        )

    def test_center_is_the_only_sampled_BRET_first_event(self) -> None:
        self.assertEqual(
            self.result["event_counts"],
            {"B.RET_candidate": 1, "algebraic": 4, "pole_x10_carrier": 2},
        )
        center = self.result["points"][3]
        self.assertEqual(center["offset_exact"], "0")
        self.assertEqual(center["first_qualifying_event"], "B.RET_candidate")
        self.assertTrue(center["kato_incoming_coordinates"]["inside_local_block"])

    def test_remote_projection_crossing_is_rejected_by_local_block(self) -> None:
        row = self.result["points"][1]
        rejected = row["rejected_incoming_projection_crossings_before_hit"]
        self.assertEqual(len(rejected), 1)
        self.assertFalse(rejected[0]["inside_local_block"])
        self.assertGreater(rejected[0]["rho_u"], 0.01)

    def test_stable_cut_uses_reverser_and_nonlinear_kato_inverse(self) -> None:
        center = self.result["points"][3]
        stable = center["stable_cut_candidate"]
        self.assertEqual(
            stable["status"], "COMPUTED/E1_KATO_COMPATIBLE_DARBOUX_SECTION"
        )
        self.assertLess(abs(stable["nu_s"]), 1.0e-9)
        self.assertLess(stable["reflected_inverse_reconstruction_defect"], 1.0e-9)
        self.assertFalse(stable["raw_chart_identical"])

    def test_fixed_Q_strata_speeds_energy_and_variational_rows_pass(self) -> None:
        self.assertTrue(all(self.result["qa"].values()))
        for row in self.result["points"]:
            self.assertGreater(row["hit_speed"]["cooriented_speed"], 0.0)
            self.assertIn("d_hit_state_d_phase", row["variational_hit_derivative"])
        self.assertFalse(
            self.result["carrier_conclusion"]["two_sided_sampled_BRET_aperture"]
        )
        self.assertFalse(self.result["claim_bearing"])


if __name__ == "__main__":
    unittest.main()
