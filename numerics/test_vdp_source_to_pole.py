from __future__ import annotations

import json
import unittest

import numpy as np

from numerics.rfsn_numerics import CORE_SOURCE_STATE
from numerics.vdp_pole import PoleParameters, pole_energy_from_labels
from numerics.vdp_source_to_pole import (
    CORE_HOMOCLINIC_PHASE,
    SOURCE_TO_POLE_CANDIDATE_STATUS,
    THEOREM_VALIDATION_STATUS,
    WINDOW_CANDIDATE_STATUS,
    compute_pole_window_candidate,
    compute_source_to_pole_connection,
    finite_horizon_unstable_graph_state,
    physical_action_density,
    same_orbit_moving_cut_balance,
)


class VdpSourceToPoleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parameters = PoleParameters(r=0.08, a2=0.0, epsilon=1.0)
        cls.connection = compute_source_to_pole_connection(
            cls.parameters,
            phase=0.0,
            graph_horizon=8.0,
            comparison_horizon=6.0,
            graph_boundary_tolerance=2.0e-10,
            gate_section_x=10.0,
            label_fit_levels=(100.0, 200.0, 500.0),
            local_points=100,
        )
        cls.window = compute_pole_window_candidate(
            cls.parameters,
            phases=(-0.2, -0.1, 0.0, 0.1, 0.2),
            graph_horizon=8.0,
            graph_boundary_tolerance=2.0e-10,
            gate_section_x=10.0,
        )

    def test_core_true_unstable_graph_bvp_recovers_frozen_anchor(self) -> None:
        coordinates = 0.01 * np.array(
            [np.cos(CORE_HOMOCLINIC_PHASE), np.sin(CORE_HOMOCLINIC_PHASE)]
        )
        state, diagnostics = finite_horizon_unstable_graph_state(
            r=0.0,
            a2=0.0,
            epsilon=1.0,
            unstable_coordinates=coordinates,
            horizon=8.0,
        )
        self.assertLess(np.linalg.norm(state - CORE_SOURCE_STATE), 1.0e-9)
        self.assertLess(diagnostics["boundary_residual_inf"], 1.0e-10)
        self.assertLess(diagnostics["source_coordinate_residual_inf"], 1.0e-12)
        self.assertLess(diagnostics["central_energy_abs"], 1.0e-11)
        self.assertIn("nonlinear W^u", diagnostics["scope_note"])

    def test_v2_moving_source_horizon_and_energy_residuals(self) -> None:
        diagnostics = self.connection.source.diagnostics
        self.assertLess(diagnostics["core_graph_boundary_residual_inf"], 1.0e-10)
        self.assertLess(
            diagnostics["positive_graph_boundary_residual_inf"], 1.0e-10
        )
        self.assertLess(diagnostics["horizon_source_defect"], 1.0e-8)
        self.assertLess(diagnostics["source_central_energy_abs"], 1.0e-11)
        self.assertEqual(
            diagnostics["theorem_validation_status"], THEOREM_VALIDATION_STATUS
        )

    def test_closed_phase_window_enters_the_pole_cone_with_margin(self) -> None:
        window = self.window
        self.assertEqual(window.diagnostics["status"], WINDOW_CANDIDATE_STATUS)
        self.assertEqual(
            window.diagnostics["theorem_validation_status"],
            THEOREM_VALIDATION_STATUS,
        )
        self.assertEqual(window.phases.shape, (5,))
        self.assertTrue(np.all(window.cone_y > 20.0))
        self.assertTrue(np.all(window.cone_d > 40.0))
        self.assertTrue(np.all(window.cone_k > 200.0))
        self.assertTrue(np.all(window.cone_y_prime > 80.0))
        self.assertTrue(np.all(window.cone_k_prime > 1000.0))
        self.assertLess(window.diagnostics["maximum_gate_residual"], 1.0e-9)
        self.assertLess(window.diagnostics["maximum_source_energy_abs"], 1.0e-11)

    def test_same_physical_orbit_reaches_gate_and_all_pole_levels(self) -> None:
        connection = self.connection
        self.assertEqual(
            connection.diagnostics["status"], SOURCE_TO_POLE_CANDIDATE_STATUS
        )
        self.assertTrue(connection.diagnostics["same_physical_ivp_source_to_last_level"])
        self.assertLess(connection.gate.diagnostics["gate_residual"], 1.0e-9)
        self.assertEqual(connection.gate.diagnostics["gate_section_x"], 10.0)
        self.assertLess(
            connection.gate.diagnostics["source_to_gate_energy_drift"], 1.0e-8
        )
        self.assertTrue(np.all(np.diff(connection.end_fit.hit_x) > 0.0))
        self.assertTrue(np.all(np.diff(connection.end_fit.level_u) > 0.0))
        np.testing.assert_allclose(
            connection.end_fit.hit_state[0],
            connection.end_fit.level_u,
            rtol=0.0,
            atol=2.0e-8,
        )

    def test_pole_time_labels_and_local_overlap_pass_candidate_gates(self) -> None:
        connection = self.connection
        fit = connection.end_fit
        self.assertEqual(
            fit.diagnostics["label_fit_levels"], [100.0, 200.0, 500.0]
        )
        self.assertLess(fit.diagnostics["pole_time_last_three_spread"], 5.0e-8)
        self.assertLess(fit.diagnostics["z0_last_three_spread"], 1.0e-6)
        self.assertLess(fit.diagnostics["w0_last_three_spread"], 1.0e-6)
        self.assertLess(abs(fit.diagnostics["label_energy_defect"]), 1.0e-9)
        self.assertLess(
            connection.diagnostics["global_local_physical_relative_defect_inf"],
            5.0e-4,
        )
        self.assertLess(
            connection.diagnostics["global_local_compact_relative_defect_inf"],
            5.0e-4,
        )
        target_energy = -self.parameters.epsilon * (
            self.parameters.a**4 / 12.0 - self.parameters.a**2 / 2.0
        )
        self.assertAlmostEqual(
            pole_energy_from_labels(self.parameters, fit.labels),
            target_energy,
            places=9,
        )
        self.assertGreater(fit.labels.kappa, 1.0e6)

    def test_same_orbit_action_ladder_has_v3_subtraction_and_stable_tail(self) -> None:
        connection = self.connection
        ladder = connection.action_ladder
        np.testing.assert_array_equal(
            ladder.raw_action - ladder.divergent_part,
            ladder.subtracted_action,
        )
        self.assertTrue(np.all(np.isfinite(ladder.raw_action)))
        self.assertTrue(np.all(np.diff(ladder.raw_action) > 0.0))
        self.assertLess(
            ladder.diagnostics["physical_compact_density_relative_defect_inf"],
            1.0e-12,
        )
        self.assertLess(
            ladder.diagnostics["last_three_subtracted_spread"], 2.0e-2
        )
        successive_changes = np.abs(np.diff(ladder.subtracted_action))
        self.assertTrue(np.all(np.diff(successive_changes) < 0.0))
        self.assertLess(successive_changes[-1], 6.0e-3)
        source_density = physical_action_density(
            connection.physical_state[:, 0], self.parameters
        )
        expected = (
            self.parameters.epsilon * connection.physical_state[1, 0] ** 2
            - connection.physical_state[3, 0] ** 2
        ) / self.parameters.delta
        self.assertAlmostEqual(float(source_density), float(expected), places=14)
        self.assertEqual(
            ladder.diagnostics["theorem_validation_status"],
            THEOREM_VALIDATION_STATUS,
        )

    def test_same_orbit_moving_cut_identity(self) -> None:
        balance = same_orbit_moving_cut_balance(
            self.connection,
            earlier_cut_x=0.0,
            later_cut_x=self.connection.gate.physical_time,
            endpoint_sigma=8.0e-5,
        )
        self.assertLess(abs(balance["moving_cut_additivity_residual"]), 1.0e-8)
        self.assertAlmostEqual(
            balance["finite_part_earlier_cut"],
            balance["finite_segment_action"]
            + balance["finite_part_later_cut"],
            places=8,
        )

    def test_refined_physical_integration_keeps_gate_and_labels(self) -> None:
        refined = compute_source_to_pole_connection(
            self.parameters,
            phase=0.0,
            graph_horizon=8.0,
            comparison_horizon=None,
            local_points=60,
            rtol=4.0e-12,
            atol=4.0e-14,
            max_step_x=8.0e-4,
        )
        self.assertLess(
            abs(refined.gate.physical_time - self.connection.gate.physical_time),
            1.0e-7,
        )
        self.assertLess(
            abs(refined.end_fit.labels.z0 - self.connection.end_fit.labels.z0),
            1.0e-6,
        )
        self.assertLess(
            abs(refined.end_fit.labels.w0 - self.connection.end_fit.labels.w0),
            1.0e-6,
        )
        self.assertLess(
            abs(
                refined.action_ladder.subtracted_action[-1]
                - self.connection.action_ladder.subtracted_action[-1]
            ),
            1.0e-4,
        )
        self.assertEqual(
            refined.diagnostics["theorem_validation_status"],
            THEOREM_VALIDATION_STATUS,
        )

    def test_outputs_are_json_and_npz_ready_without_object_arrays(self) -> None:
        json.dumps(self.connection.as_json_dict(), allow_nan=False)
        json.dumps(self.window.as_json_dict(), allow_nan=False)
        payload = self.connection.as_npz_payload()
        self.assertIn("global_on_local_sigma", payload)
        self.assertIn("physical_action", payload)
        self.assertIn("action_subtracted", payload)
        for value in payload.values():
            self.assertNotEqual(np.asarray(value).dtype, object)


if __name__ == "__main__":
    unittest.main()
