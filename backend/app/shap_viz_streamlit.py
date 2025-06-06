import streamlit as st
import requests
import shap
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="SHAP Explanation", layout="centered")

st.title("🧠 SHAP XAI Visualizer")

st.markdown("Enter sensor inputs to simulate anomaly detection and see feature contribution.")

# Input fields
temperature = st.number_input("Temperature (°C)", 15.0, 100.0, 87.0)
moisture = st.number_input("Moisture (%)", 0.0, 100.0, 25.0)
ph = st.number_input("pH", 3.0, 10.0, 5.2)
battery_level = st.number_input("Battery Level (V)", 2.0, 6.0, 3.0)
frequency = st.number_input("Request Frequency", 0.0, 20.0, 12.0)

# Send to SHAP backend
if st.button("Explain"):
    payload = {
        "temperature": temperature,
        "moisture": moisture,
        "ph": ph,
        "battery_level": battery_level,
        "frequency": frequency
    }

    with st.spinner("Requesting SHAP explanation..."):
        response = requests.post("http://localhost:8001/explain", json=payload)

    if response.status_code == 200:
        result = response.json()
        st.success(f"Prediction: {result['prediction']}")

        # SHAP Plot
        st.subheader("🔍 SHAP Waterfall Explanation")
        df = pd.DataFrame([payload])
        model = shap.Explainer(lambda x: [1 if f["prediction"] == "Allowed" else -1][0], df)
        shap_values = model(df)

        shap.plots.waterfall(shap_values[0], show=False)
        st.pyplot(plt.gcf())
    else:
        st.error("SHAP backend error: " + response.text)
