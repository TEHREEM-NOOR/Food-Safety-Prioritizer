import os, sys, html
from datetime import date, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
import numpy as np, pandas as pd, joblib, streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, roc_auc_score
from features import FEATURES, NUMERIC, CATEGORICAL
from explain import explain

BASE = os.path.dirname(os.path.abspath(__file__))
def P(*a): return os.path.join(BASE, *a)

MODEL_FILES = {"Decision tree": "decision_tree", "Naive Bayes": "naive_bayes", "Neural network": "neural_network"}
EXPLAIN_MODEL = "Decision tree"
st.set_page_config(page_title="Food Safety Inspection Prioritiser", layout="wide")

# ---------- loaders ----------
@st.cache_resource
def load_models():
    out = {}
    for name, f in MODEL_FILES.items():
        d = joblib.load(P("models", f + ".joblib"))
        out[name] = (d["model"], float(d["threshold"]))
    return out

@st.cache_data
def load_sample():
    return pd.read_csv(P("data", "app_sample.csv"), parse_dates=["inspection_date"],
                       dtype={"zip": str, "license_num": str})

def read_csv_safe(*path):
    p = P(*path)
    return pd.read_csv(p) if os.path.exists(p) else None

def cfg():
    if "cfg" not in st.session_state:
        m = load_models()
        st.session_state["cfg"] = {"model": "Decision tree", "fn": 3.0, "fp": 1.0, "tp": 0.0, "tn": 0.0,
                                   "thr": {k: v[1] for k, v in m.items()}}
    return st.session_state["cfg"]

# ---------- data preparation and scoring ----------
def prep(df):
    d = df.copy()
    d["latitude"] = pd.to_numeric(d["latitude"], errors="coerce").fillna(41.88)
    d["longitude"] = pd.to_numeric(d["longitude"], errors="coerce").fillna(-87.63)
    for c in NUMERIC:
        d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    d["zip"] = d["zip"].astype(str).str.replace(r"\.0$", "", regex=True).str[:5].replace({"nan": "unknown"})
    d["facility_group"] = d["facility_group"].fillna("unknown").astype(str)
    return d

def normalise_upload(df):
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    if "past_inspections" in df.columns:
        pi = pd.to_numeric(df["past_inspections"], errors="coerce").fillna(0)
        if "past_fail_rate" not in df.columns and "past_fails" in df.columns:
            pf = pd.to_numeric(df["past_fails"], errors="coerce").fillna(0)
            df["past_fail_rate"] = np.where(pi > 0, pf / pi.replace(0, 1), 0.0)
        if "has_history" not in df.columns:
            df["has_history"] = (pi > 0).astype(int)
    if "dba_name" not in df.columns: df["dba_name"] = "(unnamed)"
    if "address" not in df.columns: df["address"] = ""
    return df, [c for c in FEATURES if c not in df.columns]

def score(df, model_name):
    pipe, _ = load_models()[model_name]
    d = prep(df).reset_index(drop=True)
    d["risk_score"] = pipe.predict_proba(d[FEATURES])[:, 1]
    return d

@st.cache_data
def sample_scores(model_name):
    return score(load_sample(), model_name)["risk_score"].to_numpy()

def reasons_for(row_df):
    try:
        return explain(load_models()[EXPLAIN_MODEL][0], row_df)
    except Exception:
        return []

def add_reasons(d, k):
    d = d.copy().reset_index(drop=True)
    d["why"] = ""
    col = d.columns.get_loc("why")
    for i in range(min(k, len(d))):
        d.iloc[i, col] = "; ".join(reasons_for(d.iloc[[i]]))
    return d

def consequences(y, s, thr, c):
    f = s >= thr
    tp = int((f & (y == 1)).sum()); fp = int((f & (y == 0)).sum())
    fn = int((~f & (y == 1)).sum()); tn = int((~f & (y == 0)).sum())
    P_, N_ = tp + fn, tn + fp
    return dict(tp=tp, fp=fp, fn=fn, tn=tn, n=len(y),
                share=f.mean(), precision=tp / max(tp + fp, 1), recall=tp / max(P_, 1),
                accuracy=(tp + tn) / len(y), baseline=N_ / len(y),
                cost=tn * c["tn"] + fp * c["fp"] + fn * c["fn"] + tp * c["tp"],
                cost_all=P_ * c["tp"] + N_ * c["fp"],
                cost_none=N_ * c["tn"] + P_ * c["fn"])

def best_threshold(y, s, c):
    ts = np.linspace(0.01, 0.9, 90)
    costs = [consequences(y, s, t, c)["cost"] for t in ts]
    return float(ts[int(np.argmin(costs))])

def current_threshold():
    c = cfg(); return c["thr"][c["model"]]

# ---------- screen 1 ----------
def page_data():
    st.title("Food Safety Inspection Prioritiser")
    st.write("This tool ranks food premises by their predicted chance of a **serious violation** "
             "(an inspection result of *Fail*), so a limited number of inspectors can be sent where they matter most.")
    st.header("1. Data and quality")
    st.write("Source: Chicago Food Inspections open data, 2010-2019. Inspections that were not a pass/fail verdict "
             "(Not Ready, Out of Business, No Entry, Business Not Located) were removed.")
    audit = read_csv_safe("docs", "audit_report.csv")
    if audit is not None:
        st.subheader("Data-quality audit")
        st.caption("Every fault found in the raw file, how it was detected, and how many records it affected before and after repair.")
        st.dataframe(audit, use_container_width=True, hide_index=True)
    s = load_sample()
    c1, c2, c3 = st.columns(3)
    c1.metric("Premises records in demo sample", f"{len(s):,}")
    c2.metric("Share with a serious violation", f"{s['target'].mean():.1%}")
    c3.metric("Period", f"{s['inspection_date'].min().year}-{s['inspection_date'].max().year}")
    st.subheader("Preview of the prepared data")
    st.dataframe(s.head(50), use_container_width=True, hide_index=True)
    cl = P("data", "clean_sample.csv")
    if os.path.exists(cl):
        with open(cl, "rb") as f:
            st.download_button("Download the cleaned data (CSV)", f.read(), "clean_sample.csv", "text/csv")
        st.caption("Repaired fields carry a provenance column (zip_src, geo_src, risk_src, facility_type_src) "
                   "saying whether the value is original or was repaired.")
    dd = P("docs", "data_dictionary.md")
    if os.path.exists(dd):
        with st.expander("Data dictionary"):
            st.markdown(open(dd, encoding="utf-8").read())

# ---------- screen 2 ----------
def page_performance():
    c = cfg(); models = load_models()
    st.header("2. How good are the models?")
    st.info("Test period: 2015-2019. Models were trained only on 2010-2014 inspections. "
            "A model that always says 'no serious violation' is right about **78%** of the time, "
            "so accuracy alone says little. AUC, recall and precision in the top 5% say more.")
    res = read_csv_safe("docs", "model_results.csv")
    if res is not None:
        cols = ["model", "cv_auc_mean", "cv_auc_std", "test_auc", "accuracy", "baseline_acc", "precision",
                "recall", "precision@top5%", "threshold", "total_cost", "cost_if_inspect_none"]
        st.dataframe(res[[x for x in cols if x in res.columns]], use_container_width=True, hide_index=True)
        st.caption("cv_auc_std is the spread over 5 time-ordered folds. baseline_acc is the always-pass accuracy. "
                   "precision@top5% = share of the 5% highest-ranked premises that really failed (the average premises fails about 22% of the time). "
                   "Why these metrics: a supervisor has a fixed number of visits, so what matters is whether the top of the list "
                   "is richer in failures (precision@k) and how many failures are caught (recall).")
    y = load_sample()["target"].to_numpy()
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    for name in models:
        s = sample_scores(name)
        fpr, tpr, _ = roc_curve(y, s)
        ax.plot(fpr, tpr, label=f"{name} (AUC {roc_auc_score(y, s):.3f})")
    ax.plot([0, 1], [0, 1], "k--", label="Random guessing (AUC 0.500)")
    ax.set_xlabel("False positive rate"); ax.set_ylabel("True positive rate"); ax.legend(); ax.set_title("ROC curve (20,000-premises test sample)")
    st.pyplot(fig)
    st.subheader(f"Confusion matrix: {c['model']} at risk line {current_threshold():.2f}")
    r = consequences(y, sample_scores(c["model"]), current_threshold(), c)
    cm = pd.DataFrame([[r["tn"], r["fp"]], [r["fn"], r["tp"]]],
                      index=["Actually passed", "Actually failed"], columns=["Predicted: not flagged", "Predicted: flagged"])
    st.dataframe(cm)
    st.write(f"Accuracy **{r['accuracy']:.1%}** against a baseline (always 'no violation') of **{r['baseline']:.1%}**. "
             f"Precision {r['precision']:.1%}, recall {r['recall']:.1%}. "
             "Accuracy sits below the baseline because the risk line is set by the cost of a missed failure, not by accuracy.")
    st.subheader("Does the model go stale? (concept drift)")
    drift = read_csv_safe("docs", "drift_results.csv")
    if os.path.exists(P("docs", "drift.png")):
        st.image(P("docs", "drift.png"))
    if drift is not None:
        st.dataframe(drift, use_container_width=True, hide_index=True)
    st.success("**Retraining rule.** A model left untouched loses about 0.006 AUC per year and is more than 0.02 AUC below "
               "its starting level after about 15 months. Retraining on the most recent three years recovers about 0.015 AUC on average. "
               "Recommendation: retrain every 12 months on the previous three years, and at once if the monthly fail rate moves "
               "more than 3 percentage points from the training value.")
    for title, f in [("Feature selection vs PCA (same decision tree)", "reduction_comparison.csv"),
                     ("Sensitivity to the cost ratio", "cost_sensitivity.csv")]:
        t = read_csv_safe("docs", f)
        if t is not None:
            with st.expander(title):
                st.dataframe(t, use_container_width=True, hide_index=True)

# ---------- screen 3 ----------
def page_single():
    c = cfg(); s = load_sample()
    st.header("3. Check one premises")
    st.write("Describe the premises. Leave anything you do not know at its default.")
    col1, col2 = st.columns(2)
    with col1:
        fg = st.selectbox("Type of premises", sorted(s["facility_group"].dropna().unique()))
        zips = sorted(s["zip"].dropna().astype(str).unique())
        zp = st.selectbox("ZIP code", zips, index=zips.index("60614") if "60614" in zips else 0)
        risk = st.selectbox("City risk category", [1, 2, 3],
                            format_func=lambda v: {1: "1 - High", 2: "2 - Medium", 3: "3 - Low"}[v])
        month = st.selectbox("Month of the visit", list(range(1, 13)), index=date.today().month - 1)
    with col2:
        before = st.checkbox("This premises has been inspected before", value=True)
        n = f = days = lv = 0; av = 0.0; lf = False
        if before:
            n = st.number_input("Number of earlier inspections", 1, 200, 4)
            f = st.number_input("How many of them were failures", 0, int(n), 1)
            days = st.number_input("Days since the last inspection", 0, 5000, 365)
            lf = st.checkbox("It failed its last inspection")
            lv = st.number_input("Violations noted at the last inspection", 0, 60, 2)
            av = st.number_input("Average violations per earlier inspection", 0.0, 60.0, 2.0, 0.5)
    if st.button("Assess this premises", type="primary"):
        zs = s[s["zip"] == zp]
        lat = float(zs["latitude"].median()) if len(zs) else 41.88
        lon = float(zs["longitude"].median()) if len(zs) else -87.63
        row = pd.DataFrame([{"risk_level": risk, "latitude": lat, "longitude": lon, "month": month,
                             "past_inspections": n, "past_fails": f, "past_fail_rate": (f / n if n else 0.0),
                             "last_result_fail": int(lf), "days_since_last": days, "has_history": int(before),
                             "last_violation_count": lv, "avg_past_violations": av,
                             "facility_group": fg, "zip": zp}])
        d = score(row, c["model"])
        p = float(d["risk_score"].iloc[0]); thr = current_threshold()
        st.metric("Estimated chance of a serious violation", f"{p:.0%}",
                  delta=f"{(p - s['target'].mean()) * 100:+.0f} points vs the average premises ({s['target'].mean():.0%})",
                  delta_color="inverse")
        if p >= thr:
            st.error(f"**Recommend inspection.** Risk is above your line ({thr:.0%}).")
        else:
            st.success(f"**Lower priority.** Risk is below your line ({thr:.0%}).")
        st.subheader("Why")
        rs = reasons_for(d)
        for r_ in rs: st.write("- " + r_[0].upper() + r_[1:])
        if not rs: st.write("No explanation available for this case.")
        st.caption(f"Score from the **{c['model']}** model. Reasons are the path through the decision tree, "
                   "which is the app's explanation model. This is an estimate, not a finding.")

# ---------- screen 4 ----------
def page_batch():
    c = cfg()
    st.header("4. Score many premises")
    st.write("Upload a CSV with one row per premises. Needed columns: "
             + ", ".join(f"`{x}`" for x in FEATURES if x not in ("past_fail_rate", "has_history"))
             + ". Optional: `dba_name`, `address`.")
    st.download_button("Download a template (5 example rows)", load_sample().head(5)[
        ["dba_name", "address"] + [x for x in FEATURES if x not in ("past_fail_rate", "has_history")]].to_csv(index=False).encode(),
        "template.csv", "text/csv")
    up = st.file_uploader("Your CSV", type="csv")
    use_demo = st.checkbox("Or use 2,000 premises from the demo sample")
    raw = None
    if up is not None:
        raw = pd.read_csv(up, dtype={"zip": str, "license_num": str})
    elif use_demo:
        raw = load_sample().sample(2000, random_state=1)
    if raw is None:
        return
    raw, missing = normalise_upload(raw)
    if missing:
        st.error("Your file is missing these columns: " + ", ".join(missing)); return
    d = score(raw, c["model"]).sort_values("risk_score", ascending=False).reset_index(drop=True)
    thr = current_threshold()
    d["rank"] = d.index + 1
    d["risk_%"] = (d["risk_score"] * 100).round(1)
    d["flagged"] = np.where(d["risk_score"] >= thr, "Yes", "No")
    f1, f2, f3 = st.columns(3)
    minr = f1.slider("Minimum risk %", 0, 100, 0)
    zsel = f2.multiselect("ZIP codes", sorted(d["zip"].unique()))
    fsel = f3.multiselect("Premises types", sorted(d["facility_group"].unique()))
    only = st.checkbox("Show only flagged premises")
    v = d[d["risk_%"] >= minr]
    if zsel: v = v[v["zip"].isin(zsel)]
    if fsel: v = v[v["facility_group"].isin(fsel)]
    if only: v = v[v["flagged"] == "Yes"]
    k = st.number_input("Write reasons for the top ... rows", 0, 300, 25)
    v = v.reset_index(drop=True)
    v = add_reasons(v, int(k))
    out = v[["rank", "dba_name", "address", "zip", "facility_group", "risk_%", "flagged", "why"]]
    st.write(f"{len(out):,} premises shown, {int((d['flagged'] == 'Yes').sum()):,} flagged at risk line {thr:.2f}.")
    st.dataframe(out, use_container_width=True, hide_index=True)
    st.download_button("Download the ranked result (CSV)", out.to_csv(index=False).encode(), "ranked_premises.csv", "text/csv")

# ---------- screen 5 ----------
def page_settings():
    c = cfg(); models = load_models(); names = list(models)
    st.header("5. Settings")
    c["model"] = st.selectbox("Which model should the app use?", names, index=names.index(c["model"]),
                              help="The decision tree is the default because it explains itself and scores as well as the others.")
    st.subheader("What does a mistake cost?")
    a, b, c3, c4 = st.columns(4)
    c["fp"] = a.number_input("Wasted visit (premises would have passed)", 0.0, 100.0, float(c["fp"]), 0.5)
    c["fn"] = b.number_input("Missed failure", 0.0, 100.0, float(c["fn"]), 0.5)
    c["tp"] = c3.number_input("Correct catch", 0.0, 100.0, float(c["tp"]), 0.5)
    c["tn"] = c4.number_input("Correct skip", 0.0, 100.0, float(c["tn"]), 0.5)
    st.caption("Default 3:1: a missed serious violation costs about three wasted visits.")
    st.subheader("Where to draw the line")
    cur = float(min(max(c["thr"][c["model"]], 0.01), 0.9))
    thr = st.slider("Flag a premises when its risk is at least", 0.01, 0.90, cur, 0.01)
    c["thr"][c["model"]] = thr
    y = load_sample()["target"].to_numpy(); s = sample_scores(c["model"])
    if st.button("Set the line from the cost table"):
        c["thr"][c["model"]] = best_threshold(y, s, c)
        st.rerun()
    st.subheader("What this would have done (20,000-premises test sample)")
    r = consequences(y, s, thr, c)
    m = st.columns(4)
    m[0].metric("Premises flagged", f"{r['share']:.0%}")
    m[1].metric("Of flagged, truly failed", f"{r['precision']:.0%}")
    m[2].metric("Failures caught", f"{r['recall']:.0%}")
    m[3].metric("Accuracy", f"{r['accuracy']:.0%}", delta=f"baseline {r['baseline']:.0%}", delta_color="off")
    t = pd.DataFrame({"Strategy": ["This model at this line", "Inspect everyone", "Inspect no one"],
                      "Total cost": [r["cost"], r["cost_all"], r["cost_none"]]})
    st.dataframe(t, hide_index=True)
    best = min(r["cost_all"], r["cost_none"])
    if r["cost"] < best:
        st.success(f"Cheaper than the best simple strategy by {(1 - r['cost'] / best):.0%}.")
    else:
        st.warning("At these settings the model is NOT cheaper than a simple strategy. Change the line or the costs.")
    st.caption("Default lines were chosen from the cost matrix on 2014 data, never on the test years. "
               "'Set the line from the cost table' optimises on the test sample, so use it only to explore.")

# ---------- screen 6 ----------
def order_stops(g):
    n = len(g)
    if n <= 2: return g
    pts = g[["latitude", "longitude"]].to_numpy()
    cur = int(np.argmax(pts[:, 0])); path = [cur]; left = [i for i in range(n) if i != cur]
    while left:
        d = ((pts[left] - pts[cur]) ** 2).sum(axis=1)
        cur = left[int(np.argmin(d))]; path.append(cur); left.remove(cur)
    return g.iloc[path]

def build_rounds(sel, cap):
    zmean = sel.groupby("zip")["latitude"].mean().sort_values(ascending=False)
    ordered = pd.concat([order_stops(sel[sel["zip"] == z]) for z in zmean.index]).reset_index(drop=True)
    ordered["inspector"] = ordered.index // cap + 1
    ordered["stop"] = ordered.groupby("inspector").cumcount() + 1
    return ordered

def rounds_html(rounds, day):
    h = ["<html><head><meta charset='utf-8'><title>Inspection rounds</title><style>"
         "body{font-family:Arial;margin:24px}table{border-collapse:collapse;width:100%}"
         "th,td{border:1px solid #999;padding:6px;font-size:13px;text-align:left}"
         ".pb{page-break-after:always}</style></head><body>"]
    for i, g in rounds.groupby("inspector"):
        h.append(f"<div class='pb'><h2>Inspector {i} - round for {day}</h2>"
                 f"<p>{len(g)} premises | ZIP areas: {html.escape(', '.join(sorted(g['zip'].unique())))}</p>"
                 "<table><tr><th>#</th><th>Premises</th><th>Address</th><th>ZIP</th><th>Risk</th><th>Why</th><th>Done / notes</th></tr>")
        for _, r in g.iterrows():
            h.append(f"<tr><td>{r['stop']}</td><td>{html.escape(str(r['dba_name']))}</td><td>{html.escape(str(r['address']))}</td>"
                     f"<td>{r['zip']}</td><td>{r['risk_score']*100:.0f}%</td><td>{html.escape(str(r['why']))}</td><td></td></tr>")
        h.append("</table></div>")
    h.append("</body></html>")
    return "".join(h)

def page_route():
    c = cfg()
    st.header("6. Route planner")
    day = date.today() + timedelta(days=1)
    st.write(f"Plan for **{day:%A %d %B %Y}**. The highest-risk premises fill the day's capacity, are grouped by ZIP area, "
             "and are split into one round per inspector.")
    up = st.file_uploader("Candidate premises (CSV, same format as screen 4). Leave empty to use the demo sample.", type="csv")
    if up is not None:
        pool = pd.read_csv(up, dtype={"zip": str, "license_num": str})
        pool, missing = normalise_upload(pool)
        if missing:
            st.error("Missing columns: " + ", ".join(missing)); return
    else:
        s = load_sample().sort_values("inspection_date")
        pool = s.groupby("license_num", sort=False).tail(1)
        st.caption("Demo: the most recent record of each premises in the sample is treated as tomorrow's candidate list. "
                   "In service, history features would be refreshed each night.")
    a, b = st.columns(2)
    n_insp = a.number_input("Inspectors available", 1, 50, 5)
    cap = b.number_input("Inspections per inspector per day", 1, 30, 8)
    only = st.checkbox("Only include premises at or above the risk line", value=False)
    scored = score(pool, c["model"]).sort_values("risk_score", ascending=False)
    thr = current_threshold()
    above = int((scored["risk_score"] >= thr).sum())
    st.write(f"{len(scored):,} candidate premises, {above:,} at or above the risk line ({thr:.2f}). "
             f"Capacity today: **{n_insp * cap}** inspections.")
    if st.button("Build tomorrow's rounds", type="primary"):
        ranked = scored[scored["risk_score"] >= thr] if only else scored
        sel = ranked.head(int(n_insp * cap)).reset_index(drop=True)
        if sel.empty:
            st.warning("No premises qualify."); return
        rounds = add_reasons(build_rounds(sel, int(cap)), len(sel))
        st.session_state["rounds"] = (rounds, scored["risk_score"].mean(), day)
    if "rounds" not in st.session_state:
        return
    rounds, avg, d_ = st.session_state["rounds"]
    st.subheader("What this plan is expected to achieve")
    m = st.columns(3)
    m[0].metric("Premises planned", len(rounds))
    m[1].metric("Expected serious violations found", f"{rounds['risk_score'].sum():.0f}",
                delta=f"{rounds['risk_score'].sum() - avg * len(rounds):+.0f} vs picking the same number at random", delta_color="normal")
    if "target" in rounds.columns:
        m[2].metric("Real failures in this historical replay", int(rounds["target"].sum()),
                    delta=f"{rounds['target'].sum() - rounds['target'].mean() * 0 - avg * len(rounds):+.0f} vs random (expected)", delta_color="normal")
    with st.expander("Planned premises grouped by area (ZIP)"):
        g = rounds.groupby("zip").agg(premises=("risk_score", "size"), average_risk=("risk_score", "mean"),
                                      inspectors=("inspector", lambda x: ", ".join(map(str, sorted(set(x)))))).reset_index()
        g["average_risk"] = (g["average_risk"] * 100).round(0).astype(int).astype(str) + "%"
        st.dataframe(g.sort_values("premises", ascending=False), hide_index=True, use_container_width=True)
    tabs = st.tabs([f"Inspector {i}" for i in sorted(rounds["inspector"].unique())])
    for tab, i in zip(tabs, sorted(rounds["inspector"].unique())):
        with tab:
            g = rounds[rounds["inspector"] == i]
            show = g[["stop", "dba_name", "address", "zip", "risk_score", "why"]].copy()
            show["risk_score"] = (show["risk_score"] * 100).round(0).astype(int).astype(str) + "%"
            show.columns = ["Stop", "Premises", "Address", "ZIP", "Risk", "Why"]
            st.dataframe(show, hide_index=True, use_container_width=True)
            st.download_button(f"Download round {i} (CSV)", show.to_csv(index=False).encode(), f"round_inspector_{i}.csv", "text/csv", key=f"dl{i}")
    st.download_button("Download printable rounds for all inspectors (open the file, then press Ctrl+P)",
                       rounds_html(rounds, f"{d_:%d %b %Y}").encode("utf-8"), "inspection_rounds.html", "text/html")

PAGES = {"1. Data & quality": page_data, "2. Model performance": page_performance,
         "3. Single prediction": page_single, "4. Batch scoring": page_batch,
         "5. Settings": page_settings, "6. Route planner": page_route}
choice = st.sidebar.radio("Screens", list(PAGES))
st.sidebar.caption("Model: " + cfg()["model"] + " | risk line: " + f"{current_threshold():.2f}")
PAGES[choice]()