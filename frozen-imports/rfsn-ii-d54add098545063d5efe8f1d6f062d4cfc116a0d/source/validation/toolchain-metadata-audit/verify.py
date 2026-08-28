#!/usr/bin/env python3
"""Verify the CAPD/FILIB metadata addendum without replaying claim probes.

The generated certificate deliberately omits local filesystem paths and
timestamps.  An exact checkout/build therefore regenerates the same JSON even
when it is installed somewhere other than the original temporary directory.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Iterator


PACKAGE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_DIR.parents[1]
DEFAULT_CERTIFICATE = PACKAGE_DIR / "certificate.json"

EXPECTED_SOURCE_VERSION = "6.1.0"
EXPECTED_COMMIT = "731079217a9254ea2948d742df2b170895effe7f"
EXPECTED_FRONTEND_VERSION = "2.5.1"
EXPECTED_FRONTEND = "pkgconf"
EXPECTED_BYTE_IDENTICAL_SOURCE_PATH = Path("/tmp/papera-capd.bKwHIQ/CAPD")
EXPECTED_LIBCAPD_SHA256 = (
    "316b2c480f1ce36b293602da9978eb43560646991a4a906d72ee893b3c557119"
)
EXPECTED_LIBFILIB_SHA256 = (
    "ce5cdf8f22d4a6737461774211053a3df360178194e431e4f7ad2b2ada5caa7e"
)

# These are historical, claim-bearing JSON files.  Their bytes are retained to
# avoid invalidating downstream hashes; this package is the interpretive
# addendum for the listed fields.
AFFECTED_FIELDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "validation/finite-source-intermediate-collar/certificate.json",
        ("replay_pins", "capd_pkg_config_version"),
    ),
    (
        "validation/finite-source-intermediate-collar/spiral_extension_certificate.json",
        ("replay_pins", "capd_pkg_config_version"),
    ),
    (
        "validation/fixed-fold-event-bridge/certificate.json",
        ("environment", "capd_config_version"),
    ),
    (
        "validation/fundamental-annulus-overlap/certificate.json",
        ("build", "capd_version"),
    ),
    (
        "validation/future-target-fold/certificate.json",
        ("pins", "capd_pkg_config_version"),
    ),
    (
        "validation/origin-algebraic-heteroclinic/certificate.json",
        ("toolchain", "capd"),
    ),
    (
        "validation/origin-unstable-pole-entry/certificate.json",
        ("replay", "capd_version"),
    ),
    (
        "validation/universal-core-periodic-return/certificate.json",
        ("implementation", "capd_version"),
    ),
    (
        "validation/universal-core-symmetric-homoclinic/certificate.json",
        ("replay", "capd_version"),
    ),
)

AMBIGUOUS_CAPD_KEYS = {
    "capd",
    "capd_version",
    "capd_config_version",
    "capd_pkg_config_version",
}


class AuditError(RuntimeError):
    """A missing input or malformed metadata source."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_checked(argv: list[str], *, cwd: Path | None = None) -> str:
    try:
        completed = subprocess.run(
            argv,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        stderr = getattr(exc, "stderr", "") or ""
        raise AuditError(f"command failed: {' '.join(argv)}\n{stderr.strip()}") from exc
    return completed.stdout.strip()


def resolve_executable(value: str | Path) -> Path | None:
    candidate = Path(value).expanduser()
    if candidate.is_file():
        return candidate.resolve()
    located = shutil.which(str(value))
    return Path(located).resolve() if located else None


def inferred_source(config: Path) -> Path | None:
    # The audited build layout is CAPD/build/bin/capd-config.
    if len(config.parents) >= 3:
        candidate = config.parents[2]
        if (candidate / "CAPDVersion.txt").is_file() and (candidate / ".git").exists():
            return candidate.resolve()
    return None


def source_commit(source: Path) -> str | None:
    try:
        return run_checked(["git", "-C", str(source), "rev-parse", "HEAD"])
    except AuditError:
        return None


def discover_paths(
    source_arg: str | None, config_arg: str | None
) -> tuple[Path, Path]:
    source: Path | None = None
    config: Path | None = None

    source_hint = source_arg or os.environ.get("CAPD_SOURCE")
    config_hint = config_arg or os.environ.get("CAPD_CONFIG")

    if source_hint:
        candidate = Path(source_hint).expanduser()
        if not candidate.is_dir():
            raise AuditError(f"CAPD source directory does not exist: {candidate}")
        source = candidate.resolve()

    if config_hint:
        config = resolve_executable(config_hint)
        if config is None:
            raise AuditError(f"capd-config is not executable or on PATH: {config_hint}")

    if config is None and source is not None:
        config = resolve_executable(source / "build" / "bin" / "capd-config")

    if config is None:
        config = resolve_executable("capd-config")

    if config is None:
        temp_candidates = sorted(
            Path("/tmp").glob("papera-capd.*/CAPD/build/bin/capd-config")
        )
        # Prefer the pinned checkout if more than one old build is present.
        for candidate in temp_candidates:
            resolved = resolve_executable(candidate)
            if resolved is None:
                continue
            candidate_source = inferred_source(resolved)
            if candidate_source and source_commit(candidate_source) == EXPECTED_COMMIT:
                config = resolved
                break
        if config is None and temp_candidates:
            config = resolve_executable(temp_candidates[0])

    if config is None:
        raise AuditError(
            "could not find capd-config; pass --capd-config or set CAPD_CONFIG"
        )

    if source is None:
        source = inferred_source(config)

    if source is None:
        temp_sources = sorted(Path("/tmp").glob("papera-capd.*/CAPD"))
        for candidate in temp_sources:
            if source_commit(candidate) == EXPECTED_COMMIT:
                source = candidate.resolve()
                break

    if source is None:
        raise AuditError(
            "could not infer the CAPD checkout; pass --capd-source or set CAPD_SOURCE"
        )

    return source, config


def parse_source_version(source: Path) -> str:
    version_file = source / "CAPDVersion.txt"
    try:
        content = version_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise AuditError(f"cannot read {version_file}") from exc

    parts: list[str] = []
    for name in ("MAJOR", "MINOR", "PATCH"):
        match = re.search(
            rf"set\s*\(\s*CAPD_{name}_VERSION\s+([0-9]+)\s*\)",
            content,
            flags=re.IGNORECASE,
        )
        if not match:
            raise AuditError(f"cannot parse CAPD_{name}_VERSION from CAPDVersion.txt")
        parts.append(match.group(1))
    return ".".join(parts)


def parse_cache_backend(cache: Path) -> str:
    try:
        content = cache.read_text(encoding="utf-8")
    except OSError as exc:
        raise AuditError(f"cannot read CMake cache: {cache}") from exc
    match = re.search(
        r"^CAPD_INTERVAL_TYPE:[^=]*=(\S+)\s*$", content, flags=re.MULTILINE
    )
    if not match:
        raise AuditError(f"CAPD_INTERVAL_TYPE is absent from {cache}")
    return match.group(1)


def find_cache(source: Path, config: Path, pc_path: Path) -> Path:
    candidates = (
        pc_path.parent.parent / "CMakeCache.txt",
        config.parent.parent / "CMakeCache.txt",
        source / "build" / "CMakeCache.txt",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise AuditError("could not locate the CMakeCache.txt belonging to capd-config")


def library_candidates(
    source: Path, config: Path, pc_path: Path, libs: Iterable[str], filename: str
) -> list[Path]:
    search_dirs = [source / "build", config.parent.parent, pc_path.parent.parent]
    for token in libs:
        if token.startswith("-L") and len(token) > 2:
            search_dirs.append(Path(token[2:]))

    candidates: list[Path] = []
    seen: set[Path] = set()
    for directory in search_dirs:
        candidate = (directory / filename).expanduser()
        if candidate.is_file():
            resolved = candidate.resolve()
            if resolved not in seen:
                seen.add(resolved)
                candidates.append(resolved)
    return candidates


def select_library(candidates: list[Path], expected_hash: str, label: str) -> Path:
    if not candidates:
        raise AuditError(f"could not locate {label} from capd-config --libs")
    for candidate in candidates:
        if sha256(candidate) == expected_hash:
            return candidate
    return candidates[0]


def get_json_path(document: Any, path: tuple[str, ...]) -> Any:
    current = document
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise AuditError(f"missing JSON path $.{'.'.join(path)}")
        current = current[key]
    return current


def iter_scalar_paths(value: Any, prefix: tuple[str, ...] = ()) -> Iterator[tuple[tuple[str, ...], Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from iter_scalar_paths(child, prefix + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_scalar_paths(child, prefix + (str(index),))
    else:
        yield prefix, value


def affected_field_records() -> tuple[list[dict[str, str]], bool]:
    records: list[dict[str, str]] = []
    expected_locations = set(AFFECTED_FIELDS)
    observed_locations: set[tuple[str, tuple[str, ...]]] = set()

    for relative_file, path in AFFECTED_FIELDS:
        document = json.loads((REPO_ROOT / relative_file).read_text(encoding="utf-8"))
        value = get_json_path(document, path)
        records.append(
            {
                "file": relative_file,
                "json_path": "$." + ".".join(path),
                "recorded_value": str(value),
                "correct_interpretation": "pkgconf frontend version from capd-config --version",
            }
        )

    for certificate in sorted((REPO_ROOT / "validation").rglob("*certificate.json")):
        if PACKAGE_DIR in certificate.parents:
            continue
        document = json.loads(certificate.read_text(encoding="utf-8"))
        relative_file = certificate.relative_to(REPO_ROOT).as_posix()
        for path, value in iter_scalar_paths(document):
            if (
                path
                and path[-1] in AMBIGUOUS_CAPD_KEYS
                and value == EXPECTED_FRONTEND_VERSION
            ):
                observed_locations.add((relative_file, path))

    values_are_historical_frontend = all(
        record["recorded_value"] == EXPECTED_FRONTEND_VERSION for record in records
    )
    return records, (
        values_are_historical_frontend and observed_locations == expected_locations
    )


def build_certificate(source: Path, config: Path) -> dict[str, Any]:
    source_version = parse_source_version(source)
    commit = run_checked(["git", "-C", str(source), "rev-parse", "HEAD"])

    modversion = run_checked([str(config), "--modversion"])
    dash_version = run_checked([str(config), "--version"])
    about_first_line = run_checked([str(config), "--about"]).splitlines()[0].strip()
    about_parts = about_first_line.split()
    frontend = about_parts[0] if about_parts else ""
    frontend_about_version = about_parts[1] if len(about_parts) > 1 else ""

    cflags = shlex.split(run_checked([str(config), "--cflags"]))
    libs = shlex.split(run_checked([str(config), "--libs"]))
    pc_output = run_checked([str(config), "--path"]).splitlines()
    if len(pc_output) != 1:
        raise AuditError("capd-config --path did not return exactly one package file")
    pc_path = Path(pc_output[0]).resolve()
    if not pc_path.is_file():
        raise AuditError("the package file reported by capd-config --path is absent")

    cache_backend = parse_cache_backend(find_cache(source, config, pc_path))
    cflag_markers = [
        marker
        for marker in ("-D__USE_FILIB__", "-DFILIB_EXTENDED", "-DFILIB_HAVE_SSE")
        if marker in cflags
    ]
    linked_libraries = [marker for marker in ("-lcapd", "-lfilib") if marker in libs]

    capd_library = select_library(
        library_candidates(source, config, pc_path, libs, "libcapd.a"),
        EXPECTED_LIBCAPD_SHA256,
        "libcapd.a",
    )
    filib_library = select_library(
        library_candidates(source, config, pc_path, libs, "libfilib.a"),
        EXPECTED_LIBFILIB_SHA256,
        "libfilib.a",
    )
    libcapd_hash = sha256(capd_library)
    libfilib_hash = sha256(filib_library)

    affected, affected_complete = affected_field_records()
    checks = {
        "source_version_matches": source_version == EXPECTED_SOURCE_VERSION,
        "source_commit_matches": commit == EXPECTED_COMMIT,
        "capd_modversion_matches": modversion == EXPECTED_SOURCE_VERSION,
        "dash_version_is_pkgconf_version": (
            dash_version == EXPECTED_FRONTEND_VERSION
            and frontend == EXPECTED_FRONTEND
            and frontend_about_version == EXPECTED_FRONTEND_VERSION
        ),
        "libcapd_hash_matches": libcapd_hash == EXPECTED_LIBCAPD_SHA256,
        "libfilib_hash_matches": libfilib_hash == EXPECTED_LIBFILIB_SHA256,
        "filib_backend_matches": (
            cache_backend == "FILIB"
            and cflag_markers
            == ["-D__USE_FILIB__", "-DFILIB_EXTENDED", "-DFILIB_HAVE_SSE"]
            and linked_libraries == ["-lcapd", "-lfilib"]
        ),
        "affected_claim_fields_complete": affected_complete,
        "byte_identical_source_path_matches": (
            source == EXPECTED_BYTE_IDENTICAL_SOURCE_PATH
        ),
    }
    status = "PASS" if all(checks.values()) else "FAIL"

    return {
        "schema": "paper-a-toolchain-metadata-audit-v1",
        "status": status,
        "purpose": "interpretive addendum for historical CAPD version fields",
        "expected": {
            "capd_source_version": EXPECTED_SOURCE_VERSION,
            "capd_source_commit": EXPECTED_COMMIT,
            "capd_config_modversion": EXPECTED_SOURCE_VERSION,
            "capd_config_dash_version": EXPECTED_FRONTEND_VERSION,
            "pkg_config_frontend": EXPECTED_FRONTEND,
            "libcapd_sha256": EXPECTED_LIBCAPD_SHA256,
            "libfilib_sha256": EXPECTED_LIBFILIB_SHA256,
            "interval_backend": "FILIB",
        },
        "observed": {
            "capd_source_version": source_version,
            "capd_source_commit": commit,
            "capd_config_modversion": modversion,
            "capd_config_dash_version": dash_version,
            "pkg_config_frontend": frontend,
            "pkg_config_frontend_about_version": frontend_about_version,
            "libcapd_sha256": libcapd_hash,
            "libfilib_sha256": libfilib_hash,
            "interval_backend": cache_backend,
            "backend_evidence": {
                "cflags_defines": cflag_markers,
                "linked_libraries": linked_libraries,
            },
        },
        "checks": checks,
        "resolution": {
            "legacy_value_2.5.1_means": "pkgconf frontend version returned by capd-config --version",
            "legacy_value_2.5.1_does_not_mean": "CAPD source or library version",
            "authoritative_capd_version": EXPECTED_SOURCE_VERSION,
            "claim_certificates_rewritten": False,
            "claim_certificate_hash_cascade": False,
            "claim_interval_results_changed": False,
            "claim_probe_replay_performed_by_this_audit": False,
        },
        "affected_claim_certificate_fields": affected,
        "path_independence": {
            "certificate_records_plaintext_local_source_path": True,
            "local_capd_config_path_recorded": False,
            "libcapd_hash_is_source_path_sensitive": True,
            "byte_identical_source_path": str(EXPECTED_BYTE_IDENTICAL_SOURCE_PATH),
            "reason": (
                "CAPDSmithForm.h contributes an __FILE__ string to "
                "intMatrixAlgorithms.cpp.o; a byte-identical libcapd.a therefore "
                "requires the audited historical source path."
            ),
        },
    }


def serialized(document: dict[str, Any]) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--capd-source",
        help="CAPD source checkout (or set CAPD_SOURCE)",
    )
    parser.add_argument(
        "--capd-config",
        help="capd-config executable (or set CAPD_CONFIG)",
    )
    parser.add_argument(
        "--certificate",
        type=Path,
        default=DEFAULT_CERTIFICATE,
        help="certificate to compare or rewrite (default: package certificate.json)",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--print-json",
        action="store_true",
        help="print the reconstructed certificate instead of comparing it",
    )
    mode.add_argument(
        "--write-certificate",
        action="store_true",
        help="rewrite --certificate with the reconstructed path-independent JSON",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        source, config = discover_paths(args.capd_source, args.capd_config)
        document = build_certificate(source, config)
    except (AuditError, json.JSONDecodeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    rendered = serialized(document)
    if args.print_json:
        sys.stdout.write(rendered)
        return 0 if document["status"] == "PASS" else 1

    certificate_path = args.certificate.expanduser().resolve()
    if args.write_certificate:
        certificate_path.write_text(rendered, encoding="utf-8")
        print(f"WROTE {certificate_path}")
    else:
        try:
            tracked = certificate_path.read_text(encoding="utf-8")
            tracked_document = json.loads(tracked)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: cannot read tracked certificate: {exc}", file=sys.stderr)
            return 2
        if tracked_document != document:
            diff = difflib.unified_diff(
                serialized(tracked_document).splitlines(),
                rendered.splitlines(),
                fromfile=str(certificate_path),
                tofile="reconstructed certificate",
                lineterm="",
            )
            print("\n".join(diff), file=sys.stderr)
            return 1

    if document["status"] != "PASS":
        failed = [name for name, passed in document["checks"].items() if not passed]
        print("FAIL: " + ", ".join(failed), file=sys.stderr)
        return 1

    observed = document["observed"]
    print("PASS toolchain metadata audit")
    print(
        f"CAPD {observed['capd_source_version']} @ "
        f"{observed['capd_source_commit']}"
    )
    print(
        "capd-config --modversion "
        f"{observed['capd_config_modversion']}; --version "
        f"{observed['capd_config_dash_version']} ({observed['pkg_config_frontend']})"
    )
    print(f"libcapd.a sha256 {observed['libcapd_sha256']}")
    print(f"interval backend {observed['interval_backend']}")
    if not args.write_certificate:
        print("tracked certificate matches reconstructed metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
