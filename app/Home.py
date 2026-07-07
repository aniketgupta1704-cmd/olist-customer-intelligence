"""Olist Customer Intelligence Platform — landing page."""
import streamlit as st
from utils import (load_segments, segment_summary, fmt_brl,
                   SEGMENT_COLORS, SEGMENT_ORDER)

st.set_page_config(
    page_title="Olist Customer Intelligence",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Olist Customer Intelligence Platform")
st.markdown(
    "End-to-end customer analytics on **96k+ Brazilian e-commerce orders** — "
    "segmentation, cohort retention, predictive modeling, causal inference, "
    "and a retention budget allocator."
)

seg = load_segments()
summary = segment_summary()

# Headline metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers analyzed", f"{len(seg):,}")
c2.metric("Segments identified", f"{seg['segment'].nunique()}")
repeat_share = (seg["segment"] == "Repeat Buyers").mean()
c3.metric("Repeat-buyer share", f"{repeat_share:.1%}")
c4.metric("Total customer value", fmt_brl(seg["monetary"].sum()))

st.divider()

# The narrative — this is what makes it readable to a non-technical PM
st.subheader("The story in three findings")
st.markdown(
    """
    1. **Retention barely exists.** ~96% of customers order exactly once;
       cohort retention drops to near-zero after the first month. Olist's
       challenge isn't churn — it's that customers don't come back.

    2. **Loyalty can't be predicted at acquisition.** A classifier on
       first-order features predicts *spend* well but predicts *repeat
       behavior* essentially not at all — meaning future-loyal customers
       can't be flagged from their first purchase.

    3. **Delivery speed causally drives satisfaction.** Propensity score
       matching shows faster-than-promised delivery raises review scores.
       Retention can't be predicted — but satisfaction *can* be influenced.
    """
)

st.divider()
st.subheader("The four customer segments")

cols = st.columns(4)
descriptions = {
    "Repeat Buyers": "The ~3% who returned. Highest value per BRL — protect them.",
    "High-Value One-Timers": "Big single purchases. The conversion prize.",
    "Low-Value Recent": "Fresh but low-spend. Nurture candidates.",
    "Dormant Low-Value": "Stale and cheap. Lowest intervention ROI.",
}
for col, seg_name in zip(cols, SEGMENT_ORDER):
    row = summary[summary["segment"] == seg_name].iloc[0]
    with col:
        st.markdown(f"### {seg_name}")
        st.markdown(f"<div style='height:4px;background:{SEGMENT_COLORS[seg_name]};"
                    f"border-radius:2px;margin-bottom:8px'></div>",
                    unsafe_allow_html=True)
        st.metric("Customers", f"{int(row['n_customers']):,}")
        st.metric("Avg value", fmt_brl(row["avg_value"]))
        st.caption(descriptions[seg_name])

st.divider()
st.caption(
    "Navigate using the sidebar → Executive Summary · Segments Explorer · "
    "Cohort Analysis · Budget Allocator"
)