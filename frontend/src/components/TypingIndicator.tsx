/**
 * @fileoverview Typing indicator component for bot responses
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { Translations } from '@/i18n/translations';

interface TypingIndicatorProps {
  t?: Translations;
}

const TYPING_DOT_ANIMATION = {
  scale: [1, 1.3, 1],
  opacity: [0.4, 1, 0.4],
};

const TYPING_TRANSITION = {
  duration: 1.4,
  repeat: Infinity,
  ease: 'easeInOut' as const,
};

/**
 * Animated typing indicator shown when bot is processing a response.
 * Displays rotating loader icon and pulsing dots.
 * 
 * @param props - Component props
 * @param props.t - Translation object (optional, for future use)
 * @returns Rendered typing indicator component
 */
export const TypingIndicator: React.FC<TypingIndicatorProps> = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="flex items-end gap-3 mb-6"
    >
      <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        >
          <Loader2 className="w-5 h-5 text-white" />
        </motion.div>
      </div>

      <div className="message-bubble-bot">
        <div className="typing-indicator">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="typing-dot"
              animate={TYPING_DOT_ANIMATION}
              transition={{
                ...TYPING_TRANSITION,
                delay: i * 0.2,
              }}
            />
          ))}
        </div>
      </div>
    </motion.div>
  );
};