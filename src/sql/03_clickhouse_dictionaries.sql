USE sunculture_db;

-- =========================
-- PRODUCT DICTIONARY
-- =========================
CREATE DICTIONARY product_dict
(
    product_id UInt64,
    product_name String,
    product_category String,
    product_tier String,
    refurb_status String
)
PRIMARY KEY product_id
SOURCE(CLICKHOUSE(
    HOST 'localhost'
    PORT 9000
    USER 'clickhouse_user'
    TABLE 'dim_product'
    PASSWORD 'clickhouse_password'
    DB 'sunculture_db'
))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED());

-- =========================
-- COUNTRY DICTIONARY
-- =========================
CREATE DICTIONARY country_dict
(
    country_id UInt32,
    country_name String,
    region_cluster String
)
PRIMARY KEY country_id
SOURCE(CLICKHOUSE(
    HOST 'localhost'
    PORT 9000
    USER 'clickhouse_user'
    TABLE 'dim_country'
    PASSWORD 'clickhouse_password'
    DB 'sunculture_db'
))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED());

-- =========================
-- LEAD SOURCE DICTIONARY
-- =========================
CREATE DICTIONARY lead_source_dict
(
    lead_source_id UInt32,
    lead_source_name String,
    acquisition_channel String
)
PRIMARY KEY lead_source_id
SOURCE(CLICKHOUSE(
    HOST 'localhost'
    PORT 9000
    USER 'clickhouse_user'
    TABLE 'dim_lead_source'
    PASSWORD 'clickhouse_password'
    DB 'sunculture_db'
))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED());

-- =========================
-- ACCOUNT STATUS DICTIONARY
-- =========================
CREATE DICTIONARY account_status_dict
(
    account_status_id UInt32,
    account_status_name String,
    risk_category String
)
PRIMARY KEY account_status_id
SOURCE(CLICKHOUSE(
    HOST 'localhost'
    PORT 9000
    USER 'clickhouse_user'
    TABLE 'dim_account_status'
    PASSWORD 'clickhouse_password'
    DB 'sunculture_db'
))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED());

-- =========================
-- USER DICTIONARY
-- =========================
CREATE DICTIONARY user_dict
(
    user_id UInt64,
    full_name String,
    department_name String,
    role_name String
)
PRIMARY KEY user_id
SOURCE(CLICKHOUSE(
    HOST 'localhost'
    PORT 9000
    USER 'clickhouse_user'
    TABLE 'dim_user'
    PASSWORD 'clickhouse_password'
    DB 'sunculture_db'
))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED());