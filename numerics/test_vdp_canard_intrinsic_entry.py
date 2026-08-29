from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from numerics.vdp_canard_intrinsic_entry import (
    C1_STATUS,
    CONFIG_PATH,
    DERIVATIVE_STATUS,
    EVIDENCE_STATUS,
    RESULT_PATH,
    SPLITTING_STATUS,
    IntrinsicEntryError,
    build_report,
    central_hamiltonian,
    intrinsic_entry_manifest_errors,
    load_configuration,
    require_intrinsic_entry,
)


class CanardIntrinsicEntryBlockerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_configuration()
        cls.report = build_report()

    def test_default_report_fails_closed_before_c1(self) -> None:
        report = self.report
        self.assertEqual(report["evidence_status"], EVIDENCE_STATUS)
        self.assertEqual(report["C1_status"], C1_STATUS)
        self.assertFalse(report["claim_bearing"])
        self.assertIsNone(report["intrinsic_entry"])
        self.assertIsNone(report["splitting_S"])
        self.assertEqual(report["splitting_status"], SPLITTING_STATUS)
        self.assertIsNone(report["a2_derivative"])
        self.assertEqual(report["a2_derivative_status"], DERIVATIVE_STATUS)
        self.assertEqual(
            report["entry_manifest"]["errors"],
            ["no intrinsic-entry manifest was supplied"],
        )

    def test_energy_section_and_orientation_do_not_select_wcu(self) -> None:
        counterexample = self.report["constraint_nonuniqueness_counterexample"]
        first = counterexample["state_1"]
        second = counterexample["state_2"]
        self.assertNotEqual(first, second)
        self.assertGreater(counterexample["state_distance_inf"], 0.09)
        for state, residuals in (
            (first, counterexample["state_1_residuals"]),
            (second, counterexample["state_2_residuals"]),
        ):
            self.assertEqual(state[0], 16.0)
            self.assertLess(state[1], 0.0)
            self.assertLess(state[3], 0.0)
            self.assertLess(
                abs(
                    central_hamiltonian(
                        state,
                        r=self.config["parameters"]["r"],
                        a2=counterexample["a2"],
                    )
                ),
                1.0e-10,
            )
            self.assertTrue(residuals["p2_negative"])
            self.assertTrue(residuals["q2_negative"])
        self.assertEqual(
            counterexample["both_intrinsic_membership"], "UNDETERMINED"
        )

    def test_existing_candidates_are_explicitly_rejected_as_intrinsic(self) -> None:
        audit = self.report["current_candidate_audit"]
        self.assertEqual(audit["promotion_to_intrinsic_entry"], "REJECTED")
        self.assertEqual(audit["frozen_outer_u2"], 16.64508336484338)
        self.assertEqual(audit["frozen_outer_q2"], -80.0)
        self.assertIn("formal jet", audit["reason"])
        self.assertIn("Wcu membership", audit["reason"])

    def test_empty_or_frozen_manifest_cannot_pass_the_interface(self) -> None:
        with self.assertRaises(IntrinsicEntryError):
            require_intrinsic_entry({}, self.config)

        malformed = {
            "entry_state": [16.0, -2.0, 250.0, -70.0],
            "sample_a2": "not-a-number",
        }
        errors = intrinsic_entry_manifest_errors(malformed, self.config)
        self.assertIn(
            "entry sample a2 is absent or outside the frozen slice", errors
        )

        frozen = {
            "schema_version": "vdp-canard-intrinsic-entry/1",
            "status": "COMPUTED/E1_INTRINSIC_WCU_ENTRY_CANDIDATE",
            "claim_bearing": False,
            "parameters": self.config["parameters"],
            "source_section": self.config["source_section"],
            "anchor": {
                "kind": "FINITE_R_OUTER_SADDLE_SLOW_GRAPH",
                "uses_frozen_u2_boundary": True,
                "uses_formal_jet_projection": False,
                "invariance_residual": 1.0e-10,
            },
            "branch_identification": {
                "id": "PRIMARY_NO_LOOP_FROM_GAMMA0_MINUS",
                "continued_from_gamma0_minus": True,
                "first_increasing_p2_zero_verified": True,
            },
            "outer_cut_or_section_replays": [],
            "a2_tangent": {
                "entry_state_derivative": [0.0, 0.0, 0.0, 0.0],
                "splitting_derivative": 1.0,
            },
        }
        errors = intrinsic_entry_manifest_errors(frozen, self.config)
        self.assertIn("anchor still uses a frozen finite-boundary u2 value", errors)
        self.assertIn("fewer than two outer-cut/section independence replays", errors)

    def test_replays_need_distinct_locations_and_convergence_differences(self) -> None:
        replay = {
            "outer_cut_or_section_value": 20.0,
            "entry_state": [16.0, -2.0, 250.0, -70.0],
            "invariance_residual": 1.0e-9,
            "first_increasing_p2_zero_verified": True,
            "splitting": 1.0e-5,
            "splitting_derivative": 0.25,
        }
        manifest = {
            "schema_version": "vdp-canard-intrinsic-entry/1",
            "status": "COMPUTED/E1_INTRINSIC_WCU_ENTRY_CANDIDATE",
            "claim_bearing": False,
            "parameters": self.config["parameters"],
            "source_section": self.config["source_section"],
            "anchor": {
                "kind": "FINITE_R_K1_WCU_DISK",
                "uses_frozen_u2_boundary": False,
                "uses_formal_jet_projection": False,
                "invariance_residual": 1.0e-9,
            },
            "branch_identification": {
                "id": "PRIMARY_NO_LOOP_FROM_GAMMA0_MINUS",
                "continued_from_gamma0_minus": True,
                "first_increasing_p2_zero_verified": True,
            },
            "outer_cut_or_section_replays": [replay, {**replay, "splitting": 2.0e-5}],
            "a2_tangent": {
                "entry_state_derivative": [0.0, 0.0, 0.0, 0.0],
                "splitting_derivative": 0.25,
            },
        }
        errors = intrinsic_entry_manifest_errors(manifest, self.config)
        self.assertIn("outer-cut/section replay locations are not distinct", errors)
        self.assertIn("outer-cut/section independence differences are absent", errors)

    def test_audited_input_hash_tampering_is_rejected(self) -> None:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        data["audited_repository_inputs"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tampered.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(IntrinsicEntryError, "audited input changed"):
                load_configuration(path)

    def test_issue7_domain_and_route_scout_cannot_close_c4(self) -> None:
        boundary = self.report["issue7_and_C4_domain_boundary"]
        self.assertTrue(boundary["disjoint"])
        self.assertNotIn(0.08, boundary["issue7_v2_r_interval"])
        scout = self.report["narrow_slice_route_scout"]
        self.assertEqual(scout["status"], "NON_EVIDENTIARY_STRICT_BINARY_SCOUT")
        self.assertIsNone(scout["authenticated_manifest"])
        self.assertIn("closes no atom", scout["role"])
        self.assertEqual(
            self.report["decision"]["C4"],
            "NOT_STARTED_REQUIRES_SEPARATE_NARROW_SLICE_ATLAS",
        )

    def test_report_is_deterministic(self) -> None:
        self.assertEqual(self.report, build_report())
        saved = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(saved, self.report)


if __name__ == "__main__":
    unittest.main()
