"""Clean and combine scraped, API, and sample sales data into one dataset."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# Demonstration conversion rates only; replace with sourced rates for real use.
GBP_TO_INR = 110.0
USD_TO_INR = 83.0


def load_books() -> pd.DataFrame:
    path = DATA_DIR / "books_raw.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run collect_data.py first.")
    df = pd.read_csv(path)
    return pd.DataFrame({
        "product_name": df["title"],
        "category": "books",
        "price_original": pd.to_numeric(df["price_gbp"], errors="coerce"),
        "currency": "GBP",
        "price_inr": pd.to_numeric(df["price_gbp"], errors="coerce") * GBP_TO_INR,
        "rating": pd.to_numeric(df.get("rating"), errors="coerce"),
        "stock_quantity": pd.NA,
        "availability": df["availability"].fillna("Unknown"),
        "sales_quantity": 0,
        "revenue_inr": 0.0,
        "source": "web_scraping",
    })


def load_api_products() -> pd.DataFrame:
    path = DATA_DIR / "products_api_raw.json"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run collect_data.py first.")
    with path.open(encoding="utf-8") as f:
        products = json.load(f)
    df = pd.DataFrame(products)
    return pd.DataFrame({
        "product_name": df["title"],
        "category": df["category"].astype(str).str.strip().str.lower(),
        "price_original": pd.to_numeric(df["price"], errors="coerce"),
        "currency": "USD",
        "price_inr": pd.to_numeric(df["price"], errors="coerce") * USD_TO_INR,
        "rating": pd.to_numeric(df.get("rating"), errors="coerce"),
        "stock_quantity": pd.to_numeric(df.get("stock"), errors="coerce"),
        "availability": pd.to_numeric(df.get("stock"), errors="coerce").apply(
            lambda n: "In stock" if pd.notna(n) and n > 0 else "Out of stock"
        ),
        "sales_quantity": 0,
        "revenue_inr": 0.0,
        "source": "json_api",
    })


def load_sales() -> pd.DataFrame:
    path = DATA_DIR / "sales_sample.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing from the project data folder.")
    df = pd.read_csv(path)
    quantity = pd.to_numeric(df["sales_quantity"], errors="coerce").fillna(0)
    price = pd.to_numeric(df["price_inr"], errors="coerce").fillna(0)
    return pd.DataFrame({
        "product_name": df["product_name"],
        "category": df["category"].astype(str).str.strip().str.lower(),
        "price_original": price,
        "currency": "INR",
        "price_inr": price,
        "rating": pd.NA,
        "stock_quantity": pd.NA,
        "availability": "Sample sales record",
        "sales_quantity": quantity,
        "revenue_inr": quantity * price,
        "source": "sales_csv",
    })


def main() -> None:
    frames = [load_books(), load_api_products(), load_sales()]
    unified = pd.concat(frames, ignore_index=True)
    unified["product_name"] = unified["product_name"].astype(str).str.strip()
    unified["category"] = unified["category"].astype(str).str.strip().str.lower()
    unified["price_inr"] = pd.to_numeric(unified["price_inr"], errors="coerce")
    unified = unified.dropna(subset=["product_name"])
    unified = unified.sort_values(["source", "category", "product_name"])
    output = DATA_DIR / "unified_products.csv"
    unified.to_csv(output, index=False, encoding="utf-8")
    print(f"Total unified records: {len(unified)}")
    print("\nRecords by source:")
    print(unified["source"].value_counts().to_string())
    print(f"\nSaved unified dataset to {output}")


if __name__ == "__main__":
    main()
