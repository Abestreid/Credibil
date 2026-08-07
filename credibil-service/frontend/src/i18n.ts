import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import ro from './locales/ro.json';
import ru from './locales/ru.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      ro: { translation: ro },
      ru: { translation: ru },
    },
    fallbackLng: 'ro',
    interpolation: { escapeValue: false },
  });

export function detectLanguage(): 'ro' | 'ru' {
  const stored = localStorage.getItem('i18nextLng');
  if (stored) {
    const norm = stored.split('-')[0];
    if (norm === 'ru') return 'ru';
    return 'ro';
  }
  const browser = navigator.language?.split('-')[0];
  if (browser === 'ru') return 'ru';
  return 'ro';
}

export default i18n;
