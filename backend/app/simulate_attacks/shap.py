from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.model.basic_sensor_model import SoilData, AtmosphericData, WaterData, ThreatData, PlantData

import shap
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime
import base64
import matplotlib.pyplot as plt
from io import BytesIO

shap_router = APIRouter(prefix="/api/shap", tags=["SHAP"])

# Sensor type → Pydantic Model
model_map = {
    "soil": SoilData,
    "atmospheric": AtmosphericData,
    "water": WaterData,
    "threat": ThreatData,
    "plant": PlantData
}

# SHAP input feature map (manually exclude non-numeric or metadata fields)
input_features = {
    "soil": ["temperature", "moisture", "ph", "nutrient_level", "battery_level"],
    "atmospheric": ["air_temperature", "humidity", "co2", "wind_speed", "rainfall", "battery_level"],
    "water": ["flow_rate", "water_level", "salinity", "ph", "turbidity", "battery_level"],
    "threat": ["unauthorized_access", "jamming_signal", "tampering_attempts", "spoofing_attempts", "anomaly_score", "battery_level"],
    "plant": ["leaf_moisture", "chlorophyll_level", "growth_rate", "disease_risk", "stem_diameter", "battery_level"]
}

# Dummy training data (generate more realistic values if needed)
train_data_map = {
    k: pd.DataFrame({f: np.random.normal(5, 2, 100) for f in fields})
    for k, fields in input_features.items()
}

# Model + Explainer per sensor type
shap_models = {}
shap_explainers = {}
for sensor_type, df in train_data_map.items():
    clf = IsolationForest(contamination=0.1)
    clf.fit(df)
    shap_models[sensor_type] = clf
    shap_explainers[sensor_type] = shap.Explainer(clf.predict, df)


@shap_router.post("/explain")
async def explain_shap(request: Request):
    sensor_type = request.query_params.get("sensor_type")
    if not sensor_type:
        raise HTTPException(status_code=400, detail="sensor_type is required")

    model_cls = model_map.get(sensor_type)
    if not model_cls:
        raise HTTPException(status_code=400, detail=f"Unsupported sensor type: {sensor_type}")

    data = await request.json()
    try:
        validated = model_cls(**data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    features = input_features[sensor_type]
    input_df = pd.DataFrame([{k: getattr(validated, k) for k in features}])
    explainer = shap_explainers[sensor_type]
    prediction = shap_models[sensor_type].predict(input_df)[0]
    shap_values = explainer(input_df)

    explanation = {
        "sensor_type": sensor_type,
        "prediction": "Blocked" if prediction == -1 else "Allowed",
        "features": [
            {"feature": f, "contribution": round(v, 4)}
            for f, v in zip(features, shap_values.values[0])
        ],
        "base_value": round(shap_values.base_values[0], 4),
        "timestamp": datetime.utcnow().isoformat()
    }
    return JSONResponse(content=explanation)


@shap_router.post("/force-plot")
async def shap_force_plot(request: Request):
    sensor_type = request.query_params.get("sensor_type")
    if not sensor_type or sensor_type not in input_features:
        raise HTTPException(status_code=400, detail="Valid sensor_type required")

    model_cls = model_map[sensor_type]
    data = await request.json()

    try:
        validated = model_cls(**data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    features = input_features[sensor_type]
    input_df = pd.DataFrame([{k: getattr(validated, k) for k in features}])

    shap_values = shap_explainers[sensor_type](input_df)

    # Create matplotlib force plot and convert to base64
    plt.clf()
    shap.plots.waterfall(shap_values[0], show=False)
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    return JSONResponse(content={"image_base64": encoded})
