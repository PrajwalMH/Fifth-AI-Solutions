# DAY 4 TECHNICAL BYTE ASSIGNMENT
# Name: PRAJWAL MRITHYUNJAY HULAMANI
# Topic: Profile, Clean and Classify a Customer Dataset

from pathlib import Path
import warnings

warnings.filterwarnings(
    "ignore",
    message="Pyarrow will become a required dependency.*"
)

import pandas as pd

# Make the script work even when run from another folder.
BASE_DIR = Path(__file__).resolve().parent
RAW_FILE = BASE_DIR / "customer_dataset_lab.csv"
CLEAN_FILE = BASE_DIR / "customer_dataset_lab_cleaned.csv"

# ------------------------------------------------------------
# 1. PROFILE
# ------------------------------------------------------------

# Read the raw dataset.
df = pd.read_csv(RAW_FILE)

print("===== 1. DATA PROFILE =====")
print("\nDataset information:")
df.info()

print("\nMissing-value percentage by field:")
missing_pct = (df.isna().mean() * 100).round(2).sort_values(ascending=False)
print(missing_pct)

print("\nDuplicate customer IDs:")
duplicate_customer_count = df.duplicated(
    subset="customer_id",
    keep="last"
).sum()
print(duplicate_customer_count)

# ------------------------------------------------------------
# 2. CLEAN
# Record every decision and the number of affected records.
# ------------------------------------------------------------

print("\n===== 2. CLEANING =====")

# Decision 1:
# Keep the last row for a repeated customer_id.
# Assumption: later records supersede earlier records.
duplicate_count = int(
    df.duplicated(subset="customer_id", keep="last").sum()
)
df = df.drop_duplicates(subset="customer_id", keep="last")
print("Duplicate customer records removed:", duplicate_count)

# Decision 2:
# Trim spaces and lowercase email values.
# Assumption: spaces and letter case are formatting differences,
# not different email addresses.
email_before = df["email"].copy()
email_after = df["email"].astype("string").str.strip().str.lower()

email_changed_count = int(
    (email_before.astype("string") != email_after)
    .fillna(False)
    .sum()
)

df["email"] = email_after
print("Email values standardized:", email_changed_count)

# Decision 3:
# Clip negative monthly_spend values to zero.
# Assumption: negative spend is invalid in this exercise.
# IMPORTANT: count the affected rows before changing them so that
# the source-data problem is not silently hidden.
negative_spend_count = int((df["monthly_spend"] < 0).sum())
print("Negative monthly_spend values found:", negative_spend_count)

df["monthly_spend"] = df["monthly_spend"].clip(lower=0)

# Save the cleaned result.
df.to_csv(CLEAN_FILE, index=False)
print("Cleaned dataset saved as:", CLEAN_FILE.name)

# ------------------------------------------------------------
# 3. CLASSIFY EVERY FIELD
# Structure + Sensitivity + Scale
# ------------------------------------------------------------

classification = {
    "customer_id": {
        "structure": "structured",
        "sensitivity": "internal",
        "scale": "nominal"
    },
    "email": {
        "structure": "structured",
        "sensitivity": "personal",
        "scale": "nominal"
    },
    "monthly_spend": {
        "structure": "structured",
        "sensitivity": "confidential",
        "scale": "continuous"
    },
    "plan_tier": {
        "structure": "structured",
        "sensitivity": "internal",
        "scale": "ordinal"
    },
    "signup_date": {
        "structure": "structured",
        "sensitivity": "internal",
        "scale": "continuous/time"
    },
    "num_support_tickets": {
        "structure": "structured",
        "sensitivity": "internal",
        "scale": "discrete"
    },
    "satisfaction_score": {
        "structure": "structured",
        "sensitivity": "confidential",
        "scale": "ordinal"
    },
    "device_os": {
        "structure": "structured",
        "sensitivity": "internal",
        "scale": "nominal"
    },
    "data_usage_gb": {
        "structure": "structured",
        "sensitivity": "confidential",
        "scale": "continuous"
    },
    "is_active": {
        "structure": "structured",
        "sensitivity": "internal",
        "scale": "nominal"
    }
}

print("\n===== 3. FIELD CLASSIFICATION =====")

for field in df.columns:
    details = classification[field]
    print(f"\n{field}")
    print("  Structure:", details["structure"])
    print("  Sensitivity:", details["sensitivity"])
    print("  Scale:", details["scale"])

print("\n===== COMPLETE =====")
print("The dataset was profiled, cleaned and classified successfully.")
