#!/usr/bin/env python3
"""Generate all numerical centres for the proposed V/U-chart cover.

The output is text seed data plus a JSON-lines work manifest.  It is not a
certificate until validate_full_cover.py has run every manifest row.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import time

import numpy as np


HERE = Path(__file__).resolve().parent
FOLD_U = 0.04152701249
FOLD_V = 0.10250373810
INNER_U = 0.023799818459857215
SEGMENTS = 36


def grid_descending(upper: float, lower: float, maximum_stride: float):
    steps = int(math.ceil((upper - lower) / maximum_stride))
    return list(np.linspace(upper, lower, steps + 1))


def v_worklist():
    regions = (
        ("outer_v", FOLD_V, 0.025, 2e-5, 3e-5),
        ("inner_v", 0.025, 0.01, 1e-5, 1.5e-5),
        ("zero_v", 0.01, 0.0, 5e-6, 7.5e-6),
    )
    work = []
    for name, upper, lower, half_width, stride in regions:
        for value in grid_descending(upper, lower, stride):
            if work and abs(value - work[-1][1]) < 1e-14:
                # At a change of mesh keep the wider transition box.  Taking
                # the smaller radius can leave the preceding coarse box and
                # the boundary box merely touching, with zero overlap.
                old_name, old_value, old_width = work[-1]
                work[-1] = (f"{old_name}+{name}", old_value, max(old_width, half_width))
            else:
                work.append((name, float(value), half_width))
    return work


def u_worklist(upper: float):
    return [
        ("negative_u", float(value), 5e-6)
        for value in grid_descending(upper, INNER_U, 7.5e-6)
    ]


def solve_fixed_v(problem, fixed_v: float, guess):
    from scipy.integrate import solve_bvp

    values = guess.sol(problem.mesh)

    def boundary(left, right, parameters):
        return np.asarray(
            [
                left[1],
                left[3],
                left[0] - parameters[0],
                left[2] - fixed_v,
                -1.0 / right[0] - problem.section_e,
                problem.target(right),
            ]
        )

    solution = solve_bvp(
        problem.scaled_field,
        boundary,
        problem.mesh,
        values,
        p=np.asarray([guess.p[0], guess.p[1]], dtype=float),
        tol=2e-10,
        max_nodes=25000,
    )
    if not solution.success:
        raise RuntimeError(f"fixed-V solve failed at {fixed_v}: {solution.message}")
    return solution


def centre_array(solution):
    nodes = np.linspace(0.0, 1.0, SEGMENTS + 1)
    values = solution.sol(nodes)
    return np.vstack([values, np.full(SEGMENTS + 1, float(solution.p[-1]))]).T


def finite_differences(arrays: np.ndarray, parameters: np.ndarray):
    if len(parameters) < 2:
        raise ValueError("at least two centres are required for a tangent seed")
    return np.gradient(
        arrays,
        parameters,
        axis=0,
        edge_order=2 if len(parameters) >= 3 else 1,
    )


def save_checkpoint(records, path: Path):
    np.savez(
        path,
        region=np.asarray([record["region"] for record in records]),
        chart=np.asarray([record["chart"] for record in records]),
        half_width=np.asarray([record["half_width"] for record in records]),
        source_v=np.asarray([record["source_v"] for record in records]),
        source_u=np.asarray([record["source_u"] for record in records]),
        time=np.asarray([record["time"] for record in records]),
        centre=np.asarray([record["centre"] for record in records]),
        derivative_v=np.asarray([record["derivative_v"] for record in records]),
    )


def load_checkpoint(path: Path):
    data = np.load(path)
    return [
        {
            "region": str(data["region"][index]),
            "chart": str(data["chart"][index]),
            "half_width": float(data["half_width"][index]),
            "source_v": float(data["source_v"][index]),
            "source_u": float(data["source_u"][index]),
            "time": float(data["time"][index]),
            "centre": data["centre"][index],
            "derivative_v": data["derivative_v"][index],
        }
        for index in range(len(data["source_v"]))
    ]


def reconstruct_solution(problem, record):
    from scipy.integrate import solve_bvp

    mesh = np.linspace(0.0, 1.0, SEGMENTS + 1)
    values = record["centre"][:, :4].T
    fixed_v = record["source_v"]

    def boundary(left, right, parameters):
        return np.asarray(
            [
                left[1],
                left[3],
                left[0] - parameters[0],
                left[2] - fixed_v,
                -1.0 / right[0] - problem.section_e,
                problem.target(right),
            ]
        )

    solution = solve_bvp(
        problem.scaled_field,
        boundary,
        mesh,
        values,
        p=np.asarray([record["source_u"], record["time"]]),
        tol=2e-10,
        max_nodes=25000,
    )
    if not solution.success:
        raise RuntimeError(f"checkpoint reconstruction failed: {solution.message}")
    return solution


def write_outputs(records, seed_path: Path, manifest_path: Path, summary_path: Path):
    offsets = []
    with seed_path.open("wb") as handle:
        for record in records:
            offsets.append(handle.tell())
            numbers = [record["source_v"], record["source_u"], record["time"]]
            numbers.extend(record["centre"].ravel())
            numbers.extend(record["derivative_v"].ravel())
            handle.write("".join(f"{float(value):+.17e}\n" for value in numbers).encode("ascii"))

    previous_by_chart = {}
    with manifest_path.open("w") as handle:
        for index, (record, offset) in enumerate(zip(records, offsets)):
            parameter = record["source_v"] if record["chart"] == "v" else record["source_u"]
            lower = parameter - record["half_width"]
            upper = parameter + record["half_width"]
            previous = previous_by_chart.get(record["chart"])
            overlap = (
                None
                if previous is None
                else min(upper, previous[1]) - max(lower, previous[0])
            )
            if overlap is not None and overlap <= 0:
                raise RuntimeError(f"nonpositive planned overlap at record {index}")
            row = {
                "index": index,
                "region": record["region"],
                "chart": record["chart"],
                "parameter_centre": parameter,
                "half_width": record["half_width"],
                "parameter_lower": lower,
                "parameter_upper": upper,
                "overlap_with_previous": overlap,
                "seed_offset": offset,
                "source_U": record["source_u"],
                "source_V": record["source_v"],
                "source_energy": -2 * record["source_u"] ** 3 / 3
                - 2 * record["source_u"] * record["source_v"],
                "source_radius": math.hypot(record["source_u"], record["source_v"]),
                "flight_time": record["time"],
            }
            handle.write(json.dumps(row, sort_keys=True) + "\n")
            previous_by_chart[record["chart"]] = (lower, upper, index)

    v_records = [record for record in records if record["chart"] == "v"]
    u_records = [record for record in records if record["chart"] == "u"]
    switch_v = v_records[-1]
    switch_u = u_records[0] if u_records else None
    switch_gap = (
        float(np.max(np.abs(switch_v["centre"] - switch_u["centre"])))
        if switch_u is not None
        else None
    )
    summary = {
        "status": "CENTRES-GENERATED-NOT-INTERVAL-VALIDATED",
        "segments": SEGMENTS,
        "record_count": len(records),
        "v_record_count": len(v_records),
        "u_record_count": len(u_records),
        "outer_source": {"U": v_records[0]["source_u"], "V": v_records[0]["source_v"]},
        "chart_switch": (
            {
                "U": switch_v["source_u"],
                "V": switch_v["source_v"],
                "floating_node_sup_gap": switch_gap,
            }
            if switch_u is not None
            else None
        ),
        "inner_source": (
            {"U": u_records[-1]["source_u"], "V": u_records[-1]["source_v"]}
            if u_records
            else None
        ),
        "seed_file": seed_path.name,
        "manifest_file": manifest_path.name,
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, help="debug: truncate each chart")
    parser.add_argument("--seed-output", type=Path, default=HERE / "cover_seeds.txt")
    parser.add_argument("--manifest-output", type=Path, default=HERE / "cover_boxes.jsonl")
    parser.add_argument("--summary-output", type=Path, default=HERE / "cover_centres_summary.json")
    parser.add_argument("--v-checkpoint", type=Path, default=HERE / "v_centres_checkpoint.npz")
    parser.add_argument("--u-checkpoint", type=Path, default=HERE / "u_centres_checkpoint.npz")
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()

    from numerical_bvp import BranchProblem, degree_seven_graph

    _graph, h7, h7_gradient = degree_seven_graph()
    problem = BranchProblem(h7, h7_gradient, 0.0575, 2e-10, 25000)
    started = time.monotonic()
    use_v_checkpoint = args.v_checkpoint.exists() and not args.fresh and not args.limit
    if use_v_checkpoint:
        v_records = load_checkpoint(args.v_checkpoint)
        current = reconstruct_solution(problem, v_records[-1])
        print(f"loaded {len(v_records)} V centres from checkpoint", flush=True)
    else:
        fixed_time = problem.bootstrap_fixed_time(FOLD_U)
        current = problem.fixed_u_event(
            FOLD_U, fixed_time, parameters=np.asarray([FOLD_V, 15.0])
        )
        v_jobs = v_worklist()
        if args.limit:
            v_jobs = v_jobs[: args.limit]
        v_records = []
        for index, (region, value, half_width) in enumerate(v_jobs):
            if index:
                current = solve_fixed_v(problem, value, current)
            array = centre_array(current)
            v_records.append(
                {
                    "region": region,
                    "chart": "v",
                    "half_width": half_width,
                    "source_v": float(array[0, 2]),
                    "source_u": float(array[0, 0]),
                    "time": float(array[0, 4]),
                    "centre": array,
                }
            )
            if (index + 1) % 100 == 0:
                print(
                    f"v centres {index + 1}/{len(v_jobs)} "
                    f"elapsed={time.monotonic() - started:.1f}s",
                    flush=True,
                )
        v_arrays = np.asarray([record["centre"] for record in v_records])
        v_parameters = np.asarray([record["source_v"] for record in v_records])
        v_derivatives = finite_differences(v_arrays, v_parameters)
        for record, derivative in zip(v_records, v_derivatives):
            record["derivative_v"] = derivative
        if not args.limit:
            save_checkpoint(v_records, args.v_checkpoint)
            print(f"saved V checkpoint: {args.v_checkpoint}", flush=True)

    records = v_records
    if not args.limit:
        if args.u_checkpoint.exists() and not args.fresh:
            u_records = load_checkpoint(args.u_checkpoint)
            print(f"loaded {len(u_records)} U centres from checkpoint", flush=True)
        else:
            u_jobs = u_worklist(float(current.y[0, 0]))
            u_records = []
            for index, (region, value, half_width) in enumerate(u_jobs):
                if index:
                    current = problem.fixed_u_event(
                        value,
                        current,
                        parameters=np.asarray([current.y[2, 0], current.p[-1]]),
                    )
                array = centre_array(current)
                u_records.append(
                    {
                        "region": region,
                        "chart": "u",
                        "half_width": half_width,
                        "source_v": float(array[0, 2]),
                        "source_u": float(array[0, 0]),
                        "time": float(array[0, 4]),
                        "centre": array,
                    }
                )
                if (index + 1) % 100 == 0:
                    print(
                        f"u centres {index + 1}/{len(u_jobs)} "
                        f"elapsed={time.monotonic() - started:.1f}s",
                        flush=True,
                    )
            u_arrays = np.asarray([record["centre"] for record in u_records])
            u_parameters = np.asarray([record["source_u"] for record in u_records])
            derivatives_u = finite_differences(u_arrays, u_parameters)
            for record, derivative_u in zip(u_records, derivatives_u):
                dv_du = derivative_u[0, 2]
                if abs(dv_du) < 1e-3:
                    raise RuntimeError("u chart derivative reconstruction is singular")
                record["derivative_v"] = derivative_u / dv_du
            save_checkpoint(u_records, args.u_checkpoint)
            print(f"saved U checkpoint: {args.u_checkpoint}", flush=True)
        records = v_records + u_records

    write_outputs(records, args.seed_output, args.manifest_output, args.summary_output)


if __name__ == "__main__":
    main()
