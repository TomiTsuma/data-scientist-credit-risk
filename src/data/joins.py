import pandas as pd


def merge_customer_data(customer_df: pd.DataFrame, transaction_df: pd.DataFrame) -> pd.DataFrame:
    return customer_df.merge(transaction_df, on='customer_id', how='left')
