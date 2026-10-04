# Day 4 — Data Quality and Governance Assessment

**Name:** Prajwal Mrithyunjay Hulamani

This repository folder contains my Day 4 assignment on **data quality and governance**. The task uses a customer dataset with deliberately injected defects and demonstrates quantified quality measurement, traceable cleaning decisions, sensitivity classification, practical controls, and governance ownership.

## Assignment requirements covered

1. **Raw dataset with known defects** — missing values, a duplicate customer ID, invalid email syntax, inconsistent category casing, an out-of-range age, a negative spend value, an invalid satisfaction score, and negative data usage.
2. **Quality report** — completeness, validity, and uniqueness are calculated with numeric counts and percentages.
3. **Cleaning changelog** — every cleaning action records the decision, assumption, and number of affected records.
4. **Sensitivity classification** — every field is classified and given at least one practical control.
5. **Owner and steward** — a plausible business owner and data steward are named and their responsibilities are justified.

## Files

- `day4_customers_raw.csv` — raw customer dataset containing known defects.
- `day4_data_quality_governance.py` — Python program that profiles, cleans, classifies, and documents the dataset.
- `day4_customers_cleaned.csv` — cleaned output produced by the program.
- `quality_report.md` — full quality report, cleaning changelog, sensitivity controls, and governance note.

## How to run

Keep the Python file and raw CSV in the same folder, then run:

```bash
python day4_data_quality_governance.py
```

The script creates:

```text
day4_customers_cleaned.csv
quality_report.md
```

## Key quality results

- Raw rows: **15**
- Columns: **11**
- Overall completeness: **96.97%**
- Overall validity: **95.0%**
- Customer ID uniqueness: **93.33%**
- Duplicate customer records beyond the first occurrence: **1**

## Cleaning approach

I profiled the raw data before making any changes so that defects could be measured rather than silently removed. Email values and categorical labels are standardized only when the intended meaning is clear. Invalid numeric values are converted to missing instead of being guessed. Duplicate customer IDs are resolved by keeping the last record, with the explicit assumption that later records supersede earlier ones. Remaining missing values are retained because the dataset does not provide an authoritative source for safe imputation.

## Governance note

**Dataset Owner: Customer Operations Manager**  
The owner is accountable for the dataset's business purpose, acceptable use, access approvals, and required quality level.

**Dataset Steward: Data Governance Analyst**  
The steward manages field definitions, data-quality rules, issue tracking, cleaning documentation, metadata, and implementation of controls.

This split separates **business accountability** from **day-to-day data stewardship**, which improves traceability and prevents one role from defining, executing, and self-auditing every governance decision.

## Sensitivity approach

Customer identity and contact fields such as `name`, `email`, and `age` are treated as personal information and receive stronger controls such as masking, encryption, minimization, and restricted access. Behavioral and financial-style fields such as `monthly_spend`, `satisfaction_score`, and `data_usage_gb` are treated as confidential and limited to authorized business or analytics roles. Internal operational fields use least-privilege access and logging.

## Note

This dataset is synthetic and created only for learning and demonstration purposes.
