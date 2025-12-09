/**
 * @fileoverview Date utility functions for relative time formatting
 */

const SECONDS_IN_MINUTE = 60;
const MINUTES_IN_HOUR = 60;
const HOURS_IN_DAY = 24;
const DAYS_IN_WEEK = 7;

type TimeUnit = {
  justNow: string;
  minute: [string, string, string];
  hour: [string, string, string];
  day: [string, string, string];
  ago: string;
};

const TIME_TRANSLATIONS: Record<string, TimeUnit> = {
  az: {
    justNow: 'indicə',
    minute: ['dəqiqə', 'dəqiqə', 'dəqiqə'],
    hour: ['saat', 'saat', 'saat'],
    day: ['gün', 'gün', 'gün'],
    ago: 'əvvəl',
  },
  en: {
    justNow: 'just now',
    minute: ['minute', 'minutes', 'minutes'],
    hour: ['hour', 'hours', 'hours'],
    day: ['day', 'days', 'days'],
    ago: 'ago',
  },
  ru: {
    justNow: 'только что',
    minute: ['минута', 'минуты', 'минут'],
    hour: ['час', 'часа', 'часов'],
    day: ['день', 'дня', 'дней'],
    ago: 'назад',
  },
};

/**
 * Formats a date to relative time string in current language.
 * 
 * @param date - The date to format
 * @returns Localized relative time string
 * 
 * @example
 * formatDistanceToNow(new Date(Date.now() - 60000))
 * // Returns: '1 dəqiqə əvvəl' (az) / '1 minute ago' (en) / '1 минута назад' (ru)
 */
export const formatDistanceToNow = (date: Date): string => {
  const lang = (localStorage.getItem('newschat-language') || 'az') as 'az' | 'en' | 'ru';
  const t = TIME_TRANSLATIONS[lang];
  
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < SECONDS_IN_MINUTE) {
    return t.justNow;
  }

  const diffInMinutes = Math.floor(diffInSeconds / SECONDS_IN_MINUTE);
  if (diffInMinutes < MINUTES_IN_HOUR) {
    return `${diffInMinutes} ${pluralize(diffInMinutes, t.minute, lang)} ${t.ago}`;
  }

  const diffInHours = Math.floor(diffInMinutes / MINUTES_IN_HOUR);
  if (diffInHours < HOURS_IN_DAY) {
    return `${diffInHours} ${pluralize(diffInHours, t.hour, lang)} ${t.ago}`;
  }

  const diffInDays = Math.floor(diffInHours / HOURS_IN_DAY);
  if (diffInDays < DAYS_IN_WEEK) {
    return `${diffInDays} ${pluralize(diffInDays, t.day, lang)} ${t.ago}`;
  }

  const locales: Record<string, string> = {
    az: 'az-AZ',
    en: 'en-US',
    ru: 'ru-RU',
  };
  
  return date.toLocaleDateString(locales[lang]);
};

/**
 * Returns correct plural form for a number based on language rules.
 * 
 * @param count - The number to check
 * @param forms - Array of forms [one, few, many]
 * @param lang - Language code
 * @returns Correct plural form
 */
const pluralize = (count: number, forms: [string, string, string], lang: string): string => {
  if (lang === 'en') {
    return count === 1 ? forms[0] : forms[1];
  }

  if (lang === 'az') {
    return forms[0];
  }

  const mod10 = count % 10;
  const mod100 = count % 100;

  if (mod10 === 1 && mod100 !== 11) {
    return forms[0];
  }

  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) {
    return forms[1];
  }

  return forms[2];
};
