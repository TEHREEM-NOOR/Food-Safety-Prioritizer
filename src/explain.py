import numpy as np
from features import FEATURES

LABELS = {
    "past_fail_rate": ("its past failure rate", lambda v: f"{v*100:.0f}%"),
    "past_fails": ("its number of earlier failed inspections", lambda v: f"{v:.0f}"),
    "past_inspections": ("its number of earlier inspections", lambda v: f"{v:.0f}"),
    "days_since_last": ("days since its last inspection", lambda v: f"{v:.0f}"),
    "avg_past_violations": ("its average violations per past inspection", lambda v: f"{v:.1f}"),
    "last_violation_count": ("violations at its last inspection", lambda v: f"{v:.0f}"),
    "risk_level": ("its city risk level (1 = high, 3 = low)", lambda v: f"{v:.1f}"),
    "month": ("the month of the year", lambda v: f"{v:.0f}"),
    "latitude": ("its north-south location", lambda v: f"{v:.3f}"),
    "longitude": ("its east-west location", lambda v: f"{v:.3f}"),
}

def _phrase(feat, thr, went_left):
    if feat == "past_inspections":
        return "it has not been inspected before" if went_left else "it has been inspected before"
    if feat == "has_history":
        return "it has no earlier inspection on record" if went_left else "it has earlier inspections on record"
    if feat == "last_result_fail":
        return "it did not fail its last inspection" if went_left else "it failed its last inspection"
    for prefix, noun in (("facility_group_", "facility type"), ("zip_", "ZIP code")):
        if feat.startswith(prefix):
            name = feat[len(prefix):]
            return f"its {noun} is not {name}" if went_left else f"its {noun} is {name}"
    label, fmt = LABELS.get(feat, (feat.replace("_", " "), lambda v: f"{v:.2f}"))
    return f"{label} is {fmt(thr)} or lower" if went_left else f"{label} is above {fmt(thr)}"

def explain(pipe, row_df, max_reasons=4):
    """Return plain-language reasons for ONE premises (a one-row DataFrame) using the tree's decision path."""
    pre, tree = pipe.named_steps["pre"], pipe.named_steps["clf"]
    X = pre.transform(row_df[FEATURES])
    names = pre.get_feature_names_out()
    t = tree.tree_
    reasons = []
    for n in tree.decision_path(X).indices:
        if t.children_left[n] == -1: continue
        j = t.feature[n]
        went_left = X[0, j] <= t.threshold[n]
        reasons.append(_phrase(names[j].split("__", 1)[1], t.threshold[n], went_left))
    return reasons[:max_reasons]