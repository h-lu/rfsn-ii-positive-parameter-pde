from __future__ import annotations

import contextlib
import copy
import hashlib
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

import check_p2d_chart_overlaps as overlaps  # noqa: E402


def as_fraction(record: dict[str, str]) -> Fraction:
    return Fraction(int(record["numerator"]), int(record["denominator"]))


class P2DChartOverlapsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.physical_report = overlaps.physical.build_report()
        cls.proof_sha = hashlib.sha256(
            overlaps.PROOF_PATH.read_bytes()
        ).hexdigest()
        cls.config_sha = hashlib.sha256(
            overlaps.CONFIG_PATH.read_bytes()
        ).hexdigest()
        cls.config = json.loads(overlaps.CONFIG_PATH.read_text())
        with mock.patch.object(overlaps, "PROOF_SHA256", cls.proof_sha), \
                mock.patch.object(overlaps, "CONFIG_SHA256", cls.config_sha):
            cls.report = overlaps.build_report(
                physical_report=cls.physical_report
            )

    def build_bound_report(
        self,
        *,
        proof_path: Path = overlaps.PROOF_PATH,
        config_path: Path = overlaps.CONFIG_PATH,
        physical_report: dict[str, object] | None = None,
        proof_sha: str | None = None,
        config_sha: str | None = None,
    ) -> dict[str, object]:
        if proof_sha is None:
            proof_sha = self.proof_sha
        if config_sha is None:
            config_sha = hashlib.sha256(config_path.read_bytes()).hexdigest()
        with mock.patch.object(overlaps, "PROOF_SHA256", proof_sha), \
                mock.patch.object(overlaps, "CONFIG_SHA256", config_sha):
            return overlaps.build_report(
                proof_path=proof_path,
                config_path=config_path,
                physical_report=(
                    self.physical_report
                    if physical_report is None else physical_report
                ),
            )

    def test_overlap_atom_and_exact_chart_parent_pass_locally(self) -> None:
        report = self.report
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["mathematical_status"],
                         "LOCAL_MATHEMATICAL_PASS")
        self.assertEqual(
            report["mathematical_pass_scope"],
            "LOCAL_OVERLAPS_ATOM_AND_V2_EXACT_CHART_PARENT",
        )
        statuses = report["local_chart_status"]
        self.assertTrue(all(
            statuses[child] == "PASS"
            for child in overlaps.FIRST_SIX_CHILDREN
        ))
        self.assertEqual(statuses["V2.CHART.OVERLAPS"], "PASS")
        self.assertEqual(statuses["V2.EXACT_CHART"], "PASS")
        self.assertFalse(report["claim_bearing"])
        self.assertFalse(report["release_eligible"])
        self.assertEqual(report["independent_replay"], "1/2")
        boundary = report["claim_boundary"]
        self.assertEqual(boundary["V2_EVENT_ATLAS_P2e"], "OPEN")
        self.assertEqual(boundary["T2G_GLOBAL_CUT_AND_ALPHABET"], "OPEN")

    def test_two_member_relative_cover_and_common_domains_are_exact(self) -> None:
        exact = self.report["exact_values"]
        cover = exact["finite_cover"]
        self.assertEqual(cover["member_count"], 2)
        self.assertTrue(cover["relative_topology"])
        self.assertEqual(
            as_fraction(cover["relative_compact_containment_buffer"]),
            Fraction(1, 4),
        )
        self.assertEqual(
            as_fraction(cover["original_r_compact_containment_buffer"]),
            Fraction(1, 100),
        )
        self.assertEqual(
            as_fraction(cover["closed_overlap_theta_r"]["lower"]), 0
        )
        self.assertEqual(
            as_fraction(cover["closed_overlap_theta_r"]["upper"]),
            Fraction(1, 4),
        )
        self.assertTrue(all(cover["checks"].values()))

        chart = exact["common_chart_and_markings"]
        self.assertEqual(
            as_fraction(chart["epsilon_nf"]), Fraction(1, 2**22)
        )
        self.assertEqual(
            as_fraction(chart["source_polydisc_radius"]),
            Fraction(3, 2**25),
        )
        self.assertEqual(
            as_fraction(chart["inverse_polydisc_radius"]),
            Fraction(1, 2**23),
        )
        self.assertEqual(
            as_fraction(chart["physical_target_polydisc_radius"]),
            Fraction(1, 2**25),
        )
        self.assertEqual(chart["transition"], "identity")
        self.assertEqual(chart["inverse_transition"], "identity")
        self.assertEqual(as_fraction(chart["primitive_gauge_difference"]), 0)
        self.assertTrue(chart["signed_axes_preserved"])
        self.assertTrue(all(chart["checks"].values()))

    def test_identity_chart_and_blow_up_have_full_four_by_three_rectangle(self) -> None:
        identity = self.report["exact_values"][
            "identity_chart_and_blow_up_transition"
        ]
        self.assertEqual(identity["oriented_real_blow_up_transition"],
                         "identity")
        self.assertEqual(identity["oriented_real_blow_up_inverse"],
                         "identity")
        self.assertEqual(identity["positive_Kato_boundary_degree"], 1)
        rectangle = identity["full_state3_by_parameter2_rectangle"]
        self.assertEqual(set(rectangle), {
            "state_order_0", "state_order_1",
            "state_order_2", "state_order_3",
        })
        self.assertTrue(all(len(row) == 3 for row in rectangle.values()))
        self.assertEqual(identity["rectangle_entry_count"], 12)
        self.assertTrue(all(
            as_fraction(item[
                "transition_displacement_derivative_norm_upper"
            ]) == 0
            for row in rectangle.values() for item in row
        ))
        self.assertEqual(
            rectangle["state_order_1"][0]["map_derivative"],
            "identity_linear_map_norm_1",
        )
        self.assertTrue(all(identity["checks"].values()))

    def test_general_boundary_seam_has_only_colored_total_order_three(self) -> None:
        seam = self.report["exact_values"]["boundary_source_phase_seam"]
        self.assertEqual(
            seam["type"],
            "general_orientation_preserving_circle_diffeomorphism",
        )
        self.assertFalse(seam["constant_phase_translation_assumed"])
        self.assertFalse(
            seam["full_state3_parameter2_rectangle_claimed_for_seam"]
        )
        self.assertEqual(seam["boundary_degree"], 1)
        self.assertEqual(
            seam["phase_derivative_strict_lower"]["power_of_two_exponent"],
            "-9441",
        )
        self.assertEqual(
            seam["phase_derivative_strict_lower"][
                "strict_integer_margin_after_common_scaling"
            ],
            "36",
        )
        self.assertEqual(
            seam["unit_vector_full_rectangle_exponent_K_v"], "46518440"
        )
        self.assertEqual(
            seam["forward_recurrence_k"],
            ["46518441", "93036891", "279110683"],
        )
        self.assertEqual(
            seam["inverse_recurrence_ell"],
            ["279120125", "837360385", "2791201291"],
        )
        self.assertEqual(seam["forward_lift_displacement_exponent"],
                         "46518445")
        self.assertEqual(seam["inverse_lift_displacement_exponent"],
                         "279120129")
        colored = seam["colored_mixed_total_order_3_triangle"]
        self.assertEqual(seam["colored_entry_count"], 9)
        self.assertTrue(all(item["mixed_total_order"] <= 3
                            for item in colored))
        self.assertEqual(
            {(item["phase_order"], item["parameter_order"])
             for item in seam["excluded_nonadmissible_rectangle_slots"]},
            {(2, 2), (3, 1), (3, 2)},
        )
        zero = next(item for item in colored
                    if item["mixed_total_order"] == 0)
        self.assertEqual(zero["quantity"], "lift_displacement")
        self.assertEqual(zero["forward_power_of_two_exponent"], "46518445")
        self.assertEqual(zero["inverse_power_of_two_exponent"], "279120129")
        self.assertTrue(all(seam["checks"].values()))

    def test_P2b_DH_and_Kato_SO2_degree_sources_are_authenticated(self) -> None:
        source = self.report["source_authentication"]
        self.assertTrue(source["physical_local_pass"])
        self.assertEqual(
            source["frozen_source_bindings"],
            overlaps.EXPECTED_SOURCE_BINDINGS,
        )
        self.assertTrue(source["P2b_graph_DH_gate_authenticated"])
        self.assertTrue(source["Kato_SO2_and_degree_facts_authenticated"])
        seam = self.report["exact_values"]["boundary_source_phase_seam"]
        self.assertEqual(
            as_fraction(seam["authenticated_P2b_graph_DH_upper"]),
            Fraction(111, 20000),
        )
        self.assertLess(
            as_fraction(seam["authenticated_P2b_graph_DH_upper"]), 1
        )
        self.assertEqual(
            set(seam["authenticated_Kato_SO2_and_degree_facts"]),
            set(overlaps.KATO_SEAM_FACTS),
        )
        self.assertTrue(all(
            seam["authenticated_Kato_SO2_and_degree_facts"].values()
        ))

    def test_proof_mismatch_and_upstream_nonpass_are_inconclusive(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed = Path(directory) / "overlaps.md"
            changed.write_bytes(overlaps.PROOF_PATH.read_bytes() + b"\n")
            changed_report = self.build_bound_report(proof_path=changed)
        self.assertEqual(changed_report["status"], "INCONCLUSIVE")
        self.assertEqual(changed_report["source_gate_status"], "PASS")
        self.assertEqual(changed_report["local_chart_status"][
            "V2.CHART.OVERLAPS"], "OPEN")
        self.assertEqual(changed_report["local_chart_status"][
            "V2.EXACT_CHART"], "OPEN")

        upstream = copy.deepcopy(self.physical_report)
        upstream["status"] = "INCONCLUSIVE"
        upstream["mathematical_status"] = "INCONCLUSIVE"
        upstream["proof_binding"]["matched"] = False
        upstream["local_chart_status"][
            "V2.CHART.PHYSICAL_SLIDES"] = "OPEN"
        upstream_report = self.build_bound_report(physical_report=upstream)
        self.assertEqual(upstream_report["status"], "INCONCLUSIVE")
        self.assertFalse(upstream_report["source_authentication"][
            "physical_local_pass"])
        self.assertEqual(upstream_report["local_chart_status"][
            "V2.CHART.OVERLAPS"], "OPEN")

    def test_translation_or_rectangular_seam_configuration_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            changed_path = Path(directory) / "overlaps.json"
            changed = copy.deepcopy(self.config)
            changed["section_markings"][
                "seam_is_not_assumed_to_be_a_constant_phase_translation"
            ] = False
            changed_path.write_text(json.dumps(changed, indent=2) + "\n")
            with self.assertRaises(overlaps.ChartOverlapsCheckError):
                self.build_bound_report(config_path=changed_path)

            changed = copy.deepcopy(self.config)
            changed["physical_source_seam_gates"][
                "full_rectangular_claim"] = True
            changed_path.write_text(json.dumps(changed, indent=2) + "\n")
            with self.assertRaises(overlaps.ChartOverlapsCheckError):
                self.build_bound_report(config_path=changed_path)

    def test_failed_exact_gate_is_FAIL_and_cli_errors_are_fail_closed(self) -> None:
        changed_exact = copy.deepcopy(self.report["exact_values"])
        changed_exact["boundary_source_phase_seam"]["checks"][
            "phase_derivative_is_strictly_above_2_pow_minus_9441"
        ] = False
        with mock.patch.object(
                overlaps, "compute_exact_bounds", return_value=changed_exact):
            failed = self.build_bound_report()
        self.assertEqual(failed["status"], "FAIL")
        self.assertEqual(failed["source_gate_status"], "FAIL")
        self.assertEqual(failed["local_chart_status"][
            "V2.CHART.OVERLAPS"], "OPEN")
        self.assertEqual(failed["local_chart_status"][
            "V2.EXACT_CHART"], "OPEN")

        output = io.StringIO()
        with mock.patch.object(
                overlaps, "build_report",
                side_effect=overlaps.ChartOverlapsCheckError("bad source")), \
                contextlib.redirect_stdout(output):
            code = overlaps.main([])
        self.assertEqual(code, 2)
        rejected = json.loads(output.getvalue())
        self.assertEqual(rejected["status"], "INPUT_REJECTED")
        self.assertEqual(rejected["local_chart_status"][
            "V2.CHART.OVERLAPS"], "OPEN")
        self.assertEqual(rejected["claim_boundary"][
            "V2_EVENT_ATLAS_P2e"], "OPEN")

    def test_canonical_output_is_one_deterministic_json_line(self) -> None:
        first, second = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(first):
            overlaps.emit(self.report)
        with contextlib.redirect_stdout(second):
            overlaps.emit(self.report)
        self.assertEqual(first.getvalue(), second.getvalue())
        self.assertEqual(first.getvalue().count("\n"), 1)
        self.assertEqual(json.loads(first.getvalue()), self.report)


if __name__ == "__main__":
    unittest.main()
