# Data dictionary (features.csv, one row per inspection)
Measurement types follow Lecture 2.

| Column | Type | Plausible range | Role |
|---|---|---|---|
| inspection_id | Nominal (identifier) | unique integer | Identifier. Not used. |
| inspection_date | Interval | 2010-01-01 to 2019-12-04 | Used for the time split only. |
| license_num | Nominal (identifier) | integer text | Premises key for history. Not a predictor. |
| dba_name, address | Nominal (text) | any | Display only. |
| risk_level | Ordinal | 1 (high), 2, 3 (low) | Explanatory. |
| latitude | Interval | 41.6 to 42.1 | Explanatory. |
| longitude | Interval | -87.95 to -87.5 | Explanatory. |
| month | Interval (cyclic) | 1 to 12 | Explanatory. |
| past_inspections | Ratio (count) | 0 to ~100 | Explanatory (earlier inspections only). |
| past_fails | Ratio (count) | 0 to past_inspections | Explanatory (earlier only). |
| past_fail_rate | Ratio | 0 to 1 | Explanatory (earlier only). |
| last_result_fail | Nominal (binary) | 0/1 | Explanatory (previous inspection). |
| days_since_last | Ratio | 0 to ~3,600 | Explanatory (0 = no history). |
| has_history | Nominal (binary) | 0/1 | Explanatory. |
| last_violation_count | Ratio (count) | 0 to ~40 | Explanatory (previous inspection). |
| avg_past_violations | Ratio | 0 to ~40 | Explanatory (earlier only). |
| facility_group | Nominal | 13 groups (top 12 types + other) | Explanatory. |
| zip | Nominal | 5-digit text or "unknown" | Explanatory, and route area. |
| target | Nominal (binary) | 0/1 | **Target**: 1 = Results is Fail. |

Columns in clean.csv not carried into features: results and violations of the current inspection
(**must not be used**, they contain the answer), inspection_type, aka_name, city, state, address
metadata columns, and the four provenance columns (zip_src, geo_src, risk_src, facility_type_src).