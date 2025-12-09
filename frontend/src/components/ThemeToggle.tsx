/**
 * @fileoverview Theme toggle button for switching between light and dark modes
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Sun, Moon } from 'lucide-react';

interface ThemeToggleProps {
  isDark: boolean;
  onToggle: () => void;
}

const TRANSITION_CONFIG = {
  duration: 0.3,
  ease: [0.4, 0, 0.2, 1] as [number, number, number, number],
};

/**
 * Animated theme toggle button with sun/moon icons.
 * Features smooth scale and rotation transitions with glassmorphism styling.
 * 
 * @param props - Component props
 * @param props.isDark - Whether dark mode is currently active
 * @param props.onToggle - Callback function when theme is toggled
 * @returns Rendered theme toggle button
 * 
 * @example
 * ```tsx
 * <ThemeToggle isDark={isDark} onToggle={() => setIsDark(!isDark)} />
 * ```
 */
export const ThemeToggle: React.FC<ThemeToggleProps> = ({ isDark, onToggle }) => {
  return (
    <motion.button
      onClick={onToggle}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className="relative p-3 rounded-2xl glass-card-strong shadow-lg hover:shadow-glow-sm transition-all duration-300"
      aria-label="Toggle theme"
    >
      <div className="relative w-6 h-6">
        <motion.div
          initial={false}
          animate={{ 
            scale: isDark ? 0 : 1,
            rotate: isDark ? 180 : 0,
            opacity: isDark ? 0 : 1
          }}
          transition={TRANSITION_CONFIG}
          className="absolute inset-0 flex items-center justify-center"
        >
          <Sun className="w-6 h-6 text-amber-500" />
        </motion.div>
        
        <motion.div
          initial={false}
          animate={{ 
            scale: isDark ? 1 : 0,
            rotate: isDark ? 0 : -180,
            opacity: isDark ? 1 : 0
          }}
          transition={TRANSITION_CONFIG}
          className="absolute inset-0 flex items-center justify-center"
        >
          <Moon className="w-6 h-6 text-indigo-400" />
        </motion.div>
      </div>
    </motion.button>
  );
};
