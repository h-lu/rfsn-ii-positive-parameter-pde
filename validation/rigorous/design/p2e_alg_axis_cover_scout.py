#!/usr/bin/env python3
"""Adaptive nonclaim cover for the P2e algebraic zero-action channel.

The runner first tries each frozen parent with the complete proved graph tube.
Only an uncovered parent is split into its eight exact r-leaves and retried
with the same tube.  Only a still-uncovered r-leaf invokes the DIRECT_ALG
true-Wu source trace and is retried with its root_eta enclosure.  The two H10
prefilters have independent shallow depths; deep a2 refinement is reserved
for the root-conditioned stage.  Accepted a2 prefixes must form an exact cover
at whichever r level survives.

This is a design orchestrator.  It binds every accepted response to its
request, but it neither authenticates the executable build nor promotes the
result to a release certificate.
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


TARGET_KIND = "DIRECT_ALG"
SOURCE_PREFIX = "RESULT_JSON "
ALG_LABELS = ["ALG U STEP DOWN"] * 6 + ["U=-4 DOWN"]
ALG_TERMINAL_U = -Fraction(400, 23)
ALG_PHASE_LO = Fraction("5.7566913947049203") - Fraction(9, 80_000_000)
ALG_PHASE_HI = Fraction("5.7566913967948983") + Fraction(9, 80_000_000)
PROVED_ETA = (-1.0 / 200_000.0, 1.0 / 200_000.0)
PROVED_ETA_EXACT = (-Fraction(1, 200_000), Fraction(1, 200_000))


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


def bisect_fraction(box: tuple[Fraction, Fraction], half: int
                    ) -> tuple[Fraction, Fraction]:
    if half not in (0, 1):
        raise ValueError("split half must be zero or one")
    midpoint = (box[0] + box[1]) / 2
    return (box[0], midpoint) if half == 0 else (midpoint, box[1])


def r_split_path(local_r: int) -> tuple[int, int, int]:
    if local_r < 0 or local_r >= 8:
        raise ValueError("local r leaf must lie in [0,8)")
    return ((local_r >> 2) & 1, (local_r >> 1) & 1, local_r & 1)


def r_local_index(path: tuple[int, ...]) -> int:
    if len(path) != 3 or any(bit not in (0, 1) for bit in path):
        raise ValueError("a refined r path must contain three binary halves")
    return (path[0] << 2) + (path[1] << 1) + path[2]


def exact_binary_prefix_cover(paths: Iterable[tuple[int, ...]]) -> bool:
    """Return whether ``paths`` is a prefix-free exact binary cover."""

    leaves = set(paths)
    if not leaves or any(bit not in (0, 1) for path in leaves for bit in path):
        return False
    for path in leaves:
        if any(path[:length] in leaves for length in range(len(path))):
            return False

    def covers(prefix: tuple[int, ...]) -> bool:
        if prefix in leaves:
            return True
        descendants = [path for path in leaves
                       if path[:len(prefix)] == prefix]
        if not descendants:
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


def require_matching_interval(name: str, observed: Any,
                              expected: Sequence[Any]) -> None:
    observed_lower, observed_upper = interval_pair(observed, name)
    expected_lower, expected_upper = float(expected[0]), float(expected[1])
    observed_lower_exact = Fraction.from_float(observed_lower)
    observed_upper_exact = Fraction.from_float(observed_upper)
    expected_lower_exact = expected[0] if isinstance(
        expected[0], Fraction) else Fraction.from_float(expected_lower)
    expected_upper_exact = expected[1] if isinstance(
        expected[1], Fraction) else Fraction.from_float(expected_upper)
    tolerance = 1024.0 * sys.float_info.epsilon * max(
        1.0, abs(expected_lower), abs(expected_upper))
    tolerance_exact = Fraction.from_float(tolerance)
    if observed_lower_exact > expected_lower_exact \
            or observed_upper_exact < expected_upper_exact \
            or expected_lower_exact - observed_lower_exact > tolerance_exact \
            or observed_upper_exact - expected_upper_exact > tolerance_exact:
        raise ValueError(
            f"{name} does not match the requested interval: "
            f"{observed} versus [{expected_lower},{expected_upper}]")


def require_interval_sum(name: str, observed: Any, *terms: Any) -> None:
    lower = Fraction(0)
    upper = Fraction(0)
    for index, term in enumerate(terms):
        term_lower, term_upper = interval_pair(
            term, f"{name} term {index}")
        lower += Fraction.from_float(term_lower)
        upper += Fraction.from_float(term_upper)
    require_matching_interval(name, observed, (lower, upper))


def contains_zero(value: Any, name: str) -> tuple[float, float]:
    pair = interval_pair(value, name)
    if not pair[0] <= 0.0 <= pair[1]:
        raise ValueError(f"{name} does not contain zero")
    return pair


def interval_subset(inner: Any, outer: Any, name: str) -> None:
    inner_pair = interval_pair(inner, f"{name} inner")
    outer_pair = interval_pair(outer, f"{name} outer")
    if inner_pair[0] < outer_pair[0] or inner_pair[1] > outer_pair[1]:
        raise ValueError(f"{name} is not contained in its source certificate")


def source_parameter_boxes(leaf: tuple[int, int, int]
                           ) -> dict[str, tuple[Fraction, Fraction]]:
    return {
        "r": (Fraction(leaf[0], 3200), Fraction(leaf[0] + 1, 3200)),
        "a2": (Fraction(leaf[1] - 64, 256),
               Fraction(leaf[1] - 63, 256)),
        "epsilon": (Fraction(leaf[2] + 8, 10),
                    Fraction(leaf[2] + 9, 10)),
    }


def terminal_request_boxes(
        parent: tuple[int, int, int], r_path: tuple[int, ...],
        a2_path: tuple[int, ...]
        ) -> dict[str, tuple[Fraction, Fraction]]:
    boxes = {
        "r": (Fraction(parent[0], 400), Fraction(parent[0] + 1, 400)),
        "a2": (Fraction(parent[1] - 64, 256),
               Fraction(parent[1] - 63, 256)),
        "epsilon": (Fraction(parent[2] + 8, 10),
                    Fraction(parent[2] + 9, 10)),
    }
    for bit in r_path:
        boxes["r"] = bisect_fraction(boxes["r"], bit)
    for bit in a2_path:
        boxes["a2"] = bisect_fraction(boxes["a2"], bit)
    return boxes


def parse_source(stdout: str, expected_leaf: tuple[int, int, int],
                 predictor: Sequence[Any] | None = None
                 ) -> dict[str, Any]:
    lines = [line[len(SOURCE_PREFIX):] for line in stdout.splitlines()
             if line.startswith(SOURCE_PREFIX)]
    if len(lines) != 1:
        raise ValueError("source output lacks one RESULT_JSON record")
    value = json.loads(lines[0])
    validate_source_response(value, expected_leaf, predictor)
    return value


def validate_source_response(value: dict[str, Any],
                             leaf: tuple[int, int, int],
                             predictor: Sequence[Any] | None = None) -> None:
    if value.get("status") != "PASS":
        raise ValueError("source output is not PASS")
    if value.get("claim_bearing") is not False:
        raise ValueError("source claim status is not the nonclaim design scope")
    if value.get("scope") != "P2E_DIRECT_SOURCE_ROOT_CONDITIONED_LEAF" \
            or value.get("target_kind") != TARGET_KIND:
        raise ValueError("source scope or target kind does not match")
    if value.get("leaf") != list(leaf):
        raise ValueError("source leaf does not match the request")
    if value.get("split_path") != "":
        raise ValueError("source unexpectedly returned a split leaf")

    observed_parameters = value.get("parameter_box")
    if not isinstance(observed_parameters, dict):
        raise ValueError("source output lacks the parameter box")
    for parameter, box in source_parameter_boxes(leaf).items():
        require_matching_interval(
            f"source parameter {parameter}",
            observed_parameters.get(parameter), box)
    require_matching_interval(
        "source target phase", value.get("target_phase"),
        (ALG_PHASE_LO, ALG_PHASE_HI))
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
    if Fraction.from_float(eta[0]) < PROVED_ETA_EXACT[0] \
            or Fraction.from_float(eta[1]) > PROVED_ETA_EXACT[1]:
        raise ValueError("source root eta leaves the proved graph tube")
    if interval_pair(value.get("root_return_time"),
                     "source root return time")[0] <= 0.0:
        raise ValueError("source root return time is not positive")
    contains_zero(value.get("root_phase_residual"),
                  "source root phase residual")
    stable = value.get("root_stable_coordinates")
    if not isinstance(stable, list) or len(stable) != 2:
        raise ValueError("source output lacks two stable coordinates")
    interval_pair(stable[0], "source stable coordinate 0")
    interval_pair(stable[1], "source stable coordinate 1")


def terminal_argv(executable: Path, parent: tuple[int, int, int],
                  r_path: tuple[int, ...], a2_path: tuple[int, ...],
                  eta: Sequence[float] | None
                  ) -> list[str]:
    argv = [str(executable), "ALG", *(str(value) for value in parent)]
    for bit in r_path:
        if bit not in (0, 1):
            raise ValueError("r split bit must be zero or one")
        argv.extend(("r", str(bit)))
    for bit in a2_path:
        if bit not in (0, 1):
            raise ValueError("a2 split bit must be zero or one")
        argv.extend(("a2", str(bit)))
    if eta is not None:
        if len(eta) != 2:
            raise ValueError("eta enclosure must have two endpoints")
        argv.extend(("eta_box", repr(float(eta[0])), repr(float(eta[1]))))
    return argv


def parse_terminal(stdout: str) -> dict[str, Any]:
    value = json.loads(stdout)
    if not isinstance(value, dict) or value.get("status") != "PASS":
        raise ValueError("terminal output is not PASS")
    return value


def validate_terminal_response(
        value: dict[str, Any], parent: tuple[int, int, int],
        r_path: tuple[int, ...], a2_path: tuple[int, ...],
        eta: Sequence[float] | None) -> None:
    if value.get("scope") != "P2E_AXIS_ALG_TERMINAL_FIRST_HIT_CELL_SCOUT":
        raise ValueError("terminal scope does not match the ALG kernel")
    if value.get("claim_bearing") is not False:
        raise ValueError("terminal claim status is not the nonclaim design scope")
    expected_cell = {
        "r_index": parent[0], "a2_index": parent[1],
        "epsilon_index": parent[2],
    }
    if value.get("cell") != expected_cell:
        raise ValueError("terminal cell does not match the request")
    path_parts = [*(f"r:{bit}" for bit in r_path),
                  *(f"a2:{bit}" for bit in a2_path)]
    if eta is not None:
        path_parts.append("eta_box")
    expected_path = ",".join(path_parts)
    if value.get("split_path") != expected_path:
        raise ValueError("terminal split path does not match the request")
    if value.get("pole_route") != "BASE":
        raise ValueError("ALG terminal returned an unexpected pole route")

    observed_parameters = value.get("parameter_box")
    if not isinstance(observed_parameters, dict):
        raise ValueError("terminal output lacks the parameter box")
    for parameter, box in terminal_request_boxes(
            parent, r_path, a2_path).items():
        require_matching_interval(
            f"terminal parameter {parameter}",
            observed_parameters.get(parameter), box)
    require_matching_interval(
        "terminal phase", value.get("phase"),
        (ALG_PHASE_LO, ALG_PHASE_HI))
    require_matching_interval(
        "terminal eta", value.get("graph_error"),
        PROVED_ETA_EXACT if eta is None else eta)

    if value.get("event_sequence_labels") != ALG_LABELS:
        raise ValueError("terminal does not contain the seven frozen ALG legs")
    times = value.get("leg_return_times")
    residuals = value.get("leg_section_residuals")
    speeds = value.get("leg_section_speeds")
    if not isinstance(times, list) or len(times) != 7 \
            or not isinstance(residuals, list) or len(residuals) != 7 \
            or not isinstance(speeds, list) or len(speeds) != 7:
        raise ValueError("terminal does not contain seven leg diagnostics")
    for index, leg_time in enumerate(times):
        if interval_pair(leg_time, f"leg {index} return time")[0] <= 0.0:
            raise ValueError(f"leg {index} return time is not positive")
    for index, speed in enumerate(speeds):
        if interval_pair(speed, f"leg {index} speed")[1] >= 0.0:
            raise ValueError(f"leg {index} is not strictly downward")
    for index, residual in enumerate(residuals):
        contains_zero(residual, f"leg {index} section residual")
    if value.get("event_sequence_passed") is not True:
        raise ValueError("terminal event sequence is not PASS")

    finite = value.get("alg_finite_zero_energy_passage")
    if not isinstance(finite, dict) or finite.get("applicable") is not True \
            or finite.get("passed") is not True:
        raise ValueError("terminal lacks the finite ALG H=0 passage PASS")
    if finite.get("method") != "U_MINUS_ONE_TWENTIETH_H0_WQ_X_TIME":
        raise ValueError("terminal misidentifies the finite ALG passage")
    if finite.get("energy_reconstruction_identity") is not True \
            or finite.get("energy_reconstruction_identity_kind") != \
            "BY_EXACT_SOURCE_HAMILTONIAN_CONSERVATION":
        raise ValueError("finite ALG passage lacks its exact H=0 identity")
    require_matching_interval(
        "finite ALG seam x", finite.get("seam_x"),
        (Fraction(1, 20), Fraction(1, 20)))
    require_matching_interval(
        "finite ALG seam-time ledger", finite.get("seam_time"), times[0])
    if interval_pair(finite.get("seam_P"), "finite ALG seam P")[1] >= 0.0:
        raise ValueError("finite ALG seam does not have P<0")
    interval_pair(finite.get("seam_V_H0_intersection"),
                  "finite ALG seam H=0 V")
    contains_zero(finite.get("seam_energy_diagnostic"),
                  "finite ALG seam energy")
    contains_zero(finite.get("terminal_energy_diagnostic"),
                  "finite ALG terminal energy")
    if interval_pair(finite.get("clock"), "finite ALG clock")[0] <= 0.0:
        raise ValueError("finite ALG clock is not positive")
    if interval_pair(finite.get("dense_w_hull"),
                     "finite ALG dense w hull")[0] <= 0.0:
        raise ValueError("finite ALG passage does not preserve w>0")
    finite_steps = finite.get("dense_step_count")
    if not isinstance(finite_steps, int) or isinstance(finite_steps, bool) \
            or finite_steps <= 0:
        raise ValueError("finite ALG dense step count is not positive")
    x_nodes = finite.get("x_nodes")
    clock_nodes = finite.get("clock_nodes")
    finite_w_nodes = finite.get("w_nodes")
    finite_q_nodes = finite.get("q_nodes")
    if not all(isinstance(nodes, list) and len(nodes) == 6 for nodes in (
            x_nodes, clock_nodes, finite_w_nodes, finite_q_nodes)):
        raise ValueError("finite ALG passage lacks six exact slab nodes")
    finite_targets = (
        Fraction(1, 5), Fraction(1, 2), Fraction(1), Fraction(2),
        Fraction(3), Fraction(4))
    for index, (target, node, clock, w_node, q_node) in enumerate(zip(
            finite_targets, x_nodes, clock_nodes, finite_w_nodes,
            finite_q_nodes), start=1):
        require_matching_interval(
            f"finite ALG x node {index}", node, (target, target))
        if interval_pair(clock, f"finite ALG clock node {index}")[0] <= 0.0:
            raise ValueError(f"finite ALG clock node {index} is not positive")
        if interval_pair(w_node, f"finite ALG w node {index}")[0] <= 0.0:
            raise ValueError(f"finite ALG w node {index} is not positive")
        interval_pair(q_node, f"finite ALG q node {index}")
        require_interval_sum(
            f"finite ALG absolute-time node {index}", times[index],
            finite.get("seam_time"), clock)
    require_matching_interval(
        "finite ALG terminal clock ledger", finite.get("clock"),
        clock_nodes[-1])

    tail = value.get("alg_reduced_zero_energy_tail")
    if not isinstance(tail, dict) or tail.get("applicable") is not True \
            or tail.get("passed") is not True:
        raise ValueError("terminal lacks an applicable passing ALG w-tail")
    if tail.get("energy_reconstruction_identity") is not True:
        raise ValueError("terminal lacks the exact energy reconstruction")
    if tail.get("energy_reconstruction_identity_kind") != \
            "BY_EXACT_ZERO_ENERGY_FORMULA_CONSTRUCTION":
        raise ValueError("terminal misidentifies the energy construction")
    if tail.get("coordinate_kind") != \
            "W_Q_WITH_REDUNDANT_CANCELLATION_D" \
            or tail.get("cancellation_reconditioned_at_every_tau_node") \
            is not True:
        raise ValueError("ALG tail lacks the redundant cancellation route")
    require_matching_interval(
        "ALG seam-time ledger", tail.get("seam_time"), times[-1])
    if interval_pair(tail.get("seam_P"), "ALG seam P")[1] >= 0.0:
        raise ValueError("ALG seam does not have P<0")
    seam_q = interval_pair(tail.get("seam_Q"), "ALG seam Q")
    if seam_q[1] >= 0.0:
        raise ValueError("ALG seam does not have Q<0")
    require_matching_interval(
        "finite-to-tail ALG seam Q", tail.get("seam_Q"), finite_q_nodes[-1])
    if interval_pair(tail.get("tail_clock"), "ALG tail clock")[0] <= 0.0:
        raise ValueError("ALG tail clock is not positive")
    if interval_pair(tail.get("dense_w_hull"),
                     "ALG dense w hull")[0] <= 0.0:
        raise ValueError("ALG dense w hull does not stay positive")
    dense_steps = tail.get("dense_step_count")
    if not isinstance(dense_steps, int) or isinstance(dense_steps, bool) \
            or dense_steps <= 0:
        raise ValueError("ALG dense step count is not positive")

    tau_nodes = tail.get("tau_nodes")
    w_nodes = tail.get("w_nodes")
    q_nodes = tail.get("q_nodes")
    d_nodes = tail.get("d_nodes")
    cancellation_residuals = tail.get("cancellation_residuals")
    if not all(isinstance(nodes, list) and len(nodes) == 15
               for nodes in (tau_nodes, w_nodes, q_nodes, d_nodes,
                              cancellation_residuals)):
        raise ValueError("ALG tail does not contain 15 tau/w/q/d nodes")
    for index, node in enumerate(tau_nodes, start=1):
        expected = Fraction(77 * index, 400 * 15)
        require_matching_interval(
            f"tau node {index}", node, (expected, expected))
    for index, node in enumerate(w_nodes, start=1):
        if interval_pair(node, f"w node {index}")[0] <= 0.0:
            raise ValueError(f"w node {index} is not positive")
    for index, node in enumerate(q_nodes, start=1):
        if interval_pair(node, f"q node {index}")[1] >= 0.0:
            raise ValueError(f"q node {index} is not negative")
    for index, node in enumerate(d_nodes, start=1):
        interval_pair(node, f"d node {index}")
    for index, residual in enumerate(cancellation_residuals, start=1):
        contains_zero(residual, f"cancellation residual {index}")

    require_matching_interval(
        "terminal U", value.get("terminal_U"),
        (ALG_TERMINAL_U, ALG_TERMINAL_U))
    if interval_pair(value.get("terminal_P"), "terminal P")[1] >= 0.0:
        raise ValueError("terminal P is not strictly negative")
    contains_zero(value.get("section_residual"),
                  "terminal section residual")
    if value.get("terminal_speed_strictly_negative") is not True:
        raise ValueError("terminal speed is not strictly negative")
    if interval_pair(value.get("return_time"), "terminal return time")[0] \
            <= 0.0:
        raise ValueError("terminal return time is not positive")
    require_interval_sum(
        "ALG return-time ledger", value.get("return_time"),
        tail.get("seam_time"), tail.get("tail_clock"))


def source_argv(executable: Path, predictor: Sequence[Any]) -> list[str]:
    if len(predictor) != 9:
        raise ValueError("source predictor must have nine columns")
    return [
        str(executable), *(str(value) for value in predictor[:3]),
        *(str(value) for value in predictor[3:7]), str(predictor[8]),
        TARGET_KIND,
    ]


def predictor_job(task: tuple[int, int, int, str]
                  ) -> tuple[tuple[int, int, int], Sequence[Any] | None, str]:
    leaf = task[:3]
    try:
        predictor = affine_predictor(task)
        if tuple(int(value) for value in predictor[:3]) != leaf:
            raise ValueError("predictor leaf does not match its task")
        return leaf, predictor, ""
    except Exception as error:  # Process workers must return their diagnostic.
        return leaf, None, str(error)


def run_source_job(
        job: tuple[tuple[int, int, int], Sequence[Any]], executable: Path,
        timeout: float
        ) -> tuple[tuple[int, int, int], int, dict[str, Any] | None, str]:
    leaf, predictor = job
    returncode, stdout, stderr = run_process(
        source_argv(executable, predictor), timeout)
    if returncode == 0:
        try:
            return leaf, returncode, parse_source(stdout, leaf, predictor), ""
        except (KeyError, TypeError, ValueError,
                json.JSONDecodeError) as error:
            return leaf, 91, None, str(error)
    detail = (stderr or stdout).strip().splitlines()
    return leaf, returncode, None, detail[0] if detail else "no output"


TerminalJob = tuple[
    tuple[int, int, int], tuple[int, ...], tuple[int, ...],
    tuple[float, float] | None]


def run_terminal_job(
        job: TerminalJob, executable: Path, timeout: float
        ) -> tuple[tuple[int, int, int], tuple[int, ...], tuple[int, ...], int,
                   dict[str, Any] | None, str]:
    parent, r_path, a2_path, eta = job
    returncode, stdout, stderr = run_process(
        terminal_argv(executable, parent, r_path, a2_path, eta), timeout)
    if returncode == 0:
        try:
            value = parse_terminal(stdout)
            validate_terminal_response(
                value, parent, r_path, a2_path, eta)
            return parent, r_path, a2_path, returncode, value, ""
        except (KeyError, TypeError, ValueError,
                json.JSONDecodeError) as error:
            return parent, r_path, a2_path, 90, None, str(error)
    detail = (stderr or stdout).strip().splitlines()
    return parent, r_path, a2_path, returncode, None, (
        detail[0] if detail else "no output")


def adaptive_terminal_cover(
        domains: Sequence[tuple[tuple[int, int, int], tuple[int, ...],
                                tuple[float, float] | None]],
        executable: Path, timeout: float, workers: int, max_depth: int
        ) -> tuple[
            dict[tuple[tuple[int, int, int], tuple[int, ...]],
                 list[dict[str, Any]]],
            dict[tuple[tuple[int, int, int], tuple[int, ...]],
                 list[dict[str, Any]]],
            dict[str, Any]]:
    """Cover independent (parent,r-path) domains by a2 binary prefixes."""

    accepted: dict[
        tuple[tuple[int, int, int], tuple[int, ...]],
        list[dict[str, Any]]] = {
            (parent, r_path): [] for parent, r_path, _eta in domains}
    terminal_failures: dict[
        tuple[tuple[int, int, int], tuple[int, ...]],
        list[dict[str, Any]]] = {}
    front: list[TerminalJob] = [
        (parent, r_path, (), eta) for parent, r_path, eta in domains]
    attempts = 0
    split_failures = 0
    returncodes: dict[str, int] = {}
    for depth in range(max_depth + 1):
        if not front:
            break
        attempts += len(front)
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=workers) as pool:
            results = list(pool.map(
                lambda job: run_terminal_job(job, executable, timeout),
                front))
        next_front: list[TerminalJob] = []
        for job, result in zip(front, results):
            parent, r_path, a2_path, eta = job
            (_result_parent, _result_r_path, _result_a2_path,
             returncode, terminal, detail) = result
            key = (parent, r_path)
            if terminal is not None:
                accepted[key].append({
                    "parent": list(parent),
                    "r_path": list(r_path),
                    "r_leaf": (
                        8 * parent[0] + r_local_index(r_path)
                        if r_path else None),
                    "a2_path": list(a2_path),
                    "eta_mode": (
                        "ROOT_CONDITIONED_TRUE_WU"
                        if eta is not None else "PROVED_H10_TUBE"),
                    "eta": list(PROVED_ETA if eta is None else eta),
                    "terminal": compact_terminal(terminal),
                })
            elif depth < max_depth:
                split_failures += 1
                code = str(returncode)
                returncodes[code] = returncodes.get(code, 0) + 1
                next_front.extend((
                    (parent, r_path, a2_path + (0,), eta),
                    (parent, r_path, a2_path + (1,), eta),
                ))
            else:
                terminal_failures.setdefault(key, []).append({
                    "parent": list(parent), "r_path": list(r_path),
                    "a2_path": list(a2_path), "returncode": returncode,
                    "detail": detail,
                })
        front = next_front

    successful: dict[
        tuple[tuple[int, int, int], tuple[int, ...]],
        list[dict[str, Any]]] = {}
    failed: dict[
        tuple[tuple[int, int, int], tuple[int, ...]],
        list[dict[str, Any]]] = {}
    for key, candidate_records in accepted.items():
        paths = {tuple(record["a2_path"]) for record in candidate_records}
        if key not in terminal_failures and exact_binary_prefix_cover(paths):
            successful[key] = candidate_records
        else:
            failed[key] = terminal_failures.get(key, [{
                "parent": list(key[0]), "r_path": list(key[1]),
                "stage": "INEXACT_A2_PREFIX_SET",
            }])
    return successful, failed, {
        "terminal_attempts": attempts,
        "adaptive_wrapping_failures": split_failures,
        "adaptive_failure_returncodes": returncodes,
    }


def compact_source(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "parameter_box": value["parameter_box"],
        "root_eta": value["root_eta"],
        "trial_delta": value["trial_delta"],
        "interval_newton": value["interval_newton"],
        "phase_derivative": value["phase_derivative"],
        "log_radial_rate": value["log_radial_rate"],
        "phase_rate": value["phase_rate"],
        "root_return_time": value["root_return_time"],
        "root_phase_residual": value["root_phase_residual"],
    }


def compact_terminal(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "parameter_box": value["parameter_box"],
        "phase": value["phase"],
        "graph_error": value["graph_error"],
        "return_time": value["return_time"],
        "event_sequence_labels": value["event_sequence_labels"],
        "leg_return_times": value["leg_return_times"],
        "leg_section_residuals": value["leg_section_residuals"],
        "leg_section_speeds": value["leg_section_speeds"],
        "event_sequence_passed": value["event_sequence_passed"],
        "terminal_U": value["terminal_U"],
        "terminal_P": value["terminal_P"],
        "terminal_V": value["terminal_V"],
        "terminal_Q": value["terminal_Q"],
        "section_residual": value["section_residual"],
        "terminal_speed_strictly_negative":
            value["terminal_speed_strictly_negative"],
        "alg_finite_zero_energy_passage":
            value["alg_finite_zero_energy_passage"],
        "alg_reduced_zero_energy_tail":
            value["alg_reduced_zero_energy_tail"],
    }


def lower(value: Sequence[float]) -> float:
    return float(value[0])


def upper(value: Sequence[float]) -> float:
    return float(value[1])


def distance_from_zero(value: Sequence[float]) -> float:
    lo, hi = lower(value), upper(value)
    return 0.0 if lo <= 0.0 <= hi else min(abs(lo), abs(hi))


def aggregate(root_sources: Sequence[dict[str, Any]],
              records: Sequence[dict[str, Any]]) -> dict[str, float]:
    sources = [record["source"] for record in root_sources]
    terminals = [record["terminal"] for record in records]
    result: dict[str, float] = {}
    if sources:
        result.update({
            "source_abs_phase_derivative_lower": min(
                distance_from_zero(source["phase_derivative"])
                for source in sources),
            "source_log_radial_rate_lower": min(
                lower(source["log_radial_rate"]) for source in sources),
            "source_phase_rate_lower": min(
                lower(source["phase_rate"]) for source in sources),
            "source_newton_interior_margin_lower": min(
                min(lower(source["interval_newton"])
                    - lower(source["trial_delta"]),
                    upper(source["trial_delta"])
                    - upper(source["interval_newton"]))
                for source in sources),
            "source_eta_width_upper": max(
                upper(source["root_eta"]) - lower(source["root_eta"])
                for source in sources),
        })
    if terminals:
        finite_passages = [terminal["alg_finite_zero_energy_passage"]
                           for terminal in terminals]
        tails = [terminal["alg_reduced_zero_energy_tail"]
                 for terminal in terminals]
        result.update({
            "return_time_lower": min(
                lower(terminal["return_time"]) for terminal in terminals),
            "return_time_upper": max(
                upper(terminal["return_time"]) for terminal in terminals),
            "finite_dense_w_hull_lower": min(
                lower(passage["dense_w_hull"])
                for passage in finite_passages),
            "seam_P_upper": max(upper(tail["seam_P"]) for tail in tails),
            "tail_clock_lower": min(
                lower(tail["tail_clock"]) for tail in tails),
            "dense_w_hull_lower": min(
                lower(tail["dense_w_hull"]) for tail in tails),
            "w_node_lower": min(
                lower(node) for tail in tails for node in tail["w_nodes"]),
            "terminal_P_upper": max(
                upper(terminal["terminal_P"]) for terminal in terminals),
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
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--parent-h10-max-a2-depth", type=int, default=0)
    parser.add_argument("--r-leaf-h10-max-a2-depth", type=int, default=0)
    parser.add_argument("--max-a2-depth", type=int, default=5)
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
            or min(args.parent_h10_max_a2_depth,
                   args.r_leaf_h10_max_a2_depth,
                   args.max_a2_depth) < 0:
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

    # Stage 1: use the complete proved graph tube on each unsplit parent.
    coarse_domains = [(parent, (), None) for parent in parents]
    coarse_pass, coarse_fail, coarse_stats = adaptive_terminal_cover(
        coarse_domains, args.terminal_executable, args.timeout, args.workers,
        args.parent_h10_max_a2_depth)

    # Stage 2: only an uncovered parent is replaced by all eight exact
    # canonical r-leaves.  Successful stage-1 records are never duplicated.
    refined_domains = [
        (parent, r_split_path(local_r), None)
        for parent, _empty_path in coarse_fail for local_r in range(8)]
    refined_pass, refined_fail, refined_stats = adaptive_terminal_cover(
        refined_domains, args.terminal_executable, args.timeout, args.workers,
        args.r_leaf_h10_max_a2_depth) if refined_domains else ({}, {}, {
            "terminal_attempts": 0, "adaptive_wrapping_failures": 0,
            "adaptive_failure_returncodes": {}})

    # Stage 3: true-Wu source conditioning is paid only for r-leaves that
    # still fail with the complete H10 tube.
    failed_leaf_keys = sorted(refined_fail)
    tasks = [
        (8 * parent[0] + r_local_index(r_path), parent[1], parent[2],
         TARGET_KIND)
        for parent, r_path in failed_leaf_keys]
    predictor_results = []
    if tasks:
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=args.predictor_workers) as pool:
            predictor_results = list(pool.map(
                predictor_job, tasks,
                chunksize=max(1, len(tasks) // (args.predictor_workers * 8))))

    hard_failures: list[dict[str, Any]] = []
    predictor_jobs: list[tuple[tuple[int, int, int], Sequence[Any]]] = []
    for leaf, predictor, detail in predictor_results:
        if predictor is None:
            hard_failures.append({
                "stage": "FLOATING_PREDICTOR", "r_leaf": list(leaf),
                "detail": detail,
            })
        else:
            predictor_jobs.append((leaf, predictor))

    source_results = []
    if predictor_jobs:
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=args.workers) as pool:
            source_results = list(pool.map(
                lambda job: run_source_job(
                    job, args.source_executable, args.timeout),
                predictor_jobs))
    source_by_leaf: dict[tuple[int, int, int], dict[str, Any]] = {}
    for leaf, returncode, source, detail in source_results:
        if source is None:
            hard_failures.append({
                "stage": "ROOT_CONDITIONED_SOURCE", "r_leaf": list(leaf),
                "returncode": returncode, "detail": detail,
            })
        else:
            source_by_leaf[leaf] = source

    tight_domains = []
    source_key_by_leaf = {
        (8 * parent[0] + r_local_index(r_path), parent[1], parent[2]):
        (parent, r_path)
        for parent, r_path in failed_leaf_keys}
    root_sources: list[dict[str, Any]] = []
    for leaf, source in source_by_leaf.items():
        if leaf not in source_key_by_leaf:
            hard_failures.append({
                "stage": "UNREQUESTED_ROOT_CONDITIONED_SOURCE",
                "r_leaf": list(leaf),
            })
            continue
        parent, r_path = source_key_by_leaf[leaf]
        root_eta = interval_pair(source["root_eta"], "source root eta")
        tight_domains.append((parent, r_path, root_eta))
        root_sources.append({
            "parent": list(parent), "r_path": list(r_path),
            "r_leaf": leaf[0], "source": compact_source(source),
        })
    tight_pass, tight_fail, tight_stats = adaptive_terminal_cover(
        tight_domains, args.terminal_executable, args.timeout, args.workers,
        args.max_a2_depth) if tight_domains else ({}, {}, {
            "terminal_attempts": 0, "adaptive_wrapping_failures": 0,
            "adaptive_failure_returncodes": {}})
    source_by_key = {
        source_key_by_leaf[leaf]: source
        for leaf, source in source_by_leaf.items()
        if leaf in source_key_by_leaf}
    for key, values in list(tight_pass.items()):
        source_parameters = source_by_key[key]["parameter_box"]
        try:
            for record in values:
                terminal_parameters = record["terminal"]["parameter_box"]
                for parameter in ("r", "a2", "epsilon"):
                    interval_subset(
                        terminal_parameters[parameter],
                        source_parameters[parameter],
                        f"root-conditioned {parameter} box")
        except (KeyError, TypeError, ValueError) as error:
            tight_fail[key] = [{
                "parent": list(key[0]), "r_path": list(key[1]),
                "stage": "SOURCE_TERMINAL_PARAMETER_CONTAINMENT",
                "detail": str(error),
            }]
            del tight_pass[key]
    for failures in tight_fail.values():
        for failure in failures:
            hard_failures.append({
                "stage": "ROOT_CONDITIONED_ALG_TERMINAL_A2_COVER",
                **failure,
            })

    records: list[dict[str, Any]] = []
    for key, values in coarse_pass.items():
        for record in values:
            record["cover_kind"] = "PARENT_R_WITH_A2_PREFIX"
            records.append(record)
    failed_parents = {parent for parent, _path in coarse_fail}
    for parent in failed_parents:
        for local_r in range(8):
            key = (parent, r_split_path(local_r))
            values = refined_pass.get(key, tight_pass.get(key, []))
            for record in values:
                record["cover_kind"] = (
                    "R_LEAF_TRUE_WU_WITH_A2_PREFIX"
                    if key in tight_pass else
                    "R_LEAF_H10_WITH_A2_PREFIX")
                records.append(record)

    coverage_errors = []
    for parent in parents:
        coarse_paths = {
            tuple(record["a2_path"]) for record in records
            if tuple(record["parent"]) == parent
            and record["r_leaf"] is None}
        if exact_binary_prefix_cover(coarse_paths):
            if any(tuple(record["parent"]) == parent
                   and record["r_leaf"] is not None for record in records):
                coverage_errors.append(
                    f"parent {parent} mixes parent and r-leaf covers")
            continue
        missing = []
        for local_r in range(8):
            leaf = 8 * parent[0] + local_r
            paths = {
                tuple(record["a2_path"]) for record in records
                if tuple(record["parent"]) == parent
                and record["r_leaf"] == leaf}
            if not exact_binary_prefix_cover(paths):
                missing.append(local_r)
        if missing:
            coverage_errors.append(
                f"parent {parent} lacks exact a2 cover on r leaves {missing}")

    root_sources.sort(key=lambda record: (
        record["parent"], record["r_path"]))
    records.sort(key=lambda record: (
        record["parent"], -1 if record["r_leaf"] is None
        else record["r_leaf"], record["a2_path"]))
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
    runner_path = Path(__file__).resolve()
    predictor_path = Path(sys.modules[affine_predictor.__module__].__file__).resolve()
    stage_stats = {
        "parent_h10": coarse_stats,
        "r_leaf_h10": refined_stats,
        "r_leaf_root_conditioned": tight_stats,
    }
    document = {
        "schema_version": "rfsn-vdp-p2e-alg-axis-cover-scout/3",
        "status": "PASS" if success else "INCONCLUSIVE",
        "mathematical_status": (
            "COMPUTED_INTERVAL_DESIGN_PASS_FULL_BRIDGE"
            if success and full_requested else
            "COMPUTED_INTERVAL_DESIGN_PASS_REQUESTED_SUBCOVER"
            if success else "INCONCLUSIVE"),
        "claim_bearing": False,
        "scope": "P2E_AXIS_ALG_FIRST_HIT_ZERO_ENERGY_TAIL_A2_COVER",
        "requested_parent_grid": {
            "r": [args.parent_r_start, args.parent_r_stop],
            "a2": [args.a2_start, args.a2_stop],
            "epsilon": [args.epsilon_start, args.epsilon_stop],
            "parent_count": len(parents),
            "full_4096_bridge_requested": full_requested,
        },
        "method": {
            "source_leaf_attempts": len(tasks),
            "source_leaf_passes": len(source_by_leaf),
            "root_conditioned_r_leaves": len(root_sources),
            "parent_h10_passes": len(coarse_pass),
            "parent_h10_failures_refined_in_r": len(coarse_fail),
            "r_leaf_h10_passes": len(refined_pass),
            "r_leaf_h10_failures_root_conditioned": len(refined_fail),
            "terminal_stage_statistics": stage_stats,
            "a2_bisection_depths": {
                "parent_h10": args.parent_h10_max_a2_depth,
                "r_leaf_h10": args.r_leaf_h10_max_a2_depth,
                "r_leaf_root_conditioned": args.max_a2_depth,
            },
            "accepted_cover_records": len(records),
            "source_refinement": (
                "parent H10 tube first; then eight exact r-leaves only for "
                "an uncovered parent; scalar true-Wu root_eta only for an "
                "r-leaf still uncovered with the H10 tube"),
            "terminal_refinement": "a2 binary bisection only",
            "terminal_event_chain": ALG_LABELS,
            "weighted_tail": (
                "exact H=0 finite (W,Q) x-passage followed by a (w,q,d) "
                "redundant-cancellation tail on 15 exact tau slabs from "
                "U=-4 to U=-400/23"),
            "response_binding": (
                "source and terminal scope, cell/leaf, split path, exact "
                "parameter/phase/eta boxes, seven directions, positive "
                "w-tail, nodes, terminal section and speed"),
        },
        "aggregate_strict_bounds": aggregate(root_sources, records),
        "coverage_errors": coverage_errors,
        "hard_failures": hard_failures,
        "artifacts": {
            "runner": {"path": str(runner_path), "sha256": sha256(runner_path)},
            "predictor": {
                "path": str(predictor_path), "sha256": sha256(predictor_path)},
            "terminal_executable": {
                "path": str(args.terminal_executable.resolve()),
                "sha256": executable_hashes_after["terminal"],
                "unchanged_during_run": (
                    executable_hashes_before["terminal"]
                    == executable_hashes_after["terminal"])},
            "source_executable": {
                "path": str(args.source_executable.resolve()),
                "sha256": executable_hashes_after["source"],
                "unchanged_during_run": (
                    executable_hashes_before["source"]
                    == executable_hashes_after["source"])},
        },
        "elapsed_seconds": time.monotonic() - started,
        "root_conditioned_sources": root_sources,
        "records": records,
        "nonclaims": [
            "This design runner does not authenticate the CAPD/FILIB build.",
            "It does not prove the complete P2e incidence/census or m_ax.",
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
            "output": str(args.output), "records": len(records),
            "root_conditioned_sources": len(root_sources),
            "hard_failures": len(hard_failures),
            "coverage_errors": len(coverage_errors),
            "elapsed_seconds": document["elapsed_seconds"],
        }, sort_keys=True))
    return 0 if success else 20


if __name__ == "__main__":
    raise SystemExit(main())
