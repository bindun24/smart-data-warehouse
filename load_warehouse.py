"""Load the unified CSV dataset into a local SQLite database."""
from pathlib import Path
import sqlite3

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "unified_products.csv"
DB_PATH = BASE_DIR / "smart_warehouse.db"


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError("Run transform_data.py before load_warehouse.py.")
    df = pd.read_csv(CSV_PATH)
    with sqlite3.connect(DB_PATH) as connection:
        df.to_sql("products", connection, if_exists="replace", index=False)
        count = pd.read_sql_query(
            "SELECT COUNT(*) AS total_records FROM products", connection
        ).iloc[0, 0]
    print(f"Database created/updated: {DB_PATH}")
    print(f"Records loaded: {count}")


if __name__ == "__main__":
    main()
