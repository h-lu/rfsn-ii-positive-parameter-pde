from __future__ import annotations

import copy
import hashlib
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

from check_certificate import schema_errors, semantic_errors  # noqa: E402
from rigorous_common import (  # noqa: E402
    box_arguments,
    combine_verdicts,
    load_json,
    p2_jets_arguments,
    validate_exact_bridge,
    validate_exact_box,
    validate_h10_c01_configuration,
    validate_local_graph_configuration,
    validate_p2_jets_configuration,
    validate_p2b0_true_tube_implication,
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


class FrozenP2BridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bridge = load_json(RIGOROUS / "config" / "vdp_bridge_v1.json")
        self.configuration = load_json(
            RIGOROUS / "config" / "vdp_p2_local_graph_v1.json")

    def test_bridge_schema_exact_endpoints_and_anchor(self) -> None:
        jsonschema.validate(
            self.bridge,
            load_json(RIGOROUS / "continuation_bridge.schema.json"),
            format_checker=jsonschema.FormatChecker(),
        )
        self.assertEqual(validate_exact_bridge(self.bridge), [])
        self.assertEqual(
            box_arguments(self.bridge),
            ["0", "1", "2", "25", "-1", "4", "1", "4",
             "4", "5", "6", "5"],
        )
        self.assertEqual(self.bridge["anchor_face"]["equation"], "r=0")

    def test_local_graph_configuration_schema_and_bridge_hash(self) -> None:
        jsonschema.validate(
            self.configuration,
            load_json(RIGOROUS / "p2_local_graph.schema.json"),
            format_checker=jsonschema.FormatChecker(),
        )
        selected = self.configuration["selection_basis"]["continuation_bridge"]
        self.assertEqual(selected["path"], "validation/rigorous/config/vdp_bridge_v1.json")
        import hashlib
        observed = hashlib.sha256(
            (RIGOROUS / "config" / "vdp_bridge_v1.json").read_bytes()).hexdigest()
        self.assertEqual(selected["sha256"], observed)
        self.assertEqual(validate_local_graph_configuration(self.configuration), [])

        invalid = copy.deepcopy(self.configuration)
        invalid["coordinate_block"]["unstable_radius"]["numerator"] = "2"
        self.assertTrue(validate_local_graph_configuration(invalid))
        invalid = copy.deepcopy(self.configuration)
        invalid["closed_form_frame"]["formulas"] = ["junk"] * 10
        self.assertTrue(validate_local_graph_configuration(invalid))

    def test_post_result_bridge_mutation_is_detected(self) -> None:
        mutated = copy.deepcopy(self.bridge)
        mutated["variables"]["r"]["lower"]["numerator"] = "1"
        self.assertTrue(validate_exact_bridge(mutated))


class FrozenP2H10C01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.configuration = load_json(
            RIGOROUS / "config" / "vdp_p2_h10_c01_v1.json")

    def test_schema_exact_radii_gates_and_imports(self) -> None:
        jsonschema.validate(
            self.configuration,
            load_json(RIGOROUS / "p2_h10_c01.schema.json"),
            format_checker=jsonschema.FormatChecker(),
        )
        self.assertEqual(validate_h10_c01_configuration(self.configuration), [])

    def test_post_freeze_mutation_is_detected(self) -> None:
        invalid = copy.deepcopy(self.configuration)
        invalid["tube_radii"]["value_euclidean"]["numerator"] = "2"
        self.assertTrue(validate_h10_c01_configuration(invalid))
        invalid = copy.deepcopy(self.configuration)
        invalid["acceptance_gates"]["c1_cone_margin_lower"] = {
            "numerator": "0", "denominator": "1"}
        self.assertTrue(validate_h10_c01_configuration(invalid))
        invalid = copy.deepcopy(self.configuration)
        invalid["imported_core_center"]["term_table"]["sha256"] = "0" * 64
        self.assertTrue(validate_h10_c01_configuration(invalid))
        invalid = copy.deepcopy(self.configuration)
        invalid["exact_center_audit"]["defect_maximum_total_degree"] = 10
        self.assertTrue(validate_h10_c01_configuration(invalid))
        invalid = copy.deepcopy(self.configuration)
        invalid["selection_basis"]["p2a_certificate"]["sha256"] = "0" * 64
        self.assertTrue(validate_h10_c01_configuration(invalid))
        invalid = copy.deepcopy(self.configuration)
        invalid["proof_formulas"].remove("X0=R+H")
        self.assertTrue(validate_h10_c01_configuration(invalid))


class FrozenP2JetsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bridge = load_json(
            RIGOROUS / "config" / "vdp_bridge_v1.json")
        self.configuration = load_json(
            RIGOROUS / "config" / "vdp_p2_jets_v1.json")
        self.p2b0_certificate = load_json(
            RIGOROUS / "results" / "vdp_bridge_v1_p2b_h10_c01.json")

    def test_schema_contract_and_canonical_arguments(self) -> None:
        jsonschema.validate(
            self.configuration,
            load_json(RIGOROUS / "p2_jets.schema.json"),
            format_checker=jsonschema.FormatChecker(),
        )
        self.assertEqual(validate_p2_jets_configuration(self.configuration), [])
        arguments = p2_jets_arguments(self.bridge, self.configuration)
        self.assertEqual(len(arguments), 106)
        self.assertEqual(arguments[:12], box_arguments(self.bridge))
        self.assertEqual(arguments[12:18], [
            "1", "100", "251", "25000", "111", "20000"])
        self.assertEqual(arguments[26:30], ["25", "1", "625", "1"])
        self.assertEqual(arguments[30:34], ["16", "8", "4", "2"])
        self.assertEqual(validate_p2b0_true_tube_implication(
            self.configuration, self.p2b0_certificate), [])

    def test_post_freeze_norm_grid_recurrence_and_gate_mutations_are_detected(
            self) -> None:
        mutations = []
        invalid = copy.deepcopy(self.configuration)
        invalid["coordinate_domain"]["state_block_norm"] = "euclidean"
        mutations.append(invalid)
        invalid = copy.deepcopy(self.configuration)
        invalid["coefficient_grid"]["subdivisions"][0] = 8
        mutations.append(invalid)
        invalid = copy.deepcopy(self.configuration)
        invalid["lyapunov_perron_contract"] \
            ["explicit_parameter_forcing_formula"] = "unweighted h_j"
        mutations.append(invalid)
        invalid = copy.deepcopy(self.configuration)
        invalid["coefficient_upper_gates"]["ell_2"] = {
            "numerator": "1", "denominator": "10000"}
        mutations.append(invalid)
        invalid = copy.deepcopy(self.configuration)
        invalid["normalized_weighted_jet_upper_gates"]["Z_3_2"] = {
            "numerator": "100", "denominator": "1"}
        mutations.append(invalid)
        invalid = copy.deepcopy(self.configuration)
        invalid["selection_basis"]["design_scout"]["sha256"] = "0" * 64
        mutations.append(invalid)
        for value in mutations:
            self.assertTrue(validate_p2_jets_configuration(value))

    def test_true_tube_must_imply_the_frozen_coefficient_domain(self) -> None:
        invalid = copy.deepcopy(self.configuration)
        invalid["coordinate_domain"]["true_graph_x_absolute_upper"] = {
            "numerator": "1", "denominator": "100"}
        self.assertTrue(validate_p2b0_true_tube_implication(
            invalid, self.p2b0_certificate))
        invalid = copy.deepcopy(self.configuration)
        invalid["coordinate_domain"]["true_graph_first_derivative_upper"] = {
            "numerator": "21", "denominator": "4000"}
        self.assertTrue(validate_p2b0_true_tube_implication(
            invalid, self.p2b0_certificate))


class ArchivedP2B0CertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.certificate = load_json(
            RIGOROUS / "results" / "vdp_bridge_v1_p2b_h10_c01.json")

    @staticmethod
    def obligation(collection: list[dict], identifier: str) -> dict:
        return next(item for item in collection if item["id"] == identifier)

    def test_clean_certificate_is_scoped_and_internally_valid(self) -> None:
        self.assertEqual(schema_errors(self.certificate), [])
        self.assertEqual(semantic_errors(self.certificate, REPOSITORY), [])
        self.assertEqual(self.certificate["scope"], "V2_H10_C01_KERNEL")
        self.assertEqual(self.certificate["integrity_status"], "PASS")
        self.assertEqual(self.certificate["mathematical_status"], "PASS")
        self.assertEqual(self.certificate["final_status"], "INCONCLUSIVE")
        self.assertFalse(self.certificate["claim_bearing"])
        self.assertTrue(
            self.certificate["h10_exact_center_audit"]["regeneration"]
            ["byte_identical"])
        by_id = {
            item["id"]: item["status"]
            for item in self.certificate["obligations"]
        }
        self.assertEqual(by_id["P2.H10_CENTER_EXACT"], "PASS")
        self.assertEqual(by_id["V2.WU.H10_C0_TUBE"], "PASS")
        self.assertEqual(by_id["V2.WU.H10_C1_TUBE"], "PASS")

    def test_h10_scope_and_import_tampering_is_rejected(self) -> None:
        missing = copy.deepcopy(self.certificate)
        missing.pop("h10_exact_center_audit")
        self.assertTrue(schema_errors(missing))

        invalid = copy.deepcopy(self.certificate)
        invalid["toolchain"]["probe_build"]["imported_header"] \
            ["materialized_sha256"] = "0" * 64
        self.assertTrue(semantic_errors(invalid, REPOSITORY))

        invalid = copy.deepcopy(self.certificate)
        invalid["h10_exact_center_audit"]["regeneration"] \
            ["byte_identical"] = False
        self.assertTrue(semantic_errors(invalid, REPOSITORY))

    def test_insufficient_h10_margin_is_valid_inconclusive_not_fail(self) -> None:
        inconclusive = copy.deepcopy(self.certificate)
        crossing = {
            "lower_hex": "-0x1p-30",
            "upper_hex": "0x1p-30",
            "endpoint_format": "IEEE754_BINARY64_HEX",
        }
        inconclusive["raw_probe"]["acceptance_gate_margins"] \
            ["c0_inward_margin_margin"] = crossing
        for collection in (
                inconclusive["obligations"],
                inconclusive["raw_probe"]["obligations"]):
            c0 = self.obligation(collection, "V2.WU.H10_C0_TUBE")
            c1 = self.obligation(collection, "V2.WU.H10_C1_TUBE")
            c0["enclosures"]["c0_inward_margin_margin"] = crossing
            c0["status"] = "INCONCLUSIVE"
            c1["status"] = "INCONCLUSIVE"
        inconclusive["mathematical_status"] = "INCONCLUSIVE"
        inconclusive["raw_probe"]["mathematical_status"] = "INCONCLUSIVE"
        inconclusive["raw_probe"]["status"] = "INCONCLUSIVE"
        inconclusive["toolchain"]["probe_build"]["probe_exit_code"] = 2
        self.assertEqual(semantic_errors(inconclusive, REPOSITORY), [])


class ArchivedP2JetsCertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.path = (
            RIGOROUS / "results" / "vdp_bridge_v1_p2b_jets.json")
        self.certificate = load_json(self.path)

    def test_clean_certificate_closes_the_local_graph_parent(self) -> None:
        self.assertEqual(schema_errors(self.certificate), [])
        self.assertEqual(semantic_errors(self.certificate, REPOSITORY), [])
        self.assertEqual(self.certificate["scope"], "V2_P2_JETS_KERNEL")
        self.assertEqual(
            self.certificate["source_revision"]["commit"],
            "ae88ae0fb47dc43329ad2b66bd465576994df23c")
        self.assertFalse(
            self.certificate["source_revision"]["repository_dirty"])
        self.assertEqual(self.certificate["integrity_status"], "PASS")
        self.assertEqual(self.certificate["mathematical_status"], "PASS")
        self.assertEqual(self.certificate["final_status"], "INCONCLUSIVE")
        self.assertFalse(self.certificate["claim_bearing"])
        self.assertFalse(self.certificate["release_eligible"])
        self.assertEqual(
            self.certificate["independent_replay"]["observed_distinct_machines"],
            1)
        by_id = {
            item["id"]: item["status"]
            for item in self.certificate["obligations"]
        }
        for identifier in (
                "P2.JETS.COEFFICIENTS", "V2.WU.STATE_C23",
                "V2.WU.MIXED_JETS", "V2.WU.WEIGHTED_HALF_ORBITS",
                "V2.WU.JETS", "V2.WU_GRAPH"):
            self.assertEqual(by_id[identifier], "PASS")
        self.assertEqual(
            hashlib.sha256(self.path.read_bytes()).hexdigest(),
            "07b0949a3d403c0c0a85a4a157b86d7b32cce3ff0348aeffa1db474d441fca07")


class DevelopmentReplayTests(unittest.TestCase):
    @staticmethod
    def sync_p2_probe_stdout(certificate: dict) -> None:
        stdout = json.dumps(
            certificate["raw_probe"], separators=(",", ":"),
            ensure_ascii=False) + "\n"
        certificate["toolchain"]["probe_build"]["probe_stdout"] = stdout
        certificate["logs"]["probe_stdout_sha256"] = hashlib.sha256(
            stdout.encode()).hexdigest()

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

    def test_local_graph_kernel_generates_checkable_scoped_certificate(self) -> None:
        lock = load_json(RIGOROUS / "dependency.lock.json")
        capd_source = Path(lock["capd"]["reference_source_path"])
        capd_config = Path(lock["capd"]["reference_capd_config"])
        if not (capd_source.is_dir() and capd_config.is_file()):
            self.skipTest("reference CAPD development build is not present")
        with tempfile.TemporaryDirectory(prefix="rfsn-p2a-test-") as temporary:
            report = Path(temporary) / "certificate.json"
            command = [
                sys.executable,
                "-B",
                str(RIGOROUS / "run_validation.py"),
                "local-graph",
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
            self.assertEqual(certificate["scope"], "V2_LOCAL_GRAPH_KERNEL")
            self.assertEqual(certificate["mathematical_status"], "PASS")
            self.assertEqual(certificate["final_status"], "INCONCLUSIVE")
            self.assertFalse(certificate["claim_bearing"])
            by_id = {item["id"]: item for item in certificate["obligations"]}
            self.assertEqual(by_id["BRIDGE.FROZEN"]["status"], "PASS")
            self.assertEqual(
                by_id["P2.LOCAL_GRAPH_CONFIG_FROZEN"]["status"], "PASS")
            self.assertEqual(by_id["V2.WU.FRAME_BLOCK"]["status"], "PASS")
            self.assertEqual(by_id["V2.WU.COARSE_GRAPH"]["status"], "PASS")
            self.assertEqual(
                certificate["raw_probe"]["parameter_enclosures"]["r"]["lower_hex"],
                "0x0p+0",
            )
            self.assertEqual(semantic_errors(certificate, REPOSITORY), [])
            invalid = copy.deepcopy(certificate)
            invalid["continuation_bridge"]["sha256"] = "0" * 64
            self.assertTrue(semantic_errors(invalid, REPOSITORY))
            invalid = copy.deepcopy(certificate)
            invalid["validation_configuration"]["sha256"] = "0" * 64
            self.assertTrue(semantic_errors(invalid, REPOSITORY))
            invalid = copy.deepcopy(certificate)
            invalid["raw_probe"].pop("obligations")
            self.assertTrue(semantic_errors(invalid, REPOSITORY))
            invalid = copy.deepcopy(certificate)
            for item in invalid["obligations"]:
                if item["id"] == "V2.WU.FRAME_BLOCK":
                    item.pop("enclosures")
            self.assertTrue(semantic_errors(invalid, REPOSITORY))
            invalid = copy.deepcopy(certificate)
            for collection in (
                    invalid["obligations"], invalid["raw_probe"]["obligations"]):
                for item in collection:
                    if item["id"] == "V2.WU.FRAME_BLOCK":
                        item["enclosures"]["difference_cone_margin"] = {
                            "lower_hex": "-0x1p+0",
                            "upper_hex": "-0x1p-1",
                            "endpoint_format": "IEEE754_BINARY64_HEX",
                        }
            self.assertTrue(semantic_errors(invalid, REPOSITORY))
            invalid = copy.deepcopy(certificate)
            invalid["source_bindings"] = [
                item for item in invalid["source_bindings"]
                if item["path"] !=
                "validation/rigorous/src/vdp_local_graph_probe.cpp"
            ]
            self.assertTrue(semantic_errors(invalid, REPOSITORY))
            invalid = copy.deepcopy(certificate)
            invalid["toolchain"]["probe_build"]["probe_argv"][-1] = "101"
            self.assertTrue(semantic_errors(invalid, REPOSITORY))
            invalid = copy.deepcopy(certificate)
            invalid["raw_probe"]["parameter_enclosures"]["r"] = {
                "lower_hex": "0x0p+0",
                "upper_hex": "0x1p-8",
                "endpoint_format": "IEEE754_BINARY64_HEX",
            }
            self.assertTrue(semantic_errors(invalid, REPOSITORY))
            invalid = copy.deepcopy(certificate)
            for item in invalid["obligations"]:
                if item["id"] == "V2.WU.COARSE_GRAPH":
                    item["predicate"] = "proves all V2 and PDE claims"
            self.assertTrue(semantic_errors(invalid, REPOSITORY))
            invalid = copy.deepcopy(certificate)
            invalid["nonclaims"] = ["not a claim", "still not", "placeholder"]
            self.assertTrue(semantic_errors(invalid, REPOSITORY))

            # A genuine negative margin is a valid FAIL certificate, not a
            # malformed certificate.  The checker must recompute and retain
            # that verdict rather than requiring every run to pass.
            failed = copy.deepcopy(certificate)
            negative = {
                "lower_hex": "-0x1p+0",
                "upper_hex": "-0x1p-1",
                "endpoint_format": "IEEE754_BINARY64_HEX",
            }
            for collection in (
                    failed["obligations"], failed["raw_probe"]["obligations"]):
                for item in collection:
                    if item["id"] == "V2.WU.FRAME_BLOCK":
                        item["enclosures"]["difference_cone_margin"] = negative
                        item["status"] = "FAIL"
            failed["mathematical_status"] = "FAIL"
            failed["raw_probe"]["mathematical_status"] = "FAIL"
            failed["raw_probe"]["status"] = "FAIL"
            failed["toolchain"]["probe_build"]["probe_exit_code"] = 1
            failed["final_status"] = "FAIL"
            self.assertEqual(semantic_errors(failed, REPOSITORY), [])

    def test_p2_jets_kernel_replays_and_rejects_derived_field_tampering(
            self) -> None:
        lock = load_json(RIGOROUS / "dependency.lock.json")
        capd_source = Path(lock["capd"]["reference_source_path"])
        capd_config = Path(lock["capd"]["reference_capd_config"])
        if not (capd_source.is_dir() and capd_config.is_file()):
            self.skipTest("reference CAPD development build is not present")
        with tempfile.TemporaryDirectory(prefix="rfsn-p2-jets-test-") as temporary:
            report = Path(temporary) / "certificate.json"
            command = [
                sys.executable,
                "-B",
                str(RIGOROUS / "run_validation.py"),
                "p2-jets",
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
            self.assertEqual(certificate["scope"], "V2_P2_JETS_KERNEL")
            self.assertEqual(certificate["mathematical_status"], "PASS")
            self.assertEqual(certificate["final_status"], "INCONCLUSIVE")
            self.assertFalse(certificate["claim_bearing"])
            self.assertEqual(semantic_errors(certificate, REPOSITORY), [])
            self.assertEqual(
                {item["id"] for item in certificate["raw_probe"]["obligations"]},
                {"P2.JETS.COEFFICIENTS", "V2.WU.STATE_C23",
                 "V2.WU.MIXED_JETS", "V2.WU.WEIGHTED_HALF_ORBITS"})

            invalid = copy.deepcopy(certificate)
            invalid["raw_probe"]["recurrence"]["complete"] = False
            self.sync_p2_probe_stdout(invalid)
            self.assertTrue(semantic_errors(invalid, REPOSITORY))

            invalid = copy.deepcopy(certificate)
            invalid["raw_probe"]["physical_weighted_jet_enclosures"] \
                ["Z_1_0"] = {
                    "lower_hex": "0x0p+0", "upper_hex": "0x0p+0",
                    "endpoint_format": "IEEE754_BINARY64_HEX"}
            self.sync_p2_probe_stdout(invalid)
            self.assertTrue(semantic_errors(invalid, REPOSITORY))

            invalid = copy.deepcopy(certificate)
            invalid["raw_probe"]["schema_version"] = "junk"
            self.sync_p2_probe_stdout(invalid)
            self.assertTrue(semantic_errors(invalid, REPOSITORY))

            invalid = copy.deepcopy(certificate)
            invalid["raw_probe"]["unexpected"] = True
            self.sync_p2_probe_stdout(invalid)
            self.assertTrue(semantic_errors(invalid, REPOSITORY))

            # Coordinating a raw-field edit with a rewritten exact stdout and
            # hash must still fail: the checker recompiles and replays the
            # frozen probe instead of trusting certificate-local atomics.
            zero = {
                "lower_hex": "0x0p+0", "upper_hex": "0x0p+0",
                "endpoint_format": "IEEE754_BINARY64_HEX"}
            invalid = copy.deepcopy(certificate)
            invalid["raw_probe"]["coefficient_enclosures"]["B_0"] = zero
            self.sync_p2_probe_stdout(invalid)
            errors = semantic_errors(invalid, REPOSITORY)
            self.assertIn(
                "P2 replay stdout differs from the formal run", errors)

            invalid = copy.deepcopy(certificate)
            compile_argv = invalid["toolchain"]["probe_build"]["compile_argv"]
            compile_argv.append("-DUNRECORDED_SEMANTICS=1")
            invalid["toolchain"]["probe_build"]["compile_argv_sha256"] = \
                hashlib.sha256(json.dumps(
                    compile_argv, separators=(",", ":")).encode()).hexdigest()
            errors = semantic_errors(invalid, REPOSITORY)
            self.assertIn(
                "P2 replay compile argv differs from the frozen command",
                errors)

            invalid = copy.deepcopy(certificate)
            for field in (
                    "frame_derivative_enclosures",
                    "physical_weighted_jet_enclosures",
                    "original_parameter_physical_weighted_jet_enclosures"):
                for name in invalid["raw_probe"][field]:
                    invalid["raw_probe"][field][name] = zero
            self.sync_p2_probe_stdout(invalid)
            errors = semantic_errors(invalid, REPOSITORY)
            self.assertIn(
                "P2 replay stdout differs from the formal run", errors)


if __name__ == "__main__":
    unittest.main()
