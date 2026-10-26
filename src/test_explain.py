import sys, joblib, pandas as pd, numpy as np
try:
    import sklearn.compose._column_transformer as _ct
    if not hasattr(_ct, "_RemainderColsList"):
        class _RemainderColsList(list): pass
        _ct._RemainderColsList = _RemainderColsList
    from sklearn.impute import SimpleImputer
    if not hasattr(SimpleImputer, "_fill_dtype"):
        SimpleImputer._fill_dtype = property(
            lambda self: getattr(self, "_fit_dtype", getattr(self, "statistics_", np.array([0.0])).dtype)
        )
except Exception:
    pass
sys.path.insert(0, "src")
from features import load_split, FEATURES
from explain import explain
_, test = load_split()
m = joblib.load("models/decision_tree.joblib")["model"]
row = test.iloc[[0]]
print("Risk:", m.predict_proba(row[FEATURES])[0, 1])
for r in explain(m, row): print(" -", r)