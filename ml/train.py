"""Train and evaluate NutriLeaf AI using crop-specific labelled leaf images.

Run: python ml/train.py
Input: ml/data_split/{train,validation,test}/<Crop>__<Nutrient>/*.jpg
Example class folders: Maize__Nitrogen, Maize__Healthy, Banana__Iron.
"""
from pathlib import Path
import json
import csv
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

BASE = Path(__file__).resolve().parent
DATA = BASE / "data_split"
IMG_SIZE = (224, 224)
BATCH = 32
SEED = 42
EPOCHS_HEAD = 12
EPOCHS_FINE = 8

for split in ("train", "validation", "test"):
    if not (DATA / split).exists():
        raise SystemExit(f"Missing {DATA / split}. Run: python ml/prepare_dataset.py")

train = tf.keras.utils.image_dataset_from_directory(DATA / "train", image_size=IMG_SIZE, batch_size=BATCH, label_mode="int", seed=SEED)
val = tf.keras.utils.image_dataset_from_directory(DATA / "validation", image_size=IMG_SIZE, batch_size=BATCH, label_mode="int", shuffle=False)
test = tf.keras.utils.image_dataset_from_directory(DATA / "test", image_size=IMG_SIZE, batch_size=BATCH, label_mode="int", shuffle=False)
class_names = train.class_names
if val.class_names != class_names or test.class_names != class_names:
    raise SystemExit("Train/validation/test class folders do not match. Re-run prepare_dataset.py after fixing labels.")
if len(class_names) < 2:
    raise SystemExit("At least two classes are required.")

(BASE / "class_names.json").write_text(json.dumps(class_names, indent=2))
AUTOTUNE = tf.data.AUTOTUNE
# Avoid caching the full image dataset in RAM; this is safer on student laptops.
train = train.shuffle(800, seed=SEED).prefetch(AUTOTUNE)
val = val.prefetch(AUTOTUNE)
test = test.prefetch(AUTOTUNE)

backbone = tf.keras.applications.MobileNetV2(input_shape=(*IMG_SIZE, 3), include_top=False, weights="imagenet")
backbone.trainable = False
inputs = tf.keras.Input(shape=(*IMG_SIZE, 3))
x = tf.keras.layers.RandomFlip("horizontal")(inputs)
x = tf.keras.layers.RandomRotation(0.08)(x)
x = tf.keras.layers.RandomZoom(0.10)(x)
x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
x = backbone(x, training=False)
x = tf.keras.layers.GlobalAveragePooling2D()(x)
x = tf.keras.layers.Dropout(0.30)(x)
outputs = tf.keras.layers.Dense(len(class_names), activation="softmax")(x)
model = tf.keras.Model(inputs, outputs)
model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="sparse_categorical_crossentropy", metrics=["accuracy"])

# Remove stale checkpoints so a previous dataset cannot silently supply the final model.
(BASE / "best_model.keras").unlink(missing_ok=True)
callbacks = [
    tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
    tf.keras.callbacks.ModelCheckpoint(BASE / "best_model.keras", monitor="val_loss", save_best_only=True),
]
print("\nTraining classification head...")
model.fit(train, validation_data=val, epochs=EPOCHS_HEAD, callbacks=callbacks)

print("\nFine-tuning final backbone layers...")
backbone.trainable = True
for layer in backbone.layers[:-30]:
    layer.trainable = False
model.compile(optimizer=tf.keras.optimizers.Adam(1e-5), loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(train, validation_data=val, epochs=EPOCHS_FINE, callbacks=callbacks)

best_path = BASE / "best_model.keras"
if best_path.exists():
    model = tf.keras.models.load_model(best_path)
model.save(BASE / "nutrileaf_model.keras")

print("\nHeld-out test evaluation:")
test_loss, test_acc = model.evaluate(test, verbose=1)
y_true = np.concatenate([y.numpy() for _, y in test])
probs = model.predict(test, verbose=1)
y_pred = np.argmax(probs, axis=1)
report = classification_report(y_true, y_pred, labels=list(range(len(class_names))), target_names=class_names, output_dict=True, zero_division=0)
(BASE / "evaluation.json").write_text(json.dumps({"test_loss": float(test_loss), "test_accuracy": float(test_acc), "classes": class_names, "classification_report": report}, indent=2))
(BASE / "model_metadata.json").write_text(json.dumps({"architecture": "MobileNetV2 transfer learning", "input_size": [224, 224, 3], "class_count": len(class_names), "classes": class_names, "test_accuracy": float(test_acc), "trained_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}, indent=2))
with (BASE / "confusion_matrix.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["actual/predicted", *class_names])
    for name, row in zip(class_names, confusion_matrix(y_true, y_pred, labels=list(range(len(class_names))))):
        writer.writerow([name, *row.tolist()])

print(f"\nSaved model: {BASE / 'nutrileaf_model.keras'}")
print(f"Held-out test accuracy: {test_acc:.3f}")
print(f"Evaluation report: {BASE / 'evaluation.json'}")
print(f"Confusion matrix: {BASE / 'confusion_matrix.csv'}")
print("Note: test metrics are only meaningful if labels are verified and images from the same plant/session do not leak across splits.")
