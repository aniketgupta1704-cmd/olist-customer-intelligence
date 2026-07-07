"""Early-lifecycle segment / high-value prediction.

LEAKAGE FIREWALL: features use FIRST-ORDER quantities only. We deliberately
exclude lifetime recency/frequency/monetary/aov — the aggregates that DEFINED
the segments — so the model answers a genuine predictive question rather than
reverse-engineering the clustering boundaries.
"""
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier

FEATURE_COLS_NUM = ["first_n_items", "first_items_value", "first_freight",
                    "first_avg_item_price", "first_installments",
                    "first_n_payment_types", "first_payment_value",
                    "first_order_dow", "first_order_month"]
FEATURE_COLS_CAT = ["region", "first_category_grouped"]
HIGH_VALUE_SEGMENTS = ["High-Value One-Timers", "Repeat Buyers"]


def build_pipeline() -> Pipeline:
    prep = ColumnTransformer([
        ("num", StandardScaler(), FEATURE_COLS_NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
         FEATURE_COLS_CAT),
    ])
    return Pipeline([
        ("prep", prep),
        ("clf", RandomForestClassifier(n_estimators=300, max_depth=12,
                                       class_weight="balanced",
                                       random_state=42, n_jobs=-1)),
    ])


def predict_high_value(model, first_order_features: pd.DataFrame) -> np.ndarray:
    """Return P(high-value) for new customers given first-order features."""
    return model.predict_proba(first_order_features)[:, 1]


def load_classifier(path="models/segment_classifier.pkl"):
    return joblib.load(path)
