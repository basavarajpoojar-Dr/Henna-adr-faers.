# Data Access Instructions

## Source

All case data used in this study are derived from the **FDA FAERS Cosmetic Public Dashboard**:

> https://www.fda.gov/cosmetics/cosmetics-compliance-enforcement/cosmetic-adverse-event-reporting

The dashboard allows free public access to adverse event reports submitted under the Modernization of Cosmetics Regulation Act (MoCRA), 21 U.S.C. § 364 and §364i.

## Search Parameters Used

- **Product category**: Cosmetics
- **Search terms**: "henna" (all product name variants)
- **Date range**: All available records (2003 – 2025)
- **Data access date**: March 2025

## Files Required

Download and place the following files in this `data/` directory before running any script:

| Filename | Description |
|---|---|
| `Line_Listing_Henna_.xlsx` | Full case-level line listing (primary analysis file) |
| `Case_Count_by_Received_Year_Henna_.xlsx` | Annual case counts |
| `Case_Count_by_Reaction_Henna_.xlsx` | Reaction (MedDRA PT) frequency table |
| `Case_Count_by_Sex_Henna_.xlsx` | Sex distribution |
| `Case_Count_by_Age_Group_Henna_.xlsx` | Age group distribution |
| `Case_Count_by_Product_Name_Henna_.xlsx` | Product name frequency table |

## Exclusions Applied

Two cases (n=2) were excluded prior to analysis:

| Product Name | Reason |
|---|---|
| Henna City Jagua Ink Tattoo Kit | Jagua-based product (Genipa americana), not henna |
| Inkbox Henna | Jagua-based product (Genipa americana), not henna |

Final analytic cohort: **n = 110 cases**

## Product Category Classification

Products were classified into five categories by two investigators independently, with discrepancies resolved by consensus:

| Category | Classification Basis |
|---|---|
| Black Henna | Product name explicitly references "black henna" or PPD-containing composition |
| Natural Henna | Traditional Lawsonia inermis products without PPD attribution |
| Hair Colourant | Products used as hair dye applied via henna-like application route |
| Periocular | Products applied to eyebrows or eyelashes |
| Other | Products not classifiable into the above categories |

> **Note**: The `scripts/00_classify_and_validate.py` script implements a keyword-based auto-classifier. Automated classification may differ from the expert-reviewed manuscript values by a small number of cases (typically ≤5). The manuscript used investigator-adjudicated classifications.

## Citation

If you use this code or data derivation in your work, please cite:

> [Author names redacted for peer review]. Henna-associated adverse drug reactions: a pharmacovigilance analysis of the FDA FAERS Cosmetic Public Dashboard. *
