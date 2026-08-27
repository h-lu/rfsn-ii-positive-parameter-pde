from __future__ import annotations

import json
import copy
import unittest
from pathlib import Path

from numerics.check_vdp_master import FIGURE_STEMS, OUTPUT, RAW_FILES, verify
from numerics.render_vdp_figures import validate_render_provenance
from numerics.run_vdp_master import (
    FROZEN_INTERFACE_KEYS,
    validate_frozen_config_interface,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "numerics" / "config" / "vdp_v1_v7.json"


class VdpMasterContractTests(unittest.TestCase):
    def test_frozen_configuration_has_all_stages_and_four_windows(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertGreaterEqual(config["configuration_version"], 4)
        self.assertIn("source_manifold", config)
        self.assertIn("pole_connection", config)
        self.assertIn("matched_outer", config)
        self.assertNotIn("pole", config)
        self.assertNotIn("cutoff_ladders", config)
        self.assertIn("outer", config)
        self.assertGreaterEqual(
            len(config["source_manifold"]["graph_horizon_ladder"]), 2
        )
        self.assertGreaterEqual(
            len(config["pole_connection"]["blowup_u_levels"]), 3
        )
        self.assertLess(
            config["matched_outer"]["label_q"],
            config["matched_outer"]["candidate_q_end"],
        )
        self.assertIn(
            config["matched_outer"]["candidate_q_end"],
            config["matched_outer"]["gamma_horizon_ladder"],
        )
        self.assertEqual(
            config["coded_patterns"]["multipulse_target_counts"], [1, 2, 3, 4]
        )
        self.assertEqual(len(config["coded_patterns"]["aperiodic_window_levels"]), 4)
        self.assertTrue(
            any("temporal stability" in item for item in config["nonclaims"])
        )

    def test_frozen_candidate_interface_has_no_silent_config_drift(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        validate_frozen_config_interface(config)
        for section, keys in FROZEN_INTERFACE_KEYS.items():
            self.assertEqual(set(config[section]), keys)

        injected = copy.deepcopy(config)
        injected["matched_outer"]["unused_future_knob"] = 1.0
        with self.assertRaisesRegex(ValueError, "configuration drift"):
            validate_frozen_config_interface(injected)

        missing = copy.deepcopy(config)
        del missing["events"]["nu_samples"]
        with self.assertRaisesRegex(ValueError, "configuration drift"):
            validate_frozen_config_interface(missing)

    def test_all_nine_figure_contract_stems_are_distinct(self) -> None:
        self.assertEqual(len(FIGURE_STEMS), 9)
        self.assertEqual(len(set(FIGURE_STEMS)), 9)

    def test_renderer_rejects_stale_configuration_manifest(self) -> None:
        validate_render_provenance(
            {"configuration_version": 4}, {"configuration_version": 4}
        )
        with self.assertRaisesRegex(ValueError, "stale render manifest"):
            validate_render_provenance(
                {"configuration_version": 4}, {"configuration_version": 3}
            )

    def test_candidate_artifacts_are_in_the_static_raw_contract(self) -> None:
        self.assertTrue(
            {
                "v4_v5_matched_candidate.json",
                "v4_v5_matched_candidate.npz",
                "v6_complete_branches.npz",
                "v6_candidate_contract.json",
            }.issubset(RAW_FILES)
        )
        # The two per-branch JSON records are discovered dynamically because
        # their filenames contain the frozen branch ids.
        self.assertNotIn("v6_complete_*.json", RAW_FILES)

    def test_saved_master_artifact_and_stop_rule_statuses(self) -> None:
        if not (OUTPUT / "manifest.json").exists():
            self.skipTest("run numerics/run_vdp_master.py before artifact verification")
        self.assertEqual(verify(), [])


if __name__ == "__main__":
    unittest.main()
