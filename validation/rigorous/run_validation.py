#!/usr/bin/env python3
"""Compile, run, and certify the phase-1 CAPD/FILIB validation probes."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import jsonschema

from check_certificate import schema_errors, semantic_errors
from rigorous_common import (
    box_arguments,
    combine_verdicts,
    git_output,
    load_json,
    run_checked,
    safe_repository_path,
    sha256_bytes,
    sha256_file,
    validate_exact_box,
)

HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
BOX_PATH = HERE / "config" / "vdp_box_v1.json"
DEPENDENCY_LOCK_PATH = HERE / "dependency.lock.json"
FLAGSHIP_LOCK_PATH = HERE / "flagship_import.lock.json"

BOUND_SOURCES = (
    "RESEARCH_CONTRACT.md",
    "theory/BASELINE.md",
    "van-der-pol/HAMILTONIAN_CHECK.md",
    "van-der-pol/MODEL_AND_CENTRAL_CHART.md",
    "van-der-pol/CENTRAL_CONTINUATION.md",
    "validation/rigorous/README.md",
    "validation/rigorous/certificate.schema.json",
    "validation/rigorous/parameter_box.schema.json",
    "validation/rigorous/config/vdp_box_v1.json",
    "validation/rigorous/dependency.lock.json",
    "validation/rigorous/flagship_import.lock.json",
    "validation/rigorous/obligations.json",
    "validation/rigorous/include/verdict.hpp",
    "validation/rigorous/include/interval_io.hpp",
    "validation/rigorous/include/rounding_self_test.hpp",
    "validation/rigorous/include/exact_polynomial.hpp",
    "validation/rigorous/src/rounding_self_test.cpp",
    "validation/rigorous/src/vdp_parameter_box_probe.cpp",
    "validation/rigorous/rigorous_common.py",
    "validation/rigorous/run_validation.py",
    "validation/rigorous/check_certificate.py",
)


def obligation_predicates() -> dict[str, str]:
    manifest = load_json(HERE / "obligations.json")
    return {
        item["id"]: item["predicate"]
        for phase in manifest["phases"]
        for item in phase["obligations"]
    }


def verify_box(box: dict[str, Any]) -> tuple[str, list[str]]:
    errors = validate_exact_box(box)
    try:
        jsonschema.validate(
            box,
            load_json(HERE / "parameter_box.schema.json"),
            format_checker=jsonschema.FormatChecker(),
        )
    except jsonschema.ValidationError as error:
        errors.append(f"schema: {error.message}")
    basis = box.get("selection_basis", {})
    floating = basis.get("floating_configuration", {})
    try:
        floating_path = safe_repository_path(REPOSITORY, floating["path"])
        if sha256_file(floating_path) != floating["sha256"]:
            errors.append("floating configuration hash changed")
        tag_commit = git_output(
            REPOSITORY, "rev-parse", f"{basis['repository_tag']}^{{commit}}")
        if tag_commit != basis["repository_commit"]:
            errors.append("selection tag does not resolve to the frozen selection commit")
        frozen_blob = subprocess.run(
            ["git", "-C", str(REPOSITORY), "show",
             f"{basis['repository_commit']}:{floating['path']}"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
        if sha256_bytes(frozen_blob) != floating["sha256"]:
            errors.append("frozen selection-commit blob hash mismatch")
    except (KeyError, OSError, subprocess.SubprocessError) as error:
        errors.append(f"selection-basis verification failed: {error}")
    return ("PASS" if not errors else "FAIL", errors)


def verify_flagship(repository: Path | None) -> tuple[str, dict[str, Any]]:
    lock = load_json(FLAGSHIP_LOCK_PATH)
    detail: dict[str, Any] = {
        "lock_sha256": sha256_file(FLAGSHIP_LOCK_PATH),
        "commit": lock["commit"],
        "tree": lock["tree"],
        "access": "git-object-read-only",
    }
    if repository is None:
        detail["reason"] = "--flagship-repository was not supplied"
        return "INCONCLUSIVE", detail
    repository = repository.resolve()
    errors: list[str] = []
    try:
        observed_tree = git_output(repository, "rev-parse", f"{lock['commit']}^{{tree}}")
        if observed_tree != lock["tree"]:
            errors.append("frozen flagship tree mismatch")
        for relative, expected_hash in lock["files"].items():
            result = subprocess.run(
                ["git", "-C", str(repository), "show", f"{lock['commit']}:{relative}"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if sha256_bytes(result.stdout) != expected_hash:
                errors.append(f"frozen flagship object hash mismatch: {relative}")
    except (OSError, subprocess.SubprocessError) as error:
        errors.append(f"cannot read frozen flagship objects: {error}")
    detail["repository_path"] = str(repository)
    detail["errors"] = errors
    return ("PASS" if not errors else "FAIL", detail)


def parse_cache(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line or line.startswith(("#", "//")) or "=" not in line:
            continue
        key_with_type, value = line.split("=", 1)
        key = key_with_type.split(":", 1)[0]
        values[key] = value
    return values


def resolve_libraries(tokens: list[str]) -> dict[str, Path]:
    directories = [Path(token[2:]).resolve() for token in tokens if token.startswith("-L")]
    names = [token[2:] for token in tokens if token.startswith("-l")]
    result: dict[str, Path] = {}
    for name in names:
        for directory in directories:
            candidate = directory / f"lib{name}.a"
            if candidate.is_file():
                result[f"lib{name}.a"] = candidate
                break
    return result


def verify_toolchain(capd_source: Path, capd_config: Path,
                     dependency: dict[str, Any]) -> tuple[str, dict[str, Any], list[str], list[str]]:
    capd_source = capd_source.resolve()
    capd_config = capd_config.resolve()
    compiler = Path(dependency["compiler"]["executable"])
    fatal: list[str] = []
    incomplete: list[str] = []
    try:
        compiler_hash = sha256_file(compiler)
        compiler_version = run_checked([str(compiler), "--version"]).stdout.splitlines()[0]
        if compiler_hash != dependency["compiler"]["sha256"]:
            fatal.append("compiler hash mismatch")
        if compiler_version != dependency["compiler"]["first_line"]:
            fatal.append("compiler version mismatch")
        capd_head = git_output(capd_source, "rev-parse", "HEAD")
        capd_tree = git_output(capd_source, "rev-parse", "HEAD^{tree}")
        capd_dirty = bool(git_output(capd_source, "status", "--porcelain"))
        if capd_head != dependency["capd"]["source_commit"]:
            fatal.append("CAPD source commit mismatch")
        if capd_tree != dependency["capd"]["source_tree"]:
            fatal.append("CAPD source tree mismatch")
        if capd_dirty:
            fatal.append("CAPD source checkout is dirty")
        cflags_text = run_checked([str(capd_config), "--cflags"]).stdout.strip()
        libs_text = run_checked([str(capd_config), "--libs"]).stdout.strip()
        config_version = run_checked([str(capd_config), "--version"]).stdout.strip()
        if config_version != dependency["capd"]["capd_config_reported_version"]:
            fatal.append("capd-config reported-version mismatch")
    except (OSError, subprocess.SubprocessError, IndexError) as error:
        fatal.append(f"toolchain query failed: {error}")
        compiler_hash = ""
        compiler_version = ""
        capd_head = ""
        capd_tree = ""
        capd_dirty = True
        cflags_text = ""
        libs_text = ""
        config_version = ""

    cflags = shlex.split(cflags_text)
    libs = shlex.split(libs_text)
    libraries = resolve_libraries(libs)
    if "-D__USE_FILIB__" not in cflags:
        fatal.append("capd-config does not select the FILIB backend")
    forbidden_flags = dependency["compiler"]["forbidden_flags"]
    for forbidden in forbidden_flags:
        if forbidden in cflags:
            fatal.append(f"forbidden CAPD flag present: {forbidden}")
    for required in ("libcapd.a", "libfilib.a"):
        if required not in libraries:
            fatal.append(f"linked archive not resolved: {required}")

    build_directory = capd_config.resolve().parents[1]
    if capd_source not in capd_config.parents:
        fatal.append("capd-config is not inside the pinned CAPD source/build tree")
    cache_path = build_directory / "CMakeCache.txt"
    cache = parse_cache(cache_path)
    release_flags = shlex.split(cache.get("CMAKE_CXX_FLAGS_RELEASE", ""))
    strict_flags = dependency["compiler"]["required_probe_flags"]
    for forbidden in forbidden_flags:
        if forbidden in release_flags:
            fatal.append(f"forbidden CMake release flag present: {forbidden}")
    missing_library_flags = [flag for flag in strict_flags if flag not in release_flags]
    if missing_library_flags:
        incomplete.append(
            "CAPD/FILIB archives were not built with all strict flags: " +
            ", ".join(missing_library_flags))
    expected_cache = {
        "CMAKE_BUILD_TYPE": "Release",
        "CAPD_INTERVAL_TYPE": "FILIB",
        "CAPD_ENABLE_MULTIPRECISION": "OFF",
        "CAPD_BUILD_TESTS": "OFF",
        "CAPD_BUILD_EXAMPLES": "OFF",
        "CMAKE_EXPORT_COMPILE_COMMANDS": "ON",
    }
    for key, expected in expected_cache.items():
        if cache.get(key) != expected:
            fatal.append(f"CMake cache mismatch: {key}={cache.get(key)!r}, expected {expected!r}")
    cache_compiler = Path(cache.get("CMAKE_CXX_COMPILER", "/missing"))
    try:
        if cache_compiler.resolve() != compiler.resolve():
            fatal.append("CMake CXX compiler does not resolve to the locked compiler")
    except OSError as error:
        fatal.append(f"cannot resolve CMake CXX compiler: {error}")
    cmake_path = Path(cache.get("CMAKE_COMMAND", "/missing"))
    make_path = Path(cache.get("CMAKE_MAKE_PROGRAM", "/missing"))
    build_programs: dict[str, Any] = {}
    for name, path, expected_hash in (
            ("cmake", cmake_path, dependency["cmake"]["reference_sha256"]),
            ("make", make_path, dependency["build_tool"]["sha256"])):
        try:
            observed_hash = sha256_file(path)
            build_programs[name] = {
                "path": str(path.resolve()), "sha256": observed_hash}
            if observed_hash != expected_hash:
                fatal.append(f"{name} executable hash mismatch")
        except OSError as error:
            fatal.append(f"cannot hash {name} executable: {error}")
    try:
        cmake_version_line = run_checked([str(cmake_path), "--version"]).stdout.splitlines()[0]
        build_programs.setdefault("cmake", {})["version_first_line"] = cmake_version_line
        if cmake_version_line != f"cmake version {dependency['cmake']['reference_version']}":
            fatal.append("CMake version mismatch")
    except (OSError, subprocess.SubprocessError, IndexError) as error:
        fatal.append(f"cannot query CMake version: {error}")

    compile_commands_path = build_directory / "compile_commands.json"
    compile_commands_hash: str | None = None
    compile_command_summary: dict[str, Any] = {
        "entry_count": 0,
        "entries_with_all_strict_flags": 0,
        "entries_with_filib_selector": 0,
        "compiler_paths": [],
    }
    if not compile_commands_path.is_file():
        incomplete.append("compile_commands.json is missing")
    else:
        compile_commands_hash = sha256_file(compile_commands_path)
        try:
            entries = json.loads(compile_commands_path.read_text(encoding="utf-8"))
            if not isinstance(entries, list) or not entries:
                raise ValueError("compile command list is empty")
            compiler_paths: set[str] = set()
            strict_count = 0
            filib_count = 0
            for index, entry in enumerate(entries):
                tokens = entry.get("arguments")
                if tokens is None:
                    tokens = shlex.split(entry["command"])
                if not isinstance(tokens, list) or not tokens:
                    raise ValueError(f"entry {index} has no compiler argv")
                entry_compiler = Path(tokens[0]).resolve()
                compiler_paths.add(str(entry_compiler))
                if entry_compiler != compiler.resolve():
                    fatal.append(f"compile_commands entry {index} uses an unlocked compiler")
                if all(flag in tokens for flag in strict_flags):
                    strict_count += 1
                else:
                    missing = [flag for flag in strict_flags if flag not in tokens]
                    incomplete.append(
                        f"compile_commands entry {index} lacks strict flags: {', '.join(missing)}")
                present_forbidden = [flag for flag in forbidden_flags if flag in tokens]
                if present_forbidden:
                    fatal.append(
                        f"compile_commands entry {index} has forbidden flags: " +
                        ", ".join(present_forbidden))
                if "-D__USE_FILIB__" in tokens:
                    filib_count += 1
                source_file = Path(entry["file"]).resolve()
                if capd_source != source_file and capd_source not in source_file.parents:
                    fatal.append(f"compile_commands entry {index} source escapes pinned tree")
                entry_directory = Path(entry["directory"]).resolve()
                if build_directory != entry_directory and build_directory not in entry_directory.parents:
                    fatal.append(f"compile_commands entry {index} directory escapes build tree")
            compile_command_summary = {
                "entry_count": len(entries),
                "entries_with_all_strict_flags": strict_count,
                "entries_with_filib_selector": filib_count,
                "compiler_paths": sorted(compiler_paths),
            }
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            fatal.append(f"invalid compile_commands.json: {error}")

    for name, path in libraries.items():
        if build_directory != path and build_directory not in path.parents:
            fatal.append(f"linked archive escapes the bound build tree: {name}")
    reference_config = Path(dependency["capd"]["reference_capd_config"])
    if capd_config == reference_config.resolve():
        for name, expected_hash in dependency["capd"]["reference_libraries"].items():
            if name in libraries and sha256_file(libraries[name]) != expected_hash:
                fatal.append(f"reference archive hash mismatch: {name}")
    strict_status = "PASS" if not fatal and not incomplete else (
        "FAIL" if fatal else "INCONCLUSIVE")
    overall = "FAIL" if fatal else ("INCONCLUSIVE" if incomplete else "PASS")
    library_records = {
        name: {"path": str(path), "sha256": sha256_file(path)}
        for name, path in libraries.items()
    }
    detail = {
        "status": overall,
        "strict_library_build_status": strict_status,
        "dependency_lock_sha256": sha256_file(DEPENDENCY_LOCK_PATH),
        "compiler": {
            "path": str(compiler),
            "version_first_line": compiler_version,
            "sha256": compiler_hash,
        },
        "build_programs": build_programs,
        "capd": {
            "source_path": str(capd_source.resolve()),
            "source_commit": capd_head,
            "source_tree": capd_tree,
            "source_dirty": capd_dirty,
            "config_path": str(capd_config.resolve()),
            "config_version": config_version,
            "cflags": cflags,
            "libs": shlex.split(libs_text),
            "cmake_cache_sha256": sha256_file(cache_path) if cache_path.is_file() else None,
            "cmake_release_flags": release_flags,
            "cmake_configuration": {
                key: cache.get(key) for key in (*expected_cache, "CMAKE_CXX_COMPILER")
            },
            "compile_commands_sha256": compile_commands_hash,
            "compile_commands_scan": compile_command_summary,
            "linked_archives": library_records,
        },
        "fatal_errors": fatal,
        "incomplete_checks": incomplete,
    }
    return overall, detail, cflags, libs


def compile_and_run(scope: str, cflags: list[str], libs: list[str],
                    dependency: dict[str, Any], box: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str], dict[str, Any]]:
    source = HERE / "src" / (
        "rounding_self_test.cpp" if scope == "preflight" else
        "vdp_parameter_box_probe.cpp")
    compiler = dependency["compiler"]["executable"]
    strict_flags = dependency["compiler"]["required_probe_flags"]
    environment = os.environ.copy()
    environment.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "LC_ALL": "C.UTF-8"})
    with tempfile.TemporaryDirectory(prefix="rfsn-rigorous-") as temporary:
        binary = Path(temporary) / "probe"
        command = [
            compiler,
            "-std=c++17",
            f"-I{HERE / 'include'}",
            *cflags,
            *strict_flags,
            str(source),
            "-o",
            str(binary),
            *libs,
        ]
        compiled = subprocess.run(
            command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=environment, timeout=180)
        if compiled.returncode != 0:
            raise RuntimeError(
                f"probe compilation failed ({compiled.returncode}):\n{compiled.stderr}")
        run_command = [str(binary)]
        if scope == "kernel":
            run_command.extend(box_arguments(box))
        executed = subprocess.run(
            run_command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=environment, timeout=120)
        if executed.returncode not in (0, 1, 2):
            raise RuntimeError(
                f"probe terminated with unexpected code {executed.returncode}:\n"
                f"{executed.stderr}")
        try:
            raw = json.loads(executed.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"probe emitted invalid JSON: {error}") from error
        logs = {
            "compile_stdout_sha256": sha256_bytes(compiled.stdout.encode()),
            "compile_stderr_sha256": sha256_bytes(compiled.stderr.encode()),
            "probe_stdout_sha256": sha256_bytes(executed.stdout.encode()),
            "probe_stderr_sha256": sha256_bytes(executed.stderr.encode()),
        }
        build = {
            "compile_argv": command,
            "compile_argv_sha256": sha256_bytes(
                json.dumps(command, separators=(",", ":")).encode()),
            "source_sha256": sha256_file(source),
            "binary_sha256": sha256_file(binary),
            "probe_argv": run_command,
            "probe_exit_code": executed.returncode,
        }
        return raw, logs, build


def source_bindings() -> list[dict[str, str]]:
    bindings: list[dict[str, str]] = []
    for relative in BOUND_SOURCES:
        path = safe_repository_path(REPOSITORY, relative)
        if not path.is_file():
            raise FileNotFoundError(f"bound source is missing: {relative}")
        bindings.append({"path": relative, "sha256": sha256_file(path), "role": "phase-1-input"})
    return bindings


def make_obligation(identifier: str, status: str,
                    predicates: dict[str, str], **extra: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "id": identifier,
        "status": status,
        "predicate": predicates[identifier],
    }
    value.update(extra)
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scope", choices=("preflight", "kernel"))
    parser.add_argument("--capd-source", type=Path, required=True)
    parser.add_argument("--capd-config", type=Path, required=True)
    parser.add_argument("--flagship-repository", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--allow-dirty", action="store_true",
                        help="permit a hash-bound dirty development checkout")
    arguments = parser.parse_args()

    try:
        dependency = load_json(DEPENDENCY_LOCK_PATH)
        box = load_json(BOX_PATH)
        box_status, box_errors = verify_box(box)
        head = git_output(REPOSITORY, "rev-parse", "HEAD")
        dirty = bool(git_output(REPOSITORY, "status", "--porcelain"))
        if dirty and not arguments.allow_dirty:
            raise RuntimeError(
                "repository is dirty; use --allow-dirty only for a non-release development run")
        flagship_status, flagship = verify_flagship(arguments.flagship_repository)
        capd_status, toolchain, cflags, libs = verify_toolchain(
            arguments.capd_source.resolve(), arguments.capd_config.resolve(), dependency)
        toolchain["flagship_import"] = flagship
        raw, logs, build = compile_and_run(
            arguments.scope, cflags, libs, dependency, box)
        toolchain["probe_build"] = build
        report_resolved = arguments.report.resolve()
        try:
            report_location = str(report_resolved.relative_to(REPOSITORY.resolve()))
            report_inside_repository = True
        except ValueError:
            report_location = str(report_resolved)
            report_inside_repository = False
        toolchain["report_output"] = {
            "path": report_location,
            "inside_repository": report_inside_repository,
            "excluded_from_prewrite_source_observation": True,
        }

        predicates = obligation_predicates()
        source_status = flagship_status
        rounding = raw["rounding_self_test"]
        p0 = [
            make_obligation("ENV.SOURCE_BINDING", source_status, predicates),
            make_obligation("ENV.CAPD_BINDING", capd_status, predicates),
            make_obligation("ENV.ROUNDING", rounding["status"], predicates),
            make_obligation("BOX.FROZEN", box_status, predicates,
                            diagnostics=box_errors),
        ]
        mathematical: list[dict[str, Any]] = []
        if arguments.scope == "kernel":
            for item in raw["obligations"]:
                identifier = item["id"]
                mathematical.append(make_obligation(
                    identifier, item["status"], predicates,
                    **({"enclosures": item["enclosures"]}
                       if "enclosures" in item else {})))
        integrity_status = combine_verdicts(item["status"] for item in p0)
        mathematical_status = combine_verdicts(
            item["status"] for item in mathematical) if mathematical else "PASS"
        final_status = "FAIL" if "FAIL" in (integrity_status, mathematical_status) \
            else "INCONCLUSIVE"
        now = dt.datetime.now(dt.timezone.utc)
        scope_name = "PREFLIGHT" if arguments.scope == "preflight" else "V1_V2_1_KERNEL"
        certificate = {
            "schema_version": "rfsn-rigorous-run-certificate/1",
            "certificate_id": (
                f"vdp-phase1-{arguments.scope}-{now.strftime('%Y%m%dt%H%M%Sz').lower()}-"
                f"{head[:12]}"),
            "scope": scope_name,
            "created_at": now.isoformat(),
            "source_revision": {
                "repository": "h-lu/rfsn-ii-positive-parameter-pde",
                "commit": head,
                "repository_dirty": dirty,
                "allow_dirty_development": arguments.allow_dirty,
                "working_tree_observation": "BEFORE_REPORT_WRITE",
                "report_output_excluded_from_observation": True,
            },
            "source_bindings": source_bindings(),
            "parameter_box": {
                "path": "validation/rigorous/config/vdp_box_v1.json",
                "sha256": sha256_file(BOX_PATH),
                "box_id": box["box_id"],
                "variables": box["variables"],
            },
            "toolchain": toolchain,
            "rounding_self_test": rounding,
            "obligations": p0 + mathematical,
            "integrity_status": integrity_status,
            "mathematical_status": mathematical_status,
            "independent_replay": {
                "status": "PENDING_REQUIRED",
                "required_distinct_machines": dependency["independent_replay"]["minimum_distinct_machines"],
                "observed_distinct_machines": 1,
            },
            "final_status": final_status,
            "claim_bearing": False,
            "release_eligible": False,
            "raw_probe": raw,
            "logs": logs,
            "nonclaims": [
                "A local mathematical PASS is not an aggregate theorem certificate.",
                "Independent-machine replay is pending and this certificate is not claim-bearing.",
                "Phase 1 does not validate V2 continuation beyond item (1), V3--V6, temporal stability, Turing selection, or canard identification.",
            ],
        }
        errors = schema_errors(certificate) + semantic_errors(certificate, REPOSITORY)
        if errors:
            raise RuntimeError("generated certificate failed self-check:\n" + "\n".join(errors))
        arguments.report.parent.mkdir(parents=True, exist_ok=True)
        arguments.report.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8")
        print(
            f"wrote {arguments.report}: mathematical_status={mathematical_status}, "
            f"integrity_status={integrity_status}, final_status={final_status}, "
            "claim_bearing=false")
        return 1 if final_status == "FAIL" else 0
    except (OSError, KeyError, ValueError, RuntimeError,
            subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"validation runner error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
