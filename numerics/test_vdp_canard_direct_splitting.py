from __future__ import annotations

import json
import unittest

from numerics.vdp_canard_direct_splitting import RESULT_PATH, build_report


class CanardDirectSplittingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = build_report()

    def test_only_the_two_predeclared_successful_families_are_used(self) -> None:
        self.assertEqual(self.report["a2_steps"], [2e-05, 1e-05])
        self.assertEqual(
            [family["outer_q2"] for family in self.report["families"]],
            [-80.0, -100.0],
        )
        self.assertFalse(self.report["claim_bearing"])

    def test_every_direct_orbit_hits_the_first_event_increasing(self) -> None:
        for family in self.report["families"]:
            self.assertTrue(family["event_checks_pass"])
            for resolution in family["resolutions"]:
                self.assertEqual(len(resolution["samples"]), 5)
                for sample in resolution["samples"]:
                    self.assertTrue(sample["success"])
                    self.assertLess(sample["initial_p2"], 0.0)
                    self.assertTrue(sample["first_event_verified"])
                    self.assertTrue(sample["no_loop_to_first_event"])
                    self.assertEqual(sample["event_orientation"], "INCREASING")
                    self.assertGreater(sample["event_p2_prime"], 0.0)
                    self.assertLess(abs(sample["event_p2"]), 1e-10)
                    self.assertLess(sample["hamiltonian_max_abs"], 1e-9)

    def test_saved_bvp_centers_are_not_direct_ivp_zeros(self) -> None:
        for family in self.report["families"]:
            self.assertFalse(family["center_is_zero_candidate"])
            self.assertEqual(
                family["simple_zero_status"],
                "NOT_COMPUTED_DIRECT_IVP_DID_NOT_SHADOW_BVP_ZERO",
            )
            for resolution in family["resolutions"]:
                center = resolution["samples"][2]
                self.assertEqual(center["a2_offset"], 0.0)
                self.assertLess(center["splitting_S"], -1.0)

    def test_variation_does_not_pass_the_frozen_difference_check(self) -> None:
        for family in self.report["families"]:
            self.assertFalse(family["derivative_cross_check_pass"])
            for resolution in family["resolutions"]:
                checks = resolution["finite_difference_cross_checks"]
                self.assertEqual(len(checks), 2)
                self.assertTrue(
                    all(check["relative_mismatch"] > 0.9 for check in checks)
                )
            self.assertGreater(
                family["center_resolution_difference"]["splitting_abs"],
                0.1,
            )

    def test_report_stays_fail_closed(self) -> None:
        decision = self.report["decision"]
        self.assertEqual(
            decision["status"],
            "DIRECT_IVP_DID_NOT_SHADOW_BOUNDARY_BVP_CANDIDATES",
        )
        self.assertEqual(
            decision["boundary_selected_simple_zero"], "NOT_ESTABLISHED"
        )
        self.assertEqual(decision["intrinsic_maximal_canard"], "NOT_CLAIMED")

    def test_saved_report_is_the_fresh_replay(self) -> None:
        saved = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(saved, self.report)


if __name__ == "__main__":
    unittest.main()
