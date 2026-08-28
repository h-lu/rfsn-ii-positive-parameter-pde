#!/usr/bin/env python3
"""Generate the figures used by Paper A.

The return/exit, zero-action-cut, two-end finite-part, and proof-route
figures are qualitative diagrams.  The restricted-Hamiltonian figure draws
the leading-order mechanism from the asymptotic formulas in the manuscript.
The source-phase figure reads interval enclosures from the machine-readable
validation records.  Its wording deliberately distinguishes stored
certificate data from the separately reported replay status.

All figures are designed at approximately their final manuscript width.
The generator rejects any visible label smaller than seven points.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]

NAVY = "#005F73"
TEAL = "#0A9396"
ORANGE = "#CA6702"
RED = "#9B2226"
GREY = "#5B6573"
LIGHT = "#E9EEF2"
PALE_TEAL = "#DDEEF2"
PALE_ORANGE = "#F6E7D7"

TARGET_WIDTH_IN = 5.2
MIN_LABEL_PT = 7.0
SMALL_PT = 7.2
BASE_PT = 8.0
TITLE_PT = 8.4


def configure() -> None:
    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Latin Modern Roman", "CMU Serif", "STIXGeneral"],
            "mathtext.fontset": "cm",
            "font.size": BASE_PT,
            "axes.titlesize": TITLE_PT,
            "axes.labelsize": BASE_PT,
            "xtick.labelsize": SMALL_PT,
            "ytick.labelsize": SMALL_PT,
            "legend.fontsize": SMALL_PT,
            "axes.linewidth": 0.75,
            "lines.linewidth": 1.25,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.03,
        }
    )


def save_pdf(fig, name: str) -> None:
    """Write a deterministic vector PDF without wall-clock metadata."""
    undersized = [
        (artist.get_text(), artist.get_fontsize())
        for artist in fig.findobj(match=mpl.text.Text)
        if artist.get_text().strip() and artist.get_fontsize() < MIN_LABEL_PT
    ]
    if undersized:
        raise ValueError(f"labels below {MIN_LABEL_PT:g} pt in {name}: {undersized}")
    fig.savefig(
        HERE / name,
        metadata={"CreationDate": None, "ModDate": None},
    )


def arrow(ax, start, end, *, color=NAVY, style="-", rad=0.0, lw=1.5, zorder=3):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=10,
        linewidth=lw,
        linestyle=style,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=2,
        shrinkB=2,
        zorder=zorder,
    )
    ax.add_patch(patch)
    return patch


def box(
    ax,
    xy,
    width,
    height,
    text,
    *,
    edge=NAVY,
    face="white",
    style="-",
    fontsize=SMALL_PT,
):
    patch = Rectangle(
        xy,
        width,
        height,
        linewidth=1.2,
        edgecolor=edge,
        facecolor=face,
        linestyle=style,
        zorder=2,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
    )
    return patch


def recurrence_exit_geometry() -> None:
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(TARGET_WIDTH_IN, 2.72),
        gridspec_kw={"wspace": 0.18},
    )

    # Panel (a): incidence of flow tubes in the declared local domain.
    ax = axes[0]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    box(ax, (0.01, 0.42), 0.22, 0.16, "incoming\n$\\Sigma_N$", face=LIGHT)
    t = np.linspace(0.2, 4.5 * np.pi, 240)
    rr = 0.105 * np.exp(-0.10 * t)
    cx, cy = 0.39, 0.50
    ax.plot(cx + rr * np.cos(t), cy + rr * np.sin(t), color=NAVY, lw=1.5)
    ax.plot(cx, cy, marker="o", ms=3.0, color=NAVY)
    ax.text(cx, 0.72, "long passage", ha="center", color=NAVY)
    ax.text(cx, 0.29, r"winding $n\geq N$", ha="center", color=NAVY)
    arrow(ax, (0.22, 0.50), (0.29, 0.50))
    box(ax, (0.55, 0.43), 0.18, 0.14, "outgoing\nband", face=LIGHT)
    arrow(ax, (0.47, 0.50), (0.55, 0.50))

    box(ax, (0.79, 0.75), 0.20, 0.13, "homoclinic\ntube", edge=NAVY)
    box(ax, (0.79, 0.54), 0.20, 0.13, "algebraic\nsheet", edge=TEAL, style="--")
    box(ax, (0.79, 0.33), 0.20, 0.13, "pole\nwindow", edge=RED, style="-.")
    box(ax, (0.76, 0.02), 0.23, 0.15, "lateral / cut\nexit faces", edge=GREY, style=":")
    branch_x = 0.76
    ax.plot([0.73, branch_x], [0.50, 0.50], color=GREY, lw=0.9)
    ax.plot([branch_x, branch_x], [0.10, 0.82], color=GREY, lw=0.9)
    arrow(ax, (branch_x, 0.82), (0.79, 0.82), color=NAVY)
    arrow(ax, (branch_x, 0.61), (0.79, 0.61), color=TEAL, style="--")
    arrow(ax, (branch_x, 0.40), (0.79, 0.40), color=RED, style="-.")
    arrow(ax, (branch_x, 0.10), (0.76, 0.10), color=GREY, style=":")
    arrow(ax, (0.84, 0.87), (0.12, 0.59), color=NAVY, rad=0.35, lw=1.3)
    ax.text(0.48, 0.94, "return and re-entry", ha="center", color=NAVY)
    ax.set_title("(a) physical forward flow")

    # Panel (b): the resulting two-vertex graph and its terminal arrows.
    ax = axes[1]
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    for xpos, sign in [(0.18, "+"), (0.68, "-")]:
        ax.add_patch(FancyBboxPatch((xpos, 0.40), 0.16, 0.16,
                                    boxstyle="round,pad=0.015", fc=LIGHT,
                                    ec=NAVY, lw=1.2))
        ax.text(xpos + 0.08, 0.48, rf"$\Sigma_{sign}$", ha="center", va="center")
    # A small sample of the countably many directed return edges.
    arrow(ax, (0.33, 0.53), (0.68, 0.53), rad=0.20, lw=1.2)
    arrow(ax, (0.68, 0.43), (0.34, 0.43), rad=0.20, lw=1.2)
    arrow(ax, (0.25, 0.57), (0.25, 0.40), rad=0.65, lw=1.0)
    arrow(ax, (0.75, 0.40), (0.75, 0.57), rad=0.65, lw=1.0)
    ax.text(
        0.50,
        0.70,
        r"return edge $(\sigma,n,\sigma')$, $n\geq N$",
        ha="center",
        color=NAVY,
    )
    ax.text(
        0.50,
        0.63,
        r"all $(\sigma,\sigma')\in\{+,-\}^2$",
        ha="center",
        fontsize=SMALL_PT,
        color=GREY,
    )
    # Terminal types remain discrete and do not become graph edges.
    terminal_y = 0.18
    ax.plot([0.26, 0.76], [0.36, 0.36], color=GREY, lw=0.8, ls=":")
    for xpos, label, color, style in [
        (0.11, "alg.", TEAL, "--"),
        (0.28, "pole", RED, "-."),
        (0.47, r"$\mathrm{out}$", GREY, ":"),
        (0.68, r"$\mathrm{rbox}$", GREY, ":"),
        (0.89, r"$\mathrm{cut}$", "black", "-"),
    ]:
        arrow(ax, (xpos, 0.36), (xpos, terminal_y + 0.11), color=color, style=style, lw=1.0)
        ax.text(
            xpos,
            terminal_y,
            label,
            ha="center",
            va="center",
            color=color,
            fontsize=SMALL_PT,
        )
    ax.set_title("(b) symbolic incidence")

    fig.text(0.01, 0.99, "SCHEMATIC", fontsize=SMALL_PT, color=GREY, va="top")
    save_pdf(fig, "recurrence_exit_geometry.pdf")
    plt.close(fig)


def two_end_action_finite_parts() -> None:
    """Compare the two end renormalizations and their exact composition.

    This is a schematic of the proved subtraction procedures.  It does not
    identify the actual algebraic orbit with its reference orbit, and it
    does not assert that the algebraic and pole counterterms agree.
    """
    fig = plt.figure(figsize=(TARGET_WIDTH_IN, 3.65))
    grid = fig.add_gridspec(
        2,
        2,
        height_ratios=(1.75, 1.0),
        hspace=0.29,
        wspace=0.20,
    )

    # Panel (a): the actual and reference algebraic tails are compared at
    # the same value of the boundary defining function e.  They are not the
    # same curve; their separation becomes flat as e tends to zero.
    ax = fig.add_subplot(grid[0, 0])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    x = np.linspace(0.08, 0.90, 220)
    reference = 0.52 + 0.035 * np.sin(1.3 * np.pi * x)
    flat_separation = np.exp(-0.35 / x) / np.exp(-0.35 / 0.90)
    actual = reference + 0.19 * flat_separation
    ax.plot(x, actual, color=NAVY, lw=1.6, label="actual tail")
    ax.plot(x, reference, color=TEAL, lw=1.5, ls="--", label="reference tail")
    ax.fill_between(
        x,
        reference,
        actual,
        where=x >= 0.27,
        color=PALE_TEAL,
        alpha=0.72,
        zorder=0,
    )
    eps_x, cut_x = 0.27, 0.90
    ax.plot([eps_x, eps_x], [0.25, 0.80], color=GREY, lw=0.9, ls=":")
    ax.plot([cut_x, cut_x], [0.25, 0.80], color=GREY, lw=0.9, ls=":")
    arrow(ax, (0.82, 0.84), (0.14, 0.84), color=GREY, lw=0.9)
    ax.text(0.48, 0.88, "physical forward direction", ha="center", color=GREY)
    label_x = 0.56
    label_ref = 0.52 + 0.035 * np.sin(1.3 * np.pi * label_x)
    label_actual = label_ref + 0.19 * np.exp(-0.35 / label_x) / np.exp(-0.35 / 0.90)
    ax.text(label_x, label_actual + 0.055, "actual tail", color=NAVY, ha="center")
    ax.text(label_x, label_ref - 0.075, "reference tail", color=TEAL, ha="center")
    ax.text(0.06, 0.23, r"end $e=0$", ha="left")
    ax.text(eps_x, 0.15, r"cutoff $e=\epsilon$", ha="center")
    ax.text(cut_x, 0.18, r"fixed cut $e=e_*$", ha="right")
    ax.text(0.50, 0.06, r"subtract at the same $e=\epsilon$", ha="center", color=GREY)
    ax.set_title("(a) algebraic end: fixed-cut reference")

    # Panel (b): the pole cutoff is physical remaining time.  The displayed
    # Laurent--log sum is the nonintegrable part of the action density.
    ax = fig.add_subplot(grid[0, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    base_y = 0.43
    ax.plot([0.08, 0.91], [base_y, base_y], color=NAVY, lw=1.6)
    arrow(ax, (0.11, base_y), (0.91, base_y), color=NAVY, lw=1.2)
    cutoff_x = 0.72
    ax.plot([cutoff_x, cutoff_x], [0.24, 0.56], color=GREY, lw=0.9, ls=":")
    ax.plot([0.91, 0.91], [0.24, 0.56], color=RED, lw=1.1)
    ax.fill_between(
        [cutoff_x, 0.91],
        [0.39, 0.39],
        [0.47, 0.47],
        color=PALE_ORANGE,
        alpha=0.85,
    )
    ax.text(0.08, 0.32, r"$t_{\rm in}$", ha="left")
    ax.text(cutoff_x, 0.32, r"$s=\epsilon$", ha="center")
    ax.text(0.91, 0.32, r"$s=0$", ha="center", color=RED)
    ax.text(0.91, 0.20, r"$t=t_b$", ha="center", color=RED)
    ax.text(0.50, 0.84, r"physical remaining time $s=t_b-t$", ha="center")
    ax.text(
        0.50,
        0.68,
        r"$\lambda(X)=\sum_{q=-m_p}^{-1}s^qA_q(\log s,p)+R(s,p)$",
        ha="center",
        color=GREY,
    )
    ax.text(
        0.50,
        0.07,
        r"subtract the Laurent--log counterterm $C_{B,\mathrm{p}}(\epsilon,p)$",
        ha="center",
        color=GREY,
    )
    ax.set_title("(b) pole end: fixed remaining time")

    # Panel (c): the exact identity is imposed at every finite cutoff.  The
    # end-specific subtraction is made only on the terminal segment before
    # the cutoff tends to the end.
    ax = fig.add_subplot(grid[1, :])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    for xpos, label, face in [
        (0.06, r"$\Sigma^-$", LIGHT),
        (0.43, r"$\Sigma_0$", "white"),
        (0.84, r"$E_\epsilon$", PALE_ORANGE),
    ]:
        ax.add_patch(
            FancyBboxPatch(
                (xpos, 0.51),
                0.10,
                0.25,
                boxstyle="round,pad=0.012",
                ec=NAVY if xpos < 0.80 else RED,
                fc=face,
                lw=1.0,
            )
        )
        ax.text(xpos + 0.05, 0.635, label, ha="center", va="center")
    arrow(ax, (0.16, 0.64), (0.43, 0.64), lw=1.1)
    arrow(ax, (0.53, 0.64), (0.84, 0.64), color=ORANGE, lw=1.1)
    ax.text(0.295, 0.73, r"$P_1,\ B_{P_1}$", ha="center", color=NAVY)
    ax.text(0.685, 0.73, r"$P_2^\epsilon,\ B_{P_2^\epsilon}$", ha="center", color=ORANGE)
    ax.text(
        0.50,
        0.37,
        r"finite cutoff: $B_{P_2^\epsilon P_1}="
        r"B_{P_1}+B_{P_2^\epsilon}\!\circ P_1$",
        ha="center",
    )
    ax.text(
        0.50,
        0.15,
        r"subtract $C_{B,\mathsf{e}}(\epsilon)$ on the terminal segment, "
        r"then let $\epsilon\downarrow0$",
        ha="center",
        color=GREY,
    )
    ax.set_title("(c) exact action composition is retained by either finite part")

    fig.text(
        0.01,
        0.995,
        "SCHEMATIC; THE TWO COUNTERTERMS ARE END-SPECIFIC",
        fontsize=SMALL_PT,
        color=GREY,
        va="top",
    )
    save_pdf(fig, "two_end_action_finite_parts.pdf")
    plt.close(fig)


def signed_seam_crossform() -> None:
    fig, axes = plt.subplots(
        1,
        3,
        figsize=(TARGET_WIDTH_IN, 2.80),
        gridspec_kw={"wspace": 0.44},
    )

    # Panel (a): leading profiles for the mixed boundary-value problem.
    ax = axes[0]
    s = np.linspace(0, 1, 250)
    stable = np.exp(-4.2 * s)
    unstable = np.exp(-4.2 * (1 - s))
    ax.semilogy(s, stable, color=TEAL, lw=1.4, ls="--")
    ax.semilogy(s, unstable, color=NAVY, lw=1.4)
    ax.text(0.04, 0.86, r"$|\eta(t)|$", transform=ax.transAxes, color=TEAL)
    ax.text(0.72, 0.86, r"$|\xi(t)|$", transform=ax.transAxes, color=NAVY)
    ax.text(0.01, 0.05, r"$\eta(0)$ fixed", transform=ax.transAxes)
    ax.text(0.55, 0.05, r"$\xi(T)$ fixed", transform=ax.transAxes)
    ax.annotate("", xy=(0.72, 0.36), xytext=(0.30, 0.36), xycoords="axes fraction",
                arrowprops={"arrowstyle": "->", "color": TEAL, "lw": 0.8, "ls": "--"})
    ax.annotate("", xy=(0.30, 0.27), xytext=(0.72, 0.27), xycoords="axes fraction",
                arrowprops={"arrowstyle": "->", "color": NAVY, "lw": 0.8})
    ax.set_xlabel(r"$t/T$")
    ax.set_ylabel("amplitude (log scale)")
    ax.set_xticks([0, 1], [r"$0$", r"$T$"])
    ax.set_yticks([])
    ax.set_title("(a) opposite\nendpoint data", fontsize=7.5)
    ax.spines[["top", "right"]].set_visible(False)

    # Panel (b): winding strips accumulate at the removed zero-action boundary.
    ax = axes[1]
    ax.set_xlim(0, 1)
    ax.set_ylim(-1, 1)
    ax.axhline(0, color=GREY, lw=1.0, ls=(0, (3, 2)))
    ax.text(0.50, 0.02, r"zero-action boundary $\nu=0$",
            ha="center", va="bottom", color=GREY, fontsize=SMALL_PT)
    for sign, color, style in [(1, ORANGE, "--"), (-1, NAVY, "-")]:
        for j, height in enumerate([0.60, 0.34, 0.18]):
            y0 = sign * height
            thickness = 0.065 * (0.70 ** j)
            xx = np.array([0.06, 0.94])
            lower = y0 + sign * (0.04 * (xx - 0.5))
            ax.fill_between(xx, lower - thickness, lower + thickness,
                            color=color, alpha=0.18)
            ax.plot(xx, lower, color=color, lw=1.2, ls=style)
            ax.text(0.08, y0, rf"$n+{j}$" if j else r"$n$",
                    color=color, fontsize=SMALL_PT,
                    bbox={"fc": "white", "ec": "none", "pad": 0.15, "alpha": 0.82})
    ax.text(-0.05, 0.74, r"$\nu>0$", transform=ax.transAxes,
            ha="right", va="center", color="black", fontsize=SMALL_PT, clip_on=False)
    ax.text(-0.05, 0.25, r"$\nu<0$", transform=ax.transAxes,
            ha="right", va="center", color="black", fontsize=SMALL_PT, clip_on=False)
    ax.text(0.50, 0.95, "transverse-action scale",
            ha="center", va="top", fontsize=SMALL_PT, color=GREY)
    ax.text(0.50, 0.85,
            r"$g_a=\epsilon_a\widetilde g_a$",
            ha="center", va="top", fontsize=SMALL_PT, color=GREY)
    ax.text(0.50, 0.76,
            r"$\epsilon_a\asymp e^{-2\pi\alpha n/\beta}$",
            ha="center", va="top", fontsize=SMALL_PT, color=GREY)
    ax.set_xlabel(r"source angle $\phi$")
    ax.set_ylabel(r"signed action $\nu$")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("(b) high-winding\nreturn strips", fontsize=7.5)
    ax.spines[["top", "right"]].set_visible(False)

    # Panel (c): cut the closure of one winding domain at the zero-action
    # boundary of the target section.  No source cross-form scale is encoded
    # in this target-coordinate panel.
    ax = axes[2]
    ax.set_xlim(-1.0, 1.0)
    ax.set_ylim(-0.95, 0.95)
    ax.axhline(0, color=GREY, lw=1.0, ls=(0, (3, 2)))
    x = np.linspace(-0.78, 0.78, 250)
    upper = 0.52 + 0.045 * np.cos(np.pi * x)
    lower = -0.52 + 0.045 * np.sin(np.pi * x)
    ax.fill_between(x, 0, upper, color=ORANGE, alpha=0.22)
    ax.fill_between(x, lower, 0, color=NAVY, alpha=0.18)
    ax.plot(x, upper, color=GREY, lw=1.1)
    ax.plot(x, lower, color=GREY, lw=1.1)
    ax.plot([x[0], x[0]], [lower[0], upper[0]], color=GREY, lw=1.1)
    ax.plot([x[-1], x[-1]], [lower[-1], upper[-1]], color=GREY, lw=1.1)
    ax.text(0.00, 0.29, r"target $+$: $(\sigma,n,+)$",
            color=ORANGE, ha="center", fontsize=SMALL_PT)
    ax.text(0.00, -0.32, r"target $-$: $(\sigma,n,-)$",
            color=NAVY, ha="center", fontsize=SMALL_PT)
    ax.text(0.00, -0.045,
            r"first-exit cut $\bar\nu=0$",
            ha="center", va="top", fontsize=SMALL_PT,
            bbox={"fc": "white", "ec": "none", "pad": 0.3, "alpha": 0.9})
    ax.text(0.00, 0.73, "closure in cut-open target",
            ha="center", fontsize=SMALL_PT, color=GREY)
    ax.set_xlabel(r"target angle $x'$")
    ax.set_ylabel(r"target action $\bar\nu$")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("(c) zero-action cut\nin target coordinates", fontsize=7.5)
    ax.spines[["top", "right"]].set_visible(False)

    fig.text(0.01, 0.99, "SCHEMATIC",
             fontsize=SMALL_PT, color=GREY, va="top")
    save_pdf(fig, "signed_seam_crossform.pdf")
    plt.close(fig)


def proof_dependency() -> None:
    """Draw local coordinate production, analysis, and physical descent."""
    fig, ax = plt.subplots(figsize=(TARGET_WIDTH_IN, 4.55))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    def node(xy, width, height, text, *, edge=NAVY, face="white", style="-",
             fontsize=SMALL_PT):
        patch = FancyBboxPatch(xy, width, height, boxstyle="round,pad=0.012",
                               ec=edge, fc=face, lw=1.0, ls=style)
        ax.add_patch(patch)
        ax.text(xy[0] + width / 2, xy[1] + height / 2, text,
                ha="center", va="center", fontsize=fontsize)

    ax.text(
        0.01,
        0.96,
        "TWO-END RETURN--EXIT THEOREM",
        color=NAVY,
        fontsize=TITLE_PT,
        va="center",
    )

    route_x, route_w, route_h = 0.11, 0.78, 0.095
    route = [
        (
            0.82,
            "1. Geometric hypotheses: reversible saddle-focus and transverse homoclinic\n"
            "clean first-hit events; algebraic and pole compactifications",
            "#F3F3F3",
        ),
        (
            0.68,
            "2. Local exact symplectic coordinates\n"
            "equivariant Darboux theorem and reversible canonical normal form",
            LIGHT,
        ),
        (
            0.54,
            "3. Return and first-hit analysis\n"
            r"exhaustive decomposition; weighted $C^2$ time/action data; two finite parts",
            LIGHT,
        ),
        (
            0.40,
            "4. Compatibility of local descriptions\n"
            "bounded deck recoding, endpoint coboundaries, finite refinements",
            LIGHT,
        ),
        (
            0.26,
            "5. Physical long-passage relation\n"
            "unique first event, invariant closed data, compatible local codings",
            PALE_TEAL,
        ),
    ]
    for y, label, face in route:
        node((route_x, y), route_w, route_h, label, face=face)
    for upper, lower in zip(route, route[1:]):
        arrow(
            ax,
            (0.50, upper[0]),
            (0.50, lower[0] + route_h),
            lw=1.0,
        )

    ax.plot([0.02, 0.98], [0.215, 0.215], color=GREY, lw=0.75, ls=":")
    ax.text(
        0.50,
        0.205,
        "solid = theorem construction; dashed = system check or separate consequence",
        ha="center",
        va="top",
        color=GREY,
        fontsize=SMALL_PT,
    )

    # The model-specific checks supply evidence for the geometric input;
    # their replay status is stated in the manuscript rather than here.
    node(
        (0.02, 0.025),
        0.45,
        0.13,
        "Normal-form system (1.1)\n"
        "exact identities and stored interval data\n"
        "system-specific hypothesis checks",
        edge=GREY,
        face="#F3F3F3",
        style="--",
    )
    ax.plot(
        [0.035, 0.012, 0.012],
        [0.09, 0.23, 0.865],
        color=GREY,
        lw=1.0,
        ls="--",
    )
    arrow(
        ax,
        (0.012, 0.865),
        (route_x, 0.865),
        color=GREY,
        style="--",
        lw=1.0,
    )

    # The reversible-branch result is not part of the theorem route.
    node(
        (0.53, 0.017),
        0.45,
        0.145,
        "OPTIONAL SELECTED-BRANCH MODULE\n"
        "Jost identification and continuation\n"
        r"$\Longrightarrow$ logarithmic spiral and alternating extrema",
        edge=ORANGE,
        face="white",
        style="--",
    )

    fig.text(0.01, 0.99, "SCHEMATIC THEOREM ROUTE",
             fontsize=SMALL_PT, color=GREY, va="top")
    save_pdf(fig, "proof_dependency.pdf")
    plt.close(fig)


def spiral_fold_mechanism() -> None:
    """Plot the leading critical points of the restricted Hamiltonian."""
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(TARGET_WIDTH_IN, 2.82),
        gridspec_kw={"wspace": 0.34},
    )

    # Universal-core leading law: alpha=beta, hence theta=log(r)+theta_*.
    # The general formulas are displayed explicitly in both panels.
    x = np.linspace(-8.4, -0.45, 1400)
    theta0 = 0.35
    theta = x + theta0
    ax = axes[0]
    ax.plot(x, theta, color=NAVY, lw=1.5, ls="--")
    # Zeros of the normalized core row 2(sin(2 theta)+cos(2 theta)).
    k = np.arange(-8, 4)
    xcrit = (k * np.pi - np.pi / 4) / 2 - theta0
    xcrit = xcrit[(xcrit >= x.min()) & (xcrit <= x.max())]
    thcrit = xcrit + theta0
    # At a zero, the sign of the leading second derivative is the sign of
    # cos(2 theta): positive for a minimum and negative for a maximum.
    is_maximum = np.cos(2 * thcrit) < 0
    for xx, yy, maximum in zip(xcrit, thcrit, is_maximum):
        marker = "o" if maximum else "s"
        color = ORANGE if maximum else TEAL
        ax.plot(xx, yy, marker=marker, ms=4.5, mec=color, mfc="white", mew=1.1)
    ax.annotate(r"toward the saddle: $x\to-\infty$", xy=(-8.0, -7.65),
                xytext=(0.08, 0.88), textcoords="axes fraction",
                arrowprops={"arrowstyle": "->", "color": GREY}, color=GREY)
    ax.set_xlabel(r"$x=\log r$")
    ax.set_ylabel(r"lifted angle $\theta$")
    ax.text(0.50, 0.06, r"general slope: $\theta\sim(\beta/\alpha)x+\theta_*$",
            transform=ax.transAxes, ha="center", fontsize=SMALL_PT, color=GREY)
    ax.set_title(r"(a) selected reversible branch; core $\alpha=\beta$",
                 fontsize=TITLE_PT)
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    lead = 2 * (np.sin(2 * theta) + np.cos(2 * theta))
    ax.plot(x, lead, color=NAVY, lw=1.5, label="leading periodic row")
    ax.axhline(0, color=GREY, lw=0.8)
    for xx, maximum in zip(xcrit, is_maximum):
        marker = "o" if maximum else "s"
        color = ORANGE if maximum else TEAL
        ax.plot(xx, 0, linestyle="none", marker=marker, ms=4.5,
                mfc="white", mec=color, mew=1.1)
    ax.set_ylim(-3.0, 3.0)
    ax.set_xlabel(r"$x=\log r$")
    ax.set_ylabel(r"$(A^H)^{-1}e^{-2x}\,\partial_x H_{\rm lead}$")
    ax.set_title(r"(b) critical-point equation; core $\alpha=\beta$",
                 fontsize=TITLE_PT, pad=17)
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(0.50, 1.005,
            r"successive-radius ratio: $r_{m+1}/r_m\sim e^{-\pi\alpha/(2\beta)}$",
            transform=ax.transAxes, ha="center", va="bottom", color=RED, fontsize=BASE_PT,
            bbox={"fc": "white", "ec": "none", "pad": 0.4, "alpha": 0.94}, clip_on=False)
    handles = [
        Line2D([], [], marker="o", linestyle="none", mfc="white", mec=ORANGE,
               label=r"maximum of $H|_c$"),
        Line2D([], [], marker="s", linestyle="none", mfc="white", mec=TEAL,
               label=r"minimum of $H|_c$"),
    ]
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=SMALL_PT,
              handletextpad=0.25, borderaxespad=0.25)

    fig.text(0.01, 0.985, "LEADING RESTRICTED-HAMILTONIAN ASYMPTOTICS",
             fontsize=SMALL_PT, color=GREY, va="top")
    save_pdf(fig, "spiral_fold_mechanism.pdf")
    plt.close(fig)


def validated_source_phase_separation() -> None:
    """Plot source-phase enclosures stored in the certificate records."""
    hom_path = REPO_ROOT / "validation/universal-core-symmetric-homoclinic/certificate.json"
    alg_path = REPO_ROOT / "validation/origin-algebraic-heteroclinic/certificate.json"
    pole_path = REPO_ROOT / "validation/origin-unstable-pole-entry/certificate.json"
    with hom_path.open(encoding="utf-8") as stream:
        hom_certificate = json.load(stream)
    with alg_path.open(encoding="utf-8") as stream:
        alg_certificate = json.load(stream)
    with pole_path.open(encoding="utf-8") as stream:
        pole_certificate = json.load(stream)

    hom = np.asarray(hom_certificate["root"]["phase"], dtype=float)
    alg = np.asarray(
        ast.literal_eval(alg_certificate["robust_multiple_shooting"]["source_phase"]),
        dtype=float,
    )
    pole = np.asarray(pole_certificate["phase"]["closed_cover"], dtype=float)
    copied = pole_certificate["separate_certified_phases"]
    if not np.array_equal(alg, np.asarray(copied["origin_to_algebraic"], dtype=float)):
        raise ValueError("algebraic phase boxes disagree across certificates")
    if not np.array_equal(hom, np.asarray(copied["symmetric_homoclinic"], dtype=float)):
        raise ValueError("homoclinic phase boxes disagree across certificates")

    two_pi = 2 * np.pi
    alg_lift = alg - two_pi
    hom_lift = hom - two_pi
    alg_hom_gap = hom[0] - alg[1]
    pole_gaps = copied["strict_gap_lower"]
    if not alg_hom_gap > 0.104814:
        raise ValueError("stored algebraic--homoclinic gap changed")

    fig = plt.figure(figsize=(TARGET_WIDTH_IN, 2.86))
    grid = fig.add_gridspec(1, 3, width_ratios=[2.3, 1.0, 1.0], wspace=0.48)

    # Overview on the common lift centered at zero.  Root widths are below
    # this panel's resolution and are magnified in the next two panels.
    ax = fig.add_subplot(grid[0, 0])
    ax.set_xlim(-0.57, 0.22)
    ax.set_ylim(-0.55, 2.55)
    ax.axvline(0, color=GREY, lw=0.7, ls=":")
    ax.barh(2, pole[1] - pole[0], left=pole[0], height=0.25,
            color=RED, alpha=0.18, edgecolor=RED, hatch="////", linewidth=0.9)
    ax.hlines(1, hom_lift[0], hom_lift[1], color=NAVY, lw=5.0)
    ax.hlines(0, alg_lift[0], alg_lift[1], color=TEAL, lw=5.0, ls="--")
    hom_mid = float(np.mean(hom_lift))
    alg_mid = float(np.mean(alg_lift))
    ax.plot(hom_mid, 1, marker="|", ms=11, mew=1.2, color="black")
    ax.plot(alg_mid, 0, marker="|", ms=11, mew=1.2, color="black")
    ax.annotate("", xy=(-0.2, 1.52), xytext=(hom_lift[1], 1.52),
                arrowprops={"arrowstyle": "<->", "color": GREY, "lw": 0.8})
    ax.text((hom_lift[1] - 0.2) / 2, 1.60,
            rf"stored gap $>{pole_gaps['symmetric_homoclinic_vs_pole']:.5f}$",
            ha="center", color=GREY, fontsize=SMALL_PT)
    ax.annotate("", xy=(hom_lift[0], 0.48), xytext=(alg_lift[1], 0.48),
                arrowprops={"arrowstyle": "<->", "color": GREY, "lw": 0.8})
    ax.text((hom_lift[0] + alg_lift[1]) / 2, 0.56,
            r"stored gap $>0.104814$", ha="center", color=GREY, fontsize=SMALL_PT)
    ax.set_yticks(
        [0, 1, 2],
        ["algebraic", "homoclinic", "pole window"],
    )
    ax.set_xlabel(r"common lifted phase $\phi$ (radians)")
    ax.set_title("(a) phase intervals in one gauge", fontsize=TITLE_PT)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.text(0.01, 0.97, r"roots shown after $\phi\mapsto\phi-2\pi$",
            transform=ax.transAxes, ha="left", va="top", fontsize=SMALL_PT, color=GREY)
    ax.text(
        0.98,
        0.04,
        "replay status: see manuscript",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=SMALL_PT,
        color=GREY,
        bbox={"fc": "white", "ec": "none", "pad": 0.25, "alpha": 0.94},
    )

    def interval_zoom(axis, interval, scale, color, linestyle, title, exponent):
        midpoint = float(np.mean(interval))
        offsets = (interval - midpoint) * scale
        axis.hlines(0, offsets[0], offsets[1], color=color, lw=8.0, ls=linestyle)
        axis.vlines(offsets, -0.08, 0.08, color=color, lw=0.9)
        axis.plot(0, 0, marker="|", ms=17, mew=1.3, color="black")
        padding = max(0.25, 0.24 * (offsets[1] - offsets[0]))
        axis.set_xlim(offsets[0] - padding, offsets[1] + padding)
        axis.set_ylim(-0.32, 0.32)
        axis.set_yticks([])
        axis.set_xlabel(rf"$(\phi-m)\,10^{{{exponent}}}$")
        axis.set_title(title, fontsize=TITLE_PT)
        axis.spines[["top", "right", "left"]].set_visible(False)
        axis.text(0.5, 0.78, rf"$m={midpoint:.15f}$",
                  transform=axis.transAxes, ha="center", fontsize=SMALL_PT, color=GREY)

    ax_alg = fig.add_subplot(grid[0, 1])
    interval_zoom(ax_alg, alg, 1e9, TEAL, "-", "(b) algebraic\ninterval", 9)
    ax_hom = fig.add_subplot(grid[0, 2])
    interval_zoom(ax_hom, hom, 1e13, NAVY, "-", "(c) homoclinic\ninterval", 13)

    fig.text(
        0.01,
        0.99,
        "STORED CERTIFICATE INTERVALS",
        fontsize=SMALL_PT,
        color=GREY,
        va="top",
    )
    save_pdf(fig, "validated_source_phase_separation.pdf")
    plt.close(fig)


def main() -> None:
    configure()
    recurrence_exit_geometry()
    two_end_action_finite_parts()
    signed_seam_crossform()
    proof_dependency()
    spiral_fold_mechanism()
    validated_source_phase_separation()


if __name__ == "__main__":
    main()
