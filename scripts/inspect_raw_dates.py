import pandas as pd

def inspect_raw_dates():
    excel_path = "c:\\Users\\tsuma.thomas\\Documents\\Sunculture\\data\\raw\\Senior_Data_Scientist_Assessment_Data (1) (1) (1) (1).xlsx"
    
    # Load raw tables
    accounts = pd.read_excel(excel_path, sheet_name="Accounts")
    sales = pd.read_excel(excel_path, sheet_name="Sales")
    installations = pd.read_excel(excel_path, sheet_name="Installations")
    
    print("Accounts columns:", accounts.columns)
    print("Sales columns:", sales.columns)
    print("Installations columns:", installations.columns)
    
    # Join them
    # accounts has: id, customer_id, status, type, created_at, updated_at, Installation_id, Dispatch_date, First_installment_date, Agent_id, Proudct_id, lead_id
    # sales has: Id, account_id, Sale_date, created_at, updated_at
    # installations has: Id, Installation_date, engineer_id, created_at, updated_at
    
    # Merge accounts with sales
    m1 = pd.merge(accounts, sales, left_on='id', right_on='account_id', suffixes=('_acc', '_sale'))
    # Merge with installations
    m2 = pd.merge(m1, installations, left_on='Installation_id', right_on='Id', suffixes=('', '_inst'))
    
    # Parse dates
    m2['Sale_date'] = pd.to_datetime(m2['Sale_date'])
    m2['Installation_date'] = pd.to_datetime(m2['Installation_date'])
    m2['delay'] = (m2['Installation_date'] - m2['Sale_date']).dt.days
    
    print("\n--- Joined Data Preview ---")
    print(m2[['id', 'Sale_date', 'Installation_id', 'Installation_date', 'delay']].head(10))
    
    print("\n--- Delay statistics in raw data ---")
    print(m2['delay'].describe())
    
    print("\n--- Example records where delay < 0 ---")
    neg_delays = m2[m2['delay'] < 0]
    print(f"Total negative delay records: {len(neg_delays)}")
    print(neg_delays[['id', 'Sale_date', 'Installation_id', 'Installation_date', 'delay']].head(5))

    print("\n--- Example records where delay >= 0 ---")
    pos_delays = m2[m2['delay'] >= 0]
    print(f"Total positive/zero delay records: {len(pos_delays)}")
    print(pos_delays[['id', 'Sale_date', 'Installation_id', 'Installation_date', 'delay']].head(5))

if __name__ == "__main__":
    inspect_raw_dates()
