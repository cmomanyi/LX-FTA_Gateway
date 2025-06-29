import shap
import matplotlib.pyplot as plt
import uuid
import os


def generate_shap_explanation(model, features, feature_names, output_dir="shap_images"):
    try:
        os.makedirs(output_dir, exist_ok=True)
        explainer = shap.Explainer(model)
        shap_values = explainer(features)
        file_path = os.path.join(output_dir, f"shap_{uuid.uuid4().hex}.png")

        shap.plots.bar(shap_values[0], show=False)
        plt.title("SHAP Explanation for Attack Detection")
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()
        return file_path
    except Exception as e:
        print("SHAP generation error:", e)
        return None
