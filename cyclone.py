import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib
from pathlib import Path

print("--- Training Cyclone Risk AI Model ---")

# 1. Load the Data
base_dir = Path(__file__).resolve().parent
dataset_path = base_dir / 'Data sets' / 'cyclone_dataset.csv'
cyclone_df = pd.read_csv(dataset_path)

# 2. Separate Features (Inputs) and Target (Output)
# We drop 'time' because it is not a physical factor causing cyclones
X_cyclone = cyclone_df.drop(columns=['risk_level', 'time'])
y_cyclone = cyclone_df['risk_level']

# 3. Split data (80% Train, 20% Test)
X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X_cyclone, y_cyclone, test_size=0.2, random_state=42)

# 4. Train the Model
cyclone_model = RandomForestClassifier(n_estimators=100, random_state=42)
cyclone_model.fit(X_train_c, y_train_c)

# 5. Test Accuracy
cyclone_predictions = cyclone_model.predict(X_test_c)
print(f"Cyclone Model Accuracy: {accuracy_score(y_test_c, cyclone_predictions) * 100:.2f}%\n")

# 6. Save the Model
joblib.dump(cyclone_model, 'cyclone_predictor_model.pkl')
print("Success! Cyclone model saved as 'cyclone_predictor_model.pkl'.")