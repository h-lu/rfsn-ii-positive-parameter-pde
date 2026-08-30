from __future__ import annotations

import json
import unittest
from pathlib import Path


RESULT = (
    Path(__file__).resolve().parent
    / "results/vdp_p2e_channel_scout_v2/terminal_flowbox_scout.json"
)


class TerminalFlowboxScoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_result_is_explicitly_non_evidentiary(self) -> None:
        self.assertEqual(
            self.result["status"], "THREE_TERMINAL_CENTER_GERMS_SCOUTED"
        )
        self.assertEqual(
            self.result["evidence_status"], "COMPUTED/E1_NON_EVIDENTIARY"
        )
        self.assertFalse(self.result["claim_bearing"])

    def test_proposed_entry_scales_are_separate_from_phase_collars(self) -> None:
        correction = self.result["design_correction"]
        self.assertTrue(
            correction["protected_phase_collars_are_not_flowbox_entry_discs"]
        )
        self.assertEqual(
            correction["candidate_entry_phase_radii"]["homoclinic"], 1e-7
        )
        self.assertLess(
            correction["candidate_entry_action_radius"], 1e-16
        )

    def test_two_fixed_u_terminal_map_rank_scouts_pass(self) -> None:
        for channel in ("algebraic", "pole"):
            terminal = self.result[channel]["terminal"]
            derivative = self.result[channel]["finite_difference_terminal_map"]
            self.assertGreater(terminal["cooriented_speed"], 0.0)
            self.assertLess(terminal["section_residual_abs"], 1e-10)
            self.assertTrue(derivative["rank_scout_passed"])
            self.assertGreater(abs(derivative["raw_determinant"]), 1e-3)

    def test_homoclinic_endpoint_phase_probe_stays_on_incoming_face(self) -> None:
        hom = self.result["homoclinic"]
        self.assertTrue(hom["sampled_containment_passed"])
        self.assertGreater(hom["sampled_containment_margin"], 0.004)
        self.assertEqual(len(hom["endpoint_probes"]), 2)
        for row in hom["endpoint_probes"]:
            self.assertLess(row["incoming_stable_radial_speed"], 0.0)

    def test_later_matched_algebraic_candidate_is_only_a_collar_check(self) -> None:
        interface = self.result["algebraic_interface"]
        self.assertTrue(interface["inside_protected_radius_1_over_100"])
        self.assertGreater(interface["remaining_sampled_phase_margin"], 0.009)
        self.assertIn("distinct objects", interface["interpretation"])


if __name__ == "__main__":
    unittest.main()
