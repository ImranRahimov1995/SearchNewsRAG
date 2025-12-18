/**
 * @fileoverview Type definitions for News Universe / Event Map feature
 */

export type Sentiment = 'positive' | 'neutral' | 'negative';

export type EntityType = 'person' | 'organization' | 'location' | 'event' | 'topic';

export type StorylineStage = 'announcement' | 'discussion' | 'action' | 'result' | 'aftermath';

export interface IEntity {
  id: string;
  name: string;
  type: EntityType;
  mentionCount: number;
  lastMentioned?: string;
  imageUrl?: string;
  description?: string;
}

export interface IEventCluster {
  id: string;
  title: string;
  summary: string;
  category: string;
  subcategory?: string;
  articleCount: number;
  importance: number;
  sentiment: Sentiment;
  startDate: string;
  endDate?: string;
  mainEntities: IEntity[];
  keywords: string[];
  region?: string;
  isActive: boolean;
  trendDirection: 'rising' | 'stable' | 'declining';
}

export interface IStorylineEvent {
  id: string;
  title: string;
  summary: string;
  date: string;
  stage: StorylineStage;
  sentiment: Sentiment;
  importance: number;
  entities: IEntity[];
  sourceCount: number;
  sources: IStorylineSource[];
}

export interface IStorylineSource {
  id: string;
  title: string;
  url: string;
  source: string;
  date: string;
  preview?: string;
}

export interface IStoryline {
  id: string;
  title: string;
  description: string;
  category: string;
  startDate: string;
  endDate?: string;
  isOngoing: boolean;
  totalArticles: number;
  mainEntities: IEntity[];
  events: IStorylineEvent[];
  sentiment: Sentiment;
  importance: number;
  keywords: string[];
}

export interface ITimelinePoint {
  id: string;
  date: string;
  clusters: IEventCluster[];
}

export interface ICategoryTimeline {
  category: string;
  displayName: string;
  icon?: string;
  color: string;
  totalArticles: number;
  activeStorylines: number;
  timeline: ITimelinePoint[];
  topClusters: IEventCluster[];
}

export interface IRegion {
  id: string;
  name: string;
  nameAz: string;
  eventCount: number;
  activeStorylines: number;
  importance: number;
  coordinates?: {
    lat: number;
    lng: number;
  };
}

export interface IDashboardStats {
  totalArticles: number;
  totalEntities: number;
  activeStorylines: number;
  categoriesCount: number;
  lastUpdated: string;
}

export interface IImportantEvent extends IEventCluster {
  relatedStorylines: string[];
  breakingNews: boolean;
}

export interface IUniverseDashboard {
  stats: IDashboardStats;
  importantEvents: IImportantEvent[];
  categories: ICategoryTimeline[];
  activeStorylines: IStoryline[];
  regions: IRegion[];
  trendingEntities: IEntity[];
}

export type ViewMode = 'dashboard' | 'category' | 'storyline' | 'entity' | 'search';

export interface IUniverseFilters {
  dateRange: {
    start: string;
    end: string;
  };
  categories: string[];
  sentiment?: Sentiment;
  minImportance?: number;
  regions?: string[];
  entities?: string[];
}
