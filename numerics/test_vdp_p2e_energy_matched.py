from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np

from numerics.vdp_matched_outer import (
    resolved_k1_energy_equation_residual,
)
from numerics.vdp_outer import OuterParameters, energy_equation_residual


HERE = Path(__file__).resolve().parent
RESULT = (
    HERE / "results/vdp_p2e_channel_scout_v2/energy_matched_centerline.json"
)
DATA = (
    HERE / "results/vdp_p2e_channel_scout_v2/energy_matched_centerline.npz"
)


class EnergyPreservingMatchedCenterlineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.data = np.load(DATA)
        cls.parameters = OuterParameters(r=3.0 / 200.0)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.data.close()

    def test_equation_count_contains_the_previously_missing_q1_row(self) -> None:
        count = self.result["equation_count"]
        self.assertEqual(count["state_unknowns"], 4)
        self.assertEqual(len(count["scalar_parameters"]), 2)
        self.assertEqual(count["boundary_equations"], 6)
        self.assertIn("central_to_K1_q1", count["rows"])

    def test_all_predeclared_qa_passes_without_promoting_the_claim(self) -> None:
        self.assertEqual(
            self.result["status"],
            "ENERGY_PRESERVING_MATCHED_CENTERLINE_SUCCESS",
        )
        self.assertTrue(all(self.result["qa"].values()))
        self.assertFalse(self.result["claim_bearing"])
        self.assertEqual(
            self.result["evidence_status"], "COMPUTED/E1_NON_RIGOROUS"
        )

    def test_saved_k1_and_outer_states_lie_on_the_recorded_energy_shells(self) -> None:
        r1 = self.data["k1_r1"]
        pi_scaled, omega_scaled, q1 = self.data["k1_state_Pi_Omega_q1"]
        h_value = float(self.result["energy_h"])
        k1_residual = resolved_k1_energy_equation_residual(
            r1,
            pi_scaled,
            omega_scaled,
            q1,
            self.parameters,
            energy_h=h_value,
        )
        self.assertLess(np.max(np.abs(k1_residual)), 1.0e-12)

        compact_q = self.data["outer_Q"]
        beta, alpha = self.data["outer_state_beta_alpha"]
        chi = self.data["outer_chi"]
        outer_energy = self.parameters.epsilon**2.5 * self.parameters.r**6 * h_value
        outer_residual = energy_equation_residual(
            compact_q**-0.5,
            beta,
            alpha,
            chi,
            self.parameters,
            energy=outer_energy,
        )
        self.assertLess(np.max(np.abs(outer_residual)), 1.0e-12)
        self.assertGreater(np.min(self.data["outer_pi"]), 0.0)

    def test_all_three_saved_segments_have_the_declared_shapes(self) -> None:
        self.assertEqual(self.data["central_state"].shape, (4, 401))
        self.assertEqual(
            self.data["k1_state_Pi_Omega_q1"].shape, (3, 401)
        )
        self.assertEqual(
            self.data["outer_state_beta_alpha"].shape, (2, 401)
        )


if __name__ == "__main__":
    unittest.main()
