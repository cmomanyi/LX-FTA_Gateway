# shap_backend.py - SHAP explanation backend

import shap
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.ensemble import IsolationForest
from datetime import datetime
from fastapi.responses import JSONResponse

# Initialize FastAPI app
app = FastAPI()

# Allow frontend communication (CORS setup)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust if your frontend runs elsewhere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Step 1: Generate mock training data
np.random.seed(42)
train_data = pd.DataFrame({
    "temperature": np.random.normal(25, 2, 100),
    "moisture": np.random.uniform(30, 70, 100),
    "ph": np.random.uniform(6, 7.5, 100),
    "battery_level": np.random.uniform(3.3, 5.0, 100),
    "frequency": np.random.uniform(1, 10, 100)
})

# Step 2: Train Isolation Forest anomaly detection model
model = IsolationForest(contamination=0.1)
model.fit(train_data)

# Step 3: Create SHAP explainer using model's prediction function
explainer = shap.Explainer(model.predict, train_data)

# Step 4: Define request schema
class SensorInput(BaseModel):
    temperature: float
    moisture: float
    ph: float
    battery_level: float
    frequency: float

# Step 5: API endpoint to return prediction and SHAP explanation
@app.post("/explain")
def explain_decision(input: SensorInput):
    try:
        # Convert input to DataFrame
        input_df = pd.DataFrame([input.dict()])

        # Predict anomaly (-1 = anomaly, 1 = normal)
        prediction = model.predict(input_df)[0]

        # Compute SHAP values
        shap_values = explainer(input_df)
        base_value = shap_values.base_values[0]

        feature_contributions = shap_values.values[0]
        feature_names = input_df.columns.tolist()

        # Format response
        explanation = {
            "prediction": "Blocked" if prediction == -1 else "Allowed",
            "features": [
                {"feature": name, "contribution": round(contrib, 4)}
                for name, contrib in zip(feature_names, feature_contributions)
            ],
            "base_value": round(base_value, 4),
            "timestamp": datetime.utcnow().isoformat()
        }
        return JSONResponse(content=explanation)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
