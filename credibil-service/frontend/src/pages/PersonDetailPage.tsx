import { useParams, Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { usePersonDetail } from '@/lib/hooks';
import { LoadingState, ErrorState, Badge, EmptyState, statusVariant } from '@/components/ui';
import { translateStatus, translateRole, translatePersonType } from '@/lib/translate';
import ExportButtons from '@/components/ExportButtons';
import { appPath } from '@/lib/path';

export default function PersonDetailPage() {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const { data: resp, isLoading, error } = usePersonDetail(id);

  const data = resp?.data;

  if (isLoading) return <LoadingState message={t('person.loading')} />;
  if (error || !data) {
    return (
      <div>
        <Link to={appPath('/dashboard')} className="text-sm text-primary-600 hover:underline mb-4 inline-block">{t('common.backToList')}</Link>
        <ErrorState message={t('person.notFound')} />
      </div>
    );
  }

  const { person, connected_companies, total_companies, active_companies, liquidated_companies } = data;
  const roles = [...new Set(connected_companies.flatMap((c) => c.roles))].sort();

  return (
    <div>
      <Link to={appPath('/dashboard')} className="text-sm text-primary-600 hover:underline mb-4 inline-block">{t('common.backToList')}</Link>

      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{person.full_name}</h2>
            {person.idnp && <p className="text-sm text-gray-500 mt-1">IDNP: {person.idnp}</p>}
          </div>
          <ExportButtons entityType="person" entityId={person.id} />
        </div>
        <dl className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <Field label={t('person.type')} value={translatePersonType(t, person.person_type)} />
          {person.nationality && <Field label={t('person.nationality')} value={person.nationality} />}
          <Field label={t('person.roles')} value={roles.map((r) => translateRole(t, r)).join(', ')} className="col-span-2" />
          <Field label={t('person.connectedCompanies')} value={total_companies.toString()} />
          <Field label={t('person.active')} value={active_companies.toString()} />
          <Field label={t('person.liquidated')} value={liquidated_companies.toString()} />
        </dl>
      </div>

      <h2 className="text-lg font-semibold text-gray-900 mb-3">{t('person.connectedCompaniesCount', { count: total_companies })}</h2>
      {connected_companies.length === 0 ? (
        <EmptyState message={t('person.noConnectedCompanies')} />
      ) : (
        <div className="space-y-3">
          {connected_companies.map((c) => (
            <CompanyCard key={c.company_idno} company={c} />
          ))}
        </div>
      )}
    </div>
  );
}

function CompanyCard({ company }: { company: { company_id: string | null; company_idno: string; company_name: string | null; company_status: string | null; roles: string[]; ownership_percentage?: number | null; director_role?: string | null } }) {
  const { t } = useTranslation();
  const statusLabel = translateStatus(t, company.company_status);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
      <div className="flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            {company.company_id ? (
              <Link to={appPath(`/companies/${company.company_id}`)} className="font-medium text-primary-600 hover:underline">
                {company.company_name || t('person.unknownCompany')}
              </Link>
            ) : (
              <span className="font-medium text-gray-900">{company.company_name || t('person.unknownCompany')}</span>
            )}
          </div>
          <p className="text-sm text-gray-500 mt-0.5">IDNO: {company.company_idno}</p>
        </div>
        <div className="flex items-center gap-2 ml-4 shrink-0">
          {company.company_status && (
            <Badge variant={statusVariant(company.company_status)}>{statusLabel}</Badge>
          )}
        </div>
      </div>
      <div className="mt-2 flex gap-1 flex-wrap">
        {company.roles.map((r) => (
          <Badge key={r} variant="default">{translateRole(t, r)}</Badge>
        ))}
        {company.director_role && (
          <Badge variant="default">{company.director_role}</Badge>
        )}
        {company.ownership_percentage != null && (
          <Badge variant="default">{t('company.relationships.ownership', { percentage: company.ownership_percentage.toFixed(1) })}</Badge>
        )}
      </div>
    </div>
  );
}

function Field({ label, value, className = '' }: { label: string; value: string | null | undefined; className?: string }) {
  return (
    <div className={className}>
      <dt className="text-gray-500">{label}</dt>
      <dd className="font-medium text-gray-900 mt-0.5">{value || '—'}</dd>
    </div>
  );
}
