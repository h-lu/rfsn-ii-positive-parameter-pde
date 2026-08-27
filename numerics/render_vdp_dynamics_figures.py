#!/usr/bin/env python3
"""Render dynamics-screening figures only from frozen saved diagnostics."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_CONFIG = ROOT / "numerics/config/vdp_dynamics_screening.json"
DEFAULT_OUTPUT = ROOT / "numerics/results/vdp_dynamics_screening"

BLUE = "#0072B2"
ORANGE = "#D55E00"
GREEN = "#009E73"
PURPLE = "#8E44AD"
YELLOW = "#E69F00"
RED = "#B22222"
BLACK = "#222222"
GRAY = "#6C757D"
PALE_BLUE = "#EAF2F8"
PALE_RED = "#FBE9E7"
PALE_GRAY = "#F3F5F7"
COLORS = [BLUE, ORANGE, GREEN, PURPLE, YELLOW]
MARKERS = ["o", "s", "^", "D", "v"]


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 220,
            "font.size": 8.4,
            "axes.titlesize": 9.3,
            "axes.labelsize": 8.4,
            "legend.fontsize": 7.0,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "lines.linewidth": 1.45,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_render_contract(output: Path, config_path: Path) -> dict[str, Any]:
    config = load_json(config_path)
    # Import lazily to keep this renderer usable from the runner that creates
    # the contract.  The single census implementation remains in the runner.
    from numerics.run_vdp_dynamics_screening import (  # noqa: PLC0415
        source_files_for,
        validate_config,
    )

    validate_config(config)
    contract = load_json(output / "render_contract.json")
    if contract["configuration_version"] != config["configuration_version"]:
        raise ValueError("stale dynamics render contract: configuration version differs")
    if contract["configuration_sha256"] != sha256(config_path):
        raise ValueError("stale dynamics render contract: configuration hash differs")
    if contract.get("claim_bearing") is not False:
        raise ValueError("dynamics figure renderer accepts only non-claim-bearing input")
    expected_paths = source_files_for(config_path, config)
    expected = {str(path.relative_to(ROOT)): path for path in expected_paths}
    recorded = contract.get("source_files")
    if not isinstance(recorded, dict) or set(recorded) != set(expected):
        raise ValueError("stale dynamics render contract: source file census differs")
    for relative, path in expected.items():
        if recorded.get(relative) != sha256(path):
            raise ValueError(
                f"stale dynamics render contract: source hash differs for {relative}"
            )
    return config


def badge(axis: plt.Axes, label: str, *, exact: bool = False, stopped: bool = False) -> None:
    face = "white" if exact or stopped else PALE_BLUE
    edge = BLACK if exact else (RED if stopped else BLUE)
    axis.text(
        0.015,
        0.985,
        label,
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontsize=6.7,
        weight="bold",
        bbox=dict(
            boxstyle="round,pad=.23",
            facecolor=face,
            edgecolor=edge,
            hatch="///" if stopped else None,
        ),
        zorder=20,
    )


def save(figure: plt.Figure, output: Path, stem: str) -> None:
    for suffix in ("pdf", "svg", "png"):
        figure.savefig(output / f"{stem}.{suffix}", bbox_inches="tight")
    plt.close(figure)


def _complex_array(data: np.lib.npyio.NpzFile, prefix: str) -> np.ndarray:
    return np.asarray(data[f"{prefix}_real"]) + 1j * np.asarray(
        data[f"{prefix}_imag"]
    )


def figure_d1(output: Path, config: dict[str, Any]) -> None:
    report = load_json(output / "turing_report.json")
    with np.load(output / "turing_arrays.npz", allow_pickle=False) as archive:
        arrays = {key: np.asarray(archive[key]) for key in archive.files}
    figure, axes = plt.subplots(2, 2, figsize=(10.8, 7.0), constrained_layout=True)

    axis = axes[0, 0]
    axis.axis("off")
    axis.text(
        0.50,
        0.79,
        r"homogeneous stability: $\alpha=f'(a)>0$",
        transform=axis.transAxes,
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=.45", fc=PALE_BLUE, ec=BLUE),
    )
    axis.text(
        0.50,
        0.50,
        r"finite-$k$ stationary zero: $\alpha\leq-2r^2\sqrt{\epsilon}<0$",
        transform=axis.transAxes,
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=.45", fc=PALE_RED, ec=RED),
    )
    axis.annotate(
        "",
        xy=(0.50, 0.60),
        xytext=(0.50, 0.70),
        xycoords=axis.transAxes,
        arrowprops=dict(arrowstyle="<->", color=BLACK, lw=1.2),
    )
    axis.text(
        0.50,
        0.20,
        "incompatible signs\nclassical stationary Turing onset is excluded",
        transform=axis.transAxes,
        ha="center",
        va="center",
        weight="bold",
        color=RED,
    )
    axis.set_title("(a) exact two-by-two symbol obstruction")
    badge(axis, "EXACT/DERIVED", exact=True)

    axis = axes[0, 1]
    k = arrays["primary_k"]
    axis.plot(k, arrays["primary_leading_growth_rate"], color=BLUE, label="spectral abscissa")
    axis.axhline(0.0, color=BLACK, lw=.9)
    axis.scatter([0.0], [0.0], facecolors="white", edgecolors=RED, zorder=5, label=r"$k=0$ Hopf boundary")
    axis.set(
        ylim=(-1.02, .04),
        xlabel=r"physical wave number $k$",
        ylabel=r"$\Re\lambda(k)$",
        title="(b) frozen V7 point: no finite-$k$ stationary band",
    )
    axis.text(.98, .90, "the second branch is more negative\nand omitted to keep the leading rate visible", transform=axis.transAxes, ha="right", va="top", fontsize=6.5, bbox=dict(fc="white", ec=GRAY, alpha=.9))
    primary = config["primary_parameters"]
    axis.text(
        .98,
        .08,
        rf"$(r,a_2,\epsilon)=({primary['r']:g},{primary['a2']:g},{primary['epsilon']:g})$",
        transform=axis.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.5,
        bbox=dict(fc="white", ec=GRAY, alpha=.9),
    )
    axis.grid(True, alpha=.2)
    axis.legend(loc="lower right")
    badge(axis, "COMPUTED/E1")

    axis = axes[1, 0]
    remote = report["wide_stationary_band_witness_at_primary_r_epsilon"]
    roots = remote["stationary"]["k_roots"]
    axis.plot(
        arrays["remote_k"],
        arrays["remote_leading_growth_rate"],
        color=ORANGE,
        label=rf"remote diagnostic $a_2={config['turing']['remote_nonclassical_a2']:g}$",
    )
    axis.axhline(0.0, color=BLACK, lw=.9)
    if len(roots) == 2:
        axis.axvspan(roots[0], roots[1], color=RED, alpha=.10, label="finite-$k$ real-unstable band")
        axis.axvline(roots[0], color=RED, ls=":", lw=1)
        axis.axvline(roots[1], color=RED, ls=":", lw=1)
    axis.scatter([0], [remote["zero_mode_spectral_abscissa"]], color=RED, s=28, zorder=5, label=r"$k=0$ already unstable")
    axis.set(
        ylim=(-.04, .015),
        xlabel=r"physical wave number $k$",
        ylabel=r"spectral abscissa",
        title="(c) finite-$k$ band after long-wave destabilization",
    )
    axis.text(.03, .07, "deep stable trough clipped\n(full minimum about -0.97)", transform=axis.transAxes, fontsize=6.5, bbox=dict(fc="white", ec=GRAY, alpha=.9))
    axis.text(
        .97,
        .07,
        rf"$(r,a_2,\epsilon)=({primary['r']:g},{config['turing']['remote_nonclassical_a2']:g},{primary['epsilon']:g})$",
        transform=axis.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.5,
        bbox=dict(fc="white", ec=GRAY, alpha=.9),
    )
    axis.grid(True, alpha=.2)
    axis.legend(loc="best")
    badge(axis, "COMPUTED/E1 — NOT CLASSICAL TURING", stopped=True)

    axis = axes[1, 1]
    r = arrays["threshold_r"]
    threshold = arrays["threshold_near_a_equals_one_a2_threshold"]
    axis.plot(r, threshold, color=RED, lw=1.7, label=r"stationary-band threshold near $a=1$")
    box = config["issue_7_preselected_box"]
    axis.fill_between(
        [box["r"][0], box["r"][1]],
        box["a2"][0],
        box["a2"][1],
        color=GRAY,
        alpha=.22,
        label="preselected Issue #7 box projection",
    )
    primary = config["primary_parameters"]
    axis.scatter([primary["r"]], [primary["a2"]], color=BLUE, marker="*", s=70, label="frozen profile point", zorder=5)
    axis.axhline(float(config["turing"]["remote_nonclassical_a2"]), color=ORANGE, ls="--", label="remote diagnostic slice")
    counts = report["frozen_cartesian_slice_scan"]["regime_counts"]
    count_text = "frozen $3^3$ grid\n" + "\n".join(
        f"{name.replace('_', ' ').lower()}: {value}" for name, value in counts.items()
    )
    axis.text(.98, .97, count_text, transform=axis.transAxes, ha="right", va="top", fontsize=6.6, bbox=dict(fc="white", ec=GRAY, alpha=.9))
    axis.set(
        xlim=(float(r[0]), float(r[-1])),
        xlabel=r"$r$",
        ylabel=r"$a_2$",
        title="(d) threshold is far outside the frozen slice",
    )
    axis.grid(True, alpha=.2)
    axis.legend(loc="lower left")
    badge(axis, "MIXED: DERIVED CURVE + SAMPLED POINTS")

    figure.suptitle(
        "Temporal homogeneous-state screen — V7 existence is not a Turing-selection theorem",
        weight="bold",
    )
    save(figure, output, "figure_d1_turing_obstruction")


def figure_d2(output: Path) -> None:
    report = load_json(output / "bloch_report.json")
    with np.load(output / "bloch_arrays.npz", allow_pickle=False) as archive:
        labels = [str(value) for value in archive["labels"]]
        theta = np.asarray(archive["theta"])
        leading = _complex_array(archive, "leading_eigenvalues")
        abscissa = np.asarray(archive["spectral_abscissa"])
        translation = _complex_array(archive, "translation_eigenvalues")
        translation_residual = np.asarray(archive["translation_residuals"])
        refinement_theta = np.asarray(archive["refinement_theta"])
        refinement = np.asarray(archive["refinement_defects"])
        conjugacy = np.asarray(archive["conjugacy_defects"])
    figure, axes = plt.subplots(2, 2, figsize=(10.8, 7.1), constrained_layout=True)

    axis = axes[0, 0]
    selected = [0, len(labels) - 1]
    for selected_index, color, marker in zip(selected, (BLUE, ORANGE), ("o", "^"), strict=True):
        values = leading[selected_index].reshape(-1)
        axis.scatter(values.real, values.imag, s=10, alpha=.55, color=color, marker=marker, label=labels[selected_index])
    x_min, x_max = axis.get_xlim()
    if x_max > 0.0:
        axis.axvspan(0.0, x_max, color=RED, alpha=.08, zorder=-5)
    axis.axvline(0.0, color=BLACK, lw=.9)
    axis.set(
        xlabel=r"$\Re\lambda$",
        ylabel=r"$\Im\lambda$",
        title="(a) sampled leading Bloch spectral clouds",
    )
    axis.grid(True, alpha=.2)
    axis.legend(title="numerical family")
    badge(axis, "COMPUTED/E1 FINITE MATRIX")

    axis = axes[0, 1]
    for index, label in enumerate(labels):
        axis.plot(theta / np.pi, abscissa[index], marker=MARKERS[index], ms=3.1, color=COLORS[index], label=label)
    axis.axhline(0.0, color=BLACK, lw=.9)
    axis.set(
        xlabel=r"Bloch phase $\theta/\pi$",
        ylabel=r"sampled $\max\Re\lambda$",
        title="(b) all five saved periodic profiles",
    )
    axis.grid(True, alpha=.2)
    axis.legend(ncol=2)
    badge(axis, "COMPUTED/E1 BLOCH GRID")

    axis = axes[1, 0]
    x = np.arange(len(labels))
    axis.semilogy(
        x,
        np.maximum(np.abs(translation), 1e-18),
        "o-",
        color=BLUE,
        markerfacecolor="white",
        markeredgecolor=BLUE,
        label=r"$|\lambda_{trans}|$ (open: expected neutral)",
    )
    axis.semilogy(x, np.maximum(translation_residual, 1e-18), "s--", color=ORANGE, label="translation-vector residual")
    axis.set_xticks(x, labels)
    axis.set(
        xlabel="saved numerical family",
        ylabel="absolute diagnostic",
        title="(c) co-periodic translation-neutral diagnostic",
    )
    axis.grid(True, which="both", alpha=.2)
    axis.legend()
    badge(axis, "COMPUTED/QA")

    axis = axes[1, 1]
    for refinement_index, phase in enumerate(refinement_theta):
        axis.semilogy(x, np.maximum(refinement[:, refinement_index], 1e-18), marker=MARKERS[refinement_index], label=rf"grid match $\theta/\pi={phase/np.pi:g}$")
    axis.semilogy(x, np.maximum(conjugacy, 1e-18), "x:", color=BLACK, label=r"$\theta\leftrightarrow-\theta$ conjugacy")
    axis.set_xticks(x, labels)
    axis.set(
        xlabel="saved numerical family",
        ylabel="eigenvalue-set matching defect",
        title="(d) first resolution and symmetry checks",
    )
    axis.grid(True, which="both", alpha=.2)
    axis.legend(loc="best")
    outcomes = {row["label"]: row["screening_outcome"] for row in report["profiles"]}
    unstable = [label for label in labels if "INSTABILITY" in outcomes[label]]
    axis.text(.98, .04, "sampled positive growth: " + (", ".join(unstable) if unstable else "none"), transform=axis.transAxes, ha="right", va="bottom", fontsize=6.7, bbox=dict(fc="white", ec=RED if unstable else GRAY, hatch="///" if unstable else None))
    badge(axis, "COMPUTED/QA — NOT A SPECTRAL PROOF", stopped=True)

    figure.suptitle(
        "Periodic-profile Bloch prescreen — sampled instability can be detected, stability cannot be proved",
        weight="bold",
    )
    save(figure, output, "figure_d2_periodic_bloch_screen")


def figure_d3(output: Path) -> None:
    report = load_json(output / "pulse_temporal_report.json")
    with np.load(output / "screening_profiles.npz", allow_pickle=False) as archive:
        profile_arrays = {key: np.asarray(archive[key]) for key in archive.files}
    figure, axes = plt.subplots(2, 2, figsize=(10.8, 7.1), constrained_layout=True)

    axis = axes[0, 0]
    offset_step = 0.045
    for index, pulse_count in enumerate(range(1, 5)):
        x = profile_arrays[f"pulse_{pulse_count}_physical_x"]
        u = profile_arrays[f"pulse_{pulse_count}_physical_u"]
        axis.plot(x, u - 1.0 + index * offset_step, color=COLORS[index], label=f"{pulse_count} pulse" + ("" if index == 0 else f" (+{index} offset)"))
    axis.axhline(0.0, color=BLACK, lw=.8, ls=":")
    axis.set(
        xlabel="physical space $x$",
        ylabel=r"$u(x)-1$ (vertical offsets shown)",
        title="(a) saved stationary localized profiles",
    )
    axis.legend(loc="best")
    axis.grid(True, alpha=.18)
    badge(axis, "COMPUTED/E1 STATIONARY PROFILES")

    axis = axes[0, 1]
    pulse_counts = np.asarray([row["pulse_count"] for row in report["profiles"]])
    spectrum_keys = (
        ("fine_neumann", "o-", BLUE, "fine Neumann"),
        ("fine_periodic", "s--", ORANGE, "fine periodic"),
        ("coarse_neumann", "^:", GREEN, "coarse Neumann"),
    )
    for key, style, color, label in spectrum_keys:
        values = [
            row["refined_real_axis_spectra"][key][
                "leading_real_axis_candidate"
            ]["real"]
            for row in report["profiles"]
        ]
        axis.plot(pulse_counts, values, style, color=color, label=label)
    axis.axhline(0.0, color=BLACK, lw=.9)
    axis.set_xticks(pulse_counts)
    axis.set(
        xlabel="pulse count",
        ylabel="refined real-axis growth candidate",
        title="(b) high-resolution grid and boundary comparison",
    )
    axis.grid(True, alpha=.2)
    axis.legend()
    badge(axis, "COMPUTED/E1 FINITE WINDOW")

    axis = axes[1, 0]
    for index, row in enumerate(report["profiles"]):
        leading_run = row["short_time_runs"]["fine_neumann_leading_mode_half_dt"]
        generic_run = row["short_time_runs"]["fine_neumann_half_dt"]
        leading_time = np.asarray(leading_run["sample_times"])
        leading_rms = np.asarray(leading_run["sample_rms"]) / float(
            leading_run["initial_perturbation_rms"]
        )
        generic_time = np.asarray(generic_run["sample_times"])
        generic_rms = np.asarray(generic_run["sample_rms"]) / float(
            generic_run["initial_perturbation_rms"]
        )
        axis.semilogy(
            leading_time,
            leading_rms,
            color=COLORS[index],
            marker=MARKERS[index],
            markevery=max(1, len(leading_time) // 8),
            ms=3,
            label=f"pulse {row['pulse_count']}: leading mode",
        )
        axis.semilogy(
            generic_time,
            generic_rms,
            color=COLORS[index],
            ls="--",
            alpha=.78,
            label=f"pulse {row['pulse_count']}: generic",
        )
    axis.axhline(1.0, color=BLACK, lw=.8, ls=":")
    axis.set(
        xlabel="physical PDE time $t$",
        ylabel="RMS perturbation / initial RMS",
        title="(c) leading-mode growth versus generic transient decay",
    )
    axis.set_ylim(top=1.065)
    axis.grid(True, which="both", alpha=.2)
    axis.legend(ncol=2, fontsize=5.8)
    leading_runs = [
        row["short_time_runs"]["fine_neumann_leading_mode_half_dt"]
        for row in report["profiles"]
    ]
    maximum_zero_defect = max(
        float(run["zero_perturbation_defect_inf"])
        for row in report["profiles"]
        for run in row["short_time_runs"].values()
    )
    initial_amplitude = max(float(run["initial_perturbation_rms"]) for run in leading_runs)
    final_time = max(float(run["final_time"]) for run in leading_runs)
    axis.text(
        .98,
        .95,
        rf"$A_0={initial_amplitude:.1e}$; $T={final_time:g}$"
        "\n"
        rf"max zero-state defect $={maximum_zero_defect:.1e}$",
        transform=axis.transAxes,
        ha="right",
        va="top",
        fontsize=6.5,
        bbox=dict(fc="white", ec=GRAY, alpha=.9),
    )
    badge(axis, "COMPUTED/E1 SHORT TIME")

    axis = axes[1, 1]
    expected = np.asarray([
        row["sensitivity"]["leading_mode_expected_linear_envelope_amplification"]
        for row in report["profiles"]
    ])
    observed = np.asarray([
        row["sensitivity"]["leading_mode_observed_nonlinear_amplification"]
        for row in report["profiles"]
    ])
    low = min(float(np.min(expected)), float(np.min(observed)))
    high = max(float(np.max(expected)), float(np.max(observed)))
    padding = max(.02 * (high - low), 1e-4)
    axis.plot([low - padding, high + padding], [low - padding, high + padding], color=BLACK, ls=":", label="observed = linear envelope")
    for index, pulse_count in enumerate(pulse_counts):
        axis.scatter(expected[index], observed[index], color=COLORS[index], marker=MARKERS[index], s=34, label=f"pulse {pulse_count}")
    axis.set(
        xlabel="leading linear envelope amplification",
        ylabel="observed finite-time amplification",
        title="(d) internal leading-mode consistency",
    )
    axis.grid(True, alpha=.2)
    axis.ticklabel_format(style="plain", useOffset=False)
    axis.legend(ncol=1, fontsize=6.3, loc="center right")
    maximum_eigenpair_residual = max(
        float(row["sensitivity"]["leading_mode_complex_eigenpair_relative_residual"])
        for row in report["profiles"]
    )
    maximum_time_step_sensitivity = max(
        float(row["sensitivity"]["time_step_final_state_difference_over_initial_rms"])
        for row in report["profiles"]
    )
    maximum_grid_sensitivity = max(
        float(row["sensitivity"]["grid_final_state_difference_over_initial_rms"])
        for row in report["profiles"]
    )
    maximum_boundary_sensitivity = max(
        float(row["sensitivity"]["boundary_final_state_difference_over_initial_rms"])
        for row in report["profiles"]
    )
    axis.text(
        .98,
        .04,
        "residual-subtracted perturbation equation; not direct base-profile evolution\n"
        rf"max eig residual $={maximum_eigenpair_residual:.1e}$; "
        rf"state $\Delta_{{dt}}={maximum_time_step_sensitivity:.1e}$, "
        rf"$\Delta_{{grid}}={maximum_grid_sensitivity:.1e}$, "
        rf"$\Delta_{{bc}}={maximum_boundary_sensitivity:.1e}$",
        transform=axis.transAxes,
        ha="right",
        va="bottom",
        fontsize=6.3,
        bbox=dict(fc="white", ec=RED, hatch="///"),
    )
    badge(axis, "COMPUTED/QA — NOT NONLINEAR STABILITY", stopped=True)

    figure.suptitle(
        "Localized-profile temporal prescreen — finite-window spectra and short perturbation runs",
        weight="bold",
    )
    save(figure, output, "figure_d3_multipulse_temporal_screen")


def figure_d4(output: Path, config: dict[str, Any]) -> None:
    report = load_json(output / "canard_report.json")
    with np.load(output / "screening_profiles.npz", allow_pickle=False) as archive:
        profile_arrays = {key: np.asarray(archive[key]) for key in archive.files}
    figure, axes = plt.subplots(2, 2, figsize=(10.8, 7.1), constrained_layout=True)

    axis = axes[0, 0]
    for label, color, style in (("A0", BLUE, "-"), ("A2", ORANGE, "--")):
        x = profile_arrays[f"periodic_{label}_physical_x"]
        u = profile_arrays[f"periodic_{label}_physical_u"]
        axis.plot(x - .5 * (x[0] + x[-1]), u - 1.0, color=color, ls=style, label=f"periodic {label}")
    x = profile_arrays["pulse_1_physical_x"]
    u = profile_arrays["pulse_1_physical_u"]
    axis.plot(x - .5 * (x[0] + x[-1]), u - 1.0, color=GREEN, alpha=.85, label="one-pulse truncation")
    axis.axhline(0.0, color=BLACK, lw=.9, ls=":", label=r"fold level $u=1$")
    axis.axhspan(-config["canard"]["fold_collar"], config["canard"]["fold_collar"], color=GRAY, alpha=.12, label="diagnostic fold collar")
    axis.set(
        xlabel="physical space $x$",
        ylabel=r"$u(x)-1$",
        title="(a) finite profiles cross the positive fold level",
    )
    axis.grid(True, alpha=.18)
    axis.legend(loc="best")
    badge(axis, "COMPUTED/E1 FOLD PASSAGE")

    axis = axes[0, 1]
    u_grid = np.linspace(-1.65, 1.65, 600)
    v_grid = u_grid**3 / 3.0 - u_grid
    axis.axvspan(-1.0, 1.0, color=PURPLE, alpha=.08, label=r"$f'(u)<0$: elliptic fast normal")
    axis.axvspan(-1.65, -1.0, color=BLUE, alpha=.07)
    axis.axvspan(1.0, 1.65, color=BLUE, alpha=.07, label=r"$f'(u)>0$: saddle fast normal")
    axis.plot(u_grid, v_grid, color=BLACK, label=r"critical manifold $v=f(u),\ p=0$")
    folds = np.asarray([-1.0, 1.0])
    axis.scatter(folds, folds**3 / 3.0 - folds, color=RED, zorder=5, label="folds")
    axis.set(
        xlabel="$u$",
        ylabel="$v$",
        title="(b) exact singular critical-manifold geometry",
    )
    axis.grid(True, alpha=.18)
    axis.legend(loc="best", fontsize=6.7)
    badge(axis, "EXACT/DERIVED", exact=True)

    axis = axes[1, 0]
    r = np.linspace(.02, .12, 300)
    epsilon = float(config["primary_parameters"]["epsilon"])
    leading_a2 = -(5.0 * np.sqrt(epsilon) / 48.0) * r
    axis.plot(r, leading_a2, color=RED, ls="--", label=r"leading $a_{2,c}=-(5\sqrt{\epsilon}/48)r$")
    box = config["issue_7_preselected_box"]
    axis.axvspan(box["r"][0], box["r"][1], color=GRAY, alpha=.18, label=r"Issue #7 $r$ projection ($a_2$ extends to $\pm0.25$)")
    primary = config["primary_parameters"]
    axis.scatter([primary["r"]], [primary["a2"]], marker="*", s=75, color=BLUE, zorder=5, label="computed V7 point")
    reference = report["maximal_canard_reference"]
    axis.plot([primary["r"], primary["r"]], [reference["blowup_a2_leading"], primary["a2"]], color=ORANGE, lw=1.2, label="sample minus leading term")
    axis.set(
        ylim=(-.03, .03),
        xlabel="$r$",
        ylabel="$a_2$",
        title="(c) leading maximal-canard curve is a reference, not an enclosure",
    )
    axis.grid(True, alpha=.18)
    axis.legend(loc="best", fontsize=6.6)
    axis.text(.98, .04, r"unknown $O(r^3)$ remainder in $a_2$\nno finite-parameter slow-manifold intersection computed", transform=axis.transAxes, ha="right", va="bottom", fontsize=6.6, bbox=dict(fc="white", ec=RED, hatch="///"))
    badge(axis, "MIXED — ASYMPTOTIC REFERENCE")

    axis = axes[1, 1]
    axis.axis("off")
    rows = [
        ("1", "critical manifold and folds", "EXACT"),
        ("2", "saved profiles meet both fast-normal sides", "COMPUTED"),
        ("3", "current singular reduced point", "FSN-II DEGENERATE"),
        ("4", "published maximal-canard curve", "LEADING TERM ONLY"),
        ("5", "finite-parameter slow-manifold intersection", "NOT COMPUTED"),
        ("STOP", "canard identification", "NO CANARD IDENTIFICATION"),
    ]
    y = .88
    for index, (number, item, status) in enumerate(rows):
        stopped = index >= 4
        axis.text(.05, y, number, transform=axis.transAxes, weight="bold", color=RED if stopped else BLUE, va="center")
        axis.text(.16, y, item, transform=axis.transAxes, va="center")
        axis.text(.96, y, status.replace("_", " "), transform=axis.transAxes, ha="right", va="center", fontsize=6.4, weight="bold", color=RED if stopped else BLACK)
        if index < len(rows) - 1:
            axis.plot([.06, .96], [y-.075, y-.075], transform=axis.transAxes, color="#DDDDDD", lw=.7)
        y -= .145
    outer = report["outer_diagnostics"]
    axis.text(.50, .035, rf"saved outer leg: $u\in[{outer['minimum_u']:.1f},{outer['maximum_u']:.1f}]$; it stays at least {outer['minimum_distance_to_fold_set']:.1f} from either fold", transform=axis.transAxes, ha="center", va="bottom", fontsize=6.6, bbox=dict(fc=PALE_GRAY, ec=GRAY))
    axis.set_title("(d) evidence ladder and mandatory stop rule")
    badge(axis, "NO CANARD IDENTIFICATION", stopped=True)

    figure.suptitle(
        "Slow--fast geometry — fold passage and FSN-II degeneracy are not a maximal canard",
        weight="bold",
    )
    save(figure, output, "figure_d4_canard_stop_rule")


def render_all(output: Path, *, config_path: Path = DEFAULT_CONFIG) -> None:
    output = output.resolve()
    config_path = config_path.resolve()
    configure_style()
    config = validate_render_contract(output, config_path)
    figure_d1(output, config)
    figure_d2(output)
    figure_d3(output)
    figure_d4(output, config)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    arguments = parser.parse_args(argv)
    render_all(arguments.output, config_path=arguments.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
