"""Archive checks for the fixed-center V5 endpoint calculation."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent
CONFIG = HERE / "config/vdp_v5_endpoint_exchange_v2.json"
RESULT = HERE / "results/vdp_v5_endpoint_exchange_v2/result.json"
DATA = HERE / "results/vdp_v5_endpoint_exchange_v2/adjoint.npz"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class V5EndpointExchangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(CONFIG.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.data = np.load(DATA)

    def test_inputs_are_immutably_bound(self) -> None:
        for binding in self.config["input_bindings"]:
            self.assertEqual(
                sha256(REPOSITORY / binding["path"]), binding["sha256"]
            )

    def test_status_is_computed_but_nonclaiming(self) -> None:
        self.assertEqual(
            self.result["status"], "V5_ENDPOINT_EXCHANGE_COMPUTED"
        )
        self.assertEqual(
            self.result["evidence_status"],
            "COMPUTED/E1_NON_RIGOROUS_WITH_QA",
        )
        self.assertEqual(self.result["mathematical_status"], "INCONCLUSIVE")
        self.assertFalse(self.result["claim_bearing"])
        self.assertTrue(all(self.result["qa"].values()))

    def test_endpoint_compatibility_is_not_exchange(self) -> None:
        compatibility = float(
            self.data["endpoint_left_row_ell_plus"]
            @ self.data["endpoint_incoming_tangent_T_plus"]
        )
        self.assertAlmostEqual(
            compatibility,
            self.result["diagnostics"][
                "endpoint_compatibility_ell_plus_T_plus"
            ],
            places=30,
        )
        self.assertLess(abs(compatibility), 1.0e-14)
        exchange = float(
            self.data["positive_Jost_row"]
            @ self.data["frozen_growing_complement"]
        )
        self.assertAlmostEqual(
            exchange, self.result["diagnostics"]["positive_exchange"]
        )
        self.assertGreater(exchange, 0.0)

    def test_frozen_pairing_and_transport_crosschecks(self) -> None:
        target = 144.0 * np.sqrt(3.0)
        pairing = self.data["jost_symplectic_pairing"]
        np.testing.assert_allclose(pairing, target, rtol=0.0, atol=2.0e-12)
        direction_error = np.max(
            np.linalg.norm(
                self.data["adjoint_unit_row"]
                - self.data["adjoint_ratio_unit_row"],
                axis=0,
            )
        )
        self.assertLessEqual(
            direction_error,
            self.result["thresholds"][
                "full_adjoint_projective_ratio_difference_upper"
            ],
        )
        self.assertGreater(
            self.result["diagnostics"]["adjoint"][
                "central_log_raw_row_norm"
            ],
            9.0e4,
        )

    def test_outer_row_and_intrinsic_row_annihilate_tangencies(self) -> None:
        self.assertLessEqual(
            abs(
                float(
                    self.data["outer_raw_row_beta_alpha_H"]
                    @ self.data["outer_graph_tangent"]
                )
            ),
            self.result["thresholds"][
                "endpoint_graph_tangent_pairing_abs_upper"
            ],
        )
        self.assertLessEqual(
            abs(
                float(
                    self.data["outer_raw_row_beta_alpha_H"]
                    @ self.data["outer_graph_energy_tangent"]
                )
            ),
            self.result["thresholds"][
                "endpoint_graph_tangent_pairing_abs_upper"
            ],
        )
        np.testing.assert_allclose(
            self.data["outer_map_jacobian_exact"],
            self.data["outer_map_jacobian_finite_difference"],
            rtol=0.0,
            atol=self.result["thresholds"][
                "outer_map_jacobian_crosscheck_inf_upper"
            ],
        )

    def test_full_energy_direction_is_computed_and_reaches_jost_row(self) -> None:
        diagnostics = self.result["diagnostics"]
        energy = diagnostics["outer_graph_energy_sensitivity"]
        self.assertNotEqual(diagnostics["gamma_H_at_outer_seam"], 0.0)
        self.assertLessEqual(
            energy["Gamma_H_finite_difference_relative"],
            self.result["thresholds"][
                "graph_energy_sensitivity_finite_difference_relative_upper"
            ],
        )
        self.assertGreater(diagnostics["Jost_row_frozen_row_cosine"], 0.999999)
        self.assertNotEqual(float(self.data["positive_Jost_row"][3]), 0.0)
        self.assertLessEqual(
            self.result["diagnostics"][
                "central_intrinsic_flow_pairing_relative"
            ],
            self.result["thresholds"][
                "intrinsic_flow_pairing_relative_upper"
            ],
        )

    def test_matching_jacobian_archive_is_invertible_at_center(self) -> None:
        jacobian = self.data["matching_jacobian"]
        singular_values = np.linalg.svd(jacobian, compute_uv=False)
        np.testing.assert_allclose(
            singular_values,
            self.data["matching_singular_values"],
            rtol=2.0e-15,
            atol=0.0,
        )
        self.assertGreaterEqual(
            singular_values[-1],
            self.result["thresholds"]["matching_sigma_min_lower"],
        )
        self.assertLessEqual(
            singular_values[0] / singular_values[-1],
            self.result["thresholds"]["matching_condition_number_upper"],
        )
        determinant_factor = (
            self.result["diagnostics"]["central_section_speed"]
            * self.result["diagnostics"]["source_phase_incidence"]
        )
        self.assertAlmostEqual(np.linalg.det(jacobian), determinant_factor)


if __name__ == "__main__":
    unittest.main()
