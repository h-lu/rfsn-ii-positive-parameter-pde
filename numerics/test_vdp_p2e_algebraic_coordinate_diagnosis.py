from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np

from numerics.vdp_matched_outer import (
    finite_horizon_gamma_continuation,
    k1_center_graph_leading_guess,
    outer_seam_coordinates,
    resolved_k1_to_outer_normal,
)
from numerics.vdp_outer import (
    OuterParameters,
    normal_outer_rhs_q,
    normal_to_positive_pi_state,
    positive_pi_outer_rhs_q,
    positive_pi_outer_state,
)


HERE = Path(__file__).resolve().parent
RESULT = (
    HERE / "results/vdp_p2e_channel_scout_v2/algebraic_coordinate_diagnosis.json"
)


class PositivePiCoordinateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parameters = OuterParameters(r=3.0 / 200.0, a2=0.0, epsilon=1.0)
        self.z_r, self.q_r = outer_seam_coordinates(
            self.parameters, outer_r1=2.0
        )
        leading = k1_center_graph_leading_guess(
            np.array([2.0]), self.parameters
        )[:, 0]
        self.seam = resolved_k1_to_outer_normal(
            leading, self.parameters, outer_r1=2.0
        )

    def test_positive_pi_chart_round_trip_at_the_small_r_seam(self) -> None:
        transformed = normal_to_positive_pi_state(
            self.q_r, self.seam, self.parameters
        )
        beta, alpha, _chi, pi, _w = positive_pi_outer_state(
            self.q_r, transformed, self.parameters
        )
        np.testing.assert_allclose(
            np.array([beta, alpha]), self.seam, rtol=0.0, atol=2.0e-19
        )
        self.assertGreater(float(pi), 1.0e-4)

        transformed_rhs = positive_pi_outer_rhs_q(
            self.q_r, transformed, self.parameters
        )[:, 0]
        normal_rhs = normal_outer_rhs_q(
            self.q_r, self.seam, self.parameters
        )[:, 0]
        step = 1.0e-4
        forward = np.array(
            positive_pi_outer_state(
                self.q_r + step,
                transformed + step * transformed_rhs,
                self.parameters,
            )[:2]
        )
        backward = np.array(
            positive_pi_outer_state(
                self.q_r - step,
                transformed - step * transformed_rhs,
                self.parameters,
            )[:2]
        )
        np.testing.assert_allclose(
            (forward - backward) / (2.0 * step),
            normal_rhs,
            rtol=0.0,
            atol=1.0e-15,
        )

    def test_positive_pi_gamma_continuation_reaches_the_leading_seam(self) -> None:
        continuation = finite_horizon_gamma_continuation(
            self.parameters,
            (0.0, float(self.seam[0])),
            q_start=self.q_r,
            q_end=200.0,
            points=301,
            tolerance=2.0e-8,
            max_nodes=60_000,
            positive_pi=True,
        )
        sample = continuation.samples[-1]
        self.assertGreater(sample.diagnostics["minimum_pi"], 1.0e-4)
        self.assertLess(sample.diagnostics["energy_residual_inf"], 1.0e-13)
        self.assertLess(abs(float(self.seam[1]) - sample.gamma), 2.0e-12)

    def test_recorded_full_candidate_is_fail_closed_at_the_next_interface(self) -> None:
        result = json.loads(RESULT.read_text(encoding="utf-8"))
        self.assertEqual(
            result["status"],
            "OUTER_COORDINATE_REPAIRED_MATCHED_CANDIDATE_REJECTED",
        )
        self.assertTrue(
            result["coordinate_diagnosis"]["old_failure_is_a_newton_domain_escape"]
        )
        self.assertFalse(result["candidate"]["accepted_as_matched_channel"])
        self.assertGreater(
            abs(result["candidate"]["central_k1_q1_interface_residual"]), 1.0
        )
        self.assertFalse(result["claim_bearing"])


if __name__ == "__main__":
    unittest.main()
