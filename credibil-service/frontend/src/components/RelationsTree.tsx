import { useMemo, useRef, useState, useCallback, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import type { CompanyRelationships } from '@/types';
import { translateRole } from '@/lib/translate';

// Relationship-type → colour for the edges + sidebar legend.
export const REL_COLORS: Record<string, string> = {
  founder: '#059669',
  shareholder: '#7c3aed',
  director: '#2563eb',
  administrator: '#d97706',
  owner: '#0891b2',
  beneficiary: '#db2777',
  related: '#94a3b8',
};

export function relColor(rel: string | undefined): string {
  return (rel && REL_COLORS[rel]) || REL_COLORS.related;
}

// Level band colours (Контур-style coloured frames per relation distance).
const LEVEL_COLORS = ['#2563eb', '#16a34a', '#f59e0b', '#dc2626'];

interface TNode {
  id: string;
  type: 'company' | 'person';
  label: string;
  sub?: string;
  status?: string | null;
  rel?: string;
  depth: number;
  personId?: string;
  othersCount?: number;
  companyId?: string | null;
  idno?: string;
  children: TNode[];
  x: number;
  y: number;
}

const COL = 280; // horizontal gap between levels
const ROW = 64; // vertical gap between leaves

function primaryRole(roles: string[]): string {
  return roles[0] || 'related';
}

function nodeW(n: TNode): number {
  if (n.depth === 0) return 190;
  return n.type === 'person' ? 168 : 176;
}
const NODE_H = 46;

export default function RelationsTree({
  data,
  center,
  onOpenCompany,
}: {
  data: CompanyRelationships;
  center: { idno: string; name: string; status?: string | null };
  onOpenCompany?: (idno: string, companyId: string | null, name: string) => void;
}) {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [selected, setSelected] = useState<string | null>(null);

  // ---- build a tidy horizontal tree: company → persons → their companies ----
  const { nodes, edges, bands, size } = useMemo(() => {
    const root: TNode = {
      id: `c:${center.idno}`, type: 'company', label: center.name, sub: center.idno,
      status: center.status, depth: 0, idno: center.idno, children: [], x: 0, y: 0,
    };
    data.persons.forEach((p) => {
      const rel = primaryRole(p.roles_in_current);
      const others = p.connected_companies.filter((c) => !c.is_current);
      const pn: TNode = {
        id: `p:${p.person_id}`, type: 'person', label: p.person_name,
        sub: translateRole(t, rel), rel, depth: 1, personId: p.person_id,
        othersCount: others.length, children: [], x: 0, y: 0,
      };
      root.children.push(pn);
      if (expanded.has(p.person_id)) {
        others.forEach((c) => {
          pn.children.push({
            id: `cc:${p.person_id}:${c.company_idno}`, type: 'company',
            label: c.company_name || c.company_idno, sub: c.company_idno,
            status: c.company_status, rel: primaryRole(c.roles), depth: 2,
            companyId: c.company_id, idno: c.company_idno, children: [], x: 0, y: 0,
          });
        });
      }
    });

    // post-order Y assignment (Reingold-Tilford-lite)
    let cursor = 0;
    const assignY = (n: TNode): number => {
      n.x = n.depth * COL;
      if (n.children.length === 0) {
        n.y = cursor * ROW;
        cursor += 1;
        return n.y;
      }
      const ys = n.children.map(assignY);
      n.y = (ys[0] + ys[ys.length - 1]) / 2;
      return n.y;
    };
    assignY(root);

    const nodes: TNode[] = [];
    const edges: { from: TNode; to: TNode; rel: string }[] = [];
    const walk = (n: TNode) => {
      nodes.push(n);
      n.children.forEach((c) => {
        edges.push({ from: n, to: c, rel: c.rel || 'related' });
        walk(c);
      });
    };
    walk(root);

    // per-depth bands (coloured frames + labels)
    const byDepth = new Map<number, TNode[]>();
    nodes.forEach((n) => {
      if (!byDepth.has(n.depth)) byDepth.set(n.depth, []);
      byDepth.get(n.depth)!.push(n);
    });
    const bands = Array.from(byDepth.entries())
      .filter(([d]) => d >= 1)
      .map(([d, ns]) => {
        const xs = ns.map((n) => n.x);
        const ys = ns.map((n) => n.y);
        return {
          depth: d,
          x: Math.min(...xs) - nodeW(ns[0]) / 2 - 16,
          y: Math.min(...ys) - NODE_H / 2 - 34,
          w: Math.max(...xs) - Math.min(...xs) + nodeW(ns[0]) + 32,
          h: Math.max(...ys) - Math.min(...ys) + NODE_H + 50,
        };
      });

    const maxX = Math.max(...nodes.map((n) => n.x), 0);
    const maxY = Math.max(...nodes.map((n) => n.y), 0);
    return { nodes, edges, bands, size: { w: maxX + 400, h: maxY + 200 } };
  }, [data, center, expanded, t]);

  const nodeById = useMemo(() => Object.fromEntries(nodes.map((n) => [n.id, n])), [nodes]);

  // ---- pan / zoom ----
  const stageRef = useRef<HTMLDivElement>(null);
  const [tx, setTx] = useState(40);
  const [ty, setTy] = useState(40);
  const [scale, setScale] = useState(1);
  const drag = useRef<{ x: number; y: number; tx: number; ty: number; moved: boolean } | null>(null);

  const fit = useCallback(() => {
    const el = stageRef.current;
    if (!el || nodes.length === 0) return;
    const minx = Math.min(...nodes.map((n) => n.x - nodeW(n) / 2));
    const maxx = Math.max(...nodes.map((n) => n.x + nodeW(n) / 2));
    const miny = Math.min(...nodes.map((n) => n.y)) - 50;
    const maxy = Math.max(...nodes.map((n) => n.y)) + 30;
    const pad = 40;
    const gw = maxx - minx + pad * 2;
    const gh = maxy - miny + pad * 2;
    const r = el.getBoundingClientRect();
    const s = Math.max(0.3, Math.min(1.3, Math.min(r.width / gw, r.height / gh)));
    setScale(s);
    setTx(r.width / 2 - ((minx + maxx) / 2) * s);
    setTy(r.height / 2 - ((miny + maxy) / 2) * s);
  }, [nodes]);

  useEffect(() => { fit(); }, [fit]);

  const onWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const el = stageRef.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const mx = e.clientX - r.left, my = e.clientY - r.top;
    const ns = Math.max(0.3, Math.min(2.2, scale * (1 - e.deltaY * 0.0015)));
    setTx((prev) => mx - (mx - prev) * (ns / scale));
    setTy((prev) => my - (my - prev) * (ns / scale));
    setScale(ns);
  };
  const onPointerDown = (e: React.PointerEvent) => {
    if ((e.target as HTMLElement).closest('[data-node]')) return;
    drag.current = { x: e.clientX, y: e.clientY, tx, ty, moved: false };
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  };
  const onPointerMove = (e: React.PointerEvent) => {
    if (!drag.current) return;
    const dx = e.clientX - drag.current.x, dy = e.clientY - drag.current.y;
    if (Math.abs(dx) + Math.abs(dy) > 4) drag.current.moved = true;
    setTx(drag.current.tx + dx);
    setTy(drag.current.ty + dy);
  };
  const onPointerUp = (e: React.PointerEvent) => {
    const wasDrag = drag.current?.moved;
    drag.current = null;
    if (!wasDrag && !(e.target as HTMLElement).closest('[data-node]')) setSelected(null);
  };

  const neighbors = useMemo(() => {
    if (!selected) return null;
    const set = new Set<string>([selected]);
    edges.forEach((ed) => { if (ed.from.id === selected) set.add(ed.to.id); if (ed.to.id === selected) set.add(ed.from.id); });
    return set;
  }, [selected, edges]);

  const zoomBtn = (delta: number) => {
    const el = stageRef.current; if (!el) return;
    const r = el.getBoundingClientRect();
    const ns = Math.max(0.3, Math.min(2.2, scale * delta));
    setTx((p) => r.width / 2 - (r.width / 2 - p) * (ns / scale));
    setTy((p) => r.height / 2 - (r.height / 2 - p) * (ns / scale));
    setScale(ns);
  };

  const selNode = selected ? nodeById[selected] : null;

  const statusColor = (s?: string | null) =>
    s === 'liquidated' ? '#ef4444' : s === 'active' ? '#22c55e' : s ? '#f59e0b' : null;

  return (
    <div className="relative bg-white border border-gray-200 rounded-lg overflow-hidden" style={{ height: 560 }}>
      <div
        ref={stageRef}
        className="absolute inset-0 cursor-grab active:cursor-grabbing"
        style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, #eef2f7 1px, transparent 0)', backgroundSize: '22px 22px' }}
        onWheel={onWheel}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
      >
        <div style={{ position: 'absolute', left: 0, top: 0, transformOrigin: '0 0', transform: `translate(${tx}px,${ty}px) scale(${scale})` }}>
          {/* level bands */}
          {bands.map((b) => {
            const color = LEVEL_COLORS[b.depth] || '#64748b';
            return (
              <div key={`band-${b.depth}`} style={{ position: 'absolute', left: b.x, top: b.y, width: b.w, height: b.h }}>
                <div style={{ position: 'absolute', inset: 0, border: `1.5px dashed ${color}`, borderRadius: 14, opacity: 0.5 }} />
                <div style={{ position: 'absolute', top: -10, left: 12, background: '#fff', padding: '0 8px', fontSize: 11, fontWeight: 600, color }}>
                  {t(`relations.level.${b.depth}`, { defaultValue: t('relations.levelN', { n: b.depth }) })}
                </div>
              </div>
            );
          })}

          {/* edges */}
          <svg width={size.w} height={size.h} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible', pointerEvents: 'none' }}>
            {edges.map((ed, i) => {
              const a = ed.from, b = ed.to;
              const sx = a.x + nodeW(a) / 2, sy = a.y;
              const ex = b.x - nodeW(b) / 2, ey = b.y;
              const mx = (sx + ex) / 2;
              const dim = neighbors && !(neighbors.has(a.id) && neighbors.has(b.id));
              return (
                <path
                  key={i}
                  d={`M ${sx} ${sy} C ${mx} ${sy} ${mx} ${ey} ${ex} ${ey}`}
                  fill="none"
                  stroke={relColor(ed.rel)}
                  strokeWidth={dim ? 1.5 : 3}
                  strokeOpacity={dim ? 0.12 : 0.55}
                  strokeLinecap="round"
                />
              );
            })}
          </svg>

          {/* nodes */}
          {nodes.map((n) => {
            const dim = neighbors && !neighbors.has(n.id);
            const isCenter = n.depth === 0;
            const isPerson = n.type === 'person';
            const isOpen = n.personId ? expanded.has(n.personId) : false;
            const grad = isCenter
              ? 'linear-gradient(135deg,#6d28d9,#4c1d95)'
              : isPerson
                ? 'linear-gradient(135deg,#a78bfa,#8b5cf6)'
                : 'linear-gradient(135deg,#8b5cf6,#7c3aed)';
            const sc = statusColor(n.status);
            return (
              <div
                key={n.id}
                data-node
                onClick={() => setSelected(n.id)}
                style={{ position: 'absolute', left: 0, top: 0, transform: `translate(${n.x}px,${n.y}px) translate(-50%,-50%)`, opacity: dim ? 0.3 : 1, cursor: 'pointer' }}
              >
                <div
                  style={{
                    position: 'relative', width: nodeW(n), minHeight: NODE_H, padding: '8px 12px',
                    background: grad, color: '#fff',
                    borderRadius: isPerson ? 999 : 12,
                    boxShadow: selected === n.id
                      ? '0 0 0 3px rgba(124,58,237,0.35), 0 6px 16px -6px rgba(76,29,149,0.5)'
                      : '0 4px 10px -4px rgba(76,29,149,0.45)',
                    border: isCenter ? '2px solid #c4b5fd' : '1px solid rgba(255,255,255,0.15)',
                  }}
                >
                  <div style={{ fontSize: isCenter ? 13 : 12, fontWeight: 600, lineHeight: 1.25, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={n.label}>
                    {n.label}
                  </div>
                  {n.sub && (
                    <div style={{ fontSize: 10, opacity: 0.8, marginTop: 2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontVariantNumeric: 'tabular-nums' }}>
                      {n.sub}
                    </div>
                  )}
                  {sc && (
                    <span style={{ position: 'absolute', top: 6, right: 8, width: 8, height: 8, borderRadius: 999, background: sc, boxShadow: '0 0 0 2px rgba(255,255,255,0.5)' }} title={n.status || ''} />
                  )}
                  {n.personId && (n.othersCount ?? 0) > 0 && (
                    <button
                      type="button"
                      onClick={(e) => { e.stopPropagation(); setExpanded((prev) => { const s = new Set(prev); if (s.has(n.personId!)) s.delete(n.personId!); else s.add(n.personId!); return s; }); }}
                      style={{
                        position: 'absolute', right: -10, top: '50%', transform: 'translateY(-50%)',
                        height: 22, minWidth: 22, padding: '0 6px', borderRadius: 999, fontSize: 11, fontWeight: 700,
                        background: isOpen ? '#4c1d95' : '#fff', color: isOpen ? '#fff' : '#7c3aed',
                        border: '1px solid #7c3aed', boxShadow: '0 1px 3px rgba(0,0,0,0.15)', cursor: 'pointer',
                      }}
                    >
                      {isOpen ? '–' : `+${n.othersCount}`}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* zoom controls */}
      <div className="absolute bottom-3 right-3 flex flex-col bg-white border border-gray-200 rounded-lg shadow-sm">
        <button type="button" onClick={() => zoomBtn(1.25)} className="w-8 h-8 grid place-items-center text-gray-500 hover:text-gray-900">+</button>
        <button type="button" onClick={() => zoomBtn(0.8)} className="w-8 h-8 grid place-items-center text-gray-500 hover:text-gray-900 border-t border-gray-100">−</button>
        <button type="button" onClick={fit} title={t('relations.fit')} className="w-8 h-8 grid place-items-center text-gray-500 hover:text-gray-900 border-t border-gray-100">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}><path d="M8 3H5a2 2 0 00-2 2v3m18 0V5a2 2 0 00-2-2h-3M3 16v3a2 2 0 002 2h3m13-5v3a2 2 0 01-2 2h-3" /></svg>
      </button>
      </div>

      {/* selected node info */}
      {selNode && (
        <div className="absolute top-3 right-3 w-60 bg-white border border-gray-200 rounded-lg shadow-md p-3">
          <div className="text-[10px] uppercase tracking-wide text-gray-400 mb-1">
            {selNode.type === 'person' ? t('relations.person') : t('relations.company')}
          </div>
          <div className="font-semibold text-gray-900 text-sm">{selNode.label}</div>
          {selNode.sub && <div className="text-xs text-gray-500 mt-0.5 tabular-nums">{selNode.sub}</div>}
          {selNode.type === 'company' && selNode.idno && selNode.depth !== 0 && onOpenCompany && (
            <button
              type="button"
              onClick={() => onOpenCompany(selNode.idno!, selNode.companyId ?? null, selNode.label)}
              className="mt-3 w-full text-xs font-medium text-primary-600 hover:underline text-left"
            >
              {t('relations.openCard')} →
            </button>
          )}
        </div>
      )}
    </div>
  );
}
