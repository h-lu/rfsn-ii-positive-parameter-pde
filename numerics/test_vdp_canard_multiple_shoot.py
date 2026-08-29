from __future__ import annotations

import json
import unittest

from numerics.vdp_canard_multiple_shoot import (
    CONFIG_PATH,
    RESULT_PATH,
    central_field,
    left_state_and_derivative,
    load_configuration,
)
from numerics.vdp_canard_splitting_scout import central_hamiltonian


class CanardMultipleShootTests(unittest.TestCase):
    def test_frozen_problem_and_left_energy_root(self) -> None:
        config = load_configuration()
        parameters = config["parameters"]
        state, derivative = left_state_and_derivative(
            u=parameters["outer_u2"],
            q=parameters["outer_q2"],
            a2=config["initialization_only"]["a2_seed"],
            r=parameters["r"],
        )
        self.assertEqual(config["multiple_shooting"]["segments"], 80)
        self.assertLess(state[1], 0.0)
        self.assertLess(
            abs(
                central_hamiltonian(
                    state, r=parameters["r"], a2=config["initialization_only"]["a2_seed"]
                )
            ),
            1e-10,
        )
        self.assertEqual(derivative[[0, 2, 3]].tolist(), [0.0, 0.0, 0.0])

    def test_parameter_forcing_has_the_frozen_sign(self) -> None:
        config = load_configuration()
        state = [1.0, 2.0, 3.0, 4.0]
        field = central_field(state, r=0.08, a2=-0.01)
        self.assertAlmostEqual(field[3], 1.0008)

    def test_saved_report_is_fail_closed_or_a_floating_candidate(self) -> None:
        if not RESULT_PATH.exists():
            self.skipTest("retained result is created only after the freeze commit")
        report = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        self.assertFalse(report["claim_bearing"])
        self.assertEqual(report["definition"]["segments"], 80)
        self.assertIn(
            report["decision"]["status"],
            {
                "COMPUTED/E1_BOUNDARY_SELECTED_MULTIPLE_SHOOT_SIMPLE_ZERO_CANDIDATE",
                "INCONCLUSIVE_MULTIPLE_SHOOT_ACCEPTANCE_OR_DERIVATIVE_FAILED",
            },
        )
        self.assertEqual(
            report["decision"]["intrinsic_maximal_canard"], "NOT_ESTABLISHED"
        )

    def test_retained_root_passes_but_simple_zero_does_not(self) -> None:
        if not RESULT_PATH.exists():
            self.skipTest("retained result is created only after the freeze commit")
        report = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        self.assertTrue(report["retained_root"]["checks_pass"])
        self.assertLess(
            report["retained_root"]["checks"]["tight_segment_replay_inf"],
            2e-7,
        )
        self.assertFalse(report["splitting_derivative"]["checks_pass"])
        self.assertGreater(
            report["splitting_derivative"]["fixed_family_jacobian_condition_2"],
            1e15,
        )
        self.assertEqual(
            report["decision"]["status"],
            "INCONCLUSIVE_MULTIPLE_SHOOT_ACCEPTANCE_OR_DERIVATIVE_FAILED",
        )


if __name__ == "__main__":
    unittest.main()
