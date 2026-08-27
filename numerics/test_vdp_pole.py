from __future__ import annotations

import unittest

import numpy as np

from numerics.vdp_pole import (
    LOCAL_REALIZATION_STATUS,
    SOURCE_WINDOW_STATUS,
    PoleLabels,
    PoleParameters,
    action_cutoff_ladder,
    compact_to_physical,
    energy_projected_jet,
    field_crosscheck,
    fixed_source_energy_kappa,
    indicial_spectra,
    moving_cut_additivity,
    normalized_indicial_residual,
    normalized_jet,
    physical_hamiltonian,
    physical_to_compact,
    pole_energy_from_labels,
    realize_local_pole,
    resonance_identity_residuals,
)


class VanDerPolPoleTests(unittest.TestCase):
    @staticmethod
    def parameters() -> PoleParameters:
        return PoleParameters(r=0.08, a2=0.0, epsilon=1.0)

    @staticmethod
    def labels() -> PoleLabels:
        return PoleLabels(z0=0.16, w0=0.02, kappa=0.25)

    def test_exact_physical_compactified_crosscheck(self) -> None:
        parameters = self.parameters()
        labels = self.labels()
        sigma = 1.7e-3
        compact = normalized_jet(sigma, parameters, labels)
        diagnostics = field_crosscheck(sigma, compact, parameters)
        self.assertLess(
            diagnostics["physical_compact_field_relative_defect_inf"], 2.0e-12
        )
        self.assertLess(diagnostics["coordinate_roundtrip_defect_inf"], 2.0e-13)

    def test_indicial_and_resonant_coefficients(self) -> None:
        parameters = self.parameters()
        labels = self.labels()
        coefficient_residuals = resonance_identity_residuals(parameters, labels)
        scale = parameters.delta ** -4
        self.assertLess(
            max(abs(value) for value in coefficient_residuals.values()),
            2.0e-11 * scale,
        )
        sigma = np.array([1.2e-3, 8.0e-4, 5.0e-4])
        normalized = np.abs(normalized_indicial_residual(sigma, parameters, labels))
        self.assertTrue(np.all(np.isfinite(normalized)))
        self.assertLess(float(np.max(normalized)), 2.0e8)
        spectra = indicial_spectra()
        self.assertEqual(spectra["scalar_indicial_roots"], (-1.0, 4.0))
        self.assertEqual(spectra["normalized_power"], (-1.0, 0.0, 0.0, 1.0, 4.0))

    def test_finite_energy_identity_solves_for_kappa(self) -> None:
        parameters = self.parameters()
        z0, w0 = 0.16, 0.02
        kappa = fixed_source_energy_kappa(parameters, z0, w0)
        labels = PoleLabels(z0=z0, w0=w0, kappa=kappa)
        target = -parameters.epsilon * (
            parameters.a**4 / 12.0 - parameters.a**2 / 2.0
        )
        self.assertAlmostEqual(pole_energy_from_labels(parameters, labels), target, places=11)

    def test_displayed_jet_has_exact_energy_projection(self) -> None:
        parameters = self.parameters()
        labels = self.labels()
        sigma = 5.0e-4
        projected = energy_projected_jet(sigma, parameters, labels)
        physical = compact_to_physical(sigma, projected, parameters)
        self.assertAlmostEqual(
            float(physical_hamiltonian(physical, parameters)),
            pole_energy_from_labels(parameters, labels),
            places=8,
        )

    def test_local_realization_and_independent_physical_orbit(self) -> None:
        realization = realize_local_pole(
            self.parameters(),
            self.labels(),
            sigma_min=5.0e-4,
            sigma_cut=2.5e-3,
            points=120,
            physical_crosscheck=True,
        )
        self.assertEqual(realization.diagnostics["evidence_status"], LOCAL_REALIZATION_STATUS)
        self.assertEqual(realization.diagnostics["source_window_status"], SOURCE_WINDOW_STATUS)
        self.assertTrue(realization.diagnostics["solver_success"])
        self.assertGreater(realization.physical[0, 0], realization.physical[0, -1])
        self.assertLess(
            realization.diagnostics["independent_physical_compact_defect_inf"],
            2.0e-6,
        )
        roundtrip = physical_to_compact(
            realization.sigma, realization.physical, realization.parameters
        )
        self.assertLess(float(np.max(np.abs(roundtrip - realization.compact))), 2.0e-12)

    def test_action_subtraction_and_moving_cut_identity(self) -> None:
        realization = realize_local_pole(
            self.parameters(),
            self.labels(),
            sigma_min=5.0e-4,
            sigma_cut=3.0e-3,
            points=100,
        )
        ladder = action_cutoff_ladder(realization, count=6)
        np.testing.assert_allclose(
            ladder.raw_action - ladder.divergent_part,
            ladder.subtracted_action,
            rtol=0.0,
            atol=2.0e-12,
        )
        self.assertTrue(np.all(np.isfinite(ladder.subtracted_action)))
        self.assertGreater(ladder.raw_action[-1], ladder.raw_action[0])
        self.assertLess(
            float(np.ptp(ladder.subtracted_action)),
            0.01 * float(np.ptp(ladder.raw_action)),
        )
        identity = moving_cut_additivity(
            realization,
            earlier_cut_sigma=2.8e-3,
            later_cut_sigma=1.8e-3,
            endpoint_sigma=7.0e-4,
        )
        self.assertLess(abs(identity["moving_cut_additivity_residual"]), 2.0e-7)


if __name__ == "__main__":
    unittest.main()
