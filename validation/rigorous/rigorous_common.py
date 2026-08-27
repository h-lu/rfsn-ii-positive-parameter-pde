#!/usr/bin/env python3
"""Shared, dependency-light helpers for staged rigorous validation."""

from __future__ import annotations

import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

VERDICTS = ("PASS", "FAIL", "INCONCLUSIVE")

LOCAL_GRAPH_FORMULAS = [
    "alpha=sqrt(2+c)/2",
    "beta=sqrt(2-c)/2",
    "h=2*alpha*beta",
    "U=u1+s1",
    "P=alpha*u1-beta*u2-alpha*s1+beta*s2",
    "V=(c/2)*u1+h*u2+(c/2)*s1+h*s2",
    "Q=alpha*u1+beta*u2-alpha*s1-beta*s2",
    "N_u=(1/(4*alpha),-1/(4*beta))*n(U)",
    "N_s=-N_u",
    "n(U)=-a*U^2+(sqrt(epsilon)*r^2/3)*U^3",
]

LOCAL_GRAPH_ACCEPTANCE_GATES = {
    "frame_determinant_absolute_lower": "0",
    "unstable_face_outward_margin_lower": "0",
    "stable_face_inward_margin_lower": "0",
    "difference_cone_margin_lower": "0",
    "first_quadratic_coefficient_upper": "1",
    "refined_quadratic_coefficient_upper": "1/4",
    "backward_decay_rate_lower": "2/3",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_checked(arguments: list[str], cwd: Path | None = None,
                timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def git_output(repository: Path, *arguments: str) -> str:
    return run_checked(["git", "-C", str(repository), *arguments]).stdout.strip()


def combine_verdicts(statuses: Iterable[str]) -> str:
    values = list(statuses)
    if any(status == "FAIL" for status in values):
        return "FAIL"
    if any(status == "INCONCLUSIVE" for status in values):
        return "INCONCLUSIVE"
    if any(status not in VERDICTS for status in values):
        raise ValueError(f"invalid verdict in {values!r}")
    return "PASS"


def fraction(value: dict[str, str]) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def validate_exact_box(box: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "r": (Fraction(1, 25), Fraction(2, 25)),
        "a2": (Fraction(-1, 4), Fraction(1, 4)),
        "epsilon": (Fraction(4, 5), Fraction(6, 5)),
    }
    variables = box.get("variables", {})
    for name, bounds in expected.items():
        try:
            observed = (fraction(variables[name]["lower"]),
                        fraction(variables[name]["upper"]))
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
            errors.append(f"invalid exact interval for {name}: {error}")
            continue
        if observed != bounds:
            errors.append(f"frozen {name} interval changed: {observed!r} != {bounds!r}")
        if observed[0] >= observed[1]:
            errors.append(f"{name} is not a positive-width interval")
    if box.get("selected_before_interval_validation") is not True:
        errors.append("box is not marked selected_before_interval_validation")
    if box.get("status") != "FROZEN_PREVALIDATION":
        errors.append("box status is not FROZEN_PREVALIDATION")
    return errors


def validate_exact_bridge(bridge: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "r": (Fraction(0, 1), Fraction(2, 25)),
        "a2": (Fraction(-1, 4), Fraction(1, 4)),
        "epsilon": (Fraction(4, 5), Fraction(6, 5)),
    }
    variables = bridge.get("variables", {})
    for name, bounds in expected.items():
        try:
            observed = (fraction(variables[name]["lower"]),
                        fraction(variables[name]["upper"]))
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
            errors.append(f"invalid bridge interval for {name}: {error}")
            continue
        if observed != bounds:
            errors.append(
                f"frozen bridge {name} interval changed: {observed!r} != {bounds!r}")
        if observed[0] >= observed[1]:
            errors.append(f"bridge {name} is not a positive-width interval")
    if bridge.get("selected_before_p2_interval_validation") is not True:
        errors.append("bridge is not marked selected_before_p2_interval_validation")
    if bridge.get("status") != "FROZEN_PRE_P2_VALIDATION":
        errors.append("bridge status is not FROZEN_PRE_P2_VALIDATION")
    if bridge.get("anchor_face", {}).get("equation") != "r=0":
        errors.append("bridge does not retain the exact r=0 anchor face")
    return errors


def validate_local_graph_configuration(configuration: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if configuration.get("configuration_id") != "vdp-p2-local-graph-v1":
        errors.append("unexpected local-graph configuration identifier")
    if configuration.get("status") != "FROZEN_PREVALIDATION":
        errors.append("local-graph configuration is not frozen")
    if configuration.get("frozen_before_interval_run") is not True:
        errors.append("local-graph configuration was not frozen before validation")
    block = configuration.get("coordinate_block", {})
    expected_radius = Fraction(1, 100)
    for key in ("unstable_radius", "stable_radius", "source_circle_radius"):
        try:
            observed = fraction(block[key])
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
            errors.append(f"invalid local-graph {key}: {error}")
            continue
        if observed != expected_radius:
            errors.append(
                f"local-graph {key} changed: {observed!r} != {expected_radius!r}")
    frame = configuration.get("closed_form_frame", {})
    if frame.get("formulas") != LOCAL_GRAPH_FORMULAS:
        errors.append("local-graph closed-form frame formulas changed")
    if frame.get("phase_scope") != \
            "local-graph-only-not-V2-transported-absolute-phase":
        errors.append("local-graph phase-scope boundary changed")
    if configuration.get("acceptance_gates") != LOCAL_GRAPH_ACCEPTANCE_GATES:
        errors.append("local-graph acceptance gates changed")
    if configuration.get("proved_subobligations") != [
            "V2.WU.FRAME_BLOCK", "V2.WU.COARSE_GRAPH"]:
        errors.append("local-graph subobligation list changed")
    if configuration.get("pending_parent_obligation") != "V2.WU_GRAPH":
        errors.append("local-graph parent-obligation boundary changed")
    return errors


def box_arguments(box: dict[str, Any]) -> list[str]:
    arguments: list[str] = []
    for name in ("r", "a2", "epsilon"):
        interval = box["variables"][name]
        for endpoint in ("lower", "upper"):
            arguments.extend([
                interval[endpoint]["numerator"],
                interval[endpoint]["denominator"],
            ])
    return arguments


def safe_repository_path(repository: Path, relative: str) -> Path:
    candidate = (repository / relative).resolve()
    root = repository.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"path escapes repository: {relative}")
    return candidate
