/**
 * @fileoverview Index synchronization status panel
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Database, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { IIndexStatus } from '@/types';
import { formatDistanceToNow } from '@/utils/dateUtils';
import { Translations } from '@/i18n/translations';

interface IndexStatusPanelProps {
  status: IIndexStatus | null;
  t: Translations;
}

interface StatusConfig {
  icon: React.ComponentType<any>;
  color: string;
  bg: string;
}

/**
 * Gets status configuration for a given status type.
 * 
 * @param status - Status type string
 * @param t - Translation object
 * @returns Status configuration with icon, colors, and text
 * @private
 */
function getStatusConfig(status: string, t: Translations): StatusConfig & { text: string } {
  const configs: Record<string, StatusConfig & { text: string }> = {
    synced: {
      icon: CheckCircle,
      color: 'text-green-600 dark:text-green-400',
      bg: 'bg-green-100 dark:bg-green-900/30',
      text: t.indexStatus.synced,
    },
    syncing: {
      icon: Loader2,
      color: 'text-blue-600 dark:text-blue-400',
      bg: 'bg-blue-100 dark:bg-blue-900/30',
      text: t.indexStatus.syncing,
    },
    error: {
      icon: AlertCircle,
      color: 'text-red-600 dark:text-red-400',
      bg: 'bg-red-100 dark:bg-red-900/30',
      text: t.indexStatus.error,
    },
  };

  return configs[status] || {
    icon: Database,
    color: 'text-gray-600 dark:text-gray-400',
    bg: 'bg-gray-100 dark:bg-gray-700/30',
    text: t.indexStatus.unknown,
  };
}

const ROTATION_ANIMATION = {
  rotate: 360,
};

const ROTATION_TRANSITION = {
  duration: 2,
  repeat: Infinity,
  ease: 'linear' as const,
};

/**
 * Panel displaying current index synchronization status.
 * Features status-specific icons, colors, and rotating animation for syncing state.
 * 
 * @param props - Component props
 * @param props.status - Current index status data, or null if unavailable
 * @returns Rendered status panel, or null if no status
 */
export const IndexStatusPanel: React.FC<IndexStatusPanelProps> = ({ status, t }) => {
  if (!status) return null;

  const config = getStatusConfig(status.status, t);
  const StatusIcon = config.icon;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card-modern p-4"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`p-2 rounded-xl ${config.bg}`}>
            <motion.div
              animate={status.status === 'syncing' ? ROTATION_ANIMATION : {}}
              transition={ROTATION_TRANSITION}
            >
              <StatusIcon className={`w-4 h-4 ${config.color}`} />
            </motion.div>
          </div>
          <span className={`text-sm font-semibold ${config.color}`}>
            {config.text}
          </span>
        </div>
      </div>
      
      <div className="space-y-2 text-xs">
        <div className="flex justify-between items-center">
          <span className="text-gray-600 dark:text-gray-400">{t.indexStatus.lastSync}</span>
          <span className="font-medium text-gray-900 dark:text-gray-100">
            {formatDistanceToNow(status.lastSync)}
          </span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-600 dark:text-gray-400">{t.indexStatus.totalNews}</span>
          <span className="font-bold text-primary-600 dark:text-primary-400">
            {status.totalNews.toLocaleString()}
          </span>
        </div>
      </div>
    </motion.div>
  );
};
