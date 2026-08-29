"""Regression tests for the finite-horizon V4/V5 matched candidate."""

from __future__ import annotations

import unittest

import numpy as np

from numerics.run_vdp_master import matched_outer_tail_pair, strict_v5a_composition
from numerics.rfsn_numerics import vdp_hamiltonian
from numerics.vdp_matched_outer import (
    COMPUTED_E1_MATCHED_CANDIDATE,
    NOT_INTERVAL_VALIDATED,
    MatchedOuterConfig,
    central_to_resolved_k1,
    compute_matched_outer_candidate,
    finite_horizon_gamma_continuation,
    k1_center_graph_leading_guess,
    matched_action_decomposition,
    matched_outer_refinement,
    outer_seam_coordinates,
    resolved_k1_to_outer_normal,
    true_wu_source_state_provider,
    zero_energy_source_proxy_provider,
)
from numerics.vdp_outer import OuterParameters


class SameSectionFormulaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parameters = OuterParameters(r=0.08, a2=0.0, epsilon=1.0)

    def test_qr_is_the_seam_and_not_the_downstream_label(self) -> None:
        z_r, q_r = outer_seam_coordinates(self.parameters, outer_r1=2.0)
        self.assertAlmostEqual(z_r, 0.2)
        self.assertAlmostEqual(q_r, 25.0)
        self.assertLess(q_r, 65.0)

    def test_leading_k1_guess_is_close_to_the_same_section_graph(self) -> None:
        _z_r, q_r = outer_seam_coordinates(self.parameters, outer_r1=2.0)
        leading = k1_center_graph_leading_guess(
            np.array([0.16, 2.0]), self.parameters
        )
        seam = resolved_k1_to_outer_normal(
            leading[:, -1], self.parameters, outer_r1=2.0
        )
        continuation = finite_horizon_gamma_continuation(
            self.parameters,
            (0.0, float(seam[0])),
            q_start=q_r,
            q_end=100.0,
            points=301,
            tolerance=2.0e-8,
        )
        self.assertEqual(
            continuation.evidence_status, COMPUTED_E1_MATCHED_CANDIDATE
        )
        self.assertEqual(continuation.validation_status, NOT_INTERVAL_VALIDATED)
        self.assertLess(abs(float(seam[1]) - continuation.samples[-1].gamma), 1e-8)
        self.assertLess(
            continuation.samples[-1].diagnostics["energy_residual_inf"], 1e-13
        )

    def test_true_wu_provider_is_cached_and_zero_energy_to_roundoff(self) -> None:
        provider = true_wu_source_state_provider(
            self.parameters,
            source_radius=0.01,
            flowback_tau=2.0,
            graph_horizon=6.0,
            graph_boundary_tolerance=2.0e-10,
        )
        first = provider(5.4)
        second = provider(5.4)
        np.testing.assert_array_equal(first, second)
        self.assertEqual(provider.unique_evaluations, 1)  # type: ignore[attr-defined]
        self.assertIn("nonlinear W^u", provider.source_model)  # type: ignore[attr-defined]
        self.assertEqual(  # type: ignore[attr-defined]
            provider.graph_boundary_tolerance, 2.0e-10
        )
        energy = vdp_hamiltonian(
            first[:, None],
            self.parameters.r,
            self.parameters.a2,
            self.parameters.epsilon,
        )
        self.assertLess(abs(float(energy[0])), 1e-10)

class MatchedCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parameters = OuterParameters(r=0.08, a2=0.0, epsilon=1.0)
        cls.config = MatchedOuterConfig(
            q_label=65.0,
            q_end=100.0,
            mesh_points=181,
            output_points=301,
            tolerance=8.0e-5,
            boundary_tolerance=1.0e-8,
            max_nodes=30_000,
        )
        cls.proxy = staticmethod(
            zero_energy_source_proxy_provider(
                cls.parameters, source_radius=cls.config.source_radius
            )
        )
        cls.candidate = compute_matched_outer_candidate(
            cls.parameters,
            cls.config,
            source_state_provider=cls.proxy,
        )

    def test_statuses_and_scope_are_explicit(self) -> None:
        candidate = self.candidate
        self.assertEqual(
            candidate.evidence_status, COMPUTED_E1_MATCHED_CANDIDATE
        )
        self.assertEqual(candidate.validation_status, NOT_INTERVAL_VALIDATED)
        self.assertTrue(candidate.diagnostics["finite_horizon_only"])
        self.assertIn("proxy", candidate.diagnostics["source_model"])

    def test_one_orbit_closes_both_interfaces_and_same_section_root(self) -> None:
        candidate = self.candidate
        diagnostics = candidate.diagnostics
        central_interface = central_to_resolved_k1(
            candidate.central_state[:, -1], self.parameters
        )
        outer_interface = resolved_k1_to_outer_normal(
            candidate.k1_state[:, -1],
            self.parameters,
            outer_r1=self.config.outer_r1,
        )
        np.testing.assert_allclose(
            candidate.k1_state[:, 0], central_interface, rtol=0.0, atol=2e-10
        )
        np.testing.assert_allclose(
            candidate.outer_state[:, 0], outer_interface, rtol=0.0, atol=2e-10
        )
        self.assertTrue(diagnostics["solver_success"])
        self.assertTrue(diagnostics["solver_rms_residual_passed"])
        self.assertLess(diagnostics["boundary_and_interface_residual_inf"], 1e-9)
        self.assertLess(abs(diagnostics["same_section_root_residual"]), 1e-9)
        self.assertTrue(diagnostics["same_section_root_passed"])
        self.assertLess(
            abs(diagnostics["central_k1_q1_interface_residual"]), 1e-8
        )

    def test_energy_arrival_and_label_separation_diagnostics(self) -> None:
        diagnostics = self.candidate.diagnostics
        self.assertLess(diagnostics["central_energy_residual_inf"], 1e-7)
        self.assertLess(diagnostics["k1_energy_residual_inf"], 1e-6)
        self.assertLess(diagnostics["outer_energy_residual_inf"], 1e-13)
        self.assertGreater(diagnostics["minimum_outer_pi"], 0.0)
        self.assertGreater(diagnostics["minimum_k1_pi_scaled"], 0.0)
        self.assertTrue(diagnostics["q_r_q_label_separated"])
        self.assertAlmostEqual(diagnostics["q_r"], 25.0)
        self.assertAlmostEqual(diagnostics["q_label"], 65.0)
        self.assertLess(
            abs(diagnostics["k1_seam_leading_guess_residual"]), 1e-8
        )
        self.assertEqual(diagnostics["beta_equals_delta_b_residual"], 0.0)
        self.assertTrue(diagnostics["scaled_arrival_margin_passed"])
        self.assertTrue(diagnostics["unscaled_arrival_margin_passed"])
        self.assertTrue(diagnostics["source_phase_in_bracket"])
        self.assertTrue(diagnostics["seam_beta_in_bracket"])
        self.assertGreater(diagnostics["source_phase_bracket_margin"], 0.0)
        self.assertGreater(diagnostics["seam_beta_bracket_margin"], 0.0)

    def test_full_matched_horizon_refinement_is_recomputed(self) -> None:
        refinement = matched_outer_refinement(
            (85.0, 100.0),
            self.parameters,
            MatchedOuterConfig(
                q_label=60.0,
                q_end=100.0,
                mesh_points=161,
                output_points=241,
                tolerance=1.0e-4,
                boundary_tolerance=1.0e-8,
                max_nodes=30_000,
            ),
            source_state_provider=self.proxy,
        )
        self.assertEqual(
            refinement.evidence_status, COMPUTED_E1_MATCHED_CANDIDATE
        )
        self.assertEqual(refinement.validation_status, NOT_INTERVAL_VALIDATED)
        np.testing.assert_allclose(refinement.q_end, np.array([85.0, 100.0]))
        self.assertTrue(np.isnan(refinement.consecutive_state_difference[0]))
        self.assertTrue(np.isfinite(refinement.consecutive_state_difference[1]))
        self.assertLess(refinement.consecutive_state_difference[1], 1e-7)

    def test_v5a_reference_is_normalized_at_the_later_fixed_cut(self) -> None:
        pair = matched_outer_tail_pair(self.candidate)
        q_star = float(self.config.q_label)
        self.assertAlmostEqual(pair.reference.compact_q[0], q_star)
        self.assertAlmostEqual(pair.neighboring.compact_q[0], q_star)
        self.assertAlmostEqual(pair.reference.beta[0], 0.0, places=14)
        self.assertAlmostEqual(
            pair.neighboring.beta[0],
            float(self.candidate.diagnostics["label_beta"]),
            places=14,
        )
        self.assertAlmostEqual(
            pair.neighboring.beta0, pair.neighboring.beta[0], places=14
        )
        self.assertGreater(q_star, float(self.candidate.diagnostics["q_r"]))

    def test_finite_v5_action_uses_all_three_matched_segments(self) -> None:
        decomposition = matched_action_decomposition(self.candidate)
        diagnostics = decomposition.diagnostics
        self.assertAlmostEqual(decomposition.outer_q[-1], self.config.q_label)
        self.assertTrue(diagnostics["terminal_is_fixed_v5a_normalization_cut"])
        self.assertLess(
            diagnostics["central_k1_physical_interface_defect_inf"], 1e-10
        )
        self.assertLess(
            diagnostics["k1_outer_physical_interface_defect_inf"], 1e-10
        )
        self.assertLess(
            diagnostics["central_density_pullback_relative_defect"], 2e-7
        )
        self.assertLess(diagnostics["k1_density_pullback_relative_defect"], 2e-6)
        self.assertLess(
            diagnostics["outer_density_physical_relative_defect"], 2e-5
        )
        self.assertLess(
            diagnostics[
                "k1_action_direct_vs_central_pullback_relative_defect"
            ],
            1e-4,
        )
        self.assertTrue(np.isfinite(decomposition.total_action))
        self.assertGreater(decomposition.total_length, 0.0)

    def test_v5a_strict_composition_keeps_reference_endpoint_correction(self) -> None:
        decomposition = matched_action_decomposition(self.candidate)
        pair = matched_outer_tail_pair(self.candidate)
        report = strict_v5a_composition(decomposition, pair)
        self.assertTrue(report["reference_endpoint_correction_included"])
        self.assertAlmostEqual(report["q_star"], self.config.q_label)
        self.assertEqual(len(report["cut_rows"]), 3)
        self.assertLess(report["maximum_scaled_balance_residual"], 1e-12)
        self.assertGreater(
            report[
                "minimum_scaled_residual_without_reference_endpoint_correction"
            ],
            1e-6,
        )
        self.assertEqual(
            report["status"], "EXACT/DERIVED_FINITE_GRID_BOOKKEEPING"
        )


if __name__ == "__main__":
    unittest.main()
