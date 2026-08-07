import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAccreditations } from '@/lib/hooks';
import { LoadingState, ErrorState, EmptyState, Badge, statusVariant } from '@/components/ui';
import { translateStatus, translateCategory } from '@/lib/translate';

export default function AccreditationsPage() {
  const { t } = useTranslation();
  const [keyword, setKeyword] = useState('');
  const { data, isLoading, error, refetch } = useAccreditations({ keyword: keyword || undefined, limit: 50 });

  const items = data?.data ?? [];

  return (
    <div>
      <h1 className="text-xl font-bold text-gray-900 mb-4">{t('accreditationsPage.title')}</h1>

      <form onSubmit={(e) => e.preventDefault()} className="flex gap-2 mb-6">
        <input
          type="text" value={keyword} onChange={(e) => setKeyword(e.target.value)}
          placeholder={t('accreditationsPage.filterPlaceholder')}
          className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
        />
      </form>

      {isLoading && <LoadingState />}
      {error && <ErrorState message={t('accreditationsPage.failedToLoad')} retry={refetch} />}
      {!isLoading && !error && items.length === 0 && <EmptyState message={t('accreditationsPage.empty')} />}

      {items.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left font-medium text-gray-500">{t('accreditationsPage.organization')}</th>
                <th className="px-3 py-2 text-left font-medium text-gray-500">{t('accreditationsPage.certificate')}</th>
                <th className="px-3 py-2 text-left font-medium text-gray-500">{t('accreditationsPage.category')}</th>
                <th className="px-3 py-2 text-left font-medium text-gray-500">{t('accreditationsPage.standard')}</th>
                <th className="px-3 py-2 text-left font-medium text-gray-500">{t('accreditationsPage.status')}</th>
                <th className="px-3 py-2 text-left font-medium text-gray-500 hidden md:table-cell">{t('accreditationsPage.issueDate')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {items.map((a) => (
                <tr key={a.id} className="hover:bg-gray-50">
                  <td className="px-3 py-2 font-medium">{a.organization_name}</td>
                  <td className="px-3 py-2 font-mono text-xs">{a.certificate_number}</td>
                  <td className="px-3 py-2"><Badge>{translateCategory(t, a.category)}</Badge></td>
                  <td className="px-3 py-2">{a.standard}</td>
                  <td className="px-3 py-2"><Badge variant={statusVariant(a.status)}>{translateStatus(t, a.status)}</Badge></td>
                  <td className="px-3 py-2 hidden md:table-cell">{a.issue_date ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
