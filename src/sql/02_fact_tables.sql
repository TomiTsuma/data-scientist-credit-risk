USE sunculture_db;

-- =========================
-- FACT: SALES
-- =========================
CREATE TABLE fact_sales
(
    sale_id String,
    customer_id String,
    product_id String,
    lead_source_id UUID,
    agent_id String,
    account_id String,
    country_id UUID,

    sale_date Date,
    sale_timestamp DateTime,

    account_type String,
    account_status String,

    created_at DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(sale_date)
ORDER BY (country_id, sale_date, customer_id);

-- =========================
-- FACT: ACCOUNTS
-- =========================
CREATE TABLE fact_accounts_snapshots
(
    account_id String,
    customer_id String,
    product_id String,
    country_id UUID,
    lead_source_id String,
    account_status_id UUID,
    activation_date Date,
    account_age_days UInt32,
    payment_type String,
    is_currently_in_arrears Boolean,
    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(activation_date)
ORDER BY (country_id, activation_date, customer_id);

-- =========================
-- FACT: INSTALLATIONS
-- =========================
CREATE TABLE fact_installations
(
    installation_id String,
    customer_id String,
    account_id String,
    product_id String,

    engineer_id String,

    country_id UUID,
    location_id UUID,

    sale_date Date,
    installation_date Date,

    installation_status String,

    created_at DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(installation_date)
ORDER BY (country_id, installation_date);

-- =========================
-- FACT: LEAD FUNNEL
-- =========================
CREATE TABLE fact_lead_funnel
(
    lead_id String,

    customer_id String,

    lead_source_id UUID,

    agent_id Nullable(String),

    lead_created_date Date,
    converted_to_account UInt8,
    converted_to_sale UInt8,
    converted_to_installation UInt8,

    days_to_account Nullable(UInt32),
    days_to_sale Nullable(UInt32),
    days_to_dispatch Nullable(UInt32),

    lead_quality_score Float32,

    created_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(lead_created_date)
ORDER BY (lead_created_date, lead_id);

-- -- =========================
-- -- FACT: MONTHLY ACCOUNT SNAPSHOT
-- -- Useful for IFRS9 / risk trend analysis
-- -- =========================
-- CREATE TABLE fact_account_monthly_snapshot
-- (
--     snapshot_date Date,

--     account_id String,
--     customer_id String,
--     country_id UUID,

--     outstanding_balance Float64,
--     arrears_balance Float64,

--     days_past_due UInt32,

--     account_status_id UUID,

--     repayment_progress Float32,

--     is_in_arrears UInt8,
--     is_default UInt8,

--     created_at DateTime
-- )
-- ENGINE = MergeTree()
-- PARTITION BY toYYYYMM(snapshot_date)
-- ORDER BY (snapshot_date, country_id, account_id);