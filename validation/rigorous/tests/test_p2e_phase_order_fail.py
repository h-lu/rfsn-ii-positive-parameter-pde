from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from validation.rigorous.p2e_phase_order_fail import (
    AuditError,
    DEFAULT_CONFIG,
    DEFAULT_RESULT,
    REPOSITORY,
    audit,
)


class P2ePhaseOrderFailTest(unittest.TestCase):
    def test_committed_failure_certificate_is_current(self) -> None:
        result = audit()
        self.assertEqual(result, json.loads(DEFAULT_RESULT.read_text()))
        self.assertEqual(result["integrity_status"], "PASS")
        self.assertEqual(result["mathematical_status"], "FAIL")
        self.assertEqual(result["atom"]["id"], "V2.ATLAS.PHASE_GAP_AH")
        self.assertEqual(
            result["atom"]["strict_reversed_order_margin_lower"],
            "0.0000145185677072",
        )
        self.assertEqual(
            result["failure_propagation"]["vdp-positive-box-v1"], "FAIL"
        )

    def test_tampered_log_is_rejected(self) -> None:
        config = json.loads(DEFAULT_CONFIG.read_text())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "tampered.log"
            original = REPOSITORY / config["strict_root_evidence"]["stdout_path"]
            log.write_bytes(original.read_bytes().replace(
                b"5.7566768761372131", b"5.7567000000000000"))
            config["strict_root_evidence"]["stdout_path"] = str(log)
            config["strict_root_evidence"]["stdout_sha256"] = hashlib.sha256(
                log.read_bytes()).hexdigest()
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config))
            with self.assertRaisesRegex(AuditError, "phase hull changed"):
                audit(config_path)

    def test_coordinated_parameter_cell_tamper_is_rejected(self) -> None:
        config = json.loads(DEFAULT_CONFIG.read_text())
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            log = root / "tampered-cell.log"
            original = REPOSITORY / config["strict_root_evidence"]["stdout_path"]
            old = b"[0.077499999999999999, 0.080000000000000002]"
            new = b"[100, 101]"
            log.write_bytes(original.read_bytes().replace(old, new))
            config["strict_root_evidence"]["stdout_path"] = str(log)
            config["strict_root_evidence"]["stdout_sha256"] = hashlib.sha256(
                log.read_bytes()).hexdigest()
            config["strict_root_evidence"]["expected_printed_parameter_cell"][0] = (
                new.decode()
            )
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config))
            with self.assertRaisesRegex(AuditError, "printed r enclosure misses"):
                audit(config_path)

    def test_declared_cell_and_phase_semantics_are_not_mutable(self) -> None:
        original = json.loads(DEFAULT_CONFIG.read_text())
        cases = [
            ("counterexample_cell", "declared r cell does not follow"),
            ("theorem_clause", "wrong theorem clause"),
            ("phase_interface", "phase-interface semantics changed"),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for index, (case, pattern) in enumerate(cases):
                config = json.loads(json.dumps(original))
                if case == "counterexample_cell":
                    config[case]["r"] = ["100", "101"]
                elif case == "theorem_clause":
                    config[case] = "unrelated theorem"
                else:
                    config[case]["common_lift"] = "UNRELATED_PHASE"
                config_path = root / f"config-{index}.json"
                config_path.write_text(json.dumps(config))
                with self.subTest(case=case):
                    with self.assertRaisesRegex(AuditError, pattern):
                        audit(config_path)

    def test_wrong_binary_is_rejected_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            binary = Path(temporary) / "not-the-strict-binary"
            binary.write_bytes(b"not an executable")
            with self.assertRaisesRegex(AuditError, "binary hash mismatch"):
                audit(strict_binary=binary)


if __name__ == "__main__":
    unittest.main()
