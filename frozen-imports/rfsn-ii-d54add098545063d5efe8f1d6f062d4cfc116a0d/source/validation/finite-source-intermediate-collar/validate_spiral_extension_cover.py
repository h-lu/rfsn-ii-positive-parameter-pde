#!/usr/bin/env python3
"""Validate the complete finite-collar-to-fixed-annulus seam cover."""

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


def flags(capd_config: Path, option: str) -> list[str]:
    return shlex.split(
        subprocess.run(
            [str(capd_config), option],
            check=True,
            text=True,
            capture_output=True,
        ).stdout
    )


def compile_probe(destination: Path, capd_config: Path, segments: int):
    subprocess.run(
        [
            os.environ.get("CXX", "g++"),
            "-O0",
            "-std=c++17",
            f"-DPAPERA_SEGMENTS={segments}",
            str(HERE / "spiral_source_cover_probe.cpp"),
            f"-I{HERE}",
            *flags(capd_config, "--cflags"),
            *flags(capd_config, "--libs"),
            "-o",
            str(destination),
        ],
        check=True,
    )


def base_command(binary: Path, seeds: Path, row: dict) -> list[str]:
    return [
        str(binary),
        "--seed-file",
        str(seeds),
        "--seed-offset",
        str(row["seed_offset"]),
        "--parameter",
        row["chart"],
        "--seed-tangent-kind",
        row.get("seed_tangent_kind", "v"),
        "--half-width",
        repr(row["half_width"]),
        "--radius-scale",
        repr(row.get("radius_scale", 1.0)),
    ]


def run_json(command: list[str]) -> tuple[int, dict | None, str]:
    run = subprocess.run(command, text=True, capture_output=True)
    if run.returncode:
        return run.returncode, None, run.stderr.strip()
    return 0, json.loads(run.stdout), ""


def validate_one(binary: Path, seeds: Path, row: dict) -> dict:
    returncode, output, error = run_json(base_command(binary, seeds, row))
    result = {
        "index": row["index"],
        "chart": row["chart"],
        "group": row["group"],
        "region": row["region"],
        "returncode": returncode,
    }
    if returncode:
        result["error"] = error
    else:
        result.update(output)
    return result


def overlap_parameter(first: dict, second: dict) -> float | None:
    if first["chart"] != second["chart"]:
        return None
    lower = max(first["parameter_lower"], second["parameter_lower"])
    upper = min(first["parameter_upper"], second["parameter_upper"])
    if not lower < upper:
        raise RuntimeError(
            f"rows {first['index']},{second['index']} have no strict overlap"
        )
    return (lower + upper) / 2.0


def one_bridge_direction(
    binary: Path,
    seeds: Path,
    primary: dict,
    containing: dict,
    common_parameter: float | None,
) -> tuple[int, dict | None, str]:
    parameter = (
        primary["parameter_centre"]
        if common_parameter is None
        else common_parameter
    )
    command = [
        *base_command(binary, seeds, primary),
        "--bridge-seed-file",
        str(seeds),
        "--bridge-seed-offset",
        str(containing["seed_offset"]),
        "--bridge-chart",
        containing["chart"],
        "--bridge-half-width",
        repr(containing["half_width"]),
        "--bridge-parameter",
        repr(parameter),
    ]
    return run_json(command)


def validate_bridge(binary: Path, seeds: Path, first: dict, second: dict) -> dict:
    common_parameter = overlap_parameter(first, second)
    forward = one_bridge_direction(
        binary, seeds, first, second, common_parameter
    )
    if forward[0] == 0 and forward[1]["adjacent_bridge_certified"]:
        return {
            "current_index": first["index"],
            "next_index": second["index"],
            "current_chart": first["chart"],
            "next_chart": second["chart"],
            "direction": "forward",
            "returncode": 0,
            "adjacent_bridge_certified": True,
            "bridge_krawczyk_ratio": forward[1]["krawczyk_ratio"],
            "current_containment_margin": forward[1][
                "bridge_current_containment_margin"
            ],
            "next_containment_margin": forward[1][
                "bridge_next_containment_margin"
            ],
            "next_parameter_margin": forward[1][
                "bridge_next_parameter_margin"
            ],
        }

    reverse = one_bridge_direction(
        binary, seeds, second, first, common_parameter
    )
    if reverse[0] == 0 and reverse[1]["adjacent_bridge_certified"]:
        return {
            "current_index": first["index"],
            "next_index": second["index"],
            "current_chart": first["chart"],
            "next_chart": second["chart"],
            "direction": "reverse",
            "returncode": 0,
            "adjacent_bridge_certified": True,
            "bridge_krawczyk_ratio": reverse[1]["krawczyk_ratio"],
            "current_containment_margin": reverse[1][
                "bridge_current_containment_margin"
            ],
            "next_containment_margin": reverse[1][
                "bridge_next_containment_margin"
            ],
            "next_parameter_margin": reverse[1][
                "bridge_next_parameter_margin"
            ],
            "forward_error": forward[2],
        }
    return {
        "current_index": first["index"],
        "next_index": second["index"],
        "current_chart": first["chart"],
        "next_chart": second["chart"],
        "direction": "neither",
        "returncode": reverse[0] or forward[0] or 97,
        "adjacent_bridge_certified": False,
        "forward_error": forward[2],
        "reverse_error": reverse[2],
    }


def validate_box_with_bridge(
    binary: Path, seeds: Path, first: dict, second: dict | None
) -> tuple[dict, dict | None]:
    """Validate one box and, when present, its forward adjacency in one run.

    A failed forward containment is retried in reverse.  The plain box is
    rerun only when needed to distinguish a bridge-direction failure from an
    individual Krawczyk failure.
    """

    if second is None:
        return validate_one(binary, seeds, first), None
    common_parameter = overlap_parameter(first, second)
    parameter = (
        first["parameter_centre"]
        if common_parameter is None
        else common_parameter
    )
    command = [
        *base_command(binary, seeds, first),
        "--bridge-seed-file",
        str(seeds),
        "--bridge-seed-offset",
        str(second["seed_offset"]),
        "--bridge-chart",
        second["chart"],
        "--bridge-half-width",
        repr(second["half_width"]),
        "--bridge-parameter",
        repr(parameter),
    ]
    returncode, output, error = run_json(command)
    if returncode == 0 and output["adjacent_bridge_certified"]:
        box = {
            "index": first["index"],
            "chart": first["chart"],
            "group": first["group"],
            "region": first["region"],
            "returncode": 0,
            **output,
        }
        bridge = {
            "current_index": first["index"],
            "next_index": second["index"],
            "current_chart": first["chart"],
            "next_chart": second["chart"],
            "direction": "forward",
            "returncode": 0,
            "adjacent_bridge_certified": True,
            "bridge_krawczyk_ratio": output["krawczyk_ratio"],
            "current_containment_margin": output[
                "bridge_current_containment_margin"
            ],
            "next_containment_margin": output[
                "bridge_next_containment_margin"
            ],
            "next_parameter_margin": output["bridge_next_parameter_margin"],
        }
        return box, bridge

    box = validate_one(binary, seeds, first)
    if box["returncode"]:
        print(
            f"STRICT BOX FAILURE index={first['index']} "
            f"error={box.get('error', error)}",
            flush=True,
        )
        return box, {
            "current_index": first["index"],
            "next_index": second["index"],
            "current_chart": first["chart"],
            "next_chart": second["chart"],
            "direction": "not-run-after-box-failure",
            "returncode": box["returncode"],
            "adjacent_bridge_certified": False,
            "forward_error": error,
        }
    reverse = one_bridge_direction(
        binary, seeds, second, first, common_parameter
    )
    if reverse[0] == 0 and reverse[1]["adjacent_bridge_certified"]:
        return box, {
            "current_index": first["index"],
            "next_index": second["index"],
            "current_chart": first["chart"],
            "next_chart": second["chart"],
            "direction": "reverse",
            "returncode": 0,
            "adjacent_bridge_certified": True,
            "bridge_krawczyk_ratio": reverse[1]["krawczyk_ratio"],
            "current_containment_margin": reverse[1][
                "bridge_current_containment_margin"
            ],
            "next_containment_margin": reverse[1][
                "bridge_next_containment_margin"
            ],
            "next_parameter_margin": reverse[1][
                "bridge_next_parameter_margin"
            ],
            "forward_error": error,
        }
    bridge = {
        "current_index": first["index"],
        "next_index": second["index"],
        "current_chart": first["chart"],
        "next_chart": second["chart"],
        "direction": "neither",
        "returncode": reverse[0] or returncode or 97,
        "adjacent_bridge_certified": False,
        "forward_error": error,
        "reverse_error": reverse[2],
    }
    print(
        f"STRICT BRIDGE FAILURE pair={first['index']},{second['index']} "
        f"forward={error} reverse={reverse[2]}",
        flush=True,
    )
    return box, bridge


def endpoint_containment(
    binary: Path,
    extension_seeds: Path,
    first: dict,
    coarse_seeds: Path,
    coarse: dict,
    coarse_segments: int,
) -> dict:
    command = [
        *base_command(binary, extension_seeds, first),
        "--coarse-seed-file",
        str(coarse_seeds),
        "--coarse-seed-offset",
        str(coarse["seed_offset"]),
        "--coarse-segments",
        str(coarse_segments),
        "--coarse-chart",
        coarse["chart"],
        "--coarse-half-width",
        repr(coarse["half_width"]),
        "--coarse-radius-scale",
        repr(coarse.get("radius_scale", 1.0)),
    ]
    returncode, output, error = run_json(command)
    return {
        "status": (
            "PASS-FINE-ROOT-IN-COARSE-ENDPOINT-UNIQUENESS-BOX"
            if returncode == 0
            and output["coarse_endpoint_containment_certified"]
            else "FAIL"
        ),
        "returncode": returncode,
        "coarse_endpoint_index": coarse["index"],
        "fine_extension_index": first["index"],
        "containment_margin": (
            output["coarse_endpoint_containment_margin"]
            if output is not None
            else None
        ),
        "error": error or None,
    }


def seam_containment(binary: Path, seeds: Path, last: dict) -> dict:
    returncode, output, error = run_json(
        [
            *base_command(binary, seeds, last),
            "--fixed-radial-seam-containment",
        ]
    )
    return {
        "status": (
            "PASS-EVENT-ROOT-SOURCE-IN-FIXED-RADIAL-SEAM-BOX"
            if returncode == 0
            and output["fixed_radial_seam_source_containment_certified"]
            else "FAIL"
        ),
        "returncode": returncode,
        "extension_index": last["index"],
        "containment_margin": (
            output["fixed_radial_seam_source_containment_margin"]
            if output is not None
            else None
        ),
        "source_U": output.get("source_U") if output else None,
        "source_P": output.get("source_P") if output else None,
        "source_V": output.get("source_V") if output else None,
        "source_Q": output.get("source_Q") if output else None,
        "source_radius": output.get("source_radius") if output else None,
        "error": error or None,
    }


def parallel_map(function, items, workers: int, label: str, started: float):
    results = [None] * len(items)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        pending = {
            executor.submit(function, *item): position
            for position, item in enumerate(items)
        }
        completed = 0
        for future in as_completed(pending):
            results[pending[future]] = future.result()
            completed += 1
            if completed % 250 == 0:
                print(
                    f"{label} {completed}/{len(items)} "
                    f"elapsed={time.monotonic() - started:.1f}s",
                    flush=True,
                )
    return results


def write_jsonl(path: Path, rows: list[dict]):
    with path.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--coarse-manifest", type=Path, required=True)
    parser.add_argument("--coarse-seeds", type=Path, required=True)
    parser.add_argument("--coarse-segments", type=int, default=36)
    parser.add_argument("--binary", type=Path)
    parser.add_argument(
        "--capd-config",
        type=Path,
        default=Path(os.environ.get("CAPD_CONFIG", "capd-config")),
    )
    parser.add_argument(
        "--workers", type=int, default=min(24, os.cpu_count() or 1)
    )
    args = parser.parse_args()

    manifest_path = args.input_dir / "spiral_extension_boxes.jsonl"
    seeds_path = args.input_dir / "spiral_extension_seeds.txt"
    rows = [json.loads(line) for line in manifest_path.read_text().splitlines()]
    coarse_rows = [
        json.loads(line) for line in args.coarse_manifest.read_text().splitlines()
    ]
    if not rows or not coarse_rows:
        raise RuntimeError("empty extension or coarse manifest")
    segment_counts = {int(row["segments"]) for row in rows}
    if len(segment_counts) != 1:
        raise RuntimeError("extension manifest mixes shooting dimensions")
    segments = segment_counts.pop()
    if args.coarse_segments >= segments or segments % args.coarse_segments:
        raise RuntimeError("coarse endpoint does not have lower dimension")

    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise RuntimeError("output directory must be absent or empty")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    temporary = None
    if args.binary is None:
        temporary = tempfile.TemporaryDirectory(prefix="papera-spiral-cover-")
        binary = Path(temporary.name) / "source_cover_probe"
        compile_probe(binary, args.capd_config, segments)
    else:
        binary = args.binary

    combined = parallel_map(
        lambda first, second: validate_box_with_bridge(
            binary, seeds_path, first, second
        ),
        [
            (row, rows[index + 1] if index + 1 < len(rows) else None)
            for index, row in enumerate(rows)
        ],
        args.workers,
        "box+bridge tasks",
        started,
    )
    results = [item[0] for item in combined]
    bridges = [item[1] for item in combined[:-1]]
    failures = [result for result in results if result["returncode"]]
    tangent_failures = [
        result
        for result in results
        if not result["returncode"] and not result["tangent_certified"]
    ]
    write_jsonl(args.output_dir / "spiral_extension_results.jsonl", results)
    bridge_failures = [
        bridge
        for bridge in bridges
        if bridge["returncode"] or not bridge["adjacent_bridge_certified"]
    ]
    write_jsonl(
        args.output_dir / "spiral_extension_bridge_results.jsonl", bridges
    )

    endpoint = {"status": "NOT-RUN"}
    seam = {"status": "NOT-RUN"}
    if not failures and not tangent_failures and not bridge_failures:
        endpoint = endpoint_containment(
            binary,
            seeds_path,
            rows[0],
            args.coarse_seeds,
            coarse_rows[-1],
            args.coarse_segments,
        )
        seam = seam_containment(binary, seeds_path, rows[-1])

    successful = [result for result in results if not result["returncode"]]
    summary = {
        "status": (
            "PASS-COMPLETE-FINITE-COLLAR-TO-FIXED-ANNULUS-SEAM"
            if not failures
            and not tangent_failures
            and not bridge_failures
            and endpoint["status"].startswith("PASS")
            and seam["status"].startswith("PASS")
            else "INCOMPLETE-SPIRAL-EXTENSION"
        ),
        "segments": segments,
        "box_count": len(results),
        "box_failure_count": len(failures),
        "box_failure_indices": [result["index"] for result in failures],
        "tangent_failure_count": len(tangent_failures),
        "tangent_failure_indices": [
            result["index"] for result in tangent_failures
        ],
        "adjacent_bridge_count": len(bridges),
        "adjacent_bridge_failure_count": len(bridge_failures),
        "adjacent_bridge_failure_pairs": [
            [bridge["current_index"], bridge["next_index"]]
            for bridge in bridge_failures
        ],
        "reverse_bridge_count": sum(
            bridge.get("direction") == "reverse" for bridge in bridges
        ),
        "minimum_bridge_current_containment_margin": min(
            (
                bridge["current_containment_margin"]
                for bridge in bridges
                if not bridge["returncode"]
            ),
            default=None,
        ),
        "minimum_bridge_next_containment_margin": min(
            (
                bridge["next_containment_margin"]
                for bridge in bridges
                if not bridge["returncode"]
            ),
            default=None,
        ),
        "minimum_bridge_next_parameter_margin": min(
            (
                bridge["next_parameter_margin"]
                for bridge in bridges
                if not bridge["returncode"]
            ),
            default=None,
        ),
        "maximum_krawczyk_ratio": max(
            (result["krawczyk_ratio"] for result in successful),
            default=None,
        ),
        "maximum_contraction_ratio": max(
            (result["contraction_ratio"] for result in successful),
            default=None,
        ),
        "maximum_tangent_krawczyk_ratio": max(
            (result["tangent_krawczyk_ratio"] for result in successful),
            default=None,
        ),
        "all_first_event": all(
            result.get("first_event", False) for result in successful
        ),
        "coarse_endpoint_containment": endpoint,
        "fixed_radial_seam_containment": seam,
        "elapsed_seconds": time.monotonic() - started,
    }
    (args.output_dir / "spiral_extension_validation_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if temporary is not None:
        temporary.cleanup()
    if summary["status"].startswith("INCOMPLETE"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
