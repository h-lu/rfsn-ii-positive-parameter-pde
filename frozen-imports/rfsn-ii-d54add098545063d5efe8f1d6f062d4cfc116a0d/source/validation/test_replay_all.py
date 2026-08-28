#!/usr/bin/env python3
"""Adversarial regression tests for the unified replay trust boundary."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import replay_all as replay


class ReplayTrustBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(replay.DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        cls.lock = json.loads(replay.DEFAULT_LOCK.read_text(encoding="utf-8"))

    def test_runner_remapping_to_noop_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        package = next(
            item for item in manifest["packages"] if item["id"] == "future-target-fold"
        )
        package["runner"] = "toolchain-audit"
        package.pop("hash_contracts")
        with self.assertRaisesRegex(replay.ReplayError, "runner remapping"):
            replay.validate_manifest(manifest, self.lock)

    def test_claim_package_without_hash_contract_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        package = next(
            item for item in manifest["packages"] if item["id"] == "pole-cone-entry"
        )
        package.pop("hash_contracts")
        with self.assertRaisesRegex(replay.ReplayError, "has no hash contracts"):
            replay.validate_manifest(manifest, self.lock)

    def test_path_like_package_id_is_rejected(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["packages"][0]["id"] = "/tmp/replay-escape"
        with self.assertRaisesRegex(replay.ReplayError, "canonical slug"):
            replay.validate_manifest(manifest, self.lock)

    def test_all_profile_cannot_omit_a_mathematical_package(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["profiles"]["all"].remove("pole-cone-entry")
        with self.assertRaisesRegex(replay.ReplayError, "must name every mathematical package"):
            replay.validate_manifest(manifest, self.lock)

    def test_manifest_and_lock_are_mutually_bound(self) -> None:
        replay.validate_control_binding(
            self.manifest,
            self.lock,
            manifest_path=replay.DEFAULT_MANIFEST.resolve(),
            lock_path=replay.DEFAULT_LOCK.resolve(),
        )
        lock = copy.deepcopy(self.lock)
        lock["verification"]["manifest"] = "validation/README.md"
        with self.assertRaisesRegex(replay.ReplayError, "different manifest"):
            replay.validate_control_binding(
                self.manifest,
                lock,
                manifest_path=replay.DEFAULT_MANIFEST.resolve(),
                lock_path=replay.DEFAULT_LOCK.resolve(),
            )

    def test_external_control_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="paper-a-control-test-") as raw:
            external = Path(raw) / "manifest.json"
            external.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(replay.ReplayError, "inside the repository"):
                replay.controlled_repo_file(external, label="test manifest")

    def test_existing_work_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="paper-a-work-parent-") as raw:
            existing = Path(raw) / "existing"
            existing.mkdir()
            with self.assertRaisesRegex(replay.ReplayError, "new path"):
                replay.create_work_root(existing, keep_work=True)

    def test_symlinked_work_parent_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="paper-a-work-parent-") as raw:
            parent = Path(raw)
            real = parent / "real"
            real.mkdir()
            linked = parent / "linked"
            linked.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(replay.ReplayError, "symbolic-link component"):
                replay.create_work_root(linked / "new-run", keep_work=True)

    def test_symlinked_package_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="paper-a-work-") as raw:
            root = Path(raw).resolve()
            target = root / "outside-target"
            target.mkdir()
            (root / "future-target-fold").symlink_to(target, target_is_directory=True)
            context = replay.ReplayContext(
                work_root=root,
                lock=self.lock,
                capd_source=root / "capd",
                capd_config=root / "capd-config",
                jobs=1,
                report={},
            )
            with self.assertRaisesRegex(replay.ReplayError, "symbolic link"):
                context.package_dir("future-target-fold")

    def test_inherited_build_and_python_overrides_are_removed(self) -> None:
        hostile = {
            "BASH_ENV": "/tmp/evil",
            "CXX": "/tmp/evil-cxx",
            "PAPERA_POLE_ENTRY_CXX": "/tmp/evil-papera-cxx",
            "PYTHON": "/tmp/evil-python",
            "PYTHONNOUSERSITE": "1",
            "PYTHONPATH": "/tmp/evil-modules",
        }
        with tempfile.TemporaryDirectory(prefix="paper-a-env-") as raw, mock.patch.dict(
            os.environ, hostile, clear=False
        ):
            root = Path(raw).resolve()
            context = replay.ReplayContext(
                work_root=root,
                lock=self.lock,
                capd_source=root / "capd",
                capd_config=root / "capd-config",
                jobs=1,
                report={},
            )
            self.assertNotIn("BASH_ENV", context.environment)
            self.assertNotIn("CXX", context.environment)
            self.assertNotIn("PAPERA_POLE_ENTRY_CXX", context.environment)
            self.assertNotIn("PYTHONNOUSERSITE", context.environment)
            self.assertNotIn("PYTHONPATH", context.environment)
            self.assertEqual(
                context.environment["PYTHON"], str(Path(os.sys.executable).absolute())
            )

    def test_link_search_directory_resolves_static_library(self) -> None:
        with tempfile.TemporaryDirectory(prefix="paper-a-link-search-") as raw:
            directory = Path(raw)
            library = directory / "libcapd.a"
            library.write_bytes(b"locked archive")
            observed = replay.resolve_linked_library(
                Path("/usr/bin/g++"),
                [f"-L{directory}", "-lcapd"],
                "libcapd.a",
                environment=os.environ.copy(),
            )
            self.assertEqual(observed, library.resolve())

    def test_dirty_success_is_never_a_release_pass(self) -> None:
        all_order = ["toolchain-metadata-audit", "main-package"]
        report = {
            "profile": "all",
            "package_order": all_order,
            "preflight": {"checks": {"repository_clean": False}},
            "postflight": {"repository_clean": False},
        }
        replay.finalize_success_status(
            report,
            all_profile_package_order=all_order,
        )
        self.assertNotEqual(report["status"], "PASS")
        self.assertFalse(report["profile_replay_pass"])
        self.assertFalse(report["release_eligible"])

    def test_clean_all_profile_is_release_eligible(self) -> None:
        all_order = ["toolchain-metadata-audit", "main-package"]
        report = {
            "profile": "all",
            "package_order": all_order,
            "preflight": {"checks": {"repository_clean": True}},
            "postflight": {"repository_clean": True},
        }
        replay.finalize_success_status(
            report,
            all_profile_package_order=all_order,
        )
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["profile_replay_pass"])
        self.assertTrue(report["release_eligible"])

    def test_clean_non_all_profile_pass_is_not_release_eligible(self) -> None:
        all_order = ["toolchain-metadata-audit", "main-package", "ancillary-package"]
        report = {
            "profile": "main-theorem",
            "package_order": ["toolchain-metadata-audit", "main-package"],
            "preflight": {"checks": {"repository_clean": True}},
            "postflight": {"repository_clean": True},
        }
        replay.finalize_success_status(
            report,
            all_profile_package_order=all_order,
        )
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["profile_replay_pass"])
        self.assertFalse(report["release_eligible"])

    def test_clean_all_profile_with_incomplete_order_is_not_release_eligible(self) -> None:
        all_order = ["toolchain-metadata-audit", "main-package", "ancillary-package"]
        report = {
            "profile": "all",
            "package_order": ["toolchain-metadata-audit", "main-package"],
            "preflight": {"checks": {"repository_clean": True}},
            "postflight": {"repository_clean": True},
        }
        replay.finalize_success_status(
            report,
            all_profile_package_order=all_order,
        )
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["profile_replay_pass"])
        self.assertFalse(report["release_eligible"])


if __name__ == "__main__":
    unittest.main()
