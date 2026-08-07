import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useMonitoredCompanies, useNotifications, useMarkAllNotificationsRead, useRemoveMonitoring } from '@/lib/hooks';
import { LoadingState, ErrorState, EmptyState, Badge, formatDate } from '@/components/ui';
import { appPath } from '@/lib/path';
import { slugify } from '@/lib/slugify';

export default function MonitoringPage() {
  const { t } = useTranslation();
  const { data: companies, isLoading: compLoading, error: compError } = useMonitoredCompanies();
  const { data: notifications, isLoading: notifLoading } = useNotifications();
  const markAll = useMarkAllNotificationsRead();
  const removeMonitoring = useRemoveMonitoring();

  const notifs = notifications?.data ?? [];
  const unread = notifs.filter((n) => !n.is_read).length;

  return (
    <div>
      <h1 className="text-xl font-semibold text-gray-900 mb-1">{t('monitoring.title')}</h1>
      <p className="text-sm text-gray-500 mb-6">{t('monitoring.subtitle')}</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monitored companies */}
        <section>
          <h2 className="text-lg font-semibold text-gray-900 mb-3">{t('monitoring.companies')}</h2>
          {compLoading && <LoadingState message={t('monitoring.loading')} />}
          {compError && <ErrorState message={t('monitoring.couldNotLoad')} />}
          {!compLoading && !compError && (
            (companies?.data && companies.data.length > 0) ? (
              <div className="bg-white border border-gray-200 rounded-lg divide-y divide-gray-100">
                {companies.data.map((c) => (
                  <div key={c.id} className="flex items-center gap-3 p-4">
                    <div className="min-w-0 flex-1">
                      <Link
                        to={appPath(`/companies/${c.company_id ?? c.idno}/${slugify(c.company_name || '')}`)}
                        className="font-medium text-gray-900 hover:text-primary-600 truncate block"
                      >
                        {c.company_name || c.idno}
                      </Link>
                      <div className="text-xs text-gray-400 tabular-nums">IDNO {c.idno}</div>
                      {c.last_change_at && (
                        <div className="text-xs text-amber-600 mt-1">
                          {t('monitoring.lastChange')}: {formatDate(c.last_change_at)}
                        </div>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => removeMonitoring.mutate(c.idno)}
                      className="text-xs text-gray-400 hover:text-red-600 shrink-0"
                    >
                      {t('monitoring.unwatch')}
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState message={t('monitoring.noCompanies')} />
            )
          )}
        </section>

        {/* Notifications */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold text-gray-900">
              {t('monitoring.notifications')}
              {unread > 0 && (
                <span className="ml-2 text-xs font-semibold text-white bg-primary-600 rounded-full px-2 py-0.5 tabular-nums">
                  {unread}
                </span>
              )}
            </h2>
            {unread > 0 && (
              <button
                type="button"
                onClick={() => markAll.mutate()}
                className="text-xs text-primary-600 hover:underline"
              >
                {t('monitoring.markAllRead')}
              </button>
            )}
          </div>
          {notifLoading && <LoadingState message={t('monitoring.loading')} />}
          {!notifLoading && (
            notifs.length > 0 ? (
              <div className="space-y-2">
                {notifs.map((n) => (
                  <div
                    key={n.id}
                    className={`border rounded-lg p-4 ${n.is_read ? 'bg-white border-gray-200' : 'bg-primary-50 border-primary-200'}`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <Link
                        to={appPath(`/companies/${n.idno}/${slugify(n.company_name || '')}`)}
                        className="font-medium text-gray-900 hover:text-primary-600 truncate"
                      >
                        {n.company_name || n.idno}
                      </Link>
                      <span className="text-xs text-gray-400 shrink-0">{formatDate(n.created_at)}</span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{n.summary}</p>
                    <div className="flex items-center gap-1.5 mt-2 flex-wrap">
                      {n.categories.map((cat) => (
                        <Badge key={cat} variant="info">{t(`monitoring.category.${cat}`, cat)}</Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState message={t('monitoring.noNotifications')} />
            )
          )}
        </section>
      </div>
    </div>
  );
}
