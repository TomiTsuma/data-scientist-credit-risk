CREATE DATABASE IF NOT EXISTS sunculture_db;

USE sunculture_db;

-- =========================
-- DIMENSION: COUNTRY
-- =========================
CREATE TABLE dim_country
(
    country_id  UUID DEFAULT generateUUIDv4(),
    country_name String,
    currency String
)
ENGINE = MergeTree()
ORDER BY country_id;

CREATE TABLE dim_location
(
    location_id UUID DEFAULT generateUUIDv4(),
    country_id UUID,
    location_name String
)
ENGINE = MergeTree()
ORDER BY location_id;

-- =========================
-- DIMENSION: CUSTOMER
-- =========================
CREATE TABLE dim_customer
(
    customer_id String,
    gender String,
    date_of_birth Date,
    age UInt8,
    age_bucket String,
    country_id UUID,
    location_id UUID,
    latitude Float32,
    longitude Float32,
    created_at DateTime
)
ENGINE = MergeTree()
ORDER BY customer_id;

-- =========================
-- DIMENSION: PRODUCT
-- =========================
CREATE TABLE dim_product
(
    product_id String,
    product_name String,
    refurb_status String,
    created_at DateTime
)
ENGINE = MergeTree()
ORDER BY product_id;

-- =========================
-- DIMENSION: LEAD SOURCE
-- =========================
CREATE TABLE dim_lead_source
(
    lead_source_id UUID DEFAULT generateUUIDv4(),
    lead_source_name String
)
ENGINE = MergeTree()
ORDER BY lead_source_id;

-- =========================
-- DIMENSION: USER / EMPLOYEE
-- =========================
CREATE TABLE dim_employee
(
    employee_id String,
    full_name String,
    department_id String,
    created_at DateTime
)
ENGINE = MergeTree()
ORDER BY employee_id;


-- =========================
-- DIMENSION: DEPARTMENT
-- =========================
CREATE TABLE dim_department
(
    department_id String,
    department_name String
)
ENGINE = MergeTree()
ORDER BY department_id;


-- =========================
-- DIMENSION: ACCOUNT STATUS
-- =========================
CREATE TABLE dim_account_status
(
    account_status_id UUID DEFAULT generateUUIDv4(),
    account_status_name String,
    risk_category String
)
ENGINE = MergeTree()
ORDER BY account_status_id;