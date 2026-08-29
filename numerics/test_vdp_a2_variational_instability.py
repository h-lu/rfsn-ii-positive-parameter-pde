from __future__ import annotations

import unittest

import numpy as np

from numerics.vdp_a2_variational_instability import (
    EVIDENCE_STATUS,
    evaluate_a2_contract,
    pointwise_moment_identity_residual,
)


class A2VariationalInstabilityTests(unittest.TestCase):
    def test_exact_cubic_identity(self) -> None:
        values = np.linspace(-2.0, 3.0, 101)
        for a in (-0.4, 0.0, 1.0, 1.7):
            residual = pointwise_moment_identity_residual(values, a=a)
            self.assertLess(float(np.max(np.abs(residual))), 2.0e-13)

    def test_frozen_a2_candidate_has_strict_floating_margin(self) -> None:
        report = evaluate_a2_contract()
        criterion = report["variational_criterion"]
        self.assertEqual(report["status"], EVIDENCE_STATUS)
        self.assertFalse(report["claim_bearing"])
        self.assertTrue(criterion["floating_gate_pass"])
        self.assertLess(
            criterion["lambda_lower_rayleigh_numerator_upper"], -8.0e-7
        )
        self.assertGreater(criterion["computed_threshold_margin"], 3.0e-7)
        self.assertEqual(report["input"]["point_count_with_duplicate_endpoint"], 6001)
        central = report["central_augmented_integral"]
        self.assertTrue(central["floating_gate_pass"])
        self.assertLess(central["saved_candidate_z_at_half_period"], -0.13)
        self.assertLess(abs(central["physical_grid_identity_defect"]), 1.0e-18)

    def test_grid_refinement_is_stable_but_explicitly_nonrigorous(self) -> None:
        report = evaluate_a2_contract()
        refinement = report["floating_refinement"]
        self.assertGreaterEqual(len(refinement["records"]), 4)
        self.assertLess(refinement["maximum_lambda_lower_numerator_spread"], 1.0e-16)
        self.assertIn("not an outward-rounded", refinement["interpretation"])


if __name__ == "__main__":
    unittest.main()
