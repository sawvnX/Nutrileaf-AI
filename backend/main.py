from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse

from pathlib import Path
from PIL import Image, UnidentifiedImageError

from functools import lru_cache

import sqlite3
import uuid
import io
import json
import datetime
import csv


# =========================================================
# PATH CONFIGURATION
# =========================================================

ROOT = Path(__file__).resolve().parents[1]

UPLOADS = ROOT / "backend" / "uploads"
DB = ROOT / "backend" / "nutrileaf.db"

MODEL = ROOT / "ml" / "nutrileaf_model.keras"
LABELS_FILE = ROOT / "ml" / "class_names.json"

UPLOADS.mkdir(parents=True, exist_ok=True)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="NutriLeaf AI API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================================
# NUTRIENT INFORMATION
# =========================================================

NUTRIENTS = {

    "Nitrogen": {
        "symbol": "N",
        "symptoms": "Older leaves become uniformly pale green or yellow; growth may be stunted.",
        "causes": "Low available nitrogen, leaching, waterlogging or poor root function.",
        "care": "Confirm with soil testing. Apply a crop-appropriate nitrogen source in split doses; avoid over-application."
    },

    "Phosphorus": {
        "symbol": "P",
        "symptoms": "Slow growth; older leaves may appear dark green, dull or purplish, especially in cool conditions.",
        "causes": "Low soil phosphorus, cold soil, unsuitable pH or restricted roots.",
        "care": "Check soil pH and a soil-test recommendation before applying phosphate fertilizer."
    },

    "Potassium": {
        "symbol": "K",
        "symptoms": "Yellowing or scorching along older leaf margins, sometimes progressing inward.",
        "causes": "Low exchangeable potassium, drought stress or root damage.",
        "care": "Use soil-test-guided potash; maintain even watering and avoid excess competing salts."
    },

    "Magnesium": {
        "symbol": "Mg",
        "symptoms": "Interveinal chlorosis on older leaves: tissue between veins yellows while veins remain greener.",
        "causes": "Low magnesium, acidic sandy soils or potassium/calcium imbalance.",
        "care": "Confirm with soil or tissue analysis; apply a suitable magnesium source only as recommended."
    },

    "Calcium": {
        "symbol": "Ca",
        "symptoms": "Distorted or damaged young leaves and growing points; some crops show blossom-end rot.",
        "causes": "Poor calcium movement, irregular watering, root injury or low calcium availability.",
        "care": "Keep soil moisture consistent and investigate root-zone conditions."
    },

    "Iron": {
        "symbol": "Fe",
        "symptoms": "Young leaves show interveinal yellowing; severe cases may become nearly white.",
        "causes": "High soil pH, waterlogged roots or low available iron.",
        "care": "Check pH and drainage; use a crop- and soil-appropriate iron treatment."
    },

    "Sulphur": {
        "symbol": "S",
        "symptoms": "Newer leaves become uniformly pale yellow; plants may be thin and slow-growing.",
        "causes": "Low sulphur in low-organic-matter or heavily leached soils.",
        "care": "Confirm with soil/tissue testing and use a suitable sulphur-containing fertilizer if needed."
    },

    "Healthy": {
        "symbol": "✓",
        "symptoms": "No strong visual nutrient-deficiency pattern was identified by the model.",
        "causes": "The leaf may be healthy, or symptoms may not be visible in this image.",
        "care": "Continue balanced crop care and monitor new growth."
    }
}


# =========================================================
# CLASS LABEL CORRECTION
# =========================================================

LABEL_ALIASES = {

    "Helathy": "Healthy",
    "Healthy": "Healthy",

    "Magnessium": "Magnesium",
    "Magnesium": "Magnesium",

    "Nitrogen": "Nitrogen",

    "Phosphorous": "Phosphorus",
    "Phosphorus": "Phosphorus",

    "Pottasium": "Potassium",
    "Potassium": "Potassium"
}


def normalize_label(label):

    parts = [
        part.replace("_", " ").strip().title()
        for part in label.split("__")
    ]

    return [
        LABEL_ALIASES.get(part, part)
        for part in parts
    ]


def get_nutrient_from_label(label):

    parts = normalize_label(label)

    for part in parts:
        if part in NUTRIENTS:
            return part

    return None


# =========================================================
# DATABASE
# =========================================================

def db():

    con = sqlite3.connect(DB)

    con.row_factory = sqlite3.Row

    con.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            filename TEXT,
            plant TEXT,
            prediction TEXT,
            confidence REAL,
            image_path TEXT,
            created_at TEXT,
            notes TEXT
        )
    """)

    con.commit()

    return con


# =========================================================
# LOAD AI MODEL
# =========================================================

@lru_cache(maxsize=1)
def load_model_bundle():

    import tensorflow as tf

    labels = json.loads(LABELS_FILE.read_text(encoding="utf-8"))

    model = tf.keras.models.load_model(MODEL)

    return model, labels


# =========================================================
# AI PREDICTION
# =========================================================

def model_predict(image: Image.Image):

    if not MODEL.exists() or not LABELS_FILE.exists():

        raise RuntimeError("MODEL_NOT_TRAINED")

    try:

        import numpy as np

        model, labels = load_model_bundle()

        arr = np.array(
            image.convert("RGB").resize((224, 224)),
            dtype="float32"
        )

        probs = model.predict(
            np.expand_dims(arr, 0),
            verbose=0
        )[0]

        if len(labels) != len(probs):

            raise RuntimeError("MODEL_LABEL_MISMATCH")

        order = np.argsort(probs)[::-1][:3]

        ranked = [
            {
                "label": labels[int(i)],
                "confidence": float(probs[int(i)])
            }
            for i in order
        ]

        return ranked

    except ImportError:

        raise RuntimeError("TENSORFLOW_MISSING")


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
def health():

    ready = MODEL.exists() and LABELS_FILE.exists()

    classes = (
        json.loads(LABELS_FILE.read_text(encoding="utf-8"))
        if LABELS_FILE.exists()
        else []
    )

    return {
        "status": "ok",
        "model_ready": ready,
        "classes": classes,
        "message": "AI model ready" if ready else "AI model not trained"
    }


# =========================================================
# NUTRIENT LIBRARY
# =========================================================

@app.get("/api/nutrients")
def nutrients():

    return NUTRIENTS


# =========================================================
# AI SCANNER
# =========================================================

@app.post("/api/scan")
async def scan(
    file: UploadFile = File(...),
    plant: str = "Unknown"
):

    if file.content_type not in (
        "image/jpeg",
        "image/png",
        "image/webp"
    ):

        raise HTTPException(
            400,
            "Please upload a JPG, PNG or WEBP image."
        )

    raw = await file.read()

    if len(raw) > 10 * 1024 * 1024:

        raise HTTPException(
            413,
            "Image must be smaller than 10 MB."
        )

    try:

        image = Image.open(io.BytesIO(raw))

        image.verify()

        image = Image.open(
            io.BytesIO(raw)
        ).convert("RGB")

    except (UnidentifiedImageError, OSError):

        raise HTTPException(
            400,
            "The uploaded file is not a valid image."
        )

    if min(image.size) < 80:

        raise HTTPException(
            400,
            "Image is too small. Use a clear close-up of a leaf."
        )

    try:

        ranked = model_predict(image)

    except RuntimeError as e:

        if str(e) == "MODEL_NOT_TRAINED":

            raise HTTPException(
                503,
                "AI model is not trained yet."
            )

        if str(e) == "MODEL_LABEL_MISMATCH":

            raise HTTPException(
                500,
                "Model output count does not match class_names.json."
            )

        raise HTTPException(
            503,
            "TensorFlow is missing or the model could not be loaded."
        )

    if not ranked:

        raise HTTPException(
            500,
            "Model returned no predictions."
        )

    # -----------------------------------------------------
    # MAIN PREDICTION
    # -----------------------------------------------------

    label = ranked[0]["label"]

    confidence = ranked[0]["confidence"]

    parts = normalize_label(label)

    model_crop = parts[0] if len(parts) > 1 else None

    selected_crop = plant.strip().title()

    crop_aliases = {
        "Corn": "Maize"
    }

    selected_crop = crop_aliases.get(
        selected_crop,
        selected_crop
    )

    if (
        model_crop
        and selected_crop not in ("Unknown", "Other")
        and model_crop != selected_crop
    ):

        raise HTTPException(
            422,
            f"This model was trained for {model_crop}, "
            f"but the selected crop is {plant}."
        )

    nutrient = get_nutrient_from_label(label)

    if nutrient is None:

        raise HTTPException(
            500,
            f"Model predicted an unsupported class: {label}"
        )

    info = NUTRIENTS[nutrient]

    # -----------------------------------------------------
    # SAVE SCAN IN DATABASE
    # -----------------------------------------------------

    sid = str(uuid.uuid4())

    path = UPLOADS / (sid + ".jpg")

    image.save(path, quality=90)

    created = datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat()

    con = db()

    con.execute(
        "INSERT INTO scans VALUES (?,?,?,?,?,?,?,?)",
        (
            sid,
            file.filename,
            plant,
            nutrient,
            confidence,
            str(path),
            created,
            info["symptoms"]
        )
    )

    con.commit()

    con.close()

    # -----------------------------------------------------
    # TOP 3 PREDICTIONS
    # -----------------------------------------------------

    def decode_candidate(item):

        raw_label = item["label"]

        nutrient_name = get_nutrient_from_label(raw_label)

        if nutrient_name is None:

            nutrient_name = "Unmapped class"

        return {
            "label": raw_label,
            "nutrient": nutrient_name,
            "confidence": round(
                item["confidence"] * 100,
                1
            )
        }

    top_predictions = [
        decode_candidate(item)
        for item in ranked
    ]

    # -----------------------------------------------------
    # RESPONSE
    # -----------------------------------------------------

    return {

        "id": sid,

        "plant": plant,

        "prediction": nutrient,

        "confidence": round(
            confidence * 100,
            1
        ),

        "top_predictions": top_predictions,

        "created_at": created,

        "image_url": f"/api/image/{sid}",

        "details": info,

        "model_crop": model_crop or "General",

        "low_confidence": confidence < 0.55,

        "disclaimer": (
            "Image-based screening is not a laboratory diagnosis. "
            "Similar symptoms can have multiple causes; "
            "confirm with soil or tissue testing."
        )
    }


# =========================================================
# DISPLAY UPLOADED IMAGE
# =========================================================

@app.get("/api/image/{scan_id}")
def image_file(scan_id: str):

    con = db()

    row = con.execute(
        "SELECT image_path FROM scans WHERE id=?",
        (scan_id,)
    ).fetchone()

    con.close()

    if not row or not Path(row["image_path"]).exists():

        raise HTTPException(
            404,
            "Image not found"
        )

    return FileResponse(row["image_path"])


# =========================================================
# SCAN HISTORY
# =========================================================

@app.get("/api/history")
def history():

    con = db()

    rows = con.execute("""
        SELECT id, filename, plant, prediction,
        confidence, created_at
        FROM scans
        ORDER BY created_at DESC
        LIMIT 100
    """).fetchall()

    con.close()

    return [dict(row) for row in rows]


# =========================================================
# DELETE SCAN
# =========================================================

@app.delete("/api/history/{scan_id}")
def delete_scan(scan_id: str):

    con = db()

    row = con.execute(
        "SELECT image_path FROM scans WHERE id=?",
        (scan_id,)
    ).fetchone()

    if not row:

        con.close()

        raise HTTPException(
            404,
            "Scan not found"
        )

    try:

        Path(row["image_path"]).unlink(
            missing_ok=True
        )

    except OSError:

        pass

    con.execute(
        "DELETE FROM scans WHERE id=?",
        (scan_id,)
    )

    con.commit()

    con.close()

    return {
        "deleted": True
    }


# =========================================================
# DASHBOARD STATISTICS
# =========================================================

@app.get("/api/stats")
def stats():

    con = db()

    total = con.execute(
        "SELECT COUNT(*) n FROM scans"
    ).fetchone()["n"]

    rows = con.execute(
        "SELECT prediction, COUNT(*) n FROM scans GROUP BY prediction"
    ).fetchall()

    con.close()

    return {

        "total_scans": total,

        "healthy": next(
            (
                row["n"]
                for row in rows
                if row["prediction"] == "Healthy"
            ),
            0
        ),

        "deficiencies": sum(
            row["n"]
            for row in rows
            if row["prediction"] != "Healthy"
        ),

        "by_type": {
            row["prediction"]: row["n"]
            for row in rows
        }
    }


# =========================================================
# MODEL INFORMATION
# =========================================================

@app.get("/api/model-info")
def model_info():

    evaluation_path = ROOT / "ml" / "evaluation.json"

    metadata_path = ROOT / "ml" / "model_metadata.json"

    return {

        "model_ready": MODEL.exists() and LABELS_FILE.exists(),

        "model_file": MODEL.name if MODEL.exists() else None,

        "classes": (
            json.loads(LABELS_FILE.read_text(encoding="utf-8"))
            if LABELS_FILE.exists()
            else []
        ),

        "evaluation": (
            json.loads(evaluation_path.read_text(encoding="utf-8"))
            if evaluation_path.exists()
            else None
        ),

        "metadata": (
            json.loads(metadata_path.read_text(encoding="utf-8"))
            if metadata_path.exists()
            else None
        ),

        "note": (
            "Metrics are meaningful only when the held-out test set "
            "is independent and labels are verified."
        )
    }


# =========================================================
# EXPORT SCAN HISTORY AS CSV
# =========================================================

@app.get("/api/export.csv")
def export_csv():

    con = db()

    rows = con.execute("""
        SELECT id, filename, plant, prediction,
        confidence, created_at, notes
        FROM scans
        ORDER BY created_at DESC
    """).fetchall()

    con.close()

    stream = io.StringIO()

    writer = csv.writer(stream)

    writer.writerow([
        "Scan ID",
        "Filename",
        "Plant",
        "Prediction",
        "Confidence (0-1)",
        "Created at (UTC)",
        "Notes"
    ])

    for row in rows:

        writer.writerow(list(row))

    stream.seek(0)

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=nutrileaf-scan-history.csv"
        }
    )


# =========================================================
# FRONTEND
# =========================================================

app.mount(
    "/",
    StaticFiles(
        directory=ROOT / "frontend",
        html=True
    ),
    name="frontend"
)