from clickhouse_driver import Client

def test_creation():
    client = Client(
        host="localhost",
        port=9000,
        user="clickhouse_user",
        password="clickhouse_password"
    )
    
    # Let's drop them first
    marts = [
        "mart_customer_account_analytics",
        "mart_sales_performance",
        "mart_installation_operations"
    ]
    for mart in marts:
        client.execute(f"DROP TABLE IF EXISTS sunculture_db.{mart}")
        
    # Query 1
    query1 = """
        CREATE TABLE sunculture_db.mart_customer_account_analytics
        ENGINE = MergeTree()
        ORDER BY (country_id, customer_id)
        AS
        SELECT
            fa.account_id,
            fa.customer_id,
            fa.country_id,
            dc.country_name AS country_name,
            cust.gender AS gender,
            cust.age AS age,
            cust.age_bucket AS age_bucket,
            dp.product_name AS product_category,
            dp.refurb_status AS product_tier,
            das.account_status_name AS account_status,
            0.0 AS financed_amount,
            0.0 AS outstanding_balance,
            0.0 AS arrears_balance,
            0 AS days_past_due,
            fa.is_currently_in_arrears AS is_in_arrears,
            0 AS is_default,
            fa.payment_type AS payment_type,
            0.0 AS repayment_progress,
            fa.account_age_days AS account_age_days,
            now() AS created_at
        FROM sunculture_db.fact_accounts_snapshots fa
        LEFT JOIN sunculture_db.dim_customer cust ON fa.customer_id = cust.customer_id
        LEFT JOIN sunculture_db.dim_country dc ON fa.country_id = dc.country_id
        LEFT JOIN sunculture_db.dim_product dp ON fa.product_id = dp.product_id
        LEFT JOIN sunculture_db.dim_account_status das ON fa.account_status_id = das.account_status_id
    """
    
    print("\n--- Running Query 1 ---")
    try:
        client.execute(query1)
        print("Query 1 Success!")
    except Exception as e:
        print("Query 1 Failed:", str(e)[:300])
        
    # Query 2
    query2 = """
        CREATE TABLE sunculture_db.mart_sales_performance
        ENGINE = MergeTree()
        ORDER BY (country_id, sale_date)
        AS
        SELECT
            fs.sale_id,
            fs.sale_date,
            fs.country_id,
            dc.country_name AS country_name,
            dp.product_name AS product_name,
            dp.refurb_status AS product_category,
            dls.lead_source_name AS lead_source_name,
            fs.payment_type,
            1 AS quantity,
            0.0 AS total_sale_amount,
            0.0 AS financed_amount,
            now() AS created_at
        FROM sunculture_db.fact_sales fs
        LEFT JOIN sunculture_db.dim_country dc ON fs.country_id = dc.country_id
        LEFT JOIN sunculture_db.dim_product dp ON fs.product_id = dp.product_id
        LEFT JOIN sunculture_db.dim_lead_source dls ON fs.lead_source_id = dls.lead_source_id
    """
    print("\n--- Running Query 2 ---")
    try:
        client.execute(query2)
        print("Query 2 Success!")
    except Exception as e:
        print("Query 2 Failed:", str(e)[:300])
        
    # Query 3
    query3 = """
        CREATE TABLE sunculture_db.mart_installation_operations
        ENGINE = MergeTree()
        ORDER BY (country_id, installation_date)
        AS
        SELECT
            fi.installation_id,
            fi.country_id,
            dc.country_name AS country_name,
            fi.sale_date,
            fi.installation_date,
            dateDiff('day', fi.sale_date, fi.installation_date) AS installation_delay_days,
            fi.installation_status,
            dp.product_name AS product_category,
            de.full_name AS installer_name,
            dd.department_name AS installer_department,
            now() AS created_at
        FROM sunculture_db.fact_installations fi
        LEFT JOIN sunculture_db.dim_country dc ON fi.country_id = dc.country_id
        LEFT JOIN sunculture_db.dim_product dp ON fi.product_id = dp.product_id
        LEFT JOIN sunculture_db.dim_employee de ON fi.engineer_id = de.employee_id
        LEFT JOIN sunculture_db.dim_department dd ON de.department_id = dd.department_id
    """
    print("\n--- Running Query 3 ---")
    try:
        client.execute(query3)
        print("Query 3 Success!")
    except Exception as e:
        print("Query 3 Failed:", str(e)[:300])

if __name__ == "__main__":
    test_creation()
