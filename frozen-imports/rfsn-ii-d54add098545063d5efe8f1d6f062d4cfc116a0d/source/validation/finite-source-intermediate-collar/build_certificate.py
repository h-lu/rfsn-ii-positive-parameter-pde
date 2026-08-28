#!/usr/bin/env python3
"""Audit full-cover outputs and write the small, scoped certificate summary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def interval(text):
    left, right = text[1:-1].split(",")
    return float(left), float(right)


def union(records, key):
    parsed = [interval(record[key]) for record in records]
    return [min(value[0] for value in parsed), max(value[1] for value in parsed)]


def sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    manifest_path = HERE / "cover_boxes.jsonl"
    results_path = HERE / "cover_results.jsonl"
    bridges_path = HERE / "cover_bridge_results.jsonl"
    summary_path = HERE / "cover_validation_summary.json"
    manifest = [json.loads(line) for line in manifest_path.read_text().splitlines()]
    results = [json.loads(line) for line in results_path.read_text().splitlines()]
    bridges = [json.loads(line) for line in bridges_path.read_text().splitlines()]
    summary = json.loads(summary_path.read_text())
    if len(manifest) != 6316 or len(results) != 6316 or len(bridges) != 6315:
        raise RuntimeError("unexpected cover cardinality")
    if any(result["returncode"] for result in results):
        raise RuntimeError("an individual box failed")
    if any(not result["tangent_certified"] for result in results):
        raise RuntimeError("a tangent box failed")
    if any(
        bridge["returncode"] or not bridge["adjacent_bridge_certified"]
        for bridge in bridges
    ):
        raise RuntimeError("an adjacency bridge failed")

    unresolved = [
        result["index"]
        for result in results
        if not result["energy_derivative_strictly_negative"]
    ]
    if unresolved != [0, 1]:
        raise RuntimeError(f"unexpected energy-sign exceptions: {unresolved}")
    v_rows = [row for row in manifest if row["chart"] == "v"]
    u_rows = [row for row in manifest if row["chart"] == "u"]
    certificate = {
        "status": "PASS-FIRST-STAGE-INNER-ARC-BOXES-AND-TRUE-ADJACENCY",
        "claim_boundary": (
            "Uniform physical-target BVP cover from the numerical outer-fold "
            "event box to the numerical R≈0.025 intermediate source collar. "
            "This collar is not the local fundamental annulus; endpoint and "
            "spiral-extension identifications are separate gates."
        ),
        "dimensions": {
            "segments": 36,
            "state_dimension_with_time": 5,
            "unknowns": 185,
            "equations": 185,
            "continuity_rows": 180,
            "source_rows": ["P0=0", "Q0=0", "V0=v or U0=u"],
            "terminal_rows": ["e=0.0575", "p-h7-eta=0"],
        },
        "cover": {
            "box_count": len(results),
            "adjacent_bridge_count": len(bridges),
            "v_chart_box_count": len(v_rows),
            "u_chart_box_count": len(u_rows),
            "v_parameter_range": [v_rows[-1]["parameter_centre"], v_rows[0]["parameter_centre"]],
            "u_parameter_range": [u_rows[-1]["parameter_centre"], u_rows[0]["parameter_centre"]],
            "minimum_v_parameter_overlap": min(
                row["overlap_with_previous"]
                for row in v_rows
                if row["overlap_with_previous"] is not None
            ),
            "minimum_u_parameter_overlap": min(
                row["overlap_with_previous"]
                for row in u_rows
                if row["overlap_with_previous"] is not None
            ),
            "chart_switch_indices": [4918, 4919],
            "chart_switch_source_centre": {
                "U": manifest[4918]["source_U"],
                "V": manifest[4918]["source_V"],
            },
            "outer_source_centre": {
                "U": manifest[0]["source_U"],
                "V": manifest[0]["source_V"],
            },
            "inner_source_centre": {
                "U": manifest[-1]["source_U"],
                "V": manifest[-1]["source_V"],
                "radius": manifest[-1]["source_radius"],
            },
        },
        "uniform_bounds": {
            "maximum_krawczyk_ratio": summary["maximum_krawczyk_ratio"],
            "maximum_weighted_contraction_ratio": summary["maximum_contraction_ratio"],
            "maximum_tangent_krawczyk_ratio": summary["maximum_tangent_krawczyk_ratio"],
            "terminal_physical_a_union": union(results, "terminal_X_physical_a"),
            "terminal_physical_b_union": union(results, "terminal_X_physical_b"),
            "terminal_graph_energy_union_for_abs_zeta_le_2": union(
                results, "terminal_X_graph_energy_abs_zeta_le_2"
            ),
            "all_first_event": all(result["first_event"] for result in results),
            "all_tangent_certified": all(result["tangent_certified"] for result in results),
            "strict_negative_energy_derivative_index_range": [2, 6315],
            "energy_sign_unresolved_indices": unresolved,
        },
        "physical_target_contract": {
            "value_budget": "|eta| <= 2 e^8 (|zeta|<=2)",
            "row_budget": "||D eta||_2 <= 1e-5; evaluated by a component cube superset",
            "corridor": "0<e<.06, |a|<.0065, |b|<.01, |E|<.012",
        },
        "required_gates_not_proved_here": {
            "outer_fixed_time_fold_to_event_chart": "NOT-PROVED",
            "intermediate_collar_to_local_annulus_spiral_extension": "NOT-COVERED",
            "local_annulus_to_saddle_focus_sector_identification": "NOT-PROVED",
            "outer_algebraic_source_c0_to_first_fold": "NOT-COVERED",
            "exact_algebraic_c0_Jost_endpoint_identification": "NOT-PROVED",
        },
        "replay_pins": {
            "capd_commit": "731079217a9254ea2948d742df2b170895effe7f",
            "capd_pkg_config_version": "2.5.1",
            "interval_backend": "FILIB",
            "compiler": "g++ (Ubuntu 15.2.0-16ubuntu1) 15.2.0",
            "python": "3.14.4",
            "numpy": "2.5.2",
            "scipy": "1.18.0",
            "sympy": "1.14.0",
            "libcapd_sha256": "316b2c480f1ce36b293602da9978eb43560646991a4a906d72ee893b3c557119",
            "libfilib_sha256": "ce5cdf8f22d4a6737461774211053a3df360178194e431e4f7ad2b2ada5caa7e",
        },
        "source_sha256": {
            name: sha256(HERE / name)
            for name in [
                "source_cover_probe.cpp",
                "numerical_bvp.py",
                "generate_full_cover.py",
                "validate_full_cover.py",
                "build_certificate.py",
            ]
        },
        "promoted_target_header_sha256": {
            name: sha256(HERE.parent / "future-target-fold" / name)
            for name in [
                "tail_graph_generated.hpp",
                "weighted_tail_generated.hpp",
            ]
        },
        "bulk_replay_hashes": {
            "cover_boxes.jsonl": sha256(manifest_path),
            "cover_results.jsonl": sha256(results_path),
            "cover_bridge_results.jsonl": sha256(bridges_path),
            "cover_seeds.txt": sha256(HERE / "cover_seeds.txt"),
        },
    }
    output = HERE / "certificate.json"
    output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    print(json.dumps(certificate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
