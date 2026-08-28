#!/usr/bin/env python3
"""Clean source-only replay of the exact-source-to-fold certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import tempfile
import time


HERE = Path(__file__).resolve().parent
FUTURE = HERE.parent / "future-target-fold"
FINITE = HERE.parent / "finite-source-intermediate-collar"
CXX_DRIVER = os.environ.get("CXX", "g++")

EXPECTED_TOOLCHAIN = {
    "python_version": "3.14.4",
    "numpy_version": "2.5.2",
    "scipy_version": "1.18.0",
    "gmpy2_version": "2.2.2",
    "mpfr_version": "MPFR 4.2.1",
    "cxx_driver": "g++",
    "cxx_version": "15.2.0",
    "capd_source_version": "6.1.0",
    "capd_source_commit": "731079217a9254ea2948d742df2b170895effe7f",
    "capd_config_modversion": "6.1.0",
    "pkgconf_frontend_version": "2.5.1",
    "libcapd_sha256": (
        "316b2c480f1ce36b293602da9978eb43560646991a4a906d72ee893b3c557119"
    ),
    "interval_backend": "FILIB",
    "libfilib_sha256": (
        "ce5cdf8f22d4a6737461774211053a3df360178194e431e4f7ad2b2ada5caa7e"
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], *, stdout: Path | None = None, env=None) -> None:
    print("+", shlex.join(command), flush=True)
    if stdout is None:
        subprocess.run(command, check=True, env=env)
    else:
        with stdout.open("w", encoding="utf-8") as stream:
            subprocess.run(command, check=True, stdout=stream, env=env)


def capture(command: list[str]) -> str:
    return subprocess.run(
        command, check=True, text=True, capture_output=True
    ).stdout.strip()


def resolve_capd_config(value: Path) -> Path:
    if value.is_file():
        return value.resolve()
    located = shutil.which(str(value))
    if located is None:
        raise RuntimeError(f"capd-config is not executable or on PATH: {value}")
    return Path(located).resolve()


def audit_toolchain(capd_config: Path) -> dict[str, object]:
    """Fail before compilation unless the retained CAPD/FILIB build is pinned."""
    import gmpy2
    import numpy
    import scipy

    capd_config = resolve_capd_config(capd_config)
    if len(capd_config.parents) < 3:
        raise RuntimeError("cannot infer CAPD source from capd-config")
    source = capd_config.parents[2]
    build = capd_config.parents[1]
    libcapd = build / "libcapd.a"
    libfilib = build / "capdExt" / "filibsrc" / "libfilib.a"
    for path in (source / "CAPDVersion.txt", libcapd, libfilib):
        if not path.is_file():
            raise RuntimeError(f"audited toolchain input is missing: {path}")

    version_text = (source / "CAPDVersion.txt").read_text(encoding="utf-8")
    version_parts: list[str] = []
    for name in ("MAJOR", "MINOR", "PATCH"):
        match = re.search(
            rf"set\s*\(\s*CAPD_{name}_VERSION\s+([0-9]+)\s*\)",
            version_text,
            flags=re.IGNORECASE,
        )
        if match is None:
            raise RuntimeError(f"cannot parse CAPD_{name}_VERSION")
        version_parts.append(match.group(1))

    cflags = shlex.split(capture([str(capd_config), "--cflags"]))
    libs = shlex.split(capture([str(capd_config), "--libs"]))
    observed: dict[str, object] = {
        "status": "PASS-PINNED-CAPD-FILIB-PREFLIGHT",
        "python_version": platform.python_version(),
        "numpy_version": numpy.__version__,
        "scipy_version": scipy.__version__,
        "gmpy2_version": gmpy2.version(),
        "mpfr_version": gmpy2.mpfr_version(),
        "cxx_driver": Path(
            shutil.which(CXX_DRIVER) or CXX_DRIVER
        ).name,
        "cxx_version": capture(
            [CXX_DRIVER, "-dumpfullversion", "-dumpversion"]
        ),
        "capd_source_version": ".".join(version_parts),
        "capd_source_commit": capture(
            ["git", "-C", str(source), "rev-parse", "HEAD"]
        ),
        "capd_config_modversion": capture(
            [str(capd_config), "--modversion"]
        ),
        "pkgconf_frontend_version": capture(
            [str(capd_config), "--version"]
        ),
        "libcapd_sha256": sha256(libcapd),
        "interval_backend": "FILIB"
        if "-D__USE_FILIB__" in cflags and "-lfilib" in libs
        else "UNKNOWN",
        "libfilib_sha256": sha256(libfilib),
        "rounding_math_enabled": "-frounding-math" in cflags,
        "links_capd": "-lcapd" in libs,
        "links_filib": "-lfilib" in libs,
    }
    for key, expected in EXPECTED_TOOLCHAIN.items():
        if observed[key] != expected:
            raise RuntimeError(
                f"toolchain preflight mismatch for {key}: "
                f"{observed[key]!r} != {expected!r}"
            )
    if not (
        observed["rounding_math_enabled"]
        and observed["links_capd"]
        and observed["links_filib"]
    ):
        raise RuntimeError("toolchain preflight lacks required compile/link flags")
    return observed


def flags(capd_config: Path, option: str) -> list[str]:
    return shlex.split(
        subprocess.run(
            [str(capd_config), option],
            check=True,
            text=True,
            capture_output=True,
        ).stdout
    )


def compile_probe(
    source: Path, destination: Path, capd_config: Path
) -> None:
    run(
        [
            CXX_DRIVER,
            "-O1",
            "-std=c++17",
            str(source),
            f"-I{HERE}",
            f"-I{FUTURE}",
            f"-I{FINITE}",
            *flags(capd_config, "--cflags"),
            *flags(capd_config, "--libs"),
            "-o",
            str(destination),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--capd-config",
        type=Path,
        default=Path(os.environ.get("CAPD_CONFIG", "capd-config")),
    )
    parser.add_argument("--workers", type=int, default=28)
    parser.add_argument(
        "--work-dir",
        type=Path,
        help="retain all generated bulk artifacts in this directory",
    )
    parser.add_argument(
        "--output-certificate",
        type=Path,
        help="also copy the rebuilt certificate to this path",
    )
    parser.add_argument(
        "--no-compare",
        action="store_true",
        help="build but do not compare with the committed certificate",
    )
    arguments = parser.parse_args()

    started = time.monotonic()
    temporary = None
    if arguments.work_dir is None:
        temporary = tempfile.TemporaryDirectory(prefix="papera-c0-fold-clean-")
        work = Path(temporary.name)
    else:
        work = arguments.work_dir.resolve()
        work.mkdir(parents=True, exist_ok=True)
    main_dir = work / "main"
    tail_dir = work / "tail"
    validation_dir = work / "validation"
    bin_dir = work / "bin"
    validation_dir.mkdir(parents=True, exist_ok=True)
    bin_dir.mkdir(parents=True, exist_ok=True)

    capd_config = resolve_capd_config(arguments.capd_config)
    toolchain = audit_toolchain(capd_config)
    toolchain_path = validation_dir / "toolchain.json"
    toolchain_path.write_text(
        json.dumps(toolchain, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(toolchain, indent=2, sort_keys=True), flush=True)

    clean_env = os.environ.copy()
    clean_env["PYTHONDONTWRITEBYTECODE"] = "1"
    clean_env["OPENBLAS_NUM_THREADS"] = "1"
    clean_env["OMP_NUM_THREADS"] = "1"
    python = os.environ.get("PYTHON", "python3")

    run(
        [
            python,
            str(HERE / "generate_cover.py"),
            "--output-dir",
            str(main_dir),
            "--width-scale",
            "1",
            "--final-half-width",
            "1e-9",
            "--overlap-fraction",
            ".25",
            "--tolerance",
            "2e-10",
        ],
        env=clean_env,
    )
    run(
        [
            python,
            str(HERE / "generate_cover.py"),
            "--output-dir",
            str(tail_dir),
            "--tail-start-u",
            "0.04149701249032356",
            "--tail-end-u",
            "0.04152701249032356",
            "--uniform-half-width",
            "1e-8",
            "--overlap-fraction",
            ".25",
            "--energy-sign-until",
            "0.041524872490323564",
            "--tolerance",
            "2e-10",
        ],
        env=clean_env,
    )

    fixed_binary = bin_dir / "fixed_source_cover_probe"
    cap_binary = bin_dir / "mixed_fold_cap_probe"
    compile_probe(
        HERE / "fixed_source_cover_probe.cpp",
        fixed_binary,
        capd_config,
    )
    compile_probe(
        HERE / "mixed_fold_cap_probe.cpp",
        cap_binary,
        capd_config,
    )
    run(
        [python, str(HERE / "verify_jost_constant.py")],
        stdout=validation_dir / "jost.json",
        env=clean_env,
    )

    run(
        [
            python,
            str(HERE / "validate_cover.py"),
            "--manifest",
            str(main_dir / "cover_boxes.jsonl"),
            "--seeds",
            str(main_dir / "cover_seeds.txt"),
            "--binary",
            str(fixed_binary),
            "--workers",
            str(arguments.workers),
            "--box-results",
            str(validation_dir / "main_results.jsonl"),
            "--bridge-results",
            str(validation_dir / "main_bridges.jsonl"),
            "--summary",
            str(validation_dir / "main_summary.json"),
        ],
        env=clean_env,
    )
    run(
        [
            python,
            str(HERE / "validate_cover.py"),
            "--manifest",
            str(tail_dir / "cover_boxes.jsonl"),
            "--seeds",
            str(tail_dir / "cover_seeds.txt"),
            "--binary",
            str(fixed_binary),
            "--workers",
            str(arguments.workers),
            "--box-results",
            str(validation_dir / "tail_results.jsonl"),
            "--bridge-results",
            str(validation_dir / "tail_bridges.jsonl"),
            "--summary",
            str(validation_dir / "tail_summary.json"),
        ],
        env=clean_env,
    )
    run(
        [
            python,
            str(HERE / "validate_fold_closure.py"),
            "--main-manifest",
            str(main_dir / "cover_boxes.jsonl"),
            "--main-seeds",
            str(main_dir / "cover_seeds.txt"),
            "--tail-manifest",
            str(tail_dir / "cover_boxes.jsonl"),
            "--tail-seeds",
            str(tail_dir / "cover_seeds.txt"),
            "--tail-results",
            str(validation_dir / "tail_results.jsonl"),
            "--fixed-binary",
            str(fixed_binary),
            "--cap-binary",
            str(cap_binary),
            "--workers",
            str(arguments.workers),
            "--containment-results",
            str(validation_dir / "cap_containment.jsonl"),
            "--summary",
            str(validation_dir / "fold_closure.json"),
        ],
        env=clean_env,
    )

    rebuilt = work / "certificate.rebuilt.json"
    run(
        [
            python,
            str(HERE / "build_certificate.py"),
            "--main-dir",
            str(main_dir),
            "--tail-dir",
            str(tail_dir),
            "--validation-dir",
            str(validation_dir),
            "--toolchain-json",
            str(toolchain_path),
            "--output",
            str(rebuilt),
        ],
        env=clean_env,
    )
    committed = HERE / "certificate.json"
    if not arguments.no_compare:
        if not committed.exists():
            raise RuntimeError("committed certificate.json is missing")
        if rebuilt.read_bytes() != committed.read_bytes():
            raise RuntimeError(
                "rebuilt certificate differs from committed certificate: "
                f"rebuilt={sha256(rebuilt)} committed={sha256(committed)}"
            )
    if arguments.output_certificate is not None:
        arguments.output_certificate.write_bytes(rebuilt.read_bytes())
    result = {
        "status": "PASS-CLEAN-SOURCE-ONLY-REPLAY",
        "certificate_sha256": sha256(rebuilt),
        "elapsed_seconds": time.monotonic() - started,
        "work_dir": str(work) if arguments.work_dir is not None else "temporary",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    if temporary is not None:
        temporary.cleanup()


if __name__ == "__main__":
    main()
