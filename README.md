# Smart Data Warehouse

A beginner-friendly Python ETL project that collects product data from multiple sources, transforms it into a common format, stores it in SQLite, and displays it in a Streamlit dashboard.

## Project structure

```text
smart_data_warehouse/
├── data/
│   └── sales_sample.csv
├── collect_data.py
├── transform_data.py
├── load_warehouse.py
├── explore_warehouse.py
├── dashboard.py
├── requirements.txt
├── .gitignore
└── README.md
```

Generated files (raw CSV/JSON, unified CSV, and `smart_warehouse.db`) are created when you run the scripts.

## Requirements

- Windows 10/11
- Python 3.12 (64-bit) recommended
- VS Code (recommended)
- Internet connection for the scraping and API collection steps

> If your current Python installation is Python 3.15 and Pandas fails to import, install Python 3.12 and create a fresh virtual environment with it. Do not delete your project or data files.

## Setup in VS Code / PowerShell

Open the project folder in VS Code. Open **Terminal → New Terminal**, then run these commands one by one:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use this command for the current terminal session only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

If your computer does not have Python 3.12, install it from the official Python website, then reopen VS Code. Do not work around organization security controls; ask the administrator if an application-control policy blocks Python files.

## Run the project in order

Keep the `.venv` environment activated. Run each command from the project folder:

```powershell
python collect_data.py
python transform_data.py
python load_warehouse.py
python explore_warehouse.py
python -m streamlit run dashboard.py
```

Streamlit will print a local URL, usually `http://localhost:8501`. Open it in your browser.

## What each file does

1. `collect_data.py` scrapes book listings from Books to Scrape and downloads product records from DummyJSON.
2. `transform_data.py` cleans the source fields and combines the data into `data/unified_products.csv`.
3. `load_warehouse.py` loads the unified dataset into the SQLite database `smart_warehouse.db`, in a table named `products`.
4. `explore_warehouse.py` runs example SQL queries against the database.
5. `dashboard.py` provides filters, summary metrics, charts, a data table, and CSV download.

## Data and academic notes

- The book website and DummyJSON are public demonstration sources intended for practice. Be respectful of their usage policies.
- The sample sales file is fabricated demonstration data, not actual company sales.
- The GBP-to-INR rate (110) and USD-to-INR rate (83) are fixed illustrative conversion rates in `transform_data.py`, not live exchange rates.
- The project performs ETL and SQL analytics. It does not currently use machine learning.
- Results may change when the public sources update or return different records.

## Troubleshooting

**`ModuleNotFoundError`**: Activate `.venv`, then run `python -m pip install -r requirements.txt`.

**Pandas DLL / application-control error**: Check `python --version` and `python -c "import pandas; print(pandas.__version__)"`. This project recommends Python 3.12 in a clean `.venv`. If a Windows security policy blocks a DLL, contact your administrator rather than disabling the policy.

**Dashboard says database missing**: Run the collection, transformation, and loading commands in order.

**Network / scraping error**: Check your internet connection and try `python collect_data.py` again later. Public websites can change their page structure.

**Port 8501 is busy**: Run `python -m streamlit run dashboard.py --server.port 8502`.

## Refreshing the warehouse

Whenever you want fresh source data, run the full pipeline again:

```powershell
python collect_data.py
python transform_data.py
python load_warehouse.py
```
