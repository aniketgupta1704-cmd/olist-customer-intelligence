"""Page 5 — Model Performance: the metrics behind every layer of the project."""
import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import SEGMENT_COLORS

st.set_page_config(page_title="Model Performance", page_icon="📈", layout="wide")

st.title("📈 Model Performance")
st.caption("The metrics behind each layer — segmentation, prediction, and causal inference.")

METRICS_PATH = Path(__file__).resolve().parents[1].parent / "data" / "processed" / "model_metrics.json"
with open(METRICS_PATH) as f:
    M = json.load(f)

# ============================================================
# SEGMENTATION
# ============================================================
st.header("1 · Segmentation")
seg = M["segmentation"]

c1, c2, c3 = st.columns(3)
c1.metric("Silhouette score", f"{seg['silhouette']:.3f}",
          help="Higher is better (max 1.0). Measures cluster separation.")
c2.metric("Davies-Bouldin index", f"{seg['davies_bouldin']:.3f}",
          help="Lower is better. Under 1.0 indicates well-separated clusters.")
c3.metric("Clusters (k)", seg["n_clusters"])

st.markdown(f"**Algorithm choice.** {seg['algo_note']}")
st.markdown(f"**Choosing k.** {seg['chosen_k_note']}")
st.info(
    "Two independent metrics agree the segments are well-formed: silhouette "
    f"{seg['silhouette']:.3f} (separation) and Davies-Bouldin "
    f"{seg['davies_bouldin']:.3f} (compactness vs. separation, under 1.0).")

st.divider()

# ============================================================
# PREDICTION
# ============================================================
st.header("2 · Repeat-Purchase Prediction")
pred = M["prediction"]
b = pred["binary"]
mc = pred["multiclass"]

st.caption(pred["model"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Binary ROC-AUC", f"{b['roc_auc']:.3f}")
c2.metric("Precision (high-value)", f"{b['precision_high_value']:.2f}")
c3.metric("Recall (high-value)", f"{b['recall_high_value']:.2f}")
c4.metric("Multi-class accuracy", f"{mc['accuracy']:.2f}")

col_left, col_right = st.columns(2)

# Confusion matrix
with col_left:
    st.subheader("Confusion matrix (binary)")
    cm = b["confusion_matrix"]
    labels = b["cm_labels"]
    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=[f"Pred: {l}" for l in labels],
        y=[f"True: {l}" for l in labels],
        text=cm, texttemplate="%{text:,}",
        colorscale="Blues", showscale=False,
    ))
    fig.update_layout(height=340, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption(b["cm_note"])

# Per-class bars — the story lives here
with col_right:
    st.subheader("Per-class recall (multi-class)")
    per = mc["per_class"]
    rows = [{"segment": k, "recall": v["recall"]} for k, v in per.items()]
    dfp = pd.DataFrame(rows)
    fig = px.bar(dfp, x="recall", y="segment", orientation="h",
                 color="segment", color_discrete_map=SEGMENT_COLORS,
                 range_x=[0, 1])
    fig.update_layout(showlegend=False, height=340, yaxis_title="",
                      xaxis_title="Recall", margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Repeat Buyers recall ≈ 1% — the model essentially cannot "
               "identify future repeat buyers.")

st.warning(f"**Key finding →** {pred['key_finding']}")

st.divider()

# ============================================================
# CAUSAL
# ============================================================
st.header("3 · Causal Inference (Propensity Score Matching)")
ca = M["causal"]

st.markdown(f"**Question.** Does *{ca['treatment'].lower()}* cause a higher "
            f"*{ca['outcome'].lower()}*?")
st.caption(ca["method"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Naive difference", f"+{ca['naive_diff']:.2f}")
c2.metric("Matched ATT", f"+{ca['att']:.2f}",
          help="The causal estimate after matching. Nearly identical to naive → "
               "measured confounders weren't distorting much.")
c3.metric("t-statistic", f"{ca['t_stat']:.0f}")
c4.metric("Treated / Control", f"{ca['n_treated']:,} / {ca['n_control']:,}")

# THE centerpiece: SMD before vs after matching
st.subheader("Covariate balance — before vs. after matching")
st.caption(
    "This is the credibility test for matching. Each confounder's standardized "
    "mean difference (SMD) should drop below 0.1 after matching. The key win: "
    "estimated_days improves from 0.263 to 0.015.")

before = ca["smd_before"]
after = ca["smd_after"]
conf = list(before.keys())
balance_df = pd.DataFrame({
    "confounder": conf * 2,
    "SMD": [abs(before[c]) for c in conf] + [abs(after[c]) for c in conf],
    "stage": ["Before matching"] * len(conf) + ["After matching"] * len(conf),
})
fig = px.bar(balance_df, x="SMD", y="confounder", color="stage",
             orientation="h", barmode="group",
             color_discrete_map={"Before matching": "#C62828",
                                 "After matching": "#2E7D32"})
fig.add_vline(x=0.1, line_dash="dash", line_color="grey",
              annotation_text="0.1 balance threshold")
fig.update_layout(height=380, yaxis_title="", xaxis_title="|SMD| (lower = better balance)")
st.plotly_chart(fig, use_container_width=True)

st.success(
    "All confounders fall below the 0.1 threshold after matching → the matched "
    "comparison is credible.")
st.error(f"**Honest caveat →** {ca['caveat']}")

st.divider()
st.caption(
    "The narrative arc: retention barely exists → loyalty can't be predicted "
    "from the first order (section 2) → so we ask what *causally* moves customer "
    "experience, and find delivery speed does (section 3). Prediction failure "
    "is what motivated the causal layer.")