import pandas as pd
from src.features.customer_features import create_customer_features


def test_create_customer_features():
    df = pd.DataFrame({'age': [25, 55]})
    result = create_customer_features(df)
    assert 'customer_age_group' in result.columns
