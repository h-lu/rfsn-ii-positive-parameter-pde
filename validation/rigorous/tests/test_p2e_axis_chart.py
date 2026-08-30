from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest import mock


RIGOROUS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RIGOROUS))

import check_p2e_axis_chart as axis_chart  # noqa: E402


def as_fraction(value: dict[str, str]) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))


class P2EAxisChartTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = axis_chart.build_report()

    def test_local_lemma_passes_but_event_atlas_stays_open(self) -> None:
        report = self.report
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["source_gate_status"], "PASS")
        self.assertEqual(
            report["mathematical_status"], "LOCAL_MATHEMATICAL_PASS")
        self.assertEqual(
            report["mathematical_pass_scope"], axis_chart.SCOPE)
        self.assertFalse(report["claim_bearing"])
        self.assertFalse(report["release_eligible"])
        self.assertEqual(report["independent_replay"], "1/2")
        statuses = report["local_status"]
        self.assertEqual(
            statuses["P2E.ZERO_ACTION_TRUE_SOURCE_CHART"], "PASS")
        self.assertEqual(
            statuses["P2E.AXIS_SKELETON_THICKENING_CRITERION"], "PASS")
        self.assertEqual(
            statuses["P2E.ZERO_ACTION_FIRST_EVENT_SKELETON"], "OPEN")
        self.assertEqual(statuses["V2.EVENT_ATLAS"], "OPEN")

    def test_exact_hamiltonian_phase_and_embedding_gates(self) -> None:
        exact = self.report["exact_values"]
        self.assertTrue(all(exact["checks"].values()))
        constants = exact["constants"]
        self.assertEqual(
            as_fraction(constants["source_radius"]), Fraction(1, 100))
        self.assertEqual(
            as_fraction(constants["graph_C0_tube_radius"]),
            Fraction(1, 200000),
        )
        self.assertEqual(
            as_fraction(constants["eta_chart_radius"]),
            Fraction(1, 100000),
        )
        self.assertEqual(
            as_fraction(constants["total_angle_bound"]),
            Fraction(143, 240),
        )
        self.assertEqual(
            as_fraction(constants["u1_strict_lower"]),
            Fraction(41, 5000),
        )
        self.assertGreater(
            as_fraction(constants["h_strict_lower"]), 0)
        self.assertTrue(
            exact["checks"]["zero_energy_substitution_is_exact"])
        self.assertTrue(
            exact["checks"]["physical_linear_transform_determinant"])

    def test_Machin_series_validates_frozen_two_pi_enclosure(self) -> None:
        constants = self.report["exact_values"]["constants"]
        frozen_lower = as_fraction(constants["frozen_two_pi_lower"])
        frozen_upper = as_fraction(constants["frozen_two_pi_upper"])
        machin_lower = as_fraction(constants["Machin_two_pi_lower"])
        machin_upper = as_fraction(constants["Machin_two_pi_upper"])
        self.assertLess(frozen_lower, machin_lower)
        self.assertLess(machin_lower, machin_upper)
        self.assertLess(machin_upper, frozen_upper)
        self.assertEqual(
            axis_chart.arctangent_bounds(Fraction(1, 5), 8),
            tuple(sorted(axis_chart.arctangent_bounds(Fraction(1, 5), 8))),
        )

    def test_true_source_and_action_coordinates_are_not_conflated(self) -> None:
        chart = self.report["exact_values"]["exact_chart"]
        self.assertFalse(chart["eta_is_action_coordinate"])
        self.assertEqual(chart["true_source_has_P2d_action"], "nu=0")
        self.assertIn("(H_mu-H10)_1", chart["true_source_graph"])
        criterion = self.report["exact_values"]["thickening_criterion"]
        self.assertFalse(criterion["delta_ent_numeric_value_produced"])
        self.assertFalse(criterion["full_fixed_2^-55_disc_certified"])
        boundary = self.report["claim_boundary"]
        self.assertFalse(boundary["pointwise_true_graph_evaluator_claimed"])
        self.assertFalse(boundary["first_hit_calculation_performed"])
        self.assertFalse(boundary["numeric_m_ax_produced"])

    def test_proof_digest_controls_only_the_local_lemma(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "axis-chart.md"
            changed.write_bytes(axis_chart.PROOF_PATH.read_bytes() + b"\n")
            with mock.patch.object(
                axis_chart,
                "authenticate_sources",
                return_value=self.report["source_authentication"],
            ):
                report = axis_chart.build_report(proof_path=changed)
        self.assertEqual(report["status"], "INCONCLUSIVE")
        self.assertEqual(report["source_gate_status"], "PASS")
        self.assertEqual(report["mathematical_status"], "INCONCLUSIVE")
        self.assertEqual(
            report["local_status"]["P2E.ZERO_ACTION_TRUE_SOURCE_CHART"],
            "OPEN",
        )
        self.assertEqual(report["local_status"]["V2.EVENT_ATLAS"], "OPEN")

    def test_mutated_source_bytes_fail_before_semantic_use(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "p2b0.json"
            changed.write_bytes(axis_chart.P2B0_PATH.read_bytes() + b" ")
            with self.assertRaisesRegex(
                axis_chart.AxisChartCheckError, "source hash changed"
            ):
                axis_chart.authenticate_sources(p2b0_path=changed)

    def test_weakened_u1_constant_fails_closed(self) -> None:
        with mock.patch.object(axis_chart, "U1_LOWER", Fraction(0)):
            values = axis_chart.compute_exact_values()
        self.assertFalse(values["checks"]["u1_lower_is_41_over_5000"])
        self.assertFalse(values["checks"]["u1_is_strictly_positive"])

    def test_canonical_output_is_deterministic_one_line(self) -> None:
        first, second = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(first):
            axis_chart.emit(self.report)
        with contextlib.redirect_stdout(second):
            axis_chart.emit(self.report)
        self.assertEqual(first.getvalue(), second.getvalue())
        self.assertEqual(first.getvalue().count("\n"), 1)
        self.assertEqual(json.loads(first.getvalue()), self.report)


if __name__ == "__main__":
    unittest.main()
