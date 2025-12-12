/**
 * @fileoverview React hook for managing chat state and messages
 */

import { useState, useCallback, useEffect, useRef, useReducer } from 'react';
import { IMessage, IChatRequest, TimeFilter, INewsEvent, ISource, IRetrievedDocument } from '@/types';
import { apiService } from '@/services/apiService';

const DEFAULT_LANGUAGE = 'ru';
const DEFAULT_FILTER: TimeFilter = 'all';

/**
 * Transforms API sources into news event objects.
 * @param sources - Array of source objects from API response
 * @returns Array of formatted news events
 */
const transformSourcesToEvents = (
  sources: ISource[], 
  retrievedDocs: IRetrievedDocument[] = []
): INewsEvent[] => {
  return sources.map((source: ISource, index: number) => {
    // Find matching document by URL or doc_id
    const matchingDoc = retrievedDocs.find(
      (doc: IRetrievedDocument) => 
        doc.url === source.url || 
        String(doc.doc_id) === String(source.id)
    );
    
    return {
      id: source.id || `event-${Date.now()}-${index}`,
      title: String(source.title || source.headline || source.name || 'Без заголовка'),
      category: String(matchingDoc?.category || source.category || 'Общее'),
      date: String(source.date || source.published_at || new Date().toISOString()),
      summary: String(matchingDoc?.preview || source.summary || source.description || ''),
      sentiment: (matchingDoc?.sentiment || source.sentiment as 'positive' | 'neutral' | 'negative') || 'neutral',
      url: source.url || matchingDoc?.url,
      source: source.name || 'Неизвестный источник',
    };
  });
};

/**
 * Creates an error message object.
 * @param error - Error object or message
 * @returns Formatted error message
 */
const createErrorMessage = (error: Error | { message?: string }): IMessage => ({
  id: `error-${Date.now()}`,
  type: 'bot',
  content: error.message || 'Извините, произошла ошибка. Попробуйте еще раз.',
  timestamp: new Date(),
});

/**
 * Custom hook for managing chat messages and communication with API.
 * Handles message state, loading state, auto-scrolling, and filter management.
 *
 * @returns Object containing messages, loading state, send function, filter controls, and scroll ref
 *
 * @example
 * const { messages, isLoading, sendMessage, filter, setFilter, messagesEndRef } = useChat();
 * sendMessage('Покажи новости');
 */
export const useChat = () => {
  const [messages, setMessages] = useState<IMessage[]>([]);
  const [filter, setFilter] = useState<TimeFilter>(DEFAULT_FILTER);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Use ref for loading state to avoid closure issues in async callbacks
  const isLoadingRef = useRef(false);
  const [, forceUpdate] = useReducer(x => x + 1, 0);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      const userMessage: IMessage = {
        id: `user-${Date.now()}`,
        type: 'user',
        content,
        timestamp: new Date(),
      };

      setMessages((prev: IMessage[]) => [...prev, userMessage]);
      isLoadingRef.current = true;
      forceUpdate();

      try {
        const request: IChatRequest = {
          query: content,
          language: DEFAULT_LANGUAGE,
        };

        const response = await apiService.sendMessage(request);

        const events = transformSourcesToEvents(
          response.sources, 
          response.retrieved_documents
        );

        const botMessage: IMessage = {
          id: `bot-${Date.now()}`,
          type: 'bot',
          content: response.answer,
          timestamp: new Date(),
          events: events.length > 0 ? events : undefined,
          keywords: response.key_facts,
        };

        setMessages((prev: IMessage[]) => [...prev, botMessage]);
      } catch (error) {
        console.error('Failed to send message:', error);
        const errorMessage = createErrorMessage(error instanceof Error ? error : { message: String(error) });
        setMessages((prev: IMessage[]) => [...prev, errorMessage]);
      } finally {
        isLoadingRef.current = false;
        forceUpdate();
      }
    },
    []
  );

  return {
    messages,
    isLoading: isLoadingRef.current,
    sendMessage,
    filter,
    setFilter,
    messagesEndRef,
  };
};
