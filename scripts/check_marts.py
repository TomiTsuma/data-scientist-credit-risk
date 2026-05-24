from clickhouse_driver import Client

def check_marts():
    client = Client(
        host="localhost",
        port=9000,
        user="clickhouse_user",
        password="clickhouse_password"
    )
    
    marts = [
        "mart_customer_account_analytics",
        "mart_sales_performance",
        "mart_installation_operations"
    ]
    
    for mart in marts:
        print(f"\n================ MART: {mart} ================")
        try:
            desc = client.execute(f"DESCRIBE TABLE sunculture_db.{mart}")
            print("Columns:")
            for col in desc:
                print(f" - {col[0]}: {col[1]}")
            
            # Print the create statement if possible
            create_stmt = client.execute(f"SHOW CREATE TABLE sunculture_db.{mart}")[0][0]
            print("\nCreate statement:")
            print(create_stmt)
            
        except Exception as e:
            print("Error inspecting mart:", e)

if __name__ == "__main__":
    check_marts()
