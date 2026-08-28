#!/usr/bin/env python3
"""Deterministically refine failed rows of the spiral extension cover.

The interval validator, rather than this script, decides proof status.  This
script only shrinks the parameter width of base rows named in a checked-in
plan and inserts linearly interpolated preconditioner seeds wherever the
resulting adjacent parameter intervals would otherwise have too little
overlap.  Every emitted row and every emitted adjacency must subsequently be
revalidated by ``validate_spiral_extension_cover.py``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


STATE_DIMENSION = 5


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def record_value_count(segments: int) -> int:
    return 3 + 2 * (segments + 1) * STATE_DIMENSION


def load_seed_blocks(path: Path, rows: list[dict], segments: int) -> list[list[float]]:
    value_count = record_value_count(segments)
    result = []
    with path.open("rb") as handle:
        for row in rows:
            handle.seek(int(row["seed_offset"]))
            values = []
            for _ in range(value_count):
                line = handle.readline()
                if not line:
                    raise RuntimeError(
                        f"truncated seed block at base row {row['index']}"
                    )
                values.append(float(line))
            result.append(values)
    return result


def interpolate(first: list[float], second: list[float], fraction: float) -> list[float]:
    complement = 1.0 - fraction
    return [complement * left + fraction * right for left, right in zip(first, second)]


def enough_overlap(
    centres: list[float], widths: list[float], overlap_fraction: float
) -> bool:
    return all(
        widths[index]
        + widths[index + 1]
        - abs(centres[index + 1] - centres[index])
        >= overlap_fraction * min(widths[index], widths[index + 1])
        for index in range(len(centres) - 1)
    )


def insertion_count(
    first: dict, second: dict, first_width: float, second_width: float,
    overlap_fraction: float, maximum_insertions: int,
) -> int:
    if first["chart"] != second["chart"]:
        return 0
    left = float(first["parameter_centre"])
    right = float(second["parameter_centre"])
    insert_width = min(first_width, second_width)
    for count in range(maximum_insertions + 1):
        fractions = [index / (count + 1) for index in range(count + 2)]
        centres = [left + fraction * (right - left) for fraction in fractions]
        widths = [first_width] + [insert_width] * count + [second_width]
        if enough_overlap(centres, widths, overlap_fraction):
            return count
    raise RuntimeError(
        f"more than {maximum_insertions} insertions required between base "
        f"rows {first['index']} and {second['index']}"
    )


def source_fields(values: list[float], segments: int) -> dict:
    centre_start = 3
    source_u = values[centre_start]
    source_v = values[centre_start + 2]
    flight_time = values[centre_start + 4]
    return {
        "source_U": source_u,
        "source_V": source_v,
        "source_radius": math.hypot(source_u, source_v),
        "flight_time": flight_time,
    }


def make_record(
    template: dict,
    values: list[float],
    half_width: float,
    *,
    base_index: int | None,
    left_base_index: int | None = None,
    right_base_index: int | None = None,
    interpolation_fraction: float | None = None,
) -> dict:
    record = {
        "group": template["group"],
        "region": template["region"],
        "chart": template["chart"],
        "seed_tangent_kind": template.get("seed_tangent_kind", "active"),
        "segments": int(template["segments"]),
        "half_width": half_width,
        "radius_scale": float(template.get("radius_scale", 1.0)),
        "values": values,
        "base_index": base_index,
        "left_base_index": left_base_index,
        "right_base_index": right_base_index,
        "interpolation_fraction": interpolation_fraction,
    }
    record.update(source_fields(values, record["segments"]))
    if record["chart"] == "u":
        record["parameter_centre"] = record["source_U"]
    elif record["chart"] == "v":
        record["parameter_centre"] = record["source_V"]
    else:
        record["parameter_centre"] = record["source_radius"]
    return record


def build_records(
    base_rows: list[dict], base_seeds: list[list[float]], plan: dict
) -> list[dict]:
    factor = float(plan["failed_width_factor"])
    overlap_fraction = float(plan["minimum_overlap_fraction"])
    maximum_insertions = int(plan.get("maximum_insertions_per_base_gap", 8))
    failed = {int(index) for index in plan["refine_base_indices"]}
    strict_failures = {
        int(index) for index in plan.get("strict_base_failure_indices", [])
    }
    margin_refinements = {
        int(index) for index in plan.get("margin_refinement_indices", [])
    }
    if not 0.0 < factor < 1.0:
        raise RuntimeError("failed_width_factor must lie strictly between zero and one")
    if not 0.0 < overlap_fraction < 1.0:
        raise RuntimeError("minimum_overlap_fraction must lie strictly between zero and one")
    expected_indices = set(range(len(base_rows)))
    if {int(row["index"]) for row in base_rows} != expected_indices:
        raise RuntimeError("base manifest indices are not contiguous")
    if not failed <= expected_indices:
        raise RuntimeError("refinement plan names a nonexistent base row")
    if strict_failures or margin_refinements:
        if strict_failures & margin_refinements:
            raise RuntimeError("failure and margin refinement sets overlap")
        if strict_failures | margin_refinements != failed:
            raise RuntimeError("refinement plan subsets do not form the full set")
    if 0 in failed or len(base_rows) - 1 in failed:
        raise RuntimeError("endpoint refinement requires an explicit endpoint audit")

    widths = [
        float(row["half_width"]) * (factor if row["index"] in failed else 1.0)
        for row in base_rows
    ]
    records: list[dict] = []
    for index, (row, seed) in enumerate(zip(base_rows, base_seeds)):
        records.append(
            make_record(row, seed, widths[index], base_index=int(row["index"]))
        )
        if index + 1 == len(base_rows):
            continue
        following = base_rows[index + 1]
        count = insertion_count(
            row,
            following,
            widths[index],
            widths[index + 1],
            overlap_fraction,
            maximum_insertions,
        )
        for insertion in range(1, count + 1):
            fraction = insertion / (count + 1)
            # Same-chart gaps occur inside a group.  At a region boundary,
            # inherit the nearer region name solely as descriptive metadata.
            template = row if fraction <= 0.5 else following
            records.append(
                make_record(
                    template,
                    interpolate(seed, base_seeds[index + 1], fraction),
                    min(widths[index], widths[index + 1]),
                    base_index=None,
                    left_base_index=int(row["index"]),
                    right_base_index=int(following["index"]),
                    interpolation_fraction=fraction,
                )
            )
    return records


def write_outputs(records: list[dict], output_dir: Path, plan: dict, plan_path: Path):
    if output_dir.exists() and any(output_dir.iterdir()):
        raise RuntimeError("output directory must be absent or empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    seed_path = output_dir / "spiral_extension_seeds.txt"
    manifest_path = output_dir / "spiral_extension_boxes.jsonl"
    summary_path = output_dir / "spiral_extension_centres_summary.json"

    offsets = []
    with seed_path.open("wb") as handle:
        for record in records:
            offsets.append(handle.tell())
            handle.write(
                "".join(f"{value:+.17e}\n" for value in record["values"]).encode(
                    "ascii"
                )
            )

    manifest = []
    previous = None
    with manifest_path.open("w") as handle:
        for index, (record, offset) in enumerate(zip(records, offsets)):
            centre = float(record["parameter_centre"])
            width = float(record["half_width"])
            lower = centre - width
            upper = centre + width
            overlap = None
            if previous is not None and previous[0] == record["chart"]:
                overlap = min(upper, previous[2]) - max(lower, previous[1])
                required = float(plan["minimum_overlap_fraction"]) * min(
                    width, previous[3]
                )
                if overlap < required:
                    raise RuntimeError(
                        f"insufficient parameter overlap at refined row {index}: "
                        f"{overlap} < {required}"
                    )
            row = {
                key: record[key]
                for key in [
                    "group",
                    "region",
                    "chart",
                    "seed_tangent_kind",
                    "segments",
                    "parameter_centre",
                    "half_width",
                    "radius_scale",
                    "source_U",
                    "source_V",
                    "source_radius",
                    "flight_time",
                    "base_index",
                    "left_base_index",
                    "right_base_index",
                    "interpolation_fraction",
                ]
            }
            row.update(
                {
                    "index": index,
                    "parameter_lower": lower,
                    "parameter_upper": upper,
                    "overlap_with_previous": overlap,
                    "seed_offset": offset,
                }
            )
            manifest.append(row)
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            previous = (record["chart"], lower, upper, width)

    groups = []
    for name in dict.fromkeys(row["group"] for row in manifest):
        group_rows = [row for row in manifest if row["group"] == name]
        groups.append(
            {
                "name": name,
                "chart": group_rows[0]["chart"],
                "first_index": group_rows[0]["index"],
                "last_index": group_rows[-1]["index"],
                "box_count": len(group_rows),
                "parameter_range": [
                    group_rows[0]["parameter_centre"],
                    group_rows[-1]["parameter_centre"],
                ],
            }
        )
    summary = {
        "status": "REFINED-CENTRES-ONLY-NOT-INTERVAL-VALIDATED",
        "segments": manifest[0]["segments"],
        "base_box_count": int(plan["base_box_count"]),
        "box_count": len(manifest),
        "inserted_box_count": sum(row["base_index"] is None for row in manifest),
        "shrunk_base_box_count": len(plan["refine_base_indices"]),
        "groups": groups,
        "first_source": {
            "U": manifest[0]["source_U"],
            "V": manifest[0]["source_V"],
            "radius": manifest[0]["source_radius"],
        },
        "last_source": {
            "U": manifest[-1]["source_U"],
            "V": manifest[-1]["source_V"],
            "radius": manifest[-1]["source_radius"],
        },
        "refinement_plan": plan_path.name,
        "refinement_plan_sha256": sha256(plan_path),
        "seed_file": seed_path.name,
        "manifest_file": manifest_path.name,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = args.base_dir / "spiral_extension_boxes.jsonl"
    seed_path = args.base_dir / "spiral_extension_seeds.txt"
    summary_path = args.base_dir / "spiral_extension_centres_summary.json"
    plan = json.loads(args.plan.read_text())
    if sha256(manifest_path) != plan["base_manifest_sha256"]:
        raise RuntimeError("base manifest does not match the refinement plan")
    if sha256(seed_path) != plan["base_seeds_sha256"]:
        raise RuntimeError("base seeds do not match the refinement plan")
    if sha256(summary_path) != plan["base_summary_sha256"]:
        raise RuntimeError("base summary does not match the refinement plan")
    base_rows = read_jsonl(manifest_path)
    if len(base_rows) != int(plan["base_box_count"]):
        raise RuntimeError("base box count does not match the refinement plan")
    segment_counts = {int(row["segments"]) for row in base_rows}
    if len(segment_counts) != 1:
        raise RuntimeError("base manifest mixes shooting dimensions")
    segments = segment_counts.pop()
    seeds = load_seed_blocks(seed_path, base_rows, segments)
    records = build_records(base_rows, seeds, plan)
    write_outputs(records, args.output_dir, plan, args.plan)


if __name__ == "__main__":
    main()
