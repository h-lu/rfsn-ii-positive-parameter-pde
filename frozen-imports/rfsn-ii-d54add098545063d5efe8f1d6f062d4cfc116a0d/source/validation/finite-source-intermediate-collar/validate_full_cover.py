#!/usr/bin/env python3
"""Run every interval box in cover_boxes.jsonl, in parallel.

This validates individual uniform boxes.  Adjacent-box and endpoint bridge
gates are reported separately and are not inferred from box success alone.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import time


HERE = Path(__file__).resolve().parent


def flags(capd_config: Path, option: str):
    return shlex.split(
        subprocess.run(
            [str(capd_config), option], check=True, text=True, capture_output=True
        ).stdout
    )


def compile_probe(destination: Path, capd_config: Path):
    subprocess.run(
        [
            os.environ.get("CXX", "g++"),
            "-O0",
            "-std=c++17",
            str(HERE / "source_cover_probe.cpp"),
            f"-I{HERE}",
            *flags(capd_config, "--cflags"),
            *flags(capd_config, "--libs"),
            "-o",
            str(destination),
        ],
        check=True,
    )


def parse_interval(text: str):
    if text is None:
        return None
    left, right = text.strip()[1:-1].split(",")
    return float(left), float(right)


def validate_one(binary: Path, seeds: Path, row: dict):
    run = subprocess.run(
        [
            str(binary),
            "--seed-file",
            str(seeds),
            "--seed-offset",
            str(row["seed_offset"]),
            "--parameter",
            row["chart"],
            "--half-width",
            repr(row["half_width"]),
        ],
        text=True,
        capture_output=True,
    )
    result = {
        "index": row["index"],
        "chart": row["chart"],
        "region": row["region"],
        "returncode": run.returncode,
    }
    if run.returncode:
        result["error"] = run.stderr.strip()
        return result
    result.update(json.loads(run.stdout))
    derivative = parse_interval(result.get("d_source_energy_dparameter"))
    result["energy_derivative_strictly_negative"] = (
        derivative is not None and derivative[1] < 0.0
    )
    return result


def validate_bridge(binary: Path, seeds: Path, current: dict, following: dict):
    if current["chart"] == following["chart"]:
        overlap_lower = max(current["parameter_lower"], following["parameter_lower"])
        overlap_upper = min(current["parameter_upper"], following["parameter_upper"])
        if not overlap_lower < overlap_upper:
            return {
                "current_index": current["index"],
                "next_index": following["index"],
                "returncode": 98,
                "error": "no strict common parameter interval",
            }
        bridge_parameter = (overlap_lower + overlap_upper) / 2.0
    else:
        # At the V-to-U switch, fix the current V coordinate.  The bridge
        # Krawczyk image must lie in the next U uniqueness box and its source
        # U projection must lie in that box's declared U-parameter interval.
        bridge_parameter = current["parameter_centre"]
    run = subprocess.run(
        [
            str(binary),
            "--seed-file",
            str(seeds),
            "--seed-offset",
            str(current["seed_offset"]),
            "--parameter",
            current["chart"],
            "--half-width",
            repr(current["half_width"]),
            "--bridge-seed-file",
            str(seeds),
            "--bridge-seed-offset",
            str(following["seed_offset"]),
            "--bridge-chart",
            following["chart"],
            "--bridge-half-width",
            repr(following["half_width"]),
            "--bridge-parameter",
            repr(bridge_parameter),
        ],
        text=True,
        capture_output=True,
    )
    result = {
        "current_index": current["index"],
        "next_index": following["index"],
        "current_chart": current["chart"],
        "next_chart": following["chart"],
        "bridge_parameter_in_current_chart": bridge_parameter,
        "returncode": run.returncode,
    }
    if run.returncode:
        result["error"] = run.stderr.strip()
    else:
        output = json.loads(run.stdout)
        result["adjacent_bridge_certified"] = output["adjacent_bridge_certified"]
        result["current_krawczyk_ratio"] = output["krawczyk_ratio"]
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=HERE / "cover_boxes.jsonl")
    parser.add_argument("--seeds", type=Path, default=HERE / "cover_seeds.txt")
    parser.add_argument("--binary", type=Path)
    parser.add_argument(
        "--capd-config",
        type=Path,
        default=Path(os.environ.get("CAPD_CONFIG", "capd-config")),
        help="CAPD capd-config executable (or set CAPD_CONFIG)",
    )
    parser.add_argument("--workers", type=int, default=min(16, os.cpu_count() or 1))
    parser.add_argument("--limit", type=int)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--results", type=Path, default=HERE / "cover_results.jsonl")
    parser.add_argument("--summary", type=Path, default=HERE / "cover_validation_summary.json")
    parser.add_argument("--bridge-results", type=Path, default=HERE / "cover_bridge_results.jsonl")
    args = parser.parse_args()

    rows = [json.loads(line) for line in args.manifest.read_text().splitlines()]
    rows = rows[args.start :]
    if args.limit:
        rows = rows[: args.limit]
    started = time.monotonic()
    temporary = None
    if args.binary is None:
        temporary = tempfile.TemporaryDirectory(prefix="papera-cover-validation-")
        binary = Path(temporary.name) / "source_cover_probe"
        compile_probe(binary, args.capd_config)
    else:
        binary = args.binary
    results = [None] * len(rows)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        pending = {
            executor.submit(validate_one, binary, args.seeds, row): position
            for position, row in enumerate(rows)
        }
        completed = 0
        for future in as_completed(pending):
            results[pending[future]] = future.result()
            completed += 1
            if completed % 250 == 0:
                print(
                    f"validated {completed}/{len(rows)} "
                    f"elapsed={time.monotonic() - started:.1f}s",
                    flush=True,
                )

    failures = [result for result in results if result["returncode"] != 0]
    tangent_failures = [
        result
        for result in results
        if result["returncode"] == 0 and not result["tangent_certified"]
    ]
    sign_unresolved = [
        result
        for result in results[1:]
        if result["returncode"] == 0
        and not result["energy_derivative_strictly_negative"]
    ]
    with args.results.open("w") as handle:
        for result in results:
            handle.write(json.dumps(result, sort_keys=True) + "\n")

    bridge_results = []
    if not failures and not tangent_failures and len(rows) > 1:
        pairs = list(zip(rows[:-1], rows[1:]))
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            pending = {
                executor.submit(validate_bridge, binary, args.seeds, current, following): position
                for position, (current, following) in enumerate(pairs)
            }
            bridge_results = [None] * len(pairs)
            completed = 0
            for future in as_completed(pending):
                bridge_results[pending[future]] = future.result()
                completed += 1
                if completed % 250 == 0:
                    print(
                        f"bridged {completed}/{len(pairs)} "
                        f"elapsed={time.monotonic() - started:.1f}s",
                        flush=True,
                    )
    bridge_failures = [
        result
        for result in bridge_results
        if result["returncode"] != 0 or not result.get("adjacent_bridge_certified", False)
    ]
    with args.bridge_results.open("w") as handle:
        for result in bridge_results:
            handle.write(json.dumps(result, sort_keys=True) + "\n")

    successful = [result for result in results if result["returncode"] == 0]
    summary = {
        "status": (
            "PASS-ALL-BOXES-AND-TRUE-ADJACENCY"
            if not failures and not tangent_failures and not bridge_failures
            else "INCOMPLETE-BOX-VALIDATION"
        ),
        "box_count": len(results),
        "failure_count": len(failures),
        "failure_indices": [result["index"] for result in failures],
        "tangent_failure_count": len(tangent_failures),
        "tangent_failure_indices": [result["index"] for result in tangent_failures],
        "energy_sign_unresolved_count_excluding_first_box": len(sign_unresolved),
        "energy_sign_unresolved_indices": [result["index"] for result in sign_unresolved],
        "adjacent_bridge_count": len(bridge_results),
        "adjacent_bridge_failure_count": len(bridge_failures),
        "adjacent_bridge_failure_pairs": [
            [result["current_index"], result["next_index"]]
            for result in bridge_failures
        ],
        "maximum_krawczyk_ratio": max(
            (result["krawczyk_ratio"] for result in successful), default=None
        ),
        "maximum_contraction_ratio": max(
            (result["contraction_ratio"] for result in successful), default=None
        ),
        "maximum_tangent_krawczyk_ratio": max(
            (
                result["tangent_krawczyk_ratio"]
                for result in successful
                if result["tangent_certified"]
            ),
            default=None,
        ),
        "elapsed_seconds": time.monotonic() - started,
        "adjacent_bridge_gate": (
            "PASS" if bridge_results and not bridge_failures else "NOT-PASS"
        ),
        "outer_fold_event_bridge_gate": "NOT-RUN-BY-THIS-SCRIPT",
        "local_annulus_gate": "NOT-RUN-BY-THIS-SCRIPT",
    }
    args.summary.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if temporary is not None:
        temporary.cleanup()
    if failures or tangent_failures or bridge_failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
