"""Collect data from a public books website and a products API."""
from __future__ import annotations

import json
import time
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

HEADERS = {"User-Agent": "SmartDataWarehouseStudentProject/1.0"}
TIMEOUT = 20


def scrape_books(max_pages: int = 2) -> pd.DataFrame:
    """Scrape up to max_pages pages from Books to Scrape."""
    records = []
    for page in range(1, max_pages + 1):
        url = (
            "https://books.toscrape.com/catalogue/page-1.html"
            if page == 1
            else f"https://books.toscrape.com/catalogue/page-{page}.html"
        )
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for item in soup.select("article.product_pod"):
            title_tag = item.select_one("h3 a")
            price_tag = item.select_one(".price_color")
            stock_tag = item.select_one(".availability")
            rating_tag = item.select_one("p.star-rating")
            rating = None
            if rating_tag:
                rating_class = next(
                    (c for c in rating_tag.get("class", []) if c != "star-rating"),
                    None,
                )
                rating = {
                    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
                }.get(rating_class)

            if title_tag and price_tag:
                price_text = price_tag.get_text(strip=True).replace("£", "")
                records.append({
                    "title": title_tag.get("title") or title_tag.get_text(strip=True),
                    "price_gbp": float(price_text),
                    "rating": rating,
                    "availability": (
                        "In stock" if stock_tag and "In stock" in stock_tag.get_text()
                        else "Out of stock"
                    ),
                })
        time.sleep(0.3)

    return pd.DataFrame(records)


def fetch_products() -> list[dict]:
    """Fetch product records from DummyJSON."""
    url = "https://dummyjson.com/products?limit=100"
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    payload = response.json()
    return payload.get("products", [])


def main() -> None:
    print("Collecting book data...")
    books = scrape_books(max_pages=2)
    books.to_csv(DATA_DIR / "books_raw.csv", index=False, encoding="utf-8")
    print(f"Saved {len(books)} books to data/books_raw.csv")

    print("Collecting product API data...")
    products = fetch_products()
    with (DATA_DIR / "products_api_raw.json").open("w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    pd.DataFrame(products).to_csv(
        DATA_DIR / "products_api_raw.csv", index=False, encoding="utf-8"
    )
    print(f"Saved {len(products)} API products to data/products_api_raw.json and .csv")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as exc:
        raise SystemExit(
            f"Data collection failed: {exc}\nCheck your internet connection and try again."
        )
