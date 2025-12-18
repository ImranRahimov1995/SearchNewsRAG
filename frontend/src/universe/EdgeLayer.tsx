import React from 'react';
import { GraphData, GraphNode } from './types';

function clampPct(value: number): number {
  return Math.max(0, Math.min(100, value));
}

interface EdgeLayerProps {
  data: GraphData;
}

export function EdgeLayer({ data }: EdgeLayerProps) {
  const nodeMap = React.useMemo(() => {
    const map = new Map<string, GraphNode>();
    for (const node of data.nodes) map.set(node.id, node);
    return map;
  }, [data.nodes]);

  return (
    <svg
      className="absolute inset-0 w-full h-full pointer-events-none"
      viewBox="0 0 1000 600"
      preserveAspectRatio="none"
    >
      <defs>
        <linearGradient id="edge-gradient" x1="0" x2="1" y1="0" y2="1">
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

      {data.edges.map((edge) => {
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
              stroke="url(#edge-gradient)"
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
