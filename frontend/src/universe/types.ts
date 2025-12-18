export type Sentiment = 'positive' | 'neutral' | 'negative';
export type NodeKind = 'entity' | 'news' | 'event';

export interface GraphNodeMeta {
  source?: string;
  date?: string;
  sentiment?: Sentiment;
  importance?: number;
  tags?: string[];
  entities?: string[];
  category?: string;
  url?: string;
}

export interface GraphNode {
  id: string;
  kind: NodeKind;
  title: string;
  subtitle?: string;
  meta?: GraphNodeMeta;
  pos: {
    xPct: number;
    yPct: number;
  };
}

export interface GraphEdge {
  id: string;
  from: string;
  to: string;
  label?: string;
  strength: 1 | 2 | 3;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  total_news: number;
  total_entities: number;
}

export interface CategoryOption {
  category: string;
  count: number;
}
