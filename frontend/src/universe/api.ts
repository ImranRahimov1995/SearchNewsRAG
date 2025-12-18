import { GraphData, CategoryOption } from './types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchGraphData(
  category?: string,
  entity?: string,
  limit: number = 30
): Promise<GraphData> {
  const params = new URLSearchParams();
  if (category) params.set('category', category);
  if (entity) params.set('entity', entity);
  params.set('limit', limit.toString());

  const response = await fetch(`${API_BASE}/news/graph?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch graph data: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchCategories(): Promise<CategoryOption[]> {
  const response = await fetch(`${API_BASE}/news/categories`);
  if (!response.ok) {
    throw new Error(`Failed to fetch categories: ${response.statusText}`);
  }
  const data = await response.json();
  return data.categories || [];
}

export interface CategoryNode {
  name: string;
  count: number;
  subcategories: { name: string; news: NewsInCategory[] }[];
  news: NewsInCategory[];
}

export interface NewsInCategory {
  id: number;
  title: string;
  date: string | null;
  importance: number | null;
  entity_ids: number[];
}

export interface CategoryTreeResponse {
  categories: CategoryNode[];
  total_news: number;
}

export async function fetchCategoryTree(limitPerCategory: number = 20): Promise<CategoryTreeResponse> {
  const params = new URLSearchParams();
  params.set('limit_per_category', limitPerCategory.toString());
  
  const response = await fetch(`${API_BASE}/news/category-tree?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch category tree: ${response.statusText}`);
  }
  return response.json();
}

export interface EntityItem {
  id: number;
  name: string;
  type: string | null;
  news_count: number;
  news_ids: number[];
}

export interface EntityListResponse {
  entities: EntityItem[];
  total: number;
}

export async function fetchEntities(minNews: number = 2, limit: number = 100): Promise<EntityListResponse> {
  const params = new URLSearchParams();
  params.set('min_news', minNews.toString());
  params.set('limit', limit.toString());
  
  const response = await fetch(`${API_BASE}/news/entities?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch entities: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchEntityGraph(entityId?: number, limit: number = 50): Promise<GraphData> {
  const params = new URLSearchParams();
  if (entityId) params.set('entity_id', entityId.toString());
  params.set('limit', limit.toString());

  const response = await fetch(`${API_BASE}/news/entity-graph?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch entity graph: ${response.statusText}`);
  }
  return response.json();
}

export async function fetchNewsByIds(ids: number[]): Promise<GraphData> {
  const params = new URLSearchParams();
  params.set('ids', ids.join(','));

  const response = await fetch(`${API_BASE}/news/by-ids?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch news by ids: ${response.statusText}`);
  }
  return response.json();
}
