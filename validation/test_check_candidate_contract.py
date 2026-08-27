from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np

from validation.check_candidate_contract import (
    DEFAULT_ENVIRONMENT_LOCK,
    REQUIRED_THEORY_ROLES,
    validate_contract,
    validate_scaffold,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hashed(path: Path, root: Path, *, role: str) -> dict[str, str]:
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": _sha256(path),
        "role": role,
    }


class CandidateContractTests(unittest.TestCase):
    def test_repository_scaffold_is_explicitly_non_claim_bearing(self) -> None:
        self.assertEqual(validate_scaffold(), [])

    def _fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path, Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)

        theory_bindings: list[dict[str, str]] = []
        for index, role in enumerate(sorted(REQUIRED_THEORY_ROLES)):
            path = root / f"theory/{index}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"frozen {role}\n", encoding="utf-8")
            theory_bindings.append(_hashed(path, root, role=role))

        configuration = root / "numerics/config.json"
        configuration.parent.mkdir(parents=True)
        configuration.write_text(
            json.dumps(
                {"parameters": {"primary": {"r": 0.08, "a2": 0, "epsilon": 1}}}
            )
            + "\n",
            encoding="utf-8",
        )
        generator = root / "numerics/generator.py"
        generator.write_text("# frozen generator\n", encoding="utf-8")

        source = [0.0, 0.1, 0.2, 0.3]
        target = [0.4, 0.5, 0.6, 0.7]
        branch = root / "candidate/branch.json"
        branch.parent.mkdir()
        branch.write_text(
            json.dumps(
                {
                    "schema_version": "rfsn-vdp-sampled-branch/1",
                    "branch_id": "vdp-A2-return",
                    "branch_type": "finite_return",
                    "claim_bearing": False,
                    "evidence_status": (
                        "COMPUTED/E1_NONRIGOROUS_COMPLETE_RETURN_CANDIDATE"
                    ),
                    "parameters": {
                        "r": {
                            "decimal": "0.08",
                            "binary64_hex": float(0.08).hex(),
                        },
                        "a2": {
                            "decimal": "0.0",
                            "binary64_hex": float(0).hex(),
                        },
                        "epsilon": {
                            "decimal": "1.0",
                            "binary64_hex": float(1).hex(),
                        },
                    },
                    "source": {"state": source},
                    "target": {"state": target},
                    "segments": [
                        {
                            "name": "return_segment",
                            "start_state": source,
                            "end_state": target,
                            "physical_length": 2.0,
                            "physical_action": 3.0,
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        arrays = root / "candidate/branch.npz"
        prefix = "vdp_A2_return"
        np.savez_compressed(
            arrays,
            **{
                f"{prefix}_source_state": np.asarray(source),
                f"{prefix}_incoming_state": np.asarray(target),
                f"{prefix}_target_state": np.asarray(target),
                f"{prefix}_segment_0_return_segment_xi": np.array([0.0, 1.0]),
                f"{prefix}_segment_0_return_segment_central_state": np.column_stack(
                    (source, target)
                ),
                f"{prefix}_segment_0_return_segment_physical_length": np.array(
                    [0.0, 2.0]
                ),
                f"{prefix}_segment_0_return_segment_physical_action": np.array(
                    [0.0, 3.0]
                ),
            },
        )
        environment = root / "environment.lock.json"
        environment.write_bytes(DEFAULT_ENVIRONMENT_LOCK.read_bytes())

        subprocess.run(["git", "init", "-q", root], check=True)
        subprocess.run(["git", "-C", root, "add", "."], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                root,
                "-c",
                "user.name=Candidate Checker Test",
                "-c",
                "user.email=candidate-checker@example.invalid",
                "commit",
                "-qm",
                "fixture",
            ],
            check=True,
        )
        commit = subprocess.run(
            ["git", "-C", root, "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

        contract = {
            "schema_version": "rfsn-candidate-validation-contract/2",
            "contract_id": "vdp-v6-a2-draft",
            "status": "DRAFT_CANDIDATE_ONLY",
            "claim_bearing": False,
            "theorem_target": "V6",
            "created_at": "2026-08-27T12:00:00+08:00",
            "source_revision": {
                "repository": "h-lu/rfsn-ii-positive-parameter-pde",
                "commit": commit,
                "repository_dirty": False,
                "reproducibility_status": "CLEAN_BASE_COMMIT",
                "ignored_paths": ["contract.json"],
                "note": "Clean fixture; contract path excluded from dirty sampling.",
            },
            "theory_bindings": theory_bindings,
            "replay_bindings": [
                _hashed(configuration, root, role="candidate configuration"),
                _hashed(generator, root, role="candidate generator source 1"),
            ],
            "parameter_domain": {
                "selection_status": "EXPLORATORY_NOT_FROZEN",
                "variables": {
                    name: {
                        "lower_decimal": value,
                        "upper_decimal": value,
                        "endpoint_semantics": "exact_base10_rational",
                    }
                    for name, value in (
                        ("r", "0.08"),
                        ("a2", "0"),
                        ("epsilon", "1"),
                    )
                },
            },
            "observables": [
                {
                    "id": "V6.length",
                    "definition": "physical source-to-source branch length",
                    "normalization": "ordinary finite return",
                    "status": "FIXED_DEFINITION",
                }
            ],
            "obligations": [
                {
                    "id": "V6.return.A2",
                    "theorem_clause": "V6(2)--(5)",
                    "predicate": "one candidate return and its observables",
                    "status": "CANDIDATE_READY",
                    "candidate_evidence": [
                        _hashed(branch, root, role="candidate record")
                    ],
                }
            ],
            "candidate_branches": [
                {
                    "branch_id": "vdp-A2-return",
                    "branch_type": "finite_return",
                    "record": _hashed(branch, root, role="candidate record"),
                    "arrays": _hashed(arrays, root, role="candidate arrays"),
                    "array_prefix": prefix,
                    "evidence_status": "COMPUTED/E1_NONRIGOROUS_CANDIDATE",
                }
            ],
            "environment_lock": _hashed(
                environment, root, role="non-claim-bearing environment lock"
            ),
            "final_status": "NOT_RUN",
            "nonclaims": [
                "not interval validation",
                "not an exhaustive atlas",
                "not an exact V2 chart",
                "not an integer V6 winding certificate",
            ],
        }
        contract_path = root / "contract.json"
        contract_path.write_text(
            json.dumps(contract, indent=2) + "\n", encoding="utf-8"
        )
        return temporary, root, contract_path

    def test_hash_bound_contract_and_npz_schema(self) -> None:
        temporary, root, contract_path = self._fixture()
        self.addCleanup(temporary.cleanup)
        self.assertEqual(validate_contract(contract_path, repository_root=root), [])

        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        contract["candidate_branches"][0]["array_prefix"] = "wrong_prefix"
        contract_path.write_text(json.dumps(contract) + "\n", encoding="utf-8")
        failures = validate_contract(contract_path, repository_root=root)
        self.assertTrue(any("array_prefix is not derived" in item for item in failures))

    def test_npz_missing_required_branch_array_is_rejected(self) -> None:
        temporary, root, contract_path = self._fixture()
        self.addCleanup(temporary.cleanup)
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        arrays_path = root / contract["candidate_branches"][0]["arrays"]["path"]
        with np.load(arrays_path, allow_pickle=False) as archive:
            payload = {
                name: np.asarray(archive[name])
                for name in archive.files
                if not name.endswith("_target_state")
            }
        np.savez_compressed(arrays_path, **payload)
        new_hash = _sha256(arrays_path)
        contract["candidate_branches"][0]["arrays"]["sha256"] = new_hash
        contract_path.write_text(json.dumps(contract) + "\n", encoding="utf-8")
        failures = validate_contract(contract_path, repository_root=root)
        self.assertTrue(
            any("missing required NPZ array" in item for item in failures)
        )

    def test_realpath_containment_rejects_symlink_escape(self) -> None:
        temporary, root, contract_path = self._fixture()
        self.addCleanup(temporary.cleanup)
        outside = root.parent / f"{root.name}-outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)
        link = root / "escaped-theory.md"
        link.symlink_to(outside)

        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        contract["theory_bindings"][0]["path"] = link.relative_to(root).as_posix()
        contract["theory_bindings"][0]["sha256"] = _sha256(outside)
        contract_path.write_text(json.dumps(contract) + "\n", encoding="utf-8")
        failures = validate_contract(contract_path, repository_root=root)
        self.assertTrue(any("real path escapes" in item for item in failures))

    def test_source_revision_is_checked_against_git(self) -> None:
        temporary, root, contract_path = self._fixture()
        self.addCleanup(temporary.cleanup)
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        contract["source_revision"]["commit"] = "0" * 40
        contract_path.write_text(json.dumps(contract) + "\n", encoding="utf-8")
        failures = validate_contract(contract_path, repository_root=root)
        self.assertTrue(
            any("recorded source commit does not exist" in item for item in failures)
        )

    def test_descendant_head_is_a_warning_not_a_failure(self) -> None:
        temporary, root, contract_path = self._fixture()
        self.addCleanup(temporary.cleanup)
        (root / "later.txt").write_text("later committed artifact\n", encoding="utf-8")
        subprocess.run(["git", "-C", root, "add", "later.txt"], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                root,
                "-c",
                "user.name=Candidate Checker Test",
                "-c",
                "user.email=candidate-checker@example.invalid",
                "commit",
                "-qm",
                "commit generated artifact",
            ],
            check=True,
        )

        warnings: list[str] = []
        failures = validate_contract(
            contract_path,
            repository_root=root,
            warnings=warnings,
        )
        self.assertEqual(failures, [])
        self.assertTrue(any("[ADVANCED_HEAD]" in item for item in warnings))

        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        bound_path = root / contract["theory_bindings"][0]["path"]
        bound_path.write_text("changed after advancing HEAD\n", encoding="utf-8")
        failures = validate_contract(contract_path, repository_root=root)
        self.assertTrue(any("SHA-256 mismatch" in item for item in failures))

    def test_current_dirty_state_is_a_warning_not_historical_mismatch(self) -> None:
        temporary, root, contract_path = self._fixture()
        self.addCleanup(temporary.cleanup)
        (root / "unbound-scratch.txt").write_text("scratch\n", encoding="utf-8")

        warnings: list[str] = []
        failures = validate_contract(
            contract_path,
            repository_root=root,
            warnings=warnings,
        )
        self.assertEqual(failures, [])
        self.assertTrue(
            any("[CURRENT_DIRTY_WORKTREE]" in item for item in warnings)
        )

    def test_recorded_dirty_source_remains_an_explicit_warning(self) -> None:
        temporary, root, contract_path = self._fixture()
        self.addCleanup(temporary.cleanup)
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        contract["source_revision"]["repository_dirty"] = True
        contract["source_revision"]["reproducibility_status"] = (
            "DIRTY_BASE_COMMIT_WITH_HASH_BOUND_REPLAY_INPUTS_ONLY"
        )
        contract_path.write_text(json.dumps(contract) + "\n", encoding="utf-8")

        warnings: list[str] = []
        failures = validate_contract(
            contract_path,
            repository_root=root,
            warnings=warnings,
        )
        self.assertEqual(failures, [])
        self.assertTrue(any("[RECORDED_DIRTY_SOURCE]" in item for item in warnings))


if __name__ == "__main__":
    unittest.main()
