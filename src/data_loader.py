"""DuckDB analytical layer for Olist e-commerce data."""
from pathlib import Path
import duckdb

RAW_DIR = Path("data/raw")
DB_PATH = Path("data/processed/olist.duckdb")

TABLES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def get_connection(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """Return a connection to the Olist DuckDB database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH), read_only=read_only)


def build_database(overwrite: bool = True) -> None:
    """Load all 9 raw CSVs into DuckDB as native tables."""
    con = get_connection()
    for table, filename in TABLES.items():
        csv_path = RAW_DIR / filename
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing raw CSV: {csv_path}")
        if overwrite:
            con.execute(f"DROP TABLE IF EXISTS {table}")
        con.execute(
            f"CREATE TABLE {table} AS "
            f"SELECT * FROM read_csv_auto('{csv_path}', header=True)"
        )
        n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  loaded {table:24s} {n:>8,} rows")
    con.close()


def run_query(sql: str, read_only: bool = True):
    """Execute a SQL string and return a pandas DataFrame."""
    con = get_connection(read_only=read_only)
    try:
        return con.execute(sql).df()
    finally:
        con.close()
