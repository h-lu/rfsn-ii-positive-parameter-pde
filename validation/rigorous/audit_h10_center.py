#!/usr/bin/env python3
"""Audit the frozen degree-ten core graph without reading a live worktree.

The audit reads the generator and generated term table only through
``git show COMMIT:PATH``.  It then reruns the frozen generator in a temporary
directory, requires byte-identical output, and checks the four polynomial
arrays against preregistered combinatorial contracts.

Exit codes follow the rigorous-validation verdict lattice:

* 0: PASS;
* 1: FAIL (a hash, exact-output, or mathematical table contract differs);
* 2: INCONCLUSIVE (the audit could not be executed completely).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Sequence


SCHEMA_VERSION = "rfsn-vdp-h10-center-audit/1"
VERDICT_EXIT = {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 2}
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ARRAY_DECLARATION_RE = re.compile(
    r"inline\s+constexpr\s+PolynomialTerm\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\[\s*\]\s*=\s*\{"
    r"(?P<body>.*?)\};",
    re.DOTALL,
)
TERM_RE = re.compile(
    r"\{\s*(?P<px>[0-9]+)\s*,\s*(?P<py>[0-9]+)\s*,\s*"
    r'"(?P<numerator>-?(?:0|[1-9][0-9]*))"\s*,\s*'
    r'"(?P<denominator>(?:0|[1-9][0-9]*))"\s*,\s*'
    r"(?P<sqrt>true|false)\s*\}\s*,?",
)


class ArgumentError(ValueError):
    """Raised instead of emitting a non-JSON argparse diagnostic."""


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ArgumentError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def command_record(
    argv: Sequence[str], completed: subprocess.CompletedProcess[bytes]
) -> dict[str, Any]:
    return {
        "argv": list(argv),
        "exit_code": completed.returncode,
        "stdout_sha256": sha256_bytes(completed.stdout),
        "stderr_sha256": sha256_bytes(completed.stderr),
    }


def safe_tree_path(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not value
        or value.startswith("/")
        or path.is_absolute()
        or path == PurePosixPath(".")
        or ".." in path.parts
        or ":" in value
        or "\x00" in value
        or "\n" in value
        or "\r" in value
    ):
        raise ArgumentError(f"unsafe Git tree path: {value!r}")
    return value


def run_bytes(
    argv: Sequence[str], *, cwd: Path | None = None, timeout: int
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        list(argv),
        cwd=cwd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def read_frozen_object(
    repository: Path,
    commit: str,
    tree_path: str,
    expected_sha256: str,
    timeout: int,
) -> tuple[bytes | None, dict[str, Any], str | None]:
    argv = ["git", "-C", str(repository), "show", f"{commit}:{tree_path}"]
    try:
        completed = run_bytes(argv, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as error:
        return None, {
            "path": tree_path,
            "expected_sha256": expected_sha256,
            "git_show": {"argv": argv, "exception": str(error)},
        }, f"cannot read frozen object {tree_path}: {error}"

    record = {
        "path": tree_path,
        "expected_sha256": expected_sha256,
        "git_show": command_record(argv, completed),
    }
    if completed.returncode != 0:
        return None, record, (
            f"git show failed for frozen object {tree_path} "
            f"with exit code {completed.returncode}"
        )
    observed_sha256 = sha256_bytes(completed.stdout)
    record["observed_sha256"] = observed_sha256
    record["hash_matches"] = observed_sha256 == expected_sha256
    return completed.stdout, record, None


def parse_array(
    name: str,
    body: str,
    *,
    expected_count: int,
    minimum_degree: int,
    maximum_degree: int,
    expected_sqrt_flag: bool,
) -> tuple[dict[str, Any], list[str]]:
    failures: list[str] = []
    terms: list[dict[str, Any]] = []
    cursor = 0
    for match in TERM_RE.finditer(body):
        if body[cursor:match.start()].strip():
            failures.append(f"{name} contains unparsed text before term {len(terms)}")
        cursor = match.end()
        px = int(match.group("px"))
        py = int(match.group("py"))
        numerator = int(match.group("numerator"))
        denominator = int(match.group("denominator"))
        sqrt_flag = match.group("sqrt") == "true"
        terms.append({
            "px": px,
            "py": py,
            "numerator": numerator,
            "denominator": denominator,
            "times_sqrt_two": sqrt_flag,
        })
    if body[cursor:].strip():
        failures.append(f"{name} contains trailing unparsed text")

    monomials = [(term["px"], term["py"]) for term in terms]
    duplicate_monomials = sorted({
        monomial for monomial in monomials if monomials.count(monomial) > 1
    })
    nonpositive_denominators = sorted({
        (term["px"], term["py"])
        for term in terms
        if term["denominator"] <= 0
    })
    wrong_sqrt_flags = sorted({
        (term["px"], term["py"])
        for term in terms
        if term["times_sqrt_two"] is not expected_sqrt_flag
    })
    degrees = sorted({term["px"] + term["py"] for term in terms})
    expected_degrees = list(range(minimum_degree, maximum_degree + 1))

    if len(terms) != expected_count:
        failures.append(
            f"{name} term count {len(terms)} differs from {expected_count}"
        )
    if duplicate_monomials:
        failures.append(f"{name} has repeated monomials: {duplicate_monomials}")
    if nonpositive_denominators:
        failures.append(
            f"{name} has nonpositive denominators at {nonpositive_denominators}"
        )
    if wrong_sqrt_flags:
        failures.append(
            f"{name} has incorrect times_sqrt_two flags at {wrong_sqrt_flags}"
        )
    if degrees != expected_degrees:
        failures.append(
            f"{name} total degrees {degrees} differ from {expected_degrees}"
        )

    record = {
        "expected_term_count": expected_count,
        "observed_term_count": len(terms),
        "expected_total_degree_range": [minimum_degree, maximum_degree],
        "observed_total_degrees": degrees,
        "expected_times_sqrt_two": expected_sqrt_flag,
        "duplicate_monomials": [list(value) for value in duplicate_monomials],
        "nonpositive_denominator_monomials": [
            list(value) for value in nonpositive_denominators
        ],
        "incorrect_sqrt_flag_monomials": [
            list(value) for value in wrong_sqrt_flags
        ],
    }
    return record, failures


def audit_header(
    header: bytes,
    *,
    h1_count: int,
    h2_count: int,
    defect1_count: int,
    defect2_count: int,
    h_min_degree: int,
    h_max_degree: int,
    defect_min_degree: int,
    defect_max_degree: int,
) -> tuple[dict[str, Any], list[str]]:
    try:
        text = header.decode("utf-8")
    except UnicodeDecodeError as error:
        return {}, [f"frozen header is not UTF-8: {error}"]

    declarations = list(ARRAY_DECLARATION_RE.finditer(text))
    expected_names = {
        "kH1Terms",
        "kH2Terms",
        "kDefect1Terms",
        "kDefect2Terms",
    }
    observed_names = [match.group("name") for match in declarations]
    failures: list[str] = []
    if len(observed_names) != len(set(observed_names)):
        failures.append("term table contains repeated array declarations")
    if set(observed_names) != expected_names:
        failures.append(
            "term-table arrays differ: "
            f"observed={sorted(set(observed_names))}, "
            f"expected={sorted(expected_names)}"
        )

    specifications = {
        "kH1Terms": (h1_count, h_min_degree, h_max_degree, False),
        "kH2Terms": (h2_count, h_min_degree, h_max_degree, False),
        "kDefect1Terms": (
            defect1_count, defect_min_degree, defect_max_degree, True),
        "kDefect2Terms": (
            defect2_count, defect_min_degree, defect_max_degree, True),
    }
    records: dict[str, Any] = {}
    by_name = {match.group("name"): match for match in declarations}
    for name, specification in specifications.items():
        match = by_name.get(name)
        if match is None:
            continue
        record, array_failures = parse_array(
            name,
            match.group("body"),
            expected_count=specification[0],
            minimum_degree=specification[1],
            maximum_degree=specification[2],
            expected_sqrt_flag=specification[3],
        )
        records[name] = record
        failures.extend(array_failures)

    return {
        "expected_array_names": sorted(expected_names),
        "observed_array_names": observed_names,
        "arrays": records,
    }, failures


def positive_integer(value: str) -> int:
    result = int(value)
    if result <= 0:
        raise argparse.ArgumentTypeError("expected a positive integer")
    return result


def nonnegative_integer(value: str) -> int:
    result = int(value)
    if result < 0:
        raise argparse.ArgumentTypeError("expected a nonnegative integer")
    return result


def sha1(value: str) -> str:
    if not SHA1_RE.fullmatch(value):
        raise argparse.ArgumentTypeError("expected a lowercase 40-digit SHA-1")
    return value


def sha256(value: str) -> str:
    if not SHA256_RE.fullmatch(value):
        raise argparse.ArgumentTypeError("expected a lowercase 64-digit SHA-256")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = JsonArgumentParser(description=__doc__)
    parser.add_argument("--flagship-repository", type=Path, required=True)
    parser.add_argument("--commit", type=sha1, required=True)
    parser.add_argument("--generator-path", type=safe_tree_path, required=True)
    parser.add_argument("--generator-sha256", type=sha256, required=True)
    parser.add_argument("--header-path", type=safe_tree_path, required=True)
    parser.add_argument("--header-sha256", type=sha256, required=True)
    parser.add_argument("--h1-term-count", type=positive_integer, required=True)
    parser.add_argument("--h2-term-count", type=positive_integer, required=True)
    parser.add_argument("--defect1-term-count", type=positive_integer, required=True)
    parser.add_argument("--defect2-term-count", type=positive_integer, required=True)
    parser.add_argument("--h-min-degree", type=nonnegative_integer, required=True)
    parser.add_argument("--h-max-degree", type=nonnegative_integer, required=True)
    parser.add_argument("--defect-min-degree", type=nonnegative_integer, required=True)
    parser.add_argument("--defect-max-degree", type=nonnegative_integer, required=True)
    parser.add_argument("--timeout-seconds", type=positive_integer, default=900)
    return parser


def inconclusive_report(
    reason: str, arguments: argparse.Namespace | None = None
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "INCONCLUSIVE",
        "frozen_objects": {},
        "regeneration": {},
        "term_table_audit": {},
        "failures": [],
        "inconclusive_reasons": [reason],
    }
    if arguments is not None:
        report["flagship_repository"] = str(
            arguments.flagship_repository.resolve())
        report["commit"] = arguments.commit
    return report


def run_audit(arguments: argparse.Namespace) -> dict[str, Any]:
    repository = arguments.flagship_repository.resolve()
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "INCONCLUSIVE",
        "flagship_repository": str(repository),
        "commit": arguments.commit,
        "frozen_objects": {},
        "regeneration": {},
        "term_table_audit": {},
        "failures": [],
        "inconclusive_reasons": [],
    }
    if not repository.is_dir():
        report["inconclusive_reasons"].append(
            f"flagship repository is not a directory: {repository}")
        return report
    if arguments.h_min_degree > arguments.h_max_degree:
        report["inconclusive_reasons"].append(
            "H minimum degree exceeds its maximum degree")
        return report
    if arguments.defect_min_degree > arguments.defect_max_degree:
        report["inconclusive_reasons"].append(
            "defect minimum degree exceeds its maximum degree")
        return report

    generator, generator_record, generator_error = read_frozen_object(
        repository,
        arguments.commit,
        arguments.generator_path,
        arguments.generator_sha256,
        arguments.timeout_seconds,
    )
    header, header_record, header_error = read_frozen_object(
        repository,
        arguments.commit,
        arguments.header_path,
        arguments.header_sha256,
        arguments.timeout_seconds,
    )
    report["frozen_objects"] = {
        "generator": generator_record,
        "term_table": header_record,
    }
    for error in (generator_error, header_error):
        if error is not None:
            report["inconclusive_reasons"].append(error)
    if report["inconclusive_reasons"]:
        return report
    assert generator is not None and header is not None

    if generator_record["observed_sha256"] != arguments.generator_sha256:
        report["failures"].append("frozen generator SHA-256 mismatch")
    if header_record["observed_sha256"] != arguments.header_sha256:
        report["failures"].append("frozen term-table SHA-256 mismatch")
    if report["failures"]:
        report["status"] = "FAIL"
        return report

    with tempfile.TemporaryDirectory(prefix="rfsn-h10-center-") as temporary:
        temporary_path = Path(temporary)
        generator_file = temporary_path / "generate_polynomial_header.py"
        frozen_header_file = temporary_path / "unstable_graph_terms.frozen.hpp"
        regenerated_header_file = temporary_path / "unstable_graph_terms.hpp"
        generator_file.write_bytes(generator)
        frozen_header_file.write_bytes(header)
        argv = [
            sys.executable,
            "-B",
            str(generator_file),
            "--output",
            str(regenerated_header_file),
        ]
        environment = os.environ.copy()
        environment.update({
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONHASHSEED": "0",
            "LC_ALL": "C.UTF-8",
        })
        try:
            completed = subprocess.run(
                argv,
                cwd=temporary_path,
                env=environment,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=arguments.timeout_seconds,
            )
        except (OSError, subprocess.SubprocessError) as error:
            report["regeneration"] = {
                "argv": argv,
                "exception": str(error),
            }
            report["inconclusive_reasons"].append(
                f"frozen generator execution failed: {error}")
            return report

        regeneration = command_record(argv, completed)
        regeneration["output_exists"] = regenerated_header_file.is_file()
        if regenerated_header_file.is_file():
            regenerated = regenerated_header_file.read_bytes()
            regeneration["regenerated_sha256"] = sha256_bytes(regenerated)
            regeneration["frozen_sha256"] = sha256_bytes(header)
            regeneration["byte_identical"] = regenerated == header
        else:
            regenerated = None
        report["regeneration"] = regeneration

        if completed.returncode != 0:
            report["inconclusive_reasons"].append(
                "frozen generator returned nonzero exit code "
                f"{completed.returncode}")
            return report
        if regenerated is None:
            report["inconclusive_reasons"].append(
                "frozen generator returned success without an output header")
            return report
        if regenerated != header:
            report["failures"].append(
                "regenerated term table is not byte-identical to the frozen table")

    table_audit, table_failures = audit_header(
        header,
        h1_count=arguments.h1_term_count,
        h2_count=arguments.h2_term_count,
        defect1_count=arguments.defect1_term_count,
        defect2_count=arguments.defect2_term_count,
        h_min_degree=arguments.h_min_degree,
        h_max_degree=arguments.h_max_degree,
        defect_min_degree=arguments.defect_min_degree,
        defect_max_degree=arguments.defect_max_degree,
    )
    report["term_table_audit"] = table_audit
    report["failures"].extend(table_failures)
    report["status"] = "FAIL" if report["failures"] else "PASS"
    return report


def main(argv: Sequence[str] | None = None) -> int:
    arguments: argparse.Namespace | None = None
    try:
        arguments = build_parser().parse_args(argv)
        report = run_audit(arguments)
    except (ArgumentError, argparse.ArgumentTypeError, ValueError) as error:
        report = inconclusive_report(
            f"invalid audit arguments: {error}", arguments)
    except Exception as error:  # Fail closed on an unclassified execution error.
        report = inconclusive_report(
            f"unhandled audit execution failure: {type(error).__name__}: {error}",
            arguments,
        )
    print(json.dumps(report, indent=2, sort_keys=True))
    return VERDICT_EXIT[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
