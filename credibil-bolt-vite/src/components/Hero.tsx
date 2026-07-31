import { useEffect, useRef, useState } from 'react';
import { Search, ArrowRight } from 'lucide-react';

interface Node {
  id: number;
  x: number;
  y: number;
  r: number;
  pulse: boolean;
  label?: string;
}

const NODES: Node[] = [
  { id: 0, x: 50, y: 30, r: 6, pulse: true, label: 'Компания' },
  { id: 1, x: 22, y: 55, r: 4, pulse: false },
  { id: 2, x: 78, y: 50, r: 5, pulse: false, label: 'Учредитель' },
  { id: 3, x: 30, y: 82, r: 3.5, pulse: false },
  { id: 4, x: 68, y: 80, r: 4.5, pulse: false, label: 'Связь' },
  { id: 5, x: 90, y: 22, r: 3, pulse: false },
  { id: 6, x: 12, y: 30, r: 3.5, pulse: false },
];

const EDGES: [number, number][] = [
  [0, 1], [0, 2], [0, 4], [1, 3], [2, 5], [4, 3], [2, 4], [1, 6],
];

const SEARCH_TERMS = [
  'MoldovaAgroindbank',
  'IDNO 1002600030037',
  'Иван Иванов',
  'Orange Moldova',
  'IDNO 1022600050042',
];

export function Hero() {
  const [searchIdx, setSearchIdx] = useState(0);
  const [typed, setTyped] = useState('');
  const [paused, setPaused] = useState(false);
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [mouseOffset, setMouseOffset] = useState({ x: 0, y: 0 });

  // Typewriter effect
  useEffect(() => {
    if (paused) return;
    const term = SEARCH_TERMS[searchIdx];
    if (typed.length < term.length) {
      const t = setTimeout(() => setTyped(term.slice(0, typed.length + 1)), 70);
      return () => clearTimeout(t);
    }
    const hold = setTimeout(() => {
      setTyped('');
      setSearchIdx((i) => (i + 1) % SEARCH_TERMS.length);
    }, 1800);
    return () => clearTimeout(hold);
  }, [typed, searchIdx, paused]);

  // Parallax on mouse
  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      setMouseOffset({
        x: (e.clientX / window.innerWidth - 0.5) * 20,
        y: (e.clientY / window.innerHeight - 0.5) * 20,
      });
    };
    window.addEventListener('mousemove', onMove, { passive: true });
    return () => window.removeEventListener('mousemove', onMove);
  }, []);

  return (
    <section id="top" className="relative min-h-screen bg-navy overflow-hidden flex items-center">
      {/* Background grid */}
      <div className="absolute inset-0 grid-bg opacity-60" aria-hidden="true" />

      {/* Radial glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        aria-hidden="true"
        style={{
          background:
            'radial-gradient(ellipse 80% 60% at 50% 40%, rgba(42, 156, 111, 0.12), transparent 70%)',
        }}
      />

      {/* Animated network SVG */}
      <svg
        ref={svgRef}
        className="absolute inset-0 w-full h-full opacity-70"
        viewBox="0 0 100 100"
        preserveAspectRatio="xMidYMid slice"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#2A9C6F" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#2A9C6F" stopOpacity="0.1" />
          </linearGradient>
        </defs>

        <g style={{ transform: `translate(${mouseOffset.x * 0.3}px, ${mouseOffset.y * 0.3}px)` }}>
          {EDGES.map(([a, b], i) => (
            <line
              key={i}
              x1={NODES[a].x}
              y1={NODES[a].y}
              x2={NODES[b].x}
              y2={NODES[b].y}
              stroke="url(#lineGrad)"
              strokeWidth="0.2"
              strokeDasharray="2 2"
            >
              <animate
                attributeName="stroke-dashoffset"
                from="4"
                to="0"
                dur="2s"
                repeatCount="indefinite"
              />
            </line>
          ))}

          {NODES.map((node) => (
            <g key={node.id}>
              {node.pulse && (
                <circle cx={node.x} cy={node.y} r={node.r}>
                  <animate attributeName="r" values={`${node.r};${node.r * 2.5};${node.r}`} dur="3s" repeatCount="indefinite" />
                  <animate attributeName="opacity" values="0.4;0;0.4" dur="3s" repeatCount="indefinite" />
                  <animate attributeName="fill" values="#2A9C6F;#2A9C6F" dur="3s" repeatCount="indefinite" />
                </circle>
              )}
              <circle
                cx={node.x}
                cy={node.y}
                r={node.r * 0.6}
                fill={node.pulse ? '#2A9C6F' : '#FFFFFF'}
                opacity={node.pulse ? 1 : 0.7}
              />
            </g>
          ))}
        </g>
      </svg>

      {/* Floating data labels */}
      <div
        className="absolute top-[28%] left-[20%] hidden lg:block pointer-events-none"
        style={{ transform: `translate(${mouseOffset.x * 0.6}px, ${mouseOffset.y * 0.6}px)` }}
        aria-hidden="true"
      >
        <div className="px-3 py-1.5 rounded-lg bg-white/5 backdrop-blur-sm border border-white/10 text-xs text-white/60 font-mono">
          IDNO 1002600030037
        </div>
      </div>
      <div
        className="absolute top-[60%] right-[18%] hidden lg:block pointer-events-none"
        style={{ transform: `translate(${mouseOffset.x * -0.4}px, ${mouseOffset.y * -0.4}px)` }}
        aria-hidden="true"
      >
        <div className="px-3 py-1.5 rounded-lg bg-green/10 backdrop-blur-sm border border-green/20 text-xs text-green font-mono">
          Статус: Активна
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 mx-auto max-w-7xl px-5 sm:px-8 w-full pt-20">
        <div className="max-w-3xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-1.5 text-xs font-medium text-white/70 mb-8">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full rounded-full bg-green opacity-75 animate-ping" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-green" />
            </span>
            Республика Молдова · B2B-сервис проверки контрагентов
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white leading-[1.05] tracking-tight text-balance">
            Превращаем разрозненные сведения в&nbsp;понятную картину для&nbsp;решения
          </h1>

          <p className="mt-6 text-lg text-white/60 leading-relaxed max-w-xl text-pretty">
            Credibil собирает и структурирует данные из государственных и официальных источников — чтобы вы видели компанию, владельцев, связи, события и риски на одном экране.
          </p>

          {/* Animated search bar */}
          <div
            className="mt-10 max-w-xl"
            onMouseEnter={() => setPaused(true)}
            onMouseLeave={() => setPaused(false)}
          >
            <div className="group relative flex items-center gap-3 rounded-2xl border border-white/15 bg-white/5 backdrop-blur-sm px-5 py-4 transition-colors duration-300 focus-within:border-green/50">
              <Search size={20} className="text-white/40 shrink-0" aria-hidden="true" />
              <div className="flex-1 min-w-0">
                <span className="text-white text-base font-medium">
                  {typed}
                  <span className="inline-block w-0.5 h-5 bg-green ml-0.5 animate-pulse" aria-hidden="true" />
                </span>
              </div>
              <a
                href="#demo"
                className="inline-flex items-center gap-2 rounded-xl bg-green px-4 py-2.5 text-sm font-semibold text-white hover:bg-green-dark transition-colors duration-200 shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green focus-visible:ring-offset-2 focus-visible:ring-offset-navy"
              >
                Найти
                <ArrowRight size={16} aria-hidden="true" />
              </a>
            </div>
            <p className="mt-3 text-xs text-white/40">
              Поиск по названию компании, IDNO или имени и фамилии
            </p>
          </div>

          {/* Chain preview */}
          <div className="mt-14 flex flex-wrap items-center gap-x-3 gap-y-2 text-sm font-medium">
            {['Компания', 'Владельцы', 'Связи', 'События', 'Риски', 'Отчёт', 'Мониторинг'].map((step, i, arr) => (
              <div key={step} className="flex items-center gap-3">
                <span className={`${i === 0 ? 'text-green' : 'text-white/50'} ${i === 0 ? 'font-semibold' : ''}`}>
                  {step}
                </span>
                {i < arr.length - 1 && (
                  <span className="text-white/20" aria-hidden="true">→</span>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 hidden sm:flex flex-col items-center gap-2 text-white/30">
        <span className="text-xs tracking-widest uppercase">Листайте</span>
        <div className="w-px h-12 bg-gradient-to-b from-white/30 to-transparent" />
      </div>
    </section>
  );
}
