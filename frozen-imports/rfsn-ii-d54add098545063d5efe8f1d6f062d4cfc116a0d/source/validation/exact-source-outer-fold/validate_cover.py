#!/usr/bin/env python3
"""Replay the fixed-time c0-to-fold interval cover.

Floating centres are only preconditioner data.  This driver compiles the CAPD
probe and checks every parametric box and every adjacent common-root bridge.
All generated centres, binaries, and detailed results may live outside the
source tree; no bulk data are proof inputs committed to the repository.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import time


HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def capd_flags(capd_config: Path, option: str) -> list[str]:
    return shlex.split(
        subprocess.run(
            [str(capd_config), option],
            check=True,
            text=True,
            capture_output=True,
        ).stdout
    )


def compile_probe(destination: Path, capd_config: Path) -> None:
    subprocess.run(
        [
            os.environ.get("CXX", "g++"),
            "-O1",
            "-std=c++17",
            str(HERE / "fixed_source_cover_probe.cpp"),
            f"-I{HERE}",
            f"-I{HERE.parent / 'finite-source-intermediate-collar'}",
            f"-I{HERE.parent / 'future-target-fold'}",
            *capd_flags(capd_config, "--cflags"),
            *capd_flags(capd_config, "--libs"),
            "-o",
            str(destination),
        ],
        check=True,
    )


def interval(text: str) -> tuple[float, float]:
    left, right = text.strip()[1:-1].split(",")
    return float(left), float(right)


def command_for_box(binary: Path, seeds: Path, row: dict) -> list[str]:
    command = [
        str(binary),
        "--seed-file",
        str(seeds),
        "--seed-offset",
        str(row["seed_offset"]),
        "--half-width",
        repr(row["half_width"]),
    ]
    if row.get("exact_c0_endpoint", False):
        command.append("--exact-c0")
    return command


def validate_box(binary: Path, seeds: Path, row: dict) -> dict:
    run = subprocess.run(
        command_for_box(binary, seeds, row),
        text=True,
        capture_output=True,
    )
    result = {"index": row["index"], "returncode": run.returncode}
    if run.returncode:
        result["error"] = run.stderr.strip()
        return result
    result.update(json.loads(run.stdout))
    derivative = interval(result["d_source_energy_dU"])
    result["energy_sign_required"] = row["energy_sign_required"]
    result["required_energy_derivative_negative"] = (
        not row["energy_sign_required"] or derivative[1] < 0.0
    )
    return result


def validate_bridge(
    binary: Path, seeds: Path, current: dict, following: dict
) -> dict:
    overlap_lower = max(
        current["parameter_interval"][0], following["parameter_interval"][0]
    )
    overlap_upper = min(
        current["parameter_interval"][1], following["parameter_interval"][1]
    )
    if not overlap_lower < overlap_upper:
        return {
            "current_index": current["index"],
            "next_index": following["index"],
            "returncode": 98,
            "error": "no strict common parameter interval",
        }
    bridge_parameter = (overlap_lower + overlap_upper) / 2.0
    command = command_for_box(binary, seeds, current)
    command.extend(
        [
            "--bridge-seed-file",
            str(seeds),
            "--bridge-seed-offset",
            str(following["seed_offset"]),
            "--bridge-half-width",
            repr(following["half_width"]),
            "--bridge-parameter",
            repr(bridge_parameter),
        ]
    )
    run = subprocess.run(command, text=True, capture_output=True)
    result = {
        "current_index": current["index"],
        "next_index": following["index"],
        "bridge_parameter": bridge_parameter,
        "overlap_interval": [overlap_lower, overlap_upper],
        "returncode": run.returncode,
    }
    if run.returncode:
        result["error"] = run.stderr.strip()
        return result
    output = json.loads(run.stdout)
    for key in (
        "adjacent_bridge_certified",
        "bridge_current_containment_margin",
        "bridge_next_containment_margin",
        "bridge_next_parameter_margin",
        "krawczyk_ratio",
        "contraction_ratio",
        "tangent_krawczyk_ratio",
    ):
        result[key] = output[key]
    return result


def parallel_replay(
    label: str, jobs: list, worker, workers: int, started: float
) -> list[dict]:
    results: list[dict | None] = [None] * len(jobs)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        pending = {
            executor.submit(worker, *job): position
            for position, job in enumerate(jobs)
        }
        completed = 0
        for future in as_completed(pending):
            results[pending[future]] = future.result()
            completed += 1
            if completed % 250 == 0 or completed == len(jobs):
                print(
                    f"{label} {completed}/{len(jobs)} "
                    f"elapsed={time.monotonic() - started:.1f}s",
                    flush=True,
                )
    return [result for result in results if result is not None]


def write_jsonl(path: Path | None, rows: list[dict]) -> None:
    if path is None:
        return
    with path.open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, sort_keys=True) + "\n")


def extrema(rows: list[dict], key: str, kind=max):
    eligible = [(row[key], row) for row in rows if key in row]
    if not eligible:
        return None
    value, row = kind(eligible, key=lambda item: item[0])
    index = row.get("index", row.get("current_index"))
    return {"value": value, "index": index}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--seeds", type=Path, required=True)
    parser.add_argument("--binary", type=Path)
    parser.add_argument(
        "--capd-config",
        type=Path,
        default=Path(os.environ.get("CAPD_CONFIG", "capd-config")),
    )
    parser.add_argument("--workers", type=int, default=min(28, os.cpu_count() or 1))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--bridges-only", action="store_true")
    parser.add_argument("--box-results", type=Path)
    parser.add_argument("--bridge-results", type=Path)
    parser.add_argument("--summary", type=Path)
    arguments = parser.parse_args()

    rows = [
        json.loads(line)
        for line in arguments.manifest.read_text(encoding="utf-8").splitlines()
    ]
    if arguments.limit is not None:
        rows = rows[: arguments.limit]
    if len(rows) < 2:
        raise SystemExit("the replay requires at least two cover boxes")

    started = time.monotonic()
    temporary = None
    if arguments.binary is None:
        temporary = tempfile.TemporaryDirectory(prefix="papera-c0-fold-replay-")
        binary = Path(temporary.name) / "fixed_source_cover_probe"
        compile_probe(binary, arguments.capd_config)
    else:
        binary = arguments.binary

    box_results: list[dict] = []
    if not arguments.bridges_only:
        box_results = parallel_replay(
            "boxes",
            [(binary, arguments.seeds, row) for row in rows],
            validate_box,
            arguments.workers,
            started,
        )
        write_jsonl(arguments.box_results, box_results)

    bridge_results = parallel_replay(
        "bridges",
        [
            (binary, arguments.seeds, current, following)
            for current, following in zip(rows[:-1], rows[1:])
        ],
        validate_bridge,
        arguments.workers,
        started,
    )
    write_jsonl(arguments.bridge_results, bridge_results)

    box_failures = [row for row in box_results if row["returncode"]]
    sign_failures = [
        row
        for row in box_results
        if row["returncode"] == 0
        and not row["required_energy_derivative_negative"]
    ]
    bridge_failures = [
        row
        for row in bridge_results
        if row["returncode"]
        or not row.get("adjacent_bridge_certified", False)
    ]
    summary = {
        "status": (
            "PASS-ALL-REQUESTED-BOXES-AND-TRUE-ADJACENCY"
            if not box_failures and not sign_failures and not bridge_failures
            else "FAIL-COVER-REPLAY"
        ),
        "box_count": len(box_results),
        "box_failure_count": len(box_failures),
        "required_energy_sign_failure_count": len(sign_failures),
        "adjacent_bridge_count": len(bridge_results),
        "adjacent_bridge_failure_count": len(bridge_failures),
        "first_bridge_failure": bridge_failures[0] if bridge_failures else None,
        "maximum_krawczyk_ratio": extrema(box_results, "krawczyk_ratio"),
        "maximum_contraction_ratio": extrema(box_results, "contraction_ratio"),
        "maximum_tangent_krawczyk_ratio": extrema(
            box_results, "tangent_krawczyk_ratio"
        ),
        "minimum_bridge_current_margin": extrema(
            bridge_results, "bridge_current_containment_margin", min
        ),
        "minimum_bridge_next_margin": extrema(
            bridge_results, "bridge_next_containment_margin", min
        ),
        "minimum_bridge_parameter_margin": extrema(
            bridge_results, "bridge_next_parameter_margin", min
        ),
        "manifest_sha256": sha256(arguments.manifest),
        "seeds_sha256": sha256(arguments.seeds),
        "probe_sha256": sha256(HERE / "fixed_source_cover_probe.cpp"),
        "elapsed_seconds": time.monotonic() - started,
    }
    rendered = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if arguments.summary is not None:
        arguments.summary.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if temporary is not None:
        temporary.cleanup()
    if box_failures or sign_failures or bridge_failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
