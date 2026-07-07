"""Page 2 — Segments Explorer: interactive per-segment profiles."""
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import (load_segments, segment_summary, fmt_brl,
                   SEGMENT_COLORS, SEGMENT_ORDER)

st.set_page_config(page_title="Segments Explorer", page_icon="🔍", layout="wide")

st.title("🔍 Segments Explorer")
st.caption("Explore each customer segment's size, value, and behavior.")

seg = load_segments()
summary = segment_summary()

SEGMENT_ACTIONS = {
    "Repeat Buyers": ("VIP Rewards",
                      "Protect your loyal base with exclusive perks — highest ROI per BRL."),
    "High-Value One-Timers": ("Conversion Campaign",
                              "Targeted push for a second purchase — the largest pool of value."),
    "Low-Value Recent": ("Personalized Recommendations",
                         "Nurture with relevant products while they're still fresh."),
    "Dormant Low-Value": ("Do Not Target",
                          "Intervention loses money here — deliberately exclude from spend."),
}

# ---- Overview: size + value bars ----
st.header("Segment overview")
c1, c2 = st.columns(2)

with c1:
    fig = px.bar(summary, x="segment", y="n_customers",
                 color="segment", color_discrete_map=SEGMENT_COLORS,
                 category_orders={"segment": SEGMENT_ORDER},
                 title="Customers per segment")
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Customers")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    fig = px.bar(summary, x="segment", y="avg_value",
                 color="segment", color_discrete_map=SEGMENT_COLORS,
                 category_orders={"segment": SEGMENT_ORDER},
                 title="Average customer value (BRL)")
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Avg value R$")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ---- 3-D cluster structure ----
st.header("Segment structure in 3-D")
st.caption(
    "A sample of customers plotted on the transformed features used for "
    "clustering. Rotate to explore. Use the toggle to isolate one segment.")

ctrl1, ctrl2 = st.columns([2, 1])
with ctrl1:
    highlight = st.selectbox(
        "Highlight a segment (others fade)",
        ["Show all"] + SEGMENT_ORDER, key="scatter_highlight")
with ctrl2:
    sample_n = st.select_slider("Sample size", options=[3000, 5000, 8000, 10000],
                                value=8000, key="scatter_n")

plot_df = seg.sample(n=min(sample_n, len(seg)), random_state=42).copy()
plot_df["log_monetary"] = np.log1p(plot_df["monetary"])

if highlight == "Show all":
    op_map = {s: 0.22 for s in SEGMENT_ORDER}
else:
    op_map = {s: (0.85 if s == highlight else 0.04) for s in SEGMENT_ORDER}

fig3d = go.Figure()
for seg_name in SEGMENT_ORDER:
    d = plot_df[plot_df["segment"] == seg_name]
    if d.empty:
        continue
    fig3d.add_trace(go.Scatter3d(
        x=d["recency_days"], y=d["log_monetary"], z=d["frequency"],
        mode="markers", name=seg_name,
        marker=dict(size=3, color=SEGMENT_COLORS[seg_name],
                    opacity=op_map[seg_name]),
        hovertemplate=(f"<b>{seg_name}</b><br>Recency %{{x:.0f}}d<br>"
                       "log Monetary %{y:.2f}<br>Frequency %{z}<extra></extra>"),
    ))

fig3d.update_layout(
    height=700,
    scene=dict(
        xaxis_title="Recency (days)",
        yaxis_title="log Monetary",
        zaxis_title="Frequency (orders)",
        aspectmode="cube",
    ),
    legend=dict(itemsizing="constant", orientation="h",
                yanchor="bottom", y=1.02, xanchor="center", x=0.5),
    margin=dict(l=0, r=0, t=30, b=0),
)
st.plotly_chart(fig3d, use_container_width=True)

st.caption(
    "Axes: recency, log monetary, and frequency. Repeat Buyers (frequency ≥ 2) "
    "visibly separate from the single-purchase plane below — that lift-off is "
    "the ~3% who returned. Monetary and average order value are near-identical "
    "for one-time buyers, so frequency is the more informative third axis. "
    "Silhouette 0.356 / Davies-Bouldin 0.85 measure separation in the full "
    "4-feature space.")

st.divider()

# ---- Drill into one segment ----
st.header("Segment deep-dive")
chosen = st.selectbox("Choose a segment", SEGMENT_ORDER)
sub = seg[seg["segment"] == chosen]
row = summary[summary["segment"] == chosen].iloc[0]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Customers", f"{int(row['n_customers']):,}")
m2.metric("Avg value", fmt_brl(row["avg_value"]))
m3.metric("Avg recency (days)", f"{row['avg_recency']:.0f}")
m4.metric("Avg frequency", f"{row['avg_frequency']:.2f}")

action, rationale = SEGMENT_ACTIONS[chosen]
st.markdown(
    f"<div style='border-left:5px solid {SEGMENT_COLORS[chosen]};"
    f"background:rgba(255,255,255,0.03);padding:12px 16px;"
    f"border-radius:4px;margin:12px 0'>"
    f"<div style='font-size:0.8rem;color:#888;text-transform:uppercase;"
    f"letter-spacing:0.05em'>Recommended action</div>"
    f"<div style='font-size:1.4rem;font-weight:700;margin:2px 0'>"
    f"{chosen} → {action}</div>"
    f"<div style='color:#aaa'>{rationale}</div></div>",
    unsafe_allow_html=True)

# Distribution charts for the chosen segment
d1, d2 = st.columns(2)
with d1:
    fig = px.histogram(sub, x="monetary", nbins=50,
                       title=f"{chosen} — spend distribution",
                       color_discrete_sequence=[SEGMENT_COLORS[chosen]])
    fig.update_layout(xaxis_title="Monetary (R$)", yaxis_title="Customers")
    # clip x-axis to 99th pct so outliers don't flatten the view
    fig.update_xaxes(range=[0, sub["monetary"].quantile(0.99)])
    st.plotly_chart(fig, use_container_width=True)

with d2:
    fig = px.histogram(sub, x="recency_days", nbins=50,
                       title=f"{chosen} — recency distribution",
                       color_discrete_sequence=[SEGMENT_COLORS[chosen]])
    fig.update_layout(xaxis_title="Days since last order", yaxis_title="Customers")
    st.plotly_chart(fig, use_container_width=True)

# ---- Geographic + category profile (descriptive only) ----
st.subheader("Who's in this segment?")
st.caption(
    "Region and category are descriptive only — they were tested as clustering "
    "inputs and found non-discriminative, so segments are defined by value and "
    "recency, not geography or product taste."
)
g1, g2 = st.columns(2)
with g1:
    region_counts = sub["region"].value_counts().reset_index()
    region_counts.columns = ["region", "count"]
    fig = px.bar(region_counts, x="region", y="count", title="By region")
    st.plotly_chart(fig, use_container_width=True)
with g2:
    cat_counts = sub["category_grouped"].value_counts().head(8).reset_index()
    cat_counts.columns = ["category", "count"]
    fig = px.bar(cat_counts, x="category", y="count", title="Top categories")
    st.plotly_chart(fig, use_container_width=True)