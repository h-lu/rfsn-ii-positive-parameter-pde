from __future__ import annotations

import hashlib
import json
import unittest

import numpy as np

from numerics.vdp_canard_invariant_graph_scout import (
    CONFIG_PATH,
    RESULT_PATH,
    STOP_STATUS,
    build_report,
    chebyshev_grid_and_derivative,
    load_configuration,
)


class CanardInvariantGraphScoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_configuration()
        cls.report = build_report()

    def test_chebyshev_derivative_is_exact_on_quadratics(self) -> None:
        nodes, derivative = chebyshev_grid_and_derivative(9, [1.0, 1.2])
        np.testing.assert_allclose(derivative @ nodes, 1.0, atol=2e-13)
        np.testing.assert_allclose(
            derivative @ (nodes * nodes), 2.0 * nodes, atol=3e-13
        )

    def test_frozen_rectangles_overlap_the_target_away_from_the_fold(self) -> None:
        target_u = self.config["entry"]["physical_u"]
        overlap = self.config["predeclared_overlap"]
        self.assertLess(overlap["u_interval"][0], target_u)
        self.assertLess(target_u, overlap["u_interval"][1])
        gate = self.config["singular_normal_hyperbolicity_gate"]
        for rectangle in self.config["rectangles"]:
            self.assertGreater(
                rectangle["u_interval"][0] ** 2 - 1.0,
                gate["strict_lower_bound"],
            )

    def test_both_collocations_stop_before_entry_or_tangent(self) -> None:
        self.assertEqual(self.report["decision"]["status"], STOP_STATUS)
        self.assertIsNone(self.report["decision"]["intrinsic_Wcu_entry"])
        self.assertIsNone(self.report["decision"]["a2_tangent"])
        self.assertFalse(self.report["claim_bearing"])
        for row in self.report["rectangles"]:
            self.assertFalse(row["residual_gate_pass"])
            self.assertGreater(row["best_residual_inf"], 1e3 * row["residual_stop"])
            self.assertGreater(row["finite_normal_gap_at_best_iterate"], 0.2)
            newton = row["newton_diagnostic"]
            self.assertGreater(newton["condition_1_from_lu"], 1e15)
            self.assertGreater(
                newton["full_step_residual_inf"], row["best_residual_inf"]
            )

    def test_saved_stop_report_is_the_fresh_replay(self) -> None:
        saved = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(saved, self.report)
        self.assertEqual(
            self.report["configuration"]["sha256"],
            hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
