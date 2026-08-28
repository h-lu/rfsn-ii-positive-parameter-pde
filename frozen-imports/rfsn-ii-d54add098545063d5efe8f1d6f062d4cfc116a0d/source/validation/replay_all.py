#!/usr/bin/env python3
"""Fail-closed orchestrator for the Paper A interval validation packages.

The driver distinguishes four things that must not be conflated:

* a static source/dependency hash audit;
* a pinned toolchain preflight;
* execution of every package gate in a selected dependency profile; and
* exact or package-specific semantic comparison with the tracked certificate.

``--dry-run`` performs only the first item and never reports a mathematical
replay PASS.  ``--preflight-only`` adds the second item.  A normal run reports
PASS only after all four items required by the selected profile succeed.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT_MANIFEST = HERE / "replay_manifest.json"
DEFAULT_LOCK = HERE / "environment.lock.json"

PACKAGE_ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
EXPECTED_RUNNER_BY_PACKAGE = {
    "toolchain-metadata-audit": "toolchain-audit",
    "future-target-fold": "future-target-fold",
    "origin-algebraic-heteroclinic": "origin-algebraic-heteroclinic",
    "universal-core-symmetric-homoclinic": "universal-core-symmetric-homoclinic",
    "origin-unstable-pole-entry": "origin-unstable-pole-entry",
    "exact-source-outer-fold": "exact-source-outer-fold",
    "finite-source-intermediate-collar": "finite-source-intermediate-collar",
    "fixed-fold-event-bridge": "fixed-fold-event-bridge",
    "fundamental-annulus-overlap": "fundamental-annulus-overlap",
    "finite-source-spiral-extension": "finite-source-spiral-extension",
    "pole-cone-entry": "pole-cone-entry",
    "universal-core-periodic-return": "universal-core-periodic-return",
}
NONCLAIM_RUNNERS = {"toolchain-audit"}
BLOCKED_ENVIRONMENT_KEYS = {
    "BASH_ENV",
    "CC",
    "CFLAGS",
    "COMPILER_PATH",
    "CPATH",
    "CPP",
    "CPPFLAGS",
    "CPLUS_INCLUDE_PATH",
    "CXX",
    "CXXFLAGS",
    "DYLD_INSERT_LIBRARIES",
    "DYLD_LIBRARY_PATH",
    "ENV",
    "GCC_EXEC_PREFIX",
    "LD_LIBRARY_PATH",
    "LD_PRELOAD",
    "LIBRARY_PATH",
    "PYTHON",
    "PYTHONHOME",
    "PYTHONNOUSERSITE",
    "PYTHONOPTIMIZE",
    "PYTHONPATH",
    "PYTHONSTARTUP",
    "PYTHONUSERBASE",
    "PYTHONWARNINGS",
    "PKG_CONFIG_DIR",
    "PKG_CONFIG_LIBDIR",
    "PKG_CONFIG_PATH",
}


class ReplayError(RuntimeError):
    """A fail-closed replay, manifest, comparison, or preflight failure."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReplayError(f"cannot read JSON {path}: {exc}") from exc


def canonical_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def json_pointer(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise ReplayError(f"invalid JSON pointer: {pointer!r}")
    value = document
    for raw in pointer[1:].split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            try:
                value = value[int(key)]
            except (ValueError, IndexError) as exc:
                raise ReplayError(f"JSON pointer misses list item {pointer!r}") from exc
        elif isinstance(value, dict) and key in value:
            value = value[key]
        else:
            raise ReplayError(f"JSON pointer misses {key!r} in {pointer!r}")
    return value


def safe_repo_path(raw: str) -> Path:
    if not isinstance(raw, str) or not raw:
        raise ReplayError(f"repository path must be a nonempty string: {raw!r}")
    path = (REPO / raw).resolve()
    try:
        path.relative_to(REPO)
    except ValueError as exc:
        raise ReplayError(f"manifest path leaves repository: {raw!r}") from exc
    return path


def controlled_repo_file(path: Path, *, label: str) -> Path:
    """Resolve a control file and require a regular, non-symlink repo member."""

    expanded = path.expanduser()
    candidate = expanded if expanded.is_absolute() else Path.cwd() / expanded
    if candidate.is_symlink():
        raise ReplayError(f"{label} must not be a symbolic link: {candidate}")
    resolved = candidate.resolve()
    try:
        resolved.relative_to(REPO)
    except ValueError as exc:
        raise ReplayError(f"{label} must be inside the repository: {resolved}") from exc
    if not resolved.is_file():
        raise ReplayError(f"{label} is not a regular file: {resolved}")
    return resolved


def require_repo_relative_control_path(
    raw: Any, *, label: str, must_exist: bool = True
) -> Path:
    """Validate a canonical POSIX path stored inside a control document."""

    if not isinstance(raw, str) or not raw:
        raise ReplayError(f"{label} must be a nonempty repository-relative path")
    posix = PurePosixPath(raw)
    if (
        posix.is_absolute()
        or raw != posix.as_posix()
        or any(part in {"", ".", ".."} for part in posix.parts)
    ):
        raise ReplayError(f"{label} is unsafe or non-canonical: {raw!r}")
    candidate = REPO / raw
    if candidate.is_symlink():
        raise ReplayError(f"{label} must not be a symbolic link: {raw}")
    path = safe_repo_path(raw)
    if must_exist and not path.is_file():
        raise ReplayError(f"{label} must name a regular, non-symlink file: {raw}")
    return path


def resolve_executable(raw: str, *, label: str) -> Path:
    located = shutil.which(raw)
    if located is None:
        candidate = Path(raw).expanduser()
        if not candidate.is_file():
            raise ReplayError(f"cannot resolve {label}: {raw!r}")
        located = str(candidate)
    path = Path(located).absolute()
    if not path.is_file() or not os.access(path, os.X_OK):
        raise ReplayError(f"{label} is not an executable file: {path}")
    return path


def resolve_linked_library(
    compiler: Path,
    link_tokens: list[str],
    filename: str,
    *,
    environment: dict[str, str],
) -> Path:
    for token in link_tokens:
        candidate = Path(token)
        if candidate.name == filename and candidate.is_file():
            return candidate.resolve()

    search_flags: list[str] = []
    search_directories: list[Path] = []
    index = 0
    while index < len(link_tokens):
        token = link_tokens[index]
        if token == "-L" and index + 1 < len(link_tokens):
            search_flags.extend([token, link_tokens[index + 1]])
            search_directories.append(Path(link_tokens[index + 1]))
            index += 2
            continue
        if token.startswith("-L") and len(token) > 2:
            search_flags.append(token)
            search_directories.append(Path(token[2:]))
        index += 1
    matches = [
        (directory / filename).resolve()
        for directory in search_directories
        if (directory / filename).is_file()
    ]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise ReplayError(
            f"link flags resolve {filename} ambiguously: "
            f"{[str(path) for path in matches]}"
        )
    observed = run_capture(
        [str(compiler), *search_flags, f"-print-file-name={filename}"],
        environment=environment,
    )
    candidate = Path(observed)
    if observed == filename or not candidate.is_file():
        raise ReplayError(f"compiler cannot resolve linked library {filename}")
    return candidate.resolve()


def run_capture(
    argv: list[str],
    *,
    cwd: Path | None = None,
    environment: dict[str, str] | None = None,
) -> str:
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            env=environment,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = ""
        if isinstance(exc, subprocess.CalledProcessError):
            detail = (exc.stderr or exc.stdout or "").strip()
        raise ReplayError(f"command failed: {shlex.join(argv)}\n{detail}") from exc
    return completed.stdout.strip()


def git_value(*args: str) -> str:
    return run_capture(["git", "-C", str(REPO), *args])


def discovered_certificates() -> set[str]:
    paths: set[str] = set()
    for path in HERE.rglob("*.json"):
        if path.name == "certificate.json" or path.name.endswith("_certificate.json"):
            paths.add(path.relative_to(REPO).as_posix())
    return paths


def validate_control_binding(
    manifest: dict[str, Any],
    lock: dict[str, Any],
    *,
    manifest_path: Path,
    lock_path: Path,
) -> None:
    declared_lock = require_repo_relative_control_path(
        manifest.get("environment_lock"), label="manifest environment_lock"
    )
    if declared_lock != lock_path:
        raise ReplayError(
            "selected environment lock differs from the repository path bound by the manifest: "
            f"{lock_path} != {declared_lock}"
        )

    verification = lock.get("verification")
    if not isinstance(verification, dict):
        raise ReplayError("environment lock verification must be an object")
    declared_manifest = require_repo_relative_control_path(
        verification.get("manifest"), label="environment-lock manifest"
    )
    declared_driver = require_repo_relative_control_path(
        verification.get("driver"), label="environment-lock driver"
    )
    declared_verifier = require_repo_relative_control_path(
        verification.get("toolchain_verifier"),
        label="environment-lock toolchain_verifier",
    )
    if declared_manifest != manifest_path:
        raise ReplayError(
            "environment lock is bound to a different manifest: "
            f"{declared_manifest} != {manifest_path}"
        )
    if declared_driver != Path(__file__).resolve():
        raise ReplayError(
            "environment lock is bound to a different replay driver: "
            f"{declared_driver} != {Path(__file__).resolve()}"
        )
    expected_verifier = (HERE / "toolchain-metadata-audit" / "verify.py").resolve()
    if declared_verifier != expected_verifier:
        raise ReplayError(
            "environment lock is bound to a different toolchain verifier: "
            f"{declared_verifier} != {expected_verifier}"
        )


def validate_manifest(manifest: dict[str, Any], lock: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if manifest.get("schema_version") != 1:
        raise ReplayError("replay manifest must have schema_version 1")
    if lock.get("schema_version") != 1:
        raise ReplayError("environment lock must have schema_version 1")

    raw_packages = manifest.get("packages")
    if not isinstance(raw_packages, list) or not raw_packages:
        raise ReplayError("manifest packages must be a nonempty list")
    packages: dict[str, dict[str, Any]] = {}
    for package in raw_packages:
        if not isinstance(package, dict):
            raise ReplayError("every manifest package must be an object")
        package_id = package.get("id")
        if not isinstance(package_id, str) or not package_id:
            raise ReplayError("every package needs a nonempty id")
        if PACKAGE_ID_RE.fullmatch(package_id) is None:
            raise ReplayError(f"package id is not a canonical slug: {package_id!r}")
        if package_id in packages:
            raise ReplayError(f"duplicate package id: {package_id}")
        expected_runner = EXPECTED_RUNNER_BY_PACKAGE.get(package_id)
        if expected_runner is None:
            raise ReplayError(f"manifest contains an unknown package id: {package_id}")
        if package.get("runner") != expected_runner:
            raise ReplayError(
                f"runner remapping is forbidden for {package_id}: "
                f"expected {expected_runner!r}, got {package.get('runner')!r}"
            )
        if package.get("category") not in {
            "provenance-addendum",
            "source-rebuildable",
            "source-verifiable-only",
        }:
            raise ReplayError(f"invalid evidence category for {package_id}")
        for field in ("evidence_role", "comparison"):
            if not isinstance(package.get(field), str) or not package[field].strip():
                raise ReplayError(f"package {package_id} has invalid {field}")
        command_summary = package.get("command_summary")
        if not isinstance(command_summary, list) or not command_summary or not all(
            isinstance(command, str) and command.strip() for command in command_summary
        ):
            raise ReplayError(f"package {package_id} has invalid command_summary")
        certificates = package.get("certificates")
        if not isinstance(certificates, list) or not certificates:
            raise ReplayError(f"package {package_id} has no certificate list")
        if len(certificates) != len(set(certificates)):
            raise ReplayError(f"package {package_id} repeats a certificate")
        for raw in certificates:
            certificate = require_repo_relative_control_path(
                raw, label=f"certificate for {package_id}"
            )
            load_json(certificate)

        contracts = package.get("hash_contracts", [])
        if expected_runner not in NONCLAIM_RUNNERS and (
            not isinstance(contracts, list) or not contracts
        ):
            raise ReplayError(f"claim-bearing package {package_id} has no hash contracts")
        if not isinstance(contracts, list):
            raise ReplayError(f"hash contracts for {package_id} must be a list")
        for contract in contracts:
            if not isinstance(contract, dict):
                raise ReplayError(f"invalid hash contract in {package_id}")
            contract_certificate = contract.get("certificate")
            if contract_certificate not in certificates:
                raise ReplayError(
                    f"hash contract in {package_id} uses an undeclared certificate: "
                    f"{contract_certificate!r}"
                )
            require_repo_relative_control_path(
                contract_certificate,
                label=f"hash-contract certificate for {package_id}",
            )
            pointer = contract.get("pointer")
            if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
                raise ReplayError(f"invalid JSON pointer in hash contract for {package_id}")
            has_file = "file" in contract
            has_base = "base" in contract
            if has_file == has_base:
                raise ReplayError(
                    f"hash contract in {package_id} must declare exactly one of file or base"
                )
            if has_file:
                require_repo_relative_control_path(
                    contract["file"], label=f"hash-contract file for {package_id}"
                )
            else:
                base = contract["base"]
                if not isinstance(base, str) or not base:
                    raise ReplayError(f"invalid hash-contract base for {package_id}")
                if base != ".":
                    require_repo_relative_control_path(
                        base,
                        label=f"hash-contract base for {package_id}",
                        must_exist=False,
                    )
                overrides = contract.get("overrides", {})
                if not isinstance(overrides, dict) or not all(
                    isinstance(key, str) and isinstance(value, str)
                    for key, value in overrides.items()
                ):
                    raise ReplayError(f"invalid hash-contract overrides for {package_id}")
                for value in overrides.values():
                    require_repo_relative_control_path(
                        value,
                        label=f"hash-contract override for {package_id}",
                        must_exist=False,
                    )
        packages[package_id] = package

    expected_packages = set(EXPECTED_RUNNER_BY_PACKAGE)
    if set(packages) != expected_packages:
        raise ReplayError(
            "manifest package inventory differs from the fixed replay implementation; "
            f"missing={sorted(expected_packages - packages.keys())}, "
            f"extra={sorted(packages.keys() - expected_packages)}"
        )

    for package_id, package in packages.items():
        dependencies = package.get("dependencies")
        if not isinstance(dependencies, list):
            raise ReplayError(f"dependencies for {package_id} must be a list")
        if not all(
            isinstance(dependency, str)
            and PACKAGE_ID_RE.fullmatch(dependency) is not None
            for dependency in dependencies
        ):
            raise ReplayError(f"package {package_id} has a non-slug dependency")
        if len(dependencies) != len(set(dependencies)):
            raise ReplayError(f"package {package_id} repeats a dependency")
        unknown = sorted(set(dependencies) - packages.keys())
        if unknown:
            raise ReplayError(f"unknown dependencies for {package_id}: {unknown}")

    profiles = manifest.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ReplayError("manifest profiles must be a nonempty object")
    for name, selected in profiles.items():
        if PACKAGE_ID_RE.fullmatch(name) is None:
            raise ReplayError(f"profile name is not a canonical slug: {name!r}")
        if not isinstance(selected, list) or not selected:
            raise ReplayError(f"profile {name} must be a nonempty list")
        if not all(
            isinstance(package_id, str)
            and PACKAGE_ID_RE.fullmatch(package_id) is not None
            for package_id in selected
        ):
            raise ReplayError(f"profile {name} contains a non-slug package id")
        if len(selected) != len(set(selected)):
            raise ReplayError(f"profile {name} repeats a package")
        unknown = sorted(set(selected) - packages.keys())
        if unknown:
            raise ReplayError(f"profile {name} contains unknown packages: {unknown}")
    expected_all = set(packages) - {"toolchain-metadata-audit"}
    if set(profiles.get("all", [])) != expected_all:
        raise ReplayError(
            "profile 'all' must name every mathematical package exactly once; "
            f"missing={sorted(expected_all - set(profiles.get('all', [])))}, "
            f"extra={sorted(set(profiles.get('all', [])) - expected_all)}"
        )

    historical = manifest.get("historical_json_only_packages")
    if not isinstance(historical, list) or len(historical) != len(set(historical)):
        raise ReplayError("historical_json_only_packages must be a duplicate-free list")
    unknown_historical = sorted(set(historical) - packages.keys())
    if unknown_historical:
        raise ReplayError(
            f"historical_json_only_packages contains unknown packages: {unknown_historical}"
        )

    declared_certificates = {
        raw
        for package in packages.values()
        for raw in package["certificates"]
    }
    found_certificates = discovered_certificates()
    if declared_certificates != found_certificates:
        raise ReplayError(
            "manifest/certificate inventory mismatch; "
            f"undeclared={sorted(found_certificates - declared_certificates)}, "
            f"stale={sorted(declared_certificates - found_certificates)}"
        )

    # Topologically sorting every package also detects a cycle.
    topological_order(packages, set(packages))
    return packages


def dependency_closure(packages: dict[str, dict[str, Any]], selected: list[str]) -> set[str]:
    closure = set(selected)
    stack = list(selected)
    while stack:
        package_id = stack.pop()
        for dependency in packages[package_id]["dependencies"]:
            if dependency not in closure:
                closure.add(dependency)
                stack.append(dependency)
    return closure


def topological_order(
    packages: dict[str, dict[str, Any]], selected: set[str]
) -> list[str]:
    temporary: set[str] = set()
    permanent: set[str] = set()
    order: list[str] = []

    def visit(package_id: str) -> None:
        if package_id in permanent:
            return
        if package_id in temporary:
            raise ReplayError(f"cycle in replay dependency graph at {package_id}")
        temporary.add(package_id)
        for dependency in packages[package_id]["dependencies"]:
            if dependency in selected:
                visit(dependency)
        temporary.remove(package_id)
        permanent.add(package_id)
        order.append(package_id)

    for package_id in sorted(selected):
        visit(package_id)
    return order


def static_hash_audit(
    packages: dict[str, dict[str, Any]], order: list[str]
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    certificate_cache: dict[Path, Any] = {}
    for package_id in order:
        package = packages[package_id]
        for contract in package.get("hash_contracts", []):
            if not isinstance(contract, dict):
                raise ReplayError(f"invalid hash contract in {package_id}")
            certificate = safe_repo_path(contract["certificate"])
            if certificate not in certificate_cache:
                certificate_cache[certificate] = load_json(certificate)
            expected = json_pointer(certificate_cache[certificate], contract["pointer"])

            if "file" in contract:
                if not isinstance(expected, str):
                    raise ReplayError(
                        f"scalar hash contract is not a string in {certificate}"
                    )
                items = [(None, contract["file"], expected)]
            else:
                if not isinstance(expected, dict) or not all(
                    isinstance(key, str) and isinstance(value, str)
                    for key, value in expected.items()
                ):
                    raise ReplayError(
                        f"hash map is not string-to-string at {contract['pointer']}"
                    )
                base = contract.get("base", ".")
                overrides = contract.get("overrides", {})
                if not isinstance(overrides, dict):
                    raise ReplayError(f"hash overrides must be an object in {package_id}")
                stale_overrides = sorted(set(overrides) - expected.keys())
                if stale_overrides:
                    raise ReplayError(
                        f"stale hash overrides in {package_id}: {stale_overrides}"
                    )
                items = [
                    (key, overrides.get(key, f"{base.rstrip('/')}/{key}"), value)
                    for key, value in expected.items()
                ]

            for key, raw_path, expected_hash in items:
                path = safe_repo_path(raw_path)
                actual_hash = sha256_file(path) if path.is_file() else None
                status = "PASS" if actual_hash == expected_hash else "FAIL"
                results.append(
                    {
                        "package": package_id,
                        "certificate": certificate.relative_to(REPO).as_posix(),
                        "pointer": contract["pointer"],
                        "key": key,
                        "path": path.relative_to(REPO).as_posix(),
                        "expected_sha256": expected_hash,
                        "observed_sha256": actual_hash,
                        "status": status,
                    }
                )
    return results


def require_static_hashes(results: list[dict[str, Any]]) -> None:
    failures = [result for result in results if result["status"] != "PASS"]
    if failures:
        summary = "; ".join(
            f"{item['package']}:{item['path']} expected "
            f"{item['expected_sha256']} observed {item['observed_sha256']}"
            for item in failures
        )
        raise ReplayError(f"source/dependency hash audit failed: {summary}")


class ReplayContext:
    def __init__(
        self,
        *,
        work_root: Path,
        lock: dict[str, Any],
        capd_source: Path,
        capd_config: Path,
        jobs: int,
        report: dict[str, Any],
    ) -> None:
        self.work_root = work_root
        self.lock = lock
        self.capd_source = capd_source
        self.capd_config = capd_config
        self.jobs = jobs
        self.report = report
        self.artifacts: dict[str, Path] = {}
        self.cflags: list[str] = []
        self.libs: list[str] = []
        self.compiler_path: Path | None = None
        self.validation_copy: Path | None = None
        self.package_results: dict[str, dict[str, Any]] = {}

        process = lock["process"]
        self.environment = os.environ.copy()
        for name in list(self.environment):
            if name in BLOCKED_ENVIRONMENT_KEYS or name.startswith("PAPERA_"):
                self.environment.pop(name, None)
        temporary_dir = self.work_root / "tmp"
        temporary_dir.mkdir(mode=0o700)
        self.environment.update(
            {
                "LC_ALL": process["locale"],
                "LANG": process["locale"],
                "PYTHONDONTWRITEBYTECODE": "1",
                "OPENBLAS_NUM_THREADS": str(process["openblas_threads"]),
                "OMP_NUM_THREADS": str(process["omp_threads"]),
                "CAPD_CONFIG": str(capd_config),
                "CAPD_SOURCE": str(capd_source),
                "PYTHON": str(Path(sys.executable).absolute()),
                "TMPDIR": str(temporary_dir),
            }
        )

    def package_dir(self, package_id: str) -> Path:
        if PACKAGE_ID_RE.fullmatch(package_id) is None:
            raise ReplayError(f"unsafe work-directory package id: {package_id!r}")
        path = self.work_root / package_id
        if path.is_symlink():
            raise ReplayError(f"package work path is a symbolic link: {path}")
        path.mkdir(parents=True, exist_ok=True)
        resolved = path.resolve()
        try:
            resolved.relative_to(self.work_root)
        except ValueError as exc:
            raise ReplayError(f"package work path leaves work root: {path}") from exc
        if resolved.is_symlink() or not resolved.is_dir():
            raise ReplayError(f"package work path is not a real directory: {resolved}")
        return resolved

    def run(
        self,
        package_id: str,
        label: str,
        argv: list[str],
        *,
        cwd: Path | None = None,
        environment: dict[str, str] | None = None,
    ) -> Path:
        package_dir = self.package_dir(package_id)
        logs = package_dir / "logs"
        logs.mkdir(exist_ok=True)
        safe_label = re.sub(r"[^A-Za-z0-9_.-]+", "-", label).strip("-")
        index = len(self.package_results[package_id]["commands"])
        stdout_path = logs / f"{index:02d}-{safe_label}.stdout"
        stderr_path = logs / f"{index:02d}-{safe_label}.stderr"
        started = time.monotonic()
        returncode: int | None = None
        error: str | None = None
        try:
            with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
                completed = subprocess.run(
                    argv,
                    cwd=cwd or REPO,
                    env=environment or self.environment,
                    stdout=stdout,
                    stderr=stderr,
                    check=False,
                )
            returncode = completed.returncode
        except OSError as exc:
            error = str(exc)
        elapsed = time.monotonic() - started
        record = {
            "label": label,
            "argv": argv,
            "cwd": str((cwd or REPO).resolve()),
            "returncode": returncode,
            "elapsed_seconds": elapsed,
            "stdout_sha256": sha256_file(stdout_path) if stdout_path.is_file() else None,
            "stderr_sha256": sha256_file(stderr_path) if stderr_path.is_file() else None,
            "stdout_bytes": stdout_path.stat().st_size if stdout_path.is_file() else None,
            "stderr_bytes": stderr_path.stat().st_size if stderr_path.is_file() else None,
        }
        if error:
            record["launch_error"] = error
        self.package_results[package_id]["commands"].append(record)
        if error or returncode != 0:
            tail = ""
            if stderr_path.is_file():
                tail = stderr_path.read_text(encoding="utf-8", errors="replace")[-4000:]
            raise ReplayError(
                f"{package_id}/{label} failed (returncode={returncode}): "
                f"{shlex.join(argv)}\n{tail}"
            )
        return stdout_path

    def compile_cpp(
        self,
        package_id: str,
        label: str,
        source: Path,
        output: Path,
        *,
        optimization: str,
        includes: list[Path] | None = None,
    ) -> None:
        if self.compiler_path is None:
            raise ReplayError("compiler was not pinned by preflight")
        standard = self.lock["compiler"]["language_standard"]
        argv = [str(self.compiler_path), f"-std={standard}", str(source)]
        for include in includes or []:
            argv.extend(["-I", str(include)])
        argv.extend(self.cflags)
        argv.extend([optimization, "-o", str(output)])
        argv.extend(self.libs)
        self.run(package_id, label, argv)


def read_output_json(path: Path, *, label: str) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReplayError(f"{label} did not emit valid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ReplayError(f"{label} JSON output is not an object")
    return document


def require_status(document: dict[str, Any], expected: str | None = None) -> None:
    status = document.get("status")
    if not isinstance(status, str) or not status.startswith("PASS"):
        raise ReplayError(f"interval output is not PASS: {status!r}")
    if expected is not None and status != expected:
        raise ReplayError(f"unexpected PASS status: expected {expected!r}, got {status!r}")


def require_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    if marker not in text:
        raise ReplayError(f"replay output lacks required marker {marker!r}")


def compare_bytes(observed: Path, expected: Path, *, label: str) -> None:
    if observed.read_bytes() != expected.read_bytes():
        raise ReplayError(
            f"{label} differs: observed={sha256_file(observed)} "
            f"expected={sha256_file(expected)}"
        )


def compare_json_ignoring(
    observed: Path, expected: Path, ignored_top_level: set[str], *, label: str
) -> None:
    observed_json = load_json(observed)
    expected_json = load_json(expected)
    if not isinstance(observed_json, dict) or not isinstance(expected_json, dict):
        raise ReplayError(f"{label} comparison requires two JSON objects")
    for key in ignored_top_level:
        observed_json.pop(key, None)
        expected_json.pop(key, None)
    if observed_json != expected_json:
        raise ReplayError(f"{label} differs after ignoring {sorted(ignored_top_level)}")


def ensure_validation_copy(context: ReplayContext) -> Path:
    if context.validation_copy is not None:
        return context.validation_copy
    destination = context.work_root / "shared-validation-tree" / "validation"
    if destination.exists() or destination.is_symlink():
        raise ReplayError(f"shared validation copy is not fresh: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=False)
    shutil.copytree(
        HERE,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )
    resolved = destination.resolve()
    try:
        resolved.relative_to(context.work_root)
    except ValueError as exc:
        raise ReplayError("shared validation copy leaves the work root") from exc
    context.validation_copy = resolved
    return resolved


def runner_toolchain(context: ReplayContext, package: dict[str, Any]) -> None:
    # The exact package verifier is already the final command of preflight.
    context.package_results[package["id"]]["comparison"] = "preflight verifier PASS"


def runner_future_target(context: ReplayContext, package: dict[str, Any]) -> None:
    package_id = package["id"]
    source = HERE / package_id
    build = context.package_dir(package_id) / "source"
    shutil.copytree(source, build, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
    context.run(package_id, "generate-symbolic-inputs", [sys.executable, "build_prototype.py"], cwd=build)
    for name in (
        "tail_graph_generated.hpp",
        "weighted_tail_generated.hpp",
        "fold_centres_generated.hpp",
    ):
        compare_bytes(build / name, source / name, label=f"regenerated {name}")

    probes = [
        ("graph_transform_probe", "graph_transform_probe.cpp", "-O2"),
        ("weighted_corridor_probe", "weighted_corridor_probe.cpp", "-O0"),
        ("signed_corridor_probe", "signed_corridor_probe.cpp", "-O0"),
        ("terminal_physical_contract_probe", "terminal_physical_contract_probe.cpp", "-O0"),
        ("fold_interval_probe", "fold_interval_probe.cpp", "-O2"),
    ]
    binaries: dict[str, Path] = {}
    for binary_name, source_name, optimization in probes:
        binary = context.package_dir(package_id) / binary_name
        context.compile_cpp(
            package_id,
            f"compile-{binary_name}",
            build / source_name,
            binary,
            optimization=optimization,
            includes=[build],
        )
        binaries[binary_name] = binary

    outputs = [
        (
            "graph-transform",
            [str(binaries["graph_transform_probe"])],
            "PASS-GRAPH-TRANSFORM-INEQUALITIES",
        ),
        (
            "weighted-corridor",
            [str(binaries["weighted_corridor_probe"])],
            "PASS-WEIGHTED-PHYSICAL-CORRIDOR",
        ),
        (
            "signed-corridor",
            [str(binaries["signed_corridor_probe"]), "0.0065", "0.012", "0.01", "2", "0.06"],
            "PASS-ZERO-INCLUSIVE-PHYSICAL-CORRIDOR",
        ),
        (
            "padded-signed-corridor",
            [str(binaries["signed_corridor_probe"]), "0.012", "0.012", "0.06", "2", "0.06"],
            "PASS-ZERO-INCLUSIVE-PHYSICAL-CORRIDOR",
        ),
        (
            "terminal-contract",
            [str(binaries["terminal_physical_contract_probe"])],
            "PASS-TERMINAL-PHYSICAL-CONTRACT",
        ),
        (
            "fold-centre",
            [str(binaries["fold_interval_probe"])],
            "PASS-TRUNCATED-H7-FOLD",
        ),
        (
            "fold-robust",
            [str(binaries["fold_interval_probe"]), "--robust"],
            "PASS-ROBUST-H7-GRAPH-BOUNDS",
        ),
    ]
    for label, argv, status in outputs:
        output = context.run(package_id, label, argv, cwd=build)
        require_status(read_output_json(output, label=label), status)
    context.package_results[package_id]["comparison"] = package["comparison"]


def runner_origin_algebraic(context: ReplayContext, package: dict[str, Any]) -> None:
    package_id = package["id"]
    source = HERE / package_id
    build = context.package_dir(package_id)
    rebuilt_header = build / "unstable_graph_terms.rebuilt.hpp"
    context.run(
        package_id,
        "regenerate-degree-ten-header",
        [sys.executable, str(source / "generate_polynomial_header.py"), "--output", str(rebuilt_header)],
    )
    compare_bytes(
        rebuilt_header,
        source / "unstable_graph_terms.hpp",
        label="degree-ten unstable graph header",
    )

    unstable = build / "unstable_graph_probe"
    heteroclinic = build / "heteroclinic_interval_probe"
    context.compile_cpp(
        package_id,
        "compile-unstable-graph",
        source / "unstable_graph_probe.cpp",
        unstable,
        optimization="-O2",
        includes=[source],
    )
    context.compile_cpp(
        package_id,
        "compile-heteroclinic",
        source / "heteroclinic_interval_probe.cpp",
        heteroclinic,
        optimization="-O0",
        includes=[source],
    )
    graph_output = context.run(package_id, "unstable-graph", [str(unstable)])
    require_status(
        read_output_json(graph_output, label="unstable-graph"),
        "PASS-LOCAL-UNSTABLE-GRAPH",
    )
    heteroclinic_output = context.run(
        package_id, "robust-heteroclinic", [str(heteroclinic), "--robust"]
    )
    require_status(
        read_output_json(heteroclinic_output, label="robust-heteroclinic"),
        "PASS-ROBUST-HETEROCLINIC",
    )
    context.package_results[package_id]["comparison"] = package["comparison"]


def runner_symmetric_homoclinic(context: ReplayContext, package: dict[str, Any]) -> None:
    package_id = package["id"]
    source = HERE / package_id
    origin = HERE / "origin-algebraic-heteroclinic"
    binary = context.package_dir(package_id) / "homoclinic_interval_probe"
    context.compile_cpp(
        package_id,
        "compile-homoclinic",
        source / "homoclinic_interval_probe.cpp",
        binary,
        optimization="-O0",
        includes=[origin],
    )
    output = context.run(package_id, "homoclinic", [str(binary)])
    require_marker(output, "PASS robust symmetric-homoclinic")
    context.package_results[package_id]["comparison"] = package["comparison"]


def runner_origin_pole(context: ReplayContext, package: dict[str, Any]) -> None:
    package_id = package["id"]
    output_dir = context.package_dir(package_id) / "outputs"
    output_dir.mkdir()
    source = HERE / package_id
    origin = HERE / "origin-algebraic-heteroclinic"
    unstable = output_dir / "unstable_graph_probe"
    pole = output_dir / "pole_phase_interval_probe"
    context.compile_cpp(
        package_id,
        "compile-unstable-graph",
        origin / "unstable_graph_probe.cpp",
        unstable,
        optimization="-O2",
        includes=[origin],
    )
    context.compile_cpp(
        package_id,
        "compile-pole-phase",
        source / "pole_phase_interval_probe.cpp",
        pole,
        optimization="-O0",
        includes=[origin],
    )
    unstable_output = context.run(package_id, "unstable-graph", [str(unstable)])
    pole_output = context.run(package_id, "pole-phase", [str(pole)])
    shutil.copyfile(unstable_output, output_dir / "unstable_graph.json")
    shutil.copyfile(pole_output, output_dir / "pole_phase_interval.json")
    require_status(
        load_json(output_dir / "unstable_graph.json"), "PASS-LOCAL-UNSTABLE-GRAPH"
    )
    require_status(
        load_json(output_dir / "pole_phase_interval.json"),
        "PASS-TRUE-WU-OPEN-PHASE-POLE-ENTRY",
    )
    context.package_results[package_id]["comparison"] = package["comparison"]


def runner_exact_source(context: ReplayContext, package: dict[str, Any]) -> None:
    package_id = package["id"]
    source = HERE / package_id
    build = context.package_dir(package_id)
    observed = build / "certificate.rebuilt.json"
    context.run(
        package_id,
        "complete-source-replay",
        [
            sys.executable,
            "replay.py",
            "--capd-config",
            str(context.capd_config),
            "--workers",
            str(context.jobs),
            "--work-dir",
            str(build / "bulk"),
            "--output-certificate",
            str(observed),
        ],
        cwd=source,
    )
    compare_bytes(observed, source / "certificate.json", label="exact-source certificate")
    context.package_results[package_id]["comparison"] = package["comparison"]


def runner_finite_collar(context: ReplayContext, package: dict[str, Any]) -> None:
    package_id = package["id"]
    validation_copy = ensure_validation_copy(context)
    source = validation_copy / package_id
    context.run(package_id, "cover-plan", [sys.executable, "cover_plan.py"], cwd=source)
    context.run(
        package_id,
        "generate-full-cover",
        [sys.executable, "generate_full_cover.py", "--fresh"],
        cwd=source,
    )
    context.run(
        package_id,
        "validate-full-cover",
        [
            sys.executable,
            "validate_full_cover.py",
            "--workers",
            str(context.jobs),
            "--capd-config",
            str(context.capd_config),
        ],
        cwd=source,
    )
    context.run(package_id, "build-certificate", [sys.executable, "build_certificate.py"], cwd=source)
    compare_bytes(
        source / "certificate.json",
        HERE / package_id / "certificate.json",
        label="finite intermediate-collar certificate",
    )
    context.artifacts["coarse_manifest"] = source / "cover_boxes.jsonl"
    context.artifacts["coarse_seeds"] = source / "cover_seeds.txt"
    context.package_results[package_id]["comparison"] = package["comparison"]


def runner_fixed_bridge(context: ReplayContext, package: dict[str, Any]) -> None:
    package_id = package["id"]
    source = HERE / package_id
    observed = context.package_dir(package_id) / "certificate.rebuilt.json"
    context.run(
        package_id,
        "bridge-replay",
        [
            sys.executable,
            "replay.py",
            "--capd-config",
            str(context.capd_config),
            "--output",
            str(observed),
        ],
        cwd=source,
    )
    compare_json_ignoring(
        observed,
        source / "certificate.json",
        {"elapsed_seconds"},
        label="fixed-fold/event bridge certificate",
    )
    context.package_results[package_id]["comparison"] = package["comparison"]


def runner_fundamental_annulus(context: ReplayContext, package: dict[str, Any]) -> None:
    package_id = package["id"]
    output_dir = context.package_dir(package_id) / "outputs"
    output_dir.mkdir()
    source = HERE / package_id
    binaries: dict[str, Path] = {}
    for name, source_name in (
        ("local", "local_annulus_bounds_probe.cpp"),
        ("exit", "exit_target_chart_probe.cpp"),
        ("fixed", "fixed_radial_source_probe.cpp"),
    ):
        binary = output_dir / source_name.removesuffix(".cpp")
        context.compile_cpp(
            package_id,
            f"compile-{name}",
            source / source_name,
            binary,
            optimization="-O0",
        )
        binaries[name] = binary

    commands = (
        (
            "local-annulus",
            [str(binaries["local"])],
            "local_annulus_bounds.json",
            "PASS-QUANTITATIVE-LOCAL-ANNULUS",
        ),
        (
            "exit-target-chart",
            [str(binaries["exit"]), "--stable-half-width", "2e-6"],
            "exit_target_chart.json",
            "PASS-EXIT-TARGET-CHART",
        ),
        (
            "exit-target-centre",
            [str(binaries["exit"]), "--stable-half-width", "1e-12"],
            "exit_target_centre.json",
            "PASS-EXIT-TARGET-CHART",
        ),
        (
            "fixed-radial-source",
            [str(binaries["fixed"]), "--half-width", "1e-12"],
            "fixed_radial_source.json",
            "PASS-FIXED-TIME-RADIAL-ANNULUS-ENTRANCE",
        ),
    )
    for label, argv, name, expected in commands:
        stdout = context.run(package_id, label, argv)
        destination = output_dir / name
        shutil.copyfile(stdout, destination)
        require_status(load_json(destination), expected)
    context.package_results[package_id]["comparison"] = package["comparison"]


def runner_spiral_extension(context: ReplayContext, package: dict[str, Any]) -> None:
    package_id = package["id"]
    if "coarse_manifest" not in context.artifacts or "coarse_seeds" not in context.artifacts:
        raise ReplayError("spiral replay did not receive same-run coarse collar artifacts")
    source = HERE / "finite-source-intermediate-collar"
    build = context.package_dir(package_id) / "outputs"
    environment = context.environment.copy()
    environment["CAPD_CONFIG"] = str(context.capd_config)
    context.run(
        package_id,
        "spiral-extension-replay",
        [
            "bash",
            str(source / "run_spiral_extension_validation.sh"),
            str(build),
            str(context.artifacts["coarse_manifest"]),
            str(context.artifacts["coarse_seeds"]),
            str(context.jobs),
        ],
        environment=environment,
    )
    compare_bytes(
        build / "spiral_extension_certificate.json",
        source / "spiral_extension_certificate.json",
        label="spiral-extension certificate",
    )
    context.package_results[package_id]["comparison"] = package["comparison"]


def runner_pole_cone(context: ReplayContext, package: dict[str, Any]) -> None:
    package_id = package["id"]
    source = HERE / package_id
    binary = context.package_dir(package_id) / "cone_entry_certificate"
    context.compile_cpp(
        package_id,
        "compile-cone-entry",
        source / "cone_entry_certificate.cpp",
        binary,
        optimization="-O2",
    )
    output = context.run(package_id, "cone-entry", [str(binary)])
    observed = read_output_json(output, label="cone-entry")
    require_status(observed, "PASS")
    expected = load_json(source / "certificate.json")
    for key in ("status", "boxes", "cover", "theta", "X0", "c0", "c1"):
        if observed.get(key) != expected.get(key):
            raise ReplayError(f"pole-cone mathematical field differs: {key}")
    context.package_results[package_id]["comparison"] = package["comparison"]


def runner_periodic_return(context: ReplayContext, package: dict[str, Any]) -> None:
    package_id = package["id"]
    source = HERE / package_id
    binary = context.package_dir(package_id) / "periodic_return_probe"
    context.compile_cpp(
        package_id,
        "compile-periodic-return",
        source / "periodic_return_probe.cpp",
        binary,
        optimization="-O2",
    )
    output = context.run(package_id, "periodic-return", [str(binary)])
    require_marker(output, "PASS periodic-return Krawczyk")
    context.package_results[package_id]["comparison"] = package["comparison"]


RUNNERS: dict[str, Callable[[ReplayContext, dict[str, Any]], None]] = {
    "toolchain-audit": runner_toolchain,
    "future-target-fold": runner_future_target,
    "origin-algebraic-heteroclinic": runner_origin_algebraic,
    "universal-core-symmetric-homoclinic": runner_symmetric_homoclinic,
    "origin-unstable-pole-entry": runner_origin_pole,
    "exact-source-outer-fold": runner_exact_source,
    "finite-source-intermediate-collar": runner_finite_collar,
    "fixed-fold-event-bridge": runner_fixed_bridge,
    "fundamental-annulus-overlap": runner_fundamental_annulus,
    "finite-source-spiral-extension": runner_spiral_extension,
    "pole-cone-entry": runner_pole_cone,
    "universal-core-periodic-return": runner_periodic_return,
}


def preflight(
    context: ReplayContext,
    *,
    allow_dirty: bool,
) -> dict[str, Any]:
    result: dict[str, Any] = {"started_at": utc_now(), "checks": {}}
    context.report["preflight"] = result
    git_status = git_value("status", "--porcelain", "--untracked-files=all")
    repository_clean = not bool(git_status)
    if not allow_dirty:
        if not repository_clean:
            raise ReplayError(
                "repository is dirty; commit first or use --allow-dirty for development"
            )
        result["checks"]["repository_clean"] = True
    else:
        result["checks"]["repository_clean"] = repository_clean

    expected_platform = context.lock["platform"]
    observed_system = platform.system()
    observed_machine = platform.machine()
    if observed_system != expected_platform["operating_system"]:
        raise ReplayError(f"OS mismatch: expected Linux, observed {observed_system}")
    if observed_machine != expected_platform["architecture"]:
        raise ReplayError(
            f"architecture mismatch: expected {expected_platform['architecture']}, "
            f"observed {observed_machine}"
        )
    result["checks"]["platform"] = {
        "system": observed_system,
        "architecture": observed_machine,
    }

    python_lock = context.lock["python"]
    expected_python = resolve_executable(
        python_lock["executable"], label="locked Python executable"
    )
    if expected_python.resolve() != Path(sys.executable).resolve():
        raise ReplayError(
            "replay driver is running under a different Python executable than the lock: "
            f"{Path(sys.executable).resolve()} != {expected_python.resolve()}"
        )
    observed_python = platform.python_version()
    if observed_python != python_lock["version"]:
        raise ReplayError(
            f"Python mismatch: expected {python_lock['version']}, observed {observed_python}"
        )
    observed_packages: dict[str, str] = {}
    for name, expected in python_lock["packages"].items():
        try:
            observed = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError as exc:
            raise ReplayError(f"missing Python package: {name}=={expected}") from exc
        if observed != expected:
            raise ReplayError(
                f"Python package mismatch for {name}: expected {expected}, observed {observed}"
            )
        observed_packages[name] = observed
    try:
        import gmpy2  # type: ignore
    except ImportError as exc:
        raise ReplayError("gmpy2 is not importable") from exc
    observed_mpfr = gmpy2.mpfr_version()
    if observed_mpfr != python_lock["mpfr_version_via_gmpy2"]:
        raise ReplayError(
            f"MPFR mismatch: expected {python_lock['mpfr_version_via_gmpy2']}, "
            f"observed {observed_mpfr}"
        )
    sanitized_python = run_capture(
        [
            str(expected_python),
            "-c",
            (
                "import importlib.metadata as m,json,platform,gmpy2;"
                "print(json.dumps({'python':platform.python_version(),"
                "'packages':{name:m.version(name) for name in "
                "('gmpy2','numpy','scipy','sympy')},"
                "'mpfr':gmpy2.mpfr_version()},sort_keys=True))"
            ),
        ],
        cwd=context.work_root,
        environment=context.environment,
    )
    try:
        sanitized_python_document = json.loads(sanitized_python)
    except json.JSONDecodeError as exc:
        raise ReplayError(
            "sanitized Python dependency probe did not emit valid JSON"
        ) from exc
    expected_sanitized_python = {
        "python": python_lock["version"],
        "packages": python_lock["packages"],
        "mpfr": python_lock["mpfr_version_via_gmpy2"],
    }
    if sanitized_python_document != expected_sanitized_python:
        raise ReplayError(
            "sanitized Python dependency mismatch: "
            f"expected {expected_sanitized_python}, "
            f"observed {sanitized_python_document}"
        )
    result["checks"]["python"] = {
        "executable": str(Path(sys.executable).resolve()),
        "version": observed_python,
        "packages": observed_packages,
        "mpfr": observed_mpfr,
        "sanitized_subprocess_recheck": sanitized_python_document,
    }

    compiler_lock = context.lock["compiler"]
    if compiler_lock.get("language_standard") != "c++17":
        raise ReplayError("this replay implementation requires locked language_standard c++17")
    compiler_path = resolve_executable(
        compiler_lock["executable"], label="locked C++ compiler"
    )
    compiler_output = run_capture(
        [str(compiler_path), "--version"], environment=context.environment
    )
    compiler_first_line = compiler_output.splitlines()[0]
    if compiler_first_line != compiler_lock["historical_first_line"]:
        raise ReplayError(
            f"compiler identity mismatch: expected {compiler_lock['historical_first_line']!r}, "
            f"observed {compiler_first_line}"
        )
    compiler_version = run_capture(
        [str(compiler_path), "-dumpfullversion", "-dumpversion"],
        environment=context.environment,
    )
    if compiler_version != compiler_lock["version"]:
        raise ReplayError(
            f"compiler version mismatch: expected {compiler_lock['version']}, "
            f"observed {compiler_version}"
        )
    expected_compiler_hash = compiler_lock.get("binary_sha256")
    observed_compiler_hash = sha256_file(compiler_path)
    if not isinstance(expected_compiler_hash, str) or (
        observed_compiler_hash != expected_compiler_hash
    ):
        raise ReplayError(
            "compiler binary hash mismatch: "
            f"expected {expected_compiler_hash}, observed {observed_compiler_hash}"
        )
    context.compiler_path = compiler_path
    context.environment.update(
        {
            "CXX": str(compiler_path),
            "PAPERA_ANNULUS_CXX": str(compiler_path),
            "PAPERA_POLE_ENTRY_CXX": str(compiler_path),
        }
    )
    result["checks"]["compiler"] = {
        "executable": str(compiler_path),
        "first_line": compiler_first_line,
        "version": compiler_version,
        "sha256": observed_compiler_hash,
    }

    cmake_lock = context.lock["cmake"]
    cmake_path = resolve_executable(cmake_lock["executable"], label="locked CMake")
    cmake_output = run_capture(
        [str(cmake_path), "--version"], environment=context.environment
    )
    cmake_match = re.search(r"cmake version\s+(\S+)", cmake_output)
    observed_cmake = cmake_match.group(1) if cmake_match else None
    if observed_cmake != cmake_lock["version"]:
        raise ReplayError(
            f"CMake mismatch: expected {cmake_lock['version']}, observed {observed_cmake}"
        )
    result["checks"]["cmake"] = {
        "executable": str(cmake_path),
        "version": observed_cmake,
    }

    controlled_tools = {
        "bash": resolve_executable("bash", label="bash"),
        "git": resolve_executable("git", label="git"),
        "python3": expected_python,
        "sha256sum": resolve_executable("sha256sum", label="sha256sum"),
    }
    path_directories: list[str] = []
    for executable in (
        expected_python,
        compiler_path,
        cmake_path,
        context.capd_config,
        *controlled_tools.values(),
    ):
        directory = str(executable.parent)
        if directory not in path_directories:
            path_directories.append(directory)
    context.environment["PATH"] = os.pathsep.join(path_directories)
    for name, expected in controlled_tools.items():
        observed = shutil.which(name, path=context.environment["PATH"])
        if observed is None or Path(observed).resolve() != expected.resolve():
            raise ReplayError(
                f"controlled PATH resolves {name!r} incorrectly: {observed} != {expected}"
            )
    result["checks"]["controlled_path"] = {
        "PATH": context.environment["PATH"],
        "tools": {name: str(path) for name, path in controlled_tools.items()},
    }

    if not context.capd_source.is_dir():
        raise ReplayError(f"CAPD source directory does not exist: {context.capd_source}")
    if not context.capd_config.is_file():
        raise ReplayError(f"capd-config does not exist: {context.capd_config}")

    verifier = HERE / "toolchain-metadata-audit" / "verify.py"
    preflight_dir = context.work_root / "preflight"
    preflight_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = preflight_dir / "toolchain.stdout"
    stderr_path = preflight_dir / "toolchain.stderr"
    argv = [
        sys.executable,
        str(verifier),
        "--print-json",
        "--capd-source",
        str(context.capd_source),
        "--capd-config",
        str(context.capd_config),
    ]
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        completed = subprocess.run(
            argv,
            cwd=REPO,
            env=context.environment,
            stdout=stdout,
            stderr=stderr,
            check=False,
        )
    result["toolchain_verifier"] = {
        "argv": argv,
        "returncode": completed.returncode,
        "stdout_sha256": sha256_file(stdout_path),
        "stderr_sha256": sha256_file(stderr_path),
    }
    if completed.returncode != 0:
        detail = stderr_path.read_text(encoding="utf-8", errors="replace")[-4000:]
        raise ReplayError(f"toolchain metadata audit failed:\n{detail}")
    try:
        toolchain_document = json.loads(stdout_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReplayError(f"toolchain verifier did not emit valid JSON: {exc}") from exc
    tracked_toolchain = load_json(HERE / "toolchain-metadata-audit" / "certificate.json")
    if toolchain_document != tracked_toolchain:
        raise ReplayError("toolchain verifier output differs from the tracked certificate")
    if toolchain_document.get("status") != "PASS":
        raise ReplayError("toolchain verifier JSON status is not PASS")

    capd_lock = context.lock["capd"]
    observed_toolchain = toolchain_document.get("observed")
    if not isinstance(observed_toolchain, dict):
        raise ReplayError("toolchain verifier JSON lacks observed metadata")
    expected_observed = {
        "capd_source_version": capd_lock["source_version"],
        "capd_source_commit": capd_lock["source_commit"],
        "capd_config_modversion": capd_lock["capd_config_modversion"],
        "capd_config_dash_version": capd_lock["pkgconf_frontend_version"],
        "libcapd_sha256": capd_lock["libraries"]["libcapd.a"],
        "libfilib_sha256": capd_lock["libraries"]["libfilib.a"],
        "interval_backend": capd_lock["interval_backend"],
    }
    mismatches = {
        key: {"expected": expected, "observed": observed_toolchain.get(key)}
        for key, expected in expected_observed.items()
        if observed_toolchain.get(key) != expected
    }
    if mismatches:
        raise ReplayError(f"toolchain verifier and environment lock disagree: {mismatches}")

    context.cflags = shlex.split(
        run_capture(
            [str(context.capd_config), "--cflags"],
            environment=context.environment,
        )
    )
    context.libs = shlex.split(
        run_capture(
            [str(context.capd_config), "--libs"],
            environment=context.environment,
        )
    )
    required_rounding = compiler_lock["required_rounding_marker"]
    if required_rounding not in context.cflags:
        raise ReplayError(
            f"CAPD compile flags lack required rounding option {required_rounding!r}"
        )
    missing_cflag_markers = [
        marker
        for marker in capd_lock["compile_flag_markers"]
        if not any(marker in token for token in context.cflags)
    ]
    missing_link_markers = [
        marker
        for marker in capd_lock["link_markers"]
        if not any(marker in token for token in context.libs)
    ]
    if missing_cflag_markers or missing_link_markers:
        raise ReplayError(
            "CAPD flags differ from the environment lock; "
            f"missing_cflags={missing_cflag_markers}, missing_links={missing_link_markers}"
        )

    resolved_libraries: dict[str, dict[str, str]] = {}
    for filename, expected_hash in capd_lock["libraries"].items():
        library = resolve_linked_library(
            compiler_path,
            context.libs,
            filename,
            environment=context.environment,
        )
        observed_hash = sha256_file(library)
        if observed_hash != expected_hash:
            raise ReplayError(
                f"linked {filename} hash mismatch: expected {expected_hash}, "
                f"observed {observed_hash} at {library}"
            )
        resolved_libraries[filename] = {
            "path": str(library),
            "sha256": observed_hash,
        }

    link_probe_source = preflight_dir / "link_probe.cpp"
    link_probe_binary = preflight_dir / "link_probe"
    link_probe_source.write_text("int main() { return 0; }\n", encoding="utf-8")
    link_trace = subprocess.run(
        [
            str(compiler_path),
            f"-std={compiler_lock['language_standard']}",
            str(link_probe_source),
            *context.cflags,
            "-Wl,-t",
            "-o",
            str(link_probe_binary),
            *context.libs,
        ],
        cwd=preflight_dir,
        env=context.environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    trace_text = link_trace.stdout + link_trace.stderr
    if link_trace.returncode != 0:
        raise ReplayError(f"locked CAPD link probe failed:\n{trace_text[-4000:]}")
    traced_paths: list[Path] = []
    for line in trace_text.splitlines():
        candidate = Path(line.strip())
        if candidate.is_file() and candidate.name.startswith(("libcapd.", "libfilib.")):
            traced_paths.append(candidate.resolve())
    for filename, expected_hash in capd_lock["libraries"].items():
        matches = [path for path in traced_paths if path.name == filename]
        if len(matches) != 1 or sha256_file(matches[0]) != expected_hash:
            raise ReplayError(
                f"link trace does not use exactly one locked {filename}: {matches}"
            )
    unexpected_capd_libraries = [
        str(path)
        for path in traced_paths
        if path.name not in capd_lock["libraries"]
    ]
    if unexpected_capd_libraries:
        raise ReplayError(
            "link trace selected unlocked CAPD/FILIB libraries: "
            f"{unexpected_capd_libraries}"
        )

    cache_candidates = [
        context.capd_config.parent.parent / "CMakeCache.txt",
        context.capd_source / "build" / "CMakeCache.txt",
    ]
    cache = next((candidate for candidate in cache_candidates if candidate.is_file()), None)
    if cache is None:
        raise ReplayError("cannot locate the locked CAPD CMakeCache.txt")
    cache_values: dict[str, str] = {}
    for line in cache.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.fullmatch(r"([^#/:=]+):[^=]*=(.*)", line)
        if match:
            cache_values[match.group(1)] = match.group(2)
    cache_mismatches = {
        key: {"expected": expected, "observed": cache_values.get(key)}
        for key, expected in capd_lock["cmake_cache_requirements"].items()
        if cache_values.get(key) != expected
    }
    if cache_mismatches:
        raise ReplayError(f"CAPD CMake cache differs from the lock: {cache_mismatches}")
    result["checks"]["capd_cflags"] = context.cflags
    result["checks"]["capd_libs"] = context.libs
    result["checks"]["resolved_libraries"] = resolved_libraries
    result["checks"]["link_trace"] = {
        "returncode": link_trace.returncode,
        "sha256": hashlib.sha256(trace_text.encode()).hexdigest(),
        "capd_filib_paths": [str(path) for path in traced_paths],
    }
    result["checks"]["capd_cmake_cache"] = {
        "path": str(cache.resolve()),
        "requirements": {
            key: cache_values[key] for key in capd_lock["cmake_cache_requirements"]
        },
    }
    result["checks"]["sanitized_environment"] = {
        "blocked_inherited_keys": sorted(BLOCKED_ENVIRONMENT_KEYS),
        "paper_a_overrides_removed_then_pinned": True,
        "controlled_cxx": str(compiler_path),
        "controlled_python": str(Path(sys.executable).absolute()),
        "python_user_site_allowed_after_exact_version_recheck": True,
    }
    result["status"] = "PASS"
    result["finished_at"] = utc_now()
    return result


def render_command_summary(
    package: dict[str, Any], *, jobs: int, capd_source: str, capd_config: str
) -> list[str]:
    substitutions = {
        "jobs": str(jobs),
        "capd_source": capd_source,
        "capd_config": capd_config,
        "work": "<temporary-work-directory>",
        "coarse_manifest": "<same-run-coarse-manifest>",
        "coarse_seeds": "<same-run-coarse-seeds>",
    }
    return [command.format(**substitutions) for command in package["command_summary"]]


def write_report(path: Path | None, report: dict[str, Any]) -> None:
    rendered = canonical_json(report)
    if path is None:
        sys.stdout.write(rendered)
        return
    path = path.expanduser().resolve()
    try:
        path.relative_to(REPO)
    except ValueError:
        pass
    else:
        raise ReplayError("--report must be outside the repository")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    print(f"Replay report: {path}")


def require_outside_repository(path: Path, *, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(REPO)
    except ValueError:
        return resolved
    raise ReplayError(f"{label} must be outside the repository: {resolved}")


def require_no_symlink_components(path: Path, *, label: str) -> None:
    current = path.absolute()
    while True:
        if current.is_symlink():
            raise ReplayError(f"{label} contains a symbolic-link component: {current}")
        if current == current.parent:
            return
        current = current.parent


def create_work_root(
    requested: Path | None, *, keep_work: bool
) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    """Create a new, empty, non-symlink work root outside the repository."""

    temporary: tempfile.TemporaryDirectory[str] | None = None
    if requested is None:
        base_raw = Path(tempfile.gettempdir())
        require_no_symlink_components(base_raw, label="temporary-directory base")
        base = require_outside_repository(base_raw, label="temporary-directory base")
        if not base.is_dir():
            raise ReplayError(f"temporary-directory base is not a directory: {base}")
        if keep_work:
            root = Path(tempfile.mkdtemp(prefix="papera-replay-", dir=base))
        else:
            temporary = tempfile.TemporaryDirectory(prefix="papera-replay-", dir=base)
            root = Path(temporary.name)
    else:
        raw = requested.expanduser()
        candidate = raw if raw.is_absolute() else Path.cwd() / raw
        if candidate.exists() or candidate.is_symlink():
            raise ReplayError("--work-root must name a new path; existing paths are refused")
        parent_raw = candidate.parent
        require_no_symlink_components(parent_raw, label="--work-root parent")
        parent = require_outside_repository(parent_raw, label="--work-root parent")
        if not parent.is_dir():
            raise ReplayError(f"--work-root parent does not exist: {parent}")
        root = parent / candidate.name
        os.mkdir(root, mode=0o700)

    if root.is_symlink():
        raise ReplayError(f"work root must not be a symbolic link: {root}")
    root = require_outside_repository(root, label="work root")
    if not root.is_dir() or any(root.iterdir()):
        raise ReplayError(f"work root is not a new empty directory: {root}")
    return root, temporary


def finalize_success_status(
    report: dict[str, Any], *, all_profile_package_order: list[str]
) -> None:
    preflight_clean = bool(
        report.get("preflight", {}).get("checks", {}).get("repository_clean", False)
    )
    postflight_clean = bool(
        report.get("postflight", {}).get("repository_clean", False)
    )
    if preflight_clean and postflight_clean:
        report["status"] = "PASS"
        report["profile_replay_pass"] = True
        report["release_eligible"] = bool(
            report.get("profile") == "all"
            and report.get("package_order") == all_profile_package_order
        )
    else:
        report["status"] = "PASS-DEVELOPMENT-DIRTY-NOT-RELEASE-ELIGIBLE"
        report["profile_replay_pass"] = False
        report["release_eligible"] = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--environment-lock", type=Path, default=DEFAULT_LOCK)
    parser.add_argument(
        "--profile",
        default="main-theorem",
        help="manifest profile (default: main-theorem)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--list", action="store_true", help="list profiles and packages")
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "validate the manifest and frozen input hashes; do not inspect the "
            "toolchain or run probes"
        ),
    )
    mode.add_argument(
        "--preflight-only",
        action="store_true",
        help="run static hashes and the complete environment/toolchain preflight only",
    )
    parser.add_argument("--capd-source", type=Path)
    parser.add_argument("--capd-config", type=Path)
    parser.add_argument("--jobs", type=int, default=max(1, min(28, os.cpu_count() or 1)))
    parser.add_argument("--work-root", type=Path)
    parser.add_argument("--keep-work", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="development only: permit a dirty checkout and record it in the report",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest_path = controlled_repo_file(args.manifest, label="replay manifest")
    lock_path = controlled_repo_file(args.environment_lock, label="environment lock")
    if manifest_path != DEFAULT_MANIFEST.resolve():
        raise ReplayError(
            "release replay uses the repository's fixed validation/replay_manifest.json"
        )
    if lock_path != DEFAULT_LOCK.resolve():
        raise ReplayError(
            "release replay uses the repository's fixed validation/environment.lock.json"
        )
    manifest = load_json(manifest_path)
    lock = load_json(lock_path)
    if not isinstance(manifest, dict) or not isinstance(lock, dict):
        raise ReplayError("manifest and environment lock must be JSON objects")
    packages = validate_manifest(manifest, lock)
    validate_control_binding(
        manifest,
        lock,
        manifest_path=manifest_path,
        lock_path=lock_path,
    )

    if args.list:
        output = {
            "status": "LIST-ONLY-NO-CERTIFICATES-EXECUTED",
            "profile_replay_pass": False,
            "release_eligible": False,
            "profiles": manifest["profiles"],
            "packages": {
                package_id: {
                    "category": package["category"],
                    "evidence_role": package["evidence_role"],
                    "dependencies": package["dependencies"],
                    "known_blocker": package.get("known_blocker"),
                }
                for package_id, package in packages.items()
            },
        }
        write_report(args.report, output)
        return 0

    if args.profile not in manifest["profiles"]:
        raise ReplayError(
            f"unknown profile {args.profile!r}; choose from {sorted(manifest['profiles'])}"
        )
    if args.jobs < 1:
        raise ReplayError("--jobs must be positive")

    selected = dependency_closure(packages, manifest["profiles"][args.profile])
    order = topological_order(packages, selected)
    all_profile_package_order = topological_order(
        packages,
        dependency_closure(packages, manifest["profiles"]["all"]),
    )
    report: dict[str, Any] = {
        "schema_version": 1,
        "status": "RUNNING",
        "mode": (
            "dry-run"
            if args.dry_run
            else "preflight-only"
            if args.preflight_only
            else "full-replay"
        ),
        "profile": args.profile,
        "started_at": utc_now(),
        "git_commit": git_value("rev-parse", "HEAD"),
        "manifest_path": manifest_path.relative_to(REPO).as_posix(),
        "manifest_sha256": sha256_file(manifest_path),
        "environment_lock_path": lock_path.relative_to(REPO).as_posix(),
        "environment_lock_sha256": sha256_file(lock_path),
        "driver_sha256": sha256_file(Path(__file__).resolve()),
        "package_order": order,
        "planned_commands": {
            package_id: render_command_summary(
                packages[package_id],
                jobs=args.jobs,
                capd_source=str(args.capd_source or Path("<capd-source>")),
                capd_config=str(args.capd_config or Path("<capd-config>")),
            )
            for package_id in order
        },
        "profile_replay_pass": False,
        "release_eligible": False,
    }

    try:
        static_results = static_hash_audit(packages, order)
        report["static_hash_audit"] = {
            "status": "PASS"
            if all(item["status"] == "PASS" for item in static_results)
            else "FAIL",
            "checks": static_results,
        }
        require_static_hashes(static_results)

        if args.dry_run:
            report["status"] = "PASS-DRY-RUN-NO-CERTIFICATES-EXECUTED"
            report["finished_at"] = utc_now()
            write_report(args.report, report)
            return 0

        capd_source_raw = args.capd_source or (
            Path(os.environ["CAPD_SOURCE"]) if "CAPD_SOURCE" in os.environ else None
        )
        capd_config_raw = args.capd_config or (
            Path(os.environ["CAPD_CONFIG"]) if "CAPD_CONFIG" in os.environ else None
        )
        if capd_source_raw is None or capd_config_raw is None:
            raise ReplayError(
                "pass --capd-source and --capd-config (or set CAPD_SOURCE and CAPD_CONFIG)"
            )
        capd_source = capd_source_raw.expanduser().resolve()
        capd_config = capd_config_raw.expanduser().resolve()

        work_root, temporary = create_work_root(
            args.work_root, keep_work=args.keep_work
        )
        report["work_root"] = str(work_root)

        context = ReplayContext(
            work_root=work_root,
            lock=lock,
            capd_source=capd_source,
            capd_config=capd_config,
            jobs=args.jobs,
            report=report,
        )
        report["preflight"] = preflight(context, allow_dirty=args.allow_dirty)
        if args.preflight_only:
            report["status"] = "PASS-PREFLIGHT-NO-CERTIFICATES-EXECUTED"
            report["finished_at"] = utc_now()
            write_report(args.report, report)
            if temporary is not None and not args.keep_work:
                temporary.cleanup()
            return 0

        for package_id in order:
            package = packages[package_id]
            result = {
                "id": package_id,
                "category": package["category"],
                "evidence_role": package["evidence_role"],
                "started_at": utc_now(),
                "status": "RUNNING",
                "commands": [],
            }
            context.package_results[package_id] = result
            report.setdefault("packages", []).append(result)
            started = time.monotonic()
            RUNNERS[package["runner"]](context, package)
            result["elapsed_seconds"] = time.monotonic() - started
            result["finished_at"] = utc_now()
            result["status"] = "PASS"

        postflight_status = git_value(
            "status", "--porcelain", "--untracked-files=all"
        )
        postflight_clean = not bool(postflight_status)
        report["postflight"] = {
            "repository_clean": postflight_clean,
            "status_sha256": hashlib.sha256(postflight_status.encode()).hexdigest(),
        }
        if report["preflight"]["checks"]["repository_clean"] and not postflight_clean:
            raise ReplayError("the replay modified the repository worktree")
        finalize_success_status(
            report,
            all_profile_package_order=all_profile_package_order,
        )
        report["finished_at"] = utc_now()
        write_report(args.report, report)
        if temporary is not None and not args.keep_work:
            temporary.cleanup()
        return 0
    except ReplayError as exc:
        report["status"] = "FAIL"
        report["failure"] = str(exc)
        report["finished_at"] = utc_now()
        preflight_report = report.get("preflight")
        if isinstance(preflight_report, dict) and "finished_at" not in preflight_report:
            preflight_report["status"] = "FAIL"
            preflight_report["failure"] = str(exc)
            preflight_report["finished_at"] = utc_now()
        packages_report = report.get("packages")
        if isinstance(packages_report, list) and packages_report:
            last = packages_report[-1]
            if last.get("status") == "RUNNING":
                last["status"] = "FAIL"
                last["failure"] = str(exc)
                last["finished_at"] = utc_now()
        write_report(args.report, report)
        return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ReplayError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
