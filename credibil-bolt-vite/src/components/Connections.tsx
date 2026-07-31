import { useState } from 'react';
import { Network, List, Building2, User } from 'lucide-react';
import { Reveal } from './Reveal';

type GNode = { id: string; x: number; y: number; type: 'company' | 'person'; label: string; active: boolean };
type GEdge = { from: string; to: string; share?: string };

const NODES: GNode[] = [
  { id: 'c1', x: 50, y: 50, type: 'company', label: 'MoldovaAgroindbank SA', active: true },
  { id: 'c2', x: 82, y: 28, type: 'company', label: 'MAIB Leasing SRL', active: true },
  { id: 'c3', x: 18, y: 30, type: 'company', label: 'Agroind Capital SRL', active: true },
  { id: 'c4', x: 80, y: 78, type: 'company', label: 'Moldova Finance SA', active: false },
  { id: 'p1', x: 30, y: 75, type: 'person', label: 'Иван Иванов', active: true },
  { id: 'p2', x: 72, y: 58, type: 'person', label: 'Анна Кишкан', active: true },
  { id: 'p3', x: 50, y: 88, type: 'person', label: 'Сергей Райля', active: true },
];

const EDGES: GEdge[] = [
  { from: 'p1', to: 'c1', share: '34.5%' },
  { from: 'p2', to: 'c1', share: '21.0%' },
  { from: 'c1', to: 'c2', share: '100%' },
  { from: 'c1', to: 'c3', share: '55%' },
  { from: 'p3', to: 'c1' },
  { from: 'p1', to: 'c3', share: '40%' },
  { from: 'p2', to: 'c4', share: '15%' },
];

export function Connections() {
  const [view, setView] = useState<'graph' | 'list'>('graph');
  const [hovered, setHovered] = useState<string | null>(null);

  return (
    <section id="svyazi" className="relative bg-teal-dark py-24 sm:py-32 overflow-hidden">
      <div className="absolute inset-0 grid-bg opacity-30" aria-hidden="true" />
      <div className="relative mx-auto max-w-6xl px-5 sm:px-8">
        <Reveal>
          <div className="max-w-2xl mb-12">
            <span className="text-green text-sm font-semibold tracking-widest uppercase">Корпоративные связи</span>
            <h2 className="mt-4 text-3xl sm:text-4xl lg:text-5xl font-bold text-white tracking-tight text-balance">
              Кто управляет. Кто владеет. Кем&nbsp;связаны.
            </h2>
            <p className="mt-5 text-white/50 text-lg leading-relaxed text-pretty">
              Credibil показывает роли людей в организациях, доли владения и другие компании связанных лиц. Активные и ликвидированные связи выделяются отдельно.
            </p>
          </div>
        </Reveal>

        {/* View toggle */}
        <Reveal delay={100}>
          <div className="inline-flex items-center gap-1 rounded-xl border border-white/10 bg-white/5 p-1 mb-8">
            <button
              onClick={() => setView('graph')}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green ${
                view === 'graph' ? 'bg-green text-white' : 'text-white/60 hover:text-white'
              }`}
            >
              <Network size={16} aria-hidden="true" />
              Схема
            </button>
            <button
              onClick={() => setView('list')}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green ${
                view === 'list' ? 'bg-green text-white' : 'text-white/60 hover:text-white'
              }`}
            >
              <List size={16} aria-hidden="true" />
              Список
            </button>
          </div>
        </Reveal>

        {/* Graph view */}
        {view === 'graph' && (
          <Reveal delay={150}>
            <div className="rounded-3xl border border-white/10 bg-navy/40 backdrop-blur-sm p-4 sm:p-8">
              <svg viewBox="0 0 100 100" className="w-full h-[400px] sm:h-[500px]" preserveAspectRatio="xMidYMid meet">
                <defs>
                  <linearGradient id="edgeActive" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#2A9C6F" stopOpacity="0.8" />
                    <stop offset="100%" stopColor="#2A9C6F" stopOpacity="0.3" />
                  </linearGradient>
                </defs>

                {/* Edges */}
                {EDGES.map((edge, i) => {
                  const from = NODES.find((n) => n.id === edge.from)!;
                  const to = NODES.find((n) => n.id === edge.to)!;
                  const isActive = from.active && to.active;
                  const isHovered = hovered === from.id || hovered === to.id;
                  const midX = (from.x + to.x) / 2;
                  const midY = (from.y + to.y) / 2;
                  return (
                    <g key={i}>
                      <line
                        x1={from.x}
                        y1={from.y}
                        x2={to.x}
                        y2={to.y}
                        stroke={isActive ? 'url(#edgeActive)' : '#5A7275'}
                        strokeWidth={isHovered ? '0.6' : '0.3'}
                        strokeDasharray={isActive ? '' : '1 1'}
                        opacity={isActive ? (isHovered ? 1 : 0.7) : 0.3}
                      >
                        {isActive && (
                          <animate attributeName="opacity" values="0.5;0.9;0.5" dur="3s" begin={`${i * 0.3}s`} repeatCount="indefinite" />
                        )}
                      </line>
                      {edge.share && (
                        <text
                          x={midX}
                          y={midY - 1}
                          textAnchor="middle"
                          className="fill-white/60"
                          style={{ fontSize: '2.5px', fontFamily: 'monospace' }}
                        >
                          {edge.share}
                        </text>
                      )}
                    </g>
                  );
                })}

                {/* Nodes */}
                {NODES.map((node) => (
                  <g
                    key={node.id}
                    onMouseEnter={() => setHovered(node.id)}
                    onMouseLeave={() => setHovered(null)}
                    className="cursor-pointer"
                  >
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={node.type === 'company' ? '4' : '3'}
                      fill={node.active ? (node.type === 'company' ? '#2A9C6F' : '#FFFFFF') : '#5A7275'}
                      opacity={hovered === null || hovered === node.id ? 1 : 0.4}
                    />
                    {hovered === node.id && (
                      <circle cx={node.x} cy={node.y} r={node.type === 'company' ? '6' : '5'} fill="none" stroke="#2A9C6F" strokeWidth="0.4">
                        <animate attributeName="r" values={`${node.type === 'company' ? '4' : '3'};${node.type === 'company' ? '8' : '7'}`} dur="1s" repeatCount="indefinite" />
                        <animate attributeName="opacity" values="0.8;0" dur="1s" repeatCount="indefinite" />
                      </circle>
                    )}
                    <text
                      x={node.x}
                      y={node.y + (node.type === 'company' ? 8 : 7)}
                      textAnchor="middle"
                      className={node.active ? 'fill-white/80' : 'fill-white/30'}
                      style={{ fontSize: '2.8px', fontWeight: 600 }}
                    >
                      {node.label}
                    </text>
                  </g>
                ))}
              </svg>

              {/* Legend */}
              <div className="flex flex-wrap items-center gap-x-6 gap-y-2 mt-4 text-xs text-white/50">
                <span className="inline-flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full bg-green" /> Активная компания
                </span>
                <span className="inline-flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full bg-white" /> Физическое лицо
                </span>
                <span className="inline-flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full bg-text-muted" /> Ликвидирована
                </span>
              </div>
            </div>
          </Reveal>
        )}

        {/* List view */}
        {view === 'list' && (
          <Reveal delay={150}>
            <div className="rounded-3xl border border-white/10 bg-navy/40 backdrop-blur-sm overflow-hidden">
              <ul className="divide-y divide-white/10" role="list">
                {EDGES.map((edge, i) => {
                  const from = NODES.find((n) => n.id === edge.from)!;
                  const to = NODES.find((n) => n.id === edge.to)!;
                  const FromIcon = from.type === 'company' ? Building2 : User;
                  const ToIcon = to.type === 'company' ? Building2 : User;
                  return (
                    <li key={i} className="flex items-center gap-4 px-6 py-4 hover:bg-white/5 transition-colors">
                      <div className="flex items-center gap-3 min-w-0 flex-1">
                        <span className="flex items-center justify-center h-10 w-10 rounded-lg bg-white/5 shrink-0">
                          <FromIcon size={20} className={from.active ? 'text-green' : 'text-white/30'} aria-hidden="true" />
                        </span>
                        <div className="min-w-0">
                          <p className="text-white text-sm font-medium truncate">{from.label}</p>
                          <p className="text-xs text-white/40">{from.type === 'company' ? 'Компания' : 'Физическое лицо'}</p>
                        </div>
                      </div>
                      <div className="text-center px-2 shrink-0">
                        {edge.share && <span className="text-green text-sm font-semibold tabular-nums">{edge.share}</span>}
                        <p className="text-xs text-white/30">доля</p>
                      </div>
                      <div className="flex items-center gap-3 min-w-0 flex-1 justify-end text-right">
                        <div className="min-w-0">
                          <p className="text-white text-sm font-medium truncate">{to.label}</p>
                          <p className="text-xs text-white/40">{to.type === 'company' ? 'Компания' : 'Физическое лицо'}</p>
                        </div>
                        <span className="flex items-center justify-center h-10 w-10 rounded-lg bg-white/5 shrink-0">
                          <ToIcon size={20} className={to.active ? 'text-green' : 'text-white/30'} aria-hidden="true" />
                        </span>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>
          </Reveal>
        )}

        <p className="mt-4 text-xs text-white/30 text-center">
          Демонстрационная схема. Реальные персональные данные не используются.
        </p>
      </div>
    </section>
  );
}
