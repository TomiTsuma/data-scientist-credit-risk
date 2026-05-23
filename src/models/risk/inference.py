import pandas as pd


def predict_risk(model, X: pd.DataFrame) -> pd.Series:
    return model.predict_proba(X)[:, 1]
