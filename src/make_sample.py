import os
import pandas as pd

feat = pd.read_csv("data/features.csv", parse_dates=["inspection_date"],
                   dtype={"zip": str, "license_num": str})
feat["zip"] = feat["zip"].fillna("unknown")
test = feat[feat["inspection_date"] >= "2015-01-01"]
samp = test.sample(20000, random_state=0).sort_values("inspection_date")
samp.to_csv("data/app_sample.csv", index=False)

clean = pd.read_csv("data/clean.csv", dtype=str)
ids = set(samp["inspection_id"].astype(str))
keep = clean[clean["inspection_id"].isin(ids)].drop(columns=["violations"], errors="ignore")
keep.to_csv("data/clean_sample.csv", index=False)

for f in ["data/app_sample.csv", "data/clean_sample.csv"]:
    print(f, round(os.path.getsize(f) / 1e6, 1), "MB")