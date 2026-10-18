"""
05_graphical_abstract.py
========================
Henna ADR FAERS Study — Graphical Abstract (6-Panel Layout)
------------------------------------------------------------
Generates a publication-quality graphical abstract with:
  Panel A: Donut — product category distribution
  Panel B: Horizontal bars — top 8 adverse reactions
  Panel C: Line chart — temporal trend 2003–2025
  Panel D: Key metric tiles
  Panel E: Demographics (sex and paediatric)
  Panel F: Outcomes donut

Usage
-----
    python scripts/05_graphical_abstract.py [--data-dir data] [--out-dir outputs]

Output
------
    outputs/Graphical_Abstract_HennaADR.png  (300 DPI, 18×11.8 in)
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd


def parse_args():
    p = argparse.ArgumentParser(description="Generate graphical abstract.")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--out-dir", default="outputs")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Classification helpers (shared with other scripts)
# ---------------------------------------------------------------------------
JAGUA_TERMS = ["jagua", "inkbox"]
def is_jagua(name): return any(t in str(name).lower() for t in JAGUA_TERMS)

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

def classify_product(name):
    n = str(name).lower()
    if any(t in n for t in PERIOCULAR_TERMS): return "Periocular"
    if any(t in n for t in HAIR_TERMS):       return "Hair Colourant"
    if any(t in n for t in BLACK_HENNA_TERMS):return "Black Henna"
    if any(t in n for t in NATURAL_TERMS):    return "Natural Henna"
    if "black" in n:                           return "Black Henna"
    if "henna" in n:                           return "Natural Henna"
    return "Other"

def age_to_years(age_val, unit):
    try: val = float(age_val)
    except: return None
    u = str(unit).upper()
    if "YR" in u: return val
    if "MO" in u: return val / 12.0
    if "DY" in u: return val / 365.25
    if "WK" in u: return val / 52.18
    return val


# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
NAVY    = "#1a3a5c"
CAT_COLORS = {
    "Black Henna":    "#c0392b",
    "Natural Henna":  "#27ae60",
    "Hair Colourant": "#2980b9",
    "Periocular":     "#8e44ad",
    "Other":          "#7f8c8d",
}
CAT_ORDER = ["Black Henna","Natural Henna","Hair Colourant","Periocular","Other"]

SOC_COLORS = {
    "Skin":    "#8b1a1a",
    "Immune":  "#6c3483",
    "General": "#1a5276",
    "Injury":  "#b7770d",
    "Nervous": "#117a65",
    "GI":      "#1e8449",
}
PT_SOC = {
    "Pruritus":"Skin","Hypersensitivity":"Immune","Blister":"Skin",
    "Erythema":"Skin","Rash":"Skin","Swelling":"General",
    "Burning Sensation":"Nervous","Urticaria":"Skin",
}

WHITE = "white"


# ---------------------------------------------------------------------------
# Helper: tile box
# ---------------------------------------------------------------------------
def draw_tile(ax, x, y, w, h, big_text, sub_text, bg_color,
              big_size=20, sub_size=9.5):
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0,rounding_size=0.04",
                         facecolor=bg_color, edgecolor="none",
                         transform=ax.transAxes, clip_on=False, zorder=3)
    ax.add_patch(box)
    ax.text(x + w/2, y + h*0.62, big_text, transform=ax.transAxes,
            ha="center", va="center", fontsize=big_size, fontweight="bold",
            color=WHITE, zorder=4)
    ax.text(x + w/2, y + h*0.22, sub_text, transform=ax.transAxes,
            ha="center", va="center", fontsize=sub_size, color=WHITE,
            zorder=4, linespacing=1.2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()
    data_dir = Path(args.data_dir)
    out_dir  = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ll_path = data_dir / "Line_Listing_Henna_.xlsx"
    if not ll_path.exists():
        sys.exit(f"ERROR: {ll_path} not found. See data/README_data.md.")

    # ---------- Load and prepare data ----------
    df_raw = pd.read_excel(ll_path)
    df = df_raw[~df_raw["Suspect Reported Product Name"].apply(is_jagua)].copy()
    df["Category"] = df["Suspect Reported Product Name"].apply(classify_product)
    df["Serious"]  = df["Seriousness"] == "Y"
    df["Year"] = pd.to_datetime(
        df["FDA Initial Received Date"], format="%d-%b-%Y", errors="coerce"
    ).dt.year
    df["Age_years"] = df.apply(
        lambda r: age_to_years(r["Patient Age"], r["Patient Age Unit"]), axis=1
    )
    n = len(df)

    # MedDRA PT counts
    pt_counter = Counter()
    for pts in df["Event MedDRA PT(s)"].dropna():
        for pt in str(pts).split(";"):
            pt = pt.strip()
            if pt and pt.lower() not in ("","-","none"):
                pt_counter[pt] += 1
    top8 = pt_counter.most_common(8)

    # Temporal
    all_years = list(range(2003, 2026))
    yearly = df.dropna(subset=["Year"]).groupby("Year").size().reindex(all_years, fill_value=0)

    # Demographics
    sex_counts = df["Sex"].value_counts()
    n_female = int(sex_counts.get("Female", 0))
    n_male   = int(sex_counts.get("Male", 0))
    n_unk_sex = int(sex_counts.get("Not Specified", 0))
    known_age = df["Age_years"].notna()
    n_paed = int((df["Age_years"] < 18).sum())
    n_age_known = int(known_age.sum())
    n_serious = int(df["Serious"].sum())
    n_nonserious = n - n_serious
    cat_counts = df["Category"].value_counts()

    # ------------------------------------------------------------------
    # Figure
    # ------------------------------------------------------------------
    fig = plt.figure(figsize=(18, 11.8), facecolor=NAVY)
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.38, wspace=0.32,
                           left=0.05, right=0.96, top=0.88, bottom=0.12)

    ax_a = fig.add_subplot(gs[0, 0])   # Donut
    ax_b = fig.add_subplot(gs[0, 1])   # Top reactions
    ax_c = fig.add_subplot(gs[0, 2])   # Temporal
    ax_d = fig.add_subplot(gs[1, 0])   # Key tiles
    ax_e = fig.add_subplot(gs[1, 1])   # Demographics
    ax_f = fig.add_subplot(gs[1, 2])   # Outcomes

    panel_bg = "#1e2d40"
    for ax in [ax_a, ax_b, ax_c, ax_d, ax_e, ax_f]:
        ax.set_facecolor(panel_bg)
        for spine in ax.spines.values():
            spine.set_edgecolor("#2c3e50")

    # ---- Panel A: Product category donut ----------------------------
    sizes  = [cat_counts.get(c, 0) for c in CAT_ORDER if cat_counts.get(c, 0) > 0]
    labels = [c for c in CAT_ORDER if cat_counts.get(c, 0) > 0]
    colors = [CAT_COLORS[c] for c in labels]
    wedges, _ = ax_a.pie(sizes, colors=colors, startangle=140,
                         wedgeprops=dict(width=0.55, edgecolor=NAVY, linewidth=1.5),
                         counterclock=False)
    ax_a.text(0, 0, f"{n}\nCases", ha="center", va="center",
              fontsize=14, fontweight="bold", color=WHITE)
    ax_a.set_title("Product Categories", color=WHITE, fontsize=10.5,
                   fontweight="bold", pad=8)
    legend_p = [mpatches.Patch(color=CAT_COLORS[c],
                               label=f"{c}\n({cat_counts.get(c,0)/n*100:.1f}%)")
                for c in labels]
    ax_a.legend(handles=legend_p, loc="lower center",
                bbox_to_anchor=(0.5, -0.32), fontsize=6.5,
                framealpha=0, labelcolor=WHITE, ncol=2)

    # ---- Panel B: Top 8 reactions -----------------------------------
    ax_b.set_facecolor(panel_bg)
    pts_b  = [t[0] for t in top8][::-1]
    cnts_b = [t[1] for t in top8][::-1]
    pcts_b = [c/n*100 for c in cnts_b]
    bar_colors_b = [CAT_COLORS.get(PT_SOC.get(p, "Other"),
                                   SOC_COLORS.get(PT_SOC.get(p, ""), "#7f8c8d"))
                    for p in pts_b]
    yp = np.arange(len(pts_b))
    ax_b.barh(yp, cnts_b, color=bar_colors_b, height=0.62,
              edgecolor="none", zorder=3)
    for i, (c, pct) in enumerate(zip(cnts_b, pcts_b)):
        ax_b.text(c + 0.3, i, f"{pct:.1f}%", va="center", color=WHITE,
                  fontsize=7.5)
    ax_b.set_yticks(yp)
    ax_b.set_yticklabels(pts_b, color=WHITE, fontsize=8)
    ax_b.tick_params(colors=WHITE)
    ax_b.xaxis.label.set_color(WHITE)
    ax_b.set_xlabel("Cases (n)", color=WHITE, fontsize=9)
    ax_b.set_title("Top 8 Adverse Reactions", color=WHITE,
                   fontsize=10.5, fontweight="bold", pad=8)
    ax_b.set_xlim(0, max(cnts_b) * 1.25)
    ax_b.spines[["top","right"]].set_visible(False)
    ax_b.spines[["left","bottom"]].set_edgecolor("#4a6278")
    ax_b.grid(axis="x", color="#2c3e50", linestyle=":", alpha=0.5)
    ax_b.tick_params(axis="x", colors=WHITE)

    # ---- Panel C: Temporal line ------------------------------------
    ax_c.set_facecolor(panel_bg)
    ax_c.plot(all_years, yearly.values, color="#3498db", linewidth=2,
              marker="o", markersize=4, markerfacecolor=WHITE,
              markeredgewidth=1.2, zorder=3)
    ax_c.fill_between(all_years, yearly.values, alpha=0.15, color="#3498db")
    for yr, label, col in [(2009,"EU PPD\nRestriction","#e67e22"),
                           (2022,"MoCRA\n2022","#1abc9c")]:
        ax_c.axvline(yr, color=col, linestyle="--", linewidth=1.2, alpha=0.8)
        ax_c.text(yr + 0.2, yearly.max() * 0.05, label,
                  color=col, fontsize=6.5, fontweight="bold")
    ax_c.set_xticks(range(2003, 2026, 4))
    ax_c.tick_params(colors=WHITE, labelsize=7.5)
    ax_c.set_xlabel("Year", color=WHITE, fontsize=9)
    ax_c.set_ylabel("Cases (n)", color=WHITE, fontsize=9)
    ax_c.set_title("Temporal Trend (2003–2025)", color=WHITE,
                   fontsize=10.5, fontweight="bold", pad=8)
    ax_c.spines[["top","right"]].set_visible(False)
    ax_c.spines[["left","bottom"]].set_edgecolor("#4a6278")
    ax_c.yaxis.label.set_color(WHITE)
    ax_c.grid(color="#2c3e50", linestyle=":", alpha=0.5)

    # ---- Panel D: Key metric tiles ----------------------------------
    ax_d.set_xlim(0, 1); ax_d.set_ylim(0, 1); ax_d.axis("off")
    tiles = [
        (0.01, 0.55, 0.46, 0.42, f"{n}", "Total Cases",       "#c0392b"),
        (0.53, 0.55, 0.46, 0.42, f"{n_serious/n*100:.1f}%", "Serious Cases", "#8e44ad"),
        (0.01, 0.05, 0.46, 0.42, f"{n_female/n*100:.1f}%", "Female", "#2980b9"),
        (0.53, 0.05, 0.46, 0.42, f"{n_paed/n_age_known*100:.1f}%", "Paediatric\n(<18 yr)", "#16a085"),
    ]
    for x, y, w, h, big, sub, bg in tiles:
        draw_tile(ax_d, x, y, w, h, big, sub, bg)
    ax_d.set_title("Key Metrics", color=WHITE, fontsize=10.5,
                   fontweight="bold", pad=8)

    # ---- Panel E: Demographics bar ----------------------------------
    ax_e.set_facecolor(panel_bg)
    sex_labels  = ["Female", "Male", "Unknown"]
    sex_vals    = [n_female, n_male, n_unk_sex]
    sex_colors  = ["#e84393", "#3498db", "#7f8c8d"]
    xe = np.arange(3)
    bars_e = ax_e.bar(xe, sex_vals, color=sex_colors, width=0.5,
                      edgecolor="none", zorder=3)
    for bar, val in zip(bars_e, sex_vals):
        ax_e.text(bar.get_x() + bar.get_width()/2, val + 0.5,
                  f"n={val}", ha="center", va="bottom",
                  color=WHITE, fontsize=8.5, fontweight="bold")
    ax_e.set_xticks(xe)
    ax_e.set_xticklabels(sex_labels, color=WHITE, fontsize=9)
    ax_e.tick_params(colors=WHITE)
    ax_e.set_ylabel("Cases (n)", color=WHITE, fontsize=9)
    ax_e.set_title("Sex Distribution", color=WHITE,
                   fontsize=10.5, fontweight="bold", pad=8)
    ax_e.spines[["top","right"]].set_visible(False)
    ax_e.spines[["left","bottom"]].set_edgecolor("#4a6278")
    ax_e.grid(axis="y", color="#2c3e50", linestyle=":", alpha=0.5)
    ax_e.text(0.5, 0.92,
              f"62.0% of age-known cases are paediatric",
              transform=ax_e.transAxes, ha="center", fontsize=7.5,
              color="#f39c12", fontstyle="italic")

    # ---- Panel F: Outcomes donut ------------------------------------
    out_sizes  = [n_serious, n_nonserious]
    out_colors = ["#c0392b","#2ecc71"]
    out_labels = [f"Serious\n({n_serious/n*100:.1f}%)",
                  f"Non-Serious\n({n_nonserious/n*100:.1f}%)"]
    wedges_f, _ = ax_f.pie(out_sizes, colors=out_colors, startangle=90,
                            wedgeprops=dict(width=0.52, edgecolor=NAVY, linewidth=1.5),
                            counterclock=False)
    ax_f.text(0, 0, f"{n_serious/n*100:.1f}%\nSerious",
              ha="center", va="center", fontsize=11,
              fontweight="bold", color=WHITE)
    ax_f.set_title("Outcome Classification", color=WHITE,
                   fontsize=10.5, fontweight="bold", pad=8)
    legend_f = [mpatches.Patch(color=c, label=l)
                for c, l in zip(out_colors, out_labels)]
    ax_f.legend(handles=legend_f, loc="lower center",
                bbox_to_anchor=(0.5, -0.22), fontsize=7.5,
                framealpha=0, labelcolor=WHITE, ncol=2)

    # ------------------------------------------------------------------
    # Title and footer
    # ------------------------------------------------------------------
    fig.text(0.5, 0.93,
             "Henna-Associated Adverse Drug Reactions: FDA FAERS Pharmacovigilance Analysis",
             ha="center", fontsize=14, fontweight="bold", color=WHITE)
    fig.text(0.5, 0.905,
             f"n = {n} Cases · FDA FAERS Cosmetic Public Dashboard · 2003–2025",
             ha="center", fontsize=10, color="#95a5a6")
    fig.text(0.5, 0.04,
             "Black Henna products carry the highest ADR burden · Cutaneous and Ocular Toxicology",
             ha="center", fontsize=8.5, color="#bdc3c7", fontstyle="italic")

    out_path = out_dir / "Graphical_Abstract_HennaADR.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight",
                facecolor=NAVY, edgecolor="none")
    plt.close(fig)
    print(f"Saved → {out_path}")


if __name__ == "__main__":
    main()
