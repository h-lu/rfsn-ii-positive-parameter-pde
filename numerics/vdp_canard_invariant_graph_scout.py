"""Reproduce the stopped finite-r invariant-graph scout.

The frozen experiment collocates the physical saddle-slow graph equations on
two overlapping Chebyshev rectangles.  It stops without an entry or tangent
when the graph iteration misses its frozen residual threshold and the Newton
linearization is nearly singular.  No orbit BVP is used here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.sparse import bmat, csc_matrix, diags, eye, kron
from scipy.sparse.linalg import splu


HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "config" / "vdp_canard_invariant_graph_scout_v1.json"
RESULT_PATH = (
    HERE / "results" / "vdp_canard_invariant_graph_scout" / "stop_report.json"
)
STOP_STATUS = "STOP_GRAPH_PDE_RESIDUAL_AND_NEWTON_CONDITIONING"


class GraphScoutError(ValueError):
    pass


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_configuration(path: Path = CONFIG_PATH) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("schema_version") != (
        "vdp-canard-invariant-graph-scout-config/1"
    ):
        raise GraphScoutError("configuration schema changed")
    if config.get("freeze_status") != "FROZEN_BEFORE_FIRST_GRAPH_SOLVE":
        raise GraphScoutError("configuration is not pre-solve frozen")
    if config.get("claim_bearing") is not False:
        raise GraphScoutError("floating scout cannot be claim-bearing")
    parameters = config.get("parameters", {})
    if parameters.get("r") != 0.08 or parameters.get("delta") != 0.0064:
        raise GraphScoutError("the frozen r/delta slice changed")
    if not math.isclose(
        parameters["delta"], parameters["r"] ** 2, rel_tol=0.0, abs_tol=1e-16
    ):
        raise GraphScoutError("delta != r^2")
    rectangles = config.get("rectangles")
    if not isinstance(rectangles, list) or len(rectangles) != 2:
        raise GraphScoutError("exactly two frozen rectangles are required")
    overlap = config["predeclared_overlap"]
    target_u = config["entry"]["physical_u"]
    target_q_lo, target_q_hi = config["entry"]["physical_q_bracket"]
    if not (
        overlap["u_interval"][0] < target_u < overlap["u_interval"][1]
        and overlap["q_interval"][0] <= target_q_lo < target_q_hi
        <= overlap["q_interval"][1]
    ):
        raise GraphScoutError("the frozen overlap does not contain the target")
    return config


def chebyshev_grid_and_derivative(
    size: int, interval: list[float]
) -> tuple[np.ndarray, np.ndarray]:
    if size < 3:
        raise GraphScoutError("Chebyshev size must be at least three")
    nodes = np.cos(np.pi * np.arange(size) / (size - 1))
    weights = np.ones(size)
    weights[[0, -1]] = 2.0
    weights *= (-1.0) ** np.arange(size)
    differences = nodes[:, None] - nodes[None, :]
    derivative = (weights[:, None] / weights[None, :]) / (
        differences + np.eye(size)
    )
    derivative -= np.diag(derivative.sum(axis=1))
    lower, upper = interval
    physical_nodes = 0.5 * (lower + upper) + 0.5 * (upper - lower) * nodes
    return physical_nodes, derivative * (2.0 / (upper - lower))


def _collocation_data(
    rectangle: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    nu, nq = rectangle["chebyshev_shape"]
    u, du = chebyshev_grid_and_derivative(nu, rectangle["u_interval"])
    q, dq = chebyshev_grid_and_derivative(nq, rectangle["q_interval"])
    upper_u = u[:, None]
    full_q = np.broadcast_to(q[None, :], (nu, nq))
    parameters = config["parameters"]
    r = float(parameters["r"])
    a = 1.0 + r**3 * float(parameters["a2_center"])
    delta = float(parameters["delta"])
    return {
        "nu": nu,
        "nq": nq,
        "u": u,
        "q": q,
        "du": du,
        "dq": dq,
        "U": upper_u,
        "Q": full_q,
        "A": np.broadcast_to(upper_u - a, (nu, nq)),
        "f": np.broadcast_to(upper_u**3 / 3.0 - upper_u, (nu, nq)),
        "delta": delta,
    }


def _residual(
    p: np.ndarray, v: np.ndarray, data: dict[str, Any]
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    du, dq = data["du"], data["dq"]
    p_u, p_q = du @ p, p @ dq.T
    v_u, v_q = du @ v, v @ dq.T
    delta_a = data["delta"] * data["A"]
    first = p_u * p + p_q * delta_a - data["f"] + v
    second = v_u * p + v_q * delta_a - data["delta"] * data["Q"]
    return first, second, p_u, v_u


def _newton_jacobian(
    p: np.ndarray,
    p_u: np.ndarray,
    v_u: np.ndarray,
    data: dict[str, Any],
) -> csc_matrix:
    nu, nq = data["nu"], data["nq"]
    count = nu * nq
    d_u = kron(data["du"], eye(nq), format="csc")
    d_q = kron(eye(nu), data["dq"], format="csc")
    identity = eye(count, format="csc")
    transport = diags((data["delta"] * data["A"]).ravel()) @ d_q
    common = diags(p.ravel()) @ d_u + transport
    return bmat(
        [
            [common + diags(p_u.ravel()), identity],
            [diags(v_u.ravel()), common],
        ],
        format="csc",
    )


def compute_rectangle_stop(
    rectangle: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    data = _collocation_data(rectangle, config)
    denominator = data["U"] ** 2 - 1.0
    p = data["delta"] * data["Q"] / denominator
    v = data["f"].copy()
    iteration = config["graph_iteration"]
    relaxation = float(iteration["relaxation"])
    best: tuple[float, int, np.ndarray, np.ndarray] | None = None
    abort_iteration = 0
    abort_residual = math.nan

    for index in range(int(iteration["maximum_iterations"])):
        first, second, p_u, v_u = _residual(p, v, data)
        residual = max(float(np.max(np.abs(first))), float(np.max(np.abs(second))))
        if best is None or residual < best[0]:
            best = (residual, index, p.copy(), v.copy())
        abort_iteration, abort_residual = index, residual
        # Safety only: it cannot convert a failed residual gate into a pass.
        if not math.isfinite(residual) or residual > 1.0:
            break
        p_q, v_q = p @ data["dq"].T, v @ data["dq"].T
        if float(np.min(np.abs(v_u))) < 1e-12:
            break
        target_p = data["delta"] * (
            data["Q"] - v_q * data["A"]
        ) / v_u
        target_v = data["f"] - p_u * p - p_q * data["delta"] * data["A"]
        p = (1.0 - relaxation) * p + relaxation * target_p
        v = (1.0 - relaxation) * v + relaxation * target_v

    if best is None:
        raise GraphScoutError("graph iteration produced no finite residual")
    best_residual, best_iteration, p, v = best
    first, second, p_u, v_u = _residual(p, v, data)
    residual_vector = np.concatenate((first.ravel(), second.ravel()))
    jacobian = _newton_jacobian(p, p_u, v_u, data)
    lu = splu(jacobian)
    dimension = jacobian.shape[0]
    inverse = lu.solve(np.eye(dimension))
    jacobian_norm = float(np.max(np.asarray(abs(jacobian).sum(axis=0))))
    inverse_norm = float(np.max(np.sum(np.abs(inverse), axis=0)))
    inverse_identity_residual = float(
        np.max(np.abs(jacobian @ inverse - np.eye(dimension)))
    )

    step = lu.solve(-residual_vector)
    count = data["nu"] * data["nq"]
    trials: list[tuple[float, float]] = []
    for exponent in range(21):
        alpha = 2.0 ** (-exponent)
        trial_p = p + alpha * step[:count].reshape(p.shape)
        trial_v = v + alpha * step[count:].reshape(v.shape)
        trial_first, trial_second, _, _ = _residual(trial_p, trial_v, data)
        trial_residual = max(
            float(np.max(np.abs(trial_first))),
            float(np.max(np.abs(trial_second))),
        )
        trials.append((trial_residual, alpha))
    best_newton_residual, best_alpha = min(trials)

    discriminant = p_u * p_u + 4.0 * v_u
    finite_normal_gap: float | None = None
    if float(np.min(discriminant)) > 0.0:
        root = np.sqrt(discriminant)
        finite_normal_gap = float(
            np.min(
                np.minimum(
                    np.abs((-p_u + root) / 2.0),
                    np.abs((-p_u - root) / 2.0),
                )
            )
        )

    residual_stop = float(iteration["residual_stop"])
    return {
        "rectangle_id": rectangle["id"],
        "chebyshev_shape": rectangle["chebyshev_shape"],
        "singular_min_u2_minus_1": float(
            min(rectangle["u_interval"]) ** 2 - 1.0
        ),
        "best_iteration": best_iteration,
        "best_residual_inf": best_residual,
        "best_equation_residuals_inf": [
            float(np.max(np.abs(first))),
            float(np.max(np.abs(second))),
        ],
        "residual_stop": residual_stop,
        "residual_gate_pass": best_residual <= residual_stop,
        "abort_safety": {
            "iteration": abort_iteration,
            "residual_inf": abort_residual,
            "reason": "RESIDUAL_EXCEEDED_ONE",
        },
        "finite_normal_gap_at_best_iterate": finite_normal_gap,
        "newton_diagnostic": {
            "dimension": dimension,
            "jacobian_norm_1": jacobian_norm,
            "inverse_norm_1_from_lu": inverse_norm,
            "condition_1_from_lu": jacobian_norm * inverse_norm,
            "inverse_identity_residual_inf": inverse_identity_residual,
            "newton_step_inf": float(np.max(np.abs(step))),
            "full_step_residual_inf": trials[0][0],
            "best_dyadic_alpha": best_alpha,
            "best_dyadic_residual_inf": best_newton_residual,
        },
        "status": STOP_STATUS,
    }


def build_report(config_path: Path = CONFIG_PATH) -> dict[str, Any]:
    config = load_configuration(config_path)
    rows = [
        compute_rectangle_stop(rectangle, config)
        for rectangle in config["rectangles"]
    ]
    if any(row["residual_gate_pass"] for row in rows):
        raise GraphScoutError("frozen STOP result unexpectedly changed")
    return {
        "schema_version": "vdp-canard-invariant-graph-stop-report/1",
        "evidence_status": "COMPUTED/E1_FAILED_GRAPH_PDE_SCOUT",
        "claim_bearing": False,
        "configuration": {
            "path": str(config_path.relative_to(HERE.parent)),
            "sha256": _sha256(config_path),
            "freeze_status": config["freeze_status"],
        },
        "mathematical_object": {
            "physical_graph": "p=P(u,q), v=V(u,q)",
            "invariance_equations": config["graph_equations"],
            "target_section": config["entry"],
        },
        "rectangles": rows,
        "decision": {
            "status": STOP_STATUS,
            "reason": (
                "Both predeclared collocations miss the frozen invariance "
                "residual and have nearly singular Newton Jacobians. The "
                "two-dimensional graph PDE lacks inflow/gauge/branch data."
            ),
            "intrinsic_Wcu_entry": None,
            "entry_domain_independence": "NOT_TESTED_NO_ACCEPTED_GRAPH",
            "a2_tangent": None,
            "a2_tangent_domain_independence": "NOT_TESTED_NO_ACCEPTED_GRAPH",
        },
        "nonclaims": [
            "This STOP is not evidence that Wcu does not exist.",
            "No intrinsic Wcu entry or a2 tangent was computed.",
            "No A.2 finite-boundary orbit BVP was used.",
            "No C1, C2, maximal-canard, or high-winding claim is closed.",
        ],
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
    except (OSError, ValueError, GraphScoutError) as error:
        print(f"INVARIANT GRAPH SCOUT REJECTED: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
