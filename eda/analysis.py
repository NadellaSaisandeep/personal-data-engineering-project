# eda/analysis.py
"""
Exploratory Data Analysis (EDA) on cleaned B2B product data
Generates summary stats and visualizations saved in eda/plots/
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

# Ensure directories
os.makedirs("eda/plots", exist_ok=True)

# Load the cleaned data
CLEAN_PATH = "data/extracted/cleaned_products.csv"
if not os.path.exists(CLEAN_PATH):
    raise FileNotFoundError(f"Cleaned file not found at {CLEAN_PATH}")

df = pd.read_csv(CLEAN_PATH)
print("✅ Loaded cleaned data")
print("Rows:", len(df))
print("Columns:", list(df.columns))

# --- Basic overview ---
print("\n📊 Category counts:")
print(df['category'].value_counts())

print("\n💰 Price summary:")
print(df['price_numeric'].describe())

# --- Plot 1: Top 10 suppliers ---
top_suppliers = df['supplier_name'].value_counts().head(10)
plt.figure(figsize=(8,5))
top_suppliers.plot(kind='barh', color='teal')
plt.gca().invert_yaxis()
plt.title("Top 10 Suppliers by Listing Count")
plt.xlabel("Number of Listings")
plt.tight_layout()
plt.savefig("eda/plots/top_suppliers.png")
print("📈 Saved: eda/plots/top_suppliers.png")

# --- Plot 2: Median price per category ---
avg_price = df.groupby('category')['price_numeric'].median().sort_values()
plt.figure(figsize=(8,5))
avg_price.plot(kind='bar', color='coral')
plt.title("Median Price by Category")
plt.ylabel("Price (INR)")
plt.tight_layout()
plt.savefig("eda/plots/median_price_by_category.png")
print("📈 Saved: eda/plots/median_price_by_category.png")

# --- Plot 3: Price distribution ---
plt.figure(figsize=(8,5))
df['price_numeric'].plot(kind='hist', bins=50, color='skyblue', edgecolor='black')
plt.title("Price Distribution")
plt.xlabel("Price (INR)")
plt.tight_layout()
plt.savefig("eda/plots/price_distribution.png")
print("📈 Saved: eda/plots/price_distribution.png")

# --- Plot 4: Rating vs Price ---
plt.figure(figsize=(8,5))
plt.scatter(df['price_numeric'], df['rating'], alpha=0.5, s=10, color='purple')
plt.xscale('log')
plt.xlabel("Price (INR, log scale)")
plt.ylabel("Rating")
plt.title("Rating vs Price Scatter")
plt.tight_layout()
plt.savefig("eda/plots/rating_vs_price.png")
print("📈 Saved: eda/plots/rating_vs_price.png")

# --- Plot 5: Listings over time ---
df['listed_at'] = pd.to_datetime(df['listed_at'], errors='coerce')
df['listed_month'] = df['listed_at'].dt.to_period("M")
monthly_counts = df.groupby('listed_month').size()
plt.figure(figsize=(8,5))
monthly_counts.plot(kind='line', marker='o', color='green')
plt.title("Listings Over Time (Synthetic Data)")
plt.ylabel("Number of Listings")
plt.tight_layout()
plt.savefig("eda/plots/listings_over_time.png")
print("📈 Saved: eda/plots/listings_over_time.png")

print("\n✅ EDA completed! All charts saved in eda/plots/")
