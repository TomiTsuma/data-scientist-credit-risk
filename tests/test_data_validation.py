import pandas as pd
from src.data.validation import validate_schema


def test_validate_schema_passes():
    df = pd.DataFrame({'customer_id': [1], 'age': [30]})
    assert validate_schema(df, ['customer_id', 'age'])
