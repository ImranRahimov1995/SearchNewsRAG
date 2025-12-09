/**
 * @fileoverview Trending topics sidebar panel with trend indicators
 */

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Flame } from 'lucide-react';
import { ITrendingTopic } from '@/types';
import { Translations } from '@/i18n/translations';

interface TrendingTopicsPanelProps {
  topics: ITrendingTopic[];
  t: Translations;
}

const MAX_TOPICS_DISPLAY = 5;

/**
 * Returns the appropriate icon component for a trend direction.
 * 
 * @param trend - Trend direction ('up', 'down', or 'neutral')
 * @returns Icon component for the trend
 * @private
 */
function getTrendIcon(trend: ITrendingTopic['trend']): React.ComponentType<{ className?: string }> {
  switch (trend) {
    case 'up':
      return TrendingUp;
    case 'down':
      return TrendingDown;
    default:
      return Minus;
  }
}

/**
 * Returns Tailwind CSS color classes for a trend direction.
 * 
 * @param trend - Trend direction ('up', 'down', or 'neutral')
 * @returns Tailwind color classes
 * @private
 */
function getTrendColor(trend: ITrendingTopic['trend']): string {
  switch (trend) {
    case 'up':
      return 'text-green-600 dark:text-green-400';
    case 'down':
      return 'text-red-600 dark:text-red-400';
    default:
      return 'text-gray-600 dark:text-gray-400';
  }
}

/**
 * Sidebar panel displaying top trending topics with trend indicators.
 * Features numbered badges, count displays, and staggered animations.
 * 
 * @param props - Component props
 * @param props.topics - Array of trending topics to display
 * @returns Rendered trending topics panel, or null if no topics
 */
export const TrendingTopicsPanel: React.FC<TrendingTopicsPanelProps> = ({ topics, t }) => {
  if (topics.length === 0) return null;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-modern p-5"
    >
      <div className="flex items-center gap-2 mb-4">
        <div className="p-2 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 shadow-lg">
          <Flame className="w-4 h-4 text-white" />
        </div>
        <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">
          {t.trending.title}
        </h3>
      </div>
      
      <div className="space-y-2">
        {topics.slice(0, MAX_TOPICS_DISPLAY).map((topic, index) => {
          const TrendIcon = getTrendIcon(topic.trend);
          
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-center justify-between p-3 rounded-xl glass-card hover:glass-card-strong transition-all duration-200 group cursor-pointer"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <span className="flex-shrink-0 w-6 h-6 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 text-white text-xs font-bold flex items-center justify-center">
                  {index + 1}
                </span>
                <span className="text-sm text-gray-700 dark:text-gray-300 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors truncate">
                  {topic.topic}
                </span>
              </div>
              
              <div className="flex items-center gap-3 flex-shrink-0">
                <span className="text-xs font-bold text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-lg">
                  {topic.count}
                </span>
                <TrendIcon className={`w-4 h-4 ${getTrendColor(topic.trend)}`} />
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};
