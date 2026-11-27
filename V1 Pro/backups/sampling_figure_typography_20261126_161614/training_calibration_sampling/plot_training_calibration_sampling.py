"""Conceptual sampling diagram, not experimental or reliability-estimation data.

One coordinate system shows an illustrative Gaussian input density and limit state.
Training positions combine a space-filling design and boundary refinement;
calibration positions are independent Gaussian draws. All points are exported.
Run this script with Python, NumPy, SciPy, and Matplotlib.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
import numpy as np
from scipy.stats import qmc

from audit_panel_alignment import require_matplotlib_panel_alignment


OUT = Path(__file__).resolve().parent
STEM = "fig_training_calibration_sampling"
INK = "#253139"
GRAY = "#65747E"
BLUE = "#52758A"
GREEN = "#398765"
CONTOUR = "#9EB6A8"
RED = "#BA594D"
FRAME_GRAY = "#C9D2D8"
LOW = np.array([-3.0, -2.8])
HIGH = np.array([3.2, 2.9])
MEAN = np.array([-0.95, 0.05])
COV = np.array([[0.46, 0.09], [0.09, 0.62]])


def boundary(x2):
    """Failure means x1 >= boundary(x2), i.e. g(x) <= 0."""
    return 0.56 + 0.24 * (np.asarray(x2) - 0.6) ** 2 - 0.10 * np.asarray(x2)


def schematic_locations():
    # These independent seeds describe an illustration, not a reported study.
    design = qmc.scale(
        qmc.LatinHypercube(d=2, seed=512).random(14),
        [-2.6, -2.4], [2.8, 2.3],
    )
    design_rng = np.random.default_rng(810)
    y = np.linspace(-2.25, 2.25, 15) + design_rng.uniform(-0.035, 0.035, 15)
    refinement = np.column_stack((boundary(y) + design_rng.uniform(-0.23, 0.23, 15), y))
    training = np.vstack((design, refinement))
    calibration_rng = np.random.default_rng(20261126)
    calibration = calibration_rng.multivariate_normal(MEAN, COV, size=90)
    # No sample is omitted or clipped to make the conceptual density clearer.
    for points in (training, calibration):
        assert np.all(points > LOW) and np.all(points < HIGH)
    return training, calibration


def draw_geometry(ax):
    y = np.linspace(LOW[1], HIGH[1], 650)
    ax.fill_betweenx(y, boundary(y), HIGH[0], color="#FAEEEE", zorder=0)
    x1 = np.linspace(LOW[0], HIGH[0], 350)
    x2 = np.linspace(LOW[1], HIGH[1], 350)
    xx, yy = np.meshgrid(x1, x2)
    delta = np.stack((xx - MEAN[0], yy - MEAN[1]), axis=-1)
    distance = np.einsum("...i,ij,...j->...", delta, np.linalg.inv(COV), delta)
    # Ellipses are isodensity contours of the illustrative input law.
    ax.contourf(xx, yy, distance, levels=[0, 0.8, 2, 4, 6.5],
                colors=["#E6F0E9", "#EEF5F0", "#F5F9F6", "#FBFCFB"], zorder=1)
    ax.contour(xx, yy, distance, levels=[0.8, 2, 4, 6.5],
               colors=CONTOUR, linewidths=0.65, linestyles=[(0, (4, 3))], zorder=2)
    ax.plot(boundary(y), y, color=RED, lw=1.65, zorder=4)
    ax.set_xlim(LOW[0], HIGH[0])
    ax.set_ylim(LOW[1], HIGH[1])
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK)
        ax.spines[side].set_linewidth(0.85)
    ax.text(-2.10, 2.43, "Safe", color=GRAY, fontsize=10.2, ha="center", va="center")
    ax.text(-2.10, 2.06, r"$g>0$", color=GRAY, fontsize=10.2, ha="center", va="center")
    ax.text(2.10, 2.43, "Failure", color=RED, fontsize=10.2, ha="center", va="center")
    ax.text(2.10, 2.06, r"$g\leq 0$", color=RED, fontsize=10.2, ha="center", va="center")
    x_label = ax.text(1.015, -0.025, r"$x_1$", transform=ax.transAxes,
                      fontsize=11, ha="left", va="top")
    ax.text(-0.045, 1.01, r"$x_2$", transform=ax.transAxes,
            fontsize=11, ha="right", va="bottom")
    return x_label


def frame_and_separate_legend(fig, x_label, legend):
    """Match the manuscript's light frame and separate plotting/legend regions."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    label_box = x_label.get_window_extent(renderer).transformed(fig.dpi_scale_trans.inverted())
    legend_box = legend.get_window_extent(renderer).transformed(fig.dpi_scale_trans.inverted())
    gap = label_box.y0 - legend_box.y1
    assert gap >= 0.24, f"Insufficient axis-label/legend gap: {gap:.3f} inches"
    separator_y = 0.5 * (label_box.y0 + legend_box.y1)
    fig.add_artist(Line2D(
        [0.03, 0.97], [separator_y / fig.get_figheight()] * 2,
        transform=fig.transFigure, color=FRAME_GRAY, linewidth=0.55,
        clip_on=False, zorder=8,
    ))
    inset_inches = 1.5 / 72
    fig.add_artist(FancyBboxPatch(
        (inset_inches / fig.get_figwidth(), inset_inches / fig.get_figheight()),
        1 - 2 * inset_inches / fig.get_figwidth(),
        1 - 2 * inset_inches / fig.get_figheight(),
        boxstyle="round,pad=0,rounding_size=0.0052",
        transform=fig.transFigure, edgecolor=FRAME_GRAY, facecolor="none",
        linewidth=0.69, clip_on=False, zorder=9,
    ))
    return {
        "color": FRAME_GRAY,
        "outer_frame_linewidth_pt": 0.69,
        "outer_frame_inset_pt": 1.5,
        "separator_linewidth_pt": 0.55,
        "separator_y_inches": float(separator_y),
        "xlabel_to_legend_gap_inches": float(gap),
        "xlabel_to_separator_gap_pt": float(36 * gap),
        "separator_to_legend_gap_pt": float(36 * gap),
        "legend_bbox_inches": [float(x) for x in legend_box.extents],
        "plot_and_legend_separated": True,
    }


def main():
    training, calibration = schematic_locations()
    rc = {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 10,
        "text.color": INK,
        "axes.labelcolor": INK,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    }
    with plt.rc_context(rc):
        # Preserve the plot's physical size and reserve a distinct footer for the legend.
        plot_height = (0.82 * 5.35) * (HIGH[1] - LOW[1]) / (HIGH[0] - LOW[0])
        fig, ax = plt.subplots(figsize=(5.35, 5.65),
                               gridspec_kw={"left": 0.10, "right": 0.92,
                                            "bottom": 1.25 / 5.65,
                                            "top": (1.25 + plot_height) / 5.65})
        x_label = draw_geometry(ax)
        ax.scatter(calibration[:, 0], calibration[:, 1], s=25, marker="o",
                   c=GREEN, edgecolors="white", linewidths=0.45, alpha=0.85, zorder=5)
        ax.scatter(training[:, 0], training[:, 1], s=37, marker="s",
                   c=BLUE, edgecolors="white", linewidths=0.75, zorder=6)
        legend = [Line2D([0], [0], marker="s", markersize=6.2, linestyle="none",
                         markerfacecolor=BLUE, markeredgecolor="white", markeredgewidth=0.6,
                         label="Training (design / active)"),
                  Line2D([0], [0], color=CONTOUR, lw=1.0, ls=(0, (4, 3)),
                         label="Input-density contours"),
                  Line2D([0], [0], marker="o", markersize=6.0, linestyle="none",
                         markerfacecolor=GREEN, markeredgecolor="white", markeredgewidth=0.6,
                         label=r"Calibration (iid from $\mathbb{P}$)"),
                  Line2D([0], [0], color=RED, lw=1.65,
                         label=r"Limit-state boundary, $g=0$")]
        legend_artist = fig.legend(
            handles=legend, loc="lower center", bbox_to_anchor=(0.50, 0.022),
            ncol=2, fontsize=10.5, frameon=False, handlelength=2.2,
            columnspacing=1.7, handletextpad=0.6, labelspacing=0.75, borderaxespad=0,
        )
        frame_layout = frame_and_separate_legend(fig, x_label, legend_artist)
        fig.canvas.draw()
        require_matplotlib_panel_alignment(
            fig, json_out=str(OUT / f"{STEM}.alignment.json"),
            overlay_svg=str(OUT / f"{STEM}.alignment.svg"),
            require_panel_labels=False, strict=True,
        )
        fig.savefig(OUT / f"{STEM}.pdf")
        fig.savefig(OUT / f"{STEM}.svg")
        fig.savefig(OUT / f"{STEM}.png", dpi=600)
        fig.savefig(OUT / f"{STEM}.tiff", dpi=600, pil_kwargs={"compression": "tiff_lzw"})
        fig.savefig(OUT / "preview.png", dpi=300)
        plt.close(fig)
    with (OUT / "schematic_points.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["stage", "point", "x1", "x2"])
        for stage, points in [("training", training), ("calibration", calibration)]:
            for index, point in enumerate(points, 1):
                writer.writerow([stage, index, *point])
    contract = {
        "figure_role": "Conceptual sampling schematic, not empirical evidence",
        "core_message": "Training may use design or active selection; independent calibration is iid under the target input law.",
        "archetype": "single-panel sampling schematic",
        "geometry": "One input coordinate system with both training and calibration locations",
        "training": "Flexible coverage plus boundary refinement",
        "calibration": "Independent iid draws from the illustrative input law",
        "reference_reuse": "Conceptual geometry only; original vector artwork",
        "illustrative_law": {"family": "bivariate normal", "mean": MEAN.tolist(), "covariance": COV.tolist()},
        "counts": {"training": len(training), "calibration": len(calibration)},
        "calibration_seed": 20261126,
        "omitted_points": 0,
        "experimental_results": False,
        "width_inches": 5.35,
        "height_inches": 5.65,
        "frame_and_legend": frame_layout,
        "preview_dpi": 300,
        "export_dpi": 600,
    }
    (OUT / "figure_contract.json").write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {STEM}: {len(training)} training and {len(calibration)} calibration schematic points.")


if __name__ == "__main__":
    main()
