/**
 * @fileoverview Latest news sidebar panel
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Newspaper, Calendar, Tag } from 'lucide-react';
import { INewsItem } from '@/types';
import { Translations } from '@/i18n/translations';

interface LatestNewsPanelProps {
  news: INewsItem[];
  loading?: boolean;
  t: Translations;
}

const MAX_NEWS_DISPLAY = 5;

const formatDate = (dateString: string | null, t: Translations): string => {
  if (!dateString) return '';
  
  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 1) return t.latestNews.justNow;
    if (diffHours < 24) return `${diffHours}${t.latestNews.hoursAgo}`;
    
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays === 1) return t.latestNews.yesterday;
    if (diffDays < 7) return `${diffDays}${t.latestNews.daysAgo}`;
    
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
    });
  } catch {
    return '';
  }
};

const truncateText = (text: string, maxLength: number = 100): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
};

export const LatestNewsPanel: React.FC<LatestNewsPanelProps> = ({ news, loading, t }) => {
  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-modern p-5"
      >
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-500 shadow-lg">
            <Newspaper className="w-4 h-4 text-white" />
          </div>
          <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">
            {t.latestNews.title}
          </h3>
        </div>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="glass-card rounded-xl p-3 space-y-2">
              <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded animate-pulse" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-3/4 animate-pulse" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2 animate-pulse" />
            </div>
          ))}
        </div>
      </motion.div>
    );
  }

  if (news.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-modern p-5"
    >
      <div className="flex items-center gap-2 mb-4">
        <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-500 shadow-lg">
          <Newspaper className="w-4 h-4 text-white" />
        </div>
        <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">
          {t.latestNews.title}
        </h3>
      </div>

      <div className="space-y-3">
        {news.slice(0, MAX_NEWS_DISPLAY).map((item, index) => (
          <motion.div
            key={item.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="glass-card hover:glass-card-strong transition-all duration-200 rounded-xl p-3 cursor-pointer group"
          >
            <div className="space-y-2">
              <p className="text-sm text-gray-800 dark:text-gray-200 font-medium leading-snug group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                {truncateText(item.content, 120)}
              </p>
              
              <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <div className="flex items-center gap-1.5">
                  {item.category && (
                    <>
                      <Tag className="w-3 h-3" />
                      <span className="truncate max-w-[100px]">{item.category}</span>
                    </>
                  )}
                </div>
                
                {item.date && (
                  <div className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    <span className="whitespace-nowrap">{formatDate(item.date, t)}</span>
                  </div>
                )}
              </div>
              
              {item.importance !== null && item.importance >= 8 && (
                <div className="flex">
                  <span className="text-xs bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 px-2 py-0.5 rounded-md font-semibold">
                    {t.latestNews.important}
                  </span>
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};
