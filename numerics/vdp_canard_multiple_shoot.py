"""Finite-r canard coincidence by segmented exact-IVP multiple shooting.

The saved Appendix-A.3 collocation orbit is used only to initialize interior
nodes.  Every claim-bearing residual is rebuilt from DOP853 flows of the same
exact finite-r central-chart ODE.  The frozen problem has a fixed left
boundary on ``H2=0`` and asks for a terminal hit of ``p2=q2=0``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

try:
    from numerics.vdp_canard_slow_trace import (
        _localized_a3_half,
        _outside_half,
        critical_graph,
        load_configuration as load_slow_configuration,
    )
    from numerics.vdp_canard_splitting_scout import central_hamiltonian
except ModuleNotFoundError:  # Direct ``python numerics/<script>.py``.
    from vdp_canard_slow_trace import (  # type: ignore[no-redef]
        _localized_a3_half,
        _outside_half,
        critical_graph,
        load_configuration as load_slow_configuration,
    )
    from vdp_canard_splitting_scout import (  # type: ignore[no-redef]
        central_hamiltonian,
    )


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent
CONFIG_PATH = HERE / "config" / "vdp_canard_multiple_shoot_v1.json"
RESULT_PATH = HERE / "results" / "vdp_canard_multiple_shoot" / "report.json"


class MultipleShootError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_configuration(path: Path = CONFIG_PATH) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != "vdp-canard-multiple-shoot-config/1":
        raise MultipleShootError("configuration schema changed")
    if data.get("freeze_status") != (
        "FROZEN_BEFORE_RETAINED_MULTIPLE_SHOOT_RUN"
    ):
        raise MultipleShootError("configuration is not pre-run frozen")
    if data.get("claim_bearing") is not False:
        raise MultipleShootError("floating multiple shooting cannot be claim-bearing")
    parameters = data["parameters"]
    if parameters["epsilon"] != 1.0 or parameters["r"] != 0.08:
        raise MultipleShootError("the frozen (epsilon,r) slice changed")
    if data["multiple_shooting"]["segments"] != 80:
        raise MultipleShootError("the frozen segment count changed")
    return data


def central_field(state: np.ndarray, *, r: float, a2: float) -> np.ndarray:
    u, p, v, q = state
    return np.asarray(
        [p, u * u - v + r * r * u**3 / 3.0, q, u - r * a2],
        dtype=np.float64,
    )


def central_jacobian(state: np.ndarray, *, r: float) -> np.ndarray:
    u = float(state[0])
    return np.asarray(
        [
            [0.0, 1.0, 0.0, 0.0],
            [2.0 * u + r * r * u * u, 0.0, -1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0, 0.0],
        ],
        dtype=np.float64,
    )


def left_state_and_derivative(
    *, u: float, q: float, a2: float, r: float
) -> tuple[np.ndarray, np.ndarray]:
    v = float(critical_graph(u, r=r))
    radicand = q * q - 2.0 * (u - r * a2) * v + 2.0 * u**3 / 3.0
    radicand += r * r * u**4 / 6.0
    if not math.isfinite(radicand) or radicand <= 0.0:
        raise MultipleShootError(f"invalid negative-root radicand {radicand}")
    p = -math.sqrt(radicand)
    state = np.asarray([u, p, v, q], dtype=np.float64)
    derivative = np.asarray([0.0, r * v / p, 0.0, 0.0])
    return state, derivative


@dataclass(frozen=True)
class FlowResult:
    end: np.ndarray
    state_derivative: np.ndarray
    parameter_derivative: np.ndarray
    function_evaluations: int


def flow_with_variation(
    start: np.ndarray,
    *,
    duration: float,
    r: float,
    a2: float,
    rtol: float,
    atol: float,
    max_step: float,
) -> FlowResult:
    initial = np.concatenate(
        (start, np.eye(4, dtype=np.float64).ravel(), np.zeros(4))
    )

    def augmented(_time: float, value: np.ndarray) -> np.ndarray:
        state = value[:4]
        matrix = value[4:20].reshape(4, 4)
        parameter = value[20:24]
        derivative = central_jacobian(state, r=r)
        forcing = np.asarray([0.0, 0.0, 0.0, -r])
        return np.concatenate(
            (
                central_field(state, r=r, a2=a2),
                (derivative @ matrix).ravel(),
                derivative @ parameter + forcing,
            )
        )

    solution = solve_ivp(
        augmented,
        (0.0, duration),
        initial,
        method="DOP853",
        rtol=rtol,
        atol=atol,
        max_step=max_step,
    )
    if not solution.success:
        raise MultipleShootError(f"segment IVP failed: {solution.message}")
    final = np.asarray(solution.y[:, -1], dtype=np.float64)
    return FlowResult(
        end=final[:4],
        state_derivative=final[4:20].reshape(4, 4),
        parameter_derivative=final[20:24],
        function_evaluations=int(solution.nfev),
    )


class ShootingEvaluator:
    """Residual/Jacobian evaluator with exact-IVP segment flows."""

    def __init__(self, config: dict[str, Any], *, fixed_a2: float | None = None):
        self.config = config
        self.fixed_a2 = fixed_a2
        self.segments = int(config["multiple_shooting"]["segments"])
        self.scales = np.asarray(
            config["multiple_shooting"]["state_residual_scales"],
            dtype=np.float64,
        )
        self.endpoint_scales = np.asarray(
            config["multiple_shooting"]["endpoint_residual_scales"],
            dtype=np.float64,
        )
        self._cache_x: np.ndarray | None = None
        self._cache: dict[str, Any] | None = None

    @property
    def parameter_columns(self) -> int:
        return 2 if self.fixed_a2 is None else 1

    def unpack(self, unknown: np.ndarray) -> tuple[float, float, np.ndarray]:
        if self.fixed_a2 is None:
            a2 = float(unknown[0])
            log_time = float(unknown[1])
            offset = 2
        else:
            a2 = float(self.fixed_a2)
            log_time = float(unknown[0])
            offset = 1
        nodes = np.asarray(unknown[offset:], dtype=np.float64).reshape(
            self.segments - 1, 4
        )
        return a2, math.exp(log_time), nodes

    def evaluate(self, unknown: np.ndarray) -> dict[str, Any]:
        if self._cache_x is not None and np.array_equal(unknown, self._cache_x):
            assert self._cache is not None
            return self._cache
        shooting = self.config["multiple_shooting"]
        parameters = self.config["parameters"]
        a2, total_time, interior = self.unpack(unknown)
        duration = total_time / self.segments
        left, left_a2 = left_state_and_derivative(
            u=float(parameters["outer_u2"]),
            q=float(parameters["outer_q2"]),
            a2=a2,
            r=float(parameters["r"]),
        )
        nodes = np.vstack((left, interior))
        n_continuity = 4 * (self.segments - 1)
        endpoint_count = 2 if self.fixed_a2 is None else 1
        residual = np.empty(n_continuity + endpoint_count)
        jacobian = np.zeros((residual.size, unknown.size))
        raw_defects: list[np.ndarray] = []
        flows: list[FlowResult] = []
        r_value = float(parameters["r"])
        for index in range(self.segments):
            result = flow_with_variation(
                nodes[index],
                duration=duration,
                r=r_value,
                a2=a2,
                rtol=float(shooting["ivp_rtol"]),
                atol=float(shooting["ivp_atol"]),
                max_step=float(shooting["ivp_max_step"]),
            )
            flows.append(result)
            time_column = central_field(result.end, r=r_value, a2=a2) * duration
            if index < self.segments - 1:
                row = slice(4 * index, 4 * (index + 1))
                raw = result.end - nodes[index + 1]
                raw_defects.append(raw)
                residual[row] = raw / self.scales
                if self.fixed_a2 is None:
                    if index == 0:
                        a2_column = (
                            result.state_derivative @ left_a2
                            + result.parameter_derivative
                        )
                    else:
                        a2_column = result.parameter_derivative
                    jacobian[row, 0] = a2_column / self.scales
                    jacobian[row, 1] = time_column / self.scales
                    if index > 0:
                        start_column = 2 + 4 * (index - 1)
                        jacobian[row, start_column : start_column + 4] = (
                            result.state_derivative / self.scales[:, None]
                        )
                    next_column = 2 + 4 * index
                else:
                    jacobian[row, 0] = time_column / self.scales
                    if index > 0:
                        start_column = 1 + 4 * (index - 1)
                        jacobian[row, start_column : start_column + 4] = (
                            result.state_derivative / self.scales[:, None]
                        )
                    next_column = 1 + 4 * index
                jacobian[row, next_column : next_column + 4] = (
                    -np.eye(4) / self.scales[:, None]
                )
            else:
                endpoint_indices = [1, 3] if self.fixed_a2 is None else [1]
                for local_row, state_index in enumerate(endpoint_indices):
                    row_index = n_continuity + local_row
                    scale = self.endpoint_scales[local_row]
                    residual[row_index] = result.end[state_index] / scale
                    if self.fixed_a2 is None:
                        jacobian[row_index, 0] = (
                            result.parameter_derivative[state_index] / scale
                        )
                        jacobian[row_index, 1] = time_column[state_index] / scale
                        start_column = 2 + 4 * (index - 1)
                    else:
                        jacobian[row_index, 0] = time_column[state_index] / scale
                        start_column = 1 + 4 * (index - 1)
                    jacobian[
                        row_index, start_column : start_column + 4
                    ] = result.state_derivative[state_index] / scale
        cache = {
            "a2": a2,
            "total_time": total_time,
            "nodes": nodes,
            "flows": flows,
            "residual": residual,
            "jacobian": jacobian,
            "raw_defects": raw_defects,
            "terminal_state": flows[-1].end,
        }
        self._cache_x = np.array(unknown, copy=True)
        self._cache = cache
        return cache

    def residual(self, unknown: np.ndarray) -> np.ndarray:
        return self.evaluate(unknown)["residual"]

    def jacobian(self, unknown: np.ndarray) -> np.ndarray:
        return self.evaluate(unknown)["jacobian"]


def _initial_guess(config: dict[str, Any]) -> tuple[np.ndarray, dict[str, Any]]:
    slow = load_slow_configuration()
    outside = _outside_half(slow)
    candidate = _localized_a3_half(slow, outside)
    segments = int(config["multiple_shooting"]["segments"])
    sample = np.arange(1, segments, dtype=np.float64) / segments
    nodes = np.asarray(candidate.sol(sample), dtype=np.float64).T
    unknown = np.concatenate(
        ([float(candidate.p[1]), math.log(float(candidate.p[0]))], nodes.ravel())
    )
    return unknown, {
        "source": "recomputed q2=-80 Appendix-A.3 collocation branch",
        "accepted_as_evidence": False,
        "a2": float(candidate.p[1]),
        "total_time": float(candidate.p[0]),
        "max_interval_rms_relative_residual": float(
            np.max(candidate.rms_residuals)
        ),
    }


def _bounds(config: dict[str, Any], *, fixed: bool) -> tuple[np.ndarray, np.ndarray]:
    segments = int(config["multiple_shooting"]["segments"])
    dimension = (1 if fixed else 2) + 4 * (segments - 1)
    lower = np.full(dimension, -np.inf)
    upper = np.full(dimension, np.inf)
    time_bounds = config["multiple_shooting"]["total_flight_time_bounds"]
    time_column = 0 if fixed else 1
    lower[time_column], upper[time_column] = map(math.log, time_bounds)
    if not fixed:
        lower[0], upper[0] = config["parameters"]["a2_interval"]
    return lower, upper


def _solve(
    evaluator: ShootingEvaluator, initial: np.ndarray
) -> tuple[Any, dict[str, Any]]:
    settings = evaluator.config["multiple_shooting"]
    bounds = _bounds(evaluator.config, fixed=evaluator.fixed_a2 is not None)
    result = least_squares(
        evaluator.residual,
        initial,
        jac=evaluator.jacobian,
        bounds=bounds,
        x_scale="jac",
        xtol=float(settings["least_squares_xtol"]),
        ftol=float(settings["least_squares_ftol"]),
        gtol=float(settings["least_squares_gtol"]),
        max_nfev=int(settings["least_squares_max_nfev"]),
        verbose=0,
    )
    evaluated = evaluator.evaluate(result.x)
    return result, evaluated


def _tight_segment_replay(
    config: dict[str, Any], evaluated: dict[str, Any]
) -> dict[str, Any]:
    settings = config["tight_segment_replay"]
    parameters = config["parameters"]
    nodes = evaluated["nodes"]
    duration = evaluated["total_time"] / int(config["multiple_shooting"]["segments"])
    defects: list[np.ndarray] = []
    terminal = None
    evaluations = 0
    for index, start in enumerate(nodes):
        result = flow_with_variation(
            start,
            duration=duration,
            r=float(parameters["r"]),
            a2=float(evaluated["a2"]),
            rtol=float(settings["ivp_rtol"]),
            atol=float(settings["ivp_atol"]),
            max_step=float(settings["ivp_max_step"]),
        )
        evaluations += result.function_evaluations
        if index < nodes.shape[0] - 1:
            defects.append(result.end - nodes[index + 1])
        else:
            terminal = result.end
    assert terminal is not None
    return {
        "continuity_inf": float(np.max(np.abs(defects))),
        "terminal_state": terminal.tolist(),
        "terminal_abs_pq": float(np.max(np.abs(terminal[[1, 3]]))),
        "function_evaluations": evaluations,
    }


def _fixed_family_unknown(coincidence: np.ndarray) -> np.ndarray:
    return np.concatenate(([coincidence[1]], coincidence[2:]))


def _derivative_checks(
    config: dict[str, Any], coincidence: np.ndarray, full: dict[str, Any]
) -> dict[str, Any]:
    full_jacobian = np.asarray(full["jacobian"])
    fixed_jacobian = full_jacobian[:-1, 1:]
    parameter_column = full_jacobian[:-1, 0]
    condition_number = float(np.linalg.cond(fixed_jacobian))
    tangent = -np.linalg.solve(fixed_jacobian, parameter_column)
    splitting_gradient = full_jacobian[-1, 1:]
    implicit = float(full_jacobian[-1, 0] + splitting_gradient @ tangent)
    center_a2 = float(full["a2"])
    center_fixed = _fixed_family_unknown(coincidence)
    rows: list[dict[str, Any]] = []
    for step in config["splitting_derivative"]["symmetric_steps"]:
        samples: dict[int, tuple[Any, dict[str, Any]]] = {}
        for sign in (-1, 1):
            evaluator = ShootingEvaluator(config, fixed_a2=center_a2 + sign * step)
            samples[sign] = _solve(evaluator, center_fixed)
        minus_result, minus = samples[-1]
        plus_result, plus = samples[1]
        difference = (
            float(plus["terminal_state"][3])
            - float(minus["terminal_state"][3])
        ) / (2.0 * step)
        mismatch = abs(difference - implicit) / max(
            abs(difference), abs(implicit), 1.0
        )
        rows.append(
            {
                "step": step,
                "minus_optimizer_success": bool(minus_result.success),
                "plus_optimizer_success": bool(plus_result.success),
                "minus_scaled_residual_inf": float(
                    np.max(np.abs(minus["residual"]))
                ),
                "plus_scaled_residual_inf": float(
                    np.max(np.abs(plus["residual"]))
                ),
                "minus_splitting": float(minus["terminal_state"][3]),
                "plus_splitting": float(plus["terminal_state"][3]),
                "symmetric_difference": difference,
                "relative_mismatch_from_implicit": mismatch,
            }
        )
    return {
        "fixed_family_jacobian_condition_2": condition_number,
        "implicit_derivative": implicit,
        "finite_differences": rows,
    }


def build_report(config_path: Path = CONFIG_PATH) -> dict[str, Any]:
    config = load_configuration(config_path)
    initial, initialization = _initial_guess(config)
    evaluator = ShootingEvaluator(config)
    initial_evaluated = evaluator.evaluate(initial)
    solution, evaluated = _solve(evaluator, initial)
    tight = _tight_segment_replay(config, evaluated)
    derivatives = _derivative_checks(config, solution.x, evaluated)
    raw_continuity = float(np.max(np.abs(evaluated["raw_defects"])))
    terminal = np.asarray(evaluated["terminal_state"])
    nodes = np.asarray(evaluated["nodes"])
    hamiltonians = np.asarray(
        [
            central_hamiltonian(
                node,
                r=float(config["parameters"]["r"]),
                a2=float(evaluated["a2"]),
            )
            for node in nodes
        ]
    )
    acceptance = config["retained_acceptance"]
    a2_low, a2_high = config["parameters"]["a2_interval"]
    root_checks = {
        "optimizer_success": bool(solution.success),
        "scaled_residual_inf": float(np.max(np.abs(evaluated["residual"]))),
        "raw_continuity_inf": raw_continuity,
        "terminal_abs_pq": float(np.max(np.abs(terminal[[1, 3]]))),
        "tight_segment_replay_inf": tight["continuity_inf"],
        "hamiltonian_node_max_abs": float(np.max(np.abs(hamiltonians))),
        "a2_strictly_inside_interval": bool(
            a2_low < float(evaluated["a2"]) < a2_high
        ),
    }
    root_pass = bool(
        root_checks["optimizer_success"]
        and root_checks["scaled_residual_inf"]
        <= acceptance["scaled_residual_inf_max"]
        and root_checks["raw_continuity_inf"]
        <= acceptance["raw_continuity_inf_max"]
        and root_checks["terminal_abs_pq"] <= acceptance["terminal_abs_max"]
        and root_checks["tight_segment_replay_inf"]
        <= acceptance["tight_segment_replay_inf_max"]
        and root_checks["hamiltonian_node_max_abs"]
        <= acceptance["hamiltonian_node_abs_max"]
        and root_checks["a2_strictly_inside_interval"]
    )
    derivative_pass = bool(
        abs(derivatives["implicit_derivative"])
        >= config["splitting_derivative"]["simple_zero_derivative_abs_min"]
        and all(
            row["minus_optimizer_success"]
            and row["plus_optimizer_success"]
            and row["minus_scaled_residual_inf"]
            <= acceptance["scaled_residual_inf_max"]
            and row["plus_scaled_residual_inf"]
            <= acceptance["scaled_residual_inf_max"]
            and row["relative_mismatch_from_implicit"]
            <= config["splitting_derivative"]["relative_implicit_vs_fd_max"]
            for row in derivatives["finite_differences"]
        )
    )
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPOSITORY,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = "UNKNOWN"
    status = (
        "COMPUTED/E1_BOUNDARY_SELECTED_MULTIPLE_SHOOT_SIMPLE_ZERO_CANDIDATE"
        if root_pass and derivative_pass
        else "INCONCLUSIVE_MULTIPLE_SHOOT_ACCEPTANCE_OR_DERIVATIVE_FAILED"
    )
    return {
        "schema_version": "vdp-canard-multiple-shoot-report/1",
        "evidence_status": status,
        "claim_bearing": False,
        "configuration": {
            "path": str(config_path.relative_to(REPOSITORY)),
            "sha256": _sha256(config_path),
            "freeze_status": config["freeze_status"],
            "retained_run_commit": commit,
        },
        "definition": {
            "left_boundary": (
                "u2=u_star, v2=g_r(u_star), q2=-80, p2<0, H2=0"
            ),
            "segments": config["multiple_shooting"]["segments"],
            "coincidence": "terminal p2=terminal q2=0",
            "splitting_family": (
                "continue the same multiple-shoot system with a2 fixed and "
                "terminal p2=0; S(a2)=terminal q2"
            ),
        },
        "initialization_only": {
            **initialization,
            "initial_scaled_residual_inf": float(
                np.max(np.abs(initial_evaluated["residual"]))
            ),
        },
        "retained_root": {
            "a2": float(evaluated["a2"]),
            "total_flight_time": float(evaluated["total_time"]),
            "terminal_state": terminal.tolist(),
            "optimizer_status": int(solution.status),
            "optimizer_message": solution.message,
            "optimizer_nfev": int(solution.nfev),
            "optimizer_njev": int(solution.njev) if solution.njev is not None else None,
            "optimizer_cost": float(solution.cost),
            "checks": root_checks,
            "checks_pass": root_pass,
            "tight_segment_replay": tight,
        },
        "splitting_derivative": {
            **derivatives,
            "checks_pass": derivative_pass,
        },
        "decision": {
            "status": status,
            "boundary_selected_simple_zero_candidate": (
                "COMPUTED_NONRIGOROUSLY" if root_pass and derivative_pass else "NOT_ESTABLISHED"
            ),
            "intrinsic_maximal_canard": "NOT_ESTABLISHED",
            "reason": (
                "The finite-boundary multiple-shoot root and both derivative "
                "cross-checks pass the frozen floating-point gates."
                if root_pass and derivative_pass
                else "At least one frozen root, replay, or derivative gate failed."
            ),
        },
        "nonclaims": config["nonclaims"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configuration", type=Path, default=CONFIG_PATH)
    parser.add_argument("--output", type=Path, default=RESULT_PATH)
    arguments = parser.parse_args()
    try:
        report = build_report(arguments.configuration.resolve())
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report["decision"], indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, MultipleShootError, np.linalg.LinAlgError) as error:
        print(f"MULTIPLE SHOOT REJECTED: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
