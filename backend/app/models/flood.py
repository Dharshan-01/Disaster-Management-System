import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from pathlib import Path

MODEL_VERSION = "1.0.0"
FEATURES = [
    "rainfall_mm_24h",
    "river_level_m",
    "soil_moisture_pct",
    "upstream_rainfall_mm",
    "elevation_m",
    "drainage_capacity",
]

MODELS_DIR = Path(__file__).resolve().parents[2] / "trained_models"
MODEL_PATH = MODELS_DIR / "flood_model.pkl"
SCALER_PATH = MODELS_DIR / "flood_scaler.pkl"


def train_model():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    n_samples = 2000

    rainfall_mm_24h = rng.uniform(0, 250, n_samples)
    river_level_m = rng.uniform(0, 10, n_samples)
    soil_moisture_pct = rng.uniform(10, 100, n_samples)
    upstream_rainfall_mm = rng.uniform(0, 300, n_samples)
    elevation_m = rng.uniform(0, 500, n_samples)
    drainage_capacity = rng.uniform(0, 1, n_samples)

    X = np.column_stack([
        rainfall_mm_24h, river_level_m, soil_moisture_pct,
        upstream_rainfall_mm, elevation_m, drainage_capacity
    ])

    risk = (
        (rainfall_mm_24h > 100).astype(float) * 0.4 +
        (river_level_m > 5).astype(float) * 0.35 +
        (soil_moisture_pct > 80).astype(float) * 0.25
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
