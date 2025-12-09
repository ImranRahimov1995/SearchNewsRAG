/**
 * @fileoverview Message bubble component with animations
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Bot, User } from 'lucide-react';
import { IMessage } from '@/types';
import { highlightKeywords } from '@/utils/textUtils';

interface MessageBubbleProps {
  message: IMessage;
}

const ANIMATION_CONFIG = {
  duration: 0.4,
  ease: [0.4, 0, 0.2, 1] as [number, number, number, number],
  delay: 0.05,
};

const AVATAR_ANIMATION = {
  delay: 0.2,
  type: 'spring' as const,
  stiffness: 200,
};

/**
 * Displays a single chat message with user/bot avatar and animations.
 * Supports keyword highlighting for bot messages.
 * 
 * @param props - Component props
 * @param props.message - Message object to display
 * @returns Rendered message bubble component
 */
export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.type === 'user';
  
  const formattedContent = message.keywords && !isUser
    ? highlightKeywords(message.content, message.keywords)
    : message.content;

  return (
    <motion.div
      initial={{ opacity: 0, x: isUser ? 20 : -20, scale: 0.95 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      transition={ANIMATION_CONFIG}
      className={`flex items-end gap-3 mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      {!isUser && (
        <motion.div 
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={AVATAR_ANIMATION}
          className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg"
        >
          <Bot className="w-5 h-5 text-white" />
        </motion.div>
      )}

      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[75%]`}>
        <motion.div 
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          className={isUser ? 'message-bubble-user' : 'message-bubble-bot'}
        >
          <p
            className="text-[15px] leading-relaxed"
            dangerouslySetInnerHTML={{ __html: formattedContent }}
          />
        </motion.div>
        
        <span className={`text-xs mt-1.5 px-2 ${isUser ? 'text-primary-600 dark:text-primary-400' : 'text-gray-500 dark:text-gray-400'}`}>
          {message.timestamp.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      </div>

      {isUser && (
        <motion.div 
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={AVATAR_ANIMATION}
          className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg"
        >
          <User className="w-5 h-5 text-white" />
        </motion.div>
      )}
    </motion.div>
  );
};