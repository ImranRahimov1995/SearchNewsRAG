/**
 * @fileoverview React hook for fetching analytics data
 */

import { useState, useEffect } from 'react';
import { ITrendingTopic, IIndexStatus } from '@/types';
import { apiService } from '@/services/apiService';
import { useLanguage } from './useLanguage';

const REFRESH_INTERVAL_MS = 5 * 60 * 1000;

/**
 * Custom hook for fetching and managing analytics data.
 * Automatically refreshes data every 5 minutes.
 * 
 * @returns Object containing trending topics, index status, and loading state
 * 
 * @example
 * const { trendingTopics, indexStatus, isLoading } = useAnalytics();
 */
export const useAnalytics = () => {
  const { language } = useLanguage();
  const [trendingTopics, setTrendingTopics] = useState<ITrendingTopic[]>([]);
  const [indexStatus, setIndexStatus] = useState<IIndexStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setIsLoading(true);
      try {
        const [topics, status] = await Promise.all([
          apiService.getTrendingTopics(),
          apiService.getIndexStatus(),
        ]);

        setTrendingTopics(topics);
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
    trendingTopics,
    indexStatus,
    isLoading,
  };
};
