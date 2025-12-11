/**
 * @fileoverview Categories sidebar panel with document counts
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Tag } from 'lucide-react';
import { ICategory } from '@/types';
import { Translations } from '@/i18n/translations';

interface CategoriesPanelProps {
  categories: ICategory[];
  loading?: boolean;
  t: Translations;
}

const MAX_CATEGORIES_DISPLAY = 8;

export const CategoriesPanel: React.FC<CategoriesPanelProps> = ({ categories, loading, t }) => {
  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card-modern p-5"
      >
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 shadow-lg">
            <Tag className="w-4 h-4 text-white" />
          </div>
          <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">
            {t.categories.title}
          </h3>
        </div>
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-12 glass-card rounded-xl animate-pulse" />
          ))}
        </div>
      </motion.div>
    );
  }

  if (categories.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-modern p-5"
    >
      <div className="flex items-center gap-2 mb-4">
        <div className="p-2 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 shadow-lg">
          <Tag className="w-4 h-4 text-white" />
        </div>
        <h3 className="text-sm font-bold text-gray-900 dark:text-gray-100">
          {t.categories.title}
        </h3>
      </div>

      <div className="space-y-2">
        {categories.slice(0, MAX_CATEGORIES_DISPLAY).map((category, index) => {
          return (
            <motion.div
              key={category.category}
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
                  {category.category}
                </span>
              </div>

              <div className="flex items-center gap-3 flex-shrink-0">
                <span className="text-xs font-bold text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded-lg">
                  {category.count}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};
