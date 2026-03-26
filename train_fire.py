import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from pathlib import Path

print("--- Training Forest Fire Prediction AI Model (Realistic Version) ---")

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "Data sets" / "Forest_fire.csv"
MODEL_PATH = BASE_DIR / "forest_fire_predictor_model.pkl"

# 1. Load and clean the Data
fire_df = pd.read_csv(DATASET_PATH, header=1)
fire_df.columns = fire_df.columns.str.strip()
fire_df = fire_df.dropna().reset_index(drop=True)
fire_df = fire_df[fire_df['day'] != 'day'].reset_index(drop=True)

# Clean and map the target column
fire_df['Classes'] = fire_df['Classes'].str.strip()
fire_df['Classes'] = fire_df['Classes'].map({'fire': 1, 'not fire': 0})

# Ensure all columns are numeric
for col in fire_df.columns:
    fire_df[col] = pd.to_numeric(fire_df[col])

# 2. Prevent Data Leakage
# Drop the calculated fire indices. Keep only raw weather: Temp, RH, Ws, Rain.
columns_to_drop = ['Classes', 'day', 'month', 'year', 'FWI', 'ISI', 'BUI', 'FFMC', 'DMC', 'DC']
X_fire = fire_df.drop(columns=columns_to_drop) 
y_fire = fire_df['Classes']

# 3. Split data (80% Train, 20% Test)
X_train_f, X_test_f, y_train_f, y_test_f = train_test_split(X_fire, y_fire, test_size=0.2, random_state=42)

# 4. Train the Model (with anti-overfitting measures)
fire_model = RandomForestClassifier(
    n_estimators=100, 
    max_depth=5,              # Restricts how deep the decision trees can grow
    min_samples_split=10,     # Requires more samples to make a new branch
    min_samples_leaf=5,       # Requires more samples at the end of a branch
    random_state=42
)
fire_model.fit(X_train_f, y_train_f)

# 5. Check what features the AI is actually using
print("\n--- Fire Model Feature Importances ---")
importances = pd.DataFrame(
    fire_model.feature_importances_, 
    index=X_train_f.columns, 
    columns=['Importance']
).sort_values('Importance', ascending=False)
print(importances)

# 6. Test and Save
fire_predictions = fire_model.predict(X_test_f)
print(f"\nRealistic Fire Model Accuracy: {accuracy_score(y_test_f, fire_predictions) * 100:.2f}%\n")

joblib.dump(fire_model, MODEL_PATH)
print("Success! Realistic fire model saved as 'forest_fire_predictor_model.pkl'.")