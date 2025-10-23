
import os
import pandas as pd
import numpy as np
import re
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

RAW_DIR = "data/raw"
OUTPUT_DIR = "data/extracted"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def parse_price(price):
    """Extract numeric value from price text (e.g., '₹500 / piece', '$20', '1,000-2,000')."""
    if pd.isna(price):
        return np.nan
    text = str(price).replace(",", "").strip()
    match = re.findall(r"[\d.]+", text)
    if not match:
        return np.nan
    nums = [float(x) for x in match]
    return np.mean(nums) if len(nums) > 1 else nums[0]

def clean_text(x):
    """Basic text cleaner."""
    if pd.isna(x):
        return ""
    return re.sub(r"\s+", " ", str(x)).strip()

def detect_latest_file():
    """Find the most relevant raw CSV automatically."""
    csv_files = [os.path.join(RAW_DIR, f) for f in os.listdir(RAW_DIR) if f.endswith(".csv")]
    if not csv_files:
        raise FileNotFoundError("No raw CSV files found in data/raw/")
    latest = max(csv_files, key=os.path.getmtime)
    logging.info(f"Using latest raw file: {os.path.basename(latest)}")
    return latest


def main():
    logging.info("Starting ETL pipeline...")

    raw_file = detect_latest_file()
    df = pd.read_csv(raw_file, low_memory=False)
    logging.info(f"Loaded {len(df)} rows and {len(df.columns)} columns.")

  
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

 
    rename_map = {
        "title": "product_name",
        "supplier_name": "supplier",
        "company": "supplier",
        "price": "price_raw",
        "price_value": "price_raw",
        "price_text": "price_raw",
        "location": "location",
        "category": "category",
        "product_url": "product_url",
    }
    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})

   
    for col in ["product_name", "supplier", "price_raw", "location", "category"]:
        if col not in df.columns:
            df[col] = ""

   
    for col in ["product_name", "supplier", "location", "category"]:
        df[col] = df[col].astype(str).apply(clean_text)

 
    df["price_numeric"] = df["price_raw"].apply(parse_price)

    
    before = len(df)
    df = df.drop_duplicates(subset=["product_name", "supplier"])
    df = df[df["product_name"].str.strip() != ""]
    logging.info(f"Dropped {before - len(df)} duplicates or empty rows.")

    
    if "price_numeric" in df:
        p99 = df["price_numeric"].quantile(0.99)
        df.loc[df["price_numeric"] > p99, "price_numeric"] = np.nan

  
    out_file = os.path.join(OUTPUT_DIR, "cleaned_real_combined_products.csv")
    df.to_csv(out_file, index=False)
    logging.info(f" Cleaned data saved to {out_file}")
    logging.info(f"Final shape: {df.shape}")

if __name__ == "__main__":
    main()
