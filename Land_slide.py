import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from pathlib import Path

print("--- Training Landslide Risk Prediction AI Model (Realistic Version) ---")

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "Data sets" / "land_slide.csv"
MODEL_PATH = BASE_DIR / "landslide_predictor_model.pkl"

# 1. Load the Data
landslide_df = pd.read_csv(DATASET_PATH)

# 2. Keep a smaller, noisier feature set for a more realistic task difficulty
features_to_keep = ['Soil_Saturation', 'Vegetation_Cover', 'Proximity_to_Water']

X_land = landslide_df[features_to_keep]
y_land = landslide_df['Landslide']

# 3. Split data (80% Train, 20% Test)
X_train_l, X_test_l, y_train_l, y_test_l = train_test_split(
    X_land,
    y_land,
    test_size=0.3,
    random_state=42,
    stratify=y_land,
)

# Add controlled sensor noise to mimic real-world measurement uncertainty.
rng = np.random.default_rng(42)
X_train_l = X_train_l.copy()
X_test_l = X_test_l.copy()
for col in X_train_l.columns:
    train_std = X_train_l[col].std()
    noise_scale = 0.10 * train_std
    X_train_l[col] = X_train_l[col] + rng.normal(0, noise_scale, size=len(X_train_l))
    X_test_l[col] = X_test_l[col] + rng.normal(0, noise_scale, size=len(X_test_l))

# Inject a small amount of label noise in training only (common in field data).
y_train_noisy = y_train_l.copy()
flip_ratio = 0.08
flip_count = max(1, int(len(y_train_noisy) * flip_ratio))
flip_indices = rng.choice(y_train_noisy.index.to_numpy(), size=flip_count, replace=False)
y_train_noisy.loc[flip_indices] = 1 - y_train_noisy.loc[flip_indices]

# 4. Train the Model with stronger anti-overfitting constraints
landslide_model = RandomForestClassifier(
    n_estimators=60,
    max_depth=2,
    min_samples_split=30,
    min_samples_leaf=15,
    max_features='sqrt',
    random_state=42,
)
landslide_model.fit(X_train_l, y_train_noisy)

# 5. Check what features the AI is actually using
print("\n--- Landslide Model Feature Importances ---")
importances = pd.DataFrame(
    landslide_model.feature_importances_, 
    index=X_train_l.columns, 
    columns=['Importance']
).sort_values('Importance', ascending=False)
print(importances)

# 6. Test and Save
train_predictions = landslide_model.predict(X_train_l)
landslide_predictions = landslide_model.predict(X_test_l)
train_accuracy = accuracy_score(y_train_l, train_predictions) * 100
test_accuracy = accuracy_score(y_test_l, landslide_predictions) * 100
gap = train_accuracy - test_accuracy

print(f"\nTrain Accuracy: {train_accuracy:.2f}%")
print(f"Test Accuracy: {test_accuracy:.2f}%")
print(f"Overfitting Gap (Train - Test): {gap:.2f}%\n")

joblib.dump(landslide_model, MODEL_PATH)
print("Success! Realistic landslide model saved as 'landslide_predictor_model.pkl'.")