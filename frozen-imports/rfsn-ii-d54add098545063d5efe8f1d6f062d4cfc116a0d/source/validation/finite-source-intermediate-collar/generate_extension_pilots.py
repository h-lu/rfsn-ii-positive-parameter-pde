#!/usr/bin/env python3
"""Generate axis-crossing pilot seeds for the inward spiral extension.

The floating-point solves only provide Krawczyk centres.  They are not proof
data.  By default this script resumes from the optional U-chart checkpoint;
``--fresh`` reconstructs the already covered arc from the fold.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import solve_bvp

from generate_full_cover import (
    INNER_U,
    load_checkpoint,
    reconstruct_solution,
)
from numerical_bvp import BranchProblem, degree_seven_graph


HERE = Path(__file__).resolve().parent
SEGMENTS = 36


def centre_array(solution):
    nodes = np.linspace(0.0, 1.0, SEGMENTS + 1)
    values = solution.sol(nodes)
    return np.vstack([values, np.full(SEGMENTS + 1, float(solution.p[-1]))]).T


def fixed_v(problem, value, guess):
    """Fixed-V solve with a chart-independent parameter guess."""
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
        tol=2e-10,
        max_nodes=25000,
    )
    if not solution.success:
        raise RuntimeError(f"fixed-V solve failed at {value}: {solution.message}")
    return solution


def march_u(problem, current, destination, maximum_step=2e-4):
    start = float(current.y[0, 0])
    count = max(1, int(math.ceil(abs(destination - start) / maximum_step)))
    for value in np.linspace(start, destination, count + 1)[1:]:
        current = problem.fixed_u_event(
            float(value),
            current,
            parameters=np.asarray([current.y[2, 0], current.p[-1]]),
        )
    return current


def march_v(problem, current, destination, maximum_step=2e-4):
    start = float(current.y[2, 0])
    count = max(1, int(math.ceil(abs(destination - start) / maximum_step)))
    for value in np.linspace(start, destination, count + 1)[1:]:
        current = fixed_v(problem, float(value), current)
    return current


def derivative_at_u(problem, solution, difference=2e-7):
    u = float(solution.y[0, 0])
    minus = problem.fixed_u_event(
        u - difference,
        solution,
        parameters=np.asarray([solution.y[2, 0], solution.p[-1]]),
    )
    plus = problem.fixed_u_event(
        u + difference,
        solution,
        parameters=np.asarray([solution.y[2, 0], solution.p[-1]]),
    )
    derivative_u = (centre_array(plus) - centre_array(minus)) / (2 * difference)
    dv_du = derivative_u[0, 2]
    if abs(dv_du) < 1e-3:
        raise RuntimeError("axis pilot has singular U-to-V derivative conversion")
    return derivative_u / dv_du


def derivative_at_v(problem, solution, difference=2e-7):
    v = float(solution.y[2, 0])
    minus = fixed_v(problem, v - difference, solution)
    plus = fixed_v(problem, v + difference, solution)
    return (centre_array(plus) - centre_array(minus)) / (2 * difference)


def write_seed(handle, solution, derivative_v):
    offset = handle.tell()
    array = centre_array(solution)
    values = [array[0, 2], array[0, 0], array[0, 4]]
    values.extend(array.ravel())
    values.extend(derivative_v.ravel())
    handle.write("".join(f"{float(value):+.17e}\n" for value in values).encode("ascii"))
    return offset


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fresh", action="store_true")
    parser.add_argument("--segments", type=int, default=36)
    parser.add_argument(
        "--checkpoint", type=Path, default=HERE / "u_centres_checkpoint.npz"
    )
    parser.add_argument(
        "--seed-output", type=Path, default=HERE / "extension_pilot_seeds.txt"
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=HERE / "extension_pilots.jsonl",
    )
    args = parser.parse_args()

    global SEGMENTS
    SEGMENTS = args.segments

    _graph, h7, h7_gradient = degree_seven_graph()
    problem = BranchProblem(h7, h7_gradient, 0.0575, 2e-10, 25000)
    if args.checkpoint.exists() and not args.fresh:
        current = reconstruct_solution(problem, load_checkpoint(args.checkpoint)[-1])
    else:
        fixed_time = problem.bootstrap_fixed_time(0.04152701249)
        current = problem.fixed_u_event(
            0.04152701249,
            fixed_time,
            parameters=np.asarray([0.10250373810, 15.0]),
        )
        current = march_v(problem, current, 0.0)
        current = march_u(problem, current, INNER_U)

    first_u_axis = march_u(problem, current, 0.0)
    first_v_axis = march_v(problem, first_u_axis, 0.0)
    second_u_axis = march_u(problem, first_v_axis, 0.0, maximum_step=5e-5)
    cases = [
        ("first-u-axis", first_u_axis, derivative_at_u(problem, first_u_axis)),
        ("first-v-axis", first_v_axis, derivative_at_v(problem, first_v_axis)),
        ("annulus-u-axis", second_u_axis, derivative_at_u(problem, second_u_axis)),
    ]
    with args.seed_output.open("wb") as seed_handle, args.manifest_output.open("w") as manifest:
        for index, (name, solution, derivative_v) in enumerate(cases):
            offset = write_seed(seed_handle, solution, derivative_v)
            u = float(solution.y[0, 0])
            v = float(solution.y[2, 0])
            manifest.write(
                json.dumps(
                    {
                        "index": index,
                        "name": name,
                        "seed_offset": offset,
                        "source_U": u,
                        "source_V": v,
                        "source_radius": math.hypot(u, v),
                        "flight_time": float(solution.p[-1]),
                        "segments": SEGMENTS,
                    },
                    sort_keys=True,
                )
                + "\n"
            )
            print(
                f"{index} {name}: U={u:.17g} V={v:.17g} "
                f"R={math.hypot(u,v):.17g} T={solution.p[-1]:.17g}"
            )


if __name__ == "__main__":
    main()
