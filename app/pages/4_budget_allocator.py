"""Page 4 — Budget Allocator: interactive retention-spend optimizer."""
import sys
from pathlib import Path
import streamlit as st
import plotly.express as px

# Make src/ importable
sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.budget_allocator import (compute_expected_value, allocate_budget,
                                   DEFAULT_ASSUMPTIONS)
from utils import segment_summary, fmt_brl, SEGMENT_COLORS, SEGMENT_ORDER

st.set_page_config(page_title="Budget Allocator", page_icon="💰", layout="wide")

st.title("💰 Retention Budget Allocator")
st.caption("Allocate a fixed budget across segments to maximize expected return.")

st.warning(
    "**These parameters are assumptions, not measured facts.** Olist doesn't "
    "provide intervention costs or conversion rates, so this is a decision "
    "framework — adjust the sliders to run your own scenarios. Defaults are "
    "reasoned from each segment's behavior."
)

summary = segment_summary()

# ---- Global budget ----
budget = st.slider("Total retention budget (R$)",
                   min_value=50_000, max_value=2_000_000,
                   value=500_000, step=50_000, format="R$ %d")

# ---- Per-segment assumption sliders ----
st.header("Intervention assumptions per segment")
assumptions = {}
cols = st.columns(4)
for col, seg_name in zip(cols, SEGMENT_ORDER):
    d = DEFAULT_ASSUMPTIONS[seg_name]
    with col:
        st.markdown(f"<div style='border-top:4px solid {SEGMENT_COLORS[seg_name]};"
                    f"padding-top:6px'><b>{seg_name}</b></div>",
                    unsafe_allow_html=True)
        cost = st.number_input("Cost / customer (R$)", 1.0, 100.0,
                               float(d["intervention_cost"]), 1.0,
                               key=f"cost_{seg_name}")
        success = st.slider("Success rate", 0.0, 0.5,
                            float(d["success_rate"]), 0.01,
                            key=f"succ_{seg_name}")
        uplift = st.slider("Value uplift", 0.0, 1.5,
                           float(d["value_uplift"]), 0.1,
                           key=f"uplift_{seg_name}")
        assumptions[seg_name] = {"intervention_cost": cost,
                                 "success_rate": success,
                                 "value_uplift": uplift}

# ---- Compute ----
ev = compute_expected_value(summary, assumptions)
allocation = allocate_budget(ev, budget)

st.divider()
st.header("Results")

# ROI + allocation charts
c1, c2 = st.columns(2)
with c1:
    fig = px.bar(ev, x="roi", y="segment", orientation="h",
                 color="segment", color_discrete_map=SEGMENT_COLORS,
                 title="Expected ROI by segment")
    fig.add_vline(x=0, line_dash="dash", line_color="grey")
    fig.update_layout(showlegend=False, yaxis_title="", xaxis_title="ROI (net / cost)")
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = px.bar(allocation, x="allocated_budget", y="segment", orientation="h",
                 color="segment", color_discrete_map=SEGMENT_COLORS,
                 title="Recommended budget allocation")
    fig.update_layout(showlegend=False, yaxis_title="", xaxis_title="Allocated (R$)")
    st.plotly_chart(fig, use_container_width=True)

# ---- Summary metrics ----
total_allocated = allocation["allocated_budget"].sum()
total_net = (allocation.loc[allocation["allocated_budget"] > 0, "expected_net"]).sum()
unspent = budget - total_allocated

m1, m2, m3 = st.columns(3)
m1.metric("Budget allocated", fmt_brl(total_allocated))
m2.metric("Expected net return", fmt_brl(total_net))
m3.metric("Deliberately unspent", fmt_brl(unspent),
          help="Budget left unallocated because remaining segments have "
               "negative ROI — spending it would lose money.")

if unspent > 0:
    st.success(
        f"**{fmt_brl(unspent)} left unspent on purpose.** Every remaining "
        "segment has negative expected ROI under these assumptions, so "
        "allocating more would destroy value. Not spending is the optimal move."
    )

# ---- Detail table ----
st.subheader("Full breakdown")
show = allocation[["segment", "n_customers", "avg_value", "roi",
                   "expected_net", "allocated_budget"]].copy()
show["avg_value"] = show["avg_value"].map(fmt_brl)
show["expected_net"] = show["expected_net"].map(fmt_brl)
show["allocated_budget"] = show["allocated_budget"].map(fmt_brl)
show["roi"] = show["roi"].map(lambda x: f"{x:.2f}")
st.dataframe(show, use_container_width=True, hide_index=True)