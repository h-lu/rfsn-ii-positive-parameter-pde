from __future__ import annotations

import unittest

import numpy as np

from numerics.rfsn_numerics import (
    brusselator_observables,
    certified_core_center,
    compute_periodic_orbit,
    continue_homoclinics,
    origin_matrix,
    vdp_fixr_zero_energy_v,
    vdp_hamiltonian,
)


class NumericalSmokeTests(unittest.TestCase):
    def test_brusselator_linearization_places_r2_in_q_prime(self) -> None:
        matrix = origin_matrix("brusselator", 0.1, 0.0, 1.0)
        expected = np.array(
            [
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, -1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
                [1.0, 0.0, 0.01, 0.0],
            ]
        )
        np.testing.assert_allclose(matrix, expected, rtol=0.0, atol=1.0e-16)

    def test_certified_core_midpoint_reconstructs_symmetry_hit(self) -> None:
        center, diagnostics = certified_core_center()
        self.assertLess(diagnostics["certificate_midpoint_symmetry_residual"], 1.0e-8)
        self.assertAlmostEqual(center[0], 4.8785234781, places=8)
        self.assertAlmostEqual(center[2], -7.9333304422, places=8)

    def test_vdp_fixr_parameterization_has_zero_energy(self) -> None:
        r, a2, epsilon, u = 0.08, 0.0, 1.0, 4.9
        state = np.array([[u], [0.0], [vdp_fixr_zero_energy_v(u, r, a2, epsilon)], [0.0]])
        self.assertLess(abs(float(vdp_hamiltonian(state, r, a2, epsilon)[0])), 2.0e-13)

    def test_brusselator_bvp_stays_nontrivial_and_positive(self) -> None:
        result = continue_homoclinics(
            "brusselator", [0.05], domain=12.0, tolerance=2.0e-6
        )[0]
        observables = brusselator_observables(result)
        self.assertTrue(result.diagnostics["nontrivial_branch"])
        self.assertGreater(result.diagnostics["min_physical_u"], 0.0)
        self.assertGreater(result.diagnostics["min_physical_v"], 0.0)
        self.assertGreater(observables["amplitude_u"], 1.0e-3)

    def test_vdp_family_b_uses_transverse_p_event(self) -> None:
        orbit = compute_periodic_orbit(
            family="B",
            relative_winding=0,
            bracket=(0.00017, 0.00032),
            event_index=1,
            event_component=1,
            residual_component=3,
            center_u=4.925566685678478,
            r=0.08,
        )
        self.assertEqual(orbit.diagnostics["branch_selection_event_component"], "P")
        self.assertEqual(orbit.diagnostics["branch_selection_residual_component"], "Q")
        self.assertGreater(orbit.diagnostics["branch_selection_transversality"], 0.05)
        self.assertLess(orbit.diagnostics["closure_residual"], 1.0e-9)


if __name__ == "__main__":
    unittest.main()
