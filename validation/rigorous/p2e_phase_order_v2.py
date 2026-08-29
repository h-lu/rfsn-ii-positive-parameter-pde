#!/usr/bin/env python3
"""Check the three frozen P2e source-phase gaps on vdp-positive-box-v2.

This checker deliberately stops at the three scalar phase-order subatoms.
It does not materialize or certify the complete V2 event atlas.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
DEFAULT_CONFIG = HERE / "config" / "vdp_p2e_phase_order_v2.json"
DEFAULT_RESULT = HERE / "results" / "vdp_box_v2_p2e_phase_order.json"


class AuditError(ValueError):
    """A frozen input or strict interval gate does not satisfy the contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path} is not a JSON object")
    return value


def repository_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else REPOSITORY / path


def bound_json(binding: dict[str, Any], label: str) -> dict[str, Any]:
    path = repository_path(binding["path"])
    data = path.read_bytes()
    require(sha256_bytes(data) == binding["sha256"], f"{label} hash mismatch")
    value = json.loads(data)
    require(isinstance(value, dict), f"{label} is not a JSON object")
    return value


def bound_bytes(binding: dict[str, Any], label: str) -> bytes:
    data = repository_path(binding["path"]).read_bytes()
    require(sha256_bytes(data) == binding["sha256"], f"{label} hash mismatch")
    return data


def git_blob(commit: str, path: str) -> bytes:
    require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None,
            "strict source commit is not a full Git hash")
    run = subprocess.run(
        ["git", "-C", str(REPOSITORY), "show", f"{commit}:{path}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    require(run.returncode == 0,
            f"cannot materialize strict source blob: "
            f"{run.stderr.decode(errors='replace').strip()}")
    return run.stdout


def rational_interval(value: dict[str, Any], label: str) -> tuple[Fraction, Fraction]:
    endpoints = []
    for endpoint in ("lower", "upper"):
        item = value[endpoint]
        endpoints.append(Fraction(int(item["numerator"]),
                                  int(item["denominator"])))
    require(endpoints[0] <= endpoints[1], f"{label} interval is reversed")
    return endpoints[0], endpoints[1]


def rational_pair(value: Any, label: str) -> tuple[Fraction, Fraction]:
    require(isinstance(value, list) and len(value) == 2,
            f"{label} is not a rational pair")
    result = Fraction(value[0]), Fraction(value[1])
    require(result[0] <= result[1], f"{label} is reversed")
    return result


def decimal_interval(value: str, label: str) -> tuple[Decimal, Decimal]:
    match = re.fullmatch(r"\[\s*([^,]+),\s*([^\]]+)\]", value)
    require(match is not None, f"malformed {label}: {value!r}")
    result = Decimal(match.group(1)), Decimal(match.group(2))
    require(result[0] <= result[1], f"{label} is reversed")
    return result


def resolve_json_path(value: Any, path: list[str]) -> Any:
    current = value
    for key in path:
        require(isinstance(current, dict) and key in current,
                f"missing JSON path component {key!r}")
        current = current[key]
    return current


def extract(text: str, start: str, end: str, label: str) -> str:
    require(text.count(start) == 1 and text.count(end) == 1,
            f"{label} markers are not unique")
    begin = text.index(start)
    finish = text.index(end, begin) + len(end)
    return text[begin:finish]


def unique_match(pattern: str, text: str, label: str) -> re.Match[str]:
    matches = list(re.finditer(pattern, text, re.MULTILINE))
    require(len(matches) == 1, f"strict slab log has {len(matches)} {label} lines")
    return matches[0]


def parse_slab_log(value: bytes) -> dict[str, Any]:
    text = value.decode("utf-8")
    require(text.endswith("\n"), "strict slab log must end with one newline")
    require(re.search(r"^(?:FAIL|ERROR|INCONCLUSIVE|ABORT|FATAL)\b",
                      text, re.MULTILINE) is None,
            "strict slab log contains a negative terminal marker")
    for prefix in ("mode", "scope", "grid", "r_index", "cells",
                   "phase_hull"):
        require(len(re.findall(rf"^{prefix}\b[^\n]*$", text,
                               re.MULTILINE)) == 1,
                f"strict slab log has a non-unique {prefix} field")
    require(text.count("mode mu-grid-root-jets-slab\n") == 1,
            "strict slab log has the wrong mode count")
    require(text.count("scope selected_true_source_root_C2\n") == 1,
            "strict slab log has the wrong scope count")
    grid = unique_match(
        r"^grid (\d+) (\d+) (\d+) radius_factor (\d+)$",
        text, "grid declaration",
    )
    radial = unique_match(
        r"^r_index (\d+) r_cell (\[[^\n]+\])$", text, "radial cell",
    )
    cells = unique_match(r"^cells (\d+)/(\d+)$", text, "cell-count")
    phase = unique_match(
        r"^phase_hull (\[[^\n]+?\]) half_time_hull", text, "phase-hull",
    )
    terminal = "PASS mu-grid true-source root C2 jet slab"
    require(text.endswith(terminal + "\n"),
            "strict slab computation does not end in PASS")
    require(text.count(terminal) == 1,
            "strict slab log has the wrong terminal PASS count")
    return {
        "grid": [int(grid.group(index)) for index in range(1, 4)],
        "radius_factor": int(grid.group(4)),
        "r_index": int(radial.group(1)),
        "printed_r_cell": decimal_interval(radial.group(2), "printed r cell"),
        "passed_cells": int(cells.group(1)),
        "total_cells": int(cells.group(2)),
        "phase_hull": decimal_interval(phase.group(1), "homoclinic phase"),
    }


def prerequisite_atoms(certificate: dict[str, Any]) -> dict[str, str]:
    return {item.get("id"): item.get("status")
            for item in certificate.get("obligations", [])}


def audit(config_path: Path = DEFAULT_CONFIG,
          strict_binary: Path | None = None) -> dict[str, Any]:
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    require(isinstance(config, dict), "P2e v2 config is not a JSON object")
    require(config.get("schema_version") ==
            "rfsn-vdp-p2e-phase-order-config/2",
            "wrong P2e v2 config schema")
    require(config.get("scope") == "V2_P2E_THREE_PHASE_GAPS_V2",
            "wrong P2e v2 scope")
    require(config.get("box_id") == "vdp-positive-box-v2",
            "wrong P2e v2 box id")
    require(config.get("comparison_bridge_id") ==
            "vdp-core-to-positive-bridge-v2",
            "wrong P2e v2 comparison bridge id")
    require(config.get("status") ==
            "FROZEN_BEFORE_FIRST_RETAINED_EVIDENTIARY_V2_PHASE_OUTPUT" and
            config.get(
                "frozen_before_first_retained_evidentiary_v2_phase_output")
            is True,
            "phase contract was not frozen before the first retained v2 evidence")
    require(config.get("pre_freeze_aborted_execution_disclosure") == {
        "attempt_started": True,
        "completed": False,
        "stdout_placeholder_files": 8,
        "stderr_placeholder_files": 8,
        "verified_bytes_per_placeholder": 0,
        "numeric_output_emitted_inspected_or_retained": False,
        "placeholders_removed_before_freeze": True,
        "classification": "ABORTED_ZERO_OUTPUT_NON_EVIDENCE",
    }, "pre-freeze zero-output attempt disclosure changed")
    require(config.get("historical_log_disclosure", {}).get("seen_before_freeze")
            is True, "historical log disclosure is missing")
    require(config["historical_log_disclosure"].get("blinded") is False,
            "historical evidence must not be described as blinded")

    theorem_binding = config["theorem_binding"]
    theorem_text = bound_bytes(theorem_binding, "V2 theorem").decode("utf-8")
    phase_convention = extract(
        theorem_text, theorem_binding["phase_convention_start"],
        theorem_binding["phase_convention_end"], "phase convention",
    )
    phase_order = extract(
        theorem_text, theorem_binding["phase_order_start"],
        theorem_binding["phase_order_end"], "phase order",
    )
    require(sha256_bytes(phase_convention.encode()) ==
            theorem_binding["phase_convention_excerpt_sha256"],
            "phase-convention theorem extract mismatch")
    require(sha256_bytes(phase_order.encode()) ==
            theorem_binding["phase_order_excerpt_sha256"],
            "phase-order theorem extract mismatch")
    for threshold in ("0.052407", "0.16324", "0.110835"):
        require(threshold in phase_order,
                f"V2 theorem no longer contains phase threshold {threshold}")
    bound_bytes(config["core_import_binding"], "central core import")

    box = bound_json(config["target_box_binding"], "v2 target box")
    bridge = bound_json(config["comparison_bridge_binding"],
                        "v2 comparison bridge")
    require(box.get("box_id") == config["box_id"], "v2 box id changed")
    require(box.get("status") == "FROZEN_PRE_P2E_V2_VALIDATION",
            "v2 box is not frozen before P2e validation")
    require(box.get(
        "selected_before_first_v2_target_specific_outward_rounded_run") is True,
            "v2 box was not selected before validation")
    require(bridge.get("bridge_id") == config["comparison_bridge_id"],
            "v2 comparison bridge id changed")
    require(bridge.get("status") == "FROZEN_PRE_P2E_V2_VALIDATION",
            "v2 comparison bridge is not frozen before P2e validation")
    require(bridge.get(
        "selected_before_first_v2_target_specific_outward_rounded_run") is True,
            "v2 comparison bridge was not selected before validation")

    expected_box = {
        "r": (Fraction(1, 100), Fraction(1, 50)),
        "a2": (Fraction(-1, 4), Fraction(1, 4)),
        "epsilon": (Fraction(4, 5), Fraction(6, 5)),
    }
    expected_bridge = dict(expected_box)
    expected_bridge["r"] = (Fraction(0), Fraction(1, 50))
    for axis, expected in expected_box.items():
        require(rational_interval(box["variables"][axis], f"box {axis}") ==
                expected, f"v2 {axis} target changed")
    for axis, expected in expected_bridge.items():
        require(rational_interval(bridge["variables"][axis],
                                  f"bridge {axis}") == expected,
                f"v2 {axis} comparison bridge changed")

    p2c_config = bound_json(config["p2c_config_binding"], "P2c config")
    kato_config = bound_json(config["kato_config_binding"], "P2bK config")
    dependency = bound_json(config["dependency_lock_binding"],
                            "dependency lock")
    flagship = bound_json(config["flagship_lock_binding"],
                          "flagship import lock")
    checker_path = repository_path(config["checker_binding"]["path"]).resolve()
    require(checker_path == Path(__file__).resolve(),
            "checker binding does not name the executing checker")
    bound_bytes(config["checker_binding"], "P2e v2 checker")
    p2c_certificate = bound_json(config["p2c_certificate_binding"],
                                 "P2c certificate")
    kato_certificate = bound_json(config["kato_certificate_binding"],
                                  "P2bK certificate")
    require(p2c_certificate.get("mathematical_status") == "PASS" and
            prerequisite_atoms(p2c_certificate).get("V2.HOM.BRANCH") == "PASS",
            "P2c selected branch prerequisite is not PASS")
    require(kato_certificate.get("mathematical_status") == "PASS" and
            prerequisite_atoms(kato_certificate).get(
                "V2.PHASE.KATO_INTERFACE") == "PASS" and
            prerequisite_atoms(kato_certificate).get(
                "V2.PHASE.TRUE_SOURCE") == "PASS",
            "P2bK phase-interface or true-source prerequisite is not PASS")
    require(p2c_certificate.get("integrity_status") == "PASS" and
            p2c_certificate.get("configuration") == {
                "configuration_id": p2c_config["configuration_id"],
                "path": config["p2c_config_binding"]["path"],
                "sha256": config["p2c_config_binding"]["sha256"],
                "status": p2c_config["status"],
            }, "P2c certificate/configuration cross-binding changed")
    require(kato_certificate.get("integrity_status") == "PASS" and
            kato_certificate.get("p2_kato_configuration") == {
                "configuration_id": kato_config["configuration_id"],
                "path": config["kato_config_binding"]["path"],
                "sha256": config["kato_config_binding"]["sha256"],
            }, "P2bK certificate/configuration cross-binding changed")
    require(kato_config["source_circle_contract"]["phase_lift_formula"] ==
            config["phase_interface"]["coordinate_embedding_formula"],
            "Kato coordinate-embedding formula changed")
    require(config["phase_interface"]["common_lift"] ==
            "TRANSPORTED_KATO_SOURCE_PHASE",
            "phase gaps are not in the frozen transported Kato lift")

    source = config["strict_source"]
    source_blob = git_blob(source["commit"], source["path"])
    require(sha256_bytes(source_blob) == source["sha256"],
            "strict source hash mismatch")
    bound_bytes(config["h10_binding"], "frozen H10 header")
    capd_commit = dependency.get("capd", {}).get("source_commit")
    require(capd_commit == source["capd_commit"],
            "strict-source CAPD commit differs from dependency lock")
    require(p2c_config["common_external_bindings"]["capd_commit"] == capd_commit,
            "P2c CAPD commit differs from dependency lock")
    require(p2c_certificate["toolchain"]["capd_commit"] == capd_commit and
            kato_certificate["toolchain"]["capd"]["source_commit"] ==
            capd_commit and
            kato_certificate["toolchain"]["dependency_lock_sha256"] ==
            config["dependency_lock_binding"]["sha256"],
            "prerequisite certificate toolchain differs from dependency lock")
    flagship_commit = flagship.get("commit")
    require(flagship.get("status") == "READ_ONLY_FROZEN_IMPORT" and
            p2c_config["common_external_bindings"]["flagship_commit"] ==
            flagship_commit and
            kato_config["selection_basis"]["flagship_core_manuscript"]
                ["commit"] == flagship_commit and
            kato_certificate["toolchain"]["flagship_import"]["commit"] ==
            flagship_commit and
            kato_certificate["toolchain"]["flagship_import"]["lock_sha256"] ==
            config["flagship_lock_binding"]["sha256"],
            "prerequisite flagship import differs from the frozen lock")
    flagship_files = flagship.get("files", {})
    require(flagship_files.get(
                "validation/origin-algebraic-heteroclinic/certificate.json") ==
            config["algebraic_anchor_binding"]["sha256"] and
            flagship_files.get(
                "validation/origin-unstable-pole-entry/certificate.json") ==
            config["pole_anchor_binding"]["sha256"] and
            flagship_files.get(
                "validation/origin-algebraic-heteroclinic/unstable_graph_terms.hpp") ==
            config["h10_binding"]["sha256"],
            "anchor or H10 binding differs from the flagship lock")
    containing_bridge = box["selection_basis"]["containing_bridge_binding"]
    require(p2c_certificate["continuation_bridge"]["path"] ==
            containing_bridge["path"] and
            p2c_certificate["continuation_bridge"]["sha256"] ==
            containing_bridge["sha256"] and
            kato_certificate["continuation_bridge"]["path"] ==
            containing_bridge["path"] and
            kato_certificate["continuation_bridge"]["sha256"] ==
            containing_bridge["sha256"],
            "prerequisite certificate bridge binding changed")
    require(p2c_config["strict_run_bindings"]["compact_middle"][
                "source_commit"] == source["commit"] and
            p2c_config["strict_run_bindings"]["compact_middle"][
                "source_sha256"] == source["sha256"] and
            p2c_config["strict_run_bindings"]["compact_middle"][
                "strict_binary_sha256"] == source["binary_sha256"],
            "strict source/binary is not bound by the P2c record")

    grid = p2c_config["parameter_grid"]
    require(grid["ordered_axes"] == ["r", "a2", "epsilon"],
            "P2c ordered axes changed")
    require(grid["subdivisions"] == [32, 128, 4],
            "P2c grid subdivisions changed")
    require(grid["shooting_radius_factor"] == 3,
            "P2c shooting radius factor changed")
    historical_grid_bridge = {
        "r": (Fraction(0), Fraction(2, 25)),
        "a2": (Fraction(-1, 4), Fraction(1, 4)),
        "epsilon": (Fraction(4, 5), Fraction(6, 5)),
    }
    for axis, expected in historical_grid_bridge.items():
        require(rational_pair(grid["bridge"][axis], f"P2c {axis} bridge") ==
                expected, f"P2c historical {axis} bridge changed")

    bound_bytes(config["historical_log_disclosure"],
                "disclosed historical phase log")

    strict_runs = config["strict_slab_runs"]
    require(strict_runs["mode"] == "mu-grid-root-jets-slab" and
            strict_runs["shooting_radius_factor"] == 3,
            "strict phase slab mode changed")
    require(strict_runs["process_environment"] == {
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "LC_ALL": "C.UTF-8",
    }, "strict phase process environment changed")
    process_policy = dependency["platform"]["required_process_policy"]
    require(strict_runs["process_environment"] == {
        "OMP_NUM_THREADS": process_policy["omp_num_threads"],
        "OPENBLAS_NUM_THREADS": process_policy["openblas_num_threads"],
        "LC_ALL": process_policy["locale"],
    }, "strict phase environment differs from dependency lock")
    require(strict_runs["transverse_axes"] == {
        "a2": {
            "indices": [0, 127],
            "cells": 128,
            "exact_interval": ["-1/4", "1/4"],
        },
        "epsilon": {
            "indices": [0, 3],
            "cells": 4,
            "exact_interval": ["4/5", "6/5"],
        },
    }, "strict phase transverse axes changed")
    expected_indices = strict_runs["r_indices"]
    require(expected_indices == list(range(8)),
            "strict phase slab indices changed")
    runs = strict_runs["logs"]
    require([item["r_index"] for item in runs] == expected_indices,
            "strict phase slab log ordering changed")
    require(len({item["path"] for item in runs}) == 8,
            "strict phase slab paths are not unique")

    historical_r = rational_pair(grid["bridge"]["r"], "P2c radial bridge")
    radial_width = (historical_r[1] - historical_r[0]) / grid["subdivisions"][0]
    bridge_phase_hulls: list[tuple[Decimal, Decimal]] = []
    target_phase_hulls: list[tuple[Decimal, Decimal]] = []
    observed_runs = []
    replay_bytes: list[bytes] = []
    for item in runs:
        path = repository_path(item["path"])
        log_bytes = path.read_bytes()
        parsed = parse_slab_log(log_bytes)
        index = item["r_index"]
        require(parsed["r_index"] == index, "strict slab r index changed")
        require(parsed["grid"] == grid["subdivisions"],
                "strict slab grid axes changed")
        require(parsed["radius_factor"] == grid["shooting_radius_factor"],
                "strict slab shooting radius factor changed")
        expected_cells = grid["subdivisions"][1] * grid["subdivisions"][2]
        require(parsed["passed_cells"] == parsed["total_cells"] ==
                expected_cells == 512,
                "strict slab does not certify all 512 transverse cells")
        exact_cell = (historical_r[0] + index * radial_width,
                      historical_r[0] + (index + 1) * radial_width)
        declared_cell = rational_pair(item["exact_r_cell"],
                                      f"declared r cell {index}")
        require(exact_cell == declared_cell,
                "declared slab r cell does not follow from the P2c grid")
        printed = tuple(Fraction(value) for value in parsed["printed_r_cell"])
        require(printed[0] <= exact_cell[0] and exact_cell[1] <= printed[1],
                "printed slab r enclosure misses its exact rational cell")
        require(expected_bridge["r"][0] <= exact_cell[0] and
                exact_cell[1] <= expected_bridge["r"][1],
                "strict slab lies outside the v2 comparison bridge")
        bridge_phase_hulls.append(parsed["phase_hull"])
        if expected_box["r"][0] <= exact_cell[0] and \
                exact_cell[1] <= expected_box["r"][1]:
            target_phase_hulls.append(parsed["phase_hull"])
        replay_bytes.append(log_bytes)
        observed_runs.append({
            "r_index": index,
            "exact_r_cell": item["exact_r_cell"],
            "cells": 512,
            "phase_hull": [str(value) for value in parsed["phase_hull"]],
            "stdout_sha256": sha256_bytes(log_bytes),
            "terminal_status": "PASS",
        })

    require(rational_pair(runs[0]["exact_r_cell"], "first phase slab")[0] ==
            expected_bridge["r"][0] and
            rational_pair(runs[-1]["exact_r_cell"], "last phase slab")[1] ==
            expected_bridge["r"][1],
            "strict slabs do not reach both v2 comparison-bridge radial faces")
    for left, right in zip(runs, runs[1:]):
        require(rational_pair(left["exact_r_cell"], "left slab")[1] ==
                rational_pair(right["exact_r_cell"], "right slab")[0],
                "strict phase slabs have a radial gap or overlap")
    require(len(target_phase_hulls) == 4,
            "strict slabs do not contain exactly the four v2 target slabs")

    if strict_binary is not None:
        require(sha256_bytes(strict_binary.read_bytes()) ==
                source["binary_sha256"], "strict binary hash mismatch")
        environment = dict(os.environ)
        frozen_environment = strict_runs["process_environment"]
        environment.update(frozen_environment)
        for item, expected_stdout in zip(runs, replay_bytes, strict=True):
            argv = ["mu-grid-root-jets-slab", "3", str(item["r_index"])]
            run = subprocess.run(
                [str(strict_binary), *argv], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, cwd=REPOSITORY, env=environment,
            )
            require(run.returncode == 0,
                    f"strict slab replay failed for r index {item['r_index']}: "
                    f"{run.stderr.decode(errors='replace')}")
            require(run.stderr == b"",
                    f"strict slab replay emitted stderr for r index "
                    f"{item['r_index']}")
            require(run.stdout == expected_stdout,
                    f"strict replay stdout differs for r index {item['r_index']}")

    algebraic_binding = config["algebraic_anchor_binding"]
    algebraic_certificate = bound_json(algebraic_binding,
                                        "algebraic anchor certificate")
    require(algebraic_certificate.get("status") ==
            "PASS-ORIGIN-ALGEBRAIC-HETEROCLINIC",
            "algebraic anchor certificate is not PASS")
    algebraic_text = resolve_json_path(
        algebraic_certificate, algebraic_binding["json_path"])
    algebraic = decimal_interval(algebraic_text, "algebraic phase")
    require([str(value) for value in algebraic] ==
            algebraic_binding["expected_phase_hull"],
            "algebraic phase hull changed")

    pole_binding = config["pole_anchor_binding"]
    pole_certificate = bound_json(pole_binding, "pole anchor certificate")
    require(pole_certificate.get("status") ==
            "PASS-TRUE-WU-OPEN-PHASE-POLE-ENTRY",
            "pole anchor certificate is not PASS")
    pole_cover = resolve_json_path(pole_certificate,
                                   pole_binding["cover_json_path"])
    require([str(value) for value in pole_cover] ==
            pole_binding["expected_closed_cover"],
            "pole phase cover changed")
    pi_statement = resolve_json_path(pole_certificate,
                                     pole_binding["pi_bound_json_path"])
    require(pi_statement == pole_binding["required_pi_statement"],
            "pole certificate pi bound changed")
    match = re.fullmatch(r"2\*pi>([^ ]+)", pi_statement)
    require(match is not None, "malformed strict 2*pi lower bound")
    two_pi_lower = Decimal(match.group(1))

    homoclinic_bridge = (min(value[0] for value in bridge_phase_hulls),
                         max(value[1] for value in bridge_phase_hulls))
    homoclinic_target = (min(value[0] for value in target_phase_hulls),
                         max(value[1] for value in target_phase_hulls))
    pole_left_lift_lower = two_pi_lower + Decimal(str(pole_cover[0]))
    thresholds = config["phase_gap_predicates"]
    require([item["atom_id"] for item in thresholds] == [
        "V2.ATLAS.PHASE_GAP_AH",
        "V2.ATLAS.PHASE_GAP_AP",
        "V2.ATLAS.PHASE_GAP_HP",
    ], "phase-gap atom list changed")
    require([item["strict_lower"] for item in thresholds] ==
            ["0.052407", "0.16324", "0.110835"],
            "phase-gap thresholds changed")
    require([item["predicate"] for item in thresholds] == [
        "phi_h - phi_a > 0.052407 in the common transported Kato source-phase lift",
        "phi_p^- - phi_a > 0.16324 after lifting the left pole-cover endpoint by 2*pi",
        "phi_p^- - phi_h > 0.110835 after lifting the left pole-cover endpoint by 2*pi",
    ], "phase-gap predicate semantics changed")
    gap_lowers = {
        "V2.ATLAS.PHASE_GAP_AH": homoclinic_bridge[0] - algebraic[1],
        "V2.ATLAS.PHASE_GAP_AP": pole_left_lift_lower - algebraic[1],
        "V2.ATLAS.PHASE_GAP_HP": pole_left_lift_lower - homoclinic_bridge[1],
    }
    atoms = []
    for predicate in thresholds:
        atom_id = predicate["atom_id"]
        threshold = Decimal(predicate["strict_lower"])
        lower = gap_lowers[atom_id]
        require(lower > threshold, f"{atom_id} strict gap is not PASS")
        atoms.append({
            "id": atom_id,
            "status": "PASS",
            "predicate": predicate["predicate"],
            "strict_gap_lower": str(lower),
            "required_strict_lower": str(threshold),
            "strict_margin_lower": str(lower - threshold),
        })

    atlas = config["full_event_atlas_contract"]
    require(set(atlas) == {
        "decomposition_status", "status", "full_run_status", "parent_atom",
        "parent_atoms", "required_core_manifest", "materialization_gate",
        "logic_boundary",
    }, "full event-atlas contract keys changed")
    require(atlas["status"] == "PENDING_DEFINITION" and
            atlas["full_run_status"] == "PROHIBITED_BEFORE_CORE_FREEZE",
            "full event-atlas run is not fail-closed")
    require(atlas["decomposition_status"] ==
            "PROPOSED_LOCAL_DECOMPOSITION_NOT_AN_IMPORTED_FLAGSHIP_NAMING" and
            atlas["parent_atom"] == {
                "id": "V2.EVENT_ATLAS", "status": "PENDING"} and
            atlas["parent_atoms"] == [
                {"id": "V2.ATLAS.CORE_MANIFEST", "status": "PENDING"},
                {"id": "V2.ATLAS.INCIDENCE_COMPLEX", "status": "PENDING"},
                {"id": "V2.ATLAS.FIRST_EVENT_CENSUS", "status": "PENDING"},
                {"id": "V2.ATLAS.TRANSPORTED_TRACES", "status": "PENDING"},
            ], "full event-atlas local decomposition changed")
    require(atlas["required_core_manifest"] == [
        "physical_event_faces",
        "defining_functions_domains_and_coorientations",
        "cell_face_corner_ids_and_sign_strata",
        "connected_components_and_empty_incidences",
        "fixed_corner_priority",
        "normalized_rank_speed_and_separation_margins",
        "phase_cut_containment_and_inactive_face_margins",
        "strict_event_order_margins",
        "homoclinic_tube_and_saddle_block_buffer",
        "complete_first_event_census",
        "exhaustion_with_no_residual_component",
        "transported_kato_traces_anchors_and_proper_phase_arc",
        "three_phase_gaps",
    ], "full event-atlas required core manifest changed")
    gate = atlas["materialization_gate"]
    require(gate == {
        "status": "PENDING_DEFINITION",
        "must_freeze_before": "FIRST_FULL_EVENT_ATLAS_RUN",
        "required_numeric_choices": ["D", "N", "precision"],
        "predeclared_parameter_cover": {
            "grid_axes": ["r", "a2", "epsilon"],
            "index_ranges_inclusive": {
                "r": [0, 7],
                "a2": [0, 127],
                "epsilon": [0, 3],
            },
            "cells": 4096,
        },
    }, "full event-atlas materialization gate changed")
    require(atlas["logic_boundary"] ==
            "Passing the three scalar phase gaps does not pass any proposed parent atom, Theorem V2(5), or V2.EVENT_ATLAS.",
            "full event-atlas logic boundary changed")
    require(config["refinement_budget"] == {
        "phase_gap_run": "NO_REFINEMENT_REUSE_P2C_GRID",
        "full_event_atlas": "PENDING_DEFINITION_BEFORE_FIRST_FULL_RUN",
        "budget_exhaustion_verdict": "INCONCLUSIVE",
    }, "refinement policy changed")
    require(config["nonclaims"] == [
        "Only the three frozen scalar phase-gap subatoms are evaluated.",
        "The full source-phase-and-order statement V2(5) remains pending because transported residual traces, the proper cut, and the complete cyclic-order manifest are not materialized.",
        "The full V2 event atlas and all four proposed local parent atoms remain pending.",
        "No P3--P5, temporal stability, Turing selection, or canard statement follows.",
        "The target was selected after disclosed historical design output and is not described as blinded confirmation.",
        "Independent-machine replay remains pending, so this local result is non-claim-bearing and not release-eligible.",
    ], "P2e v2 nonclaim boundary changed")

    return {
        "schema_version": "rfsn-vdp-p2e-phase-order-certificate/2",
        "scope": config["scope"],
        "box_id": config["box_id"],
        "comparison_bridge_id": config["comparison_bridge_id"],
        "status": "INCONCLUSIVE",
        "integrity_status": ("PASS_STRICT_BINARY_REPLAY" if
                             strict_binary is not None else
                             "PASS_LOG_BINDINGS_ONLY"),
        "mathematical_status": "INCONCLUSIVE",
        "local_subatom_status": "PASS_THREE_PHASE_GAPS_ONLY",
        "claim_bearing": False,
        "release_eligible": False,
        "phase_lift": config["phase_interface"]["common_lift"],
        "phase_hulls": {
            "algebraic": [str(value) for value in algebraic],
            "homoclinic_comparison_bridge_hull":
                [str(value) for value in homoclinic_bridge],
            "homoclinic_v2_target_hull":
                [str(value) for value in homoclinic_target],
            "pole_closed_cover_mod_2pi": [str(value) for value in pole_cover],
            "strict_two_pi_lower": str(two_pi_lower),
            "strict_pole_left_lift_lower": str(pole_left_lift_lower),
        },
        "obligations": atoms + [
            {"id": "V2.SOURCE_PHASES_AND_ORDER", "status": "PENDING"},
            {"id": "V2.EVENT_ATLAS", "status": "PENDING"},
        ],
        "strict_slab_evidence": observed_runs,
        "execution_verification": {
            "strict_binary_replayed_in_this_audit": strict_binary is not None,
            "mode": ("POST_FREEZE_STRICT_BINARY_EXACT_STDOUT_REPLAY" if
                     strict_binary is not None else
                     "LOG_PARSE_ONLY_NO_BINARY_EXECUTION"),
            "historical_design_log_disclosed_before_freeze": True,
            "frozen_process_environment": (strict_runs["process_environment"]
                                            if strict_binary is not None else
                                            None),
        },
        "full_event_atlas_contract": atlas,
        "evidence": {
            "configuration_sha256": sha256_bytes(config_bytes),
            "theorem_sha256": theorem_binding["sha256"],
            "target_box_sha256": config["target_box_binding"]["sha256"],
            "comparison_bridge_sha256":
                config["comparison_bridge_binding"]["sha256"],
            "strict_source_commit": source["commit"],
            "strict_source_sha256": source["sha256"],
            "strict_binary_sha256": source["binary_sha256"],
            "capd_commit": source["capd_commit"],
            "p2c_certificate_sha256":
                config["p2c_certificate_binding"]["sha256"],
            "kato_certificate_sha256":
                config["kato_certificate_binding"]["sha256"],
            "algebraic_anchor_sha256": algebraic_binding["sha256"],
            "pole_anchor_sha256": pole_binding["sha256"],
        },
        "nonclaims": config["nonclaims"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--strict-binary", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-result", type=Path)
    args = parser.parse_args()
    require(args.strict_binary is not None or
            (args.output is None and args.check_result is None),
            "--output and --check-result require --strict-binary")
    result = audit(args.config, args.strict_binary)
    if args.check_result is not None:
        require(load_json(args.check_result) == result,
                "committed P2e v2 phase result is stale")
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
