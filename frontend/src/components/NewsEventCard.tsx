/**
 * @fileoverview News event card component with sentiment indicators
 */

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Newspaper, ExternalLink } from 'lucide-react';
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

  const handleClick = () => {
    if (event.url) {
      window.open(event.url, '_blank', 'noopener,noreferrer');
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
      whileHover={event.url ? { scale: 1.01, y: -1 } : {}}
      onClick={handleClick}
      className={`
        bg-white/40 dark:bg-gray-800/40 backdrop-blur-sm
        rounded-lg sm:rounded-xl p-2.5 sm:p-3.5 mb-2 sm:mb-2.5
        border border-gray-200/50 dark:border-gray-700/50
        ${event.url ? 'cursor-pointer hover:bg-white/60 dark:hover:bg-gray-800/60 hover:border-primary-400/50' : ''}
        transition-all duration-200
        group
      `}
    >
      <div className="flex items-start justify-between gap-2 mb-1.5 sm:mb-2">
        <h3 className="font-semibold text-xs sm:text-sm text-gray-800 dark:text-gray-200 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors leading-snug flex-1">
          {event.title}
        </h3>
        {event.url && (
          <ExternalLink className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-primary-500 flex-shrink-0 mt-0.5 group-hover:text-primary-600" />
        )}
      </div>

      {event.summary && (
        <p className="text-[11px] sm:text-xs text-gray-600 dark:text-gray-400 line-clamp-2 leading-relaxed mb-2">
          {event.summary}
        </p>
      )}

      <div className="flex items-center justify-between gap-2 text-[10px] sm:text-xs">
        <div className="flex items-center gap-2">
          {event.sentiment && (
            <div className="flex items-center gap-1 sm:gap-1.5">
              <SentimentIcon className={`w-3 h-3 sm:w-3.5 sm:h-3.5 ${config.text}`} />
              <span className={`font-medium ${config.text} capitalize`}>
                {getSentimentLabel(event.sentiment)}
              </span>
            </div>
          )}
        </div>
        
        {event.source && (
          <div className="flex items-center gap-1 sm:gap-1.5 text-gray-500 dark:text-gray-400">
            <Newspaper className="w-2.5 h-2.5 sm:w-3 sm:h-3" />
            <span className="font-medium truncate max-w-[80px] sm:max-w-[120px]">
              {event.source}
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
};
