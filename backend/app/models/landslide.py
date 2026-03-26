import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from pathlib import Path

MODEL_VERSION = "1.0.0"
FEATURES = [
    "rainfall_mm_48h",
    "slope_angle_deg",
    "soil_saturation_pct",
    "vegetation_cover_pct",
    "slope_aspect_deg",
]

MODELS_DIR = Path(__file__).resolve().parents[2] / "trained_models"
MODEL_PATH = MODELS_DIR / "landslide_model.pkl"
SCALER_PATH = MODELS_DIR / "landslide_scaler.pkl"


def train_model():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    n_samples = 2000

    rainfall_mm_48h = rng.uniform(0, 300, n_samples)
    slope_angle_deg = rng.uniform(0, 70, n_samples)
    soil_saturation_pct = rng.uniform(10, 100, n_samples)
    vegetation_cover_pct = rng.uniform(0, 100, n_samples)
    slope_aspect_deg = rng.uniform(0, 360, n_samples)

    X = np.column_stack([
        rainfall_mm_48h, slope_angle_deg, soil_saturation_pct,
        vegetation_cover_pct, slope_aspect_deg
    ])

    risk = (
        (rainfall_mm_48h > 150).astype(float) * 0.4 +
        (slope_angle_deg > 30).astype(float) * 0.35 +
        (soil_saturation_pct > 90).astype(float) * 0.25
    )
    y = (risk >= 0.4).astype(int)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    return model, scaler


def load_or_train():
    if MODEL_PATH.exists() and SCALER_PATH.exists():
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
    else:
        model, scaler = train_model()
    return model, scaler


_model, _scaler = load_or_train()


def predict(features: dict) -> dict:
    values = [features.get(f, 0.0) for f in FEATURES]
    X = np.array(values).reshape(1, -1)
    X_scaled = _scaler.transform(X)

    proba = _model.predict_proba(X_scaled)[0]
    risk_score = float(proba[1]) if len(proba) > 1 else float(proba[0])

    if risk_score >= 0.7:
        risk_level = "HIGH"
    elif risk_score >= 0.4:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    importances = _model.feature_importances_
    indexed = sorted(enumerate(importances), key=lambda x: x[1], reverse=True)
    contributing_factors = [FEATURES[i] for i, _ in indexed[:3]]

    return {
        "risk_score": round(risk_score, 4),
        "risk_level": risk_level,
        "contributing_factors": contributing_factors,
    }
