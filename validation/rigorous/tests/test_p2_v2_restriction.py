from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from validation.rigorous import p2_v2_restriction as restriction


class P2V2RestrictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = restriction.build_certificate()

    def temporary_config(self, value: dict) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "restriction.json"
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return path

    def test_complete_restricted_atom_set_and_schema(self) -> None:
        certificate = self.certificate
        self.assertEqual(restriction.schema_errors(certificate), [])
        self.assertEqual(certificate["restriction_status"],
                         restriction.RESTRICTION_STATUS)
        self.assertEqual(certificate["integrity_status"], "PASS")
        self.assertEqual(certificate["mathematical_status"],
                         restriction.RESTRICTION_STATUS)
        self.assertEqual(len(certificate["atoms"]), 32)
        self.assertEqual(
            tuple(item["id"] for item in certificate["atoms"]),
            restriction.ALL_REQUIRED_ATOMS,
        )
        self.assertTrue(all(
            item["restriction_status"] == restriction.RESTRICTION_STATUS
            and item["constants"] == "INHERITED_UNCHANGED"
            for item in certificate["atoms"]
        ))

    def test_exact_domains_and_inherited_normalization(self) -> None:
        domains = self.certificate["domains"]
        self.assertEqual(domains["relations"], {
            "restricted_bridge_is_strict_subset": True,
            "transverse_ranges_equal": True,
            "anchor_face_equal": True,
            "restricted_positive_box_is_subset": True,
            "source_and_restricted_positive_boxes_are_disjoint": True,
        })
        normalization = domains["inherited_parameter_normalization"]
        self.assertFalse(normalization["reparameterized"])
        self.assertEqual(normalization["v2_bridge_theta_r"], {
            "lower": {"numerator": "-1", "denominator": "1"},
            "upper": {"numerator": "-1", "denominator": "2"},
        })
        self.assertEqual(normalization["v2_box_theta_r"], {
            "lower": {"numerator": "-3", "denominator": "4"},
            "upper": {"numerator": "-1", "denominator": "2"},
        })
        self.assertEqual(
            domains["source_positive_box"]["inheritance"],
            "NOT_INHERITED_DISJOINT_FROM_V2_TARGET",
        )

    def test_grid_alignment_is_not_a_new_numerical_claim(self) -> None:
        records = {item["stage"]: item
                   for item in self.certificate["grid_restrictions"]}
        self.assertEqual(records["P2b"]["selected_r_indices"], list(range(4)))
        self.assertEqual(records["P2b"]["selected_cell_count"], 256)
        self.assertEqual(records["P2bK"]["selected_cell_count"], 128)
        self.assertEqual(records["P2d-frame"]["selected_cell_count"], 128)
        self.assertEqual(records["P2c"]["selected_r_indices"], list(range(8)))
        self.assertEqual(
            records["P2c"]["restricted_positive_target_r_indices"],
            list(range(4, 8)),
        )
        self.assertEqual(records["P2c"]["selected_cell_count"], 4096)
        self.assertEqual(records["P2c"]["selected_internal_face_count"], 10720)
        self.assertTrue(all(
            item["role"] == "ALIGNMENT_CHECK_ONLY_NO_RECOMPUTED_HULL"
            for item in records.values()
        ))
        principle = self.certificate["restriction_principle"]
        self.assertFalse(principle["interval_monotonicity_assumed"])
        self.assertFalse(principle["new_numerical_enclosures_claimed"])

    def test_overlap_restricts_to_one_anchor_chart(self) -> None:
        overlap = self.certificate["p2d_overlap_restriction"]
        self.assertEqual(overlap["nonempty_v2_members"], ["anchor"])
        self.assertTrue(overlap["anchor_member_covers_v2"])
        self.assertFalse(overlap["positive_member_intersects_v2"])
        self.assertFalse(overlap["v1_nonempty_overlap_intersects_v2"])
        self.assertEqual(
            overlap["transition_obligation_on_v2"],
            "VACUOUS_SINGLE_ANCHOR_CHART",
        )
        self.assertEqual(
            overlap["parent_exact_chart_basis"],
            "RESTRICTION_OF_ONE_GLOBAL_NORMALIZED_MOSER_FAMILY",
        )
        by_atom = {item["id"]: item for item in self.certificate["atoms"]}
        self.assertEqual(
            by_atom["V2.CHART.OVERLAPS"]["restriction_kind"],
            "SINGLE_ANCHOR_CHART_VACUOUS_TRANSITION",
        )
        self.assertEqual(
            by_atom["V2.EXACT_CHART"]["restriction_kind"],
            "ALL_SEVEN_RESTRICTED_CHILDREN",
        )

    def test_claim_and_replay_boundary_is_not_promoted(self) -> None:
        certificate = self.certificate
        self.assertEqual(certificate["final_status"], "INCONCLUSIVE")
        self.assertFalse(certificate["claim_bearing"])
        self.assertFalse(certificate["release_eligible"])
        self.assertEqual(certificate["independent_replay"], {
            "required_distinct_machines": 2,
            "observed_distinct_machines": 1,
            "status": "PENDING_REQUIRED",
        })
        self.assertTrue(all(
            item["claim_bearing"] is False
            and item["independent_replay"] == "1/2"
            for item in certificate["historical_certificate_authentication"]
        ))

    def test_wrong_frozen_source_hash_fails_closed(self) -> None:
        config = json.loads(restriction.CONFIG_PATH.read_text(encoding="utf-8"))
        changed = copy.deepcopy(config)
        binding = next(
            item for item in changed["source_bindings"]
            if item["path"] == restriction.V2_BRIDGE_RELATIVE
        )
        binding["sha256"] = "0" * 64
        with self.assertRaisesRegex(restriction.RestrictionError,
                                    "current source binding changed"):
            restriction.build_certificate(self.temporary_config(changed))

    def test_historical_validator_is_loaded_from_baseline_blob(self) -> None:
        records = {
            item["path"]: item
            for item in self.certificate["source_authentication"]
        }
        validator = records[restriction.HISTORICAL_CHECKER_RELATIVE]
        self.assertEqual(validator["role"],
                         "historical-validator-baseline")
        self.assertEqual(validator["baseline_blob"], "MATCH")
        self.assertEqual(
            validator["current_blob"],
            "SUPERSEDED_BY_V2_COMPATIBLE_VALIDATOR",
        )

    def test_historical_validator_hash_tamper_fails_closed(self) -> None:
        config = json.loads(restriction.CONFIG_PATH.read_text(encoding="utf-8"))
        changed = copy.deepcopy(config)
        binding = next(
            item for item in changed["source_bindings"]
            if item["path"] == restriction.HISTORICAL_CHECKER_RELATIVE
        )
        binding["sha256"] = "0" * 64
        with self.assertRaisesRegex(restriction.RestrictionError,
                                    "frozen baseline blob"):
            restriction.build_certificate(self.temporary_config(changed))

    def test_stage_atom_tamper_fails_before_evidence_replay(self) -> None:
        config = json.loads(restriction.CONFIG_PATH.read_text(encoding="utf-8"))
        changed = copy.deepcopy(config)
        changed["stages"][0]["atoms"].pop()
        with self.assertRaisesRegex(restriction.RestrictionError,
                                    "stage/atom table changed"):
            restriction.build_certificate(self.temporary_config(changed))

    def test_checker_self_hash_tamper_fails_closed(self) -> None:
        config = json.loads(restriction.CONFIG_PATH.read_text(encoding="utf-8"))
        changed = copy.deepcopy(config)
        changed["generated_source_bindings"]["checker"]["sha256"] = "f" * 64
        with self.assertRaisesRegex(restriction.RestrictionError,
                                    "checker self-binding changed"):
            restriction.build_certificate(self.temporary_config(changed))

    def test_result_tamper_is_rejected_by_schema(self) -> None:
        changed = copy.deepcopy(self.certificate)
        changed["claim_bearing"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            path.write_text(json.dumps(changed) + "\n", encoding="utf-8")
            errors = restriction.check_result(path)
        self.assertTrue(errors)
        self.assertTrue(any("False was expected" in error for error in errors))

    def test_exact_result_reconstructs_byte_independently(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            path.write_text(restriction.canonical_json(self.certificate),
                            encoding="utf-8")
            errors = restriction.check_result(path)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
