# Food Safety Inspection Prioritiser (DSC306, Project 16)

Ranks food premises by predicted risk of a serious violation and builds a daily route for each inspector.

## Requirements
- Python 3.11 (3.10 or newer should also work)
- About 500 MB of free disk space

## How to run (after downloading)

1. Unzip the project (or `git clone` it) and open a terminal **inside the project folder**, the one containing `app.py`.

2. Create and activate a virtual environment.

   **Windows (PowerShell):**
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

   **Mac / Linux:**
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Start the app (this is the single start command):
   ```
   streamlit run app.py
   ```
   The browser opens at http://localhost:8501. If it does not, open that address yourself.

No paths need editing. The demo data (`data/app_sample.csv`) and the trained models (`models/`) are included.

## Using the app
1. **Data & quality**: audit report, data preview, cleaned-data download.
2. **Model performance**: model comparison, ROC curve, confusion matrix, drift chart and retraining rule.
3. **Single prediction**: describe one premises, get its risk and the reasons.
4. **Batch scoring**: upload a CSV (a template is downloadable on the page) and get a ranked table.
5. **Settings**: choose the model, move the risk line, edit the cost matrix.
6. **Route planner**: set inspectors and capacity, get a round per inspector, print it.

## Troubleshooting
- `streamlit` not recognised: the virtual environment is not active. Repeat step 2.
- Port busy: `streamlit run app.py --server.port 8502`
- Compatibility note: The application includes internal compatibility shims supporting Python 3.11 up to Python 3.14+ and scikit-learn 1.5 through 1.9+.

## Improved Model Pipeline (v2)
To run the extended feature engineering and retraining pipeline with TimeSeriesSplit validation:
```
python src/train_v2.py
```
This produces `models/neural_network_v2.joblib` (AUC: 0.663, Recall: 52.9%, P@5%: 41.9%) and updates `docs/model_results_v2.csv`.

## Rebuild everything from the raw data (optional)
Download the Chicago Food Inspections CSV from the Chicago Data Portal and save it as `data/raw_full.csv`, then run in order:
```
python src/clean.py
python src/features.py
python src/train.py
python src/drift.py
python src/compare_reduction.py
python src/cost_sensitivity.py
python src/make_sample.py
```

## Project layout
- `app.py`: the Streamlit web application
- `src/`: cleaning, features, training (v1 & v2), drift, explanations, UI theme
- `models/`: trained models (v1 baseline and v2 improved)
- `data/`: demo sample files and cleaned datasets
- `docs/`: audit report, benchmark results, data dictionary, leakage statement, design decisions

## Method summary
Time split: train 2010–2014, test 2015–2019 (strictly preventing chronological data leakage). Models: decision tree (used for explainability), naive Bayes, and neural network (v1 & v2). Source data: Chicago Food Inspections open data (2010–2019).