from __future__ import annotations

import unittest

import numpy as np

from numerics.vdp_complete_branches import (
    A2_REFERENCE_PHYSICAL_ACTION,
    A2_REFERENCE_PHYSICAL_PERIOD,
    EVIDENCE_STATUS,
    compute_a2_complete_return_candidate,
    integrate_complete_return_branch,
)


class CompleteReturnBranchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.a2 = compute_a2_complete_return_candidate()

    def test_a2_uses_one_composable_outgoing_face(self) -> None:
        branch = self.a2
        self.assertEqual(branch.source_sign_proxy, "positive")
        self.assertEqual(branch.target_sign_proxy, "positive")
        self.assertEqual(branch.local_return_radius, branch.source_radius)
        self.assertTrue(branch.diagnostics["local_return_equals_source_radius"])
        self.assertLess(float(branch.diagnostics["source_face_residual"]), 1.0e-11)
        self.assertLess(float(branch.diagnostics["incoming_face_residual"]), 1.0e-11)
        self.assertLess(float(branch.diagnostics["target_face_residual"]), 1.0e-11)
        self.assertLess(
            np.max(
                np.abs(
                    branch.segments[0].central_state[:, -1]
                    - branch.segments[1].central_state[:, 0]
                )
            ),
            1.0e-13,
        )
        self.assertLess(float(branch.diagnostics["incoming_event_speed"]), 0.0)
        self.assertGreater(float(branch.diagnostics["target_event_speed"]), 0.0)

    def test_a2_augmented_length_and_action_compose(self) -> None:
        branch = self.a2
        self.assertGreater(branch.physical_length, 0.0)
        self.assertGreater(branch.physical_action, 0.0)
        self.assertLess(
            abs(float(branch.diagnostics["segment_length_composition_residual"])),
            1.0e-14,
        )
        self.assertLess(
            abs(float(branch.diagnostics["segment_action_composition_residual"])),
            1.0e-16,
        )
        self.assertLess(
            abs(float(branch.diagnostics["resampled_action_difference"])),
            2.0e-15,
        )
        self.assertLess(float(branch.diagnostics["energy_abs_max"]), 2.0e-12)
        # This comparison is QA against the independently produced periodic
        # candidate.  It is not an interval enclosure or a V6 word proof.
        self.assertLess(
            abs(branch.physical_action - A2_REFERENCE_PHYSICAL_ACTION),
            2.0e-12,
        )
        self.assertLess(
            abs(branch.physical_length - A2_REFERENCE_PHYSICAL_PERIOD),
            5.0e-4,
        )

    def test_target_label_uses_transverse_coordinate_not_phase_half_plane(self) -> None:
        # The B1 target has positive first unstable coordinate but negative
        # numerical transverse coordinate.  It catches the old return+/-
        # convention, which incorrectly used the former quantity.
        b1_source = np.array(
            [
                0.0040554020828554955,
                0.0070909393784836005,
                -0.005914044358061063,
                0.0015356527706468924,
            ]
        )
        branch = integrate_complete_return_branch(
            source_state=b1_source,
            branch_id="vdp-B1-target-sign-regression",
            r=0.08,
            a2=0.0,
            epsilon=1.0,
        )
        self.assertGreater(
            float(branch.diagnostics["target_unstable_first_coordinate"]), 0.0
        )
        self.assertLess(
            float(branch.target_coordinates["transverse_coordinate"]), 0.0
        )
        self.assertEqual(branch.target_sign_proxy, "negative")

    def test_candidate_record_and_npz_payload_preserve_nonclaim(self) -> None:
        record = self.a2.as_candidate_record()
        self.assertEqual(record["evidence_status"], EVIDENCE_STATUS)
        self.assertFalse(record["claim_bearing"])
        self.assertIn("PROXY_ONLY", record["event"]["winding_status"])
        self.assertEqual(record["event"]["physical_event"], "return")
        self.assertGreaterEqual(len(record["nonclaims"]), 4)
        for array in self.a2.as_npz_payload().values():
            self.assertNotEqual(array.dtype, object)

    def test_complete_branch_rejects_a_noncomposable_return_radius(self) -> None:
        with self.assertRaisesRegex(ValueError, "composable complete branch"):
            integrate_complete_return_branch(
                source_state=self.a2.source_state,
                branch_id="noncomposable-radius-regression",
                r=0.08,
                a2=0.0,
                epsilon=1.0,
                source_radius=0.01,
                local_return_radius=0.009,
            )


if __name__ == "__main__":
    unittest.main()
