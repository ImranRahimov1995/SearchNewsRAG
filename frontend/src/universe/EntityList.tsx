import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Users, User, Building, MapPin, Tag, Search } from 'lucide-react';
import { EntityItem } from './api';
import { Translations } from '../i18n/translations';

interface EntityListProps {
  entities: EntityItem[];
  selectedEntityId: number | null;
  onSelectEntity: (entity: EntityItem | null) => void;
  t: Translations;
}

const entityTypeIcons: Record<string, React.ReactNode> = {
  PERSON: <User className="w-3.5 h-3.5" />,
  ORGANIZATION: <Building className="w-3.5 h-3.5" />,
  ORG: <Building className="w-3.5 h-3.5" />,
  LOCATION: <MapPin className="w-3.5 h-3.5" />,
  LOC: <MapPin className="w-3.5 h-3.5" />,
  GPE: <MapPin className="w-3.5 h-3.5" />,
};

export function EntityList({ entities, selectedEntityId, onSelectEntity, t }: EntityListProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredEntities = entities.filter((e) =>
    e.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full">
      <div className="relative mb-3">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder={t.universe.searchEntity}
          className="w-full pl-9 pr-3 py-2 rounded-xl text-sm bg-white/5 border border-white/10 text-gray-200 placeholder-gray-500 focus:outline-none focus:border-primary-500/50"
        />
      </div>

      <div className="flex-1 overflow-y-auto space-y-1 scrollbar-custom">
        {selectedEntityId && (
          <motion.button
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onClick={() => onSelectEntity(null)}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-xl bg-primary-500/20 border border-primary-500/30 text-primary-300 text-sm font-medium"
          >
            <Users className="w-4 h-4" />
            {t.universe.allCategories}
          </motion.button>
        )}

        {filteredEntities.map((entity) => {
          const isSelected = entity.id === selectedEntityId;
          const Icon = entityTypeIcons[entity.type?.toUpperCase() || ''] || <Tag className="w-3.5 h-3.5" />;

          return (
            <motion.button
              key={entity.id}
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              onClick={() => onSelectEntity(isSelected ? null : entity)}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-left transition-all ${
                isSelected
                  ? 'bg-accent-500/20 border border-accent-500/30'
                  : 'bg-white/5 border border-transparent hover:bg-white/10 hover:border-white/10'
              }`}
            >
              <div className={`p-1.5 rounded-lg ${isSelected ? 'bg-accent-500/30 text-accent-300' : 'bg-white/10 text-gray-400'}`}>
                {Icon}
              </div>
              <div className="flex-1 min-w-0">
                <div className={`text-sm font-medium truncate ${isSelected ? 'text-accent-200' : 'text-gray-300'}`}>
                  {entity.name}
                </div>
                <div className="text-[10px] text-gray-500">
                  {entity.type || 'Entity'} · {entity.news_count} {t.universe.nodes}
                </div>
              </div>
              <div className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                isSelected ? 'bg-accent-500/30 text-accent-300' : 'bg-white/10 text-gray-400'
              }`}>
                {entity.news_count}
              </div>
            </motion.button>
          );
        })}

        {filteredEntities.length === 0 && (
          <div className="text-center py-8 text-gray-500 text-sm">
            {t.universe.noData}
          </div>
        )}
      </div>
    </div>
  );
}
