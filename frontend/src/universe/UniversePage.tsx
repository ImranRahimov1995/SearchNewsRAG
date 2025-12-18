import { useEffect, useState, useCallback, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  RefreshCw, AlertCircle, 
  PanelLeftClose, PanelLeftOpen, PanelRightClose, PanelRightOpen,
  Sparkles, Users, Zap, X, ExternalLink, Calendar, Tag, Building2,
  MapPin, User, Hash, ChevronRight, Newspaper, Search, ChevronDown,
  ThumbsUp, ThumbsDown, Minus
} from 'lucide-react';
import { GraphData, GraphNode } from './types';
import { 
  fetchCategoryTree, fetchEntities, fetchEntityGraph, fetchNewsByIds,
  CategoryNode, EntityItem 
} from './api';
import { Translations } from '../i18n/translations';

interface UniversePageProps {
  onBackToChat: () => void;
  t: Translations;
  isDark: boolean;
}

interface ExpandedNewsData {
  id: number;
  title: string;
  content?: string;
  date?: string;
  source?: string;
  importance?: number;
  sentiment?: string;
  entities: Array<{ name: string; id?: number }>;
  url?: string;
}

interface NodePosition {
  x: number;
  y: number;
}

function getEntityIcon(type: string | null) {
  switch (type?.toLowerCase()) {
    case 'person': return User;
    case 'organization': return Building2;
    case 'location': return MapPin;
    case 'event': return Zap;
    default: return Tag;
  }
}

function getEntityTypeLabel(type: string | null): string {
  switch (type?.toLowerCase()) {
    case 'person': return 'Персоны';
    case 'organization': return 'Организации';
    case 'location': return 'Локации';
    case 'event': return 'События';
    default: return 'Другое';
  }
}

export function UniversePage({ onBackToChat, t, isDark }: UniversePageProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [categories, setCategories] = useState<CategoryNode[]>([]);
  const [entities, setEntities] = useState<EntityItem[]>([]);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedEntityId, setSelectedEntityId] = useState<number | null>(null);
  const [graphTitle, setGraphTitle] = useState<string>('');
  
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(false);
  const [rightSidebarOpen, setRightSidebarOpen] = useState(false);
  
  const [expandedNews, setExpandedNews] = useState<ExpandedNewsData | null>(null);
  
  const [globalSearch, setGlobalSearch] = useState('');
  const [entitySearch, setEntitySearch] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [expandedEntityTypes, setExpandedEntityTypes] = useState<Set<string>>(new Set(['person', 'organization']));
  
  const [nodePositions, setNodePositions] = useState<Map<string, NodePosition>>(new Map());
  const [draggingNode, setDraggingNode] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  
  const [viewOffset, setViewOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  
  const [hoveredEdge, setHoveredEdge] = useState<{ label: string; x: number; y: number } | null>(null);
  
  const [sentimentFilter, setSentimentFilter] = useState<'all' | 'positive' | 'neutral' | 'negative'>('all');
  const [dateFilter, setDateFilter] = useState<'all' | 'today' | 'week' | 'month'>('all');

  const filteredGraphData = useMemo(() => {
    if (!graphData) return null;
    
    let filteredNodes = graphData.nodes;
    
    // Date filter
    if (dateFilter !== 'all') {
      const now = new Date();
      filteredNodes = filteredNodes.filter(n => {
        if (!n.meta?.date) return false;
        const nodeDate = new Date(n.meta.date);
        const diffDays = (now.getTime() - nodeDate.getTime()) / (1000 * 60 * 60 * 24);
        if (dateFilter === 'today') return diffDays <= 1;
        if (dateFilter === 'week') return diffDays <= 7;
        if (dateFilter === 'month') return diffDays <= 30;
        return true;
      });
    }
    
    // Sentiment filter
    if (sentimentFilter !== 'all') {
      filteredNodes = filteredNodes.filter(n => n.meta?.sentiment === sentimentFilter);
    }
    
    const nodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = graphData.edges.filter(e => nodeIds.has(e.from) && nodeIds.has(e.to));
    
    return { ...graphData, nodes: filteredNodes, edges: filteredEdges };
  }, [graphData, sentimentFilter, dateFilter]);

  const entityTypes = useMemo(() => {
    const types = new Map<string, EntityItem[]>();
    entities.forEach(e => {
      const type = e.type?.toLowerCase() || 'other';
      if (!types.has(type)) types.set(type, []);
      types.get(type)!.push(e);
    });
    return types;
  }, [entities]);

  const filteredEntitiesByType = useMemo(() => {
    const result = new Map<string, EntityItem[]>();
    const search = entitySearch.toLowerCase();
    entityTypes.forEach((items, type) => {
      const filtered = items.filter(e => !search || e.name.toLowerCase().includes(search));
      if (filtered.length > 0) result.set(type, filtered);
    });
    return result;
  }, [entityTypes, entitySearch]);

  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [treeData, entityData] = await Promise.all([
          fetchCategoryTree(20),
          fetchEntities(2, 200),
        ]);
        setCategories(treeData.categories);
        setEntities(entityData.entities);
      } catch (err) {
        console.error('Failed to load sidebar data:', err);
      }
    };
    loadInitialData();
  }, []);

  const calculateGroupedPositions = useCallback((data: GraphData, containerRect: DOMRect) => {
    const newPositions = new Map<string, NodePosition>();
    
    if (data.nodes.length === 0) return newPositions;
    
    // Build adjacency list from edges
    const adjacency = new Map<string, Set<string>>();
    data.nodes.forEach(n => adjacency.set(n.id, new Set()));
    data.edges.forEach(e => {
      adjacency.get(e.from)?.add(e.to);
      adjacency.get(e.to)?.add(e.from);
    });
    
    // Find connected components (groups)
    const visited = new Set<string>();
    const groups: string[][] = [];
    
    const dfs = (nodeId: string, group: string[]) => {
      if (visited.has(nodeId)) return;
      visited.add(nodeId);
      group.push(nodeId);
      adjacency.get(nodeId)?.forEach(neighbor => dfs(neighbor, group));
    };
    
    data.nodes.forEach(n => {
      if (!visited.has(n.id)) {
        const group: string[] = [];
        dfs(n.id, group);
        groups.push(group);
      }
    });
    
    // Sort each group by date (newest first)
    const nodeMap = new Map(data.nodes.map(n => [n.id, n]));
    groups.forEach(group => {
      group.sort((a, b) => {
        const nodeA = nodeMap.get(a);
        const nodeB = nodeMap.get(b);
        const dateA = nodeA?.meta?.date ? new Date(nodeA.meta.date).getTime() : 0;
        const dateB = nodeB?.meta?.date ? new Date(nodeB.meta.date).getTime() : 0;
        return dateB - dateA; // Newest first
      });
    });
    
    // Sort groups by size (largest first) then by first node date
    groups.sort((a, b) => {
      if (b.length !== a.length) return b.length - a.length;
      const dateA = nodeMap.get(a[0])?.meta?.date ? new Date(nodeMap.get(a[0])!.meta!.date!).getTime() : 0;
      const dateB = nodeMap.get(b[0])?.meta?.date ? new Date(nodeMap.get(b[0])!.meta!.date!).getTime() : 0;
      return dateB - dateA;
    });
    
    // Position groups in a grid layout
    const padding = 120;
    const cardWidth = 220;
    const cardHeight = 160;
    const groupGap = 80;
    
    let currentX = padding;
    let currentY = padding;
    let rowHeight = 0;
    
    groups.forEach(group => {
      const groupCols = Math.min(3, Math.ceil(Math.sqrt(group.length)));
      const groupWidth = groupCols * cardWidth + (groupCols - 1) * 30;
      const groupRows = Math.ceil(group.length / groupCols);
      const groupHeight = groupRows * cardHeight + (groupRows - 1) * 20;
      
      // Check if group fits in current row
      if (currentX + groupWidth > containerRect.width - padding && currentX > padding) {
        currentX = padding;
        currentY += rowHeight + groupGap;
        rowHeight = 0;
      }
      
      // Position nodes within group
      group.forEach((nodeId, idx) => {
        const col = idx % groupCols;
        const row = Math.floor(idx / groupCols);
        const x = currentX + col * (cardWidth + 30) + cardWidth / 2;
        const y = currentY + row * (cardHeight + 20) + cardHeight / 2;
        newPositions.set(nodeId, { x, y });
      });
      
      rowHeight = Math.max(rowHeight, groupHeight);
      currentX += groupWidth + groupGap;
    });
    
    return newPositions;
  }, []);

  const loadEntityGraph = useCallback(async (entityId?: number, title?: string) => {
    setLoading(true);
    setError(null);
    setExpandedNews(null);
    setNodePositions(new Map());
    setViewOffset({ x: 0, y: 0 });
    try {
      const data = await fetchEntityGraph(entityId, 50);
      setGraphData(data);
      setGraphTitle(title || t.universe.title);
      
      if (containerRef.current && data.nodes.length > 0) {
        const rect = containerRef.current.getBoundingClientRect();
        const newPositions = calculateGroupedPositions(data, rect);
        setNodePositions(newPositions);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : t.universe.error);
    } finally {
      setLoading(false);
    }
  }, [t, calculateGroupedPositions]);

  useEffect(() => {
    loadEntityGraph();
  }, [loadEntityGraph]);

  const loadNewsByIds = useCallback(async (ids: number[], title: string) => {
    setLoading(true);
    setError(null);
    setExpandedNews(null);
    setNodePositions(new Map());
    setViewOffset({ x: 0, y: 0 });
    try {
      const data = await fetchNewsByIds(ids);
      setGraphData(data);
      setGraphTitle(title);
      
      if (containerRef.current && data.nodes.length > 0) {
        const rect = containerRef.current.getBoundingClientRect();
        const newPositions = calculateGroupedPositions(data, rect);
        setNodePositions(newPositions);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load news');
    } finally {
      setLoading(false);
    }
  }, [calculateGroupedPositions]);

  const handleSelectEntity = (entity: EntityItem | null) => {
    setSelectedEntityId(entity?.id || null);
    loadEntityGraph(entity?.id, entity?.name);
    setRightSidebarOpen(false);
  };

  const handleEntityClickInModal = (entityName: string) => {
    const entity = entities.find(e => e.name === entityName);
    if (entity) {
      setExpandedNews(null);
      handleSelectEntity(entity);
    }
  };

  const handleNodeClick = (node: GraphNode) => {
    const entityList = (node.meta?.entities || []).map(name => {
      const found = entities.find(e => e.name === name);
      return { name, id: found?.id };
    });
    
    setExpandedNews({
      id: parseInt(node.id.replace('news-', '')),
      title: node.title,
      content: node.subtitle || 'Полный текст новости...',
      date: node.meta?.date,
      source: node.meta?.source,
      importance: node.meta?.importance,
      sentiment: node.meta?.sentiment,
      entities: entityList,
      url: node.meta?.url,
    });
  };

  const handleMouseDown = (e: React.MouseEvent, nodeId: string) => {
    e.preventDefault();
    e.stopPropagation();
    const pos = nodePositions.get(nodeId);
    if (pos) {
      setDraggingNode(nodeId);
      setDragOffset({ x: e.clientX - pos.x, y: e.clientY - pos.y });
    }
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (draggingNode && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const newX = e.clientX - rect.left - dragOffset.x + viewOffset.x;
      const newY = e.clientY - rect.top - dragOffset.y + viewOffset.y;
      
      setNodePositions(prev => {
        const next = new Map(prev);
        next.set(draggingNode, { x: newX, y: newY });
        return next;
      });
    } else if (isPanning) {
      const dx = e.clientX - panStart.x;
      const dy = e.clientY - panStart.y;
      setViewOffset(prev => ({ x: prev.x + dx, y: prev.y + dy }));
      setPanStart({ x: e.clientX, y: e.clientY });
    }
  }, [draggingNode, dragOffset, isPanning, panStart, viewOffset]);

  const handleMouseUp = useCallback(() => {
    setDraggingNode(null);
    setIsPanning(false);
  }, []);

  const handleContainerMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.target === e.currentTarget || (e.target as HTMLElement).tagName === 'svg') {
      setIsPanning(true);
      setPanStart({ x: e.clientX, y: e.clientY });
    }
  }, []);

  const handleTouchStart = useCallback((e: React.TouchEvent, nodeId?: string) => {
    if (nodeId) {
      e.stopPropagation();
      const touch = e.touches[0];
      const pos = nodePositions.get(nodeId);
      if (pos) {
        setDraggingNode(nodeId);
        setDragOffset({ x: touch.clientX - pos.x + viewOffset.x, y: touch.clientY - pos.y + viewOffset.y });
      }
    } else {
      const touch = e.touches[0];
      setIsPanning(true);
      setPanStart({ x: touch.clientX, y: touch.clientY });
    }
  }, [nodePositions, viewOffset]);

  const handleTouchMove = useCallback((e: TouchEvent) => {
    const touch = e.touches[0];
    if (draggingNode && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const newX = touch.clientX - rect.left - dragOffset.x + viewOffset.x;
      const newY = touch.clientY - rect.top - dragOffset.y + viewOffset.y;
      
      setNodePositions(prev => {
        const next = new Map(prev);
        next.set(draggingNode, { x: newX, y: newY });
        return next;
      });
    } else if (isPanning) {
      const dx = touch.clientX - panStart.x;
      const dy = touch.clientY - panStart.y;
      setViewOffset(prev => ({ x: prev.x + dx, y: prev.y + dy }));
      setPanStart({ x: touch.clientX, y: touch.clientY });
    }
  }, [draggingNode, dragOffset, isPanning, panStart, viewOffset]);

  const handleTouchEnd = useCallback(() => {
    setDraggingNode(null);
    setIsPanning(false);
  }, []);

  useEffect(() => {
    if (draggingNode || isPanning) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      window.addEventListener('touchmove', handleTouchMove, { passive: false });
      window.addEventListener('touchend', handleTouchEnd);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
        window.removeEventListener('touchmove', handleTouchMove);
        window.removeEventListener('touchend', handleTouchEnd);
      };
    }
  }, [draggingNode, isPanning, handleMouseMove, handleMouseUp, handleTouchMove, handleTouchEnd]);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    setViewOffset(prev => ({
      x: prev.x - e.deltaX,
      y: prev.y - e.deltaY
    }));
  }, []);

  const toggleCategory = (name: string) => {
    setExpandedCategories(prev => {
      const next = new Set(prev);
      next.has(name) ? next.delete(name) : next.add(name);
      return next;
    });
  };

  const toggleEntityType = (type: string) => {
    setExpandedEntityTypes(prev => {
      const next = new Set(prev);
      next.has(type) ? next.delete(type) : next.add(type);
      return next;
    });
  };

  const handleGlobalSearch = async () => {
    if (!globalSearch.trim()) {
      loadEntityGraph();
      setGraphTitle(t.universe.title);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await fetchEntityGraph(undefined, 100);
      const searchLower = globalSearch.toLowerCase();
      const filteredNodes = data.nodes.filter(n => 
        n.title.toLowerCase().includes(searchLower) ||
        n.subtitle?.toLowerCase().includes(searchLower) ||
        n.meta?.category?.toLowerCase().includes(searchLower) ||
        n.meta?.entities?.some(e => e.toLowerCase().includes(searchLower))
      );
      
      if (filteredNodes.length === 0) {
        setGraphData({ ...data, nodes: [], edges: [] });
        setNodePositions(new Map());
        setGraphTitle(`Поиск: "${globalSearch}" - Ничего не найдено`);
        setLoading(false);
        return;
      }
      
      const nodeIds = new Set(filteredNodes.map(n => n.id));
      const filteredEdges = data.edges.filter(e => nodeIds.has(e.from) && nodeIds.has(e.to));
      
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        const cols = Math.max(2, Math.ceil(Math.sqrt(filteredNodes.length)));
        const newPositions = new Map<string, NodePosition>();
        filteredNodes.forEach((node, i) => {
          const row = Math.floor(i / cols);
          const col = i % cols;
          const xStep = (rect.width - 300) / Math.max(1, cols - 1);
          const yStep = (rect.height - 200) / Math.max(1, Math.ceil(filteredNodes.length / cols) - 1);
          newPositions.set(node.id, {
            x: 150 + col * xStep,
            y: 100 + row * yStep,
          });
        });
        setNodePositions(newPositions);
      }
      
      setGraphData({ ...data, nodes: filteredNodes, edges: filteredEdges });
      setGraphTitle(`Поиск: "${globalSearch}" (${filteredNodes.length})`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const themeClasses = isDark 
    ? 'bg-gray-950 text-gray-100' 
    : 'bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 text-gray-900';

  const cardBg = isDark 
    ? 'bg-gray-900/90 border-gray-700/50' 
    : 'bg-white/90 border-gray-200/50';

  const sidebarBg = isDark 
    ? 'bg-gray-900/95 border-gray-700/50' 
    : 'bg-white/95 border-gray-200/50';

  return (
    <div className={`flex-1 flex flex-col overflow-hidden ${themeClasses} relative`}>
      {/* Stars background */}
      {isDark && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(30)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-white rounded-full"
              style={{ left: `${Math.random() * 100}%`, top: `${Math.random() * 100}%` }}
              animate={{ opacity: [0.2, 0.7, 0.2], scale: [1, 1.3, 1] }}
              transition={{ duration: 2 + Math.random() * 2, repeat: Infinity, delay: Math.random() * 2 }}
            />
          ))}
        </div>
      )}

      {/* Header */}
      <div className={`flex-shrink-0 px-3 sm:px-4 py-2 sm:py-3 backdrop-blur-xl ${cardBg} border-b flex items-center gap-2 sm:gap-3 z-20`}>
        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={() => setLeftSidebarOpen(!leftSidebarOpen)}
          className={`p-2 rounded-xl transition-colors ${isDark ? 'bg-gray-800/50 hover:bg-gray-700 text-gray-300' : 'bg-gray-100 hover:bg-gray-200 text-gray-600'}`}
        >
          {leftSidebarOpen ? <PanelLeftClose className="w-5 h-5" /> : <PanelLeftOpen className="w-5 h-5" />}
        </motion.button>
        
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <motion.div 
            className="hidden sm:flex p-2 rounded-xl bg-gradient-to-br from-primary-500 via-accent-500 to-primary-600 shadow-lg"
            animate={{ boxShadow: ['0 8px 12px -3px rgba(14, 165, 233, 0.3)', '0 8px 12px -3px rgba(217, 70, 239, 0.3)', '0 8px 12px -3px rgba(14, 165, 233, 0.3)'] }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
          </motion.div>
          <div className="min-w-0">
            <h2 className={`text-sm sm:text-lg font-black truncate ${isDark ? 'text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-accent-400' : 'text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-accent-600'}`}>
              {graphTitle || t.universe.title}
            </h2>
            <p className={`hidden sm:block text-xs ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{t.universe.subtitle}</p>
          </div>
        </div>

        {/* Global Search */}
        <div className="flex-1 max-w-xs sm:max-w-md">
          <div className="relative flex gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={globalSearch}
                onChange={(e) => setGlobalSearch(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleGlobalSearch()}
                placeholder="Поиск новостей..."
                className={`w-full pl-9 pr-3 py-2 rounded-xl text-sm ${
                  isDark 
                    ? 'bg-gray-800/50 border-gray-700/50 text-gray-200 placeholder-gray-500' 
                    : 'bg-gray-100 border-gray-200 text-gray-800 placeholder-gray-400'
                } border focus:outline-none focus:ring-2 focus:ring-primary-500/30`}
              />
              <Search className={`absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 ${isDark ? 'text-gray-500' : 'text-gray-400'}`} />
            </div>
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={handleGlobalSearch}
              className={`px-3 py-2 rounded-xl font-medium text-sm ${
                isDark 
                  ? 'bg-primary-500/20 hover:bg-primary-500/30 text-primary-300' 
                  : 'bg-primary-100 hover:bg-primary-200 text-primary-600'
              }`}
            >
              Найти
            </motion.button>
          </div>
        </div>

        <div className="flex items-center gap-1 sm:gap-2">
          {/* Date Filter */}
          <div className={`hidden lg:flex items-center gap-1 px-2 py-1 rounded-xl ${isDark ? 'bg-gray-800/50' : 'bg-gray-100'}`}>
            {(['all', 'today', 'week', 'month'] as const).map((filter) => (
              <motion.button
                key={filter}
                whileTap={{ scale: 0.95 }}
                onClick={() => setDateFilter(filter)}
                className={`px-2 py-1 rounded-lg text-xs font-medium ${
                  dateFilter === filter 
                    ? (isDark ? 'bg-primary-500/30 text-primary-300' : 'bg-primary-100 text-primary-600 shadow') 
                    : (isDark ? 'text-gray-400 hover:text-gray-200' : 'text-gray-500 hover:text-gray-700')
                }`}
              >
                {filter === 'all' ? 'Все' : filter === 'today' ? 'Сегодня' : filter === 'week' ? 'Неделя' : 'Месяц'}
              </motion.button>
            ))}
          </div>
          
          {/* Sentiment Filter */}
          <div className={`hidden md:flex items-center gap-1 px-2 py-1 rounded-xl ${isDark ? 'bg-gray-800/50' : 'bg-gray-100'}`}>
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => setSentimentFilter('all')}
              className={`p-1.5 rounded-lg ${sentimentFilter === 'all' ? (isDark ? 'bg-gray-700 text-white' : 'bg-white text-gray-800 shadow') : ''}`}
              title="Все"
            >
              <Hash className="w-4 h-4" />
            </motion.button>
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => setSentimentFilter('positive')}
              className={`p-1.5 rounded-lg ${sentimentFilter === 'positive' ? 'bg-emerald-500/20 text-emerald-400' : (isDark ? 'text-gray-400 hover:text-emerald-400' : 'text-gray-500 hover:text-emerald-500')}`}
              title="Позитивные"
            >
              <ThumbsUp className="w-4 h-4" />
            </motion.button>
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => setSentimentFilter('neutral')}
              className={`p-1.5 rounded-lg ${sentimentFilter === 'neutral' ? 'bg-gray-500/20 text-gray-400' : (isDark ? 'text-gray-400 hover:text-gray-300' : 'text-gray-500 hover:text-gray-600')}`}
              title="Нейтральные"
            >
              <Minus className="w-4 h-4" />
            </motion.button>
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => setSentimentFilter('negative')}
              className={`p-1.5 rounded-lg ${sentimentFilter === 'negative' ? 'bg-rose-500/20 text-rose-400' : (isDark ? 'text-gray-400 hover:text-rose-400' : 'text-gray-500 hover:text-rose-500')}`}
              title="Негативные"
            >
              <ThumbsDown className="w-4 h-4" />
            </motion.button>
          </div>
          
          {filteredGraphData && (
            <div className={`hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs ${isDark ? 'bg-gray-800/50 text-gray-300' : 'bg-gray-100/80 text-gray-600'}`}>
              <span>{filteredGraphData.nodes.length} новостей</span>
              <span className={isDark ? 'text-gray-600' : 'text-gray-300'}>•</span>
              <span>{filteredGraphData.edges.length} связей</span>
            </div>
          )}
          
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={() => loadEntityGraph(selectedEntityId || undefined)}
            disabled={loading}
            className={`p-2 rounded-xl ${isDark ? 'bg-gray-800/50 hover:bg-gray-700 text-gray-300' : 'bg-gray-100 hover:bg-gray-200 text-gray-600'}`}
            title="Обновить"
          >
            <RefreshCw className={`w-4 h-4 sm:w-5 sm:h-5 ${loading ? 'animate-spin' : ''}`} />
          </motion.button>

          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={() => setViewOffset({ x: 0, y: 0 })}
            className={`p-2 rounded-xl ${isDark ? 'bg-gray-800/50 hover:bg-gray-700 text-gray-300' : 'bg-gray-100 hover:bg-gray-200 text-gray-600'}`}
            title="Сбросить позицию"
          >
            <MapPin className="w-4 h-4 sm:w-5 sm:h-5" />
          </motion.button>

          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={onBackToChat}
            className={`hidden sm:block px-3 py-2 rounded-xl font-medium text-xs sm:text-sm ${isDark ? 'bg-gray-800 hover:bg-gray-700 text-gray-200' : 'bg-gray-100 hover:bg-gray-200 text-gray-700'}`}
          >
            {t.universe.backToChat}
          </motion.button>

          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={() => setRightSidebarOpen(!rightSidebarOpen)}
            className={`p-2 rounded-xl ${isDark ? 'bg-gray-800/50 hover:bg-gray-700 text-gray-300' : 'bg-gray-100 hover:bg-gray-200 text-gray-600'}`}
          >
            {rightSidebarOpen ? <PanelRightClose className="w-5 h-5" /> : <PanelRightOpen className="w-5 h-5" />}
          </motion.button>
        </div>
      </div>

      <div className="flex-1 flex relative">
        {/* Left Sidebar - Categories (Overlay on mobile) */}
        <AnimatePresence>
          {leftSidebarOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="md:hidden fixed inset-0 bg-black/50 z-30"
                onClick={() => setLeftSidebarOpen(false)}
              />
              <motion.aside
                initial={{ x: -300 }}
                animate={{ x: 0 }}
                exit={{ x: -300 }}
                transition={{ type: 'spring', damping: 25 }}
                className={`fixed md:relative left-0 top-0 h-full w-72 sm:w-80 backdrop-blur-xl ${sidebarBg} border-r flex flex-col z-40`}
              >
                <div className={`p-3 sm:p-4 border-b ${isDark ? 'border-gray-700/50' : 'border-gray-200/50'} flex items-center justify-between`}>
                  <div className="flex items-center gap-2">
                    <Newspaper className={`w-5 h-5 ${isDark ? 'text-primary-400' : 'text-primary-500'}`} />
                    <h2 className={`font-bold text-sm ${isDark ? 'text-gray-100' : 'text-gray-800'}`}>{t.categories.title}</h2>
                  </div>
                  <button onClick={() => setLeftSidebarOpen(false)} className="md:hidden p-1">
                    <X className="w-5 h-5" />
                  </button>
                </div>
                
                <div className="flex-1 overflow-y-auto p-2 sm:p-3 scrollbar-custom">
                  {categories.map((category) => {
                    const isExpanded = expandedCategories.has(category.name);
                    const hasSubcategories = category.subcategories && category.subcategories.length > 0;
                    
                    return (
                      <div key={category.name} className="mb-1">
                        <motion.button
                          onClick={() => toggleCategory(category.name)}
                          className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-sm ${
                            isDark ? 'hover:bg-white/5 text-gray-200' : 'hover:bg-gray-100 text-gray-700'
                          }`}
                          whileHover={{ x: 2 }}
                        >
                          <motion.div animate={{ rotate: isExpanded ? 90 : 0 }} transition={{ duration: 0.2 }}>
                            <ChevronRight className="w-4 h-4" />
                          </motion.div>
                          <span className="flex-1 text-left truncate font-medium">{category.name}</span>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${isDark ? 'bg-primary-500/20 text-primary-300' : 'bg-primary-100 text-primary-600'}`}>
                            {category.count}
                          </span>
                        </motion.button>
                        
                        <AnimatePresence>
                          {isExpanded && hasSubcategories && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              className="overflow-hidden ml-4 pl-2 border-l border-gray-700/30"
                            >
                              {category.subcategories.map((sub) => (
                                <motion.button
                                  key={`${category.name}-${sub.name}`}
                                  onClick={() => {
                                    const ids = sub.news.map(n => n.id);
                                    if (ids.length > 0) {
                                      loadNewsByIds(ids, `${category.name} › ${sub.name}`);
                                      setLeftSidebarOpen(false);
                                    }
                                  }}
                                  className={`w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs ${
                                    isDark ? 'hover:bg-white/5 text-gray-400' : 'hover:bg-gray-50 text-gray-600'
                                  }`}
                                  whileHover={{ x: 2 }}
                                >
                                  <Hash className="w-3 h-3 text-accent-400 flex-shrink-0" />
                                  <span className="flex-1 text-left truncate">{sub.name}</span>
                                  <span className={`text-[10px] ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
                                    {sub.news.length}
                                  </span>
                                </motion.button>
                              ))}
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    );
                  })}
                </div>
              </motion.aside>
            </>
          )}
        </AnimatePresence>

        {/* Main Graph Area */}
        <div 
          ref={containerRef}
          className={`flex-1 relative ${isPanning ? 'cursor-grabbing' : 'cursor-grab'}`}
          style={{ 
            touchAction: 'none',
            background: isDark 
              ? 'radial-gradient(circle at 50% 50%, rgba(30, 41, 59, 0.5) 0%, transparent 70%)' 
              : 'radial-gradient(circle at 50% 50%, rgba(219, 234, 254, 0.5) 0%, transparent 70%)'
          }}
          onMouseDown={handleContainerMouseDown}
          onWheel={handleWheel}
          onTouchStart={(e) => handleTouchStart(e)}
        >
          {/* Grid pattern background */}
          <div 
            className="absolute inset-0 pointer-events-none opacity-20"
            style={{
              backgroundImage: isDark 
                ? 'linear-gradient(rgba(148, 163, 184, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(148, 163, 184, 0.1) 1px, transparent 1px)'
                : 'linear-gradient(rgba(148, 163, 184, 0.2) 1px, transparent 1px), linear-gradient(90deg, rgba(148, 163, 184, 0.2) 1px, transparent 1px)',
              backgroundSize: '50px 50px',
              backgroundPosition: `${viewOffset.x % 50}px ${viewOffset.y % 50}px`
            }}
          />

          {loading ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className="w-12 h-12 sm:w-16 sm:h-16 rounded-full border-4 border-primary-500/20 border-t-primary-500"
              />
            </div>
          ) : error ? (
            <div className="absolute inset-0 flex items-center justify-center p-4">
              <div className="text-center">
                <AlertCircle className="w-10 h-10 text-red-500 mx-auto" />
                <p className="mt-3 text-red-400 text-sm">{error}</p>
                <motion.button
                  whileTap={{ scale: 0.95 }}
                  onClick={() => loadEntityGraph()}
                  className="mt-3 px-4 py-2 rounded-xl bg-primary-500 hover:bg-primary-600 text-white text-sm"
                >
                  {t.universe.retry}
                </motion.button>
              </div>
            </div>
          ) : !filteredGraphData || filteredGraphData.nodes.length === 0 ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <Sparkles className={`w-10 h-10 mx-auto ${isDark ? 'text-gray-600' : 'text-gray-400'}`} />
                <p className={`mt-3 text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>{t.universe.noData}</p>
              </div>
            </div>
          ) : (
            <>
              {/* SVG Lines - Curved Bezier */}
              <svg className="absolute inset-0 w-full h-full" style={{ zIndex: 1, cursor: isPanning ? 'grabbing' : 'grab' }}>
                <defs>
                  <linearGradient id="line-grad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor={isDark ? '#38bdf8' : '#0ea5e9'} stopOpacity="0.6" />
                    <stop offset="50%" stopColor={isDark ? '#a78bfa' : '#8b5cf6'} stopOpacity="0.8" />
                    <stop offset="100%" stopColor={isDark ? '#e879f9' : '#d946ef'} stopOpacity="0.6" />
                  </linearGradient>
                  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur stdDeviation="2" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>
                {filteredGraphData.edges.map((edge) => {
                  const fromPos = nodePositions.get(edge.from);
                  const toPos = nodePositions.get(edge.to);
                  if (!fromPos || !toPos) return null;

                  const fromX = fromPos.x + viewOffset.x;
                  const fromY = fromPos.y + viewOffset.y;
                  const toX = toPos.x + viewOffset.x;
                  const toY = toPos.y + viewOffset.y;

                  // Calculate control points for smooth bezier curve
                  const dx = toX - fromX;
                  const dy = toY - fromY;
                  const distance = Math.sqrt(dx * dx + dy * dy);
                  const curvature = Math.min(distance * 0.3, 80);
                  
                  // Create perpendicular offset for control point
                  const midX = (fromX + toX) / 2;
                  const midY = (fromY + toY) / 2;
                  const perpX = -dy / distance * curvature;
                  const perpY = dx / distance * curvature;
                  
                  const ctrlX = midX + perpX;
                  const ctrlY = midY + perpY;

                  return (
                    <g key={edge.id}>
                      {/* Invisible wider path for easier hover */}
                      <path
                        d={`M ${fromX} ${fromY} Q ${ctrlX} ${ctrlY} ${toX} ${toY}`}
                        stroke="transparent"
                        strokeWidth={20}
                        fill="none"
                        style={{ cursor: 'pointer' }}
                        onMouseEnter={(e) => setHoveredEdge({ label: edge.label || 'связь', x: e.clientX, y: e.clientY })}
                        onMouseMove={(e) => setHoveredEdge({ label: edge.label || 'связь', x: e.clientX, y: e.clientY })}
                        onMouseLeave={() => setHoveredEdge(null)}
                      />
                      {/* Visible path */}
                      <path
                        d={`M ${fromX} ${fromY} Q ${ctrlX} ${ctrlY} ${toX} ${toY}`}
                        stroke="url(#line-grad)"
                        strokeWidth={edge.strength === 3 ? 3 : edge.strength === 2 ? 2 : 1.5}
                        strokeLinecap="round"
                        fill="none"
                        filter="url(#glow)"
                        opacity={0.7}
                        style={{ pointerEvents: 'none' }}
                      />
                    </g>
                  );
                })}
              </svg>

              {/* Nodes */}
              {filteredGraphData.nodes.map((node) => {
                const pos = nodePositions.get(node.id);
                if (!pos) return null;

                return (
                  <motion.div
                    key={node.id}
                    className="absolute cursor-pointer select-none touch-none"
                    style={{ 
                      left: pos.x + viewOffset.x, 
                      top: pos.y + viewOffset.y,
                      transform: 'translate(-50%, -50%)',
                      zIndex: draggingNode === node.id ? 100 : 10,
                    }}
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: draggingNode === node.id ? 1.05 : 1 }}
                    onMouseDown={(e) => handleMouseDown(e, node.id)}
                    onTouchStart={(e) => handleTouchStart(e, node.id)}
                    onClick={() => !draggingNode && handleNodeClick(node)}
                  >
                    <div className={`w-40 sm:w-48 rounded-2xl backdrop-blur-xl ${cardBg} border p-2 sm:p-2.5 shadow-lg hover:shadow-xl transition-all ${
                      draggingNode === node.id ? 'ring-2 ring-primary-500 shadow-2xl' : ''
                    }`}>
                      <div className="flex items-start gap-2">
                        <div className={`flex-shrink-0 w-6 h-6 sm:w-7 sm:h-7 rounded-lg flex items-center justify-center ${
                          isDark ? 'bg-gray-700/50 text-gray-400' : 'bg-gray-100 text-gray-500'
                        }`}>
                          <Newspaper className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className={`text-xs sm:text-sm font-semibold leading-tight line-clamp-2 ${isDark ? 'text-gray-100' : 'text-gray-800'}`}>
                            {node.title}
                          </h3>
                          {node.meta?.date && (
                            <p className={`mt-1 text-[9px] sm:text-[10px] flex items-center gap-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                              <Calendar className="w-2.5 h-2.5 sm:w-3 sm:h-3" />
                              {node.meta.date}
                            </p>
                          )}
                        </div>
                      </div>
                      {node.meta?.sentiment && (
                        <div className="mt-1.5 sm:mt-2 flex items-center gap-1.5 flex-wrap">
                          <span className={`inline-block px-1.5 sm:px-2 py-0.5 rounded-full text-[9px] sm:text-[10px] font-medium ${
                            node.meta.sentiment === 'positive' ? 'bg-emerald-500/20 text-emerald-400' 
                            : node.meta.sentiment === 'negative' ? 'bg-rose-500/20 text-rose-400'
                            : isDark ? 'bg-gray-600/50 text-gray-400' : 'bg-gray-200 text-gray-600'
                          }`}>
                            {t.sentiment[node.meta.sentiment as keyof typeof t.sentiment] || node.meta.sentiment}
                          </span>
                          {node.meta?.url && (
                            <motion.a
                              href={node.meta.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              onClick={(e) => e.stopPropagation()}
                              whileHover={{ scale: 1.1 }}
                              className={`p-1 rounded-lg ${isDark ? 'bg-primary-500/20 text-primary-400 hover:bg-primary-500/30' : 'bg-primary-100 text-primary-600 hover:bg-primary-200'}`}
                              title="Открыть оригинал"
                            >
                              <ExternalLink className="w-3 h-3" />
                            </motion.a>
                          )}
                        </div>
                      )}
                      {/* Entities preview */}
                      {node.meta?.entities && node.meta.entities.length > 0 && (
                        <div className="mt-1.5 flex flex-wrap gap-1">
                          {node.meta.entities.slice(0, 3).map((entity, i) => (
                            <span 
                              key={i}
                              className={`text-[8px] sm:text-[9px] px-1.5 py-0.5 rounded-md ${
                                isDark ? 'bg-accent-500/10 text-accent-400/80' : 'bg-accent-50 text-accent-600/80'
                              }`}
                            >
                              {entity.length > 12 ? entity.slice(0, 12) + '...' : entity}
                            </span>
                          ))}
                          {node.meta.entities.length > 3 && (
                            <span className={`text-[8px] sm:text-[9px] px-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>
                              +{node.meta.entities.length - 3}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </motion.div>
                );
              })}

              {/* Edge Tooltip */}
              {hoveredEdge && (
                <div
                  className={`fixed px-3 py-2 rounded-lg shadow-lg text-xs font-medium z-50 pointer-events-none ${
                    isDark ? 'bg-gray-800 text-gray-100 border border-gray-700' : 'bg-white text-gray-800 border border-gray-200'
                  }`}
                  style={{
                    left: hoveredEdge.x + 15,
                    top: hoveredEdge.y - 10,
                    transform: 'translateY(-100%)',
                  }}
                >
                  <div className="flex items-center gap-1.5">
                    <Hash className="w-3 h-3 text-primary-500" />
                    <span>{hoveredEdge.label}</span>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Right Sidebar - Entities by Type (Overlay on mobile) */}
        <AnimatePresence>
          {rightSidebarOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="md:hidden fixed inset-0 bg-black/50 z-30"
                onClick={() => setRightSidebarOpen(false)}
              />
              <motion.aside
                initial={{ x: 300 }}
                animate={{ x: 0 }}
                exit={{ x: 300 }}
                transition={{ type: 'spring', damping: 25 }}
                className={`fixed md:relative right-0 top-0 h-full w-72 sm:w-80 backdrop-blur-xl ${sidebarBg} border-l flex flex-col z-40`}
              >
                <div className={`p-3 sm:p-4 border-b ${isDark ? 'border-gray-700/50' : 'border-gray-200/50'}`}>
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <Users className={`w-5 h-5 ${isDark ? 'text-accent-400' : 'text-accent-500'}`} />
                      <h2 className={`font-bold text-sm ${isDark ? 'text-gray-100' : 'text-gray-800'}`}>Сущности</h2>
                    </div>
                    <button onClick={() => setRightSidebarOpen(false)} className="md:hidden p-1">
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  <input
                    type="text"
                    value={entitySearch}
                    onChange={(e) => setEntitySearch(e.target.value)}
                    placeholder="Поиск сущностей..."
                    className={`w-full px-3 py-2 rounded-xl text-sm ${
                      isDark 
                        ? 'bg-gray-800/50 border-gray-700/50 text-gray-200 placeholder-gray-500' 
                        : 'bg-gray-100 border-gray-200 text-gray-800 placeholder-gray-400'
                    } border focus:outline-none focus:ring-2 focus:ring-primary-500/20`}
                  />
                </div>
                
                <div className="flex-1 overflow-y-auto scrollbar-custom">
                  {Array.from(filteredEntitiesByType.entries()).map(([type, items]) => {
                    const Icon = getEntityIcon(type);
                    const isExpanded = expandedEntityTypes.has(type);
                    const label = getEntityTypeLabel(type);
                    
                    return (
                      <div key={type} className={`border-b ${isDark ? 'border-gray-700/30' : 'border-gray-200/30'}`}>
                        <motion.button
                          onClick={() => toggleEntityType(type)}
                          className={`w-full flex items-center gap-2 px-4 py-3 ${
                            isDark ? 'hover:bg-white/5' : 'hover:bg-gray-50'
                          }`}
                        >
                          <Icon className={`w-4 h-4 ${
                            type === 'event' ? 'text-orange-400' : 
                            type === 'person' ? 'text-blue-400' :
                            type === 'organization' ? 'text-green-400' :
                            type === 'location' ? 'text-red-400' : 'text-gray-400'
                          }`} />
                          <span className={`flex-1 text-left text-sm font-medium ${isDark ? 'text-gray-200' : 'text-gray-700'}`}>
                            {label}
                          </span>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${isDark ? 'bg-gray-700/50 text-gray-400' : 'bg-gray-200 text-gray-600'}`}>
                            {items.length}
                          </span>
                          <motion.div animate={{ rotate: isExpanded ? 180 : 0 }}>
                            <ChevronDown className="w-4 h-4" />
                          </motion.div>
                        </motion.button>
                        
                        <AnimatePresence>
                          {isExpanded && (
                            <motion.div
                              initial={{ height: 0 }}
                              animate={{ height: 'auto' }}
                              exit={{ height: 0 }}
                              className="overflow-hidden"
                            >
                              <div className="px-2 pb-2 space-y-0.5">
                                {items.slice(0, 20).map((entity) => (
                                  <motion.button
                                    key={entity.id}
                                    onClick={() => handleSelectEntity(entity)}
                                    whileHover={{ x: 3 }}
                                    className={`w-full flex items-center gap-2 px-3 py-2 rounded-xl text-left text-xs sm:text-sm ${
                                      selectedEntityId === entity.id
                                        ? isDark ? 'bg-accent-500/20 text-accent-300' : 'bg-accent-100 text-accent-700'
                                        : isDark ? 'hover:bg-white/5 text-gray-400' : 'hover:bg-gray-50 text-gray-600'
                                    }`}
                                  >
                                    <span className="flex-1 truncate">{entity.name}</span>
                                    <span className={`text-[10px] ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
                                      {entity.news_count}
                                    </span>
                                  </motion.button>
                                ))}
                                {items.length > 20 && (
                                  <p className={`px-3 py-1 text-[10px] ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
                                    +{items.length - 20} ещё...
                                  </p>
                                )}
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    );
                  })}
                </div>
              </motion.aside>
            </>
          )}
        </AnimatePresence>
      </div>

      {/* Expanded News Modal */}
      <AnimatePresence>
        {expandedNews && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4"
            onClick={() => setExpandedNews(null)}
          >
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className={`relative w-full max-w-lg sm:max-w-2xl max-h-[85vh] overflow-hidden rounded-2xl sm:rounded-3xl shadow-2xl ${
                isDark ? 'bg-gray-900 border border-gray-700' : 'bg-white border border-gray-200'
              }`}
            >
              <div className={`sticky top-0 p-4 sm:p-6 border-b ${isDark ? 'border-gray-700/50 bg-gray-900' : 'border-gray-200 bg-white'}`}>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <h2 className={`text-base sm:text-xl font-bold leading-tight ${isDark ? 'text-gray-100' : 'text-gray-900'}`}>
                      {expandedNews.title}
                    </h2>
                    <div className="flex items-center gap-2 sm:gap-3 mt-2 flex-wrap">
                      {expandedNews.date && (
                        <span className={`flex items-center gap-1 text-xs sm:text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                          <Calendar className="w-3 h-3 sm:w-4 sm:h-4" />
                          {expandedNews.date}
                        </span>
                      )}
                      {expandedNews.source && (
                        <span className={`flex items-center gap-1 text-xs sm:text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                          <ExternalLink className="w-3 h-3 sm:w-4 sm:h-4" />
                          {expandedNews.source}
                        </span>
                      )}
                      {expandedNews.importance && (
                        <span className={`flex items-center gap-1 text-xs sm:text-sm ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                          <Tag className="w-3 h-3 sm:w-4 sm:h-4" />
                          {expandedNews.importance}/10
                        </span>
                      )}
                    </div>
                  </div>
                  <motion.button
                    whileTap={{ scale: 0.9 }}
                    onClick={() => setExpandedNews(null)}
                    className={`p-2 rounded-xl ${isDark ? 'hover:bg-gray-800 text-gray-400' : 'hover:bg-gray-100 text-gray-500'}`}
                  >
                    <X className="w-5 h-5" />
                  </motion.button>
                </div>
              </div>

              <div className="p-4 sm:p-6 overflow-y-auto max-h-[40vh]">
                <p className={`text-sm sm:text-base leading-relaxed ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                  {expandedNews.content}
                </p>
              </div>

              {expandedNews.entities.length > 0 && (
                <div className={`p-4 sm:p-6 border-t ${isDark ? 'border-gray-700/50' : 'border-gray-200'}`}>
                  <h3 className={`text-xs sm:text-sm font-bold mb-2 sm:mb-3 ${isDark ? 'text-gray-300' : 'text-gray-600'}`}>
                    Связанные сущности (нажмите для поиска)
                  </h3>
                  <div className="flex flex-wrap gap-1.5 sm:gap-2">
                    {expandedNews.entities.map((entity, i) => (
                      <motion.button
                        key={i}
                        onClick={() => handleEntityClickInModal(entity.name)}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className={`px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-xl text-xs sm:text-sm font-medium cursor-pointer transition-colors ${
                          isDark 
                            ? 'bg-accent-500/20 text-accent-300 border border-accent-500/30 hover:bg-accent-500/30' 
                            : 'bg-accent-50 text-accent-700 border border-accent-200 hover:bg-accent-100'
                        }`}
                      >
                        {entity.name}
                      </motion.button>
                    ))}
                  </div>
                </div>
              )}

              {/* URL Button */}
              {expandedNews.url && (
                <div className={`p-4 sm:p-6 border-t ${isDark ? 'border-gray-700/50' : 'border-gray-200'}`}>
                  <motion.a
                    href={expandedNews.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={`flex items-center justify-center gap-2 w-full px-4 py-3 rounded-xl font-medium text-sm transition-colors ${
                      isDark 
                        ? 'bg-primary-500/20 hover:bg-primary-500/30 text-primary-300 border border-primary-500/30' 
                        : 'bg-primary-50 hover:bg-primary-100 text-primary-600 border border-primary-200'
                    }`}
                  >
                    <ExternalLink className="w-4 h-4" />
                    Открыть оригинал новости
                  </motion.a>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
