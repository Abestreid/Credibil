import { useCallback, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  useSearchParamsState,
  useCrossSearch,
  useAutocomplete,
  useDebouncedValue,
} from '@/lib/hooks';
import { LoadingState, ErrorState, EmptyState, Badge, statusVariant } from '@/components/ui';
import { translateStatus, translateLegalForm } from '@/lib/translate';
import { appPath } from '@/lib/path';
import type { SearchHit, AutocompleteSuggestion } from '@/types';

const MATCH_COLORS: Record<string, string> = {
  exact_idno: 'bg-green-100 text-green-800',
  exact_name: 'bg-blue-100 text-blue-800',
  normalized_name: 'bg-blue-50 text-blue-700',
  prefix: 'bg-yellow-50 text-yellow-700',
  transliteration: 'bg-purple-50 text-purple-700',
  fuzzy: 'bg-gray-100 text-gray-600',
  person_exact: 'bg-green-100 text-green-800',
  person_prefix: 'bg-yellow-50 text-yellow-700',
  person_related: 'bg-orange-50 text-orange-700',
};

const ENTITY_ICONS: Record<string, string> = {
  company: '🏢',
  person: '👤',
};

const ENTITY_ROUTES: Record<string, (hit: SearchHit) => string> = {
  company: (hit) => `/companies/${hit.id}`,
  person: (hit) => `/persons/${hit.id}`,
};

export default function SearchPage() {
  const { t } = useTranslation();
  const [params, setParams] = useSearchParamsState({
    q: '',
    page: '1',
  });

  const [inputValue, setInputValue] = useState(params.q);
  const debouncedInput = useDebouncedValue(inputValue, 300);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const query = params.q;
  const page = parseInt(params.page, 10) || 1;
  const pageSize = 20;

  const hasQuery = query.length > 0;
  const { data, isLoading, error } = useCrossSearch(query, page, pageSize, hasQuery);
  const { data: autocompleteData } = useAutocomplete(debouncedInput, debouncedInput.length >= 2);

  const suggestions = useMemo(
    () => autocompleteData?.suggestions ?? [],
    [autocompleteData]
  );

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const trimmed = inputValue.trim();
      if (trimmed) {
        setParams({ q: trimmed, page: '1' });
      }
    },
    [inputValue, setParams]
  );

  const handleSuggestionClick = useCallback(
    (suggestion: AutocompleteSuggestion) => {
      const name = (suggestion.data.name_ro as string) || (suggestion.data.full_name as string) || '';
      setInputValue(name);
      setShowDropdown(false);
      setParams({ q: name, page: '1' });
    },
    [setParams]
  );

  const handlePageChange = useCallback(
    (newPage: number) => {
      setParams({ page: String(newPage) });
    },
    [setParams]
  );

  const totalPages = data?.meta.total_pages ?? 1;
  const totalHits = data?.meta.total_hits ?? 0;

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-xl font-bold text-gray-900 mb-4">{t('search.title')}</h1>

      <form onSubmit={handleSubmit} className="relative mb-6">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => {
                setInputValue(e.target.value);
                setShowDropdown(true);
              }}
              onFocus={() => setShowDropdown(true)}
              onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
              placeholder={t('search.placeholder')}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
              aria-label={t('search.ariaLabel')}
              aria-autocomplete="list"
              aria-expanded={showDropdown && suggestions.length > 0}
            />
            {showDropdown && suggestions.length > 0 && (
              <div
                ref={dropdownRef}
                className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg max-h-80 overflow-y-auto"
                role="listbox"
              >
                {suggestions.map((s) => (
                  <button
                    key={`${s.entity_type}-${s.id}`}
                    type="button"
                    className="w-full px-3 py-2 text-left hover:bg-gray-50 flex items-center gap-3 text-sm"
                    onMouseDown={() => handleSuggestionClick(s)}
                    role="option"
                  >
                    <span className="text-lg">{ENTITY_ICONS[s.entity_type] ?? '📄'}</span>
                    <div className="min-w-0">
                      <span className="font-medium text-gray-900 truncate block">
                        {(s.data.name_ro as string) || (s.data.full_name as string) || s.id}
                      </span>
                      {s.entity_type === 'company' && Boolean(s.data.idno) && (
                        <span className="text-xs text-gray-500 font-mono">{t('search.idno')}: {String(s.data.idno)}</span>
                      )}
                      {s.entity_type === 'person' && Boolean(s.data.idnp) && (
                        <span className="text-xs text-gray-500 font-mono">{t('search.idnp')}: {String(s.data.idnp)}</span>
                      )}
                    </div>
                    {s.match_reason && (
                      <span className="text-xs text-gray-400 ml-auto shrink-0">{s.match_reason}</span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-md hover:bg-primary-700"
          >
            {t('search.find')}
          </button>
        </div>
      </form>

      {isLoading && <LoadingState message={t('search.searching')} />}
      {error && <ErrorState message={t('search.searchError')} />}

      {data && data.hits.length === 0 && (
        <EmptyState message={t('search.noResults', { query: data.query })} />
      )}

      {data && data.hits.length > 0 && (
        <div>
          <p className="text-sm text-gray-500 mb-3">
            {t('search.resultsCount', { count: totalHits, time: data.processing_time_ms })}
          </p>
          <div className="space-y-3">
            {data.hits.map((hit) => (
              <HitCard key={`${hit.entity_type}-${hit.id}`} hit={hit} />
            ))}
          </div>

          {totalPages > 1 && (
            <Pagination
              page={page}
              totalPages={totalPages}
              onPageChange={handlePageChange}
            />
          )}
        </div>
      )}
    </div>
  );
}

function HitCard({ hit }: { hit: SearchHit }) {
  const { t } = useTranslation();
  const d = hit.data;
  const entityType = hit.entity_type as string;
  const isCompany = entityType === 'company';
  const icon = ENTITY_ICONS[entityType] ?? '📄';

  const name = isCompany
    ? ((d.name_ro as string) || (d.name_ru as string) || t('search.noName'))
    : ((d.full_name as string) || t('search.noNamePerson'));

  const route = ENTITY_ROUTES[entityType]?.(hit);

  const matchColor = hit.match_type ? MATCH_COLORS[hit.match_type] : null;
  const matchLabel = hit.match_type ? t(`search.matchLabels.${hit.match_type}`) : null;
  const isExact = hit.match_type === 'exact_idno' || hit.match_type === 'exact_name' || hit.match_type === 'person_exact';

  const id = isCompany ? (d.idno as string) : (d.idnp as string);

  return (
    <div
      className={`bg-white border rounded-lg p-4 transition-colors ${
        isExact ? 'border-green-300 ring-1 ring-green-100' : 'border-gray-200 hover:border-gray-300'
      }`}
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl mt-0.5">{icon}</span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            {route ? (
              <Link to={appPath(route)} className="font-medium text-primary-600 hover:underline truncate">
                {name}
              </Link>
            ) : (
              <span className="font-medium text-gray-900 truncate">{name}</span>
            )}
            {isCompany && Boolean(d.status) && (
              <Badge variant={statusVariant(String(d.status))}>{translateStatus(t, String(d.status))}</Badge>
            )}
            {isCompany && Boolean(d.legal_form) && (
              <span className="text-xs text-gray-500">{translateLegalForm(t, String(d.legal_form))}</span>
            )}
            {matchLabel && matchColor && (
              <span className={`text-xs px-1.5 py-0.5 rounded ${matchColor}`}>
                {matchLabel}
              </span>
            )}
          </div>

          {id && (
            <p className="text-xs font-mono text-gray-500">
              {isCompany ? t('search.idno') : t('search.idnp')}: {id}
            </p>
          )}

          <div className="flex gap-4 mt-1 text-xs text-gray-500 flex-wrap">
            {isCompany && Boolean(d.caem) && <span>{t('search.caemLabel')} {String(d.caem)}</span>}
            {isCompany && Boolean(d.legal_address) && (
              <span className="truncate max-w-[200px]">{String(d.legal_address)}</span>
            )}
            {isCompany && Boolean(d.registration_date) && (
              <span>{t('search.founded')} {new Date(String(d.registration_date)).getFullYear()}</span>
            )}
            {!isCompany && Boolean(d.nationality) && <span>{t('search.nationality')} {String(d.nationality)}</span>}
            {!isCompany && Array.isArray(d.company_names) && d.company_names.length > 0 && (
              <span>{t('search.companies')} {(d.company_names as string[]).slice(0, 3).join(', ')}</span>
            )}
          </div>

          {hit.match_reason && (
            <p className="text-xs text-gray-400 mt-1">{hit.match_reason}</p>
          )}
        </div>
      </div>
    </div>
  );
}

function Pagination({
  page,
  totalPages,
  onPageChange,
}: {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}) {
  const { t } = useTranslation();
  const pages = useMemo(() => {
    const result: (number | '...')[] = [];
    const maxVisible = 7;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) result.push(i);
      return result;
    }

    result.push(1);

    let start = Math.max(2, page - 1);
    let end = Math.min(totalPages - 1, page + 1);

    if (page <= 3) {
      end = Math.min(totalPages - 1, 5);
    }
    if (page >= totalPages - 2) {
      start = Math.max(2, totalPages - 4);
    }

    if (start > 2) result.push('...');
    for (let i = start; i <= end; i++) result.push(i);
    if (end < totalPages - 1) result.push('...');

    result.push(totalPages);
    return result;
  }, [page, totalPages]);

  return (
    <div className="flex items-center justify-center gap-1 mt-6">
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        className="px-3 py-1.5 text-sm border rounded disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50"
      >
        {t('search.previous')}
      </button>
      {pages.map((p, i) =>
        p === '...' ? (
          <span key={`dots-${i}`} className="px-2 py-1.5 text-sm text-gray-400">
            ...
          </span>
        ) : (
          <button
            key={p}
            onClick={() => onPageChange(p)}
            className={`px-3 py-1.5 text-sm border rounded ${
              p === page ? 'bg-primary-600 text-white border-primary-600' : 'hover:bg-gray-50'
            }`}
          >
            {p}
          </button>
        )
      )}
      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        className="px-3 py-1.5 text-sm border rounded disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50"
      >
        {t('search.next')}
      </button>
    </div>
  );
}
