# NutriLeaf AI — Dataset and Model Training Guide

## Recommended first experiment

Start with one crop and a small, well-defined set of labels rather than attempting every crop at once. For example, a maize model may use `Maize__Healthy`, `Maize__Nitrogen`, `Maize__Phosphorus`, `Maize__Potassium`, and `Maize__Magnesium` only if the source dataset genuinely labels those categories. Do not create labels for nutrients absent from the dataset.

## Folder naming

Use `<Crop>__<Class>` with two underscores. Examples: `Tomato__Iron`, `Rice__Nitrogen`, `Banana__Healthy`. The folder name becomes the model class. Use `Healthy` for a healthy reference class.

## Image collection checklist

- Correctly labelled by a qualified source or dataset metadata.
- Multiple plants, plots, growth stages, backgrounds, and lighting conditions.
- Similar number of images per class where possible.
- No corrupt files, duplicates, collages, screenshots of text, or unrelated objects.
- Dataset licence permits the intended academic use.
- Keep a record of source URL, citation, access date, and licence.

## Prevent data leakage

The included `prepare_dataset.py` splits individual image files randomly. If multiple images show the same plant or come from one recording session, they may land in both train and test sets and inflate the reported score. For a stronger experiment, manually group data by plant, plot, farm, or capture session and create separate train/validation/test folders. Never use the test set for tuning.

## Run commands

```bash
pip install -r requirements-ml.txt
python ml/prepare_dataset.py
python ml/train.py
```

Training uses MobileNetV2 with ImageNet initialization, a frozen feature extractor phase, fine-tuning of the final backbone layers, image augmentation, early stopping, and best validation-loss checkpointing. The final metrics are computed on the held-out test folder.

## Interpret results

- Accuracy alone can hide poor performance on minority classes.
- Review per-class precision, recall, F1-score, and confusion matrix.
- A high softmax score is not automatically a calibrated probability.
- Test images should represent plants and conditions not seen during training.
- If test performance is weak or classes are confused, collect better data, rebalance labels, and rerun the experiment.

## Why model predictions are only screening

Nitrogen, sulphur, iron, magnesium, and other deficiencies can all cause chlorosis under different conditions. Water stress, root damage, pathogens, pests, cultivar, age, and soil pH can produce similar appearances. Confirm with soil/tissue testing and expert assessment before fertilizer application.
