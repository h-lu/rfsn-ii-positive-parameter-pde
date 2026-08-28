#!/usr/bin/env python3
"""Clean source-only replay of the fixed-time-fold/event-chart bridge."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import time


HERE = Path(__file__).resolve().parent
VALIDATION = HERE.parent if HERE.parent.name == "validation" else None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(command: list[str], *, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        command,
        check=True,
        text=True,
        capture_output=True,
        env=env,
    )
    return completed.stdout


def capd_flags(capd_config: Path, option: str) -> list[str]:
    return shlex.split(run([str(capd_config), option]))


def interval(text: str) -> tuple[float, float]:
    left, right = text.strip()[1:-1].split(",")
    return float(left), float(right)


def strict_subset(inner: tuple[float, float], outer: tuple[float, float]) -> bool:
    return outer[0] < inner[0] and inner[1] < outer[1]


def locate_validation() -> Path:
    if VALIDATION is not None:
        return VALIDATION
    candidate = Path.cwd() / "validation"
    if candidate.is_dir():
        return candidate
    raise RuntimeError("package must live under validation/ for replay")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--capd-config",
        type=Path,
        default=Path(os.environ.get("CAPD_CONFIG", "capd-config")),
    )
    parser.add_argument("--output", type=Path, default=HERE / "certificate.json")
    args = parser.parse_args()

    validation = locate_validation()
    fold = validation / "future-target-fold"
    collar = validation / "finite-source-intermediate-collar"
    required = [
        fold / "fold_interval_probe.cpp",
        fold / "fold_centres_generated.hpp",
        fold / "tail_graph_generated.hpp",
        fold / "weighted_tail_generated.hpp",
        fold / "certificate.json",
        collar / "generate_full_cover.py",
        collar / "numerical_bvp.py",
        collar / "source_cover_probe.cpp",
        collar / "certificate.json",
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"missing promoted dependencies: {missing}")
    dependency_hashes_at_start = {
        str(path.relative_to(validation)): sha256(path) for path in required
    }

    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="papera-fold-event-bridge-") as raw:
        build = Path(raw)
        generator_source = build / "generate_full_cover.py"
        numerical_source = build / "numerical_bvp.py"
        collar_probe_source = build / "source_cover_probe.cpp"
        upstream_fold_source = build / "fold_interval_probe.upstream.cpp"
        for source, destination in [
            (collar / "generate_full_cover.py", generator_source),
            (collar / "numerical_bvp.py", numerical_source),
            (collar / "source_cover_probe.cpp", collar_probe_source),
            (fold / "fold_interval_probe.cpp", upstream_fold_source),
            (fold / "fold_centres_generated.hpp", build / "fold_centres_generated.hpp"),
            (fold / "tail_graph_generated.hpp", build / "tail_graph_generated.hpp"),
            (fold / "weighted_tail_generated.hpp", build / "weighted_tail_generated.hpp"),
        ]:
            shutil.copy2(source, destination)
        seed = build / "box0_seeds.txt"
        manifest = build / "box0_manifest.jsonl"
        summary = build / "box0_seed_summary.json"
        run(
            [
                sys.executable,
                str(generator_source),
                "--fresh",
                "--limit",
                "3",
                "--seed-output",
                str(seed),
                "--manifest-output",
                str(manifest),
                "--summary-output",
                str(summary),
                "--v-checkpoint",
                str(build / "unused-v.npz"),
                "--u-checkpoint",
                str(build / "unused-u.npz"),
            ],
            env=environment,
        )
        rows = [json.loads(line) for line in manifest.read_text().splitlines()]
        if len(rows) != 3 or rows[0]["index"] != 0 or rows[0]["chart"] != "v":
            raise RuntimeError("unexpected deterministic box-0 seed manifest")
        if rows[0]["seed_offset"] != 0 or rows[0]["half_width"] != 2e-5:
            raise RuntimeError("box-0 seed contract changed")

        sharp_fold = build / "fold_interval_probe.cpp"
        run(
            [
                sys.executable,
                str(HERE / "prepare_sharp_fold.py"),
                str(upstream_fold_source),
                str(sharp_fold),
            ],
            env=environment,
        )

        compiler = os.environ.get("CXX", "g++")
        common = [
            *capd_flags(args.capd_config, "--cflags"),
            *capd_flags(args.capd_config, "--libs"),
        ]
        bridge_binary = build / "fold_event_flow_bridge_probe"
        subprocess.run(
            [
                compiler,
                "-O0",
                "-std=c++17",
                str(HERE / "fold_event_flow_bridge_probe.cpp"),
                f"-I{build}",
                f"-I{fold}",
                *common,
                "-o",
                str(bridge_binary),
            ],
            check=True,
        )
        collar_binary = build / "source_cover_probe"
        subprocess.run(
            [
                compiler,
                "-O0",
                "-std=c++17",
                str(collar_probe_source),
                f"-I{build}",
                *common,
                "-o",
                str(collar_binary),
            ],
            check=True,
        )

        bridge_result = json.loads(
            run(
                [
                    str(bridge_binary),
                    "--seed-file",
                    str(seed),
                    "--seed-offset",
                    "0",
                ]
            )
        )
        box0_result = json.loads(
            run(
                [
                    str(collar_binary),
                    "--seed-file",
                    str(seed),
                    "--seed-offset",
                    "0",
                    "--parameter",
                    "v",
                    "--half-width",
                    "2e-5",
                ]
            )
        )

        if bridge_result["status"] != "PASS-FOLD-BOX-FLOW-CONTAINMENT-IN-COLLAR-BOX0":
            raise RuntimeError("flow-containment bridge did not pass")
        if not all(
            bridge_result[key]
            for key in [
                "upstream_robust_fold_krawczyk_replayed",
                "strict_negative_P_on_event_bracket",
                "first_event_after_T15",
                "strict_flow_containment_in_box0",
                "strict_time_containment_in_box0",
                "fold_V_strictly_inside_collar_parameter",
            ]
        ):
            raise RuntimeError("one bridge gate is false")
        if box0_result["status"] != "PASS-PARAMETRIC-SOURCE-COVER-BOX":
            raise RuntimeError("collar box 0 did not pass")
        if not box0_result["first_event"] or not box0_result["tangent_certified"]:
            raise RuntimeError("box-0 first-event/tangent gate failed")

        fold_slope = interval(bridge_result["fold_source_dU_dV_enclosure"])
        collar_slope = interval(box0_result["d_source_U_dparameter"])
        tangent_containment = strict_subset(fold_slope, collar_slope)
        if not tangent_containment:
            raise RuntimeError("fold tangent slope leaves collar tangent enclosure")

        fold_v = interval(bridge_result["fold_source_V"])
        collar_v = interval(bridge_result["collar_box0_V_parameter"])
        if not strict_subset(fold_v, collar_v):
            raise RuntimeError("fold V root leaves collar parameter interval")

        dependencies_at_end = {
            str(path.relative_to(validation)): sha256(path) for path in required
        }
        if dependencies_at_end != dependency_hashes_at_start:
            raise RuntimeError("an upstream dependency changed during replay")
        dependencies = dependency_hashes_at_start
        source_hashes = {
            name: sha256(HERE / name)
            for name in [
                "fold_event_flow_bridge_probe.cpp",
                "prepare_sharp_fold.py",
                "replay.py",
            ]
        }
        certificate = {
            "status": "PASS-SAME-ORBIT-FIXED-T-FOLD-TO-EVENT-BOX0-BRIDGE",
            "claim_boundary": (
                "For the canonical physical future graph only, the unique "
                "fixed-T=15 fold root reaches its first e=0.0575 event and "
                "its complete event-chart representation lies strictly in "
                "the finite intermediate-collar box-0 uniqueness tube."
            ),
            "quantifier": {
                "target": "one and the same canonical physical future graph",
                "sharp_fold_value_budget": "|eta| <= 2*(0.06)^8 = 3.359232e-10",
                "sharp_fold_C1_budget": "||D eta||_2 <= 1e-5",
                "sharp_fold_C2_budget": "||D^2 eta||_2 <= 1e-3",
                "box0_value_budget": "|eta| <= 2 e^8",
                "box0_C1_budget": "||D eta||_2 <= 1e-5",
            },
            "logic": {
                "fold_root": "sharp physical-budget Krawczyk replay in upstream fold box",
                "same_orbit": "exact IVP flow from the captured fold Krawczyk image",
                "target_at_event": "invariance of the same canonical physical graph",
                "common_root": (
                    "strict containment in box 0 plus box-0 Krawczyk uniqueness"
                ),
                "not_used": "midpoint proximity or two independent root enclosures",
            },
            "bridge": bridge_result,
            "box0": box0_result,
            "tangent": {
                "fold_source_dU_dV": bridge_result[
                    "fold_source_dU_dV_enclosure"
                ],
                "box0_dU_dV": box0_result["d_source_U_dparameter"],
                "strict_containment": tangent_containment,
            },
            "deterministic_seed": {
                "generator_mode": "generate_full_cover.py --fresh --limit 3",
                "reason_for_three_centres": (
                    "box-0 endpoint tangent uses the same second-order "
                    "three-centre finite difference as the full cover"
                ),
                "sha256": sha256(seed),
                "box0_manifest": rows[0],
            },
            "generated_sharp_fold_source_sha256": sha256(sharp_fold),
            "dependency_sha256": dependencies,
            "source_sha256": source_hashes,
            "environment": {
                "capd_config_version": run(
                    [str(args.capd_config), "--version"]
                ).strip(),
                "compiler": run([compiler, "--version"]).splitlines()[0],
                "interval_backend": "FILIB",
            },
            "elapsed_seconds": time.monotonic() - started,
            "remaining_gates": {
                "intermediate_collar_to_local_annulus": "NOT-COVERED-HERE",
                "fold_to_exact_algebraic_source": "NOT-COVERED-HERE",
            },
        }
        args.output.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
        print(json.dumps(certificate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
