# Henna-Associated Adverse Drug Reactions — FAERS Pharmacovigilance Analysis

**Manuscript**: Henna-Associated Adverse Drug Reactions: A Pharmacovigilance Analysis of the FDA FAERS Cosmetic Public Dashboard  
**Journal**: *Cutaneous and Ocular Toxicology* (Manuscript ID: LCOT-2026-0235.R1)  
**Data source**: FDA FAERS Cosmetic Public Dashboard · 2003–2025 · n = 110 cases

---

## Overview

This repository contains the data visualisation and statistical analysis scripts used in the above manuscript. All scripts read directly from the FDA FAERS Cosmetic Public Dashboard data exports and reproduce the figures and summary statistics reported in the paper.

Raw case-level data are **not deposited here** because the source database is freely and publicly accessible in its entirety at:

> https://www.fda.gov/cosmetics/cosmetics-compliance-enforcement/cosmetic-adverse-event-reporting

See [`data/README_data.md`](data/README_data.md) for download instructions, the two excluded cases (Jagua-based products), and the product-category classification scheme.

---

## Repository Structure

```
henna-adr-faers/
├── README.md
├── requirements.txt
├── data/
│   └── README_data.md          ← Data download instructions
├── scripts/
│   ├── 00_classify_and_validate.py   ← Classification + all statistics
│   ├── 01_flow_diagram.py            ← PRISMA data-selection flow diagram
│   ├── 02_fig_s1_temporal.py         ← Supplementary Fig S1: Temporal trend
│   ├── 03_fig_s2_reactions.py        ← Supplementary Fig S2: Top 20 reactions
│   ├── 04_fig_s3_outcomes.py         ← Supplementary Fig S3: Outcome/severity
│   └── 05_graphical_abstract.py      ← Graphical abstract (6-panel)
└── outputs/                          ← Generated figures (gitignored)
```

---

## Quick Start

### 1 — Install dependencies

```bash
pip install -r requirements.txt
```

Requires Python ≥ 3.9.

### 2 — Obtain the FAERS data

Download the six XLSX files listed in [`data/README_data.md`](data/README_data.md) from the FDA FAERS Cosmetic Public Dashboard and place them in the `data/` directory.

### 3 — Run the classification and validation script

```bash
python scripts/00_classify_and_validate.py --data-dir data --out-dir outputs
```

This prints the full statistical validation report and writes `outputs/validation_summary.csv`.

### 4 — Generate all figures

```bash
python scripts/01_flow_diagram.py        --out-dir outputs
python scripts/02_fig_s1_temporal.py     --data-dir data --out-dir outputs
python scripts/03_fig_s2_reactions.py    --data-dir data --out-dir outputs
python scripts/04_fig_s3_outcomes.py     --data-dir data --out-dir outputs
python scripts/05_graphical_abstract.py  --data-dir data --out-dir outputs
```

All figures are saved as 300 DPI PNG files in `outputs/`.

---

## Scripts

| Script | Description | Output |
|---|---|---|
| `00_classify_and_validate.py` | Loads line listing; applies Jagua exclusion; keyword-based product classification; computes sex, seriousness, age, top-20 PTs, Fisher's Exact, chi-square, PRR | `outputs/validation_summary.csv` |
| `01_flow_diagram.py` | PRISMA-style data-selection flow diagram (N=112 → n=110) | `outputs/DataSelection_FlowDiagram_HennaADR.png` |
| `02_fig_s1_temporal.py` | Panel A: Annual case trend 2003–2025 with regulatory milestones; Panel B: Stacked bar by product category | `outputs/FigS1_Temporal_Distribution.png` |
| `03_fig_s2_reactions.py` | Top 20 MedDRA PTs, SOC colour-coded | `outputs/FigS2_Top20_Reactions.png` |
| `04_fig_s3_outcomes.py` | Panel A: Serious/Non-Serious donut; Panel B: Seriousness by category stacked bar with chi-square | `outputs/FigS3_Outcome_Severity.png` |
| `05_graphical_abstract.py` | 6-panel graphical abstract (donut, reactions, temporal, key tiles, demographics, outcomes) | `outputs/Graphical_Abstract_HennaADR.png` |

---

## Methods Summary

### Cohort construction
- Source: FDA FAERS Cosmetic Public Dashboard (all cosmetic adverse event reports containing "henna" in the product name)
- Initial retrieval: N = 112 reports
- Exclusions: 2 cases involving Jagua-based products (Genipa americana) — not true henna (Lawsonia inermis)
- Analytic cohort: **n = 110 cases**

### Product category classification
Products were classified by two investigators independently into five categories (see `data/README_data.md`). The `00_classify_and_validate.py` script implements a keyword-based auto-classifier which may produce minor differences (typically ≤ 5 cases) from the manually adjudicated manuscript values.

### Disproportionality analysis
- Proportional Reporting Ratio (PRR) calculated against the FAERS Cosmetic all-product background query
- Signal threshold: PRR ≥ 2, χ² ≥ 4, n ≥ 3 (Evans 2001)
- PRR background values are embedded as manuscript-reported constants in `00_classify_and_validate.py` because the full FAERS Cosmetic background query file is not included in this repository

### Statistical tests
- Fisher's Exact: Black Henna vs non-Black Henna × Seriousness (scipy.stats)
- Pearson Chi-square: Product Category × Seriousness (scipy.stats)
- All computations reproduced programmatically from the line listing

---

## Reproducibility Note

Minor numerical differences between the automated script outputs and the published manuscript values may arise from:
1. **Product classification**: The keyword classifier is deterministic but may diverge from expert-adjudicated classifications at the margin (ambiguous product names)
2. **PRR background**: The background FAERS query for PRR computation is not deposited; manuscript PRR values are embedded as validated constants
3. **MedDRA PT spelling**: PT text strings in the FAERS export are used as-is; counts are case-insensitive but punctuation-sensitive

These differences do not affect the qualitative conclusions of the manuscript.

---

## Citation

If you use this code in your work, please cite:

> [Authors]. Henna-Associated Adverse Drug Reactions: A Pharmacovigilance Analysis of the FDA FAERS Cosmetic Public Dashboard. *Cutaneous and Ocular Toxicology*, 2026. DOI: [forthcoming]

---

## Licence

Scripts are released under the **MIT Licence**. The underlying FAERS data are in the public domain (US government works). See the FDA FAERS terms of use for any redistribution of the raw data.
