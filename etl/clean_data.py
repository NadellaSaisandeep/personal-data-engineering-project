# etl/clean_data.py (fixed, debug-friendly)
import os
import pandas as pd
import numpy as np
import re

RAW_PATH = "data/raw/synthetic_products.csv"
OUT_DIR = "data/extracted"
OUT_PATH = os.path.join(OUT_DIR, "cleaned_products.csv")
os.makedirs(OUT_DIR, exist_ok=True)

print("DEBUG: Starting ETL")
print("DEBUG: Raw path exists?", os.path.exists(RAW_PATH))
if os.path.exists(RAW_PATH):
    print("DEBUG: Raw file size (bytes):", os.path.getsize(RAW_PATH))

def parse_price(price_raw):
    if pd.isna(price_raw):
        return np.nan
    s = str(price_raw)
    nums = re.findall(r"[\d,]+", s)
    if not nums:
        return np.nan
    n = nums[0].replace(",", "")
    try:
        return float(n)
    except:
        return np.nan

def normalize_text(s):
    if pd.isna(s):
        return s
    return str(s).strip()

def main():
    print("DEBUG: About to read CSV")
    try:
        df = pd.read_csv(RAW_PATH)
    except Exception as e:
        print("ERROR reading CSV:", repr(e))
        return

    print("Loaded rows:", len(df))
    print("Columns:", list(df.columns)[:50])

    # Normalize text fields
    df['title'] = df.get('title', pd.Series(dtype=str)).apply(normalize_text)
    df['supplier_name'] = df.get('supplier_name', pd.Series(dtype=str)).apply(normalize_text)
    df['location'] = df.get('location', pd.Series(dtype=str)).apply(normalize_text)

    # Parse numeric fields robustly
    df['price_numeric'] = df.get('price_raw', pd.Series()).apply(parse_price)
    # Ensure moq is numeric
    if 'moq' in df.columns:
        df['moq'] = pd.to_numeric(df['moq'], errors='coerce').fillna(1).astype(int)
    else:
        df['moq'] = 1

    # Drop rows without title (essential)
    before = len(df)
    df = df[df['title'].notna() & (df['title'] != "")]
    after_drop = len(df)
    print(f"Dropped {before-after_drop} rows without title")

    # Deduplicate by title + supplier_name
    before = len(df)
    df = df.drop_duplicates(subset=['title','supplier_name'])
    after = len(df)
    print(f"Dropped {before-after} duplicate rows")

    # Fill missing price_numeric with group median using transform (preserves index)
    # First, ensure price_numeric is float dtype
    df['price_numeric'] = pd.to_numeric(df['price_numeric'], errors='coerce')

    # Compute group medians and fillna using transform
    try:
        medians = df.groupby('category')['price_numeric'].transform('median')
        df['price_numeric'] = df['price_numeric'].fillna(medians)
    except Exception as e:
        print("WARNING: group median fill failed:", repr(e))
        # fallback: fill with global median
        global_median = df['price_numeric'].median()
        df['price_numeric'] = df['price_numeric'].fillna(global_median)

    # Compute price per moq safely
    df['price_per_moq'] = df['price_numeric'] / df['moq'].replace(0,1)

    # Remove extreme outliers per category using z-score (4 sigma)
    def remove_outliers(group):
        vals = group['price_numeric'].astype(float)
        mean = vals.mean()
        std = vals.std(ddof=0) if vals.std(ddof=0) > 0 else 1.0
        mask = (np.abs((vals - mean) / std) < 4)
        return group[mask]

    try:
        df = df.groupby('category', group_keys=False).apply(remove_outliers)
    except Exception as e:
        print("WARNING: outlier removal failed:", repr(e))

    # Final sanity: reset index and write CSV
    df = df.reset_index(drop=True)
    try:
        df.to_csv(OUT_PATH, index=False)
        print("Saved cleaned data to", OUT_PATH)
        print("Final rows:", len(df))
    except Exception as e:
        print("ERROR writing CSV:", repr(e))

if __name__ == "__main__":
    main()
