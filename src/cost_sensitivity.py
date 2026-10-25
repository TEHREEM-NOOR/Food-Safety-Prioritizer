import sys, joblib, numpy as np, pandas as pd
sys.path.insert(0, "src")
from features import load_split, FEATURES

_, test = load_split()
y = test["target"].values
m = joblib.load("models/decision_tree.joblib")["model"]
s = m.predict_proba(test[FEATURES])[:, 1]
n_pass = int((y == 0).sum())

rows = []
for r in [2, 3, 4, 5, 10]:
    t = 1 / (1 + r)
    f = s >= t
    tp = int((f & (y == 1)).sum()); fp = int((f & (y == 0)).sum())
    fn = int(((~f) & (y == 1)).sum())
    rows.append({"FN:FP cost": f"{r}:1", "threshold": round(t, 3),
                 "share flagged": round(float(f.mean()), 3),
                 "precision": round(tp / max(f.sum(), 1), 3),
                 "recall": round(tp / y.sum(), 3),
                 "model cost": fn * r + fp,
                 "inspect-all cost": n_pass,
                 "inspect-none cost": int(y.sum() * r)})
out = pd.DataFrame(rows)
out.to_csv("docs/cost_sensitivity.csv", index=False)
print(out.to_string(index=False))