USE sunculture_db;

-- ===================================
-- MART: CUSTOMER ACCOUNT ANALYTICS
-- ===================================
CREATE TABLE mart_customer_account_analytics
ENGINE = MergeTree()
ORDER BY (country_id, customer_id)
AS
SELECT
    fa.account_id,
    fa.customer_id,
    fa.country_id,

    dictGet('country_dict', 'country_name', fa.country_id) AS country_name,

    dc.gender,
    dc.age,
    dc.age_bucket,

    dictGet(
        'product_dict',
        'product_category',
        fa.product_id
    ) AS product_category,

    dictGet(
        'product_dict',
        'product_tier',
        fa.product_id
    ) AS product_tier,

    dictGet(
        'account_status_dict',
        'account_status_name',
        fa.account_status_id
    ) AS account_status,

    fa.financed_amount,
    fa.outstanding_balance,
    fa.arrears_balance,
    fa.days_past_due,

    fa.is_in_arrears,
    fa.is_default,

    fa.payment_type,

    fa.repayment_progress,

    fa.account_age_days,

    now() AS created_at

FROM fact_accounts fa
LEFT JOIN dim_customer dc
ON fa.customer_id = dc.customer_id;

-- ===================================
-- MART: SALES PERFORMANCE
-- ===================================
CREATE TABLE mart_sales_performance
ENGINE = MergeTree()
ORDER BY (country_id, sale_date)
AS
SELECT
    fs.sale_id,
    fs.sale_date,
    fs.country_id,

    dictGet(
        'country_dict',
        'country_name',
        fs.country_id
    ) AS country_name,

    dictGet(
        'product_dict',
        'product_name',
        fs.product_id
    ) AS product_name,

    dictGet(
        'product_dict',
        'product_category',
        fs.product_id
    ) AS product_category,

    dictGet(
        'lead_source_dict',
        'lead_source_name',
        fs.lead_source_id
    ) AS lead_source_name,

    fs.payment_type,

    fs.quantity,
    fs.total_sale_amount,
    fs.financed_amount,

    now() AS created_at

FROM fact_sales fs;

-- ===================================
-- MART: OPERATIONAL INSTALLATIONS
-- ===================================
CREATE TABLE mart_installation_operations
ENGINE = MergeTree()
ORDER BY (country_id, installation_date)
AS
SELECT
    fi.installation_id,
    fi.country_id,

    dictGet(
        'country_dict',
        'country_name',
        fi.country_id
    ) AS country_name,

    fi.sale_date,
    fi.installation_date,

    fi.installation_delay_days,

    fi.installation_status,

    dictGet(
        'product_dict',
        'product_category',
        fi.product_id
    ) AS product_category,

    dictGet(
        'user_dict',
        'full_name',
        fi.installer_user_id
    ) AS installer_name,

    dictGet(
        'user_dict',
        'department_name',
        fi.installer_user_id
    ) AS installer_department,

    now() AS created_at

FROM fact_installations fi;