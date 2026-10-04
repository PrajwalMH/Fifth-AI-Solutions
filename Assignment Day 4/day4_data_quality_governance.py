# DAY 4 ASSIGNMENT
# Name: PRAJWAL MRITHYUNJAY HULAMANI
# Topic: Data Quality and Governance Assessment
#
# Keep this file in the same folder as day4_customers_raw.csv.
# Running it creates:
#   1. day4_customers_cleaned.csv
#   2. quality_report.md

import warnings
warnings.filterwarnings(
    "ignore",
    message="Pyarrow will become a required dependency.*"
)

from pathlib import Path
import re
import pandas as pd
import numpy as np

RAW_FILE = Path("day4_customers_raw.csv")
CLEAN_FILE = Path("day4_customers_cleaned.csv")
REPORT_FILE = Path("quality_report.md")

ALLOWED_PLAN_TIERS = {"Basic", "Standard", "Premium"}
ALLOWED_DEVICE_OS = {"iOS", "Android", "Windows", "macOS"}

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CUSTOMER_ID_PATTERN = re.compile(r"^C\d{3}$")


def pct(part, whole):
    return round((part / whole * 100), 2) if whole else 0.0


def profile_quality(df):
    """Measure completeness, validity and uniqueness on the RAW dataset."""
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = int(df.isna().sum().sum())
    present_cells = total_cells - missing_cells

    completeness = pd.DataFrame({
        "missing_count": df.isna().sum(),
        "missing_percent": (df.isna().mean() * 100).round(2),
        "complete_percent": ((1 - df.isna().mean()) * 100).round(2)
    })

    nonmissing = df.notna().sum().astype(int)

    # Validity checks are applied to non-missing values.
    invalid = {}

    invalid["customer_id"] = int(
        (~df["customer_id"].fillna("").astype(str).str.match(r"^C\d{3}$")).sum()
        - df["customer_id"].isna().sum()
    )

    invalid["name"] = int(
        (df["name"].notna() & (df["name"].astype(str).str.strip() == "")).sum()
    )

    invalid["email"] = int(
        df["email"].dropna().astype(str).apply(
            lambda x: not bool(EMAIL_PATTERN.match(x.strip()))
        ).sum()
    )

    invalid["age"] = int(
        (df["age"].notna() & ~df["age"].between(18, 100)).sum()
    )

    invalid["monthly_spend"] = int(
        (df["monthly_spend"].notna() & (df["monthly_spend"] < 0)).sum()
    )

    invalid["plan_tier"] = int(
        (df["plan_tier"].notna() & ~df["plan_tier"].isin(ALLOWED_PLAN_TIERS)).sum()
    )

    parsed_dates = pd.to_datetime(df["signup_date"], errors="coerce")
    invalid["signup_date"] = int(
        (df["signup_date"].notna() & parsed_dates.isna()).sum()
    )

    invalid["satisfaction_score"] = int(
        (df["satisfaction_score"].notna()
         & ~df["satisfaction_score"].between(1, 5)).sum()
    )

    invalid["device_os"] = int(
        (df["device_os"].notna() & ~df["device_os"].isin(ALLOWED_DEVICE_OS)).sum()
    )

    invalid["data_usage_gb"] = int(
        (df["data_usage_gb"].notna() & (df["data_usage_gb"] < 0)).sum()
    )

    invalid["is_active"] = int(
        (df["is_active"].notna()
         & ~df["is_active"].isin([True, False])).sum()
    )

    validity_rows = []
    for col in df.columns:
        nm = int(nonmissing[col])
        bad = int(invalid[col])
        validity_rows.append({
            "field": col,
            "non_missing": nm,
            "invalid_count": bad,
            "validity_percent": pct(nm - bad, nm)
        })
    validity = pd.DataFrame(validity_rows).set_index("field")

    duplicate_id_rows = int(df.duplicated(subset="customer_id", keep=False).sum())
    duplicate_ids_beyond_first = int(df.duplicated(subset="customer_id", keep="first").sum())
    unique_customer_ids = int(df["customer_id"].nunique(dropna=True))

    overall = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "total_cells": int(total_cells),
        "missing_cells": int(missing_cells),
        "overall_completeness_percent": pct(present_cells, total_cells),
        "invalid_nonmissing_values": int(validity["invalid_count"].sum()),
        "overall_validity_percent": pct(
            int(validity["non_missing"].sum() - validity["invalid_count"].sum()),
            int(validity["non_missing"].sum())
        ),
        "unique_customer_ids": unique_customer_ids,
        "customer_id_uniqueness_percent": pct(unique_customer_ids, len(df)),
        "duplicate_id_rows": duplicate_id_rows,
        "duplicate_ids_beyond_first": duplicate_ids_beyond_first,
    }

    return overall, completeness, validity


def clean_data(df):
    """Clean data while recording every decision and number of affected records."""
    out = df.copy()
    changelog = []

    # Normalize email formatting.
    before = out["email"].copy()
    normalized = out["email"].astype("string").str.strip().str.lower()
    changed = int((before.astype("string") != normalized).fillna(False).sum())
    out["email"] = normalized
    changelog.append({
        "decision": "Trim whitespace and lowercase email values",
        "assumption": "Leading/trailing spaces and letter case are formatting differences, not different addresses.",
        "records_affected": changed,
    })

    # Standardize plan tier casing.
    plan_map = {"basic": "Basic", "standard": "Standard", "premium": "Premium"}
    before = out["plan_tier"].copy()
    normalized = out["plan_tier"].astype("string").str.strip().str.lower().map(plan_map)
    changed = int((before.astype("string") != normalized.astype("string")).fillna(False).sum())
    out["plan_tier"] = normalized
    changelog.append({
        "decision": "Standardize plan_tier values to Basic, Standard or Premium",
        "assumption": "Case differences represent the same business category.",
        "records_affected": changed,
    })

    # Standardize device OS labels.
    os_map = {"ios": "iOS", "android": "Android", "windows": "Windows", "macos": "macOS"}
    before = out["device_os"].copy()
    normalized = out["device_os"].astype("string").str.strip().str.lower().map(os_map)
    changed = int((before.astype("string") != normalized.astype("string")).fillna(False).sum())
    out["device_os"] = normalized
    changelog.append({
        "decision": "Standardize device_os labels",
        "assumption": "Case differences represent the same operating system.",
        "records_affected": changed,
    })

    # Invalid emails -> missing because we cannot safely reconstruct them.
    invalid_email_mask = out["email"].notna() & ~out["email"].astype(str).str.match(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )
    affected = int(invalid_email_mask.sum())
    out.loc[invalid_email_mask, "email"] = pd.NA
    changelog.append({
        "decision": "Replace invalid email syntax with missing value",
        "assumption": "An invalid address cannot be corrected reliably without an authoritative source.",
        "records_affected": affected,
    })

    # Invalid age -> missing.
    invalid_age = out["age"].notna() & ~out["age"].between(18, 100)
    affected = int(invalid_age.sum())
    out.loc[invalid_age, "age"] = np.nan
    changelog.append({
        "decision": "Replace age outside 18-100 with missing value",
        "assumption": "The out-of-range value is treated as a data-entry error and is not guessed.",
        "records_affected": affected,
    })

    # Negative spend -> missing.
    negative_spend = out["monthly_spend"].notna() & (out["monthly_spend"] < 0)
    affected = int(negative_spend.sum())
    out.loc[negative_spend, "monthly_spend"] = np.nan
    changelog.append({
        "decision": "Replace negative monthly_spend with missing value",
        "assumption": "Customer spending cannot be negative in this dataset and the true value is unknown.",
        "records_affected": affected,
    })

    # Satisfaction outside 1-5 -> missing.
    bad_score = out["satisfaction_score"].notna() & ~out["satisfaction_score"].between(1, 5)
    affected = int(bad_score.sum())
    out.loc[bad_score, "satisfaction_score"] = np.nan
    changelog.append({
        "decision": "Replace satisfaction_score outside 1-5 with missing value",
        "assumption": "The survey scale is defined as 1 through 5.",
        "records_affected": affected,
    })

    # Negative usage -> missing.
    negative_usage = out["data_usage_gb"].notna() & (out["data_usage_gb"] < 0)
    affected = int(negative_usage.sum())
    out.loc[negative_usage, "data_usage_gb"] = np.nan
    changelog.append({
        "decision": "Replace negative data_usage_gb with missing value",
        "assumption": "Usage cannot be negative and the true amount is unknown.",
        "records_affected": affected,
    })

    # Remove duplicate customer IDs, keeping the later row.
    duplicate_beyond_first = int(out.duplicated(subset="customer_id", keep="last").sum())
    out = out.drop_duplicates(subset="customer_id", keep="last").copy()
    changelog.append({
        "decision": "Remove duplicate customer_id records and keep the last row",
        "assumption": "Later records supersede earlier records for the same customer.",
        "records_affected": duplicate_beyond_first,
    })

    # Parse date after duplicate removal.
    out["signup_date"] = pd.to_datetime(out["signup_date"], errors="coerce").dt.strftime("%Y-%m-%d")

    # Existing missing values are intentionally not imputed.
    remaining_missing = int(out.isna().sum().sum())
    changelog.append({
        "decision": "Leave unresolved missing values as missing",
        "assumption": "No authoritative source is available, so inventing replacement values would reduce data integrity.",
        "records_affected": remaining_missing,
    })

    return out, pd.DataFrame(changelog)


def sensitivity_table():
    """Classify every field and assign one practical control."""
    data = [
        ["customer_id", "Internal", "Role-based access control (RBAC) and access logging"],
        ["name", "Personal", "Encrypt at rest and mask in non-production environments"],
        ["email", "Personal", "Mask in reports and restrict access to approved roles"],
        ["age", "Personal", "Use age bands for analytics where exact age is unnecessary"],
        ["monthly_spend", "Confidential", "Restrict to finance/customer-analytics roles"],
        ["plan_tier", "Internal", "RBAC; expose only to teams with a business need"],
        ["signup_date", "Internal", "Restrict bulk exports and log access"],
        ["satisfaction_score", "Confidential", "Report in aggregate where possible"],
        ["device_os", "Internal", "Least-privilege analytics access"],
        ["data_usage_gb", "Confidential", "Restrict behavioral-usage data to authorized analytics roles"],
        ["is_active", "Internal", "RBAC and access logging"],
    ]
    return pd.DataFrame(data, columns=["field", "sensitivity", "control"])


def markdown_table(df):
    """Create a simple GitHub-compatible Markdown table without extra packages."""
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(str(c) for c in cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for _, row in df.iterrows():
        vals = []
        for c in cols:
            v = row[c]
            if pd.isna(v):
                v = ""
            vals.append(str(v).replace("|", "\\|"))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def build_report(overall, completeness, validity, changelog, sensitivity):
    completeness_out = completeness.reset_index().rename(columns={"index": "field"})
    validity_out = validity.reset_index()

    owner_steward = """
## Governance owner and steward

**Dataset Owner: Customer Operations Manager**

The owner is accountable for why the customer dataset exists, which business uses are permitted, who should receive access, and the quality level required for operational decisions.

**Dataset Steward: Data Governance Analyst**

The steward manages the day-to-day definitions, quality rules, issue tracking, cleaning documentation, metadata, and control implementation.

**Why split the roles?**  
The owner provides business accountability and decision authority, while the steward provides operational data-management expertise. Separating these responsibilities prevents quality and access decisions from being both defined and self-audited by the same role.
""".strip()

    report = f"""# Day 4 — Data Quality and Governance Assessment

**Name:** Prajwal Mrithyunjay Hulamani

## 1. Quality report

### Dataset summary

- Raw rows: **{overall['rows']}**
- Columns: **{overall['columns']}**
- Overall completeness: **{overall['overall_completeness_percent']}%**
- Overall validity across non-missing values: **{overall['overall_validity_percent']}%**
- Unique customer IDs: **{overall['unique_customer_ids']}**
- Customer ID uniqueness: **{overall['customer_id_uniqueness_percent']}%**
- Rows involved in duplicate customer IDs: **{overall['duplicate_id_rows']}**
- Duplicate customer records beyond the first occurrence: **{overall['duplicate_ids_beyond_first']}**

### Completeness by field

{markdown_table(completeness_out)}

### Validity by field

{markdown_table(validity_out)}

## 2. Cleaning changelog

{markdown_table(changelog)}

## 3. Sensitivity classification and controls

{markdown_table(sensitivity)}

{owner_steward}

## Notes and assumptions

- Quality measurements are taken on the raw dataset before cleaning.
- Missing values are not automatically imputed because the dataset contains no authoritative source for replacement values.
- Duplicate `customer_id` records are resolved by keeping the last row, explicitly assuming that later records supersede earlier ones.
- Invalid numeric values are converted to missing rather than silently clipped or guessed.
- The sensitivity labels and controls are examples of reasonable governance controls for a customer-data context.
"""
    return report


def main():
    df = pd.read_csv(RAW_FILE)

    overall, completeness, validity = profile_quality(df)
    cleaned, changelog = clean_data(df)
    sensitivity = sensitivity_table()

    cleaned.to_csv(CLEAN_FILE, index=False)
    report = build_report(overall, completeness, validity, changelog, sensitivity)
    REPORT_FILE.write_text(report, encoding="utf-8")

    print("===== DAY 4 DATA QUALITY & GOVERNANCE ASSESSMENT =====")
    print(f"Raw rows: {overall['rows']}")
    print(f"Overall completeness: {overall['overall_completeness_percent']}%")
    print(f"Overall validity: {overall['overall_validity_percent']}%")
    print(f"Customer ID uniqueness: {overall['customer_id_uniqueness_percent']}%")
    print(f"Cleaned rows: {len(cleaned)}")
    print()
    print("Created:")
    print(f"  - {CLEAN_FILE}")
    print(f"  - {REPORT_FILE}")


if __name__ == "__main__":
    main()
