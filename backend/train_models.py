# train_models.py
import pandas as pd
import numpy as np
from pathlib import Path
import json
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPRegressor, MLPClassifier
from sklearn.metrics import r2_score, mean_absolute_error, accuracy_score, classification_report

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "farming_dataset_realistic(1).csv"
OUT = ROOT / "models"
OUT.mkdir(exist_ok=True)

# -------------- Load and clean ----------------
df = pd.read_csv(DATA_PATH)
# unify column names
df.columns = [c.strip() for c in df.columns]
# strip strings
for c in df.select_dtypes(include='object').columns:
    df[c] = df[c].astype(str).str.strip()

# NOTE: Update these names if your CSV columns differ exactly.
cat_features = ['Region', 'Soil Type', 'Crop Name']

# Identify regression target columns - include nutrients, pH, turbidity, and water temp
nutrient_targets = []
for t in ['N (kg/ha)', 'P₂O₅ (kg/ha)', 'K₂O (kg/ha)', 'Zn (kg/ha)', 'S (kg/ha)']:
    if t in df.columns:
        nutrient_targets.append(t)

# Add pH, Turbidity, and Water Temperature targets
additional_targets = []
for t in ['Recommended pH', 'Turbidity (NTU)', 'Water Temp (°C)']:
    if t in df.columns:
        additional_targets.append(t)

targets = nutrient_targets + additional_targets
print("Using targets:", targets)

# Fertilizer column detection (text label)
fert_col_candidates = [c for c in df.columns if 'Fertil' in c or 'fertil' in c]
fert_col = fert_col_candidates[0] if fert_col_candidates else None
print("Fertilizer column:", fert_col)

# Keep only rows with needed columns
keep_cols = cat_features + targets + ([fert_col] if fert_col else [])
df_clean = df[keep_cols].replace({'': np.nan, 'nan': np.nan}).dropna()
print("Rows after dropna:", df_clean.shape[0])

# Prepare X and y
X = df_clean[cat_features]
y_reg = df_clean[targets].astype(float)
y_clf = df_clean[fert_col] if fert_col else None

# -------------- Preprocessor ----------------
preprocessor = ColumnTransformer([
    ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_features)
], remainder='passthrough')

X_trans = preprocessor.fit_transform(X)

# Save dropdown values for frontend
dropdown_data = {
    "Region": sorted(df_clean["Region"].unique().tolist()),
    "Soil Type": sorted(df_clean["Soil Type"].unique().tolist()),
    "Crop Name": sorted(df_clean["Crop Name"].unique().tolist())
}
with open(OUT / "dropdown_data.json", "w", encoding="utf-8") as f:
    json.dump(dropdown_data, f, ensure_ascii=False, indent=2)

# -------------- Train/test split ----------------
X_train, X_test, y_train, y_test = train_test_split(X_trans, y_reg, test_size=0.2, random_state=42)

# For classifier if available
if y_clf is not None:
    Xc_train, Xc_test, yc_train, yc_test = train_test_split(X_trans, y_clf, test_size=0.2, random_state=42)
else:
    Xc_train = Xc_test = yc_train = yc_test = None

# -------------- Models to train ----------------
models_reg = {
    'rf_reg': MultiOutputRegressor(RandomForestRegressor(n_estimators=150, random_state=42, n_jobs=-1)),
    'gb_reg': MultiOutputRegressor(GradientBoostingRegressor(n_estimators=200, random_state=42)),
    'mlp_reg': MultiOutputRegressor(MLPRegressor(hidden_layer_sizes=(64,32), max_iter=300, random_state=42))
}

trained_reg = {}
metrics = {}

for name, mdl in models_reg.items():
    print(f"Training {name} ...")
    mdl.fit(X_train, y_train)
    preds = mdl.predict(X_test)
    r2s = [r2_score(y_test.iloc[:, i], preds[:, i]) for i in range(preds.shape[1])]
    maes = [mean_absolute_error(y_test.iloc[:, i], preds[:, i]) for i in range(preds.shape[1])]
    metrics[name] = {'r2_mean': float(np.mean(r2s)), 'mae_mean': float(np.mean(maes))}
    trained_reg[name] = mdl
    print(f"{name} done. mean R2: {metrics[name]['r2_mean']:.4f}, mean MAE: {metrics[name]['mae_mean']:.4f}")

# -------------- Classifier (optional) ----------------
trained_clf = {}
clf_metrics = {}

# Fertilizer classifier
if y_clf is not None:
    # RandomForest classifier
    rf_clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    rf_clf.fit(Xc_train, yc_train)
    preds = rf_clf.predict(Xc_test)
    acc = accuracy_score(yc_test, preds)
    trained_clf['rf_clf'] = rf_clf
    clf_metrics['rf_clf'] = {'accuracy': float(acc)}
    print("rf_clf accuracy:", acc)

    # MLP classifier
    mlp_clf = MLPClassifier(hidden_layer_sizes=(64,32), max_iter=300, random_state=42)
    mlp_clf.fit(Xc_train, yc_train)
    preds2 = mlp_clf.predict(Xc_test)
    acc2 = accuracy_score(yc_test, preds2)
    trained_clf['mlp_clf'] = mlp_clf
    clf_metrics['mlp_clf'] = {'accuracy': float(acc2)}
    print("mlp_clf accuracy:", acc2)

# -------------- Crop Recommendation Model ----------------
# Train a model to predict best crop based on Region, Soil Type, and derived features
print("\nTraining crop recommendation model...")

# Add engineered features to improve prediction
crop_df = df_clean.copy()

# Add climate zone mapping based on region
climate_zones = {
    'Punjab': 'Semi-Arid', 'Haryana': 'Semi-Arid', 'Rajasthan': 'Arid',
    'Gujarat': 'Semi-Arid', 'Maharashtra': 'Tropical', 'Madhya Pradesh': 'Tropical',
    'Bihar': 'Humid', 'Uttar Pradesh': 'Humid', 'Kerala': 'Tropical', 'Tamil Nadu': 'Tropical'
}
crop_df['Climate_Zone'] = crop_df['Region'].map(climate_zones)

# Add soil fertility score based on soil type
soil_fertility = {
    'Alluvial': 5, 'Black': 4, 'Red': 3, 'Loamy': 5, 'Clay': 3,
    'Sandy': 2, 'Laterite': 2, 'Peaty': 4, 'Chalky': 3, 'Saline': 1
}
crop_df['Soil_Fertility'] = crop_df['Soil Type'].map(soil_fertility)

crop_features = ['Region', 'Soil Type', 'Climate_Zone', 'Soil_Fertility']
crop_target = 'Crop Name'

# Prepare data for crop prediction
X_crop = crop_df[crop_features]
y_crop = crop_df[crop_target]

# Enhanced preprocessor with new features
crop_preprocessor = ColumnTransformer([
    ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['Region', 'Soil Type', 'Climate_Zone']),
    ('num', 'passthrough', ['Soil_Fertility'])
], remainder='drop')

X_crop_trans = crop_preprocessor.fit_transform(X_crop)

# Train/test split for crop prediction
Xcrop_train, Xcrop_test, ycrop_train, ycrop_test = train_test_split(
    X_crop_trans, y_crop, test_size=0.2, random_state=42
)

# Train crop recommendation models with improved parameters
crop_models = {
    'rf_crop': RandomForestClassifier(
        n_estimators=500,      # More trees
        max_depth=10,          # Deeper trees
        min_samples_split=5,   # Better splits
        min_samples_leaf=2,    # Prevent overfitting
        class_weight='balanced', # Handle class imbalance
        random_state=42, 
        n_jobs=-1
    ),
    'gb_crop': GradientBoostingClassifier(
        n_estimators=300,      # More boosting rounds
        max_depth=8,           # Deeper trees
        learning_rate=0.1,     # Learning rate
        subsample=0.8,         # Prevent overfitting
        random_state=42
    ),
}

crop_trained = {}
crop_metrics = {}

for name, model in crop_models.items():
    print(f"Training {name} for crop recommendation...")
    model.fit(Xcrop_train, ycrop_train)
    preds = model.predict(Xcrop_test)
    acc = accuracy_score(ycrop_test, preds)
    crop_trained[name] = model
    crop_metrics[name] = {'accuracy': float(acc)}
    print(f"{name} crop recommendation accuracy: {acc:.4f}")

print("Crop recommendation metrics:", crop_metrics)

# -------------- Save preprocessor & models ----------------
joblib.dump(preprocessor, OUT / "preprocessor.joblib")
for name, mdl in trained_reg.items():
    joblib.dump(mdl, OUT / f"{name}.joblib")
for name, mdl in trained_clf.items():
    joblib.dump(mdl, OUT / f"{name}.joblib")

# Save crop recommendation models and preprocessor
joblib.dump(crop_preprocessor, OUT / "crop_preprocessor.joblib")
for name, mdl in crop_trained.items():
    joblib.dump(mdl, OUT / f"{name}.joblib")

# Save metadata (targets order and categories)
meta = {
    "targets": targets, 
    "nutrient_targets": nutrient_targets,
    "additional_targets": additional_targets,
    "fertilizer_column": fert_col,
    "crop_features": crop_features,
    "crop_models": list(crop_trained.keys())
}
with open(OUT / "meta.json", "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print("\nSaved models and dropdowns to 'models/'")
print("Regression metrics summary:", metrics)
if clf_metrics:
    print("Classifier metrics:", clf_metrics)
print("Crop recommendation metrics:", crop_metrics)
