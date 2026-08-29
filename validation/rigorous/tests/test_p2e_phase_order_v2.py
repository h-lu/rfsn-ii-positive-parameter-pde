from __future__ import annotations

import hashlib
import json
import re
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from validation.rigorous.p2e_phase_order_v2 import (
    AuditError,
    DEFAULT_CONFIG,
    REPOSITORY,
    audit,
    parse_slab_log,
)


HISTORICAL_COMBINED_LOG = (
    REPOSITORY / "validation/rigorous/design/logs/p2c_root_jets_v1.log"
)
MODE_LINE = "mode mu-grid-root-jets-slab\n"


def historical_slab_blocks() -> dict[int, str]:
    """Return test fixtures only; these are never promoted to v2 evidence."""

    text = HISTORICAL_COMBINED_LOG.read_text(encoding="utf-8")
    blocks: dict[int, str] = {}
    for tail in text.split(MODE_LINE)[1:]:
        block = MODE_LINE + tail
        match = re.search(r"^r_index (\d+) r_cell", block, re.MULTILINE)
        if match is not None:
            blocks[int(match.group(1))] = block
    return blocks


@contextmanager
def fixture_configuration() -> Iterator[tuple[Path, dict[int, Path]]]:
    """Materialize historical-format parser fixtures outside the repository."""

    config = json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))
    blocks = historical_slab_blocks()
    if set(range(8)) - blocks.keys():
        raise AssertionError("historical parser fixture lacks an r=0,...,7 slab")
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        paths: dict[int, Path] = {}
        for item in config["strict_slab_runs"]["logs"]:
            index = item["r_index"]
            path = root / f"fixture-r{index:02d}.log"
            path.write_text(blocks[index], encoding="utf-8")
            item["path"] = str(path)
            paths[index] = path
        config_path = root / "config.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        yield config_path, paths


class P2ePhaseOrderV2Test(unittest.TestCase):
    def test_eight_slab_fixture_closes_only_three_phase_subatoms(self) -> None:
        with fixture_configuration() as (config_path, _):
            result = audit(config_path)

        self.assertEqual(result["status"], "INCONCLUSIVE")
        self.assertEqual(result["mathematical_status"], "INCONCLUSIVE")
        self.assertEqual(result["integrity_status"],
                         "PASS_LOG_BINDINGS_ONLY")
        self.assertFalse(result["execution_verification"]
                         ["strict_binary_replayed_in_this_audit"])
        self.assertEqual(
            result["local_subatom_status"], "PASS_THREE_PHASE_GAPS_ONLY"
        )
        self.assertFalse(result["claim_bearing"])
        self.assertFalse(result["release_eligible"])
        statuses = {item["id"]: item["status"]
                    for item in result["obligations"]}
        self.assertEqual(
            {key for key, value in statuses.items() if value == "PASS"},
            {
                "V2.ATLAS.PHASE_GAP_AH",
                "V2.ATLAS.PHASE_GAP_AP",
                "V2.ATLAS.PHASE_GAP_HP",
            },
        )
        self.assertEqual(statuses["V2.SOURCE_PHASES_AND_ORDER"], "PENDING")
        self.assertEqual(statuses["V2.EVENT_ATLAS"], "PENDING")
        self.assertEqual(len(result["strict_slab_evidence"]), 8)
        self.assertEqual(
            sum(item["cells"] for item in result["strict_slab_evidence"]),
            4096,
        )

    def test_bridge_and_target_hulls_and_strict_gaps_are_explicit(self) -> None:
        with fixture_configuration() as (config_path, _):
            result = audit(config_path)

        hulls = result["phase_hulls"]
        self.assertEqual(
            hulls["homoclinic_comparison_bridge_hull"],
            ["5.8339105054727822", "5.8888259815044703"],
        )
        self.assertEqual(
            hulls["homoclinic_v2_target_hull"],
            ["5.8339105054727822", "5.8888259815044703"],
        )
        gaps = {item["id"]: item for item in result["obligations"]
                if item["status"] == "PASS"}
        self.assertEqual(
            gaps["V2.ATLAS.PHASE_GAP_AH"]["strict_gap_lower"],
            "0.0772191086778839",
        )
        self.assertEqual(
            gaps["V2.ATLAS.PHASE_GAP_AP"]["strict_gap_lower"],
            "0.3264886032051017",
        )
        self.assertEqual(
            gaps["V2.ATLAS.PHASE_GAP_HP"]["strict_gap_lower"],
            "0.1943540184955297",
        )

    def test_bridge_only_slabs_do_not_contaminate_target_hull(self) -> None:
        with fixture_configuration() as (config_path, paths):
            path = paths[0]
            text = path.read_text(encoding="utf-8")
            text = re.sub(
                r"^phase_hull \[[^\n]+?\] half_time_hull",
                "phase_hull [5.82,5.90] half_time_hull",
                text,
                count=1,
                flags=re.MULTILINE,
            )
            path.write_text(text, encoding="utf-8")
            result = audit(config_path)

        self.assertEqual(
            result["phase_hulls"]["homoclinic_comparison_bridge_hull"],
            ["5.82", "5.90"],
        )
        self.assertEqual(
            result["phase_hulls"]["homoclinic_v2_target_hull"],
            ["5.8339105054727822", "5.8888259815044703"],
        )

    def test_full_atlas_is_fail_closed_and_has_four_pending_local_parents(self) -> None:
        with fixture_configuration() as (config_path, _):
            atlas = audit(config_path)["full_event_atlas_contract"]

        self.assertEqual(atlas["status"], "PENDING_DEFINITION")
        self.assertEqual(
            atlas["full_run_status"], "PROHIBITED_BEFORE_CORE_FREEZE"
        )
        self.assertEqual(
            [item["id"] for item in atlas["parent_atoms"]],
            [
                "V2.ATLAS.CORE_MANIFEST",
                "V2.ATLAS.INCIDENCE_COMPLEX",
                "V2.ATLAS.FIRST_EVENT_CENSUS",
                "V2.ATLAS.TRANSPORTED_TRACES",
            ],
        )
        self.assertTrue(all(item["status"] == "PENDING"
                            for item in atlas["parent_atoms"]))
        gate = atlas["materialization_gate"]
        self.assertEqual(gate["required_numeric_choices"],
                         ["D", "N", "precision"])
        self.assertEqual(gate["predeclared_parameter_cover"]["cells"], 4096)

    def test_incomplete_slab_is_rejected(self) -> None:
        with fixture_configuration() as (config_path, paths):
            path = paths[0]
            path.write_text(
                path.read_text(encoding="utf-8").replace(
                    "cells 512/512", "cells 511/512"
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(AuditError, "all 512 transverse cells"):
                audit(config_path)

    def test_duplicate_structural_log_field_is_rejected(self) -> None:
        block = historical_slab_blocks()[0]
        duplicate = block.replace(
            "cells 512/512\n", "cells 512/512\ncells 512/512\n"
        )
        with self.assertRaisesRegex(AuditError, "non-unique cells field"):
            parse_slab_log(duplicate.encode())

    def test_malformed_conflicting_reserved_field_is_rejected(self) -> None:
        block = historical_slab_blocks()[0]
        tampered = block.replace(
            "cells 512/512\n", "cells 512/512\ncells conflicting-count\n"
        )
        with self.assertRaisesRegex(AuditError, "non-unique cells field"):
            parse_slab_log(tampered.encode())

    def test_trailing_content_after_terminal_pass_is_rejected(self) -> None:
        block = historical_slab_blocks()[0]
        with self.assertRaisesRegex(AuditError, "does not end in PASS"):
            parse_slab_log((block + "\n").encode())

    def test_negative_terminal_marker_is_rejected(self) -> None:
        block = historical_slab_blocks()[0]
        tampered = block.replace(
            "cells 512/512\n", "cells 512/512\nFAIL injected diagnostic\n"
        )
        with self.assertRaisesRegex(AuditError, "negative terminal marker"):
            parse_slab_log(tampered.encode())

    def test_coordinated_r_index_tamper_is_rejected(self) -> None:
        with fixture_configuration() as (config_path, paths):
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["strict_slab_runs"]["r_indices"][0] = 8
            config["strict_slab_runs"]["logs"][0]["r_index"] = 8
            config["strict_slab_runs"]["logs"][0]["exact_r_cell"] = [
                "1/50", "9/400"
            ]
            config["strict_slab_runs"]["logs"][0]["path"] = str(paths[0])
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(AuditError, "slab indices changed"):
                audit(config_path)

    def test_capd_commit_tamper_is_rejected(self) -> None:
        with fixture_configuration() as (config_path, _):
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["strict_source"]["capd_commit"] = "0" * 40
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(AuditError, "CAPD commit differs"):
                audit(config_path)

    def test_anchor_pass_status_tamper_is_rejected(self) -> None:
        with fixture_configuration() as (config_path, _):
            config = json.loads(config_path.read_text(encoding="utf-8"))
            binding = config["algebraic_anchor_binding"]
            anchor = json.loads((REPOSITORY / binding["path"]).read_text())
            anchor["status"] = "FAIL-INJECTED"
            anchor_path = config_path.parent / "algebraic-anchor.json"
            anchor_path.write_text(json.dumps(anchor), encoding="utf-8")
            binding["path"] = str(anchor_path)
            binding["sha256"] = hashlib.sha256(
                anchor_path.read_bytes()).hexdigest()
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(AuditError, "anchor or H10 binding"):
                audit(config_path)

    def test_flagship_commit_cross_binding_tamper_is_rejected(self) -> None:
        with fixture_configuration() as (config_path, _):
            config = json.loads(config_path.read_text(encoding="utf-8"))
            binding = config["flagship_lock_binding"]
            lock = json.loads((REPOSITORY / binding["path"]).read_text())
            lock["commit"] = "0" * 40
            lock_path = config_path.parent / "flagship.lock.json"
            lock_path.write_text(json.dumps(lock), encoding="utf-8")
            binding["path"] = str(lock_path)
            binding["sha256"] = hashlib.sha256(lock_path.read_bytes()).hexdigest()
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(AuditError,
                                        "prerequisite flagship import"):
                audit(config_path)

    def test_p2c_certificate_config_cross_binding_tamper_is_rejected(self) -> None:
        with fixture_configuration() as (config_path, _):
            config = json.loads(config_path.read_text(encoding="utf-8"))
            binding = config["p2c_certificate_binding"]
            certificate = json.loads(
                (REPOSITORY / binding["path"]).read_text())
            certificate["configuration"]["path"] = "wrong-config.json"
            certificate_path = config_path.parent / "p2c-certificate.json"
            certificate_path.write_text(json.dumps(certificate),
                                        encoding="utf-8")
            binding["path"] = str(certificate_path)
            binding["sha256"] = hashlib.sha256(
                certificate_path.read_bytes()).hexdigest()
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(AuditError,
                                        "certificate/configuration cross-binding"):
                audit(config_path)

    def test_process_environment_tamper_is_rejected(self) -> None:
        with fixture_configuration() as (config_path, _):
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["strict_slab_runs"]["process_environment"][
                "OMP_NUM_THREADS"] = "2"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(AuditError, "process environment"):
                audit(config_path)

    def test_wrong_binary_is_rejected_before_execution(self) -> None:
        with fixture_configuration() as (config_path, _):
            with tempfile.TemporaryDirectory() as temporary:
                binary = Path(temporary) / "wrong-binary"
                binary.write_bytes(b"not the strict executable")
                with self.assertRaisesRegex(AuditError, "binary hash mismatch"):
                    audit(config_path, strict_binary=binary)

    def test_full_atlas_numeric_choices_cannot_be_pretended_frozen(self) -> None:
        with fixture_configuration() as (config_path, _):
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["full_event_atlas_contract"]["materialization_gate"][
                "required_numeric_choices"
            ] = ["D", "N"]
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(AuditError, "materialization gate changed"):
                audit(config_path)

    def test_full_atlas_gate_status_cannot_be_pretended_pass(self) -> None:
        with fixture_configuration() as (config_path, _):
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["full_event_atlas_contract"]["materialization_gate"][
                "status"] = "PASS"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(AuditError, "materialization gate changed"):
                audit(config_path)

    def test_nonclaim_boundary_cannot_be_deleted(self) -> None:
        with fixture_configuration() as (config_path, _):
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["nonclaims"] = []
            config_path.write_text(json.dumps(config), encoding="utf-8")
            with self.assertRaisesRegex(AuditError, "nonclaim boundary changed"):
                audit(config_path)


if __name__ == "__main__":
    unittest.main()
