from __future__ import annotations

import copy
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


RIGOROUS = Path(__file__).resolve().parents[1]
REPOSITORY = RIGOROUS.parents[1]
sys.path.insert(0, str(RIGOROUS))

import p2d_frame_certificate as frame  # noqa: E402


def interval(lower: str = "0x1p-10", upper: str = "0x1p-9") -> dict[str, str]:
    return {
        "lower_hex": lower,
        "upper_hex": upper,
        "endpoint_format": "IEEE754_BINARY64_HEX",
    }


def semantic_raw_stub() -> dict:
    margins = {name: interval() for name in frame.GATE_ORDER}
    return {
        "schema_version": "rfsn-vdp-p2d-symplectic-frame-probe/1",
        "status": "PASS",
        "mathematical_status": "PASS",
        "structure_status": "PASS",
        "rounding_self_test": {
            "status": "PASS",
            "tests": [
                {"id": "ROUND.CAPD_LEGACY_SELF_TEST", "status": "PASS"},
                {"id": "ROUND.UPWARD", "status": "PASS"},
            ],
        },
        "grid": {"subdivisions": [16, 8, 4], "cell_count": 512},
        "gate_margins": margins,
        "obligations": [{
            "id": "V2.CHART.SYMPLECTIC_FRAME",
            "component": "interval_component_only",
            "status": "PASS",
        }],
        "claim_boundary": {
            "raw_pass_scope": "interval_frame_predicate_only",
            "claim_bearing": False,
            "exact_audit_included_in_raw_status": False,
            "P2bK_prerequisite_included_in_raw_status": False,
            "V2_CHART_SYMPLECTIC_FRAME_closed_by_raw_probe": False,
            "V2_EXACT_CHART_closed": False,
        },
    }


def schema_certificate_stub() -> dict:
    zero_hash = "0" * 64
    bindings = [
        {"path": f"bound/input-{index}", "sha256": zero_hash,
         "role": "p2d-frame-input"}
        for index in range(12)
    ]
    return {
        "schema_version": frame.SCHEMA_VERSION,
        "certificate_id": "vdp-p2d-frame-0123456789ab",
        "scope": frame.SCOPE,
        "created_at": "2026-08-28T00:00:00+00:00",
        "source_revision": {
            "repository": "h-lu/rfsn-ii-positive-parameter-pde",
            "commit": "0" * 40,
            "repository_dirty": True,
            "allow_dirty_development": True,
            "working_tree_observation": "BEFORE_REPORT_WRITE",
            "report_output_excluded_from_observation": True,
        },
        "source_bindings": bindings,
        "configuration": {
            "path": frame.CONFIG_RELATIVE,
            "sha256": zero_hash,
            "configuration_id": frame.CONFIGURATION_ID,
        },
        "continuation_bridge": {
            "path": frame.BRIDGE_RELATIVE,
            "sha256": zero_hash,
            "bridge_id": "vdp-core-to-positive-bridge-v1",
            "variables": {},
        },
        "p2bk_prerequisite": {
            "path": frame.P2BK_RELATIVE,
            "sha256": zero_hash,
            "scope": "V2_P2_KATO_KERNEL",
            "source_commit": "0" * 40,
            "integrity_status": "PASS",
            "mathematical_status": "PASS",
            "final_status": "INCONCLUSIVE",
            "claim_bearing": False,
            "required_atoms": {
                "V2.PHASE.TRUE_SOURCE": "PASS",
                "V2.PHASE.KATO_INTERFACE": "PASS",
            },
        },
        "exact_audit": {
            "path": frame.AUDIT_RELATIVE,
            "sha256": zero_hash,
            "report": {},
            "execution": {
                "python_executable": "/usr/bin/python3",
                "argv": ["/usr/bin/python3", "-B", "/tmp/audit.py"],
                "argv_sha256": zero_hash,
                "exit_code": 0,
                "stdout": "{}\n",
                "stdout_sha256": zero_hash,
                "stderr_sha256": zero_hash,
            },
        },
        "toolchain": {
            "status": "PASS",
            "strict_library_build_status": "PASS",
            "dependency_lock_sha256": zero_hash,
            "compiler": {},
            "capd": {},
            "exact_symbolic_backend": {},
            "probe_build": {},
        },
        "raw_probe": {},
        "obligations": [
            {"id": "P2.P2BK_PREREQUISITE", "predicate": "bound PASS",
             "status": "PASS", "components": {}},
            {"id": "V2.CHART.SYMPLECTIC_FRAME", "predicate": "three factors",
             "status": "PASS", "components": {}},
        ],
        "chart_status": frame.CHART_STATUS,
        "integrity_status": "PASS",
        "mathematical_status": "PASS",
        "independent_replay": {
            "status": "PENDING_REQUIRED",
            "required_distinct_machines": 2,
            "observed_distinct_machines": 1,
        },
        "final_status": "INCONCLUSIVE",
        "claim_bearing": False,
        "release_eligible": False,
        "nonclaims": frame.NONCLAIMS,
    }


class P2DFrameConfigurationTests(unittest.TestCase):
    def test_frozen_configuration_and_argv_contract(self) -> None:
        configuration = frame.load_json(frame.CONFIG_PATH)
        bridge = frame.load_json(frame.BRIDGE_PATH)
        self.assertEqual(frame.validate_configuration_semantics(configuration), [])
        arguments = frame.probe_arguments(bridge, configuration)
        self.assertEqual(len(arguments), 55)
        self.assertEqual(arguments[:15], [
            "0", "1", "2", "25", "-1", "4", "1", "4",
            "4", "5", "6", "5", "16", "8", "4",
        ])

    def test_gate_and_selection_mutations_are_rejected(self) -> None:
        configuration = frame.load_json(frame.CONFIG_PATH)
        invalid = copy.deepcopy(configuration)
        invalid["acceptance_gates"]["anchor_deviation_upper"] = {
            "numerator": "1", "denominator": "20"}
        self.assertTrue(frame.validate_configuration_semantics(invalid))
        invalid = copy.deepcopy(configuration)
        invalid["frame_contract"]["formulas"][0] = "c=0"
        self.assertTrue(frame.validate_configuration_semantics(invalid))
        invalid = copy.deepcopy(configuration)
        invalid["selection_basis"]["formal_probe"]["sha256"] = "0" * 64
        self.assertTrue(frame.validate_configuration_semantics(invalid))


class P2DFrameRawBoundaryTests(unittest.TestCase):
    def validate_semantics_only(self, raw: dict) -> list[str]:
        configuration = frame.load_json(frame.CONFIG_PATH)
        with mock.patch.object(frame, "validate_schema", return_value=[]):
            return frame.validate_raw_probe(raw, configuration)

    def test_interval_component_pass_does_not_close_parent(self) -> None:
        self.assertEqual(self.validate_semantics_only(semantic_raw_stub()), [])

    def test_raw_overclaim_and_nonpositive_margin_are_rejected(self) -> None:
        overclaim = semantic_raw_stub()
        overclaim["claim_boundary"][
            "V2_CHART_SYMPLECTIC_FRAME_closed_by_raw_probe"] = True
        self.assertTrue(self.validate_semantics_only(overclaim))
        invalid_margin = semantic_raw_stub()
        invalid_margin["gate_margins"]["kappa_lower"] = interval(
            "-0x1p-10", "0x1p-10")
        self.assertTrue(self.validate_semantics_only(invalid_margin))


class P2DFrameCertificateBoundaryTests(unittest.TestCase):
    def test_schema_freezes_local_pass_open_parent_and_nonclaim(self) -> None:
        certificate = schema_certificate_stub()
        self.assertEqual(frame.certificate_schema_errors(certificate), [])
        for path, value in (
                (("claim_bearing",), True),
                (("release_eligible",), True),
                (("final_status",), "PASS"),
                (("chart_status", "V2.EXACT_CHART"), "PASS"),
                (("chart_status", "V2.CHART.SYMPLECTIC_FRAME"), "OPEN")):
            invalid = copy.deepcopy(certificate)
            target = invalid
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
            self.assertTrue(frame.certificate_schema_errors(invalid))

    def test_dirty_certificate_without_permission_is_rejected_early(self) -> None:
        certificate = schema_certificate_stub()
        certificate["source_revision"]["commit"] = subprocess.run(
            ["git", "-C", str(REPOSITORY), "rev-parse", "HEAD"],
            check=True, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE).stdout.strip()
        certificate["source_revision"]["allow_dirty_development"] = False
        errors = frame.semantic_errors(certificate)
        self.assertTrue(any("--allow-dirty" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
