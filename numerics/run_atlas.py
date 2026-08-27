#!/usr/bin/env python3
"""Compute the theorem-to-PDE numerical atlas and write figures/data."""

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

from rfsn_numerics import (
    brusselator_observables,
    common_slope_fit,
    compute_periodic_orbit,
    continue_homoclinics,
    reflected_profile,
)


COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]
PROFILE_LINESTYLES = ["-", "--", "-.", ":", (0, (5, 1)), (0, (3, 1, 1, 1))]


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 220,
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "legend.fontsize": 7.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "lines.linewidth": 1.7,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def save_figure(figure: plt.Figure, output: Path, stem: str) -> None:
    for suffix in ("pdf", "svg", "png"):
        figure.savefig(output / f"{stem}.{suffix}", bbox_inches="tight")
    plt.close(figure)


def figure_dictionary(output: Path) -> None:
    figure = plt.figure(figsize=(10.2, 5.6), constrained_layout=True)
    grid = figure.add_gridspec(2, 5, height_ratios=[0.7, 1.0])
    top = figure.add_subplot(grid[0, :])
    top.axis("off")
    boxes = [
        (0.02, "stationary PDE\n$u_t=v_t=0$"),
        (0.27, "4D spatial ODE\n$x$ is orbit time"),
        (0.52, "return / coding\ngeometry"),
        (0.77, "bounded stationary\nspatial profile"),
    ]
    for x, label in boxes:
        top.text(
            x,
            0.52,
            label,
            transform=top.transAxes,
            ha="left",
            va="center",
            bbox=dict(boxstyle="round,pad=.45", fc="#F4F7FA", ec="#4C6478"),
        )
    for x0, x1 in zip((0.18, 0.43, 0.68), (0.265, 0.515, 0.765)):
        top.annotate(
            "",
            xy=(x1, 0.52),
            xytext=(x0, 0.52),
            xycoords=top.transAxes,
            arrowprops=dict(arrowstyle="->", lw=1.5, color="#4C6478"),
        )
    top.text(0.01, 0.96, "SCHEMATIC — theorem-to-pattern dictionary", transform=top.transAxes, weight="bold")

    x = np.linspace(-4.0, 4.0, 500)
    examples = [
        (np.zeros_like(x), "equilibrium", "flat state"),
        (np.exp(-x * x), "homoclinic", "localized pulse"),
        (0.55 * np.cos(2.8 * x), "periodic orbit", "periodic stripe"),
        (
            np.exp(-3.5 * (x + 1.35) ** 2) + 0.9 * np.exp(-3.5 * (x - 1.35) ** 2),
            "admissible finite word",
            "multipulse",
        ),
        (
            0.35 * np.sin(2.4 * x) + 0.18 * np.sin(np.sqrt(2.0) * 3.1 * x),
            "nonperiodic bi-infinite word",
            "stationary aperiodic",
        ),
    ]
    for index, (values, orbit_name, profile_name) in enumerate(examples):
        axis = figure.add_subplot(grid[1, index])
        axis.plot(x, values, color=COLORS[index % len(COLORS)])
        axis.axhline(0.0, color="#777777", lw=0.6)
        axis.set_xticks([])
        axis.set_yticks([])
        axis.set_title(f"{orbit_name}\n" + r"$\Downarrow$  " + profile_name)
        if index == 3:
            axis.text(0.5, -0.2, "word length = macro-pulse count", transform=axis.transAxes, ha="center", fontsize=7)
        if index == 4:
            axis.text(0.5, -0.2, "spatial complexity, not temporal chaos", transform=axis.transAxes, ha="center", fontsize=7)
    top.text(
        0.985,
        0.05,
        "Exit branches are terminal and are not bounded patterns.",
        transform=top.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.5,
        color="#555555",
    )
    save_figure(figure, output, "figure_01_theorem_to_patterns")


def power_fit(x: np.ndarray, y: np.ndarray, count: int = 4) -> tuple[float, float]:
    slope, intercept = np.polyfit(np.log(x[:count]), np.log(y[:count]), 1)
    return float(slope), float(intercept)


def figure_brusselator(output: Path, results: list, observations: list[dict[str, float]]) -> dict[str, float]:
    figure, axes = plt.subplots(2, 3, figsize=(11.2, 6.7), constrained_layout=True)
    parameter_colors = [
        mpl.colormaps["viridis"](0.08 + 0.84 * index / max(1, len(results) - 1))
        for index in range(len(results))
    ]
    chosen = [0, len(results) // 2, len(results) - 1]
    for result_index in chosen:
        result = results[result_index]
        xi, state = reflected_profile(result)
        r = result.r
        x = r * xi
        label = rf"$d={r**4:.1e}$"
        style = PROFILE_LINESTYLES[result_index]
        color = parameter_colors[result_index]
        axes[0, 0].plot(x, r * r * state[0], color=color, ls=style, label=label)
        axes[0, 1].plot(x, r**4 * state[2], color=color, ls=style, label=label)
    axes[0, 0].set(title="physical activator pulse", xlabel="$x$", ylabel="$u_d-1$")
    axes[0, 1].set(title="physical inhibitor pulse", xlabel="$x$", ylabel="$v_d-1$")
    axes[0, 0].legend()
    axes[0, 1].legend()

    for index, result in enumerate(results):
        xi, state = reflected_profile(result)
        color = parameter_colors[index]
        style = PROFILE_LINESTYLES[index]
        axes[0, 2].plot(xi, state[0], color=color, ls=style, alpha=0.9, label=rf"$r={result.r:.3f}$")
        axes[1, 0].plot(xi, state[2], color=color, ls=style, alpha=0.9)
    axes[0, 2].set(xlim=(-8, 8), title="activator scaling collapse", xlabel=r"$\xi=x/d^{1/4}$", ylabel=r"$(u_d-1)/d^{1/2}=U_r$")
    axes[1, 0].set(xlim=(-8, 8), title="inhibitor scaling collapse", xlabel=r"$\xi=x/d^{1/4}$", ylabel=r"$(v_d-1)/d=V_r$")
    axes[0, 2].legend(ncol=1, loc="upper right")

    d = np.array([row["d"] for row in observations])
    amp_u = np.array([row["amplitude_u"] for row in observations])
    amp_v = np.array([row["amplitude_v"] for row in observations])
    width_u = np.array([row["width_u"] for row in observations])
    width_v = np.array([row["width_v"] for row in observations])
    slope_u, intercept_u = power_fit(d, amp_u)
    slope_v, intercept_v = power_fit(d, amp_v)
    slope_wu, intercept_wu = power_fit(d, width_u)
    slope_wv, intercept_wv = power_fit(d, width_v)
    axes[1, 1].loglog(d, amp_u, "o-", color=COLORS[0], label=rf"$\|u-1\|_\infty$; fit {slope_u:.3f}")
    axes[1, 1].loglog(d, amp_v, "s-", color=COLORS[1], label=rf"$\|v-1\|_\infty$; fit {slope_v:.3f}")
    axes[1, 1].loglog(d, np.exp(intercept_u) * d**0.5, "--", color=COLORS[0], alpha=0.65, label="reference slope $1/2$")
    axes[1, 1].loglog(d, np.exp(intercept_v) * d, ":", color=COLORS[1], alpha=0.75, label="reference slope $1$")
    axes[1, 1].set(title="amplitude laws (fit: smallest four $d$)", xlabel="$d$", ylabel="amplitude")
    axes[1, 1].legend()
    axes[1, 1].grid(True, which="both", alpha=0.2)

    axes[1, 2].loglog(d, width_u, "o-", color=COLORS[2], label=rf"$W_u$; fit {slope_wu:.3f}")
    axes[1, 2].loglog(d, width_v, "s--", color=COLORS[3], label=rf"$W_v$; fit {slope_wv:.3f}")
    axes[1, 2].loglog(d, np.exp(intercept_wu) * d**0.25, ":", color="#444444", alpha=0.8, label="reference slope $1/4$")
    axes[1, 2].set(title="half-height widths (fit: smallest four $d$)", xlabel="$d$", ylabel="physical width")
    axes[1, 2].legend()
    axes[1, 2].grid(True, which="both", alpha=0.2)

    figure.suptitle(
        "COMPUTED/E1 — positive-diffusion Brusselator homoclinic branch\n"
        + r"$A=B=1,\quad d=r^4$",
        weight="bold",
    )
    save_figure(figure, output, "figure_02_brusselator_scaling")
    return {
        "amplitude_u_slope": slope_u,
        "amplitude_v_slope": slope_v,
        "width_u_slope": slope_wu,
        "width_v_slope": slope_wv,
    }


def figure_vdp(output: Path, orbits: list, slope_fit: dict[str, object], r: float, epsilon: float) -> dict[str, float]:
    figure, axes = plt.subplots(2, 2, figsize=(10.6, 7.0), constrained_layout=True)
    family_a = [orbit for orbit in orbits if orbit.family == "A"]
    for index, orbit in enumerate(family_a):
        color = COLORS[index]
        style = PROFILE_LINESTYLES[index]
        axes[0, 0].plot(
            orbit.physical_x,
            orbit.physical_u - 1.0,
            color=color,
            ls=style,
            label=rf"relative winding $k={orbit.relative_winding}$",
        )
        local_mask = np.linalg.norm(orbit.state, axis=0) < 0.25
        if np.any(local_mask):
            axes[0, 1].plot(
                orbit.physical_x,
                np.where(local_mask, orbit.state[0], np.nan),
                color=color,
                ls=style,
                label=rf"$k={orbit.relative_winding}$",
            )
    axes[0, 0].set(title="physical profiles, family A (color/style = $k$)", xlabel="$x$", ylabel="$u(x)-a$")
    axes[0, 0].legend()
    axes[0, 1].axhline(0.0, color="#666666", lw=0.7)
    axes[0, 1].set(
        ylim=(-0.15, 0.15),
        xlim=(0.4, 1.75),
        title=r"local saddle block $\|Z\|<0.25$: color/style = $k$",
        xlabel="$x$",
        ylabel="scaled central coordinate $U$",
    )
    axes[0, 1].text(
        0.03,
        0.94,
        r"$k=0$ does not enter this displayed block",
        transform=axes[0, 1].transAxes,
        va="top",
        fontsize=7.5,
        color="#555555",
    )
    axes[0, 1].legend()

    expected_slope = 2.0 * np.pi * r / (epsilon**0.25 * (1.0 / np.sqrt(2.0)))
    for family, marker, color, style in (("A", "o", COLORS[0], "-"), ("B", "s", COLORS[1], "--")):
        selected = sorted((orbit for orbit in orbits if orbit.family == family), key=lambda item: item.relative_winding)
        k = np.array([orbit.relative_winding for orbit in selected], dtype=float)
        period = np.array([orbit.diagnostics["physical_period"] for orbit in selected])
        axes[1, 0].plot(k, period, marker=marker, color=color, ls="none", label=f"family {family}: computed")
        intercept = slope_fit["intercepts"][family]
        axes[1, 0].plot(k, intercept + slope_fit["slope"] * k, color=color, ls=style, alpha=0.75, label=f"family {family}: common-slope fit")
    axes[1, 0].set(title="period law (marker/color = family)", xlabel="relative winding $k$", ylabel="physical period $L$")
    axes[1, 0].text(
        0.03,
        0.96,
        rf"fit slope $={slope_fit['slope']:.6f}$" + "\n" + rf"V7 coefficient $2\pi r/\beta={expected_slope:.6f}$",
        transform=axes[1, 0].transAxes,
        va="top",
        bbox=dict(fc="white", ec="#BBBBBB", alpha=0.9),
    )
    axes[1, 0].legend()

    for family, marker, color, style in (("A", "o", COLORS[0], "-"), ("B", "s", COLORS[1], "--")):
        selected = sorted((orbit for orbit in orbits if orbit.family == family), key=lambda item: item.relative_winding)
        k = np.array([orbit.relative_winding for orbit in selected], dtype=float)
        action = np.array([orbit.physical_action for orbit in selected])
        axes[1, 1].plot(k, action, marker=marker, color=color, ls=style, label=f"family {family}")
    axes[1, 1].set(title="closed physical action (exploratory convergence signal)", xlabel="relative winding $k$", ylabel=r"$\oint\lambda_\delta$")
    axes[1, 1].ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
    axes[1, 1].legend()
    figure.suptitle(
        "COMPUTED/E1 — van der Pol zero-energy reversible periodic orbits\n"
        + rf"$r={r:g},\ \epsilon={epsilon:g},\ a_2=0,\ a=1,\ d={r**4:.3e}$",
        weight="bold",
    )
    save_figure(figure, output, "figure_03_vdp_winding_and_period")
    return {
        "expected_period_slope": expected_slope,
        "fitted_period_slope": float(slope_fit["slope"]),
        "period_slope_relative_error": float(abs(slope_fit["slope"] - expected_slope) / expected_slope),
    }


def figure_context(output: Path, sample_d: np.ndarray, vdp_d: float) -> None:
    figure, axes = plt.subplots(2, 2, figsize=(10.8, 7.0), constrained_layout=True)
    d = np.logspace(-8, -2, 400)
    gap_b = (1.0 + np.sqrt(d)) ** 2 - 1.0
    axes[0, 0].loglog(d, gap_b, color=COLORS[0], label=r"exact gap $B_T(d)-1$")
    axes[0, 0].scatter(
        sample_d,
        np.full_like(sample_d, 0.055),
        transform=axes[0, 0].get_xaxis_transform(),
        marker="|",
        color=COLORS[1],
        s=90,
        zorder=3,
        label=r"computed $d$ on selected path $B=1$",
    )
    axes[0, 0].set(title="Brusselator ($A=1$): neutral-curve gap above $B=1$", xlabel="$d$", ylabel=r"$B_T(d)-1$")
    axes[0, 0].text(
        0.03,
        0.13,
        "markers encode horizontal location only",
        transform=axes[0, 0].transAxes,
        fontsize=7.2,
        color="#555555",
        bbox=dict(fc="white", ec="none", alpha=0.82, pad=0.2),
    )
    axes[0, 0].legend()
    axes[0, 0].grid(True, which="both", alpha=0.2)

    d_v = np.logspace(-8, np.log10(0.24), 400)
    gap_a = 1.0 - np.sqrt(1.0 - 2.0 * np.sqrt(d_v))
    axes[0, 1].loglog(d_v, gap_a, color=COLORS[2], label=r"exact gap $1-a_T(d)$")
    axes[0, 1].scatter(
        [vdp_d],
        [0.055],
        transform=axes[0, 1].get_xaxis_transform(),
        marker="|",
        color=COLORS[3],
        s=110,
        zorder=3,
        label=r"computed $d$ on selected path $a=1$",
    )
    axes[0, 1].set(title=r"van der Pol ($\epsilon=1$): finite-wave neutral gap below $a=1$", xlabel="$d$", ylabel=r"$1-a_T(d)$")
    axes[0, 1].text(
        0.03,
        0.13,
        r"$a=1$: $k=0$ Hopf/marginality; marker gives $d$ only",
        transform=axes[0, 1].transAxes,
        fontsize=7.2,
        color="#555555",
        bbox=dict(fc="white", ec="none", alpha=0.82, pad=0.2),
    )
    axes[0, 1].legend()
    axes[0, 1].grid(True, which="both", alpha=0.2)

    geometry = axes[1, 0]
    geometry.axis("off")
    labels = [
        (0.04, 0.65, "saddle-focus\nlocal winding"),
        (0.39, 0.65, "$K_2\\to K_1$\nmatching"),
        (0.73, 0.78, "outer algebraic\ncanard-organized exit"),
        (0.73, 0.31, "finite-distance\npole exit"),
    ]
    for x, y, label in labels:
        geometry.text(x, y, label, transform=geometry.transAxes, ha="left", va="center", bbox=dict(boxstyle="round,pad=.35", fc="#F4F7FA", ec="#617789"))
    for start, end in [((0.27, 0.65), (0.39, 0.65)), ((0.60, 0.65), (0.73, 0.78)), ((0.60, 0.60), (0.73, 0.34))]:
        geometry.annotate("", xy=end, xytext=start, xycoords=geometry.transAxes, arrowprops=dict(arrowstyle="->", color="#4C6478", lw=1.5))
    geometry.annotate("bounded return", xy=(0.08, 0.48), xytext=(0.48, 0.44), xycoords=geometry.transAxes, arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.35", color=COLORS[0]), ha="center", color=COLORS[0])
    geometry.set_title("SCHEMATIC — canard organization and high winding are distinct")

    ladder = axes[1, 1]
    ladder.axis("off")
    steps = [
        (0.82, "analytic theorem", "existence and organization"),
        (0.59, "computed stationary profile", "shape, scaling, period"),
        (0.36, "temporal spectrum/simulation", "selection and stability"),
        (0.13, "experiment", "calibration and observation"),
    ]
    for index, (y, title, subtitle) in enumerate(steps):
        ladder.text(0.08, y, f"{index + 1}", transform=ladder.transAxes, ha="center", va="center", color="white", bbox=dict(boxstyle="circle", fc=COLORS[index]))
        ladder.text(0.17, y + 0.025, title, transform=ladder.transAxes, weight="bold", va="center")
        ladder.text(0.17, y - 0.045, subtitle, transform=ladder.transAxes, color="#555555", va="center")
        if index < len(steps) - 1:
            ladder.annotate("", xy=(0.08, y - 0.14), xytext=(0.08, y - 0.07), xycoords=ladder.transAxes, arrowprops=dict(arrowstyle="->", color="#777777"))
    ladder.set_title("Application chain: atlas reaches stationary-profile stage")
    figure.suptitle("MIXED — Turing, canard, and what the theorem does not decide", weight="bold")
    save_figure(figure, output, "figure_04_turing_canard_context")


def serializable_diagnostics(result: object) -> dict[str, object]:
    return {
        "model": result.model,
        "r": result.r,
        "d": result.r**4,
        "epsilon": result.epsilon,
        "a2": result.a2,
        "domain": result.domain,
        "diagnostics": result.diagnostics,
        "center": result.solution.y[:, 0].tolist(),
        "tail": result.solution.y[:, -1].tolist(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "results" / "atlas")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    configure_style()

    figure_dictionary(output)

    brusselator_r = [0.025, 0.03535533905932738, 0.05, 0.07071067811865475, 0.1, np.sqrt(0.02)]
    brusselator = continue_homoclinics(
        "brusselator", brusselator_r, domain=24.0, tolerance=1.0e-8
    )
    observations = [brusselator_observables(result) for result in brusselator]
    scaling = figure_brusselator(output, brusselator, observations)

    # A longer/tighter BVP fixes the homoclinic center accurately enough to
    # resolve periodic roots whose distance is exponentially small.
    vdp_r = 0.08
    vdp_homoclinics = continue_homoclinics(
        "vdp", [0.02, 0.04, 0.06, vdp_r], a2=0.0, epsilon=1.0, domain=26.0, tolerance=2.0e-10
    )
    vdp_homoclinic = vdp_homoclinics[-1]
    center_u = float(vdp_homoclinic.solution.y[0, 0])
    specifications = [
        # A targets are transverse Q=0 events with P as residual.
        ("A", 0, (-0.0062, -0.0046), 0, 3, 1),
        # B targets lie on U=P=Q=0, where Q=0 is cubic/nontransverse;
        # use the transverse P=0 event and Q as the residual instead.
        ("B", 0, (0.00017, 0.00032), 1, 1, 3),
        ("A", 1, (-1.8e-5, -8.0e-6), 1, 3, 1),
        ("B", 1, (3.0e-7, 6.2e-7), 2, 1, 3),
        ("A", 2, (-3.5e-8, -1.0e-8), 2, 3, 1),
    ]
    orbits = [
        compute_periodic_orbit(
            family=family,
            relative_winding=winding,
            bracket=bracket,
            event_index=event_index,
            center_u=center_u,
            r=vdp_r,
            a2=0.0,
            epsilon=1.0,
            event_component=event_component,
            residual_component=residual_component,
        )
        for family, winding, bracket, event_index, event_component, residual_component in specifications
    ]
    fit = common_slope_fit(orbits)
    period_summary = figure_vdp(output, orbits, fit, vdp_r, 1.0)
    figure_context(output, np.array([row["d"] for row in observations]), vdp_r**4)

    np.savez_compressed(
        output / "brusselator_profiles.npz",
        r=np.array(brusselator_r),
        xi=np.linspace(-24.0, 24.0, 6001),
        state=np.stack([reflected_profile(result)[1] for result in brusselator]),
    )
    np.savez_compressed(
        output / "vdp_periodic_orbits.npz",
        **{
            f"{orbit.family}{orbit.relative_winding}_{name}": value
            for orbit in orbits
            for name, value in (
                ("xi", orbit.xi),
                ("state", orbit.state),
                ("physical_x", orbit.physical_x),
                ("physical_u", orbit.physical_u),
                ("physical_v", orbit.physical_v),
            )
        },
    )
    source_files = [
        Path(__file__).resolve(),
        Path(__file__).resolve().with_name("rfsn_numerics.py"),
    ]
    manifest = {
        "evidence_status": "COMPUTED/E1 non-rigorous floating-point numerics",
        "nonclaims": [
            "not task #7 interval validation",
            "no explicit theorem box is certified by these parameter samples",
            "finite periodic samples do not prove asymptotic accumulation",
            "neutral/Turing curves are context only; no stationary branch connection is inferred",
            "no temporal spectral or nonlinear stability conclusion",
            "no experimental calibration",
        ],
        "software": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "matplotlib": mpl.__version__,
            "platform": platform.platform(),
        },
        "source_sha256": {
            source.name: hashlib.sha256(source.read_bytes()).hexdigest()
            for source in source_files
        },
        "solver_settings": {
            "homoclinic_method": "scipy.integrate.solve_bvp",
            "brusselator_domain_xi": 24.0,
            "brusselator_tolerance": 1.0e-8,
            "vdp_homoclinic_domain_xi": 26.0,
            "vdp_homoclinic_tolerance": 2.0e-10,
            "periodic_integrator": "DOP853",
            "periodic_primary_rtol": 1.0e-12,
            "periodic_primary_atol": 1.0e-14,
            "periodic_primary_max_step": 0.008,
            "periodic_independent_max_step": 0.004,
        },
        "brusselator": {
            "parameters": {"A": 1.0, "B": 1.0, "r": brusselator_r},
            "homoclinics": [serializable_diagnostics(result) for result in brusselator],
            "observables": observations,
            "scaling_fits_smallest_four": scaling,
        },
        "van_der_pol": {
            "parameters": {"r": vdp_r, "d": vdp_r**4, "a2": 0.0, "a": 1.0, "epsilon": 1.0},
            "homoclinic": serializable_diagnostics(vdp_homoclinic),
            "periodic_orbits": [
                {
                    "family": orbit.family,
                    "relative_winding": orbit.relative_winding,
                    "initial_offset_from_homoclinic": orbit.initial_offset,
                    "half_period_xi": orbit.half_period_xi,
                    "central_action": orbit.central_action,
                    "physical_action": orbit.physical_action,
                    "diagnostics": orbit.diagnostics,
                }
                for orbit in orbits
            ],
            "common_slope_fit": fit,
            "period_law_summary": period_summary,
        },
        "reproduction": "python3 numerics/run_atlas.py",
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output": str(output), "scaling": scaling, "period": period_summary}, indent=2))


if __name__ == "__main__":
    main()
