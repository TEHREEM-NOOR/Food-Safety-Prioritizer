import sys, warnings, joblib, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "src")
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from features import load_split, NUMERIC, CATEGORICAL, FEATURES

train, test = load_split()
for d in (train, test):
    d[NUMERIC] = d[NUMERIC].apply(pd.to_numeric, errors="coerce")
    d[CATEGORICAL] = d[CATEGORICAL].fillna("unknown").astype(str)

best = joblib.load("models/decision_tree.joblib")["model"].named_steps["clf"]
def tree(): return DecisionTreeClassifier(max_depth=best.max_depth, min_samples_leaf=best.min_samples_leaf, random_state=0)
def ohe(): return OneHotEncoder(handle_unknown="ignore", min_frequency=50)
imp = SimpleImputer(strategy="constant", fill_value=0)

variants = {
 "All features": Pipeline([("pre", ColumnTransformer([("n", imp, NUMERIC), ("c", ohe(), CATEGORICAL)])), ("clf", tree())]),
 "Feature selection (top 15 by ANOVA F)": Pipeline([("pre", ColumnTransformer([("n", imp, NUMERIC), ("c", ohe(), CATEGORICAL)])),
                                                    ("sel", SelectKBest(f_classif, k=15)), ("clf", tree())]),
 "PCA (6 components on numeric)": Pipeline([("pre", ColumnTransformer([("n", Pipeline([("i", imp), ("s", StandardScaler()), ("p", PCA(6))]), NUMERIC),
                                                                       ("c", ohe(), CATEGORICAL)])), ("clf", tree())]),
}
cv = TimeSeriesSplit(n_splits=5)
rows = []
for name, p in variants.items():
    sc = cross_val_score(p, train[FEATURES], train["target"], cv=cv, scoring="roc_auc")
    fit = clone(p).fit(train[FEATURES], train["target"])
    rows.append({"variant": name, "cv_auc_mean": round(sc.mean(), 3), "cv_auc_std": round(sc.std(), 3),
                 "test_auc": round(roc_auc_score(test["target"], fit.predict_proba(test[FEATURES])[:, 1]), 3)})
out = pd.DataFrame(rows); out.to_csv("docs/reduction_comparison.csv", index=False)
print(out.to_string(index=False))