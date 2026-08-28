#!/usr/bin/env python3
"""Audit clean replay products and emit the deterministic small certificate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ARCHIVED_PAPER = (
    HERE.parent.parent
    / "archive"
    / "research-history"
    / "papers"
    / "paper-a"
)
FUTURE = HERE.parent / "future-target-fold"
FINITE = HERE.parent / "finite-source-intermediate-collar"

EXPECTED_TOOLCHAIN = {
    "status": "PASS-PINNED-CAPD-FILIB-PREFLIGHT",
    "python_version": "3.14.4",
    "numpy_version": "2.5.2",
    "scipy_version": "1.18.0",
    "gmpy2_version": "2.2.2",
    "mpfr_version": "MPFR 4.2.1",
    "cxx_driver": "g++",
    "cxx_version": "15.2.0",
    "capd_source_version": "6.1.0",
    "capd_source_commit": "731079217a9254ea2948d742df2b170895effe7f",
    "capd_config_modversion": "6.1.0",
    "pkgconf_frontend_version": "2.5.1",
    "libcapd_sha256": (
        "316b2c480f1ce36b293602da9978eb43560646991a4a906d72ee893b3c557119"
    ),
    "interval_backend": "FILIB",
    "libfilib_sha256": (
        "ce5cdf8f22d4a6737461774211053a3df360178194e431e4f7ad2b2ada5caa7e"
    ),
    "rounding_math_enabled": True,
    "links_capd": True,
    "links_filib": True,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def check_cover(
    name: str,
    manifest: list[dict],
    results: list[dict],
    bridges: list[dict],
    summary: dict,
) -> None:
    if not len(manifest) == len(results) == summary["box_count"]:
        raise RuntimeError(f"{name} box cardinality mismatch")
    if not len(bridges) == len(manifest) - 1 == summary[
        "adjacent_bridge_count"
    ]:
        raise RuntimeError(f"{name} bridge cardinality mismatch")
    if [row["index"] for row in manifest] != list(range(len(manifest))):
        raise RuntimeError(f"{name} manifest indices are not contiguous")
    if [row["index"] for row in results] != list(range(len(results))):
        raise RuntimeError(f"{name} result indices are not contiguous")
    if any(row["returncode"] for row in results):
        raise RuntimeError(f"{name} contains a failed box")
    if any(
        row["returncode"] or not row["adjacent_bridge_certified"]
        for row in bridges
    ):
        raise RuntimeError(f"{name} contains a failed common-root bridge")
    if summary["status"] != "PASS-ALL-REQUESTED-BOXES-AND-TRUE-ADJACENCY":
        raise RuntimeError(f"{name} summary is not PASS")
    for key in (
        "maximum_krawczyk_ratio",
        "maximum_contraction_ratio",
        "maximum_tangent_krawczyk_ratio",
    ):
        if not summary[key]["value"] < 1.0:
            raise RuntimeError(f"{name} non-strict Krawczyk bound: {key}")
    for key in (
        "minimum_bridge_current_margin",
        "minimum_bridge_next_margin",
        "minimum_bridge_parameter_margin",
    ):
        if not summary[key]["value"] > 0.0:
            raise RuntimeError(f"{name} non-strict bridge margin: {key}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-dir", type=Path, required=True)
    parser.add_argument("--tail-dir", type=Path, required=True)
    parser.add_argument("--validation-dir", type=Path, required=True)
    parser.add_argument("--toolchain-json", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    main_manifest_path = arguments.main_dir / "cover_boxes.jsonl"
    main_seeds_path = arguments.main_dir / "cover_seeds.txt"
    main_centres_summary_path = arguments.main_dir / "cover_summary.json"
    tail_manifest_path = arguments.tail_dir / "cover_boxes.jsonl"
    tail_seeds_path = arguments.tail_dir / "cover_seeds.txt"
    tail_centres_summary_path = arguments.tail_dir / "cover_summary.json"
    main_results_path = arguments.validation_dir / "main_results.jsonl"
    main_bridges_path = arguments.validation_dir / "main_bridges.jsonl"
    main_summary_path = arguments.validation_dir / "main_summary.json"
    tail_results_path = arguments.validation_dir / "tail_results.jsonl"
    tail_bridges_path = arguments.validation_dir / "tail_bridges.jsonl"
    tail_summary_path = arguments.validation_dir / "tail_summary.json"
    containment_path = arguments.validation_dir / "cap_containment.jsonl"
    closure_path = arguments.validation_dir / "fold_closure.json"
    jost_path = arguments.validation_dir / "jost.json"

    main_manifest = load_jsonl(main_manifest_path)
    main_results = load_jsonl(main_results_path)
    main_bridges = load_jsonl(main_bridges_path)
    main_summary = load(main_summary_path)
    tail_manifest = load_jsonl(tail_manifest_path)
    tail_results = load_jsonl(tail_results_path)
    tail_bridges = load_jsonl(tail_bridges_path)
    tail_summary = load(tail_summary_path)
    containments = load_jsonl(containment_path)
    closure = load(closure_path)
    jost = load(jost_path)
    toolchain = load(arguments.toolchain_json)

    for key, expected in EXPECTED_TOOLCHAIN.items():
        if toolchain.get(key) != expected:
            raise RuntimeError(
                f"toolchain certificate mismatch for {key}: "
                f"{toolchain.get(key)!r} != {expected!r}"
            )

    check_cover(
        "main", main_manifest, main_results, main_bridges, main_summary
    )
    check_cover(
        "tail", tail_manifest, tail_results, tail_bridges, tail_summary
    )
    if len(main_manifest) != 17345 or len(tail_manifest) != 2002:
        raise RuntimeError("unexpected final cover cardinality")
    if closure["status"] != "PASS-FIRST-FOLD-CLOSURE":
        raise RuntimeError("fold closure summary is not PASS")
    if len(containments) != closure["cap_family_box_count"]:
        raise RuntimeError("cap containment cardinality mismatch")
    if any(row["returncode"] for row in containments):
        raise RuntimeError("a family-to-cap containment failed")
    if jost["status"] != "PASS-DIRECTED-MPFR-K0":
        raise RuntimeError("directed MPFR Jost audit is not PASS")
    if not main_results[0]["exact_c0_state_contained"]:
        raise RuntimeError("exact algebraic c0 state is not contained")
    if not main_results[0]["exact_Jost_slope_contained"]:
        raise RuntimeError("exact Jost tangent is not contained")
    if not main_results[0]["exact_algebraic_target_within_C0_budget"]:
        raise RuntimeError("exact algebraic terminal misses target budget")
    cap = closure["mixed_cap"]
    if not (
        cap["existing_fold_full_state_contained"]
        and cap["existing_fold_in_fixed_family_full_state"]
        and cap["krawczyk_ratio"] < 1.0
        and cap["contraction_ratio"] < 1.0
        and cap["minimum_containment_margin"] > 0.0
    ):
        raise RuntimeError("augmented cap/fold identification is not strict")

    source_files = [
        "README.md",
        "fixed_source_cover_probe.cpp",
        "mixed_fold_cap_probe.cpp",
        "generate_cover.py",
        "validate_cover.py",
        "validate_fold_closure.py",
        "verify_jost_constant.py",
        "build_certificate.py",
        "replay.py",
    ]
    dependency_files = {
        "future-target-fold/certificate.json": FUTURE / "certificate.json",
        "future-target-fold/fold_interval_probe.cpp": FUTURE
        / "fold_interval_probe.cpp",
        "future-target-fold/fold_centres_generated.hpp": FUTURE
        / "fold_centres_generated.hpp",
        "future-target-fold/tail_graph_generated.hpp": FUTURE
        / "tail_graph_generated.hpp",
        "future-target-fold/weighted_tail_generated.hpp": FUTURE
        / "weighted_tail_generated.hpp",
        "finite-source-intermediate-collar/numerical_bvp.py": FINITE
        / "numerical_bvp.py",
        "archive/research-history/papers/paper-a/LIMITING_JOST_THEORY.md": ARCHIVED_PAPER
        / "LIMITING_JOST_THEORY.md",
        "archive/research-history/papers/paper-a/UNIVERSAL_CORE_FINITE_TO_LOCAL_SEAM.md": ARCHIVED_PAPER
        / "UNIVERSAL_CORE_FINITE_TO_LOCAL_SEAM.md",
    }

    certificate = {
        "status": "PASS-EXACT-ALGEBRAIC-SOURCE-TO-FIRST-OUTER-FOLD",
        "created_at": "2026-08-24",
        "toolchain": toolchain,
        "claim_boundary": (
            "One selected C2 arc of the declared finite backward saturation "
            "W_a intersect Fix(R), from the exact algebraic source "
            "c0=(U,P,V,Q)=(0,0,1/6,0) to its first source-energy fold. "
            "No assertion outside the declared flow tube, no classification "
            "of other Fix(R) branches, and no origin-unstable incidence claim."
        ),
        "equations": {
            "raw": ["U'=P", "P'=-U^2-V", "V'=Q", "Q'=U"],
            "energy": "Q^2-P^2-(2/3)U^3-2UV",
            "source_section": "P=Q=0",
        },
        "fixed_time_formulation": {
            "physical_time": 15.0,
            "segments": 30,
            "base_unknowns": 124,
            "augmented_fold_unknowns": 248,
            "raw_nodes": [0, 3],
            "raw_to_compact_switch_node": 4,
            "switch_time": 2.0,
            "compact_nodes": [4, 30],
            "terminal_contract": {
                "value": "|eta| <= 2 e^8",
                "first_derivatives_componentwise": 1e-5,
                "second_derivatives_componentwise": 1e-3,
                "slope_subdivision": "none; whole declared cube",
            },
        },
        "exact_c0_endpoint": {
            "state_contained": True,
            "minimum_state_margin": main_results[0][
                "exact_c0_minimum_state_margin"
            ],
            "algebraic_target_residual": main_results[0][
                "exact_algebraic_target_residual"
            ],
            "k0_interval": main_results[0]["rigorous_k0"],
            "Jost_dV_dU_interval": main_results[0]["exact_Jost_dV_dU"],
            "analytic_identification": (
                "The validated tail graph has tangent span{T,Z,s}; finite "
                "variational pullback gives T_c0 W_a, whose intersection "
                "with P=Q=0 is span Z(0), so dV/dU=-2k0. See README Lemma."
            ),
            "mpfr_precision_bits": jost["precision_bits"],
        },
        "main_cover": {
            "box_count": len(main_results),
            "adjacent_common_root_bridge_count": len(main_bridges),
            "source_U_range": load(main_centres_summary_path)[
                "source_u_range"
            ],
            "fold_U_interval": load(main_centres_summary_path)[
                "fold_u_interval"
            ],
            "maximum_krawczyk_ratio": main_summary[
                "maximum_krawczyk_ratio"
            ],
            "maximum_contraction_ratio": main_summary[
                "maximum_contraction_ratio"
            ],
            "maximum_tangent_krawczyk_ratio": main_summary[
                "maximum_tangent_krawczyk_ratio"
            ],
            "minimum_bridge_current_margin": main_summary[
                "minimum_bridge_current_margin"
            ],
            "minimum_bridge_next_margin": main_summary[
                "minimum_bridge_next_margin"
            ],
            "minimum_bridge_parameter_margin": main_summary[
                "minimum_bridge_parameter_margin"
            ],
            "all_first_e_0p06_event": all(
                row["first_e_0.06_event"] for row in main_results
            ),
        },
        "fine_sign_tail": {
            "box_count": len(tail_results),
            "adjacent_common_root_bridge_count": len(tail_bridges),
            "negative_sign_box_count": closure["negative_sign_box_count"],
            "negative_sign_parameter_end": closure[
                "negative_sign_parameter_end"
            ],
            "maximum_negative_energy_derivative_upper": closure[
                "maximum_negative_energy_derivative_upper"
            ],
            "maximum_krawczyk_ratio": tail_summary[
                "maximum_krawczyk_ratio"
            ],
            "maximum_tangent_krawczyk_ratio": tail_summary[
                "maximum_tangent_krawczyk_ratio"
            ],
        },
        "three_full_state_identifications": {
            "main_cover_to_fine_tail": closure[
                "main_cover_to_sign_tail_identification"
            ],
            "fine_family_to_augmented_cap": {
                **closure["family_to_augmented_cap_identification"],
                "parameter_start": closure["cap_family_parameter_start"],
                "sign_overlap": closure["sign_to_cap_overlap"],
                "minimum_full_state_margin": closure[
                    "minimum_family_cap_full_state_margin"
                ],
            },
            "existing_fold_to_cap_and_final_fixed_family": closure[
                "existing_fold_identification"
            ],
        },
        "augmented_fold_cap": {
            "source_X_U": cap["source_X_U"],
            "krawczyk_ratio": cap["krawczyk_ratio"],
            "contraction_ratio": cap["contraction_ratio"],
            "minimum_containment_margin": cap["minimum_containment_margin"],
            "target_C0_bound": cap["target_eta_C0_bound"],
            "target_C1_bound": cap["target_eta_C1_bound"],
            "target_C2_bound": cap["target_eta_C2_bound"],
            "terminal_e": cap["terminal_X_e"],
            "terminal_a": cap["terminal_X_a"],
            "terminal_b": cap["terminal_X_b"],
            "terminal_graph_energy": cap["terminal_X_graph_energy"],
        },
        "source_sha256": {
            name: sha256(HERE / name) for name in source_files
        },
        "dependency_sha256": {
            name: sha256(path) for name, path in dependency_files.items()
        },
        "bulk_replay_sha256": {
            "main_cover_boxes.jsonl": sha256(main_manifest_path),
            "main_cover_seeds.txt": sha256(main_seeds_path),
            "main_cover_summary.json": sha256(main_centres_summary_path),
            "main_results.jsonl": sha256(main_results_path),
            "main_bridges.jsonl": sha256(main_bridges_path),
            "tail_cover_boxes.jsonl": sha256(tail_manifest_path),
            "tail_cover_seeds.txt": sha256(tail_seeds_path),
            "tail_cover_summary.json": sha256(tail_centres_summary_path),
            "tail_results.jsonl": sha256(tail_results_path),
            "tail_bridges.jsonl": sha256(tail_bridges_path),
            "cap_containment.jsonl": sha256(containment_path),
        },
    }
    rendered = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    arguments.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
