from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from numerics.vdp_p2e_channel_scout import (
    DEFAULT_CONFIG,
    ScoutError,
    build_scout,
)


REPOSITORY = Path(__file__).resolve().parents[1]
SAVED_REPORT = (
    REPOSITORY / "numerics/results/vdp_p2e_channel_scout_v2/scout.json"
)


class VdpP2eChannelScoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
        cls.saved = json.loads(SAVED_REPORT.read_text(encoding="utf-8"))
        cls.recomputed, cls.arrays = build_scout()
        cls.saved_data_path = REPOSITORY / cls.saved["data"]["path"]
        cls.saved_arrays = np.load(cls.saved_data_path)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.saved_arrays.close()

    def test_fixed_point_and_partial_nonclaim_status_are_immutable(self) -> None:
        self.assertEqual(
            self.config["parameter_point"],
            {
                "r": "3/200",
                "a2": "0",
                "epsilon": "1",
                "required_relation": "STRICT_INTERIOR_OF_VDP_POSITIVE_BOX_V2",
            },
        )
        self.assertEqual(self.saved["status"], "PARTIAL_SCOUT_SUCCESS")
        self.assertEqual(self.saved["evidence_status"], "NON_EVIDENTIARY")
        self.assertEqual(self.saved["mathematical_status"], "INCONCLUSIVE")
        self.assertFalse(self.saved["claim_bearing"])
        self.assertEqual(
            self.saved["atlas_materialization_status"], "NOT_STARTED"
        )

    def test_archived_centerlines_match_the_single_replay(self) -> None:
        self.assertEqual(self.recomputed["channel_status"],
                         self.saved["channel_status"])
        for name, values in self.arrays.items():
            self.assertIn(name, self.saved_arrays.files)
            np.testing.assert_allclose(
                values, self.saved_arrays[name], rtol=2.0e-13, atol=2.0e-14
            )
        digest = hashlib.sha256(self.saved_data_path.read_bytes()).hexdigest()
        self.assertEqual(digest, self.saved["data"]["sha256"])

    def test_homoclinic_and_pole_use_real_ode_hit_functions(self) -> None:
        hom = self.saved["homoclinic"]
        pole = self.saved["pole"]
        self.assertEqual(hom["status"], "HOMOCLINIC_CHANNEL_SCOUT_SUCCESS")
        self.assertLess(hom["shooting_residual_inf"], 1.0e-10)
        self.assertLess(hom["kato_source_state_defect"], 1.0e-12)
        self.assertLess(hom["sampled_energy_drift"], 1.0e-10)
        self.assertGreater(hom["terminal_joint_event_speed"], 0.0)
        self.assertTrue(all(hom["qa"].values()))

        self.assertEqual(pole["status"], "POLE_CHANNEL_SCOUT_SUCCESS")
        self.assertIn("g_pole=U_central-(-10)", pole["gate_function"])
        self.assertLess(pole["gate_residual"], 1.0e-10)
        self.assertLess(pole["sampled_energy_drift"], 1.0e-12)
        self.assertLess(pole["pre_gate_sampled_maximum"], 0.0)
        self.assertGreater(pole["event_speed_physical"], 0.0)
        self.assertTrue(all(pole["qa"].values()))

    def test_centerline_shapes_and_reversibility_are_explicit(self) -> None:
        hom_xi = self.saved_arrays["hom_centered_xi"]
        hom_state = self.saved_arrays["hom_central_state"]
        self.assertEqual(hom_xi.shape, (1601,))
        self.assertEqual(hom_state.shape, (4, 1601))
        np.testing.assert_allclose(hom_xi, -hom_xi[::-1], atol=2.0e-14)
        reverser = np.array([1.0, -1.0, 1.0, -1.0])[:, None]
        np.testing.assert_allclose(
            hom_state, reverser * hom_state[:, ::-1], atol=2.0e-13
        )
        self.assertEqual(self.saved_arrays["pole_physical_state"].shape,
                         (4, 801))
        self.assertEqual(self.saved_arrays["pole_central_state"].shape,
                         (4, 801))
        self.assertTrue(np.all(np.diff(
            self.saved_arrays["pole_physical_x"]) > 0.0))

    def test_algebraic_raw_stop_is_preserved_without_retry(self) -> None:
        algebraic = self.saved["algebraic"]
        self.assertEqual(algebraic["status"], "ALGEBRAIC_CHANNEL_STOP")
        self.assertEqual(algebraic["attempts_used"], 1)
        self.assertEqual(algebraic["attempts_allowed"], 1)
        self.assertEqual(algebraic["failure"]["exception_type"], "ValueError")
        self.assertEqual(
            algebraic["failure"]["message"],
            "Q is not a forward coordinate when pi is nonpositive",
        )
        self.assertEqual(
            algebraic["failure"]["origin_function"], "normal_outer_rhs_q"
        )

    def test_saved_output_cannot_be_read_as_atlas_materialization(self) -> None:
        qa = self.saved["qa"]
        self.assertFalse(qa["contains_artificial_lateral"])
        self.assertFalse(qa["contains_incidence_census"])
        self.assertFalse(qa["contains_numeric_m0"])
        self.assertFalse(qa["theorem_faces_claimed"])
        combined = " ".join(self.saved["nonclaims"])
        for word in ("theorem face", "incidence complex", "numeric m0"):
            self.assertIn(word, combined)

    def test_source_hash_tamper_stops_before_any_solve(self) -> None:
        config = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
        config["source_bindings"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "tampered.json"
            path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(ScoutError, "source binding mismatch"):
                build_scout(path)


if __name__ == "__main__":
    unittest.main()
