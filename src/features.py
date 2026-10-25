import pandas as pd, numpy as np

IN, OUT = "data/clean.csv", "data/features.csv"
SPLIT_DATE = pd.Timestamp("2015-01-01")   # train: 2010-2014, test: 2015-2019

NUMERIC = ["risk_level", "latitude", "longitude", "month",
           "past_inspections", "past_fails", "past_fail_rate",
           "last_result_fail", "days_since_last", "has_history",
           "last_violation_count", "avg_past_violations"]
CATEGORICAL = ["facility_group", "zip"]
FEATURES = NUMERIC + CATEGORICAL

def count_violations(s):
    return 0 if (pd.isna(s) or s == "") else s.count("|") + 1

def build_features(df):
    df = df.copy()
    df["inspection_date"] = pd.to_datetime(df["inspection_date"])

        # rows with no licence number: treat each as its own premises (no history) so groupby does not drop them
    bad = df["license_num"].isna() | df["license_num"].astype(str).str.strip().isin(["", "0", "nan"])
    df.loc[bad, "license_num"] = "nolic_" + df.loc[bad, "inspection_id"].astype(str)

    # premises = license_num; order strictly by time within each premises
    df = df.sort_values(["license_num", "inspection_date", "inspection_id"]).reset_index(drop=True)

    df["n_viol"] = df["violations"].apply(count_violations)   # used ONLY after shifting
    g = df.groupby("license_num", sort=False)

    df["past_inspections"] = g.cumcount()                      # earlier inspections only
    df["past_fails"] = g["target"].cumsum() - df["target"]     # earlier fails only
    df["past_fail_rate"] = np.where(df["past_inspections"] > 0,
                                    df["past_fails"] / df["past_inspections"].replace(0, 1), 0.0)
    df["has_history"] = (df["past_inspections"] > 0).astype(int)
    df["last_result_fail"] = g["target"].shift(1).fillna(0).astype(int)

    prev_date = g["inspection_date"].shift(1)
    df["days_since_last"] = (df["inspection_date"] - prev_date).dt.days.fillna(0)

    df["last_violation_count"] = g["n_viol"].shift(1).fillna(0)
    past_viol_total = g["n_viol"].cumsum() - df["n_viol"]
    df["avg_past_violations"] = np.where(df["past_inspections"] > 0,
                                         past_viol_total / df["past_inspections"].replace(0, 1), 0.0)

    df["month"] = df["inspection_date"].dt.month
    top = df["facility_type"].value_counts().head(12).index
    df["facility_group"] = df["facility_type"].where(df["facility_type"].isin(top), "other")
    df[NUMERIC] = df[NUMERIC].apply(pd.to_numeric, errors="coerce").fillna(0)
    
    keep = ["inspection_id", "inspection_date", "license_num", "dba_name", "address"] + FEATURES + ["target"]
    return df[keep].sort_values("inspection_date").reset_index(drop=True)

def load_split(path=OUT):
    """Time split: returns train (< 2015) and test (>= 2015). Never random."""
    df = pd.read_csv(path, parse_dates=["inspection_date"], dtype={"zip": str})
    return df[df["inspection_date"] < SPLIT_DATE].copy(), df[df["inspection_date"] >= SPLIT_DATE].copy()

if __name__ == "__main__":
    clean = pd.read_csv(IN, dtype={"zip": str, "license_num": str})
    feats = build_features(clean)
    feats.to_csv(OUT, index=False)
    print("Saved", feats.shape, "to", OUT)