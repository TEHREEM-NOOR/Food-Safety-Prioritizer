# STYLE.md — Food Safety Inspection Prioritiser
## UI Redesign Specification

**Purpose:** Redesign the Streamlit interface into a polished, cohesive, university-project-ready public-health analytics dashboard while preserving all existing data, ML, and operational behavior.

**Design direction:** Soft Editorial Analytics  
**Framework:** Existing Streamlit application  
**Primary constraint:** Visual redesign only. Do not alter model behavior or business logic.

---

## 1. Design principles

1. **Professional before decorative.** The application should feel like a credible public-health analytics tool, not a generic AI-generated dashboard template.
2. **Clear hierarchy.** Make page titles, key metrics, controls, charts, and results easy to scan.
3. **Consistent components.** Reuse the same spacing, typography, card, button, table, and section-heading patterns across all six screens.
4. **Data readability first.** Model metrics, confusion matrices, ROC curves, tables, and route information must remain readable at normal desktop sizes.
5. **Subtle personality.** Use the muted indigo–mauve palette, small line icons, and restrained animation. Avoid excessive gradients, emojis, badges, shadows, and decorative banners.
6. **Preserve trust.** Never invent, hardcode, or cosmetically alter data values, model results, risk scores, thresholds, or claims.

## 2. Color tokens

Use these tokens consistently. Do not introduce extra accent colors without a clear semantic or accessibility reason.

```css
:root {
  /* Brand palette */
  --space-indigo: #22223B;
  --dusty-grape: #4A4E69;
  --lilac-ash: #9A8C98;
  --almond-silk: #C9ADA7;
  --parchment: #F2E9E4;

  /* Interface surfaces */
  --app-background: #FAF8F6;
  --surface: #FFFFFF;
  --surface-subtle: #F6F2F0;
  --border: #E7E0DD;
  --border-strong: #D6CBC8;

  /* Text */
  --text-primary: #22223B;
  --text-secondary: #625E6A;
  --text-muted: #77717B;
  --text-on-dark: #FFFFFF;

  /* Semantic status colors — use only for actual status meaning */
  --success: #287A58;
  --success-soft: #E7F3EC;
  --warning: #946200;
  --warning-soft: #FBF1D8;
  --danger: #B4233C;
  --danger-soft: #FBE9EC;
  --info: #365C87;
  --info-soft: #EAF0F7;

  /* Shape and depth */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --shadow-card: 0 2px 10px rgba(34, 34, 59, 0.045);
  --shadow-hover: 0 5px 16px rgba(34, 34, 59, 0.08);
}
```

### Color usage rules
- Use `--space-indigo` for the sidebar, primary headings, and primary action buttons.
- Use `--dusty-grape` for secondary actions, active navigation accents, and chart series.
- Use `--lilac-ash` sparingly for secondary details and muted accents.
- Use `--almond-silk` for restrained decorative highlights, not for small text on a white background.
- Use `--parchment` for subtle selected states or warm section accents, not as the default text color.
- Use `--app-background` as the main content background and `--surface` for cards and form surfaces.
- Use semantic status colors only to communicate actual outcomes or status. Always include a text label; never rely on color alone.
- Maintain accessible contrast, especially for small text and button labels. If a token combination fails contrast, use a darker/lighter variant or a different surface rather than forcing the palette.
- Do not use the palette to disguise a model risk level or to make weak results appear stronger.

## 3. Typography

- Preferred typeface: **Inter**, with a system sans-serif fallback.
- If Inter is already loaded, reuse it. Otherwise use a sensible fallback and do not make the app depend on an external font request to function.
- Use a restrained type scale:
  - Page title: approximately 1.8–2.2rem, medium/semibold weight.
  - Section title: approximately 1.15–1.4rem, semibold.
  - Body text: approximately 0.9–1rem.
  - Supporting labels: approximately 0.75–0.85rem, with adequate contrast.
  - KPI value: approximately 1.5–2rem, semibold/bold.
- Avoid all-caps labels everywhere. Use them only for short, secondary KPI labels where they remain legible.
- Avoid huge titles that wrap unnecessarily. Keep headings concise and ensure responsive wrapping.

## 4. Layout and spacing

- Use a consistent spacing scale based on 4px: 4, 8, 12, 16, 20, 24, 32, 40, 48.
- Keep the main content width comfortable for data tables and charts. Avoid both excessive full-width stretching and narrow compressed chart columns.
- Use compact page headers instead of repeated oversized hero banners. Each page header should contain:
  - A small consistent line icon.
  - A clear page title.
  - One short explanatory sentence.
  - Optional compact status text only when useful.
- Remove redundant decorative badges, page-number pills, and repeated icon ornaments.
- Align cards and form controls to a common grid.
- Use whitespace to separate meaningful sections, not to create unnecessarily long pages.
- Avoid nested cards unless they represent a genuinely separate task or information group.

## 5. Sidebar and navigation

- Use a **Space Indigo** sidebar with white/light text.
- Brand area: compact shield/food-safety mark, product name, and optional small subtitle.
- Active navigation: a restrained Dusty Grape surface or indicator; use a clear text label and selected state.
- Inactive navigation: muted light text with adequate contrast.
- Keep all six existing navigation destinations and their order:
  1. Data & Quality
  2. Model Performance
  3. Single Prediction
  4. Batch Prioritisation
  5. Settings & Cost Calibration
  6. Inspector Route Planner
- Keep system status visible but compact. Preserve the actual sample count, evaluation split, and number of loaded models based on the existing runtime state.
- Do not create fake live indicators or claim live connectivity when no such check exists.
- Do not hide essential Streamlit controls just to make a screenshot cleaner.

## 6. Shared components

### Page header
- Compact, consistent, no giant gradient panel.
- Use the same title hierarchy and spacing on every screen.
- Icons should come from one consistent line-icon family if the project already includes one. Do not add a dependency solely for decorative icons.
- Prefer a small icon beside the title rather than a large emoji.

### KPI cards
- Use white surfaces, subtle borders, small/moderate rounding, and minimal shadows.
- Use the same padding, label position, value size, and supporting text placement across screens.
- Keep the number visually prominent but do not exaggerate it.
- Show units and context where needed.
- Avoid adding unsupported comparisons, deltas, or status badges.

### Buttons and controls
- Primary action: Space Indigo background, white text, clear focus state.
- Secondary action: white or subtle surface with indigo text and border.
- Keep labels concise and action-oriented.
- Maintain existing Streamlit input types, keys, values, callbacks, validation, and session-state behavior.
- Do not replace functional widgets with static HTML lookalikes.
- Do not remove confirmation or validation messages.

### Tables
- Use readable font sizes and row spacing.
- Align numeric values consistently; use appropriate decimal precision without changing underlying values.
- Preserve sorting, filtering, selection, pagination, and download behavior wherever already present.
- Avoid truncating essential values. If horizontal scrolling is necessary, make it usable.
- Use semantic status text in addition to any colored status indicators.
- Do not invent or reorder data in a way that changes its meaning.

### Charts
- Keep Plotly and existing chart-generation logic unless a genuine visual defect requires a narrowly scoped presentation change.
- Use Space Indigo and Dusty Grape as primary series colors; use muted neutral colors for secondary series.
- Reserve semantic green/amber/red for meaningful status or outcomes.
- Increase chart height/width where needed. Prevent legend, axis, hover-label, and confusion-matrix annotation overlap.
- Keep axes, units, titles, and legends legible.
- Never change the data, evaluation sample, threshold, aggregation, or metric calculation just to make a chart look better.
- Check charts at the actual application viewport, not only in a standalone figure.

### Expanders, alerts, and feedback
- Use expanders for secondary methodology, data dictionary, and advanced explanations when appropriate.
- Preserve important caveats and methodology notes.
- Alerts must have clear labels and adequate contrast.
- Loading and error states should explain what is happening and how the user can recover.
- Respect reduced-motion preferences.

## 7. Screen-by-screen requirements

### Screen 1 — Data & Quality
**Goal:** Make dataset provenance, quality, and distributions easy to understand.

Recommended order:
1. Compact page header.
2. Four existing data-quality/dataset KPI cards.
3. Data-quality audit table.
4. Two balanced distribution charts.
5. Dataset explorer in a clearly separated section.
6. Data dictionary in an expander.

Requirements:
- Keep the existing audit data and source attribution.
- Preserve dataset filters and CSV download.
- Keep data dictionary content intact.
- Tables must not become unreadably small or overly tall.
- Do not label a dataset “verified” unless the existing validation results support that claim.

### Screen 2 — Model Performance
**Goal:** Make the evaluation credible and easy to present during the midterm.

Recommended order:
1. Compact page header.
2. Existing evaluation-methodology callout.
3. Four KPI cards: Test ROC-AUC, Recall, Precision@Top 5%, and inspection cost, using existing results.
4. Model benchmark table.
5. ROC curve and confusion matrix in balanced, sufficiently wide panels.
6. Concept-drift chart.
7. Feature-selection, cost-sensitivity, and methodological details in expanders.

Requirements:
- Preserve the current chronological train/test split and evaluation methodology.
- Use existing model result files as the source of displayed metrics.
- Fix overlapping confusion-matrix labels and undersized ROC charts.
- Clearly distinguish validation results from final test results.
- Do not describe an improvement as statistically significant unless tested.
- Do not make accuracy the sole headline metric for an imbalanced prioritisation task.
- Do not change model predictions or evaluation metrics as part of the UI redesign.

### Screen 3 — Single Prediction
**Goal:** Make the prediction form easy to complete and the result easy to interpret.

Recommended order:
1. Compact page header.
2. Two aligned sections:
   - Establishment Profile.
   - Inspection Track Record.
3. Primary assessment button.
4. Result panel shown after a prediction is actually run.
5. Existing explanation/reasoning section.

Requirements:
- Preserve every current input, default, validation, and feature mapping.
- Preserve model selection and threshold behavior as currently implemented.
- Show probability, decision/priority label, and existing explanation.
- Use text and numerical values as well as color to communicate risk.
- Do not imply a prediction is a guarantee or a confirmed inspection outcome.

### Screen 4 — Batch Prioritisation
**Goal:** Support reliable bulk scoring and efficient review of ranked premises.

Recommended order:
1. Compact page header.
2. Upload panel and template download.
3. Required-column guidance and validation feedback.
4. Existing summary KPI cards.
5. Risk-score distribution chart.
6. Compact aligned filter toolbar.
7. Ranked results table.
8. Existing CSV export action.

Requirements:
- Preserve uploaded-file validation and the demo-sample option.
- Keep all current required/optional columns and their semantics.
- Preserve filters, ranking, risk threshold, explanation logic, and downloads.
- Do not silently discard invalid records; retain existing warnings or improve their clarity.
- Ensure long tables remain usable and important columns are not hidden.

### Screen 5 — Settings & Cost Calibration
**Goal:** Separate model configuration from policy consequences.

Recommended order:
1. Compact page header.
2. Active model selector.
3. Cost-matrix controls.
4. Decision threshold slider and existing optimal-threshold action.
5. Policy-simulation KPI cards.
6. Strategy comparison table.
7. Existing cost comparison summary.

Requirements:
- Preserve the existing cost definitions and calculation formulas.
- Preserve threshold-slider behavior and session state.
- Do not claim the threshold is optimal unless it is calculated from the intended validation data under the existing method.
- Keep the distinction between configurable policy simulation and held-out test evaluation clear.
- Do not use the test set to retune the threshold as part of the UI redesign.

### Screen 6 — Inspector Route Planner
**Goal:** Make dispatch configuration, map, and inspector assignments operationally clear.

Recommended order:
1. Compact page header.
2. Manifest upload and existing demonstration-pool description.
3. Aligned controls for inspector count, stops per inspector, and threshold filtering.
4. Candidate-pool and capacity summary.
5. Primary “Generate Dispatch Rounds” action.
6. Route/map output after generation.
7. Inspector-wise manifests, summary tables, and print/CSV exports.

Requirements:
- Preserve candidate-pool logic, risk scoring, inspector capacity, route sequencing, map fields, and exports.
- Do not imply road-optimal routing when the existing implementation uses straight-line/Euclidean distance or a nearest-neighbor heuristic.
- Keep map labels and hover details readable.
- Preserve the actual planning date logic and clearly label demo data where applicable.

## 8. Animation and interaction

Use restrained motion only:
- Short fade-in for newly displayed page content where compatible.
- Smooth color/border/shadow transitions on buttons and cards.
- Subtle hover elevation for clickable cards only.
- Gentle result reveal after a completed action if it does not interfere with Streamlit reruns.
- Respect `prefers-reduced-motion: reduce`.
- Keep animations short and avoid large movement.

Do not:
- Add continuous animation or bouncing elements.
- Animate every item independently.
- add heavy JavaScript or a new frontend framework.
- make functional elements appear clickable if they are not.
- use animation as a replacement for clear loading/progress feedback.

## 9. Responsive behavior and accessibility

- Prioritise the desktop/laptop viewport used for the midterm presentation.
- At narrower widths, stack multi-column layouts rather than squeezing controls or charts.
- Avoid clipped text, overlapping labels, horizontal overflow at the page level, and inaccessible controls.
- Keep form labels and help text visible.
- Maintain visible keyboard focus.
- Do not rely on color alone for success, warning, failure, or priority.
- Use adequate contrast for text, especially small labels on muted surfaces.
- Respect reduced-motion preferences.

## 10. Strict functionality-preservation rules

**This is a UI-only task.**

Do not modify:
- `src/train.py`, `src/train_v2.py`, feature engineering, or data-cleaning logic.
- Model artifact files or model serialization.
- Prediction/scoring calculations, threshold values, cost formulas, or evaluation methodology.
- Dataset contents, filtering semantics, split dates, or target definitions.
- Route-planning calculations or assignment logic.
- Data import/export schemas or column names.
- Existing widget keys, callback semantics, and session-state contracts unless a verified UI defect makes a minimal change unavoidable.

Prefer changes to:
- `src/ui_theme.py` or the existing theme/style module.
- CSS and presentation-only Plotly layout properties.
- Layout grouping, headings, helper text, spacing, and component presentation in `app.py`.

Before editing:
1. Inspect the current repository and Git diff/status.
2. Identify the current theme entry point and all six screen sections.
3. Create a backup or use a dedicated Git branch/commit before substantial changes.
4. Do not overwrite user changes or discard uncommitted work.
5. Keep changes focused and explain any unavoidable non-visual edit.

## 11. Verification checklist

After implementation, run all checks supported by the repository:

- [ ] Python syntax/compilation succeeds.
- [ ] App imports and starts successfully.
- [ ] All six screens are reachable.
- [ ] All existing models load and produce scores.
- [ ] Single prediction works with valid inputs.
- [ ] Batch upload, validation, filtering, and CSV download work.
- [ ] Threshold and cost controls recalculate as before.
- [ ] Route generation respects configured inspector capacity.
- [ ] Map and route exports render successfully.
- [ ] Model metrics match the existing result files.
- [ ] ROC curve and confusion matrix labels are readable.
- [ ] No new console errors or missing dependency issues.
- [ ] Screens are checked at a normal desktop viewport and a narrower viewport.
- [ ] Reduced-motion behavior is respected where implemented.

If a check cannot be run, report it as **not verified** rather than claiming it passed.

## 12. Completion report required from the agent

When finished, report:
1. Files changed.
2. Visual changes made on each of the six screens.
3. Functionality explicitly preserved.
4. Commands and tests actually run, with pass/fail results.
5. Any checks not run and why.
6. Any remaining visual limitations or known issues.

Do not claim the redesign is complete based on code edits alone. Confirm the app starts and inspect the rendered screens if browser/UI verification is available.

---

## Final acceptance criteria

The redesign is successful only if:
- The six screens share one consistent visual identity.
- The UI is cleaner, more readable, and less repetitive than the current version.
- Charts and tables are legible at presentation size.
- Animations are subtle and do not interfere with use.
- Existing application behavior and ML outputs remain unchanged.
- The agent reports only tests and results that were actually verified.
