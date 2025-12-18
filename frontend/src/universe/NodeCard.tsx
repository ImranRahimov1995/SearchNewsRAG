import { motion } from 'framer-motion';
import { Calendar, ExternalLink, Tag, Users, Route, Link2 } from 'lucide-react';
import { GraphNode, Sentiment, NodeKind } from './types';
import { Translations } from '../i18n/translations';

function clampPct(value: number): number {
  return Math.max(0, Math.min(100, value));
}

function sentimentClasses(sentiment: Sentiment | undefined): string {
  if (sentiment === 'positive') return 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 border-emerald-500/30';
  if (sentiment === 'negative') return 'bg-rose-500/15 text-rose-700 dark:text-rose-300 border-rose-500/30';
  return 'bg-gray-500/15 text-gray-700 dark:text-gray-300 border-gray-500/30';
}

function nodeAccent(kind: NodeKind): {
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

interface NodeCardProps {
  node: GraphNode;
  selected: boolean;
  onSelect: (nodeId: string) => void;
  t: Translations;
}

export function NodeCard({ node, selected, onSelect, t }: NodeCardProps) {
  const accent = nodeAccent(node.kind);
  const sentiment = node.meta?.sentiment;

  const getNodeTypeLabel = (kind: NodeKind): string => {
    switch (kind) {
      case 'entity': return t.universe.nodeTypes.entity;
      case 'event': return t.universe.nodeTypes.event;
      case 'news': return t.universe.nodeTypes.news;
    }
  };

  return (
    <motion.button
      type="button"
      onClick={() => onSelect(node.id)}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={
        `absolute -translate-x-1/2 -translate-y-1/2 w-[220px] sm:w-[260px] text-left ` +
        `rounded-2xl glass-card-strong ${accent.ring} ${accent.glow} ` +
        `border border-white/30 dark:border-gray-700/40 ` +
        `hover:shadow-glow-md transition-all duration-300 ` +
        (selected ? 'ring-4 ring-primary-500/35' : '')
      }
      style={{ left: `${clampPct(node.pos.xPct)}%`, top: `${clampPct(node.pos.yPct)}%` }}
    >
      <div className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className={`px-1.5 py-0.5 rounded-lg text-[10px] font-bold ${accent.badge}`}>
                {getNodeTypeLabel(node.kind)}
              </span>
              {sentiment && (
                <span
                  className={`px-1.5 py-0.5 rounded-lg text-[10px] font-bold border ${sentimentClasses(sentiment)}`}
                >
                  {t.sentiment[sentiment] || sentiment}
                </span>
              )}
            </div>
            <h3 className="mt-1.5 font-bold text-sm text-gray-900 dark:text-gray-100 leading-snug line-clamp-2">
              {node.title}
            </h3>
            {node.subtitle && (
              <p className="mt-0.5 text-[11px] font-medium text-gray-600 dark:text-gray-400 truncate">
                {node.subtitle}
              </p>
            )}
          </div>
          <div className="flex-shrink-0 w-8 h-8 rounded-xl glass-card flex items-center justify-center">
            {node.kind === 'entity' ? (
              <Users className="w-4 h-4 text-accent-600 dark:text-accent-400" />
            ) : node.kind === 'event' ? (
              <Route className="w-4 h-4 text-primary-600 dark:text-primary-400" />
            ) : (
              <Link2 className="w-4 h-4 text-gray-700 dark:text-gray-300" />
            )}
          </div>
        </div>

        <div className="mt-2 flex flex-wrap gap-1.5">
          {node.meta?.date && (
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-lg text-[10px] font-semibold glass-card">
              <Calendar className="w-3 h-3 text-gray-500" />
              <span className="text-gray-700 dark:text-gray-300">{node.meta.date}</span>
            </span>
          )}
          {node.meta?.source && (
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-lg text-[10px] font-semibold glass-card">
              <ExternalLink className="w-3 h-3 text-gray-500" />
              <span className="text-gray-700 dark:text-gray-300">{node.meta.source}</span>
            </span>
          )}
          {typeof node.meta?.importance === 'number' && (
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-lg text-[10px] font-semibold glass-card">
              <Tag className="w-3 h-3 text-gray-500" />
              <span className="text-gray-700 dark:text-gray-300">{node.meta.importance}/10</span>
            </span>
          )}
        </div>

        {node.meta?.tags?.length ? (
          <div className="mt-2 flex flex-wrap gap-1">
            {node.meta.tags.slice(0, 2).map((tag) => (
              <span
                key={tag}
                className="px-1.5 py-0.5 rounded-lg text-[10px] font-bold bg-primary-500/10 text-primary-700 dark:text-primary-300 border border-primary-500/20"
              >
                {tag}
              </span>
            ))}
          </div>
        ) : null}
      </div>
    </motion.button>
  );
}
