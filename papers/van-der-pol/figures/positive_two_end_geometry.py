#!/usr/bin/env python3
"""Render the schematic geometry used in the van der Pol companion paper."""

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle


HERE = Path(__file__).resolve().parent
PDF = HERE / "positive_two_end_geometry.pdf"
PNG = HERE / "positive_two_end_geometry.png"

mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.size": 9.5,
        "axes.linewidth": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    }
)


def arrow(ax, start, end, color, style="-", width=2.0, rad=0.0, zorder=4):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=width,
        linestyle=style,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=0,
        shrinkB=0,
        zorder=zorder,
    )
    ax.add_patch(patch)


def main():
    blue = "#265D9B"
    red = "#A33A3A"
    green = "#2C7A53"
    gray = "#777777"
    dark = "#202020"

    fig = plt.figure(figsize=(7.25, 4.75), constrained_layout=False)
    ax = fig.add_axes([0.035, 0.12, 0.93, 0.80])
    ax.set_xlim(0, 11.2)
    ax.set_ylim(-3.1, 3.3)
    ax.axis("off")

    # Source and return sections.
    ax.plot([0.75, 0.75], [-1.2, 1.25], color=dark, lw=1.6)
    ax.text(0.28, 1.62, r"source collar $\Sigma_{T_*}$", ha="left")
    ax.plot([4.45, 4.45], [-0.9, 0.9], color=dark, lw=1.4)
    ax.text(4.48, -1.15, "outgoing first-event cell", ha="center")

    # Representative incoming flight and a logarithmic high-winding spiral.
    arrow(ax, (0.83, 0.85), (1.82, 0.45), dark, width=1.8, rad=-0.08)
    center = np.array([2.75, 0.05])
    theta = np.linspace(0.2, 7.0 * np.pi, 600)
    radius = np.linspace(0.92, 0.14, theta.size)
    spiral = center[:, None] + np.vstack(
        (radius * np.cos(theta), 0.72 * radius * np.sin(theta))
    )
    ax.plot(spiral[0], spiral[1], color=dark, lw=1.25)
    k = 535
    arrow(
        ax,
        (spiral[0, k], spiral[1, k]),
        (spiral[0, k + 30], spiral[1, k + 30]),
        dark,
        width=1.25,
    )
    ax.plot(center[0], center[1], marker="o", ms=5, color=dark)
    ax.text(center[0] - 0.18, -1.02, r"saddle--focus $O_\mu$", ha="center")
    ax.text(2.72, 1.03, r"high winding $n\gg1$", ha="center")
    arrow(ax, (2.88, 0.25), (4.38, 0.25), dark, width=1.8, rad=0.06)

    # Return branch.
    arrow(ax, (4.55, 0.52), (0.78, 1.00), blue, style="-", width=2.25, rad=0.38)
    ax.text(2.75, 2.55, "return branch", color=blue, ha="center")
    ax.text(2.75, 2.25, "another high-winding visit", color=blue, ha="center", fontsize=8.7)

    # Pole branch, ending at a finite physical position.
    arrow(ax, (4.56, 0.05), (7.05, -1.55), red, style="-.", width=2.3, rad=-0.12)
    ax.plot([7.12, 7.12], [-2.15, -1.15], color=red, lw=2.0)
    ax.text(7.18, -1.34, r"pole: $u\to+\infty$", color=red, ha="left")
    ax.text(7.18, -1.68, r"$x\to x_{\mathrm{b}}<\infty$", color=red, ha="left")

    # Algebraic branch, asymptotic to a future-staying sheet.
    x = np.linspace(4.55, 10.5, 240)
    y = -0.18 + 0.78 * (1 - np.exp(-0.75 * (x - 4.55)))
    ax.plot(x, y, color=green, lw=2.25, ls="--")
    arrow(ax, (9.55, y[-40]), (10.65, y[-1]), green, style="--", width=2.25)
    ax.plot([7.7, 10.75], [0.72, 0.72], color=green, lw=1.0, ls=":")
    ax.text(8.75, 1.02, "algebraic future-staying sheet", color=green, ha="center")
    ax.text(9.15, 0.08, r"$u\to+\infty$, $x\to+\infty$", color=green, ha="center")

    # Auxiliary finite exits, intentionally quiet.
    arrow(ax, (4.52, -0.45), (5.75, -2.55), gray, style=":", width=1.2, rad=0.08, zorder=2)
    arrow(ax, (4.50, 0.75), (5.95, 2.75), gray, style=":", width=1.2, rad=-0.08, zorder=2)
    ax.text(5.26, -2.72, "finite cut/lateral exits", color=gray, ha="center", fontsize=8.3)
    ax.text(5.65, 2.95, "finite auxiliary exits", color=gray, ha="center", fontsize=8.3)

    # Matching inset.
    inset = Rectangle((7.35, -2.92), 3.55, 1.00, facecolor="white", edgecolor="#555555", lw=0.8)
    ax.add_patch(inset)
    ax.text(7.52, -2.12, "algebraic matching bridge", fontsize=8.4, ha="left")
    boxes = [(7.55, r"$K_2$"), (8.55, r"$K_1$"), (9.60, "outer")]
    for bx, label in boxes:
        ax.add_patch(Rectangle((bx, -2.72), 0.72, 0.36, fill=False, edgecolor=dark, lw=0.9))
        ax.text(bx + 0.36, -2.54, label, ha="center", va="center", fontsize=8.4)
    arrow(ax, (8.28, -2.54), (8.50, -2.54), green, style="--", width=1.3)
    arrow(ax, (9.28, -2.54), (9.55, -2.54), green, style="--", width=1.3)

    ax.text(0.05, 3.15, "SCHEMATIC: stationary spatial dynamics; geometry and distances are not quantitative", color=gray, fontsize=8.0)

    fig.savefig(PDF, bbox_inches="tight", pad_inches=0.02)
    fig.savefig(PNG, dpi=220, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


if __name__ == "__main__":
    main()
