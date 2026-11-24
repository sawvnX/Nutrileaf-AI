# NutriLeaf AI model training

See the root `README.md` for full instructions. Quick steps:

1. Create class folders under `data_raw/`, e.g. `Maize__Healthy`, `Maize__Nitrogen`, `Maize__Phosphorus`, `Maize__Potassium`.
2. Add verified labelled images. Aim for hundreds per class; 10 is only the minimum script threshold.
3. Install `requirements-ml.txt`.
4. Run `python ml/prepare_dataset.py` from the project root, then `python ml/train.py`.
5. Check `evaluation.json` and `confusion_matrix.csv`; do not report only overall accuracy. Review per-class precision/recall and class balance.
6. Restart the app. The model and class names must match.

The training script uses MobileNetV2 transfer learning at 224x224. It applies augmentation to training images, freezes most of the backbone for the classification head, fine-tunes the final layers, checkpoints on validation loss and evaluates on the held-out test split.

The included splitter is deterministic but file-level. For rigorous experiments, manually split by plant/plot/session first to prevent leakage.
