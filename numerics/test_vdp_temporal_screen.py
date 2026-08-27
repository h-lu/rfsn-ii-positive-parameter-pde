from __future__ import annotations

import unittest

import numpy as np
from scipy.linalg import eigvals

from numerics.vdp_temporal_screen import (
    DEFAULT_MULTIPULSE_ARCHIVE,
    EVIDENCE_STATUS,
    PhysicalProfile,
    TemporalParameters,
    analytic_fourier_growth_rates,
    build_linearized_operator,
    deterministic_initial_perturbation,
    dominant_linear_mode,
    discrete_laplacian_eigenvalues,
    evolve_frozen_profile_perturbation,
    finite_volume_laplacian,
    finite_window_spectrum,
    homogeneous_fourier_validation,
    load_multipulse_profiles,
    refined_real_axis_spectrum,
    run_temporal_prescreen,
)


class VdpTemporalScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parameters = TemporalParameters(r=0.08, a2=0.0, epsilon=1.0)
        cls.profile = load_multipulse_profiles(
            DEFAULT_MULTIPULSE_ARCHIVE, pulse_counts=(1,)
        )[0]

    def test_loads_all_saved_physical_multipulses(self) -> None:
        profiles = load_multipulse_profiles(DEFAULT_MULTIPULSE_ARCHIVE)
        self.assertEqual([profile.pulse_count for profile in profiles], [1, 2, 3, 4])
        for profile in profiles:
            self.assertEqual(profile.x.shape, profile.u.shape)
            self.assertEqual(profile.x.shape, profile.v.shape)
            self.assertTrue(np.all(np.diff(profile.x) > 0.0))
            self.assertLess(abs(profile.u[0] - self.parameters.a), 1.0e-4)
            self.assertLess(abs(profile.u[-1] - self.parameters.a), 1.0e-4)

    def test_continuum_fourier_growth_formula_at_zero_mode(self) -> None:
        rates = analytic_fourier_growth_rates(0.0, self.parameters)
        self.assertEqual(rates.shape, (2,))
        self.assertAlmostEqual(float(np.max(rates.real)), 0.0, places=14)
        self.assertTrue(np.allclose(np.sort(rates.imag), [-1.0, 1.0], atol=1.0e-14))

    def test_discrete_homogeneous_modes_match_matrix_spectrum(self) -> None:
        length = 3.5
        points = 17
        for boundary in ("neumann", "periodic"):
            with self.subTest(boundary=boundary):
                discretization = finite_volume_laplacian(
                    (0.0, length), points, boundary
                )
                operator = build_linearized_operator(
                    np.full(points, self.parameters.a),
                    discretization.laplacian,
                    self.parameters,
                )
                numerical = eigvals(operator.toarray())
                rho = discrete_laplacian_eigenvalues(length, points, boundary)
                # Use the continuum formula with the exact modified
                # finite-volume wavenumbers sqrt(-rho).
                expected = analytic_fourier_growth_rates(
                    np.sqrt(-rho), self.parameters
                ).reshape(-1)
                for value in numerical:
                    self.assertLess(float(np.min(np.abs(expected - value))), 2.0e-10)

    def test_homogeneous_fourier_validation_passes_for_both_boundaries(self) -> None:
        report = homogeneous_fourier_validation(
            self.parameters, interval_length=4.0, grid_points=20
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(
            set(report["finite_volume_matrix_vs_analytic_discrete_modes"]),
            {"neumann", "periodic"},
        )

    def test_zero_perturbation_is_preserved_for_both_boundaries(self) -> None:
        points = 33
        zeros = (np.zeros(points), np.zeros(points))
        for boundary in ("neumann", "periodic"):
            with self.subTest(boundary=boundary):
                result = evolve_frozen_profile_perturbation(
                    self.profile,
                    self.parameters,
                    grid_points=points,
                    boundary_condition=boundary,
                    final_time=0.04,
                    dt=0.01,
                    initial_perturbation=zeros,
                )
                self.assertEqual(result.initial_rms, 0.0)
                self.assertEqual(result.final_rms, 0.0)
                self.assertEqual(result.zero_perturbation_defect_inf, 0.0)

    def test_imex_time_step_refinement_reduces_error(self) -> None:
        points = 41
        initial = deterministic_initial_perturbation(
            finite_volume_laplacian(self.profile.interval, points, "neumann").x
        )
        results = []
        for dt in (0.01, 0.005, 0.0025):
            results.append(
                evolve_frozen_profile_perturbation(
                    self.profile,
                    self.parameters,
                    grid_points=points,
                    boundary_condition="neumann",
                    final_time=0.1,
                    dt=dt,
                    initial_perturbation=initial,
                )
            )
        differences = []
        for left, right in zip(results[:-1], results[1:], strict=True):
            differences.append(
                np.sqrt(
                    np.mean(
                        (left.final_u_perturbation - right.final_u_perturbation) ** 2
                        + (left.final_v_perturbation - right.final_v_perturbation) ** 2
                    )
                )
            )
        self.assertLess(differences[1], differences[0])

    def test_finite_window_spectrum_is_explicitly_candidate_only(self) -> None:
        for boundary in ("neumann", "periodic"):
            with self.subTest(boundary=boundary):
                result = finite_window_spectrum(
                    self.profile,
                    self.parameters,
                    grid_points=31,
                    boundary_condition=boundary,
                    leading_count=6,
                )
                record = result.as_record()
                self.assertEqual(record["evidence_status"], EVIDENCE_STATUS)
                self.assertEqual(record["boundary_condition_on_perturbations"], boundary)
                self.assertEqual(len(record["leading_eigenvalues"]), 6)
                self.assertTrue(np.isfinite(result.spectral_abscissa))
                self.assertIn("finite-window", record["interpretation"])

    def test_leading_mode_is_a_resolved_eigenpair_and_grows_on_short_run(self) -> None:
        value, initial, residual = dominant_linear_mode(
            self.profile,
            self.parameters,
            grid_points=41,
            boundary_condition="neumann",
        )
        self.assertGreater(value.real, 0.0)
        self.assertLess(residual, 1.0e-11)
        result = evolve_frozen_profile_perturbation(
            self.profile,
            self.parameters,
            grid_points=41,
            boundary_condition="neumann",
            final_time=0.1,
            dt=0.0025,
            initial_perturbation=initial,
        )
        self.assertGreater(result.amplification, 1.0)

    def test_refined_real_axis_candidate_matches_complete_small_grid_spectrum(self) -> None:
        complete = finite_window_spectrum(
            self.profile,
            self.parameters,
            grid_points=81,
            boundary_condition="neumann",
        )
        refined = refined_real_axis_spectrum(
            self.profile,
            self.parameters,
            maximum_cell_width=(self.profile.x[-1] - self.profile.x[0]) / 81.0,
            boundary_condition="neumann",
            candidate_count=8,
        )
        self.assertAlmostEqual(
            refined.leading_real_axis_candidate,
            complete.spectral_abscissa,
            places=10,
        )
        self.assertLess(refined.leading_eigenpair_residual_l2, 1.0e-9)

    def test_small_end_to_end_screen_reports_all_sensitivities_and_nonclaims(self) -> None:
        report = run_temporal_prescreen(
            DEFAULT_MULTIPULSE_ARCHIVE,
            parameters=self.parameters,
            pulse_counts=(1,),
            grid_points=35,
            coarse_grid_points=25,
            final_time=0.04,
            dt=0.01,
            leading_count=4,
            refined_maximum_cell_width=0.08,
            coarse_refined_maximum_cell_width=0.12,
        )
        self.assertFalse(report["claim_bearing"])
        self.assertEqual(report["final_status"], "TEMPORAL_PRESCREEN_ONLY")
        self.assertEqual(report["profile_count"], 1)
        self.assertGreaterEqual(len(report["nonclaims"]), 4)
        profile = report["profiles"][0]
        self.assertEqual(
            set(profile["linear_spectra"]),
            {"fine_neumann", "fine_periodic", "coarse_neumann"},
        )
        self.assertEqual(
            set(profile["sensitivity"]),
            {
                "spectral_grid_abscissa_difference",
                "spectral_boundary_abscissa_difference",
                "full_spectrum_audit_grid_abscissa_difference",
                "full_spectrum_audit_boundary_abscissa_difference",
                "time_step_final_state_difference_over_initial_rms",
                "grid_final_state_difference_over_initial_rms",
                "boundary_final_state_difference_over_initial_rms",
                "leading_mode_expected_linear_envelope_amplification",
                "leading_mode_observed_nonlinear_amplification",
                "leading_mode_complex_eigenpair_relative_residual",
                "spectral_sign_agrees_across_checks",
            },
        )
        for run in profile["short_time_runs"].values():
            self.assertEqual(run["zero_perturbation_defect_inf"], 0.0)

    def test_profile_validation_rejects_nonphysical_shapes(self) -> None:
        with self.assertRaisesRegex(ValueError, "equal size"):
            PhysicalProfile(
                pulse_count=1,
                x=np.linspace(0.0, 1.0, 5),
                u=np.zeros(4),
                v=np.zeros(5),
            )


if __name__ == "__main__":
    unittest.main()
