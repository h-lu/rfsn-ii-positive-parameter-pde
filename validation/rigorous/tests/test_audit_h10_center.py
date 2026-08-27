from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RIGOROUS = Path(__file__).resolve().parents[1]
AUDITOR = RIGOROUS / "audit_h10_center.py"

HEADER = b"""#pragma once

struct PolynomialTerm {
  int px;
  int py;
  const char* numerator;
  const char* denominator;
  bool times_sqrt_two;
};

inline constexpr PolynomialTerm kH1Terms[] = {
  {2, 0, "1", "2", false},
};

inline constexpr PolynomialTerm kH2Terms[] = {
  {1, 1, "-1", "3", false},
};

inline constexpr PolynomialTerm kDefect1Terms[] = {
  {3, 0, "5", "7", true},
};

inline constexpr PolynomialTerm kDefect2Terms[] = {
  {0, 3, "-11", "13", true},
};
"""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


class H10CenterAuditTests(unittest.TestCase):
    def make_repository(self, root: Path, *, generator_fails: bool = False) -> tuple[Path, str]:
        repository = root / "flagship"
        repository.mkdir()
        if generator_fails:
            generator = b"raise RuntimeError('deliberate execution failure')\n"
        else:
            generator = (
                b"import argparse\n"
                b"from pathlib import Path\n"
                b"p=argparse.ArgumentParser()\n"
                b"p.add_argument('--output',type=Path,required=True)\n"
                b"a=p.parse_args()\n"
                + f"a.output.write_bytes({HEADER!r})\n".encode()
            )
        (repository / "generator.py").write_bytes(generator)
        (repository / "terms.hpp").write_bytes(HEADER)
        subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
        subprocess.run(
            ["git", "config", "user.email", "audit@example.invalid"],
            cwd=repository,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "H10 Audit Test"],
            cwd=repository,
            check=True,
        )
        subprocess.run(["git", "add", "generator.py", "terms.hpp"], cwd=repository, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "fixture"], cwd=repository, check=True)
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        return repository, commit

    def command(self, repository: Path, commit: str) -> list[str]:
        generator = subprocess.run(
            ["git", "show", f"{commit}:generator.py"],
            cwd=repository,
            check=True,
            stdout=subprocess.PIPE,
        ).stdout
        return [
            sys.executable,
            "-B",
            str(AUDITOR),
            "--flagship-repository",
            str(repository),
            "--commit",
            commit,
            "--generator-path",
            "generator.py",
            "--generator-sha256",
            sha256(generator),
            "--header-path",
            "terms.hpp",
            "--header-sha256",
            sha256(HEADER),
            "--h1-term-count",
            "1",
            "--h2-term-count",
            "1",
            "--defect1-term-count",
            "1",
            "--defect2-term-count",
            "1",
            "--h-min-degree",
            "2",
            "--h-max-degree",
            "2",
            "--defect-min-degree",
            "3",
            "--defect-max-degree",
            "3",
        ]

    def execute(self, command: list[str]) -> tuple[subprocess.CompletedProcess[str], dict]:
        completed = subprocess.run(
            command,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
        return completed, json.loads(completed.stdout)

    def test_passes_byte_identical_exact_fixture(self) -> None:
        with tempfile.TemporaryDirectory(prefix="h10-audit-test-") as temporary:
            repository, commit = self.make_repository(Path(temporary))
            completed, report = self.execute(self.command(repository, commit))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(report["regeneration"]["byte_identical"])
        self.assertEqual(
            report["term_table_audit"]["arrays"]["kH1Terms"]["observed_term_count"],
            1,
        )

    def test_hash_mismatch_is_fail(self) -> None:
        with tempfile.TemporaryDirectory(prefix="h10-audit-test-") as temporary:
            repository, commit = self.make_repository(Path(temporary))
            command = self.command(repository, commit)
            index = command.index("--header-sha256") + 1
            command[index] = "0" * 64
            completed, report = self.execute(command)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("frozen term-table SHA-256 mismatch", report["failures"])

    def test_generator_execution_failure_is_inconclusive(self) -> None:
        with tempfile.TemporaryDirectory(prefix="h10-audit-test-") as temporary:
            repository, commit = self.make_repository(
                Path(temporary), generator_fails=True)
            completed, report = self.execute(self.command(repository, commit))
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(report["status"], "INCONCLUSIVE")
        self.assertEqual(report["regeneration"]["exit_code"], 1)

    def test_table_contract_mismatch_is_fail(self) -> None:
        with tempfile.TemporaryDirectory(prefix="h10-audit-test-") as temporary:
            repository, commit = self.make_repository(Path(temporary))
            command = self.command(repository, commit)
            index = command.index("--h1-term-count") + 1
            command[index] = "2"
            completed, report = self.execute(command)
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("kH1Terms term count" in item for item in report["failures"]))


if __name__ == "__main__":
    unittest.main()
