/**
 * @fileoverview React hook for fetching analytics data
 */

import { useState, useEffect } from 'react';
import { ICategory, INewsItem, IIndexStatus } from '@/types';
import { apiService } from '@/services/apiService';
import { useLanguage } from './useLanguage';

const REFRESH_INTERVAL_MS = 5 * 60 * 1000;

/**
 * Custom hook for fetching and managing analytics data.
 * Automatically refreshes data every 5 minutes.
 *
 * @returns Object containing categories, latest news, index status, and loading state
 *
 * @example
 * const { categories, latestNews, indexStatus, isLoading } = useAnalytics();
 */
export const useAnalytics = () => {
  const { language } = useLanguage();
  const [categories, setCategories] = useState<ICategory[]>([]);
  const [latestNews, setLatestNews] = useState<INewsItem[]>([]);
  const [indexStatus, setIndexStatus] = useState<IIndexStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setIsLoading(true);
      try {
        const [categoriesRes, newsRes, status] = await Promise.all([
          apiService.getCategories(language),
          apiService.getNews({ language, dateFilter: 'all', sortOrder: 'desc', page: 1, pageSize: 10 }),
          apiService.getIndexStatus(),
        ]);

        setCategories(categoriesRes.categories);
        setLatestNews(newsRes.results.news);
        setIndexStatus(status);
      } catch (error) {
        console.error('Failed to fetch analytics:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();

    const interval = setInterval(fetchAnalytics, REFRESH_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [language]);

  return {
    categories,
    latestNews,
    indexStatus,
    isLoading,
  };
};
