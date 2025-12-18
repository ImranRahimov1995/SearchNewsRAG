import React from 'react';
import { motion } from 'framer-motion';
import { Share2 } from 'lucide-react';
import { GraphData } from './types';
import { Translations } from '../i18n/translations';

interface SidePanelProps {
  data: GraphData;
  selectedId: string | null;
  t: Translations;
}

export function SidePanel({ data, selectedId, t }: SidePanelProps) {
  const selected = React.useMemo(
    () => data.nodes.find((n) => n.id === selectedId) ?? null,
    [data.nodes, selectedId]
  );

  return (
    <div className="space-y-4">
      <div className="card-modern p-4">
        <h3 className="text-sm font-black text-gray-900 dark:text-gray-100">
          {t.universe.selected.title}
        </h3>
        {!selected ? (
          <div className="mt-3 glass-card rounded-2xl p-4">
            <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              {t.universe.selected.hint}
            </p>
          </div>
        ) : (
          <div className="mt-3 glass-card rounded-2xl p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="text-[11px] font-black text-gray-500 dark:text-gray-400 uppercase">
                  {selected.kind === 'entity' 
                    ? t.universe.nodeTypes.entity 
                    : selected.kind === 'event' 
                    ? t.universe.nodeTypes.event 
                    : t.universe.nodeTypes.news}
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
                <p className="text-[11px] font-black text-gray-500 dark:text-gray-400">
                  {t.universe.selected.source}
                </p>
                <p className="mt-1 text-xs font-bold text-gray-900 dark:text-gray-100">
                  {selected.meta?.source ?? '—'}
                </p>
              </div>
              <div className="glass-card rounded-xl p-3">
                <p className="text-[11px] font-black text-gray-500 dark:text-gray-400">
                  {t.universe.selected.time}
                </p>
                <p className="mt-1 text-xs font-bold text-gray-900 dark:text-gray-100">
                  {selected.meta?.date ?? '—'}
                </p>
              </div>
              <div className="glass-card rounded-xl p-3 col-span-2">
                <p className="text-[11px] font-black text-gray-500 dark:text-gray-400">
                  {t.universe.selected.impact}
                </p>
                <p className="mt-1 text-xs font-bold text-gray-900 dark:text-gray-100">
                  {typeof selected.meta?.importance === 'number' ? `${selected.meta.importance}/10` : '—'}
                </p>
              </div>
            </div>

            {selected.meta?.entities?.length ? (
              <div className="mt-3">
                <p className="text-[11px] font-black text-gray-500 dark:text-gray-400 uppercase">
                  {t.universe.selected.entities}
                </p>
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
        <h3 className="text-sm font-black text-gray-900 dark:text-gray-100">
          {t.universe.legend.title}
        </h3>
        <div className="mt-3 space-y-2">
          <div className="flex items-center justify-between glass-card rounded-2xl p-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-accent-500" />
              <p className="text-xs font-bold text-gray-900 dark:text-gray-100">
                {t.universe.legend.entity}
              </p>
            </div>
            <p className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">
              {t.universe.legend.entityDesc}
            </p>
          </div>
          <div className="flex items-center justify-between glass-card rounded-2xl p-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-primary-500" />
              <p className="text-xs font-bold text-gray-900 dark:text-gray-100">
                {t.universe.legend.event}
              </p>
            </div>
            <p className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">
              {t.universe.legend.eventDesc}
            </p>
          </div>
          <div className="flex items-center justify-between glass-card rounded-2xl p-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-gray-500" />
              <p className="text-xs font-bold text-gray-900 dark:text-gray-100">
                {t.universe.legend.news}
              </p>
            </div>
            <p className="text-[11px] font-semibold text-gray-600 dark:text-gray-400">
              {t.universe.legend.newsDesc}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
