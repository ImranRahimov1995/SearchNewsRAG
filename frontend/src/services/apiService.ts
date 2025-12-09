/**
 * @fileoverview API service for NewsChat backend communication
 */

import axios, { AxiosInstance } from 'axios';
import { IChatRequest, IChatResponse, IChatSession, ITrendingTopic, IIndexStatus } from '@/types';

const DEFAULT_API_URL = 'http://0.0.0.0:8000';
const REQUEST_TIMEOUT = 30000;
const MOCK_SYNC_DELAY_MS = 5 * 60 * 1000;
const MOCK_TOTAL_NEWS = 15420;

/**
 * Service class for handling all API communications.
 * Implements singleton pattern for consistent API instance management.
 */
class ApiService {
  private api: AxiosInstance;
  private baseUrl: string;

  constructor() {
    this.baseUrl = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_URL;
    
    this.api = axios.create({
      baseURL: this.baseUrl,
      timeout: REQUEST_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  /**
   * Configures axios interceptors for error handling.
   * @private
   */
  private setupInterceptors(): void {
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Creates a new chat session.
   * @returns Promise resolving to session information
   */
  async createSession(): Promise<IChatSession> {
    return {
      sessionId: `local-${Date.now()}`,
      createdAt: new Date(),
    };
  }

  /**
   * Sends a message to the chat API.
   * @param request - The chat request containing query and language
   * @returns Promise resolving to chat response with answer and metadata
   * @throws Error with detailed message if API request fails
   */
  async sendMessage(request: IChatRequest): Promise<IChatResponse> {
    try {
      const response = await this.api.post('/chat/ask', request);
      return response.data;
    } catch (error: any) {
      if (error.response?.data?.detail) {
        console.error('API Error Details:', error.response.data.detail);
        const errorMsg = error.response.data.detail
          .map((err: any) => err.msg)
          .join(', ');
        throw new Error(errorMsg);
      }
      console.error('Failed to send message:', error);
      throw error;
    }
  }

  /**
   * Retrieves trending topics.
   * @returns Promise resolving to array of trending topics
   */
  async getTrendingTopics(): Promise<ITrendingTopic[]> {
    const lang = localStorage.getItem('newschat-language') || 'az';
    
    const topics: Record<string, ITrendingTopic[]> = {
      az: [
        { topic: 'Texnologiya', count: 245, trend: 'up' },
        { topic: 'Siyasət', count: 189, trend: 'down' },
        { topic: 'İqtisadiyyat', count: 156, trend: 'up' },
        { topic: 'İdman', count: 134, trend: 'stable' },
        { topic: 'Elm', count: 98, trend: 'up' },
      ],
      en: [
        { topic: 'Technology', count: 245, trend: 'up' },
        { topic: 'Politics', count: 189, trend: 'down' },
        { topic: 'Economy', count: 156, trend: 'up' },
        { topic: 'Sports', count: 134, trend: 'stable' },
        { topic: 'Science', count: 98, trend: 'up' },
      ],
      ru: [
        { topic: 'Технологии', count: 245, trend: 'up' },
        { topic: 'Политика', count: 189, trend: 'down' },
        { topic: 'Экономика', count: 156, trend: 'up' },
        { topic: 'Спорт', count: 134, trend: 'stable' },
        { topic: 'Наука', count: 98, trend: 'up' },
      ],
    };
    
    return topics[lang] || topics.az;
  }

  /**
   * Retrieves news index synchronization status.
   * @returns Promise resolving to index status information
   */
  async getIndexStatus(): Promise<IIndexStatus> {
    return {
      lastSync: new Date(Date.now() - MOCK_SYNC_DELAY_MS),
      totalNews: MOCK_TOTAL_NEWS,
      status: 'synced',
    };
  }
}

export const apiService = new ApiService();
