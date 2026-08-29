"""Archive and formula checks for the fixed v2 V4 graph slice."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import numpy as np

from numerics.vdp_outer import (
    OuterParameters,
    energy_equation_residual,
    normal_outer_state,
)
from numerics.vdp_v4_future_graph_slice import normal_nullcline_alpha


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent
CONFIG = HERE / "config/vdp_v4_future_graph_slice_v2.json"
RESULT = HERE / "results/vdp_v4_future_graph_slice_v2/result.json"
DATA = HERE / "results/vdp_v4_future_graph_slice_v2/slice.npz"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class V4FutureGraphSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.data = np.load(DATA)

    def test_matched_centerline_inputs_are_bound(self) -> None:
        binding = self.config["matched_centerline_binding"]
        self.assertEqual(
            sha256(REPOSITORY / binding["report_path"]),
            binding["report_sha256"],
        )
        self.assertEqual(
            sha256(REPOSITORY / binding["data_path"]),
            binding["data_sha256"],
        )

    def test_status_remains_nonclaiming(self) -> None:
        self.assertEqual(
            self.result["status"], "V4_FUTURE_GRAPH_SLICE_COMPUTED"
        )
        self.assertEqual(
            self.result["evidence_status"],
            "COMPUTED/E1_NON_RIGOROUS_WITH_QA",
        )
        self.assertEqual(self.result["mathematical_status"], "INCONCLUSIVE")
        self.assertFalse(self.result["claim_bearing"])
        self.assertTrue(all(self.result["qa"].values()))

    def test_axis_log_pi_binding_update_is_explicit(self) -> None:
        update = self.result["binding_update"]
        self.assertFalse(update["qa_status_changed"])
        self.assertEqual(
            update["source_commits_on_integration"], ["e348fa8", "6ab05a0"]
        )
        self.assertNotEqual(
            update["report_sha256"]["superseded"],
            update["report_sha256"]["current"],
        )
        np.testing.assert_allclose(
            self.data["binding_energy_H_superseded_current"],
            np.array(
                [2.1287391499046257e-14, 1.6531401306609465e-14]
            ),
            rtol=0.0,
            atol=0.0,
        )
        self.assertEqual(
            self.data["binding_headline_metrics_superseded_current"].shape,
            (8, 2),
        )

    def test_two_constructions_and_horizon_ladder_agree(self) -> None:
        diagnostics = self.result["diagnostics"]
        thresholds = self.result["thresholds"]
        self.assertLessEqual(
            diagnostics["horizon_seam_gamma_spread_max"],
            thresholds["horizon_seam_gamma_spread_upper"],
        )
        self.assertLessEqual(
            diagnostics["method_seam_gamma_difference_abs_max"],
            thresholds["method_seam_gamma_difference_upper"],
        )
        self.assertLessEqual(
            diagnostics["method_common_state_difference_inf"],
            thresholds["method_common_state_difference_upper"],
        )
        self.assertEqual(self.data["collocation_alpha"].shape, (3, 3, 7))
        self.assertEqual(self.data["shooting_alpha"].shape, (3, 7))

    def test_saved_states_satisfy_exact_energy_relation(self) -> None:
        parameters = OuterParameters(r=3.0 / 200.0, a2=0.0, epsilon=1.0)
        energy = float(self.result["fixed_energy"])
        q = self.data["common_Q"]
        beta = self.data["collocation_beta"][-1]
        alpha = self.data["collocation_alpha"][-1]
        chi = self.data["collocation_chi"][-1]
        residual = energy_equation_residual(
            q[np.newaxis, :] ** -0.5,
            beta,
            alpha,
            chi,
            parameters,
            energy=energy,
        )
        self.assertLessEqual(
            float(np.max(np.abs(residual))),
            self.result["thresholds"]["energy_residual_upper"],
        )
        _chi, pi, _w = normal_outer_state(
            q[np.newaxis, :] ** -0.5,
            beta,
            alpha,
            parameters,
            energy=energy,
        )
        self.assertGreater(
            float(np.min(pi)), self.result["thresholds"]["minimum_pi_lower"]
        )

    def test_terminal_model_and_rate_proxies_are_recorded(self) -> None:
        parameters = OuterParameters(r=3.0 / 200.0, a2=0.0, epsilon=1.0)
        energy = float(self.result["fixed_energy"])
        q_end = float(self.result["collocation_Q_end_ladder"][-1])
        last = self.result["diagnostics"]["collocation"][-1]
        target = normal_nullcline_alpha(
            q_end,
            float(last["terminal_beta"]),
            parameters,
            energy=energy,
            alpha_half_width=float(
                self.config["sampled_corridor"]["alpha_half_width"]
            ),
        )
        self.assertAlmostEqual(target, float(last["terminal_alpha"]), places=17)
        self.assertLessEqual(
            self.result["diagnostics"]["invariance_residual_inf"],
            self.result["thresholds"]["invariance_residual_upper"],
        )
        self.assertGreaterEqual(
            self.result["diagnostics"]["third_order_bunching_rate_min"],
            self.result["thresholds"]["third_order_bunching_rate_lower"],
        )
        self.assertEqual(self.data["rate_bunching_gamma_j"].shape, (4, 4))


if __name__ == "__main__":
    unittest.main()
