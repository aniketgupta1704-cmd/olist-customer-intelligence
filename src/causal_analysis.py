"""Propensity score matching for the delivery-speed -> review-score question.

IMPORTANT CAVEAT (see notebook 05): the estimated effect is an UPPER BOUND.
Review scores partly reflect delivery timing directly (a late review is often a
complaint about lateness), so treatment and outcome are coupled in a way PSM
cannot fully correct. Report direction with confidence, magnitude with caution.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.neighbors import NearestNeighbors
from scipy import stats

CONFOUNDERS_NUM = ["n_items", "items_value", "freight_value",
                   "estimated_days", "order_month"]
CONFOUNDERS_CAT = ["customer_state", "category_en"]


def estimate_propensity(df: pd.DataFrame) -> pd.Series:
    prep = ColumnTransformer([
        ("num", StandardScaler(), CONFOUNDERS_NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
         CONFOUNDERS_CAT),
    ])
    model = Pipeline([("prep", prep),
                      ("clf", LogisticRegression(max_iter=1000))])
    model.fit(df[CONFOUNDERS_NUM + CONFOUNDERS_CAT], df["treated"])
    return pd.Series(
        model.predict_proba(df[CONFOUNDERS_NUM + CONFOUNDERS_CAT])[:, 1],
        index=df.index)


def match_nearest(df: pd.DataFrame, caliper: float = 0.01):
    treated = df[df["treated"] == 1].copy()
    control = df[df["treated"] == 0].copy()
    nn = NearestNeighbors(n_neighbors=1).fit(control[["propensity"]])
    dist, idx = nn.kneighbors(treated[["propensity"]])
    keep = dist.flatten() <= caliper
    return treated[keep].copy(), control.iloc[idx.flatten()[keep]].copy()


def standardized_mean_diff(a: pd.Series, b: pd.Series) -> float:
    return (a.mean() - b.mean()) / np.sqrt((a.var() + b.var()) / 2)


def estimate_att(matched_treated: pd.DataFrame, matched_control: pd.DataFrame,
                 outcome: str = "review_score") -> dict:
    att = matched_treated[outcome].mean() - matched_control[outcome].mean()
    t, p = stats.ttest_rel(matched_treated[outcome].values,
                           matched_control[outcome].values)
    return {"att": att, "t_stat": t, "p_value": p,
            "n_pairs": len(matched_treated)}
