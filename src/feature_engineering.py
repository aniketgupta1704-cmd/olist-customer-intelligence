"""RFM, cohort, and CLV feature engineering for Olist."""
from pathlib import Path
import pandas as pd
from src.data_loader import run_query

SNAPSHOT_DATE = "2018-08-29"


def build_rfm(snapshot_date: str = SNAPSHOT_DATE) -> pd.DataFrame:
    sql = f"""
        WITH delivered AS (
            SELECT c.customer_unique_id, o.order_id,
                   o.order_purchase_timestamp,
                   SUM(oi.price + oi.freight_value) AS order_value
            FROM orders o
            JOIN customers c         ON o.customer_id = c.customer_id
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY 1, 2, 3
        )
        SELECT customer_unique_id,
               DATE_DIFF('day', MAX(order_purchase_timestamp), DATE '{snapshot_date}') AS recency_days,
               COUNT(DISTINCT order_id) AS frequency,
               SUM(order_value)         AS monetary,
               AVG(order_value)         AS avg_order_value,
               MIN(order_purchase_timestamp) AS first_purchase,
               MAX(order_purchase_timestamp) AS last_purchase
        FROM delivered GROUP BY customer_unique_id
    """
    return run_query(sql)


def add_rfm_scores(rfm: pd.DataFrame) -> pd.DataFrame:
    rfm = rfm.copy()
    rfm["R_score"] = pd.qcut(rfm["recency_days"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["M_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5,
                             labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]
    return rfm


def build_cohort_retention() -> pd.DataFrame:
    sql = Path("sql/03_cohort_retention.sql").read_text()
    long = run_query(sql)
    counts = long.pivot(index="cohort_month", columns="month_offset",
                        values="active_customers")
    return counts.divide(counts[0], axis=0) * 100
