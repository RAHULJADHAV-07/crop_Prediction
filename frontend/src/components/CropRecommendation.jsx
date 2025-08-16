import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';

const API_BASE_URL = 'http://127.0.0.1:5000';

const CropRecommendation = () => {
  const { t } = useTranslation();
  const [dropdownData, setDropdownData] = useState({});
  const [selectedRegion, setSelectedRegion] = useState('');
  const [selectedSoilType, setSelectedSoilType] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  // Function to translate chemical names
  const translateChemical = (chemicalKey) => {
    return t(`chemicals.${chemicalKey}`, { defaultValue: chemicalKey });
  };

  // Function to translate region names
  const translateRegion = (regionKey) => {
    return t(`regions.${regionKey}`, { defaultValue: regionKey });
  };

  // Function to translate soil type names
  const translateSoilType = (soilTypeKey) => {
    return t(`soilTypes.${soilTypeKey}`, { defaultValue: soilTypeKey });
  };

  // Function to translate fertilizer names
  const translateFertilizer = (fertilizerKey) => {
    return t(`fertilizers.${fertilizerKey}`, { defaultValue: fertilizerKey });
  };

  useEffect(() => {
    // Fetch dropdown data on component mount
    const fetchDropdownData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/dropdown-data`);
        const data = await response.json();
        setDropdownData(data);
      } catch (error) {
        console.error('Error fetching dropdown data:', error);
        setError(t('errors.dropdownFailed'));
      }
    };

    fetchDropdownData();
  }, []);

  const getConfidenceLevel = (confidence) => {
    const rawPercentage = confidence * 100;
    if (rawPercentage >= 25) return Math.min(90, 60 + (rawPercentage - 10) * 1.5).toFixed(0);
    if (rawPercentage >= 20) return Math.min(85, 55 + (rawPercentage - 10) * 2).toFixed(0);
    if (rawPercentage >= 15) return Math.min(75, 50 + (rawPercentage - 10) * 2.5).toFixed(0);
    if (rawPercentage >= 10) return Math.min(65, 45 + (rawPercentage - 10) * 3).toFixed(0);
    return Math.max(40, rawPercentage * 4).toFixed(0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedRegion || !selectedSoilType) {
      setError(t('form.selectBothFields'));
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      // Get crop recommendations
      const cropResponse = await fetch(`${API_BASE_URL}/recommend-crop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          Region: selectedRegion,
          'Soil Type': selectedSoilType,
        }),
      });

      const cropData = await cropResponse.json();
      
      if (!cropData.top_recommendations) {
        throw new Error(t('errors.noRecommendations'));
      }

      // Get detailed predictions for top 3 crops
      const cropDetails = await Promise.all(
        cropData.top_recommendations.map(async (crop) => {
          const detailResponse = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              Region: selectedRegion,
              'Soil Type': selectedSoilType,
              'Crop Name': crop.crop,
            }),
          });
          const detailData = await detailResponse.json();
          return {
            crop: crop.crop,
            confidence: crop.confidence,
            details: detailData,
          };
        })
      );

      setResults({
        region: selectedRegion,
        soilType: selectedSoilType,
        crops: cropDetails,
      });
    } catch (error) {
      console.error('Error:', error);
      setError(t('errors.fetchFailed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      {/* Input Form */}
      <div className="card">
        <h2>{t('form.title')}</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            {/* Region Dropdown */}
            <div className="form-group">
              <label>{t('form.region')}</label>
              <select
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                required
              >
                <option value="">{t('form.regionPlaceholder')}</option>
                {dropdownData.Region && dropdownData.Region.map((region) => (
                  <option key={region} value={region}>
                    {translateRegion(region)}
                  </option>
                ))}
              </select>
            </div>

            {/* Soil Type Dropdown */}
            <div className="form-group">
              <label>{t('form.soilType')}</label>
              <select
                value={selectedSoilType}
                onChange={(e) => setSelectedSoilType(e.target.value)}
                required
              >
                <option value="">{t('form.soilTypePlaceholder')}</option>
                {dropdownData['Soil Type'] && dropdownData['Soil Type'].map((soilType) => (
                  <option key={soilType} value={soilType}>
                    {translateSoilType(soilType)}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {error && (
            <div className="error">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
          >
            {loading ? (
              <span style={{display: 'flex', alignItems: 'center'}}>
                <div className="spinner"></div>
                {t('form.gettingRecommendations')}
              </span>
            ) : (
              t('form.getRecommendations')
            )}
          </button>
        </form>
      </div>

      {/* Results */}
      {results && (
        <div>
          {/* Farm Info */}
          <div className="card">
            <h2>{t('results.title')}</h2>
            <div className="farm-info">
              <h3>{t('results.farmDetails')}</h3>
              <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem'}}>
                <p><strong>{t('results.region')}:</strong> {translateRegion(results.region)}</p>
                <p><strong>{t('results.soilType')}:</strong> {translateSoilType(results.soilType)}</p>
              </div>
            </div>
          </div>

          {/* Crop Cards */}
          {results.crops.map((crop, index) => (
            <div key={crop.crop} className="crop-card">
              <div className="crop-header">
                <div style={{display: 'flex', alignItems: 'center', gap: '0.75rem'}}>
                  <span style={{fontSize: '1.5rem'}}>🌾</span>
                  <h3>
                    {t('results.crop')} {index + 1}: {crop.crop}
                  </h3>
                </div>
                <div className="confidence-badge">
                  {getConfidenceLevel(crop.confidence)}% {t('results.recommended')}
                </div>
              </div>

              <div className="crop-details">
                {/* Nutrients */}
                <div className="detail-section nutrients">
                  <h4>{t('results.nutrients')}</h4>
                  <div className="nutrient-list">
                    {crop.details.Nutrients && Object.entries(crop.details.Nutrients).map(([key, value]) => (
                      <div key={key} className="nutrient-item">
                        <span className="nutrient-label">{translateChemical(key)}:</span>
                        <span className="nutrient-value">{Number(value).toFixed(1)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Water Quality */}
                <div className="detail-section water-quality">
                  <h4>{t('results.waterQuality')}</h4>
                  <div className="nutrient-list">
                    {crop.details['Water Quality'] && Object.entries(crop.details['Water Quality']).map(([key, value]) => (
                      <div key={key} className="nutrient-item">
                        <span className="nutrient-label">{translateChemical(key)}:</span>
                        <span className="nutrient-value">{Number(value).toFixed(1)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Fertilizer */}
                <div className="detail-section fertilizer">
                  <h4>{t('results.fertilizer')}</h4>
                  <p style={{fontWeight: '600', color: '#1f2937'}}>
                    {translateFertilizer(crop.details.Fertilizer)}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CropRecommendation;
