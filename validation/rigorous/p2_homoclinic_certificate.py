#!/usr/bin/env python3
"""Build and check the local P2c strict-evidence summary certificate.

This deliberately does not rerun the 16,384-cell CAPD computations.  It
materializes the source snapshot named by the certificate, verifies and
parses the four archived fixed-order strict logs, checks the historical
P2a/P2b/P2bK certificate bindings at their recorded Git commits, and reruns
the inexpensive exact-Fraction tail composition.  Independent-machine replay
remains a separate release gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any

import jsonschema


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
CONFIG_PATH = "validation/rigorous/config/vdp_p2_homoclinic_v1.json"
CONFIG_SCHEMA_PATH = "validation/rigorous/p2_homoclinic.schema.json"
CERTIFICATE_SCHEMA_PATH = (
    "validation/rigorous/p2_homoclinic_certificate.schema.json")
SCOPE = "V2_P2C_HOMOCLINIC_KERNEL"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()

ATOM_IDS = [
    "V2.HOM.BRANCH",
    "V2.HOM.FIRST_HIT",
    "V2.HOM.TRANSVERSE",
    "V2.HOM.TAILS",
    "V2.HOM.MIDDLE_C2",
]
NONCLAIMS_PREFIX = [
    "A local mathematical PASS is not an aggregate theorem certificate.",
    "Independent-machine replay is pending and this certificate is not claim-bearing.",
]
CONFIG_NONCLAIMS = [
    "The certificate does not assert uniqueness outside the finite parameter-following lifted multiple-shooting tube.",
    "It does not validate the P2d exact saddle charts, the P2e event atlas, or P3--P5.",
    "It does not prove temporal stability or dynamic Turing-pattern selection.",
    "It does not identify a finite-parameter canard.",
    "The strict executable bytes are not archived; their SHA-256 values are provenance records, while this certificate parses archived logs and does not rebuild or rerun the full grid.",
    "The evidence freeze is retrospective and the independent-machine replay remains pending; therefore this local certificate is not claim-bearing.",
]
MUTATION_POLICY = (
    "Any change to the bridge, source family, lifted shooting tube, grid, "
    "first-hit partition, derivative norm, tail composition, evidence log, "
    "or acceptance constant requires a new versioned configuration and "
    "certificate."
)
LOCAL_PRE_SOURCE_DOMAIN = (
    "fixed xi in [-11,-T_h], plus its reversible reflection"
)
LOCAL_PRE_SOURCE_FORMULA = (
    "Y(theta,xi)=physical_Z(theta,b_s(theta),xi+T_h(theta))"
)
LOCAL_AND_TAIL_SCOPE = (
    "covers the two infinite tails and local pre-source segments only; "
    "it does not yet cover the source-to-symmetry compact core"
)
MIDDLE_COVERAGE = {
    "full_real_line": True,
    "negative_half": [
        "xi<=-11 infinite tail",
        "-11<=xi<=-T_h local pre-source",
        "-T_h<=xi<=0 continuous centered compact middle",
    ],
    "positive_half": "fixed parameter-independent Euclidean-isometric reverser",
}
SOURCE_PATHS = [
    "RESEARCH_CONTRACT.md",
    "theory/BASELINE.md",
    "van-der-pol/CENTRAL_CONTINUATION.md",
    "validation/rigorous/P2_VALIDATION_CONTRACT.md",
    "validation/rigorous/P2C_SCOUT_REPORT.md",
    "validation/rigorous/README.md",
    "validation/rigorous/obligations.json",
    "validation/rigorous/dependency.lock.json",
    "validation/rigorous/flagship_import.lock.json",
    "validation/rigorous/config/vdp_box_v1.json",
    "validation/rigorous/config/vdp_bridge_v1.json",
    CONFIG_PATH,
    CONFIG_SCHEMA_PATH,
    CERTIFICATE_SCHEMA_PATH,
    "validation/rigorous/certificate.schema.json",
    "validation/rigorous/check_certificate.py",
    "validation/rigorous/rigorous_common.py",
    "validation/rigorous/p2_kato.schema.json",
    "validation/rigorous/p2_homoclinic_certificate.py",
    "validation/rigorous/tests/test_p2_homoclinic_certificate.py",
    "validation/rigorous/results/vdp_bridge_v1_p2a_local_graph.json",
    "validation/rigorous/results/vdp_bridge_v1_p2b_jets.json",
    "validation/rigorous/results/vdp_bridge_v1_p2b_kato.json",
    "validation/rigorous/design/p2c_homoclinic_multishoot_scout.cpp",
    "validation/rigorous/design/p2c_root_jet_summary_v1.json",
    "validation/rigorous/design/p2c_tail_composition_scout.py",
    "validation/rigorous/design/p2c_tail_composition_v1.json",
    "validation/rigorous/design/p2c_middle_jet_summary_v1.json",
    "validation/rigorous/design/logs/README.md",
    "validation/rigorous/design/logs/p2c_branch_v1.log",
    "validation/rigorous/design/logs/p2c_first_hit_v1.log",
    "validation/rigorous/design/logs/p2c_root_jets_v1.log",
    "validation/rigorous/design/logs/p2c_middle_c2_v1.log",
]


class EvidenceError(ValueError):
    """A frozen P2c evidence interface is malformed or fails a gate."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json_bytes(value: bytes, label: str) -> dict[str, Any]:
    try:
        result = json.loads(value)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise EvidenceError(f"cannot parse {label}: {error}") from error
    if not isinstance(result, dict):
        raise EvidenceError(f"{label} is not a JSON object")
    return result


def git_blob(repository: Path, commit: str, path: str) -> bytes:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise EvidenceError(f"invalid Git commit for {path}: {commit!r}")
    if path.startswith("/") or ".." in Path(path).parts:
        raise EvidenceError(f"unsafe repository path: {path!r}")
    run = subprocess.run(
        ["git", "-C", str(repository), "show", f"{commit}:{path}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if run.returncode != 0:
        detail = run.stderr.decode(errors="replace").strip()
        raise EvidenceError(f"cannot materialize {commit}:{path}: {detail}")
    return run.stdout


def git_text(repository: Path, commit: str, path: str) -> str:
    try:
        return git_blob(repository, commit, path).decode("utf-8")
    except UnicodeDecodeError as error:
        raise EvidenceError(f"{commit}:{path} is not UTF-8") from error


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvidenceError(message)


def require_hash(value: bytes, expected: str, label: str) -> None:
    observed = sha256_bytes(value)
    require(observed == expected,
            f"{label} SHA-256 mismatch: {observed} != {expected}")


def decimal(value: str) -> Decimal:
    try:
        result = Decimal(value)
    except Exception as error:  # pragma: no cover - Decimal's subclasses vary.
        raise EvidenceError(f"invalid decimal {value!r}") from error
    require(result.is_finite(), f"non-finite decimal {value!r}")
    return result


def one_match(pattern: str, text: str, label: str) -> re.Match[str]:
    matches = list(re.finditer(pattern, text, re.MULTILINE))
    require(len(matches) == 1,
            f"{label}: expected one match for {pattern!r}, found {len(matches)}")
    return matches[0]


def mode_blocks(text: str, mode: str) -> list[str]:
    return re.findall(
        rf"(?ms)^mode {re.escape(mode)}\n.*?(?=^mode |\Z)", text)


def pair(pattern: str, text: str, label: str) -> tuple[Decimal, Decimal]:
    match = one_match(pattern, text, label)
    lower, upper = decimal(match.group(1)), decimal(match.group(2))
    require(lower <= upper, f"{label}: reversed interval")
    return lower, upper


def dec_text(value: Decimal) -> str:
    return str(value)


def interval_hull(values: list[tuple[Decimal, Decimal]]) -> list[str]:
    return [dec_text(min(value[0] for value in values)),
            dec_text(max(value[1] for value in values))]


def parse_branch(text: str) -> dict[str, Any]:
    anchors = mode_blocks(text, "mu-grid-anchor")
    slabs = mode_blocks(text, "mu-grid-slab")
    require(len(anchors) == 1, "branch log must contain one anchor block")
    require(len(slabs) == 32, "branch log must contain 32 slab blocks")
    anchor = anchors[0]
    for line in (
        "PASS mu-grid frozen-core anchor",
        "anchor_face direction core->cell",
        "anchor_import phase",
    ):
        require(line in anchor, f"branch anchor lacks {line!r}")
    require("anchor_face direction core->cell" in anchor and
            " graph-e PASS" in anchor,
            "branch anchor common-face gate is not PASS")
    require("anchor_import phase" in anchor and anchor.count(" PASS") >= 4,
            "branch anchor import gate is not PASS")

    cells = 0
    face_totals = {"a2": 0, "epsilon": 0, "r": 0}
    inclusion: list[Decimal] = []
    contraction: list[Decimal] = []
    determinants: list[tuple[Decimal, Decimal]] = []
    face_ratios: dict[str, list[Decimal]] = {key: [] for key in face_totals}
    indices: list[int] = []
    r_cells: dict[int, tuple[Decimal, Decimal]] = {}
    for slab in slabs:
        require("grid 32 128 4 radius_factor 3" in slab,
                "branch slab grid contract changed")
        index = int(one_match(r"^r_index ([0-9]+) ", slab,
                              "branch r index").group(1))
        indices.append(index)
        r_cells[index] = pair(
            r"^r_index [0-9]+ r_cell \[([^,]+), ([^\]]+)\]$", slab,
            f"branch slab {index} r cell")
        cell = one_match(
            r"^cells ([0-9]+) pass ([0-9]+) max_inclusion ([^ ]+) .*?"
            r"max_contraction ([^ ]+) .*?determinant_hull \[([^,]+), ([^\]]+)\] PASS$",
            slab, f"branch slab {index} cells")
        total, passed = int(cell.group(1)), int(cell.group(2))
        require(total == passed == 512,
                f"branch slab {index} is not 512/512 PASS")
        cells += passed
        inc, con = decimal(cell.group(3)), decimal(cell.group(4))
        det = decimal(cell.group(5)), decimal(cell.group(6))
        require(inc < 1 and con < 1,
                f"branch slab {index} Krawczyk gate is not strict")
        require(det[0] > 0 and det[0] <= det[1],
                f"branch slab {index} determinant is not strictly positive")
        inclusion.append(inc)
        contraction.append(con)
        determinants.append(det)
        for key, expected in (("a2", 508), ("epsilon", 384), ("r", 512)):
            face = one_match(
                rf"^{key}_faces ([0-9]+) pass ([0-9]+) max_ratio ([^ ]+) .* PASS$",
                slab, f"branch slab {index} {key} faces")
            total_faces, passed_faces = int(face.group(1)), int(face.group(2))
            if key == "r" and index == 31:
                expected = 0
            require(total_faces == passed_faces == expected,
                    f"branch slab {index} {key}-face cover changed")
            ratio = decimal(face.group(3))
            require(ratio < 1, f"branch slab {index} {key}-face gate is not strict")
            face_totals[key] += passed_faces
            face_ratios[key].append(ratio)
        require(slab.rstrip().endswith("PASS mu-grid slab root identification"),
                f"branch slab {index} lacks terminal PASS")
    require(sorted(indices) == list(range(32)), "branch slab indices are incomplete")
    require(cells == 16384, "branch total cell count changed")
    require(face_totals == {"a2": 16256, "epsilon": 12288, "r": 15872},
            "branch common-face totals changed")
    for index in range(32):
        observed_lower = Fraction.from_float(float(r_cells[index][0]))
        observed_upper = Fraction.from_float(float(r_cells[index][1]))
        exact_lower, exact_upper = Fraction(index, 400), Fraction(index + 1, 400)
        require(observed_lower <= exact_lower <= exact_upper <= observed_upper,
                f"branch slab {index} does not enclose its exact rational r cell")
    require(32 * 128 * 4 == cells and
            32 * 127 * 4 == face_totals["a2"] and
            32 * 128 * 3 == face_totals["epsilon"] and
            31 * 128 * 4 == face_totals["r"],
            "branch grid/face combinatorics do not form the declared box complex")
    return {
        "status": "PASS",
        "cells_passed": cells,
        "cells_total": cells,
        "common_faces_passed": {**face_totals, "total": sum(face_totals.values())},
        "frozen_core_anchor": "PASS",
        "maximum_inclusion": dec_text(max(inclusion)),
        "maximum_contraction": dec_text(max(contraction)),
        "determinant_hull": interval_hull(determinants),
        "maximum_face_ratio": {
            key: dec_text(max(values)) for key, values in face_ratios.items()},
        "grid_geometry": {
            "r_cells": "R_i=[i/400,(i+1)/400], 0<=i<32",
            "a2_cells": "A_j=[(j-64)/256,(j-63)/256], 0<=j<128",
            "epsilon_cells": "E_k=[(8+k)/10,(9+k)/10], 0<=k<4",
            "gap_free_box_complex": "PASS"},
        "uniqueness_scope": "finite parameter-following lifted 38-dimensional multiple-shooting tube",
    }


def parse_first_hit(text: str) -> dict[str, Any]:
    slabs = mode_blocks(text, "mu-grid-first-hit-slab")
    require(len(slabs) == 32, "first-hit log must contain 32 slab blocks")
    indices: list[int] = []
    cells = dense_steps = 0
    margins: dict[str, list[Decimal]] = {
        key: [] for key in
        ("P_positive", "Q_positive", "P_negative", "Q_negative", "U_final")}
    half_times: list[tuple[Decimal, Decimal]] = []
    return_times: list[tuple[Decimal, Decimal]] = []
    for slab in slabs:
        require("pre_source_local_graph_exclusion imported_prerequisite_not_evaluated" in slab,
                "first-hit log changed its pre-source prerequisite boundary")
        require("grid 32 128 4 radius_factor 3" in slab,
                "first-hit slab grid contract changed")
        index = int(one_match(r"^r_index ([0-9]+) ", slab,
                              "first-hit r index").group(1))
        indices.append(index)
        count = one_match(r"^cells ([0-9]+) pass ([0-9]+) dense_steps ([0-9]+)$",
                          slab, f"first-hit slab {index} counts")
        total, passed, steps = map(int, count.groups())
        require(total == passed == 512,
                f"first-hit slab {index} is not 512/512 PASS")
        cells += passed
        dense_steps += steps
        for key in margins:
            match = one_match(rf"^signed_margin {key} ([^ ]+) ", slab,
                              f"first-hit slab {index} {key}")
            value = decimal(match.group(1))
            require(value > 0, f"first-hit slab {index} {key} is not strict")
            margins[key].append(value)
        return_times.append(pair(
            r"^return_time_hull \[([^,]+), ([^\]]+)\]$", slab,
            f"first-hit slab {index} return time"))
        half_times.append(pair(
            r"^half_time_hull \[([^,]+), ([^\]]+)\]$", slab,
            f"first-hit slab {index} half time"))
        require(return_times[-1][0] > 0 and return_times[-1][1] < Decimal("0.2"),
                f"first-hit slab {index} event is outside the final flow box")
        require(slab.rstrip().endswith(
            "PASS mu-grid selected-source first symmetry-hit slab"),
            f"first-hit slab {index} lacks terminal PASS")
    require(sorted(indices) == list(range(32)), "first-hit slab indices are incomplete")
    require(cells == 16384 and dense_steps == 306287,
            "first-hit full-grid counts changed")
    return {
        "status": "PASS",
        "cells_passed": cells,
        "cells_total": cells,
        "dense_continuous_steps": dense_steps,
        "minimum_signed_margins": {
            key: dec_text(min(values)) for key, values in margins.items()},
        "return_time_hull": interval_hull(return_times),
        "half_time_hull": interval_hull(half_times),
        "pre_source_gate": "imported P2a true-graph exclusion",
        "final_flow_box": "Q strictly increasing because U>0",
    }


def to_hex(value: Decimal) -> str:
    result = float(value)
    require(math.isfinite(result), "decimal-to-binary64 conversion is non-finite")
    return result.hex()


def summary_hex(summary: dict[str, Any], *keys: str) -> str:
    current: Any = summary
    for key in keys:
        require(isinstance(current, dict) and key in current,
                f"summary lacks {'.'.join(keys)}")
        current = current[key]
    require(isinstance(current, str), f"summary {'.'.join(keys)} is not text")
    return current


def parse_root_jets(text: str, summary: dict[str, Any]) -> dict[str, Any]:
    slabs = mode_blocks(text, "mu-grid-root-jets-slab")
    require(len(slabs) == 32, "root-jet log must contain 32 slab blocks")
    indices: list[int] = []
    phase_hulls: list[tuple[Decimal, Decimal]] = []
    time_hulls: list[tuple[Decimal, Decimal]] = []
    return_hulls: list[tuple[Decimal, Decimal]] = []
    weighted: list[Decimal] = []
    solve: list[Decimal] = []
    event_u: list[Decimal] = []
    first_phase: dict[str, list[Decimal]] = {key: [] for key in
                                             ("theta_r", "theta_a", "theta_epsilon")}
    first_time = {key: [] for key in first_phase}
    second_order = [
        ("theta_r", "theta_r"), ("theta_r", "theta_a"),
        ("theta_r", "theta_epsilon"), ("theta_a", "theta_a"),
        ("theta_a", "theta_epsilon"), ("theta_epsilon", "theta_epsilon")]
    second_phase = {key: [] for key in second_order}
    second_time = {key: [] for key in second_order}
    for slab in slabs:
        require("grid 32 128 4 radius_factor 3" in slab,
                "root-jet slab grid contract changed")
        index = int(one_match(r"^r_index ([0-9]+) ", slab,
                              "root-jet r index").group(1))
        indices.append(index)
        count = one_match(r"^cells ([0-9]+)/([0-9]+)$", slab,
                          f"root-jet slab {index} cells")
        require(count.groups() == ("512", "512"),
                f"root-jet slab {index} is not 512/512")
        phase_hulls.append(pair(r"^phase_hull \[([^,]+), ([^\]]+)\] ", slab,
                                f"root-jet slab {index} phase"))
        time_hulls.append(pair(r"half_time_hull \[([^,]+), ([^\]]+)\] ", slab,
                               f"root-jet slab {index} half time"))
        return_hulls.append(pair(r"return_time_hull \[([^,]+), ([^\]]+)\]$", slab,
                                 f"root-jet slab {index} return time"))
        event_u.append(decimal(one_match(r"^event_minimum_U ([^ ]+) ", slab,
                                         f"root-jet slab {index} event U").group(1)))
        weighted.append(decimal(one_match(
            r"^maximum_weighted_inverse_contraction ([^ ]+) ", slab,
            f"root-jet slab {index} weighted contraction").group(1)))
        solve.append(decimal(one_match(r"^maximum_solve_inclusion ([^ ]+) ", slab,
                                       f"root-jet slab {index} solve").group(1)))
        require(weighted[-1] < 1 and solve[-1] < 1 and event_u[-1] > 0,
                f"root-jet slab {index} has a non-strict implicit/event gate")
        for key in first_phase:
            match = one_match(
                rf"^normalized_first_abs {key} root [^ ]+ phase ([^ ]+) half_time ([^ ]+) ",
                slab, f"root-jet slab {index} first {key}")
            first_phase[key].append(decimal(match.group(1)))
            first_time[key].append(decimal(match.group(2)))
        for left, right in second_order:
            match = one_match(
                rf"^normalized_second_abs {left} {right} root [^ ]+ phase ([^ ]+) half_time ([^ ]+) ",
                slab, f"root-jet slab {index} second {left},{right}")
            second_phase[left, right].append(decimal(match.group(1)))
            second_time[left, right].append(decimal(match.group(2)))
        require(slab.rstrip().endswith("PASS mu-grid true-source root C2 jet slab"),
                f"root-jet slab {index} lacks terminal PASS")
    require(sorted(indices) == list(range(32)), "root-jet slab indices are incomplete")
    phase_first_max = [max(first_phase[key]) for key in first_phase]
    time_first_max = [max(first_time[key]) for key in first_time]
    phase_second_max = [max(second_phase[key]) for key in second_order]
    time_second_max = [max(second_time[key]) for key in second_order]
    require(summary.get("schema_version") == "rfsn-vdp-p2c-root-jet-summary/1" and
            summary.get("status") == "PASS" and summary.get("claim_bearing") is False,
            "root-jet summary status or schema changed")
    require(summary.get("grid") == {
        "radius_factor": 3, "subdivisions": [32, 128, 4],
        "passed_cells": 16384, "total_cells": 16384},
        "root-jet summary grid changed")
    expected_hex_lists = {
        "phase_first_abs_upper_hex": [to_hex(value) for value in phase_first_max],
        "time_first_abs_upper_hex": [to_hex(value) for value in time_first_max],
        "phase_second_abs_upper_hex": [to_hex(value) for value in phase_second_max],
        "time_second_abs_upper_hex": [to_hex(value) for value in time_second_max],
    }
    for key, expected in expected_hex_lists.items():
        require(summary.get(key) == expected, f"root-jet summary {key} differs from logs")
    require(summary.get("half_time_upper_hex") == to_hex(max(value[1] for value in time_hulls)),
            "root-jet summary half-time upper differs from logs")
    return {
        "status": "PASS", "cells_passed": 16384, "cells_total": 16384,
        "phase_hull": interval_hull(phase_hulls),
        "half_time_hull": interval_hull(time_hulls),
        "return_time_hull": interval_hull(return_hulls),
        "minimum_event_U": dec_text(min(event_u)),
        "maximum_weighted_inverse_contraction": dec_text(max(weighted)),
        "maximum_componentwise_solve_inclusion": dec_text(max(solve)),
        "complete_parameter_derivative_order": 2,
    }


def interval_record_matches(record: Any, hull: list[str]) -> bool:
    if not isinstance(record, dict):
        return False
    try:
        return (record["lower"]["binary64_hex"] == to_hex(decimal(hull[0])) and
                record["upper"]["binary64_hex"] == to_hex(decimal(hull[1])))
    except (KeyError, EvidenceError):
        return False


def parse_middle(text: str, summary: dict[str, Any]) -> dict[str, Any]:
    slabs = mode_blocks(text, "mu-grid-middle-jets-slab")
    require(len(slabs) == 32, "middle-C2 log must contain 32 slab blocks")
    indices: list[int] = []
    cells = steps = sections = 0
    half_times: list[tuple[Decimal, Decimal]] = []
    return_times: list[tuple[Decimal, Decimal]] = []
    centered: list[tuple[Decimal, Decimal]] = []
    physical: list[list[tuple[Decimal, Decimal]]] = [[], [], [], []]
    metrics: dict[str, list[Decimal]] = {key: [] for key in (
        "normalized_state_C0_euclidean",
        "normalized_fixed_t_L1_hilbert_schmidt",
        "normalized_fixed_t_L2_hilbert_schmidt",
        "normalized_centered_xi_L1_hilbert_schmidt",
        "normalized_centered_xi_L2_hilbert_schmidt")}
    for slab in slabs:
        require("grid 32 128 4 radius_factor 3" in slab and
                "capd_hessian_convention_self_check PASS" in slab,
                "middle-C2 slab grid or CAPD Hessian convention changed")
        index = int(one_match(r"^r_index ([0-9]+) ", slab,
                              "middle-C2 r index").group(1))
        indices.append(index)
        count = one_match(
            r"^cells ([0-9]+)/([0-9]+) dense_steps ([0-9]+) explicit_initial_sections ([0-9]+)$",
            slab, f"middle-C2 slab {index} counts")
        passed, total, slab_steps, slab_sections = map(int, count.groups())
        require(passed == total == 512, f"middle-C2 slab {index} is not 512/512")
        cells += passed; steps += slab_steps; sections += slab_sections
        half_times.append(pair(r"^half_time_hull \[([^,]+), ([^\]]+)\] ", slab,
                               f"middle-C2 slab {index} half time"))
        return_times.append(pair(r"return_time_hull \[([^,]+), ([^\]]+)\]$", slab,
                                 f"middle-C2 slab {index} return time"))
        centered.append(pair(r"^centered_tube_xi_hull \[([^,]+), ([^\]]+)\]$", slab,
                             f"middle-C2 slab {index} centered tube"))
        require(centered[-1][0] <= -half_times[-1][1],
                f"middle-C2 slab {index} does not reach every source seam")
        require(centered[-1][1] >= 0,
                f"middle-C2 slab {index} does not reach the symmetry seam")
        require(centered[-1][0] > Decimal("-11") and
                centered[-1][1] < Decimal("11"),
                f"middle-C2 slab {index} leaves the |xi|<11 weight window")
        for key in metrics:
            metrics[key].append(decimal(one_match(
                rf"^{key} ([^ ]+) ", slab,
                f"middle-C2 slab {index} {key}").group(1)))
        state = one_match(
            r"^physical_state_hull \[([^,]+), ([^\]]+)\] \[([^,]+), ([^\]]+)\] "
            r"\[([^,]+), ([^\]]+)\] \[([^,]+), ([^\]]+)\]$",
            slab, f"middle-C2 slab {index} physical hull")
        for coordinate in range(4):
            physical[coordinate].append((
                decimal(state.group(2 * coordinate + 1)),
                decimal(state.group(2 * coordinate + 2))))
        seam = one_match(
            r"^minus_11_to_source_seam imported_exact_algebra_local_pre_source_bound "
            r"original_parameter_common_upper ([0-9]+)$", slab,
            f"middle-C2 slab {index} seam")
        require(seam.group(1) == "342685",
                f"middle-C2 slab {index} seam constant changed")
        require(slab.rstrip().endswith(
            "PASS mu-grid continuous compact-middle C2 jet slab"),
            f"middle-C2 slab {index} lacks terminal PASS")
    require(sorted(indices) == list(range(32)), "middle-C2 slab indices are incomplete")
    require((cells, steps, sections) == (16384, 262144, 163840),
            "middle-C2 aggregate counts changed")
    require(summary.get("schema_version") == "rfsn-vdp-p2c-compact-middle-summary/1" and
            summary.get("status") == "PASS" and summary.get("claim_bearing") is False,
            "middle summary status or schema changed")
    grid = summary.get("grid", {})
    require(grid.get("slabs_passed") == grid.get("slabs_total") == 32 and
            grid.get("cells_passed") == grid.get("cells_total") == cells and
            grid.get("dense_steps") == steps and
            grid.get("explicit_initial_sections") == sections,
            "middle summary counts differ from logs")
    hulls = {
        "half_time": interval_hull(half_times),
        "return_time": interval_hull(return_times),
        "centered_tube_xi": interval_hull(centered),
        "physical_state_U": interval_hull(physical[0]),
        "physical_state_P": interval_hull(physical[1]),
        "physical_state_V": interval_hull(physical[2]),
        "physical_state_Q": interval_hull(physical[3]),
    }
    for key, hull in hulls.items():
        require(interval_record_matches(summary.get("continuous_hulls", {}).get(key), hull),
                f"middle summary {key} differs from logs")
    metric_keys = {
        "normalized_state_C0_euclidean": "normalized_state_C0_euclidean",
        "normalized_fixed_t_L1_hilbert_schmidt": "normalized_fixed_t_L1_hilbert_schmidt",
        "normalized_fixed_t_L2_hilbert_schmidt": "normalized_fixed_t_L2_hilbert_schmidt",
        "normalized_centered_xi_L1_hilbert_schmidt": "normalized_centered_xi_L1_hilbert_schmidt",
        "normalized_centered_xi_L2_hilbert_schmidt": "normalized_centered_xi_L2_hilbert_schmidt",
    }
    for log_key, summary_key in metric_keys.items():
        observed = summary.get("global_maxima", {}).get(summary_key, {}).get("upper", {})
        require(observed.get("binary64_hex") == to_hex(max(metrics[log_key])),
                f"middle summary {summary_key} differs from logs")
    require(summary.get("coverage") == MIDDLE_COVERAGE,
            "middle summary coverage decomposition changed")
    return {
        "status": "PASS", "slabs_passed": 32, "slabs_total": 32,
        "cells_passed": cells, "cells_total": cells,
        "dense_continuous_steps": steps,
        "explicit_initial_sections": sections,
        "continuous_hulls": hulls,
        "global_maxima": {key: dec_text(max(values))
                           for key, values in metrics.items()},
        "coverage_seams": {
            "every_slab_reaches_source": True,
            "every_slab_reaches_symmetry": True,
            "every_slab_strictly_inside_abs_xi_11": True,
        },
    }


def fraction_record(value: Any, label: str) -> Fraction:
    require(isinstance(value, dict), f"{label} is not a rational record")
    try:
        result = Fraction(int(value["numerator"]), int(value["denominator"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        raise EvidenceError(f"invalid rational record {label}") from error
    return result


def ceiling(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def verify_historical_certificate(
        repository: Path, snapshot_commit: str, binding: dict[str, Any]
        ) -> dict[str, Any]:
    path = binding["path"]
    blob = git_blob(repository, snapshot_commit, path)
    require_hash(blob, binding["sha256"], path)
    certificate = load_json_bytes(blob, path)
    source_commit = certificate.get("source_revision", {}).get("commit")
    require(isinstance(source_commit, str), f"{path} lacks source commit")
    schema_blob = git_blob(repository, source_commit,
                           "validation/rigorous/certificate.schema.json")
    schema = load_json_bytes(schema_blob, f"{source_commit}:certificate schema")
    try:
        jsonschema.validate(certificate, schema,
                            format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as error:
        raise EvidenceError(f"historical certificate {path} schema: {error.message}") from error
    for source in certificate.get("source_bindings", []):
        require(isinstance(source, dict), f"{path} has malformed source binding")
        frozen = git_blob(repository, source_commit, source["path"])
        require_hash(frozen, source["sha256"],
                     f"historical {path} binding {source['path']}")
    statuses = {item.get("id"): item.get("status")
                for item in certificate.get("obligations", [])
                if isinstance(item, dict)}
    require(certificate.get("scope") == binding["required_scope"],
            f"historical certificate {path} scope changed")
    require(certificate.get("integrity_status") == "PASS" and
            certificate.get("mathematical_status") == "PASS" and
            certificate.get("final_status") == "INCONCLUSIVE" and
            certificate.get("claim_bearing") is False,
            f"historical certificate {path} status boundary changed")
    for atom in binding["required_atoms"]:
        require(statuses.get(atom) == "PASS",
                f"historical certificate {path} lacks PASS for {atom}")
    return {
        "path": path, "sha256": binding["sha256"],
        "scope": certificate["scope"], "source_commit": source_commit,
        "source_bindings_verified_at_recorded_commit": len(
            certificate.get("source_bindings", [])),
        "integrity_status": "PASS", "mathematical_status": "PASS",
        "final_status": "INCONCLUSIVE", "claim_bearing": False,
        "required_atoms": {atom: statuses[atom] for atom in binding["required_atoms"]},
    }


def compatibility_extract(text: str, start: str, end: str) -> bytes:
    require(text.count(start) == 1 and text.count(end) == 1,
            "P2bK compatibility markers are not unique")
    first = text.index(start)
    last = text.index(end, first) + len(end)
    return text[first:last].encode("utf-8")


def validate_config(
        repository: Path, source_commit: str, config: dict[str, Any]) -> None:
    schema = load_json_bytes(git_blob(repository, source_commit, CONFIG_SCHEMA_PATH),
                             CONFIG_SCHEMA_PATH)
    try:
        jsonschema.validate(config, schema,
                            format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as error:
        raise EvidenceError(f"P2c configuration schema: {error.message}") from error
    require(config.get("proved_subobligations") == ATOM_IDS,
            "P2c mathematical atom list changed")
    require(config.get("parent_obligation") == "V2.HOMOCLINIC",
            "P2c parent obligation changed")
    require(config.get("uniqueness_scope") ==
            "Exactly one selected physical zero record in each fiber of the finite parameter-following lifted 38-dimensional multiple-shooting tube; no tube-exterior or global direct-shooting uniqueness is asserted.",
            "P2c uniqueness scope changed")
    require(config.get("mutation_policy") == MUTATION_POLICY,
            "P2c mutation policy changed")
    require(config.get("nonclaims") == CONFIG_NONCLAIMS,
            "P2c nonclaim boundary changed")
    basis = config.get("selection_basis", {})
    require(isinstance(basis, dict), "P2c selection basis is not an object")
    expected_prerequisites = {
        "p2a_certificate": {
            "path": "validation/rigorous/results/vdp_bridge_v1_p2a_local_graph.json",
            "sha256": "192b351c3f153080d82bc856fa3c667388dc16c7b4cf0cfa8568fa347bcaf6be",
            "required_scope": "V2_LOCAL_GRAPH_KERNEL",
            "required_atoms": ["V2.WU.FRAME_BLOCK", "V2.WU.COARSE_GRAPH"],
        },
        "p2b_certificate": {
            "path": "validation/rigorous/results/vdp_bridge_v1_p2b_jets.json",
            "sha256": "07b0949a3d403c0c0a85a4a157b86d7b32cce3ff0348aeffa1db474d441fca07",
            "required_scope": "V2_P2_JETS_KERNEL",
            "required_atoms": ["V2.WU.JETS", "V2.WU_GRAPH"],
        },
        "p2bk_certificate": {
            "path": "validation/rigorous/results/vdp_bridge_v1_p2b_kato.json",
            "sha256": "c67cce575caa396eba5b4388e8ba9a0c9d73fd702f69911d64c878f57f27bff3",
            "required_scope": "V2_P2_KATO_KERNEL",
            "required_atoms": ["V2.PHASE.TRUE_SOURCE", "V2.PHASE.KATO_INTERFACE"],
        },
    }
    for name, expected in expected_prerequisites.items():
        require(basis.get(name) == expected,
                f"P2c canonical {name} binding changed")
    require(basis.get("evidence_snapshot_commit") ==
            "33a830298df9c58f4dee5530e30d3bdf6b9874f4",
            "P2c evidence snapshot commit changed")
    require(basis.get("continuation_bridge") == {
        "path": "validation/rigorous/config/vdp_bridge_v1.json",
        "sha256": "2b62e6fc5625d3f5634d986f7e9cbe8199abfc45c7b97ca29e5efd464b5b69c7"},
        "P2c canonical bridge binding changed")
    require(basis.get("current_v2_theorem") == {
        "path": "van-der-pol/CENTRAL_CONTINUATION.md",
        "sha256": "51dbc0dbeb9ac232fc41f21af83930b3b3c9e98385f0b7ed9963ca6dc10f0aa3"},
        "P2c current V2 theorem binding changed")
    require(basis.get("p2bk_configuration") == {
        "path": "validation/rigorous/config/vdp_p2_kato_v1.json",
        "sha256": "676de23609a66b9a6fa35d2cc476878018bc84b4615460719f9c2f87eb1823e3"},
        "P2c canonical P2bK configuration binding changed")
    require(basis.get("dependency_lock") == {
        "path": "validation/rigorous/dependency.lock.json",
        "sha256": "4d486a63cddf0902cc9fc4dedacc5a172527f6e167e2d311afa680c077a45b68"} and
        basis.get("flagship_import_lock") == {
            "path": "validation/rigorous/flagship_import.lock.json",
            "sha256": "6c1752d6ee78d4b670c74ecb85e776eddcb4459e0b0e7f7ae14cae2325e0476e"},
        "P2c dependency/import lock binding changed")
    compatibility = basis.get("historical_p2bk_source_compatibility")
    require(isinstance(compatibility, dict) and
            compatibility.get("historical_commit") ==
            "91007a88395290a594ba88047ff6ae45b9cebb80" and
            compatibility.get("current_commit") ==
            "33a830298df9c58f4dee5530e30d3bdf6b9874f4" and
            compatibility.get("path") == "van-der-pol/CENTRAL_CONTINUATION.md" and
            compatibility.get("common_extract_sha256") ==
            "490bc36b38d3bb65a937e0b2a363c38c5ef687d7316e7019fbc3928266717682",
            "P2c P2bK compatibility binding changed")
    grid = config.get("parameter_grid", {})
    require(grid == {
        "bridge": {"r": ["0", "2/25"], "a2": ["-1/4", "1/4"],
                   "epsilon": ["4/5", "6/5"]},
        "ordered_axes": ["r", "a2", "epsilon"],
        "subdivisions": [32, 128, 4], "cells": 16384,
        "shooting_radius_factor": 3,
        "require_gap_free_exact_rational_cells": True},
        "P2c exact parameter grid changed")
    acceptance = config.get("acceptance_contract", {})
    required_acceptance = {
        "branch_cells_passed": 16384,
        "branch_faces": {"a2": 16256, "epsilon": 12288,
                         "r": 15872, "total": 44416},
        "frozen_core_anchor_required": True,
        "first_hit_cells_passed": 16384,
        "first_hit_dense_steps": 306287,
        "root_jet_cells_passed": 16384,
        "middle_slabs_passed": 32,
        "middle_cells_passed": 16384,
        "middle_dense_steps": 262144,
        "middle_explicit_initial_sections": 163840,
        "tail_cut_T_star": 11,
        "tail_weight_eta": {"numerator": "1", "denominator": "5"},
        "strict_exponential_upper": 27,
        "original_parameter_first_factor": 25,
        "original_parameter_second_factor": 625,
        "tail_common_integer_original_mu": 95434,
        "local_pre_source_and_tail_common_integer_original_mu": 342685,
        "global_common_integer_normalized_theta": 114395,
        "global_common_integer_original_mu": 71496600,
        "global_original_mu_C2": {
            "numerator": "78611342260591861875",
            "denominator": "1099511627776"},
        "require_full_real_line_coverage": True,
    }
    require(acceptance == required_acceptance, "P2c acceptance contract changed")
    snapshot = basis.get("evidence_snapshot_commit")
    require(isinstance(snapshot, str), "P2c evidence snapshot commit is missing")
    ancestor = subprocess.run(
        ["git", "-C", str(repository), "merge-base", "--is-ancestor",
         snapshot, source_commit])
    require(ancestor.returncode == 0,
            "P2c evidence snapshot is not an ancestor of the certificate source")
    for name in ("continuation_bridge", "current_v2_theorem",
                 "p2bk_configuration", "dependency_lock", "flagship_import_lock"):
        item = basis.get(name, {})
        blob = git_blob(repository, snapshot, item.get("path", ""))
        require_hash(blob, item.get("sha256", ""), f"P2c selection {name}")
        current = git_blob(repository, source_commit, item.get("path", ""))
        require_hash(current, item.get("sha256", ""), f"P2c current {name}")
    p2bk_config_item = basis["p2bk_configuration"]
    p2bk_config = load_json_bytes(
        git_blob(repository, source_commit, p2bk_config_item["path"]),
        "historical P2bK configuration")
    p2bk_schema = load_json_bytes(
        git_blob(repository, source_commit,
                 "validation/rigorous/p2_kato.schema.json"),
        "P2bK configuration schema")
    try:
        jsonschema.validate(p2bk_config, p2bk_schema,
                            format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as error:
        raise EvidenceError(
            f"historical P2bK configuration schema: {error.message}") from error
    p2bk_basis = p2bk_config.get("selection_basis", {})
    old_source = p2bk_basis.get("v2_source_definition", {})
    for commit_name, commit in (
            ("selection", p2bk_basis.get("repository_commit")),
            ("certificate", basis["historical_p2bk_source_compatibility"]
             ["historical_commit"])):
        require(isinstance(commit, str),
                f"P2bK {commit_name} commit is missing")
        old_blob = git_blob(repository, commit, old_source.get("path", ""))
        require_hash(old_blob, old_source.get("sha256", ""),
                     f"P2bK {commit_name} source definition")
    expected_runs = {
        "branch": (
            "2c60e4930bb585a24d7a8945c1b5b3e7469a1cf8",
            "76d4ca6e953c0446c981b89b51b1f569cb1626a15f9fc2898aae2d106acf60ec",
            "46cc65468a7082f5adaa5902d76c962ead8a123653f3bfd39959769650ee63dc",
            "73afc5b9a365ea7ab505095feb7098154a0ab5f83cfe7c6dbd0e8788a275e364"),
        "first_hit": (
            "25ff53a7f4fa2457a09767d2cad992aff245bcea",
            "3aa6368471ced8afc37e73128149548e7756caa04505ebcb615a3451bf6beabd",
            "b6d27a618146ea90db1310c1f0b510190a573b35bd8d5d669f5e354d6f6f0fd0",
            "09f3e809b4651a3ed8dfc5482b9900aadf35367b08202dbc17a3a79af5f6b5f3"),
        "root_jets": (
            "0f35363264d29a8b4b3b39ab10317273aff35fab",
            "d3fe590fd64da02e18941d32e8d43a3b50e018f37d59513e37a41d1d32cf7a2f",
            "b7235063abff295b0d0e51a0587e5c8dd871af35a1c5d4af7a060e3e6cde0f04",
            "b503e777183e6a5f759978b081828b70119bbfb95f48e643649857a89cace969"),
        "compact_middle": (
            "c1b8c815a1ffd0b690c46d1631b383f16b11fce4",
            "7f1947f4d8ca7eaa74194a5060911a167982e6e5038c585be7609e5e36a98493",
            "1d5b8092148d2a9cf1892e0880c01bd122edf03421f168142585818a5f3e9c7e",
            "9027b0d8e5247bc81df05ef680346133a0ffc0bb63354d5ae8e35c19255a4300"),
    }
    for name, expected in expected_runs.items():
        item = config.get("strict_run_bindings", {}).get(name, {})
        observed = (item.get("source_commit"), item.get("source_sha256"),
                    item.get("strict_binary_sha256"), item.get("log_sha256"))
        require(observed == expected, f"P2c {name} strict-run binding changed")
        source = git_blob(repository, item["source_commit"], item["source_path"])
        require_hash(source, item["source_sha256"], f"P2c {name} historical source")
        log = git_blob(repository, source_commit, item["log_path"])
        require_hash(log, item["log_sha256"], f"P2c {name} log")
    expected_evidence = {
        "root_jet_summary": {
            "path": "validation/rigorous/design/p2c_root_jet_summary_v1.json",
            "sha256": "13e5c345a8c762c707ae19455ca67510e587a97c526f718f175e59da2657d2fd"},
        "tail_composition_source": {
            "path": "validation/rigorous/design/p2c_tail_composition_scout.py",
            "sha256": "f52c42792347f4428cca7667bf09b62bc2a3b81e11f45872e8bd82f298a0ba68"},
        "tail_composition_output": {
            "path": "validation/rigorous/design/p2c_tail_composition_v1.json",
            "sha256": "0999f97a65fd5c58258a7aeec0ec820e272306a5e89acacafe09ea0183350eef"},
        "middle_summary": {
            "path": "validation/rigorous/design/p2c_middle_jet_summary_v1.json",
            "sha256": "2bd9a929603c2fa9a3a2e666bec05466dbba6cc0571a041d365eda7d27d45725"},
    }
    require(config.get("evidence_files") == expected_evidence,
            "P2c canonical evidence-file bindings changed")
    for name, item in config.get("evidence_files", {}).items():
        blob = git_blob(repository, source_commit, item["path"])
        require_hash(blob, item["sha256"], f"P2c evidence {name}")
    external = config.get("common_external_bindings", {})
    require(external == {
        "capd_commit": "731079217a9254ea2948d742df2b170895effe7f",
        "flagship_commit": "d54add098545063d5efe8f1d6f062d4cfc116a0d",
        "frozen_h10_header_sha256":
            "d617587ea1b9037c1c7575ccdde5029529ec5b736dee259baff9a2a162001e96"},
        "P2c canonical external bindings changed")
    dependency = load_json_bytes(
        git_blob(repository, source_commit, basis["dependency_lock"]["path"]),
        "dependency lock")
    flagship = load_json_bytes(
        git_blob(repository, source_commit, basis["flagship_import_lock"]["path"]),
        "flagship import lock")
    require(dependency.get("capd", {}).get("source_commit") ==
            external.get("capd_commit"), "P2c CAPD commit differs from dependency lock")
    require(flagship.get("commit") == external.get("flagship_commit") and
            flagship.get("files", {}).get(
                "validation/origin-algebraic-heteroclinic/unstable_graph_terms.hpp") ==
            external.get("frozen_h10_header_sha256"),
            "P2c flagship/H10 binding differs from import lock")
    compatibility = basis.get("historical_p2bk_source_compatibility", {})
    old_text = git_text(repository, compatibility["historical_commit"],
                        compatibility["path"])
    new_text = git_text(repository, compatibility["current_commit"],
                        compatibility["path"])
    old_extract = compatibility_extract(
        old_text, compatibility["start_marker"], compatibility["end_marker"])
    new_extract = compatibility_extract(
        new_text, compatibility["start_marker"], compatibility["end_marker"])
    require(old_extract == new_extract,
            "historical P2bK source interface changed before P2c")
    require_hash(old_extract, compatibility["common_extract_sha256"],
                 "historical P2bK compatible source extract")


def materialized_json(repository: Path, commit: str, path: str) -> dict[str, Any]:
    return load_json_bytes(git_blob(repository, commit, path), path)


def run_tail_audit(
        repository: Path, source_commit: str, config: dict[str, Any]
        ) -> tuple[dict[str, Any], dict[str, Any]]:
    evidence = config["evidence_files"]
    with tempfile.TemporaryDirectory(prefix="rfsn-p2c-tail-audit-") as temporary:
        root = Path(temporary)
        paths = {
            "script": root / "validation/rigorous/design/p2c_tail_composition_scout.py",
            "summary": root / "validation/rigorous/design/p2c_root_jet_summary_v1.json",
            "p2b": root / "validation/rigorous/results/vdp_bridge_v1_p2b_jets.json",
            "p2bk": root / "validation/rigorous/results/vdp_bridge_v1_p2b_kato.json",
        }
        sources = {
            "script": evidence["tail_composition_source"]["path"],
            "summary": evidence["root_jet_summary"]["path"],
            "p2b": config["selection_basis"]["p2b_certificate"]["path"],
            "p2bk": config["selection_basis"]["p2bk_certificate"]["path"],
        }
        for key, target in paths.items():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git_blob(repository, source_commit, sources[key]))
        environment = os.environ.copy()
        environment.update({
            "LC_ALL": "C.UTF-8", "PYTHONHASHSEED": "0",
            "PYTHONPYCACHEPREFIX": str(root / "pycache")})
        run = subprocess.run(
            [sys.executable, "-B", str(paths["script"]), str(paths["summary"])],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment,
            timeout=60)
    require(run.returncode == 0, "exact tail composition replay did not PASS")
    require(run.stderr == b"", "exact tail composition replay emitted stderr")
    canonical = git_blob(
        repository, source_commit, evidence["tail_composition_output"]["path"])
    require(run.stdout == canonical,
            "exact tail composition replay differs bytewise from the canonical output")
    output = load_json_bytes(run.stdout, "exact tail composition output")
    require(output.get("status") == "PASS" and
            all(output.get("gates", {}).values()),
            "exact tail composition gates do not all PASS")
    return output, {
        "status": "PASS", "method": "exact Fraction replay; no ODE integration",
        "exit_code": run.returncode,
        "stdout_sha256": sha256_bytes(run.stdout),
        "stderr_sha256": sha256_bytes(run.stderr),
    }


def weighted_audit(config: dict[str, Any], tail: dict[str, Any],
                   middle: dict[str, Any],
                   parsed_middle: dict[str, Any] | None = None) -> dict[str, Any]:
    acceptance = config["acceptance_contract"]
    tail_common = fraction_record(
        tail["tail_weight_one_fifth_constants"]
        ["original_parameters_coarse_25_625"]["common_C"], "tail common C")
    local_common = fraction_record(
        tail["covered_local_and_infinite_common_C"]
        ["original_parameters_coarse_25_625"], "local-and-tail common C")
    constants = middle["weighted_constants"]
    normalized = constants["global_normalized_theta"]
    original = constants["global_original_mu"]
    middle_normalized = constants["middle_normalized_theta"]
    middle_original = constants["middle_original_mu"]
    local_normalized = constants[
        "local_pre_source_and_infinite_normalized_theta"]
    local_original = constants[
        "local_pre_source_and_infinite_original_mu"]
    normalized_values = {
        key: fraction_record(normalized[key], f"global normalized {key}")
        for key in ("C0", "C1", "C2")}
    original_values = {
        key: fraction_record(original[key], f"global original {key}")
        for key in ("C0", "C1", "C2")}
    middle_normalized_values = {
        key: fraction_record(middle_normalized[key], f"middle normalized {key}")
        for key in ("C0", "C1", "C2")}
    middle_original_values = {
        key: fraction_record(middle_original[key], f"middle original {key}")
        for key in ("C0", "C1", "C2")}
    local_normalized_values = {
        key: fraction_record(local_normalized[key], f"local normalized {key}")
        for key in ("C0", "C1", "C2")}
    local_original_values = {
        key: fraction_record(local_original[key], f"local original {key}")
        for key in ("C0", "C1", "C2")}
    if parsed_middle is None:
        parsed_metrics = middle.get("global_maxima", {})
        metric_fractions = {
            "C0": Fraction.from_float(float.fromhex(
                parsed_metrics["normalized_state_C0_euclidean"]["upper"]
                ["binary64_hex"])),
            "C1": Fraction.from_float(float.fromhex(
                parsed_metrics["normalized_centered_xi_L1_hilbert_schmidt"]
                ["upper"]["binary64_hex"])),
            "C2": Fraction.from_float(float.fromhex(
                parsed_metrics["normalized_centered_xi_L2_hilbert_schmidt"]
                ["upper"]["binary64_hex"])),
        }
    else:
        parsed_metrics = parsed_middle["global_maxima"]
        metric_fractions = {
            "C0": Fraction.from_float(float(parsed_metrics[
                "normalized_state_C0_euclidean"])),
            "C1": Fraction.from_float(float(parsed_metrics[
                "normalized_centered_xi_L1_hilbert_schmidt"])),
            "C2": Fraction.from_float(float(parsed_metrics[
                "normalized_centered_xi_L2_hilbert_schmidt"])),
        }
    recomputed_middle_normalized = {
        key: acceptance["strict_exponential_upper"] * value
        for key, value in metric_fractions.items()}
    require(middle_normalized_values == recomputed_middle_normalized,
            "middle C0/C1/C2 constants do not equal 27 times parsed log maxima")
    require(middle_original_values == {
        "C0": recomputed_middle_normalized["C0"],
        "C1": 25 * recomputed_middle_normalized["C1"],
        "C2": 625 * recomputed_middle_normalized["C2"]},
        "middle original C0/C1/C2 conversion changed")
    require(normalized_values == {
        key: max(middle_normalized_values[key], local_normalized_values[key])
        for key in ("C0", "C1", "C2")},
        "global normalized C0/C1/C2 do not dominate both middle and tails")
    require(original_values == {
        key: max(middle_original_values[key], local_original_values[key])
        for key in ("C0", "C1", "C2")},
        "global original C0/C1/C2 do not dominate both middle and tails")
    normalized_c1 = normalized_values["C1"]
    normalized_c2 = normalized_values["C2"]
    original_c1 = original_values["C1"]
    original_c2 = original_values["C2"]
    require(ceiling(tail_common) == acceptance["tail_common_integer_original_mu"],
            "tail integer ceiling changed")
    require(ceiling(local_common) ==
            acceptance["local_pre_source_and_tail_common_integer_original_mu"],
            "local-and-tail integer ceiling changed")
    require(ceiling(normalized_c2) ==
            acceptance["global_common_integer_normalized_theta"],
            "normalized global integer ceiling changed")
    require(ceiling(original_c2) ==
            acceptance["global_common_integer_original_mu"],
            "original global integer ceiling changed")
    require(original_c1 == 25 * normalized_c1 and
            original_c2 == 625 * normalized_c2,
            "25/625 original-parameter conversion changed")
    require(original_values["C0"] == normalized_values["C0"],
            "order-zero original/normalized conversion changed")
    require(original_c2 == fraction_record(
        acceptance["global_original_mu_C2"], "frozen global C2"),
        "global original-parameter C2 fraction changed")
    require(original_c2 < acceptance["global_common_integer_original_mu"] and
            local_common < acceptance["global_common_integer_original_mu"] and
            all(value < acceptance["global_common_integer_original_mu"]
                for value in original_values.values()) and
            all(value < acceptance["global_common_integer_normalized_theta"]
                for value in normalized_values.values()),
            "global common integer does not strictly dominate all pieces")
    require(5**11 < acceptance["strict_exponential_upper"] * 4**11,
            "strict exp(11/5)<27 integer comparison failed")
    method = tail.get("method", {})
    tail_cut = fraction_record(method.get("tail_cut"), "tail cut")
    tail_weight = fraction_record(method.get("tail_weight"), "tail weight")
    require(tail_cut == acceptance["tail_cut_T_star"] and
            tail_weight == Fraction(
                int(acceptance["tail_weight_eta"]["numerator"]),
                int(acceptance["tail_weight_eta"]["denominator"])),
            "tail cutoff or weight differs from the frozen coverage contract")
    local_segment = tail.get("compact_local_pre_source_segment", {})
    covered = tail.get("covered_local_and_infinite_common_C", {})
    require(local_segment.get("domain") == LOCAL_PRE_SOURCE_DOMAIN and
            local_segment.get("formula") == LOCAL_PRE_SOURCE_FORMULA and
            covered.get("scope_boundary") == LOCAL_AND_TAIL_SCOPE,
            "local/tail domain decomposition changed")
    require(tail.get("tail_weight_one_fifth_constants", {}).get(
                "negative_and_positive_tails_use_same_constants") is True and
            local_segment.get("weight_one_fifth_compact_constants", {}).get(
                "negative_and_reflected_positive_segments_use_same_constants")
            is True,
            "reversible local/tail constant transfer changed")
    half_time_upper = Fraction.from_float(float.fromhex(summary_hex(
        middle, "continuous_hulls", "half_time", "upper", "binary64_hex")))
    xi_lower = Fraction.from_float(float.fromhex(summary_hex(
        middle, "continuous_hulls", "centered_tube_xi", "lower",
        "binary64_hex")))
    xi_upper = Fraction.from_float(float.fromhex(summary_hex(
        middle, "continuous_hulls", "centered_tube_xi", "upper",
        "binary64_hex")))
    tail_time_margin = fraction_record(
        tail.get("margins", {}).get("tail_cut_minus_one_minus_half_time_upper"),
        "tail/source seam margin")
    require(tail_time_margin == tail_cut - 1 - half_time_upper and
            tail_time_margin > 0,
            "tail/source seam is not strictly inside the cutoff")
    require(-tail_cut < xi_lower <= -half_time_upper and
            0 <= xi_upper < tail_cut,
            "parsed compact middle does not cover [-T_h,0] inside |xi|<T_star")
    if parsed_middle is not None:
        require(parsed_middle.get("coverage_seams") == {
            "every_slab_reaches_source": True,
            "every_slab_reaches_symmetry": True,
            "every_slab_strictly_inside_abs_xi_11": True,
        }, "per-slab compact-middle seam audit changed")
    require(middle.get("coverage") == MIDDLE_COVERAGE and
            acceptance["require_full_real_line_coverage"] is True,
            "full-real-line coverage contract changed")
    return {
        "status": "PASS", "T_star": 11,
        "eta": {"numerator": "1", "denominator": "5"},
        "strict_exponential_upper": 27,
        "tail_common_integer_original_mu": ceiling(tail_common),
        "local_pre_source_and_tail_common_integer_original_mu": ceiling(local_common),
        "global_common_integer_normalized_theta": ceiling(normalized_c2),
        "global_common_integer_original_mu": ceiling(original_c2),
        "global_original_mu_C2": acceptance["global_original_mu_C2"],
        "coverage": {
            "status": "PASS",
            "negative_tail": "xi<=-11",
            "local_pre_source": "-11<=xi<=-T_h",
            "compact_middle": "-T_h<=xi<=0",
            "tail_source_margin": {
                "numerator": str(tail_time_margin.numerator),
                "denominator": str(tail_time_margin.denominator),
            },
            "middle_centered_hull_binary64_hex": [
                summary_hex(middle, "continuous_hulls", "centered_tube_xi",
                            "lower", "binary64_hex"),
                summary_hex(middle, "continuous_hulls", "centered_tube_xi",
                            "upper", "binary64_hex"),
            ],
            "positive_half": MIDDLE_COVERAGE["positive_half"],
        },
    }


def source_bindings(repository: Path, source_commit: str) -> list[dict[str, str]]:
    return [{"path": path, "sha256": sha256_bytes(
        git_blob(repository, source_commit, path))} for path in sorted(SOURCE_PATHS)]


def obligation(identifier: str, predicate: str) -> dict[str, str]:
    return {"id": identifier, "predicate": predicate, "status": "PASS"}


def build_certificate(
        repository: Path, source_commit: str, created_at: str) -> dict[str, Any]:
    config_blob = git_blob(repository, source_commit, CONFIG_PATH)
    config = load_json_bytes(config_blob, CONFIG_PATH)
    validate_config(repository, source_commit, config)
    basis = config["selection_basis"]
    prerequisites = {
        "p2a": verify_historical_certificate(
            repository, source_commit, basis["p2a_certificate"]),
        "p2b": verify_historical_certificate(
            repository, source_commit, basis["p2b_certificate"]),
        "p2bk": verify_historical_certificate(
            repository, source_commit, basis["p2bk_certificate"]),
        "p2bk_source_compatibility": {
            "status": "PASS",
            "historical_commit": basis["historical_p2bk_source_compatibility"]
            ["historical_commit"],
            "current_commit": basis["historical_p2bk_source_compatibility"]
            ["current_commit"],
            "common_extract_sha256": basis[
                "historical_p2bk_source_compatibility"]["common_extract_sha256"],
        },
    }
    runs = config["strict_run_bindings"]
    log_text = {name: git_text(repository, source_commit, item["log_path"])
                for name, item in runs.items()}
    root_summary = materialized_json(
        repository, source_commit, config["evidence_files"]["root_jet_summary"]["path"])
    middle_summary = materialized_json(
        repository, source_commit, config["evidence_files"]["middle_summary"]["path"])
    branch = parse_branch(log_text["branch"])
    first_hit = parse_first_hit(log_text["first_hit"])
    root_jets = parse_root_jets(log_text["root_jets"], root_summary)
    compact_middle = parse_middle(log_text["compact_middle"], middle_summary)
    for name, summary in (("root_jets", root_summary),
                          ("compact_middle", middle_summary)):
        provenance = summary.get("provenance", {})
        binding = runs[name]
        require(provenance.get("repository_commit") == binding["source_commit"] and
                provenance.get("source_path") == binding["source_path"] and
                provenance.get("source_sha256") == binding["source_sha256"] and
                provenance.get("strict_binary_sha256") ==
                binding["strict_binary_sha256"] and
                provenance.get("fixed_numeric_order_log_concatenation_sha256") ==
                binding["log_sha256"] and
                provenance.get("capd_commit") ==
                config["common_external_bindings"]["capd_commit"] and
                provenance.get("flagship_commit") ==
                config["common_external_bindings"]["flagship_commit"] and
                provenance.get("frozen_h10_header_sha256") ==
                config["common_external_bindings"]["frozen_h10_header_sha256"],
                f"{name} summary provenance differs from strict-run binding")
    require(middle_summary.get("provenance", {}).get("root_jet_summary_sha256") ==
            config["evidence_files"]["root_jet_summary"]["sha256"] and
            middle_summary.get("provenance", {}).get(
                "tail_composition_source_sha256") ==
            config["evidence_files"]["tail_composition_source"]["sha256"] and
            middle_summary.get("provenance", {}).get("tail_local_output_sha256") ==
            config["evidence_files"]["tail_composition_output"]["sha256"],
            "compact-middle downstream evidence provenance changed")
    tail, tail_execution = run_tail_audit(repository, source_commit, config)
    global_weight = weighted_audit(
        config, tail, middle_summary, compact_middle)
    raw_evidence = {
        "schema_version": "rfsn-vdp-p2c-local-strict-evidence/1",
        "status": "PASS",
        "evidence_class": "archived local strict logs plus exact algebraic replay",
        "full_grid_replayed_during_certificate_build": False,
        "branch_cover": branch,
        "first_hit_cover": first_hit,
        "root_jets": root_jets,
        "tail_exact_audit": tail_execution,
        "compact_middle": compact_middle,
        "global_weighted_bound": global_weight,
        "historical_execution_bindings": runs,
    }
    predicates = {
        "ENV.SOURCE_BINDING": "Every local source, evidence artifact, and historical run source is hash-bound at an explicit Git commit.",
        "ENV.P2C_HISTORICAL_RUN_RECORDS": "All four archived P2c logs are bound to historical source commits, source hashes, the recorded CAPD commit, and recorded strict-binary hashes; executable bytes and build-environment replay are not asserted.",
        "BRIDGE.FROZEN": "The exact rational comparison bridge is the common gap-free domain of every P2c grid run.",
        "P2.P2A_PREREQUISITE": "The historical P2a certificate is schema-valid at its source commit and supplies the pre-source true-graph exclusion.",
        "P2.P2B_JETS_PREREQUISITE": "The historical P2b certificate is schema-valid at its source commit and supplies the weighted graph and half-orbit jets.",
        "P2.P2BK_PREREQUISITE": "The historical P2bK certificate is schema-valid at its source commit, its true-source atoms pass, and its source interface is byte-compatible with the current P2c theorem snapshot.",
        "P2.HOMOCLINIC_CONFIG_FROZEN": "The post-design retrospective P2c evidence contract was frozen before this local certificate was assembled.",
        "V2.HOM.BRANCH": "A gap-free 32x128x4 cover, all 44,416 internal faces, and the frozen core anchor identify one selected branch unique in the finite lifted multiple-shooting tube.",
        "V2.HOM.FIRST_HIT": "The P2a pre-source exclusion, continuous strict sign tubes, and final U-positive flow box prove the selected event is the first nonzero symmetry hit.",
        "V2.HOM.TRANSVERSE": "Every selected endpoint is nonzero and has strictly positive shooting determinant and event transversality margins.",
        "V2.HOM.TAILS": "Exact composition of certified source/root jets with P2b half-orbits gives explicit weight-one-fifth C2 bounds on both infinite tails.",
        "V2.HOM.MIDDLE_C2": "Continuous CAPD C2 enclosures, event-time centering, local pre-source composition, and reversibility give the full-real-line global weighted bound.",
        "V2.HOMOCLINIC": "All five P2c mathematical atoms pass, yielding the selected C2 homoclinic branch, first hit, transversality, and explicit global weighted parameter-two-jet bound.",
    }
    obligation_ids = [
        "ENV.SOURCE_BINDING", "ENV.P2C_HISTORICAL_RUN_RECORDS", "BRIDGE.FROZEN",
        "P2.P2A_PREREQUISITE", "P2.P2B_JETS_PREREQUISITE",
        "P2.P2BK_PREREQUISITE", "P2.HOMOCLINIC_CONFIG_FROZEN",
        *ATOM_IDS, "V2.HOMOCLINIC"]
    box_path = "validation/rigorous/config/vdp_box_v1.json"
    bridge_path = "validation/rigorous/config/vdp_bridge_v1.json"
    box_blob = git_blob(repository, source_commit, box_path)
    bridge_blob = git_blob(repository, source_commit, bridge_path)
    box = load_json_bytes(box_blob, box_path)
    bridge = load_json_bytes(bridge_blob, bridge_path)
    return {
        "schema_version": "rfsn-vdp-p2-homoclinic-certificate/1",
        "certificate_id": f"vdp-p2c-homoclinic-{source_commit[:12]}",
        "scope": SCOPE,
        "created_at": created_at,
        "source_revision": {
            "repository": "h-lu/rfsn-ii-positive-parameter-pde",
            "commit": source_commit, "repository_dirty": False,
            "working_tree_observation": "BEFORE_REPORT_WRITE",
            "report_output_excluded_from_observation": True,
        },
        "source_bindings": source_bindings(repository, source_commit),
        "configuration": {
            "path": CONFIG_PATH, "sha256": sha256_bytes(config_blob),
            "configuration_id": config["configuration_id"],
            "status": config["status"],
        },
        "parameter_box": {
            "path": box_path, "sha256": sha256_bytes(box_blob),
            "box_id": box["box_id"], "variables": box["variables"]},
        "continuation_bridge": {
            "path": bridge_path, "sha256": sha256_bytes(bridge_blob),
            "bridge_id": bridge["bridge_id"], "variables": bridge["variables"]},
        "prerequisites": prerequisites,
        "toolchain": {
            "certificate_mode": "archived-strict-summary-no-full-grid-replay",
            "capd_commit": config["common_external_bindings"]["capd_commit"],
            "historical_strict_execution_record_binding_status": "PASS",
            "full_grid_rebuilt_during_certificate_build": False,
            "tail_exact_replay": tail_execution,
        },
        "raw_evidence": raw_evidence,
        "obligations": [obligation(identifier, predicates[identifier])
                        for identifier in obligation_ids],
        "integrity_status": "PASS", "mathematical_status": "PASS",
        "independent_replay": {
            "required_distinct_machines": 2,
            "observed_distinct_machines": 1,
            "status": "PENDING_REQUIRED"},
        "final_status": "INCONCLUSIVE", "claim_bearing": False,
        "release_eligible": False,
        "nonclaims": NONCLAIMS_PREFIX + config["nonclaims"],
    }


def schema_errors(certificate: dict[str, Any]) -> list[str]:
    schema = json.loads((HERE / "p2_homoclinic_certificate.schema.json").read_text())
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker())
    return [
        f"P2c schema {'.'.join(str(part) for part in error.absolute_path) or '<root>'}: {error.message}"
        for error in sorted(validator.iter_errors(certificate),
                            key=lambda item: tuple(str(part) for part in item.path))]


def semantic_errors(certificate: dict[str, Any],
                    repository: Path = REPOSITORY) -> list[str]:
    try:
        source_revision = certificate.get("source_revision")
        require(isinstance(source_revision, dict),
                "P2c certificate source_revision is not an object")
        source_commit = source_revision.get("commit")
        created_at = certificate.get("created_at")
        require(isinstance(source_commit, str), "P2c certificate lacks source commit")
        require(isinstance(created_at, str), "P2c certificate lacks creation time")
        try:
            parsed_time = datetime.fromisoformat(created_at)
        except ValueError as error:
            raise EvidenceError("P2c certificate creation time is not ISO 8601") from error
        require(parsed_time.tzinfo is not None,
                "P2c certificate creation time lacks a UTC offset")
        frozen_schema = load_json_bytes(
            git_blob(repository, source_commit, CERTIFICATE_SCHEMA_PATH),
            "snapshot P2c certificate schema")
        try:
            jsonschema.validate(certificate, frozen_schema,
                                format_checker=jsonschema.FormatChecker())
        except jsonschema.ValidationError as error:
            raise EvidenceError(
                f"snapshot P2c certificate schema: {error.message}") from error
        expected = build_certificate(repository, source_commit, created_at)
    except (EvidenceError, OSError, subprocess.SubprocessError,
            json.JSONDecodeError, KeyError, TypeError, AttributeError,
            IndexError) as error:
        return [f"P2c semantic audit could not close: {error}"]
    if certificate == expected:
        return []
    errors: list[str] = []
    keys = sorted(set(certificate) | set(expected))
    for key in keys:
        if certificate.get(key) != expected.get(key):
            errors.append(f"P2c certificate field {key} differs from reconstructed evidence")
    return errors or ["P2c certificate differs from reconstructed evidence"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="assemble a certificate from clean HEAD")
    build.add_argument("output", type=Path)
    build.add_argument("--repository", type=Path, default=REPOSITORY)
    check = subparsers.add_parser("check", help="check an existing certificate")
    check.add_argument("certificate", type=Path)
    check.add_argument("--repository", type=Path, default=REPOSITORY)
    arguments = parser.parse_args()
    repository = arguments.repository.resolve()
    try:
        if arguments.command == "build":
            status = subprocess.run(
                ["git", "-C", str(repository), "status", "--porcelain"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            require(status.stdout == b"", "certificate build requires a clean working tree")
            source_commit = subprocess.check_output(
                ["git", "-C", str(repository), "rev-parse", "HEAD"],
                text=True).strip()
            certificate = build_certificate(
                repository, source_commit, datetime.now(timezone.utc).isoformat())
            arguments.output.parent.mkdir(parents=True, exist_ok=True)
            arguments.output.write_text(
                json.dumps(certificate, indent=2, sort_keys=True) + "\n",
                encoding="utf-8")
            print(f"PASS: wrote local non-claim-bearing P2c certificate to {arguments.output}")
            return 0
        certificate = json.loads(arguments.certificate.read_text(encoding="utf-8"))
        errors = schema_errors(certificate) + semantic_errors(certificate, repository)
        if errors:
            for error in errors:
                print(f"INVALID: {error}", file=sys.stderr)
            return 1
        print("VALID: P2c local mathematical PASS; final_status=INCONCLUSIVE; claim_bearing=false")
        return 0
    except (EvidenceError, OSError, subprocess.SubprocessError,
            json.JSONDecodeError, KeyError, TypeError, AttributeError,
            IndexError) as error:
        print(f"INVALID: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
