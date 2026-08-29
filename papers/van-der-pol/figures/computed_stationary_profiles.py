#!/usr/bin/env python3
"""Render the two-panel computed stationary-profile figure.

Data come from ``numerics/results/vdp_v1_v7``.  The figure is explanatory
COMPUTED/E1 evidence at (r,a2,epsilon)=(0.08,0,1); it does not assign exact
V6/V7 words.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULTS = ROOT / "numerics" / "results" / "vdp_v1_v7"

BLUE = "#1f5a94"
ORANGE = "#d2691e"
GREEN = "#2f7d4a"
PURPLE = "#7353a6"
BLACK = "#1f1f1f"


def main() -> None:
    plt.rcParams.update(
        {
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.family": "DejaVu Sans",
            "axes.linewidth": 0.8,
        }
    )
    periodic = np.load(RESULTS / "v7_periodic.npz")
    multipulse = np.load(RESULTS / "v7_multipulses.npz")
    figure, axes = plt.subplots(
        1, 2, figsize=(10.0, 3.65), constrained_layout=True
    )

    for stem, color, style, label in (
        ("B1", ORANGE, "--", "B1 numerical family"),
        ("A2", BLUE, "-", "A2 numerical family"),
    ):
        x = np.asarray(periodic[f"{stem}_physical_x"], dtype=float)
        x = x - 0.5 * (x[0] + x[-1])
        u = np.asarray(periodic[f"{stem}_physical_u"], dtype=float) - 1.0
        axes[0].plot(
            x, u, color=color, linestyle=style, linewidth=1.45, label=label
        )
    axes[0].axhline(0.0, color=BLACK, linestyle=":", linewidth=.8)
    axes[0].set(
        xlabel=r"physical coordinate $\mathsf{x}$",
        ylabel=r"$u(\mathsf{x})-a$",
        title="(a) two periodic stationary profiles",
    )
    axes[0].legend(frameon=False, fontsize=8)

    # Draw the widest candidates first, so the nested one- and two-pulse
    # profiles are not hidden underneath the three- and four-pulse curves.
    for count, color, style in (
        (4, PURPLE, "-"),
        (3, ORANGE, "--"),
        (2, GREEN, "-."),
        (1, BLACK, ":"),
    ):
        stem = f"pulse_{count}"
        x = np.asarray(multipulse[f"{stem}_physical_x"], dtype=float)
        u = np.asarray(multipulse[f"{stem}_physical_u"], dtype=float) - 1.0
        axes[1].plot(
            x,
            u,
            color=color,
            linestyle=style,
            linewidth=1.25,
            label=rf"{count}-pulse candidate",
        )
    axes[1].axhline(0.0, color=BLACK, linestyle=":", linewidth=.8)
    axes[1].set(
        xlabel=r"physical coordinate $\mathsf{x}$",
        ylabel=r"$u(\mathsf{x})-a$",
        title="(b) localized stationary profiles",
    )
    handles, labels = axes[1].get_legend_handles_labels()
    axes[1].legend(
        handles[::-1],
        labels[::-1],
        frameon=False,
        fontsize=7.4,
        ncol=2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.18),
    )

    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)
        axis.tick_params(labelsize=8)
        axis.grid(color="#d9d9d9", linewidth=.45, alpha=.55)
    figure.suptitle(
        r"Computed full-ODE profiles at $(r,a_2,\epsilon)=(0.08,0,1)$",
        fontsize=11,
        fontweight="bold",
    )
    metadata = {
        "Title": "Computed van der Pol stationary profiles",
        "Subject": "COMPUTED/E1 profiles; not exact V6/V7 word assignments",
        "Creator": "computed_stationary_profiles.py",
    }
    figure.savefig(HERE / "computed_stationary_profiles.pdf", metadata=metadata)
    figure.savefig(
        HERE / "computed_stationary_profiles.png", dpi=220, metadata=metadata
    )
    plt.close(figure)


if __name__ == "__main__":
    main()
