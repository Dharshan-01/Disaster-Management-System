import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from pathlib import Path

print("--- Training Earthquake Risk AI Model ---")

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "Data sets" / "earthquake_dataset.csv"
MODEL_PATH = BASE_DIR / "earthquake_predictor_model.pkl"

# 1. Load the Data
earthquake_df = pd.read_csv(DATASET_PATH)

# 2. Separate Features (Inputs) and Target (Output)
# Drop 'time' as we are predicting based on physical seismic markers
X_earthquake = earthquake_df.drop(columns=['risk_level', 'time'])
y_earthquake = earthquake_df['risk_level']

# 3. Split data (80% Train, 20% Test)
X_train_e, X_test_e, y_train_e, y_test_e = train_test_split(X_earthquake, y_earthquake, test_size=0.2, random_state=42)

# 4. Train the Model
earthquake_model = RandomForestClassifier(n_estimators=100, random_state=42)
earthquake_model.fit(X_train_e, y_train_e)

# 5. Test Accuracy
earthquake_predictions = earthquake_model.predict(X_test_e)
print(f"Earthquake Model Accuracy: {accuracy_score(y_test_e, earthquake_predictions) * 100:.2f}%\n")

# 6. Save the Model
joblib.dump(earthquake_model, MODEL_PATH)
print("Success! Earthquake model saved as 'earthquake_predictor_model.pkl'.")