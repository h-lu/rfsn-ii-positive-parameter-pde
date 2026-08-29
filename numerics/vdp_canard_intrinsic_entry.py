"""Fail-closed interface for the missing intrinsic canard entry.

The existing canard scripts produce useful finite-boundary and formal-entry
candidates.  Neither input identifies the finite-r trace of the outer saddle
slow manifold (equivalently, the relevant W^cu branch).  This module records
that precise application-layer blocker and refuses to emit a splitting or an
a2 derivative until an explicit intrinsic-entry manifest supplies the missing
object.

This is a lightweight audit.  It runs no collocation, interval integration,
or parameter continuation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parent
CONFIG_PATH = HERE / "config" / "vdp_canard_intrinsic_entry_v1.json"
RESULT_PATH = (
    HERE / "results" / "vdp_canard_intrinsic_entry" / "blocker_audit.json"
)

EVIDENCE_STATUS = "AUDITED/E1_APPLICATION_INTRINSIC_ENTRY_BLOCKER"
C1_STATUS = "BLOCKED_MISSING_FINITE_R_WCU_BRANCH_SELECTOR"
SPLITTING_STATUS = "NOT_COMPUTED_NO_INTRINSIC_ENTRY"
DERIVATIVE_STATUS = "NOT_COMPUTED_NO_INTRINSIC_ENTRY_TANGENT"
THEORY_STATUS = "NO_THEORY_ERROR_IDENTIFIED_APPLICATION_INTERFACE_MISSING"
BASELINE_COMMIT = "8ba7ffc0bb2cdced0c904ff6dfa319e4a5bd9b2b"


class IntrinsicEntryError(ValueError):
    """The supplied data do not identify the intrinsic entry."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json(path: Path, label: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise IntrinsicEntryError(f"{label} is not a JSON object")
    return value


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _is_finite_vector(value: Any, length: int) -> bool:
    return (
        isinstance(value, list)
        and len(value) == length
        and all(_is_finite_number(component) for component in value)
    )


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPOSITORY))
    except ValueError:
        return str(path)


def load_configuration(path: Path = CONFIG_PATH) -> dict[str, Any]:
    config = _load_json(path, "intrinsic-entry configuration")
    if config.get("schema_version") != (
        "vdp-canard-intrinsic-entry-blocker-config/1"
    ):
        raise IntrinsicEntryError("intrinsic-entry configuration version changed")
    if config.get("claim_bearing") is not False:
        raise IntrinsicEntryError("blocker configuration must be non-claim-bearing")
    baseline = config.get("repository_baseline")
    if not isinstance(baseline, dict) or baseline.get("commit") != BASELINE_COMMIT:
        raise IntrinsicEntryError("the read-only audit baseline changed")
    parameters = config.get("parameters")
    if parameters != {
        "r": 0.08,
        "epsilon": 1.0,
        "a2_interval": [-0.0125, 0.0],
    }:
        raise IntrinsicEntryError("the fixed C1 parameter slice changed")
    if config.get("source_section") != {
        "equation": "u2=16",
        "u2": 16.0,
        "orientation": ["p2<0", "q2<0"],
    }:
        raise IntrinsicEntryError("the physical central source section changed")
    if config.get("target_event") != {
        "equation": "p2=0",
        "direction": "increasing",
        "transversality": "p2_prime>0",
        "splitting": "S=q2",
    }:
        raise IntrinsicEntryError("the first-hit splitting convention changed")

    bindings = config.get("audited_repository_inputs")
    if not isinstance(bindings, list) or len(bindings) != 7:
        raise IntrinsicEntryError("the audited repository binding set changed")
    seen: set[str] = set()
    for binding in bindings:
        if not isinstance(binding, dict):
            raise IntrinsicEntryError("an audited input binding is malformed")
        relative = binding.get("path")
        expected = binding.get("sha256")
        if not isinstance(relative, str) or not isinstance(expected, str):
            raise IntrinsicEntryError("an audited input binding is incomplete")
        if relative in seen:
            raise IntrinsicEntryError(f"duplicate audited input: {relative}")
        seen.add(relative)
        actual = _sha256(REPOSITORY / relative)
        if actual != expected:
            raise IntrinsicEntryError(f"audited input changed: {relative}")
    return config


def central_hamiltonian(
    state: tuple[float, float, float, float] | list[float],
    *,
    r: float,
    a2: float,
) -> float:
    """Return the exact epsilon=1 K2 Hamiltonian in repository coordinates."""

    u2, p2, v2, q2 = (float(value) for value in state)
    return (
        0.5 * (p2 * p2 - q2 * q2)
        + (u2 - r * a2) * v2
        - u2**3 / 3.0
        - r * r * u2**4 / 12.0
    )


def negative_zero_energy_state(
    *, u2: float, p2: float, v2: float, r: float, a2: float
) -> tuple[float, float, float, float]:
    """Complete section data to H2=0 with q2<0.

    This algebraic completion deliberately supplies no invariant-manifold
    membership.  It is used below to demonstrate why section, energy, and
    orientation constraints cannot select W^cu.
    """

    radicand = (
        p2 * p2
        + 2.0 * (u2 - r * a2) * v2
        - 2.0 * u2**3 / 3.0
        - r * r * u2**4 / 6.0
    )
    if not math.isfinite(radicand) or radicand <= 0.0:
        raise IntrinsicEntryError(
            f"negative-q H2=0 completion has radicand {radicand}"
        )
    return (float(u2), float(p2), float(v2), -math.sqrt(radicand))


def section_energy_orientation_residuals(
    state: tuple[float, float, float, float] | list[float],
    *,
    r: float,
    a2: float,
    section_u2: float,
) -> dict[str, float | bool]:
    u2, p2, _v2, q2 = (float(value) for value in state)
    return {
        "u2_minus_section": u2 - section_u2,
        "hamiltonian": central_hamiltonian(state, r=r, a2=a2),
        "p2_negative": p2 < 0.0,
        "q2_negative": q2 < 0.0,
    }


def intrinsic_entry_manifest_errors(
    manifest: dict[str, Any], config: dict[str, Any]
) -> list[str]:
    """Validate only the minimum interface needed before S may be computed."""

    errors: list[str] = []
    if manifest.get("schema_version") != "vdp-canard-intrinsic-entry/1":
        errors.append("missing intrinsic-entry manifest schema")
    if manifest.get("status") != "COMPUTED/E1_INTRINSIC_WCU_ENTRY_CANDIDATE":
        errors.append("entry is not identified as a finite-r Wcu candidate")
    if manifest.get("claim_bearing") is not False:
        errors.append("an E1 intrinsic-entry candidate must be non-claim-bearing")
    if manifest.get("parameters") != config["parameters"]:
        errors.append("entry parameter slice does not match the frozen C1 slice")
    if manifest.get("source_section") != config["source_section"]:
        errors.append("entry source section or orientation changed")

    anchor = manifest.get("anchor")
    if not isinstance(anchor, dict):
        errors.append("finite-r Wcu anchor is absent")
    else:
        if anchor.get("kind") not in {
            "FINITE_R_K1_WCU_DISK",
            "FINITE_R_OUTER_SADDLE_SLOW_GRAPH",
        }:
            errors.append("anchor is neither a finite-r K1 Wcu disk nor slow graph")
        if anchor.get("uses_frozen_u2_boundary") is not False:
            errors.append("anchor still uses a frozen finite-boundary u2 value")
        if anchor.get("uses_formal_jet_projection") is not False:
            errors.append("anchor still uses a projected formal jet")
        if not _is_finite_number(anchor.get("invariance_residual")):
            errors.append("anchor has no finite-r invariance residual")

    sample_a2 = manifest.get("sample_a2")
    interval = config["parameters"]["a2_interval"]
    valid_sample = _is_finite_number(sample_a2) and (
        float(interval[0]) <= float(sample_a2) <= float(interval[1])
    )
    if not valid_sample:
        errors.append("entry sample a2 is absent or outside the frozen slice")

    entry = manifest.get("entry_state")
    if not _is_finite_vector(entry, 4):
        errors.append("intrinsic entry state is absent or non-finite")
    else:
        residuals = section_energy_orientation_residuals(
            entry,
            r=float(config["parameters"]["r"]),
            a2=float(sample_a2) if valid_sample else math.nan,
            section_u2=float(config["source_section"]["u2"]),
        )
        if abs(float(residuals["u2_minus_section"])) > 1.0e-10:
            errors.append("intrinsic entry is not on u2=16")
        if not residuals["p2_negative"] or not residuals["q2_negative"]:
            errors.append("intrinsic entry has the wrong source orientation")
        if valid_sample and abs(float(residuals["hamiltonian"])) > 1.0e-8:
            errors.append("intrinsic entry is not on H2=0 within E1 tolerance")

    branch = manifest.get("branch_identification")
    if not isinstance(branch, dict):
        errors.append("primary no-loop branch identification is absent")
    else:
        if branch.get("id") != "PRIMARY_NO_LOOP_FROM_GAMMA0_MINUS":
            errors.append("entry is not on the primary no-loop branch")
        if branch.get("continued_from_gamma0_minus") is not True:
            errors.append("Gamma0-minus continuation is not recorded")
        if branch.get("first_increasing_p2_zero_verified") is not True:
            errors.append("the first-event census is incomplete")

    event = manifest.get("target_event_data")
    if not isinstance(event, dict):
        errors.append("first increasing p2=0 event data are absent")
    else:
        event_state = event.get("state")
        if not _is_finite_vector(event_state, 4):
            errors.append("first-event state is absent or non-finite")
        else:
            if abs(float(event_state[1])) > 1.0e-8:
                errors.append("first-event state is not on p2=0")
            splitting = event.get("splitting")
            if not _is_finite_number(splitting) or abs(
                float(splitting) - float(event_state[3])
            ) > 1.0e-10:
                errors.append("event splitting is not S=q2")
        if not _is_finite_number(event.get("p2_prime")) or float(
            event.get("p2_prime", math.nan)
        ) <= 0.0:
            errors.append("first-event transversality p2_prime>0 is absent")
        if event.get("first_increasing_p2_zero_verified") is not True:
            errors.append("target event does not carry a complete first-hit census")

    replays = manifest.get("outer_cut_or_section_replays")
    minimum = config["required_intrinsic_entry"][
        "minimum_outer_cut_or_section_replays"
    ]
    if not isinstance(replays, list) or len(replays) < minimum:
        errors.append("fewer than two outer-cut/section independence replays")
    elif len({json.dumps(item, sort_keys=True) for item in replays}) != len(replays):
        errors.append("outer-cut/section replays are not distinct")
    else:
        replay_locations: list[float] = []
        for index, replay in enumerate(replays):
            if not isinstance(replay, dict):
                errors.append(f"outer replay {index} is malformed")
                continue
            location = replay.get("outer_cut_or_section_value")
            if not _is_finite_number(location):
                errors.append(f"outer replay {index} has no finite cut/section value")
            else:
                replay_locations.append(float(location))
            entry = replay.get("entry_state")
            if not (
                _is_finite_vector(entry, 4)
            ):
                errors.append(f"outer replay {index} has no finite entry state")
            for field in (
                "invariance_residual",
                "splitting",
                "splitting_derivative",
            ):
                value = replay.get(field)
                if not _is_finite_number(value):
                    errors.append(f"outer replay {index} has no finite {field}")
            if replay.get("first_increasing_p2_zero_verified") is not True:
                errors.append(f"outer replay {index} lacks a first-event census")
        if len(replay_locations) == len(replays) and len(set(replay_locations)) != len(replays):
            errors.append("outer-cut/section replay locations are not distinct")

        convergence = manifest.get("outer_independence_convergence")
        if not isinstance(convergence, dict):
            errors.append("outer-cut/section independence differences are absent")
        else:
            for field in (
                "entry_state_difference_inf",
                "splitting_difference_abs",
                "splitting_derivative_difference_abs",
            ):
                value = convergence.get(field)
                if not _is_finite_number(value):
                    errors.append(f"outer independence check has no finite {field}")

    tangent = manifest.get("a2_tangent")
    if not isinstance(tangent, dict):
        errors.append("a2 tangent data are absent")
    else:
        entry_tangent = tangent.get("entry_state_derivative")
        splitting_tangent = tangent.get("splitting_derivative")
        if not (
            _is_finite_vector(entry_tangent, 4)
        ):
            errors.append("d(entry state)/d(a2) is incomplete")
        if not _is_finite_number(splitting_tangent):
            errors.append("dS/d(a2) is absent")
    return errors


def require_intrinsic_entry(
    manifest: dict[str, Any], config: dict[str, Any]
) -> None:
    errors = intrinsic_entry_manifest_errors(manifest, config)
    if errors:
        raise IntrinsicEntryError("; ".join(errors))


def _counterexample(config: dict[str, Any]) -> dict[str, Any]:
    r = float(config["parameters"]["r"])
    a2 = -1.0 / 120.0
    u2 = float(config["source_section"]["u2"])
    p2 = -2.24
    critical_v2 = u2 * u2 + r * r * u2**3 / 3.0
    first = negative_zero_energy_state(
        u2=u2, p2=p2, v2=critical_v2, r=r, a2=a2
    )
    second = negative_zero_energy_state(
        u2=u2, p2=p2, v2=critical_v2 - 0.1, r=r, a2=a2
    )
    first_residuals = section_energy_orientation_residuals(
        first, r=r, a2=a2, section_u2=u2
    )
    second_residuals = section_energy_orientation_residuals(
        second, r=r, a2=a2, section_u2=u2
    )
    if not (
        abs(float(first_residuals["hamiltonian"])) < 1.0e-10
        and abs(float(second_residuals["hamiltonian"])) < 1.0e-10
        and first_residuals["p2_negative"]
        and first_residuals["q2_negative"]
        and second_residuals["p2_negative"]
        and second_residuals["q2_negative"]
        and first != second
    ):
        raise IntrinsicEntryError("section nonuniqueness counterexample failed")
    return {
        "purpose": (
            "H2=0, u2=16, p2<0 and q2<0 admit distinct points; these "
            "constraints do not identify Wcu."
        ),
        "a2": a2,
        "state_1": list(first),
        "state_2": list(second),
        "state_distance_inf": max(abs(a - b) for a, b in zip(first, second)),
        "state_1_residuals": first_residuals,
        "state_2_residuals": second_residuals,
        "both_intrinsic_membership": "UNDETERMINED",
    }


def build_report(
    config_path: Path = CONFIG_PATH,
    entry_manifest_path: Path | None = None,
) -> dict[str, Any]:
    config = load_configuration(config_path)
    slow_config = _load_json(
        HERE / "config" / "vdp_canard_slow_trace_v1.json",
        "finite-boundary slow-trace configuration",
    )
    slow_result = _load_json(
        HERE / "results" / "vdp_canard_slow_trace" / "fixed_r_candidate.json",
        "finite-boundary slow-trace result",
    )
    surrogate_result = _load_json(
        HERE
        / "results"
        / "vdp_canard_splitting_scout"
        / "fixed_r_report.json",
        "formal-entry splitting result",
    )
    if slow_config.get("a3_outer_u2_boundary") != 16.64508336484338:
        raise IntrinsicEntryError("the audited frozen A.3 u2 boundary changed")
    if "Frozen" not in slow_config.get("a3_outer_u2_boundary_source", ""):
        raise IntrinsicEntryError("the audited A.3 boundary provenance changed")
    if slow_result.get("claim_bearing") is not False:
        raise IntrinsicEntryError("finite-boundary result claim status changed")
    if surrogate_result.get("claim_bearing") is not False:
        raise IntrinsicEntryError("surrogate result claim status changed")

    manifest_errors: list[str]
    manifest_path: str | None
    if entry_manifest_path is None:
        manifest_errors = ["no intrinsic-entry manifest was supplied"]
        manifest_path = None
    else:
        manifest = _load_json(entry_manifest_path, "intrinsic-entry manifest")
        manifest_errors = intrinsic_entry_manifest_errors(manifest, config)
        manifest_path = str(entry_manifest_path)

    return {
        "schema_version": "vdp-canard-intrinsic-entry-blocker-audit/1",
        "evidence_status": EVIDENCE_STATUS,
        "claim_bearing": False,
        "configuration": {
            "path": _display_path(config_path),
            "sha256": _sha256(config_path),
            "configuration_id": config["configuration_id"],
            "repository_baseline": config["repository_baseline"],
        },
        "fixed_problem": {
            "parameters": config["parameters"],
            "source_section": config["source_section"],
            "target_event": config["target_event"],
            "exact_k2_field": [
                "u2'=p2",
                "p2'=u2^2-v2+r^2*u2^3/3",
                "v2'=q2",
                "q2'=u2-r*a2",
            ],
        },
        "literature_coordinate_audit": {
            "source": config["literature_interface"]["source"],
            "K2_match": (
                "Repository epsilon=1 equations and H2 agree with (6.8)--"
                "(6.10); K1/K2 transition is (6.31)--(6.32)."
            ),
            "A2_scope": (
                "Finite q0- or u0-boundary BVPs numerically parameterize "
                "saddle slow-manifold subsets; A.2 supplies no canonical "
                "boundary limit at r=0.08."
            ),
            "A3_scope": (
                "Reverser parity plus the integral H2=0 constraint; no Wcu "
                "or outer saddle-slow membership condition."
            ),
            "theory_scope": (
                "The K1 center-manifold/foliation result and asymptotic "
                "Wcu-Wcs coincidence do not provide a numerical finite-r "
                "branch selector on u2=16."
            ),
            "theory_status": THEORY_STATUS,
        },
        "current_candidate_audit": {
            "finite_boundary_a3_status": slow_result.get("evidence_status"),
            "frozen_outer_u2": slow_config["a3_outer_u2_boundary"],
            "frozen_outer_q2": slow_config["outer_q_boundary"],
            "formal_entry_status": surrogate_result.get("evidence_status"),
            "promotion_to_intrinsic_entry": "REJECTED",
            "reason": (
                "One candidate freezes a finite A.2 boundary and the other "
                "projects a formal jet; neither supplies finite-r Wcu membership."
            ),
        },
        "constraint_nonuniqueness_counterexample": _counterexample(config),
        "required_intrinsic_entry_interface": config["required_intrinsic_entry"],
        "entry_manifest": {
            "path": manifest_path,
            "status": "REJECTED_OR_ABSENT" if manifest_errors else "ACCEPTED",
            "errors": manifest_errors,
        },
        "C1_status": C1_STATUS if manifest_errors else (
            "INTERFACE_ACCEPTED_SPLITTING_IMPLEMENTATION_PENDING"
        ),
        "intrinsic_entry": None,
        "splitting_S": None,
        "splitting_status": SPLITTING_STATUS,
        "a2_derivative": None,
        "a2_derivative_status": DERIVATIVE_STATUS,
        "issue7_and_C4_domain_boundary": {
            "C1_fixed_r": 0.08,
            "issue7_v2_r_interval": [0.01, 0.02],
            "disjoint": True,
            "v1_wide_box_failure_implication_for_C1_narrow_slice": "NONE",
            "C4_requirement": (
                "Separate narrow-slice branch-identification/event-atlas "
                "certificate; no substitute for the frozen A2 edge."
            ),
        },
        "narrow_slice_route_scout": {
            "status": "NON_EVIDENTIARY_STRICT_BINARY_SCOUT",
            "authenticated_manifest": None,
            "cells_passed": 8,
            "cells_total": 8,
            "r_cell": [31.0 / 400.0, 2.0 / 25.0],
            "a2_cover": [-1.0 / 64.0, 0.0],
            "epsilon_cover": [0.9, 1.1],
            "hom_phase_hull": [5.85287545765196, 5.860747521968327],
            "frozen_alg_upper": 5.756691396794898,
            "AH_gap_lower_approx": 0.0961840608570616,
            "role": (
                "Route planning only: a prospective C4 narrow-slice "
                "certificate appears feasible. This closes no atom."
            ),
        },
        "decision": {
            "C1": C1_STATUS,
            "C2": "NOT_STARTED_REQUIRES_C1_ENTRY_AND_DS_DA2",
            "C4": "NOT_STARTED_REQUIRES_SEPARATE_NARROW_SLICE_ATLAS",
            "next_input": (
                "A finite-r K1 Wcu disk or outer saddle-slow graph with an "
                "authenticated K1-to-K2 trace on u2=16, primary no-loop "
                "branch continuation, two cut/section replays, and a2 tangent."
            ),
        },
        "nonclaims": [
            "This audit does not compute an intrinsic slow-manifold entry.",
            "It does not compute S or dS/da2.",
            "The counterexample states are not asserted to lie on Wcu.",
            "The missing application selector is not identified as an error in the cited theory.",
            "The non-evidentiary narrow-slice scout does not close C4.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configuration", type=Path, default=CONFIG_PATH)
    parser.add_argument("--entry-manifest", type=Path)
    parser.add_argument("--output", type=Path, default=RESULT_PATH)
    arguments = parser.parse_args()
    try:
        report = build_report(
            arguments.configuration.resolve(),
            None if arguments.entry_manifest is None else arguments.entry_manifest.resolve(),
        )
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(report["decision"], indent=2, sort_keys=True))
        return 0
    except (OSError, json.JSONDecodeError, IntrinsicEntryError) as error:
        print(f"INTRINSIC ENTRY AUDIT REJECTED: {error}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
