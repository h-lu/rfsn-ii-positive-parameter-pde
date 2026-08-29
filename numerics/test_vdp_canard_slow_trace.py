from __future__ import annotations

import unittest

import numpy as np

from numerics.vdp_canard_slow_trace import (
    A3_CANDIDATE_STATUS,
    C1_STATUS,
    C2_STATUS,
    COINCIDENCE_STATUS,
    ENTRY_STATUS,
    MAXIMAL_CANARD_STATUS,
    compute_candidate,
    load_configuration,
)


class CanardSlowTraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.configuration = load_configuration()
        cls.report, cls.arrays = compute_candidate(cls.configuration)

    def test_frozen_scaling_matches_the_published_leading_slice(self) -> None:
        self.assertEqual(self.configuration.epsilon, 1.0)
        self.assertAlmostEqual(self.configuration.r, 0.08)
        self.assertAlmostEqual(self.configuration.a2, -1.0 / 120.0)
        self.assertAlmostEqual(
            self.report["parameters"]["published_leading_a2"],
            -1.0 / 120.0,
        )

    def test_primary_entry_is_on_the_boundary_selected_collocation_orbit(self) -> None:
        primary = self.report["primary_saddle_slow_representative"]
        self.assertEqual(primary["status"], ENTRY_STATUS)
        entry = primary["entry_state"]
        self.assertAlmostEqual(entry[0], self.configuration.entry_section_u2, places=8)
        self.assertLess(entry[1], 0.0)
        self.assertLess(entry[3], 0.0)
        self.assertGreater(abs(primary["entry_hamiltonian"]), 1.0e-5)
        self.assertLess(abs(primary["entry_hamiltonian"]), 1.0e-3)
        self.assertAlmostEqual(
            primary["full_reflected_orbit_entry_section_s"],
            0.5 * primary["half_orbit_entry_section_s"],
            places=5,
        )

    def test_primary_entry_coordinate_matches_saved_full_orbit(self) -> None:
        primary = self.report["primary_saddle_slow_representative"]
        section_s = primary["full_reflected_orbit_entry_section_s"]
        interpolated = np.asarray(
            [
                np.interp(
                    section_s,
                    self.arrays["primary_s"],
                    component,
                )
                for component in self.arrays["primary_states"]
            ]
        )
        np.testing.assert_allclose(
            interpolated,
            np.asarray(primary["entry_state"]),
            rtol=0.0,
            atol=2.0e-5,
        )

    def test_zero_energy_root_and_first_hit_are_numerically_closed(self) -> None:
        candidate = self.report["zero_energy_coincidence_candidate"]
        self.assertEqual(candidate["status"], COINCIDENCE_STATUS)
        self.assertLess(candidate["hamiltonian_abs_at_left"], 1.0e-9)
        self.assertLess(candidate["hamiltonian_drift"], 2.0e-8)
        self.assertLess(
            candidate["max_interval_rms_relative_residual"], 5.0e-7
        )
        self.assertLess(candidate["reversibility_residual_inf"], 1.0e-10)
        self.assertLess(abs(candidate["splitting_q2"]), 1.0e-10)
        self.assertGreater(candidate["event_p2_derivative"], 0.1)
        bracket = candidate["hamiltonian_bracket"]
        self.assertLess(bracket["negative"], 0.0)
        self.assertGreater(bracket["positive"], 0.0)

    def test_target_branch_gate_prevents_a_maximal_canard_claim(self) -> None:
        diagnostic = self.report["target_branch_diagnostic"]
        self.assertFalse(diagnostic["passes"])
        self.assertGreater(
            abs(diagnostic["candidate_minus_formal_midpoint"][0]), 0.5
        )
        decision = self.report["decision"]
        self.assertEqual(
            decision["C1_finite_parameter_saddle_slow_manifolds"], C1_STATUS
        )
        self.assertEqual(decision["C2_coincidence_curve"], C2_STATUS)
        self.assertEqual(
            decision["finite_parameter_maximal_canard_status"],
            MAXIMAL_CANARD_STATUS,
        )
        self.assertEqual(
            decision["current_sample_a2_zero_classification"], "INCONCLUSIVE"
        )
        self.assertFalse(self.report["claim_bearing"])

    def test_saved_arrays_have_consistent_shapes(self) -> None:
        self.assertEqual(self.arrays["zero_energy_states"].shape[0], 4)
        self.assertEqual(
            self.arrays["zero_energy_states"].shape[1],
            self.arrays["s"].size,
        )
        self.assertEqual(self.arrays["primary_states"].shape[0], 4)
        self.assertEqual(
            self.arrays["primary_states"].shape[1],
            self.arrays["primary_s"].size,
        )
        self.assertEqual(
            self.arrays["continuation_period"].size,
            self.arrays["continuation_hamiltonian"].size,
        )

    def test_a3_candidate_has_the_six_frozen_boundary_conditions(self) -> None:
        candidate = self.report[
            "finite_boundary_a3_compatible_half_candidate"
        ]
        self.assertEqual(candidate["status"], A3_CANDIDATE_STATUS)
        self.assertEqual(
            self.configuration.a3_outer_u2_boundary,
            16.64508336484338,
        )
        self.assertAlmostEqual(
            candidate["left_state"][0],
            self.configuration.a3_outer_u2_boundary,
            places=12,
        )
        lower, upper = self.configuration.a3_candidate_a2_interval
        self.assertLessEqual(lower, candidate["a2_candidate"])
        self.assertLessEqual(candidate["a2_candidate"], upper)
        self.assertLess(candidate["boundary_residual_inf"], 1.0e-8)
        residuals = candidate["boundary_residuals"]
        self.assertEqual(len(residuals), 6)
        self.assertLess(abs(residuals["right_p2"]), 1.0e-8)
        self.assertLess(abs(residuals["right_q2"]), 1.0e-8)
        self.assertLess(abs(residuals["left_hamiltonian"]), 1.0e-8)

    def test_a3_primary_branch_diagnostics_are_central_and_no_loop(self) -> None:
        candidate = self.report[
            "finite_boundary_a3_compatible_half_candidate"
        ]
        self.assertLess(
            candidate["max_interval_rms_relative_residual"], 1.0e-7
        )
        self.assertLess(candidate["hamiltonian_drift"], 1.0e-8)
        self.assertLess(
            abs(candidate["u2_minus_r_a2_at_reverser"]), 1.0e-6
        )
        self.assertLess(
            abs(candidate["v2_plus_one_sixth_at_reverser"]), 1.0e-4
        )
        self.assertGreater(candidate["event_p2_derivative"], 0.16)
        self.assertTrue(candidate["no_loop_sample_pass"])
        difference = candidate["candidate_minus_formal_reverser"]
        self.assertLess(abs(difference[0]), 1.0e-6)
        self.assertLess(abs(difference[2]), 1.0e-4)
        self.assertTrue(
            candidate["central_localization_diagnostic"]["passes"]
        )

    def test_a3_reflection_preserves_the_nonclaim_boundary(self) -> None:
        reflected = self.report["reflected_a3_full_segment"]
        self.assertLess(
            reflected["midpoint_fix_reverser_residual_inf"], 1.0e-8
        )
        self.assertLess(reflected["endpoint_reverser_residual_inf"], 1.0e-8)
        self.assertLess(reflected["sampled_parity_residual_inf"], 1.0e-8)
        self.assertEqual(self.arrays["a3_half_states"].shape[0], 4)
        self.assertEqual(
            self.arrays["a3_half_states"].shape[1],
            self.arrays["a3_half_s"].size,
        )
        self.assertEqual(self.arrays["a3_full_states"].shape[0], 4)
        self.assertEqual(
            self.arrays["a3_full_states"].shape[1],
            self.arrays["a3_full_s"].size,
        )
        candidate = self.report[
            "finite_boundary_a3_compatible_half_candidate"
        ]
        np.testing.assert_allclose(
            self.arrays["a3_half_states"][:, 0],
            np.asarray(candidate["left_state"]),
            rtol=0.0,
            atol=1.0e-12,
        )
        np.testing.assert_allclose(
            self.arrays["a3_half_states"][:, -1],
            np.asarray(candidate["reverser_state"]),
            rtol=0.0,
            atol=1.0e-12,
        )
        np.testing.assert_allclose(
            self.arrays["a3_full_states"][:, self.arrays["a3_full_s"].size // 2],
            np.asarray(candidate["reverser_state"]),
            rtol=0.0,
            atol=1.0e-12,
        )
        self.assertFalse(self.report["target_branch_diagnostic"]["passes"])
        self.assertFalse(self.report["claim_bearing"])
        self.assertEqual(
            self.report["decision"]["C1_finite_parameter_saddle_slow_manifolds"],
            C1_STATUS,
        )
        self.assertEqual(
            self.report["decision"]["C2_coincidence_curve"], C2_STATUS
        )


if __name__ == "__main__":
    unittest.main()
