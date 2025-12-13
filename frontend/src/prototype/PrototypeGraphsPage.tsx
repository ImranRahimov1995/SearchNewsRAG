import React from 'react';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Calendar,
  ExternalLink,
  Link2,
  Network,
  Route,
  Search,
  Share2,
  Tag,
  Users,
} from 'lucide-react';

type GraphVariant = 'single-chain' | 'multi-chain' | 'entity-hub';

type Sentiment = 'positive' | 'neutral' | 'negative';

type GraphNode = {
  id: string;
  kind: 'entity' | 'news' | 'event';
  title: string;
  subtitle?: string;
  meta?: {
    source?: string;
    date?: string;
    confidence?: number;
    sentiment?: Sentiment;
    importance?: number;
    tags?: string[];
    entities?: string[];
  };
  pos: {
    xPct: number;
    yPct: number;
  };
};

type GraphEdge = {
  id: string;
  from: string;
  to: string;
  label?: string;
  strength: 1 | 2 | 3;
};

type GraphModel = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};

function clampPct(value: number): number {
  return Math.max(0, Math.min(100, value));
}

function sentimentClasses(sentiment: Sentiment | undefined): string {
  if (sentiment === 'positive') return 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30';
  if (sentiment === 'negative') return 'bg-rose-500/15 text-rose-700 dark:text-rose-300 border-rose-500/30';
  return 'bg-gray-500/15 text-gray-700 dark:text-gray-300 border-gray-500/30';
}

function nodeAccent(kind: GraphNode['kind']): {
  ring: string;
  badge: string;
  glow: string;
} {
  if (kind === 'entity') {
    return {
      ring: 'ring-2 ring-accent-500/40',
      badge: 'bg-gradient-to-r from-accent-500 to-accent-600 text-white',
      glow: 'shadow-glow-accent',
    };
  }

  if (kind === 'event') {
    return {
      ring: 'ring-2 ring-primary-500/35',
      badge: 'bg-gradient-to-r from-primary-500 to-primary-600 text-white',
      glow: 'shadow-glow-sm',
    };
  }

  return {
    ring: 'ring-1 ring-white/30 dark:ring-gray-700/40',
    badge: 'glass-card',
    glow: 'shadow-elevated dark:shadow-elevated-dark',
  };
}

function buildGraphModel(variant: GraphVariant): GraphModel {
  if (variant === 'single-chain') {
    return {
      nodes: [
        {
          id: 'entity-aliyev',
          kind: 'entity',
          title: 'Ilham Aliyev',
          subtitle: 'Entity 중심 (cluster)',
          meta: {
            tags: ['person', 'president'],
            entities: ['Azerbaijan', 'Baku', 'government'],
          },
          pos: { xPct: 12, yPct: 18 },
        },
        {
          id: 'news-1',
          kind: 'news',
          title: 'Official meeting announced',
          subtitle: 'Statement published by press service',
          meta: {
            date: '2025-12-12 10:24',
            source: 'Telegram',
            sentiment: 'neutral',
            importance: 7,
            tags: ['statement', 'agenda'],
          },
          pos: { xPct: 28, yPct: 25 },
        },
        {
          id: 'news-2',
          kind: 'event',
          title: 'Meeting with delegation',
          subtitle: 'Key topics: energy, transport corridors',
          meta: {
            date: '2025-12-12 14:10',
            source: 'Qafqazinfo',
            sentiment: 'positive',
            importance: 9,
            tags: ['diplomacy', 'energy'],
            entities: ['delegation', 'minister'],
          },
          pos: { xPct: 48, yPct: 45 },
        },
        {
          id: 'news-3',
          kind: 'news',
          title: 'Follow-up reactions',
          subtitle: 'Opposition and analysts comment',
          meta: {
            date: '2025-12-12 19:40',
            source: 'Operativ',
            sentiment: 'neutral',
            importance: 6,
            tags: ['reaction', 'analysis'],
          },
          pos: { xPct: 66, yPct: 38 },
        },
        {
          id: 'news-4',
          kind: 'event',
          title: 'Signed memorandum',
          subtitle: 'Document strengthens cooperation',
          meta: {
            date: '2025-12-13 09:05',
            source: 'Telegram',
            sentiment: 'positive',
            importance: 8,
            tags: ['agreement'],
          },
          pos: { xPct: 84, yPct: 52 },
        },
      ],
      edges: [
        { id: 'e1', from: 'entity-aliyev', to: 'news-1', label: 'mentioned', strength: 2 },
        { id: 'e2', from: 'news-1', to: 'news-2', label: 'leads to', strength: 3 },
        { id: 'e3', from: 'news-2', to: 'news-3', label: 'covered by', strength: 2 },
        { id: 'e4', from: 'news-3', to: 'news-4', label: 'culminates', strength: 3 },
        { id: 'e5', from: 'entity-aliyev', to: 'news-2', label: 'central', strength: 3 },
        { id: 'e6', from: 'entity-aliyev', to: 'news-4', label: 'central', strength: 3 },
      ],
    };
  }

  if (variant === 'multi-chain') {
    return {
      nodes: [
        {
          id: 'cluster-aliyev',
          kind: 'entity',
          title: 'Ilham Aliyev',
          subtitle: 'Cluster A',
          meta: { tags: ['person', 'leadership'] },
          pos: { xPct: 12, yPct: 20 },
        },
        {
          id: 'cluster-economy',
          kind: 'entity',
          title: 'Economy & Energy',
          subtitle: 'Cluster B',
          meta: { tags: ['topic'] },
          pos: { xPct: 12, yPct: 62 },
        },
        {
          id: 'a1',
          kind: 'news',
          title: 'Speech excerpt',
          subtitle: 'Domestic priorities outlined',
          meta: {
            date: '2025-12-11 09:15',
            source: 'Telegram',
            sentiment: 'neutral',
            importance: 6,
            tags: ['speech'],
          },
          pos: { xPct: 34, yPct: 18 },
        },
        {
          id: 'a2',
          kind: 'event',
          title: 'Public appearance',
          subtitle: 'Ceremony in Baku',
          meta: {
            date: '2025-12-11 12:30',
            source: 'Operativ',
            sentiment: 'positive',
            importance: 7,
            tags: ['ceremony'],
            entities: ['Baku'],
          },
          pos: { xPct: 52, yPct: 25 },
        },
        {
          id: 'a3',
          kind: 'news',
          title: 'International coverage',
          subtitle: 'Foreign media recap',
          meta: {
            date: '2025-12-11 18:05',
            source: 'Qafqazinfo',
            sentiment: 'neutral',
            importance: 5,
            tags: ['media'],
          },
          pos: { xPct: 74, yPct: 15 },
        },
        {
          id: 'b1',
          kind: 'news',
          title: 'Gas corridor update',
          subtitle: 'New milestones reported',
          meta: {
            date: '2025-12-10 11:00',
            source: 'Telegram',
            sentiment: 'positive',
            importance: 8,
            tags: ['energy'],
            entities: ['pipeline'],
          },
          pos: { xPct: 34, yPct: 60 },
        },
        {
          id: 'b2',
          kind: 'event',
          title: 'Negotiations round',
          subtitle: 'Pricing and transit terms',
          meta: {
            date: '2025-12-10 15:20',
            source: 'Operativ',
            sentiment: 'neutral',
            importance: 7,
            tags: ['negotiation'],
          },
          pos: { xPct: 54, yPct: 70 },
        },
        {
          id: 'b3',
          kind: 'news',
          title: 'Market reaction',
          subtitle: 'Analysts discuss impacts',
          meta: {
            date: '2025-12-10 18:40',
            source: 'Qafqazinfo',
            sentiment: 'neutral',
            importance: 6,
            tags: ['market'],
          },
          pos: { xPct: 78, yPct: 64 },
        },
        {
          id: 'bridge-1',
          kind: 'event',
          title: 'Shared mention',
          subtitle: 'Cross-topic connector',
          meta: {
            date: '2025-12-11 20:10',
            source: 'Telegram',
            sentiment: 'neutral',
            importance: 7,
            tags: ['connector'],
          },
          pos: { xPct: 60, yPct: 46 },
        },
      ],
      edges: [
        { id: 'ea1', from: 'cluster-aliyev', to: 'a1', label: 'mentions', strength: 2 },
        { id: 'ea2', from: 'a1', to: 'a2', label: 'timeline', strength: 3 },
        { id: 'ea3', from: 'a2', to: 'a3', label: 'coverage', strength: 2 },
        { id: 'eb1', from: 'cluster-economy', to: 'b1', label: 'topic', strength: 2 },
        { id: 'eb2', from: 'b1', to: 'b2', label: 'timeline', strength: 3 },
        { id: 'eb3', from: 'b2', to: 'b3', label: 'analysis', strength: 2 },
        { id: 'x1', from: 'a2', to: 'bridge-1', label: 'shared entity', strength: 1 },
        { id: 'x2', from: 'b2', to: 'bridge-1', label: 'shared entity', strength: 1 },
        { id: 'x3', from: 'cluster-aliyev', to: 'bridge-1', label: 'mentions', strength: 2 },
      ],
    };
  }

  return {
    nodes: [
      {
        id: 'hub',
        kind: 'entity',
        title: 'Ilham Aliyev',
        subtitle: 'Entity hub (knowledge graph)',
        meta: {
          tags: ['person', 'central'],
          entities: ['Azerbaijan', 'Baku', 'cabinet', 'delegation'],
        },
        pos: { xPct: 40, yPct: 44 },
      },
      {
        id: 'event-1',
        kind: 'event',
        title: 'Diplomatic meeting',
        subtitle: 'High-confidence event',
        meta: {
          date: '2025-12-12 14:10',
          source: 'Qafqazinfo',
          sentiment: 'positive',
          importance: 9,
          confidence: 0.86,
          tags: ['diplomacy'],
          entities: ['delegation'],
        },
        pos: { xPct: 18, yPct: 25 },
      },
      {
        id: 'event-2',
        kind: 'event',
        title: 'Economic statement',
        subtitle: 'Market-sensitive mention',
        meta: {
          date: '2025-12-10 11:00',
          source: 'Telegram',
          sentiment: 'neutral',
          importance: 8,
          confidence: 0.78,
          tags: ['energy', 'economy'],
          entities: ['gas corridor'],
        },
        pos: { xPct: 18, yPct: 62 },
      },
      {
        id: 'news-brief-1',
        kind: 'news',
        title: 'Breaking: official note',
        subtitle: 'Short post with link',
        meta: {
          date: '2025-12-12 10:24',
          source: 'Telegram',
          sentiment: 'neutral',
          importance: 6,
          confidence: 0.71,
          tags: ['statement'],
        },
        pos: { xPct: 62, yPct: 18 },
      },
      {
        id: 'news-brief-2',
        kind: 'news',
        title: 'Follow-up analysis',
        subtitle: 'Multiple entities extracted',
        meta: {
          date: '2025-12-12 19:40',
          source: 'Operativ',
          sentiment: 'neutral',
          importance: 7,
          confidence: 0.75,
          tags: ['analysis'],
          entities: ['opposition', 'experts'],
        },
        pos: { xPct: 72, yPct: 46 },
      },
      {
        id: 'entity-1',
        kind: 'entity',
        title: 'Baku',
        subtitle: 'Location entity',
        meta: {
          tags: ['location'],
          confidence: 0.83,
        },
        pos: { xPct: 70, yPct: 70 },
      },
      {
        id: 'entity-2',
        kind: 'entity',
        title: 'Delegation',
        subtitle: 'Organization/group',
        meta: {
          tags: ['org'],
          confidence: 0.8,
        },
        pos: { xPct: 58, yPct: 84 },
      },
    ],
    edges: [
      { id: 'h1', from: 'hub', to: 'event-1', label: 'participates', strength: 3 },
      { id: 'h2', from: 'hub', to: 'event-2', label: 'mentions', strength: 2 },
      { id: 'h3', from: 'hub', to: 'news-brief-1', label: 'mentioned', strength: 2 },
      { id: 'h4', from: 'hub', to: 'news-brief-2', label: 'referenced', strength: 2 },
      { id: 'h5', from: 'news-brief-2', to: 'entity-1', label: 'location', strength: 1 },
      { id: 'h6', from: 'event-1', to: 'entity-2', label: 'party', strength: 1 },
      { id: 'h7', from: 'event-1', to: 'entity-1', label: 'takes place', strength: 1 },
    ],
  };
}

function EdgeLayer({ model }: { model: GraphModel }) {
  const nodeMap = React.useMemo(() => {
    const map = new Map<string, GraphNode>();
    for (const node of model.nodes) map.set(node.id, node);
    return map;
  }, [model.nodes]);

  return (
    <svg
      className="absolute inset-0 w-full h-full"
      viewBox="0 0 1000 600"
      preserveAspectRatio="none"
    >
      <defs>
        <linearGradient id="edge" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stopColor="rgba(14,165,233,0.55)" />
          <stop offset="55%" stopColor="rgba(217,70,239,0.45)" />
          <stop offset="100%" stopColor="rgba(14,165,233,0.35)" />
        </linearGradient>
        <filter id="softGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="2.2" result="blur" />
          <feColorMatrix
            in="blur"
            type="matrix"
            values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 0.9 0"
            result="glow"
          />
          <feMerge>
            <feMergeNode in="glow" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      {model.edges.map((edge) => {
        const from = nodeMap.get(edge.from);
        const to = nodeMap.get(edge.to);
        if (!from || !to) return null;

        const x1 = (clampPct(from.pos.xPct) / 100) * 1000;
        const y1 = (clampPct(from.pos.yPct) / 100) * 600;
        const x2 = (clampPct(to.pos.xPct) / 100) * 1000;
        const y2 = (clampPct(to.pos.yPct) / 100) * 600;

        const dx = Math.abs(x2 - x1);
        const curvature = Math.min(180, 60 + dx * 0.18);
        const c1x = x1 + (x2 > x1 ? curvature : -curvature);
        const c1y = y1;
        const c2x = x2 + (x2 > x1 ? -curvature : curvature);
        const c2y = y2;
        const width = edge.strength === 3 ? 2.6 : edge.strength === 2 ? 1.9 : 1.2;
        const dash = edge.strength === 1 ? '6 6' : '0';

        return (
          <g key={edge.id} filter="url(#softGlow)">
            <path
              d={`M ${x1} ${y1} C ${c1x} ${c1y} ${c2x} ${c2y} ${x2} ${y2}`}
              stroke="url(#edge)"
              strokeWidth={width}
              strokeDasharray={dash}
              fill="none"
              opacity={0.9}
            />
          </g>
        );
      })}
    </svg>
  );
}

function NodeCard({
  node,
  selected,
  onSelect,
}: {
  node: GraphNode;
  selected: boolean;
  onSelect: (nodeId: string) => void;
}) {
  const accent = nodeAccent(node.kind);
  const sentiment = node.meta?.sentiment;

  return (
    <motion.button
      type="button"
      onClick={() => onSelect(node.id)}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={
        `absolute -translate-x-1/2 -translate-y-1/2 w-[250px] sm:w-[290px] text-left ` +
        `rounded-2xl glass-card-strong ${accent.ring} ${accent.glow} ` +
        `border border-white/30 dark:border-gray-700/40 ` +
        `hover:shadow-glow-md transition-all duration-300 ` +
        (selected ? 'ring-4 ring-primary-500/35' : '')
      }
      style={{ left: `${clampPct(node.pos.xPct)}%`, top: `${clampPct(node.pos.yPct)}%` }}
    >
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className={`px-2 py-1 rounded-lg text-[11px] font-bold ${accent.badge}`}>
                {node.kind === 'entity' ? 'ENTITY' : node.kind === 'event' ? 'EVENT' : 'NEWS'}
              </span>
              {sentiment && (
                <span
                  className={`px-2 py-1 rounded-lg text-[11px] font-bold border ${sentimentClasses(sentiment)}`}
                >
                  {sentiment.toUpperCase()}
                </span>
              )}
            </div>
            <h3 className="mt-2 font-black text-gray-900 dark:text-gray-100 leading-snug truncate">
              {node.title}
            </h3>
            {node.subtitle && (
              <p className="mt-1 text-xs font-medium text-gray-600 dark:text-gray-400 line-clamp-2">
                {node.subtitle}
              </p>
            )}
          </div>
          <div className="flex-shrink-0 w-10 h-10 rounded-2xl glass-card flex items-center justify-center">
            {node.kind === 'entity' ? (
              <Users className="w-5 h-5 text-accent-600 dark:text-accent-400" />
            ) : node.kind === 'event' ? (
              <Route className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            ) : (
              <Link2 className="w-5 h-5 text-gray-700 dark:text-gray-300" />
            )}
          </div>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {node.meta?.date && (
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-semibold glass-card">
              <Calendar className="w-3.5 h-3.5 text-gray-500" />
              <span className="text-gray-700 dark:text-gray-300">{node.meta.date}</span>
            </span>
          )}
          {node.meta?.source && (
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-semibold glass-card">
              <ExternalLink className="w-3.5 h-3.5 text-gray-500" />
              <span className="text-gray-700 dark:text-gray-300">{node.meta.source}</span>
            </span>
          )}
          {typeof node.meta?.confidence === 'number' && (
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-semibold glass-card">
              <Search className="w-3.5 h-3.5 text-gray-500" />
              <span className="text-gray-700 dark:text-gray-300">{Math.round(node.meta.confidence * 100)}%</span>
            </span>
          )}
          {typeof node.meta?.importance === 'number' && (
            <span className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-[11px] font-semibold glass-card">
              <Tag className="w-3.5 h-3.5 text-gray-500" />
              <span className="text-gray-700 dark:text-gray-300">Impact {node.meta.importance}/10</span>
            </span>
          )}
        </div>

        {node.meta?.tags?.length ? (
          <div className="mt-3 flex flex-wrap gap-2">
            {node.meta.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="px-2 py-1 rounded-lg text-[11px] font-bold bg-primary-500/10 text-primary-700 dark:text-primary-300 border border-primary-500/20"
              >
                {tag}
              </span>
            ))}
            {node.meta.tags.length > 3 && (
              <span className="px-2 py-1 rounded-lg text-[11px] font-bold glass-card text-gray-700 dark:text-gray-300">
                +{node.meta.tags.length - 3}
              </span>
            )}
          </div>
        ) : null}
      </div>
    </motion.button>
  );
}

function SidePanel({
  variant,
  model,
  selectedId,
  onChangeVariant,
}: {
  variant: GraphVariant;
  model: GraphModel;
  selectedId: string | null;
  onChangeVariant: (variant: GraphVariant) => void;
}) {
  const selected = React.useMemo(
    () => model.nodes.find((n) => n.id === selectedId) ?? null,
    [model.nodes, selectedId]
  );

  return (
    <div className="space-y-4">
      <div className="card-modern p-4">
        <div className="flex items-center justify-between gap-3">
          <div className="min-w-0">
            <h2 className="text-sm font-black text-gray-900 dark:text-gray-100">Graph View</h2>
            <p className="mt-1 text-xs font-medium text-gray-600 dark:text-gray-400">
              Mock UI for connected news & entities
            </p>
          </div>
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-primary-500 to-accent-600 shadow-lg shadow-primary-500/30 flex items-center justify-center">
            <Network className="w-5 h-5 text-white" />
          </div>
        </div>

        <div className="mt-4 grid grid-cols-3 gap-2">
          {(
            [
              { id: 'single-chain' as const, label: 'Chain' },
              { id: 'multi-chain' as const, label: 'Chains' },
              { id: 'entity-hub' as const, label: 'Hub' },
            ]
          ).map((item) => (
            <motion.button
              key={item.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => onChangeVariant(item.id)}
              className={
                'px-3 py-2 rounded-xl text-xs font-black transition-all duration-300 ' +
                (variant === item.id
                  ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-md'
                  : 'glass-card text-gray-700 dark:text-gray-300 hover:bg-white/80 dark:hover:bg-gray-700/80')
              }
            >
              {item.label}
            </motion.button>
          ))}
        </div>
      </div>

      <div className="card-modern p-4">
        <h3 className="text-sm font-black text-gray-900 dark:text-gray-100">Selected</h3>
        {!selected ? (
          <div className="mt-3 glass-card rounded-2xl p-4">
            <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              Click a node in the graph to preview extracted metadata.
            </p>
          </div>
        ) : (
          <div className="mt-3 glass-card rounded-2xl p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="text-[11px] font-black text-gray-500 dark:text-gray-400 uppercase">
                  {selected.kind}
                </p>
                <p className="mt-1 text-sm font-black text-gray-900 dark:text-gray-100 break-words">
                  {selected.title}
                </p>
                {selected.subtitle ? (
                  <p className="mt-1 text-xs font-medium text-gray-600 dark:text-gray-400">
                    {selected.subtitle}
                  </p>
                ) : null}
              </div>
              <motion.button
                type="button"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="p-2 rounded-xl glass-card"
                aria-label="Share"
              >
                <Share2 className="w-4 h-4 text-gray-700 dark:text-gray-300" />
              </motion.button>
            </div>

            <div className="mt-3 grid grid-cols-2 gap-2">
              <div className="glass-card rounded-xl p-3">
                <p className="text-[11px] font-black text-gray-500 dark:text-gray-400">Source</p>
                <p className="mt-1 text-xs font-bold text-gray-900 dark:text-gray-100">
                  {selected.meta?.source ?? '—'}
                </p>
              </div>
              <div className="glass-card rounded-xl p-3">
                <p className="text-[11px] font-black text-gray-500 dark:text-gray-400">Time</p>
                <p className="mt-1 text-xs font-bold text-gray-900 dark:text-gray-100">
                  {selected.meta?.date ?? '—'}
                </p>
              </div>
              <div className="glass-card rounded-xl p-3">
                <p className="text-[11px] font-black text-gray-500 dark:text-gray-400">Impact</p>
                <p className="mt-1 text-xs font-bold text-gray-900 dark:text-gray-100">
                  {typeof selected.meta?.importance === 'number' ? `${selected.meta.importance}/10` : '—'}
                </p>
              </div>
              <div className="glass-card rounded-xl p-3">
                <p className="text-[11px] font-black text-gray-500 dark:text-gray-400">Confidence</p>
                <p className="mt-1 text-xs font-bold text-gray-900 dark:text-gray-100">
                  {typeof selected.meta?.confidence === 'number' ? `${Math.round(selected.meta.confidence * 100)}%` : '—'}
                </p>
              </div>
            </div>

            {selected.meta?.entities?.length ? (
              <div className="mt-3">
                <p className="text-[11px] font-black text-gray-500 dark:text-gray-400 uppercase">Entities</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {selected.meta.entities.slice(0, 8).map((e) => (
                    <span
                      key={e}
                      className="px-2 py-1 rounded-lg text-[11px] font-bold bg-accent-500/10 text-accent-700 dark:text-accent-300 border border-accent-500/20"
                    >
                      {e}
                    </span>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        )}
      </div>

      <div className="card-modern p-4">
        <h3 className="text-sm font-black text-gray-900 dark:text-gray-100">Legend</h3>
        <div className="mt-3 space-y-2">
          <div className="flex items-center justify-between glass-card rounded-2xl p-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-accent-500" />
              <p className="text-xs font-bold text-gray-900 dark:text-gray-100">Entity</p>
            </div>
            <p className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">people, orgs, places</p>
          </div>
          <div className="flex items-center justify-between glass-card rounded-2xl p-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-primary-500" />
              <p className="text-xs font-bold text-gray-900 dark:text-gray-100">Event</p>
            </div>
            <p className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">detected from news</p>
          </div>
          <div className="flex items-center justify-between glass-card rounded-2xl p-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-gray-500" />
              <p className="text-xs font-bold text-gray-900 dark:text-gray-100">News</p>
            </div>
            <p className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">raw post/article</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export function PrototypeGraphsPage({ onBackToChat }: { onBackToChat: () => void }) {
  const [variant, setVariant] = React.useState<GraphVariant>('single-chain');
  const [selectedId, setSelectedId] = React.useState<string | null>(null);

  const model = React.useMemo(() => buildGraphModel(variant), [variant]);

  React.useEffect(() => {
    setSelectedId(null);
  }, [variant]);

  return (
    <div className="flex-1 flex overflow-hidden max-w-7xl w-full mx-auto min-h-0">
      <div className="flex-1 flex flex-col min-w-0 min-h-0">
        <div className="flex-shrink-0 px-3 sm:px-6 py-3 sm:py-4 glass-card border-b border-white/20 dark:border-gray-700/30">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="min-w-0">
              <h2 className="text-base sm:text-lg font-black gradient-text">Connected News Graph</h2>
              <p className="mt-1 text-xs font-medium text-gray-600 dark:text-gray-400">
                Visual prototype: link news, events, and extracted entities into a knowledge graph
              </p>
            </div>
            <div className="flex items-center gap-2">
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.98 }}
                onClick={onBackToChat}
                className="btn-secondary px-4 py-2"
              >
                Back to chat
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.98 }}
                className="btn-primary px-4 py-2"
              >
                Generate graph
                <ArrowRight className="w-4 h-4 inline-block ml-2" />
              </motion.button>
            </div>
          </div>
        </div>

        <div className="flex-1 min-h-0 p-3 sm:p-6">
          <div className="relative h-full rounded-3xl glass-card-strong border border-white/30 dark:border-gray-700/40 shadow-2xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-transparent to-accent-600/10" />

            <div className="absolute left-4 top-4 right-4 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-2 px-3 py-2 rounded-2xl glass-card">
                  <Network className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                  <span className="text-xs font-black text-gray-900 dark:text-gray-100">
                    {variant === 'single-chain'
                      ? 'Single chain'
                      : variant === 'multi-chain'
                      ? 'Multiple chains'
                      : 'Entity hub'}
                  </span>
                </span>
                <span className="hidden sm:inline-flex items-center gap-2 px-3 py-2 rounded-2xl glass-card">
                  <Link2 className="w-4 h-4 text-gray-700 dark:text-gray-300" />
                  <span className="text-xs font-bold text-gray-700 dark:text-gray-300">
                    {model.nodes.length} nodes · {model.edges.length} links
                  </span>
                </span>
              </div>

              <div className="hidden md:flex items-center gap-2">
                <span className="inline-flex items-center gap-2 px-3 py-2 rounded-2xl glass-card">
                  <Tag className="w-4 h-4 text-accent-600 dark:text-accent-400" />
                  <span className="text-xs font-bold text-gray-700 dark:text-gray-300">entity extraction</span>
                </span>
              </div>
            </div>

            <div className="absolute inset-0 pt-20 pb-4">
              <EdgeLayer model={model} />

              {model.nodes.map((node) => (
                <NodeCard
                  key={node.id}
                  node={node}
                  selected={node.id === selectedId}
                  onSelect={setSelectedId}
                />
              ))}

              <div className="absolute left-5 bottom-5">
                <div className="glass-card rounded-3xl px-4 py-3 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-primary-500 via-primary-600 to-accent-600 shadow-lg shadow-primary-500/30 flex items-center justify-center">
                    <Users className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <p className="text-xs font-black text-gray-900 dark:text-gray-100">Example entity</p>
                    <p className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">Ilham Aliyev</p>
                  </div>
                </div>
              </div>

              <div className="absolute right-5 bottom-5 hidden lg:block">
                <div className="glass-card rounded-3xl px-4 py-3 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl glass-card flex items-center justify-center">
                    <Share2 className="w-5 h-5 text-gray-700 dark:text-gray-300" />
                  </div>
                  <div>
                    <p className="text-xs font-black text-gray-900 dark:text-gray-100">Export</p>
                    <p className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">PNG · JSON · Neo4j</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <motion.aside
        initial={{ x: 60, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ delay: 0.15 }}
        className="hidden lg:block w-96 glass-card border-l border-white/20 dark:border-gray-700/30 p-6 overflow-y-auto scrollbar-custom"
      >
        <SidePanel
          variant={variant}
          model={model}
          selectedId={selectedId}
          onChangeVariant={setVariant}
        />
      </motion.aside>
    </div>
  );
}
