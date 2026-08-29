from __future__ import annotations

import unittest

import numpy as np

from numerics.vdp_canard_slow_trace import (
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


if __name__ == "__main__":
    unittest.main()
