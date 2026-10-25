import pandas as pd

CHECKS = [
    ("inspection_id is unique",        lambda d: d["inspection_id"].is_unique),
    ("target exists and is 0/1",       lambda d: set(d["target"].dropna().unique()) <= {0, 1} and d["target"].notna().all()),
    ("inspection_date is datetime",    lambda d: pd.api.types.is_datetime64_any_dtype(d["inspection_date"])),
    ("no missing dates",               lambda d: d["inspection_date"].notna().all()),
    ("dates between 2010 and today",   lambda d: d["inspection_date"].between("2010-01-01", pd.Timestamp.today()).all()),
    ("zip is 5 digits or 'unknown'",   lambda d: d["zip"].astype(str).str.fullmatch(r"\d{5}|unknown").all()),
    ("latitude within Chicago box",    lambda d: d["latitude"].dropna().between(41.6, 42.1).all()),
    ("longitude within Chicago box",   lambda d: d["longitude"].dropna().between(-87.95, -87.5).all()),
    ("risk_level in {1,2,3}",          lambda d: d["risk_level"].isin([1, 2, 3]).all()),
    ("facility_type has no missing",   lambda d: d["facility_type"].notna().all()),
    ("facility_type is normalised",    lambda d: (d["facility_type"] == d["facility_type"].str.strip().str.lower()).all()),
    ("provenance columns present",     lambda d: all(c in d.columns for c in ["zip_src", "facility_type_src", "risk_src", "geo_src"])),
    ("at least 2000 rows",             lambda d: len(d) >= 2000),
]

def validate(df, verbose=True):
    failed = []
    for name, fn in CHECKS:
        try:
            ok = bool(fn(df))
        except Exception:
            ok = False
        if verbose:
            print(("PASS  " if ok else "FAIL  ") + name)
        if not ok:
            failed.append(name)
    if failed:
        raise AssertionError(f"{len(failed)} checks failed: {failed}")
    print("All checks passed.")
    return True