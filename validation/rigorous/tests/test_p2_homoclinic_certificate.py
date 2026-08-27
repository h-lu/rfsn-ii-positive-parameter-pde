from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

import jsonschema


RIGOROUS = Path(__file__).resolve().parents[1]
REPOSITORY = RIGOROUS.parents[1]
sys.path.insert(0, str(RIGOROUS))

import p2_homoclinic_certificate as p2c  # noqa: E402
import check_certificate as generic_checker  # noqa: E402


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path} is not a JSON object")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class P2HomoclinicCertificateTests(unittest.TestCase):
    config_path = RIGOROUS / "config" / "vdp_p2_homoclinic_v1.json"
    certificate_path = (
        RIGOROUS / "results" / "vdp_bridge_v1_p2c_homoclinic.json")

    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load(cls.config_path)
        cls.design = RIGOROUS / "design"
        cls.root = load(cls.design / "p2c_root_jet_summary_v1.json")
        cls.middle = load(cls.design / "p2c_middle_jet_summary_v1.json")
        cls.tail = load(cls.design / "p2c_tail_composition_v1.json")

    def test_config_schema_and_frozen_bindings(self) -> None:
        jsonschema.validate(
            self.config, load(RIGOROUS / "p2_homoclinic.schema.json"),
            format_checker=jsonschema.FormatChecker())
        self.assertEqual(
            self.config["status"], "FROZEN_POST_STRICT_DESIGN_PRE_CERTIFICATE")
        self.assertTrue(self.config["retrospective_evidence_freeze"])
        self.assertEqual(self.config["proved_subobligations"], p2c.ATOM_IDS)
        self.assertEqual(self.config["mutation_policy"], p2c.MUTATION_POLICY)
        for item in self.config["strict_run_bindings"].values():
            self.assertEqual(
                sha256(REPOSITORY / item["log_path"]), item["log_sha256"])
        for item in self.config["evidence_files"].values():
            self.assertEqual(
                sha256(REPOSITORY / item["path"]), item["sha256"])

    def test_exact_full_grid_counts(self) -> None:
        branch_text = (self.design / "logs" / "p2c_branch_v1.log").read_text()
        first_text = (self.design / "logs" / "p2c_first_hit_v1.log").read_text()
        root_text = (self.design / "logs" / "p2c_root_jets_v1.log").read_text()
        middle_text = (self.design / "logs" / "p2c_middle_c2_v1.log").read_text()
        branch = p2c.parse_branch(branch_text)
        first_hit = p2c.parse_first_hit(first_text)
        root = p2c.parse_root_jets(root_text, self.root)
        middle = p2c.parse_middle(middle_text, self.middle)
        self.assertEqual(branch["cells_passed"], 16384)
        self.assertEqual(branch["common_faces_passed"]["total"], 44416)
        self.assertEqual(branch["frozen_core_anchor"], "PASS")
        self.assertEqual(first_hit["cells_passed"], 16384)
        self.assertEqual(first_hit["dense_continuous_steps"], 306287)
        self.assertEqual(root["cells_passed"], 16384)
        self.assertEqual(middle["slabs_passed"], 32)
        self.assertEqual(middle["cells_passed"], 16384)
        self.assertEqual(middle["dense_continuous_steps"], 262144)
        self.assertEqual(middle["explicit_initial_sections"], 163840)
        self.assertTrue(all(middle["coverage_seams"].values()))
        invalid_cases = [
            (p2c.parse_branch,
             (branch_text.replace(
                 "max_inclusion 0.61714910438851445",
                 "max_inclusion 1", 1),)),
            (p2c.parse_first_hit,
             (first_text.replace(
                 "signed_margin P_positive 0.0025679246194170494",
                 "signed_margin P_positive 0", 1),)),
            (p2c.parse_root_jets,
             (root_text.replace(
                 "maximum_weighted_inverse_contraction 0.10270761025942336",
                 "maximum_weighted_inverse_contraction 1", 1), self.root)),
            (p2c.parse_middle,
             (middle_text.replace(
                 "capd_hessian_convention_self_check PASS",
                 "capd_hessian_convention_self_check FAIL", 1), self.middle)),
            (p2c.parse_middle,
             (middle_text.replace(
                 "centered_tube_xi_hull [-9.6418719060017821, 0.0075827262378833638]",
                 "centered_tube_xi_hull [-9, 0.0075827262378833638]", 1),
              self.middle)),
        ]
        for parser, arguments in invalid_cases:
            with self.subTest(parser=parser.__name__):
                with self.assertRaises(p2c.EvidenceError):
                    parser(*arguments)

    def test_exact_global_constants(self) -> None:
        audit = p2c.weighted_audit(self.config, self.tail, self.middle)
        self.assertEqual(audit["T_star"], 11)
        self.assertEqual(audit["eta"], {"numerator": "1", "denominator": "5"})
        self.assertEqual(audit["tail_common_integer_original_mu"], 95434)
        self.assertEqual(
            audit["local_pre_source_and_tail_common_integer_original_mu"],
            342685)
        self.assertEqual(audit["global_common_integer_normalized_theta"], 114395)
        self.assertEqual(audit["global_common_integer_original_mu"], 71496600)
        self.assertEqual(audit["coverage"]["status"], "PASS")
        self.assertEqual(audit["coverage"]["negative_tail"], "xi<=-11")
        self.assertEqual(audit["coverage"]["compact_middle"], "-T_h<=xi<=0")
        value = Fraction(
            int(audit["global_original_mu_C2"]["numerator"]),
            int(audit["global_original_mu_C2"]["denominator"]))
        self.assertLess(value, 71496600)
        self.assertEqual(self.middle["coverage"], p2c.MIDDLE_COVERAGE)

    def test_archived_certificate_and_tamper_rejection(self) -> None:
        self.assertTrue(
            self.certificate_path.exists(), "P2c result certificate is missing")
        certificate = load(self.certificate_path)
        self.assertEqual(generic_checker.schema_errors(certificate), [])
        self.assertEqual(
            generic_checker.semantic_errors(certificate, REPOSITORY), [])
        by_id = {item["id"]: item["status"]
                 for item in certificate["obligations"]}
        for identifier in [*p2c.ATOM_IDS, "V2.HOMOCLINIC"]:
            self.assertEqual(by_id[identifier], "PASS")
        invalid = copy.deepcopy(certificate)
        invalid["raw_evidence"]["branch_cover"]["cells_passed"] -= 1
        self.assertTrue(generic_checker.semantic_errors(invalid, REPOSITORY))

    def test_claim_boundary(self) -> None:
        self.assertTrue(
            self.certificate_path.exists(), "P2c result certificate is missing")
        certificate = load(self.certificate_path)
        self.assertEqual(certificate["mathematical_status"], "PASS")
        self.assertEqual(certificate["final_status"], "INCONCLUSIVE")
        self.assertFalse(certificate["claim_bearing"])
        self.assertFalse(certificate["release_eligible"])
        joined = " ".join(certificate["nonclaims"])
        for phrase in ("outside the finite parameter-following lifted",
                       "P2d exact saddle charts", "Turing", "canard"):
            self.assertIn(phrase, joined)
        invalid = copy.deepcopy(certificate)
        invalid["claim_bearing"] = True
        self.assertTrue(generic_checker.schema_errors(invalid) or
                        generic_checker.semantic_errors(invalid, REPOSITORY))
        invalid = copy.deepcopy(certificate)
        invalid["source_revision"] = []
        self.assertTrue(generic_checker.semantic_errors(invalid, REPOSITORY))


if __name__ == "__main__":
    unittest.main()
