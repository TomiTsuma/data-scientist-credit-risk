import pandas as pd

def inspect_timeline():
    excel_path = "c:\\Users\\tsuma.thomas\\Documents\\Sunculture\\data\\raw\\Senior_Data_Scientist_Assessment_Data (1) (1) (1) (1).xlsx"
    
    # Load all tables
    cust = pd.read_excel(excel_path, sheet_name="Customers")
    leads = pd.read_excel(excel_path, sheet_name="Leads")
    accounts = pd.read_excel(excel_path, sheet_name="Accounts")
    sales = pd.read_excel(excel_path, sheet_name="Sales")
    inst = pd.read_excel(excel_path, sheet_name="Installations")
    
    # Rename columns for join and display
    cust = cust.rename(columns={'id': 'customer_id', 'created_at': 'cust_created'})
    leads = leads.rename(columns={'Id': 'lead_id', 'created_at': 'lead_created'})
    accounts = accounts.rename(columns={'id': 'account_id', 'created_at': 'acc_created'})
    sales = sales.rename(columns={'Id': 'sale_id', 'created_at': 'sale_created'})
    inst = inst.rename(columns={'Id': 'inst_id', 'created_at': 'inst_created'})
    
    # Join
    df = pd.merge(cust[['customer_id', 'region', 'cust_created']], accounts[['account_id', 'customer_id', 'acc_created', 'Installation_id', 'lead_id', 'First_installment_date', 'Dispatch_date']], on='customer_id', how='inner')
    df = pd.merge(df, leads[['lead_id', 'lead_created']], on='lead_id', how='left')
    df = pd.merge(df, sales[['account_id', 'sale_id', 'Sale_date']], on='account_id', how='left')
    df = pd.merge(df, inst[['inst_id', 'Installation_date', 'inst_created']], left_on='Installation_id', right_on='inst_id', how='left')
    
    # Print the first 10 rows with formatted columns
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    for i, row in df.head(10).iterrows():
        print(f"Row {i}: Customer: {row['customer_id']} ({row['region']})")
        print(f"  - Cust Created: {str(row['cust_created'])[:10]}")
        print(f"  - Lead Created: {str(row['lead_created'])[:10]}")
        print(f"  - Acc Created:  {str(row['acc_created'])[:10]}")
        print(f"  - Sale Date:    {str(row['Sale_date'])[:10]}")
        print(f"  - Install Date: {str(row['Installation_date'])[:10]}")
        print(f"  - Disp Date:    {str(row['Dispatch_date'])[:10]}")
        print(f"  - First Inst:   {str(row['First_installment_date'])[:10]}")
        print()

if __name__ == "__main__":
    inspect_timeline()
