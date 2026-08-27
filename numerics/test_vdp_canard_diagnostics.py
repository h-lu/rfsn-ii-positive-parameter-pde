from __future__ import annotations

import json
import unittest
from pathlib import Path

import numpy as np

from numerics.vdp_bridge import BridgeParameters
from numerics.vdp_canard_diagnostics import (
    CANARD_STOP_STATUS,
    _crosses_fold_levels,
    critical_manifold_v,
    desingularized_reduced_field,
    fast_normal_eigenvalue_squared,
    folded_linear_product,
    folded_singularity_classification,
    maximal_canard_leading_parameter,
    profile_fold_diagnostics,
    screen_saved_profiles,
)


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "numerics" / "results" / "vdp_v1_v7"
CONFIG = ROOT / "numerics" / "config" / "vdp_dynamics_screening.json"


class CanardDiagnosticTests(unittest.TestCase):
    def test_critical_manifold_and_fold_eigenvalues(self) -> None:
        u = np.array([-1.0, 0.0, 1.0, 2.0])
        np.testing.assert_allclose(critical_manifold_v(u), u**3 / 3.0 - u)
        np.testing.assert_allclose(
            fast_normal_eigenvalue_squared(u), np.array([0.0, -1.0, 0.0, 3.0])
        )

    def test_desingularized_field_and_fsn_degeneracy(self) -> None:
        field = desingularized_reduced_field(1.0, 0.0, a=1.0, epsilon=1.0)
        np.testing.assert_allclose(field, 0.0)
        self.assertEqual(folded_linear_product(fold=1.0, a=1.0, epsilon=1.0), 0.0)
        self.assertLess(folded_linear_product(fold=1.0, a=1.1, epsilon=1.0), 0.0)
        self.assertGreater(folded_linear_product(fold=1.0, a=0.9, epsilon=1.0), 0.0)
        self.assertEqual(
            folded_singularity_classification(fold=1.0, a=1.0, epsilon=1.0),
            "FSN_DEGENERATE_SINGULAR_LIMIT",
        )
        self.assertEqual(
            folded_singularity_classification(fold=1.0, a=0.9, epsilon=1.0),
            "DESINGULARIZED_REDUCED_SADDLE",
        )
        self.assertEqual(
            folded_singularity_classification(fold=1.0, a=1.1, epsilon=1.0),
            "DESINGULARIZED_REDUCED_CENTER",
        )

    def test_published_canard_curve_is_translated_to_repository_scaling(self) -> None:
        reference = maximal_canard_leading_parameter(r=0.08, epsilon=1.0)
        self.assertAlmostEqual(reference["blowup_a2_leading"], -1.0 / 120.0)
        self.assertAlmostEqual(
            reference["physical_a_leading"],
            1.0 - (5.0 / 48.0) * 0.08**4,
        )

    def test_synthetic_profile_crossing_is_detected(self) -> None:
        parameters = BridgeParameters(r=0.08, a2=0.0, epsilon=1.0)
        coordinate = np.linspace(-1.0, 1.0, 21)
        # central U changing sign makes physical u=1-r^2 U cross the fold.
        central = np.zeros((4, coordinate.size))
        central[0] = coordinate
        report = profile_fold_diagnostics(coordinate, central, parameters)
        self.assertGreaterEqual(report["crossing_count"], 1)
        self.assertEqual(report["canard_identification_status"], CANARD_STOP_STATUS)
        self.assertGreater(report["samples_on_hyperbolic_side"], 0)
        self.assertGreater(report["samples_on_elliptic_side"], 0)

    def test_negative_fold_uses_fast_normal_side_labels(self) -> None:
        parameters = BridgeParameters(r=0.08, a2=0.0, epsilon=1.0)
        coordinate = np.linspace(-1.0, 1.0, 5)
        physical_u = np.array([-1.2, -1.05, -1.0, -0.95, -0.8])
        central = np.zeros((4, coordinate.size))
        central[0] = (parameters.a - physical_u) / (
            np.sqrt(parameters.epsilon) * parameters.r**2
        )
        report = profile_fold_diagnostics(
            coordinate, central, parameters, fold=-1.0
        )
        self.assertEqual(report["crossing_count"], 1)
        self.assertEqual(report["samples_on_hyperbolic_side"], 2)
        self.assertEqual(report["samples_on_elliptic_side"], 2)

    def test_connected_fold_crossing_does_not_require_an_exact_sample(self) -> None:
        self.assertTrue(_crosses_fold_levels([0.8, 1.2]))
        self.assertTrue(_crosses_fold_levels([-1.2, -0.8]))
        self.assertFalse(_crosses_fold_levels([1.1, 2.0]))

    def test_saved_profiles_cross_positive_fold_but_outer_does_not(self) -> None:
        if not RESULTS.exists():
            self.skipTest("run numerics/run_vdp_master.py first")
        configuration = json.loads(CONFIG.read_text(encoding="utf-8"))
        canard = configuration["canard"]
        report = screen_saved_profiles(
            RESULTS,
            fold=float(canard["positive_fold"]),
            fold_collar=float(canard["fold_collar"]),
            reference_curve=str(canard["reference_curve"]),
        )
        self.assertEqual(report["canard_identification_status"], CANARD_STOP_STATUS)
        self.assertEqual(report["screened_fold"], canard["positive_fold"])
        self.assertEqual(report["fold_collar"], canard["fold_collar"])
        self.assertEqual(
            report["reference_curve_configuration"], canard["reference_curve"]
        )
        self.assertTrue(
            all(
                row["fold_collar"] == canard["fold_collar"]
                for row in report["profile_diagnostics"].values()
            )
        )
        self.assertTrue(
            all(
                row["crossing_count"] >= 1
                for row in report["profile_diagnostics"].values()
            )
        )
        outer = report["outer_diagnostics"]
        self.assertFalse(outer["crosses_a_fold"])
        self.assertGreaterEqual(outer["minimum_u"], 5.0 - 1.0e-12)
        self.assertGreater(outer["minimum_distance_to_fold_set"], 3.9)
        canard_reference = report["maximal_canard_reference"]
        self.assertAlmostEqual(canard_reference["sample_minus_leading_a2"], 1 / 120)


if __name__ == "__main__":
    unittest.main()
