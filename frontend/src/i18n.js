import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import all language files
import en from './locales/en.json';
import hi from './locales/hi.json';
import gu from './locales/gu.json';
import ta from './locales/ta.json';
import ml from './locales/ml.json';
import mr from './locales/mr.json';
import pa from './locales/pa.json';
import raj from './locales/raj.json';
import bn from './locales/bn.json';
import kn from './locales/kn.json';
import as from './locales/as.json';
import te from './locales/te.json';

const resources = {
  en: { translation: en },
  hi: { translation: hi },
  gu: { translation: gu },
  ta: { translation: ta },
  ml: { translation: ml },
  mr: { translation: mr },
  pa: { translation: pa },
  raj: { translation: raj },
  bn: { translation: bn },
  kn: { translation: kn },
  as: { translation: as },
  te: { translation: te }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: false,
    interpolation: {
      escapeValue: false, // React already escapes by default
    },
    detection: {
      // Detection options
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
  });

export default i18n;
