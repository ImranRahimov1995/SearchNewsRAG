/**
 * @fileoverview Main application component for NewsChat
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Menu, X } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { useChat } from '@/hooks/useChat';
import { useAnalytics } from '@/hooks/useAnalytics';
import { useLanguage } from '@/hooks/useLanguage';
import { ThemeToggle } from '@/components/ThemeToggle';
import { ChatMessages } from '@/components/ChatMessages';
import { ChatInput } from '@/components/ChatInput';
import { TimeFilterSelector } from '@/components/TimeFilterSelector';
import { QuickQueryTemplates } from '@/components/QuickQueryTemplates';
import { IndexStatusPanel } from '@/components/IndexStatusPanel';
import { CategoriesPanel } from '@/components/TrendingTopicsPanel';
import { LatestNewsPanel } from '@/components/LatestNewsPanel';
import { UniversePage } from '@/universe';

const HEADER_ANIMATION = {
  initial: { y: -100 },
  animate: { y: 0 },
};

const FILTER_ANIMATION = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  transition: { delay: 0.2 },
};

const INPUT_ANIMATION = {
  initial: { y: 100 },
  animate: { y: 0 },
};

const SIDEBAR_ANIMATION = {
  initial: { x: 100, opacity: 0 },
  animate: { x: 0, opacity: 1 },
  transition: { delay: 0.3 },
};

const MOBILE_OVERLAY_ANIMATION = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

const MOBILE_SIDEBAR_ANIMATION = {
  initial: { x: '100%' },
  animate: { x: 0 },
  exit: { x: '100%' },
  transition: { type: 'spring' as const, damping: 25 },
};

/**
 * Root application component.
 * Manages layout, theme, chat state, and responsive sidebar navigation.
 *
 * @returns Rendered application
 */
function App() {
  const { theme, toggleTheme } = useTheme();
  const { language, setLanguage, t } = useLanguage();
  const { messages, isLoading, sendMessage, filter, setFilter, messagesEndRef } = useChat();
  const { categories, latestNews, indexStatus, isLoading: analyticsLoading } = useAnalytics();
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const [view, setView] = React.useState<'chat' | 'universe'>('chat');

  return (
    <div className="h-screen flex flex-col overflow-hidden" style={{ height: '100dvh' }}>
      <motion.header
        {...HEADER_ANIMATION}
        className="flex-shrink-0 glass-card-strong border-b border-white/20 dark:border-gray-700/30 shadow-xl z-10"
      >
        <div className="w-full px-3 sm:px-6 py-2 sm:py-3 flex items-center justify-between">
          <motion.div
            className="flex items-center gap-2 sm:gap-3"
            whileHover={{ scale: 1.02 }}
          >
            <div className="p-2 sm:p-3 rounded-xl sm:rounded-2xl bg-gradient-to-br from-primary-500 via-primary-600 to-accent-600 shadow-lg shadow-primary-500/50">
              <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg sm:text-2xl font-black gradient-text">
                {t.app.title}
              </h1>
              <p className="hidden sm:block text-xs font-medium text-gray-600 dark:text-gray-400">
                {t.app.subtitle}
              </p>
            </div>
          </motion.div>

          <div className="flex items-center gap-2 sm:gap-3">
            <div className="flex gap-1 p-1 rounded-lg sm:rounded-xl glass-card">
              {(
                [
                  { id: 'chat' as const, label: t.nav.chat },
                  { id: 'universe' as const, label: t.nav.universe },
                ]
              ).map((item) => (
                <motion.button
                  key={item.id}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setView(item.id)}
                  className={`px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg text-xs font-bold transition-all duration-300 ${
                    view === item.id
                      ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-md'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                >
                  {item.label}
                </motion.button>
              ))}
            </div>
            <div className="flex gap-1 p-1 rounded-lg sm:rounded-xl glass-card">
              {(['az', 'en', 'ru'] as const).map((lang) => (
                <motion.button
                  key={lang}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setLanguage(lang)}
                  className={`px-2 sm:px-3 py-1 sm:py-1.5 rounded-md sm:rounded-lg text-xs font-bold uppercase transition-all duration-300 ${
                    language === lang
                      ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-md'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                >
                  {lang}
                </motion.button>
              ))}
            </div>
            <ThemeToggle isDark={theme === 'dark'} onToggle={toggleTheme} />

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="lg:hidden p-2 sm:p-3 rounded-xl sm:rounded-2xl glass-card-strong shadow-lg"
            >
              {isSidebarOpen ? (
                <X className="w-5 h-5 sm:w-5 sm:h-5 text-gray-700 dark:text-gray-300" />
              ) : (
                <Menu className="w-5 h-5 sm:w-5 sm:h-5 text-gray-700 dark:text-gray-300" />
              )}
            </motion.button>
          </div>
        </div>
      </motion.header>

      {view === 'universe' ? (
        <UniversePage onBackToChat={() => setView('chat')} t={t} isDark={theme === 'dark'} />
      ) : (
        <div className="flex-1 flex overflow-hidden w-full min-h-0">
          <div className="flex-1 flex flex-col min-w-0 min-h-0">
            <motion.div
              {...FILTER_ANIMATION}
              className="flex-shrink-0 px-3 sm:px-6 py-3 sm:py-4 glass-card border-b border-white/20 dark:border-gray-700/30"
            >
              <TimeFilterSelector currentFilter={filter} onFilterChange={setFilter} t={t} />
            </motion.div>

            <ChatMessages messages={messages} messagesEndRef={messagesEndRef} isLoading={isLoading} t={t} />

            <motion.div
              {...INPUT_ANIMATION}
              className="flex-shrink-0 glass-card-strong border-t border-white/20 dark:border-gray-700/30 p-3 sm:p-4 md:p-6 shadow-2xl"
            >
              <QuickQueryTemplates onSelectTemplate={sendMessage} t={t} />
              <ChatInput onSendMessage={sendMessage} isLoading={isLoading} t={t} />
            </motion.div>
          </div>

          <motion.aside
            {...SIDEBAR_ANIMATION}
            className="hidden lg:block w-96 glass-card border-l border-white/20 dark:border-gray-700/30 p-6 overflow-y-auto scrollbar-custom"
          >
            <div className="space-y-4">
              <IndexStatusPanel status={indexStatus} t={t} />
              <CategoriesPanel categories={categories} loading={analyticsLoading} t={t} />
              <LatestNewsPanel news={latestNews} loading={analyticsLoading} t={t} />
            </div>
          </motion.aside>

          {isSidebarOpen && (
            <motion.div
              {...MOBILE_OVERLAY_ANIMATION}
              className="lg:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
              onClick={() => setIsSidebarOpen(false)}
            >
              <motion.aside
                {...MOBILE_SIDEBAR_ANIMATION}
                onClick={(e) => e.stopPropagation()}
                className="absolute right-0 top-0 h-full w-[85vw] max-w-sm glass-card-strong border-l border-white/20 dark:border-gray-700/30 p-4 sm:p-6 overflow-y-auto shadow-2xl"
              >
                <div className="space-y-4">
                  <IndexStatusPanel status={indexStatus} t={t} />
                  <CategoriesPanel categories={categories} loading={analyticsLoading} t={t} />
                  <LatestNewsPanel news={latestNews} loading={analyticsLoading} t={t} />
                </div>
              </motion.aside>
            </motion.div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
