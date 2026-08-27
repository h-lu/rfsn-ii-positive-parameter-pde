from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import numpy as np

from validation.build_vdp_candidate_contract import (
    BranchDescriptor,
    CandidateContractBuildError,
    THEORY_FILES,
    build_vdp_candidate_contract,
)
from validation.check_candidate_contract import (
    DEFAULT_ENVIRONMENT_LOCK,
    DEFAULT_SCHEMA,
    validate_contract,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BuildVdpCandidateContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        (self.root / "validation").mkdir()
        shutil.copy2(DEFAULT_SCHEMA, self.root / "validation/candidate_contract.schema.json")
        shutil.copy2(DEFAULT_ENVIRONMENT_LOCK, self.root / "validation/environment.lock.json")

        for role, relative_path in THEORY_FILES:
            path = self.root / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"frozen {role}\n", encoding="utf-8")

        config_directory = self.root / "numerics/config"
        config_directory.mkdir(parents=True)
        self.configuration = config_directory / "vdp.json"
        self.configuration.write_text(
            json.dumps(
                {"parameters": {"primary": {"r": 0.08, "a2": 0, "epsilon": 1}}}
            )
            + "\n",
            encoding="utf-8",
        )
        self.generator = self.root / "numerics/vdp_complete_branches.py"
        self.generator.write_text("# frozen candidate generator\n", encoding="utf-8")

        def branch_record(branch_id: str, evidence_status: str) -> dict[str, object]:
            source = [0.0, 0.1, 0.2, 0.3]
            incoming = [0.4, 0.5, 0.6, 0.7]
            target = [0.8, 0.9, 1.0, 1.1]
            return {
                "schema_version": "rfsn-vdp-sampled-branch/1",
                "branch_id": branch_id,
                "branch_type": "finite_return",
                "claim_bearing": False,
                "evidence_status": evidence_status,
                "parameters": {
                    "r": {"decimal": "0.08", "binary64_hex": float(0.08).hex()},
                    "a2": {"decimal": "0.0", "binary64_hex": float(0).hex()},
                    "epsilon": {"decimal": "1.0", "binary64_hex": float(1).hex()},
                },
                "source": {"state": source},
                "target": {"state": target},
                "segments": [
                    {
                        "name": "global_excursion",
                        "start_state": source,
                        "end_state": incoming,
                        "physical_length": 2.0,
                        "physical_action": 3.0,
                    },
                    {
                        "name": "local_saddle_passage",
                        "start_state": incoming,
                        "end_state": target,
                        "physical_length": 4.0,
                        "physical_action": 5.0,
                    },
                ],
            }

        candidate_directory = self.root / "candidate"
        candidate_directory.mkdir()
        self.a2_record = candidate_directory / "a2.json"
        self.a2_record.write_text(
            json.dumps(branch_record(
                "vdp-A2-return",
                "COMPUTED/E1_NONRIGOROUS_COMPLETE_RETURN_CANDIDATE",
            ))
            + "\n",
            encoding="utf-8",
        )
        self.a2_arrays = candidate_directory / "a2.npz"
        prefix = "vdp_A2_return"
        source = np.array([0.0, 0.1, 0.2, 0.3])
        incoming = np.array([0.4, 0.5, 0.6, 0.7])
        target = np.array([0.8, 0.9, 1.0, 1.1])
        first_state = np.column_stack((source, incoming))
        second_state = np.column_stack((incoming, target))
        np.savez_compressed(
            self.a2_arrays,
            **{
                f"{prefix}_source_state": source,
                f"{prefix}_incoming_state": incoming,
                f"{prefix}_target_state": target,
                f"{prefix}_segment_0_global_excursion_xi": np.array([0.0, 1.0]),
                f"{prefix}_segment_0_global_excursion_central_state": first_state,
                f"{prefix}_segment_0_global_excursion_physical_length": np.array([0.0, 2.0]),
                f"{prefix}_segment_0_global_excursion_physical_action": np.array([0.0, 3.0]),
                f"{prefix}_segment_1_local_saddle_passage_xi": np.array([1.0, 2.0]),
                f"{prefix}_segment_1_local_saddle_passage_central_state": second_state,
                f"{prefix}_segment_1_local_saddle_passage_physical_length": np.array([2.0, 6.0]),
                f"{prefix}_segment_1_local_saddle_passage_physical_action": np.array([3.0, 8.0]),
            },
        )
        self.b1_record = candidate_directory / "b1.json"
        self.b1_record.write_text(
            json.dumps(branch_record(
                "vdp-B1-return",
                "COMPUTED/E1_NONRIGOROUS_RETURN_CANDIDATE",
            ))
            + "\n",
            encoding="utf-8",
        )
        self.evidence = candidate_directory / "candidate-summary.json"
        self.evidence.write_text('{"claim_bearing": false}\n', encoding="utf-8")

        (self.root / ".gitignore").write_text("generated/\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", self.root], check=True)
        subprocess.run(["git", "-C", self.root, "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                self.root,
                "-c",
                "user.name=Candidate Contract Test",
                "-c",
                "user.email=candidate-contract@example.invalid",
                "commit",
                "-qm",
                "fixture",
            ],
            check=True,
        )

    def contract_inputs(self) -> dict[str, object]:
        return {
            "parameter_point": {"r": "0.08", "a2": "0", "epsilon": "1"},
            "configuration_path": self.configuration,
            "generator_source_paths": [self.generator],
        }

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_builds_hash_bound_point_contract_and_self_validates(self) -> None:
        output = self.root / "generated/v6-candidate.json"
        contract = build_vdp_candidate_contract(
            repository_root=self.root,
            output_path=output,
            branches=[
                BranchDescriptor(
                    branch_id="vdp-A2-return",
                    type="finite_return",
                    record="candidate/a2.json",
                    arrays=self.a2_arrays,
                ),
                {
                    "branch_id": "vdp-B1-return",
                    "branch_type": "finite_return",
                    "record": self.b1_record,
                },
            ],
            candidate_evidence_paths=[self.evidence, "candidate/a2.json"],
            contract_id="vdp-v6-test-candidate",
            created_at="2026-08-27T12:00:00+08:00",
            **self.contract_inputs(),
        )

        self.assertTrue(output.is_file())
        self.assertEqual(contract, json.loads(output.read_text(encoding="utf-8")))
        self.assertFalse(contract["claim_bearing"])
        self.assertEqual(contract["final_status"], "NOT_RUN")
        self.assertEqual(contract["theorem_target"], "V6")
        self.assertFalse(contract["source_revision"]["repository_dirty"])
        self.assertEqual(
            contract["parameter_domain"]["variables"],
            {
                "r": {
                    "lower_decimal": "0.08",
                    "upper_decimal": "0.08",
                    "endpoint_semantics": "exact_base10_rational",
                },
                "a2": {
                    "lower_decimal": "0",
                    "upper_decimal": "0",
                    "endpoint_semantics": "exact_base10_rational",
                },
                "epsilon": {
                    "lower_decimal": "1",
                    "upper_decimal": "1",
                    "endpoint_semantics": "exact_base10_rational",
                },
            },
        )

        theory_by_role = {
            row["role"]: row for row in contract["theory_bindings"]
        }
        self.assertEqual(set(theory_by_role), {role for role, _ in THEORY_FILES})
        for role, relative_path in THEORY_FILES:
            self.assertEqual(theory_by_role[role]["path"], relative_path)
            self.assertEqual(
                theory_by_role[role]["sha256"], _sha256(self.root / relative_path)
            )
        self.assertEqual(len(contract["candidate_branches"]), 2)
        self.assertIn("arrays", contract["candidate_branches"][0])
        self.assertEqual(
            contract["candidate_branches"][0]["array_prefix"], "vdp_A2_return"
        )
        self.assertNotIn("arrays", contract["candidate_branches"][1])
        replay_by_role = {row["role"]: row for row in contract["replay_bindings"]}
        self.assertEqual(
            set(replay_by_role),
            {"candidate configuration", "candidate generator source 1"},
        )
        self.assertEqual(
            validate_contract(
                output,
                schema_path=self.root / "validation/candidate_contract.schema.json",
                repository_root=self.root,
            ),
            [],
        )

        v6_path = self.root / THEORY_FILES[0][1]
        v6_path.write_text("changed theorem\n", encoding="utf-8")
        failures = validate_contract(
            output,
            schema_path=self.root / "validation/candidate_contract.schema.json",
            repository_root=self.root,
        )
        self.assertTrue(any("SHA-256 mismatch" in failure for failure in failures))

    def test_rejects_evidence_outside_repository(self) -> None:
        outside = self.root.parent / f"{self.root.name}-outside-evidence.json"
        outside.write_text("{}\n", encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)
        with self.assertRaisesRegex(
            CandidateContractBuildError, "must remain inside the repository"
        ):
            build_vdp_candidate_contract(
                repository_root=self.root,
                output_path="generated/v6-candidate.json",
                branches=[
                    BranchDescriptor(
                        branch_id="vdp-A2-return",
                        type="finite_return",
                        record=self.a2_record,
                        arrays=self.a2_arrays,
                    )
                ],
                candidate_evidence_paths=[outside],
                **self.contract_inputs(),
            )

    def test_rejects_output_that_would_overwrite_a_bound_input(self) -> None:
        with self.assertRaisesRegex(CandidateContractBuildError, "overwrite"):
            build_vdp_candidate_contract(
                repository_root=self.root,
                output_path=self.a2_record,
                branches=[
                    BranchDescriptor(
                        branch_id="vdp-A2-return",
                        type="finite_return",
                        record=self.a2_record,
                        arrays=self.a2_arrays,
                    )
                ],
                candidate_evidence_paths=[self.evidence],
                **self.contract_inputs(),
            )
        self.assertEqual(
            json.loads(self.a2_record.read_text(encoding="utf-8"))["branch_id"],
            "vdp-A2-return",
        )

    def test_failed_self_check_does_not_replace_existing_output(self) -> None:
        output = self.root / "generated/v6-candidate.json"
        output.parent.mkdir()
        output.write_text("preserve me\n", encoding="utf-8")
        with patch(
            "validation.build_vdp_candidate_contract.validate_contract",
            return_value=["injected validation failure"],
        ):
            with self.assertRaisesRegex(
                CandidateContractBuildError, "injected validation failure"
            ):
                build_vdp_candidate_contract(
                    repository_root=self.root,
                    output_path=output,
                    branches=[
                        BranchDescriptor(
                            branch_id="vdp-A2-return",
                            type="finite_return",
                            record=self.a2_record,
                            arrays=self.a2_arrays,
                        )
                    ],
                    candidate_evidence_paths=[self.evidence],
                    **self.contract_inputs(),
                )
        self.assertEqual(output.read_text(encoding="utf-8"), "preserve me\n")

    def test_rejects_parameter_mismatch_in_every_branch_record(self) -> None:
        record = json.loads(self.a2_record.read_text(encoding="utf-8"))
        record["parameters"]["r"] = {
            "decimal": "0.09",
            "binary64_hex": float(0.09).hex(),
        }
        self.a2_record.write_text(json.dumps(record) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(
            CandidateContractBuildError, "differs from parameter_point"
        ):
            build_vdp_candidate_contract(
                repository_root=self.root,
                output_path="generated/v6-candidate.json",
                branches=[
                    BranchDescriptor(
                        branch_id="vdp-A2-return",
                        type="finite_return",
                        record=self.a2_record,
                        arrays=self.a2_arrays,
                    )
                ],
                candidate_evidence_paths=[self.evidence],
                **self.contract_inputs(),
            )


if __name__ == "__main__":
    unittest.main()
