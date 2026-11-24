"""Create deterministic train/validation/test folders from ml/data_raw/<class>.

Expected labels are crop-specific, e.g. Maize__Nitrogen, Banana__Iron, Coffee__Healthy.
Keep photos from the same plant/session together before running this script; this
script splits individual files and cannot infer plant identity from a photo.
"""
from pathlib import Path
import random, shutil

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "data_raw"
DEST = ROOT / "data_split"
EXTS = {".jpg", ".jpeg", ".png", ".webp"}
SEED = 42
RATIOS = (0.70, 0.15, 0.15)

if not SOURCE.exists():
    raise SystemExit(f"Missing {SOURCE}. Create one subfolder per class first.")
classes = sorted(p for p in SOURCE.iterdir() if p.is_dir())
if len(classes) < 2:
    raise SystemExit("Need at least two labelled class folders in ml/data_raw/.")

random.seed(SEED)
# Rebuild the split from scratch so reruns never leave stale images/classes.
if DEST.exists():
    shutil.rmtree(DEST)
counts = {}
for split in ("train", "validation", "test"):
    (DEST / split).mkdir(parents=True, exist_ok=True)

for class_dir in classes:
    files = [p for p in class_dir.rglob("*") if p.is_file() and p.suffix.lower() in EXTS]
    if len(files) < 10:
        raise SystemExit(f"Class '{class_dir.name}' has only {len(files)} images. Add at least 10 labelled images per class (preferably hundreds) before splitting.")
    random.shuffle(files)
    n = len(files)
    n_train = int(n * RATIOS[0])
    n_val = int(n * RATIOS[1])
    assignments = {
        "train": files[:n_train],
        "validation": files[n_train:n_train+n_val],
        "test": files[n_train+n_val:],
    }
    for split, selected in assignments.items():
        target = DEST / split / class_dir.name
        target.mkdir(parents=True, exist_ok=True)
        for index, src in enumerate(selected):
            # Prefix avoids collisions from nested source directories.
            shutil.copy2(src, target / f"{index:06d}_{src.name}")
        counts[f"{split}/{class_dir.name}"] = len(selected)
    print(f"{class_dir.name}: {len(files)} images -> " + ", ".join(f"{k}={len(v)}" for k,v in assignments.items()))

print(f"\nPrepared dataset at: {DEST}")
print("IMPORTANT: This is a file-level split. If multiple images come from the same plant or photo session, group them into one split manually to prevent data leakage.")
