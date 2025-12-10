/**
 * @fileoverview Chat input component with send button and animations
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Loader2, Sparkles } from 'lucide-react';
import { Translations } from '@/i18n/translations';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  t: Translations;
}

/**
 * Text input field for composing and sending chat messages.
 * Features animated send button, loading state, and focus effects.
 *
 * @param props - Component props
 * @param props.onSendMessage - Callback function to handle message submission
 * @param props.isLoading - Whether the chat is currently processing a message
 * @param props.t - Translation object
 * @returns Rendered chat input component
 */
export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading, t }) => {
  const [input, setInput] = useState('');
  const [isFocused, setIsFocused] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const isButtonEnabled = input.trim() && !isLoading;

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className={`relative transition-all duration-300 ${isFocused ? 'scale-[1.01]' : 'scale-100'}`}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={t.chat.inputPlaceholder}
          disabled={isLoading}
          className="input-modern pr-24"
        />

        <AnimatePresence>
          {isFocused && (
            <motion.div
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0 }}
              className="absolute left-4 -top-3 flex items-center gap-1 px-2 py-0.5 bg-gradient-to-r from-primary-500 to-accent-500 rounded-full shadow-lg"
            >
              <Sparkles className="w-3 h-3 text-white" />
              <span className="text-xs text-white font-medium">AI готов помочь</span>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2">
          <motion.button
            type="submit"
            disabled={!isButtonEnabled}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className={`
              p-3 rounded-xl font-medium transition-all duration-300
              ${isButtonEnabled
                ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-500/40 hover:shadow-glow-md'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
              }
            `}
          >
            <AnimatePresence mode="wait">
              {isLoading ? (
                <motion.div
                  key="loading"
                  initial={{ rotate: 0 }}
                  animate={{ rotate: 360 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                >
                  <Loader2 className="w-5 h-5" />
                </motion.div>
              ) : (
                <motion.div
                  key="send"
                  initial={{ scale: 0, rotate: -45 }}
                  animate={{ scale: 1, rotate: 0 }}
                  exit={{ scale: 0, rotate: 45 }}
                  transition={{ type: 'spring', stiffness: 200 }}
                >
                  <Send className="w-5 h-5" />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>
        </div>
      </div>
    </form>
  );
};
