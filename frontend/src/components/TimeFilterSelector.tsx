/**
 * @fileoverview Time range filter selector for news filtering
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Clock, Calendar, CalendarDays, CalendarRange, Infinity } from 'lucide-react';
import { TimeFilter } from '@/types';
import { Translations } from '@/i18n/translations';

interface TimeFilterSelectorProps {
  currentFilter: TimeFilter;
  onFilterChange: (filter: TimeFilter) => void;
  t: Translations;
}

interface FilterConfig {
  value: TimeFilter;
  icon: React.ComponentType<{ className?: string }>;
}

const TRANSITION_CONFIG = {
  type: 'spring' as const,
  stiffness: 300,
  damping: 30,
};

/**
 * Horizontal scrollable filter chips for time range selection.
 * Features animated active state indicator and icon-label combinations.
 * 
 * @param props - Component props
 * @param props.currentFilter - Currently selected time filter
 * @param props.onFilterChange - Callback when filter selection changes
 * @returns Rendered filter chip list
 */
export const TimeFilterSelector: React.FC<TimeFilterSelectorProps> = ({
  currentFilter,
  onFilterChange,
  t,
}) => {
  const FILTER_OPTIONS: Array<FilterConfig & { label: string }> = [
    { value: 'today', label: t.filters.today, icon: Clock },
    { value: 'week', label: t.filters.week, icon: Calendar },
    { value: 'month', label: t.filters.month, icon: CalendarDays },
    { value: 'year', label: t.filters.year, icon: CalendarRange },
    { value: 'all', label: t.filters.all, icon: Infinity },
  ];

  return (
    <div className="flex gap-2 overflow-x-auto scrollbar-hide pb-2">
      {FILTER_OPTIONS.map((filter) => {
        const Icon = filter.icon;
        const isActive = currentFilter === filter.value;
        
        return (
          <motion.button
            key={filter.value}
            onClick={() => onFilterChange(filter.value)}
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
            className={`
              relative px-4 py-2.5 rounded-xl text-sm font-semibold whitespace-nowrap
              transition-all duration-300 flex items-center gap-2
              ${
                isActive
                  ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-500/40'
                  : 'glass-card text-gray-700 dark:text-gray-300 hover:shadow-md'
              }
            `}
          >
            <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-gray-500 dark:text-gray-400'}`} />
            {filter.label}
            
            {isActive && (
              <motion.div
                layoutId="activeFilter"
                className="absolute inset-0 bg-gradient-to-r from-primary-500 to-primary-600 rounded-xl -z-10"
                transition={TRANSITION_CONFIG}
              />
            )}
          </motion.button>
        );
      })}
    </div>
  );
};
