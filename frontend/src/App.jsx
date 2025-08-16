import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import CropRecommendation from './components/CropRecommendation';
import LanguageSelector from './components/LanguageSelector';
import './i18n';

function App() {
  const { t } = useTranslation();

  return (
    <div style={{minHeight: '100vh'}}>
      <LanguageSelector />
      <div className="container">
        <header style={{textAlign: 'center', marginBottom: '3rem'}}>
          <h1>{t('title')}</h1>
          <p style={{fontSize: '1.25rem', color: '#6b7280', maxWidth: '600px', margin: '0 auto'}}>
            {t('subtitle')}
          </p>
        </header>
        
        <main>
          <CropRecommendation />
        </main>
        
        <footer>
          <p>{t('footer')}</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
