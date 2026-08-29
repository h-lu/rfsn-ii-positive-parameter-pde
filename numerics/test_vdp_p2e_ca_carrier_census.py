from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULT = HERE / "results/vdp_p2e_channel_scout_v2/ca_carrier_census.json"
EXPECTED_OFFSETS = [-0.04, -0.02, -0.01, 0.0, 0.01, 0.02, 0.04]


class CACarrierCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_exact_predeclared_stencil_and_frozen_pole_sign_are_retained(self) -> None:
        self.assertEqual(self.result["predeclared_offsets"], EXPECTED_OFFSETS)
        self.assertEqual(
            self.result["parameter_point_exact"],
            {"r": "3/200", "a2": "0", "epsilon": "1"},
        )
        pole = self.result["event_definitions"]["pole"]
        self.assertIn("central U=-10", pole["carrier"])
        self.assertIn("x=-U=10", pole["sign_correction"])

    def test_four_algebraic_and_three_pole_first_events_are_preserved(self) -> None:
        self.assertEqual(
            self.result["event_counts"],
            {"algebraic": 4, "pole_x10_carrier": 3},
        )
        events = [row["first_qualifying_event"] for row in self.result["points"]]
        self.assertEqual(
            events, ["algebraic"] * 4 + ["pole_x10_carrier"] * 3
        )
        for row in self.result["points"][4:]:
            rejected = row["rejected_algebraic_crossings_before_first_event"]
            self.assertEqual(len(rejected), 1)
            self.assertGreater(rejected[0]["state"][3], 0.0)

    def test_hits_are_transverse_separated_and_energy_drift_is_finite(self) -> None:
        for row in self.result["points"]:
            self.assertLess(row["hit_speed"]["central_dU_dxi"], 0.0)
            self.assertGreater(
                row["hit_speed"]["cooriented_minus_dU_dxi"], 0.0
            )
            self.assertAlmostEqual(
                row["inactive_carrier_gap_at_hit"]["value"], 6.0, places=11
            )
            self.assertLess(row["hit_function_residual_abs"], 1.0e-10)
            self.assertTrue(
                np.isfinite(
                    row["hamiltonian"]["sampled_drift_to_first_event"]
                )
            )

    def test_variational_hit_rows_and_algebraic_monotonicity_pass(self) -> None:
        for row in self.result["points"]:
            derivative = row["variational_hit_derivative"]
            self.assertEqual(len(derivative["d_hit_state_d_phase"]), 4)
            self.assertLess(
                derivative["fixed_surface_tangency_residual_abs"], 1.0e-8
            )
        monotonicity = self.result["phase_monotonicity"]["algebraic"]
        self.assertTrue(
            monotonicity["sampled_hit_time_strictly_increases_with_phase"]
        )
        self.assertTrue(
            monotonicity["sampled_Q_hit_strictly_decreases_with_phase"]
        )
        self.assertTrue(
            monotonicity[
                "variational_d_hit_time_d_phase_positive_at_every_sample"
            ]
        )

    def test_scope_stops_before_a_two_sided_aperture_or_event_atlas(self) -> None:
        candidate = self.result["ca_carrier_candidate"]
        self.assertTrue(candidate["selected_phase_is_oriented_algebraic_hit"])
        self.assertFalse(candidate["two_sided_sampled_aperture_certified"])
        self.assertEqual(
            self.result["event_definitions"]["return_or_stable_cut"]["status"],
            "OMITTED_NO_COMPATIBLE_ACTUAL_DEFINITION",
        )
        self.assertFalse(self.result["claim_bearing"])
        self.assertIn("do not", self.result["nonclaim"])


if __name__ == "__main__":
    unittest.main()
