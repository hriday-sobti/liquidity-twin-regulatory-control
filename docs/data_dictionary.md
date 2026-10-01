# Regulatory Liquidity Data Dictionary

**Schema**: PostgreSQL / SQLite Dual-Dialect  
**Monetary Standard**: `NUMERIC(24, 4)` in database, Python `Decimal` (`ROUND_HALF_EVEN`)  

---

## 1. Dimensional Entities

### `dim_date`
| Field Name | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `date_key` | Integer | Primary Key | Format YYYYMMDD (e.g. 20260930). |
| `date` | Date | Unique, Non-null | Calendar date representation. |
| `year` | Integer | Non-null | Calendar year. |
| `quarter` | Integer | Non-null | Calendar quarter (1–4). |
| `month` | Integer | Non-null | Month of year (1–12). |
| `day` | Integer | Non-null | Day of month (1–31). |
| `day_name` | String(16) | Non-null | Monday through Sunday. |
| `is_month_end` | Boolean | Non-null | True if date is final day of month. |
| `is_quarter_end`| Boolean | Non-null | True if date is final day of quarter. |
| `is_business_day`| Boolean | Non-null | True if Monday–Friday non-holiday. |

### `dim_account`
| Field Name | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `account_id` | String(64) | Primary Key | Unique account identifier (e.g. `ACC-CORP_OPERATIONAL`). |
| `account_number`| String(64)| Unique, Non-null | Core banking account reference. |
| `customer_id` | String(64) | Foreign Key | References `dim_customer.customer_id`. |
| `entity_id` | String(64) | Foreign Key | References `dim_entity.entity_id`. |
| `product_id` | String(64) | Foreign Key | References `dim_product.product_id`. |
| `currency` | String(3) | Non-null | ISO-4217 standard currency code (`USD`). |
| `open_date` | Date | Non-null | Date account was originated. |
| `status` | String(16) | Non-null | `ACTIVE`, `DORMANT`, or `CLOSED`. |
| `is_operational`| Boolean | Non-null | True if operational cash management relationship. |
| `is_insured` | Boolean | Non-null | True if covered by deposit insurance scheme. |

---

## 2. Fact Entities

### `fact_balance_sheet`
| Field Name | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `balance_id` | String(64) | Primary Key | Unique line balance identifier. |
| `snapshot_id` | String(64) | Foreign Key | References `fact_reporting_snapshot.snapshot_id`. |
| `business_date`| Date | Non-null | As-of reporting date. |
| `account_id` | String(64) | Foreign Key | References `dim_account.account_id`. |
| `opening_balance`| Numeric(24,4)| Non-null | Balance at start of close period. |
| `movement_amount`| Numeric(24,4)| Non-null | Net transaction inflows/outflows in period. |
| `closing_balance`| Numeric(24,4)| Non-null | Closing balance in account currency. |
| `closing_balance_usd`| Numeric(24,4)| Non-null| Closing balance converted to USD base. |
| `residual_maturity_days`| Integer| Nullable | Remaining days to contractual maturity. |
| `maturity_bucket`| String(32)| Non-null | `<6M`, `6M-1Y`, `>=1Y`, or `PERPETUAL`. |
| `is_encumbered`| Boolean | Non-null | True if pledged as repo or clearing margin. |
| `asf_factor` | Numeric(6,4)| Nullable | Applied Available Stable Funding weight. |
| `rsf_factor` | Numeric(6,4)| Nullable | Applied Required Stable Funding weight. |
| `asf_amount` | Numeric(24,4)| Non-null | `closing_balance_usd * asf_factor`. |
| `rsf_amount` | Numeric(24,4)| Non-null | `closing_balance_usd * rsf_factor`. |

### `fact_reporting_snapshot`
| Field Name | Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `snapshot_id` | String(64) | Primary Key | e.g. `SNAP-2026-Q3-BASE`. |
| `snapshot_name`| String(128)| Non-null | Formal title of reporting run. |
| `period` | String(16) | Non-null | Reporting period (`2026-Q3`). |
| `business_date`| Date | Non-null | Cutoff date for transaction events. |
| `snapshot_type`| String(32) | Non-null | `BASELINE`, `SCENARIO`, or `ADJUSTED`. |
| `status` | String(32) | Non-null | `FROZEN`, `SIGNED_OFF`, or `SUPERSEDED`. |
| `nsfr_value` | Numeric(10,4)| Nullable | Official calculated NSFR percentage (117.64%). |
| `lcr_value` | Numeric(10,4)| Nullable | Official calculated LCR percentage (132.49%). |
| `asf_amount` | Numeric(24,4)| Nullable | Total Available Stable Funding ($842.3M). |
| `rsf_amount` | Numeric(24,4)| Nullable | Total Required Stable Funding ($716.0M). |
| `control_score`| Numeric(6,2)| Nullable | Percentage of automated controls passing (98.0%). |
| `open_exceptions_count`| Integer| Non-null | Count of active unremediated breaks. |
