from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path


RIGOROUS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RIGOROUS))

import check_p2d_normal_form_source_bounds as source  # noqa: E402


def as_fraction(record: dict[str, str]) -> Fraction:
    return Fraction(int(record["numerator"]), int(record["denominator"]))


class P2DNormalFormSourceBoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate, cls.digest = source.scout.load_frame_certificate()
        cls.low_order = source.run_low_order_audit()
        cls.report = source.build_report(low_order_result=cls.low_order)

    def test_archived_probe_and_dictionary_are_deeply_authenticated(self) -> None:
        authentication = source.authenticate_frame_source(
            self.certificate, self.digest)
        self.assertEqual(authentication["grid_cells"], 512)
        self.assertEqual(
            authentication["frame_source_commit"],
            source.scout.FRAME_SOURCE_COMMIT,
        )
        self.assertLess(
            as_fraction(
                authentication["L_inverse_operator_upper_from_anchor"]),
            Fraction(8, 7),
        )

        changed_commit = copy.deepcopy(self.certificate)
        changed_commit["source_revision"]["commit"] = "0" * 40
        with self.assertRaisesRegex(
                source.scout.ScoutInputError, "source commit"):
            source.authenticate_frame_source(changed_commit, self.digest)

        changed_stdout = copy.deepcopy(self.certificate)
        changed_stdout["toolchain"]["probe_build"]["probe_stdout"] += " "
        with self.assertRaisesRegex(
                source.SourceCheckError, "stdout SHA-256"):
            source.authenticate_frame_source(changed_stdout, self.digest)

        changed_order = copy.deepcopy(self.certificate)
        changed_order["raw_probe"]["input_binding"][
            "normalized_D1_order"
        ][0] = "theta_a"
        with self.assertRaisesRegex(
                source.scout.ScoutInputError, "first-parameter order"):
            source.authenticate_frame_source(changed_order, self.digest)

    def test_exact_model_majorant_and_domain_gates_pass(self) -> None:
        report = self.report
        self.assertEqual(report["status"], "PASS")
        expected_is_bound = len(source.THEORY_SHA256) == 64
        self.assertEqual(
            report["mathematical_status"],
            "LOCAL_MATHEMATICAL_PASS" if expected_is_bound
            else "LOCAL_SOURCE_GATES_PASS",
        )
        self.assertEqual(
            report["mathematical_pass_scope"],
            "LOCAL_ANALYTIC_NORMAL_FORM_ATOM" if expected_is_bound
            else "LOCAL_SOURCE_GATES_ONLY",
        )
        self.assertTrue(all(
            result
            for group in report["checks"].values()
            for result in group.values()
        ))

        values = report["exact_values"]
        inputs = values["equations_17_to_19"]
        self.assertLessEqual(as_fraction(inputs["E"]), 4)
        self.assertLessEqual(as_fraction(inputs["h_in"]), Fraction(1, 64))
        self.assertLessEqual(
            as_fraction(inputs["kappa_J"]), Fraction(5, 3))

        schedule = values["equations_38_to_44a"]
        self.assertEqual(as_fraction(schedule["Bz"]), Fraction(37, 691200))
        self.assertEqual(
            as_fraction(schedule["Az"]), Fraction(691200, 691163))
        self.assertLess(
            as_fraction(schedule["forward_displacement"]),
            as_fraction(schedule["Dmid_gap"]),
        )

        finite = values["N2_equations_45_to_47a"]
        inverse_tail = as_fraction(finite["inverse_coordinate_tail"])
        forward_tail = as_fraction(finite["forward_coordinate_tail"])
        self.assertEqual(inverse_tail, Fraction(1, 3092376453120))
        self.assertEqual(
            forward_tail,
            as_fraction(schedule["Az"]) * inverse_tail,
        )

    def test_sections_six_and_seven_are_exact_rational_tails(self) -> None:
        sections = self.report["exact_values"]["sections_6_and_7"]
        constants = sections["accumulated_constants"]
        self.assertGreater(as_fraction(constants["Hbar"]), 600)
        self.assertLess(as_fraction(constants["Ltheta"]), Fraction(10001, 10000))
        for group_name in ("N2_C2_tails", "N2_primitive_tails"):
            self.assertTrue(all(
                as_fraction(value) > 0
                for value in sections[group_name].values()
            ))
        checks = self.report["checks"]["C2_and_primitive"]
        self.assertTrue(checks["equation_51e_V0"])
        self.assertTrue(checks["equation_51e_B0"])
        self.assertTrue(checks["equation_51e_C0"])
        self.assertTrue(checks["equation_54f_Achi0"])
        self.assertTrue(checks["equation_54f_G0"])
        self.assertTrue(checks["equation_54f_K0"])

    def test_theory_version_controls_only_the_local_atom_pass(self) -> None:
        boundary = self.report["claim_boundary"]
        binding = self.report["proof_bindings"]["analytic_majorant"]
        expected_is_bound = len(source.THEORY_SHA256) == 64
        self.assertEqual(binding["matched"], expected_is_bound)
        self.assertEqual(
            self.report["local_chart_status"][
                "V2.CHART.ANALYTIC_NORMAL_FORM"
            ],
            "PASS" if expected_is_bound else "OPEN",
        )
        self.assertFalse(self.report["claim_bearing"])
        self.assertFalse(boundary["claim_bearing"])
        self.assertEqual(
            self.report["local_chart_status"]["V2.EXACT_CHART"], "OPEN")

        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "majorant.md"
            changed.write_bytes(source.THEORY_PATH.read_bytes() + b"\n")
            changed_report = source.build_report(
                theory_path=changed, low_order_result=self.low_order)
        self.assertFalse(
            changed_report["proof_bindings"]["analytic_majorant"]["matched"])
        self.assertEqual(
            changed_report["local_chart_status"][
                "V2.CHART.ANALYTIC_NORMAL_FORM"
            ],
            "OPEN",
        )
        self.assertEqual(changed_report["status"], "PASS")

    def test_low_order_prefix_and_one_line_output_are_deterministic(self) -> None:
        self.assertEqual(self.low_order["status"], "PASS")
        self.assertEqual(self.low_order["check_count"], 26)
        first, second = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(first):
            source.emit(self.report)
        with contextlib.redirect_stdout(second):
            source.emit(self.report)
        self.assertEqual(first.getvalue(), second.getvalue())
        self.assertEqual(first.getvalue().count("\n"), 1)
        self.assertEqual(json.loads(first.getvalue()), self.report)


if __name__ == "__main__":
    unittest.main()
