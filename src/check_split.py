import pandas as pd
from features import load_split

train, test = load_split()
print(f"Train: {len(train)} rows, {train.inspection_date.min().date()} to {train.inspection_date.max().date()}")
print(f"Test : {len(test)} rows, {test.inspection_date.min().date()} to {test.inspection_date.max().date()}")

print("\nFail rate by year (the base rate itself may drift):")
all_df = pd.concat([train, test])
print(all_df.groupby(all_df.inspection_date.dt.year)["target"].mean().round(3).to_string())

base = 1 - test["target"].mean()
print(f"\nMajority-class baseline on TEST (always predict 'no serious violation'): {base:.3f}")

print("\nSanity check, past_fail_rate vs target (should be positive, not ~1.0):")
print(all_df[["past_fail_rate", "last_result_fail", "days_since_last", "target"]].corr()["target"].round(3).to_string())
print("\nHistory missing for first inspections:", f"{(all_df.has_history == 0).mean():.1%}")