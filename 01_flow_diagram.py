"""
01_flow_diagram.py
==================
Henna ADR FAERS Study — PRISMA-Style Data Selection Flow Diagram
-----------------------------------------------------------------
Generates the PRISMA-style case-selection flow diagram (Figure 0 /
data selection figure). Output is a 300 DPI PNG file.

Usage
-----
    python scripts/01_flow_diagram.py [--out-dir outputs]

Output
------
    outputs/DataSelection_FlowDiagram_HennaADR.png
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch


def parse_args():
    p = argparse.ArgumentParser(description="Generate PRISMA flow diagram.")
    p.add_argument("--out-dir", default="outputs",
                   help="Output directory (default: outputs/)")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_box(ax, x, y, w, h, text, facecolor, edgecolor, fontsize=10,
             text_color="white", bold_first_line=False, radius=0.015):
    """Draw a rounded rectangle with centred text."""
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=facecolor, edgecolor=edgecolor, linewidth=1.4,
        transform=ax.transAxes, clip_on=False, zorder=3,
    )
    ax.add_patch(box)
    lines = text.split("\n")
    if bold_first_line and len(lines) > 1:
        # Draw first line bold, rest normal
        full_text = "\n".join(lines)
        ax.text(x, y, full_text, ha="center", va="center",
                fontsize=fontsize, color=text_color,
                fontweight="bold", transform=ax.transAxes,
                linespacing=1.4, zorder=4)
    else:
        ax.text(x, y, text, ha="center", va="center",
                fontsize=fontsize, color=text_color,
                fontweight="bold", transform=ax.transAxes,
                linespacing=1.4, zorder=4)


def arrow(ax, x1, y1, x2, y2, color="#444444"):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        xycoords="axes fraction", textcoords="axes fraction",
        arrowprops=dict(arrowstyle="-|>", color=color,
                        lw=1.5, mutation_scale=14),
        zorder=2,
    )


def hline(ax, x1, y_coord, x2, line_color="#444444"):
    ax.annotate(
        "", xy=(x2, y_coord), xytext=(x1, y_coord),
        xycoords="axes fraction", textcoords="axes fraction",
        arrowprops=dict(arrowstyle="-", color=line_color, lw=1.5),
        zorder=2,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

NAVY   = "#1a3a5c"
RED    = "#c0392b"
AMBER  = "#b7770d"
SILVER = "#ecf0f1"
WHITE  = "white"
BORDER = "#7f8c8d"

STAGE_LABELS = ["IDENTIFICATION", "EXCLUSION", "ELIGIBILITY",
                "RETENTION NOTE", "INCLUDED"]
STAGE_COLORS = [NAVY, RED, NAVY, AMBER, NAVY]


def main():
    args = parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 12))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)

    # -- Stage label bands (left sidebar) --
    stage_y = [0.87, 0.74, 0.60, 0.46, 0.30]
    stage_h = 0.10

    for label, sy, sc in zip(STAGE_LABELS, stage_y, STAGE_COLORS):
        band = FancyBboxPatch(
            (0.01, sy - stage_h / 2), 0.14, stage_h,
            boxstyle="round,pad=0,rounding_size=0.008",
            facecolor=sc, edgecolor="none",
            transform=ax.transAxes, clip_on=False, zorder=2,
        )
        ax.add_patch(band)
        ax.text(0.08, sy, label, ha="center", va="center",
                fontsize=7.5, color=WHITE, fontweight="bold",
                rotation=90, transform=ax.transAxes, zorder=3)

    # -- Main flow boxes (centre column) --
    cx = 0.57   # centre x
    bw = 0.65   # box width

    boxes = [
        # (y_centre, height, text, facecolor, edgecolor)
        (0.87, 0.09,
         "Records identified from FDA FAERS\nCosmetic Public Dashboard\n(N = 112)",
         NAVY, NAVY),
        (0.60, 0.09,
         "Records assessed for eligibility\n(n = 110)",
         NAVY, NAVY),
        (0.30, 0.10,
         "Cases included in final analysis\n(n = 110)\n\nFDA FAERS Cosmetic Public Dashboard\n(2003 – 2025)",
         NAVY, NAVY),
    ]

    for y, h, txt, fc, ec in boxes:
        draw_box(ax, cx, y, bw, h, txt, fc, ec, fontsize=10,
                 text_color=WHITE, radius=0.012)

    # Eligibility note box (amber)
    draw_box(ax, cx, 0.46, bw, 0.08,
             "All 110 records met eligibility criteria:\n"
             "cosmetic henna products with reported adverse events",
             AMBER, AMBER, fontsize=9.5, text_color=WHITE, radius=0.012)

    # -- Exclusion box (right column) --
    ex = 0.915  # exclusion box centre x
    ew = 0.15   # exclusion box width
    draw_box(ax, ex, 0.74, ew, 0.09,
             "Excluded\n(n = 2)\n\nJagua-based products\n(Genipa americana)",
             RED, RED, fontsize=8.5, text_color=WHITE, radius=0.012)

    # -- Arrows --
    # Identification → screening gap (branching point)
    arrow(ax, cx, 0.825, cx, 0.78, color=BORDER)   # down from ID box
    # Horizontal to exclusion box
    mid_y = 0.74
    hline(ax, cx, mid_y, ex - ew / 2, line_color=BORDER)
    # From branch down to eligibility box
    arrow(ax, cx, mid_y, cx, 0.645, color=BORDER)
    # Eligibility → retention note
    arrow(ax, cx, 0.555, cx, 0.505, color=BORDER)
    # Retention note → included
    arrow(ax, cx, 0.415, cx, 0.355, color=BORDER)

    # Add small dot at branch point
    ax.plot(cx, mid_y, "o", color=BORDER, ms=5, transform=ax.transAxes,
            zorder=5, clip_on=False)

    plt.tight_layout(pad=0.3)
    out_path = out_dir / "DataSelection_FlowDiagram_HennaADR.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight",
                facecolor=WHITE, edgecolor="none")
    plt.close(fig)
    print(f"Saved → {out_path}")


if __name__ == "__main__":
    main()
