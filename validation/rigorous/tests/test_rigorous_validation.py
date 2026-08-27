from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import jsonschema

RIGOROUS = Path(__file__).resolve().parents[1]
REPOSITORY = RIGOROUS.parents[1]
sys.path.insert(0, str(RIGOROUS))

from check_certificate import semantic_errors  # noqa: E402
from rigorous_common import (  # noqa: E402
    box_arguments,
    combine_verdicts,
    load_json,
    validate_exact_box,
)


class FrozenBoxTests(unittest.TestCase):
    def setUp(self) -> None:
        self.box = load_json(RIGOROUS / "config" / "vdp_box_v1.json")

    def test_schema_and_exact_endpoints(self) -> None:
        jsonschema.validate(
            self.box,
            load_json(RIGOROUS / "parameter_box.schema.json"),
            format_checker=jsonschema.FormatChecker(),
        )
        self.assertEqual(validate_exact_box(self.box), [])
        self.assertEqual(
            box_arguments(self.box),
            ["1", "25", "2", "25", "-1", "4", "1", "4",
             "4", "5", "6", "5"],
        )

    def test_post_result_box_mutation_is_detected(self) -> None:
        mutated = copy.deepcopy(self.box)
        mutated["variables"]["r"]["upper"]["numerator"] = "3"
        self.assertTrue(validate_exact_box(mutated))

    def test_verdict_lattice(self) -> None:
        self.assertEqual(combine_verdicts(["PASS", "PASS"]), "PASS")
        self.assertEqual(
            combine_verdicts(["PASS", "INCONCLUSIVE"]), "INCONCLUSIVE")
        self.assertEqual(combine_verdicts(["INCONCLUSIVE", "FAIL"]), "FAIL")


class DevelopmentReplayTests(unittest.TestCase):
    def test_reference_backend_generates_checkable_nonclaim_certificate(self) -> None:
        lock = load_json(RIGOROUS / "dependency.lock.json")
        capd_source = Path(lock["capd"]["reference_source_path"])
        capd_config = Path(lock["capd"]["reference_capd_config"])
        if not (capd_source.is_dir() and capd_config.is_file()):
            self.skipTest("reference CAPD development build is not present")
        with tempfile.TemporaryDirectory(prefix="rfsn-rigorous-test-") as temporary:
            report = Path(temporary) / "certificate.json"
            command = [
                sys.executable,
                "-B",
                str(RIGOROUS / "run_validation.py"),
                "kernel",
                "--allow-dirty",
                "--capd-source", str(capd_source),
                "--capd-config", str(capd_config),
                "--report", str(report),
            ]
            completed = subprocess.run(
                command, cwd=REPOSITORY, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            certificate = json.loads(report.read_text(encoding="utf-8"))
            self.assertEqual(certificate["toolchain"]["status"], "PASS")
            self.assertEqual(certificate["rounding_self_test"]["status"], "PASS")
            self.assertEqual(certificate["integrity_status"], "INCONCLUSIVE")
            self.assertEqual(certificate["mathematical_status"], "PASS")
            self.assertEqual(certificate["final_status"], "INCONCLUSIVE")
            self.assertFalse(certificate["claim_bearing"])
            self.assertTrue(
                certificate["rounding_self_test"]["legacy_capd_is_working"])
            by_id = {
                item["id"]: item
                for item in certificate["rounding_self_test"]["tests"]
            }
            self.assertEqual(
                by_id["ROUND.NEGATIVE_RATIONAL_DIVISION"]["status"], "PASS")
            self.assertEqual(
                by_id["ROUND.POLYNOMIAL_CONTAINMENT"]["status"], "PASS")
            self.assertEqual(semantic_errors(certificate, REPOSITORY), [])
            invalid = copy.deepcopy(certificate)
            invalid["claim_bearing"] = True
            self.assertTrue(semantic_errors(invalid, REPOSITORY))
            fake_replay = copy.deepcopy(certificate)
            fake_replay["independent_replay"]["status"] = "PASS"
            fake_replay["independent_replay"]["observed_distinct_machines"] = 2
            fake_replay["final_status"] = "PASS"
            fake_replay["claim_bearing"] = True
            fake_replay["release_eligible"] = True
            self.assertTrue(semantic_errors(fake_replay, REPOSITORY))
            checked = subprocess.run(
                [sys.executable, "-B", str(RIGOROUS / "check_certificate.py"), str(report)],
                cwd=REPOSITORY, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            self.assertEqual(checked.returncode, 0, checked.stderr)
            self.assertIn("claim_bearing=false", checked.stdout)


if __name__ == "__main__":
    unittest.main()
