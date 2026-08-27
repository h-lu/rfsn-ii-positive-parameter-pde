"""Fast regression tests for the V4--V5A numerical probes."""

from __future__ import annotations

import unittest

import numpy as np

from numerics.vdp_outer import (
    COMPUTED_E1,
    NOT_NUMERICALLY_RESOLVED,
    OuterParameters,
    central_section_to_k1,
    compactified_outer_rhs_tau,
    energy_equation_residual,
    finite_horizon_tail_pair,
    frozen_exchange_pairing,
    gauge_composition_balance,
    k1_to_outer,
    leading_counterterm_differences,
    matching_determinant_proxy,
    numerical_cut_balance,
    outer_asymptotic_diagnostics,
    positive_energy_root,
    reference_change_balance,
    reference_subtracted_integrals,
    terminal_potential_transfer,
    v5_matching_status,
)


class ExactOuterFormulaTests(unittest.TestCase):
    def test_positive_energy_root_and_exact_field(self) -> None:
        parameters = OuterParameters(r=0.2, a2=0.1, epsilon=1.1)
        z = np.array([0.12, 0.16, 0.20])
        beta = np.array([1.0e-4, -1.5e-4, 2.0e-4])
        alpha = np.array([2.0e-4, 1.0e-4, -1.0e-4])
        chi = positive_energy_root(z, beta, alpha, parameters)
        residual = energy_equation_residual(z, beta, alpha, chi, parameters)
        self.assertTrue(np.all(chi > 0.0))
        self.assertLess(float(np.max(np.abs(residual))), 5.0e-15)

        rhs = compactified_outer_rhs_tau(
            np.array([z[0], 0.04, -0.002, chi[0]]), parameters
        )
        self.assertEqual(rhs.shape, (4,))
        self.assertLess(rhs[0], 0.0)

    def test_exact_chart_crosswalk_and_unresolved_matching_label(self) -> None:
        parameters = OuterParameters(r=0.08, a2=0.0, epsilon=1.0)
        k1 = central_section_to_k1(
            parameters, section_m=4.0, p2=0.7, v2=-0.2, q2=0.5
        )
        outer = k1_to_outer(
            r1=k1["r1"],
            delta1=k1["delta1"],
            p1=k1["p1"],
            v1=k1["v1"],
            q1=k1["q1"],
            epsilon=parameters.epsilon,
        )
        self.assertLess(abs(outer["h_identity_residual"]), 2.0e-19)
        self.assertAlmostEqual(frozen_exchange_pairing(), 144.0 * np.sqrt(3.0))
        self.assertAlmostEqual(matching_determinant_proxy(-2.0, 3.0), -6.0)
        status = v5_matching_status(parameters)
        self.assertEqual(status["status"], NOT_NUMERICALLY_RESOLVED)
        self.assertIsNone(status["computed_positive_parameter_exchange"])
        self.assertIsNone(status["computed_matching_determinant"])


class OuterFinitePartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parameters = OuterParameters(r=0.2, a2=0.0, epsilon=1.0)
        cls.pair = finite_horizon_tail_pair(
            cls.parameters,
            2.0e-4,
            q_start=16.0,
            q_end=36.0,
            points=601,
            tolerance=4.0e-7,
        )
        cls.arrays = reference_subtracted_integrals(cls.pair)

    def test_zero_energy_same_q_tails_and_asymptotics(self) -> None:
        reference = self.pair.reference
        neighboring = self.pair.neighboring
        self.assertEqual(reference.evidence_status, COMPUTED_E1)
        self.assertTrue(reference.diagnostics["solver_success"])
        self.assertTrue(neighboring.diagnostics["solver_success"])
        self.assertLess(reference.diagnostics["energy_residual_inf"], 2.0e-14)
        self.assertLess(neighboring.diagnostics["energy_residual_inf"], 2.0e-14)
        self.assertGreater(reference.diagnostics["minimum_pi"], 0.0)
        initial_gap = abs(neighboring.beta[0] - reference.beta[0])
        terminal_gap = abs(neighboring.beta[-1] - reference.beta[-1])
        self.assertAlmostEqual(initial_gap, 2.0e-4, places=10)
        self.assertLess(terminal_gap, initial_gap * 1.0e-5)

        diagnostics = outer_asymptotic_diagnostics(self.pair)
        self.assertTrue(diagnostics["physical_distance_increases"])
        self.assertTrue(diagnostics["counterterm_action_diverges_negative"])
        self.assertEqual(diagnostics["matching_status"], NOT_NUMERICALLY_RESOLVED)
        self.assertGreater(diagnostics["length_counterterm_at_q_end"], 0.0)
        self.assertLess(diagnostics["action_counterterm_at_q_end"], 0.0)
        self.assertLess(
            abs(
                diagnostics["length_density_scaled"]
                / diagnostics["length_density_scaled_limit"]
                - 1.0
            ),
            0.35,
        )
        self.assertLess(
            abs(
                diagnostics["action_density_scaled"]
                / diagnostics["action_density_scaled_limit"]
                - 1.0
            ),
            0.35,
        )
        self.assertLess(abs(diagnostics["renormalized_length_tail_change"]), 1.0e-9)
        self.assertLess(abs(diagnostics["renormalized_action_tail_change"]), 1.0e-7)

    def test_counterterms_and_cut_reference_gauge_balances(self) -> None:
        q = self.arrays.compact_q
        self.assertTrue(np.all(np.diff(self.arrays.counterterm_length) > 0.0))
        self.assertLess(self.arrays.counterterm_action[-1], 0.0)
        leading_length, leading_action = leading_counterterm_differences(
            q, self.parameters, q_start=float(q[0])
        )
        self.assertGreater(leading_length[-1], 0.0)
        self.assertLess(leading_action[-1], 0.0)

        length_difference_density = (
            self.pair.neighboring.length_density
            - self.pair.reference.length_density
        )
        action_difference_density = (
            self.pair.neighboring.action_density
            - self.pair.reference.action_density
        )
        self.assertLess(
            abs(numerical_cut_balance(q, length_difference_density, q.size // 2)),
            2.0e-14,
        )
        self.assertLess(
            abs(numerical_cut_balance(q, action_difference_density, q.size // 2)),
            2.0e-12,
        )

        synthetic_reference = self.pair.reference.action_density + 0.02 * np.exp(
            -(q - q[0])
        )
        self.assertLess(
            abs(
                reference_change_balance(
                    q,
                    self.pair.neighboring.action_density,
                    self.pair.reference.action_density,
                    synthetic_reference,
                )
            ),
            2.0e-12,
        )
        self.assertEqual(gauge_composition_balance(2.0, -0.7, 0.4, -1.2, 3.1), 0.0)
        self.assertAlmostEqual(terminal_potential_transfer(5.0, 1.25, -0.5), 3.25)


if __name__ == "__main__":
    unittest.main()
