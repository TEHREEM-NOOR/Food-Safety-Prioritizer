# Columns not known when the user asks the question

The supervisor plans tomorrow's inspections BEFORE any inspection happens.

| Column | Decision | Reason |
|---|---|---|
| Results | EXCLUDED (it is the target) | The outcome of the inspection we are predicting |
| Violations | EXCLUDED for the current inspection | Written during the inspection; it contains the answer |
| Inspection ID | EXCLUDED (identifier) | No predictive meaning; assigned in order |
| Inspection Type | EXCLUDED | Re-inspections and complaint visits are triggered by earlier failures or events not known when ranking all premises |
| Inspection Date (year) | EXCLUDED as a feature | Using year would hide concept drift; month is kept |
| Violations of PREVIOUS inspections | ALLOWED | Already known on the day (last_violation_count, avg_past_violations) |
| Past results of the same premises | ALLOWED | Computed from strictly earlier inspections only |
| DBA / AKA Name, Address | Display only | Used to show the premises in the app, not as predictors |

Label: target = 1 if Results = "Fail". Pass and Pass w/ Conditions = 0. Rows with
outcomes that are not a pass/fail verdict (Not Ready, Out of Business, No Entry,
Business Not Located) are removed.