import React from 'react';
import { useTranslation } from 'react-i18next';

const LanguageSelector = () => {
  const { i18n } = useTranslation();

  const languages = [
    { code: 'en', name: 'English', native: 'English' },
    { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
    { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી' },
    { code: 'ta', name: 'Tamil', native: 'தமிழ்' },
    { code: 'ml', name: 'Malayalam', native: 'മലയാളം' },
    { code: 'mr', name: 'Marathi', native: 'मराठी' },
    { code: 'pa', name: 'Punjabi', native: 'ਪੰਜਾਬੀ' },
    { code: 'raj', name: 'Rajasthani', native: 'राजस्थानी' },
    { code: 'bn', name: 'Bengali', native: 'বাংলা' },
    { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ' },
    { code: 'as', name: 'Assamese', native: 'অসমীয়া' },
    { code: 'te', name: 'Telugu', native: 'తెలుగు' }
  ];

  const changeLanguage = (event) => {
    i18n.changeLanguage(event.target.value);
  };

  return (
    <div className="language-selector">
      <select 
        value={i18n.language} 
        onChange={changeLanguage}
        className="language-select"
        title="Select Language / भाषा चुनें"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.native} ({lang.name})
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageSelector;
