"""Interactive Streamlit dashboard for the Smart Data Warehouse."""
from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "smart_warehouse.db"

st.set_page_config(
    page_title="Smart Data Warehouse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    with sqlite3.connect(DB_PATH) as connection:
        return pd.read_sql_query("SELECT * FROM products", connection)


st.title("📊 Smart Data Warehouse")
st.caption("An ETL project combining web-scraped, API, and sample CSV data.")

df = load_data()
if df.empty:
    st.warning("The warehouse database is empty or missing.")
    st.code(
        "python collect_data.py\n"
        "python transform_data.py\n"
        "python load_warehouse.py\n"
        "python -m streamlit run dashboard.py",
        language="powershell",
    )
    st.stop()

df["price_inr"] = pd.to_numeric(df["price_inr"], errors="coerce")
df["sales_quantity"] = pd.to_numeric(df["sales_quantity"], errors="coerce").fillna(0)
df["revenue_inr"] = pd.to_numeric(df["revenue_inr"], errors="coerce").fillna(0)

st.sidebar.header("Filters")
categories = sorted(df["category"].dropna().unique().tolist())
sources = sorted(df["source"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Select category", categories, default=categories
)
selected_sources = st.sidebar.multiselect(
    "Select data source", sources, default=sources
)

filtered_df = df[
    df["category"].isin(selected_categories) & df["source"].isin(selected_sources)
].copy()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total records", f"{len(filtered_df):,}")
col2.metric("Categories", f"{filtered_df['category'].nunique():,}")
col3.metric("Average price", f"₹{filtered_df['price_inr'].mean():,.2f}" if not filtered_df.empty else "—")
col4.metric("Sample sales revenue", f"₹{filtered_df.loc[filtered_df['source'] == 'sales_csv', 'revenue_inr'].sum():,.2f}")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Records by data source")
    source_counts = filtered_df["source"].value_counts().rename_axis("source").reset_index(name="records")
    if not source_counts.empty:
        st.plotly_chart(
            px.pie(source_counts, names="source", values="records",
                   title="Data source distribution", hole=0.35),
            use_container_width=True,
        )

with right:
    st.subheader("Average price by category")
    category_prices = (
        filtered_df.groupby("category", as_index=False)["price_inr"]
        .mean().sort_values("price_inr", ascending=True)
    )
    if not category_prices.empty:
        st.plotly_chart(
            px.bar(category_prices, x="price_inr", y="category",
                   orientation="h", title="Average price (INR)",
                   labels={"price_inr": "Average price (₹)", "category": "Category"},
                   template="plotly_white"),
            use_container_width=True,
        )

st.divider()
st.subheader("🏆 Top 5 Most Expensive Products")
top_df = filtered_df.dropna(subset=["price_inr"]).nlargest(5, "price_inr")
if not top_df.empty:
    fig_top = px.bar(
        top_df.sort_values("price_inr", ascending=True),
        x="price_inr", y="product_name", orientation="h",
        title="Top 5 Most Expensive Products",
        labels={"price_inr": "Price (₹)", "product_name": "Product"},
        text="price_inr", template="plotly_white",
    )
    fig_top.update_traces(texttemplate="₹%{x:,.0f}", textposition="outside", cliponaxis=False)
    fig_top.update_layout(showlegend=False, height=450, margin=dict(l=15, r=90, t=60, b=30))
    st.plotly_chart(fig_top, use_container_width=True)

st.divider()
st.subheader("🗂️ Warehouse Records")
st.write(f"Showing **{len(filtered_df):,}** records matching your filters.")
st.dataframe(filtered_df, use_container_width=True, hide_index=True)
st.download_button(
    "⬇️ Download filtered records as CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_warehouse_records.csv",
    mime="text/csv",
)
