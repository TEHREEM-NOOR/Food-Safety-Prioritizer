
import warnings; warnings.filterwarnings("ignore")
import os, joblib, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, KBinsDiscretizer
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import roc_auc_score, roc_curve, accuracy_score, recall_score, precision_score
from features import load_split, NUMERIC, CATEGORICAL, FEATURES

COST_FN, COST_FP = 3, 1  # missing a failing premises costs 3x a wasted visit (editable in the app)
TOP_FRAC = 0.05               # "capacity": inspect the top 5% of ranked premises

os.makedirs("models", exist_ok=True); os.makedirs("docs", exist_ok=True)
train, test = load_split()
for d in (train, test):
    d[NUMERIC] = d[NUMERIC].apply(pd.to_numeric, errors="coerce")
    d[CATEGORICAL] = d[CATEGORICAL].fillna("unknown").astype(str)
Xtr, ytr, Xte, yte = train[FEATURES], train["target"], test[FEATURES], test["target"]

def ohe(): return OneHotEncoder(handle_unknown="ignore", min_frequency=50)

def pipe(kind, clf):
    imp = SimpleImputer(strategy="constant", fill_value=0)   # safety net: no NaN can reach any model
    if kind == "tree": num = imp
    if kind == "nb":   num = Pipeline([("imp", imp), ("bin", KBinsDiscretizer(n_bins=5, encode="onehot", strategy="quantile"))])
    if kind == "mlp":  num = Pipeline([("imp", imp), ("sc", StandardScaler())])
    pre = ColumnTransformer([("n", num, NUMERIC), ("c", ohe(), CATEGORICAL)])
    return Pipeline([("pre", pre), ("clf", clf)])

MODELS = {
    "Decision tree": (pipe("tree", DecisionTreeClassifier(random_state=0)),
        {"clf__max_depth": [4, 6, 8, 12], "clf__min_samples_leaf": [50, 200, 500]}),
    "Naive Bayes": (pipe("nb", BernoulliNB()),
        {"clf__alpha": [0.1, 1.0, 5.0]}),
    "Neural network": (pipe("mlp", MLPClassifier(early_stopping=True, max_iter=200, random_state=0)),
        {"clf__hidden_layer_sizes": [(32,), (64, 32)], "clf__alpha": [1e-4, 1e-2]}),
}

def precision_at_k(y, s, frac):
    k = int(len(y) * frac); idx = np.argsort(-s)[:k]
    return float(np.asarray(y)[idx].mean())

def best_threshold(y, s):
    fpr, tpr, thr = roc_curve(y, s)
    P, N = y.sum(), (1 - y).sum()
    cost = COST_FN * (1 - tpr) * P + COST_FP * fpr * N
    return float(thr[np.argmin(cost)])

cv = TimeSeriesSplit(n_splits=5)            # time-ordered folds: always train on past, validate on future
early, late = train[train.inspection_date < "2014-01-01"], train[train.inspection_date >= "2014-01-01"]
base = 1 - yte.mean()
rows, scores, plt_data = [], {}, {}

for name, (pl, grid) in MODELS.items():
    print("Tuning", name, "...")
    gs = GridSearchCV(pl, grid, cv=cv, scoring="roc_auc", n_jobs=-1, refit=True).fit(Xtr, ytr)
    i = gs.best_index_
    cv_mean, cv_std = gs.cv_results_["mean_test_score"][i], gs.cv_results_["std_test_score"][i]

    # threshold chosen from the cost matrix on 2014 (validation), never on test
    tmp = clone(gs.best_estimator_).fit(early[FEATURES], early["target"])
    thr = best_threshold(late["target"].values, tmp.predict_proba(late[FEATURES])[:, 1])

    s = gs.best_estimator_.predict_proba(Xte)[:, 1]
    pred = (s >= thr).astype(int)
    fpr, tpr, _ = roc_curve(yte, s)
    plt_data[name] = (fpr, tpr, roc_auc_score(yte, s))
    tn_fp_fn_tp = pd.crosstab(yte, pred).reindex(index=[0, 1], columns=[0, 1], fill_value=0).values.ravel()
    tn, fp, fn, tp = tn_fp_fn_tp
    rows.append({"model": name, "best_params": str(gs.best_params_),
        "cv_auc_mean": round(cv_mean, 3), "cv_auc_std": round(cv_std, 3),
        "test_auc": round(roc_auc_score(yte, s), 3),
        "accuracy": round(accuracy_score(yte, pred), 3), "baseline_acc": round(base, 3),
        "precision": round(precision_score(yte, pred, zero_division=0), 3),
        "recall": round(recall_score(yte, pred), 3),
        f"precision@top{int(TOP_FRAC*100)}%": round(precision_at_k(yte, s, TOP_FRAC), 3),
        "threshold": round(thr, 3), "total_cost": int(fn * COST_FN + fp * COST_FP),
        "cost_if_inspect_none": int(yte.sum() * COST_FN), "TN": tn, "FP": fp, "FN": fn, "TP": tp})
    joblib.dump({"model": gs.best_estimator_, "threshold": thr}, f"models/{name.replace(' ', '_').lower()}.joblib")

res = pd.DataFrame(rows); res.to_csv("docs/model_results.csv", index=False)
print("\nTest base rate (fail):", round(yte.mean(), 3), "| baseline accuracy:", round(base, 3))
print(res.drop(columns=["best_params"]).T.to_string())

plt.figure(figsize=(6, 5))
for n, (f, t, a) in plt_data.items(): plt.plot(f, t, label=f"{n} (AUC {a:.3f})")
plt.plot([0, 1], [0, 1], "k--", label="Random (AUC 0.5)")
plt.xlabel("False positive rate"); plt.ylabel("True positive rate"); plt.legend(); plt.title("ROC on test (2015-2019)")
plt.savefig("docs/roc.png", dpi=120, bbox_inches="tight")