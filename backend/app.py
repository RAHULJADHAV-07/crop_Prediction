from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import json
import pandas as pd
from pathlib import Path
import traceback

# ---------------- Setup ----------------
app = Flask(__name__)
CORS(app)

ROOT = Path(__file__).parent
MODELS_DIR = ROOT / "models"

# ---------------- Load Models ----------------
try:
    preprocessor = joblib.load(MODELS_DIR / "preprocessor.joblib")
    crop_preprocessor = joblib.load(MODELS_DIR / "crop_preprocessor.joblib")
    crop_model = joblib.load(MODELS_DIR / "rf_crop.joblib")
    reg_model = joblib.load(MODELS_DIR / "mlp_reg.joblib")
    print("All models loaded successfully")
except FileNotFoundError as e:
    raise RuntimeError(f"Model file not found: {e}. Please run train_models.py first.")

# ---------------- Load Metadata ----------------
try:
    with open(MODELS_DIR / "meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    
    target_names = meta.get("targets", [])
    nutrient_targets = meta.get("nutrient_targets", [])
    additional_targets = meta.get("additional_targets", [])
    fertilizer_column = meta.get("fertilizer_column", None)
except FileNotFoundError:
    raise RuntimeError("meta.json not found. Please run train_models.py first.")

# ---------------- Load Classifier (Optional) ----------------
clf_model = None
if fertilizer_column:
    clf_path = MODELS_DIR / "rf_clf.joblib"
    if clf_path.exists():
        clf_model = joblib.load(clf_path)

# ---------------- Load Dropdown Data ----------------
try:
    with open(MODELS_DIR / "dropdown_data.json", "r", encoding="utf-8") as f:
        dropdown_data = json.load(f)
except FileNotFoundError:
    dropdown_data = {}

# ---------------- Routes ----------------
@app.route("/")
def index():
    return jsonify({
        "message": "Farmer Recommender API",
        "version": "1.0.0",
        "endpoints": {
            "dropdown_data": "/dropdown-data",
            "crop_recommendation": "/recommend-crop",
            "predictions": "/predict"
        }
    })

@app.route("/test-crop", methods=["GET"])
def test_crop():
    """Test endpoint to check crop model status"""
    return jsonify({
        "crop_model_loaded": crop_model is not None,
        "crop_preprocessor_loaded": crop_preprocessor is not None,
        "dropdown_data_loaded": len(dropdown_data) > 0
    })

@app.route("/dropdown-data", methods=["GET"])
def get_dropdown_data():
    return jsonify(dropdown_data)

@app.route("/recommend-crop", methods=["POST"])
def recommend_crop():
    try:
        data = request.get_json()
        print(f"Received data: {data}")

        region = data.get("Region")
        soil = data.get("Soil Type")
        
        print(f"Region: {region}, Soil: {soil}")

        if not region or not soil:
            return jsonify({"error": "Region and Soil Type are required"}), 400

        # Validate values are in dataset
        if region not in dropdown_data.get("Region", []):
            return jsonify({"error": f"Invalid Region: {region}"}), 400
        if soil not in dropdown_data.get("Soil Type", []):
            return jsonify({"error": f"Invalid Soil Type: {soil}"}), 400

        # Add engineered features for crop prediction
        climate_zones = {
            'Punjab': 'Semi-Arid', 'Haryana': 'Semi-Arid', 'Rajasthan': 'Arid',
            'Gujarat': 'Semi-Arid', 'Maharashtra': 'Tropical', 'Madhya Pradesh': 'Tropical',
            'Bihar': 'Humid', 'Uttar Pradesh': 'Humid', 'Kerala': 'Tropical', 'Tamil Nadu': 'Tropical'
        }
        soil_fertility = {
            'Alluvial': 5, 'Black': 4, 'Red': 3, 'Loamy': 5, 'Clay': 3,
            'Sandy': 2, 'Laterite': 2, 'Peaty': 4, 'Chalky': 3, 'Saline': 1
        }
        
        climate_zone = climate_zones.get(region, 'Tropical')
        fertility_score = soil_fertility.get(soil, 3)

        # Transform input for crop prediction with enhanced features
        crop_input_df = pd.DataFrame([[region, soil, climate_zone, fertility_score]], 
                                   columns=['Region', 'Soil Type', 'Climate_Zone', 'Soil_Fertility'])
        
        print(f"Input DataFrame: {crop_input_df}")
        
        X_crop = crop_preprocessor.transform(crop_input_df)
        print(f"Transformed input shape: {X_crop.shape}")
        
        # Get crop recommendation
        recommended_crop = crop_model.predict(X_crop)[0]
        
        # Get probability scores for top crops
        crop_probabilities = crop_model.predict_proba(X_crop)[0]
        crop_classes = crop_model.classes_
        
        # Get top 3 crop recommendations with confidence scores
        top_indices = crop_probabilities.argsort()[-3:][::-1]
        top_crops = []
        for idx in top_indices:
            top_crops.append({
                "crop": crop_classes[idx],
                "confidence": float(crop_probabilities[idx])
            })

        result = {
            "recommended_crop": recommended_crop,
            "top_recommendations": top_crops,
            "region": region,
            "soil_type": soil
        }
        
        print(f"Result: {result}")
        return jsonify(result)

    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debug logging

        # Validate input
        region = data.get("Region")
        soil = data.get("Soil Type")
        crop = data.get("Crop Name")
        
        print(f"Region: {region}, Soil: {soil}, Crop: {crop}")  # Debug logging

        if not region or not soil or not crop:
            return jsonify({"error": "Region, Soil Type, and Crop Name are required"}), 400

        # Ensure values are in dataset dropdowns
        for field, value in [("Region", region), ("Soil Type", soil), ("Crop Name", crop)]:
            if value not in dropdown_data.get(field, []):
                print(f"Invalid {field}: {value}")  # Debug logging
                return jsonify({"error": f"Invalid {field}: {value}"}), 400

        print("Input validation passed")  # Debug logging
        
        # Transform input & predict nutrients - Create DataFrame with correct column names
        input_df = pd.DataFrame([[region, soil, crop]], columns=['Region', 'Soil Type', 'Crop Name'])
        X = preprocessor.transform(input_df)
        print("Preprocessor transform successful")  # Debug logging
        
        preds = reg_model.predict(X)[0]
        print("Regression prediction successful:", preds)  # Debug logging

        # Organize predictions by category
        nutrients = {}
        water_quality = {}
        
        for i, target in enumerate(target_names):
            if i < len(preds):
                value = float(preds[i])
                if target in nutrient_targets:
                    nutrients[target] = value
                elif target in additional_targets:
                    # Map to more user-friendly names
                    if target == "Recommended pH":
                        water_quality["pH"] = value
                    elif target == "Turbidity (NTU)":
                        water_quality["Turbidity (NTU)"] = value
                    elif target == "Water Temp (°C)":
                        water_quality["Water Temperature (°C)"] = value

        # Predict fertilizer if classifier exists
        fertilizer = None
        if clf_model and fertilizer_column:
            fertilizer = clf_model.predict(X)[0]
            print("Fertilizer prediction successful:", fertilizer)  # Debug logging

        result = {
            "Nutrients": nutrients,
            "Water Quality": water_quality,
            "Fertilizer": fertilizer
        }
        print("Final result:", result)  # Debug logging
        return jsonify(result)

    except Exception as e:
        print("Exception occurred:", str(e))  # Debug logging
        print("Traceback:", traceback.format_exc())  # Debug logging
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

# ---------------- Run Server ----------------
if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
