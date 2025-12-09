/**
 * @fileoverview Language selection and translation hook
 */

import { useState, useEffect } from 'react';
import { Language, translations } from '@/i18n/translations';

const LANGUAGE_STORAGE_KEY = 'newschat-language';
const DEFAULT_LANGUAGE: Language = 'az';

/**
 * Hook for managing application language and translations.
 * Persists language selection to localStorage and provides translation utilities.
 * 
 * @returns Language state and translation functions
 * 
 * @example
 * ```tsx
 * const { language, setLanguage, t } = useLanguage();
 * console.log(t.app.title); // "NewsChat"
 * ```
 */
export const useLanguage = () => {
  const [language, setLanguageState] = useState<Language>(() => {
    const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY);
    return (stored as Language) || DEFAULT_LANGUAGE;
  });

  useEffect(() => {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, language);
    document.documentElement.lang = language;
  }, [language]);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
  };

  const t = translations[language];

  return {
    language,
    setLanguage,
    t,
  };
};
