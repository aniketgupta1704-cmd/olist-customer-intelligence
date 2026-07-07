"""Page 6 — Customer Journey: the whole narrative in one flow."""
import streamlit as st
import plotly.graph_objects as go
from utils import load_segments, segment_summary, fmt_brl, SEGMENT_COLORS, SEGMENT_ORDER

st.set_page_config(page_title="Customer Journey", page_icon="🧭", layout="wide")

st.title("🧭 The Customer Journey")
st.caption("From 96k orders to a budget decision — the whole project in one view.")

seg = load_segments()
summary = segment_summary()

n_orders = 96478
n_customers = len(seg)
seg_counts = {s: int(summary.loc[summary["segment"] == s, "n_customers"].iloc[0])
              for s in SEGMENT_ORDER}
one_time = n_customers - seg_counts["Repeat Buyers"]
repeat = seg_counts["Repeat Buyers"]

# ============================================================
# TOP: the funnel of big numbers
# ============================================================
st.header("The narrowing funnel")
f = st.columns(5)
f[0].metric("Delivered orders", f"{n_orders:,}")
f[1].metric("Unique customers", f"{n_customers:,}")
one_time = int((seg["frequency"] == 1).sum())
f[2].metric("Buy exactly once", f"{one_time / n_customers:.1%}",
            help=f"{one_time:,} customers have frequency = 1.")
f[3].metric("Repeat buyers", f"{repeat / n_customers:.1%}",
            help=f"Only {repeat:,} customers returned.")
f[4].metric("Held by repeat + high-value",
            fmt_brl(summary.loc[summary["segment"].isin(
                ["Repeat Buyers", "High-Value One-Timers"]), "avg_value"].mul(
                summary.loc[summary["segment"].isin(
                    ["Repeat Buyers", "High-Value One-Timers"]),
                    "n_customers"]).sum()))

st.divider()

# ============================================================
# MIDDLE: the Sankey flow
# ============================================================
st.header("How value flows through the customer base")

# Node list (index matters for links)
nodes = [
    "Delivered orders",       # 0
    "Unique customers",       # 1
    "Repeat Buyers",          # 2
    "High-Value One-Timers",  # 3
    "Low-Value Recent",       # 4
    "Dormant Low-Value",      # 5
    "Fund (positive ROI)",    # 6
    "Do not fund",            # 7
]
node_colors = [
    "#455A64", "#455A64",
    SEGMENT_COLORS["Repeat Buyers"], SEGMENT_COLORS["High-Value One-Timers"],
    SEGMENT_COLORS["Low-Value Recent"], SEGMENT_COLORS["Dormant Low-Value"],
    "#2E7D32", "#9E9E9E",
]

# Links: orders->customers, customers->each segment, segments->strategy
src = [0,  1, 1, 1, 1,  2, 3, 4, 5]
tgt = [1,  2, 3, 4, 5,  6, 6, 7, 7]
val = [n_orders,
       seg_counts["Repeat Buyers"], seg_counts["High-Value One-Timers"],
       seg_counts["Low-Value Recent"], seg_counts["Dormant Low-Value"],
       seg_counts["Repeat Buyers"], seg_counts["High-Value One-Timers"],
       seg_counts["Low-Value Recent"], seg_counts["Dormant Low-Value"]]

# Link colors: tint by source segment where relevant
link_colors = [
    "rgba(69,90,100,0.3)",
    "rgba(46,125,50,0.4)", "rgba(21,101,192,0.4)",
    "rgba(249,168,37,0.4)", "rgba(158,158,158,0.4)",
    "rgba(46,125,50,0.4)", "rgba(21,101,192,0.4)",
    "rgba(158,158,158,0.4)", "rgba(158,158,158,0.4)",
]

fig = go.Figure(go.Sankey(
    arrangement="snap",
    node=dict(label=nodes, color=node_colors, pad=18, thickness=20,
              line=dict(color="rgba(0,0,0,0)", width=0)),
    link=dict(source=src, target=tgt, value=val, color=link_colors),
))
fig.update_layout(height=460, font_size=13, margin=dict(t=10, b=10))
st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Orders collapse into customers, customers split into four value segments, "
    "and segments flow to a funding decision. The two high-value segments "
    "(Repeat Buyers, High-Value One-Timers) are the only ones worth retention "
    "spend — everything else flows to 'do not fund'.")

st.divider()

st.divider()

# ============================================================
# RETENTION TRIANGLE — why the funnel is so lopsided
# ============================================================
st.header("Why the funnel collapses: retention")
st.caption(
    "The Sankey shows customers splitting into segments — but almost none return "
    "for a second purchase. This heatmap is the evidence. Color scale capped at "
    "5% so near-zero repeat activity is visible; month 0 is 100% by definition.")

from utils import load_cohort_matrix
retention = load_cohort_matrix()
month_cols = sorted(retention.columns, key=lambda c: int(c))

fig_ret = go.Figure(data=go.Heatmap(
    z=retention[month_cols].values,
    x=[f"M{c}" for c in month_cols],
    y=[str(i) for i in retention.index],
    colorscale="Blues", zmin=0, zmax=5,
    colorbar=dict(title="Retention %"),
    hovertemplate="Cohort %{y}<br>Month %{x}<br>Retention %{z:.2f}%<extra></extra>",
))
fig_ret.update_layout(xaxis_title="Months since first purchase",
                      yaxis_title="Acquisition cohort", height=520)
st.plotly_chart(fig_ret, use_container_width=True)

# The one quantified takeaway (condensed from the old cohort page)
if "1" in retention.columns:
    avg_m1 = retention["1"].dropna().mean()
    r1, r2 = st.columns(2)
    r1.metric("Avg month-1 retention", f"{avg_m1:.2f}%")
    r2.metric("Implied one-and-done rate", f"{100 - avg_m1:.1f}%")
st.caption(
    "Black cells are cohort-months with no customers (typically the smallest "
    "early cohorts like Oct 2016) — distinct from near-white near-zero cells.")

# ============================================================
# BOTTOM: the narrative chain in words
# ============================================================
st.header("The reasoning chain")
steps = [
    ("96,478 delivered orders", "The raw activity on the marketplace."),
    ("93,358 unique customers", "Orders map to people — many fewer than orders suggest."),
    ("97% buy exactly once", "Retention barely exists; this reframes the whole problem."),
    ("Loyalty can't be predicted", "First-order features predict spend, not repeat behavior."),
    ("But delivery causally lifts satisfaction", "PSM shows early delivery raises reviews."),
    ("So: allocate budget by segment ROI", "Fund the value segments, invest in delivery, skip the rest."),
]
for i, (head, sub) in enumerate(steps):
    st.markdown(
        f"<div style='display:flex;align-items:baseline;gap:12px;margin:2px 0'>"
        f"<div style='font-size:1.1rem;font-weight:700;color:#1565C0;"
        f"min-width:24px'>{i+1}</div>"
        f"<div><b>{head}</b><br>"
        f"<span style='color:#aaa'>{sub}</span></div></div>",
        unsafe_allow_html=True)
    if i < len(steps) - 1:
        st.markdown("<div style='color:#555;margin-left:4px'>↓</div>",
                    unsafe_allow_html=True)
        
st.divider()
st.header("How it's built")

with st.expander("View the system architecture", expanded=False):
    st.html("""
<style>
.arch-wrap { max-width: 900px; margin: 0 auto; font-family: 'Helvetica', sans-serif; }
.arch-box { border-radius: 10px; padding: 14px 18px; margin: 0 auto; color: white;
    text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.25); }
.arch-box b { font-size: 1.02rem; display: block; margin-bottom: 3px; }
.arch-box span { font-size: 0.8rem; opacity: 0.85; }
.arch-arrow { text-align: center; color: #666; font-size: 1.4rem; line-height: 1.1; margin: 6px 0; }
.arch-cluster { border: 1px solid #37474F; border-radius: 12px; padding: 16px;
    margin-bottom: 4px; background: rgba(69,90,100,0.08); }
.arch-cluster-label { color: #90A4AE; font-size: 0.85rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; text-align:center; }
.arch-row { display: flex; gap: 14px; justify-content: center; }
.arch-row .arch-box { flex: 1; margin: 0; }
.w-data { background: #546E7A; } .w-raw { background: #455A64; }
.w-seg { background: #1565C0; } .w-branch { background: #00838F; }
.w-strat { background: #2E7D32; } .w-app { background: #6A1B9A; }
.arch-note { text-align:center; color:#888; font-size:0.78rem; font-style:italic; margin:6px 0; }
</style>
<div class="arch-wrap">
  <div class="arch-cluster">
    <div class="arch-cluster-label">Data Engineering</div>
    <div class="arch-box w-raw"><b>9 Olist CSVs</b><span>96,478 delivered orders</span></div>
    <div class="arch-arrow">↓</div>
    <div class="arch-box w-data"><b>DuckDB analytical layer</b><span>multi-table SQL · window functions · CTEs</span></div>
    <div class="arch-arrow">↓</div>
    <div class="arch-box w-data"><b>Feature engineering</b><span>RFM · CLV · cohorts · 93,358 customers</span></div>
  </div>
  <div class="arch-arrow">↓</div>
  <div class="arch-box w-seg" style="max-width:420px;"><b>RFM Segmentation</b><span>K-Means k=4 · silhouette 0.356 · Davies-Bouldin 0.85</span></div>
  <div class="arch-arrow">↓ &nbsp;&nbsp; ↓ &nbsp;&nbsp; ↓</div>
  <div class="arch-row">
    <div class="arch-box w-branch"><b>Cohort Analysis</b><span>triangular retention · ~1% month-1</span></div>
    <div class="arch-box w-branch"><b>Repeat-Purchase Prediction</b><span>Random Forest · AUC 0.97 spend / ~1% loyalty</span></div>
    <div class="arch-box w-branch"><b>Propensity Score Matching</b><span>delivery → review · ATT +1.73 (upper bound)</span></div>
  </div>
  <div class="arch-note">loyalty unpredictable → motivates causal inference</div>
  <div class="arch-arrow">↓ &nbsp;&nbsp; ↓ &nbsp;&nbsp; ↓</div>
  <div class="arch-box w-strat" style="max-width:420px;"><b>Business Strategy</b><span>segment ROI · expected value</span></div>
  <div class="arch-arrow">↓</div>
  <div class="arch-box w-strat" style="max-width:420px;"><b>Budget Optimizer</b><span>greedy allocation by ROI · funds positive-ROI segments only</span></div>
  <div class="arch-arrow">↓</div>
  <div class="arch-box w-app" style="max-width:420px;"><b>Streamlit Dashboard</b><span>6 pages · PDF export · reads precomputed artifacts</span></div>
</div>
""")