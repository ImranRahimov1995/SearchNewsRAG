/**
 * @fileoverview Welcome screen displayed when chat is empty
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Zap, TrendingUp, Search } from 'lucide-react';
import { Translations } from '@/i18n/translations';

interface WelcomeScreenProps {
  t: Translations;
}

interface Feature {
  icon: React.ComponentType<any>;
  title: string;
  description: string;
}

const HERO_ANIMATION = {
  initial: { opacity: 0, scale: 0.9 },
  animate: { opacity: 1, scale: 1 },
  transition: { duration: 0.5 },
};

const ICON_ANIMATION = {
  initial: { scale: 0 },
  animate: { scale: 1 },
  transition: { delay: 0.2, type: 'spring' as const, stiffness: 200 },
};

/**
 * Welcome screen shown before any messages are sent.
 * Features animated hero section, feature cards, and call-to-action.
 * 
 * @param props - Component props
 * @param props.t - Translation object
 * @returns Rendered welcome screen
 */
export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ t }) => {
  const FEATURES: Feature[] = [
    {
      icon: Sparkles,
      title: t.welcome.features.ai.title,
      description: t.welcome.features.ai.description,
    },
    {
      icon: Search,
      title: t.welcome.features.search.title,
      description: t.welcome.features.search.description,
    },
    {
      icon: TrendingUp,
      title: t.welcome.features.trends.title,
      description: t.welcome.features.trends.description,
    },
    {
      icon: Zap,
      title: t.welcome.features.instant.title,
      description: t.welcome.features.instant.description,
    },
  ];

  return (
    <div className="flex-1 flex items-center justify-center p-8">
      <motion.div {...HERO_ANIMATION} className="max-w-2xl w-full">
        <div className="text-center mb-12">
          <motion.div
            {...ICON_ANIMATION}
            className="inline-block p-6 rounded-3xl bg-gradient-to-br from-primary-500 via-primary-600 to-accent-600 shadow-2xl shadow-primary-500/30 mb-6"
          >
            <Sparkles className="w-16 h-16 text-white" />
          </motion.div>

          <motion.h2
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-4xl font-black mb-4"
          >
            <span className="gradient-text">{t.welcome.title}</span>
          </motion.h2>

          <motion.p
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-lg text-gray-600 dark:text-gray-400 max-w-xl mx-auto"
          >
            {t.welcome.subtitle}
          </motion.p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          {FEATURES.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
                whileHover={{ scale: 1.05, y: -5 }}
                className="card-modern p-6 group cursor-pointer"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 shadow-lg group-hover:shadow-glow-sm transition-all">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-1">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9 }}
          className="text-center"
        >
          <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center justify-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-green-500 animate-pulse-dot"></span>
            {t.welcome.cta}
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
};