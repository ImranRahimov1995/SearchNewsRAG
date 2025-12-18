/**
 * @fileoverview Type definitions for NewsChat application
 */

export interface IMessage {
  id: string;
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
  events?: INewsEvent[];
  keywords?: string[];
}

export interface INewsEvent {
  id: string;
  title: string;
  category: string;
  date: string;
  summary?: string;
  sentiment?: 'positive' | 'neutral' | 'negative';
  url?: string;
  source?: string;
}

export type TimeFilter = 'today' | 'week' | 'month' | 'year' | 'all';

export interface IFilterOptions {
  timeRange: TimeFilter;
  category?: string;
}

export interface IChatSession {
  sessionId: string;
  createdAt: Date;
}

export interface IChatRequest {
  query: string;
  language?: string;
}

export interface ISource {
  id: string;
  name: string;
  url?: string;
  category?: string;
  title?: string;
  headline?: string;
  date?: string;
  published_at?: string;
  summary?: string;
  description?: string;
  sentiment?: 'positive' | 'neutral' | 'negative';
  [key: string]: unknown;
}

export interface IRetrievedDocument {
  doc_id: number;
  score: number;
  category?: string;
  importance?: number;
  source?: string;
  url?: string;
  preview?: string;
  sentiment?: 'positive' | 'neutral' | 'negative';
  [key: string]: unknown;
}

export interface IChatResponse {
  query: string;
  language: string;
  intent: string;
  answer: string;
  sources: ISource[];
  confidence: string;
  key_facts: string[];
  retrieved_documents: IRetrievedDocument[];
  total_found: number;
  handler_used: string;
}

export interface IApiError {
  detail: Array<{
    loc: Array<string | number>;
    msg: string;
    type: string;
  }>;
}

export interface ITrendingTopic {
  topic: string;
  count: number;
  trend: 'up' | 'down' | 'stable';
}

export interface IIndexStatus {
  lastSync: Date;
  totalNews: number;
  status: 'synced' | 'syncing' | 'error';
}

export interface ICategory {
  category: string;
  count: number;
}

export interface ICategoriesResponse {
  categories: ICategory[];
  total_documents: number;
}

export interface INewsItem {
  id: string;
  content: string;
  category: string | null;
  date: string | null;
  importance: number | null;
}

export interface IPaginationInfo {
  count: number;
  next: string | null;
  previous: string | null;
}

export interface INewsListResponse extends IPaginationInfo {
  results: {
    news: INewsItem[];
  };
}

export type DateFilter = 'today' | 'week' | 'month' | 'all';
export type SortOrder = 'desc' | 'asc';

export type Theme = 'light' | 'dark';

export * from './universe';
