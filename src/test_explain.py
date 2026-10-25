import sys, joblib, pandas as pd
sys.path.insert(0, "src")
from features import load_split, FEATURES
from explain import explain
_, test = load_split()
m = joblib.load("models/decision_tree.joblib")["model"]
row = test.iloc[[0]]
print("Risk:", m.predict_proba(row[FEATURES])[0, 1])
for r in explain(m, row): print(" -", r)