"""Page 1 — Executive Summary: the findings and recommendation in plain terms."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.pdf_report import build_executive_pdf
import streamlit as st
from utils import (load_segments, segment_summary, load_propensity,
                   fmt_brl, SEGMENT_COLORS)

st.set_page_config(page_title="Executive Summary", page_icon="📄", layout="wide")

st.title("📄 Executive Summary")
seg = load_segments()
summary = segment_summary()

pdf_bytes = build_executive_pdf(
    seg_summary=summary,
    n_customers=len(seg),
    repeat_share=(seg["segment"] == "Repeat Buyers").mean(),
    total_value=seg["monetary"].sum(),
)
st.download_button(
    "⬇ Download executive summary (PDF)",
    data=pdf_bytes,
    file_name="olist_executive_summary.pdf",
    mime="application/pdf",
)
st.caption("For business stakeholders — the findings, what they mean, and what to do.")

seg = load_segments()
summary = segment_summary()

# ---- The situation ----
st.header("The situation")
st.markdown(
    f"""
    We analyzed **{len(seg):,} customers** across **96,478 delivered orders**
    on Olist's Brazilian e-commerce marketplace (Sep 2016 – Aug 2018).
    The defining fact of this customer base: **the overwhelming majority buy
    once and never return.** Only **{(seg['segment']=='Repeat Buyers').mean():.1%}**
    are repeat buyers.
    """
)

# ---- Three findings ----
# ---- Three findings ----
st.header("Three findings")

f1, f2, f3 = st.columns(3)

with f1:
    with st.container(border=True):
        st.markdown(
            "<div style='font-size:2.6rem;font-weight:700;color:#1565C0;"
            "line-height:1.1'>97%</div>"
            "<div style='font-weight:600;margin-bottom:6px'>"
            "Customers purchase exactly once</div>",
            unsafe_allow_html=True)
        st.caption(
            "Retention collapses to near-zero after month 0. The strategic "
            "question is converting one-time buyers — not retaining an active "
            "base that doesn't exist.")

with f2:
    with st.container(border=True):
        st.markdown(
            "<div style='font-size:2.6rem;font-weight:700;color:#1565C0;"
            "line-height:1.1'>~1%</div>"
            "<div style='font-weight:600;margin-bottom:6px'>"
            "Month-1 retention</div>",
            unsafe_allow_html=True)
        st.caption(
            "A first-order classifier predicts spend well (AUC 0.97) but "
            "predicts repeat behavior essentially not at all. Future loyalty "
            "can't be flagged at acquisition — it must be built.")

with f3:
    with st.container(border=True):
        st.markdown(
            "<div style='font-size:2.6rem;font-weight:700;color:#2E7D32;"
            "line-height:1.1'>+1.73</div>"
            "<div style='font-weight:600;margin-bottom:6px'>"
            "Review points from early delivery</div>",
            unsafe_allow_html=True)
        st.caption(
            "Propensity score matching shows faster-than-promised delivery "
            "raises review scores (upper-bound estimate). Satisfaction is a "
            "lever the business controls, even when loyalty isn't predictable.")

# ---- The recommendation ----
st.header("Recommendation")
st.markdown(
    """
    Because loyalty can't be predicted but satisfaction can be influenced, the
    strategy is to **allocate retention spend by segment ROI, and invest in the
    operational lever (delivery) that provably moves customer experience:**
    """
)

rec_cols = st.columns(4)
recs = {
    "Repeat Buyers": "Protect. Highest ROI per BRL — cheapest to retain, already loyal.",
    "High-Value One-Timers": "Convert. Largest pool of value; the prime target for a second purchase.",
    "Low-Value Recent": "Nurture selectively — only where intervention ROI is positive.",
    "Dormant Low-Value": "Do not spend. Intervention loses money here.",
}
for col, (seg_name, rec) in zip(rec_cols, recs.items()):
    with col:
        st.markdown(f"<div style='border-top:4px solid {SEGMENT_COLORS[seg_name]};"
                    f"padding-top:6px'><b>{seg_name}</b></div>",
                    unsafe_allow_html=True)
        st.caption(rec)

st.divider()
st.caption(
    "Method note: segmentation via K-Means on RFM features; prediction via "
    "random forest on first-order features; causal estimate via propensity "
    "score matching. See the repository notebooks and docs/limitations.md for "
    "full methodology and caveats."
)