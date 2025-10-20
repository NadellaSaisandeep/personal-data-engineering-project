# crawler/generate_synthetic_data.py
"""
Generate a realistic synthetic B2B product dataset for the take-home.
Outputs CSV to data/raw/synthetic_products.csv
"""

import os
import random
from faker import Faker
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

OUT_DIR = "data/raw"
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, "synthetic_products.csv")

CATEGORIES = [
    "Industrial Machinery",
    "Electronics",
    "Textiles",
    "Chemical Supplies",
    "Packaging",
    "Construction Equipment"
]

BRANDS = [
    "Apex Engineering", "Metro Components", "PrimeTextiles", "Nova Chemicals",
    "GigaElectro", "Suresh Fabrics", "Vijay Industries", "Mahadev Works",
    "OmniPack", "RoboMach"
]

LOCATIONS = [
    "Mumbai, Maharashtra", "Delhi, Delhi", "Chennai, Tamil Nadu", "Bengaluru, Karnataka",
    "Pune, Maharashtra", "Ahmedabad, Gujarat", "Hyderabad, Telangana", "Kolkata, West Bengal",
    "Faridabad, Haryana", "Surat, Gujarat"
]

UNITS = ["piece", "set", "kg", "meter", "pack"]

def random_price_for_category(cat):
    # returns (price, currency, moq)
    if cat == "Industrial Machinery":
        price = round(random.uniform(50000, 500000), -2)
        moq = random.choice([1, 1, 1, 2, 5])
    elif cat == "Electronics":
        price = round(random.uniform(500, 50000), -1)
        moq = random.choice([1, 5, 10, 50])
    elif cat == "Textiles":
        price = round(random.uniform(50, 5000), -0)
        moq = random.choice([10, 50, 100, 500])
    elif cat == "Chemical Supplies":
        price = round(random.uniform(2000, 200000), -1)
        moq = random.choice([1, 5, 10])
    elif cat == "Packaging":
        price = round(random.uniform(10, 2000), -0)
        moq = random.choice([100, 500, 1000])
    else:
        price = round(random.uniform(1000, 100000), -1)
        moq = random.choice([1, 10, 50])
    return price, "INR", moq

def make_title(cat, brand):
    # simple template-based titles
    if cat == "Industrial Machinery":
        return f"{brand} Hydraulic Press Model {fake.bothify(text='##??')}"
    if cat == "Electronics":
        return f"{brand} Industrial Motor {fake.bothify(text='M-###')}"
    if cat == "Textiles":
        return f"{brand} Cotton Fabric {random.choice(['Plain','Printed','Knitted'])}"
    if cat == "Chemical Supplies":
        return f"{brand} Industrial Solvent {fake.bothify(text='S-###')}"
    if cat == "Packaging":
        return f"{brand} Corrugated Box {random.choice(['Single Wall','Double Wall'])}"
    return f"{brand} Product {fake.bothify(text='P-###')}"

def generate_row(i):
    category = random.choice(CATEGORIES)
    brand = random.choice(BRANDS)
    title = make_title(category, brand)
    price, currency, moq = random_price_for_category(category)
    unit = random.choice(UNITS)
    supplier = f"{brand} ({fake.company_suffix()})"
    location = random.choice(LOCATIONS)
    rating = round(random.uniform(3.2, 5.0), 1)
    reviews = random.randint(0, 120)
    lead_time_days = random.choice([1,3,7,14,30])
    product_url = f"https://example.com/{category.replace(' ','-').lower()}/{i}"
    listed_at = (datetime.utcnow() - timedelta(days=random.randint(0,365))).isoformat()
    description = fake.sentence(nb_words=12)
    return {
        "id": f"P{i:06d}",
        "category": category,
        "title": title,
        "brand": brand,
        "price_raw": f"INR {price:,} per {unit}",
        "price_numeric": price,
        "currency": currency,
        "unit": unit,
        "moq": moq,
        "supplier_name": supplier,
        "location": location,
        "rating": rating,
        "num_reviews": reviews,
        "lead_time_days": lead_time_days,
        "product_url": product_url,
        "listed_at": listed_at,
        "description": description
    }

def main(num_rows=5000):
    rows = []
    for i in range(1, num_rows+1):
        rows.append(generate_row(i))
        if i % 500 == 0:
            print("Generated", i, "rows")
    df = pd.DataFrame(rows)
    df.to_csv(OUT_PATH, index=False)
    print("Saved synthetic dataset to", OUT_PATH)
    print(df.shape)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--rows", type=int, default=5000, help="Number of synthetic rows to generate")
    args = p.parse_args()
    main(args.rows)
