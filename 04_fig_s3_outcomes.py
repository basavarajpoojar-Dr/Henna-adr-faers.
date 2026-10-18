"""
04_fig_s3_outcomes.py
=====================
Henna ADR FAERS Study — Supplementary Figure S3: Outcome & Severity
---------------------------------------------------------------------
Panel A: Donut chart — Serious vs Non-Serious case distribution with
         sub-outcome annotation ring.
Panel B: Stacked horizontal bar — Seriousness by product category with
         chi-square annotation.

Usage
-----
    python scripts/04_fig_s3_outcomes.py [--data-dir data] [--out-dir outputs]

Output
------
    outputs/FigS3_Outcome_Severity.png  (300 DPI)
"""

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from scipy import stats


def parse_args():
    p = argparse.ArgumentParser(description="Generate Supplementary Figure S3.")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--out-dir", default="outputs")
    return p.parse_args()


JAGUA_TERMS = ["jagua", "inkbox"]

def is_jagua(name: str) -> bool:
    return any(t in str(name).lower() for t in JAGUA_TERMS)

BLACK_HENNA_TERMS = [
    "black henna","henna black","henna tattoo (black","henna tattoo(black",
    "black tattoo","nisha henna black","ppd henna","eurus black henna",
    "mira","black hair dye",
]
HAIR_TERMS = ["hair dye","hair henna","hair color","hair colour",
              "hair creme","surya brasil","tancho","parampara"]
PERIOCULAR_TERMS = ["eyebrow","eyelash","periocular","eyelid"]
NATURAL_TERMS = [
    "natural","pure","jamilla","jamila","golecha","asma henna","shweta",
    "royal gift","rainbow","henna powder","henna cone","rivaaj","dulthan",
    "mehandi","cinderella","henna temporary","temporary henna","patel",
    "castle art","henna tattoo - dye","henna tattoo henna","henna used at",
    "listed on sign",
]

def classify_product(name: str) -> str:
    n = str(name).lower()
    if any(t in n for t in PERIOCULAR_TERMS):
        return "Periocular"
    if any(t in n for t in HAIR_TERMS):
        return "Hair Colourant"
    if any(t in n for t in BLACK_HENNA_TERMS):
        return "Black Henna"
    if any(t in n for t in NATURAL_TERMS):
        return "Natural Henna"
    if "black" in n:
        return "Black Henna"
    if "henna" in n:
        return "Natural Henna"
    return "Other"


CAT_ORDER  = ["Black Henna", "Natural Henna", "Hair Colourant", "Periocular", "Other"]
CAT_COLORS = {
    "Black Henna":    "#c0392b",
    "Natural Henna":  "#27ae60",
    "Hair Colourant": "#2980b9",
    "Periocular":     "#8e44ad",
    "Other":          "#7f8c8d",
}


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
    df["Serious"]  = df["Seriousness"] == "Y"
    n = len(df)

    n_serious    = int(df["Serious"].sum())
    n_nonserious = n - n_serious

    # Sub-outcomes
    outcomes_raw = df["Case Outcomes(s)"].fillna("Non-Serious")
    outcome_counter: dict = {}
    for out in outcomes_raw:
        for part in str(out).split(";"):
            part = part.strip()
            if part and part.lower() not in ("", "-"):
                outcome_counter[part] = outcome_counter.get(part, 0) + 1

    # Chi-square: Category × Seriousness
    ct = pd.crosstab(df["Category"], df["Serious"])
    chi2, p_chi2, dof, _ = stats.chi2_contingency(ct)

    # ------------------------------------------------------------------
    # Figure
    # ------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.patch.set_facecolor("white")

    # ---- Panel A: Donut -----------------------------------------------
    sizes = [n_serious, n_nonserious]
    colors = ["#c0392b", "#2ecc71"]
    labels = [f"Serious\nn = {n_serious}\n({n_serious/n*100:.1f}%)",
              f"Non-Serious\nn = {n_nonserious}\n({n_nonserious/n*100:.1f}%)"]

    wedges, _ = ax1.pie(
        sizes, colors=colors, startangle=90,
        wedgeprops=dict(width=0.55, edgecolor="white", linewidth=2),
        counterclock=False,
    )
    ax1.text(0, 0, f"Total\nn = {n}", ha="center", va="center",
             fontsize=12, fontweight="bold", color="#2c3e50")

    # Custom legend below
    legend_patches = [
        mpatches.Patch(color=c, label=l.replace("\n", " "))
        for c, l in zip(colors, labels)
    ]
    ax1.legend(handles=legend_patches, loc="lower center",
               bbox_to_anchor=(0.5, -0.18), fontsize=9,
               framealpha=0.9, edgecolor="#bdc3c7", ncol=2)

    # Annotate sub-outcomes for serious cases
    serious_outcomes = {k: v for k, v in outcome_counter.items()
                        if k != "Non-Serious"}
    note_lines = ["Serious case sub-outcomes:"]
    for k, v in sorted(serious_outcomes.items(), key=lambda x: -x[1]):
        note_lines.append(f"  {k}: n={v}")
    ax1.text(1.15, 0.5, "\n".join(note_lines),
             transform=ax1.transAxes, fontsize=7.5, va="center",
             color="#2c3e50", bbox=dict(boxstyle="round,pad=0.4",
                                        facecolor="#ecf0f1",
                                        edgecolor="#bdc3c7"))

    ax1.set_title("Panel A  —  Serious vs Non-Serious Outcome Distribution",
                  fontsize=11, fontweight="bold", pad=14)

    # ---- Panel B: Stacked bar by category ----------------------------
    ax2.set_facecolor("#f8f9fa")
    cat_serious = ct.reindex(CAT_ORDER, fill_value=0)
    # Ensure columns True/False exist
    for col in [True, False]:
        if col not in cat_serious.columns:
            cat_serious[col] = 0

    present_cats = [c for c in CAT_ORDER if c in cat_serious.index
                    and cat_serious.loc[c, [True, False]].sum() > 0]
    y_pos = np.arange(len(present_cats))

    # Serious bars
    serious_vals    = cat_serious.loc[present_cats, True].values.astype(float)
    nonserious_vals = cat_serious.loc[present_cats, False].values.astype(float)

    ax2.barh(y_pos, serious_vals, color="#c0392b", height=0.6,
             label="Serious", edgecolor="white", linewidth=0.5, zorder=3)
    ax2.barh(y_pos, nonserious_vals, left=serious_vals, color="#2ecc71",
             height=0.6, label="Non-Serious", edgecolor="white",
             linewidth=0.5, zorder=3)

    # Percentage labels
    totals = serious_vals + nonserious_vals
    for i, (s, ns, tot) in enumerate(zip(serious_vals, nonserious_vals, totals)):
        if tot > 0:
            ax2.text(s / 2, i, f"{s:.0f}", va="center", ha="center",
                     fontsize=8, color="white", fontweight="bold")
            ax2.text(s + ns / 2, i, f"{ns:.0f}", va="center", ha="center",
                     fontsize=8, color="white", fontweight="bold")

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(present_cats, fontsize=9)
    ax2.set_xlabel("Number of Cases", fontsize=11, labelpad=6)
    ax2.set_title("Panel B  —  Seriousness by Product Category",
                  fontsize=11, fontweight="bold", pad=14)
    ax2.legend(loc="lower right", fontsize=8.5, framealpha=0.9,
               edgecolor="#bdc3c7")
    ax2.grid(axis="x", linestyle=":", alpha=0.5, color="#bdc3c7", zorder=0)
    ax2.spines[["top", "right"]].set_visible(False)

    # Chi-square annotation
    ax2.text(0.98, 0.02,
             f"χ² = {chi2:.3f}, df = {dof}, p = {p_chi2:.3f}",
             transform=ax2.transAxes, ha="right", va="bottom",
             fontsize=8.5, color="#555555",
             bbox=dict(boxstyle="round,pad=0.3", facecolor="#ecf0f1",
                       edgecolor="#bdc3c7", alpha=0.9))

    plt.tight_layout(pad=2.0)
    out_path = out_dir / "FigS3_Outcome_Severity.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"Saved → {out_path}")


if __name__ == "__main__":
    main()
