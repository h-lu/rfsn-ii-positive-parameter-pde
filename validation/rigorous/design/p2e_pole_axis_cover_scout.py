#!/usr/bin/env python3
"""Adaptive outward-rounded design cover for the P2e pole axis channel.

The inexpensive pass uses the complete proved H10-centered true-graph tube
on one frozen 4096-cell bridge box.  Only a failed parent is refined into its
eight canonical r-leaves.  A refined leaf is first tried with the same coarse
graph tube; only a remaining wrapping failure invokes the scalar true-Wu
source trace and its root-conditioned eta enclosure.

Every accepted terminal job checks the first U=-10 encounter and strict
interior entry into the positive pole cone.  This orchestrator is a design
runner, not a release certificate: it does not authenticate the executable
build or prove the rest of the P2e incidence atlas.
"""

from __future__ import annotations

import argparse
import concurrent.futures
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Iterable, Sequence

from p2e_source_trace_predictors import affine_predictor


TARGET_KIND = "DIRECT_POLE_CENTER"
SOURCE_PREFIX = "RESULT_JSON "
BASE_LABELS = [
    "U=-.05 DOWN I", "Q=0 DOWN", "P=0 MIN", "U=-.05 UP", "Q=0 UP",
    "P=0 MAX", "V=0 UP", "U=-.2 DOWN", "U=-.5 DOWN", "U=-1 DOWN",
    "U=-2 DOWN", "U=-4 DOWN", "U=-7 DOWN", "U=-10 DOWN",
]
V_STEPS_LABELS = BASE_LABELS[:7] + [
    "V=.5 UP", "V=.75 UP", "V=.8 UP",
] + BASE_LABELS[7:]
TURN_REDUCED_LABELS = BASE_LABELS[:5] + [
    "U=2.5 UP", "U=2.75 UP",
] + BASE_LABELS[5:]
BASE_SIGNS = [-1, -1, 1, 1, 1, -1, 1] + [-1] * 7
V_STEPS_SIGNS = BASE_SIGNS[:7] + [1, 1, 1] + BASE_SIGNS[7:]
TURN_REDUCED_SIGNS = BASE_SIGNS[:5] + [1, 1] + \
    BASE_SIGNS[5:]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checked_half_open(start: int, stop: int, limit: int, name: str) -> range:
    if start < 0 or stop > limit or start >= stop:
        raise ValueError(f"invalid {name} range [{start},{stop})")
    return range(start, stop)


SplitPath = tuple[tuple[str, int], ...]


def r_split_path(r_leaf: int) -> SplitPath:
    local = r_leaf % 8
    return tuple(("r", half) for half in (
        (local >> 2) & 1, (local >> 1) & 1, local & 1))


def r_local_index(path: SplitPath) -> int:
    halves = [half for variable, half in path if variable == "r"]
    if len(halves) != 3:
        raise ValueError("a refined r path must contain exactly three halves")
    return (halves[0] << 2) + (halves[1] << 1) + halves[2]


def phase_bits(path: SplitPath) -> tuple[int, ...]:
    return tuple(half for variable, half in path if variable == "phase")


def binary_prefix_cover(paths: Iterable[tuple[int, ...]]) -> bool:
    leaves = set(paths)
    if not leaves or any(bit not in (0, 1) for path in leaves for bit in path):
        return False
    for path in leaves:
        if any(path[:length] in leaves for length in range(len(path))):
            return False

    def covers(prefix: tuple[int, ...]) -> bool:
        if prefix in leaves:
            return True
        if not any(path[:len(prefix)] == prefix for path in leaves):
            return False
        return covers(prefix + (0,)) and covers(prefix + (1,))

    return covers(())


def run_process(argv: Sequence[str], timeout: float) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            list(argv), text=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=timeout, check=False)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout.decode() if isinstance(error.stdout, bytes) else (
            error.stdout or "")
        stderr = error.stderr.decode() if isinstance(error.stderr, bytes) else (
            error.stderr or "")
        return 124, stdout, stderr + "\nprocess timeout"


def interval_pair(value: Any, name: str) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"{name} is not an interval pair")
    lower_value, upper_value = float(value[0]), float(value[1])
    if not math.isfinite(lower_value) or not math.isfinite(upper_value) \
            or lower_value > upper_value:
        raise ValueError(f"{name} is not a finite ordered interval")
    return lower_value, upper_value


def bisect_fraction(box: tuple[Fraction, Fraction], half: int
                    ) -> tuple[Fraction, Fraction]:
    midpoint = (box[0] + box[1]) / 2
    return (box[0], midpoint) if half == 0 else (midpoint, box[1])


def expected_request_boxes(
        parent: tuple[int, int, int], path: SplitPath,
        eta: Sequence[float] | None
        ) -> tuple[dict[str, tuple[Fraction, Fraction]],
                   tuple[Fraction, Fraction], tuple[float, float]]:
    r_index, a2_index, epsilon_index = parent
    parameters = {
        "r": (Fraction(r_index, 400), Fraction(r_index + 1, 400)),
        "a2": (Fraction(a2_index - 64, 256),
               Fraction(a2_index - 63, 256)),
        "epsilon": (Fraction(epsilon_index + 8, 10),
                    Fraction(epsilon_index + 9, 10)),
    }
    pole_radius = Fraction(9, 800000)
    phase = (Fraction(103993, 16551) - pole_radius,
             Fraction(208696, 33215) + pole_radius)
    graph_error = (-1.0 / 200000.0, 1.0 / 200000.0)
    for variable, half in path:
        if variable in parameters:
            parameters[variable] = bisect_fraction(parameters[variable], half)
        elif variable == "phase":
            phase = bisect_fraction(phase, half)
        elif variable == "eta":
            graph_error = tuple(float(value) for value in bisect_fraction(
                (Fraction.from_float(graph_error[0]),
                 Fraction.from_float(graph_error[1])), half))
        else:
            raise ValueError(f"unsupported request split {variable}")
    if eta is not None:
        graph_error = (float(eta[0]), float(eta[1]))
    return parameters, phase, graph_error


def require_matching_interval(name: str, observed: Any,
                              expected: Sequence[Any]) -> None:
    observed_lower, observed_upper = interval_pair(observed, name)
    expected_lower, expected_upper = float(expected[0]), float(expected[1])
    tolerance = 1024.0 * sys.float_info.epsilon * max(
        1.0, abs(expected_lower), abs(expected_upper))
    if observed_lower > expected_lower or observed_upper < expected_upper or \
            expected_lower - observed_lower > tolerance or \
            observed_upper - expected_upper > tolerance:
        raise ValueError(
            f"{name} does not match the requested interval: "
            f"{observed} versus [{expected_lower},{expected_upper}]")


def require_interval_subset(name: str, inner: Any, outer: Any) -> None:
    inner_pair = interval_pair(inner, f"{name} inner")
    outer_pair = interval_pair(outer, f"{name} outer")
    if inner_pair[0] < outer_pair[0] or inner_pair[1] > outer_pair[1]:
        raise ValueError(f"{name} is not contained in its source certificate")


def parse_terminal(stdout: str) -> dict[str, Any]:
    value = json.loads(stdout)
    if value.get("status") != "PASS":
        raise ValueError("terminal output is not PASS")
    cone = value.get("pole_cone")
    if not isinstance(cone, dict) or not cone.get("applicable") \
            or not cone.get("passed"):
        raise ValueError("terminal output lacks a strict pole-cone PASS")
    if not value.get("event_sequence_passed"):
        raise ValueError("terminal output lacks the frozen event-sequence PASS")
    escape = value.get("escape_cone_entry")
    if not isinstance(escape, dict) or not escape.get("applicable") \
            or not escape.get("passed"):
        raise ValueError("terminal output lacks the x=1/5 escape-cone PASS")
    guard = value.get("pre_escape_no_pole_guard")
    if not isinstance(guard, dict) or not guard.get("applicable") \
            or not guard.get("passed"):
        raise ValueError("terminal output lacks the pre-escape no-pole PASS")
    if not interval_pair(guard.get("escape_section_residual"),
                         "guard escape residual")[0] <= 0.0 <= \
            interval_pair(guard.get("escape_section_residual"),
                          "guard escape residual")[1]:
        raise ValueError("guard escape section does not contain zero")
    p3_entry = value.get("p3_zero_action_entry_bounds")
    if not isinstance(p3_entry, dict) or not p3_entry.get("applicable") \
            or not p3_entry.get("passed"):
        raise ValueError("terminal output lacks the zero-action P3 gate PASS")
    return value


def validate_terminal_response(
        value: dict[str, Any], parent: tuple[int, int, int], path: SplitPath,
        eta: Sequence[float] | None, route: str) -> None:
    if value.get("scope") != "P2E_AXIS_POLE_TERMINAL_FIRST_HIT_CELL_SCOUT":
        raise ValueError("terminal scope does not match the POLE kernel")
    if value.get("claim_bearing") is not False:
        raise ValueError("terminal claim status is not the nonclaim design scope")
    if value.get("event_sequence_passed") is not True:
        raise ValueError("terminal event sequence is not PASS")
    for name in ("escape_cone_entry", "pre_escape_no_pole_guard",
                 "pole_cone", "p3_zero_action_entry_bounds"):
        item = value.get(name)
        if not isinstance(item, dict) or item.get("applicable") is not True \
                or item.get("passed") is not True:
            raise ValueError(f"terminal {name} is not an applicable PASS")
    expected_cell = {
        "r_index": parent[0], "a2_index": parent[1],
        "epsilon_index": parent[2],
    }
    if value.get("cell") != expected_cell:
        raise ValueError("terminal cell does not match the request")
    if value.get("pole_route") != route:
        raise ValueError("terminal route does not match the request")
    split_parts = [f"{variable}:{half}" for variable, half in path]
    split_parts.append(f"pole_route:{route}")
    if eta is not None:
        split_parts.append("eta_box")
    if value.get("split_path") != ",".join(split_parts):
        raise ValueError("terminal split path does not match the request")
    expected_labels = {
        "BASE": BASE_LABELS,
        "V_STEPS": V_STEPS_LABELS,
        "TURN_REDUCED": TURN_REDUCED_LABELS,
    }[route]
    if value.get("event_sequence_labels") != expected_labels:
        raise ValueError("terminal labels do not match the requested route")
    expected_signs = {
        "BASE": BASE_SIGNS,
        "V_STEPS": V_STEPS_SIGNS,
        "TURN_REDUCED": TURN_REDUCED_SIGNS,
    }[route]
    times = value.get("leg_return_times")
    residuals = value.get("leg_section_residuals")
    speeds = value.get("leg_section_speeds")
    if not all(isinstance(items, list) and len(items) == len(expected_labels)
               for items in (times, residuals, speeds)):
        raise ValueError("terminal lacks the complete leg diagnostics")
    for index, (leg_time, residual, speed, sign) in enumerate(zip(
            times, residuals, speeds, expected_signs)):
        if interval_pair(leg_time, f"leg {index} return time")[0] <= 0.0:
            raise ValueError(f"leg {index} return time is not positive")
        residual_pair = interval_pair(residual, f"leg {index} residual")
        if not residual_pair[0] <= 0.0 <= residual_pair[1]:
            raise ValueError(f"leg {index} residual does not contain zero")
        speed_pair = interval_pair(speed, f"leg {index} speed")
        if sign < 0 and speed_pair[1] >= 0.0:
            raise ValueError(f"leg {index} is not strictly downward")
        if sign > 0 and speed_pair[0] <= 0.0:
            raise ValueError(f"leg {index} is not strictly upward")

    parameter_boxes, phase_box, graph_box = expected_request_boxes(
        parent, path, eta)
    observed_parameters = value.get("parameter_box")
    if not isinstance(observed_parameters, dict):
        raise ValueError("terminal output lacks the parameter box")
    for parameter, box in parameter_boxes.items():
        require_matching_interval(
            f"parameter {parameter}", observed_parameters.get(parameter), box)
    require_matching_interval("phase", value.get("phase"), phase_box)
    require_matching_interval(
        "graph error", value.get("graph_error"), graph_box)
    terminal_u = interval_pair(value.get("terminal_U"), "terminal U")
    if not terminal_u[0] <= -10.0 <= terminal_u[1]:
        raise ValueError("terminal U does not contain -10")
    residual = interval_pair(value.get("section_residual"),
                             "terminal section residual")
    if not residual[0] <= 0.0 <= residual[1]:
        raise ValueError("terminal section residual does not contain zero")
    if value.get("terminal_speed_strictly_negative") is not True:
        raise ValueError("terminal speed is not strictly negative")
    guard = value["pre_escape_no_pole_guard"]
    minimum_time = interval_pair(guard["minimum_time"], "guard minimum time")
    maximum_time = interval_pair(guard["maximum_time"], "guard maximum time")
    escape_time = interval_pair(guard["escape_time"], "guard escape time")
    return_time = interval_pair(value["return_time"], "terminal return time")
    if minimum_time[0] <= 0.0 or maximum_time[0] <= minimum_time[1] \
            or escape_time[0] <= maximum_time[1] \
            or return_time[0] <= escape_time[1]:
        raise ValueError("guard event times are not strictly ordered")
    if interval_pair(guard["minimum_U"], "guard minimum U")[0] <= -1.0:
        raise ValueError("guard minimum can reach the pole side")
    if interval_pair(guard["minimum_P_prime"],
                     "guard minimum acceleration")[0] <= 0.0:
        raise ValueError("guard minimum is not strict")
    if interval_pair(guard["maximum_U"], "guard maximum U")[0] <= 0.0:
        raise ValueError("guard maximum is not on U>0")
    if interval_pair(guard["maximum_P_prime"],
                     "guard maximum acceleration")[1] >= 0.0:
        raise ValueError("guard maximum is not strict")
    if interval_pair(guard["escape_P"], "guard escape P")[1] >= 0.0:
        raise ValueError("guard escape is not strictly downward")
    escape = value["escape_cone_entry"]
    for key, threshold in (("y", 2.0), ("D", 0.0), ("K", 0.0),
                           ("gamma", 0.0),
                           ("K_prime_boundary_margin", 0.0)):
        if interval_pair(escape[key], f"escape {key}")[0] <= threshold:
            raise ValueError(f"escape {key} lacks its strict margin")
    cone = value["pole_cone"]
    for key in ("y", "D", "K", "y_prime", "K_prime"):
        if interval_pair(cone[key], f"pole cone {key}")[0] <= 0.0:
            raise ValueError(f"pole cone {key} is not positive")
    if interval_pair(cone["y"], "P3 y")[0] < 13.0 \
            or interval_pair(cone["D"], "P3 D")[0] < 26.0 \
            or interval_pair(cone["K"], "P3 K")[0] < 131.0:
        raise ValueError("terminal misses the zero-action P3 thresholds")
    turn = value.get("pole_upper_turn_reduced_passage")
    if route == "TURN_REDUCED":
        if not isinstance(turn, dict) or turn.get("applicable") is not True \
                or turn.get("passed") is not True:
            raise ValueError("terminal lacks the upper-turn reduced PASS")
        require_matching_interval("upper-turn seam U", turn.get("seam_U"),
                                  (-0.05, -0.05))
        require_matching_interval("upper-turn terminal U",
                                  turn.get("terminal_U"), (2.2, 2.2))
        if interval_pair(turn.get("clock"), "upper-turn clock")[0] <= 0.0:
            raise ValueError("upper-turn clock is not positive")
        if interval_pair(turn.get("dense_P_hull"),
                         "upper-turn dense P hull")[0] <= 0.0:
            raise ValueError("upper-turn passage does not keep P>0")
        steps = turn.get("dense_step_count")
        if not isinstance(steps, int) or isinstance(steps, bool) or steps <= 0:
            raise ValueError("upper-turn dense step count is not positive")
        escape_reduced = value.get("pole_escape_reduced_passage")
        if not isinstance(escape_reduced, dict) \
                or escape_reduced.get("applicable") is not True \
                or escape_reduced.get("passed") is not True:
            raise ValueError("terminal lacks the escape reduced PASS")
        require_matching_interval("escape seam V",
                                  escape_reduced.get("seam_V"), (0.0, 0.0))
        require_matching_interval(
            "escape terminal V", escape_reduced.get("terminal_V"),
            (0.8, 0.8))
        if interval_pair(escape_reduced.get("clock"),
                         "escape reduced clock")[0] <= 0.0:
            raise ValueError("escape reduced clock is not positive")
        if interval_pair(escape_reduced.get("dense_Q_hull"),
                         "escape dense Q hull")[0] <= 0.0:
            raise ValueError("escape reduced passage does not keep Q>0")
        escape_steps = escape_reduced.get("dense_step_count")
        if not isinstance(escape_steps, int) \
                or isinstance(escape_steps, bool) or escape_steps <= 0:
            raise ValueError("escape dense step count is not positive")


def parse_source(stdout: str,
                 expected_leaf: tuple[int, int, int] | None = None,
                 predictor: Sequence[Any] | None = None
                 ) -> dict[str, Any]:
    lines = [line[len(SOURCE_PREFIX):] for line in stdout.splitlines()
             if line.startswith(SOURCE_PREFIX)]
    if len(lines) != 1:
        raise ValueError("source output lacks one RESULT_JSON record")
    value = json.loads(lines[0])
    if value.get("status") != "PASS":
        raise ValueError("root-conditioned source output is not PASS")
    if value.get("claim_bearing") is not False:
        raise ValueError("source claim status is not the nonclaim design scope")
    if value.get("scope") != "P2E_DIRECT_SOURCE_ROOT_CONDITIONED_LEAF" \
            or value.get("target_kind") != TARGET_KIND:
        raise ValueError("source scope or target kind does not match")
    if expected_leaf is not None:
        if value.get("leaf") != list(expected_leaf):
            raise ValueError("source leaf does not match the request")
        if value.get("split_path") != "":
            raise ValueError("source unexpectedly returned a split leaf")
        expected_parameters = {
            "r": (Fraction(expected_leaf[0], 3200),
                  Fraction(expected_leaf[0] + 1, 3200)),
            "a2": (Fraction(expected_leaf[1] - 64, 256),
                   Fraction(expected_leaf[1] - 63, 256)),
            "epsilon": (Fraction(expected_leaf[2] + 8, 10),
                        Fraction(expected_leaf[2] + 9, 10)),
        }
        observed_parameters = value.get("parameter_box")
        if not isinstance(observed_parameters, dict):
            raise ValueError("source output lacks the parameter box")
        for parameter, box in expected_parameters.items():
            require_matching_interval(
                f"source parameter {parameter}",
                observed_parameters.get(parameter), box)
        pole_radius = Fraction(9, 800000)
        require_matching_interval(
            "source target phase", value.get("target_phase"),
            (Fraction(103993, 16551) - pole_radius,
             Fraction(208696, 33215) + pole_radius))
    if predictor is not None:
        if len(predictor) != 9:
            raise ValueError("source predictor must have nine columns")
        require_matching_interval(
            "source theta0", value.get("theta0"),
            (predictor[3], predictor[3]))
        slopes = value.get("theta_parameter_slopes")
        if not isinstance(slopes, list) or len(slopes) != 3:
            raise ValueError("source output lacks three theta slopes")
        for index, requested in enumerate(predictor[4:7]):
            require_matching_interval(
                f"source theta slope {index}", slopes[index],
                (requested, requested))
        radius = float(predictor[8])
        require_matching_interval(
            "source trial delta", value.get("trial_delta"),
            (-radius, radius))
    trial = interval_pair(value.get("trial_delta"), "source trial delta")
    newton = interval_pair(
        value.get("interval_newton"), "source interval Newton")
    if not trial[0] < newton[0] <= newton[1] < trial[1]:
        raise ValueError("source interval Newton is not strictly interior")
    derivative = interval_pair(
        value.get("phase_derivative"), "source phase derivative")
    if derivative[0] <= 0.0 <= derivative[1]:
        raise ValueError("source phase derivative contains zero")
    if interval_pair(value.get("log_radial_rate"),
                     "source log radial rate")[0] <= 0.0:
        raise ValueError("source log radial rate is not positive")
    if interval_pair(value.get("phase_rate"),
                     "source phase rate")[0] <= 0.0:
        raise ValueError("source phase rate is not positive")
    eta = interval_pair(value.get("root_eta"), "source root eta")
    if eta[0] < -1.0 / 200000.0 or eta[1] > 1.0 / 200000.0:
        raise ValueError("source root eta leaves the proved graph tube")
    if interval_pair(value.get("root_return_time"),
                     "source root return time")[0] <= 0.0:
        raise ValueError("source root return time is not positive")
    residual = interval_pair(
        value.get("root_phase_residual"), "source root phase residual")
    if not residual[0] <= 0.0 <= residual[1]:
        raise ValueError("source root phase residual does not contain zero")
    return value


def compact_terminal(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "parameter_box": value["parameter_box"],
        "phase": value["phase"],
        "graph_error": value["graph_error"],
        "pole_route": value["pole_route"],
        "return_time": value["return_time"],
        "event_sequence_labels": value["event_sequence_labels"],
        "leg_return_times": value["leg_return_times"],
        "leg_section_residuals": value["leg_section_residuals"],
        "leg_section_speeds": value["leg_section_speeds"],
        "event_sequence_passed": value["event_sequence_passed"],
        "escape_cone_entry": value["escape_cone_entry"],
        "pre_escape_no_pole_guard": value["pre_escape_no_pole_guard"],
        "terminal_U": value["terminal_U"],
        "terminal_P": value["terminal_P"],
        "terminal_V": value["terminal_V"],
        "terminal_Q": value["terminal_Q"],
        "section_residual": value["section_residual"],
        "terminal_speed_strictly_negative":
            value["terminal_speed_strictly_negative"],
        "pole_cone": value["pole_cone"],
        "p3_zero_action_entry_bounds":
            value["p3_zero_action_entry_bounds"],
        "pole_upper_turn_reduced_passage":
            value["pole_upper_turn_reduced_passage"],
        "pole_escape_reduced_passage":
            value["pole_escape_reduced_passage"],
    }


def compact_source(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "parameter_box": value["parameter_box"],
        "target_phase": value["target_phase"],
        "theta0": value["theta0"],
        "theta_parameter_slopes": value["theta_parameter_slopes"],
        "trial_delta": value["trial_delta"],
        "interval_newton": value["interval_newton"],
        "phase_derivative": value["phase_derivative"],
        "log_radial_rate": value["log_radial_rate"],
        "phase_rate": value["phase_rate"],
        "root_eta": value["root_eta"],
        "root_stable_coordinates": value["root_stable_coordinates"],
        "root_return_time": value["root_return_time"],
        "root_phase_residual": value["root_phase_residual"],
    }


def terminal_argv(executable: Path, parent: tuple[int, int, int],
                  split_path: SplitPath = (),
                  eta: Sequence[float] | None = None,
                  route: str = "BASE") -> list[str]:
    argv = [str(executable), "POLE", *(str(value) for value in parent)]
    for variable, half in split_path:
        argv.extend((variable, str(half)))
    argv.extend(("pole_route", route))
    if eta is not None:
        if len(eta) != 2:
            raise ValueError("eta enclosure must have two endpoints")
        argv.extend(("eta_box", repr(eta[0]), repr(eta[1])))
    return argv


def run_terminal_job(job: tuple[tuple[int, int, int], SplitPath,
                                Sequence[float] | None],
                     executable: Path, timeout: float
                     ) -> tuple[tuple[int, int, int], SplitPath,
                                int, dict[str, Any] | None, str]:
    parent, path, eta = job
    failures = []
    last_returncode = 11
    for route in ("BASE", "V_STEPS", "TURN_REDUCED"):
        returncode, stdout, stderr = run_process(
            terminal_argv(executable, parent, path, eta, route), timeout)
        last_returncode = returncode
        if returncode == 0:
            try:
                value = parse_terminal(stdout)
                validate_terminal_response(value, parent, path, eta, route)
                return parent, path, returncode, value, ""
            except (KeyError, TypeError, ValueError,
                    json.JSONDecodeError) as error:
                failures.append(f"{route}: {error}")
                last_returncode = 90
                continue
        detail = (stderr or stdout).strip().splitlines()
        failures.append(
            f"{route}: {detail[0] if detail else 'no output'}")
    return parent, path, last_returncode, None, "; ".join(failures)


def run_many_terminal(
        jobs: Sequence[tuple[tuple[int, int, int], SplitPath,
                             Sequence[float] | None]],
        executable: Path, timeout: float, workers: int
        ) -> list[tuple[tuple[int, int, int], SplitPath, int,
                        dict[str, Any] | None, str]]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(
            lambda job: run_terminal_job(job, executable, timeout), jobs))


def run_source_job(predictor: Sequence[Any], executable: Path,
                   timeout: float) -> tuple[tuple[int, int, int], int,
                                             dict[str, Any] | None, str]:
    leaf = tuple(int(value) for value in predictor[:3])
    argv = [
        str(executable), *(str(value) for value in predictor[:3]),
        *(str(value) for value in predictor[3:7]), str(predictor[8]),
        TARGET_KIND,
    ]
    returncode, stdout, stderr = run_process(argv, timeout)
    if returncode == 0:
        try:
            return leaf, returncode, parse_source(stdout, leaf, predictor), ""
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            return leaf, 91, None, str(error)
    detail = (stderr or stdout).strip().splitlines()
    return leaf, returncode, None, detail[0] if detail else "no output"


def lower(interval: Sequence[float]) -> float:
    return float(interval[0])


def upper(interval: Sequence[float]) -> float:
    return float(interval[1])


def distance_from_zero(interval: Sequence[float]) -> float:
    lo, hi = lower(interval), upper(interval)
    if lo <= 0.0 <= hi:
        return 0.0
    return min(abs(lo), abs(hi))


def aggregate(records: Sequence[dict[str, Any]]) -> dict[str, float]:
    terminals = [record["terminal"] for record in records]
    cones = [terminal["pole_cone"] for terminal in terminals]
    escape_cones = [terminal["escape_cone_entry"] for terminal in terminals]
    pre_escape_guards = [
        terminal["pre_escape_no_pole_guard"] for terminal in terminals]
    result = {
        "return_time_lower": min(lower(t["return_time"]) for t in terminals),
        "return_time_upper": max(upper(t["return_time"]) for t in terminals),
        "terminal_speed_y_lower": min(lower(c["y"]) for c in cones),
        "D_lower": min(lower(c["D"]) for c in cones),
        "K_lower": min(lower(c["K"]) for c in cones),
        "y_prime_lower": min(lower(c["y_prime"]) for c in cones),
        "K_prime_lower": min(lower(c["K_prime"]) for c in cones),
        "p3_y_margin_lower": min(lower(c["y"]) - 13.0 for c in cones),
        "p3_D_margin_lower": min(lower(c["D"]) - 26.0 for c in cones),
        "p3_K_margin_lower": min(lower(c["K"]) - 131.0 for c in cones),
        "escape_y_lower": min(lower(c["y"]) for c in escape_cones),
        "escape_D_lower": min(lower(c["D"]) for c in escape_cones),
        "escape_K_lower": min(lower(c["K"]) for c in escape_cones),
        "escape_gamma_lower": min(
            lower(c["gamma"]) for c in escape_cones),
        "escape_K_prime_boundary_margin_lower": min(
            lower(c["K_prime_boundary_margin"]) for c in escape_cones),
        "guard_minimum_U_lower": min(
            lower(g["minimum_U"]) for g in pre_escape_guards),
        "guard_minimum_P_prime_lower": min(
            lower(g["minimum_P_prime"]) for g in pre_escape_guards),
        "guard_maximum_U_lower": min(
            lower(g["maximum_U"]) for g in pre_escape_guards),
        "guard_maximum_P_prime_upper": max(
            upper(g["maximum_P_prime"]) for g in pre_escape_guards),
        "guard_escape_P_upper": max(
            upper(g["escape_P"]) for g in pre_escape_guards),
    }
    source_records = [record["source"] for record in records
                      if record.get("source") is not None]
    turn_passages = [
        terminal["pole_upper_turn_reduced_passage"]
        for terminal in terminals
        if terminal["pole_upper_turn_reduced_passage"]["applicable"]]
    escape_passages = [
        terminal["pole_escape_reduced_passage"]
        for terminal in terminals
        if terminal["pole_escape_reduced_passage"]["applicable"]]
    if turn_passages:
        result.update({
            "turn_reduced_P_lower": min(
                lower(passage["dense_P_hull"]) for passage in turn_passages),
            "turn_reduced_clock_lower": min(
                lower(passage["clock"]) for passage in turn_passages),
        })
    if escape_passages:
        result.update({
            "escape_reduced_Q_lower": min(
                lower(passage["dense_Q_hull"])
                for passage in escape_passages),
            "escape_reduced_clock_lower": min(
                lower(passage["clock"]) for passage in escape_passages),
        })
    if source_records:
        result.update({
            "source_log_radial_rate_lower": min(
                lower(source["log_radial_rate"]) for source in source_records),
            "source_phase_rate_lower": min(
                lower(source["phase_rate"]) for source in source_records),
            "source_abs_phase_derivative_lower": min(
                distance_from_zero(source["phase_derivative"])
                for source in source_records),
            "source_newton_interior_margin_lower": min(
                min(lower(source["interval_newton"]) -
                    lower(source["trial_delta"]),
                    upper(source["trial_delta"]) -
                    upper(source["interval_newton"]))
                for source in source_records),
        })
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--terminal-executable", type=Path, required=True)
    parser.add_argument("--source-executable", type=Path, required=True)
    parser.add_argument("--workers", type=int,
                        default=max(1, min(28, os.cpu_count() or 1)))
    parser.add_argument("--predictor-workers", type=int,
                        default=max(1, min(16, (os.cpu_count() or 2) // 2)))
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--max-extra-r-depth", type=int, default=4)
    parser.add_argument("--parent-r-start", type=int, default=0)
    parser.add_argument("--parent-r-stop", type=int, default=8)
    parser.add_argument("--a2-start", type=int, default=0)
    parser.add_argument("--a2-stop", type=int, default=128)
    parser.add_argument("--epsilon-start", type=int, default=0)
    parser.add_argument("--epsilon-stop", type=int, default=4)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.workers < 1 or args.predictor_workers < 1 or args.timeout <= 0 \
            or args.max_extra_r_depth < 0:
        raise ValueError("workers/timeout must be positive and depth nonnegative")
    for executable in (args.terminal_executable, args.source_executable):
        if not executable.is_file() or not os.access(executable, os.X_OK):
            raise ValueError(f"executable is unavailable: {executable}")
    executable_hashes_before = {
        "terminal": sha256(args.terminal_executable),
        "source": sha256(args.source_executable),
    }

    r_range = checked_half_open(
        args.parent_r_start, args.parent_r_stop, 8, "parent r")
    a2_range = checked_half_open(args.a2_start, args.a2_stop, 128, "a2")
    epsilon_range = checked_half_open(
        args.epsilon_start, args.epsilon_stop, 4, "epsilon")
    parents = [(r, a2, epsilon) for r in r_range for a2 in a2_range
               for epsilon in epsilon_range]
    started = time.monotonic()

    coarse_jobs = [(parent, (), None) for parent in parents]
    coarse_results = run_many_terminal(
        coarse_jobs, args.terminal_executable, args.timeout, args.workers)
    records: list[dict[str, Any]] = []
    failed_parents: list[tuple[int, int, int]] = []
    diagnostics: list[dict[str, Any]] = []
    for parent, _path, returncode, terminal, detail in coarse_results:
        if terminal is not None:
            records.append({
                "cover_kind": "COARSE_PROVED_H10_TUBE",
                "parent": list(parent),
                "r_leaf": None,
                "extra_r_path": [],
                "source": None,
                "terminal": compact_terminal(terminal),
            })
        else:
            failed_parents.append(parent)
            diagnostics.append({
                "stage": "COARSE_EXPECTED_WRAPPING_FAILURE",
                "parent": list(parent), "returncode": returncode,
                "detail": detail,
            })

    refined_jobs = []
    for parent in failed_parents:
        for local_r in range(8):
            r_leaf = 8 * parent[0] + local_r
            refined_jobs.append((parent, r_split_path(r_leaf), None))
    refined_results = run_many_terminal(
        refined_jobs, args.terminal_executable, args.timeout, args.workers)
    tight_leaf_tasks: list[tuple[int, int, int, str]] = []
    for parent, path, returncode, terminal, detail in refined_results:
        local_r = r_local_index(path)
        leaf = (8 * parent[0] + local_r, parent[1], parent[2])
        if terminal is not None:
            records.append({
                "cover_kind": "REFINED_PROVED_H10_TUBE",
                "parent": list(parent),
                "r_leaf": list(leaf),
                "extra_r_path": [],
                "source": None,
                "terminal": compact_terminal(terminal),
            })
        else:
            tight_leaf_tasks.append((*leaf, TARGET_KIND))
            diagnostics.append({
                "stage": "REFINED_EXPECTED_WRAPPING_FAILURE",
                "parent": list(parent), "r_leaf": list(leaf),
                "returncode": returncode, "detail": detail,
            })

    predictors: list[Sequence[Any]] = []
    if tight_leaf_tasks:
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=args.predictor_workers) as pool:
            predictors = list(pool.map(
                affine_predictor, tight_leaf_tasks, chunksize=1))

    source_results: list[tuple[tuple[int, int, int], int,
                               dict[str, Any] | None, str]] = []
    if predictors:
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=args.workers) as pool:
            source_results = list(pool.map(
                lambda predictor: run_source_job(
                    predictor, args.source_executable, args.timeout),
                predictors))

    source_by_leaf: dict[tuple[int, int, int], dict[str, Any]] = {}
    hard_failures: list[dict[str, Any]] = []
    for leaf, returncode, source, detail in source_results:
        if source is None:
            hard_failures.append({
                "stage": "ROOT_CONDITIONED_SOURCE",
                "r_leaf": list(leaf), "returncode": returncode,
                "detail": detail,
            })
        else:
            source_by_leaf[leaf] = source

    tight_terminal_jobs = []
    tight_job_leaf = []
    for leaf, source in source_by_leaf.items():
        parent = (leaf[0] // 8, leaf[1], leaf[2])
        tight_terminal_jobs.append((
            parent, r_split_path(leaf[0]), source["root_eta"]))
        tight_job_leaf.append(leaf)
    tight_terminal_results = run_many_terminal(
        tight_terminal_jobs, args.terminal_executable,
        args.timeout, args.workers) if tight_terminal_jobs else []
    extra_r_front: list[tuple[tuple[int, int, int], dict[str, Any],
                             tuple[int, ...]]] = []
    extra_r_attempts = 0
    for leaf, result in zip(tight_job_leaf, tight_terminal_results):
        parent, _path, returncode, terminal, detail = result
        source = source_by_leaf[leaf]
        if terminal is not None:
            try:
                for parameter in ("r", "a2", "epsilon"):
                    require_interval_subset(
                        f"root-conditioned {parameter} box",
                        terminal["parameter_box"][parameter],
                        source["parameter_box"][parameter])
            except (KeyError, TypeError, ValueError) as error:
                terminal = None
                returncode = 92
                detail = str(error)
        if terminal is None:
            if args.max_extra_r_depth == 0:
                hard_failures.append({
                    "stage": "TIGHT_TERMINAL",
                    "parent": list(parent), "r_leaf": list(leaf),
                    "extra_r_path": [], "returncode": returncode,
                    "detail": detail,
                })
            else:
                extra_r_front.extend(((leaf, source, (0,)),
                                      (leaf, source, (1,))))
        else:
            records.append({
                "cover_kind": "REFINED_ROOT_CONDITIONED_TRUE_WU",
                "parent": list(parent),
                "r_leaf": list(leaf),
                "extra_r_path": [],
                "source": compact_source(source),
                "terminal": compact_terminal(terminal),
            })

    for depth in range(1, args.max_extra_r_depth + 1):
        if not extra_r_front:
            break
        jobs = []
        for leaf, source, bits in extra_r_front:
            split_path = r_split_path(leaf[0]) + tuple(
                ("r", half) for half in bits)
            parent = (leaf[0] // 8, leaf[1], leaf[2])
            jobs.append((parent, split_path, source["root_eta"]))
        results = run_many_terminal(
            jobs, args.terminal_executable, args.timeout, args.workers)
        extra_r_attempts += len(results)
        next_front = []
        for item, result in zip(extra_r_front, results):
            leaf, source, bits = item
            parent, _path, returncode, terminal, detail = result
            if terminal is not None:
                try:
                    for parameter in ("r", "a2", "epsilon"):
                        require_interval_subset(
                            f"root-conditioned {parameter} box",
                            terminal["parameter_box"][parameter],
                            source["parameter_box"][parameter])
                except (KeyError, TypeError, ValueError) as error:
                    terminal = None
                    returncode = 92
                    detail = str(error)
            if terminal is not None:
                records.append({
                    "cover_kind": (
                        "REFINED_ROOT_CONDITIONED_TRUE_WU_EXTRA_R_SPLIT"),
                    "parent": list(parent),
                    "r_leaf": list(leaf),
                    "extra_r_path": list(bits),
                    "source": compact_source(source),
                    "terminal": compact_terminal(terminal),
                })
            elif depth < args.max_extra_r_depth:
                next_front.extend(((leaf, source, bits + (0,)),
                                   (leaf, source, bits + (1,))))
            else:
                hard_failures.append({
                    "stage": "TIGHT_TERMINAL_EXTRA_R_COVER",
                    "parent": list(parent), "r_leaf": list(leaf),
                    "extra_r_path": list(bits), "returncode": returncode,
                    "detail": detail,
                })
        extra_r_front = next_front

    parent_counts: dict[tuple[int, int, int], int] = {
        parent: 0 for parent in parents}
    coarse_parent: set[tuple[int, int, int]] = set()
    refined_extra_r_paths: dict[
        tuple[int, int, int], dict[int, set[tuple[int, ...]]]] = {
            parent: {} for parent in failed_parents}
    for record in records:
        parent = tuple(record["parent"])
        parent_counts[parent] += 1
        if record["r_leaf"] is None:
            coarse_parent.add(parent)
        else:
            local_r = record["r_leaf"][0] % 8
            refined_extra_r_paths[parent].setdefault(local_r, set()).add(
                tuple(record["extra_r_path"]))
    coverage_errors = []
    for parent in parents:
        if parent in coarse_parent:
            if parent_counts[parent] != 1:
                coverage_errors.append(
                    f"coarse parent {parent} has {parent_counts[parent]} records")
        else:
            extra_r_cover = refined_extra_r_paths.get(parent, {})
            missing = [local_r for local_r in range(8)
                       if not binary_prefix_cover(
                           extra_r_cover.get(local_r, set()))]
            if missing:
                coverage_errors.append(
                    f"refined parent {parent} lacks complete extra-r cover "
                    f"on r leaves {missing}")

    full_requested = (
        args.parent_r_start == 0 and args.parent_r_stop == 8
        and args.a2_start == 0 and args.a2_stop == 128
        and args.epsilon_start == 0 and args.epsilon_stop == 4)
    executable_hashes_after = {
        "terminal": sha256(args.terminal_executable),
        "source": sha256(args.source_executable),
    }
    if executable_hashes_after != executable_hashes_before:
        hard_failures.append({
            "stage": "EXECUTABLE_CHANGED_DURING_RUN",
            "before": executable_hashes_before,
            "after": executable_hashes_after,
        })
    success = not hard_failures and not coverage_errors
    records.sort(key=lambda record: (
        record["parent"], -1 if record["r_leaf"] is None
        else record["r_leaf"][0], record["extra_r_path"]))
    document = {
        "schema_version": "rfsn-vdp-p2e-pole-axis-cover-scout/2",
        "status": "PASS" if success else "INCONCLUSIVE",
        "mathematical_status": (
            "COMPUTED_INTERVAL_DESIGN_PASS_FULL_BRIDGE"
            if success and full_requested else
            "COMPUTED_INTERVAL_DESIGN_PASS_REQUESTED_SUBCOVER"
            if success else "INCONCLUSIVE"),
        "claim_bearing": False,
        "scope": "P2E_AXIS_POLE_FIRST_HIT_AND_POSITIVE_CONE_ENTRY",
        "requested_parent_grid": {
            "r": [args.parent_r_start, args.parent_r_stop],
            "a2": [args.a2_start, args.a2_stop],
            "epsilon": [args.epsilon_start, args.epsilon_stop],
            "parent_count": len(parents),
            "full_4096_bridge_requested": full_requested,
        },
        "method": {
            "coarse_parent_attempts": len(coarse_jobs),
            "coarse_parent_passes": len(parents) - len(failed_parents),
            "refined_broad_attempts": len(refined_jobs),
            "root_conditioned_source_attempts": len(predictors),
            "adaptive_extra_r_terminal_attempts": extra_r_attempts,
            "max_extra_r_bisection_depth": args.max_extra_r_depth,
            "accepted_cover_records": len(records),
            "coarse_graph_tube": "|eta|<=1/200000",
            "refinement": (
                "eight exact canonical r-leaves after parent wrapping; "
                "only a still-failed root-conditioned leaf is bisected "
                "further in r"),
            "tightening": (
                "scalar interval Newton from rho=1e-6 true-Wu graph to "
                "the first rho=1e-2 hit; eta is then reinserted through "
                "the exact zero-energy source chart"),
            "terminal_event": (
                "first encounter U=-10 after the frozen U/Q/P global-turn "
                "sequence, using directed Poincare maps"),
            "terminal_routes": [
                "BASE", "V_STEPS_AFTER_V_EQUALS_ZERO",
                "TURN_REDUCED_U_TIME_AND_V_TIME_PASSAGES"],
            "response_binding": (
                "scope, requested cell and split path, route labels, exact "
                "parameter/phase/eta boxes, terminal section and speed"),
            "pole_cone": "x=10, y=-P, D=50+V, K=10y+Q",
            "p3_zero_action_entry_gate": "y>=13, D>=26, K>=131 at x=10",
            "first_hit_guard": (
                "from the first U=-.05 hit, independently take the first "
                "P minimum, next P maximum, and first later U=-.2 hit; "
                "on that same first-hit image verify y>2, D>0, K>0, "
                "a>1/2, gamma>0 and "
                "y^2-1/(4 gamma)>0; the resulting forward-invariant cone "
                "makes x strictly increasing through x=10"),
        },
        "aggregate_strict_bounds": aggregate(records) if records else {},
        "coverage_errors": coverage_errors,
        "hard_failures": hard_failures,
        "expected_wrapping_diagnostic_count": len(diagnostics),
        "executables": {
            "terminal": {
                "path": str(args.terminal_executable.resolve()),
                "sha256": executable_hashes_after["terminal"],
                "unchanged_during_run": (
                    executable_hashes_before["terminal"]
                    == executable_hashes_after["terminal"]),
            },
            "source": {
                "path": str(args.source_executable.resolve()),
                "sha256": executable_hashes_after["source"],
                "unchanged_during_run": (
                    executable_hashes_before["source"]
                    == executable_hashes_after["source"]),
            },
        },
        "elapsed_seconds": time.monotonic() - started,
        "records": records,
        "nonclaims": [
            "This design runner does not authenticate the CAPD/FILIB build.",
            "It proves neither the complete P2e incidence/census nor m_ax.",
            "The x=10 P3 inequalities are proved only on the zero-action "
            "axis; no off-axis P3 source window or mixed jets are proved.",
            "It proves no off-axis action collar, temporal stability, "
            "Turing selection, or canard statement.",
        ],
    }
    text = json.dumps(
        document, indent=2 if args.pretty else None, sort_keys=True,
        separators=None if args.pretty else (",", ":")) + "\n"
    if args.output is None:
        sys.stdout.write(text)
    else:
        args.output.write_text(text, encoding="utf-8")
        print(json.dumps({
            "status": document["status"],
            "mathematical_status": document["mathematical_status"],
            "output": str(args.output),
            "records": len(records),
            "hard_failures": len(hard_failures),
            "coverage_errors": len(coverage_errors),
            "elapsed_seconds": document["elapsed_seconds"],
        }, sort_keys=True))
    return 0 if success else 20


if __name__ == "__main__":
    raise SystemExit(main())
