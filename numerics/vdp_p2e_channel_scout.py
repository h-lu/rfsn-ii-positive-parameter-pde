"""Minimal non-evidentiary P2e channel scout at one frozen v2 point.

The script serializes only two successful floating-point centerlines and one
raw solver stop.  It never constructs lateral faces, an incidence census, or
an event-atlas certificate.
"""

from __future__ import annotations

import hashlib
import json
import sys
import traceback
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import numpy as np
from numpy.typing import NDArray
from scipy.integrate import solve_ivp


_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))

from numerics.rfsn_numerics import vdp_field_point, vdp_hamiltonian
from numerics.vdp_bridge import (
    BridgeParameters,
    central_to_physical,
    physical_to_central,
)
from numerics.vdp_matched_outer import (
    MatchedOuterConfig,
    compute_matched_outer_candidate,
)
from numerics.vdp_outer import OuterParameters
from numerics.vdp_p2c_branch_scout import (
    P2CParameters,
    P2CScoutConfiguration,
    solve_direct_source_branch,
)
from numerics.vdp_pole import (
    PoleParameters,
    cubic_potential,
    physical_field,
    physical_hamiltonian,
)
from numerics.vdp_source_to_pole import (
    KATO_DARBOUX_SECTION_STATUS,
    KatoSourceParameters,
    calibrated_source_frame,
    compute_kato_darboux_source_point,
    finite_horizon_unstable_graph_state,
)


Array = NDArray[np.float64]
HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent
DEFAULT_CONFIG = HERE / "config" / "vdp_p2e_channel_scout_v2.json"
REVERSER = np.array([1.0, -1.0, 1.0, -1.0], dtype=np.float64)


class ScoutError(RuntimeError):
    """The frozen exploratory contract or a required successful channel failed."""


def _json_ready(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repository_path(relative: str) -> Path:
    path = (REPOSITORY / relative).resolve()
    if not path.is_relative_to(REPOSITORY.resolve()):
        raise ScoutError(f"path escapes repository: {relative}")
    return path


def _load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if config.get("schema_version") != (
        "rfsn-vdp-p2e-minimal-channel-scout-config/1"
    ):
        raise ScoutError("unexpected channel-scout schema")
    if config.get("status") != (
        "PREFROZEN_FOR_ONE_RECORDED_NON_EVIDENTIARY_REPLAY"
    ) or config.get("evidence_status") != "NON_EVIDENTIARY":
        raise ScoutError("channel scout is not frozen as non-evidentiary")
    point = config["parameter_point"]
    if (point["r"], point["a2"], point["epsilon"]) != (
        "3/200", "0", "1"
    ):
        raise ScoutError("the frozen exploratory point changed")
    if config["algebraic_matched_single_attempt"]["allowed_attempts"] != 1:
        raise ScoutError("the algebraic stop rule permits more than one attempt")
    for binding in config["source_bindings"]:
        source = _repository_path(binding["path"])
        if not source.is_file() or _sha256(source) != binding["sha256"]:
            raise ScoutError(f"source binding mismatch: {binding['role']}")

    box = json.loads(_repository_path(
        "validation/rigorous/config/vdp_box_v2.json"
    ).read_text(encoding="utf-8"))
    for variable in ("r", "a2", "epsilon"):
        value = Fraction(point[variable])
        lower_record = box["variables"][variable]["lower"]
        upper_record = box["variables"][variable]["upper"]
        lower = Fraction(
            int(lower_record["numerator"]), int(lower_record["denominator"])
        )
        upper = Fraction(
            int(upper_record["numerator"]), int(upper_record["denominator"])
        )
        if not lower < value < upper:
            raise ScoutError(
                f"exploratory {variable} is not strictly inside v2"
            )
    return config


def _sampled_bounds(state: Array) -> dict[str, list[float]]:
    labels = ("U", "P", "V", "Q")
    return {
        label: [float(np.min(state[index])), float(np.max(state[index]))]
        for index, label in enumerate(labels)
    }


def _direct_kato_provider(
    *, r: float, a2: float, epsilon: float, source_radius: float,
    graph_horizon: float, graph_boundary_tolerance: float,
) -> Callable[[float], Array]:
    """Return the direct P2bK/R_chi nonlinear-Wu provider used by P2c."""

    cache: dict[float, Array] = {}
    frame = calibrated_source_frame(r, a2, epsilon)

    def provider(phase: float) -> Array:
        key = float(phase)
        if key not in cache:
            phase_vector = np.array(
                [np.cos(key), np.sin(key)], dtype=np.float64
            )
            unstable = source_radius * frame.phase_rotation @ phase_vector
            state, diagnostics = finite_horizon_unstable_graph_state(
                r=r,
                a2=a2,
                epsilon=epsilon,
                unstable_coordinates=unstable,
                horizon=graph_horizon,
                boundary_tolerance=graph_boundary_tolerance,
                rtol=1.0e-11,
                atol=1.0e-13,
                max_step=0.04,
            )
            if not diagnostics["boundary_residual_passed"]:
                raise ScoutError("direct Kato graph boundary solve failed")
            cache[key] = np.asarray(state, dtype=np.float64)
            provider.unique_evaluations = len(cache)  # type: ignore[attr-defined]
        return cache[key].copy()

    provider.source_model = (  # type: ignore[attr-defined]
        "direct finite-horizon nonlinear W^u in the P2bK algebraic frame "
        "with R_chi; NON_EVIDENTIARY"
    )
    provider.unique_evaluations = 0  # type: ignore[attr-defined]
    return provider


def _homoclinic_centerline(
    config: dict[str, Any], *, r: float, a2: float, epsilon: float
) -> tuple[dict[str, Any], dict[str, Array]]:
    source = config["common_source_convention"]
    choices = config["homoclinic"]
    solver_config = P2CScoutConfiguration(
        source_radius=float(source["source_radius"]),
        graph_horizon=float(source["graph_horizon"]),
        graph_boundary_tolerance=float(source["graph_boundary_tolerance"]),
        rtol=float(choices["rtol"]),
        atol=float(choices["atol"]),
        flight_max_step=float(choices["max_step"]),
    )
    core = solve_direct_source_branch(
        P2CParameters(0.0, 0.0, 1.0),
        choices["core_seed"],
        configuration=solver_config,
    )
    branch = solve_direct_source_branch(
        P2CParameters(r, a2, epsilon),
        (core.phase, core.half_time),
        configuration=solver_config,
    )
    kato = compute_kato_darboux_source_point(
        KatoSourceParameters(r, a2, epsilon),
        branch.phase,
        0.0,
        source_radius=float(source["source_radius"]),
        graph_horizon=float(source["graph_horizon"]),
        graph_boundary_tolerance=float(source["graph_boundary_tolerance"]),
        rtol=float(choices["rtol"]),
        atol=float(choices["atol"]),
        max_step=0.04,
    )
    if kato.status != KATO_DARBOUX_SECTION_STATUS or kato.state is None:
        raise ScoutError(f"homoclinic Kato source failed: {kato.status}")
    source_state = np.asarray(branch.source_state, dtype=np.float64)
    kato_source_defect = float(np.linalg.norm(source_state - kato.state))

    integration = solve_ivp(
        lambda time, state: vdp_field_point(
            time, state, r=r, a2=a2, epsilon=epsilon
        ),
        (0.0, branch.half_time),
        source_state,
        method="DOP853",
        rtol=float(choices["rtol"]),
        atol=float(choices["atol"]),
        max_step=float(choices["max_step"]),
        dense_output=True,
    )
    if not integration.success or integration.sol is None:
        raise ScoutError(f"homoclinic centerline integration failed: {integration.message}")
    half_time = np.linspace(
        0.0, branch.half_time, int(choices["half_centerline_points"])
    )
    half_state = np.asarray(integration.sol(half_time), dtype=np.float64)
    centered_xi = np.concatenate(
        (half_time - branch.half_time, branch.half_time - half_time[-2::-1])
    )
    reflected = REVERSER[:, None] * half_state[:, -2::-1]
    full_state = np.concatenate((half_state, reflected), axis=1)
    energy = vdp_hamiltonian(full_state, r, a2, epsilon)
    terminal = half_state[:, -1]
    terminal_residual = float(np.linalg.norm(terminal[[1, 3]]))
    integration_endpoint_defect = float(
        np.linalg.norm(terminal - np.asarray(branch.endpoint_state))
    )
    thresholds = config["qa_thresholds"]
    qa = {
        "shooting_residual_passed": bool(
            branch.shooting_residual_inf
            <= thresholds["homoclinic_shooting_residual_inf_upper"]
        ),
        "source_energy_passed": bool(
            branch.source_energy_abs
            <= thresholds["homoclinic_source_energy_abs_upper"]
        ),
        "kato_source_identity_passed": bool(
            kato_source_defect
            <= thresholds["homoclinic_kato_source_defect_upper"]
        ),
        "sampled_energy_drift_passed": bool(
            np.ptp(energy)
            <= thresholds["homoclinic_sampled_energy_drift_upper"]
        ),
        "sampled_first_hit_partition_passed": bool(
            branch.first_hit_common_segments_passed
        ),
        "positive_terminal_speed_passed": bool(
            branch.endpoint_pq_speed > 0.0
        ),
    }
    if not all(qa.values()):
        raise ScoutError(f"homoclinic floating QA failed: {qa}")
    report = {
        "status": "HOMOCLINIC_CHANNEL_SCOUT_SUCCESS",
        "evidence_status": "NON_EVIDENTIARY",
        "claim_bearing": False,
        "parameters": {"r": r, "a2": a2, "epsilon": epsilon},
        "source_phase": branch.phase,
        "half_time": branch.half_time,
        "source_state": source_state,
        "source_algebraic_coordinates": branch.source_algebraic_coordinates,
        "source_radius_error": branch.source_radius_error,
        "source_energy_abs": branch.source_energy_abs,
        "kato_source_status": kato.status,
        "kato_source_state_defect": kato_source_defect,
        "shooting_residual": branch.shooting_residual,
        "shooting_residual_inf": branch.shooting_residual_inf,
        "shooting_determinant": branch.shooting_determinant,
        "terminal_state": terminal,
        "terminal_hit_functions": {"P": float(terminal[1]), "Q": float(terminal[3])},
        "terminal_joint_event_speed": branch.endpoint_pq_speed,
        "integration_endpoint_defect": integration_endpoint_defect,
        "sampled_energy_abs_max": float(np.max(np.abs(energy))),
        "sampled_energy_drift": float(np.ptp(energy)),
        "sampled_state_bounds_not_a_tube": _sampled_bounds(full_state),
        "first_hit_segments": [
            {
                "id": item.label,
                "relation": item.relation,
                "time_interval": item.time_interval,
                "sampled_signed_margin": item.sampled_signed_margin,
            }
            for item in branch.first_hit_segments
        ],
        "qa": qa,
        "nonclaim": (
            "This sampled source-to-source reversible centerline and its "
            "real P=Q=0 symmetry hit are not a theorem tube or event-atlas face."
        ),
    }
    arrays = {
        "hom_centered_xi": centered_xi,
        "hom_central_state": full_state,
    }
    return report, arrays


def _pole_centerline(
    config: dict[str, Any], *, r: float, a2: float, epsilon: float
) -> tuple[dict[str, Any], dict[str, Array]]:
    source = config["common_source_convention"]
    choices = config["pole"]
    point = compute_kato_darboux_source_point(
        KatoSourceParameters(r, a2, epsilon),
        float(choices["phase"]),
        float(choices["nu"]),
        source_radius=float(source["source_radius"]),
        graph_horizon=float(source["graph_horizon"]),
        graph_boundary_tolerance=float(source["graph_boundary_tolerance"]),
        rtol=1.0e-11,
        atol=1.0e-13,
        max_step=0.04,
    )
    if point.status != KATO_DARBOUX_SECTION_STATUS or point.state is None:
        raise ScoutError(f"pole Kato source failed: {point.status}")
    parameters = PoleParameters(r=r, a2=a2, epsilon=epsilon)
    bridge = BridgeParameters(r=r, a2=a2, epsilon=epsilon)
    physical_source = central_to_physical(point.state, bridge)
    central_gate_u = float(choices["central_gate_U"])
    physical_threshold = (
        parameters.a
        - np.sqrt(epsilon) * r * r * central_gate_u
    )

    def gate_event(_physical_x: float, state: Array) -> float:
        return float(state[0] - physical_threshold)

    gate_event.direction = 1  # type: ignore[attr-defined]
    gate_event.terminal = True  # type: ignore[attr-defined]
    integration = solve_ivp(
        lambda physical_x, state: physical_field(
            physical_x, state, parameters
        ),
        (0.0, float(choices["maximum_physical_x"])),
        physical_source,
        method="DOP853",
        rtol=float(choices["rtol"]),
        atol=float(choices["atol"]),
        max_step=float(choices["max_step_physical_x"]),
        events=gate_event,
        dense_output=True,
    )
    if not integration.success or integration.sol is None:
        raise ScoutError(f"pole integration failed: {integration.message}")
    if integration.t_events[0].size != 1:
        raise ScoutError("pole orbit did not have exactly one recorded gate hit")
    gate_x = float(integration.t_events[0][0])
    physical_x = np.linspace(
        0.0, gate_x, int(choices["centerline_points"])
    )
    physical_state = np.asarray(integration.sol(physical_x)[:4], dtype=np.float64)
    central_state = physical_to_central(physical_state, bridge)
    central_time = physical_x * epsilon**0.25 / r
    energy = np.asarray(
        physical_hamiltonian(physical_state, parameters), dtype=np.float64
    )
    gate_physical = physical_state[:, -1]
    gate_central = central_state[:, -1]
    gate_residual = float(abs(gate_central[0] - central_gate_u))
    event_speed = float(physical_field(gate_x, gate_physical, parameters)[0])
    pre_gate_maximum = float(
        np.max(physical_state[0, :-1] - physical_threshold)
    )
    target_energy = -epsilon * float(cubic_potential(parameters.a))
    energy_defect = float(
        physical_hamiltonian(gate_physical, parameters) - target_energy
    )
    thresholds = config["qa_thresholds"]
    qa = {
        "gate_residual_passed": bool(
            gate_residual <= thresholds["pole_gate_residual_abs_upper"]
        ),
        "energy_drift_passed": bool(
            np.ptp(energy) <= thresholds["pole_energy_drift_upper"]
        ),
        "strictly_pre_gate_samples_passed": bool(pre_gate_maximum < 0.0),
        "positive_event_speed_passed": bool(event_speed > 0.0),
        "source_section_passed": bool(
            point.diagnostics.get("section_gates_passed") is True
        ),
    }
    if not all(qa.values()):
        raise ScoutError(f"pole floating QA failed: {qa}")
    report = {
        "status": "POLE_CHANNEL_SCOUT_SUCCESS",
        "evidence_status": "NON_EVIDENTIARY",
        "claim_bearing": False,
        "parameters": {"r": r, "a2": a2, "epsilon": epsilon},
        "source_phase": float(choices["phase"]),
        "source_nu": float(choices["nu"]),
        "source_status": point.status,
        "source_state": point.state,
        "source_energy_abs": point.diagnostics["central_energy_abs"],
        "gate_function": (
            "g_pole=U_central-(-10), equivalently "
            "u_physical-(a+10*sqrt(epsilon)*r^2)"
        ),
        "gate_physical_x": gate_x,
        "gate_central_time": float(central_time[-1]),
        "gate_physical_state": gate_physical,
        "gate_central_state": gate_central,
        "gate_residual": gate_residual,
        "event_speed_physical": event_speed,
        "pre_gate_sampled_maximum": pre_gate_maximum,
        "sampled_energy_drift": float(np.ptp(energy)),
        "gate_energy_defect": energy_defect,
        "sampled_central_state_bounds_not_a_tube": _sampled_bounds(central_state),
        "qa": qa,
        "nonclaim": (
            "This is one sampled true-ODE source-to-gate centerline, not a "
            "uniform pole window, theorem face, or basin-entry certificate."
        ),
    }
    arrays = {
        "pole_physical_x": physical_x,
        "pole_physical_state": physical_state,
        "pole_central_time": central_time,
        "pole_central_state": central_state,
    }
    return report, arrays


def _algebraic_matched_attempt(
    config: dict[str, Any], *, r: float, a2: float, epsilon: float
) -> dict[str, Any]:
    source = config["common_source_convention"]
    choices = config["algebraic_matched_single_attempt"]
    provider = _direct_kato_provider(
        r=r,
        a2=a2,
        epsilon=epsilon,
        source_radius=float(source["source_radius"]),
        graph_horizon=float(source["graph_horizon"]),
        graph_boundary_tolerance=float(source["graph_boundary_tolerance"]),
    )
    phase_midpoint = float(choices["core_phase_midpoint"])
    matched_config = MatchedOuterConfig(
        section_m=float(choices["central_section_m"]),
        outer_r1=float(choices["outer_r1"]),
        q_label=float(choices["q_label"]),
        q_end=float(choices["q_end"]),
        source_radius=float(source["source_radius"]),
        source_phase_seed=(
            phase_midpoint + float(choices["source_phase_seed_offset"])
        ),
        source_phase_reference_midpoint=phase_midpoint,
        source_phase_offset_bracket=tuple(
            float(value) for value in choices["source_phase_offset_bracket"]
        ),
        source_flowback_tau=2.0,
        source_graph_horizon=float(source["graph_horizon"]),
        source_graph_boundary_tolerance=float(
            source["graph_boundary_tolerance"]
        ),
        seam_beta_bracket=tuple(
            float(value) for value in choices["seam_beta_bracket"]
        ),
        scaled_beta_collar=float(choices["scaled_beta_collar"]),
        mesh_points=int(choices["mesh_points"]),
        output_points=int(choices["output_points"]),
        tolerance=float(choices["tolerance"]),
        boundary_tolerance=float(choices["boundary_tolerance"]),
        same_section_root_tolerance=float(
            choices["same_section_root_tolerance"]
        ),
        max_nodes=int(choices["max_nodes"]),
    )
    try:
        candidate = compute_matched_outer_candidate(
            OuterParameters(r=r, a2=a2, epsilon=epsilon),
            matched_config,
            source_state_provider=provider,
        )
    except Exception as error:  # The raw one-attempt STOP is the intended datum.
        frames = traceback.extract_tb(error.__traceback__)
        return {
            "status": "ALGEBRAIC_CHANNEL_STOP",
            "evidence_status": "NON_EVIDENTIARY",
            "claim_bearing": False,
            "attempts_used": 1,
            "attempts_allowed": 1,
            "solver": "compute_matched_outer_candidate",
            "source_model": getattr(provider, "source_model"),
            "failure": {
                "exception_type": type(error).__name__,
                "message": str(error),
                "call_chain": [frame.name for frame in frames],
                "origin_function": frames[-1].name if frames else None,
            },
            "stop_reason": (
                "The existing leading outer construction reaches nonpositive "
                "pi at the frozen v2 point and therefore cannot use Q as its "
                "forward coordinate; no retuning or second attempt is "
                "authorized in this scout."
            ),
            "nonclaim": (
                "No algebraic/matched centerline, channel, terminal face, "
                "or theorem failure follows from this numerical solver stop."
            ),
        }
    return {
        "status": "UNEXPECTED_ALGEBRAIC_CANDIDATE_REQUIRES_NEW_REVIEW",
        "evidence_status": "NON_EVIDENTIARY",
        "claim_bearing": False,
        "attempts_used": 1,
        "attempts_allowed": 1,
        "source_phase": candidate.source_phase,
        "diagnostics": candidate.diagnostics,
        "stop_reason": (
            "The previewed STOP did not reproduce; this output is not archived "
            "as a channel without a newly frozen review."
        ),
    }


def build_scout(config_path: Path = DEFAULT_CONFIG) -> tuple[
    dict[str, Any], dict[str, Array]
]:
    config = _load_config(config_path)
    point = config["parameter_point"]
    r = float(Fraction(point["r"]))
    a2 = float(Fraction(point["a2"]))
    epsilon = float(Fraction(point["epsilon"]))
    homoclinic, hom_arrays = _homoclinic_centerline(
        config, r=r, a2=a2, epsilon=epsilon
    )
    pole, pole_arrays = _pole_centerline(
        config, r=r, a2=a2, epsilon=epsilon
    )
    algebraic = _algebraic_matched_attempt(
        config, r=r, a2=a2, epsilon=epsilon
    )
    if algebraic["status"] != "ALGEBRAIC_CHANNEL_STOP":
        raise ScoutError(algebraic["stop_reason"])
    arrays = {**hom_arrays, **pole_arrays}
    report = {
        "schema_version": "rfsn-vdp-p2e-minimal-channel-scout-result/1",
        "status": "PARTIAL_SCOUT_SUCCESS",
        "channel_status": {
            "homoclinic": homoclinic["status"],
            "pole": pole["status"],
            "algebraic": algebraic["status"],
        },
        "evidence_status": "NON_EVIDENTIARY",
        "mathematical_status": "INCONCLUSIVE",
        "claim_bearing": False,
        "atlas_materialization_status": "NOT_STARTED",
        "configuration": {
            "path": str(config_path.relative_to(REPOSITORY)),
            "sha256": _sha256(config_path),
            "configuration_id": config["configuration_id"],
        },
        "parameter_point": point,
        "state_coordinate_order": ["U", "P", "V", "Q"],
        "homoclinic": homoclinic,
        "pole": pole,
        "algebraic": algebraic,
        "qa": {
            "homoclinic_all_passed": all(homoclinic["qa"].values()),
            "pole_all_passed": all(pole["qa"].values()),
            "algebraic_stop_preserved": True,
            "contains_artificial_lateral": False,
            "contains_incidence_census": False,
            "contains_numeric_m0": False,
            "theorem_faces_claimed": False,
        },
        "nonclaims": config["nonclaims"],
    }
    return _json_ready(report), arrays


def write_scout(config_path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config = _load_config(config_path)
    report, arrays = build_scout(config_path)
    data_path = _repository_path(config["output"]["data_path"])
    report_path = _repository_path(config["output"]["report_path"])
    data_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(data_path, **arrays)
    report["data"] = {
        "path": str(data_path.relative_to(REPOSITORY)),
        "sha256": _sha256(data_path),
        "array_shapes": {
            key: list(value.shape) for key, value in arrays.items()
        },
    }
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    report = write_scout()
    print(report["status"])
    print(report["channel_status"])
    print(report["data"]["path"])


if __name__ == "__main__":
    main()


__all__ = [
    "DEFAULT_CONFIG",
    "ScoutError",
    "build_scout",
    "write_scout",
]
