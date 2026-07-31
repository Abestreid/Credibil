import { useEffect, useRef, useState } from 'react';
import { Search, Building2, User, ArrowRight, Check } from 'lucide-react';

type Result = {
  type: 'company' | 'person';
  name: string;
  subtitle: string;
  status?: string;
};

const ALL_RESULTS: Result[] = [
  { type: 'company', name: 'MoldovaAgroindbank SA', subtitle: 'IDNO 1002600030037', status: 'Активна' },
  { type: 'company', name: 'Orange Moldova SA', subtitle: 'IDNO 1022600050042', status: 'Активна' },
  { type: 'company', name: 'Moldcell SA', subtitle: 'IDNO 1004600003218', status: 'Активна' },
  { type: 'company', name: 'Zorile SA', subtitle: 'IDNO 1012600014532', status: 'Активна' },
  { type: 'person', name: 'Иван Иванов', subtitle: 'Учредитель · 3 организации' },
  { type: 'person', name: 'Анна Кишкан', subtitle: 'Администратор · 2 организации' },
  { type: 'person', name: 'Сергей Райля', subtitle: 'Учредитель · 5 организаций' },
];

const SAMPLE_QUERY = 'Mold';

export function SearchDemo() {
  const [query, setQuery] = useState('');
  const [tab, setTab] = useState<'all' | 'company' | 'person'>('all');
  const [focused, setFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const sectionRef = useRef<HTMLDivElement | null>(null);
  const [started, setStarted] = useState(false);

  // Auto-type when section enters viewport
  useEffect(() => {
    const node = sectionRef.current;
    if (!node) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !started) {
          setStarted(true);
          let i = 0;
          const interval = setInterval(() => {
            i++;
            setQuery(SAMPLE_QUERY.slice(0, i));
            if (i >= SAMPLE_QUERY.length) clearInterval(interval);
          }, 80);
          observer.disconnect();
        }
      },
      { threshold: 0.4 }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, [started]);

  const results = ALL_RESULTS.filter((r) => {
    const matchesTab = tab === 'all' || r.type === tab;
    const matchesQuery =
      query.trim() === '' ||
      r.name.toLowerCase().includes(query.toLowerCase()) ||
      r.subtitle.toLowerCase().includes(query.toLowerCase());
    return matchesTab && matchesQuery;
  });

  return (
    <section id="poisk" ref={sectionRef} className="relative bg-surface-warm py-24 sm:py-32">
      <div className="mx-auto max-w-5xl px-5 sm:px-8">
        <div className="max-w-2xl mb-12">
          <span className="text-green-dark text-sm font-semibold tracking-widest uppercase">Единый поиск</span>
          <h2 className="mt-4 text-3xl sm:text-4xl lg:text-5xl font-bold text-navy tracking-tight text-balance">
            Один запрос — компании и&nbsp;физические лица
          </h2>
          <p className="mt-5 text-text-muted text-lg leading-relaxed text-pretty">
            Введите название компании, IDNO или имя и фамилию. Результаты разделяются на компании и физических лиц, чтобы вы сразу находили нужное.
          </p>
        </div>

        {/* Search interface */}
        <div className="rounded-3xl border border-border bg-white shadow-xl shadow-navy/5 overflow-hidden">
          {/* Search bar */}
          <div className="flex items-center gap-3 border-b border-border px-5 py-4">
            <Search size={20} className="text-text-muted shrink-0" aria-hidden="true" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              placeholder="Название компании, IDNO или ФИО…"
              className="flex-1 min-w-0 text-navy placeholder:text-text-muted/60 text-base bg-transparent outline-none"
              aria-label="Поиск компаний и физических лиц"
              autoComplete="off"
            />
            {query && (
              <button
                onClick={() => setQuery('')}
                className="text-text-muted hover:text-navy text-sm shrink-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green rounded"
                aria-label="Очистить поиск"
              >
                Очистить
              </button>
            )}
          </div>

          {/* Tabs */}
          <div className="flex items-center gap-1 px-5 pt-4">
            {[
              { key: 'all', label: 'Все результаты', count: ALL_RESULTS.length },
              { key: 'company', label: 'Компании', count: ALL_RESULTS.filter((r) => r.type === 'company').length },
              { key: 'person', label: 'Физические лица', count: ALL_RESULTS.filter((r) => r.type === 'person').length },
            ].map((t) => (
              <button
                key={t.key}
                onClick={() => setTab(t.key as typeof tab)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green ${
                  tab === t.key
                    ? 'bg-navy text-white'
                    : 'text-text-muted hover:text-navy hover:bg-surface'
                }`}
              >
                {t.label} <span className="tabular-nums opacity-60">{t.count}</span>
              </button>
            ))}
          </div>

          {/* Results */}
          <div className="p-5">
            {results.length === 0 ? (
              <div className="py-12 text-center">
                <p className="text-text-muted">Ничего не найдено по запросу «{query}»</p>
                <p className="text-text-muted/60 text-sm mt-1">Попробуйте изменить запрос</p>
              </div>
            ) : (
              <ul className="space-y-2" role="list">
                {results.map((r) => (
                  <li key={r.name}>
                    <a
                      href="#kartochka"
                      className="group flex items-center gap-4 rounded-2xl border border-transparent hover:border-border hover:bg-surface transition-all duration-200 p-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-green"
                    >
                      <div
                        className={`flex items-center justify-center h-12 w-12 rounded-xl shrink-0 ${
                          r.type === 'company' ? 'bg-navy/5 text-navy' : 'bg-green/10 text-green-dark'
                        }`}
                      >
                        {r.type === 'company' ? <Building2 size={22} /> : <User size={22} />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-semibold text-navy truncate">{r.name}</span>
                          {r.status && (
                            <span className="inline-flex items-center gap-1 rounded-full bg-green/10 px-2.5 py-0.5 text-xs font-medium text-green-dark">
                              <Check size={12} aria-hidden="true" />
                              {r.status}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-text-muted mt-0.5 truncate">{r.subtitle}</p>
                      </div>
                      <ArrowRight
                        size={18}
                        className="text-text-muted/40 group-hover:text-green group-hover:translate-x-1 transition-all duration-200 shrink-0"
                        aria-hidden="true"
                      />
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <p className="mt-4 text-xs text-text-muted/60 text-center">
          Демонстрационные данные. Реальные персональные данные не используются.
        </p>
      </div>
    </section>
  );
}
