/**
 * @fileoverview Quick query template buttons for common searches
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Zap, TrendingUp, Globe, Briefcase, Cpu } from 'lucide-react';
import { Translations } from '@/i18n/translations';

interface QuickQueryTemplatesProps {
  onSelectTemplate: (query: string) => void;
  t: Translations;
}

interface QueryTemplate {
  text: string;
  icon: React.ComponentType<{ className?: string }>;
}

/**
 * Horizontal scrollable quick query buttons with icons.
 * Features staggered entrance animations and hover effects.
 * 
 * @param props - Component props
 * @param props.onSelectTemplate - Callback when template is selected
 * @returns Rendered quick query template buttons
 */
export const QuickQueryTemplates: React.FC<QuickQueryTemplatesProps> = ({
  onSelectTemplate,
  t,
}) => {
  const QUERY_TEMPLATES: QueryTemplate[] = [
    { text: t.quickQueries.positive, icon: TrendingUp },
    { text: t.quickQueries.loudest, icon: Zap },
    { text: t.quickQueries.today, icon: Globe },
    { text: t.quickQueries.politics, icon: Briefcase },
    { text: t.quickQueries.tech, icon: Cpu },
  ];

  return (
    <div className="mb-4">
      <div className="flex items-center gap-2 mb-3">
        <Zap className="w-4 h-4 text-primary-500" />
        <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300">
          {t.quickQueries.title}
        </h3>
      </div>
      
      <div className="flex gap-2 overflow-x-auto scrollbar-hide">
        {QUERY_TEMPLATES.map((template, index) => {
          const Icon = template.icon;
          return (
            <motion.button
              key={index}
              onClick={() => onSelectTemplate(template.text)}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
              className="
                flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-medium whitespace-nowrap
                glass-card hover:glass-card-strong
                text-gray-700 dark:text-gray-300
                shadow-md hover:shadow-lg
                transition-all duration-300
                border border-white/30 dark:border-gray-700/30
              "
            >
              <Icon className="w-3.5 h-3.5 text-primary-500" />
              {template.text}
            </motion.button>
          );
        })}
      </div>
    </div>
  );
};
