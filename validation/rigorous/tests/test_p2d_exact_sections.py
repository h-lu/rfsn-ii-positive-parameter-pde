from __future__ import annotations

import contextlib
import copy
import io
import json
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest import mock


RIGOROUS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RIGOROUS))

import check_p2d_exact_sections as exact_sections  # noqa: E402


def as_fraction(record: dict[str, str]) -> Fraction:
    return Fraction(int(record["numerator"]), int(record["denominator"]))


class P2DExactSectionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = exact_sections.build_report()

    def test_local_atom_pass_and_parent_stays_open(self) -> None:
        report = self.report
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["mathematical_status"],
                         "LOCAL_MATHEMATICAL_PASS")
        self.assertEqual(
            report["local_chart_status"]["V2.CHART.EXACT_SECTIONS"],
            "PASS",
        )
        self.assertEqual(
            report["local_chart_status"]["V2.EXACT_CHART"], "OPEN")
        self.assertFalse(report["claim_bearing"])
        self.assertFalse(report["release_eligible"])

    def test_exact_frozen_radius_and_domain_margins(self) -> None:
        exact = self.report["exact_values"]
        constants = exact["constants"]
        self.assertEqual(
            as_fraction(constants["section_radius_rho"]),
            Fraction(5, 2**26),
        )
        self.assertEqual(
            as_fraction(constants["section_nu_star"]),
            Fraction(25, 2**54),
        )
        self.assertEqual(
            as_fraction(constants["rho_over_source_radius"]), Fraction(5, 6))
        self.assertEqual(
            as_fraction(constants["positive_flight_ratio"]),
            Fraction(587, 768),
        )
        self.assertEqual(
            as_fraction(constants["source_inclusion_ratio"]),
            Fraction(2935, 4608),
        )
        self.assertTrue(all(exact["checks"].values()))

    def test_required_arbitrary_q_section_identities_are_authenticated(self) -> None:
        audit = self.report["exact_audit"]
        self.assertEqual(audit["source_sha256"], exact_sections.AUDIT_SHA256)
        self.assertEqual(audit["archived_check_count"], 59)
        self.assertEqual(
            set(audit["required_checks"]),
            set(exact_sections.REQUIRED_AUDIT_CHECKS),
        )
        self.assertTrue(all(audit["required_checks"].values()))

    def test_proof_digest_failure_is_inconclusive_and_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "exact-sections.md"
            changed.write_bytes(exact_sections.PROOF_PATH.read_bytes() + b"\n")
            changed_report = exact_sections.build_report(proof_path=changed)
        self.assertEqual(changed_report["status"], "INCONCLUSIVE")
        self.assertEqual(changed_report["source_gate_status"], "PASS")
        self.assertEqual(changed_report["mathematical_pass_scope"], "NONE")
        self.assertEqual(
            changed_report["local_chart_status"]["V2.CHART.EXACT_SECTIONS"],
            "OPEN",
        )
        output = io.StringIO()
        with mock.patch.object(
                exact_sections, "build_report", return_value=changed_report), \
                contextlib.redirect_stdout(output):
            code = exact_sections.main([])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output.getvalue())["status"],
                         "INCONCLUSIVE")

    def test_upstream_proof_mismatch_stays_inconclusive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "zero-energy.md"
            changed.write_bytes(
                exact_sections.zero_energy.PROOF_PATH.read_bytes() + b"\n")
            report = exact_sections.build_report(
                zero_energy_proof_path=changed)
        self.assertEqual(report["status"], "INCONCLUSIVE")
        self.assertEqual(report["source_gate_status"], "PASS")
        self.assertFalse(
            report["source_authentication"]["zero_energy_local_pass"])
        self.assertEqual(
            report["local_chart_status"]["V2.CHART.ZERO_ENERGY"], "OPEN")
        self.assertEqual(
            report["local_chart_status"]["V2.CHART.EXACT_SECTIONS"], "OPEN")
        with mock.patch.object(
                exact_sections, "build_report", return_value=report), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(exact_sections.main([]), 1)

    def test_upstream_subprocess_error_is_input_rejected(self) -> None:
        output = io.StringIO()
        error = subprocess.TimeoutExpired("audit", 1)
        with mock.patch.object(
                exact_sections.zero_energy, "build_report",
                side_effect=error), contextlib.redirect_stdout(output):
            code = exact_sections.main([])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(output.getvalue())["status"],
                         "INPUT_REJECTED")

    def test_archived_exact_audit_mutation_is_rejected(self) -> None:
        certificate, _ = (
            exact_sections.zero_energy.normal_form.scout
            .load_frame_certificate(
                exact_sections.zero_energy.normal_form.scout.FRAME_PATH))
        changed = copy.deepcopy(certificate)
        changed["exact_audit"]["report"]["checks"][
            exact_sections.REQUIRED_AUDIT_CHECKS[0]] = False
        with self.assertRaises(exact_sections.ExactSectionsCheckError):
            exact_sections.exact_audit_gates(changed)

    def test_failed_domain_gate_keeps_exact_sections_open(self) -> None:
        changed_bounds = copy.deepcopy(self.report["exact_values"])
        changed_bounds["checks"][
            "complete_passage_tube_lies_in_exact_source_chart"] = False
        with mock.patch.object(
                exact_sections, "compute_section_bounds",
                return_value=changed_bounds):
            report = exact_sections.build_report()
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["source_gate_status"], "FAIL")
        self.assertEqual(
            report["local_chart_status"]["V2.CHART.EXACT_SECTIONS"], "OPEN")

    def test_non_utf8_proof_is_rejected_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            invalid = Path(directory) / "exact-sections.md"
            invalid.write_bytes(b"\xff\xfe")
            with self.assertRaises(exact_sections.ExactSectionsCheckError):
                exact_sections.proof_binding(invalid)

    def test_canonical_output_is_one_line_and_deterministic(self) -> None:
        first, second = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(first):
            exact_sections.emit(self.report)
        with contextlib.redirect_stdout(second):
            exact_sections.emit(self.report)
        self.assertEqual(first.getvalue(), second.getvalue())
        self.assertEqual(first.getvalue().count("\n"), 1)
        self.assertEqual(json.loads(first.getvalue()), self.report)


if __name__ == "__main__":
    unittest.main()
