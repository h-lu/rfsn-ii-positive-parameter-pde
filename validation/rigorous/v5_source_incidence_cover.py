#!/usr/bin/env python3
"""Run and verify the fixed 64x128x48 V5 source-incidence cover."""

from __future__ import annotations

import argparse
import concurrent.futures
import contextlib
import dataclasses
import fcntl
import hashlib
import itertools
import json
import math
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence


RIGOROUS = Path(__file__).resolve().parent
REPOSITORY = RIGOROUS.parents[1]
CONFIG_PATH = RIGOROUS / "config" / "vdp_v5_source_incidence_cover_v1.json"
GRID = (64, 128, 48)
CELL_COUNT = 393216
CONFIG_SCHEMA = "rfsn-vdp-v5-source-incidence-cover-config/1"
MANIFEST_SCHEMA = "rfsn-vdp-v5-source-incidence-cover-manifest/1"
SUMMARY_SCHEMA = "rfsn-vdp-v5-source-incidence-cover-summary/1"
CELL_SCHEMA = "rfsn-vdp-v5-source-incidence-merged-cell/1"
FAST_MODE = "incidence-merged-cell"
ROBUST_MODE = "incidence-merged-cell-rect2"
OUTPUT_MODES = {FAST_MODE: "C0_HO_RECT2_FAST", ROBUST_MODE: "C0_RECT2_ROBUST"}
TARGET_GRAPH_CONTRACT = {
    "base_half_width": "27/200000", "normal_half_width": "1/12500",
    "slope_bound": "7/10", "source_slope_limit": "1/2",
}
REQUIRED_GATES = (
    "anchor_interval_newton", "anchor_root_boxes_contain_zero",
    "exact_source_zero_energy_identity", "theta_coordinate_regular",
    "complete_graph_error_half_union", "complete_anchor_graph_error_slice_union",
    "complete_phase_slab_union", "continuation_faces",
    "phase_monotonicity_on_continuation_cover",
    "anchor_interval_newton_by_slice", "anchor_root_contains_zero_by_slice",
    "continuation_faces_by_half", "root_derivatives",
    "fixed_eta_n_theta_negative", "exterior_seam_P_negative",
    "source_slope_below_one_half", "graph_slope_contraction",
    "negative_K1_sheet_patch", "regular_source_to_terminal_passage",
    "base_budget", "nonempty_candidates",
)
MANIFEST_NAME = "manifest.json"
MANIFEST_HASH_NAME = "manifest.sha256"
SUMMARY_NAME = "summary.json"
COMPILE_FLAGS = (
    "-O2", "-DNDEBUG", "-fno-fast-math", "-frounding-math",
    "-ffp-contract=off", "-fno-tree-vectorize", "-fno-ipa-pure-const",
    "-Wall", "-Wextra", "-Werror", "-Wno-overloaded-virtual",
)
FORBIDDEN_FLAGS = {"-ffast-math", "-Ofast", "-ffinite-math-only"}
HEX_FLOAT = re.compile(
    r"^-?0x(?:[0-9a-f]+(?:\.[0-9a-f]*)?|\.[0-9a-f]+)p[+-]?\d+$"
)

EXTREMA_SPECS = (
    ("min_incidence_base_margin", "incidence_base_margin", "lower", "min"),
    ("max_source_slope", "source_abs_db_over_minus_dn", "upper", "max"),
    ("max_fixed_eta_n_theta", "fixed_eta_n_theta", "upper", "max"),
    ("max_exterior_seam_P", "exterior_seam_P", "upper", "max"),
    ("min_terminal_Q", "candidate_terminal_Q", "lower", "min"),
    ("max_terminal_Q", "candidate_terminal_Q", "upper", "max"),
    ("min_source_phase_margin", "candidate_source_u1_phase_domain_margin",
     "lower", "min"),
    ("min_source_U", "candidate_source_U", "lower", "min"),
    ("max_candidate_seam_P", "candidate_seam_P", "upper", "max"),
    ("min_pre_seam_U_margin", "candidate_pre_seam_U_margin", "lower", "min"),
    ("min_dense_W", "candidate_dense_W", "lower", "min"),
)


class CoverError(RuntimeError): pass
class IntegrityError(CoverError): pass
class CellFormatError(CoverError): pass


@dataclasses.dataclass(frozen=True)
class CellCheck:
    status: str; extrema: Mapping[str, tuple[float, str]]


@dataclasses.dataclass(frozen=True)
class CellOutcome:
    index: tuple[int, int, int]; kind: str; attempts: tuple[str, ...]
    error: str | None = None; wrote_cell: bool = False


def _require(condition: bool, message: str,
             error: type[CoverError] = IntegrityError) -> None:
    if not condition:
        raise error(message)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_loads(payload: bytes, label: str,
                error: type[CoverError] = IntegrityError) -> Any:
    try:
        return json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise error(f"{label}: invalid strict JSON: {exc}") from exc


def _json_file(path: Path, label: str,
               error: type[CoverError] = IntegrityError) -> Any:
    try:
        return _json_loads(path.read_bytes(), label, error)
    except OSError as exc:
        raise error(f"{label}: cannot read {path}: {exc}") from exc


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _relative_path(value: Any, label: str) -> Path:
    _require(isinstance(value, str), f"{label}: path is not a string")
    path = Path(value)
    _require(not path.is_absolute() and ".." not in path.parts,
             f"{label}: unsafe relative path")
    return path


def _validate_config(config: Any) -> dict[str, Any]:
    _require(isinstance(config, dict), "cover configuration is not an object")
    _require(config.get("schema_version") == CONFIG_SCHEMA,
             "unexpected cover configuration schema")
    _require(config.get("cover_id") == "vdp-v5-source-incidence-cover-v1" and
             config.get("box_id") == "vdp-positive-box-v2",
             "cover identity changed")
    _require(config.get("grid") == list(GRID) and math.prod(GRID) == CELL_COUNT,
             "cover grid must be exactly 64x128x48 = 393216")
    probe = config.get("probe")
    _require(isinstance(probe, dict), "missing probe configuration")
    _relative_path(probe.get("source"), "probe/source")
    _require(probe.get("cell_schema_version") == CELL_SCHEMA and
             probe.get("fast_mode") == FAST_MODE and
             probe.get("fallback_mode") == ROBUST_MODE and
             probe.get("output_modes") == OUTPUT_MODES,
             "probe modes or schema changed")

    compile_config = config.get("compile")
    _require(isinstance(compile_config, dict) and
             compile_config.get("compiler") == "/usr/bin/g++" and
             compile_config.get("language_standard") == "c++17" and
             tuple(compile_config.get("flags", ())) == COMPILE_FLAGS,
             "strict compile contract changed")
    headers = compile_config.get("headers")
    _require(isinstance(headers, list) and len(headers) == 4 and
             all(isinstance(item, str) for item in headers),
             "compile header inventory changed")
    for item in headers:
        _relative_path(item, "compile/header")
    _relative_path(compile_config.get("default_capd_config"),
                   "compile/default_capd_config")

    frozen_inputs = config.get("frozen_inputs")
    _require(isinstance(frozen_inputs, dict) and len(frozen_inputs) == 7,
             "frozen input inventory changed")
    expected_paths = {probe["source"], *headers, *config.get("provenance_inputs", [])}
    _require(set(frozen_inputs) == expected_paths,
             "frozen input paths disagree with source/header/provenance lists")
    for path, digest in frozen_inputs.items():
        _relative_path(path, "frozen input")
        _require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest),
                 f"frozen input {path}: invalid sha256")

    execution = config.get("execution")
    _require(isinstance(execution, dict) and
             type(execution.get("cell_timeout_seconds")) is int and
             execution["cell_timeout_seconds"] > 0 and
             execution.get("environment") == {
                 "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
                 "LC_ALL": "C.UTF-8",
             }, "execution contract changed")
    _require(isinstance(config.get("summary_claim_boundary"), dict),
             "missing summary claim boundary")
    contract = config.get("cell_contract")
    _require(isinstance(contract, dict) and
             contract.get("target_graph_contract") == TARGET_GRAPH_CONTRACT and
             tuple(contract.get("required_gates", ())) == REQUIRED_GATES,
             "cell mathematical contract changed")
    return config


def _load_config(path: Path = CONFIG_PATH) -> dict[str, Any]:
    return _validate_config(_json_file(path, "cover configuration"))


def _check_repository_inputs(config: Mapping[str, Any]) -> None:
    for relative, expected in config["frozen_inputs"].items():
        path = REPOSITORY / relative
        _require(path.is_file(), f"missing frozen input: {relative}")
        _require(_sha256_file(path) == expected,
                 f"frozen input hash drift: {relative}")


def _resolve_capd_config(config: Mapping[str, Any], supplied: Path | None) -> Path:
    if supplied is not None:
        candidate = supplied
    elif os.environ.get("RFSN_CAPD_CONFIG"):
        candidate = Path(os.environ["RFSN_CAPD_CONFIG"])
    else:
        candidate = REPOSITORY / config["compile"]["default_capd_config"]
    try:
        resolved = candidate.expanduser().resolve(strict=True)
    except OSError as exc:
        raise IntegrityError(f"CAPD config is unavailable: {candidate}") from exc
    _require(resolved.is_file() and os.access(resolved, os.X_OK),
             f"CAPD config is not executable: {resolved}")
    return resolved


def _prepare(run_dir: Path, supplied_capd_config: Path | None) -> dict[str, Any]:
    config = _load_config()
    _check_repository_inputs(config)
    capd_config = _resolve_capd_config(config, supplied_capd_config)
    run_dir = run_dir.expanduser().resolve()
    if run_dir.exists():
        _require(run_dir.is_dir() and not any(run_dir.iterdir()),
                 f"prepare requires an empty run directory: {run_dir}")
    else:
        run_dir.mkdir(parents=True)
    (run_dir / "cells").mkdir()

    config_payload = CONFIG_PATH.read_bytes()
    _atomic_write(run_dir / "config.json", config_payload)
    cflags = shlex.split(subprocess.run(
        [str(capd_config), "--cflags"], check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout)
    libraries = shlex.split(subprocess.run(
        [str(capd_config), "--libs"], check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout)
    _require(not any(flag in FORBIDDEN_FLAGS for flag in (*cflags, *libraries)),
             "CAPD configuration emits a forbidden floating-point flag")
    compiler = Path(config["compile"]["compiler"]).resolve(strict=True)
    include_dirs = sorted({
        (REPOSITORY / item).parent for item in config["compile"]["headers"]
    })
    binary = run_dir / "probe"
    compile_argv = [
        str(compiler), f"-std={config['compile']['language_standard']}",
        *(f"-I{path}" for path in include_dirs), *config["compile"]["flags"],
        str(REPOSITORY / config["probe"]["source"]), "-o", str(binary),
        *cflags, *libraries,
    ]
    compiled = subprocess.run(
        compile_argv, cwd=run_dir, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if compiled.returncode != 0:
        raise IntegrityError(
            "strict probe compilation failed:\n" +
            compiled.stderr.decode("utf-8", errors="replace")
        )
    binary.chmod(0o755)
    manifest = {
        "schema_version": MANIFEST_SCHEMA,
        "cover_id": config["cover_id"],
        "grid": list(GRID), "cell_count": CELL_COUNT,
        "config": {"path": "config.json", "sha256": _sha256_bytes(config_payload)},
        "binary": {"path": "probe", "sha256": _sha256_file(binary)},
        "input_hashes": config["frozen_inputs"],
    }
    manifest_payload = _json_bytes(manifest)
    _atomic_write(run_dir / MANIFEST_NAME, manifest_payload)
    manifest_hash = _sha256_bytes(manifest_payload)
    _atomic_write(run_dir / MANIFEST_HASH_NAME,
                  f"{manifest_hash}  {MANIFEST_NAME}\n".encode("ascii"))
    return {
        "status": "PREPARED", "run_directory": str(run_dir),
        "manifest_sha256": manifest_hash,
        "config_sha256": manifest["config"]["sha256"],
        "binary_sha256": manifest["binary"]["sha256"],
        "claim_bearing": False,
    }


def _validate_run(run_dir: Path) -> tuple[
        dict[str, Any], dict[str, Any], str, Path]:
    manifest_payload = (run_dir / MANIFEST_NAME).read_bytes()
    manifest_hash = _sha256_bytes(manifest_payload)
    try:
        sidecar = (run_dir / MANIFEST_HASH_NAME).read_text(encoding="ascii").split()
    except OSError as exc:
        raise IntegrityError("cannot read manifest hash sidecar") from exc
    _require(sidecar == [manifest_hash, MANIFEST_NAME],
             "manifest hash sidecar does not match manifest.json")
    manifest = _json_loads(manifest_payload, "run manifest")
    _require(isinstance(manifest, dict) and
             manifest.get("schema_version") == MANIFEST_SCHEMA and
             manifest.get("grid") == list(GRID) and
             manifest.get("cell_count") == CELL_COUNT,
             "run manifest contract changed")
    _require(manifest.get("config", {}).get("path") == "config.json" and
             manifest.get("binary", {}).get("path") == "probe",
             "run artifact paths changed")
    config_path, binary = run_dir / "config.json", run_dir / "probe"
    _require(config_path.is_file() and
             _sha256_file(config_path) == manifest["config"].get("sha256"),
             "frozen configuration hash drift")
    _require(binary.is_file() and os.access(binary, os.X_OK) and
             _sha256_file(binary) == manifest["binary"].get("sha256"),
             "frozen binary hash drift")
    config = _load_config(config_path)
    _require(manifest.get("input_hashes") == config["frozen_inputs"],
             "manifest input hashes disagree with frozen configuration")
    return manifest, config, manifest_hash, binary


def _cell_name(index: tuple[int, int, int]) -> str:
    return f"cell-r{index[0]:02d}-a{index[1]:03d}-e{index[2]:02d}.json"


def _all_indices() -> Iterator[tuple[int, int, int]]:
    return itertools.product(range(GRID[0]), range(GRID[1]), range(GRID[2]))


def _cell_index(value: Any, label: str) -> tuple[int, int, int]:
    _require(isinstance(value, list) and len(value) == 3 and
             all(type(item) is int for item in value),
             f"{label}: invalid cell index", CellFormatError)
    index = value[0], value[1], value[2]
    _require(all(0 <= index[axis] < GRID[axis] for axis in range(3)),
             f"{label}: cell index out of range: {index}", CellFormatError)
    return index


def _boolean_tree(value: Any) -> bool:
    return (value if isinstance(value, bool) else
            bool(value) and all(_boolean_tree(item) for item in value)
            if isinstance(value, list) else False)


def _interval(payload: Mapping[str, Any], name: str) -> tuple[
        tuple[float, str], tuple[float, str]]:
    enclosures = payload.get("enclosures")
    _require(isinstance(enclosures, dict) and isinstance(enclosures.get(name), dict),
             f"missing critical enclosure: {name}", CellFormatError)
    value = enclosures[name]
    lower_hex, upper_hex = value.get("lower_hex"), value.get("upper_hex")
    _require(isinstance(lower_hex, str) and isinstance(upper_hex, str) and
             HEX_FLOAT.fullmatch(lower_hex) and HEX_FLOAT.fullmatch(upper_hex) and
             value.get("endpoint_format") == "IEEE754_BINARY64_HEX",
             f"enclosures/{name}: invalid hexadecimal endpoints", CellFormatError)
    lower, upper = float.fromhex(lower_hex), float.fromhex(upper_hex)
    _require(math.isfinite(lower) and math.isfinite(upper) and lower <= upper,
             f"enclosures/{name}: invalid interval order", CellFormatError)
    return (lower, lower_hex), (upper, upper_hex)


def _validate_cell(payload: Any, config: Mapping[str, Any],
                   expected_index: tuple[int, int, int] | None,
                   require_provenance: bool,
                   expected_mode: str | None = None) -> CellCheck:
    _require(isinstance(payload, dict), "cell payload is not an object",
             CellFormatError)
    _require(payload.get("schema_version") == CELL_SCHEMA and
             payload.get("box_id") == "vdp-positive-box-v2" and
             payload.get("grid") == list(GRID) and
             payload.get("claim_bearing") is False,
             "cell identity, grid, or claim boundary changed", CellFormatError)
    index = _cell_index(payload.get("cell_index"), "cell_index")
    if expected_index is not None:
        _require(index == expected_index,
                 f"cell index mismatch: expected {expected_index}, got {index}",
                 CellFormatError)
    status = payload.get("status")
    _require(status in ("PASS", "INCONCLUSIVE") and
             payload.get("mathematical_status") == status,
             "cell status is inconsistent", CellFormatError)
    rounding, gates = payload.get("rounding_self_test"), payload.get("gates")
    _require(isinstance(rounding, dict) and rounding.get("status") == "PASS",
             "rounding self-test did not pass", CellFormatError)
    _require(isinstance(gates, dict) and gates, "cell gates are missing",
             CellFormatError)
    contract = config["cell_contract"]
    _require(payload.get("target_graph_contract") ==
             contract["target_graph_contract"],
             "target-graph contract changed", CellFormatError)
    _require(set(gates) == set(contract["required_gates"]),
             "cell gate inventory changed", CellFormatError)
    if status == "PASS":
        merged = payload.get("merged_root_exterior")
        _require(all(_boolean_tree(value) for value in gates.values()) and
                 isinstance(merged, dict) and
                 merged.get("candidate_hull_consistency_gate") is True and
                 merged.get("kernel_gate") is True,
                 "PASS cell contains a false or malformed gate", CellFormatError)
    output_mode = payload.get("exterior_propagation_mode")
    if expected_mode is not None:
        _require(output_mode == OUTPUT_MODES[expected_mode],
                 "probe mode disagrees with cell output", CellFormatError)
    cache: dict[str, tuple[tuple[float, str], tuple[float, str]]] = {}
    extrema: dict[str, tuple[float, str]] = {}
    for summary_name, enclosure, endpoint, _ in EXTREMA_SPECS:
        cache.setdefault(enclosure, _interval(payload, enclosure))
        extrema[summary_name] = cache[enclosure][0 if endpoint == "lower" else 1]
    if require_provenance:
        provenance = payload.get("driver_execution_provenance")
        _require(isinstance(provenance, dict) and
                 set(provenance) == {"attempted_modes", "final_mode"},
                 "missing minimal driver provenance", CellFormatError)
        attempts = provenance["attempted_modes"]
        _require(attempts in ([FAST_MODE], [FAST_MODE, ROBUST_MODE]) and
                 provenance["final_mode"] == attempts[-1] and
                 output_mode == OUTPUT_MODES[attempts[-1]],
                 "invalid driver attempt provenance", CellFormatError)
    return CellCheck(status, extrema)


def _run_probe(binary: Path, config: Mapping[str, Any],
               index: tuple[int, int, int], run_dir: Path,
               mode: str) -> tuple[str, dict[str, Any] | None, str | None]:
    argv = [str(binary), mode, *(str(value) for value in GRID),
            *(str(value) for value in index)]
    environment = {**os.environ, **config["execution"]["environment"]}
    try:
        completed = subprocess.run(
            argv, cwd=run_dir, env=environment, check=False,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=config["execution"]["cell_timeout_seconds"],
        )
    except subprocess.TimeoutExpired:
        return "INFRASTRUCTURE_FAILURE", None, "probe timed out"
    except OSError as exc:
        return "INFRASTRUCTURE_FAILURE", None, f"probe execution failed: {exc}"
    if completed.returncode not in (0, 1):
        stderr = completed.stderr.decode("utf-8", errors="replace")[-1000:]
        return "INFRASTRUCTURE_FAILURE", None, (
            f"probe exited {completed.returncode}: {stderr}"
        )
    try:
        payload = _json_loads(completed.stdout, f"probe output for cell {index}",
                              CellFormatError)
        check = _validate_cell(payload, config, index, False, mode)
    except CellFormatError as exc:
        return "INFRASTRUCTURE_FAILURE", None, f"invalid probe payload: {exc}"
    expected = "PASS" if completed.returncode == 0 else "INCONCLUSIVE"
    if check.status != expected:
        return "INFRASTRUCTURE_FAILURE", None, (
            f"exit code {completed.returncode} requires {expected}, not {check.status}"
        )
    return check.status, payload, None


def _invoke_cell(binary: Path, config: Mapping[str, Any],
                 index: tuple[int, int, int], run_dir: Path) -> CellOutcome:
    attempts = [FAST_MODE]
    kind, payload, error = _run_probe(binary, config, index, run_dir, FAST_MODE)
    final_mode = FAST_MODE
    if kind == "INFRASTRUCTURE_FAILURE":
        attempts.append(ROBUST_MODE)
        final_mode = ROBUST_MODE
        kind, payload, error = _run_probe(binary, config, index, run_dir, ROBUST_MODE)
    if kind == "INFRASTRUCTURE_FAILURE":
        return CellOutcome(index, kind, tuple(attempts), (error or "")[:2000])
    assert payload is not None
    _require("driver_execution_provenance" not in payload,
             "probe fabricated driver provenance", CellFormatError)
    payload["driver_execution_provenance"] = {
        "attempted_modes": attempts, "final_mode": final_mode,
    }
    _atomic_write(run_dir / "cells" / _cell_name(index), _json_bytes(payload))
    return CellOutcome(index, kind, tuple(attempts), wrote_cell=True)


def _update_extrema(aggregate: dict[str, dict[str, Any]], check: CellCheck,
                    index: tuple[int, int, int]) -> None:
    reducers = {name: reducer for name, _, _, reducer in EXTREMA_SPECS}
    for name, (number, hexadecimal) in check.extrema.items():
        current = aggregate.get(name)
        better = current is None or (
            number < current["number"] if reducers[name] == "min"
            else number > current["number"]
        )
        if better:
            aggregate[name] = {
                "number": number, "hex": hexadecimal, "cell_index": index,
            }


def _scan_cells(run_dir: Path, config: Mapping[str, Any],
                collect_extrema: bool = False) -> tuple[
        set[tuple[int, int, int]], tuple[tuple[int, int, int], ...],
        dict[str, dict[str, Any]]]:
    seen: set[tuple[int, int, int]] = set()
    stops: list[tuple[int, int, int]] = []
    extrema: dict[str, dict[str, Any]] = {}
    for path in sorted((run_dir / "cells").glob("*.json")):
        payload = _json_file(path, f"cell {path.name}", CellFormatError)
        index = _cell_index(payload.get("cell_index"), f"{path.name}/cell_index")
        _require(path.name == _cell_name(index),
                 f"noncanonical cell filename: {path.name}")
        _require(index not in seen, f"duplicate cell index: {index}")
        check = _validate_cell(payload, config, index, True)
        seen.add(index)
        if check.status == "INCONCLUSIVE":
            stops.append(index)
        if collect_extrema:
            _update_extrema(extrema, check, index)
    return seen, tuple(sorted(stops)), extrema


def _missing_cells(seen: set[tuple[int, int, int]],
                   sample_limit: int = 10) -> tuple[int, list[list[int]]]:
    missing = [index for index in _all_indices() if index not in seen]
    return len(missing), [list(index) for index in missing[:sample_limit]]


@contextlib.contextmanager
def _run_lock(run_dir: Path) -> Iterator[None]:
    with (run_dir / ".run.lock").open("a+b") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise IntegrityError(
                "another run/verify process holds this run directory"
            ) from exc
        yield


def _run(run_dir: Path, jobs: int) -> dict[str, Any]:
    _require(jobs > 0, "--jobs must be a positive integer")
    run_dir = run_dir.expanduser().resolve(strict=True)
    _, config, manifest_hash, binary = _validate_run(run_dir)
    with _run_lock(run_dir):
        seen, prior_stops, _ = _scan_cells(run_dir, config)
        if prior_stops:
            return {
                "status": "STOPPED_MATHEMATICALLY",
                "cell_index": list(prior_stops[0]),
                "completed_cell_count": len(seen), "claim_bearing": False,
            }
        pending = (index for index in _all_indices() if index not in seen)
        completed, stop = len(seen), None
        futures: dict[concurrent.futures.Future[CellOutcome],
                      tuple[int, int, int]] = {}
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=jobs)

        def fill() -> None:
            while stop is None and len(futures) < jobs:
                try:
                    index = next(pending)
                except StopIteration:
                    return
                future = executor.submit(_invoke_cell, binary, config, index, run_dir)
                futures[future] = index

        try:
            fill()
            while futures:
                done, _ = concurrent.futures.wait(
                    futures, return_when=concurrent.futures.FIRST_COMPLETED
                )
                outcomes = []
                for future in done:
                    futures.pop(future)
                    outcomes.append(future.result())
                for outcome in sorted(outcomes, key=lambda item: item.index):
                    completed += outcome.wrote_cell
                    if outcome.kind != "PASS" and stop is None:
                        stop = outcome
                if stop is None:
                    fill()
        finally:
            executor.shutdown(wait=True, cancel_futures=True)
        if stop is not None:
            status = ("STOPPED_MATHEMATICALLY" if stop.kind == "INCONCLUSIVE"
                      else "STOPPED_INFRASTRUCTURE")
            result = {
                "status": status, "cell_index": list(stop.index),
                "attempted_modes": list(stop.attempts),
                "completed_cell_count": completed,
                "manifest_sha256": manifest_hash, "claim_bearing": False,
            }
            if stop.error:
                result["error"] = stop.error
            return result
        _require(completed == CELL_COUNT,
                 "scheduler exhausted without completing the fixed grid")
        return {"status": "READY_FOR_VERIFY", "completed_cell_count": completed,
                "manifest_sha256": manifest_hash, "claim_bearing": False}


def _verify(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.expanduser().resolve(strict=True)
    manifest, config, manifest_hash, _ = _validate_run(run_dir)
    with _run_lock(run_dir):
        seen, stops, extrema = _scan_cells(run_dir, config, collect_extrema=True)
        _require(not stops, f"mathematical INCONCLUSIVE cells: {stops[:10]}")
        missing_count, sample = _missing_cells(seen)
        _require(missing_count == 0,
                 f"cover is missing {missing_count} cells; first: {sample}")
        _require(len(seen) == CELL_COUNT,
                 f"cover has {len(seen)} unique PASS cells, expected {CELL_COUNT}")
        serialized_extrema = {
            name: {"value_hex": value["hex"],
                   "cell_index": list(value["cell_index"]),
                   "endpoint_format": "IEEE754_BINARY64_HEX"}
            for name, value in sorted(extrema.items())
        }
        summary = {
            "schema_version": SUMMARY_SCHEMA, "cover_id": config["cover_id"],
            "status": "PASS", "mathematical_status": "PASS",
            "claim_bearing": False, "grid": list(GRID),
            "unique_pass_cell_count": len(seen),
            "critical_extrema": serialized_extrema,
            "provenance": {
                "manifest_sha256": manifest_hash,
                "config_sha256": manifest["config"]["sha256"],
                "binary_sha256": manifest["binary"]["sha256"],
                "probe_source_sha256": config["frozen_inputs"][
                    config["probe"]["source"]
                ],
            },
            "claim_boundary": config["summary_claim_boundary"],
        }
        summary_payload = _json_bytes(summary)
        _atomic_write(run_dir / SUMMARY_NAME, summary_payload)
        summary_hash = _sha256_bytes(summary_payload)
        return {"status": "PASS", "mathematical_status": "PASS",
                "claim_bearing": False, "unique_pass_cell_count": len(seen),
                "summary_sha256": summary_hash,
                "summary": str(run_dir / SUMMARY_NAME)}


def _parse_arguments(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="freeze and compile one run")
    prepare.add_argument("--run-dir", required=True, type=Path)
    prepare.add_argument("--capd-config", type=Path)
    run = commands.add_parser("run", help="run or resume the fixed cover")
    run.add_argument("--run-dir", required=True, type=Path)
    run.add_argument("--jobs", required=True, type=int)
    verify = commands.add_parser("verify", help="verify all 393216 PASS cells")
    verify.add_argument("--run-dir", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parse_arguments(argv)
    try:
        if arguments.command == "prepare":
            result = _prepare(arguments.run_dir, arguments.capd_config)
        elif arguments.command == "run":
            result = _run(arguments.run_dir, arguments.jobs)
        else:
            result = _verify(arguments.run_dir)
    except (CoverError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc),
                          "claim_bearing": False}, sort_keys=True),
              file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] in ("PREPARED", "READY_FOR_VERIFY", "PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
