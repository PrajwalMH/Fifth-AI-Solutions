# Day 4 — Data Quality and Governance Assessment

**Name:** Prajwal Mrithyunjay Hulamani

## 1. Quality report

### Dataset summary

- Raw rows: **15**
- Columns: **11**
- Overall completeness: **96.97%**
- Overall validity across non-missing values: **95.0%**
- Unique customer IDs: **14**
- Customer ID uniqueness: **93.33%**
- Rows involved in duplicate customer IDs: **2**
- Duplicate customer records beyond the first occurrence: **1**

### Completeness by field

| field | missing_count | missing_percent | complete_percent |
| --- | --- | --- | --- |
| customer_id | 0 | 0.0 | 100.0 |
| name | 0 | 0.0 | 100.0 |
| email | 1 | 6.67 | 93.33 |
| age | 1 | 6.67 | 93.33 |
| monthly_spend | 1 | 6.67 | 93.33 |
| plan_tier | 0 | 0.0 | 100.0 |
| signup_date | 1 | 6.67 | 93.33 |
| satisfaction_score | 0 | 0.0 | 100.0 |
| device_os | 0 | 0.0 | 100.0 |
| data_usage_gb | 1 | 6.67 | 93.33 |
| is_active | 0 | 0.0 | 100.0 |

### Validity by field

| field | non_missing | invalid_count | validity_percent |
| --- | --- | --- | --- |
| customer_id | 15 | 0 | 100.0 |
| name | 15 | 0 | 100.0 |
| email | 14 | 1 | 92.86 |
| age | 14 | 1 | 92.86 |
| monthly_spend | 14 | 1 | 92.86 |
| plan_tier | 15 | 2 | 86.67 |
| signup_date | 14 | 0 | 100.0 |
| satisfaction_score | 15 | 1 | 93.33 |
| device_os | 15 | 1 | 93.33 |
| data_usage_gb | 14 | 1 | 92.86 |
| is_active | 15 | 0 | 100.0 |

## 2. Cleaning changelog

| decision | assumption | records_affected |
| --- | --- | --- |
| Trim whitespace and lowercase email values | Leading/trailing spaces and letter case are formatting differences, not different addresses. | 3 |
| Standardize plan_tier values to Basic, Standard or Premium | Case differences represent the same business category. | 2 |
| Standardize device_os labels | Case differences represent the same operating system. | 1 |
| Replace invalid email syntax with missing value | An invalid address cannot be corrected reliably without an authoritative source. | 1 |
| Replace age outside 18-100 with missing value | The out-of-range value is treated as a data-entry error and is not guessed. | 1 |
| Replace negative monthly_spend with missing value | Customer spending cannot be negative in this dataset and the true value is unknown. | 1 |
| Replace satisfaction_score outside 1-5 with missing value | The survey scale is defined as 1 through 5. | 1 |
| Replace negative data_usage_gb with missing value | Usage cannot be negative and the true amount is unknown. | 1 |
| Remove duplicate customer_id records and keep the last row | Later records supersede earlier records for the same customer. | 1 |
| Leave unresolved missing values as missing | No authoritative source is available, so inventing replacement values would reduce data integrity. | 10 |

## 3. Sensitivity classification and controls

| field | sensitivity | control |
| --- | --- | --- |
| customer_id | Internal | Role-based access control (RBAC) and access logging |
| name | Personal | Encrypt at rest and mask in non-production environments |
| email | Personal | Mask in reports and restrict access to approved roles |
| age | Personal | Use age bands for analytics where exact age is unnecessary |
| monthly_spend | Confidential | Restrict to finance/customer-analytics roles |
| plan_tier | Internal | RBAC; expose only to teams with a business need |
| signup_date | Internal | Restrict bulk exports and log access |
| satisfaction_score | Confidential | Report in aggregate where possible |
| device_os | Internal | Least-privilege analytics access |
| data_usage_gb | Confidential | Restrict behavioral-usage data to authorized analytics roles |
| is_active | Internal | RBAC and access logging |

## Governance owner and steward

**Dataset Owner: Customer Operations Manager**

The owner is accountable for why the customer dataset exists, which business uses are permitted, who should receive access, and the quality level required for operational decisions.

**Dataset Steward: Data Governance Analyst**

The steward manages the day-to-day definitions, quality rules, issue tracking, cleaning documentation, metadata, and control implementation.

**Why split the roles?**  
The owner provides business accountability and decision authority, while the steward provides operational data-management expertise. Separating these responsibilities prevents quality and access decisions from being both defined and self-audited by the same role.

## Notes and assumptions

- Quality measurements are taken on the raw dataset before cleaning.
- Missing values are not automatically imputed because the dataset contains no authoritative source for replacement values.
- Duplicate `customer_id` records are resolved by keeping the last row, explicitly assuming that later records supersede earlier ones.
- Invalid numeric values are converted to missing rather than silently clipped or guessed.
- The sensitivity labels and controls are examples of reasonable governance controls for a customer-data context.
