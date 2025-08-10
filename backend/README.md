# 🌾 Smart Farmer Recommender - Backend API

## 📋 Overview
Flask-based REST API providing intelligent crop recommendations, nutrient analysis, and water quality insights for agricultural decision-making.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- pip package manager

### Installation & Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Train ML models
python train_models.py

# 6. Start the server
python app.py
```

The API will be available at: `http://127.0.0.1:5000`

## 🔌 API Endpoints

### 1. Crop Recommendations
**POST** `/recommend-crop`

**Request:**
```json
{
  "Region": "Punjab",
  "Soil Type": "Alluvial"
}
```

**Response:**
```json
{
  "recommended_crop": "Wheat",
  "top_recommendations": [
    {"crop": "Wheat", "confidence": 0.23},
    {"crop": "Rice", "confidence": 0.18},
    {"crop": "Cotton", "confidence": 0.17}
  ],
  "region": "Punjab",
  "soil_type": "Alluvial"
}
```

### 2. Nutrient & Water Quality Predictions
**POST** `/predict`

**Request:**
```json
{
  "Region": "Punjab",
  "Soil Type": "Alluvial", 
  "Crop Name": "Wheat"
}
```

**Response:**
```json
{
  "Nutrients": {
    "N (kg/ha)": 156.42,
    "P₂O₅ (kg/ha)": 60.16,
    "K₂O (kg/ha)": 45.23,
    "Zn (kg/ha)": 2.15,
    "S (kg/ha)": 12.30
  },
  "Water Quality": {
    "pH": 6.61,
    "Turbidity (NTU)": 10.15,
    "Water Temperature (°C)": 24.5
  },
  "Fertilizer": "Superphosphate, Lime"
}
```

### 3. Get Dropdown Options
**GET** `/dropdown-data`

**Response:**
```json
{
  "Region": ["Punjab", "Bihar", "Gujarat", ...],
  "Soil Type": ["Alluvial", "Black", "Red", ...],
  "Crop Name": ["Wheat", "Rice", "Cotton", ...]
}
```

### 4. Health Check
**GET** `/`

Returns API information and available endpoints.

## 📁 Project Structure

```
backend/
├── app.py                 # Main Flask application
├── train_models.py        # ML model training script
├── requirements.txt       # Python dependencies
├── data/                  # Training dataset
├── models/                # Trained ML models
│   ├── *.joblib          # Pickled model files
│   ├── meta.json         # Model metadata
│   └── dropdown_data.json # UI dropdown options
├── venv/                  # Virtual environment
└── test_*.py             # API testing scripts
```

## 🤖 Machine Learning Models

### Algorithms Used
- **Multi-Layer Perceptron (MLP)**: Nutrient & water quality prediction
- **Random Forest**: Crop recommendations & fertilizer suggestions
- **Feature Engineering**: Climate zones, soil fertility scoring

### Model Performance
- **Regression (Nutrients)**: R² Score ~0.52, MAE ~4.9 kg/ha
- **Classification (Crops)**: Multi-class with confidence scores
- **Data**: 1000+ agricultural records from Indian regions

## 🧪 Testing

### Run Test Scripts
```bash
# Test individual models
python test_models.py

# Test API endpoints
python test_api.py

# Test frontend integration
python test_frontend_request.py

# Debug model loading
python debug_models.py
```

### Manual API Testing
```bash
# Test crop recommendations
curl -X POST http://127.0.0.1:5000/recommend-crop \
  -H "Content-Type: application/json" \
  -d '{"Region": "Punjab", "Soil Type": "Alluvial"}'

# Test nutrient predictions  
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"Region": "Punjab", "Soil Type": "Alluvial", "Crop Name": "Wheat"}'
```

## 🛠️ Development

### Adding New Features
1. Update model training in `train_models.py`
2. Add new endpoints in `app.py`
3. Update model metadata in `models/meta.json`
4. Test with provided test scripts

### Environment Variables
```bash
export FLASK_ENV=development  # or production
export FLASK_DEBUG=1          # for development
```

## 📦 Dependencies

**Core Dependencies:**
- Flask 2.3.0+ - Web framework
- Flask-CORS - Cross-origin support
- scikit-learn 1.7.1 - Machine learning
- pandas - Data manipulation
- joblib - Model persistence

**See `requirements.txt` for complete list**

## 🚀 Deployment

### Production Setup
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 app:app

# Or with environment variables
FLASK_ENV=production gunicorn app:app
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python train_models.py
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## 🔧 Troubleshooting

### Common Issues

**Model Loading Errors:**
```bash
# Retrain models
python train_models.py
```

**Scikit-learn Version Mismatch:**
```bash
# Upgrade scikit-learn
pip install --upgrade scikit-learn
python train_models.py
```

**CORS Issues:**
- Ensure Flask-CORS is installed
- Check frontend URL in CORS configuration

**Port Already in Use:**
```bash
# Kill process on port 5000
# Windows: netstat -ano | findstr :5000
# Linux/Mac: lsof -ti:5000 | xargs kill
```

## 📊 API Usage Examples

### Python Client
```python
import requests

# Crop recommendation
response = requests.post('http://127.0.0.1:5000/recommend-crop', 
                        json={"Region": "Punjab", "Soil Type": "Alluvial"})
print(response.json())

# Nutrient prediction
response = requests.post('http://127.0.0.1:5000/predict',
                        json={"Region": "Punjab", "Soil Type": "Alluvial", "Crop Name": "Wheat"})
print(response.json())
```

### JavaScript Client
```javascript
// Crop recommendation
const response = await fetch('http://127.0.0.1:5000/recommend-crop', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({"Region": "Punjab", "Soil Type": "Alluvial"})
});
const data = await response.json();
console.log(data);
```

## 📈 Performance & Monitoring

### Metrics to Monitor
- Response time per endpoint
- Model prediction accuracy
- Memory usage for model loading
- Concurrent request handling

### Optimization Tips
- Use model caching for faster predictions
- Implement request rate limiting
- Add response compression
- Monitor memory usage with large datasets

---

**API Version:** 1.0.0  
**Last Updated:** August 2025  
**Python Version:** 3.8+  
**License:** MIT
