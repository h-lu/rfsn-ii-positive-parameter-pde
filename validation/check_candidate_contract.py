#!/usr/bin/env python3
"""Validate a non-claim-bearing Issue #7 candidate contract.

This checker verifies schema conformance, exact-decimal interval ordering, and
SHA-256 bindings to local inputs.  It never reports an interval theorem as
``PASS``: the only success reported here is that a *candidate contract* is
well-formed and replay inputs have not changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from decimal import Decimal, InvalidOperation
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = Path(__file__).with_name("candidate_contract.schema.json")
DEFAULT_ENVIRONMENT_LOCK = Path(__file__).with_name("environment.lock.json")
REQUIRED_THEORY_ROLES = frozenset(
    {
        "V2 theorem",
        "V3 theorem",
        "V4 theorem",
        "V5 theorem",
        "V5A theorem",
        "V6 theorem",
    }
)
POINT_PARAMETERS = ("r", "a2", "epsilon")
_SAFE_ARRAY_COMPONENT = re.compile(r"^[A-Za-z0-9_]+$")


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _format_path(parts: Iterable[Any]) -> str:
    rendered = "$"
    for part in parts:
        if isinstance(part, int):
            rendered += f"[{part}]"
        else:
            rendered += f".{part}"
    return rendered


def _validate_schema(schema_path: Path) -> list[str]:
    try:
        schema = _load_json(schema_path)
        Draft202012Validator.check_schema(schema)
    except (OSError, json.JSONDecodeError, SchemaError) as error:
        return [f"invalid candidate schema {schema_path}: {error}"]
    return []


def validate_scaffold(
    *,
    schema_path: Path = DEFAULT_SCHEMA,
    environment_lock_path: Path = DEFAULT_ENVIRONMENT_LOCK,
) -> list[str]:
    failures = _validate_schema(schema_path)

    try:
        environment = _load_json(environment_lock_path)
    except (OSError, json.JSONDecodeError) as error:
        failures.append(f"invalid environment lock {environment_lock_path}: {error}")
        return failures

    if environment.get("lock_status") != "INCOMPLETE_SCAFFOLD_NOT_CLAIM_BEARING":
        failures.append("environment lock lost its explicit incomplete-scaffold status")
    if environment.get("claim_bearing") is not False:
        failures.append("environment lock must remain non-claim-bearing")
    if environment.get("rounding_validation", {}).get("status") != "NOT_IMPLEMENTED":
        failures.append(
            "scaffold checker expected rounding validation to remain NOT_IMPLEMENTED"
        )
    if environment.get("issue_7_status") != "SCAFFOLD_ONLY_NOT_A_VALIDATION_RESULT":
        failures.append("environment lock has an unexpected Issue #7 status")
    capd_commit = environment.get("proposed_claim_bearing_backend", {}).get("commit")
    if not isinstance(capd_commit, str) or len(capd_commit) != 40 or any(
        character not in "0123456789abcdef" for character in capd_commit
    ):
        failures.append("proposed CAPD backend is not pinned to a full commit")
    return failures


def _resolve_hashed_file(
    root: Path, descriptor: dict[str, Any], label: str
) -> tuple[Path | None, list[str]]:
    failures: list[str] = []
    relative = Path(str(descriptor.get("path", "")))
    if relative.is_absolute() or ".." in relative.parts:
        return None, [f"{label}: path must remain inside the repository"]
    candidate = root / relative
    try:
        path = candidate.resolve(strict=True)
    except OSError:
        return None, [f"{label}: missing file {relative}"]
    try:
        path.relative_to(root)
    except ValueError:
        return None, [f"{label}: real path escapes the repository: {relative}"]
    if not path.is_file():
        return None, [f"{label}: not a regular file {relative}"]
    expected = descriptor.get("sha256")
    actual = _sha256(path)
    if actual != expected:
        failures.append(
            f"{label}: SHA-256 mismatch for {relative}: expected {expected}, got {actual}"
        )
    return path, failures


def _run_git(root: Path, *arguments: str) -> tuple[str | None, str | None]:
    try:
        completed = subprocess.run(
            ["git", "-C", os.fspath(root), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        detail = ""
        if isinstance(error, subprocess.CalledProcessError):
            detail = (error.stderr or error.stdout or "").strip()
        return None, detail or str(error)
    return completed.stdout.strip(), None


def _safe_ignored_relative(root: Path, value: Any) -> tuple[str | None, str | None]:
    relative = Path(str(value))
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        return None, "source_revision ignored path must remain inside repository"
    resolved = (root / relative).resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError:
        return None, "source_revision ignored path resolves outside repository"
    return relative.as_posix(), None


def _git_is_ancestor(
    root: Path, ancestor: str, descendant: str
) -> tuple[bool | None, str | None]:
    """Return Git ancestry without treating ``not an ancestor`` as an error."""

    try:
        completed = subprocess.run(
            [
                "git",
                "-C",
                os.fspath(root),
                "merge-base",
                "--is-ancestor",
                ancestor,
                descendant,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        return None, str(error)
    if completed.returncode == 0:
        return True, None
    if completed.returncode == 1:
        return False, None
    detail = (completed.stderr or completed.stdout or "").strip()
    return None, detail or f"git exited with status {completed.returncode}"


def _validate_source_revision(
    root: Path,
    contract_path: Path,
    source_revision: dict[str, Any],
    *,
    warnings: list[str] | None = None,
) -> list[str]:
    failures: list[str] = []
    warning_sink = warnings if warnings is not None else []
    top_level, error = _run_git(root, "rev-parse", "--show-toplevel")
    if error is not None or top_level is None:
        return [f"source_revision: cannot inspect git worktree: {error}"]
    try:
        actual_top_level = Path(top_level).resolve(strict=True)
    except OSError as resolve_error:
        return [f"source_revision: invalid git worktree path: {resolve_error}"]
    if actual_top_level != root:
        failures.append(
            "source_revision: repository_root is not the exact git worktree root"
        )

    recorded_commit = str(source_revision.get("commit", ""))
    _, commit_error = _run_git(
        root, "cat-file", "-e", f"{recorded_commit}^{{commit}}"
    )
    recorded_commit_exists = commit_error is None
    if not recorded_commit_exists:
        failures.append(
            "source_revision: recorded source commit does not exist in this repository"
        )

    head, error = _run_git(root, "rev-parse", "--verify", "HEAD")
    if error is not None or head is None:
        failures.append(f"source_revision: cannot inspect HEAD: {error}")
    elif recorded_commit_exists and head != recorded_commit:
        is_ancestor, ancestry_error = _git_is_ancestor(root, recorded_commit, head)
        if ancestry_error is not None:
            failures.append(
                "source_revision: cannot compare recorded source commit with "
                f"current HEAD: {ancestry_error}"
            )
        elif is_ancestor:
            warning_sink.append(
                "[ADVANCED_HEAD] source_revision: current HEAD is ahead of the "
                "recorded source commit; all declared hashes were checked against "
                "the current files, but this is not a clean checkout replay of the "
                "recorded commit"
            )
        else:
            warning_sink.append(
                "[DIVERGED_HEAD] source_revision: recorded source commit exists but "
                "is not an ancestor of current HEAD; all declared hashes were checked "
                "against the current files, but the current checkout has no direct "
                "descendant relationship to the recorded source state"
            )

    recorded_dirty = bool(source_revision.get("repository_dirty"))
    expected_status = (
        "DIRTY_BASE_COMMIT_WITH_HASH_BOUND_REPLAY_INPUTS_ONLY"
        if recorded_dirty
        else "CLEAN_BASE_COMMIT"
    )
    if source_revision.get("reproducibility_status") != expected_status:
        failures.append(
            "source_revision: reproducibility_status contradicts repository_dirty"
        )
    if recorded_dirty:
        warning_sink.append(
            "[RECORDED_DIRTY_SOURCE] source_revision: the contract was generated "
            "from a dirty worktree; the recorded commit alone cannot reconstruct "
            "unlisted generation-time changes"
        )

    ignored: list[str] = []
    for value in source_revision.get("ignored_paths", []):
        relative, path_error = _safe_ignored_relative(root, value)
        if path_error is not None:
            failures.append(f"source_revision: {path_error}: {value!r}")
        elif relative is not None:
            ignored.append(relative)
    try:
        contract_relative = contract_path.relative_to(root).as_posix()
    except ValueError:
        failures.append("candidate contract real path escapes repository_root")
        contract_relative = None
    if contract_relative is not None:
        ignored.append(contract_relative)
    arguments = ["status", "--porcelain=v1", "--untracked-files=all", "--", "."]
    arguments.extend(
        f":(exclude,literal){relative}" for relative in sorted(set(ignored))
    )
    status, error = _run_git(root, *arguments)
    if error is not None or status is None:
        failures.append(f"source_revision: cannot inspect dirty status: {error}")
    elif bool(status):
        warning_sink.append(
            "[CURRENT_DIRTY_WORKTREE] source_revision: the current worktree is dirty "
            "after excluding declared contract paths; declared hashes still match, "
            "but the checkout is not a clean replay environment"
        )
    return failures


def _parameter_point(contract: dict[str, Any]) -> tuple[dict[str, Decimal], list[str]]:
    failures: list[str] = []
    variables = contract["parameter_domain"]["variables"]
    if set(variables) != set(POINT_PARAMETERS):
        failures.append(
            "parameter_domain must contain exactly r, a2, and epsilon for this VdP contract"
        )
    point: dict[str, Decimal] = {}
    for name in POINT_PARAMETERS:
        interval = variables.get(name)
        if not isinstance(interval, dict):
            continue
        try:
            lower = Decimal(interval["lower_decimal"])
            upper = Decimal(interval["upper_decimal"])
        except (InvalidOperation, KeyError):
            continue
        if lower != upper:
            failures.append(
                f"parameter {name}: candidate replay contract must bind an exact point"
            )
        else:
            point[name] = lower
    return point, failures


def _record_parameter(
    record: dict[str, Any], *, branch_label: str, name: str
) -> tuple[Decimal | None, list[str]]:
    try:
        entry = record["parameters"][name]
        decimal_value = Decimal(str(entry["decimal"]))
        binary_value = float.fromhex(str(entry["binary64_hex"]))
    except (KeyError, TypeError, InvalidOperation, ValueError, OverflowError) as error:
        return None, [
            f"{branch_label}: invalid record parameter {name!r} metadata: {error}"
        ]
    if not decimal_value.is_finite() or binary_value != float(decimal_value):
        return None, [
            f"{branch_label}: parameter {name!r} decimal/binary64 metadata disagree"
        ]
    return decimal_value, []


def _require_numeric_array(
    arrays: Any,
    key: str,
    shape: tuple[int | None, ...],
    label: str,
) -> tuple[np.ndarray | None, list[str]]:
    failures: list[str] = []
    if key not in arrays.files:
        return None, [f"{label}: missing required NPZ array {key!r}"]
    try:
        value = np.asarray(arrays[key])
    except (OSError, ValueError) as error:
        return None, [f"{label}: cannot read NPZ array {key!r}: {error}"]
    if value.dtype.kind not in "fiu":
        failures.append(f"{label}: NPZ array {key!r} must be numeric")
    elif not np.all(np.isfinite(value)):
        failures.append(f"{label}: NPZ array {key!r} contains non-finite values")
    if value.ndim != len(shape) or any(
        expected is not None and actual != expected
        for actual, expected in zip(value.shape, shape)
    ):
        rendered = "x".join("*" if item is None else str(item) for item in shape)
        failures.append(
            f"{label}: NPZ array {key!r} has shape {value.shape}, expected {rendered}"
        )
    return value, failures


def _record_vector(value: Any, *, label: str) -> tuple[np.ndarray | None, list[str]]:
    try:
        vector = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as error:
        return None, [f"{label}: invalid four-component record state: {error}"]
    if vector.shape != (4,) or not np.all(np.isfinite(vector)):
        return None, [f"{label}: record state must be a finite four-vector"]
    return vector, []


def _validate_branch_npz(
    arrays_path: Path,
    *,
    prefix: str,
    record: dict[str, Any],
    label: str,
) -> list[str]:
    failures: list[str] = []
    try:
        archive = np.load(arrays_path, allow_pickle=False)
    except (OSError, ValueError) as error:
        return [f"{label}: sampled arrays are not a readable non-pickle NPZ: {error}"]
    with archive:
        state_arrays: dict[str, np.ndarray] = {}
        for suffix in ("source_state", "incoming_state", "target_state"):
            key = f"{prefix}_{suffix}"
            value, errors = _require_numeric_array(archive, key, (4,), label)
            failures.extend(errors)
            if value is not None:
                state_arrays[suffix] = value

        segments = record.get("segments")
        if not isinstance(segments, list) or not segments:
            failures.append(f"{label}: record must contain a nonempty segments array")
            return failures
        for index, segment in enumerate(segments):
            if not isinstance(segment, dict):
                failures.append(f"{label}: segment {index} is not an object")
                continue
            name = str(segment.get("name", ""))
            if not _SAFE_ARRAY_COMPONENT.fullmatch(name):
                failures.append(f"{label}: segment {index} has unsafe/empty array name")
                continue
            stem = f"{prefix}_segment_{index}_{name}"
            xi, errors = _require_numeric_array(archive, f"{stem}_xi", (None,), label)
            failures.extend(errors)
            count = int(xi.size) if xi is not None and xi.ndim == 1 else None
            state, errors = _require_numeric_array(
                archive, f"{stem}_central_state", (4, count), label
            )
            failures.extend(errors)
            length, errors = _require_numeric_array(
                archive, f"{stem}_physical_length", (count,), label
            )
            failures.extend(errors)
            action, errors = _require_numeric_array(
                archive, f"{stem}_physical_action", (count,), label
            )
            failures.extend(errors)
            if xi is not None and xi.ndim == 1:
                if xi.size < 2:
                    failures.append(f"{label}: {stem!r} needs at least two samples")
                elif not np.all(np.diff(xi) > 0.0):
                    failures.append(f"{label}: {stem!r} xi must be strictly increasing")
            if (
                state is not None
                and state.ndim == 2
                and state.shape[0] == 4
                and state.shape[1] > 0
            ):
                for endpoint, column in (("start_state", 0), ("end_state", -1)):
                    expected, state_errors = _record_vector(
                        segment.get(endpoint), label=f"{label}: {stem!r} {endpoint}"
                    )
                    failures.extend(state_errors)
                    if expected is not None and not np.array_equal(state[:, column], expected):
                        failures.append(
                            f"{label}: {stem!r} {endpoint} differs from branch record"
                        )
            for values, observable in (
                (length, "physical_length"),
                (action, "physical_action"),
            ):
                if values is not None and values.ndim == 1 and values.size >= 2:
                    recorded = segment.get(observable)
                    if not isinstance(recorded, (int, float)) or not np.isclose(
                        values[-1] - values[0],
                        float(recorded),
                        rtol=5.0e-12,
                        atol=5.0e-13,
                    ):
                        failures.append(
                            f"{label}: {stem!r} {observable} differs from branch record"
                        )

        for suffix, record_key in (
            ("source_state", "source"),
            ("target_state", "target"),
        ):
            value = state_arrays.get(suffix)
            section = record.get(record_key)
            state_value = section.get("state") if isinstance(section, dict) else None
            expected, state_errors = _record_vector(
                state_value, label=f"{label}: record {record_key}.state"
            )
            failures.extend(state_errors)
            if value is not None and expected is not None and not np.array_equal(value, expected):
                failures.append(
                    f"{label}: {prefix}_{suffix} differs from branch record"
                )
        incoming = state_arrays.get("incoming_state")
        if incoming is not None and segments:
            first_segment = segments[0] if isinstance(segments[0], dict) else {}
            expected, state_errors = _record_vector(
                first_segment.get("end_state"),
                label=f"{label}: record incoming state",
            )
            failures.extend(state_errors)
            if expected is not None and not np.array_equal(incoming, expected):
                failures.append(
                    f"{label}: {prefix}_incoming_state differs from branch record"
                )
    return failures


def validate_contract(
    contract_path: Path,
    *,
    schema_path: Path = DEFAULT_SCHEMA,
    repository_root: Path = ROOT,
    warnings: list[str] | None = None,
) -> list[str]:
    """Return hard contract failures and optionally collect non-fatal warnings.

    ``source_revision.repository_dirty`` describes the worktree when the
    contract was built.  A later clean commit or a later dirty checkout does
    not rewrite that historical fact.  Callers that need the distinction can
    pass a mutable ``warnings`` list; the legacy return value remains a list of
    hard failures.
    """

    failures = _validate_schema(schema_path)
    if failures:
        return failures

    try:
        root = repository_root.resolve(strict=True)
    except OSError as error:
        return [f"invalid repository_root {repository_root}: {error}"]
    if not root.is_dir():
        return [f"repository_root is not a directory: {root}"]
    try:
        resolved_contract_path = contract_path.resolve(strict=True)
    except OSError as error:
        return [f"invalid candidate contract {contract_path}: {error}"]
    try:
        resolved_contract_path.relative_to(root)
    except ValueError:
        return ["candidate contract real path must remain inside repository_root"]

    schema = _load_json(schema_path)
    try:
        contract = _load_json(resolved_contract_path)
    except (OSError, json.JSONDecodeError) as error:
        return [f"invalid candidate contract {contract_path}: {error}"]

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(contract), key=lambda item: list(item.path)):
        failures.append(f"{_format_path(error.path)}: {error.message}")
    if failures:
        return failures

    if contract["status"] != "DRAFT_CANDIDATE_ONLY" or contract["claim_bearing"]:
        failures.append("candidate checker refuses claim-bearing contract status")
    if contract["final_status"] != "NOT_RUN":
        failures.append("candidate checker refuses a final validation result")

    failures.extend(
        _validate_source_revision(
            root,
            resolved_contract_path,
            contract["source_revision"],
            warnings=warnings,
        )
    )

    seen_ids: set[str] = set()
    for section in ("observables", "obligations"):
        for row in contract[section]:
            identifier = str(row["id"])
            if identifier in seen_ids:
                failures.append(f"duplicate contract identifier: {identifier}")
            seen_ids.add(identifier)

    for name, interval in contract["parameter_domain"]["variables"].items():
        try:
            lower = Decimal(interval["lower_decimal"])
            upper = Decimal(interval["upper_decimal"])
        except InvalidOperation:
            failures.append(f"parameter {name}: invalid exact decimal endpoint")
            continue
        if not (lower.is_finite() and upper.is_finite()):
            failures.append(f"parameter {name}: endpoints must be finite")
        elif lower > upper:
            failures.append(
                f"parameter {name}: lower endpoint {lower} exceeds upper {upper}"
            )
    point, point_errors = _parameter_point(contract)
    failures.extend(point_errors)

    theory_roles: list[str] = []
    for index, descriptor in enumerate(contract["theory_bindings"]):
        theory_roles.append(str(descriptor.get("role", "")))
        _, errors = _resolve_hashed_file(
            root, descriptor, f"theory_bindings[{index}]"
        )
        failures.extend(errors)
    if set(theory_roles) != REQUIRED_THEORY_ROLES:
        missing = sorted(REQUIRED_THEORY_ROLES - set(theory_roles))
        unexpected = sorted(set(theory_roles) - REQUIRED_THEORY_ROLES)
        detail: list[str] = []
        if missing:
            detail.append("missing " + ", ".join(missing))
        if unexpected:
            detail.append("unexpected " + ", ".join(unexpected))
        failures.append("theory_bindings role set is incomplete (" + "; ".join(detail) + ")")
    if len(theory_roles) != len(set(theory_roles)):
        failures.append("theory_bindings roles must be unique")

    replay_roles: list[str] = []
    replay_paths: list[Path] = []
    configuration_path: Path | None = None
    for index, descriptor in enumerate(contract["replay_bindings"]):
        role = str(descriptor.get("role", ""))
        replay_roles.append(role)
        path, errors = _resolve_hashed_file(
            root, descriptor, f"replay_bindings[{index}]"
        )
        failures.extend(errors)
        if path is not None and not errors:
            replay_paths.append(path)
            if role == "candidate configuration":
                configuration_path = path
            elif role.startswith("candidate generator source ") and path.suffix != ".py":
                failures.append(
                    f"replay_bindings[{index}]: candidate generator source must be Python"
                )
    if replay_roles.count("candidate configuration") != 1:
        failures.append("replay_bindings must contain exactly one candidate configuration")
    generator_roles = [
        role for role in replay_roles if role.startswith("candidate generator source ")
    ]
    if not generator_roles:
        failures.append("replay_bindings must contain candidate generator source code")
    if len(replay_roles) != len(set(replay_roles)):
        failures.append("replay_bindings roles must be unique")
    if len(replay_paths) != len(set(replay_paths)):
        failures.append("replay_bindings must resolve to distinct files")
    if configuration_path is not None:
        try:
            configuration = _load_json(configuration_path)
            primary = configuration["parameters"]["primary"]
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
            failures.append(f"candidate configuration is malformed: {error}")
        else:
            if not isinstance(primary, dict):
                failures.append(
                    "candidate configuration parameters.primary must be an object"
                )
                primary = {}
            for name, expected in point.items():
                try:
                    actual = Decimal(str(primary[name]))
                except (KeyError, TypeError, InvalidOperation) as error:
                    failures.append(
                        f"candidate configuration parameter {name!r} is invalid: {error}"
                    )
                    continue
                if not actual.is_finite() or actual != expected:
                    failures.append(
                        f"candidate configuration parameter {name!r} differs from contract"
                    )

    for obligation_index, obligation in enumerate(contract["obligations"]):
        for evidence_index, descriptor in enumerate(
            obligation.get("candidate_evidence", [])
        ):
            _, errors = _resolve_hashed_file(
                root,
                descriptor,
                (
                    f"obligations[{obligation_index}]"
                    f".candidate_evidence[{evidence_index}]"
                ),
            )
            failures.extend(errors)

    for index, branch in enumerate(contract["candidate_branches"]):
        record_path, record_errors = _resolve_hashed_file(
            root, branch["record"], f"candidate_branches[{index}].record"
        )
        failures.extend(record_errors)
        arrays_path: Path | None = None
        array_errors: list[str] = []
        if "arrays" in branch:
            arrays_path, array_errors = _resolve_hashed_file(
                root,
                branch["arrays"],
                f"candidate_branches[{index}].arrays",
            )
            failures.extend(array_errors)
        if record_path is not None and not record_errors:
            try:
                record = _load_json(record_path)
            except (OSError, json.JSONDecodeError) as error:
                failures.append(f"candidate branch record is not JSON: {error}")
            else:
                if not isinstance(record, dict):
                    failures.append(
                        f"candidate_branches[{index}] record must be a JSON object"
                    )
                    continue
                if record.get("claim_bearing") is not False:
                    failures.append(
                        f"candidate_branches[{index}] record must be non-claim-bearing"
                    )
                if not str(record.get("evidence_status", "")).startswith(
                    "COMPUTED/E1_NONRIGOROUS"
                ):
                    failures.append(
                        f"candidate_branches[{index}] record has unexpected evidence status"
                    )
                if record.get("branch_id") != branch["branch_id"]:
                    failures.append(
                        f"candidate_branches[{index}] branch_id differs from its record"
                    )
                if record.get("branch_type") != branch["branch_type"]:
                    failures.append(
                        f"candidate_branches[{index}] branch_type differs from its record"
                    )
                if record.get("schema_version") != "rfsn-vdp-sampled-branch/1":
                    failures.append(
                        f"candidate_branches[{index}] record has unexpected schema_version"
                    )
                for name, expected in point.items():
                    actual, parameter_errors = _record_parameter(
                        record,
                        branch_label=f"candidate_branches[{index}]",
                        name=name,
                    )
                    failures.extend(parameter_errors)
                    if actual is not None and actual != expected:
                        failures.append(
                            f"candidate_branches[{index}] parameter {name!r} "
                            "differs from contract"
                        )
                if arrays_path is not None and not array_errors:
                    prefix = str(branch.get("array_prefix", ""))
                    expected_prefix = str(branch["branch_id"]).replace("-", "_")
                    if prefix != expected_prefix:
                        failures.append(
                            f"candidate_branches[{index}] array_prefix is not derived "
                            "from branch_id"
                        )
                    else:
                        failures.extend(
                            _validate_branch_npz(
                                arrays_path,
                                prefix=prefix,
                                record=record,
                                label=f"candidate_branches[{index}]",
                            )
                        )

    environment_path, errors = _resolve_hashed_file(
        root, contract["environment_lock"], "environment_lock"
    )
    failures.extend(errors)
    if environment_path is not None and not errors:
        try:
            environment = _load_json(environment_path)
        except (OSError, json.JSONDecodeError) as error:
            failures.append(f"referenced environment lock is invalid JSON: {error}")
        else:
            if not isinstance(environment, dict):
                failures.append("referenced environment lock must be a JSON object")
                return failures
            if environment.get("claim_bearing") is not False:
                failures.append("referenced environment lock is unexpectedly claim-bearing")
            if environment.get("rounding_validation", {}).get("status") != "NOT_IMPLEMENTED":
                failures.append(
                    "candidate contract may reference only the explicit pre-validation scaffold"
                )
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "contract",
        nargs="?",
        type=Path,
        help="candidate contract JSON; omit to check only the schema and lock scaffold",
    )
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--repository-root", type=Path, default=ROOT)
    arguments = parser.parse_args()

    if arguments.contract is None:
        failures = validate_scaffold(schema_path=arguments.schema)
        success = "PASS: candidate schema and incomplete environment scaffold are valid"
    else:
        warnings: list[str] = []
        failures = validate_contract(
            arguments.contract,
            schema_path=arguments.schema,
            repository_root=arguments.repository_root,
            warnings=warnings,
        )
        warning_codes = {
            warning.split("]", 1)[0].removeprefix("[")
            for warning in warnings
            if warning.startswith("[") and "]" in warning
        }
        if "ADVANCED_HEAD" in warning_codes:
            success = (
                "PASS_WITH_ADVANCED_HEAD_WARNING: declared candidate hashes match "
                "the current files, but current HEAD is newer than the recorded "
                "source commit; no interval validation was performed"
            )
        elif "DIVERGED_HEAD" in warning_codes:
            success = (
                "PASS_WITH_DIVERGED_HEAD_WARNING: declared candidate hashes match "
                "the current files, but current HEAD does not descend from the "
                "recorded source commit; no interval validation was performed"
            )
        elif warning_codes & {"RECORDED_DIRTY_SOURCE", "CURRENT_DIRTY_WORKTREE"}:
            success = (
                "PASS_WITH_DIRTY_SOURCE_WARNING: listed candidate inputs are "
                "hash-bound, but a dirty source state is not reproduced by the "
                "recorded commit alone; no interval validation was performed"
            )
        else:
            success = (
                "PASS: candidate contract is well-formed and hash-bound to a "
                "clean base commit; no interval validation was performed"
            )
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        raise SystemExit(1)
    if arguments.contract is not None:
        for warning in warnings:
            print(f"WARNING: {warning}")
    print(success)


if __name__ == "__main__":
    main()
