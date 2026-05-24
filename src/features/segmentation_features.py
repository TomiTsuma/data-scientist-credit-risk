"""Feature engineering and sklearn preprocessing for customer segmentation."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler

# Columns used in clustering (documented in segmentation_report.md)
NUMERIC_FEATURES = [
    "age",
    "account_age_days",
    "financed_amount_log",
    "outstanding_to_financed",
    "repayment_progress",
    "arrears_rate",
    "days_past_due_cap",
    "lead_conversion_speed",
    "installation_delay_days",
    "lead_quality_score",
    "recency_score",
    "frequency_score",
    "monetary_score",
    "risk_stress_score",
]

CATEGORICAL_FEATURES = [
    "country_name",
    "gender",
    "age_bucket",
    "payment_type",
    "product_tier",
    "lead_source",
]

BINARY_FEATURES = ["is_in_arrears", "is_default", "is_healthy", "install_delay_flag"]

FEATURE_JUSTIFICATION = {
    "age": "Life-stage influences product fit and repayment capacity.",
    "account_age_days": "Tenure reflects relationship maturity and observed payment history length.",
    "financed_amount_log": "Log-scaled exposure proxy; reduces skew from product/pricing tiers.",
    "outstanding_to_financed": "Leverage remaining on the account.",
    "repayment_progress": "Payment discipline signal (derived from balance proxies).",
    "arrears_rate": "Current financial stress on outstanding balance.",
    "days_past_due_cap": "Delinquency severity (capped for stability).",
    "lead_conversion_speed": "Faster conversion often correlates with intent and channel quality.",
    "installation_delay_days": "Operational friction may precede payment stress.",
    "lead_quality_score": "Historical health rate by lead source (acquisition quality).",
    "recency_score": "RFM-style engagement proxy.",
    "frequency_score": "Multi-account / repeat relationship proxy.",
    "monetary_score": "Relative financed exposure within portfolio.",
    "risk_stress_score": "Composite arrears/default/delinquency signal.",
    "country_name": "Regional market and macro context (Kenya/Uganda/CIV).",
    "gender": "Demographic profile dimension.",
    "payment_type": "PAYG vs CASH captures financing behavior.",
    "product_tier": "New vs refurbished proxies product/affluence segment.",
    "lead_source": "Acquisition channel quality differs materially.",
}


def create_segmentation_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns used for clustering."""
    out = df.copy()
    out["financed_amount_log"] = np.log1p(out["financed_amount"].clip(lower=0))
    out["product_tier_ord"] = out["product_tier"].map({"Refurbished": 1, "New": 3}).fillna(2)
    out["payment_type_enc"] = (out["payment_type"] == "PAYG").astype(int)
    for col in BINARY_FEATURES:
        if col not in out.columns:
            out[col] = 0
    for col in NUMERIC_FEATURES:
        if col not in out.columns:
            out[col] = 0.0
    for col in CATEGORICAL_FEATURES:
        if col not in out.columns:
            out[col] = "Unknown"
        out[col] = out[col].fillna("Unknown").astype(str)
    return out


def get_feature_columns() -> list[str]:
    return NUMERIC_FEATURES + CATEGORICAL_FEATURES + BINARY_FEATURES


def build_preprocessor() -> ColumnTransformer:
    """Robust scaling for numerics; median imputation by column; one-hot categoricals."""
    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", RobustScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, NUMERIC_FEATURES),
            ("cat", categorical_pipe, CATEGORICAL_FEATURES),
            ("bin", "passthrough", BINARY_FEATURES),
        ],
        remainder="drop",
    )


def prepare_feature_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Return modeling frame and column list."""
    featured = create_segmentation_features(df)
    cols = get_feature_columns()
    return featured, cols
