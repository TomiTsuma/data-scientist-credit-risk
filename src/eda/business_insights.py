import pandas as pd


def summarize_business_metrics(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            'metric': ['total_customers', 'average_order_value'],
            'value': [df['customer_id'].nunique(), df['order_value'].mean() if 'order_value' in df else 0],
        }
    )
