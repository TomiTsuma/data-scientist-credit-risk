from clickhouse_driver import Client

def test_queries():
    client = Client(
        host="localhost",
        port=9000,
        user="clickhouse_user",
        password="clickhouse_password"
    )
    
    # 1. Test mart_sales_performance SELECT
    print("--- Testing mart_sales_performance SELECT ---")
    query_sales = """
        SELECT
            fs.sale_id,
            fs.sale_date,
            fs.country_id,
            fs.payment_type
        FROM sunculture_db.fact_sales fs
        LIMIT 5
    """
    try:
        res = client.execute(query_sales)
        print("Success! Sample:", res)
    except Exception as e:
        print("Failed:", e)

    # Let's see if we can query dictGet on product_dict or country_dict
    print("\n--- Testing dictGet ---")
    query_dict = """
        SELECT 
            sale_id,
            dictGet('country_dict', 'country_name', country_id) as country_name
        FROM sunculture_db.fact_sales
        LIMIT 2
    """
    try:
        res = client.execute(query_dict)
        print("Success! Sample:", res)
    except Exception as e:
        print("Failed:", e)

if __name__ == "__main__":
    test_queries()
