"""Finite two-dimensional source-patch census for the v2 P2e scout.

This is deliberately floating evidence.  It thickens the three previously
computed ``nu=0`` carrier germs in the same Kato-compatible numerical source
coordinates, but it neither materializes nor certifies ``V2.EVENT_ATLAS``.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp

from numerics.rfsn_numerics import vdp_field_point, vdp_hamiltonian
from numerics.vdp_source_to_pole import (
    CENTRAL_REVERSER_MATRIX,
    KATO_DARBOUX_SECTION_STATUS,
    KatoSourceParameters,
    calibrated_source_frame,
    compute_kato_darboux_source_point,
    invert_kato_darboux_source_coordinates,
)


Array = NDArray[np.float64]
HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent
DEFAULT_CONFIG = HERE / "config/vdp_p2e_source_patch_census_v2.json"
DEFAULT_RESULT = (
    HERE / "results/vdp_p2e_source_patch_census_v2/result.json"
)
DEFAULT_ARRAYS = (
    HERE / "results/vdp_p2e_source_patch_census_v2/trajectories.npz"
)


class SourcePatchCensusError(RuntimeError):
    """The prospectively frozen source-patch run could not be completed."""


def _fraction(value: str) -> float:
    return float(Fraction(value))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _bound_path(record: dict[str, str]) -> Path:
    path = (REPOSITORY / record["path"]).resolve()
    if not path.is_relative_to(REPOSITORY.resolve()):
        raise SourcePatchCensusError("source binding escapes the repository")
    if not path.is_file() or _sha256(path) != record["sha256"]:
        raise SourcePatchCensusError(
            f"source binding mismatch: {record['path']}"
        )
    return path


def load_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("schema_version") != (
        "rfsn-vdp-p2e-source-patch-census-config/1"
    ):
        raise SourcePatchCensusError("unexpected source-patch schema")
    if config.get("status") != (
        "PREFROZEN_BEFORE_FIRST_RETAINED_SOURCE_PATCH_RUN"
    ):
        raise SourcePatchCensusError("source-patch configuration is not frozen")
    if config["retained_run_policy"] != {
        "allowed_runs": 1,
        "no_grid_retry": True,
        "no_threshold_retry": True,
        "preserve_inconclusive_source_points": True,
        "preserve_unresolved_or_guarded_trajectories": True,
    }:
        raise SourcePatchCensusError("retained-run policy changed")
    for binding in config["source_bindings"]:
        _bound_path(binding)
    return config


def _radial_data(state: Array, field: Array, frame: Any) -> dict[str, float]:
    coordinates = frame.coordinates(state)
    stable = coordinates[2:]
    rho_s = float(np.linalg.norm(stable))
    rho_u = float(np.linalg.norm(coordinates[:2]))
    if rho_s == 0.0:
        rho_s_speed = float("nan")
    else:
        coordinate_velocity = frame.inverse @ field
        rho_s_speed = float(stable @ coordinate_velocity[2:] / rho_s)
    return {
        "rho_u": rho_u,
        "rho_s": rho_s,
        "rho_s_speed": rho_s_speed,
    }


def _integrate_source_point(
    state: Array,
    *,
    parameters: KatoSourceParameters,
    config: dict[str, Any],
) -> tuple[dict[str, Any], Array, Array]:
    source_radius = _fraction(config["source"]["source_radius"])
    integration = config["integration"]
    frame = calibrated_source_frame(
        parameters.r, parameters.a2, parameters.epsilon
    )

    def field(time: float, value: Array) -> Array:
        return vdp_field_point(
            time,
            value,
            r=parameters.r,
            a2=parameters.a2,
            epsilon=parameters.epsilon,
        )

    def incoming(time: float, value: Array) -> float:
        del time
        return float(np.linalg.norm(frame.coordinates(value)[2:]) - source_radius)

    incoming.direction = -1.0  # type: ignore[attr-defined]
    incoming.terminal = False  # type: ignore[attr-defined]

    def algebraic(time: float, value: Array) -> float:
        del time
        return float(value[0] + 4.0)

    algebraic.direction = -1.0  # type: ignore[attr-defined]
    algebraic.terminal = False  # type: ignore[attr-defined]

    def pole(time: float, value: Array) -> float:
        del time
        return float(value[0] + 10.0)

    pole.direction = -1.0  # type: ignore[attr-defined]
    pole.terminal = False  # type: ignore[attr-defined]

    guard_norm = _fraction(integration["state_norm_guard"])

    def guard(time: float, value: Array) -> float:
        del time
        return float(np.linalg.norm(value) - guard_norm)

    guard.direction = 1.0  # type: ignore[attr-defined]
    guard.terminal = True  # type: ignore[attr-defined]

    solution = solve_ivp(
        field,
        (0.0, _fraction(integration["maximum_central_time"])),
        np.asarray(state, dtype=np.float64),
        method=integration["method"],
        rtol=float(integration["rtol"]),
        atol=float(integration["atol"]),
        max_step=_fraction(integration["max_step"]),
        events=(incoming, algebraic, pole, guard),
        dense_output=True,
    )
    if not solution.success or solution.sol is None:
        raise SourcePatchCensusError(
            f"central integration failed: {solution.message}"
        )

    candidates: list[tuple[float, str, Array, float, dict[str, float]]] = []
    rejected_return_crossings: list[dict[str, float]] = []
    for time, hit in zip(solution.t_events[0], solution.y_events[0]):
        hit_state = np.asarray(hit, dtype=np.float64)
        hit_field = field(float(time), hit_state)
        radial = _radial_data(hit_state, hit_field, frame)
        row = {"time": float(time), **radial}
        if radial["rho_u"] <= source_radius and radial["rho_s_speed"] < 0.0:
            candidates.append(
                (
                    float(time),
                    "return",
                    hit_state,
                    radial["rho_s_speed"],
                    radial,
                )
            )
        else:
            rejected_return_crossings.append(row)
    for time, hit in zip(solution.t_events[1], solution.y_events[1]):
        hit_state = np.asarray(hit, dtype=np.float64)
        if hit_state[1] < 0.0 and hit_state[3] < 0.0:
            candidates.append(
                (
                    float(time),
                    "algebraic",
                    hit_state,
                    float(field(float(time), hit_state)[0]),
                    _radial_data(hit_state, field(float(time), hit_state), frame),
                )
            )
    for time, hit in zip(solution.t_events[2], solution.y_events[2]):
        hit_state = np.asarray(hit, dtype=np.float64)
        candidates.append(
            (
                float(time),
                "pole",
                hit_state,
                float(field(float(time), hit_state)[0]),
                _radial_data(hit_state, field(float(time), hit_state), frame),
            )
        )

    stop_reason = "maximum_time"
    stop_time = float(solution.t[-1])
    if len(solution.t_events[3]):
        stop_reason = "state_norm_guard"
        stop_time = float(solution.t_events[3][0])
    if candidates:
        hit_time, outcome, hit_state, hit_speed, radial = min(
            candidates, key=lambda item: item[0]
        )
        stop_time = hit_time
        stop_reason = "qualifying_event"
        event_residual = {
            "return": radial["rho_s"] - source_radius,
            "algebraic": float(hit_state[0] + 4.0),
            "pole": float(hit_state[0] + 10.0),
        }[outcome]
    else:
        outcome = "unresolved"
        hit_state = np.asarray(solution.sol(stop_time), dtype=np.float64)
        hit_speed = None
        event_residual = None
        radial = _radial_data(hit_state, field(stop_time, hit_state), frame)

    sample_time = np.linspace(
        0.0, stop_time, int(integration["energy_samples"])
    )
    sample_state = np.asarray(solution.sol(sample_time), dtype=np.float64)
    energy = vdp_hamiltonian(
        sample_state,
        parameters.r,
        parameters.a2,
        parameters.epsilon,
    )
    stable_label: dict[str, Any] | None = None
    if outcome == "return":
        inverse = invert_kato_darboux_source_coordinates(
            CENTRAL_REVERSER_MATRIX @ hit_state,
            parameters,
            source_radius=source_radius,
            graph_horizon=_fraction(config["source"]["graph_horizon"]),
            phase_difference_step=_fraction(
                config["source"]["phase_difference_step"]
            ),
            graph_boundary_tolerance=float(
                config["source"]["graph_boundary_tolerance"]
            ),
            energy_tolerance=float(
                config["qa_thresholds"]["source_energy_abs_upper"]
            ),
            rtol=float(integration["rtol"]),
            atol=float(integration["atol"]),
            max_step=_fraction(integration["max_step"]),
        )
        stable_label = {
            "status": inverse.status,
            "phase": float(inverse.phase),
            "c_stable": float(inverse.nu),
            "reconstruction_defect": float(
                np.linalg.norm(inverse.reconstructed_state - (
                    CENTRAL_REVERSER_MATRIX @ hit_state
                ))
            ),
        }

    return (
        {
            "outcome": outcome,
            "hit_time": stop_time,
            "stop_reason": stop_reason,
            "hit_state": hit_state.tolist(),
            "event_function_residual_abs": (
                None if event_residual is None else abs(float(event_residual))
            ),
            "event_speed": (
                None if hit_speed is None else float(hit_speed)
            ),
            "radial_at_hit": radial,
            "stable_label": stable_label,
            "rejected_return_crossings": rejected_return_crossings,
            "hamiltonian_abs_max": float(np.max(np.abs(energy))),
            "hamiltonian_drift": float(np.ptp(energy)),
        },
        sample_time,
        sample_state,
    )


def _boundary_brackets(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    brackets: list[dict[str, Any]] = []
    by_nu: dict[str, list[dict[str, Any]]] = {}
    by_phase: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_nu.setdefault(row["nu_exact"], []).append(row)
        by_phase.setdefault(row["phase_key"], []).append(row)
    for nu_exact, line in by_nu.items():
        line.sort(key=lambda item: item["phase"])
        for left, right in zip(line, line[1:]):
            if left["outcome"] != right["outcome"]:
                brackets.append(
                    {
                        "axis": "phase",
                        "fixed_nu_exact": nu_exact,
                        "left": [left["phase"], left["outcome"]],
                        "right": [right["phase"], right["outcome"]],
                    }
                )
    for phase_key, line in by_phase.items():
        line.sort(key=lambda item: item["nu"])
        for lower, upper in zip(line, line[1:]):
            if lower["outcome"] != upper["outcome"]:
                brackets.append(
                    {
                        "axis": "nu",
                        "fixed_phase_key": phase_key,
                        "lower": [lower["nu"], lower["outcome"]],
                        "upper": [upper["nu"], upper["outcome"]],
                    }
                )
    return brackets


def run(
    config_path: Path = DEFAULT_CONFIG,
    result_path: Path = DEFAULT_RESULT,
    arrays_path: Path = DEFAULT_ARRAYS,
) -> dict[str, Any]:
    config = load_config(config_path)
    point = config["parameter_point"]
    parameters = KatoSourceParameters(
        _fraction(point["r"]),
        _fraction(point["a2"]),
        _fraction(point["epsilon"]),
    )
    source = config["source"]
    integration = config["integration"]
    rows: list[dict[str, Any]] = []
    arrays: dict[str, Array] = {}
    for patch in config["patches"]:
        center = float(patch["center"])
        for phase_index, offset_exact in enumerate(patch["phase_offsets"]):
            phase = center + _fraction(offset_exact)
            phase_key = f"{patch['id']}:{phase_index}:{offset_exact}"
            for nu_index, nu_exact in enumerate(config["nu_values"]):
                nu = _fraction(nu_exact)
                source_point = compute_kato_darboux_source_point(
                    parameters,
                    phase,
                    nu,
                    source_radius=_fraction(source["source_radius"]),
                    graph_horizon=_fraction(source["graph_horizon"]),
                    phase_difference_step=_fraction(
                        source["phase_difference_step"]
                    ),
                    graph_boundary_tolerance=float(
                        source["graph_boundary_tolerance"]
                    ),
                    energy_tolerance=float(
                        config["qa_thresholds"]["source_energy_abs_upper"]
                    ),
                    maximum_abs_nu=_fraction(source["maximum_abs_nu"]),
                    rtol=float(integration["rtol"]),
                    atol=float(integration["atol"]),
                    max_step=_fraction(integration["max_step"]),
                )
                prefix = f"{patch['id']}_p{phase_index}_n{nu_index}"
                if (
                    source_point.status != KATO_DARBOUX_SECTION_STATUS
                    or source_point.state is None
                ):
                    rows.append(
                        {
                            "patch": patch["id"],
                            "phase_key": phase_key,
                            "phase_offset_exact": offset_exact,
                            "phase": phase,
                            "nu_exact": nu_exact,
                            "nu": nu,
                            "source_status": source_point.status,
                            "source_diagnostics": source_point.diagnostics,
                            "outcome": "source_inconclusive",
                        }
                    )
                    continue
                event, times, states = _integrate_source_point(
                    np.asarray(source_point.state, dtype=np.float64),
                    parameters=parameters,
                    config=config,
                )
                arrays[f"{prefix}_time"] = times
                arrays[f"{prefix}_state"] = states
                rows.append(
                    {
                        "patch": patch["id"],
                        "phase_key": phase_key,
                        "phase_offset_exact": offset_exact,
                        "phase": phase,
                        "nu_exact": nu_exact,
                        "nu": nu,
                        "source_status": source_point.status,
                        "source_diagnostics": source_point.diagnostics,
                        **event,
                    }
                )

    arrays_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(arrays_path, **arrays)
    thresholds = config["qa_thresholds"]
    resolved = [
        row for row in rows
        if row["outcome"] not in {"source_inconclusive", "unresolved"}
    ]
    source_pass = all(
        row["source_status"] == KATO_DARBOUX_SECTION_STATUS
        and float(row["source_diagnostics"]["central_energy_abs"])
        <= float(thresholds["source_energy_abs_upper"])
        and abs(float(row["source_diagnostics"]["nu_roundtrip_defect"]))
        <= float(thresholds["source_nu_roundtrip_abs_upper"])
        for row in rows
        if row["outcome"] != "source_inconclusive"
    ) and all(row["outcome"] != "source_inconclusive" for row in rows)
    event_pass = all(
        row["event_function_residual_abs"]
        <= float(thresholds["event_hit_residual_abs_upper"])
        and abs(row["event_speed"])
        >= float(thresholds["event_speed_abs_lower"])
        and row["hamiltonian_drift"]
        <= float(thresholds["sampled_hamiltonian_drift_upper"])
        for row in resolved
    )
    inverse_pass = all(
        row["stable_label"] is None
        or (
            row["stable_label"]["status"] == KATO_DARBOUX_SECTION_STATUS
            and row["stable_label"]["reconstruction_defect"]
            <= float(
                thresholds["return_inverse_reconstruction_defect_upper"]
            )
        )
        for row in resolved
    )
    patch_summaries: dict[str, Any] = {}
    for patch in config["patches"]:
        patch_rows = [row for row in rows if row["patch"] == patch["id"]]
        patch_summaries[patch["id"]] = {
            "sample_count": len(patch_rows),
            "outcomes": dict(sorted(Counter(
                row["outcome"] for row in patch_rows
            ).items())),
            "boundary_brackets": _boundary_brackets(patch_rows),
        }
    result: dict[str, Any] = {
        "schema_version": "rfsn-vdp-p2e-source-patch-census-result/1",
        "status": "COMPUTED_E1_SOURCE_PATCH_CENSUS",
        "mathematical_status": "INCONCLUSIVE",
        "claim_bearing": False,
        "configuration": {
            "path": str(config_path.relative_to(REPOSITORY)),
            "sha256": _sha256(config_path),
        },
        "parameter_point": point,
        "sample_count": len(rows),
        "outcomes": dict(sorted(Counter(
            row["outcome"] for row in rows
        ).items())),
        "patch_summaries": patch_summaries,
        "qa": {
            "source_coordinates_pass": source_pass,
            "resolved_event_pass": event_pass,
            "return_inverse_pass": inverse_pass,
            "all_declared_floating_gates_pass": bool(
                source_pass and event_pass and inverse_pass
            ),
        },
        "arrays": {
            "path": str(arrays_path.relative_to(REPOSITORY)),
            "sha256": _sha256(arrays_path),
            "array_count": len(arrays),
        },
        "samples": rows,
        "nonclaims": config["nonclaims"],
        "interpretation": (
            "Actual two-dimensional floating source-patch outcomes in the "
            "same numerical Kato convention as the centerline scouts.  They "
            "are candidate carrier/aperture data, not V2.EVENT_ATLAS."
        ),
    }
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    result = run()
    print(json.dumps({
        "status": result["status"],
        "sample_count": result["sample_count"],
        "outcomes": result["outcomes"],
        "qa": result["qa"],
    }, indent=2, sort_keys=True))
    return 0 if result["qa"]["all_declared_floating_gates_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
