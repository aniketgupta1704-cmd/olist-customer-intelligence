"""Customer segmentation: feature prep, clustering, and labeling.

Note: clustering uses NUMERIC features only. Geographic (region) and
product category were tested as cluster inputs and found non-discriminative
(uniform across clusters), so they are retained for descriptive profiling
of the resulting value segments rather than as clustering inputs.
"""
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

NUMERIC_FEATS = ["recency_days", "frequency", "log_monetary", "log_aov"]

REGION_MAP = {
    "SP": "southeast", "RJ": "southeast", "MG": "southeast", "ES": "southeast",
    "PR": "south", "SC": "south", "RS": "south",
    "BA": "northeast", "PE": "northeast", "CE": "northeast", "MA": "northeast",
    "PB": "northeast", "RN": "northeast", "AL": "northeast", "SE": "northeast",
    "PI": "northeast",
    "GO": "centerwest", "DF": "centerwest", "MT": "centerwest", "MS": "centerwest",
    "PA": "north", "AM": "north", "RO": "north", "TO": "north",
    "AP": "north", "AC": "north", "RR": "north",
}


def engineer_features(df: pd.DataFrame, top_cats=None) -> pd.DataFrame:
    """Add log-transformed monetary fields and descriptive region/category."""
    df = df.copy()
    df["log_monetary"] = np.log1p(df["monetary"])
    df["log_aov"] = np.log1p(df["avg_order_value"])
    if top_cats is None:
        top_cats = df["category_en"].value_counts().head(10).index
    df["category_grouped"] = np.where(df["category_en"].isin(top_cats),
                                      df["category_en"], "other")
    df["region"] = df["customer_state"].map(REGION_MAP).fillna("unknown")
    return df


def build_preprocessor() -> StandardScaler:
    """Numeric-only scaler. See module docstring for why categoricals excluded."""
    return StandardScaler()


def fit_clusterer(X, n_clusters: int, random_state: int = 42) -> KMeans:
    return KMeans(n_clusters=n_clusters, random_state=random_state,
                  n_init=10).fit(X)


def load_artifacts(clusterer_path="models/clusterer.pkl",
                   preprocessor_path="models/preprocessor.pkl"):
    return joblib.load(clusterer_path), joblib.load(preprocessor_path)
