"""Build a hash-bound, non-claim-bearing van der Pol V6 contract.

The public :func:`build_vdp_candidate_contract` entry point is intended for
direct use by ``numerics.run_vdp_master`` (or another artifact producer).  It
binds already-written candidate records and arrays to the local V2--V6 theorem
texts, the candidate configuration, the generator sources, and the candidate
environment lock.  Its exact parameter point is supplied explicitly by the
caller and cross-checked against both the configuration and every branch
record.  The resulting JSON is a replay manifest for future Issue #7 work; it
cannot report an interval-validation result.

Before replacing the requested output, the builder calls the repository's
existing candidate-contract validator.  A failed self-check therefore leaves
an existing output untouched.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any, Mapping, Sequence

from validation.check_candidate_contract import validate_contract


REPOSITORY_NAME = "h-lu/rfsn-ii-positive-parameter-pde"
SCHEMA_VERSION = "rfsn-candidate-validation-contract/2"
DEFAULT_CONTRACT_ID = "vdp-v6-candidate"

THEORY_FILES: tuple[tuple[str, str], ...] = (
    ("V2 theorem", "van-der-pol/CENTRAL_CONTINUATION.md"),
    ("V3 theorem", "van-der-pol/POSITIVE_POLE_FINITE_PART.md"),
    ("V4 theorem", "van-der-pol/OUTER_FUTURE_STAYING.md"),
    ("V5 theorem", "van-der-pol/CENTRAL_OUTER_MATCHING.md"),
    ("V5A theorem", "van-der-pol/OUTER_ALGEBRAIC_FINITE_PART.md"),
    ("V6 theorem", "van-der-pol/TWO_END_RETURN_EXIT_AND_PDE.md"),
)
ENVIRONMENT_LOCK_PATH = "validation/environment.lock.json"
SCHEMA_PATH = "validation/candidate_contract.schema.json"

ALLOWED_BRANCH_TYPES = frozenset(
    {
        "finite_return",
        "stable_cut",
        "pole_exit_candidate",
        "algebraic_exit_candidate",
        "lateral_exit",
    }
)


class CandidateContractBuildError(RuntimeError):
    """Raised when inputs or the generated candidate contract are invalid."""


@dataclass(frozen=True)
class BranchDescriptor:
    """Files describing one non-rigorous branch candidate.

    ``type`` deliberately matches the compact descriptor key accepted from a
    master artifact dictionary.  The emitted schema field is ``branch_type``.
    ``arrays`` may be omitted for a record without a dense numeric payload.
    """

    branch_id: str
    type: str
    record: str | os.PathLike[str]
    arrays: str | os.PathLike[str] | None = None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _repository_file(repository_root: Path, value: str | os.PathLike[str]) -> Path:
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = repository_root / candidate
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise CandidateContractBuildError(
            f"candidate input does not exist: {candidate}"
        ) from error
    if not resolved.is_file():
        raise CandidateContractBuildError(f"candidate input is not a file: {candidate}")
    try:
        resolved.relative_to(repository_root)
    except ValueError as error:
        raise CandidateContractBuildError(
            f"candidate input must remain inside the repository: {candidate}"
        ) from error
    return resolved


def _hashed_file(
    repository_root: Path,
    value: str | os.PathLike[str],
    *,
    role: str,
) -> dict[str, str]:
    path = _repository_file(repository_root, value)
    return {
        "path": path.relative_to(repository_root).as_posix(),
        "sha256": _sha256(path),
        "role": role,
    }


def _run_git(repository_root: Path, *arguments: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", os.fspath(repository_root), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        detail = ""
        if isinstance(error, subprocess.CalledProcessError):
            detail = (error.stderr or error.stdout or "").strip()
        suffix = f": {detail}" if detail else ""
        raise CandidateContractBuildError(
            f"cannot inspect repository revision with git{suffix}"
        ) from error
    return completed.stdout.strip()


def _repository_dirty(
    repository_root: Path,
    *,
    ignored_paths: Sequence[Path] = (),
) -> bool:
    arguments = ["status", "--porcelain=v1", "--untracked-files=all", "--", "."]
    for path in ignored_paths:
        try:
            relative = path.resolve(strict=False).relative_to(repository_root)
        except ValueError as error:
            raise CandidateContractBuildError(
                f"ignored source-revision path is outside repository: {path}"
            ) from error
        arguments.append(f":(exclude,literal){relative.as_posix()}")
    return bool(_run_git(repository_root, *arguments))


def _source_revision(
    repository_root: Path,
    *,
    ignored_paths: Sequence[Path] = (),
) -> dict[str, Any]:
    commit = _run_git(repository_root, "rev-parse", "--verify", "HEAD")
    if len(commit) != 40 or any(character not in "0123456789abcdef" for character in commit):
        raise CandidateContractBuildError(
            f"git returned a non-full or non-lowercase commit id: {commit!r}"
        )
    dirty = _repository_dirty(repository_root, ignored_paths=ignored_paths)
    ignored_relative = [
        path.resolve(strict=False).relative_to(repository_root).as_posix()
        for path in ignored_paths
    ]
    return {
        "repository": REPOSITORY_NAME,
        "commit": commit,
        "repository_dirty": dirty,
        "reproducibility_status": (
            "DIRTY_BASE_COMMIT_WITH_HASH_BOUND_REPLAY_INPUTS_ONLY"
            if dirty
            else "CLEAN_BASE_COMMIT"
        ),
        "ignored_paths": ignored_relative,
        "note": (
            "Dirty status excludes only the generated contract path and was "
            "sampled before writing it; it is historical metadata and need not "
            "equal the status of a later checkout.  A dirty source commit is not "
            "a complete snapshot of generation-time changes; only the listed "
            "hash-bound inputs are replayable."
        ),
    }


def _normalise_branch_descriptor(
    value: BranchDescriptor | Mapping[str, Any],
) -> BranchDescriptor:
    if isinstance(value, BranchDescriptor):
        descriptor = value
    elif isinstance(value, Mapping):
        try:
            branch_type = value.get("type", value.get("branch_type"))
            descriptor = BranchDescriptor(
                branch_id=str(value["branch_id"]),
                type=str(branch_type),
                record=value["record"],
                arrays=value.get("arrays"),
            )
        except KeyError as error:
            raise CandidateContractBuildError(
                f"branch descriptor is missing {error.args[0]!r}"
            ) from error
    else:
        raise CandidateContractBuildError(
            "branch descriptors must be BranchDescriptor objects or mappings"
        )
    if descriptor.type not in ALLOWED_BRANCH_TYPES:
        allowed = ", ".join(sorted(ALLOWED_BRANCH_TYPES))
        raise CandidateContractBuildError(
            f"branch {descriptor.branch_id!r} has unsupported type "
            f"{descriptor.type!r}; expected one of {allowed}"
        )
    return descriptor


def _created_at(value: datetime | str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")
    if isinstance(value, str):
        return value
    if value.tzinfo is None or value.utcoffset() is None:
        raise CandidateContractBuildError("created_at datetime must include a timezone")
    return value.isoformat(timespec="seconds")


def _exact_point(value: str) -> dict[str, str]:
    return {
        "lower_decimal": value,
        "upper_decimal": value,
        "endpoint_semantics": "exact_base10_rational",
    }


def _decimal_text(value: Any, *, name: str) -> str:
    """Return a finite base-10 value without pretending binary64 is exact."""

    if isinstance(value, bool):
        raise CandidateContractBuildError(f"parameter {name!r} must be numeric")
    if isinstance(value, Decimal):
        text = str(value)
    elif isinstance(value, (str, int, float)):
        text = str(value)
    else:
        raise CandidateContractBuildError(
            f"parameter {name!r} must be a decimal string or scalar"
        )
    try:
        number = Decimal(text)
    except InvalidOperation as error:
        raise CandidateContractBuildError(
            f"parameter {name!r} has invalid decimal value {text!r}"
        ) from error
    if not number.is_finite():
        raise CandidateContractBuildError(f"parameter {name!r} must be finite")
    return text


def _normalise_parameter_point(value: Mapping[str, Any]) -> dict[str, str]:
    expected = ("r", "a2", "epsilon")
    missing = [name for name in expected if name not in value]
    extra = sorted(set(value) - set(expected))
    if missing or extra:
        details: list[str] = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if extra:
            details.append(f"unexpected {', '.join(extra)}")
        raise CandidateContractBuildError(
            "parameter_point must contain exactly r, a2, epsilon ("
            + "; ".join(details)
            + ")"
        )
    return {name: _decimal_text(value[name], name=name) for name in expected}


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CandidateContractBuildError(f"{label} is not valid JSON: {path}") from error
    if not isinstance(value, dict):
        raise CandidateContractBuildError(f"{label} must be a JSON object: {path}")
    return value


def _record_parameter_decimal(
    record: Mapping[str, Any], *, branch_id: str, name: str
) -> Decimal:
    try:
        entry = record["parameters"][name]
        text = entry["decimal"]
        binary64_hex = entry["binary64_hex"]
    except (KeyError, TypeError) as error:
        raise CandidateContractBuildError(
            f"branch {branch_id!r} record lacks parameter {name!r} metadata"
        ) from error
    try:
        number = Decimal(str(text))
        binary_value = float.fromhex(str(binary64_hex))
    except (InvalidOperation, ValueError, OverflowError) as error:
        raise CandidateContractBuildError(
            f"branch {branch_id!r} has invalid parameter {name!r} metadata"
        ) from error
    if not number.is_finite() or not (binary_value == float(number)):
        raise CandidateContractBuildError(
            f"branch {branch_id!r} parameter {name!r} decimal/binary64 mismatch"
        )
    return number


def _crosscheck_branch_record(
    descriptor: BranchDescriptor,
    record: Mapping[str, Any],
    parameter_point: Mapping[str, str],
) -> None:
    label = descriptor.branch_id
    if record.get("branch_id") != label:
        raise CandidateContractBuildError(
            f"branch {label!r} branch_id differs from its record"
        )
    if record.get("branch_type") != descriptor.type:
        raise CandidateContractBuildError(
            f"branch {label!r} type differs from its record"
        )
    if record.get("claim_bearing") is not False:
        raise CandidateContractBuildError(
            f"branch {label!r} record must remain non-claim-bearing"
        )
    if not str(record.get("evidence_status", "")).startswith(
        "COMPUTED/E1_NONRIGOROUS"
    ):
        raise CandidateContractBuildError(
            f"branch {label!r} record has unexpected evidence status"
        )
    for name, expected_text in parameter_point.items():
        actual = _record_parameter_decimal(record, branch_id=label, name=name)
        if actual != Decimal(expected_text):
            raise CandidateContractBuildError(
                f"branch {label!r} parameter {name!r} differs from parameter_point"
            )


def _crosscheck_configuration(
    configuration: Mapping[str, Any], parameter_point: Mapping[str, str]
) -> None:
    try:
        primary = configuration["parameters"]["primary"]
    except (KeyError, TypeError) as error:
        raise CandidateContractBuildError(
            "candidate configuration lacks parameters.primary"
        ) from error
    if not isinstance(primary, Mapping):
        raise CandidateContractBuildError(
            "candidate configuration parameters.primary must be an object"
        )
    for name, expected_text in parameter_point.items():
        if name not in primary:
            raise CandidateContractBuildError(
                f"candidate configuration lacks primary parameter {name!r}"
            )
        actual_text = _decimal_text(primary[name], name=name)
        if Decimal(actual_text) != Decimal(expected_text):
            raise CandidateContractBuildError(
                f"candidate configuration parameter {name!r} differs from parameter_point"
            )


def build_vdp_candidate_contract(
    *,
    repository_root: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    branches: Sequence[BranchDescriptor | Mapping[str, Any]],
    candidate_evidence_paths: Sequence[str | os.PathLike[str]],
    parameter_point: Mapping[str, Any],
    configuration_path: str | os.PathLike[str],
    generator_source_paths: Sequence[str | os.PathLike[str]],
    contract_id: str = DEFAULT_CONTRACT_ID,
    created_at: datetime | str | None = None,
) -> dict[str, Any]:
    """Write and return a self-validated V6 candidate contract.

    Paths in branch descriptors, ``candidate_evidence_paths``, and replay
    bindings may be
    repository-relative or absolute.  Every bound input must resolve to a
    regular file inside ``repository_root``.  The builder accepts the compact
    mapping key ``type`` requested by the numerical master and also
    ``branch_type`` for callers already using the schema vocabulary.

    This function raises :class:`CandidateContractBuildError` on malformed
    input or any failure reported by :func:`validate_contract`.
    """

    root = Path(repository_root).resolve(strict=True)
    if not root.is_dir():
        raise CandidateContractBuildError(f"repository root is not a directory: {root}")

    branch_inputs = [_normalise_branch_descriptor(item) for item in branches]
    if not branch_inputs:
        raise CandidateContractBuildError("at least one branch descriptor is required")
    branch_ids = [item.branch_id for item in branch_inputs]
    if len(set(branch_ids)) != len(branch_ids):
        raise CandidateContractBuildError("branch_id values must be unique")
    if not candidate_evidence_paths:
        raise CandidateContractBuildError(
            "at least one candidate evidence path is required"
        )
    if not generator_source_paths:
        raise CandidateContractBuildError(
            "at least one candidate generator source path is required"
        )

    parameter_values = _normalise_parameter_point(parameter_point)

    destination = Path(output_path)
    if not destination.is_absolute():
        destination = root / destination
    destination = destination.resolve(strict=False)
    try:
        destination_relative = destination.relative_to(root)
    except ValueError as error:
        raise CandidateContractBuildError(
            f"contract output must remain inside the repository: {destination}"
        ) from error
    if destination_relative.parts and destination_relative.parts[0] == ".git":
        raise CandidateContractBuildError("contract output may not be written under .git")
    if destination.exists() and not destination.is_file():
        raise CandidateContractBuildError(
            f"contract output exists and is not a regular file: {destination}"
        )

    source_revision = _source_revision(root, ignored_paths=(destination,))
    schema_path = _repository_file(root, SCHEMA_PATH)
    theory_bindings = [
        _hashed_file(root, relative_path, role=role)
        for role, relative_path in THEORY_FILES
    ]
    environment_lock = _hashed_file(
        root,
        ENVIRONMENT_LOCK_PATH,
        role="non-claim-bearing candidate environment lock",
    )
    configuration_file = _repository_file(root, configuration_path)
    configuration = _load_json_object(
        configuration_file, label="candidate configuration"
    )
    _crosscheck_configuration(configuration, parameter_values)
    replay_bindings = [
        _hashed_file(
            root,
            configuration_file,
            role="candidate configuration",
        ),
        *[
            _hashed_file(
                root,
                path,
                role=f"candidate generator source {index + 1}",
            )
            for index, path in enumerate(generator_source_paths)
        ],
    ]
    replay_paths = [row["path"] for row in replay_bindings]
    if len(set(replay_paths)) != len(replay_paths):
        raise CandidateContractBuildError("replay binding paths must be unique")
    evidence = [
        _hashed_file(root, path, role=f"candidate evidence {index + 1}")
        for index, path in enumerate(candidate_evidence_paths)
    ]

    candidate_branches: list[dict[str, Any]] = []
    array_prefixes: list[str] = []
    for descriptor in branch_inputs:
        record_file = _repository_file(root, descriptor.record)
        record = _load_json_object(record_file, label="candidate branch record")
        _crosscheck_branch_record(descriptor, record, parameter_values)
        array_prefix = descriptor.branch_id.replace("-", "_")
        row: dict[str, Any] = {
            "branch_id": descriptor.branch_id,
            "branch_type": descriptor.type,
            "record": _hashed_file(
                root,
                record_file,
                role=f"{descriptor.branch_id} candidate record",
            ),
            "evidence_status": "COMPUTED/E1_NONRIGOROUS_CANDIDATE",
        }
        if descriptor.arrays is not None:
            row["array_prefix"] = array_prefix
            array_prefixes.append(array_prefix)
            row["arrays"] = _hashed_file(
                root,
                descriptor.arrays,
                role=f"{descriptor.branch_id} sampled numeric arrays",
            )
        candidate_branches.append(row)
    if len(set(array_prefixes)) != len(array_prefixes):
        raise CandidateContractBuildError(
            "branch identifiers produce colliding sampled-array prefixes"
        )

    bound_descriptors = [
        *theory_bindings,
        *replay_bindings,
        environment_lock,
        *evidence,
    ]
    for branch in candidate_branches:
        bound_descriptors.append(branch["record"])
        if "arrays" in branch:
            bound_descriptors.append(branch["arrays"])
    bound_paths = {
        (root / descriptor["path"]).resolve(strict=True)
        for descriptor in bound_descriptors
    }
    bound_paths.add(schema_path)
    if destination in bound_paths:
        raise CandidateContractBuildError(
            "contract output may not overwrite a bound input or its schema"
        )

    contract: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "contract_id": contract_id,
        "status": "DRAFT_CANDIDATE_ONLY",
        "claim_bearing": False,
        "theorem_target": "V6",
        "created_at": _created_at(created_at),
        "source_revision": source_revision,
        "theory_bindings": theory_bindings,
        "replay_bindings": replay_bindings,
        "parameter_domain": {
            "selection_status": "PRESELECTED_FOR_FUTURE_VALIDATION_NOT_YET_RUN",
            "variables": {
                name: _exact_point(value)
                for name, value in parameter_values.items()
            },
            "selection_note": (
                "Exact point parameters for deterministic candidate replay; "
                "no outward-rounded parameter box has been validated."
            ),
        },
        "observables": [
            {
                "id": "V6.first_event_target",
                "definition": (
                    "candidate first return or first-exit target in the declared "
                    "local numerical chart"
                ),
                "normalization": "branch-record target-face convention",
                "status": "DRAFT_DEFINITION",
            },
            {
                "id": "V6.physical_length",
                "definition": "physical length accumulated along one finite branch",
                "normalization": "branch record plus its declared end counterterm",
                "status": "FIXED_DEFINITION",
            },
            {
                "id": "V6.physical_action",
                "definition": "physical action accumulated along one finite branch",
                "normalization": "branch record plus its declared end counterterm",
                "status": "FIXED_DEFINITION",
            },
            {
                "id": "V6.local_winding_label",
                "definition": (
                    "integer local winding label after future rigorous chart calibration"
                ),
                "normalization": "V6 chart-local marked-section convention",
                "status": "DRAFT_DEFINITION",
            },
        ],
        "obligations": [
            {
                "id": "V6.candidate_replay_inputs",
                "theorem_clause": "V6(1)--(5)",
                "predicate": (
                    "all listed floating-point branch and finite-part inputs are "
                    "present and hash-bound for deterministic replay"
                ),
                "status": "CANDIDATE_READY",
                "candidate_evidence": evidence,
            },
            {
                "id": "V6.outward_rounded_validation",
                "theorem_clause": "Issue #7 validation gate for V6",
                "predicate": (
                    "outward-rounded enclosures verify exhaustive first-event cells, "
                    "transversality, chart labels, and length/action bounds"
                ),
                "status": "BLOCKED",
                "blocker": (
                    "The candidate environment has no implemented directed-rounding "
                    "or interval replay backend."
                ),
            },
        ],
        "candidate_branches": candidate_branches,
        "environment_lock": environment_lock,
        "final_status": "NOT_RUN",
        "nonclaims": [
            "This contract records floating-point candidate inputs only.",
            "No outward-rounded integration or interval enclosure was performed.",
            "No exhaustive V6 return/first-exit cell atlas is certified.",
            "Numerical transverse signs are not exact V2 action signs.",
            "A winding proxy is not an integer V6 winding certificate.",
            (
                "The recorded base commit does not snapshot unlisted dirty-worktree "
                "files; only explicitly hash-bound inputs are replay bindings."
            ),
        ],
    }

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temporary_path = Path(stream.name)
            json.dump(contract, stream, indent=2, sort_keys=True)
            stream.write("\n")
        failures = validate_contract(
            temporary_path,
            schema_path=schema_path,
            repository_root=root,
        )
        if failures:
            rendered = "\n".join(f"- {failure}" for failure in failures)
            raise CandidateContractBuildError(
                f"generated candidate contract failed self-validation:\n{rendered}"
            )
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
    return contract


__all__ = [
    "ALLOWED_BRANCH_TYPES",
    "BranchDescriptor",
    "CandidateContractBuildError",
    "DEFAULT_CONTRACT_ID",
    "THEORY_FILES",
    "build_vdp_candidate_contract",
]
