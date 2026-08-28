#!/usr/bin/env python3
"""Audit bulk spiral-cover products and emit the small source certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def interval(text: str) -> tuple[float, float]:
    left, right = text[1:-1].split(",")
    return float(left), float(right)


def interval_union(records: list[dict], key: str) -> list[float]:
    values = [interval(record[key]) for record in records]
    return [min(value[0] for value in values), max(value[1] for value in values)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-centres-dir", type=Path, required=True)
    parser.add_argument("--centres-dir", type=Path, required=True)
    parser.add_argument("--validation-dir", type=Path, required=True)
    parser.add_argument("--refinement-plan", type=Path, required=True)
    parser.add_argument("--coarse-manifest", type=Path, required=True)
    parser.add_argument("--coarse-seeds", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest_path = args.centres_dir / "spiral_extension_boxes.jsonl"
    seeds_path = args.centres_dir / "spiral_extension_seeds.txt"
    centres_summary_path = (
        args.centres_dir / "spiral_extension_centres_summary.json"
    )
    results_path = args.validation_dir / "spiral_extension_results.jsonl"
    bridges_path = (
        args.validation_dir / "spiral_extension_bridge_results.jsonl"
    )
    summary_path = (
        args.validation_dir / "spiral_extension_validation_summary.json"
    )
    manifest = [json.loads(line) for line in manifest_path.read_text().splitlines()]
    results = [json.loads(line) for line in results_path.read_text().splitlines()]
    bridges = [json.loads(line) for line in bridges_path.read_text().splitlines()]
    centres_summary = json.loads(centres_summary_path.read_text())
    summary = json.loads(summary_path.read_text())
    refinement_plan = json.loads(args.refinement_plan.read_text())
    base_manifest_path = args.base_centres_dir / "spiral_extension_boxes.jsonl"
    base_seeds_path = args.base_centres_dir / "spiral_extension_seeds.txt"
    base_summary_path = (
        args.base_centres_dir / "spiral_extension_centres_summary.json"
    )

    if summary["status"] != "PASS-COMPLETE-FINITE-COLLAR-TO-FIXED-ANNULUS-SEAM":
        raise RuntimeError("spiral extension summary is not PASS")
    expected_count = int(centres_summary["box_count"])
    if not (
        len(manifest) == len(results) == expected_count
        and len(bridges) == expected_count - 1
    ):
        raise RuntimeError("unexpected spiral cover cardinality")
    if [row["index"] for row in manifest] != list(range(expected_count)):
        raise RuntimeError("spiral cover indices are not contiguous")
    if any(
        bridge["current_index"] != index
        or bridge["next_index"] != index + 1
        for index, bridge in enumerate(bridges)
    ):
        raise RuntimeError("bridge results do not enumerate every adjacency")
    if any(result["returncode"] for result in results):
        raise RuntimeError("an individual spiral box failed")
    if any(not result["tangent_certified"] for result in results):
        raise RuntimeError("a tangent inclusion failed")
    if any(not result["first_event"] for result in results):
        raise RuntimeError("a first-event check failed")
    if any(
        bridge["returncode"] or not bridge["adjacent_bridge_certified"]
        for bridge in bridges
    ):
        raise RuntimeError("an adjacent common-root bridge failed")
    if not summary["coarse_endpoint_containment"]["status"].startswith("PASS"):
        raise RuntimeError("coarse-to-fine endpoint containment failed")
    if not summary["fixed_radial_seam_containment"]["status"].startswith("PASS"):
        raise RuntimeError("fixed radial seam containment failed")
    if not (
        summary["maximum_krawczyk_ratio"] < 1.0
        and summary["maximum_contraction_ratio"] < 1.0
        and summary["maximum_tangent_krawczyk_ratio"] < 1.0
    ):
        raise RuntimeError("a reported Krawczyk bound is not strict")
    if not all(
        summary[key] > 0.0
        for key in [
            "minimum_bridge_current_containment_margin",
            "minimum_bridge_next_containment_margin",
            "minimum_bridge_next_parameter_margin",
        ]
    ):
        raise RuntimeError("a reported bridge containment margin is not strict")
    if sha256(args.refinement_plan) != centres_summary["refinement_plan_sha256"]:
        raise RuntimeError("centres summary does not bind the refinement plan")
    if sha256(base_manifest_path) != refinement_plan["base_manifest_sha256"]:
        raise RuntimeError("base spiral manifest does not match refinement plan")
    if sha256(base_seeds_path) != refinement_plan["base_seeds_sha256"]:
        raise RuntimeError("base spiral seeds do not match refinement plan")
    if sha256(base_summary_path) != refinement_plan["base_summary_sha256"]:
        raise RuntimeError("base spiral summary does not match refinement plan")

    first_stage = json.loads((HERE / "certificate.json").read_text())
    expected_manifest = first_stage["bulk_replay_hashes"]["cover_boxes.jsonl"]
    expected_seeds = first_stage["bulk_replay_hashes"]["cover_seeds.txt"]
    if sha256(args.coarse_manifest) != expected_manifest:
        raise RuntimeError("coarse manifest does not match promoted first stage")
    if sha256(args.coarse_seeds) != expected_seeds:
        raise RuntimeError("coarse seeds do not match promoted first stage")

    groups = centres_summary["groups"]
    chart_switch_pairs = [
        [manifest[index]["index"], manifest[index + 1]["index"]]
        for index in range(len(manifest) - 1)
        if manifest[index]["chart"] != manifest[index + 1]["chart"]
    ]
    certificate = {
        "status": "PASS-FINITE-COLLAR-TO-FIXED-ANNULUS-SEAM",
        "created_at": "2026-08-24",
        "claim_boundary": (
            "Uniform physical-target event-BVP cover from the promoted "
            "R≈0.025 intermediate collar to the promoted fixed radial local "
            "seam R=2.4e-4.  This closes only the inward finite-to-local seam; "
            "the outer fold and algebraic-source sides remain separate gates."
        ),
        "dimensions": {
            "segments": 108,
            "state_dimension_with_time": 5,
            "unknowns": 545,
            "equations": 545,
            "continuity_rows": 540,
            "source_rows": [
                "P0=0",
                "Q0=0",
                "U0=u, V0=v, or sqrt(U0^2+V0^2)=R",
            ],
            "terminal_rows": ["e=0.0575", "p-h7-eta=0"],
        },
        "cover": {
            "box_count": len(results),
            "adjacent_common_root_bridge_count": len(bridges),
            "reverse_bridge_count": summary["reverse_bridge_count"],
            "groups": groups,
            "chart_switch_pairs": chart_switch_pairs,
            "base_box_count": centres_summary["base_box_count"],
            "inserted_box_count": centres_summary["inserted_box_count"],
            "shrunk_base_box_count": centres_summary["shrunk_base_box_count"],
            "outer_endpoint": centres_summary["first_source"],
            "fixed_radial_endpoint": centres_summary["last_source"],
            "former_isolated_radius_0p000304_role": (
                "strictly bridged interior chart-switch row, not an endpoint "
                "or substitute for the chain to R=2.4e-4"
            ),
        },
        "refinement": {
            "plan_sha256": sha256(args.refinement_plan),
            "failed_base_box_count": len(
                refinement_plan["strict_base_failure_indices"]
            ),
            "margin_refinement_base_box_count": len(
                refinement_plan["margin_refinement_indices"]
            ),
            "width_factor": refinement_plan["failed_width_factor"],
            "minimum_parameter_overlap_fraction": refinement_plan[
                "minimum_overlap_fraction"
            ],
            "selection_rule": refinement_plan["selection_rule"],
        },
        "uniform_bounds": {
            "maximum_krawczyk_ratio": summary["maximum_krawczyk_ratio"],
            "maximum_contraction_ratio": summary["maximum_contraction_ratio"],
            "maximum_tangent_krawczyk_ratio": summary[
                "maximum_tangent_krawczyk_ratio"
            ],
            "minimum_bridge_current_containment_margin": summary[
                "minimum_bridge_current_containment_margin"
            ],
            "minimum_bridge_next_containment_margin": summary[
                "minimum_bridge_next_containment_margin"
            ],
            "minimum_bridge_next_parameter_margin": summary[
                "minimum_bridge_next_parameter_margin"
            ],
            "all_first_event": summary["all_first_event"],
            "terminal_physical_a_union": interval_union(
                results, "terminal_X_physical_a"
            ),
            "terminal_physical_b_union": interval_union(
                results, "terminal_X_physical_b"
            ),
            "terminal_graph_energy_union_for_abs_zeta_le_2": interval_union(
                results, "terminal_X_graph_energy_abs_zeta_le_2"
            ),
        },
        "endpoint_identifications": {
            "promoted_36_to_108_endpoint": summary[
                "coarse_endpoint_containment"
            ],
            "event_root_source_to_fixed_radial_seam": summary[
                "fixed_radial_seam_containment"
            ],
            "local_selected_arm_identity": (
                "The fixed radial package identifies its seam root with the "
                "unique local selected arm through the common exit-target chart."
            ),
        },
        "physical_target_contract": {
            "value_budget": "|eta| <= 2 e^8 (|zeta|<=2)",
            "row_budget": "||D eta||_2 <= 1e-5; component-cube superset",
            "corridor": "0<e<.06, |a|<.0065, |b|<.01, |E|<.012",
        },
        "remaining_gates_not_proved_here": {
            "outer_fixed_time_fold_to_event_chart": "NOT-PROVED-HERE",
            "outer_algebraic_source_c0_to_first_fold": "NOT-PROVED-HERE",
            "exact_algebraic_c0_Jost_endpoint_identification": "NOT-PROVED-HERE",
        },
        "replay_pins": first_stage["replay_pins"],
        "source_sha256": {
            name: sha256(HERE / name)
            for name in [
                "spiral_source_cover_probe.cpp",
                "generate_spiral_extension_cover.py",
                "refine_spiral_extension_cover.py",
                "validate_spiral_extension_cover.py",
                "build_spiral_extension_certificate.py",
                "run_spiral_extension_validation.sh",
                "generate_full_cover.py",
                "numerical_bvp.py",
            ]
        },
        "dependency_sha256": {
            "promoted_first_stage_certificate.json": sha256(HERE / "certificate.json"),
            "promoted_fundamental_annulus_certificate.json": sha256(
                HERE.parent / "fundamental-annulus-overlap" / "certificate.json"
            ),
            "fixed_radial_source_centres.hpp": sha256(
                HERE.parent
                / "fundamental-annulus-overlap"
                / "fixed_radial_source_centres.hpp"
            ),
            "tail_graph_generated.hpp": sha256(
                HERE.parent / "future-target-fold" / "tail_graph_generated.hpp"
            ),
            "weighted_tail_generated.hpp": sha256(
                HERE.parent / "future-target-fold" / "weighted_tail_generated.hpp"
            ),
        },
        "bulk_replay_sha256": {
            "spiral_extension_boxes.jsonl": sha256(manifest_path),
            "spiral_extension_seeds.txt": sha256(seeds_path),
            "spiral_extension_centres_summary.json": sha256(centres_summary_path),
            "spiral_extension_results.jsonl": sha256(results_path),
            "spiral_extension_bridge_results.jsonl": sha256(bridges_path),
            "base_spiral_extension_boxes.jsonl": sha256(base_manifest_path),
            "base_spiral_extension_seeds.txt": sha256(base_seeds_path),
            "base_spiral_extension_centres_summary.json": sha256(
                base_summary_path
            ),
            "promoted_first_stage_boxes.jsonl": sha256(args.coarse_manifest),
            "promoted_first_stage_seeds.txt": sha256(args.coarse_seeds),
        },
    }
    args.output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print(json.dumps(certificate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
