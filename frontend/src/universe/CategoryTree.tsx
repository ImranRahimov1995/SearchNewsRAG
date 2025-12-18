import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, Folder, FileText, Hash } from 'lucide-react';
import { CategoryNode, NewsInCategory } from './api';

interface CategoryTreeProps {
  categories: CategoryNode[];
  onSelectNews: (newsIds: number[], title: string) => void;
}

export function CategoryTree({ categories, onSelectNews }: CategoryTreeProps) {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [expandedSubcategories, setExpandedSubcategories] = useState<Set<string>>(new Set());

  const toggleCategory = (name: string) => {
    const next = new Set(expandedCategories);
    if (next.has(name)) {
      next.delete(name);
    } else {
      next.add(name);
    }
    setExpandedCategories(next);
  };

  const toggleSubcategory = (key: string) => {
    const next = new Set(expandedSubcategories);
    if (next.has(key)) {
      next.delete(key);
    } else {
      next.add(key);
    }
    setExpandedSubcategories(next);
  };

  const handleNewsClick = (news: NewsInCategory) => {
    onSelectNews([news.id], news.title);
  };

  const handleCategoryNewsClick = (category: CategoryNode) => {
    const allNews = [
      ...category.news,
      ...category.subcategories.flatMap(s => s.news),
    ];
    const newsIds = allNews.map(n => n.id);
    onSelectNews(newsIds, category.name);
  };

  return (
    <div className="space-y-1">
      {categories.map((category) => {
        const isExpanded = expandedCategories.has(category.name);
        const hasSubcategories = category.subcategories.length > 0;
        const hasDirectNews = category.news.length > 0;

        return (
          <div key={category.name} className="select-none">
            <motion.div
              className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-white/10 cursor-pointer group"
              onClick={() => toggleCategory(category.name)}
            >
              <motion.div
                initial={false}
                animate={{ rotate: isExpanded ? 90 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </motion.div>
              <Folder className="w-4 h-4 text-primary-400" />
              <span className="flex-1 text-sm font-semibold text-gray-200 truncate">
                {category.name}
              </span>
              <span className="text-xs text-gray-500 group-hover:text-gray-400">
                {category.count}
              </span>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={(e) => {
                  e.stopPropagation();
                  handleCategoryNewsClick(category);
                }}
                className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-primary-500/20"
                title="Show all news in category"
              >
                <Hash className="w-3 h-3 text-primary-400" />
              </motion.button>
            </motion.div>

            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden ml-4 border-l border-gray-700/50"
                >
                  {hasSubcategories && category.subcategories.map((subcat) => {
                    const subKey = `${category.name}-${subcat.name}`;
                    const isSubExpanded = expandedSubcategories.has(subKey);

                    return (
                      <div key={subKey}>
                        <motion.div
                          className="flex items-center gap-2 px-2 py-1 rounded-lg hover:bg-white/10 cursor-pointer ml-2"
                          onClick={() => toggleSubcategory(subKey)}
                        >
                          <motion.div
                            initial={false}
                            animate={{ rotate: isSubExpanded ? 90 : 0 }}
                            transition={{ duration: 0.2 }}
                          >
                            <ChevronRight className="w-3 h-3 text-gray-500" />
                          </motion.div>
                          <Folder className="w-3.5 h-3.5 text-accent-400" />
                          <span className="flex-1 text-xs font-medium text-gray-300 truncate">
                            {subcat.name}
                          </span>
                          <span className="text-[10px] text-gray-500">
                            {subcat.news.length}
                          </span>
                        </motion.div>

                        <AnimatePresence>
                          {isSubExpanded && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              className="overflow-hidden ml-6"
                            >
                              {subcat.news.map((news) => (
                                <motion.div
                                  key={news.id}
                                  whileHover={{ x: 2 }}
                                  onClick={() => handleNewsClick(news)}
                                  className="flex items-center gap-2 px-2 py-1 rounded hover:bg-white/5 cursor-pointer"
                                >
                                  <FileText className="w-3 h-3 text-gray-500" />
                                  <span className="text-[11px] text-gray-400 truncate flex-1">
                                    {news.title}
                                  </span>
                                </motion.div>
                              ))}
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    );
                  })}

                  {hasDirectNews && (
                    <div className="ml-2">
                      {category.news.slice(0, 10).map((news) => (
                        <motion.div
                          key={news.id}
                          whileHover={{ x: 2 }}
                          onClick={() => handleNewsClick(news)}
                          className="flex items-center gap-2 px-2 py-1 rounded hover:bg-white/5 cursor-pointer"
                        >
                          <FileText className="w-3 h-3 text-gray-500" />
                          <span className="text-[11px] text-gray-400 truncate flex-1">
                            {news.title}
                          </span>
                        </motion.div>
                      ))}
                      {category.news.length > 10 && (
                        <div className="text-[10px] text-gray-600 px-2 py-1">
                          +{category.news.length - 10} more...
                        </div>
                      )}
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
}
