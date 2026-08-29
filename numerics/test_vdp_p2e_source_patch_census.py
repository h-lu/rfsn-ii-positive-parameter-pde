"""Regression checks for the prospectively frozen v2 source-patch census."""

from __future__ import annotations

import hashlib
import json
import unittest

from numerics import vdp_p2e_source_patch_census as census


class SourcePatchCensusTests(unittest.TestCase):
    def test_frozen_grid_has_one_hundred_points(self) -> None:
        config = census.load_config()
        phase_count = sum(
            len(patch["phase_offsets"]) for patch in config["patches"]
        )
        self.assertEqual(phase_count, 20)
        self.assertEqual(len(config["nu_values"]), 5)
        self.assertEqual(phase_count * len(config["nu_values"]), 100)

    def test_result_is_bound_when_present(self) -> None:
        if not census.DEFAULT_RESULT.is_file():
            self.skipTest("retained source-patch result has not been run yet")
        result = json.loads(census.DEFAULT_RESULT.read_text(encoding="utf-8"))
        self.assertEqual(
            result["schema_version"],
            "rfsn-vdp-p2e-source-patch-census-result/1",
        )
        self.assertEqual(result["sample_count"], 100)
        self.assertFalse(result["claim_bearing"])
        self.assertEqual(result["mathematical_status"], "INCONCLUSIVE")
        self.assertEqual(
            result["configuration"]["sha256"],
            hashlib.sha256(census.DEFAULT_CONFIG.read_bytes()).hexdigest(),
        )
        arrays = census.REPOSITORY / result["arrays"]["path"]
        self.assertEqual(
            result["arrays"]["sha256"],
            hashlib.sha256(arrays.read_bytes()).hexdigest(),
        )


if __name__ == "__main__":
    unittest.main()
