#!/usr/bin/env python3
"""Audit the prospectively frozen Issue #7 v2 box and derived bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any

import jsonschema


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
DEFAULT_BOX = HERE / "config" / "vdp_box_v2.json"
DEFAULT_BRIDGE = HERE / "config" / "vdp_bridge_v2.json"
SCHEMA = HERE / "parameter_box_v2.schema.json"


class AuditError(ValueError):
    """A frozen input or exact relationship violates the v2 contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path} is not a JSON object")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repository_path(relative: str) -> Path:
    path = (REPOSITORY / relative).resolve()
    require(path.is_relative_to(REPOSITORY.resolve()),
            f"path escapes repository: {relative}")
    return path


def exact_interval(value: dict[str, Any], label: str) -> tuple[Fraction, Fraction]:
    result: list[Fraction] = []
    for endpoint in ("lower", "upper"):
        item = value[endpoint]
        result.append(Fraction(int(item["numerator"]), int(item["denominator"])))
    require(result[0] <= result[1], f"{label} interval is reversed")
    return result[0], result[1]


def string_interval(value: list[str], label: str) -> tuple[Fraction, Fraction]:
    require(isinstance(value, list) and len(value) == 2,
            f"{label} is not an exact string interval")
    result = Fraction(value[0]), Fraction(value[1])
    require(result[0] <= result[1], f"{label} interval is reversed")
    return result


def bound_json(binding: dict[str, Any], label: str) -> dict[str, Any]:
    path = repository_path(binding["path"])
    require(sha256_file(path) == binding["sha256"], f"{label} hash mismatch")
    return load_json(path)


def audit(box_path: Path = DEFAULT_BOX,
          bridge_path: Path = DEFAULT_BRIDGE) -> dict[str, Any]:
    box = load_json(box_path)
    schema = load_json(SCHEMA)
    try:
        jsonschema.validate(
            box, schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as error:
        raise AuditError(f"v2 box schema: {error.message}") from error

    basis = box["selection_basis"]
    design_commit = basis["design_basis_commit"]
    exists = subprocess.run(
        ["git", "-C", str(REPOSITORY), "cat-file", "-e",
         f"{design_commit}^{{commit}}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    require(exists.returncode == 0, "design-basis commit is unavailable")
    ancestor = subprocess.run(
        ["git", "-C", str(REPOSITORY), "merge-base", "--is-ancestor",
         design_commit, "HEAD"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    require(ancestor.returncode == 0,
            "design-basis commit is not an ancestor of the current source")

    predecessor = basis["failed_predecessor"]
    old_box = bound_json({
        "path": predecessor["box_path"],
        "sha256": predecessor["box_sha256"],
    }, "v1 box")
    old_failure = bound_json({
        "path": predecessor["failure_path"],
        "sha256": predecessor["failure_sha256"],
    }, "v1 failure")
    require(old_box.get("box_id") == predecessor["box_id"],
            "v1 box identifier mismatch")
    require(old_failure.get("box_id") == predecessor["box_id"] and
            old_failure.get("mathematical_status") == "FAIL" and
            old_failure.get("status") == predecessor["required_status"],
            "predecessor is not the frozen mathematical FAIL")

    expected_theory = [
        ("van-der-pol/CENTRAL_CORE_IMPORT.md",
         "037abc2fc9e54ebd8ec645489a5d62ba8e3cd06013360dfad82351e6eb442a56"),
        ("van-der-pol/CENTRAL_CONTINUATION.md",
         "e02d067595f89ea7f19dfac81a7eba84ea0bdda17e4bbe12f569e776ba775026"),
    ]
    observed_theory = [(item["path"], item["sha256"])
                       for item in basis["analytic_basis"]]
    require(observed_theory == expected_theory,
            "analytic selection basis changed")
    for path, digest in expected_theory:
        require(sha256_file(repository_path(path)) == digest,
                f"analytic basis hash mismatch: {path}")

    containing_binding = basis["containing_bridge_binding"]
    old_bridge = bound_json(containing_binding, "v1 containing bridge")
    require(old_bridge.get("bridge_id") == containing_binding["bridge_id"],
            "v1 containing-bridge identifier mismatch")

    variables = box["variables"]
    old_variables = old_box["variables"]
    bridge_variables = old_bridge["variables"]
    v2 = {name: exact_interval(variables[name], f"v2 {name}")
          for name in ("r", "a2", "epsilon")}
    v1 = {name: exact_interval(old_variables[name], f"v1 {name}")
          for name in ("r", "a2", "epsilon")}
    outer = {name: exact_interval(bridge_variables[name], f"v1 bridge {name}")
             for name in ("r", "a2", "epsilon")}
    require(v2["r"] == (v1["r"][0] / 4, v1["r"][1] / 4),
            "v2 r interval is not the exact r/4 image of v1")
    for name in ("a2", "epsilon"):
        require(v2[name] == v1[name] == outer[name],
                f"{name} transverse interval changed")
    expected_conventions = {
        "d": "r^4",
        "delta": "r^2",
        "a": "1+sqrt(epsilon)*r^3*a2",
        "c": "2*r*a2+sqrt(epsilon)*r^4*a2^2",
        "alpha": "sqrt(2+c)/2",
        "beta": "sqrt(2-c)/2",
    }
    require(box["derived_conventions"] == expected_conventions and
            old_box["derived_conventions"] == expected_conventions,
            "v2 derived conventions differ from the frozen v1 formulas")
    require(v2["r"][1] < v1["r"][0],
            "v2 and v1 positive r intervals are not disjoint as declared")
    require(outer["r"][0] < v2["r"][0] and
            v2["r"][1] < outer["r"][1],
            "v2 is not a strict subset of the v1 comparison bridge")

    expected_gaps = {
        "algebraic_to_homoclinic": {
            "r0_lower": "0.104814", "required_v2_lower": "0.052407"},
        "algebraic_to_pole": {
            "r0_lower": "0.32648", "required_v2_lower": "0.16324"},
        "homoclinic_to_pole": {
            "r0_lower": "0.22167", "required_v2_lower": "0.110835"},
    }
    require(basis["phase_gap_targets"] == expected_gaps,
            "frozen phase-gap target dictionary changed")
    require(box["inheritance_policy"] == {
        "p1_v1_positive_box":
            "NOT_INHERITED_BECAUSE_V2_IS_OUTSIDE_V1_POSITIVE_R_INTERVAL",
        "p2a_through_p2d_v1_bridge":
            "RESTRICTION_ALLOWED_ONLY_AFTER_EXACT_DOMAIN_AND_HASH_CHECKS",
        "p2e_and_later": "NO_TARGET_SPECIFIC_RESULT_IS_INHERITED",
        "forbidden": "A v1 FAIL, sampled candidate, or design log may not be relabelled as a v2 PASS.",
    }, "v2 inheritance policy changed")
    require(box["mutation_policy"] ==
            "Never overwrite, shrink, translate, or selectively trim this box after any v2 target-specific outward-rounded output is inspected.",
            "v2 mutation policy changed")
    require(box["stop_policy"] ==
            "A strict v2 mathematical FAIL remains FAIL and stops its dependent run.  A run with an integrity or enclosure failure is INCONCLUSIVE and may use only refinement already frozen for that same target; neither outcome authorizes a v3 box under the current programme.",
            "v2 stop policy changed")
    require(box["nonclaims"] == [
        "Freezing v2 is not a validation result.",
        "The historical P2c design log is disclosed target-selection information, not a v2 P2e certificate.",
        "No v1 failure is erased or weakened.",
        "The box was not selected for temporal stability, Turing selection, or canard behavior.",
    ], "v2 nonclaim boundary changed")

    grid_binding = basis["grid_alignment"]
    p2c_path = repository_path(grid_binding["p2c_config_path"])
    require(sha256_file(p2c_path) == grid_binding["p2c_config_sha256"],
            "P2c grid configuration hash mismatch")
    p2c = load_json(p2c_path)
    grid = p2c["parameter_grid"]
    require(grid["ordered_axes"] == ["r", "a2", "epsilon"],
            "P2c grid axis order changed")
    r_bridge = string_interval(grid["bridge"]["r"], "P2c r bridge")
    subdivisions = grid["subdivisions"][0]
    width = (r_bridge[1] - r_bridge[0]) / subdivisions
    cells = []
    for index in grid_binding["original_r_grid_indices"]:
        cells.append((r_bridge[0] + index * width,
                      r_bridge[0] + (index + 1) * width))
    declared_cells = [string_interval(item, "declared v2 r cell")
                      for item in grid_binding["exact_r_grid_cells"]]
    require(cells == declared_cells, "v2 r cells do not match the P2c grid")
    require(cells[0][0] == v2["r"][0] and cells[-1][1] == v2["r"][1] and
            all(left[1] == right[0]
                for left, right in zip(cells, cells[1:])),
            "declared v2 r cells are not a gap-free cover of v2")

    disclosure = basis["preexisting_nonclaim_evidence_disclosed"]
    log_path = repository_path(disclosure["path"])
    require(sha256_file(log_path) == disclosure["sha256"],
            "disclosed exploratory log hash mismatch")
    log = log_path.read_text(encoding="utf-8")
    for index in grid_binding["original_r_grid_indices"]:
        require(f"r_index {index} " in log,
                f"disclosed log lacks r slab {index}")
    require("phase_hull " in log and "PASS mu-grid true-source root C2 jet slab" in log,
            "disclosed log does not contain the declared phase-hull evidence")

    bridge = load_json(bridge_path)
    expected_bridge_keys = {
        "schema_version", "bridge_id", "status",
        "selected_before_first_v2_target_specific_outward_rounded_run",
        "selection_date", "selection_basis", "variables", "anchor_face",
        "target_relation", "inheritance_policy", "mutation_policy",
        "stop_policy", "nonclaims",
    }
    require(set(bridge) == expected_bridge_keys,
            "v2 bridge top-level contract changed")
    require(bridge["schema_version"] ==
            "rfsn-vdp-rigorous-continuation-bridge/2" and
            bridge["bridge_id"] == "vdp-core-to-positive-bridge-v2" and
            bridge["status"] == "FROZEN_PRE_P2E_V2_VALIDATION" and
            bridge["selected_before_first_v2_target_specific_outward_rounded_run"]
            is True,
            "v2 bridge identity or freeze status changed")
    require(bridge["selection_date"] == box["selection_date"],
            "v2 box and bridge freeze dates differ")
    bridge_basis = bridge["selection_basis"]
    require(bridge_basis["design_basis_commit"] == design_commit and
            bridge_basis["classification"] ==
            "DERIVED_TARGET_BRIDGE_WITH_NO_NEW_MATHEMATICAL_VERDICT" and
            bridge_basis["construction_rule"] ==
            "Take the exact rectangular hull of the complete r=0 anchor face and vdp-positive-box-v2, retaining the v2 a2 and epsilon intervals.",
            "v2 bridge derivation contract changed")
    target_binding = bridge_basis["target_box"]
    require(target_binding == {
        "path": "validation/rigorous/config/vdp_box_v2.json",
        "sha256": sha256_file(box_path),
        "box_id": "vdp-positive-box-v2",
    }, "v2 bridge target-box binding mismatch")
    require(bridge_basis["containing_bridge"] == {
        "path": containing_binding["path"],
        "sha256": containing_binding["sha256"],
        "bridge_id": containing_binding["bridge_id"],
    }, "v2 bridge does not bind the same v1 containing bridge")
    derived = {name: exact_interval(bridge["variables"][name],
                                    f"v2 bridge {name}")
               for name in ("r", "a2", "epsilon")}
    require(derived["r"] == (Fraction(0), v2["r"][1]),
            "v2 bridge is not the exact r=0-to-target hull")
    for name in ("a2", "epsilon"):
        require(derived[name] == v2[name],
                f"v2 bridge changed the {name} target interval")
    require(outer["r"][0] == derived["r"][0] and
            derived["r"][1] < outer["r"][1],
            "v2 bridge is not a strict subset of v1 bridge")
    require(bridge["anchor_face"] == {
        "equation": "r=0",
        "role": "frozen-selected-core-branch",
        "dummy_parameters": ["a2", "epsilon"],
    }, "v2 bridge anchor face changed")
    require(bridge["target_relation"] == {
        "positive_box_is_subset": True,
        "shared_upper_r_face": "r=1/50",
        "bridge_is_strict_subset_of_v1_bridge": True,
        "transverse_ranges_equal_v1_bridge": True,
    }, "v2 bridge target relation changed")
    require(bridge["inheritance_policy"] ==
            "A mathematical statement proved uniformly on vdp-core-to-positive-bridge-v1 may be restricted to this bridge only after its source, theorem, domain, and certificate hashes are checked.  This derived bridge creates no PASS by itself.",
            "v2 bridge inheritance policy changed")
    require(bridge["mutation_policy"] ==
            "Never shrink or overwrite this bridge after any v2 target-specific outward-rounded output is inspected.",
            "v2 bridge mutation policy changed")
    require(bridge["stop_policy"] ==
            "The bridge follows the v2 box stop rule; no failed or inconclusive v2 result authorizes a narrower bridge under the current programme.",
            "v2 bridge stop policy changed")
    require(bridge["nonclaims"] == [
        "Freezing the v2 bridge does not prove continuation or an event atlas.",
        "The bridge is not an additional parameter-box attempt.",
        "No v1 failure or non-claim-bearing prerequisite is promoted by restriction.",
        "No temporal-stability, Turing-selection, or canard conclusion follows.",
    ], "v2 bridge nonclaim boundary changed")

    return {
        "schema_version": "rfsn-vdp-box-v2-freeze-audit/1",
        "status": "PASS",
        "mathematical_status": "NOT_RUN",
        "box_id": box["box_id"],
        "box_sha256": sha256_file(box_path),
        "bridge_id": bridge["bridge_id"],
        "bridge_sha256": sha256_file(bridge_path),
        "design_basis_commit": design_commit,
        "selection_classification": basis["classification"],
        "redesign_budget_consumed": True,
        "claim_bearing": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--box", type=Path, default=DEFAULT_BOX)
    parser.add_argument("--bridge", type=Path, default=DEFAULT_BRIDGE)
    arguments = parser.parse_args()
    result = audit(arguments.box, arguments.bridge)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
