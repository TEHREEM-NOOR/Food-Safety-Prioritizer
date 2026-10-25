import os
import pandas as pd, numpy as np
from validate import validate

RAW, OUT = "data/raw_full.csv", "data/clean.csv"

def load_raw():
    df = pd.read_csv(RAW, dtype=str)
    df.columns = [c.strip().lower().replace("#", "num").replace(" ", "_") for c in df.columns]
    return df

def count_faults(df):
    """Detect each fault and return {name: (lecture-2 category, detection expression, count)}"""
    d = pd.to_datetime(df["inspection_date"], errors="coerce")
    lat = pd.to_numeric(df["latitude"], errors="coerce")
    lon = pd.to_numeric(df["longitude"], errors="coerce")
    z = df["zip"].astype("string")
    ft = df["facility_type"].astype("string")
    return {
        "missing facility_type": ("Missing value", "facility_type.isna()", int(ft.isna().sum())),
        "missing zip": ("Missing value", "zip.isna()", int(z.isna().sum())),
        "missing/zero coordinates": ("Missing value", "latitude.isna()", int(lat.isna().sum())),
        "duplicate inspection_id": ("Duplicate data", "inspection_id.duplicated()", int(df["inspection_id"].duplicated().sum())),
        "facility_type spelling variants": ("Inconsistent values", "nunique(raw) - nunique(strip.lower)",
                                            int(ft.nunique() - ft.str.strip().str.lower().nunique())),
        "invalid zip format": ("Inconsistent values / noise", r"~zip.str.fullmatch(r'\d{5}') & zip.notna()",
                               int((~z.str.fullmatch(r"\d{5}") & z.notna()).sum())),
        "coordinates outside Chicago": ("Outlier / impossible value", "lat not in [41.6,42.1] or lon not in [-87.95,-87.5]",
                                        int((lat.notna() & ~(lat.between(41.6, 42.1) & lon.between(-87.95, -87.5))).sum())),
        "unparseable or future dates": ("Impossible value", "to_datetime fails or > today",
                                        int((d.isna() | (d > pd.Timestamp.today())).sum())),
        "invalid risk category": ("Inconsistent values", "risk not in Risk 1/2/3",
                                  int((~df["risk"].isin(["Risk 1 (High)", "Risk 2 (Medium)", "Risk 3 (Low)"])).sum())),
        "non-informative outcomes": ("Irrelevant data", "results not in Pass/Fail/Pass w/ Conditions",
                                     int((~df["results"].str.lower().isin(["pass", "fail", "pass w/ conditions"])).sum())),
    }

def clean(df):
    df = df.copy()
    # duplicates
    df = df.drop_duplicates("inspection_id", keep="first")

    # dates
    df["inspection_date"] = pd.to_datetime(df["inspection_date"], errors="coerce")
    df = df[df["inspection_date"].notna() & (df["inspection_date"] <= pd.Timestamp.today())]

    # target: keep only informative outcomes
    r = df["results"].str.strip().str.lower()
    df = df[r.isin(["pass", "fail", "pass w/ conditions"])].copy()
    df["target"] = (r[df.index] == "fail").astype(int)

    # facility_type
    df["facility_type_src"] = np.where(df["facility_type"].isna(), "imputed_unknown",
                              np.where(df["facility_type"] != df["facility_type"].str.strip().str.lower(), "normalised", "original"))
    df["facility_type"] = df["facility_type"].fillna("unknown").str.strip().str.lower()

    # risk -> ordinal 1 (high) .. 3 (low)
    m = {"Risk 1 (High)": 1, "Risk 2 (Medium)": 2, "Risk 3 (Low)": 3}
    df["risk_level"] = df["risk"].map(m)
    df["risk_src"] = np.where(df["risk_level"].isna(), "imputed_mode_by_facility", "original")
    mode_by_ft = df.groupby("facility_type")["risk_level"].agg(lambda s: s.mode().iloc[0] if s.notna().any() else np.nan)
    df["risk_level"] = df["risk_level"].fillna(df["facility_type"].map(mode_by_ft)).fillna(1).astype(int)

    # zip
    z = df["zip"].astype("string").str.strip().str[:5]
    valid = z.str.fullmatch(r"\d{5}").fillna(False)
    df["zip_src"] = np.where(valid & (df["zip"] == z), "original", "repaired")
    z = z.where(valid)
    by_lic = df.assign(z=z).groupby("license_num")["z"].agg(lambda s: s.mode().iloc[0] if s.notna().any() else np.nan)
    z = z.fillna(df["license_num"].map(by_lic)).fillna("unknown")
    df["zip"] = z.astype(str)

    # coordinates
    lat = pd.to_numeric(df["latitude"], errors="coerce")
    lon = pd.to_numeric(df["longitude"], errors="coerce")
    ok = lat.between(41.6, 42.1) & lon.between(-87.95, -87.5)
    lat, lon = lat.where(ok), lon.where(ok)
    df["geo_src"] = np.where(ok, "original", "imputed_premises_median")
    g = df.assign(lat=lat, lon=lon).groupby("license_num")[["lat", "lon"]].transform("median")
    df["latitude"], df["longitude"] = lat.fillna(g["lat"]), lon.fillna(g["lon"])
    df["geo_src"] = np.where(df["latitude"].isna(), "missing", df["geo_src"])
    df["latitude"] = df["latitude"].fillna(df["latitude"].median())
    df["longitude"] = df["longitude"].fillna(df["longitude"].median())

    # name tidy
    df["dba_name"] = df["dba_name"].str.strip().str.title()
    return df.sort_values("inspection_date").reset_index(drop=True)

if __name__ == "__main__":
    os.makedirs("docs", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    raw = load_raw()
    before = count_faults(raw)

    print("=== validate(RAW) - should FAIL ===")
    try:
        validate(raw)
    except AssertionError as e:
        print("Raw failed as expected:", e)

    cleaned = clean(raw)
    # after-repair counts (same detectors on the cleaned columns where meaningful)
    after = {
        "missing facility_type": int(cleaned["facility_type"].isna().sum()),
        "missing zip": int((cleaned["zip"] == "unknown").sum()),
        "missing/zero coordinates": int((cleaned["geo_src"] == "missing").sum()),
        "duplicate inspection_id": int(cleaned["inspection_id"].duplicated().sum()),
        "facility_type spelling variants": int(cleaned["facility_type"].nunique() - cleaned["facility_type"].str.strip().str.lower().nunique()),
        "invalid zip format": int((~cleaned["zip"].str.fullmatch(r"\d{5}|unknown")).sum()),
        "coordinates outside Chicago": int((~(cleaned["latitude"].between(41.6, 42.1) & cleaned["longitude"].between(-87.95, -87.5))).sum()),
        "unparseable or future dates": int((cleaned["inspection_date"] > pd.Timestamp.today()).sum()),
        "invalid risk category": int((~cleaned["risk_level"].isin([1, 2, 3])).sum()),
        "non-informative outcomes": 0,
    }
    rows = [dict(fault=k, category=v[0], detection=v[1], count_before=v[2], count_after=after[k]) for k, v in before.items()]
    audit = pd.DataFrame(rows)
    audit.to_csv("docs/audit_report.csv", index=False)
    print("\n", audit[["fault", "count_before", "count_after"]].to_string(index=False))

    print("\n=== validate(CLEAN) - should PASS ===")
    validate(cleaned)
    cleaned.to_csv(OUT, index=False)
    print(f"\nSaved {len(cleaned)} rows to {OUT}")
    print("Target balance:\n", cleaned["target"].value_counts(normalize=True))
    print("Years:\n", cleaned["inspection_date"].dt.year.value_counts().sort_index())