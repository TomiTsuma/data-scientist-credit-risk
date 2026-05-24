# `fact_lead_funnel` — Population Guide

> **Purpose:** This document describes how to populate the `fact_lead_funnel` table defined in [`src/sql/02_fact_tables.sql`](../src/sql/02_fact_tables.sql) using the raw source data found in the assessment Excel workbook.

---

## 1. Table Schema Reference

```sql
CREATE TABLE fact_lead_funnel
(
    lead_id                   UInt64,
    customer_id               String,
    lead_source_id            UInt32,
    employee_id               String,
    country_id                UInt32,
    lead_created_date         Date,
    converted_to_account      UInt8,
    converted_to_sale         UInt8,
    converted_to_installation UInt8,
    days_to_account           Nullable(UInt32),
    days_to_sale              Nullable(UInt32),
    days_to_installation      Nullable(UInt32),
    lead_quality_score        Float32,
    created_at                DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(lead_created_date)
ORDER BY (country_id, lead_created_date);
```

---

## 2. Source Data Overview

The raw data is contained in the Excel workbook:

```
data/raw/Senior_Data_Scientist_Assessment_Data.xlsx
```

The workbook contains the following sheets, all of which contribute to populating this table:

| Sheet          | Primary Key       | Rows  | Description                                      |
|----------------|-------------------|-------|--------------------------------------------------|
| `Leads`        | `Id`              | 6,000 | One row per lead — the **grain** of this table   |
| `Accounts`     | `id`              | 4,750 | Accounts linked back to leads via `lead_id`      |
| `Sales`        | `Id`              | 4,750 | Sales linked to accounts via `account_id`        |
| `Installations`| `Id`              | 4,500 | Installations linked to accounts via `Installation_id` |
| `Customers`    | `id`              | 5,000 | Customer demographic data (region, gender, etc.) |
| `Users`        | `Id`              | 30    | Employees (agents, engineers)                    |
| `Departments`  | `Id`              | 5     | Department reference                             |

---

## 3. Column-by-Column Mapping

### 3.1 `lead_id` — `UInt64`

**Source:** `Leads.Id`

The raw lead IDs follow the format `LEAD-XXXXX` (e.g., `LEAD-50000`). Strip the `LEAD-` prefix and cast the numeric portion to `UInt64`.

```python
# Python example
lead_id = int(row['Id'].replace('LEAD-', ''))
```

---

### 3.2 `customer_id` — `String`

**Source:** `Leads.customer_id`

Direct copy. Values follow the format `CUST-XXXXX` (e.g., `CUST-10000`). Join to the `dim_customer` table on `customer_id`.

---

### 3.3 `lead_source_id` — `UInt32`

**Source:** `Leads.Source` → `dim_lead_source.lead_source_id`

The `Leads.Source` field contains free-text channel names. These must first be resolved to surrogate keys by joining against `dim_lead_source`.

**Observed lead source values in raw data:**

| Source Name      | Description                          |
|------------------|--------------------------------------|
| `Roadshow`       | Field marketing events               |
| `Refer and Earn` | Customer referral programme          |
| `Facebook`       | Social media (Facebook)              |
| `Website`        | Organic / paid web traffic           |
| `Walk-in`        | Customer walked into a branch        |
| `Telesales`      | Outbound / inbound call centre       |
| `Door to Door`   | Field agent canvassing               |
| `Partners`       | Third-party distribution partners    |

```sql
-- Example join
SELECT
    l.Id AS lead_id,
    dls.lead_source_id
FROM Leads l
JOIN dim_lead_source dls ON dls.lead_source_name = l.Source
```

---

### 3.4 `employee_id` — `String`

**Source:** `Accounts.Agent_id`

The agent who processed the associated account. This is available only for leads that converted to an account. For leads with no account, set to an empty string `''` or a sentinel value (e.g., `'UNKNOWN'`).

Join path: `Leads.Id` → `Accounts.lead_id` → `Accounts.Agent_id`

```python
agent_id = account['Agent_id'] if account else ''
```

---

### 3.5 `country_id` — `UInt32`

**Source:** `Customers.region` → `dim_country.country_id`

Join `Leads.customer_id` → `Customers.id` to obtain the customer's region, then resolve to the `dim_country` surrogate key.

**Observed regions in raw data:**

| Region code | Country              |
|-------------|----------------------|
| `kenya`     | Kenya                |
| `uganda`    | Uganda               |
| `civ`       | Côte d'Ivoire        |

```sql
SELECT
    c.region,
    dc.country_id
FROM Customers c
JOIN dim_country dc ON lower(dc.country_name) = lower(c.region)
```

> **Note:** The `country_id` in the table is typed `UInt32`. If `dim_country` uses UUIDs (as defined in `01_dimension_tables.sql`), consider converting to an integer hash or updating the fact table type to `UUID` for consistency.

---

### 3.6 `lead_created_date` — `Date`

**Source:** `Leads.created_at`

Cast directly to `Date`. This field also drives the table's partition key (`toYYYYMM(lead_created_date)`).

```python
lead_created_date = datetime.strptime(row['created_at'], '%Y-%m-%d').date()
```

---

### 3.7 `converted_to_account` — `UInt8` (boolean flag)

**Source:** Derived — join `Leads.Id` → `Accounts.lead_id`

Set to `1` if a matching row exists in the `Accounts` sheet for this lead; `0` otherwise.

**Observed conversion rate:** ~79.2% of leads (4,750 out of 6,000) have a linked account.

```python
converted_to_account = 1 if lead_id in acc_by_lead else 0
```

---

### 3.8 `converted_to_sale` — `UInt8` (boolean flag)

**Source:** Derived — join `Leads.Id` → `Accounts.lead_id` → `Sales.account_id`

Set to `1` if the lead has a linked account **and** that account has a linked sale; `0` otherwise.

**Observed conversion rate:** ~79.2% (4,750 out of 6,000). In the raw data, every account has exactly one sale, so `converted_to_account` and `converted_to_sale` currently have the same rate.

```python
account = acc_by_lead.get(lead_id)
converted_to_sale = 1 if account and account['id'] in sale_by_acc else 0
```

---

### 3.9 `converted_to_installation` — `UInt8` (boolean flag)

**Source:** Derived — join `Leads.Id` → `Accounts.lead_id` → `Accounts.Installation_id` → `Installations.Id`

Set to `1` if the linked account has a valid `Installation_id` that exists in the `Installations` sheet; `0` otherwise.

**Observed conversion rate:** ~75.0% (4,500 out of 6,000 leads). Some accounts have no installation, which represents accounts dispatched but not yet installed, repossessed, or written off.

```python
inst_id = account.get('Installation_id') if account else None
converted_to_installation = 1 if inst_id and inst_id in inst_by_id else 0
```

---

### 3.10 `days_to_account` — `Nullable(UInt32)`

**Source:** Derived — `Accounts.created_at` minus `Leads.created_at`

Number of calendar days from lead creation to account creation. Set to `NULL` if the lead did not convert to an account.

```python
if account:
    delta = (parse_date(account['created_at']) - lead_date).days
    days_to_account = max(0, delta)  # clamp negatives to 0 (see data quality note below)
else:
    days_to_account = None
```

> **⚠️ Data Quality Note:** The raw data contains negative `days_to_account` values (minimum observed: -817 days), indicating that some accounts have a `created_at` date earlier than their linked lead's `created_at`. This is likely a data entry inconsistency in the source system. **Recommended handling:** clamp negative values to `0` and flag them in a separate data quality log, or use `NULL` if the timeline cannot be determined reliably.

---

### 3.11 `days_to_sale` — `Nullable(UInt32)`

**Source:** Derived — `Sales.Sale_date` minus `Leads.created_at`

Number of calendar days from lead creation to sale date. Set to `NULL` if no sale occurred.

In the current dataset, `days_to_account` and `days_to_sale` are identical because the `Accounts.created_at` and `Sales.Sale_date` are the same on every row.

```python
if sale:
    delta = (parse_date(sale['Sale_date']) - lead_date).days
    days_to_sale = max(0, delta)
else:
    days_to_sale = None
```

---

### 3.12 `days_to_installation` — `Nullable(UInt32)`

**Source:** Derived — `Installations.Installation_date` minus `Leads.created_at`

Number of calendar days from lead creation to physical installation. Set to `NULL` if no installation exists.

```python
if installation:
    delta = (parse_date(installation['Installation_date']) - lead_date).days
    days_to_installation = max(0, delta)
else:
    days_to_installation = None
```

---

### 3.13 `lead_quality_score` — `Float32`

**Source:** Derived / engineered — **no direct source column exists in the raw data**

This field must be calculated. It is a composite score (range `0.0` – `1.0`) that summarises the likelihood or quality of a lead. A recommended baseline approach:

| Component                       | Weight | Logic                                                    |
|---------------------------------|--------|----------------------------------------------------------|
| Converted to account            | 40%    | `0.4` if `converted_to_account = 1`, else `0.0`         |
| Converted to sale               | 30%    | `0.3` if `converted_to_sale = 1`, else `0.0`            |
| Converted to installation       | 20%    | `0.2` if `converted_to_installation = 1`, else `0.0`    |
| Speed-to-account bonus          | 10%    | Scaled inversely by `days_to_account` (faster = higher) |

```python
def compute_quality_score(converted_to_account, converted_to_sale,
                          converted_to_installation, days_to_account):
    score = 0.0
    score += 0.4 if converted_to_account else 0.0
    score += 0.3 if converted_to_sale else 0.0
    score += 0.2 if converted_to_installation else 0.0
    if days_to_account is not None and days_to_account >= 0:
        # bonus: max 0.1 for same-day conversion, decays over 90 days
        speed_bonus = max(0.0, 0.1 * (1 - days_to_account / 90))
        score += speed_bonus
    return round(min(score, 1.0), 4)
```

> **Note:** This scoring formula is a starting point. It should be validated and refined using historical outcome data (e.g., account status, repayment behaviour).

---

### 3.14 `created_at` — `DateTime`

**Source:** Computed at ETL load time

Set to the current UTC timestamp at the time the row is inserted into ClickHouse.

```python
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
```

---

## 4. Join Map (Entity Relationship)

```
Leads (Id)
  │
  ├─── customer_id ──────► Customers (id) ──► dim_country (via region)
  │
  ├─── Source ────────────► dim_lead_source (lead_source_name)
  │
  └─── Id = Accounts.lead_id
            │
            ├─── Agent_id ──────────► dim_employee (employee_id)
            ├─── id ───────────────► Sales (account_id) ──► Sale_date
            └─── Installation_id ──► Installations (Id) ──► Installation_date
```

---

## 5. Conversion Funnel Summary (Observed in Raw Data)

```
6,000  Total Leads
  │
  ├── 4,750  Converted to Account      (79.2%)
  │     │
  │     ├── 4,750  Converted to Sale   (79.2% of leads / 100% of accounts)
  │     │
  │     └── 4,500  Converted to Install(75.0% of leads / 94.7% of accounts)
  │
  └── 1,250  No conversion             (20.8%)
```

---

## 6. Full ETL Pseudocode

```python
import openpyxl
from datetime import datetime, timezone, date

wb = openpyxl.load_workbook('data/raw/Senior_Data_Scientist_Assessment_Data.xlsx')

# --- Load source sheets ---
leads_rows        = load_sheet(wb, 'Leads')        # Id, Source, customer_id, created_at
accounts_rows     = load_sheet(wb, 'Accounts')      # id, customer_id, lead_id, Agent_id, Installation_id, created_at
sales_rows        = load_sheet(wb, 'Sales')         # Id, account_id, Sale_date
installations_rows= load_sheet(wb, 'Installations') # Id, Installation_date
customers_rows    = load_sheet(wb, 'Customers')     # id, region

# --- Build lookup maps ---
acc_by_lead  = {r['lead_id']: r for r in accounts_rows}
sale_by_acc  = {r['account_id']: r for r in sales_rows}
inst_by_id   = {r['Id']: r for r in installations_rows}
cust_by_id   = {r['id']: r for r in customers_rows}

# --- Load dimension lookups (from dim tables already populated) ---
country_map   = load_dim_country()     # {'kenya': 1, 'uganda': 2, 'civ': 3}
lead_src_map  = load_dim_lead_source() # {'Roadshow': 101, 'Facebook': 102, ...}

fact_rows = []
for lead in leads_rows:
    lead_id_raw   = lead['Id']                              # 'LEAD-50000'
    lead_id       = int(lead_id_raw.replace('LEAD-', ''))  # 50000
    customer_id   = lead['customer_id']
    lead_date     = parse_date(lead['created_at'])

    account       = acc_by_lead.get(lead_id_raw)
    sale          = sale_by_acc.get(account['id']) if account else None
    installation  = inst_by_id.get(account.get('Installation_id')) if account else None
    customer      = cust_by_id.get(customer_id)

    # --- Dimension keys ---
    lead_source_id = lead_src_map.get(lead['Source'], 0)
    employee_id    = account['Agent_id'] if account else ''
    region         = customer['region'] if customer else ''
    country_id     = country_map.get(region, 0)

    # --- Conversion flags ---
    converted_to_account      = 1 if account else 0
    converted_to_sale         = 1 if sale else 0
    converted_to_installation = 1 if installation else 0

    # --- Days metrics ---
    days_to_account      = safe_days(account['created_at'], lead_date) if account else None
    days_to_sale         = safe_days(sale['Sale_date'], lead_date) if sale else None
    days_to_installation = safe_days(installation['Installation_date'], lead_date) if installation else None

    # --- Quality score ---
    lead_quality_score = compute_quality_score(
        converted_to_account, converted_to_sale,
        converted_to_installation, days_to_account
    )

    fact_rows.append({
        'lead_id':                   lead_id,
        'customer_id':               customer_id,
        'lead_source_id':            lead_source_id,
        'employee_id':               employee_id,
        'country_id':                country_id,
        'lead_created_date':         lead_date,
        'converted_to_account':      converted_to_account,
        'converted_to_sale':         converted_to_sale,
        'converted_to_installation': converted_to_installation,
        'days_to_account':           days_to_account,
        'days_to_sale':              days_to_sale,
        'days_to_installation':      days_to_installation,
        'lead_quality_score':        lead_quality_score,
        'created_at':                datetime.now(timezone.utc),
    })

insert_into_clickhouse('fact_lead_funnel', fact_rows)
```

---

## 7. Data Quality Checks

Before loading, validate the following:

| Check | Expected | Action on Failure |
|---|---|---|
| All `Leads.Id` values are unique | No duplicates | Deduplicate on latest `updated_at` |
| `Leads.customer_id` exists in `Customers.id` | 100% match | Log and set `customer_id = ''` |
| `Accounts.lead_id` references a valid `Leads.Id` | 100% match | Log orphan accounts |
| `Sales.account_id` references a valid `Accounts.id` | 100% match | Log orphan sales |
| `Installations.Id` referenced in `Accounts` exists | 100% match | Set installation flag = 0 |
| `days_to_account >= 0` | No negative values | Clamp to 0; log anomalies |
| `lead_quality_score` between 0.0 and 1.0 | Always true | Cap / floor score |
| `Leads.Source` maps to a known `dim_lead_source` | 8 known values | Reject or use `0` as unknown |

---

## 8. Partitioning & Ordering Notes

The table is partitioned by `toYYYYMM(lead_created_date)` and ordered by `(country_id, lead_created_date)`. This means:

- **Insert order matters:** batch inserts should be sorted by `country_id, lead_created_date` to avoid out-of-order part merges.
- **Query patterns:** analytical queries that filter by country and date range will be most efficient.
- **Backfill:** when loading historical data, partition by month to avoid creating too many small parts.

---

## 9. Related Tables

| Table | Relationship | Usage |
|---|---|---|
| `dim_customer` | `fact_lead_funnel.customer_id = dim_customer.customer_id` | Customer demographics |
| `dim_lead_source` | `fact_lead_funnel.lead_source_id = dim_lead_source.lead_source_id` | Channel attribution |
| `dim_employee` | `fact_lead_funnel.employee_id = dim_employee.employee_id` | Agent performance |
| `dim_country` | `fact_lead_funnel.country_id = dim_country.country_id` | Country segmentation |
| `fact_sales` | Join on `customer_id` | Cross-reference sale revenue |
| `fact_installations` | Join on `customer_id` / `account_id` | Installation details |
| `fact_account_monthly_snapshot` | Join on `customer_id` | Account health over time |
