import sys, warnings, joblib, numpy as np, pandas as pd, matplotlib
warnings.filterwarnings("ignore"); matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.metrics import roc_auc_score
sys.path.insert(0, "src")
from features import FEATURES, CATEGORICAL, OUT

df = pd.read_csv(OUT, parse_dates=["inspection_date"], dtype={"zip": str})
df[CATEGORICAL] = df[CATEGORICAL].fillna("unknown").astype(str)
template = joblib.load("models/decision_tree.joblib")["model"]     # same tuned settings as the final model

def p_at_k(y, s, frac=0.05):
    k = int(len(y) * frac); return float(np.asarray(y)[np.argsort(-s)[:k]].mean())

TRAIN_END = pd.Timestamp("2013-01-01")
train = df[df.inspection_date < TRAIN_END]
fixed = clone(template).fit(train[FEATURES], train["target"])

rows = []
for year in range(2013, 2020):
    for h in (0, 1):
        start = pd.Timestamp(year, 1 + 6 * h, 1)
        end = start + pd.DateOffset(months=6)
        te = df[(df.inspection_date >= start) & (df.inspection_date < end)]
        if len(te) < 2000: continue
        gap_m = round(((start + (end - start) / 2) - TRAIN_END).days / 30.4, 1)
        s_fixed = fixed.predict_proba(te[FEATURES])[:, 1]
        # rolling retrain: always the 3 years immediately before the test period
        win = df[(df.inspection_date >= start - pd.DateOffset(years=3)) & (df.inspection_date < start)]
        roll = clone(template).fit(win[FEATURES], win["target"])
        s_roll = roll.predict_proba(te[FEATURES])[:, 1]
        rows.append({"period": f"{year}H{h+1}", "gap_months": gap_m, "n": len(te),
                     "base_rate": round(te.target.mean(), 3),
                     "auc_fixed_2010_12": round(roc_auc_score(te.target, s_fixed), 3),
                     "auc_retrained": round(roc_auc_score(te.target, s_roll), 3),
                     "p@5%_fixed": round(p_at_k(te.target, s_fixed), 3),
                     "p@5%_retrained": round(p_at_k(te.target, s_roll), 3)})

res = pd.DataFrame(rows); res.to_csv("docs/drift_results.csv", index=False)
print(res.to_string(index=False))

slope = np.polyfit(res.gap_months, res.auc_fixed_2010_12, 1)[0] * 12
print(f"\nTrend of the FIXED model: {slope:+.4f} AUC per year of gap")
first = res.auc_fixed_2010_12.iloc[0]
bad = res[res.auc_fixed_2010_12 < first - 0.02]
print("First period where the fixed model is >0.02 AUC below its first period:",
      bad.period.iloc[0] if len(bad) else "none in the record")
print("Mean AUC fixed:", round(res.auc_fixed_2010_12.mean(), 3), "| retrained:", round(res.auc_retrained.mean(), 3))

plt.figure(figsize=(7, 4.5))
plt.plot(res.gap_months, res.auc_fixed_2010_12, "o-", label="Trained once (2010-2012)")
plt.plot(res.gap_months, res.auc_retrained, "s--", label="Retrained on previous 3 years")
plt.xlabel("Months between end of training data and period predicted"); plt.ylabel("Test AUC")
plt.title("Concept drift: AUC vs training gap"); plt.legend(); plt.grid(alpha=.3)
plt.savefig("docs/drift.png", dpi=120, bbox_inches="tight")