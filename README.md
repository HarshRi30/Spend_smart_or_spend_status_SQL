# Spend Smart or Spend Status?
### A Cross-Class Analysis of Consumer Buying Behaviour Towards Branded vs Unbranded Products in Mumbai

---

## Overview

This project analyzes consumer buying behaviour across Mumbai's socioeconomic spectrum - examining whether people buy branded products for quality (smart spending) or for social status. The dataset covers 500 respondents across 5 income classes and 5 Mumbai regions, built from a Google Forms survey and synthetically augmented to ensure class-level representation.

The full pipeline covers data collection, preprocessing in Python, PostgreSQL schema design, and 22 structured SQL queries across 4 analysis areas.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python (pandas) | Data cleaning, encoding, dummy variable creation |
| PostgreSQL 17 | Relational schema, data storage, analysis queries |
| pgAdmin 4 | Query execution and data import |
| Power BI | Dashboard and visualization (in progress) |

---

## Dataset

| Attribute | Detail |
|---|---|
| Total Respondents | 500 |
| Total Columns | 34 |
| Survey Tool | Google Forms |
| Geography | Mumbai — 5 regions |
| Income Classes | Poor \| Lower Middle \| Upper Middle \| Rich |
| Source | Google Forms survey — original responses supplemented with simulated entries to ensure class-level representation across all 5 income segments |

**Regions covered:** South Mumbai, Western Suburbs, Central Suburbs, Navi Mumbai, Thane

> **Privacy Notice:** The `email` column present in the raw survey data has been removed from this repository to protect respondent privacy. All analysis in this project is based solely on the remaining 33 anonymised columns.

**Preprocessing steps:**
- Encoded all categorical columns to numeric
- Fixed encoding bug in `branded_is_social_status` column (0–3 → 1–4)
- Derived `class_label` from `monthly_income`
- Exploded two multi-select columns (`Branded products preference`, `Influential factors`) into 11 binary dummy columns using `pandas.get_dummies()`
- Final dataset: 500 rows × 34 columns, fully numeric and query-ready

---

## Repository Structure

```
spend-smart-sql/
│
├── README.md
├── schema.sql               -- CREATE TABLE script
├── analysis.sql             -- All 22 analysis queries with findings
└── Dataset_for_Spend_Smart_final.csv   -- Final cleaned dataset
```

---

## Key Findings

### Demographics
- Dataset is nearly 50-50 gender split (Male 49.8%, Female 46.2%)
- Central Suburbs has the most respondents (26%) - dominated by Poor class
- Rich class is concentrated in South Mumbai (64 out of 91 South Mumbai respondents)

### Brand Affinity
- Brand affinity rises with income: Rich (4.07) → Upper Middle (3.68) → Lower Middle (3.13) → Poor (3.08)
- South Mumbai scores highest brand affinity (4.05), Navi Mumbai lowest (3.26)
- Income and brand affinity have a **0.53 Pearson correlation** - moderate and statistically meaningful
- **Biggest insight:** Poor class scores higher on brand influence awareness (3.63) than Lower Middle (3.49) — they see brand culture around them but cannot participate in it

### Brand vs Value Gap
- Rich class: quality belief (4.18) vs VFM belief (2.36) → gap of **+1.83** - strongly brand-biased
- Poor class: quality belief (2.93) vs VFM belief (3.83) → gap of **-0.91** - trust unbranded for value
- The gap flips sign exactly at the class boundary between Upper Middle and Lower Middle

### Buying Behaviour
- Overall: Smart Spender 36.2% \| Combination 25.8% \| Status-oriented 21.8% \| Depends 16.2%
- **42.4% of Rich respondents are status-oriented** vs only **5.7% of Lower Middle**
- Status-oriented buyers have highest brand affinity (4.01) and lowest price consciousness (2.77)
- Smart Spenders are the exact opposite — brand affinity 3.18, price consciousness 3.84
- 56.9% of all status-oriented buyers live in South Mumbai or Western Suburbs

### Purchase Factors
- Quality (356) and Price (328) dominate overall — Mumbai consumers are fundamentally rational
- **Top factor by class:** Rich → Brand name (169) \| Poor → Price (164) \| LMC → Price (83) \| UMC → Quality (41)
- Rich class cites both Price AND Brand name together most (42 respondents, 36.5%) — they evaluate cost even while being brand-driven
- Price consciousness vs status belief gap nearly disappears for Rich (+0.03) — they are equally price and status aware

### Category Preferences
- Electronics is the most universally branded category - even Poor class at 65.9%
- Groceries is least brand-loyal across all classes - Rich only 26.1%, Poor just 7.3%
- Clothing separates classes most sharply - Rich 82.1% vs Poor 28.5%
- Personal care is surprisingly high for Poor (63.7%) - trust in branded health/hygiene products

---

## SQL Techniques Used

- `GROUP BY` with `COUNT`, `SUM`, `AVG`, `ROUND`
- Window functions - `RANK() OVER (PARTITION BY ...)`, `SUM() OVER ()`
- `CASE WHEN` for conditional aggregation and label decoding
- CTEs (`WITH ... AS`) for multi-step analysis
- `CORR()` for Pearson correlation coefficient
- `UNION ALL` for unpivoting factor columns
- Percentage calculations within and across groups

---

## Analysis Areas

| # | Area | Queries |
|---|---|---|
| 1 | Demographics & Distribution | Q1 – Q4 |
| 2 | Brand Affinity Analysis | Q5 – Q8 |
| 3 | Buying Behaviour Analysis | Q9 – Q12 |
| 4 | Purchase Factor Analysis | Q13 – Q17 |
| 5 | Intermediate Analysis | Q18 – Q22 |

---

## Status

- [x] Data collection and preprocessing
- [x] PostgreSQL schema design and data import
- [x] 22 SQL analysis queries completed
- [ ] Power BI dashboard (in progress)

---

## Author

**Rishi Agrawal**
B.Tech CSE (Data Science) — Shri Ramdeobaba College of Engineering and Management, Nagpur
[GitHub](https://github.com/HarshRi30) | [LinkedIn](https://www.linkedin.com/in/rishi-agrawal30)
