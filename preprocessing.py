"""
preprocessing.py
================
Spend Smart or Spend Status? — Mumbai Consumer Survey
Author : Rishi Agrawal (HarshRi30)

Transforms the raw 500-row Google Forms export
(FINAL_all_500_responses.csv) into the cleaned, fully-encoded dataset
(Dataset_for_Spend_Smart_final.csv) that is loaded into PostgreSQL.

Pipeline
--------
1.  Load raw CSV
2.  Rename long survey column names → short readable names
3.  Encode ordinal / categorical columns to integers
4.  Fix Branded=social status? encoding  (see note below)
5.  Derive class_label from Monthly Income
6.  Explode multi-select columns → binary dummy columns
7.  Drop helper / PII columns (Timestamp, email)
8.  Rename to SQL-friendly lowercase identifiers
9.  Export final CSV

Note — Branded=social status? encoding
---------------------------------------
The original Google Form had 4 options:
    No / Sometimes / Maybe / Yes  →  encoded as  1 / 2 / 3 / 4
This ordering matches how the column is interpreted in all SQL analysis
queries (higher value = stronger perception of brand-as-status).

Usage
-----
    python preprocessing.py
Expects FINAL_all_500_responses.csv in the working directory.
Writes Dataset_for_Spend_Smart_final.csv to the working directory.
"""

import pandas as pd

# ── 0. LOAD ──────────────────────────────────────────────────────────────────

df = pd.read_csv("FINAL_all_500_responses.csv")
print(f"Loaded  : {df.shape[0]} rows × {df.shape[1]} columns")

# ── 1. RENAME LONG SURVEY COLUMNS ───────────────────────────────────────────

df = df.rename(columns={
    "email "                                          : "email",
    "Age Group"                                       : "age_group",
    "Education Level"                                 : "education_level",
    "Monthly Income (₹)"                              : "monthly_income",
    "Area of Residence in Mumbai"                     : "area_of_residence",
    "How often do you shop for consumer products?"    : "shopping_frequency",
    "Which type of products do you generally prefer?" : "product_preference",
    "For which product categories do you prefer branded products?"
                                                      : "branded_products_preference",
    "When buying clothes (e.g., Zudio, Pantaloons vs local street shops), what do you usually prefer?"
                                                      : "clothes_preference",
    " For groceries (e.g., packaged brands vs local kirana stores in Mumbai), what do you prefer?"
                                                      : "grocery_preference",
    "For electronics (e.g., mobile phones, earphones), which do you trust more?"
                                                      : "electronics_preference",
    "What factors influence your purchase decision the most?\n(Select up to 3)"
                                                      : "influential_factors",
    "Branded products offer better quality than unbranded products."
                                                      : "branded_quality",
    " Unbranded products are value for money."        : "unbranded_is_vfm",
    " Do you believe branded products reflect social status?"
                                                      : "branded_is_social_status",
    " I feel more confident using branded products in social situations."
                                                      : "brand__is_confidence",
    " People in Mumbai are influenced by brand image while shopping."
                                                      : "mumbai_brand_influence",
    "Social media and advertisements influence my choice of branded products."
                                                      : "social_media_influence",
    " Local markets in Mumbai (e.g., street markets, local shops) influence my decision to buy unbranded products."
                                                      : "local_market_influence",
    "Shopping malls and branded stores in Mumbai influence my preference for branded products."
                                                      : "mall_influence",
    "Rising cost of living in Mumbai makes me more price-conscious while shopping."
                                                      : "price_consciousness",
    "In your opinion, what best describes your buying behaviour?"
                                                      : "buying_behaviour",
})

# ── 2. ENCODE ORDINAL / CATEGORICAL COLUMNS ──────────────────────────────────

# --- 5-point Likert scales (Strongly Disagree=1 … Strongly Agree=5) ----------
likert_map = {
    "Strongly Disagree": 1,
    "Strongly disagree": 1,
    "Disagree"         : 2,
    "Neutral"          : 3,
    "Agree"            : 4,
    "Strongly Agree"   : 5,
    "Strongly agree"   : 5,
}
likert_cols = [
    "branded_quality",
    "unbranded_is_vfm",
    "brand__is_confidence",
    "mumbai_brand_influence",
    "social_media_influence",
    "local_market_influence",
    "mall_influence",
    "price_consciousness",
]
for col in likert_cols:
    df[col] = df[col].map(likert_map)

# --- Shopping frequency (Rarely=1 … Very frequently=4) -----------------------
df["shopping_frequency"] = df["shopping_frequency"].map({
    "Rarely"          : 1,
    "Occasionally"    : 2,
    "Frequently"      : 3,
    "Very frequently" : 4,
})

# --- Product preference (Mostly branded=1 … Depends=4) ----------------------
df["product_preference"] = df["product_preference"].map({
    "Mostly branded"       : 1,
    "Mostly unbranded"     : 2,
    "Both"                 : 3,
    "Depends on the product": 4,
})

# --- Clothes preference (Branded only=1 … Depends=4) ------------------------
df["clothes_preference"] = df["clothes_preference"].map({
    "Branded stores only"          : 1,
    "Local / unbranded shops only" : 2,
    "Both"                         : 3,
    "Depends on price and occasion": 4,
})

# --- Grocery preference (Branded=1 … Depends=4) -----------------------------
df["grocery_preference"] = df["grocery_preference"].map({
    "Mostly branded packaged products" : 1,
    "Mostly local/unbranded products"  : 2,
    "Depends on availability"          : 3,
    "Both equally"                     : 4,
})

# --- Electronics preference (Branded=1 … Both=4) ----------------------------
df["electronics_preference"] = df["electronics_preference"].map({
    "Branded products"            : 1,
    "Unbranded / local products"  : 2,
    "Depends on warranty and price": 3,
    "both"                        : 4,
})

# --- Buying behaviour (Smart spender=1 … Depends=4) -------------------------
df["buying_behaviour"] = df["buying_behaviour"].map({
    "Smart spender (value-oriented)" : 1,
    "Status-oriented buyer"          : 2,
    "Combination of both"            : 3,
    "Depends on the situation"       : 4,
})

# --- Occupation (Student=1 … Other=5) ----------------------------------------
df["Occupation"] = df["Occupation"].map({
    "Student"                  : 1,
    "Salaried employee"        : 2,
    "Self-employed / Business" : 3,
    "Homemaker"                : 4,
    "Other"                    : 5,
})

# --- Gender (Male=1, Female=2, PNTS=3) ---------------------------------------
df["Gender"] = df["Gender"].map({
    "male"             : 1,
    "female"           : 2,
    "prefer not to say": 3,
})

# --- Branded = social status? (No=1, Sometimes=2, Maybe=3, Yes=4) -------------
# Ordering: No < Sometimes < Maybe < Yes  (ascending brand-status perception)
df["branded_is_social_status"] = df["branded_is_social_status"].map({
    "No"       : 1,
    "Sometimes": 2,
    "Maybe"    : 3,
    "Yes"      : 4,
})

# Rename Occupation & Gender to lowercase now that encoding is done
df = df.rename(columns={"Occupation": "occupation", "Gender": "gender"})

# ── 3. DERIVE CLASS LABEL ─────────────────────────────────────────────────────

income_map = {
    "Not applicable"   : "Poor",
    "Below 20,000"     : "Poor",
    "20,001 \u2013 40,000" : "Lower Middle",   # em-dash
    "40,001 \u2013 60,000" : "Upper Middle",
    "Above 60,000"     : "Rich",
}
df["class_label"] = df["monthly_income"].map(income_map)
print("class_label distribution:")
print(df["class_label"].value_counts())

# ── 4. MULTI-SELECT → BINARY DUMMY COLUMNS ───────────────────────────────────

# Product categories (branded preference)
cat_dummies = df["branded_products_preference"].str.get_dummies(sep=", ")
cat_dummies.columns = [
    "cat_" + c.lower().replace(" ", "_") for c in cat_dummies.columns
]

# Purchase decision factors
factor_dummies = df["influential_factors"].str.get_dummies(sep=", ")
factor_dummies.columns = [
    "factor_" + c.lower().replace(" ", "_") for c in factor_dummies.columns
]

# Drop originals and merge dummies
df = df.drop(columns=["branded_products_preference", "influential_factors"])
df = pd.concat([df, cat_dummies, factor_dummies], axis=1)

print(f"\nAfter dummies: {df.shape[0]} rows × {df.shape[1]} columns")

# ── 5. DROP PII / HELPER COLUMNS ─────────────────────────────────────────────

df = df.drop(columns=["Timestamp", "email"])

# ── 6. FINAL COLUMN ORDER (matches fact_respondents schema) ──────────────────

ordered_cols = [
    "age_group", "gender", "education_level", "occupation",
    "monthly_income", "area_of_residence",
    "shopping_frequency", "product_preference",
    "clothes_preference", "grocery_preference", "electronics_preference",
    "branded_quality", "unbranded_is_vfm", "branded_is_social_status",
    "brand__is_confidence", "mumbai_brand_influence",
    "social_media_influence", "local_market_influence",
    "mall_influence", "price_consciousness",
    "buying_behaviour", "class_label",
    "cat_clothing", "cat_electronics", "cat_footwear",
    "cat_groceries", "cat_personal_care_products",
    "factor_advertisement", "factor_brand_name",
    "factor_price", "factor_quality",
    "factor_recommendations_from_others", "factor_social_status",
]
df = df[ordered_cols]

# ── 7. EXPORT ─────────────────────────────────────────────────────────────────

out_path = "Dataset_for_Spend_Smart_final.csv"
df.to_csv(out_path, index=False)
print(f"\nExported : {out_path}")
print(f"Shape    : {df.shape[0]} rows × {df.shape[1]} columns")
print(f"Columns  : {df.columns.tolist()}")

# ── CODEBOOK (for reference) ──────────────────────────────────────────────────

CODEBOOK = {
    "gender"                  : {1: "Male", 2: "Female", 3: "Prefer not to say"},
    "occupation"              : {1: "Student", 2: "Salaried employee",
                                  3: "Self-employed/Business",
                                  4: "Homemaker", 5: "Other"},
    "shopping_frequency"      : {1: "Rarely", 2: "Occasionally",
                                  3: "Frequently", 4: "Very frequently"},
    "product_preference"      : {1: "Mostly branded", 2: "Mostly unbranded",
                                  3: "Both", 4: "Depends on product"},
    "clothes_preference"      : {1: "Branded only", 2: "Local/unbranded",
                                  3: "Both", 4: "Depends on price/occasion"},
    "grocery_preference"      : {1: "Branded packaged", 2: "Local/unbranded",
                                  3: "Depends on availability", 4: "Both equally"},
    "electronics_preference"  : {1: "Branded", 2: "Unbranded/local",
                                  3: "Depends on warranty/price", 4: "Both"},
    "buying_behaviour"        : {1: "Smart spender", 2: "Status-oriented",
                                  3: "Combination", 4: "Depends on situation"},
    "likert_5pt (all)"        : {1: "Strongly Disagree", 2: "Disagree",
                                  3: "Neutral", 4: "Agree", 5: "Strongly Agree"},
    "branded_is_social_status": {1: "No", 2: "Sometimes", 3: "Maybe", 4: "Yes"},
}
