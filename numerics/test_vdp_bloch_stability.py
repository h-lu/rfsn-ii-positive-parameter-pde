from __future__ import annotations

import json
from pathlib import Path
import unittest

import numpy as np

from numerics.vdp_bloch_stability import (
    EVIDENCE_STATUS,
    NONCLAIMS,
    analytic_constant_profile_dispersion,
    bloch_eigenvalues,
    constant_profile_dispersion_crosscheck,
    eigenvalue_set_matching_defect,
    load_physical_periodic_profiles,
    resample_periodic_profile,
    screen_saved_periodic_profiles,
    translation_mode_diagnostic,
)


RESULTS = Path(__file__).resolve().parent / "results" / "vdp_v1_v7"
PERIODIC_ARCHIVE = RESULTS / "v7_periodic.npz"


class BlochStabilityTests(unittest.TestCase):
    def test_constant_profile_matches_exact_modal_dispersion(self) -> None:
        defect = constant_profile_dispersion_crosscheck(
            period=1.37,
            grid_points=15,
            theta=0.731,
            d=0.08**4,
            epsilon=1.0,
            homogeneous_u=1.0,
        )
        self.assertLess(defect, 3.0e-11)

        numerical = bloch_eigenvalues(
            np.ones(15),
            period=1.37,
            theta=0.731,
            d=0.08**4,
            epsilon=1.0,
        )
        analytic = analytic_constant_profile_dispersion(
            period=1.37,
            grid_points=15,
            theta=0.731,
            d=0.08**4,
            epsilon=1.0,
            homogeneous_u=1.0,
        )
        self.assertLess(eigenvalue_set_matching_defect(numerical, analytic), 3.0e-11)

    def test_real_profile_has_bloch_conjugate_symmetry(self) -> None:
        points = 21
        grid = np.arange(points, dtype=float) / points
        u = 1.0 + 0.04 * np.cos(2.0 * np.pi * grid) - 0.01 * np.sin(
            4.0 * np.pi * grid
        )
        positive = bloch_eigenvalues(
            u, period=1.0, theta=1.19, d=0.08**4, epsilon=1.0
        )
        negative = bloch_eigenvalues(
            u, period=1.0, theta=-1.19, d=0.08**4, epsilon=1.0
        )
        self.assertLess(
            eigenvalue_set_matching_defect(negative, np.conjugate(positive)),
            2.0e-10,
        )

    def test_saved_a2_translation_mode_and_grid_refinement(self) -> None:
        profile = load_physical_periodic_profiles(PERIODIC_ARCHIVE, ("A2",))[0]
        _x_fine, u_fine, v_fine = resample_periodic_profile(profile, 127)
        _x_coarse, u_coarse, _v_coarse = resample_periodic_profile(profile, 95)

        fine_spectrum = bloch_eigenvalues(
            u_fine,
            period=profile.period,
            theta=0.0,
            d=0.08**4,
            epsilon=1.0,
        )
        translation_eigenvalue, translation_residual = translation_mode_diagnostic(
            u_fine,
            v_fine,
            period=profile.period,
            d=0.08**4,
            epsilon=1.0,
            theta_zero_spectrum=fine_spectrum,
        )
        coarse_leading = bloch_eigenvalues(
            u_coarse,
            period=profile.period,
            theta=0.0,
            d=0.08**4,
            epsilon=1.0,
            leading_count=8,
        )
        self.assertLess(abs(translation_eigenvalue), 2.0e-9)
        self.assertLess(translation_residual, 2.0e-6)
        self.assertLess(
            eigenvalue_set_matching_defect(fine_spectrum[:8], coarse_leading),
            2.0e-7,
        )

    def test_five_profile_screen_preserves_nonrigorous_status_and_arrays(self) -> None:
        result = screen_saved_periodic_profiles(
            PERIODIC_ARCHIVE,
            theta=(-0.6, 0.0, 0.6),
            grid_points=31,
            coarse_grid_points=21,
            leading_count=6,
            refinement_theta=(0.0,),
        )
        self.assertEqual(result.labels, ("A0", "B0", "A1", "B1", "A2"))
        self.assertEqual(result.leading_eigenvalues.shape, (5, 3, 6))
        self.assertEqual(result.spectral_abscissa.shape, (5, 3))
        self.assertEqual(result.co_periodic_spectral_abscissa.shape, (5,))
        self.assertEqual(result.status, EVIDENCE_STATUS)
        self.assertFalse(result.claim_bearing)
        self.assertTrue(np.all(np.isfinite(result.conjugacy_defects)))
        self.assertLess(float(np.max(result.conjugacy_defects)), 2.0e-9)
        self.assertTrue(np.all(np.max(result.spectral_abscissa, axis=1) > 1.0e-3))
        self.assertTrue(np.all(result.co_periodic_spectral_abscissa > 1.0e-3))

        payload = result.as_npz_payload()
        self.assertTrue(all(array.dtype != object for array in payload.values()))
        report = result.as_report()
        self.assertFalse(report["claim_bearing"])
        self.assertEqual(report["status"], EVIDENCE_STATUS)
        self.assertEqual(
            report["interpretation"]["proof_status"],
            "NOT_A_PROOF / NOT_INTERVAL_VALIDATED",
        )
        self.assertTrue(
            all(
                profile["co_periodic_outcome"]
                == "SAMPLED_COPERIODIC_INSTABILITY_DETECTED"
                for profile in report["profiles"]
            )
        )
        self.assertEqual(report["nonclaims"], list(NONCLAIMS))
        self.assertIn("finite", " ".join(report["nonclaims"]).lower())
        json.dumps(report, allow_nan=False)

    def test_even_grid_is_rejected_to_keep_fourier_modes_paired(self) -> None:
        with self.assertRaisesRegex(ValueError, "must be odd"):
            bloch_eigenvalues(
                np.ones(16),
                period=1.0,
                theta=0.0,
                d=0.08**4,
                epsilon=1.0,
            )


if __name__ == "__main__":
    unittest.main()
