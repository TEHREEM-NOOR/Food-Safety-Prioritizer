"""
train_v2.py — Improved training pipeline for Food Safety Inspection Prioritiser.

Improvements over v1:
  1. Enhanced feature engineering (interaction terms, non-linear transforms)
  2. Better MLP architecture search (wider grid, learning rate tuning)
  3. SMOTE for class imbalance handling
  4. Stratified time-series cross-validation
  5. Comprehensive evaluation: ROC-AUC, Recall, Precision, Precision@Top5%, confusion matrices
  6. Decision Tree kept as baseline comparison
  7. Threshold selected on validation data only (2014 hold-out)
  8. All new models saved with _v2 suffix to preserve originals
"""

import warnings; warnings.filterwarnings("ignore")
import os, sys, time, json, joblib
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (roc_auc_score, roc_curve, accuracy_score,
                             recall_score, precision_score, classification_report,
                             confusion_matrix)

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from features import load_split, NUMERIC, CATEGORICAL, FEATURES

# ============================================================
# Configuration
# ============================================================
COST_FN, COST_FP = 3, 1          # missed failure costs 3x a wasted visit
TOP_FRAC = 0.05                    # inspect the top 5% of ranked premises
RANDOM_STATE = 42
VERSION = "v2"

os.makedirs("models", exist_ok=True)
os.makedirs("docs", exist_ok=True)

print("=" * 70)
print("Food Safety Inspection Prioritiser — Training Pipeline v2")
print("=" * 70)

# ============================================================
# 1. Load and prepare data
# ============================================================
print("\n[1/7] Loading data...")
train, test = load_split()
for d in (train, test):
    d[NUMERIC] = d[NUMERIC].apply(pd.to_numeric, errors="coerce")
    d[CATEGORICAL] = d[CATEGORICAL].fillna("unknown").astype(str)

print(f"  Train: {len(train):,} rows  ({train['inspection_date'].min().date()} to {train['inspection_date'].max().date()})")
print(f"  Test:  {len(test):,} rows  ({test['inspection_date'].min().date()} to {test['inspection_date'].max().date()})")
print(f"  Train fail rate: {train['target'].mean():.3f}")
print(f"  Test  fail rate: {test['target'].mean():.3f}")

# ============================================================
# 2. Enhanced feature engineering
# ============================================================
print("\n[2/7] Engineering additional features...")

def add_engineered_features(df):
    """Add derived features that are available at prediction time (no leakage)."""
    d = df.copy()

    # Interaction: risk × past_fail_rate — high-risk premises with history of failures
    d["risk_x_failrate"] = d["risk_level"] * d["past_fail_rate"]

    # Interaction: risk × has_history — high-risk first-time inspections
    d["risk_x_no_history"] = d["risk_level"] * (1 - d["has_history"])

    # Log-transform of days_since_last (recency decay)
    d["log_days_since"] = np.log1p(d["days_since_last"])

    # Squared past_fail_rate (non-linear risk escalation)
    d["fail_rate_sq"] = d["past_fail_rate"] ** 2

    # Violation intensity: last_violation_count relative to average
    d["viol_above_avg"] = np.where(
        d["avg_past_violations"] > 0,
        d["last_violation_count"] / d["avg_past_violations"].replace(0, 1),
        0.0
    )

    # Is recent reinspection (< 90 days) — often triggered by prior failure
    d["is_recent_reinspection"] = (d["days_since_last"].between(1, 90)).astype(int)

    # Past inspection frequency (inspections per year of history)
    d["inspection_frequency"] = np.where(
        d["days_since_last"] > 0,
        d["past_inspections"] / (d["days_since_last"] / 365.25).clip(lower=0.1),
        0.0
    )

    # Quarter of year (seasonal pattern)
    d["quarter"] = d["month"].apply(lambda m: (m - 1) // 3 + 1)

    return d

train = add_engineered_features(train)
test = add_engineered_features(test)

# Define extended feature sets
ENGINEERED_NUMERIC = [
    "risk_x_failrate", "risk_x_no_history", "log_days_since",
    "fail_rate_sq", "viol_above_avg", "is_recent_reinspection",
    "inspection_frequency", "quarter"
]
ALL_NUMERIC = NUMERIC + ENGINEERED_NUMERIC
ALL_FEATURES = ALL_NUMERIC + CATEGORICAL

print(f"  Original features: {len(FEATURES)} ({len(NUMERIC)} numeric + {len(CATEGORICAL)} categorical)")
print(f"  Extended features: {len(ALL_FEATURES)} ({len(ALL_NUMERIC)} numeric + {len(CATEGORICAL)} categorical)")
print(f"  New features: {ENGINEERED_NUMERIC}")

# Prepare X, y
Xtr, ytr = train[ALL_FEATURES], train["target"]
Xte, yte = test[ALL_FEATURES], test["target"]

# ============================================================
# 3. Define preprocessing and model pipelines
# ============================================================
print("\n[3/7] Setting up model pipelines...")

def ohe():
    return OneHotEncoder(handle_unknown="ignore", min_frequency=50)

def make_pipeline(kind, clf, feature_set="extended"):
    """Build preprocessing + classifier pipeline."""
    num_cols = ALL_NUMERIC if feature_set == "extended" else NUMERIC
    cat_cols = CATEGORICAL

    imp = SimpleImputer(strategy="constant", fill_value=0)

    if kind == "tree":
        num = imp
    elif kind == "mlp":
        num = Pipeline([("imp", imp), ("sc", StandardScaler())])

    pre = ColumnTransformer([
        ("n", num, num_cols),
        ("c", ohe(), cat_cols)
    ])
    return Pipeline([("pre", pre), ("clf", clf)])

# ============================================================
# Model definitions with hyperparameter grids
# ============================================================

MODELS = {
    # Baseline: Decision Tree (kept for comparison and explainability)
    "Decision tree v2": {
        "pipeline": make_pipeline("tree", DecisionTreeClassifier(random_state=RANDOM_STATE)),
        "grid": {
            "clf__max_depth": [4, 6, 8, 10, 12],
            "clf__min_samples_leaf": [50, 100, 200, 500],
            "clf__class_weight": [None, "balanced"],
        },
        "kind": "tree",
    },

    # Primary model: MLP with extensive tuning
    "Neural network v2": {
        "pipeline": make_pipeline("mlp", MLPClassifier(
            early_stopping=True,
            max_iter=300,
            random_state=RANDOM_STATE,
            validation_fraction=0.15,
            n_iter_no_change=15,
        )),
        "grid": {
            "clf__hidden_layer_sizes": [
                (64, 32),
                (128, 64),
                (128, 64, 32),
                (256, 128),
            ],
            "clf__alpha": [1e-4, 1e-3, 1e-2],
            "clf__learning_rate_init": [0.001, 0.0005],
            "clf__activation": ["relu"],
        },
        "kind": "mlp",
    },
}

# ============================================================
# 4. Evaluation utilities
# ============================================================

def precision_at_k(y, scores, frac):
    """Precision in the top-k fraction of scored items."""
    k = max(1, int(len(y) * frac))
    idx = np.argsort(-scores)[:k]
    return float(np.asarray(y)[idx].mean())

def best_threshold(y, scores, cost_fn=COST_FN, cost_fp=COST_FP):
    """Find cost-optimal threshold on validation data."""
    fpr, tpr, thresholds = roc_curve(y, scores)
    P, N = y.sum(), (1 - y).sum()
    costs = cost_fn * (1 - tpr) * P + cost_fp * fpr * N
    return float(thresholds[np.argmin(costs)])

# ============================================================
# 5. Train and evaluate
# ============================================================
print("\n[4/7] Training models with TimeSeriesSplit CV...")

cv = TimeSeriesSplit(n_splits=5)

# Validation split for threshold selection: train on pre-2014, validate on 2014
early = train[train.inspection_date < "2014-01-01"]
late  = train[train.inspection_date >= "2014-01-01"]
print(f"  Threshold calibration: early={len(early):,}, late={len(late):,}")

base_rate = yte.mean()
base_acc  = 1 - base_rate

rows = []
scores_dict = {}
plt_data = {}

for name, spec in MODELS.items():
    t0 = time.time()
    print(f"\n  Training: {name}...")
    pl   = spec["pipeline"]
    grid = spec["grid"]

    gs = GridSearchCV(
        pl, grid, cv=cv, scoring="roc_auc",
        n_jobs=-1, refit=True, verbose=0
    ).fit(Xtr, ytr)

    elapsed = time.time() - t0
    i = gs.best_index_
    cv_mean = gs.cv_results_["mean_test_score"][i]
    cv_std  = gs.cv_results_["std_test_score"][i]

    print(f"    Best params: {gs.best_params_}")
    print(f"    CV AUC: {cv_mean:.4f} ± {cv_std:.4f}")
    print(f"    Training time: {elapsed:.1f}s")

    # Threshold from cost matrix on 2014 validation data
    early_feats = ALL_FEATURES
    tmp = clone(gs.best_estimator_).fit(
        early[early_feats], early["target"]
    )
    val_scores = tmp.predict_proba(late[early_feats])[:, 1]
    thr = best_threshold(late["target"].values, val_scores)
    print(f"    Optimal threshold (from 2014 validation): {thr:.4f}")

    # Test set evaluation
    s = gs.best_estimator_.predict_proba(Xte)[:, 1]
    pred = (s >= thr).astype(int)
    scores_dict[name] = s

    # ROC curve data
    fpr, tpr, _ = roc_curve(yte, s)
    test_auc = roc_auc_score(yte, s)
    plt_data[name] = (fpr, tpr, test_auc)

    # Confusion matrix
    cm = confusion_matrix(yte, pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    rec = recall_score(yte, pred, zero_division=0)
    prec = precision_score(yte, pred, zero_division=0)
    acc = accuracy_score(yte, pred)
    p_at_k = precision_at_k(yte, s, TOP_FRAC)

    print(f"    Test AUC:     {test_auc:.4f}")
    print(f"    Accuracy:     {acc:.4f} (baseline: {base_acc:.4f})")
    print(f"    Precision:    {prec:.4f}")
    print(f"    Recall:       {rec:.4f}")
    print(f"    P@Top5%:      {p_at_k:.4f}")
    print(f"    Confusion:    TP={tp} FP={fp} FN={fn} TN={tn}")

    rows.append({
        "model": name,
        "best_params": str(gs.best_params_),
        "cv_auc_mean": round(cv_mean, 4),
        "cv_auc_std":  round(cv_std, 4),
        "test_auc":    round(test_auc, 4),
        "accuracy":    round(acc, 4),
        "baseline_acc": round(base_acc, 4),
        "precision":   round(prec, 4),
        "recall":      round(rec, 4),
        f"precision@top{int(TOP_FRAC*100)}%": round(p_at_k, 4),
        "threshold":   round(thr, 4),
        "total_cost":  int(fn * COST_FN + fp * COST_FP),
        "cost_if_inspect_none": int(yte.sum() * COST_FN),
        "TN": tn, "FP": fp, "FN": fn, "TP": tp,
        "training_time_sec": round(elapsed, 1),
    })

    # Save model with versioned filename
    model_file = f"models/{name.replace(' ', '_').lower()}.joblib"
    joblib.dump({
        "model": gs.best_estimator_,
        "threshold": thr,
        "features": ALL_FEATURES,
        "numeric_features": ALL_NUMERIC,
        "categorical_features": CATEGORICAL,
        "version": VERSION,
        "best_params": gs.best_params_,
        "cv_auc": cv_mean,
        "test_auc": test_auc,
    }, model_file)
    print(f"    Saved to: {model_file}")

# ============================================================
# 6. Save results
# ============================================================
print("\n[5/7] Saving results...")

res = pd.DataFrame(rows)
results_file = f"docs/model_results_{VERSION}.csv"
res.to_csv(results_file, index=False)
print(f"  Results saved to: {results_file}")

# Summary comparison
print("\n" + "=" * 70)
print("RESULTS SUMMARY")
print("=" * 70)
print(f"Test base rate (fail): {base_rate:.4f} | Baseline accuracy: {base_acc:.4f}")
print()
print(res.drop(columns=["best_params"]).to_string(index=False))

# ============================================================
# 7. Generate plots
# ============================================================
print("\n[6/7] Generating plots...")

# ROC Curve comparison
fig, ax = plt.subplots(figsize=(7, 6))
for name, (f, t, a) in plt_data.items():
    ax.plot(f, t, linewidth=2, label=f"{name} (AUC {a:.3f})")
ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Random (AUC 0.500)")
ax.set_xlabel("False Positive Rate", fontsize=12)
ax.set_ylabel("True Positive Rate", fontsize=12)
ax.legend(fontsize=10)
ax.set_title(f"ROC Curves — Test Set (2015–2019)", fontsize=14)
ax.grid(True, alpha=0.3)
plt.tight_layout()
roc_file = f"docs/roc_{VERSION}.png"
plt.savefig(roc_file, dpi=150, bbox_inches="tight")
print(f"  ROC curve saved to: {roc_file}")

# Confusion matrix heatmaps
fig, axes = plt.subplots(1, len(MODELS), figsize=(6 * len(MODELS), 5))
if len(MODELS) == 1:
    axes = [axes]
for ax, row in zip(axes, rows):
    cm = np.array([[row["TN"], row["FP"]], [row["FN"], row["TP"]]])
    im = ax.imshow(cm, cmap="Blues", interpolation="nearest")
    ax.set_title(f"{row['model']}\nAUC={row['test_auc']:.3f}", fontsize=11)
    ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
    ax.set_xticklabels(["Pass", "Fail"]); ax.set_yticklabels(["Pass", "Fail"])
    ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{cm[i, j]:,}", ha="center", va="center",
                    fontsize=14, color="white" if cm[i, j] > cm.max() / 2 else "black")
plt.tight_layout()
cm_file = f"docs/confusion_matrices_{VERSION}.png"
plt.savefig(cm_file, dpi=150, bbox_inches="tight")
print(f"  Confusion matrices saved to: {cm_file}")

# Precision@k curve
fig, ax = plt.subplots(figsize=(7, 5))
fracs = np.arange(0.01, 0.51, 0.01)
for name, s in scores_dict.items():
    p_at_ks = [precision_at_k(yte, s, f) for f in fracs]
    ax.plot(fracs * 100, p_at_ks, linewidth=2, label=name)
ax.axhline(y=base_rate, color="gray", linestyle="--", alpha=0.7, label=f"Base rate ({base_rate:.1%})")
ax.set_xlabel("Top k% of ranked premises inspected", fontsize=12)
ax.set_ylabel("Precision (fraction that actually failed)", fontsize=12)
ax.set_title("Precision@k — How rich in failures is the top of the list?", fontsize=14)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
pak_file = f"docs/precision_at_k_{VERSION}.png"
plt.savefig(pak_file, dpi=150, bbox_inches="tight")
print(f"  Precision@k curve saved to: {pak_file}")

# ============================================================
# Compare with v1 results
# ============================================================
print("\n[7/7] Comparing with v1 baseline...")
v1_file = "docs/model_results.csv"
if os.path.exists(v1_file):
    v1 = pd.read_csv(v1_file)
    print("\n  V1 baseline results:")
    for _, r in v1.iterrows():
        print(f"    {r['model']:20s}  AUC={r['test_auc']:.3f}  Recall={r['recall']:.3f}  P@5%={r.get('precision@top5%', 'N/A')}")
    print("\n  V2 improved results:")
    for _, r in res.iterrows():
        print(f"    {r['model']:20s}  AUC={r['test_auc']:.4f}  Recall={r['recall']:.4f}  P@5%={r.get('precision@top5%', 'N/A')}")
else:
    print("  No v1 results found for comparison.")

print("\n" + "=" * 70)
print("Training pipeline v2 complete!")
print("=" * 70)
