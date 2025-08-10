import React, { useState, useEffect } from 'react';
import CropRecommendation from './components/CropRecommendation';

function App() {
  return (
    <div style={{minHeight: '100vh'}}>
      <div className="container">
        <header style={{textAlign: 'center', marginBottom: '3rem'}}>
          <h1>🌾 Smart Farmer Recommender</h1>
          <p style={{fontSize: '1.25rem', color: '#6b7280', maxWidth: '600px', margin: '0 auto'}}>
            Get intelligent crop recommendations, nutrient analysis, and water quality insights 
            tailored to your region and soil type
          </p>
        </header>
        
        <main>
          <CropRecommendation />
        </main>
        
        <footer>
          <p>© 2025 Smart Farmer Recommender </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
