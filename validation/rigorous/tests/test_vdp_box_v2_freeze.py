from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from validation.rigorous.check_vdp_box_v2_freeze import (
    AuditError,
    DEFAULT_BOX,
    DEFAULT_BRIDGE,
    audit,
)


class VdpBoxV2FreezeTest(unittest.TestCase):
    def test_committed_freeze_contract_passes(self) -> None:
        result = audit()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["mathematical_status"], "NOT_RUN")
        self.assertFalse(result["claim_bearing"])
        self.assertTrue(result["redesign_budget_consumed"])

    def test_coordinated_endpoint_tamper_is_rejected(self) -> None:
        box = json.loads(DEFAULT_BOX.read_text())
        bridge = json.loads(DEFAULT_BRIDGE.read_text())
        box["variables"]["r"]["upper"] = {
            "numerator": "3", "denominator": "100"}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            box_path = root / "box.json"
            box_path.write_text(json.dumps(box), encoding="utf-8")
            bridge["selection_basis"]["target_box"]["sha256"] = (
                hashlib.sha256(box_path.read_bytes()).hexdigest())
            bridge["variables"]["r"]["upper"] = {
                "numerator": "3", "denominator": "100"}
            bridge_path = root / "bridge.json"
            bridge_path.write_text(json.dumps(bridge), encoding="utf-8")
            with self.assertRaisesRegex(AuditError, "exact r/4 image"):
                audit(box_path, bridge_path)

    def test_disclosed_evidence_hash_tamper_is_rejected(self) -> None:
        box = json.loads(DEFAULT_BOX.read_text())
        box["selection_basis"][
            "preexisting_nonclaim_evidence_disclosed"]["sha256"] = "0" * 64
        bridge = copy.deepcopy(json.loads(DEFAULT_BRIDGE.read_text()))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            box_path = root / "box.json"
            box_path.write_text(json.dumps(box), encoding="utf-8")
            bridge["selection_basis"]["target_box"]["sha256"] = (
                hashlib.sha256(box_path.read_bytes()).hexdigest())
            bridge_path = root / "bridge.json"
            bridge_path.write_text(json.dumps(bridge), encoding="utf-8")
            with self.assertRaisesRegex(AuditError, "exploratory log hash"):
                audit(box_path, bridge_path)

    def test_coordinated_derived_formula_tamper_is_rejected(self) -> None:
        box = json.loads(DEFAULT_BOX.read_text())
        bridge = json.loads(DEFAULT_BRIDGE.read_text())
        box["derived_conventions"]["d"] = "r^5"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            box_path = root / "box.json"
            box_path.write_text(json.dumps(box), encoding="utf-8")
            bridge["selection_basis"]["target_box"]["sha256"] = (
                hashlib.sha256(box_path.read_bytes()).hexdigest())
            bridge_path = root / "bridge.json"
            bridge_path.write_text(json.dumps(bridge), encoding="utf-8")
            with self.assertRaisesRegex(AuditError, "v2 box schema"):
                audit(box_path, bridge_path)

    def test_bridge_hull_tamper_is_rejected(self) -> None:
        bridge = json.loads(DEFAULT_BRIDGE.read_text())
        bridge["variables"]["r"]["upper"] = {
            "numerator": "3", "denominator": "100"}
        with tempfile.TemporaryDirectory() as temporary:
            bridge_path = Path(temporary) / "bridge.json"
            bridge_path.write_text(json.dumps(bridge), encoding="utf-8")
            with self.assertRaisesRegex(AuditError, "exact r=0-to-target hull"):
                audit(DEFAULT_BOX, bridge_path)


if __name__ == "__main__":
    unittest.main()
