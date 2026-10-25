# Design decisions

## Label
target = 1 if Results = "Fail" (Pass and Pass w/ Conditions = 0). Rows that are not a pass/fail
verdict (Not Ready, Out of Business, No Entry, Business Not Located; 25,224 rows) are removed
because they carry no information about food safety.

## Rescaling per model family
- Decision tree: none. Splits depend on order only, not on scale.
- Naive Bayes: no rescaling; numeric attributes discretised into 5 quantile (equal-frequency) bins
  then one-hot, because Bernoulli NB needs discrete features. Quantile bins avoid empty bins on skewed counts.
  Zero-heavy columns collapse to fewer bins, which is expected.
- Neural network: StandardScaler. Gradient descent is sensitive to feature scale.

## Dimensionality reduction vs feature selection (same decision tree, time-ordered CV)
All features CV AUC 0.678 +/- 0.005 (test 0.662); top-15 ANOVA selection 0.675 +/- 0.008 (0.647);
PCA 6 components 0.656 +/- 0.011 (0.634). We keep the original features: they are best and explainable.

## Hyper-parameters
Grid search, scored by AUC, with 5-fold TimeSeriesSplit on the training years only. Test set used once.

## Metrics (beyond accuracy) and why
- AUC: ranks premises regardless of threshold, which is how the product is used.
- Recall: share of serious violations caught. A miss exposes the public.
- Precision@top 5%: capacity is fixed, so what matters is how rich the top of the list is.
  Result: 36-39% of the top 5% fail against a 21.8% base rate (about 1.7x lift).

## Cost matrix and threshold
Missed failure : wasted visit = 3 : 1 (a failed premises is re-inspected anyway, so a miss is costly
but not unbounded). Threshold chosen by minimising expected cost on 2014 (validation slice of train).
Sensitivity from 2:1 to 10:1 is in docs/cost_sensitivity.csv. At 10:1 the model flags 84% of premises
and barely beats "inspect everyone".

## Drift
Fixed model trained on 2010-2012: AUC 0.691 at 3 months to 0.645 at 81 months (about -0.006/year).
Retraining on the previous 3 years averages 0.676 vs 0.661. Rule: retrain every 12 months, or when
the monthly fail rate moves more than 3 points. Half-year AUCs are noisy (about +/-0.005).

## Limitations (state these yourself)
- Test AUC is about 0.66: modest signal, not a strong model.
- Accuracy at the chosen threshold (0.71) is below the 78% baseline by design.
- Re-inspections (mostly pass, scheduled by rule) are mixed into training and dilute the signal.
  A routine-only scope would be cleaner.
- Naive Bayes is weak (test AUC 0.53) and poorly calibrated; correlated history features violate its independence assumption.
- Reasons come from the decision tree, even when another model is selected.
- validate() fails on raw partly because derived columns do not exist yet, not only because of bad values.
- Same-day inspections of one premises are ordered by inspection_id. Premises = licence number.
- The demo route plan replays historical records; in service, history features must be refreshed nightly.
- The ZIP route grouping is a heuristic (nearest-neighbour inside each ZIP), not an optimal route.