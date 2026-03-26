import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from pathlib import Path

MODEL_VERSION = "1.0.0"
FEATURES = [
    "recent_tremors_count",
    "fault_distance_km",
    "historical_magnitude_avg",
    "ground_deformation_mm",
    "radon_level_ppm",
]

MODELS_DIR = Path(__file__).resolve().parents[2] / "trained_models"
MODEL_PATH = MODELS_DIR / "earthquake_model.pkl"
SCALER_PATH = MODELS_DIR / "earthquake_scaler.pkl"


def train_model():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    n_samples = 2000

    recent_tremors_count = rng.uniform(0, 30, n_samples)
    fault_distance_km = rng.uniform(0, 50, n_samples)
    historical_magnitude_avg = rng.uniform(1, 9, n_samples)
    ground_deformation_mm = rng.uniform(0, 20, n_samples)
    radon_level_ppm = rng.uniform(0, 100, n_samples)

    X = np.column_stack([
        recent_tremors_count, fault_distance_km, historical_magnitude_avg,
        ground_deformation_mm, radon_level_ppm
    ])

    risk = (
        (recent_tremors_count > 10).astype(float) * 0.4 +
        (fault_distance_km < 5).astype(float) * 0.35 +
        (ground_deformation_mm > 5).astype(float) * 0.25
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
