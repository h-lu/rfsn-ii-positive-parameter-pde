#!/usr/bin/env python3
"""Generate floating centres for the fixed-T=15 c0-to-fold cover.

The emitted centres and finite differences are preconditioner data only.
All proof claims are made by the interval replay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time

import numpy as np
from scipy.integrate import solve_bvp


HERE = Path(__file__).resolve().parent
UPSTREAM = HERE.parent / "finite-source-intermediate-collar"
sys.path.insert(0, str(UPSTREAM))

from numerical_bvp import core, degree_seven_graph, gamma0  # noqa: E402


FOLD_U = 0.041527012490323562
FOLD_U_INTERVAL = (0.041527012176079285, 0.041527012805834346)
FINAL_TIME = 15.0
SEGMENTS = 30
SWITCH_NODE = 4


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def compact(raw: np.ndarray) -> np.ndarray:
    """Map (...,4) raw states to (e,p,d,omega)."""
    raw = np.asarray(raw, dtype=float)
    u, p_raw, v, q_raw = np.moveaxis(raw, -1, 0)
    e = -1.0 / u
    e32 = e**1.5
    return np.stack(
        [
            e,
            p_raw * e32,
            q_raw * e32 + 2.0 / np.sqrt(3.0),
            1.0 + v * e**2,
        ],
        axis=-1,
    )


def mixed_nodes(solution) -> np.ndarray:
    times = np.linspace(0.0, FINAL_TIME, SEGMENTS + 1)
    raw = solution.sol(times).T
    result = raw.copy()
    result[SWITCH_NODE:] = compact(raw[SWITCH_NODE:])
    return result


def scheduled_half_width(source_u: float, width_scale: float) -> float:
    if source_u < 0.012:
        return width_scale * 3.1e-6
    if source_u < 0.025:
        return width_scale * 2.2e-6
    if source_u < 0.035:
        return width_scale * 1.45e-6
    return width_scale * 7e-7


def worklist(width_scale: float, final_half_width: float,
             overlap_fraction: float) -> list[tuple[float, float]]:
    tail_width = scheduled_half_width(FOLD_U, width_scale)
    if not (0.0 < final_half_width < tail_width):
        raise ValueError("final half width must lie below the tail width")
    if not (0.0 < overlap_fraction < 1.0):
        raise ValueError("overlap fraction must lie in (0,1)")

    # Build a geometrically graded endpoint cap backwards from the exact
    # floating fold centre.  Consecutive intervals overlap by one quarter of
    # the sum of their half widths.
    tail = [(FOLD_U, final_half_width)]
    next_centre, next_width = tail[0]
    while next_width < tail_width:
        previous_width = min(tail_width, 2.0 * next_width)
        previous_centre = next_centre - 0.8 * (
            previous_width + next_width
        )
        tail.append((previous_centre, previous_width))
        next_centre, next_width = previous_centre, previous_width
    tail.reverse()

    first_tail = tail[0][0]
    result = [(0.0, scheduled_half_width(0.0, width_scale))]
    while True:
        centre, half_width = result[-1]
        probe = min(first_tail, centre + 2.0 * half_width)
        next_width = scheduled_half_width(probe, width_scale)
        maximum_step = 2.0 * min(half_width, next_width) * (
            1.0 - overlap_fraction
        )
        if centre + maximum_step >= first_tail:
            break
        next_centre = centre + maximum_step
        result.append(
            (next_centre, scheduled_half_width(next_centre, width_scale))
        )
    if not result[-1][0] + result[-1][1] > first_tail - tail[0][1]:
        raise RuntimeError("scheduled prefix does not overlap endpoint tail")
    result.append(tail[0])
    result.extend(tail[1:])

    for (left_c, left_h), (right_c, right_h) in zip(result, result[1:]):
        if not left_c < right_c:
            raise RuntimeError("non-increasing cover worklist")
        if not left_c + left_h > right_c - right_h:
            raise RuntimeError("cover worklist lost strict scalar overlap")
    if not result[0][0] - result[0][1] < 0.0 < result[0][0] + result[0][1]:
        raise RuntimeError("c0 is not a strict parameter-interior point")
    if not (
        result[-1][0] - result[-1][1] < FOLD_U_INTERVAL[0]
        and result[-1][0] + result[-1][1] > FOLD_U_INTERVAL[1]
    ):
        raise RuntimeError("final parameter cap does not contain fold enclosure")
    return result


def uniform_tail_worklist(start_u: float, end_u: float, half_width: float,
                          overlap_fraction: float) -> list[tuple[float, float]]:
    """Build a fine sign-audit cover on a prescribed terminal subinterval."""
    if not (0.0 <= start_u < end_u <= FOLD_U):
        raise ValueError("tail endpoints must satisfy 0 <= start < end <= fold")
    if not half_width > 0.0:
        raise ValueError("uniform tail half width must be positive")
    if not (0.0 < overlap_fraction < 1.0):
        raise ValueError("overlap fraction must lie in (0,1)")
    step = 2.0 * half_width * (1.0 - overlap_fraction)
    result = [(start_u, half_width)]
    while result[-1][0] + step < end_u:
        result.append((result[-1][0] + step, half_width))
    if result[-1][0] < end_u:
        result.append((end_u, half_width))
    for (left_c, left_h), (right_c, right_h) in zip(result, result[1:]):
        if not left_c + left_h > right_c - right_h:
            raise RuntimeError("uniform tail worklist lost strict overlap")
    return result


def mixed_tangent(raw: np.ndarray, tangent: np.ndarray) -> np.ndarray:
    """Apply the raw-to-compact differential at nodes in the tail chart."""
    result = np.asarray(tangent, dtype=float).copy()
    z = np.asarray(raw[SWITCH_NODE:], dtype=float)
    w = np.asarray(tangent[SWITCH_NODE:], dtype=float)
    u, p_raw, v, q_raw = np.moveaxis(z, -1, 0)
    wu, wp, wv, wq = np.moveaxis(w, -1, 0)
    e = -1.0 / u
    de = wu / u**2
    root_e = np.sqrt(e)
    e32 = e * root_e
    de32 = 1.5 * root_e * de
    result[SWITCH_NODE:] = np.stack(
        [
            de,
            wp * e32 + p_raw * de32,
            wq * e32 + q_raw * de32,
            wv * e**2 + 2.0 * v * e * de,
        ],
        axis=-1,
    )
    return result


def solve_centres(jobs: list[tuple[float, float]], tolerance: float):
    _graph, h7, h7_gradient = degree_seven_graph()

    def target(state):
        u, p_raw, v, q_raw = state
        e = -1.0 / u
        e32 = e**1.5
        p = p_raw * e32
        d = q_raw * e32 + 2.0 / np.sqrt(3.0)
        omega = 1.0 + v * e**2
        return p - h7(e, d, omega)

    mesh = np.linspace(0.0, FINAL_TIME, 801)
    values = gamma0(mesh)
    records = []
    common_mesh = np.linspace(0.0, FINAL_TIME, 801)
    started = time.monotonic()
    for index, (source_u, half_width) in enumerate(jobs):
        values[0] += source_u - values[0, 0]

        def boundary(left, right, fixed_u=float(source_u)):
            return np.asarray(
                [left[0] - fixed_u, left[1], left[3], target(right)]
            )

        solution = solve_bvp(
            core,
            boundary,
            mesh,
            values,
            tol=tolerance,
            max_nodes=30000,
        )
        if not solution.success:
            raise RuntimeError(
                f"fixed-time solve failed at U={source_u:.17g}: "
                f"{solution.message}"
            )
        mesh, values = solution.x, solution.y
        nodes = mixed_nodes(solution)
        records.append(
            {
                "index": index,
                "source_u": float(source_u),
                "source_v": float(solution.y[2, 0]),
                "half_width": float(half_width),
                "nodes": nodes,
                "solution": solution,
                "raw_common": solution.sol(common_mesh).T,
            }
        )
        if (index + 1) % 100 == 0 or index + 1 == len(jobs):
            print(
                f"centres {index + 1}/{len(jobs)} "
                f"elapsed={time.monotonic() - started:.1f}s",
                flush=True,
            )

    parameters = np.asarray([record["source_u"] for record in records])
    raw_common = np.asarray([record["raw_common"] for record in records])
    raw_guesses = np.gradient(
        raw_common, parameters, axis=0, edge_order=2
    )

    tangent_nodes = []
    for index, (record, raw_guess) in enumerate(zip(records, raw_guesses)):
        solution = record["solution"]
        terminal = solution.sol(FINAL_TIME)

        def target_raw_gradient(state):
            u, p_raw, v, q_raw = state
            e = -1.0 / u
            root_e = np.sqrt(e)
            e32 = e * root_e
            de_du = 1.0 / u**2
            p_gradient = np.asarray(
                [p_raw * 1.5 * root_e * de_du, e32, 0.0, 0.0]
            )
            d_gradient = np.asarray(
                [q_raw * 1.5 * root_e * de_du, 0.0, 0.0, e32]
            )
            omega_gradient = np.asarray(
                [2.0 * v * e * de_du, 0.0, e**2, 0.0]
            )
            he, hd, homega = np.asarray(
                h7_gradient(
                    e,
                    q_raw * e32 + 2.0 / np.sqrt(3.0),
                    1.0 + v * e**2,
                ),
                dtype=float,
            ).reshape(3)
            return (
                p_gradient
                - he * np.asarray([de_du, 0.0, 0.0, 0.0])
                - hd * d_gradient
                - homega * omega_gradient
            )

        terminal_gradient = target_raw_gradient(terminal)

        def tangent_field(times, tangent):
            base = solution.sol(times)
            return np.vstack(
                [
                    tangent[1],
                    -2.0 * base[0] * tangent[0] - tangent[2],
                    tangent[3],
                    tangent[0],
                ]
            )

        def tangent_boundary(left, right):
            return np.asarray(
                [left[0] - 1.0, left[1], left[3], terminal_gradient @ right]
            )

        tangent_solution = solve_bvp(
            tangent_field,
            tangent_boundary,
            common_mesh,
            raw_guess.T,
            tol=tolerance,
            max_nodes=30000,
        )
        if not tangent_solution.success:
            raise RuntimeError(
                f"tangent solve failed at U={record['source_u']:.17g}: "
                f"{tangent_solution.message}"
            )
        times = np.linspace(0.0, FINAL_TIME, SEGMENTS + 1)
        raw_nodes = solution.sol(times).T
        tangent_raw = tangent_solution.sol(times).T
        tangent_nodes.append(mixed_tangent(raw_nodes, tangent_raw))
        del record["solution"]
        del record["raw_common"]
        if (index + 1) % 200 == 0 or index + 1 == len(records):
            print(f"tangents {index + 1}/{len(records)}", flush=True)

    tangents = np.asarray(tangent_nodes)
    curvatures = np.gradient(tangents, parameters, axis=0, edge_order=2)
    for record, tangent, curvature in zip(records, tangents, curvatures):
        record["tangent"] = tangent
        record["curvature"] = curvature
    return records


def write_outputs(records, output_dir: Path,
                  energy_sign_until: float | None = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    seeds = output_dir / "cover_seeds.txt"
    manifest = output_dir / "cover_boxes.jsonl"
    summary = output_dir / "cover_summary.json"

    offsets = []
    with seeds.open("wb") as stream:
        for record in records:
            offsets.append(stream.tell())
            values = [record["source_u"], record["source_v"]]
            values.extend(record["nodes"].ravel())
            values.extend(record["tangent"].ravel())
            values.extend(record["curvature"].ravel())
            line = " ".join(f"{float(value):.17g}" for value in values) + "\n"
            stream.write(line.encode("ascii"))

    with manifest.open("w", encoding="utf-8") as stream:
        for record, offset in zip(records, offsets):
            source_u = record["source_u"]
            half_width = record["half_width"]
            parameter_interval = [source_u - half_width, source_u + half_width]
            item = {
                "index": record["index"],
                "source_u": source_u,
                "source_v": record["source_v"],
                "half_width": half_width,
                "parameter_interval": parameter_interval,
                "seed_offset": offset,
                "energy_sign_required": (
                    parameter_interval[1] < (
                        energy_sign_until
                        if energy_sign_until is not None
                        else FOLD_U_INTERVAL[0] - 5e-5
                    )
                ),
                "exact_c0_endpoint": (
                    parameter_interval[0] < 0.0 < parameter_interval[1]
                ),
                "fold_endpoint": (
                    parameter_interval[0] < FOLD_U_INTERVAL[0]
                    and parameter_interval[1] > FOLD_U_INTERVAL[1]
                ),
            }
            stream.write(json.dumps(item, sort_keys=True) + "\n")

    u = np.asarray([record["source_u"] for record in records])
    v = np.asarray([record["source_v"] for record in records])
    energy = -2.0 * u**3 / 3.0 - 2.0 * u * v
    data = {
        "status": "FLOATING-PRECONDITIONERS-ONLY",
        "boxes": len(records),
        "segments": SEGMENTS,
        "switch_node": SWITCH_NODE,
        "switch_time": SWITCH_NODE * FINAL_TIME / SEGMENTS,
        "charts": {
            "nodes_0_through_3": "raw-(U,P,V,Q)",
            "nodes_4_through_30": "compact-(e,p,d,omega)",
        },
        "source_u_range": [float(u.min()), float(u.max())],
        "source_v_range": [float(v.min()), float(v.max())],
        "source_energy_range": [float(energy.min()), float(energy.max())],
        "fold_u_interval": list(FOLD_U_INTERVAL),
        "bulk_sha256": {
            "cover_boxes.jsonl": sha256(manifest),
            "cover_seeds.txt": sha256(seeds),
        },
    }
    summary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--width-scale", type=float, default=1.0)
    parser.add_argument("--final-half-width", type=float, default=1e-9)
    parser.add_argument("--overlap-fraction", type=float, default=0.25)
    parser.add_argument("--tolerance", type=float, default=2e-10)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--tail-start-u", type=float)
    parser.add_argument("--tail-end-u", type=float)
    parser.add_argument("--uniform-half-width", type=float)
    parser.add_argument("--energy-sign-until", type=float)
    arguments = parser.parse_args()
    tail_arguments = (
        arguments.tail_start_u,
        arguments.tail_end_u,
        arguments.uniform_half_width,
    )
    if any(value is not None for value in tail_arguments):
        if any(value is None for value in tail_arguments):
            parser.error(
                "--tail-start-u, --tail-end-u, and --uniform-half-width "
                "must be supplied together"
            )
        jobs = uniform_tail_worklist(
            arguments.tail_start_u,
            arguments.tail_end_u,
            arguments.uniform_half_width,
            arguments.overlap_fraction,
        )
        energy_sign_until = (
            arguments.energy_sign_until
            if arguments.energy_sign_until is not None
            else arguments.tail_end_u + arguments.uniform_half_width
        )
    else:
        jobs = worklist(
            arguments.width_scale,
            arguments.final_half_width,
            arguments.overlap_fraction,
        )
        if arguments.energy_sign_until is not None:
            parser.error("--energy-sign-until is only valid for a tail cover")
        energy_sign_until = None
    if arguments.limit is not None:
        jobs = jobs[: arguments.limit]
    records = solve_centres(jobs, arguments.tolerance)
    write_outputs(records, arguments.output_dir, energy_sign_until)


if __name__ == "__main__":
    main()
