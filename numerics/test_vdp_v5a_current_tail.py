"""Archive checks for the current v2 V5A finite-Q tail object."""

from __future__ import annotations

import hashlib
import json
import unittest

import numpy as np
from scipy.integrate import simpson, trapezoid

from numerics.vdp_outer import OuterParameters
from numerics.vdp_v5a_current_tail import (
    DEFAULT_CONFIG,
    DEFAULT_DATA,
    DEFAULT_RESULT,
    ROOT,
    outer_densities,
)


def sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class V5ACurrentTailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
        cls.result = json.loads(DEFAULT_RESULT.read_text(encoding="utf-8"))
        cls.data = np.load(DEFAULT_DATA)

    def test_status_and_bindings_remain_nonclaiming(self) -> None:
        self.assertEqual(
            self.result["status"],
            "CURRENT_CENTERLINE_V5A_FINITE_Q_OBJECT_COMPUTED",
        )
        self.assertEqual(
            self.result["evidence_status"], "COMPUTED/E1_NON_RIGOROUS"
        )
        self.assertEqual(self.result["theorem_status"], "INCONCLUSIVE")
        self.assertFalse(self.result["claim_bearing"])
        self.assertTrue(all(self.result["qa"].values()))
        binding = self.result["input_binding"]
        self.assertEqual(
            binding["frozen_config_sha256"], sha256(DEFAULT_CONFIG)
        )
        self.assertEqual(
            binding["centerline_json_sha256"],
            sha256(ROOT / binding["centerline_json"]),
        )
        self.assertEqual(
            binding["centerline_npz_sha256"],
            sha256(ROOT / binding["centerline_npz"]),
        )

    def test_saved_densities_are_the_exact_common_q_formulas(self) -> None:
        point = self.result["parameter_point"]
        parameters = OuterParameters(
            r=float(point["r"]),
            a2=float(point["a2"]),
            epsilon=float(point["epsilon"]),
        )
        energy = self.result["normalization"][
            "outer_energy_from_current_centerline"
        ]
        length, action, chi, pi, _w = outer_densities(
            self.data["outer_Q"],
            self.data["actual_beta"],
            self.data["actual_alpha"],
            parameters,
            energy=energy,
        )
        np.testing.assert_allclose(
            length, self.data["actual_length_density"], rtol=0.0, atol=0.0
        )
        np.testing.assert_allclose(
            action, self.data["actual_action_density"], rtol=0.0, atol=0.0
        )
        np.testing.assert_allclose(
            chi, self.data["actual_chi"], rtol=0.0, atol=0.0
        )
        np.testing.assert_allclose(
            pi, self.data["actual_pi"], rtol=0.0, atol=0.0
        )

    def test_current_centerline_and_grid_ladder_are_resolved(self) -> None:
        reconstruction = self.result["current_centerline_reconstruction"]
        thresholds = self.result["thresholds"]
        self.assertLessEqual(
            reconstruction["state_beta_alpha_residual_inf"],
            thresholds["saved_node_state_reconstruction_inf"],
        )
        self.assertLessEqual(
            reconstruction["chi_pi_residual_inf"],
            thresholds["saved_node_chi_pi_reconstruction_inf"],
        )
        finite = self.result["finite_cut_reference_subtraction"]
        self.assertLessEqual(
            finite["last_grid_length_change_abs"],
            thresholds["last_grid_length_change_abs"],
        )
        self.assertLessEqual(
            finite["last_grid_action_change_abs"],
            thresholds["last_grid_action_change_abs"],
        )
        self.assertGreater(
            abs(finite["reference_raw_action_at_q_end"]), 1.0e8
        )
        self.assertLess(abs(finite["relative_action_at_q_end"]), 3.0)

    def test_independent_simpson_quadrature_agrees(self) -> None:
        q = self.data["integration_Q"]
        for key, tolerance in (
            ("integration_delta_length_density", 1.0e-12),
            ("integration_delta_action_density", 1.0e-6),
        ):
            density = self.data[key]
            self.assertLessEqual(
                abs(float(simpson(density, x=q) - trapezoid(density, q))),
                tolerance,
            )

    def test_finite_covariance_does_not_claim_the_improper_limit(self) -> None:
        covariance = self.result["finite_covariance"]
        thresholds = self.result["thresholds"]
        self.assertTrue(all(
            abs(row["length_balance_residual"])
            <= thresholds["cut_balance_length_abs"]
            and abs(row["action_balance_residual"])
            <= thresholds["cut_balance_action_abs"]
            for row in covariance["cut"]
        ))
        self.assertLessEqual(
            abs(covariance["gauge"]["balance_residual"]),
            thresholds["gauge_balance_action_abs"],
        )
        self.assertEqual(covariance["coordinate"]["status"], "NOT_COMPUTED")
        self.assertIn("Q to infinity", self.result["strict_scope"]["unresolved"])


if __name__ == "__main__":
    unittest.main()
