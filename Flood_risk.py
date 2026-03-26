import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from pathlib import Path

print("--- Training Flood Risk Prediction AI Model ---")

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "Data sets" / "Flood_risk.csv"
MODEL_PATH = BASE_DIR / "flood_predictor_model.pkl"

# 1. Load the Dataset
flood_df = pd.read_csv(DATASET_PATH)

# 2. Separate Features (Inputs) and Target (Output)
# This dataset contains numeric weather/hydrology features and target column 'Flood'.
X = flood_df.drop(columns=['Flood'])
y = flood_df['Flood']

# 3. Split data into Training (80%) and Testing (20%) sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Build and Train the Model
# Random Forest is highly accurate for complex environmental and weather data
flood_model = RandomForestClassifier(n_estimators=100, random_state=42)
flood_model.fit(X_train, y_train)

# 5. Test the Model and Print Accuracy
flood_predictions = flood_model.predict(X_test)
accuracy = accuracy_score(y_test, flood_predictions)
print(f"Flood Prediction Model Accuracy: {accuracy * 100:.2f}%\n")

# 6. Save the Model
joblib.dump(flood_model, MODEL_PATH)

print("Success! Model has been saved locally.")
print(" - flood_predictor_model.pkl")
