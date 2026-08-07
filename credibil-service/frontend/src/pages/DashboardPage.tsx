import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useCompanies } from '@/lib/hooks';
import { LoadingState, ErrorState, Badge, formatDate, statusVariant } from '@/components/ui';
import { translateStatus, translateLegalForm } from '@/lib/translate';
import { appPath } from '@/lib/path';
import { slugify } from '@/lib/slugify';

export default function DashboardPage() {
  const { t } = useTranslation();
  const [page, setPage] = useState(1);
  const { data, isLoading, error, refetch } = useCompanies({ page, per_page: 10 });

  const companies = data?.data ?? [];
  const meta = data?.meta;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-gray-900">{t('dashboard.title')}</h1>
        <Link to={appPath('/search')} className="text-sm text-primary-600 hover:underline">{t('dashboard.searchCompanies')}</Link>
      </div>

      {isLoading && <LoadingState />}
      {error && <ErrorState message={t('dashboard.failedToLoad')} retry={refetch} />}
      {!isLoading && !error && companies.length === 0 && <p className="text-sm text-gray-500 py-8 text-center">{t('dashboard.empty')}</p>}

      {companies.length > 0 && (
        <>
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">{t('dashboard.name')}</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">{t('dashboard.idno')}</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">{t('dashboard.status')}</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">{t('dashboard.legalForm')}</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500 hidden md:table-cell">{t('dashboard.caem')}</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500 hidden lg:table-cell">{t('dashboard.registered')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {companies.map((c) => (
                  <tr key={c.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <Link to={appPath(`/companies/${c.id}/${slugify(c.name_ro || '')}`)} className="text-primary-600 hover:underline font-medium">{c.name_ro}</Link>
                    </td>
                    <td className="px-4 py-3 font-mono text-gray-600">{c.idno}</td>
                    <td className="px-4 py-3"><Badge variant={statusVariant(c.status)}>{translateStatus(t, c.status)}</Badge></td>
                    <td className="px-4 py-3 text-gray-600">{translateLegalForm(t, c.legal_form)}</td>
                    <td className="px-4 py-3 text-gray-600 hidden md:table-cell">{c.caem ?? '—'}</td>
                    <td className="px-4 py-3 text-gray-600 hidden lg:table-cell">{formatDate(c.registration_date)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {meta && meta.total_pages > 1 && (
            <div className="flex items-center justify-between mt-4 text-sm">
              <span className="text-gray-500">
                {t('dashboard.page', { page: meta.page, total: meta.total_pages, count: meta.total })}
              </span>
              <div className="flex gap-2">
                <button disabled={!meta.has_prev} onClick={() => setPage((p) => p - 1)}
                  className="px-3 py-1 border rounded disabled:opacity-40 hover:bg-gray-50">{t('dashboard.previous')}</button>
                <button disabled={!meta.has_next} onClick={() => setPage((p) => p + 1)}
                  className="px-3 py-1 border rounded disabled:opacity-40 hover:bg-gray-50">{t('dashboard.next')}</button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
