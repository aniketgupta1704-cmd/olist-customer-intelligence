"""Shared data loaders and helpers for the Olist dashboard.
All data access is cached so pages stay fast and DRY.
"""
from pathlib import Path
import pandas as pd
import streamlit as st

# Project root = one level above app/
ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"

# Segment display order + colors, reused across pages for consistency
SEGMENT_ORDER = ["Repeat Buyers", "High-Value One-Timers",
                 "Low-Value Recent", "Dormant Low-Value"]
SEGMENT_COLORS = {
    "Repeat Buyers": "#2E7D32",         # green — most valuable
    "High-Value One-Timers": "#1565C0",  # blue — conversion target
    "Low-Value Recent": "#F9A825",       # amber — nurture
    "Dormant Low-Value": "#9E9E9E",      # grey — write-off
}


@st.cache_data
def load_segments() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "customer_segments.csv")


@st.cache_data
def load_features() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "customer_features.csv")


@st.cache_data
def load_cohort_matrix() -> pd.DataFrame:
    # First column is the cohort_month index
    return pd.read_csv(PROCESSED / "cohort_matrix.csv", index_col=0)


@st.cache_data
def load_propensity() -> pd.DataFrame:
    return pd.read_csv(PROCESSED / "propensity_scores.csv")


@st.cache_data
def segment_summary() -> pd.DataFrame:
    """Per-segment size + avg value, ordered. Drives allocator + overview."""
    seg = load_segments()
    summary = (seg.groupby("segment")
               .agg(n_customers=("customer_unique_id", "count"),
                    avg_value=("monetary", "mean"),
                    avg_recency=("recency_days", "mean"),
                    avg_frequency=("frequency", "mean"))
               .reindex(SEGMENT_ORDER)
               .reset_index())
    return summary


def fmt_brl(x: float) -> str:
    """Format a number as Brazilian Real."""
    return f"R$ {x:,.0f}"