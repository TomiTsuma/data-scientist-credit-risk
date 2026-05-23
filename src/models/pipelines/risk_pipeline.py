from src.features.risk_features import create_risk_features


def run_risk_pipeline(df):
    return create_risk_features(df)
