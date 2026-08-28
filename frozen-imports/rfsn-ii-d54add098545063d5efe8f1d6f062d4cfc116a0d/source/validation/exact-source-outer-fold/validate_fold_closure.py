#!/usr/bin/env python3
"""Validate the sign-tail, fold cap, and all endpoint identifications."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import time


HERE = Path(__file__).resolve().parent
FOLD_U = 0.041527012490323562
FOLD_U_INTERVAL = (0.041527012176079285, 0.041527012805834346)
CAP_HALF_WIDTH = 1.5e-6
FAMILY_START_U = FOLD_U - 2.08e-6
SIGN_UNTIL_U = FOLD_U - 1.99e-6
ENDPOINT_RADIUS_SCALE = 5.0


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def interval(text: str) -> tuple[float, float]:
    left, right = text.strip()[1:-1].split(",")
    return float(left), float(right)


def run_json(command: list[str]) -> dict:
    run = subprocess.run(command, text=True, capture_output=True)
    if run.returncode:
        raise RuntimeError(
            f"command failed ({run.returncode}): {' '.join(command)}\n"
            f"{run.stderr.strip()}"
        )
    return json.loads(run.stdout)


def cap_containment(
    cap_binary: Path, tail_seeds: Path, row: dict
) -> dict:
    command = [
        str(cap_binary),
        "--containment-only",
        "--cap-half-width",
        repr(CAP_HALF_WIDTH),
        "--family-seed-file",
        str(tail_seeds),
        "--family-seed-offset",
        str(row["seed_offset"]),
        "--family-half-width",
        repr(row["half_width"]),
    ]
    try:
        output = run_json(command)
    except RuntimeError as error:
        return {
            "index": row["index"],
            "source_u": row["source_u"],
            "returncode": 12,
            "error": str(error),
        }
    output["index"] = row["index"]
    output["source_u"] = row["source_u"]
    output["returncode"] = 0
    return output


def main_to_tail_bridge(
    fixed_binary: Path,
    main_rows: list[dict],
    main_seeds: Path,
    tail_row: dict,
    tail_seeds: Path,
) -> dict:
    candidates = [
        row
        for row in main_rows
        if row["parameter_interval"][0] < tail_row["source_u"]
        < row["parameter_interval"][1]
    ]
    if len(candidates) != 1:
        raise RuntimeError(
            f"expected one main-cover box at tail start, got {len(candidates)}"
        )
    main_row = candidates[0]
    overlap_lower = max(
        main_row["parameter_interval"][0],
        tail_row["parameter_interval"][0],
    )
    overlap_upper = min(
        main_row["parameter_interval"][1],
        tail_row["parameter_interval"][1],
    )
    if not overlap_lower < overlap_upper:
        raise RuntimeError("main cover and sign tail have no strict overlap")
    bridge_parameter = (overlap_lower + overlap_upper) / 2.0

    # Use the narrow tail Krawczyk image and require it to lie in both
    # uniqueness boxes.  This is a true common-root check, not scalar overlap.
    output = run_json(
        [
            str(fixed_binary),
            "--seed-file",
            str(tail_seeds),
            "--seed-offset",
            str(tail_row["seed_offset"]),
            "--half-width",
            repr(tail_row["half_width"]),
            "--bridge-seed-file",
            str(main_seeds),
            "--bridge-seed-offset",
            str(main_row["seed_offset"]),
            "--bridge-half-width",
            repr(main_row["half_width"]),
            "--bridge-parameter",
            repr(bridge_parameter),
        ]
    )
    if not output["adjacent_bridge_certified"]:
        raise RuntimeError("main-cover to sign-tail common-root gate failed")
    return {
        "status": "PASS-TRUE-COMMON-ROOT",
        "main_index": main_row["index"],
        "tail_index": tail_row["index"],
        "bridge_parameter": bridge_parameter,
        "current_containment_margin": output[
            "bridge_current_containment_margin"
        ],
        "main_containment_margin": output["bridge_next_containment_margin"],
        "main_parameter_margin": output["bridge_next_parameter_margin"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-manifest", type=Path, required=True)
    parser.add_argument("--main-seeds", type=Path, required=True)
    parser.add_argument("--tail-manifest", type=Path, required=True)
    parser.add_argument("--tail-seeds", type=Path, required=True)
    parser.add_argument("--tail-results", type=Path, required=True)
    parser.add_argument("--fixed-binary", type=Path, required=True)
    parser.add_argument("--cap-binary", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=28)
    parser.add_argument("--containment-results", type=Path)
    parser.add_argument("--summary", type=Path)
    arguments = parser.parse_args()
    started = time.monotonic()

    main_rows = load_jsonl(arguments.main_manifest)
    tail_rows = load_jsonl(arguments.tail_manifest)
    tail_results = load_jsonl(arguments.tail_results)
    if len(tail_rows) != len(tail_results):
        raise RuntimeError("tail manifest/results length mismatch")
    for position, (row, result) in enumerate(zip(tail_rows, tail_results)):
        if row["index"] != position or result["index"] != position:
            raise RuntimeError("tail order/index mismatch")
        if result["returncode"]:
            raise RuntimeError(f"tail box {position} did not pass")

    sign_rows = [
        (row, result)
        for row, result in zip(tail_rows, tail_results)
        if row["parameter_interval"][1] < SIGN_UNTIL_U
    ]
    if not sign_rows:
        raise RuntimeError("empty sign-tail audit")
    sign_failures = [
        (row["index"], result["d_source_energy_dU"])
        for row, result in sign_rows
        if interval(result["d_source_energy_dU"])[1] >= 0.0
    ]
    if sign_failures:
        raise RuntimeError(f"sign-tail derivative failure: {sign_failures[0]}")
    sign_maximum = max(
        (interval(result["d_source_energy_dU"])[1], row["index"])
        for row, result in sign_rows
    )

    family_rows = [row for row in tail_rows if row["source_u"] >= FAMILY_START_U]
    if not family_rows:
        raise RuntimeError("empty cap-family cover")
    if not family_rows[0]["parameter_interval"][0] < SIGN_UNTIL_U:
        raise RuntimeError("negative-sign cover does not overlap cap-family cover")
    if not (
        family_rows[-1]["parameter_interval"][0] < FOLD_U_INTERVAL[0]
        and family_rows[-1]["parameter_interval"][1] > FOLD_U_INTERVAL[1]
    ):
        raise RuntimeError("cap-family cover does not contain fold endpoint")
    for current, following in zip(family_rows[:-1], family_rows[1:]):
        if not current["parameter_interval"][1] > following[
            "parameter_interval"
        ][0]:
            raise RuntimeError("cap-family cover lost strict adjacency")

    containment_results: list[dict | None] = [None] * len(family_rows)
    with ThreadPoolExecutor(max_workers=arguments.workers) as executor:
        pending = {
            executor.submit(
                cap_containment, arguments.cap_binary, arguments.tail_seeds, row
            ): position
            for position, row in enumerate(family_rows)
        }
        for completed, future in enumerate(as_completed(pending), 1):
            containment_results[pending[future]] = future.result()
            if completed % 100 == 0 or completed == len(family_rows):
                print(
                    f"cap containment {completed}/{len(family_rows)}",
                    flush=True,
                )
    containments = [row for row in containment_results if row is not None]
    containment_failures = [row for row in containments if row["returncode"]]
    if arguments.containment_results is not None:
        with arguments.containment_results.open("w", encoding="utf-8") as stream:
            for row in containments:
                stream.write(json.dumps(row, sort_keys=True) + "\n")
    if containment_failures:
        raise RuntimeError(
            f"first family/cap containment failure: {containment_failures[0]}"
        )

    final_row = tail_rows[-1]
    cap_output = run_json(
        [
            str(arguments.cap_binary),
            "--cap-half-width",
            repr(CAP_HALF_WIDTH),
            "--family-seed-file",
            str(arguments.tail_seeds),
            "--family-seed-offset",
            str(final_row["seed_offset"]),
            "--family-half-width",
            repr(final_row["half_width"]),
            "--family-radius-scale",
            repr(ENDPOINT_RADIUS_SCALE),
        ]
    )
    for gate in (
        "existing_fold_full_state_contained",
        "existing_fold_in_fixed_family_full_state",
    ):
        if not cap_output[gate]:
            raise RuntimeError(f"fold identification gate failed: {gate}")
    endpoint_output = run_json(
        [
            str(arguments.fixed_binary),
            "--seed-file",
            str(arguments.tail_seeds),
            "--seed-offset",
            str(final_row["seed_offset"]),
            "--half-width",
            repr(final_row["half_width"]),
            "--radius-scale",
            repr(ENDPOINT_RADIUS_SCALE),
        ]
    )

    cross_bridge = main_to_tail_bridge(
        arguments.fixed_binary,
        main_rows,
        arguments.main_seeds,
        tail_rows[0],
        arguments.tail_seeds,
    )
    summary = {
        "status": "PASS-FIRST-FOLD-CLOSURE",
        "negative_sign_box_count": len(sign_rows),
        "negative_sign_parameter_end": sign_rows[-1][0]["parameter_interval"][1],
        "maximum_negative_energy_derivative_upper": {
            "value": sign_maximum[0],
            "index": sign_maximum[1],
        },
        "cap_family_box_count": len(family_rows),
        "cap_family_parameter_start": family_rows[0]["parameter_interval"][0],
        "sign_to_cap_overlap": SIGN_UNTIL_U
        - family_rows[0]["parameter_interval"][0],
        "minimum_family_cap_full_state_margin": min(
            row["minimum_full_state_margin"] for row in containments
        ),
        "main_cover_to_sign_tail_identification": cross_bridge,
        "family_to_augmented_cap_identification": {
            "status": "PASS-ALL-BASE-AND-TANGENT-UNIQUENESS-BOXES-CONTAINED",
            "box_count": len(containments),
        },
        "existing_fold_identification": {
            "status": "PASS-FULL-STATE-COMMON-ROOT",
            "fold_to_cap_margin": cap_output["existing_fold_cap_margin"],
            "fold_to_final_fixed_family_margin": cap_output[
                "existing_fold_fixed_family_margin"
            ],
            "fold_parameter_to_final_interval_margin": cap_output[
                "existing_fold_fixed_parameter_margin"
            ],
            "fixed_endpoint_radius_scale": ENDPOINT_RADIUS_SCALE,
            "fixed_endpoint_krawczyk_ratio": endpoint_output[
                "krawczyk_ratio"
            ],
            "fixed_endpoint_contraction_ratio": endpoint_output[
                "contraction_ratio"
            ],
            "fixed_endpoint_tangent_krawczyk_ratio": endpoint_output[
                "tangent_krawczyk_ratio"
            ],
        },
        "mixed_cap": cap_output,
        "hashes": {
            "main_manifest": sha256(arguments.main_manifest),
            "main_seeds": sha256(arguments.main_seeds),
            "tail_manifest": sha256(arguments.tail_manifest),
            "tail_seeds": sha256(arguments.tail_seeds),
            "fixed_probe_source": sha256(HERE / "fixed_source_cover_probe.cpp"),
            "cap_probe_source": sha256(HERE / "mixed_fold_cap_probe.cpp"),
        },
        "elapsed_seconds": time.monotonic() - started,
    }
    rendered = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if arguments.summary is not None:
        arguments.summary.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
