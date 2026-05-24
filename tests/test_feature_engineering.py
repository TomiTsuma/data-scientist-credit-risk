import pandas as pd

from src.data.joins import build_customer_analytics_table
from src.features.segmentation_features import create_segmentation_features, get_feature_columns


def test_create_segmentation_features():
    df = pd.DataFrame(
        {
            "customer_id": ["C1"],
            "age": [35],
            "account_age_days": [400],
            "financed_amount": [150000],
            "outstanding_balance": [50000],
            "arrears_balance": [0],
            "repayment_progress": [0.7],
            "days_past_due": [0],
            "is_in_arrears": [0],
            "is_default": [0],
            "is_healthy": [1],
            "country_name": ["Kenya"],
            "gender": ["Male"],
            "age_bucket": ["35-49"],
            "payment_type": ["PAYG"],
            "product_tier": ["New"],
            "lead_source": ["Agent"],
            "lead_conversion_speed": [10],
            "installation_delay_days": [5],
            "lead_quality_score": [0.6],
            "recency_score": [0.5],
            "frequency_score": [0.3],
            "monetary_score": [0.8],
            "risk_stress_score": [0.1],
            "install_delay_flag": [0],
        }
    )
    result = create_segmentation_features(df)
    assert "financed_amount_log" in result.columns
    assert len(get_feature_columns()) >= 10


def test_build_customer_table_from_excel():
    try:
        df = build_customer_analytics_table()
    except FileNotFoundError:
        return
    assert "customer_id" in df.columns
    assert len(df) > 1000
