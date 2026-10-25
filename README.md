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
- Model loading error or version warning: install the exact versions in `requirements.txt`. The saved models need the same scikit-learn version.
- Port busy: `streamlit run app.py --server.port 8502`

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
- `app.py`: the web application
- `src/`: cleaning, features, training, drift, explanations
- `models/`: trained models
- `data/`: demo sample files
- `docs/`: audit report, results, data dictionary, leakage statement, design decisions

## Method summary
Time split: train 2010-2014, test 2015-2019. Models: decision tree (used for explanations), naive Bayes, neural network. Source data: Chicago Food Inspections open data.