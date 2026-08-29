"""Render the V1--V7 atlas strictly from saved arrays and diagnostics."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))

from numerics.vdp_outer import OuterParameters, outer_physical_densities


BLUE = "#0072B2"
ORANGE = "#D55E00"
GREEN = "#009E73"
PURPLE = "#8E44AD"
RED = "#C0392B"
GRAY = "#6C757D"
BLACK = "#222222"
PALE = "#F3F5F7"
COLORS = [BLUE, ORANGE, GREEN, PURPLE, "#E69F00"]
STYLES = ["-", "--", "-.", ":", (0, (5, 2))]


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 220,
            "font.size": 8.5,
            "axes.titlesize": 9.5,
            "axes.labelsize": 8.5,
            "legend.fontsize": 7.2,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "lines.linewidth": 1.55,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "vdp-v1-v7",
        }
    )


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_render_provenance(
    config: dict[str, Any], manifest: dict[str, Any]
) -> None:
    """Refuse to render a figure atlas against stale configuration metadata."""

    config_version = config.get("configuration_version")
    manifest_version = manifest.get("configuration_version")
    if manifest_version != config_version:
        raise ValueError(
            "stale render manifest: configuration version "
            f"{config_version!r} != manifest version {manifest_version!r}"
        )


def badge(axis: plt.Axes, label: str, *, unresolved: bool = False) -> None:
    axis.text(
        0.015,
        0.985,
        label,
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontsize=7,
        weight="bold",
        bbox=dict(
            boxstyle="round,pad=.25",
            facecolor="white" if unresolved else "#EAF2F8",
            edgecolor=BLACK if unresolved else BLUE,
            hatch="///" if unresolved else None,
        ),
        zorder=10,
    )


def save(figure: plt.Figure, output: Path, stem: str) -> None:
    figure.savefig(
        output / f"{stem}.pdf",
        bbox_inches="tight",
        metadata={"CreationDate": None, "ModDate": None},
    )
    svg_path = output / f"{stem}.svg"
    figure.savefig(
        svg_path,
        bbox_inches="tight",
        metadata={"Date": None},
    )
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_path.read_text().splitlines())
        + "\n",
        encoding="utf-8",
    )
    figure.savefig(output / f"{stem}.png", bbox_inches="tight")
    plt.close(figure)


def finite_abs(value: Any, floor: float = 1.0e-18) -> float:
    """Return a log-safe absolute scalar for stored floating-point diagnostics."""

    try:
        number = abs(float(value))
    except (TypeError, ValueError):
        return floor
    return max(number, floor) if np.isfinite(number) else floor


def branch_label(branch: dict[str, Any]) -> str:
    """Short display label for a complete-return candidate record."""

    provenance = branch.get("provenance", {})
    family = provenance.get("family")
    winding = provenance.get("relative_winding_metadata")
    if family is not None and winding is not None:
        return f"{family}{int(winding)}"
    identifier = str(branch.get("branch_id", "branch"))
    for candidate in ("B1", "A2"):
        if candidate in identifier:
            return candidate
    return identifier


def branch_array_prefix(branch: dict[str, Any]) -> str:
    return str(branch["branch_id"]).replace("-", "_")


def cumulative_trapezoid_values(coordinate: np.ndarray, density: np.ndarray) -> np.ndarray:
    """Cumulative trapezoid using only already-saved samples."""

    values = np.zeros_like(density, dtype=float)
    values[1:] = np.cumsum(
        0.5 * (density[1:] + density[:-1]) * np.diff(coordinate)
    )
    return values


def figure_01(output: Path) -> None:
    report = load_json(output / "v1_structure.json")
    data = np.load(output / "v1_bridge.npz")
    figure = plt.figure(figsize=(10.8, 7.0), constrained_layout=True)
    grid = figure.add_gridspec(2, 2)

    axis = figure.add_subplot(grid[0, 0])
    axis.axis("off")
    residuals = report["symbolic"]["residuals"]
    rows = [[name.replace("_", " "), value] for name, value in residuals.items()]
    table = axis.table(
        cellText=rows,
        colLabels=["identity", "exact residual"],
        colWidths=[0.78, 0.18],
        cellLoc="left",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(6.7)
    table.scale(1.0, 1.18)
    axis.set_title("(a) Hamiltonian / reverser identities")
    badge(axis, "EXACT/DERIVED")

    axis = figure.add_subplot(grid[0, 1])
    axis.axis("off")
    labels = [
        (0.04, 0.52, r"physical $x$"),
        (0.29, 0.52, r"fast $y=x/r^2$"),
        (0.56, 0.52, r"central $y_2=ry$"),
        (0.82, 0.52, r"universal $\xi=\epsilon^{1/4}y_2$"),
    ]
    for x, y, text in labels:
        axis.text(
            x,
            y,
            text,
            transform=axis.transAxes,
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=.35", fc=PALE, ec=BLACK),
        )
    arrows = [
        (0.15, 0.24, r"$dx=r^2dy$"),
        (0.42, 0.51, r"$dy_2=rdy$"),
        (0.69, 0.78, r"$d\xi=\epsilon^{1/4}dy_2$"),
    ]
    for left, right, text in arrows:
        axis.annotate(
            "",
            xy=(right, 0.52),
            xytext=(left, 0.52),
            xycoords=axis.transAxes,
            arrowprops=dict(arrowstyle="<->", color=BLACK),
        )
        axis.text((left + right) / 2, 0.39, text, transform=axis.transAxes, ha="center")
    axis.text(
        0.5,
        0.16,
        r"$\lambda_\delta=\epsilon^{9/4}r^5(P\,dU-Q\,dV)$; action is a state-space integral",
        transform=axis.transAxes,
        ha="center",
    )
    axis.set_title("(b) exact coordinate / clock crosswalk")
    badge(axis, "EXACT/DERIVED")

    axis = figure.add_subplot(grid[1, 0])
    xi = data["xi"]
    central = data["central_state"]
    physical = data["physical_state"]
    axis.plot(xi, central[0], color=BLUE, label=r"central $U(\xi)$")
    axis.plot(
        xi,
        (1.0 - physical[0]) / 0.08**2,
        color=ORANGE,
        ls="--",
        label=r"physical reconstruction $(a-u)/r^2$",
    )
    axis.set(xlim=(-8, 8), xlabel=r"universal clock $\xi$", ylabel="scaled state")
    axis.set_title("(c) same finite orbit in two formulations")
    axis.legend()
    badge(axis, "COMPUTED/QA")

    axis = figure.add_subplot(grid[1, 1])
    tolerance = data["refinement_tolerance"]
    for key, marker, color, label in (
        ("refinement_state_defect", "o", BLUE, "state round trip"),
        ("refinement_energy_defect", "s", ORANGE, "energy scaling"),
        ("refinement_action_defect", "^", GREEN, "action"),
    ):
        axis.loglog(tolerance, np.maximum(data[key], 1e-18), marker=marker, color=color, label=label)
    axis.invert_xaxis()
    axis.axhline(1e-6, color=BLACK, ls=":", label="independent-difference gate")
    axis.set(xlabel="solver tolerance (decreasing right)", ylabel="absolute defect")
    axis.set_title("(d) independent physical/central refinement")
    axis.grid(True, which="both", alpha=0.2)
    axis.legend()
    badge(axis, "COMPUTED/QA")

    figure.suptitle(
        "V1 — exact Hamiltonian bridge and numerical clock consistency\n"
        r"$(r,a_2,\epsilon)=(0.08,0,1)$; no theorem-box validation",
        weight="bold",
    )
    save(figure, output, "figure_01_v1_structure")


def figure_02(output: Path) -> None:
    report = load_json(output / "v2_central.json")
    hom = np.load(output / "v2_homoclinics.npz")
    passage = np.load(output / "v2_passage.npz")
    figure, axes = plt.subplots(2, 2, figsize=(10.8, 7.0), constrained_layout=True)

    xi_half = hom["xi_half"]
    for index, r in enumerate(hom["r"]):
        values = hom["state_half"][index, 0]
        xi = np.concatenate((-xi_half[:0:-1], xi_half))
        profile = np.concatenate((values[:0:-1], values))
        axes[0, 0].plot(xi, profile, color=COLORS[index], ls=STYLES[index], label=rf"$r={r:.2f}$")
    axes[0, 0].axvline(xi_half[-1], color=GRAY, ls=":", lw=1)
    axes[0, 0].axvline(-xi_half[-1], color=GRAY, ls=":", lw=1)
    axes[0, 0].set(xlim=(-10, 10), xlabel=r"$\xi$", ylabel=r"$U(\xi)$", title="(a) continued symmetric homoclinics")
    axes[0, 0].legend()
    badge(axes[0, 0], "COMPUTED/E1")

    axis = axes[0, 1]
    axis.plot(hom["r"], hom["alpha"], "o-", color=BLUE, label=r"$\alpha$")
    axis.plot(hom["r"], hom["beta"], "s--", color=ORANGE, label=r"$\beta$")
    twin = axis.twinx()
    twin.semilogy(hom["r"], hom["ode_residual_inf"], "^:", color=GREEN, label="ODE residual")
    twin.semilogy(hom["r"], hom["tail_norm"], "d-.", color=PURPLE, label="tail norm")
    axis.set(xlabel=r"$r$", ylabel="saddle rates", title="(b) spectrum and finite-tail QA")
    twin.set_ylabel("residual / tail norm")
    lines = axis.lines + twin.lines
    axis.legend(lines, [line.get_label() for line in lines], loc="center right")
    badge(axis, "COMPUTED/QA")

    x = -np.log(np.abs(passage["nu_proxy"]))
    for sign, marker, color, style in ((-1, "^", ORANGE, "--"), (1, "o", BLUE, "-")):
        mask = passage["sign"] == sign
        order = np.argsort(x[mask])
        axes[1, 0].plot(x[mask][order], passage["passage_time_xi"][mask][order], marker=marker, color=color, ls=style, label=rf"sign {sign:+d}")
        axes[1, 1].plot(x[mask][order], passage["oriented_phase_change"][mask][order], marker=marker, color=color, ls=style, label=rf"sign {sign:+d}")
    expected_time = float(report["passage"]["expected_time_slope"])
    expected_phase = float(report["passage"]["expected_phase_slope"])
    axes[1, 0].text(0.03, 0.08, rf"predicted slope in $-\log|\nu|$: ${-expected_time:.6f}$", transform=axes[1, 0].transAxes)
    axes[1, 1].text(0.03, 0.08, rf"magnitude predicted: ${abs(expected_phase):.6f}$", transform=axes[1, 1].transAxes)
    axes[1, 0].set(xlabel=r"$-\log|\nu_{proxy}|$", ylabel=r"passage time $T_\xi$", title="(c) logarithmic passage time")
    axes[1, 1].set(xlabel=r"$-\log|\nu_{proxy}|$", ylabel="oriented phase change", title="(d) logarithmic phase rotation")
    for axis in axes[1]:
        axis.legend()
        axis.grid(True, alpha=0.2)
        badge(axis, "COMPUTED/E1 PROXY")
    figure.suptitle(
        "V2 — positive-parameter central continuation and saddle-focus passage\n"
        "raw eigen-coordinate proxy; not the transported V2 action/phase chart",
        weight="bold",
    )
    save(figure, output, "figure_02_v2_central_passage")


def figure_03(output: Path) -> None:
    report = load_json(output / "v3_pole.json")
    data = np.load(output / "v3_pole.npz")
    figure, axes = plt.subplots(2, 2, figsize=(10.8, 7.0), constrained_layout=True)
    labels = report["labels"]
    end_fit = report["connection"]["end_fit"]
    end_diagnostics = end_fit["diagnostics"]

    # Sampled window: markers only, because no interval enclosure between the
    # nine evaluated phases has been computed.
    window_phase = data["window_phase"]
    for key, label, color, marker in (
        ("window_cone_y", r"$y$", BLUE, "o"),
        ("window_cone_D", r"$D$", ORANGE, "s"),
        ("window_cone_K", r"$K$", GREEN, "^"),
        ("window_cone_y_prime", r"$y'$", PURPLE, "d"),
        ("window_cone_K_prime", r"$K'$", BLACK, "x"),
    ):
        axes[0, 0].scatter(
            window_phase,
            data[key],
            color=color,
            marker=marker,
            s=24,
            label=label,
        )
    axes[0, 0].axvline(0.0, color=BLACK, lw=.9, ls=":", label="representative phase")
    axes[0, 0].set_yscale("log")
    axes[0, 0].set(
        xlabel="sampled V2 source phase",
        ylabel="positive gate quantity",
        title="(a) sampled source-window cone margins",
    )
    axes[0, 0].legend(ncol=2, loc="center left")
    axes[0, 0].text(
        .98,
        .06,
        "positivity tested only at markers\nuniform/certified window not validated",
        transform=axes[0, 0].transAxes,
        ha="right",
        fontsize=6.9,
        bbox=dict(facecolor="white", edgecolor=BLACK, hatch="///", alpha=.9),
    )
    badge(axes[0, 0], "COMPUTED/E1 CANDIDATE")

    # One physical IVP from source to the highest stored pole level.
    physical_x = data["physical_x"]
    physical_state = data["physical_state"]
    source_parameters = report["connection"]["source"]["parameters"]
    physical_a = 1.0 + np.sqrt(float(source_parameters["epsilon"])) * float(
        source_parameters["r"]
    ) * float(source_parameters["a2"])
    axes[0, 1].plot(
        physical_x,
        physical_state[0] - physical_a,
        color=BLUE,
        label=r"same-orbit $u(x)-a$",
    )
    gate_x = float(report["connection"]["gate"]["physical_time"])
    axes[0, 1].axvline(gate_x, color=ORANGE, ls="--", label=r"gate $-U=10$")
    axes[0, 1].scatter(
        data["level_hit_x"],
        data["level_u"] - physical_a,
        s=24,
        facecolors="none",
        edgecolors=GREEN,
        marker="o",
        label="high-$u$ labels",
        zorder=4,
    )
    axes[0, 1].set_yscale("symlog", linthresh=0.1)
    axes[0, 1].set(
        xlabel="physical x from the V2 source",
        ylabel=r"$u-a$",
        title="(b) same physical IVP and local-chart overlap",
    )
    axes[0, 1].legend(loc="center left")
    overlap_axis = axes[0, 1].inset_axes([.50, .10, .47, .34])
    sigma = data["local_sigma"]
    overlap_defect = np.max(
        np.abs(data["global_compact_on_local_sigma"] - data["local_compact"]),
        axis=0,
    )
    overlap_axis.loglog(sigma, np.maximum(overlap_defect, 1.0e-18), color=ORANGE, ls="--")
    overlap_axis.set(xlabel=r"$\sigma$", ylabel="compact defect", title="global/local", xscale="log", yscale="log")
    overlap_axis.tick_params(labelsize=5.8)
    badge(axes[0, 1], "COMPUTED/E1 CANDIDATE")

    # Fit ladders use the actual generated labels, not the obsolete hand seed.
    levels = np.asarray(end_fit["level_u"], dtype=float)
    ladder_rows = (
        (np.asarray(end_fit["blowup_estimate_ladder"]), float(end_diagnostics["blowup_position_x"]), r"x_b", BLACK, "o"),
        (np.asarray(end_fit["z0_ladder"]), float(labels["z0"]), r"Z_0", BLUE, "s"),
        (np.asarray(end_fit["w0_ladder"]), float(labels["w0"]), r"W_0", ORANGE, "^"),
    )
    for values, fitted, name, color, marker in ladder_rows:
        axes[1, 0].loglog(
            levels,
            np.maximum(np.abs(values - fitted), 1.0e-18),
            color=color,
            marker=marker,
            label=rf"$|{name}(u_{{level}})-{name}|$",
        )
    overlap_physical = finite_abs(report["diagnostics"]["global_local_physical_relative_defect_inf"])
    overlap_compact = finite_abs(report["diagnostics"]["global_local_compact_relative_defect_inf"])
    axes[1, 0].text(
        .03,
        .05,
        f"fit: Z0={float(labels['z0']):.9f}, W0={float(labels['w0']):.9f}\n"
        f"last-3 spreads: xb={float(end_diagnostics['pole_time_last_three_spread']):.2e}, "
        f"Z0={float(end_diagnostics['z0_last_three_spread']):.2e}, W0={float(end_diagnostics['w0_last_three_spread']):.2e}\n"
        f"global/local relative defects: physical={overlap_physical:.2e}, compact={overlap_compact:.2e}",
        transform=axes[1, 0].transAxes,
        fontsize=6.7,
    )
    axes[1, 0].set(
        xlabel=r"terminal level $u_{level}$",
        ylabel="absolute fit-ladder defect",
        title="(c) generated pole-label fit ladders",
    )
    axes[1, 0].legend(loc="center right")
    badge(axes[1, 0], "COMPUTED/QA")

    cuts = data["action_sigma"]
    axes[1, 1].plot(
        cuts,
        data["action_raw"],
        "o-",
        color=BLACK,
        label="raw same-orbit action",
    )
    axes[1, 1].plot(
        cuts,
        data["action_divergent_part"],
        "s--",
        color=GRAY,
        label="analytic divergent part",
    )
    action_twin = axes[1, 1].twinx()
    action_twin.plot(
        cuts,
        data["action_subtracted"],
        "d-.",
        color=BLUE,
        label="subtracted finite-cut value",
    )
    axes[1, 1].set_xscale("log")
    axes[1, 1].invert_xaxis()
    axes[1, 1].set_yscale("symlog", linthresh=1.0)
    axes[1, 1].set(
        xlabel=r"same-orbit cutoff $\sigma\downarrow$",
        ylabel="raw / divergent action",
        title="(d) action finite-part ladder",
    )
    action_twin.set_ylabel("subtracted action")
    action_lines = axes[1, 1].lines + action_twin.lines
    axes[1, 1].legend(
        action_lines,
        [line.get_label() for line in action_lines],
        loc="best",
    )
    action_diagnostics = report["action_cutoff"]["diagnostics"]
    residual = finite_abs(report["moving_cut"]["moving_cut_additivity_residual"])
    axes[1, 1].text(
        0.04,
        0.08,
        f"last-3 subtracted spread = {float(action_diagnostics['last_three_subtracted_spread']):.2e}\n"
        f"moved-gate residual = {residual:.2e}\n"
        f"physical/compact density cross-check = {float(action_diagnostics['physical_compact_density_relative_defect_inf']):.2e}",
        transform=axes[1, 1].transAxes,
        fontsize=6.8,
    )
    badge(axes[1, 1], "COMPUTED/E1 CANDIDATE")
    figure.suptitle(
        "V3 — CONNECTED FLOATING CANDIDATE: sampled source window, generated labels, and same-orbit action\n"
        "finite cutoffs only — NOT_INTERVAL_VALIDATED (#7)",
        weight="bold",
    )
    save(figure, output, "figure_03_v3_pole_finite_part")


def figure_04(output: Path) -> None:
    report = load_json(output / "v4_v5_matched_candidate.json")
    outer_report = load_json(output / "v4_v5_outer_matching.json")
    data = np.load(output / "v4_v5_matched_candidate.npz")
    figure, axes = plt.subplots(2, 2, figsize=(10.8, 7.0), constrained_layout=True)
    diagnostics = report["diagnostics"]

    central = data["central_state"]
    axes[0, 0].plot(central[0], central[2], color=BLUE, label=r"central orbit $(U,V)$")
    axes[0, 0].scatter(
        [central[0, 0], central[0, -1]],
        [central[2, 0], central[2, -1]],
        color=[GREEN, ORANGE],
        marker="o",
        s=30,
        zorder=4,
    )
    midpoint = central.shape[1] // 2
    if midpoint + 2 < central.shape[1]:
        axes[0, 0].annotate(
            "",
            xy=(central[0, midpoint + 2], central[2, midpoint + 2]),
            xytext=(central[0, midpoint], central[2, midpoint]),
            arrowprops=dict(arrowstyle="->", color=BLACK),
        )
    axes[0, 0].text(.03, .08, "green: nonlinear $W^u$ source; orange: $U=-M$ cut", transform=axes[0, 0].transAxes)
    axes[0, 0].set(xlabel=r"central $U$", ylabel=r"central $V$", title="(a) nonlinear source → central cut")
    axes[0, 0].legend()
    badge(axes[0, 0], "COMPUTED/E1 CANDIDATE")

    k1_r1 = data["k1_r1"]
    k1_state = data["k1_state"]
    axes[0, 1].plot(k1_r1, k1_state[0], color=BLUE, label=r"$\Pi$")
    axes[0, 1].plot(k1_r1, k1_state[1], color=ORANGE, ls="--", label=r"$\Omega$")
    axes[0, 1].scatter(
        [k1_r1[0], k1_r1[-1]],
        [k1_state[0, 0], k1_state[0, -1]],
        facecolors="none",
        edgecolors=[GREEN, PURPLE],
        marker="o",
        s=34,
        zorder=4,
    )
    axes[0, 1].set(
        xlabel=r"resolved $K_1$ coordinate $r_1$",
        ylabel=r"resolved state $(\Pi,\Omega)$",
        title="(b) central interface → fixed-$r_1$ seam",
    )
    axes[0, 1].legend()
    badge(axes[0, 1], "COMPUTED/E1 CANDIDATE")

    compact_q = data["compact_q"]
    axes[1, 0].plot(compact_q, data["outer_beta"], color=BLUE, label=r"$\beta$")
    axes[1, 0].plot(compact_q, data["outer_alpha"], color=ORANGE, ls="--", label=r"$\alpha$")
    q_label = float(diagnostics["q_label"])
    axes[1, 0].axvline(compact_q[0], color=GREEN, ls=":", label=r"$Q_R$")
    axes[1, 0].axvline(q_label, color=PURPLE, ls="-.", label=r"$Q_{label}$")
    axes[1, 0].axvline(compact_q[-1], color=BLACK, ls=":", label=r"$Q_{end}$")
    axes[1, 0].set(
        xlabel=r"outer coordinate $Q=z^{-2}$",
        ylabel="outer normal coordinate",
        title="(c) same candidate on the finite outer graph",
    )
    axes[1, 0].legend(ncol=2)
    gamma_axis = axes[1, 0].inset_axes([.49, .12, .47, .35])
    full_gamma_saved = "gamma_beta0" in data.files
    if full_gamma_saved:
        gamma_beta = data["gamma_beta0"]
        gamma_alpha = data["gamma_alpha0"]
        gamma_label = r"independent finite-$Q$ $\Gamma(\beta)$ samples"
        gamma_beta_plot = gamma_beta
        gamma_alpha_plot = gamma_alpha
        seam_beta_plot = float(diagnostics["seam_beta"])
        seam_alpha_plot = float(diagnostics["seam_alpha"])
    else:
        gamma_beta = np.array(
            [diagnostics["leading_guess_beta"], diagnostics["seam_beta"]],
            dtype=float,
        )
        gamma_alpha = np.array(
            [diagnostics["leading_guess_gamma"], diagnostics["same_section_root_gamma"]],
            dtype=float,
        )
        gamma_label = r"stored independent $\Gamma_{Q_{end}}$ samples"
        gamma_beta_plot = 1.0e11 * (gamma_beta - float(diagnostics["seam_beta"]))
        gamma_alpha_plot = 1.0e11 * (gamma_alpha - float(diagnostics["same_section_root_gamma"]))
        seam_beta_plot = 0.0
        seam_alpha_plot = 1.0e11 * (
            float(diagnostics["seam_alpha"])
            - float(diagnostics["same_section_root_gamma"])
        )
    gamma_axis.scatter(
        gamma_beta_plot,
        gamma_alpha_plot,
        color=ORANGE,
        marker="^",
        s=24,
        label=gamma_label,
    )
    gamma_axis.scatter(
        [seam_beta_plot],
        [seam_alpha_plot],
        facecolors="none",
        edgecolors=BLUE,
        marker="o",
        s=42,
        label="coupled seam",
    )
    short_gamma = float(diagnostics["same_section_root_gamma"]) - float(
        diagnostics["gamma_horizon_difference_at_seam"]
    )
    gamma_axis.scatter(
        [seam_beta_plot],
        [short_gamma if full_gamma_saved else 1.0e11 * (short_gamma - float(diagnostics["same_section_root_gamma"]))],
        color=GRAY,
        marker="x",
        s=28,
        label=rf"short horizon $Q={float(diagnostics['gamma_short_horizon']):g}$",
    )
    if "gamma_horizon_at_seam" in data.files:
        gamma_axis.scatter(
            np.full_like(data["gamma_horizon_at_seam"], float(diagnostics["seam_beta"])),
            data["gamma_horizon_at_seam"],
            facecolors="none",
            edgecolors=GRAY,
            marker="s",
            s=18,
            label="stored horizon ladder at seam",
        )
    if full_gamma_saved:
        gamma_axis.set(xlabel=r"$\beta$", ylabel=r"$\alpha$", title="same-section root")
    else:
        gamma_axis.set(xlabel=r"$10^{11}(\beta-\beta_*)$", ylabel=r"$10^{11}(\alpha-\Gamma_*)$", title="same-section root")
    gamma_axis.tick_params(labelsize=5.5)
    gamma_axis.legend(fontsize=5.1)
    badge(axes[1, 0], "COMPUTED/E1 CANDIDATE")

    # Mixed panel: finite candidate residuals remain visually separate from
    # the infinite/uniform theorem objects that were not computed.
    axes[1, 1].axis("off")
    residual_axis = axes[1, 1].inset_axes([.02, .08, .53, .82])
    residual_names = ["BVP", r"$\Gamma$ root", r"$q_1$ seam", "central E", r"$K_1$ E", "outer E", "solver RMS"]
    residual_values = np.array(
        [
            finite_abs(diagnostics["boundary_and_interface_residual_inf"]),
            finite_abs(diagnostics["same_section_root_residual"]),
            finite_abs(diagnostics["central_k1_q1_interface_residual"]),
            finite_abs(diagnostics["central_energy_residual_inf"]),
            finite_abs(diagnostics["k1_energy_residual_inf"]),
            finite_abs(diagnostics["outer_energy_residual_inf"]),
            finite_abs(diagnostics["solver_rms_residual_max"]),
        ]
    )
    residual_axis.scatter(residual_values, np.arange(residual_values.size), color=BLUE, marker="o", s=22)
    if "gamma_solver_rms_residual" in data.files:
        gamma_qa = np.array(
            [
                np.max(np.abs(data["gamma_solver_rms_residual"])),
                np.max(np.abs(data["gamma_boundary_residual"])),
                np.max(np.abs(data["gamma_energy_residual"])),
            ],
            dtype=float,
        )
        residual_axis.scatter(
            np.maximum(gamma_qa, 1.0e-18),
            np.full(3, 1.0),
            color=ORANGE,
            marker="^",
            s=18,
            label=r"independent $\Gamma$: RMS/BC/E",
        )
        residual_axis.legend(fontsize=5.4, loc="lower right")
    residual_axis.set_xscale("log")
    residual_axis.set_yticks(np.arange(residual_values.size), residual_names, fontsize=6.0)
    residual_axis.invert_yaxis()
    residual_axis.set_xlabel("stored absolute diagnostic", fontsize=6.3)
    residual_axis.set_title("finite candidate QA", fontsize=7.0)
    residual_axis.tick_params(axis="x", labelsize=5.8)
    residual_axis.text(
        .02,
        .02,
        f"phase={float(report['source_phase']):.8f}; flight={float(report['central_flight_time']):.4f}\n"
        f"min $\\Pi$={float(diagnostics['minimum_k1_pi_scaled']):.3g}; min $\\pi$={float(diagnostics['minimum_outer_pi']):.3g}\n"
        f"arrival margins: scaled={diagnostics['scaled_arrival_margin_passed']}, unscaled={diagnostics['unscaled_arrival_margin_passed']}",
        transform=residual_axis.transAxes,
        fontsize=5.7,
    )
    missing_axis = axes[1, 1].inset_axes([.59, .08, .39, .82])
    missing_axis.set_facecolor("white")
    missing_axis.patch.set_hatch("///")
    missing_axis.patch.set_edgecolor(BLACK)
    missing_axis.set_xticks([])
    missing_axis.set_yticks([])
    exchange = outer_report["v5_analytic_nonexplicit_objects"]
    missing_axis.text(.06, .94, "FINITE HORIZON ONLY", va="top", weight="bold", fontsize=6.8)
    missing_axis.text(
        .06,
        .82,
        r"$\alpha(Q_{end})=0$" + "\n"
        + rf"$Q_R<Q_{{label}}<Q_{{end}}$: {diagnostics['q_r_q_label_separated']}\n"
        + rf"$|\Delta\Gamma_{{horizon}}|={abs(float(diagnostics['gamma_horizon_difference_at_seam'])):.2e}$",
        va="top",
        fontsize=6.1,
    )
    missing_axis.text(.06, .57, "NOT NUMERICALLY RESOLVED", va="top", weight="bold", fontsize=6.6, color=RED)
    missing_axis.text(
        .06,
        .47,
        "infinite/maximal V4 graph\nuniform tube and bunching\nendpoint adjoint / exchange\ninvertible matching derivative\nuniqueness and parameter jets",
        va="top",
        fontsize=5.8,
    )
    missing_axis.text(
        .06,
        .05,
        rf"frozen exact comparison: $144\sqrt{{3}}={float(exchange['frozen_exchange_pairing']):.6f}$",
        fontsize=5.7,
    )
    axes[1, 1].set_title("(d) finite diagnostics versus unfinished theorem objects")
    axes[1, 1].text(
        .98,
        .99,
        "MIXED: E1 / NOT INTERVAL",
        transform=axes[1, 1].transAxes,
        ha="right",
        va="top",
        fontsize=7,
        weight="bold",
        bbox=dict(boxstyle="round,pad=.25", facecolor="white", edgecolor=BLACK, hatch="///"),
        zorder=10,
    )
    figure.suptitle(
        "V4/V5 — COMPUTED/E1_MATCHED_CANDIDATE: nonlinear-$W^u$ → central → resolved-$K_1$ → outer\n"
        "independent finite-horizon Gamma check — NOT_INTERVAL_VALIDATED",
        weight="bold",
    )
    save(figure, output, "figure_04_v4_v5_outer_matching")


def figure_05(output: Path) -> None:
    report = load_json(output / "v5a_outer_finite_part.json")
    matched_report = load_json(output / "v4_v5_matched_candidate.json")
    data = np.load(output / "v4_v5a_outer.npz")
    figure, axes = plt.subplots(2, 2, figsize=(10.8, 7.0), constrained_layout=True)
    q = data["compact_q"]
    parameters = OuterParameters(**matched_report["parameters"])
    reference_length_density, reference_action_density, *_ = outer_physical_densities(
        q, data["reference_beta"], data["reference_alpha"], parameters
    )
    neighbor_length_density, neighbor_action_density, *_ = outer_physical_densities(
        q, data["neighbor_beta"], data["neighbor_alpha"], parameters
    )
    length_limit = float(report["diagnostics"]["length_density_scaled_limit"])
    action_limit = float(report["diagnostics"]["action_density_scaled_limit"])
    q_star = float(report["normalization"]["fixed_v5a_cut_q_star"])

    axes[0, 0].plot(q, reference_length_density * np.sqrt(q), color=GRAY, ls="--", label=r"reference $Q^{1/2}\mathcal{T}$")
    axes[0, 0].plot(q, neighbor_length_density * np.sqrt(q), color=BLUE, label=r"matched $Q^{1/2}\mathcal{T}$")
    axes[0, 0].axhline(length_limit, color=BLACK, ls=":", label=r"$1/(2q_*)$")
    density_twin = axes[0, 0].twinx()
    density_twin.plot(q, reference_action_density / q**1.5, color=GRAY, ls="-.", label=r"reference $Q^{-3/2}\mathcal{A}$")
    density_twin.plot(q, neighbor_action_density / q**1.5, color=ORANGE, ls="--", label=r"matched $Q^{-3/2}\mathcal{A}$")
    density_twin.axhline(action_limit, color=BLACK, ls=(0, (5, 2)), label=r"$-q_*/(2\delta)$")
    axes[0, 0].set(
        xlabel=r"same outer coordinate $Q$",
        ylabel=r"scaled length density",
        title="(a) exact densities with finite predicted scaling",
    )
    axes[0, 0].text(
        .02,
        .05,
        rf"fixed normalization $Q_*={q_star:g}$, $\beta_{{ref}}(Q_*)=0$",
        transform=axes[0, 0].transAxes,
        fontsize=6.2,
        bbox=dict(facecolor="white", edgecolor="none", alpha=.85),
    )
    density_twin.set_ylabel("scaled action density")
    density_lines = axes[0, 0].lines + density_twin.lines
    axes[0, 0].legend(density_lines, [line.get_label() for line in density_lines], ncol=2, loc="center right")
    gap_axis = axes[0, 0].inset_axes([.52, .08, .44, .27])
    sample = np.linspace(0, q.size - 1, 121, dtype=int)
    for gap, label, color, marker in (
        (neighbor_length_density - reference_length_density, r"$\Delta\mathcal{T}$", BLUE, "o"),
        (neighbor_action_density - reference_action_density, r"$\Delta\mathcal{A}$", ORANGE, "^"),
    ):
        positive = gap[sample] >= 0.0
        gap_axis.scatter(q[sample][positive], np.maximum(np.abs(gap[sample][positive]), 1e-30), color=color, marker=marker, s=7, label=label + " (+)")
        gap_axis.scatter(q[sample][~positive], np.maximum(np.abs(gap[sample][~positive]), 1e-30), facecolors="none", edgecolors=color, marker=marker, s=8, label=label + " (-)")
    gap_axis.set_yscale("log")
    gap_axis.set_title("signed same-Q density gaps", fontsize=6.1)
    gap_axis.tick_params(labelsize=5.2)
    badge(axes[0, 0], "COMPUTED/E1 CANDIDATE")

    neighboring_raw_length = cumulative_trapezoid_values(q, neighbor_length_density)
    axes[0, 1].plot(np.sqrt(q), neighboring_raw_length, color=BLUE, label="raw matched length")
    axes[0, 1].plot(np.sqrt(q), data["counterterm_length"], color=GRAY, ls="--", label="complete reference counterterm")
    length_inset = axes[0, 1].inset_axes([.52, .12, .44, .31])
    length_inset.plot(np.sqrt(q), data["relative_length"], color=BLUE, marker="o", markevery=max(1, q.size // 12), ms=2.4)
    length_inset.set_title("matched minus complete reference", fontsize=6.1)
    length_inset.tick_params(labelsize=5.2)
    axes[0, 1].axvline(np.sqrt(q[-1]), color=BLACK, lw=.9, ls=":")
    axes[0, 1].set(
        xlabel=r"$Q^{1/2}$",
        ylabel="truncated physical length",
        title="(b) raw length and complete reference counterterm",
    )
    axes[0, 1].legend(loc="center left")
    axes[0, 1].text(.98, .92, r"$Q>Q_{end}$ not computed", transform=axes[0, 1].transAxes, ha="right", fontsize=6.5, bbox=dict(facecolor="white", edgecolor=BLACK, hatch="///"))
    badge(axes[0, 1], "COMPUTED/E1 CANDIDATE")

    neighboring_raw_action = cumulative_trapezoid_values(q, neighbor_action_density)
    axes[1, 0].plot(q**2.5, neighboring_raw_action, color=BLUE, label="raw matched action")
    axes[1, 0].plot(q**2.5, data["counterterm_action"], color=GRAY, ls="--", label="complete reference counterterm")
    action_inset = axes[1, 0].inset_axes([.52, .13, .44, .31])
    action_inset.plot(q**2.5, data["relative_action"], color=BLUE, marker="o", markevery=max(1, q.size // 12), ms=2.4)
    action_inset.set_title("matched minus complete reference", fontsize=6.1)
    action_inset.tick_params(labelsize=5.2)
    axes[1, 0].axvline(q[-1] ** 2.5, color=BLACK, lw=.9, ls=":")
    axes[1, 0].set(
        xlabel=r"$Q^{5/2}$",
        ylabel="truncated physical action (signed)",
        title="(c) raw action and negative complete counterterm",
    )
    axes[1, 0].legend()
    badge(axes[1, 0], "COMPUTED/E1 CANDIDATE")

    axes[1, 1].axis("off")
    balances = report["balances"]
    grid_length_change = abs(float(data["finite_part_refined_length"][-1] - data["finite_part_refined_length"][-2]))
    grid_action_change = abs(float(data["finite_part_refined_action"][-1] - data["finite_part_refined_action"][-2]))
    horizon_action_change = abs(float(data["q_end_relative_action"][-1] - data["q_end_relative_action"][-2]))
    strict_composition_residual = abs(
        float(report["strict_composition"]["maximum_scaled_balance_residual"])
    )
    qa_rows = [
        ("cut additivity (max)", max(abs(float(balances["length_cut_balance"])), abs(float(balances["action_cut_balance"]))), "PASS", BLUE, "●"),
        ("reference change", abs(float(balances["synthetic_reference_change_balance"])), "PASS", BLUE, "●"),
        ("gauge coboundary", abs(float(balances["exact_gauge_composition_balance"])), "PASS", BLUE, "●"),
        ("output-grid Δ length", grid_length_change, "PASS", BLUE, "●"),
        ("output-grid Δ action", grid_action_change, "PASS", BLUE, "●"),
        ("outer-only horizon Δ action", horizon_action_change, "INCONCLUSIVE", ORANGE, "▲"),
        ("finite-grid composition identity", strict_composition_residual, "DERIVED", BLACK, "◆"),
    ]
    axes[1, 1].text(.67, .88, "value / status", transform=axes[1, 1].transAxes, weight="bold", fontsize=7.2)
    for index, (name, value, status, color, marker) in enumerate(qa_rows):
        y = .77 - .105 * index
        axes[1, 1].text(.02, y, name, transform=axes[1, 1].transAxes, fontsize=6.8)
        value_text = "—" if value is None else f"{value:.2e}"
        axes[1, 1].text(.64, y, marker, transform=axes[1, 1].transAxes, color=color, fontsize=9, weight="bold")
        axes[1, 1].text(.70, y, f"{value_text}  {status}", transform=axes[1, 1].transAxes, fontsize=6.6)
    axes[1, 1].text(.02, .015, "grid threshold = 2e-3; balance threshold = 1e-8\nhorizon row is an independent outer-only proxy", transform=axes[1, 1].transAxes, fontsize=6.2)
    axes[1, 1].set_title("(d) cutoff, grid, horizon, and bookkeeping")
    badge(axes[1, 1], "COMPUTED/QA; HORIZON INCONCLUSIVE", unresolved=True)
    figure.suptitle(
        "V5A — FIXED-$Q_*$ MATCHED/REFERENCE CANDIDATE: scaled densities and complete counterterms\n"
        "finite Q only — improper limits and uniform covariance NOT_INTERVAL_VALIDATED",
        weight="bold",
    )
    save(figure, output, "figure_05_v5a_algebraic_finite_part")


EVENT_STYLE = {
    "return+": (BLUE, "o"),
    "return-": (ORANGE, "^"),
    "stable_cut_proxy": (BLACK, "|"),
    "pole_gate_proxy": (RED, "D"),
    "algebraic_gate_proxy": (PURPLE, "s"),
    "escape_unresolved": (GRAY, "x"),
    "time_limit_unresolved": (GRAY, "o"),
}


def figure_06(output: Path) -> None:
    report = load_json(output / "v6_events.json")
    data = np.load(output / "v6_events.npz")
    figure, axes = plt.subplots(2, 2, figsize=(10.8, 7.0), constrained_layout=True)
    names = data["event_name"]
    for event in np.unique(names):
        mask = names == event
        color, marker = EVENT_STYLE.get(str(event), (GRAY, "x"))
        marker_options: dict[str, Any] = {"color": color}
        if marker not in {"|", "x"}:
            marker_options = {
                "facecolors": "none" if "unresolved" in str(event) else color,
                "edgecolors": color,
            }
        axes[0, 0].scatter(
            data["phase"][mask],
            data["transverse_coordinate"][mask],
            s=22,
            marker=marker,
            label=str(event),
            alpha=.8,
            **marker_options,
        )
    axes[0, 0].set(xlabel="numerical canonical eigenplane phase", ylabel="source transverse coordinate", title="(a) finite source-section first events")
    axes[0, 0].legend(ncol=2)
    axes[0, 0].text(
        .98,
        .92,
        r"return $+/-$: target transverse sign",
        transform=axes[0, 0].transAxes,
        ha="right",
        va="top",
        fontsize=7.1,
        bbox=dict(facecolor="white", edgecolor="none", alpha=.85),
    )
    badge(axes[0, 0], "COMPUTED/E1 FINITE SAMPLE")

    adaptive = np.char.startswith(data["sample_tag"].astype(str), "adaptive")
    for event in np.unique(names[adaptive]):
        mask = adaptive & (names == event)
        color, marker = EVENT_STYLE.get(str(event), (GRAY, "x"))
        axes[0, 1].scatter(data["phase"][mask], data["transverse_coordinate"][mask], s=32, color=color, marker=marker, label=str(event))
    axes[0, 1].set(xlabel="source phase", ylabel="source transverse coordinate", title="(b) periodic-anchor adaptive neighborhoods")
    axes[0, 1].ticklabel_format(axis="both", style="plain", useOffset=False)
    axes[0, 1].legend()
    badge(axes[0, 1], "COMPUTED/E1; BOUNDARIES UNRESOLVED")

    order = sorted(report["event_counts"])
    counts = [report["event_counts"][name] for name in order]
    colors = [EVENT_STYLE.get(name, (GRAY, "x"))[0] for name in order]
    axes[1, 0].barh(np.arange(len(order)), counts, color=colors, hatch=["//" if "unresolved" in name else "" for name in order])
    axes[1, 0].set_yticks(np.arange(len(order)), order)
    axes[1, 0].set(xlabel="finite sample count", title="(c) observed labels (not a cell census)")
    badge(axes[1, 0], "COMPUTED/QA")

    branches = report.get("complete_return_branches", [])
    if branches:
        short_labels = [branch_label(branch) for branch in branches]
        locations = np.arange(len(branches))
        lengths = [float(branch["observables"]["physical_length"]) for branch in branches]
        actions = [float(branch["observables"]["physical_action"]) for branch in branches]
        axes[1, 1].bar(locations - .17, lengths, width=.34, color=BLUE, label="physical length")
        summary_twin = axes[1, 1].twinx()
        summary_twin.bar(locations + .17, actions, width=.34, color=ORANGE, hatch="//", label="physical action")
        axes[1, 1].set_xticks(locations, short_labels)
        axes[1, 1].set_ylabel("complete-return length")
        summary_twin.set_ylabel("complete-return action")
        summary_lines = [
            mpl.patches.Patch(facecolor=BLUE, label="physical length"),
            mpl.patches.Patch(facecolor=ORANGE, hatch="//", label="physical action"),
        ]
        axes[1, 1].legend(handles=summary_lines, loc="upper center")
        target_signs = "\n".join(
            f"{label} → {branch['target']['sign_proxy']}"
            for label, branch in zip(short_labels, branches)
        )
        axes[1, 1].text(
            .03,
            .88,
            "target transverse signs\n" + target_signs,
            transform=axes[1, 1].transAxes,
            va="top",
            fontsize=7.1,
            bbox=dict(facecolor="white", edgecolor="none", alpha=.82),
        )
    else:
        axes[1, 1].text(.5, .55, "no complete-return candidate saved", ha="center", transform=axes[1, 1].transAxes)
        axes[1, 1].set_xticks([])
    axes[1, 1].set_title("(d) selected complete-return branch summary")
    badge(axes[1, 1], "COMPUTED/E1 CANDIDATE")
    figure.suptitle(
        "V6 — finite source-section atlas plus selected complete return candidates\n"
        "target-sign semantics fixed / exhaustive cells and winding labels NOT INTERVAL VALIDATED",
        weight="bold",
    )
    save(figure, output, "figure_06_v6_first_event_cells")


def figure_07(output: Path) -> None:
    report = load_json(output / "v7_patterns.json")
    event_report = load_json(output / "v6_events.json")
    complete = np.load(output / "v6_complete_branches.npz")
    figure, axes = plt.subplots(2, 2, figsize=(10.8, 7.0), constrained_layout=True)
    desired_order = {"B1": 0, "A2": 1}
    branches = sorted(
        event_report.get("complete_return_branches", []),
        key=lambda branch: desired_order.get(branch_label(branch), 99),
    )

    def draw_cumulative(axis: plt.Axes, branch: dict[str, Any], panel: str) -> None:
        prefix = branch_array_prefix(branch)
        length_lines = []
        action_twin = axis.twinx()
        for index, segment in enumerate(branch["segments"]):
            segment_prefix = f"{prefix}_segment_{index}_{segment['name']}"
            xi = complete[f"{segment_prefix}_xi"]
            length = complete[f"{segment_prefix}_physical_length"]
            action = complete[f"{segment_prefix}_physical_action"]
            style = "-" if index == 0 else "--"
            segment_name = "global" if index == 0 else "local saddle"
            length_lines += axis.plot(xi, length, color=BLUE, ls=style, label=f"length: {segment_name}")
            length_lines += action_twin.plot(xi, action, color=ORANGE, ls=style, label=f"action: {segment_name}")
            if index == 1:
                axis.axvline(xi[0], color=BLACK, ls=":", lw=.9)
        axis.set(xlabel=r"central time $\xi$", ylabel="cumulative physical length", title=f"({panel}) {branch_label(branch)} complete return")
        action_twin.set_ylabel("cumulative physical action")
        axis.legend(length_lines, [line.get_label() for line in length_lines], ncol=2, loc="best")
        residual = max(
            finite_abs(branch["diagnostics"]["segment_length_composition_residual"]),
            finite_abs(branch["diagnostics"]["segment_action_composition_residual"]),
        )
        axis.text(.03, .06, f"dotted seam; composition residual = {residual:.2e}", transform=axis.transAxes, fontsize=7.0)
        badge(axis, "COMPUTED/E1 CANDIDATE")

    for axis, index, panel in ((axes[0, 0], 0, "a"), (axes[0, 1], 1, "b")):
        if index < len(branches):
            draw_cumulative(axis, branches[index], panel)
        else:
            axis.text(.5, .5, "complete branch unavailable", ha="center", transform=axis.transAxes)
            axis.set_title(f"({panel}) complete return")

    for index, branch in enumerate(branches):
        prefix = branch_array_prefix(branch)
        color = COLORS[index]
        for segment_index, segment in enumerate(branch["segments"]):
            segment_prefix = f"{prefix}_segment_{segment_index}_{segment['name']}"
            length = complete[f"{segment_prefix}_physical_length"]
            action = complete[f"{segment_prefix}_physical_action"]
            axes[1, 0].plot(
                length,
                action,
                color=color,
                ls="-" if segment_index == 0 else "--",
                label=branch_label(branch) if segment_index == 0 else None,
            )
            if segment_index == 1:
                axes[1, 0].scatter(length[0], action[0], color=color, marker="D", s=24, zorder=4)
    axes[1, 0].set(
        xlabel="cumulative physical length",
        ylabel="cumulative physical action",
        title="(c) one observable record across the segment seam",
    )
    axes[1, 0].legend()
    axes[1, 0].text(.03, .06, "solid: global; dashed: local; diamond: stitched seam", transform=axes[1, 0].transAxes, fontsize=7.0)
    badge(axes[1, 0], "COMPUTED/E1 CANDIDATE")

    periodic = report["periodic_orbits"]
    period_twin = axes[1, 1].twinx()
    all_lines = []
    for family, marker, color, style in (("A", "o", BLUE, "-"), ("B", "s", ORANGE, "--")):
        chosen = [row for row in periodic if row["family"] == family]
        k = np.array([row["relative_winding"] for row in chosen])
        period = np.array([row["diagnostics"]["physical_period"] for row in chosen])
        action = np.array([row["physical_action"] for row in chosen])
        all_lines += axes[1, 1].plot(k, period, marker=marker, color=color, ls=style, label=f"{family}: period")
        all_lines += period_twin.plot(k, action, marker=marker, color=color, ls=":", label=f"{family}: action")
    axes[1, 1].set(xlabel="relative winding metadata k", ylabel="physical period", title="(d) retained periodic length/action trend")
    period_twin.set_ylabel("closed physical action")
    axes[1, 1].legend(all_lines, [line.get_label() for line in all_lines], ncol=2)
    badge(axes[1, 1], "COMPUTED/E1")
    figure.suptitle(
        "V6/V7 — B1/A2 complete finite-return records and periodic trends\n"
        "shared augmented IVPs / selected candidates only / NOT INTERVAL VALIDATED",
        weight="bold",
    )
    save(figure, output, "figure_07_v6_length_action")


def figure_08(output: Path) -> None:
    report = load_json(output / "v7_patterns.json")
    periodic = np.load(output / "v7_periodic.npz")
    multipulse = np.load(output / "v7_multipulses.npz")
    figure, axes = plt.subplots(2, 2, figsize=(11.2, 7.2), constrained_layout=True)
    orbit_rows = report["periodic_orbits"]
    for index, row in enumerate(orbit_rows):
        stem = f"{row['family']}{row['relative_winding']}"
        x = periodic[f"{stem}_physical_x"]
        u = periodic[f"{stem}_physical_u"]
        axes[0, 0].plot(x, u - 1.0, color=COLORS[index], ls=STYLES[index], label=stem)
    axes[0, 0].set(xlabel="physical x", ylabel=r"$u(x)-a$", title="(a) actual reversible periodic stationary profiles")
    axes[0, 0].legend(ncol=2)
    badge(axes[0, 0], "COMPUTED/E1")

    for index, count in enumerate((1, 2)):
        x = multipulse[f"pulse_{count}_physical_x"]
        u = multipulse[f"pulse_{count}_physical_u"]
        axes[0, 1].plot(x, u - 1.0, color=COLORS[index], ls=STYLES[index], label=f"{count} pulse")
    axes[0, 1].set(xlabel="physical x", ylabel=r"$u(x)-a$", title="(b) one- and two-pulse profiles")
    axes[0, 1].legend()
    badge(axes[0, 1], "COMPUTED/E1 FULL ODE")

    for index, count in enumerate((3, 4)):
        x = multipulse[f"pulse_{count}_physical_x"]
        u = multipulse[f"pulse_{count}_physical_u"]
        axes[1, 0].plot(x, u - 1.0, color=COLORS[index + 2], ls=STYLES[index + 2], label=f"{count} pulses")
    axes[1, 0].set(xlabel="physical x", ylabel=r"$u(x)-a$", title="(c) three- and four-pulse profiles")
    axes[1, 0].legend()
    badge(axes[1, 0], "COMPUTED/E1 FULL ODE")

    axis = axes[1, 1]
    pulse_rows = report["multipulses"]
    counts = np.array([row["pulse_count_requested"] for row in pulse_rows])
    pde = np.array([max(row["diagnostics"]["physical_stationary_u_residual_inf"], row["diagnostics"]["physical_stationary_v_residual_inf"]) for row in pulse_rows])
    energy = np.array([row["diagnostics"]["hamiltonian_drift"] for row in pulse_rows])
    axis.semilogy(counts, pde, "o-", color=BLUE, label="physical PDE residual")
    axis.semilogy(counts, energy, "s--", color=ORANGE, label="Hamiltonian drift")
    axis.axhline(2e-6, color=BLACK, ls=":", label="multipulse PDE gate")
    axis.set(xlabel="observed macro-pulse count", ylabel="residual", title="(d) profile QA and coding boundary")
    axis.text(0.03, .08, "A/B labels and pulse counts are not verified V7 edge words.\nBi-infinite numerical orbit: NOT RESOLVED.", transform=axis.transAxes)
    axis.legend()
    badge(axis, "COMPUTED/QA; ITINERARY OPEN", unresolved=True)
    figure.suptitle(
        "V7 — computed stationary PDE profiles at positive parameters\n"
        "existence in the computed ODE does not imply temporal stability or Turing selection",
        weight="bold",
    )
    save(figure, output, "figure_08_v7_patterns")


def figure_09(output: Path) -> None:
    qa = load_json(output / "qa.json")
    config = load_json(Path(__file__).resolve().parent / "config" / "vdp_v1_v7.json")
    manifest = load_json(output / "manifest.json")
    contract = load_json(output / "v6_candidate_contract.json")
    v1 = load_json(output / "v1_structure.json")
    v2 = load_json(output / "v2_central.json")
    v3 = load_json(output / "v3_pole.json")
    v4 = load_json(output / "v4_v5_outer_matching.json")
    matched = load_json(output / "v4_v5_matched_candidate.json")
    v5a = load_json(output / "v5a_outer_finite_part.json")
    v6 = load_json(output / "v6_events.json")
    v7 = load_json(output / "v7_patterns.json")
    bridge_data = np.load(output / "v1_bridge.npz")
    pole_data = np.load(output / "v3_pole.npz")
    outer_data = np.load(output / "v4_v5a_outer.npz")
    acceptance = config["acceptance"]
    figure = plt.figure(figsize=(11.2, 7.3), constrained_layout=True)
    grid = figure.add_gridspec(2, 2)

    # Threshold-normalized residuals: x=1 is the frozen pass boundary.
    axis = figure.add_subplot(grid[0, 0])
    v2_samples = v2["parameter_slices"]["r_slice"]["samples"]
    v5_diagnostics = matched["diagnostics"]
    v5a_balance = max(
        abs(float(v5a["balances"][key]))
        for key in ("length_cut_balance", "action_cut_balance", "synthetic_reference_change_balance", "exact_gauge_composition_balance")
    )
    v5a_grid_change = max(
        abs(float(outer_data["finite_part_refined_length"][-1] - outer_data["finite_part_refined_length"][-2])),
        abs(float(outer_data["finite_part_refined_action"][-1] - outer_data["finite_part_refined_action"][-2])),
    )
    branch_composition_ratio = max(
        max(
            abs(float(branch["diagnostics"]["segment_length_composition_residual"])) / 1.0e-12,
            abs(float(branch["diagnostics"]["segment_action_composition_residual"])) / 1.0e-14,
        )
        for branch in v6["complete_return_branches"]
    )
    residual_rows = [
        ("V1 independent state", float(bridge_data["refinement_state_defect"][-1]), float(acceptance["independent_difference"])),
        ("V2 normalized ODE", max(float(row["diagnostics"]["normalized_ode_residual_inf"]) for row in v2_samples), float(acceptance.get("scaled_ode_residual", 1.0e-7))),
        ("V2 energy drift", max(float(row["diagnostics"]["hamiltonian_drift"]) for row in v2_samples), float(acceptance["energy_drift"])),
        ("V3 global/local overlap", max(float(v3["diagnostics"]["global_local_physical_relative_defect_inf"]), float(v3["diagnostics"]["global_local_compact_relative_defect_inf"])), float(acceptance["independent_difference"])),
        ("V3 moved cut", abs(float(v3["moving_cut"]["moving_cut_additivity_residual"])), 2.0e-7),
        ("V3 density cross-check", abs(float(v3["action_cutoff"]["diagnostics"]["physical_compact_density_relative_defect_inf"])), 1.0e-10),
        ("V5 interfaces/root", max(abs(float(v5_diagnostics[key])) for key in ("boundary_and_interface_residual_inf", "same_section_root_residual", "central_k1_q1_interface_residual")), 1.0e-7),
        ("V5 central/K1/outer energy", max(abs(float(v5_diagnostics[key])) for key in ("central_energy_residual_inf", "k1_energy_residual_inf", "outer_energy_residual_inf")), 1.0e-6),
        ("V5A cut/reference/gauge", v5a_balance, 1.0e-8),
        ("V5A output-grid change", v5a_grid_change, float(acceptance["finite_part_grid_difference"])),
        ("V6 segment composition", branch_composition_ratio, 1.0),
        ("V7 periodic closure", max(float(row["diagnostics"]["closure_residual"]) for row in v7["periodic_orbits"]), float(acceptance["closure_residual"])),
        ("V7 stationary PDE", max(max(float(row["diagnostics"]["physical_stationary_u_residual_inf"]), float(row["diagnostics"]["physical_stationary_v_residual_inf"])) for row in v7["multipulses"]), float(acceptance["multipulse_physical_fd_residual"])),
    ]
    metric_display = {
        "v3_source_graph_boundary_residual": "V3 source-graph boundary",
        "v3_gate_residual": "V3 gate event",
        "v3_gate_energy_drift": "V3 gate energy",
        "v4_gamma_solver_rms_residual": "V4 Gamma solver RMS",
        "v4_gamma_boundary_residual": "V4 Gamma boundary",
        "v4_gamma_energy_residual": "V4 Gamma energy",
        "v5_coupled_bvp_rms_residual": "V5 coupled BVP RMS",
        "v5_same_section_root_residual": "V5 same-section root",
        "v5a_endpoint_grid_difference": "V5A endpoint grid",
        "v6_complete_face_residual": "V6 complete-return faces",
        "v6_complete_energy_defect": "V6 complete-return energy",
        "v6_complete_action_quadrature_difference": "V6 action quadrature",
    }
    if qa.get("metrics"):
        # Preserve central and PDE cross-formulation rows, and prefer the
        # master's frozen measured/threshold wiring for candidate interfaces.
        preserved = [residual_rows[index] for index in (0, 1, 11, 12)]
        wired = []
        for key, label in metric_display.items():
            metric = qa["metrics"].get(key)
            if metric is not None and metric.get("comparator", "<=") in {"<=", "<"}:
                wired.append((label, float(metric["measured"]), float(metric["threshold"])))
        residual_rows = preserved + wired
    residual_ratios = np.array([finite_abs(value / threshold) for _, value, threshold in residual_rows])
    residual_y = np.arange(len(residual_rows))
    passed = residual_ratios <= 1.0
    axis.scatter(residual_ratios[passed], residual_y[passed], color=BLUE, marker="o", s=24, label="pass")
    axis.scatter(residual_ratios[~passed], residual_y[~passed], color=RED, marker="x", s=30, label="fail")
    axis.axvline(1.0, color=BLACK, ls="--", label="frozen threshold")
    axis.set_xscale("log")
    axis.set_yticks(residual_y, [row[0] for row in residual_rows], fontsize=5.8)
    axis.invert_yaxis()
    axis.set(xlabel="measured / frozen threshold", title="(a) threshold-normalized residuals")
    axis.legend(fontsize=6.2)
    badge(axis, "COMPUTED/QA")

    # Refinement and sensitivity: ratios below one improve; open circles are
    # required studies for which the frozen run has no ladder.
    axis = figure.add_subplot(grid[0, 1])
    pole_changes = np.abs(np.diff(pole_data["action_subtracted"]))
    grid_changes = np.abs(np.diff(outer_data["finite_part_refined_action"]))
    horizon_changes = np.abs(np.diff(outer_data["q_end_relative_action"]))
    max_event_refinement = max(abs(float(row["event_time_difference"])) for row in v6["refinement"])
    convergence_rows = [
        ("V1 tolerance ladder (last/first)", finite_abs(float(bridge_data["refinement_state_defect"][-1] / bridge_data["refinement_state_defect"][0])), "ratio", BLUE, "o"),
        ("V2 domain enlargement", None, "NOT RUN", GRAY, "o"),
        ("V3 cutoff ladder (last/first)", finite_abs(float(pole_changes[-1] / pole_changes[0])), "ratio", BLUE, "o"),
        ("V4 Gamma horizon / root tol", finite_abs(abs(float(v5_diagnostics["gamma_horizon_difference_at_seam"])) / float(config["matched_outer"].get("independent_root_tolerance", config["matched_outer"]["same_section_root_residual_tolerance"]))), "threshold", BLUE, "o"),
        ("V5A output grid (last/first)", finite_abs(float(grid_changes[-1] / grid_changes[0])), "ratio", BLUE, "o"),
        ("outer-only horizon (last/first)", finite_abs(float(horizon_changes[-1] / horizon_changes[0])), "INCONCLUSIVE", ORANGE, "^"),
        ("V6 step-halving relative change", finite_abs(max_event_refinement / max(float(sample["event_time_xi"]) for sample in v6["samples"])), "ratio", BLUE, "o"),
        ("directed-rounding replay", None, "NOT RUN", GRAY, "o"),
    ]
    y = np.arange(len(convergence_rows))
    for index, (_, value, status, color, marker) in enumerate(convergence_rows):
        if value is None:
            axis.scatter([1.0e-8], [index], facecolors="none", edgecolors=color, marker=marker, s=30)
            axis.text(1.8e-8, index, status, va="center", fontsize=5.8, color=color)
        else:
            axis.scatter([value], [index], color=color, marker=marker, s=26)
            if status == "INCONCLUSIVE":
                axis.text(value * 1.3, index, status, va="center", fontsize=5.6, color=ORANGE)
    axis.axvline(1.0, color=BLACK, ls="--", label="threshold / no-improvement ratio")
    axis.set_xscale("log")
    axis.set_yticks(y, [row[0] for row in convergence_rows], fontsize=5.9)
    axis.invert_yaxis()
    axis.set(xlabel="dimensionless last-step or threshold ratio", title="(b) refinement and finite-horizon sensitivity")
    axis.legend(fontsize=6.0)
    badge(axis, "COMPUTED/QA")

    axis = figure.add_subplot(grid[1, 0])
    stages = ["V1", "V2", "V3", "V4", "V5", "V5A", "V6", "V7"]
    coverage_rows = [
        ("finite / exact object", ["E/D"] + ["E1"] * 7),
        ("numerical QA", ["QA"] * 8),
        ("uniform / infinite target", ["—", "NI", "NI", "NI", "NI", "NI", "R#7", "NR"]),
        ("atlas / coding target", ["—", "—", "—", "—", "—", "—", "NR", "NR"]),
    ]
    coverage_style = {
        "E/D": (PALE, None, BLACK),
        "E1": (BLUE, None, "white"),
        "QA": ("#BBDDF0", "..", BLACK),
        "NI": ("white", "///", BLACK),
        "R#7": ("white", "xx", BLACK),
        "NR": ("white", "\\\\", BLACK),
        "—": (PALE, None, GRAY),
    }
    for row_index, (_row_name, statuses) in enumerate(coverage_rows):
        for column, status in enumerate(statuses):
            facecolor, hatch, text_color = coverage_style[status]
            axis.add_patch(mpl.patches.Rectangle((column - .46, row_index - .42), .92, .84, facecolor=facecolor, edgecolor=BLACK, hatch=hatch))
            axis.text(column, row_index, status, ha="center", va="center", color=text_color, weight="bold", fontsize=6.6)
    axis.set_xlim(-0.55, len(stages) - 0.45)
    axis.set_ylim(len(coverage_rows) - .35, -.55)
    axis.set_xticks(np.arange(len(stages)), stages)
    axis.set_yticks(np.arange(len(coverage_rows)), [row[0] for row in coverage_rows], fontsize=6.4)
    axis.text(.0, -.18, "E/D EXACT/DERIVED   E1 COMPUTED/E1   QA COMPUTED/QA   NI NOT_INTERVAL_VALIDATED\nR#7 RIGOROUS-ONLY (#7)   NR NOT NUMERICALLY RESOLVED", transform=axis.transAxes, fontsize=5.7, va="top")
    axis.set_title("(c) object-by-object coverage; no completeness score")
    badge(axis, "MIXED COVERAGE")

    axis = figure.add_subplot(grid[1, 1])
    axis.axis("off")
    source_hashes = manifest["source_hashes"]
    result_hashes = manifest["result_hashes"]
    environment = manifest["environment"]
    provenance_lines = [
        f"configuration_version: {manifest['configuration_version']}  (frozen {config['frozen_before_claim_bearing_run']})",
        f"parameters: r={manifest['parameters']['primary']['r']}, a2={manifest['parameters']['primary']['a2']}, epsilon={manifest['parameters']['primary']['epsilon']}",
        f"repository: {manifest['repository_commit'][:12]}  dirty={manifest['repository_dirty']}",
        f"environment: Python {environment['python'].split()[0]}, NumPy {environment['numpy']}, SciPy {environment['scipy']}",
        f"config hash: {source_hashes['numerics/config/vdp_v1_v7.json'][:16]}",
        f"runner hash: {source_hashes['numerics/run_vdp_master.py'][:16]}",
        f"V3 result hash: {result_hashes['v3_pole.json'][:16]}",
        f"candidate contract: claim_bearing={contract['claim_bearing']}, final_status={contract['final_status']}",
        "reproduce: python3 numerics/run_vdp_master.py",
    ]
    axis.text(.03, .88, "\n".join(provenance_lines), transform=axis.transAxes, va="top", family="monospace", fontsize=6.6, bbox=dict(boxstyle="round,pad=.4", facecolor=PALE, edgecolor=BLACK))
    axis.text(.03, .36, "GLOBAL NONCLAIMS", transform=axis.transAxes, weight="bold", fontsize=7.2)
    nonclaim_text = "\n".join("• " + item for item in manifest["nonclaims"])
    axis.text(.04, .31, nonclaim_text, transform=axis.transAxes, va="top", fontsize=6.5, wrap=True)
    axis.set_title("(d) frozen provenance and reproduction boundary")
    badge(axis, "EXACT/DERIVED PROVENANCE")
    figure.suptitle(
        "V1–V7 van der Pol numerical atlas — normalized QA, convergence, coverage, and provenance",
        weight="bold",
    )
    save(figure, output, "figure_09_numerical_qa")


def render_all(output: Path) -> None:
    configure_style()
    config = load_json(_REPOSITORY_ROOT / "numerics" / "config" / "vdp_v1_v7.json")
    manifest = load_json(output / "manifest.json")
    validate_render_provenance(config, manifest)
    for function in (
        figure_01,
        figure_02,
        figure_03,
        figure_04,
        figure_05,
        figure_06,
        figure_07,
        figure_08,
        figure_09,
    ):
        function(output)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    render_all(arguments.output.resolve())
