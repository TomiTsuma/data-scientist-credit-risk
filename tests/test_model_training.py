import pandas as pd
from src.models.risk.train import train_logistic_risk_model


def test_train_logistic_risk_model():
    X = pd.DataFrame({'age': [25, 45], 'income': [50000, 80000]})
    y = pd.Series([0, 1])
    model = train_logistic_risk_model(X, y)
    assert model is not None
