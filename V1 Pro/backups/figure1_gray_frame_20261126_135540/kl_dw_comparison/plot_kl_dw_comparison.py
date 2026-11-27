"""Plot the pointwise KL/DW acceptance envelopes defined in manuscript.tex.

Run with Python; NumPy, SciPy, Matplotlib and Pillow are required.
The default N=100 and theta=3 are illustrative, not confidence calibrations.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnchoredOffsetbox, DrawingArea, HPacker, TextArea
from matplotlib.patches import ConnectionPatch, Rectangle
from matplotlib.ticker import FormatStrFormatter
from matplotlib.transforms import Bbox
import numpy as np
from PIL import Image
import scipy
from scipy.optimize import brentq
from scipy.special import expit, xlogy


INK = "#253139"
GRAY = "#65747E"
LIGHT_GRAY = "#D6DBDF"
BLUE = "#52758A"
BLUE_FILL = "#D5E6F1"
GOLD = "#9B752B"
GOLD_FILL = "#F7E6AF"


@dataclass
class Endpoint:
    p: float
    log_p: float
    log_one_minus_p: float
    residual: float


def correction(q: float, p: float) -> float:
    """Minimum of psi_0 on [min(q,p), max(q,p)], with nu=1."""
    v = float(np.clip(0.5, min(q, p), max(q, p)))
    if v == 0.0 or v == 1.0:
        return float("inf")
    rho = np.log1p(-np.log(4.0 * v * (1.0 - v)))
    return float(rho + np.log1p(rho * rho))


def discrepancy(q: float, z: float, n: int, dw: bool) -> float:
    """Evaluate at p=expit(z), retaining accurate logs near both boundaries."""
    log_p = -np.logaddexp(0.0, -z)
    log_one_minus_p = -np.logaddexp(0.0, z)
    phi = (
        xlogy(q, q)
        + xlogy(1.0 - q, 1.0 - q)
        - q * log_p
        - (1.0 - q) * log_one_minus_p
    )
    return float(n * phi - (correction(q, float(expit(z))) if dw else 0.0))


def solve_endpoint(q: float, n: int, theta: float, dw: bool, upper: bool) -> Endpoint:
    if q == 0.0 and not upper:
        return Endpoint(0.0, -np.inf, 0.0, 0.0)
    z_center = np.log(q) - np.log1p(-q) if q else -80.0
    f = lambda z: discrepancy(q, z, n, dw) - theta
    direction = 1.0 if upper else -1.0
    step = 1.0
    z_outer = z_center + direction * step
    while f(z_outer) < 0.0:
        step *= 2.0
        z_outer = z_center + direction * step
    a, b = sorted((z_center, z_outer))
    z = brentq(f, a, b, xtol=1e-12, rtol=4.0 * np.finfo(float).eps)
    return Endpoint(
        float(expit(z)),
        float(-np.logaddexp(0.0, -z)),
        float(-np.logaddexp(0.0, z)),
        float(f(z)),
    )


def reflected(endpoint: Endpoint) -> Endpoint:
    # -expm1(log p) preserves tiny distances from one when possible.
    return Endpoint(
        float(-np.expm1(endpoint.log_p)),
        endpoint.log_one_minus_p,
        endpoint.log_p,
        endpoint.residual,
    )


def compute_envelopes(n: int, theta: float):
    q_left = np.unique(np.r_[np.linspace(0.0, 0.04, 801), np.linspace(0.04, 0.5, 921)])
    endpoints = {
        name: [solve_endpoint(float(q), n, theta, dw, upper) for q in q_left]
        for name, dw, upper in [
            ("kl_lower", False, False), ("kl_upper", False, True),
            ("dw_lower", True, False), ("dw_upper", True, True),
        ]
    }
    mirror_name = {
        "kl_lower": "kl_upper", "kl_upper": "kl_lower",
        "dw_lower": "dw_upper", "dw_upper": "dw_lower",
    }
    full = {
        name: values + [reflected(e) for e in endpoints[mirror_name[name]][-2::-1]]
        for name, values in endpoints.items()
    }
    q = np.r_[q_left, 1.0 - q_left[-2::-1]]
    curves = {name: np.array([e.p for e in values]) for name, values in full.items()}
    return q, curves, full


def draw_regions(ax, q, curves, *, inset=False):
    ax.fill_between(q, curves["dw_lower"], curves["kl_lower"], color=GOLD_FILL, zorder=1)
    ax.fill_between(q, curves["kl_upper"], curves["dw_upper"], color=GOLD_FILL, zorder=1)
    ax.fill_between(q, curves["kl_lower"], curves["kl_upper"], color=BLUE_FILL, zorder=2)
    for side in ("lower", "upper"):
        ax.plot(q, curves[f"dw_{side}"], color=GOLD, lw=1.35 if inset else 1.5,
                ls=(0, (4, 2.5)), zorder=4)
        ax.plot(q, curves[f"kl_{side}"], color=BLUE, lw=1.35 if inset else 1.5, zorder=5)
    ax.plot(q, q, color=INK, ls=(0, (2, 3)), lw=0.9, zorder=3)


def style_axes(ax, *, inset=False):
    ax.set_facecolor("white")
    for spine in ax.spines.values():
        spine.set_color(GRAY if inset else INK)
        spine.set_linewidth(0.8 if inset else 1.0)
    ax.tick_params(axis="both", colors=INK, direction="out", width=0.8,
                   length=3.0 if inset else 4.0, labelsize=9.5 if inset else 12)
    ax.grid(False)


def add_inline_legend(fig):
    """Arrange the two regions, their color-block sum, and p=q on one line."""
    def text_box(label):
        return TextArea(label, textprops={"fontsize": 11.5, "color": INK})

    def swatch(face, edge, dashed=False, width=22):
        box = DrawingArea(width, 12, 0, 0)
        box.add_artist(Rectangle((0, 1), width, 10, facecolor=face, edgecolor=edge,
                                 linewidth=1.1, linestyle="--" if dashed else "-"))
        return box

    def packed(children, sep=6):
        return HPacker(children=children, align="center", pad=0, sep=sep)

    kl = packed([swatch(BLUE_FILL, BLUE), text_box("KL feasible")])
    dw_only = packed([swatch(GOLD_FILL, GOLD, True), text_box("DW only")])
    dw_sum = packed([
        swatch(BLUE_FILL, BLUE, width=16), text_box("+"),
        swatch(GOLD_FILL, GOLD, True, width=16), text_box("= DW feasible"),
    ], sep=4)
    diagonal = DrawingArea(22, 12, 0, 0)
    diagonal.add_artist(Line2D([0, 22], [6, 6], color=INK, lw=1.0, ls=(0, (2, 3))))
    identity = packed([diagonal, text_box(r"$p=q$")])
    row = packed([kl, dw_only, dw_sum, identity], sep=17)
    legend = AnchoredOffsetbox(loc="lower center", child=row, frameon=False,
                              pad=0, borderpad=0, bbox_to_anchor=(0.535, 0.078),
                              bbox_transform=fig.transFigure)
    fig.add_artist(legend)


def make_figure(q, curves, n, theta):
    style = {
        "font.family": "Times New Roman", "font.serif": ["Times New Roman", "DejaVu Serif"],
        "mathtext.fontset": "stix", "font.size": 12,
        "text.color": INK, "axes.labelcolor": INK,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "savefig.facecolor": "white", "figure.facecolor": "white",
    }
    with plt.rc_context(style):
        fig = plt.figure(figsize=(7.4, 6.4))
        ax = fig.add_axes([0.12, 0.20, 0.835, 0.69])
        draw_regions(ax, q, curves)
        style_axes(ax)
        ax.set(xlim=(0, 1), ylim=(0, 1),
               xlabel=r"Empirical probability $q$", ylabel=r"Candidate probability $p$")
        ax.set_xticks(np.linspace(0, 1, 6))
        ax.set_yticks(np.linspace(0, 1, 6))
        ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
        ax.xaxis.label.set_size(14)
        ax.yaxis.label.set_size(14)

        # The inset occupies empty space above the acceptance envelopes.
        inset = ax.inset_axes([0.09, 0.61, 0.36, 0.32], zorder=8)
        draw_regions(inset, q[q <= 0.03], {k: v[q <= 0.03] for k, v in curves.items()}, inset=True)
        style_axes(inset, inset=True)
        inset.set(xlim=(0, 0.03), ylim=(0, 0.11), xlabel=r"$q$", ylabel=r"$p$")
        inset.set_xticks([0.00, 0.01, 0.02, 0.03])
        inset.set_yticks([0.00, 0.05, 0.10])
        inset.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        inset.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        inset.xaxis.label.set_size(12)
        inset.yaxis.label.set_size(12)
        inset.xaxis.labelpad = 0.5
        inset.yaxis.labelpad = 0.5
        inset.set_title("Left-tail detail", loc="left", fontsize=11.5, pad=6)

        inset.annotate("DW only", xy=(0.006, 0.055), xytext=(0.003, 0.095),
                       fontsize=10, color=GOLD,
                       arrowprops={"arrowstyle": "->", "color": GOLD, "lw": 0.8},
                       ha="left", va="center", zorder=9)
        zoom_box = Rectangle((0, 0), 0.03, 0.11, facecolor="none", edgecolor=GRAY,
                             lw=0.9, ls=(0, (3, 2)), zorder=7)
        ax.add_patch(zoom_box)
        connector = ConnectionPatch(xyA=(0.03, 0.11), coordsA=ax.transData,
                                    xyB=(0, 0.25), coordsB=inset.transAxes,
                                    connectionstyle="angle,angleA=90,angleB=180,rad=0",
                                    color=GRAY, lw=0.8, ls=(0, (3, 3)),
                                    zorder=6, clip_on=False)
        fig.add_artist(connector)

        ax.text(0.55, 0.25, rf"$N^{{\mathrm{{te}}}}={n},\quad\theta={theta:g},\quad s=\nu=1$",
                transform=ax.transAxes, fontsize=12)
        ax.text(0.55, 0.165, r"KL: $N^{\mathrm{te}}\phi(q,p)\leq\theta$",
                transform=ax.transAxes, fontsize=12, color=BLUE)
        ax.text(0.55, 0.09, r"DW: $N^{\mathrm{te}}\phi(q,p)-\psi(q,p)\leq\theta$",
                transform=ax.transAxes, fontsize=12, color=GOLD)

        add_inline_legend(fig)
        return fig


def verify(q, curves, endpoints, n, theta):
    tolerance = 2e-12
    assert np.all(curves["dw_lower"] <= curves["kl_lower"] + tolerance)
    assert np.all(curves["kl_lower"] <= q + tolerance)
    assert np.all(q <= curves["kl_upper"] + tolerance)
    assert np.all(curves["kl_upper"] <= curves["dw_upper"] + tolerance)
    residual = max(abs(e.residual) for values in endpoints.values() for e in values)
    assert residual < 2e-9, residual
    # Check the analytical minimizer of psi_0 independently against a dense scan.
    correction_checks = []
    for a, b in [(0.001, 0.02), (0.9, 0.99), (0.2, 0.8), (0.4, 0.45)]:
        v = np.linspace(a, b, 20001)
        rho = np.log1p(-np.log(4 * v * (1 - v)))
        scanned = float(np.min(rho + np.log1p(rho * rho)))
        error = abs(correction(a, b) - scanned)
        assert error < 1e-10
        correction_checks.append(error)
    # Independent closed forms for uncorrected q=0 and q=1/2 endpoints.
    assert abs(curves["kl_upper"][0] - (-np.expm1(-theta / n))) < 1e-12
    mid = int(np.argmin(abs(q - 0.5)))
    expected_mid = 0.5 * (1 + np.sqrt(-np.expm1(-2 * theta / n)))
    assert abs(curves["kl_upper"][mid] - expected_mid) < 1e-12
    assert abs(curves["dw_upper"][mid] - expected_mid) < 1e-12
    return {"max_boundary_equation_residual": residual,
            "nested_regions_verified": True, "closed_form_checks_passed": True,
            "correction_minimum_checks": correction_checks}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=100)
    parser.add_argument("--theta", type=float, default=3.0)
    parser.add_argument("--dpi", type=int, default=600)
    parser.add_argument("--outdir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    if args.n < 1 or args.theta <= 0:
        parser.error("n must be positive and theta must be strictly positive")
    args.outdir.mkdir(parents=True, exist_ok=True)
    stem = args.outdir / "fig_kl_dw_ambiguity_comparison"
    q, curves, endpoints = compute_envelopes(args.n, args.theta)
    checks = verify(q, curves, endpoints, args.n, args.theta)

    with stem.with_suffix(".csv").open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        names = list(curves)
        writer.writerow(["q", *names, *[f"log_{name}" for name in names]])
        for i, empirical in enumerate(q):
            writer.writerow([format(empirical, ".17g"),
                             *[format(curves[k][i], ".17g") for k in names],
                             *[format(endpoints[k][i].log_p, ".17g") for k in names]])

    fig = make_figure(q, curves, args.n, args.theta)
    with plt.rc_context({"pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none"}):
        # Crop only vertical whitespace; keep the original width and all artist geometry.
        fig.set_dpi(args.dpi)
        fig.canvas.draw()
        tight = fig.get_tightbbox(fig.canvas.get_renderer())
        margin = 0.04  # inches
        # Align the crop to whole pixels in both the 600 and 180 dpi outputs.
        crop_bottom = max(0.0, np.floor((tight.y0 - margin) * 60.0) / 60.0)
        crop_top = min(fig.get_figheight(), np.ceil((tight.y1 + margin) * 60.0) / 60.0)
        crop = Bbox.from_extents(0.0, crop_bottom, fig.get_figwidth(), crop_top)
        for extension in ("pdf", "svg", "png"):
            fig.savefig(stem.with_suffix("." + extension), dpi=args.dpi, facecolor="white",
                        bbox_inches=crop, pad_inches=0)
        fig.savefig(args.outdir / "preview.png", dpi=180, facecolor="white",
                    bbox_inches=crop, pad_inches=0)
    plt.close(fig)
    with Image.open(stem.with_suffix(".png")) as im:
        raster_metadata = {"size_pixels": list(im.size), "dpi": list(im.info.get("dpi", []))}
    manuscript = Path(__file__).resolve().parents[2] / "manuscript.tex"
    manifest = {
        "source_manuscript": str(manuscript),
        "source_sha256": hashlib.sha256(manuscript.read_bytes()).hexdigest(),
        "parameters": {"N_te": args.n, "theta": args.theta, "s": 1, "nu": 1},
        "parameter_status": "illustrative common threshold; not a confidence calibration",
        "semantics": "pointwise acceptance envelopes, continuous q display",
        "q_note": "Actual empirical CDF levels are j/N_te; q is drawn continuously for illustration.",
        "solver": "brentq in logit(p), exact manuscript constraints; no quadratic approximation",
        "endpoint_convention": "q=p=0 and q=p=1 use manuscript closure conventions",
        "small_numbers": "Log probabilities are retained in CSV when ordinary p underflows.",
        "symmetry": "Right-half endpoints reflect left-half roots using (q,p)->(1-q,1-p).",
        "points": len(q), "checks": checks,
        "physical_size_inches": [float(crop.width), float(crop.height)],
        "original_canvas_inches": [7.4, 6.4],
        "crop": {"vertical_only": True, "bottom_inches": float(crop_bottom),
                 "top_inches": float(crop_top), "margin_inches": margin},
        "raster": raster_metadata,
        "palette": {"blue_fill": BLUE_FILL, "gold_fill": GOLD_FILL,
                    "blue_boundary": BLUE, "gold_boundary": GOLD, "text": INK},
        "style_reference": ["fig_response_threshold_band.png", "fig_joint_partition.png"],
        "versions": {"numpy": np.__version__, "scipy": scipy.__version__,
                     "matplotlib": matplotlib.__version__},
    }
    stem.with_suffix(".json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"output": str(stem), "points": len(q), "checks": checks,
                      "q_zero_upper_endpoints": {k: float(curves[k][0]) for k in ("kl_upper", "dw_upper")}},
                     indent=2))


if __name__ == "__main__":
    main()
