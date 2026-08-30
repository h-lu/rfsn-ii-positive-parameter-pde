#!/usr/bin/env python3
"""Generate non-evidentiary predictors for a direct P2bK source point.

This is not the P2d transported phase used by the current P2e B.OUT design.
The script merely solves the centre floating-point problem and estimates its
parameter slopes, so every generated number remains a nonclaim candidate.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import math
import os
from pathlib import Path
from typing import Sequence

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import root_scalar


INNER_RADIUS = 1.0e-6
OUTER_RADIUS = 1.0e-2
LOG_FLIGHT = math.log(OUTER_RADIUS / INNER_RADIUS)
ALG_TARGET = 0.5 * (5.7566913947049203 + 5.7566913967948983)
POLE_TARGET = 0.5 * (103993 / 16551 + 208696 / 33215)
TARGETS = {"DIRECT_ALG": ALG_TARGET,
           "DIRECT_POLE_CENTER": POLE_TARGET}


def parameter_centre(r_index: int, a2_index: int,
                     epsilon_index: int) -> np.ndarray:
    return np.array([
        (r_index + 0.5) / 3200,
        (a2_index - 64 + 0.5) / 256,
        (epsilon_index + 8 + 0.5) / 10,
    ], dtype=float)


def coefficients(mu: Sequence[float]) -> tuple[float, ...]:
    r, a2, epsilon = mu
    root_epsilon = math.sqrt(epsilon)
    a = 1 + root_epsilon * r**3 * a2
    b = root_epsilon * r**2 / 3
    c = 2 * r * a2 + root_epsilon * r**4 * a2**2
    alpha = 0.5 * math.sqrt(2 + c)
    beta = 0.5 * math.sqrt(2 - c)
    chi = math.atan((1 / math.sqrt(2) - alpha) / beta)
    return a, b, alpha, beta, math.cos(chi), math.sin(chi)


def field(mu: Sequence[float]):
    a, b, alpha, beta, cos_chi, sin_chi = coefficients(mu)

    def rhs(_time: float, state: np.ndarray) -> np.ndarray:
        ell, theta, s1, s2 = state
        rho = math.exp(ell)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        v1 = rho * cos_theta
        v2 = rho * sin_theta
        u1 = cos_chi * v1 - sin_chi * v2
        u2 = sin_chi * v1 + cos_chi * v2
        total_u = u1 + s1
        nonlinear = -a * total_u**2 + b * total_u**3
        du1 = alpha * u1 - beta * u2 + nonlinear / (4 * alpha)
        du2 = beta * u1 + alpha * u2 - nonlinear / (4 * beta)
        dv1 = cos_chi * du1 + sin_chi * du2
        dv2 = -sin_chi * du1 + cos_chi * du2
        radial = cos_theta * dv1 + sin_theta * dv2
        return np.array([
            radial / rho,
            (-sin_theta * dv1 + cos_theta * dv2) / rho,
            -alpha * s1 + beta * s2 - nonlinear / (4 * alpha),
            -beta * s1 - alpha * s2 + nonlinear / (4 * beta),
        ])

    return rhs


def first_radius_hit_phase(theta: float, mu: Sequence[float]) -> float:
    target_ell = math.log(OUTER_RADIUS)

    def outer_radius(_time: float, state: np.ndarray) -> float:
        return state[0] - target_ell

    outer_radius.direction = 1
    outer_radius.terminal = True
    solution = solve_ivp(
        field(mu), (0.0, 25.0),
        np.array([math.log(INNER_RADIUS), theta, 0.0, 0.0]),
        method="DOP853", rtol=2.0e-12, atol=2.0e-14,
        max_step=0.05, events=outer_radius,
    )
    if not solution.success or len(solution.t_events[0]) != 1:
        raise RuntimeError("floating first-radius-hit integration failed")
    return float(solution.y_events[0][0, 1])


def linear_seed(mu: Sequence[float], target: float) -> float:
    _a, _b, alpha, beta, _cos_chi, _sin_chi = coefficients(mu)
    return target + 2 * math.pi - LOG_FLIGHT * beta / alpha


def centre_root(mu: Sequence[float], target: float) -> float:
    wanted = target + 2 * math.pi

    def residual(theta: float) -> float:
        return first_radius_hit_phase(theta, mu) - wanted

    seed = linear_seed(mu, target)
    half_width = 0.002
    for _attempt in range(8):
        left, right = seed - half_width, seed + half_width
        f_left, f_right = residual(left), residual(right)
        if f_left * f_right <= 0:
            result = root_scalar(
                residual, bracket=(left, right), method="brentq",
                xtol=2.0e-13, rtol=1.0e-14,
            )
            if result.converged:
                return float(result.root)
        half_width *= 2
    raise RuntimeError("could not bracket floating centre root")


def affine_predictor(task: tuple[int, int, int, str]) -> list[object]:
    r_index, a2_index, epsilon_index, target_kind = task
    target = TARGETS[target_kind]
    mu = parameter_centre(r_index, a2_index, epsilon_index)
    theta = centre_root(mu, target)

    # Differentiate the first-hit phase equation at the centre.  These
    # floating differences choose a chart only; the interval kernel later
    # encloses the full composed derivatives on the exact leaf.
    theta_step = 1.0e-6
    phase_theta = (
        first_radius_hit_phase(theta + theta_step, mu)
        - first_radius_hit_phase(theta - theta_step, mu)
    ) / (2 * theta_step)
    parameter_steps = (1.0e-6, 1.0e-5, 1.0e-5)
    slopes = []
    for axis, step in enumerate(parameter_steps):
        plus = mu.copy()
        minus = mu.copy()
        plus[axis] += step
        minus[axis] -= step
        phase_parameter = (
            first_radius_hit_phase(theta, plus)
            - first_radius_hit_phase(theta, minus)
        ) / (2 * step)
        slopes.append(-phase_parameter / phase_theta)

    residual = first_radius_hit_phase(theta, mu) - (target + 2 * math.pi)
    return [
        r_index, a2_index, epsilon_index, format(theta, ".17g"),
        *(format(float(value), ".17g") for value in slopes),
        format(residual, ".17g"), "0.0004",
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=sorted(TARGETS), required=True)
    parser.add_argument("--r-start", type=int, default=0)
    parser.add_argument("--r-stop", type=int, default=64)
    parser.add_argument("--a2-start", type=int, default=0)
    parser.add_argument("--a2-stop", type=int, default=128)
    parser.add_argument("--epsilon-start", type=int, default=0)
    parser.add_argument("--epsilon-stop", type=int, default=4)
    parser.add_argument("--workers", type=int, default=max(1, os.cpu_count() // 2))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def checked_range(start: int, stop: int, limit: int, name: str) -> range:
    if start < 0 or stop > limit or start >= stop:
        raise ValueError(f"invalid {name} half-open range [{start},{stop})")
    return range(start, stop)


def main() -> int:
    args = parse_args()
    tasks = [
        (r, a2, epsilon, args.target)
        for r in checked_range(args.r_start, args.r_stop, 64, "r")
        for a2 in checked_range(args.a2_start, args.a2_stop, 128, "a2")
        for epsilon in checked_range(
            args.epsilon_start, args.epsilon_stop, 4, "epsilon")
    ]
    with concurrent.futures.ProcessPoolExecutor(
            max_workers=args.workers) as executor:
        records = list(executor.map(affine_predictor, tasks, chunksize=4))
    document = {
        "schema_version": "rfsn-vdp-p2bk-direct-source-predictor-scout/1",
        "evidence": "FLOATING_POINT_CANDIDATE_GENERATOR_NONCLAIM",
        "claim_bearing": False,
        "target_kind": args.target,
        "target_midpoint": format(TARGETS[args.target], ".17g"),
        "grid": {
            "r": "[i/3200,(i+1)/3200]",
            "a2": "[(j-64)/256,(j-63)/256]",
            "epsilon": "[(k+8)/10,(k+9)/10]",
            "r_refinement_factor_over_frozen_bridge": 8,
        },
        "method": {
            "solver": "scipy.solve_ivp/DOP853",
            "scipy_version": scipy.__version__,
            "stable_graph_predictor": "s1=s2=0 only",
            "acceptance": "none; strict interval Newton is separate",
        },
        "record_count": len(records),
        "record_columns": [
            "r_leaf_index", "a2_index", "epsilon_index", "theta0",
            "theta_r", "theta_a2", "theta_epsilon", "centre_residual",
            "delta_radius",
        ],
        "records": records,
    }
    if args.pretty:
        output = json.dumps(document, indent=2, sort_keys=True) + "\n"
    else:
        output = json.dumps(
            document, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output is None:
        print(output, end="")
    else:
        args.output.write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
