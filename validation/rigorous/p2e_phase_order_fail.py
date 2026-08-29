#!/usr/bin/env python3
"""Certify the fail-fast phase-order obstruction for vdp-positive-box-v1."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
DEFAULT_CONFIG = HERE / "config" / "vdp_p2e_phase_order_fail_v1.json"
DEFAULT_RESULT = HERE / "results" / "vdp_box_v1_p2e_phase_order_fail.json"


class AuditError(ValueError):
    """A frozen input or strict comparison does not satisfy the contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path} is not a JSON object")
    return value


def parse_interval_text(value: str, label: str) -> tuple[Decimal, Decimal]:
    match = re.fullmatch(r"\[\s*([^,]+),\s*([^\]]+)\]", value)
    require(match is not None, f"malformed {label}: {value!r}")
    lower, upper = Decimal(match.group(1)), Decimal(match.group(2))
    require(lower <= upper, f"reversed {label}")
    return lower, upper


def parse_log(value: str) -> dict[str, Any]:
    require(value.endswith("\n"), "strict log must end with one newline")
    require(value.count("mode mu-grid-root-jets\n") == 1,
            "strict log has the wrong mode count")
    indices = re.search(r"^indices (\d+) (\d+) (\d+)$", value, re.MULTILINE)
    require(indices is not None, "strict log lacks grid indices")
    cell = re.search(
        r"^parameter_cell (\[[^\n]+?\]) (\[[^\n]+?\]) (\[[^\n]+?\])$",
        value, re.MULTILINE)
    require(cell is not None, "strict log lacks the parameter cell")
    phase = re.search(
        r"^phase_hull (\[[^\n]+?\]) half_time_hull", value, re.MULTILINE)
    require(phase is not None, "strict log lacks the phase hull")
    require(value.rstrip().endswith("PASS mu-grid true-source root C2 jets"),
            "strict selected-root computation is not PASS")
    return {
        "indices": [int(indices.group(i)) for i in range(1, 4)],
        "printed_parameter_cell": [cell.group(i) for i in range(1, 4)],
        "phase_hull": parse_interval_text(phase.group(1), "homoclinic phase"),
    }


def git_blob(commit: str, path: str) -> bytes:
    require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None,
            "source commit is not a full Git hash")
    run = subprocess.run(
        ["git", "-C", str(REPOSITORY), "show", f"{commit}:{path}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    require(run.returncode == 0,
            f"cannot materialize {commit}:{path}: "
            f"{run.stderr.decode(errors='replace').strip()}")
    return run.stdout


def resolve_json_path(value: Any, path: list[str]) -> Any:
    current = value
    for key in path:
        require(isinstance(current, dict) and key in current,
                f"missing JSON path component {key!r}")
        current = current[key]
    return current


def bound_json(path_spec: dict[str, Any], label: str) -> dict[str, Any]:
    path = REPOSITORY / path_spec["path"]
    value = path.read_bytes()
    require(sha256_bytes(value) == path_spec["sha256"],
            f"{label} hash mismatch")
    parsed = json.loads(value)
    require(isinstance(parsed, dict), f"{label} is not a JSON object")
    return parsed


def extract(text: str, start: str, end: str, label: str) -> str:
    require(text.count(start) == 1 and text.count(end) == 1,
            f"{label} markers are not unique")
    first = text.index(start)
    last = text.index(end, first) + len(end)
    return text[first:last]


def rational_pair(value: list[str], label: str) -> tuple[Fraction, Fraction]:
    require(isinstance(value, list) and len(value) == 2,
            f"{label} is not a rational pair")
    lower, upper = Fraction(value[0]), Fraction(value[1])
    require(lower <= upper, f"{label} is reversed")
    return lower, upper


def frozen_box_pair(value: dict[str, Any], label: str) -> tuple[Fraction, Fraction]:
    result = []
    for endpoint in ("lower", "upper"):
        item = value[endpoint]
        result.append(Fraction(int(item["numerator"]), int(item["denominator"])))
    require(result[0] <= result[1], f"{label} frozen box is reversed")
    return result[0], result[1]


def audit(config_path: Path = DEFAULT_CONFIG,
          strict_binary: Path | None = None) -> dict[str, Any]:
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    require(isinstance(config, dict), "phase-order config is not a JSON object")
    require(config["schema_version"] ==
            "rfsn-vdp-p2e-phase-order-fail-config/1",
            "wrong phase-order config schema")
    require(config["scope"] == "V2_P2E_PHASE_ORDER_FAIL_FAST",
            "wrong phase-order scope")
    require(config["box_id"] == "vdp-positive-box-v1",
            "wrong frozen box id")
    require(config["atom_id"] == "V2.ATLAS.PHASE_GAP_AH",
            "wrong phase-order atom")
    require(config["theorem_clause"] ==
            "van-der-pol/CENTRAL_CONTINUATION.md, Theorem V2(5)",
            "wrong theorem clause")
    require(config["required_predicate"] ==
            "phi_h - phi_a > 0.052407 in the common transported Kato source-phase lift",
            "wrong theorem predicate")
    require(config["required_gap_lower"] == "0.052407",
            "wrong theorem gap")

    theorem_binding = config["theorem_binding"]
    theorem_path = REPOSITORY / theorem_binding["path"]
    theorem_bytes = theorem_path.read_bytes()
    require(sha256_bytes(theorem_bytes) == theorem_binding["sha256"],
            "V2 theorem hash mismatch")
    theorem_text = theorem_bytes.decode("utf-8")
    convention = extract(
        theorem_text, theorem_binding["phase_convention_start"],
        theorem_binding["phase_convention_end"], "phase convention")
    order = extract(
        theorem_text, theorem_binding["phase_order_start"],
        theorem_binding["phase_order_end"], "phase order")
    require(sha256_bytes(convention.encode()) ==
            theorem_binding["phase_convention_excerpt_sha256"],
            "phase-convention theorem extract mismatch")
    require(sha256_bytes(order.encode()) ==
            theorem_binding["phase_order_excerpt_sha256"],
            "phase-order theorem extract mismatch")
    require("transported label \\(\\phi\\) is declared to be the common source phase" in
            convention, "theorem does not fix the transported Kato phase")
    require("0.052407" in order and "cyclic order is unchanged" in order,
            "theorem extract does not contain the required phase-order gate")

    target_box = bound_json(config["target_box_binding"], "target box")
    require(target_box.get("box_id") == config["box_id"] and
            target_box.get("status") == "FROZEN_PREVALIDATION" and
            target_box.get("selected_before_interval_validation") is True,
            "target box is not the frozen v1 target")
    p2c_config = bound_json(config["p2c_config_binding"], "P2c config")
    kato_config = bound_json(config["kato_config_binding"], "P2bK config")
    require(kato_config["source_circle_contract"]["phase_lift_formula"] ==
            config["kato_config_binding"]["required_embedding_formula"],
            "P2bK phase embedding formula changed")
    expected_interface = {
        "homoclinic_phase": "absolute transported Kato source label phi returned by the P2c selected-root solve",
        "algebraic_phase": "the frozen algebraic-directed anchor label, continued with the same transported Kato label on S_mu",
        "coordinate_embedding": "phi_algebraic=phi+chi(c) embeds the Kato label in the algebraic graph coordinates; it is not the phase quantity compared here",
        "common_lift": "TRANSPORTED_KATO_SOURCE_PHASE",
    }
    require(config["phase_interface"] == expected_interface,
            "phase-interface semantics changed")

    root_evidence = config["strict_root_evidence"]
    source = git_blob(root_evidence["source_commit"],
                      root_evidence["source_path"])
    require(sha256_bytes(source) == root_evidence["source_sha256"],
            "strict root source hash mismatch")

    h10_path = REPOSITORY / root_evidence["frozen_h10_path"]
    require(sha256_bytes(h10_path.read_bytes()) ==
            root_evidence["frozen_h10_sha256"],
            "frozen H10 header hash mismatch")

    log_path = REPOSITORY / root_evidence["stdout_path"]
    log_bytes = log_path.read_bytes()
    require(sha256_bytes(log_bytes) == root_evidence["stdout_sha256"],
            "strict root stdout hash mismatch")
    parsed = parse_log(log_bytes.decode("utf-8"))
    require(parsed["indices"] == config["counterexample_cell"]["grid_indices"],
            "strict root grid cell changed")
    require(parsed["printed_parameter_cell"] ==
            root_evidence["expected_printed_parameter_cell"],
            "strict printed parameter cell changed")
    require(root_evidence["argv"] == [
        "mu-grid-root-jets",
        config["counterexample_cell"]["shooting_radius_factor"],
        *(str(item) for item in parsed["indices"]),
    ], "strict argv does not select the declared cell")
    require(root_evidence["required_terminal_line"] ==
            "PASS mu-grid true-source root C2 jets",
            "strict terminal gate changed")

    grid = p2c_config["parameter_grid"]
    axes = grid["ordered_axes"]
    require(axes == ["r", "a2", "epsilon"],
            "P2c grid axes changed")
    require(grid["shooting_radius_factor"] ==
            int(config["counterexample_cell"]["shooting_radius_factor"]),
            "P2c shooting radius changed")
    declared_cells = []
    for axis, subdivisions, index, printed in zip(
            axes, grid["subdivisions"], parsed["indices"],
            parsed["printed_parameter_cell"], strict=True):
        bridge_lower, bridge_upper = rational_pair(
            grid["bridge"][axis], f"P2c {axis} bridge")
        require(0 <= index < subdivisions, f"{axis} grid index is out of range")
        width = (bridge_upper - bridge_lower) / subdivisions
        reconstructed = (bridge_lower + index * width,
                         bridge_lower + (index + 1) * width)
        declared = rational_pair(
            config["counterexample_cell"][axis], f"declared {axis} cell")
        require(reconstructed == declared,
                f"declared {axis} cell does not follow from the P2c grid index")
        printed_decimal = parse_interval_text(printed, f"printed {axis} cell")
        printed_fraction = tuple(Fraction(item) for item in printed_decimal)
        require(printed_fraction[0] <= declared[0] and
                declared[1] <= printed_fraction[1],
                f"printed {axis} enclosure misses its exact rational cell")
        box_interval = frozen_box_pair(target_box["variables"][axis], axis)
        require(box_interval[0] <= declared[0] and
                declared[1] <= box_interval[1],
                f"counterexample {axis} cell is outside vdp-positive-box-v1")
        declared_cells.append([str(declared[0]), str(declared[1])])

    compact_binding = p2c_config["strict_run_bindings"]["compact_middle"]
    require(compact_binding["source_commit"] == root_evidence["source_commit"] and
            compact_binding["source_path"] == root_evidence["source_path"] and
            compact_binding["source_sha256"] == root_evidence["source_sha256"] and
            compact_binding["strict_binary_sha256"] ==
            root_evidence["strict_binary_sha256"],
            "strict root executable is not bound by the P2c config")
    expected_h = tuple(Decimal(item) for item in
                       root_evidence["expected_phase_hull"])
    require(parsed["phase_hull"] == expected_h,
            "strict homoclinic phase hull changed")

    if strict_binary is not None:
        binary_bytes = strict_binary.read_bytes()
        require(sha256_bytes(binary_bytes) ==
                root_evidence["strict_binary_sha256"],
                "strict binary hash mismatch")
        run = subprocess.run(
            [str(strict_binary), *root_evidence["argv"]],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        require(run.returncode == 0,
                f"strict replay failed: {run.stderr.decode(errors='replace')}")
        require(run.stdout == log_bytes,
                "strict replay stdout differs from the frozen log")

    prerequisite = config["p2c_prerequisite"]
    prerequisite_path = REPOSITORY / prerequisite["path"]
    prerequisite_bytes = prerequisite_path.read_bytes()
    require(sha256_bytes(prerequisite_bytes) == prerequisite["sha256"],
            "P2c prerequisite hash mismatch")
    prerequisite_json = json.loads(prerequisite_bytes)
    require(prerequisite_json.get("mathematical_status") ==
            prerequisite["required_mathematical_status"],
            "P2c prerequisite is not a mathematical PASS")
    atoms = {item.get("id"): item.get("status")
             for item in prerequisite_json.get("obligations", [])}
    require(atoms.get(prerequisite["required_atom"]) == "PASS",
            "selected homoclinic branch prerequisite is not PASS")

    anchor = config["algebraic_anchor"]
    anchor_path = REPOSITORY / anchor["path"]
    anchor_bytes = anchor_path.read_bytes()
    require(sha256_bytes(anchor_bytes) == anchor["sha256"],
            "algebraic anchor certificate hash mismatch")
    anchor_json = json.loads(anchor_bytes)
    anchor_text = resolve_json_path(anchor_json, anchor["json_path"])
    algebraic = parse_interval_text(anchor_text, "algebraic phase")
    expected_a = tuple(Decimal(item) for item in anchor["expected_phase_hull"])
    require(algebraic == expected_a, "algebraic phase hull changed")
    homoclinic = parsed["phase_hull"]
    wrong_order_margin = algebraic[0] - homoclinic[1]
    required_gap = Decimal(config["required_gap_lower"])
    maximum_requested_gap = homoclinic[1] - algebraic[0]
    shortfall = required_gap - maximum_requested_gap
    require(wrong_order_margin > 0,
            "the alleged counterexample does not strictly reverse phase order")
    require(maximum_requested_gap < required_gap,
            "the required positive phase gap has not failed")

    interval = lambda value: [str(value[0]), str(value[1])]
    return {
        "schema_version": "rfsn-vdp-p2e-phase-order-fail-certificate/1",
        "scope": config["scope"],
        "box_id": config["box_id"],
        "status": "FAIL",
        "integrity_status": "PASS",
        "mathematical_status": "FAIL",
        "claim_bearing": False,
        "atom": {
            "id": config["atom_id"],
            "status": "FAIL",
            "required_predicate": config["required_predicate"],
            "homoclinic_phase_hull": interval(homoclinic),
            "algebraic_phase_hull": interval(algebraic),
            "strict_reversed_order_margin_lower": str(wrong_order_margin),
            "maximum_phi_h_minus_phi_a": str(maximum_requested_gap),
            "required_gap_lower": str(required_gap),
            "required_gap_shortfall_lower": str(shortfall),
        },
        "counterexample_cell": config["counterexample_cell"],
        "evidence": {
            "configuration_sha256": sha256_bytes(config_bytes),
            "strict_source_commit": root_evidence["source_commit"],
            "strict_source_sha256": root_evidence["source_sha256"],
            "strict_binary_sha256": root_evidence["strict_binary_sha256"],
            "strict_stdout_sha256": root_evidence["stdout_sha256"],
            "strict_stdout_terminal_status": "PASS",
            "p2c_prerequisite_sha256": prerequisite["sha256"],
            "algebraic_anchor_sha256": anchor["sha256"],
            "phase_interface": config["phase_interface"],
            "theorem_sha256": theorem_binding["sha256"],
            "target_box_sha256": config["target_box_binding"]["sha256"],
            "p2c_config_sha256": config["p2c_config_binding"]["sha256"],
            "kato_config_sha256": config["kato_config_binding"]["sha256"],
        },
        "failure_propagation": config["failure_propagation"],
        "nonclaims": config["nonclaims"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--strict-binary", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check-result", type=Path)
    args = parser.parse_args()
    result = audit(args.config, args.strict_binary)
    if args.check_result is not None:
        require(load_json(args.check_result) == result,
                "committed phase-order result is stale")
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
