#!/usr/bin/env python3
"""Generate floating centres for the finite-collar-to-annulus seam cover.

The output consists only of preconditioner data.  No record acquires proof
status until every row and every adjacent bridge has passed the CAPD/FILIB
validator.  The generator writes all large products to a caller-selected
directory so a clean replay leaves the repository source-only.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import time

import numpy as np
from scipy.integrate import solve_bvp

from generate_full_cover import INNER_U
from numerical_bvp import BranchProblem, degree_seven_graph


FOLD_U = 0.04152701249
FOLD_V = 0.10250373810
SEAM_RADIUS = 2.4e-4
SEAM_V_CENTRE = 0.0002332590482087833
DEFAULT_SEGMENTS = 108


def grid(start: float, stop: float, maximum_stride: float) -> list[float]:
    steps = max(1, int(math.ceil(abs(stop - start) / maximum_stride)))
    return [float(value) for value in np.linspace(start, stop, steps + 1)]


def centre_array(solution, segments: int) -> np.ndarray:
    nodes = np.linspace(0.0, 1.0, segments + 1)
    values = solution.sol(nodes)
    return np.vstack(
        [values, np.full(segments + 1, float(solution.p[-1]))]
    ).T


def fixed_v(problem: BranchProblem, value: float, guess):
    values = guess.sol(problem.mesh)

    def boundary(left, right, parameters):
        return np.asarray(
            [
                left[1],
                left[3],
                left[0] - parameters[0],
                left[2] - value,
                -1.0 / right[0] - problem.section_e,
                problem.target(right),
            ]
        )

    solution = solve_bvp(
        problem.scaled_field,
        boundary,
        problem.mesh,
        values,
        p=np.asarray([guess.y[0, 0], guess.p[-1]], dtype=float),
        tol=problem.tolerance,
        max_nodes=problem.max_nodes,
    )
    if not solution.success:
        raise RuntimeError(f"fixed-V solve failed at {value}: {solution.message}")
    return solution


def fixed_radius(problem: BranchProblem, radius: float, guess):
    values = guess.sol(problem.mesh)

    def boundary(left, right, parameters):
        return np.asarray(
            [
                left[1],
                left[3],
                math.hypot(left[0], left[2]) - radius,
                -1.0 / right[0] - problem.section_e,
                problem.target(right),
            ]
        )

    solution = solve_bvp(
        problem.scaled_field,
        boundary,
        problem.mesh,
        values,
        p=np.asarray([guess.p[-1]], dtype=float),
        tol=problem.tolerance,
        max_nodes=problem.max_nodes,
    )
    if not solution.success:
        raise RuntimeError(
            f"fixed-radius solve failed at {radius}: {solution.message}"
        )
    return solution


def march_u(problem: BranchProblem, current, destination: float, step=2e-4):
    start = float(current.y[0, 0])
    for value in grid(start, destination, step)[1:]:
        current = problem.fixed_u_event(
            value,
            current,
            parameters=np.asarray([current.y[2, 0], current.p[-1]]),
        )
    return current


def march_v(problem: BranchProblem, current, destination: float, step=2e-4):
    start = float(current.y[2, 0])
    for value in grid(start, destination, step)[1:]:
        current = fixed_v(problem, value, current)
    return current


def reconstruct_intermediate_endpoint(problem: BranchProblem):
    fixed_time = problem.bootstrap_fixed_time(FOLD_U)
    current = problem.fixed_u_event(
        FOLD_U,
        fixed_time,
        parameters=np.asarray([FOLD_V, 15.0]),
    )
    current = march_v(problem, current, 0.0)
    return march_u(problem, current, INNER_U)


def append_group(
    records: list[dict],
    problem: BranchProblem,
    current,
    *,
    group: str,
    chart: str,
    pieces: list[tuple[str, float, float, float]],
    segments: int,
    started: float,
):
    """Append one regular chart group.

    Each piece is ``(region, stop, half_width, maximum_stride)``.  A shared
    piece endpoint is stored only once, with the width of the incoming piece;
    the next centre has strict overlap with it.
    """

    group_records: list[dict] = []
    active = float(current.y[0, 0] if chart == "u" else current.y[2, 0])
    for piece_index, (region, stop, half_width, maximum_stride) in enumerate(pieces):
        values = grid(active, stop, maximum_stride)
        if piece_index:
            values = values[1:]
        for value_index, value in enumerate(values):
            if group_records or value_index:
                if chart == "u":
                    current = problem.fixed_u_event(
                        value,
                        current,
                        parameters=np.asarray([current.y[2, 0], current.p[-1]]),
                    )
                else:
                    current = fixed_v(problem, value, current)
            group_records.append(
                {
                    "group": group,
                    "region": region,
                    "chart": chart,
                    "half_width": half_width,
                    "radius_scale": 1.0,
                    "solution": current,
                    "centre": centre_array(current, segments),
                }
            )
            if (len(records) + len(group_records)) % 250 == 0:
                print(
                    f"centres {len(records) + len(group_records)} "
                    f"group={group} elapsed={time.monotonic() - started:.1f}s",
                    flush=True,
                )
        active = stop

    arrays = np.asarray([record["centre"] for record in group_records])
    parameters = np.asarray(
        [
            record["centre"][0, 0]
            if chart == "u"
            else record["centre"][0, 2]
            for record in group_records
        ]
    )
    derivatives = np.gradient(arrays, parameters, axis=0, edge_order=2)
    for record, derivative_parameter in zip(group_records, derivatives):
        record["derivative_parameter"] = derivative_parameter
    records.extend(group_records)
    return current


def add_radial_seam_record(
    records: list[dict],
    problem: BranchProblem,
    current,
    segments: int,
):
    current = fixed_radius(problem, SEAM_RADIUS, current)
    difference = 2e-8
    minus = fixed_radius(problem, SEAM_RADIUS - difference, current)
    plus = fixed_radius(problem, SEAM_RADIUS + difference, current)
    derivative_r = (
        centre_array(plus, segments) - centre_array(minus, segments)
    ) / (2 * difference)
    records.append(
        {
            "group": "fixed-radial-seam",
            "region": "fixed-radial-seam",
            "chart": "radius",
            "half_width": 1e-12,
            "radius_scale": 1.0,
            "solution": current,
            "centre": centre_array(current, segments),
            "derivative_parameter": derivative_r,
        }
    )
    return current


def source_parameter(record: dict) -> float:
    centre = record["centre"]
    if record["chart"] == "u":
        return float(centre[0, 0])
    if record["chart"] == "v":
        return float(centre[0, 2])
    return math.hypot(float(centre[0, 0]), float(centre[0, 2]))


def write_outputs(records: list[dict], output_dir: Path, segments: int):
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
            array = record["centre"]
            values = [array[0, 2], array[0, 0], array[0, 4]]
            values.extend(array.ravel())
            values.extend(record["derivative_parameter"].ravel())
            handle.write(
                "".join(f"{float(value):+.17e}\n" for value in values).encode(
                    "ascii"
                )
            )

    previous = None
    manifest = []
    with manifest_path.open("w") as handle:
        for index, (record, offset) in enumerate(zip(records, offsets)):
            parameter = source_parameter(record)
            lower = parameter - record["half_width"]
            upper = parameter + record["half_width"]
            overlap = None
            if previous is not None and previous[0] == record["chart"]:
                overlap = min(upper, previous[2]) - max(lower, previous[1])
                if not overlap > 0:
                    raise RuntimeError(f"nonpositive parameter overlap at row {index}")
            centre = record["centre"]
            row = {
                "index": index,
                "group": record["group"],
                "region": record["region"],
                "chart": record["chart"],
                "seed_tangent_kind": "active",
                "segments": segments,
                "parameter_centre": parameter,
                "half_width": record["half_width"],
                "radius_scale": record["radius_scale"],
                "parameter_lower": lower,
                "parameter_upper": upper,
                "overlap_with_previous": overlap,
                "seed_offset": offset,
                "source_U": float(centre[0, 0]),
                "source_V": float(centre[0, 2]),
                "source_radius": math.hypot(
                    float(centre[0, 0]), float(centre[0, 2])
                ),
                "flight_time": float(centre[0, 4]),
            }
            manifest.append(row)
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            previous = (record["chart"], lower, upper)

    groups = []
    for name in dict.fromkeys(row["group"] for row in manifest):
        rows = [row for row in manifest if row["group"] == name]
        groups.append(
            {
                "name": name,
                "chart": rows[0]["chart"],
                "first_index": rows[0]["index"],
                "last_index": rows[-1]["index"],
                "box_count": len(rows),
                "parameter_range": [
                    rows[0]["parameter_centre"],
                    rows[-1]["parameter_centre"],
                ],
            }
        )
    summary = {
        "status": "CENTRES-ONLY-NOT-INTERVAL-VALIDATED",
        "segments": segments,
        "box_count": len(manifest),
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
        "seed_file": seed_path.name,
        "manifest_file": manifest_path.name,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--segments", type=int, default=DEFAULT_SEGMENTS)
    args = parser.parse_args()
    if args.segments < 36 or args.segments % 12:
        raise RuntimeError("segments must be a multiple of 12 and at least 36")

    _graph, h7, h7_gradient = degree_seven_graph()
    problem = BranchProblem(h7, h7_gradient, 0.0575, 2e-10, 25000)
    started = time.monotonic()
    current = reconstruct_intermediate_endpoint(problem)
    records: list[dict] = []

    current = append_group(
        records,
        problem,
        current,
        group="quadrant-IV-u-chart",
        chart="u",
        pieces=[("quadrant-IV-u-chart", 0.0, 4e-6, 6e-6)],
        segments=args.segments,
        started=started,
    )
    current = append_group(
        records,
        problem,
        current,
        group="quadrant-III-v-chart",
        chart="v",
        pieces=[
            ("quadrant-III-v-chart-outer", -0.002, 3e-6, 4.5e-6),
            ("quadrant-III-v-chart-inner", 0.0, 1e-6, 1.5e-6),
        ],
        segments=args.segments,
        started=started,
    )
    current = append_group(
        records,
        problem,
        current,
        group="quadrant-II-u-chart",
        chart="u",
        pieces=[
            ("quadrant-II-u-chart-outer", -0.0005, 5e-7, 7.5e-7),
            ("quadrant-II-u-chart-inner", 0.0, 2e-7, 3e-7),
        ],
        segments=args.segments,
        started=started,
    )
    current = append_group(
        records,
        problem,
        current,
        group="quadrant-I-v-chart-to-seam",
        chart="v",
        pieces=[
            ("quadrant-I-v-chart-to-seam", SEAM_V_CENTRE, 2e-7, 3e-7)
        ],
        segments=args.segments,
        started=started,
    )
    add_radial_seam_record(records, problem, current, args.segments)
    write_outputs(records, args.output_dir, args.segments)


if __name__ == "__main__":
    main()
