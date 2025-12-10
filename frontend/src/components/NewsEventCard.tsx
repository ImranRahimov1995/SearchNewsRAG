/**
 * @fileoverview News event card component with sentiment indicators
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, TrendingUp, TrendingDown, Minus, Newspaper } from 'lucide-react';
import { INewsEvent } from '@/types';
import { Translations } from '@/i18n/translations';

interface NewsEventCardProps {
  event: INewsEvent;
  index?: number;
  t: Translations;
}

interface SentimentConfig {
  bg: string;
  border: string;
  text: string;
  icon: React.ComponentType<{ className?: string }>;
}

const SENTIMENT_CONFIGS: Record<string, SentimentConfig> = {
  positive: {
    bg: 'bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-900/30 dark:to-emerald-800/30',
    border: 'border-green-300 dark:border-green-700',
    text: 'text-green-700 dark:text-green-300',
    icon: TrendingUp,
  },
  negative: {
    bg: 'bg-gradient-to-br from-red-50 to-rose-100 dark:from-red-900/30 dark:to-rose-800/30',
    border: 'border-red-300 dark:border-red-700',
    text: 'text-red-700 dark:text-red-300',
    icon: TrendingDown,
  },
  neutral: {
    bg: 'bg-gradient-to-br from-gray-50 to-slate-100 dark:from-gray-800/30 dark:to-slate-700/30',
    border: 'border-gray-300 dark:border-gray-600',
    text: 'text-gray-700 dark:text-gray-300',
    icon: Minus,
  },
};

/**
 * Displays a news event card with category, date, title, and sentiment.
 * Features hover animations and gradient styling.
 *
 * @param props - Component props
 * @param props.event - News event data to display
 * @param props.index - Index for staggered animation delay
 * @param props.t - Translation object
 * @returns Rendered news event card
 */
export const NewsEventCard: React.FC<NewsEventCardProps> = ({ event, index = 0, t }) => {
  const config = SENTIMENT_CONFIGS[event.sentiment || 'neutral'];
  const SentimentIcon = config.icon;

  const getSentimentLabel = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return t.sentiment.positive;
      case 'negative':
        return t.sentiment.negative;
      default:
        return t.sentiment.neutral;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{
        duration: 0.4,
        delay: index * 0.1,
        ease: [0.4, 0, 0.2, 1]
      }}
      whileHover={{ scale: 1.02, y: -2 }}
      className="card-modern p-4 mb-3 border border-white/20 dark:border-gray-700/30 cursor-pointer group"
    >
      <div className="flex justify-between items-start mb-3">
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-xl ${config.bg} border ${config.border}`}>
          <Newspaper className={`w-3.5 h-3.5 ${config.text}`} />
          <span className={`text-xs font-semibold ${config.text}`}>
            {event.category}
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-gray-500 dark:text-gray-400">
          <Calendar className="w-3.5 h-3.5" />
          <span className="text-xs font-medium">
            {new Date(event.date).toLocaleDateString('ru-RU', {
              day: 'numeric',
              month: 'short'
            })}
          </span>
        </div>
      </div>

      <h3 className="font-bold text-sm mb-2 text-gray-900 dark:text-gray-100 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors leading-snug">
        {event.title}
      </h3>

      {event.summary && (
        <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 leading-relaxed">
          {event.summary}
        </p>
      )}

      {event.sentiment && (
        <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 flex items-center gap-2">
          <SentimentIcon className={`w-4 h-4 ${config.text}`} />
          <span className={`text-xs font-medium ${config.text} capitalize`}>
            {getSentimentLabel(event.sentiment)}
          </span>
        </div>
      )}
    </motion.div>
  );
};
