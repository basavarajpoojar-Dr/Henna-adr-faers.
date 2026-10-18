"""
02_fig_s1_temporal.py
=====================
Henna ADR FAERS Study — Supplementary Figure S1: Temporal Distribution
-----------------------------------------------------------------------
Panel A: Annual case count line chart (2003–2025) with annotated peaks
         and regulatory milestone markers.
Panel B: Stacked bar chart of annual cases by product category for
         selected high-volume years.

Usage
-----
    python scripts/02_fig_s1_temporal.py [--data-dir data] [--out-dir outputs]

Output
------
    outputs/FigS1_Temporal_Distribution.png  (300 DPI)
"""

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd


def parse_args():
    p = argparse.ArgumentParser(description="Generate Supplementary Figure S1.")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--out-dir", default="outputs")
    return p.parse_args()


JAGUA_TERMS = ["jagua", "inkbox"]

def is_jagua(name: str) -> bool:
    n = str(name).lower()
    return any(t in n for t in JAGUA_TERMS)

BLACK_HENNA_TERMS = [
    "black henna", "henna black", "henna tattoo (black",
    "henna tattoo(black", "black tattoo", "nisha henna black",
    "ppd henna", "eurus black henna", "mira", "black hair dye",
]
HAIR_TERMS = ["hair dye","hair henna","hair color","hair colour",
              "hair creme","surya brasil","tancho","parampara"]
PERIOCULAR_TERMS = ["eyebrow","eyelash","periocular","eyelid"]

def classify_product(name: str) -> str:
    n = str(name).lower()
    if any(t in n for t in PERIOCULAR_TERMS):
        return "Periocular"
    if any(t in n for t in HAIR_TERMS):
        return "Hair Colourant"
    if any(t in n for t in BLACK_HENNA_TERMS):
        return "Black Henna"
    if any(t in n for t in ["natural","pure","jamilla","jamila","golecha","asma henna",
                             "shweta","royal gift","rainbow","henna powder","henna cone",
                             "rivaaj","dulthan","mehandi","cinderella","henna temporary",
                             "temporary henna","patel","castle art","henna tattoo - dye",
                             "henna tattoo henna","henna used at","listed on sign"]):
        return "Natural Henna"
    if "black" in n:
        return "Black Henna"
    if "henna" in n:
        return "Natural Henna"
    return "Other"


# Category colours
CAT_COLORS = {
    "Black Henna":    "#c0392b",
    "Natural Henna":  "#27ae60",
    "Hair Colourant": "#2980b9",
    "Periocular":     "#8e44ad",
    "Other":          "#7f8c8d",
}
CAT_ORDER = ["Black Henna", "Natural Henna", "Hair Colourant", "Periocular", "Other"]


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

    df["Category"] = df["Suspect Reported Product Name"].apply(classify_product)
    df["Year"] = pd.to_datetime(
        df["FDA Initial Received Date"], format="%d-%b-%Y", errors="coerce"
    ).dt.year

    df_valid = df.dropna(subset=["Year"]).copy()
    df_valid["Year"] = df_valid["Year"].astype(int)

    # Full year range
    all_years = list(range(int(df_valid["Year"].min()), int(df_valid["Year"].max()) + 1))

    yearly_total = df_valid.groupby("Year").size().reindex(all_years, fill_value=0)

    yearly_cat = (
        df_valid.groupby(["Year", "Category"])
        .size()
        .unstack(fill_value=0)
        .reindex(all_years, fill_value=0)
    )
    for cat in CAT_ORDER:
        if cat not in yearly_cat.columns:
            yearly_cat[cat] = 0
    yearly_cat = yearly_cat[CAT_ORDER]

    # ------------------------------------------------------------------
    # Figure layout
    # ------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6),
                                   gridspec_kw={"width_ratios": [3, 2]})
    fig.patch.set_facecolor("white")

    # ---- Panel A: Temporal line chart --------------------------------
    ax1.set_facecolor("#f8f9fa")
    ax1.plot(all_years, yearly_total.values, color="#1a3a5c",
             linewidth=2.2, marker="o", markersize=5,
             markerfacecolor="white", markeredgewidth=1.5, zorder=3)
    ax1.fill_between(all_years, yearly_total.values, alpha=0.12,
                     color="#1a3a5c", zorder=2)

    # Annotate peaks
    peaks = {2005: 15, 2013: 12, 2017: 12}
    for yr, cnt in peaks.items():
        if yr in all_years:
            ax1.annotate(
                f"n={cnt}", xy=(yr, cnt), xytext=(yr + 0.4, cnt + 1.2),
                fontsize=8.5, color="#1a3a5c", fontweight="bold",
                arrowprops=dict(arrowstyle="-", color="#7f8c8d", lw=0.8),
            )

    # Regulatory milestones
    milestones = {
        2009: ("EU PPD\nRestriction", "#e67e22"),
        2022: ("MoCRA\n2022",         "#16a085"),
    }
    for yr, (label, col) in milestones.items():
        ax1.axvline(yr, color=col, linestyle="--", linewidth=1.4,
                    alpha=0.75, zorder=2)
        ax1.text(yr + 0.15, ax1.get_ylim()[1] * 0.02 if ax1.get_ylim()[1] > 0 else 0.5,
                 label, color=col, fontsize=7.5, va="bottom",
                 fontweight="bold")

    ax1.set_xlabel("Year", fontsize=11, labelpad=6)
    ax1.set_ylabel("Number of Cases", fontsize=11, labelpad=6)
    ax1.set_title("Panel A  —  Annual Adverse Event Reports\n(FDA FAERS Cosmetic Dashboard, 2003–2025)",
                  fontsize=11, fontweight="bold", pad=10)
    ax1.set_xticks(all_years[::2])
    ax1.tick_params(axis="x", rotation=45, labelsize=8.5)
    ax1.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax1.grid(axis="y", linestyle=":", alpha=0.5, color="#bdc3c7")
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.text(0.02, 0.97, "n = 110", transform=ax1.transAxes,
             fontsize=9, va="top", color="#555555",
             fontstyle="italic")

    # ---- Panel B: Stacked bar by category for selected years ---------
    # Select years with ≥5 cases for bar chart
    selected_years = sorted(yearly_total[yearly_total >= 5].index.tolist())
    if not selected_years:
        selected_years = sorted(yearly_total.nlargest(8).index.tolist())

    bar_data = yearly_cat.loc[selected_years]
    present_cats = [c for c in CAT_ORDER if bar_data[c].sum() > 0]

    ax2.set_facecolor("#f8f9fa")
    x = np.arange(len(selected_years))
    bottoms = np.zeros(len(selected_years))
    for cat in present_cats:
        vals = bar_data[cat].values.astype(float)
        ax2.bar(x, vals, bottom=bottoms, color=CAT_COLORS[cat],
                label=cat, width=0.65, edgecolor="white",
                linewidth=0.6, zorder=3)
        bottoms += vals

    ax2.set_xticks(x)
    ax2.set_xticklabels(selected_years, rotation=45, ha="right", fontsize=8.5)
    ax2.set_xlabel("Year", fontsize=11, labelpad=6)
    ax2.set_ylabel("Number of Cases", fontsize=11, labelpad=6)
    ax2.set_title("Panel B  —  Cases by Product Category\n(Years with ≥ 5 Reports)",
                  fontsize=11, fontweight="bold", pad=10)
    ax2.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax2.grid(axis="y", linestyle=":", alpha=0.5, color="#bdc3c7")
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.legend(loc="upper left", fontsize=7.5, framealpha=0.9,
               edgecolor="#bdc3c7", title="Category", title_fontsize=8)

    plt.tight_layout(pad=2.0)
    out_path = out_dir / "FigS1_Temporal_Distribution.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"Saved → {out_path}")


if __name__ == "__main__":
    main()
