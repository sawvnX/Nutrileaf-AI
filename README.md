# NutriLeaf AI — Final Complete Edition (2026)

**AI-Based Plant Nutrient Deficiency Screening System**  
Developer: **Sawan Kumar** · Biology × Artificial Intelligence

This is the consolidated project package. It brings the application, API, database, AI training/evaluation pipeline, analytics, scan history, export, and project documentation into one release so you do not need to install separate V1/V2/V3/V4 packages.

## What is included

- Responsive multi-page web app: overview, AI scanner, history, analytics, nutrient library, care guide, and project information.
- Leaf image upload, drag-and-drop, and browser camera capture.
- FastAPI backend with image validation and SQLite scan history.
- MobileNetV2 transfer-learning pipeline with augmentation, fine-tuning, early stopping, best-checkpoint saving, and held-out test evaluation.
- Top-3 class candidates, confidence display, model metadata, classification report, and confusion matrix export.
- CSV history export and browser print / Save as PDF.
- Windows and macOS/Linux launch scripts.
- Dataset guide, academic project report outline, and viva preparation notes.

## Important truth about AI readiness

The web application runs immediately. **A trained nutrient-deficiency model is not bundled**, because a real model requires a properly labelled dataset and training/evaluation on that data. Until you train and install a model, the scanner intentionally reports that AI is unavailable; it does not invent a prediction. Model accuracy is never pre-filled or fabricated.

Image-only nutrient screening has scientific limits: visual symptoms overlap with disease, pests, water stress, cultivar, soil pH, and multiple deficiencies. Treat model output as a screening clue, not a laboratory diagnosis or fertilizer prescription. Confirm important decisions with soil/tissue testing or an agricultural expert.

## Run on Windows (recommended)

1. Install **Python 3.11 or 3.12** from the official Python website. During installation, select **Add Python to PATH**.
2. Extract `NutriLeaf-AI-Final-2026.zip` completely.
3. Open the extracted `NutriLeaf-AI` folder.
4. Double-click `START_NUTRILEAF.bat`. First run creates `.venv` and installs dependencies; internet is required for this one-time setup.
5. Open `http://127.0.0.1:8000` if it does not open automatically.
6. Keep the terminal window open while using the app. Press `Ctrl+C` in that window to stop the server.

### macOS / Linux

```bash
chmod +x START_NUTRILEAF_MAC_LINUX.sh
./START_NUTRILEAF_MAC_LINUX.sh
```

### Manual start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

## Train the actual AI model

1. Read `DATASET_GUIDE.md` and verify dataset licence, labels, and crop scope.
2. Put images into one folder per label under `ml/data_raw/`. Example:

```text
ml/data_raw/
  Maize__Healthy/
  Maize__Nitrogen/
  Maize__Phosphorus/
  Maize__Potassium/
  Maize__Magnesium/
```

3. Activate the project virtual environment and install ML dependencies:

```bash
pip install -r requirements-ml.txt
```

4. Prepare train/validation/test folders:

```bash
python ml/prepare_dataset.py
```

5. Train and evaluate:

```bash
python ml/train.py
```

On Windows, `TRAIN_AI_MODEL.bat` performs these steps. Training downloads ImageNet MobileNetV2 weights on first run, so internet is needed. A GPU is optional; CPU training can take considerably longer. TensorFlow compatibility is best with Python 3.10–3.12.

### Training outputs

- `ml/nutrileaf_model.keras` — trained model used by the scanner.
- `ml/class_names.json` — exact output class order.
- `ml/evaluation.json` — held-out test metrics and per-class precision/recall/F1.
- `ml/confusion_matrix.csv` — class confusion matrix.
- `ml/model_metadata.json` — architecture, training timestamp, class list, and test accuracy.

Restart the web server after training. Keep the model and matching JSON metadata files together.

## Dataset quality rules

- Prefer hundreds of labelled images per class; the preparation script requires at least 10 only as a technical minimum, not as a scientific recommendation.
- Include healthy leaves and relevant deficiency classes for each crop model.
- Keep related images from the same plant, plot, video burst, or capture session in only one split. The included splitter is file-level and cannot detect plant identity. For research-grade testing, manually create independent plant/session splits.
- Avoid mixing crop classes unless intentionally training a multi-crop model with balanced data.
- Never infer a class label from a model prediction and then use it as ground truth.
- Record dataset source, licence, collection conditions, and class definitions in your report.

## API routes

- `GET /api/health` — backend and model readiness.
- `GET /api/model-info` — classes, metadata, evaluation report.
- `GET /api/nutrients` — nutrient reference library.
- `POST /api/scan` — image classification (requires trained model).
- `GET /api/history` — recent scan records.
- `DELETE /api/history/{scan_id}` — delete a scan.
- `GET /api/stats` — dashboard statistics.
- `GET /api/export.csv` — download history.
- `GET /docs` — interactive API documentation.

## Troubleshooting

- **Python not found:** install Python 3.11/3.12 and enable Add Python to PATH; reopen the terminal.
- **Port 8000 busy:** stop the other process or launch with `--port 8001`, then open `http://127.0.0.1:8001`.
- **Camera blocked:** allow browser camera access on localhost; image upload remains available.
- **AI not trained:** expected on a fresh install; follow the training steps above.
- **TensorFlow installation fails:** use a fresh Python 3.10–3.12 environment and check TensorFlow platform compatibility. The core app does not require TensorFlow.
- **Wrong crop warning:** choose the crop represented by the installed model or train a crop-specific model.

## Academic integrity

Do not claim a detection accuracy until the model has been trained and tested on a genuinely independent, correctly labelled test set. Report per-class metrics and limitations, not accuracy alone. This is an educational prototype, not a certified agricultural diagnostic product.
