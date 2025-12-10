/**
 * @fileoverview Chat messages container with welcome screen
 */

import React from 'react';
import { AnimatePresence } from 'framer-motion';
import { MessageBubble } from './MessageBubble';
import { NewsEventCard } from './NewsEventCard';
import { TypingIndicator } from './TypingIndicator';
import { WelcomeScreen } from './WelcomeScreen';
import { IMessage } from '@/types';
import { Translations } from '@/i18n/translations';

interface ChatMessagesProps {
  messages: IMessage[];
  messagesEndRef: React.RefObject<HTMLDivElement>;
  isLoading?: boolean;
  t: Translations;
}

/**
 * Container component for displaying chat messages with animations.
 * Shows welcome screen when no messages exist, typing indicator when loading.
 *
 * @param props - Component props
 * @param props.messages - Array of chat messages to display
 * @param props.messagesEndRef - Ref for auto-scrolling to bottom
 * @param props.isLoading - Whether bot is currently generating response
 * @returns Rendered chat messages container
 */
export const ChatMessages: React.FC<ChatMessagesProps> = ({
  messages,
  messagesEndRef,
  isLoading = false,
  t,
}) => {
  if (messages.length === 0 && !isLoading) {
    return <WelcomeScreen t={t} />;
  }

  return (
    <div className="flex-1 overflow-y-auto px-6 py-8 scrollbar-custom">
      <AnimatePresence mode="popLayout">
        {messages.map((message) => (
          <div key={message.id}>
            <MessageBubble message={message} />

            {message.events && message.events.length > 0 && (
              <div className="mt-4">
                <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-3 ml-2 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary-500"></span>
                  {t.topEvents}
                </p>
                {message.events.map((event, index) => (
                  <NewsEventCard key={event.id} event={event} index={index} t={t} />
                ))}
              </div>
            )}
          </div>
        ))}

        {isLoading && <TypingIndicator key="typing" t={t} />}
      </AnimatePresence>

      <div ref={messagesEndRef} />
    </div>
  );
};
