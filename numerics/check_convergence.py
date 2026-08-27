#!/usr/bin/env python3
"""Domain convergence checks for the Brusselator atlas."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy

from rfsn_numerics import brusselator_observables, continue_homoclinics


def compute_case(domain: float, tolerance: float) -> dict[str, float]:
    results = continue_homoclinics(
        "brusselator",
        [0.025, 0.05, 0.1],
        domain=domain,
        tolerance=tolerance,
    )
    result = results[-1]
    observables = brusselator_observables(result)
    return {
        "domain": domain,
        "tolerance": tolerance,
        "center_u": float(result.solution.y[0, 0]),
        "center_v": float(result.solution.y[2, 0]),
        "amplitude_u": observables["amplitude_u"],
        "amplitude_v": observables["amplitude_v"],
        "width_u": observables["width_u"],
        "width_v": observables["width_v"],
        "normalized_ode_residual_inf": float(
            result.diagnostics["normalized_ode_residual_inf"]
        ),
        "tail_norm": float(result.diagnostics["tail_norm"]),
    }


def save_figure(cases: list[dict[str, float]], output: Path) -> None:
    reference = cases[-1]
    domains = np.array([case["domain"] for case in cases])
    figure, axes = plt.subplots(1, 2, figsize=(8.8, 3.5), constrained_layout=True)
    for key, label, marker in (
        ("center_u", "$U(0)$", "o"),
        ("center_v", "$V(0)$", "s"),
        ("width_u", "$W_u$", "^"),
        ("width_v", "$W_v$", "D"),
    ):
        errors = np.array([abs(case[key] - reference[key]) for case in cases[:-1]])
        axes[0].semilogy(domains[:-1], np.maximum(errors, 1.0e-15), marker=marker, label=label)
    axes[0].set(title=r"common-observable change vs $L_\xi=28$", xlabel=r"truncation domain $L_\xi$", ylabel="absolute difference")
    axes[0].legend()
    axes[0].grid(True, which="both", alpha=0.25)
    axes[0].text(
        0.43,
        0.86,
        "zero floating-point differences\nare shown at the $10^{-15}$ plotting floor",
        transform=axes[0].transAxes,
        ha="center",
        fontsize=7.2,
        color="#555555",
        bbox=dict(fc="white", ec="none", alpha=0.82, pad=0.2),
    )
    axes[1].semilogy(domains, [case["tail_norm"] for case in cases], "o-", label="tail norm")
    axes[1].semilogy(domains, [case["normalized_ode_residual_inf"] for case in cases], "s-", label="scaled ODE residual")
    axes[1].set(title="tail and collocation diagnostics", xlabel=r"truncation domain $L_\xi$", ylabel="diagnostic")
    axes[1].legend()
    axes[1].grid(True, which="both", alpha=0.25)
    figure.suptitle("COMPUTED/QA — Brusselator domain convergence at $r=0.1$", weight="bold")
    for suffix in ("pdf", "svg", "png"):
        figure.savefig(output / f"figure_05_numerical_convergence.{suffix}", bbox_inches="tight", dpi=220)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "results" / "atlas")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    mpl.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42, "svg.fonttype": "none"})
    domains = [16.0, 20.0, 24.0, 28.0]
    cases = [compute_case(domain, 1.0e-8) for domain in domains]
    reference = cases[-1]
    summary = {
        "evidence_status": "COMPUTED/QA non-rigorous",
        "model": "Brusselator A=B=1, r=0.1",
        "software": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "matplotlib": mpl.__version__,
            "platform": platform.platform(),
        },
        "source_sha256": {
            source.name: hashlib.sha256(source.read_bytes()).hexdigest()
            for source in (
                Path(__file__).resolve(),
                Path(__file__).resolve().with_name("rfsn_numerics.py"),
            )
        },
        "cases": cases,
        "reference_domain": 28.0,
        "maximum_common_observable_difference_L24_to_L28": float(
            max(
                abs(cases[-2][key] - reference[key])
                for key in ("center_u", "center_v", "amplitude_u", "amplitude_v", "width_u", "width_v")
            )
        ),
        "reproduction": "python3 numerics/check_convergence.py",
    }
    (output / "convergence.json").write_text(json.dumps(summary, indent=2) + "\n")
    save_figure(cases, output)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
