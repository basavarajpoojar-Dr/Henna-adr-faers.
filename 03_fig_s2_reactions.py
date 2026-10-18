"""
03_fig_s2_reactions.py
======================
Henna ADR FAERS Study — Supplementary Figure S2: Top 20 Adverse Reactions
--------------------------------------------------------------------------
Horizontal bar chart of the 20 most-frequently reported MedDRA Preferred
Terms (PTs), colour-coded by System Organ Class (SOC).

Usage
-----
    python scripts/03_fig_s2_reactions.py [--data-dir data] [--out-dir outputs]

Output
------
    outputs/FigS2_Top20_Reactions.png  (300 DPI)
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd


def parse_args():
    p = argparse.ArgumentParser(description="Generate Supplementary Figure S2.")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--out-dir", default="outputs")
    return p.parse_args()


JAGUA_TERMS = ["jagua", "inkbox"]

def is_jagua(name: str) -> bool:
    return any(t in str(name).lower() for t in JAGUA_TERMS)


# MedDRA SOC mapping for the top reactions in this cohort
# Source: MedDRA v28 hierarchy
SOC_MAP = {
    "Pruritus":             "Skin & Subcutaneous Tissue Disorders",
    "Hypersensitivity":     "Immune System Disorders",
    "Blister":              "Skin & Subcutaneous Tissue Disorders",
    "Erythema":             "Skin & Subcutaneous Tissue Disorders",
    "Rash":                 "Skin & Subcutaneous Tissue Disorders",
    "Swelling":             "General Disorders & Administration Site Conditions",
    "Burning Sensation":    "Nervous System Disorders",
    "Urticaria":            "Skin & Subcutaneous Tissue Disorders",
    "Scar":                 "Injury, Poisoning & Procedural Complications",
    "Pain":                 "General Disorders & Administration Site Conditions",
    "Skin Irritation":      "Skin & Subcutaneous Tissue Disorders",
    "Skin Reaction":        "Skin & Subcutaneous Tissue Disorders",
    "Skin Discolouration":  "Skin & Subcutaneous Tissue Disorders",
    "Skin Exfoliation":     "Skin & Subcutaneous Tissue Disorders",
    "Chemical Burn":        "Injury, Poisoning & Procedural Complications",
    "No Adverse Event":     "General Disorders & Administration Site Conditions",
    "Paraesthesia":         "Nervous System Disorders",
    "Feeling Hot":          "General Disorders & Administration Site Conditions",
    "Rash Papular":         "Skin & Subcutaneous Tissue Disorders",
    "Skin Swelling":        "Skin & Subcutaneous Tissue Disorders",
    "Nausea":               "Gastrointestinal Disorders",
}

SOC_COLORS = {
    "Skin & Subcutaneous Tissue Disorders":             "#8b1a1a",
    "Immune System Disorders":                          "#6c3483",
    "General Disorders & Administration Site Conditions": "#1a5276",
    "Injury, Poisoning & Procedural Complications":     "#b7770d",
    "Nervous System Disorders":                         "#117a65",
    "Gastrointestinal Disorders":                       "#1e8449",
}
DEFAULT_COLOR = "#717d7e"


def main():
    args = parse_args()
    data_dir = Path(args.data_dir)
    out_dir  = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ll_path = data_dir / "Line_Listing_Henna_.xlsx"
    if not ll_path.exists():
        sys.exit(f"ERROR: {ll_path} not found. See data/README_data.md.")

    df_raw = pd.read_excel(ll_path)
    df = df_raw[~df_raw["Suspect Reported Product Name"].apply(is_jagua)].copy()
    n = len(df)   # should be 110

    # Count MedDRA PTs
    pt_counter = Counter()
    for pts in df["Event MedDRA PT(s)"].dropna():
        for pt in str(pts).split(";"):
            pt = pt.strip()
            if pt and pt.lower() not in ("", "-", "none"):
                pt_counter[pt] += 1

    top20 = pd.DataFrame(pt_counter.most_common(20),
                         columns=["PT", "Count"])
    top20["Pct"]   = top20["Count"] / n * 100
    top20["SOC"]   = top20["PT"].map(SOC_MAP).fillna("Other")
    top20["Color"] = top20["SOC"].map(SOC_COLORS).fillna(DEFAULT_COLOR)

    # Reverse for horizontal bar (highest at top)
    top20 = top20.iloc[::-1].reset_index(drop=True)

    # ------------------------------------------------------------------
    # Figure
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(13, 9))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#f8f9fa")

    y_pos = np.arange(len(top20))
    bars = ax.barh(y_pos, top20["Count"], color=top20["Color"],
                   edgecolor="white", linewidth=0.5, height=0.72, zorder=3)

    # Percentage labels
    for i, (cnt, pct) in enumerate(zip(top20["Count"], top20["Pct"])):
        ax.text(cnt + 0.3, i, f"{pct:.1f}%",
                va="center", ha="left", fontsize=8.5, color="#2c3e50")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(top20["PT"], fontsize=9)
    ax.set_xlabel("Number of Cases", fontsize=11, labelpad=6)
    ax.set_title(
        "Top 20 Adverse Reactions — Henna-Associated Cases (n = 110)\n"
        "FDA FAERS Cosmetic Public Dashboard · MedDRA Preferred Terms",
        fontsize=11, fontweight="bold", pad=12,
    )
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.set_xlim(0, top20["Count"].max() * 1.18)
    ax.grid(axis="x", linestyle=":", alpha=0.5, color="#bdc3c7", zorder=0)
    ax.spines[["top", "right"]].set_visible(False)

    # SOC legend
    seen_socs = top20["SOC"].unique()
    legend_patches = [
        mpatches.Patch(color=SOC_COLORS.get(s, DEFAULT_COLOR), label=s)
        for s in SOC_COLORS if s in seen_socs
    ]
    ax.legend(handles=legend_patches, loc="lower right",
              fontsize=7.5, title="System Organ Class",
              title_fontsize=8, framealpha=0.92,
              edgecolor="#bdc3c7")

    plt.tight_layout(pad=1.5)
    out_path = out_dir / "FigS2_Top20_Reactions.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"Saved → {out_path}")


if __name__ == "__main__":
    main()
