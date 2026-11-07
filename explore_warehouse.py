"""Run example SQL queries against the warehouse database."""
from pathlib import Path
import sqlite3

import pandas as pd

DB_PATH = Path(__file__).resolve().parent / "smart_warehouse.db"


def run_query(connection, title: str, query: str) -> None:
    print(f"\n--- {title} ---")
    print(pd.read_sql_query(query, connection).to_string(index=False))


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError("Run load_warehouse.py before explore_warehouse.py.")
    with sqlite3.connect(DB_PATH) as connection:
        run_query(connection, "Total records", "SELECT COUNT(*) AS total FROM products")
        run_query(
            connection, "Records by source",
            "SELECT source, COUNT(*) AS records FROM products GROUP BY source"
        )
        run_query(
            connection, "Average price by category",
            """SELECT category, ROUND(AVG(price_inr), 2) AS average_price_inr
               FROM products GROUP BY category ORDER BY average_price_inr DESC"""
        )
        run_query(
            connection, "Five highest-priced products",
            """SELECT product_name, category, ROUND(price_inr, 2) AS price_inr, source
               FROM products ORDER BY price_inr DESC LIMIT 5"""
        )
        run_query(
            connection, "Sample sales summary",
            """SELECT SUM(sales_quantity) AS units_sold,
                      ROUND(SUM(revenue_inr), 2) AS revenue_inr
               FROM products WHERE source = 'sales_csv'"""
        )


if __name__ == "__main__":
    main()
