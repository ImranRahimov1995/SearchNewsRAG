/**
 * @fileoverview React hook for managing application theme
 */

import { useState, useEffect } from 'react';
import { Theme } from '@/types';

const THEME_STORAGE_KEY = 'theme';
const LIGHT_THEME: Theme = 'light';
const DARK_THEME: Theme = 'dark';

/**
 * Custom hook for managing light/dark theme with localStorage persistence.
 *
 * @returns Object containing current theme and toggle function
 *
 * @example
 * const { theme, toggleTheme } = useTheme();
 * toggleTheme();
 */
export const useTheme = () => {
  const [theme, setTheme] = useState<Theme>(() => {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY) as Theme;
    return savedTheme || LIGHT_THEME;
  });

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove(LIGHT_THEME, DARK_THEME);
    root.classList.add(theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === LIGHT_THEME ? DARK_THEME : LIGHT_THEME));
  };

  return { theme, toggleTheme };
};
