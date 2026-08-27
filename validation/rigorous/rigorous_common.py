#!/usr/bin/env python3
"""Shared, dependency-light helpers for phase-1 rigorous validation."""

from __future__ import annotations

import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

VERDICTS = ("PASS", "FAIL", "INCONCLUSIVE")


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
