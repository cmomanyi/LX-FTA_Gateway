# shap_backend.py - SHAP explanation backend

import shap
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.ensemble import IsolationForest
from datetime import datetime
from fastapi.responses import JSONResponse

router = APIRouter()

# Sample training data to simulate a pre-trained model
np.random.seed(42)
train_data = pd.DataFrame({
    "temperature": np.random.normal(25, 2, 100),
    "moisture": np.random.uniform(30, 70, 100),
    "ph": np.random.uniform(6, 7.5, 100),
    "battery_level": np.random.uniform(3.3, 5.0, 100),
    "frequency": np.random.uniform(1, 10, 100)
})

# Train Isolation Forest model
model = IsolationForest(contamination=0.1)
model.fit(train_data)
explainer = shap.Explainer(model.predict, train_data)


# Request schema
class SensorInput(BaseModel):
    temperature: float
    moisture: float
    ph: float
    battery_level: float
    frequency: float


@router.post("/explain")
def explain_decision(input: SensorInput):
    try:
        input_df = pd.DataFrame([input.dict()])
        prediction = model.predict(input_df)[0]  # -1 means anomaly

        shap_values = explainer(input_df)
        base_values = shap_values.base_values[0]
        values = shap_values.values[0]
        feature_names = input_df.columns.tolist()

        explanation = {
            "prediction": "Blocked" if prediction == -1 else "Allowed",
            "features": [
                {"feature": f, "contribution": round(v, 4)}
                for f, v in zip(feature_names, values)
            ],
            "base_value": round(base_values, 4),
            "timestamp": datetime.utcnow().isoformat()
        }
        return JSONResponse(content=explanation)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
