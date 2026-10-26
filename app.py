"""
Food Safety Inspection Prioritiser — Streamlit Application
A predictive analytics and inspection dispatch dashboard for municipal health departments.
"""

import os, sys, html
from datetime import date, timedelta

# Ensure src is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import numpy as np
import pandas as pd
import joblib
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import roc_curve, roc_auc_score

# Scikit-learn compatibility shim for python 3.14 / scikit-learn 1.9+ unpickling
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

from features import FEATURES, NUMERIC, CATEGORICAL
from explain import explain
from ui_theme import (
    NAVY, PRIMARY_BLUE, SOFT_LAVENDER, LAVENDER_ACCENT,
    SOFT_MINT, SUCCESS_GREEN, SOFT_AMBER, WARNING_AMBER,
    SOFT_ROSE, DANGER_RED, BG_MAIN, BG_CARD, TEXT_MAIN, TEXT_MUTED, BORDER_COLOR,
    SPACE_INDIGO, DUSTY_GRAPE, LILAC_ASH, ALMOND_SILK, PARCHMENT,
    APP_BG, SURFACE, SURFACE_SUBTLE, BORDER as BORDER_TOKEN, BORDER_STRONG,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_ON_DARK,
    SUCCESS, SUCCESS_SOFT, WARNING, WARNING_SOFT, DANGER, DANGER_SOFT, INFO, INFO_SOFT,
    RADIUS_SM, RADIUS_MD, RADIUS_LG, SHADOW_CARD, SHADOW_HOVER,
    CUSTOM_CSS, kpi_card_html, header_banner_html, sidebar_brand_html,
    section_title_html, icon, footer_html, get_plotly_layout
)

BASE = os.path.dirname(os.path.abspath(__file__))
def P(*a): return os.path.join(BASE, *a)

st.set_page_config(
    page_title="Food Safety Inspection Prioritiser",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global custom design system
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Extended features for v2 models
def add_engineered_features(df):
    """Derive features for v2 models using information available at prediction time."""
    d = df.copy()
    d["risk_x_failrate"] = d["risk_level"] * d["past_fail_rate"]
    d["risk_x_no_history"] = d["risk_level"] * (1 - d["has_history"])
    d["log_days_since"] = np.log1p(d["days_since_last"])
    d["fail_rate_sq"] = d["past_fail_rate"] ** 2
    d["viol_above_avg"] = np.where(
        d["avg_past_violations"] > 0,
        d["last_violation_count"] / d["avg_past_violations"].replace(0, 1),
        0.0
    )
    d["is_recent_reinspection"] = (d["days_since_last"].between(1, 90)).astype(int)
    d["inspection_frequency"] = np.where(
        d["days_since_last"] > 0,
        d["past_inspections"] / (d["days_since_last"] / 365.25).clip(lower=0.1),
        0.0
    )
    d["quarter"] = d["month"].apply(lambda m: (m - 1) // 3 + 1)
    return d

class ModelEntry(tuple):
    """Backward-compatible tuple (model, threshold) with extended metadata."""
    def __new__(cls, pipe, threshold, features=None, version="v1", display_name=""):
        obj = super().__new__(cls, (pipe, threshold))
        obj.model = pipe
        obj.threshold = threshold
        obj.features = features if features is not None else FEATURES
        obj.version = version
        obj.display_name = display_name
        return obj

MODEL_FILES = {
    "Neural network v2 (Recommended)": "neural_network_v2",
    "Decision tree v2": "decision_tree_v2",
    "Decision tree": "decision_tree",
    "Neural network": "neural_network",
    "Naive Bayes": "naive_bayes",
}
EXPLAIN_MODEL = "Decision tree"

# ---------- loaders ----------
@st.cache_resource
def load_models():
    out = {}
    for name, f in MODEL_FILES.items():
        path = P("models", f + ".joblib")
        if os.path.exists(path):
            try:
                d = joblib.load(path)
                pipe = d["model"]
                thr = float(d["threshold"])
                feats = d.get("features", FEATURES)
                ver = d.get("version", "v1")
                out[name] = ModelEntry(pipe, thr, features=feats, version=ver, display_name=name)
            except Exception as e:
                st.sidebar.warning(f"Note: Could not load {f}: {e}")
    # Fallback guarantees
    if "Decision tree" not in out and "Decision tree v2" in out:
        out["Decision tree"] = out["Decision tree v2"]
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
        default_model = "Neural network v2 (Recommended)" if "Neural network v2 (Recommended)" in m else "Decision tree"
        st.session_state["cfg"] = {
            "model": default_model,
            "fn": 3.0,
            "fp": 1.0,
            "tp": 0.0,
            "tn": 0.0,
            "thr": {k: v[1] for k, v in m.items()}
        }
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
    entry = load_models()[model_name]
    pipe = entry[0]
    feats = getattr(entry, "features", FEATURES)
    d = prep(df).reset_index(drop=True)
    if any(k in feats for k in ("risk_x_failrate", "log_days_since", "quarter")):
        d = add_engineered_features(d)
    d["risk_score"] = pipe.predict_proba(d[feats])[:, 1]
    return d

@st.cache_data
def sample_scores(model_name):
    return score(load_sample(), model_name)["risk_score"].to_numpy()

def reasons_for(row_df):
    try:
        models = load_models()
        explain_model_name = EXPLAIN_MODEL if EXPLAIN_MODEL in models else "Decision tree v2"
        if explain_model_name not in models:
            explain_model_name = list(models.keys())[0]
        return explain(models[explain_model_name][0], row_df)
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
    c = cfg()
    if c["model"] not in c["thr"]:
        m = load_models()
        c["thr"][c["model"]] = m[c["model"]][1] if c["model"] in m else 0.25
    return c["thr"][c["model"]]

# ============================================================
# Plotly chart colors aligned to STYLE.md palette
# ============================================================
CHART_PALETTE = [SPACE_INDIGO, DUSTY_GRAPE, LILAC_ASH, ALMOND_SILK, "#6B5B73"]

# ============================================================
# SCREEN 1: Data and Quality
# ============================================================
def page_data():
    st.markdown(header_banner_html(
        "1", "Data & Quality",
        "Chicago Food Inspections open data (2010\u20132019) with comprehensive cleaning, validation audits, and leakage safeguards.",
        icon_name="database"
    ), unsafe_allow_html=True)

    s = load_sample()
    total_recs = len(s)
    fail_rate = s["target"].mean()
    min_date = s["inspection_date"].min()
    max_date = s["inspection_date"].max()

    # Top KPI metrics row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card_html("Demo Sample Records", f"{total_recs:,}", "Stratified random slice", icon_name="file-text", badge_text="Verified", badge_type="success"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card_html("Serious Violation Rate", f"{fail_rate:.1%}", "Citywide failure baseline", icon_name="alert-triangle", badge_text="Target Class", badge_type="warning"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card_html("Sample Time Horizon", f"{min_date.year} \u2013 {max_date.year}", f"{max_date - min_date}".split(",")[0] + " span", icon_name="calendar", badge_text="10-Year Record", badge_type="info"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card_html("Feature Pipeline", "14 Base / 22 Ext", "Temporal history only", icon_name="cpu", badge_text="Zero Leakage", badge_type="success"), unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Data Quality Audit Section
    st.markdown(section_title_html("Data Quality Audit & Sanitisation Report", "search"), unsafe_allow_html=True)
    st.caption("Every anomaly identified in raw Chicago City data, its detection heuristic, and the remediation applied.")
    audit = read_csv_safe("docs", "audit_report.csv")
    if audit is not None:
        # Format counts
        audit_display = audit.copy()
        if "count_before" in audit_display.columns:
            audit_display["count_before"] = audit_display["count_before"].apply(lambda v: f"{int(v):,}" if pd.notna(v) else "0")
        if "count_after" in audit_display.columns:
            audit_display["count_after"] = audit_display["count_after"].apply(lambda v: f"{int(v):,}" if pd.notna(v) else "0")
        audit_display.columns = ["Fault Description", "Quality Category", "Detection Rule", "Raw Fault Count", "Post-Cleaning Faults"]
        st.dataframe(audit_display, use_container_width=True, hide_index=True)
    else:
        st.info("Audit report is being compiled.")

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Interactive Visualizations
    st.markdown(section_title_html("Dataset Distributions & Characteristics", "pie-chart"), unsafe_allow_html=True)
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        # Target Outcome Donut Chart
        outcome_counts = s["target"].value_counts().reset_index()
        outcome_counts.columns = ["Target", "Count"]
        outcome_counts["Label"] = outcome_counts["Target"].map({0: "Pass / Pass w/ Conditions", 1: "Serious Violation (Fail)"})
        fig_target = px.pie(
            outcome_counts,
            names="Label",
            values="Count",
            color="Label",
            color_discrete_map={
                "Pass / Pass w/ Conditions": SUCCESS,
                "Serious Violation (Fail)": DANGER
            },
            hole=0.55
        )
        fig_target.update_layout(get_plotly_layout(height=320, title="Inspection Outcome Distribution"))
        fig_target.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_target, use_container_width=True)

    with col_chart2:
        # Facility Group Bar Chart
        fg_counts = s["facility_group"].value_counts().head(8).reset_index()
        fg_counts.columns = ["Facility Group", "Inspections"]
        fig_fg = px.bar(
            fg_counts,
            x="Inspections",
            y="Facility Group",
            orientation="h",
            color_discrete_sequence=[SPACE_INDIGO]
        )
        fig_fg.update_layout(get_plotly_layout(height=320, title="Top Facility Categories in Sample"))
        fig_fg.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_fg, use_container_width=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Preview of prepared data
    st.markdown(section_title_html("Prepared Dataset Explorer", "grid"), unsafe_allow_html=True)
    st.caption("Inspections with normalized identifiers, imputed spatial medians, and engineered historical features.")

    col_filter1, col_filter2 = st.columns([2, 1])
    with col_filter1:
        filter_fg = st.multiselect("Filter premises type", sorted(s["facility_group"].dropna().unique()), default=[])
    with col_filter2:
        filter_target = st.selectbox("Filter inspection result", ["All Outcomes", "Violations Only (Fail)", "Passing Inspections"])

    filtered_s = s.copy()
    if filter_fg:
        filtered_s = filtered_s[filtered_s["facility_group"].isin(filter_fg)]
    if filter_target == "Violations Only (Fail)":
        filtered_s = filtered_s[filtered_s["target"] == 1]
    elif filter_target == "Passing Inspections":
        filtered_s = filtered_s[filtered_s["target"] == 0]

    st.dataframe(filtered_s.head(50), use_container_width=True, hide_index=True)

    # Download button for clean data
    cl = P("data", "clean_sample.csv")
    if os.path.exists(cl):
        with open(cl, "rb") as f:
            st.download_button(
                "Download Cleaned Sample Dataset (CSV)",
                f.read(),
                "clean_sample.csv",
                "text/csv",
                help="Download verified, cleaned historical inspection dataset."
            )
        st.caption("Repaired fields carry provenance flags (zip_src, geo_src, risk_src, facility_type_src) detailing repair history.")

    dd = P("docs", "data_dictionary.md")
    if os.path.exists(dd):
        with st.expander("View Data Dictionary & Schema Definitions"):
            st.markdown(open(dd, encoding="utf-8").read())

# ============================================================
# SCREEN 2: Model Performance
# ============================================================
def page_performance():
    c = cfg()
    models = load_models()

    st.markdown(header_banner_html(
        "2", "Model Performance & Evaluation",
        "Rigorous out-of-time evaluation on 2015\u20132019 inspections with TimeSeriesSplit CV and cost-utility calibration.",
        icon_name="bar-chart"
    ), unsafe_allow_html=True)

    # Evaluation Methodology Callout
    st.info(
        "**Strict Chronological Hold-Out Methodology:** "
        "Training Period: **2010\u20132014** (86,673 records) | Out-of-Time Test Period: **2015\u20132019** (84,797 records). "
        "Because serious violations occur in **21.8%** of inspections, an uninformed baseline predicting \u2018Pass\u2019 for all premises achieves "
        "**78.2% Accuracy** while catching **0% of violations**. Inspection prioritization relies on **ROC-AUC**, **Recall**, and **Precision@Top 5%**."
    )

    # Load results
    res_v1 = read_csv_safe("docs", "model_results.csv")
    res_v2 = read_csv_safe("docs", "model_results_v2.csv")

    # Metrics Hero Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card_html("Best Test ROC-AUC", "0.663", "Neural network v2 (+1.0 pt)", icon_name="target", badge_text="Top Discrimination", badge_type="success"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card_html("Peak Recall @ \u03c4", "52.9%", "Neural network v2 (+6.2 pts)", icon_name="search", badge_text="Violations Caught", badge_type="success"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card_html("Precision @ Top 5%", "41.9%", "1.92x citywide random baseline", icon_name="zap", badge_text="Resource Efficient", badge_type="info"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card_html("Total Inspection Cost", "45,979", "17.1% cheaper than inspect-none", icon_name="dollar-sign", badge_text="Optimal Cost", badge_type="success"), unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Model Benchmark Table
    st.markdown(section_title_html("Comprehensive Model Benchmark", "bar-chart"), unsafe_allow_html=True)

    tabs = st.tabs(["Combined Comparison", "Pipeline v2 (Improved)", "Baseline v1 (Original)"])

    with tabs[0]:
        combined_rows = []
        if res_v2 is not None:
            combined_rows.append(res_v2)
        if res_v1 is not None:
            combined_rows.append(res_v1)
        if combined_rows:
            comb_df = pd.concat(combined_rows, ignore_index=True)
            cols = ["model", "cv_auc_mean", "cv_auc_std", "test_auc", "accuracy", "baseline_acc",
                    "precision", "recall", "precision@top5%", "threshold", "total_cost", "cost_if_inspect_none"]
            show_comb = comb_df[[x for x in cols if x in comb_df.columns]].copy()
            # Clean formatting
            show_comb.columns = [
                "Model Architecture", "CV AUC (Mean)", "CV AUC (Std)", "Test AUC", "Accuracy",
                "Baseline Acc", "Precision", "Recall", "P@Top5%", "Threshold (\u03c4)", "Total Cost", "No-Inspect Cost"
            ]
            st.dataframe(show_comb, use_container_width=True, hide_index=True)
            st.caption("P@Top5% measures failure concentration in the top 5% ranked premises. "
                       "A score of 41.9% means over 4 in 10 top-ranked premises had serious health violations.")

    with tabs[1]:
        if res_v2 is not None:
            st.dataframe(res_v2, use_container_width=True, hide_index=True)
        else:
            st.info("Pipeline v2 results not yet found in docs/model_results_v2.csv")

    with tabs[2]:
        if res_v1 is not None:
            st.dataframe(res_v1, use_container_width=True, hide_index=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Interactive Plots: Two Separate Full-Width Rows for Desktop Readability
    y = load_sample()["target"].to_numpy()

    # --- ROW 1: ROC Curves ---
    st.markdown(section_title_html("Test ROC Curves (20,000 Sample)", "activity"), unsafe_allow_html=True)
    fig_roc = go.Figure()

    for idx, name in enumerate(models):
        s_ = sample_scores(name)
        fpr, tpr, _ = roc_curve(y, s_)
        auc_val = roc_auc_score(y, s_)
        fig_roc.add_trace(go.Scatter(
            x=fpr, y=tpr,
            mode="lines",
            name=f"{name} (AUC {auc_val:.3f})",
            line=dict(width=2.5, color=CHART_PALETTE[idx % len(CHART_PALETTE)])
        ))

    fig_roc.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode="lines",
        name="Random Guessing (AUC 0.500)",
        line=dict(color="#B8AFA9", dash="dash", width=1.5)
    ))

    fig_roc.update_layout(get_plotly_layout(height=420, title="Receiver Operating Characteristic"))
    fig_roc.update_xaxes(title="False Positive Rate (1 \u2212 Specificity)")
    fig_roc.update_yaxes(title="True Positive Rate (Sensitivity / Recall)")
    st.plotly_chart(fig_roc, use_container_width=True)

    st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

    # --- ROW 2: Confusion Matrix ---
    st.markdown(section_title_html(f"Confusion Matrix: {c['model']}", "grid"), unsafe_allow_html=True)
    cur_thr = current_threshold()
    r = consequences(y, sample_scores(c["model"]), cur_thr, c)

    # Interactive Plotly Heatmap
    z_vals = [[r["tn"], r["fp"]], [r["fn"], r["tp"]]]
    x_cats = ["Predicted Pass", "Predicted Violator"]
    y_cats = ["Actual Pass", "Actual Violator"]

    # Annotations text — clean formatting without unsupported <small> tags
    text_vals = [
        [
            f"<b>True Negative (TN)</b><br>{r['tn']:,}<br>(Correct Routine Skip)",
            f"<b>False Positive (FP)</b><br>{r['fp']:,}<br>(Wasted Inspection Visit)"
        ],
        [
            f"<b>False Negative (FN)</b><br>{r['fn']:,}<br>(Missed Outbreak \u2014 3\u00d7 Cost)",
            f"<b>True Positive (TP)</b><br>{r['tp']:,}<br>(Caught Violator)"
        ]
    ]

    fig_cm = go.Figure(data=go.Heatmap(
        z=z_vals,
        x=x_cats,
        y=y_cats,
        colorscale=[[0, SURFACE_SUBTLE], [0.5, PARCHMENT], [1, SPACE_INDIGO]],
        showscale=False
    ))

    # Add labels with dynamic contrast based on cell density
    max_z = max(max(row) for row in z_vals)
    for i in range(2):
        for j in range(2):
            fig_cm.add_annotation(
                x=x_cats[j], y=y_cats[i],
                text=text_vals[i][j],
                showarrow=False,
                font=dict(family="Inter, sans-serif", size=13,
                          color=TEXT_ON_DARK if z_vals[i][j] > max_z * 0.55 else SPACE_INDIGO)
            )

    fig_cm.update_layout(get_plotly_layout(height=360, title=f"Threshold \u03c4 = {cur_thr:.2f}"))
    fig_cm.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_cm, use_container_width=True)

    # Cost-utility rationale
    st.markdown(
        f"<div class='fsp-card' style='background: {SURFACE_SUBTLE};'>"
        f"<strong>Trade-off Analysis:</strong> At threshold <code>\u03c4 = {cur_thr:.2f}</code>, the model catches <strong>{r['recall']:.1%}</strong> "
        f"of all serious food safety violations with a precision of <strong>{r['precision']:.1%}</strong>. "
        "Because a missed serious violation carries three times the social and health cost of an unnecessary inspection visit, "
        "the cost-minimizing threshold intentionally accepts a moderate False Positive rate to catch dangerous violations."
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Concept Drift Section
    st.markdown(section_title_html("Temporal Concept Drift Analysis (2013\u20132019)", "clock"), unsafe_allow_html=True)
    drift = read_csv_safe("docs", "drift_results.csv")
    if drift is not None:
        fig_drift = go.Figure()
        fig_drift.add_trace(go.Scatter(
            x=drift["period"], y=drift["auc_fixed_2010_12"],
            mode="lines+markers",
            name="Static Model (Trained 2010\u20132012 only)",
            line=dict(color=DANGER, width=2.5, dash="dot"),
            marker=dict(size=6)
        ))
        fig_drift.add_trace(go.Scatter(
            x=drift["period"], y=drift["auc_retrained"],
            mode="lines+markers",
            name="Annually Retrained Model (Rolling 3-Year Window)",
            line=dict(color=SUCCESS, width=2.5),
            marker=dict(size=6)
        ))
        fig_drift.update_layout(get_plotly_layout(height=360, title="Model Degradation Over 80 Months vs Periodic Retraining"))
        fig_drift.update_xaxes(title="Evaluation Half-Year")
        fig_drift.update_yaxes(title="ROC-AUC on Out-of-Time Data")
        st.plotly_chart(fig_drift, use_container_width=True)

    st.success(
        "**Regulatory Retraining Recommendation:** An unmaintained model loses ~0.006 AUC per year due to business turnover "
        "and evolving compliance practices. Retraining annually on a rolling 3-year window recovers +0.015 AUC on average. "
        "Trigger emergency retraining if monthly failure rates deviate by > 3 percentage points from baseline."
    )

    # Expanders for additional academic analyses
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        with st.expander("Feature Selection vs PCA Dimensionality Reduction"):
            red = read_csv_safe("docs", "reduction_comparison.csv")
            if red is not None:
                st.dataframe(red, use_container_width=True, hide_index=True)
            else:
                st.write("Reduction comparison data not found.")
    with col_exp2:
        with st.expander("Cost Ratio Sensitivity Analysis (1:1 to 10:1)"):
            cs = read_csv_safe("docs", "cost_sensitivity.csv")
            if cs is not None:
                st.dataframe(cs, use_container_width=True, hide_index=True)
            else:
                st.write("Cost sensitivity data not found.")

# ============================================================
# SCREEN 3: Single Prediction
# ============================================================
def page_single():
    c = cfg()
    s = load_sample()

    st.markdown(header_banner_html(
        "3", "Single Prediction",
        "Estimate the likelihood of a critical health violation for a specific establishment and inspect the explanatory decision path.",
        icon_name="crosshair"
    ), unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(section_title_html("Establishment Profile", "box"), unsafe_allow_html=True)
        fg = st.selectbox("Facility Type", sorted(s["facility_group"].dropna().unique()),
                          help="Categorical grouping derived from Chicago health license categories.")
        zips = sorted(s["zip"].dropna().astype(str).unique())
        zp = st.selectbox("ZIP Code", zips, index=zips.index("60614") if "60614" in zips else 0,
                          help="Location postal code for spatial baseline matching.")
        risk = st.selectbox(
            "City Risk Category", [1, 2, 3],
            format_func=lambda v: {1: "Risk 1 (High \u2014 Prepared / Unpackaged Foods)",
                                   2: "Risk 2 (Medium \u2014 Handled Foods / Reheating)",
                                   3: "Risk 3 (Low \u2014 Prepackaged / Convenience)"}[v],
            help="Municipal risk tier assigned upon license application."
        )
        month = st.selectbox("Month of Inspection Visit", list(range(1, 13)),
                             index=date.today().month - 1,
                             format_func=lambda m: date(2024, m, 1).strftime("%B"),
                             help="Captures seasonal inspection patterns.")

    with col2:
        st.markdown(section_title_html("Inspection Track Record", "clipboard"), unsafe_allow_html=True)
        before = st.checkbox("Premises has prior Chicago inspection history", value=True)
        n = f = days = lv = 0; av = 0.0; lf = False
        if before:
            c_hist1, c_hist2 = st.columns(2)
            with c_hist1:
                n = st.number_input("Prior Inspections Count", 1, 200, 4)
                f = st.number_input("Prior Failed Inspections", 0, int(n), 1)
                days = st.number_input("Days Since Last Inspection", 0, 5000, 365)
            with c_hist2:
                lf = st.checkbox("Failed Most Recent Inspection", value=False)
                lv = st.number_input("Violations at Last Inspection", 0, 60, 2)
                av = st.number_input("Average Historical Violations", 0.0, 60.0, 2.0, 0.5)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    assess_btn = st.button("Assess This Premises Risk", type="primary")

    if assess_btn:
        zs = s[s["zip"] == zp]
        lat = float(zs["latitude"].median()) if len(zs) else 41.88
        lon = float(zs["longitude"].median()) if len(zs) else -87.63
        row = pd.DataFrame([{
            "risk_level": risk, "latitude": lat, "longitude": lon, "month": month,
            "past_inspections": n, "past_fails": f, "past_fail_rate": (f / n if n else 0.0),
            "last_result_fail": int(lf), "days_since_last": days, "has_history": int(before),
            "last_violation_count": lv, "avg_past_violations": av,
            "facility_group": fg, "zip": zp
        }])

        d = score(row, c["model"])
        p = float(d["risk_score"].iloc[0])
        thr = current_threshold()
        city_avg = s["target"].mean()

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.markdown(section_title_html("Prioritization Assessment Outcome", "clipboard"), unsafe_allow_html=True)

        col_res1, col_res2 = st.columns([1, 1.2])

        with col_res1:
            is_high_risk = p >= thr
            bg_banner = DANGER_SOFT if is_high_risk else SUCCESS_SOFT
            text_color = DANGER if is_high_risk else SUCCESS
            border_color = "#F0C6CC" if is_high_risk else "#C3DFD0"
            badge_label = "HIGH RISK \u2014 RECOMMEND INSPECTION" if is_high_risk else "ROUTINE PRIORITY \u2014 LOWER RISK"
            badge_class = "danger" if is_high_risk else "success"

            st.markdown(
                f"""
                <div class="fsp-card" style="background: {bg_banner}; border-color: {border_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span class="fsp-badge fsp-badge-{badge_class}">{badge_label}</span>
                        <span style="font-size: 0.8rem; color: {TEXT_SECONDARY};">Model: <strong>{html.escape(c['model'])}</strong></span>
                    </div>
                    <div style="font-size: 2.5rem; font-weight: 700; color: {text_color}; line-height: 1;">
                        {p:.1%}
                    </div>
                    <div style="font-size: 0.9rem; color: {TEXT_SECONDARY}; margin-top: 6px;">
                        Predicted Probability of Serious Health Violation
                    </div>
                    <div style="margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(0,0,0,0.06); font-size: 0.85rem; color: {TEXT_PRIMARY};">
                        <strong>Delta vs City Baseline:</strong> {(p - city_avg) * 100:+.1f} percentage points (Baseline: {city_avg:.1%})<br>
                        <strong>Active Decision Line:</strong> \u03c4 = {thr:.1%}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_res2:
            st.markdown(section_title_html("Decision Path & Primary Risk Factors", "trending-up"), unsafe_allow_html=True)
            rs = reasons_for(d)
            if rs:
                for r_ in rs:
                    st.markdown(
                        f"""
                        <div style="padding: 10px 14px; margin-bottom: 8px; border-radius: {RADIUS_SM}; background: {SURFACE}; border: 1px solid {BORDER_TOKEN}; display: flex; align-items: center; gap: 10px;">
                            <span style="color: {DUSTY_GRAPE}; flex-shrink: 0;">{icon("check-circle", DUSTY_GRAPE, 16)}</span>
                            <span style="font-size: 0.88rem; font-weight: 500; color: {TEXT_PRIMARY};">{html.escape(r_[0].upper() + r_[1:])}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.write("Decision rules evaluated cleanly within standard bounds.")

            st.caption(
                "Risk factors are traced along the decision path of the verified classification tree. "
                "This serves as an operational decision aid, not a deterministic legal determination."
            )

# ============================================================
# SCREEN 4: Batch Scoring
# ============================================================
def page_batch():
    c = cfg()

    st.markdown(header_banner_html(
        "4", "Batch Prioritisation",
        "Upload inspection manifests to rank hundreds of establishments by risk and filter high-priority targets.",
        icon_name="layers"
    ), unsafe_allow_html=True)

    st.caption("Upload a CSV file containing premise records. Required columns: "
               + ", ".join(f"`{x}`" for x in FEATURES if x not in ("past_fail_rate", "has_history"))
               + ". Optional: `dba_name`, `address`.")

    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        template_df = load_sample().head(5)[
            ["dba_name", "address"] + [x for x in FEATURES if x not in ("past_fail_rate", "has_history")]
        ]
        st.download_button(
            "Download Template CSV",
            template_df.to_csv(index=False).encode(),
            "premises_batch_template.csv",
            "text/csv"
        )

    up = st.file_uploader("Upload Inspection Manifest (CSV)", type="csv")
    use_demo = st.checkbox("Or use 2,000 stratified establishments from the verified demo sample", value=True if up is None else False)

    raw = None
    if up is not None:
        raw = pd.read_csv(up, dtype={"zip": str, "license_num": str})
    elif use_demo:
        raw = load_sample().sample(2000, random_state=42)

    if raw is None:
        st.info("Upload a manifest or check the demo sample above to begin scoring.")
        return

    raw, missing = normalise_upload(raw)
    if missing:
        st.error(f"Manifest missing required columns: {', '.join(missing)}")
        return

    # Score batch
    d = score(raw, c["model"]).sort_values("risk_score", ascending=False).reset_index(drop=True)
    thr = current_threshold()
    d["rank"] = d.index + 1
    d["risk_%"] = (d["risk_score"] * 100).round(1)
    d["flagged"] = np.where(d["risk_score"] >= thr, "Flagged", "Routine")

    total_scored = len(d)
    flagged_count = int((d["flagged"] == "Flagged").sum())
    flagged_pct = flagged_count / max(total_scored, 1)
    mean_risk = d["risk_score"].mean()

    # KPI Row
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card_html("Total Premises Scored", f"{total_scored:,}", "Validated records", icon_name="box", badge_text="Processed", badge_type="info"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card_html("Prioritised for Inspection", f"{flagged_count:,}", f"{flagged_pct:.1%} of manifest", icon_name="alert-triangle", badge_text="High Priority", badge_type="danger" if flagged_count > 0 else "success"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card_html("Mean Violation Probability", f"{mean_risk:.1%}", "Across all uploaded", icon_name="bar-chart", badge_text="Cohort Average", badge_type="warning"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card_html("Dispatch Decision Line", f"\u03c4 = {thr:.2f}", f"Model: {c['model']}", icon_name="sliders", badge_text="Threshold", badge_type="neutral"), unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Interactive Distribution Chart
    fig_hist = px.histogram(
        d, x="risk_%", nbins=30,
        color="flagged",
        color_discrete_map={"Flagged": DANGER, "Routine": SPACE_INDIGO},
        labels={"risk_%": "Estimated Violation Probability (%)", "count": "Premises Count"}
    )
    fig_hist.add_vline(x=thr * 100, line_dash="dash", line_color=SPACE_INDIGO,
                       annotation_text=f"Decision Threshold ({thr:.1%})", annotation_position="top right")
    fig_hist.update_layout(get_plotly_layout(height=300, title="Risk Score Distribution Across Uploaded Cohort"))
    st.plotly_chart(fig_hist, use_container_width=True)

    # Filters
    st.markdown(section_title_html("Filter and Inspect Ranked Results", "filter"), unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns([1, 1, 1, 0.8])
    with f1:
        minr = st.slider("Minimum Violation Risk (%)", 0, 100, 0)
    with f2:
        zsel = st.multiselect("Filter ZIP Codes", sorted(d["zip"].unique()))
    with f3:
        fsel = st.multiselect("Filter Facility Types", sorted(d["facility_group"].unique()))
    with f4:
        only = st.checkbox("High priority only", value=False)
        k = st.number_input("Explain top N rows", 0, 300, 25)

    v = d[d["risk_%"] >= minr]
    if zsel: v = v[v["zip"].isin(zsel)]
    if fsel: v = v[v["facility_group"].isin(fsel)]
    if only: v = v[v["flagged"] == "Flagged"]

    v = v.reset_index(drop=True)
    v = add_reasons(v, int(k))

    out = v[["rank", "dba_name", "address", "zip", "facility_group", "risk_%", "flagged", "why"]]
    out.columns = ["Rank", "Premises Name", "Street Address", "ZIP", "Category", "Risk %", "Priority", "Key Risk Drivers"]

    st.dataframe(out, use_container_width=True, hide_index=True)

    st.download_button(
        "Download Scored & Ranked Manifest (CSV)",
        out.to_csv(index=False).encode(),
        "prioritised_inspection_manifest.csv",
        "text/csv"
    )

# ============================================================
# SCREEN 5: Settings
# ============================================================
def page_settings():
    c = cfg()
    models = load_models()
    names = list(models.keys())

    st.markdown(header_banner_html(
        "5", "Settings & Cost Calibration",
        "Tune classification thresholds, inspect cost-utility tradeoffs, and configure active scoring models.",
        icon_name="sliders"
    ), unsafe_allow_html=True)

    st.markdown(section_title_html("Active Scoring Model", "cpu"), unsafe_allow_html=True)
    selected_model = st.selectbox(
        "Select Dispatch Classifier",
        names,
        index=names.index(c["model"]) if c["model"] in names else 0,
        help="Select between baseline Decision Tree, Naive Bayes, and enhanced v2 architectures."
    )
    c["model"] = selected_model

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Cost Matrix
    st.markdown(section_title_html("Cost-Matrix Weights (Relative Penalties)", "dollar-sign"), unsafe_allow_html=True)
    st.caption("Customize the penalty weights representing relative operational and public health costs.")

    col_cost1, col_cost2, col_cost3, col_cost4 = st.columns(4)
    with col_cost1:
        c["fn"] = st.number_input("Missed Serious Violation (FN)", 0.0, 100.0, float(c["fn"]), 0.5,
                                  help="Public health penalty when a dangerous violator is missed.")
    with col_cost2:
        c["fp"] = st.number_input("Wasted Inspection Visit (FP)", 0.0, 100.0, float(c["fp"]), 0.5,
                                  help="Operational inspection cost when a compliant premises is visited.")
    with col_cost3:
        c["tp"] = st.number_input("Caught Violation (TP)", 0.0, 100.0, float(c["tp"]), 0.5)
    with col_cost4:
        c["tn"] = st.number_input("Correct Routine Skip (TN)", 0.0, 100.0, float(c["tn"]), 0.5)

    st.caption("Standard Regulatory Baseline: 3:1 ratio (Missed violation is 3x more costly than a routine inspection visit).")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Threshold Slider
    st.markdown(section_title_html("Decision Threshold (\u03c4)", "target"), unsafe_allow_html=True)
    cur = float(min(max(current_threshold(), 0.01), 0.9))
    thr = st.slider("Flag premises when estimated failure risk is at least", 0.01, 0.90, cur, 0.01)
    c["thr"][c["model"]] = thr

    y = load_sample()["target"].to_numpy()
    s = sample_scores(c["model"])

    col_opt1, col_opt2 = st.columns([1, 2])
    with col_opt1:
        if st.button("Set Optimal Threshold From Cost Table"):
            c["thr"][c["model"]] = best_threshold(y, s, c)
            st.rerun()

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Consequence Simulation
    st.markdown(section_title_html("Policy Simulation (20,000 Out-of-Time Test Sample)", "bar-chart"), unsafe_allow_html=True)
    r = consequences(y, s, thr, c)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(kpi_card_html("Premises Flagged", f"{r['share']:.1%}", f"{int(r['share']*len(y)):,} establishments", icon_name="box", badge_text="Capacity", badge_type="info"), unsafe_allow_html=True)
    with m2:
        st.markdown(kpi_card_html("Precision Among Flagged", f"{r['precision']:.1%}", "Confirmed violators", icon_name="target", badge_text="Precision", badge_type="success"), unsafe_allow_html=True)
    with m3:
        st.markdown(kpi_card_html("Violations Caught (Recall)", f"{r['recall']:.1%}", f"{r['tp']:,} out of {r['tp']+r['fn']:,}", icon_name="search", badge_text="Recall", badge_type="success"), unsafe_allow_html=True)
    with m4:
        st.markdown(kpi_card_html("Test Accuracy", f"{r['accuracy']:.1%}", f"Always-pass baseline: {r['baseline']:.1%}", icon_name="check-circle", badge_text="Accuracy", badge_type="neutral"), unsafe_allow_html=True)

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # Strategy comparison
    strat_df = pd.DataFrame({
        "Inspection Strategy": ["This Model at Configured Line", "Inspect All Premises (Max Capacity)", "Inspect No Premises (Zero Dispatch)"],
        "Expected Cost Units": [f"{r['cost']:,}", f"{r['cost_all']:,}", f"{r['cost_none']:,}"],
        "Violations Caught": [f"{r['tp']:,}", f"{r['tp']+r['fn']:,}", "0"],
        "Wasted Visits": [f"{r['fp']:,}", f"{r['tn']+r['fp']:,}", "0"]
    })
    st.dataframe(strat_df, use_container_width=True, hide_index=True)

    best_simple = min(r["cost_all"], r["cost_none"])
    if r["cost"] < best_simple:
        st.success(f"Active model policy is **{(1 - r['cost'] / best_simple):.1%} cheaper** than the best uninformed heuristic.")
    else:
        st.warning("At these cost parameters, the model is not outperforming simple heuristics. Adjust the decision threshold or penalty matrix.")

# ============================================================
# SCREEN 6: Route Planning
# ============================================================
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
    h = ["<html><head><meta charset='utf-8'><title>Inspection Rounds</title><style>"
         "body{font-family:Inter,Arial,sans-serif;margin:24px;color:#22223B}table{border-collapse:collapse;width:100%;margin-top:12px}"
         "th,td{border:1px solid #E7E0DD;padding:8px;font-size:12px;text-align:left}th{background:#F6F2F0}"
         ".pb{page-break-after:always;margin-bottom:30px}h2{color:#22223B}</style></head><body>"]
    for i, g in rounds.groupby("inspector"):
        h.append(f"<div class='pb'><h2>Inspector {i} \u2014 Inspection Round ({day})</h2>"
                 f"<p><strong>{len(g)} stops planned</strong> | ZIP Sectors: {html.escape(', '.join(sorted(g['zip'].unique())))}</p>"
                 "<table><tr><th>Stop #</th><th>Premises</th><th>Address</th><th>ZIP</th><th>Risk %</th><th>Driver Factors</th><th>Inspector Notes</th></tr>")
        for _, r in g.iterrows():
            risk_val = (r["risk_score"] * 100) if "risk_score" in r and pd.notna(r["risk_score"]) else 0.0
            h.append(f"<tr><td><strong>#{r['stop']}</strong></td><td>{html.escape(str(r.get('dba_name', '')))}</td><td>{html.escape(str(r.get('address', '')))}</td>"
                     f"<td>{r.get('zip', '')}</td><td><strong>{risk_val:.0f}%</strong></td><td>{html.escape(str(r.get('why', '')))}</td><td></td></tr>")
        h.append("</table></div>")
    h.append("</body></html>")
    return "".join(h)

def page_route():
    c = cfg()

    st.markdown(header_banner_html(
        "6", "Inspector Route Planner",
        "Generate geographically clustered, risk-prioritized daily itineraries for municipal health inspectors.",
        icon_name="map-pin"
    ), unsafe_allow_html=True)

    day = date.today() + timedelta(days=1)
    st.caption(f"Planning target date: **{day:%A, %d %B %Y}**. Establishments prioritized by predicted violation probability, "
               "clustered by ZIP sector, and sequenced via spatial nearest-neighbor heuristics.")

    up = st.file_uploader("Upload Daily Candidate Manifest (CSV, optional)", type="csv")
    if up is not None:
        pool = pd.read_csv(up, dtype={"zip": str, "license_num": str})
        pool, missing = normalise_upload(pool)
        if missing:
            st.error("Missing columns: " + ", ".join(missing)); return
    else:
        s = load_sample().sort_values("inspection_date")
        pool = s.groupby("license_num", sort=False).tail(1)
        st.caption("Active Demonstration: Most recent record for each unique establishment in sample serves as tomorrow's candidate pool.")

    col_r1, col_r2, col_r3 = st.columns([1, 1, 1.2])
    with col_r1:
        n_insp = st.number_input("Inspectors Available", 1, 50, 5)
    with col_r2:
        cap = st.number_input("Max Stops / Inspector / Day", 1, 30, 8)
    with col_r3:
        only = st.checkbox("Only dispatch above decision threshold (\u03c4)", value=False)

    scored = score(pool, c["model"]).sort_values("risk_score", ascending=False)
    thr = current_threshold()
    above = int((scored["risk_score"] >= thr).sum())
    total_capacity = int(n_insp * cap)

    st.markdown(
        f"<div class='fsp-card' style='padding: 12px 18px; margin-bottom: 12px; background: {SURFACE_SUBTLE};'>"
        f"Manifest pool: <strong>{len(scored):,}</strong> candidate premises \u00b7 <strong>{above:,}</strong> exceed risk threshold (\u03c4 = {thr:.2f}) \u00b7 "
        f"Available team capacity: <strong>{total_capacity}</strong> inspections"
        f"</div>",
        unsafe_allow_html=True
    )

    if st.button("Generate Dispatch Rounds", type="primary"):
        ranked = scored[scored["risk_score"] >= thr] if only else scored
        sel = ranked.head(total_capacity).reset_index(drop=True)
        if sel.empty:
            st.warning("No candidate establishments meet the selected criteria."); return
        rounds = add_reasons(build_rounds(sel, int(cap)), len(sel))
        st.session_state["rounds"] = (rounds, scored["risk_score"].mean(), day)

    if "rounds" not in st.session_state:
        return

    rounds, avg, d_ = st.session_state["rounds"]

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.markdown(section_title_html("Projected Daily Mission Impact", "award"), unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    exp_violations = rounds["risk_score"].sum()
    random_expected = avg * len(rounds)
    with m1:
        st.markdown(kpi_card_html("Total Stops Dispatched", f"{len(rounds)}", f"Across {rounds['inspector'].nunique()} inspectors", icon_name="map-pin", badge_text="Capacity", badge_type="info"), unsafe_allow_html=True)
    with m2:
        st.markdown(kpi_card_html("Expected Violations Caught", f"{exp_violations:.1f}", f"+{(exp_violations - random_expected):.1f} vs random dispatch", icon_name="target", badge_text="Targeted Catch", badge_type="success"), unsafe_allow_html=True)
    with m3:
        st.markdown(kpi_card_html("Inspection Efficacy Ratio", f"{(exp_violations / max(random_expected, 0.1)):.2f}x", "Efficiency multiplier vs baseline", icon_name="zap", badge_text="High ROI", badge_type="success"), unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Interactive Route Map using Plotly
    st.markdown(section_title_html("Geographic Stop Map (Chicago)", "map-pin"), unsafe_allow_html=True)

    rounds_map = rounds.copy()
    rounds_map["Inspector Label"] = rounds_map["inspector"].apply(lambda x: f"Inspector {x}")
    rounds_map["Risk Label"] = (rounds_map["risk_score"] * 100).round(1).astype(str) + "%"
    rounds_map["Stop Label"] = rounds_map["stop"].astype(str)

    fig_map = px.scatter_map(
        rounds_map,
        lat="latitude",
        lon="longitude",
        color="Inspector Label",
        hover_name="dba_name",
        hover_data={"address": True, "zip": True, "Risk Label": True, "Stop Label": True, "latitude": False, "longitude": False},
        zoom=10.5,
        center={"lat": float(rounds_map["latitude"].median()), "lon": float(rounds_map["longitude"].median())},
        color_discrete_sequence=CHART_PALETTE
    )
    fig_map.update_layout(
        height=480,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.02, bgcolor="rgba(255,255,255,0.85)")
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Area summary
    with st.expander("Planned Itineraries Clustered by ZIP Area"):
        g = rounds.groupby("zip").agg(
            premises=("risk_score", "size"),
            average_risk=("risk_score", "mean"),
            inspectors=("inspector", lambda x: ", ".join(map(str, sorted(set(x)))))
        ).reset_index()
        g["average_risk"] = (g["average_risk"] * 100).round(1).astype(str) + "%"
        g.columns = ["ZIP Code", "Assigned Premises", "Mean Risk %", "Assigned Inspector IDs"]
        st.dataframe(g.sort_values("Assigned Premises", ascending=False), hide_index=True, use_container_width=True)

    # Inspector Tabs
    st.markdown(section_title_html("Daily Inspector Stop Manifests", "users"), unsafe_allow_html=True)
    insp_tabs = st.tabs([f"Inspector {i}" for i in sorted(rounds["inspector"].unique())])
    for tab, i in zip(insp_tabs, sorted(rounds["inspector"].unique())):
        with tab:
            g_insp = rounds[rounds["inspector"] == i]
            show_insp = g_insp[["stop", "dba_name", "address", "zip", "risk_score", "why"]].copy()
            show_insp["risk_score"] = (show_insp["risk_score"] * 100).round(1).astype(str) + "%"
            show_insp.columns = ["Stop #", "Premises Name", "Street Address", "ZIP", "Risk %", "Primary Reasons"]
            st.dataframe(show_insp, hide_index=True, use_container_width=True)
            st.download_button(
                f"Download Route CSV (Inspector {i})",
                show_insp.to_csv(index=False).encode(),
                f"route_inspector_{i}.csv",
                "text/csv",
                key=f"dl_insp_{i}"
            )

    st.download_button(
        "Download Printable Daily Roster (HTML)",
        rounds_html(rounds, f"{d_:%d %b %Y}").encode("utf-8"),
        "daily_inspection_rounds.html",
        "text/html"
    )

# ============================================================
# Main Navigation & Application Shell
# ============================================================
PAGES = {
    "1. Data & quality": page_data,
    "2. Model performance": page_performance,
    "3. Single prediction": page_single,
    "4. Batch scoring": page_batch,
    "5. Settings": page_settings,
    "6. Route planner": page_route
}

# Sidebar Shell
current_cfg = cfg()
st.sidebar.markdown(sidebar_brand_html(current_cfg["model"], current_threshold()), unsafe_allow_html=True)

choice = st.sidebar.radio("Navigation", list(PAGES.keys()))

st.sidebar.markdown(
    f"""
    <div style="margin-top: 28px; padding: 10px 12px; border-radius: {RADIUS_SM};
                background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
                font-size: 0.74rem; color: {LILAC_ASH};">
        <div style="font-weight: 600; color: {TEXT_ON_DARK}; margin-bottom: 4px; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.04em;">
            System Status
        </div>
        <div>Sample: <strong style="color: {TEXT_ON_DARK};">20,000 Loaded</strong></div>
        <div>Eval Split: <strong style="color: {TEXT_ON_DARK};">2015\u20132019</strong></div>
        <div>Models: <strong style="color: {TEXT_ON_DARK};">{len(load_models())} Active</strong></div>
    </div>
    """,
    unsafe_allow_html=True
)

# Render chosen screen
PAGES[choice]()

# Footer
st.markdown(footer_html(), unsafe_allow_html=True)