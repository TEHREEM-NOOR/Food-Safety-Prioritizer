import pandas as pd
d = pd.read_csv("data/features.csv")
d["gap"] = pd.cut(d["days_since_last"], [-1, 0, 30, 90, 365, 5000],
                  labels=["no history", "<=30d", "31-90d", "91-365d", ">1yr"])
print(d.groupby("gap", observed=True)["target"].agg(["mean", "count"]).round(3))
print(d.groupby("last_result_fail")["target"].agg(["mean", "count"]).round(3))