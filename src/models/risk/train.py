import pandas as pd
from sklearn.linear_model import LogisticRegression


def train_logistic_risk_model(X: pd.DataFrame, y: pd.Series):
    model = LogisticRegression(max_iter=500)
    model.fit(X, y)
    return model
