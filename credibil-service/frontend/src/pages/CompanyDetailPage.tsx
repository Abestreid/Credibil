import { useState } from 'react';
import { useParams, Link, Navigate, useNavigate } from 'react-router-dom';
import RelationsTree, { REL_COLORS } from '@/components/RelationsTree';
import { useTranslation } from 'react-i18next';
import { useCompany, useDashboard, useFinancialReports, useCourtCases, useTendersByBuyer, useAccreditations, useCompanyRelationships, useCheckTaxDebt, useEnforcement, useEnforcementSummary, useMonitoredCompanies, useAddMonitoring, useRemoveMonitoring } from '@/lib/hooks';
import { LoadingState, ErrorState, Badge, EmptyState, formatCurrency, formatDate, statusVariant } from '@/components/ui';
import { translateStatus, translateRole, translateCategory, translateLegalForm, translateCourtType, translateRiskLevel, roleBadgeVariant } from '@/lib/translate';
import ExportButtons from '@/components/ExportButtons';
import { appPath } from '@/lib/path';
import { slugify } from '@/lib/slugify';
import type { DashboardResponse, CompanyRelationships, RelationshipPerson } from '@/types';

export default function CompanyDetailPage() {
  const { t } = useTranslation();
  const { id, slug } = useParams<{ id: string; slug?: string }>();
  const { data: companyResp, isLoading: companyLoading, error: companyError } = useCompany(id);

  const company = companyResp?.data;
  const idno = company?.idno;
  const { data: dashboard, isLoading: dashLoading, error: dashError, refetch: dashRefetch } = useDashboard(idno);
  const { data: financial, isLoading: finLoading, error: finError } = useFinancialReports(idno);
  const { data: court, isLoading: courtLoading, error: courtError } = useCourtCases(idno);
  const { data: tenders, isLoading: tenderLoading, error: tenderError } = useTendersByBuyer(idno);
  const { data: accreditations, isLoading: accredLoading, error: accredError } = useAccreditations({ keyword: company?.name_ro, limit: 20 });
  const { data: relationships, isLoading: relLoading, error: relError } = useCompanyRelationships(idno);

  if (companyLoading) {
    return <LoadingState message={t('company.loading')} />;
  }

  if (company) {
    const expectedSlug = slugify(company.name_ro || '');
    if (slug !== expectedSlug) {
      return <Navigate to={appPath(`/companies/${id}/${expectedSlug}`)} replace />;
    }
  }

  if (companyError || !company) {
    return (
      <div>
        <Link to={appPath('/dashboard')} className="text-sm text-primary-600 hover:underline mb-4 inline-block">
          {t('common.backToList')}
        </Link>
        <ErrorState message={t('company.notFound')} />
      </div>
    );
  }

  return (
    <div>
      <Link to={appPath('/dashboard')} className="text-sm text-primary-600 hover:underline mb-4 inline-block">
        {t('common.backToList')}
      </Link>

      <CompanyHeader company={company} relationships={relationships?.data} />

      <RelationsSection
        data={relationships?.data}
        loading={relLoading}
        error={!!relError}
        idno={idno}
        companyName={company.name_ro || company.name_ru || ''}
        companyStatus={company.status}
      />

      <div className="mt-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">{t('company.sections.overview')}</h2>
        {dashLoading && <LoadingState message={t('company.sections.loadingDashboard')} />}
        {dashError && <ErrorState message={t('company.sections.couldNotLoadDashboard')} retry={dashRefetch} />}
        {dashboard?.data && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {dashboard.data.risk_indicators.length > 0 && <RiskCard indicators={dashboard.data.risk_indicators} />}
            {dashboard.data.sanctions.is_sanctioned && <SanctionsCard sanctions={dashboard.data.sanctions} />}
            {dashboard.data.timeline.length > 0 && <TimelineCard entries={dashboard.data.timeline} />}
            {dashboard.data.financial && <FinancialSummaryCard financial={dashboard.data.financial} />}
            {!dashLoading && !dashError
              && dashboard.data.risk_indicators.length === 0
              && !dashboard.data.sanctions.is_sanctioned
              && dashboard.data.timeline.length === 0
              && !dashboard.data.financial && (
              <p className="text-sm text-gray-400 col-span-full">{t('company.sections.noAnalytics')}</p>
            )}
          </div>
        )}
      </div>

      <div className="mt-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">{t('company.sections.financialReports')}</h2>
        {finLoading && <LoadingState message={t('company.sections.loadingFinancial')} />}
        {finError && <ErrorState message={t('company.sections.couldNotLoadFinancial')} />}
        {!finLoading && !finError && financial?.data && financial.data.length > 0 && (
          <FinancialTable reports={financial.data} />
        )}
        {!finLoading && !finError && financial?.data && financial.data.length === 0 && (
          <NoFinancialData />
        )}
        {!finLoading && !finError && !financial && (
          <LoadingState message={t('company.sections.initializingFinancial')} />
        )}
      </div>

      <div className="mt-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">{t('company.sections.courtCases')}</h2>
        {courtLoading && <LoadingState message={t('company.sections.loadingCourt')} />}
        {courtError && <ErrorState message={t('company.sections.couldNotLoadCourt')} />}
        {!courtLoading && !courtError && (
          court?.data && court.data.length > 0
            ? <CourtTable cases={court.data} />
            : <EmptyState message={t('company.sections.noCourtCases')} />
        )}
      </div>

      <div className="mt-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">{t('company.sections.enforcement')}</h2>
        <EnforcementSection idno={idno} />
      </div>

      <div className="mt-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">{t('company.sections.procurement')}</h2>
        {tenderLoading && <LoadingState message={t('company.sections.loadingTenders')} />}
        {tenderError && <ErrorState message={t('company.sections.couldNotLoadTenders')} />}
        {!tenderLoading && !tenderError && (
          tenders?.data && tenders.data.length > 0
            ? <TenderTable tenders={tenders.data} />
            : <EmptyState message={t('company.sections.noTenders')} />
        )}
      </div>

      <div className="mt-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">{t('company.sections.acreditări')}</h2>
        {accredLoading && <LoadingState message={t('company.sections.loadingAccreditations')} />}
        {accredError && <ErrorState message={t('company.sections.couldNotLoadAccreditations')} />}
        {!accredLoading && !accredError && (
          accreditations?.data && accreditations.data.length > 0
            ? <AccreditationTable accreditations={accreditations.data} />
            : <EmptyState message={t('company.sections.noAccreditations')} />
        )}
      </div>

      <div className="mt-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">{t('company.sections.sanctions')}</h2>
        {dashboard?.data?.sanctions ? (
          dashboard.data.sanctions.is_sanctioned
            ? <SanctionsCard sanctions={dashboard.data.sanctions} />
            : <div className="bg-green-50 border border-green-200 rounded-lg p-5"><p className="text-sm text-green-700">{t('company.sections.noSanctions')}</p></div>
        ) : (
          !dashLoading && !dashError && <EmptyState message={t('company.sections.sanctionsNotAvailable')} />
        )}
      </div>
    </div>
  );
}

function MonitorButton({ idno }: { idno: string }) {
  const { t } = useTranslation();
  const { data: monitored } = useMonitoredCompanies();
  const add = useAddMonitoring();
  const remove = useRemoveMonitoring();
  const isMonitored = monitored?.data?.some((m) => m.idno === idno) ?? false;
  const busy = add.isPending || remove.isPending;

  const toggle = () => {
    if (isMonitored) remove.mutate(idno);
    else add.mutate(idno);
  };

  return (
    <button
      type="button"
      onClick={toggle}
      disabled={busy}
      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium border transition-colors disabled:opacity-50 ${
        isMonitored
          ? 'bg-primary-50 text-primary-700 border-primary-200 hover:bg-primary-100'
          : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
      }`}
    >
      <svg className="w-4 h-4" fill={isMonitored ? 'currentColor' : 'none'} stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
      {isMonitored ? t('monitoring.watching') : t('monitoring.watch')}
    </button>
  );
}

function CompanyHeader({ company, relationships }: { company: NonNullable<ReturnType<typeof useCompany>['data']>['data']; relationships?: CompanyRelationships }) {
  const { t } = useTranslation();
  const statusLabel = translateStatus(t, company.status);
  const checkTaxDebt = useCheckTaxDebt(company.id);

  const founders = relationships?.persons.filter((p) => p.roles_in_current.includes('founder')) ?? [];
  const directors = relationships?.persons.filter((p) => p.roles_in_current.includes('director')) ?? [];

  const founderNames = founders.map((p) => {
    const cc = p.connected_companies.find((c) => c.is_current);
    const pct = cc?.ownership_percentage;
    return pct != null ? `${p.person_name} (${pct.toFixed(0)}%)` : p.person_name;
  });

  // Group directors by role
  const directorsByRole = new Map<string, string[]>();
  for (const p of directors) {
    const cc = p.connected_companies.find((c) => c.is_current);
    const role = cc?.director_role || t('company.header.unknownRole');
    if (!directorsByRole.has(role)) directorsByRole.set(role, []);
    directorsByRole.get(role)!.push(p.person_name);
  }
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">{company.name_ro}</h2>
          {company.name_ru && <p className="text-sm text-gray-500">{company.name_ru}</p>}
        </div>
        <div className="flex items-center gap-2">
          {company.status && (
            company.status === 'liquidated'
              ? <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-700 border border-red-300">{statusLabel}</span>
              : <Badge variant={statusVariant(company.status)}>{statusLabel}</Badge>
          )}
          <MonitorButton idno={company.idno} />
          <ExportButtons entityType="company" entityId={company.idno} />
        </div>
      </div>
      <dl className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <Field label={t('company.header.idno')} value={company.idno} />
        <Field label={t('company.header.legalForm')} value={translateLegalForm(t, company.legal_form)} />
        <Field label={t('company.header.caem')} value={company.caem} />
        <Field label={t('company.header.registration')} value={formatDate(company.registration_date)} />
        <Field label={t('company.header.address')} value={company.legal_address} className="col-span-2" />
        <Field label={t('company.header.postalCode')} value={company.postal_code} />
        <Field label={t('company.header.cuiio')} value={company.cuiio} />
        <Field label={t('company.header.cuatm')} value={company.cuatm} />
        <Field label={t('company.header.cfp')} value={company.cfp} />
        <Field label={t('company.header.cfoj')} value={company.cfoj} />
        <Field label={t('company.header.category')} value={translateCategory(t, company.business_category)} />
        <div>
          <dt className="text-gray-500">{t('company.header.taxDebt')}</dt>
          <dd className="font-medium text-gray-900 mt-0.5">
            {company.tax_debt != null ? `${company.tax_debt.toLocaleString()} MDL` : '—'}
          </dd>
          {company.tax_debt_fetched_at && (
            <dd className="text-xs text-gray-400 mt-0.5">
              {t('company.header.fetched')} {new Date(company.tax_debt_fetched_at).toLocaleDateString()}
            </dd>
          )}
          <button
            onClick={() => checkTaxDebt.mutate()}
            disabled={checkTaxDebt.isPending}
            className="mt-1 px-2 py-0.5 text-xs bg-blue-50 text-blue-600 rounded hover:bg-blue-100 disabled:opacity-50"
            title={t('company.header.refreshTaxDebt')}
          >
            {checkTaxDebt.isPending ? t('company.header.refreshing') : t('company.header.refresh')}
          </button>
        </div>
        <Field
          label={t('company.header.founders')}
          value={
            founderNames.length > 0
              ? <span>{founderNames.length} <span className="text-gray-400 font-normal text-xs">({founderNames.join(', ')})</span></span>
              : company.founder_count?.toString()
          }
        />
        {directorsByRole.size > 0
          ? [...directorsByRole.entries()].map(([role, names]) => (
            <Field
              key={role}
              label={role}
              value={<span>{names.length} <span className="text-gray-400 font-normal text-xs">({names.join(', ')})</span></span>}
            />
          ))
          : <Field label={t('company.header.directors')} value={company.director_count?.toString()} />
        }
        <Field label={t('company.header.caemDesc')} value={company.caem_description} className="col-span-2" />
      </dl>
      {checkTaxDebt.isSuccess && (
        <p className="mt-2 text-xs text-green-600">{t('company.header.taxDebtQueued')}</p>
      )}
      {checkTaxDebt.isError && (
        <p className="mt-2 text-xs text-red-600">{t('company.header.taxDebtFailed')}</p>
      )}
    </div>
  );
}

function Field({ label, value, className = '' }: { label: string; value: string | number | React.ReactNode | null | undefined; className?: string }) {
  return (
    <div className={className}>
      <dt className="text-gray-500">{label}</dt>
      <dd className="font-medium text-gray-900 mt-0.5">{value || '—'}</dd>
    </div>
  );
}

function RelationsSection({ data, loading, error, idno, companyName, companyStatus }: {
  data?: CompanyRelationships;
  loading: boolean;
  error: boolean;
  idno?: string;
  companyName: string;
  companyStatus?: string | null;
}) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [view, setView] = useState<'list' | 'graph'>('list');

  const hasData = !loading && !error && data && data.persons.length > 0;
  const rolesPresent = Array.from(
    new Set((data?.persons ?? []).flatMap((p) => p.roles_in_current)),
  ).filter((r) => REL_COLORS[r]);

  const viewBtn = (key: 'list' | 'graph', label: string, icon: JSX.Element) => (
    <button
      type="button"
      onClick={() => setView(key)}
      className={`flex items-center gap-2 w-full px-3 py-2 rounded-md text-sm font-medium transition-colors ${
        view === key ? 'bg-primary-50 text-primary-700' : 'text-gray-600 hover:bg-gray-50'
      }`}
    >
      {icon}
      {label}
    </button>
  );

  return (
    <div className="mt-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-3">{t('company.sections.relationships')}</h2>
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_224px] gap-4">
        <div className="min-w-0 order-2 lg:order-1">
          {loading && <LoadingState message={t('company.sections.loadingRelationships')} />}
          {error && <ErrorState message={t('company.sections.couldNotLoadRelationships')} />}
          {!loading && !error && (
            hasData ? (
              view === 'list'
                ? <RelationshipsList data={data!} currentIdno={idno} />
                : (
                  <RelationsTree
                    data={data!}
                    center={{ idno: idno || '', name: companyName, status: companyStatus }}
                    onOpenCompany={(cidno, cid, name) =>
                      navigate(appPath(`/companies/${cid ?? cidno}/${slugify(name)}`))
                    }
                  />
                )
            ) : (
              <EmptyState message={t('company.sections.noRelationships')} />
            )
          )}
        </div>

        {/* right sidebar: view switcher + legend */}
        <aside className="order-1 lg:order-2">
          <div className="bg-white border border-gray-200 rounded-lg p-3 lg:sticky lg:top-4">
            <div className="text-[11px] font-semibold uppercase tracking-wide text-gray-400 mb-2">
              {t('relations.viewAs')}
            </div>
            <div className="space-y-1">
              {viewBtn('list', t('relations.list'),
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" /></svg>)}
              {viewBtn('graph', t('relations.graph'),
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8a3 3 0 100-6 3 3 0 000 6zM5 22a3 3 0 100-6 3 3 0 000 6zM19 22a3 3 0 100-6 3 3 0 000 6zM12 8v3m0 0l-5 5m5-5l5 5" /></svg>)}
            </div>

            {view === 'graph' && rolesPresent.length > 0 && (
              <div className="mt-4 pt-3 border-t border-gray-100">
                <div className="text-[11px] font-semibold uppercase tracking-wide text-gray-400 mb-2">
                  {t('relations.legend')}
                </div>
                <div className="space-y-1.5">
                  {rolesPresent.map((r) => (
                    <div key={r} className="flex items-center gap-2 text-xs text-gray-600">
                      <span className="inline-block w-4 h-0.5 rounded" style={{ background: REL_COLORS[r] }} />
                      {translateRole(t, r)}
                    </div>
                  ))}
                </div>
                <p className="text-[11px] text-gray-400 mt-3">{t('relations.hint')}</p>
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}

function RelationshipsList({ data, currentIdno }: { data: CompanyRelationships; currentIdno?: string }) {
  return (
    <div className="space-y-4">
      {data.persons.map((person) => (
        <PersonRelationshipCard key={person.person_id} person={person} currentIdno={currentIdno} />
      ))}
    </div>
  );
}

function PersonRelationshipCard({ person, currentIdno }: { person: RelationshipPerson; currentIdno?: string }) {
  const { t } = useTranslation();
  const statusLabel = (s: string | null) => translateStatus(t, s);

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <div className="flex items-start justify-between mb-3">
        <div>
          <Link to={appPath(`/persons/${person.person_id}`)} className="font-medium text-primary-600 hover:underline text-sm">
            {person.person_name}
          </Link>
          <p className="text-xs text-gray-500 mt-0.5">
            {person.roles_in_current.map((r) => translateRole(t, r)).join(' & ')}
          </p>
        </div>
        <div className="text-right text-xs text-gray-500 shrink-0 ml-4">
          <div>{t('company.relationships.connected', { count: person.total_companies })}</div>
          {person.active_companies > 0 && <div className="text-green-600">{t('company.relationships.active', { count: person.active_companies })}</div>}
          {person.liquidated_companies > 0 && <div className="text-red-500">{t('company.relationships.liquidated', { count: person.liquidated_companies })}</div>}
        </div>
      </div>

      <div className="space-y-1.5">
        {person.connected_companies.map((c) => {
          const isCurrent = c.company_idno === currentIdno;
          return (
            <div key={c.company_idno} className={`flex items-center justify-between text-sm py-1 px-2 rounded ${isCurrent ? 'bg-primary-50' : 'hover:bg-gray-50'}`}>
              <div className="min-w-0 flex-1">
                {c.company_id ? (
                  <Link to={appPath(`/companies/${c.company_idno}`)} className="font-medium text-gray-900 hover:text-primary-600 truncate block">
                    {c.company_name || t('company.relationships.unknown')}
                  </Link>
                ) : (
                  <span className="font-medium text-gray-900 truncate block">{c.company_name || t('company.relationships.unknown')}</span>
                )}
                <span className="text-xs text-gray-500">IDNO: {c.company_idno}</span>
              </div>
              <div className="flex items-center gap-2 ml-3 shrink-0">
                <div className="flex gap-1">
                  {c.roles.map((r) => (
                    <Badge key={r} variant={isCurrent ? roleBadgeVariant(r) : 'default'}>{translateRole(t, r)}</Badge>
                  ))}
                  {c.director_role && (
                    <Badge variant={isCurrent ? roleBadgeVariant(c.director_role) : 'default'}>{c.director_role}</Badge>
                  )}
                  {c.ownership_percentage != null && (
                    <Badge variant={isCurrent ? 'success' : 'default'}>{t('company.relationships.ownership', { percentage: c.ownership_percentage.toFixed(1) })}</Badge>
                  )}
                </div>
                {c.company_status && <Badge variant={statusVariant(c.company_status)}>{statusLabel(c.company_status)}</Badge>}
                {isCurrent && <span className="text-xs text-primary-600 font-medium">{t('company.relationships.current')}</span>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function RiskCard({ indicators }: { indicators: NonNullable<DashboardResponse['risk_indicators']> }) {
  const { t } = useTranslation();
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-3">{t('company.risk')}</h3>
      <div className="space-y-2">
        {indicators.map((r, i) => (
          <div key={i} className="flex items-center justify-between text-sm">
            <span className="text-gray-700">{r.category}</span>
            <Badge variant={r.level === 'low' ? 'success' : r.level === 'medium' ? 'warning' : 'danger'}>{translateRiskLevel(t, r.level)}</Badge>
          </div>
        ))}
      </div>
    </div>
  );
}

function SanctionsCard({ sanctions }: { sanctions: NonNullable<DashboardResponse['sanctions']> }) {
  const { t } = useTranslation();
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-5">
      <h3 className="text-sm font-semibold text-red-800 mb-2">{t('company.sanctions.activeSanctions')}</h3>
      <p className="text-sm text-red-700">
        {t('company.sanctions.activeCount', {
          active: sanctions.active_sanctions,
          total: sanctions.sanctions_count > 0 ? t('company.sanctions.total', { count: sanctions.sanctions_count }) : '',
        })}
      </p>
      {sanctions.sanction_types.length > 0 && (
        <div className="flex gap-1 mt-2 flex-wrap">{sanctions.sanction_types.map((t_) => <Badge key={t_} variant="danger">{t_}</Badge>)}</div>
      )}
    </div>
  );
}

function TimelineCard({ entries }: { entries: NonNullable<DashboardResponse['timeline']> }) {
  const { t } = useTranslation();
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-3">{t('company.timeline')}</h3>
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {entries.slice(0, 20).map((e, i) => (
          <div key={i} className="text-sm">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs text-gray-400">{e.date}</span>
              <Badge>{e.event_type}</Badge>
            </div>
            <p className="text-gray-700 mt-0.5">{e.title}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function FinancialSummaryCard({ financial }: { financial: NonNullable<DashboardResponse['financial']> }) {
  const { t } = useTranslation();
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-3">{t('company.financialSummary', { years: financial.years_analyzed.join(', ') })}</h3>
      {financial.revenue_chart.length > 0 && (
        <div className="space-y-1 text-sm">
          {financial.revenue_chart.map((p) => (
            <div key={p.year} className="flex justify-between">
              <span className="text-gray-600">{p.year}</span>
              <span className="font-medium">{formatCurrency(p.value)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function NoFinancialData() {
  const { t } = useTranslation();
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 text-center">
      <p className="text-sm text-gray-500">{t('company.noFinancialData')}</p>
    </div>
  );
}

function FinancialTable({ reports }: { reports: NonNullable<ReturnType<typeof useFinancialReports>['data']>['data'] }) {
  const { t } = useTranslation();
  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-x-auto">
      <table className="min-w-max divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-3 py-2 text-left font-medium text-gray-500 sticky left-0 bg-gray-50">{t('company.financial.year')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.revenue')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.costOfSales')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.distribution')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.admin')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.financialExp')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.tax')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.netProfit')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.totalAssets')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.currentAssets')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.inventories')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.receivables')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.cash')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.shortTermDatorii')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.longTermDatorii')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.equity')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.shareCapital')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 whitespace-nowrap">{t('company.financial.employees')}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {reports.map((r) => (
            <tr key={r.id} className="hover:bg-gray-50">
              <td className="px-3 py-2 font-medium sticky left-0 bg-white">{r.year}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.revenue)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.cost_of_goods_sold)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.distribution_expenses)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.admin_expenses)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.financial_expenses)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.income_tax)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.profit)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.total_assets)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.current_assets)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.inventories)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.trade_receivables)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.cash_and_banks)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.short_term_debt)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.long_term_debt)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.equity)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{formatCurrency(r.share_capital)}</td>
              <td className="px-3 py-2 text-right whitespace-nowrap">{r.employees_count ?? '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CourtTable({ cases }: { cases: NonNullable<ReturnType<typeof useCourtCases>['data']>['data'] }) {
  const { t } = useTranslation();
  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.court.caseNumber')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.court.type')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.court.court')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.court.status')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500 hidden md:table-cell">{t('company.court.judge')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500 hidden lg:table-cell">{t('company.court.date')}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {cases.map((c) => (
            <tr key={c.id} className="hover:bg-gray-50">
              <td className="px-3 py-2 font-mono text-xs">{c.case_number}</td>
              <td className="px-3 py-2">{translateCourtType(t, c.case_type)}</td>
              <td className="px-3 py-2">{c.court_name}</td>
              <td className="px-3 py-2"><Badge variant={statusVariant(c.status)}>{translateStatus(t, c.status)}</Badge></td>
              <td className="px-3 py-2 hidden md:table-cell">{c.judge_name ?? '—'}</td>
              <td className="px-3 py-2 hidden lg:table-cell">{formatDate(c.registration_date)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function EnforcementSection({ idno }: { idno: string | undefined }) {
  const { t } = useTranslation();
  const [tab, setTab] = useState<'active' | 'archived'>('active');
  const { data: summary } = useEnforcementSummary(idno);
  const { data, isLoading, error } = useEnforcement(idno, tab);

  const counts = summary?.data;
  const rows = data?.data ?? [];

  const tabBtn = (key: 'active' | 'archived', label: string, count: number) => (
    <button
      type="button"
      onClick={() => setTab(key)}
      className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
        tab === key ? 'bg-primary-50 text-primary-700' : 'text-gray-500 hover:bg-gray-50'
      }`}
    >
      {label}
      <span className="ml-1.5 text-xs text-gray-400 tabular-nums">{count}</span>
    </button>
  );

  return (
    <div>
      <div className="flex items-center gap-1 mb-3">
        {tabBtn('active', t('company.enforcement.active'), counts?.active ?? 0)}
        {tabBtn('archived', t('company.enforcement.archived'), counts?.archived ?? 0)}
        {counts && (counts.as_debtor > 0 || counts.as_creditor > 0) && (
          <span className="ml-auto text-xs text-gray-400">
            {t('company.enforcement.asDebtor')}: {counts.as_debtor} · {t('company.enforcement.asCreditor')}: {counts.as_creditor}
          </span>
        )}
      </div>
      {isLoading && <LoadingState message={t('company.sections.loadingEnforcement')} />}
      {error && <ErrorState message={t('company.sections.couldNotLoadEnforcement')} />}
      {!isLoading && !error && (
        rows.length > 0
          ? <EnforcementTable rows={rows} />
          : <EmptyState message={tab === 'active' ? t('company.enforcement.noActive') : t('company.enforcement.noArchived')} />
      )}
    </div>
  );
}

function EnforcementTable({ rows }: { rows: NonNullable<ReturnType<typeof useEnforcement>['data']>['data'] }) {
  const { t } = useTranslation();
  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.enforcement.role')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.enforcement.counterparty')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500 hidden md:table-cell">{t('company.enforcement.docNumber')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500 hidden lg:table-cell">{t('company.enforcement.court')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500">{t('company.enforcement.amount')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500 hidden md:table-cell">{t('company.enforcement.published')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {rows.map((r) => {
            const counterparty = r.role === 'debtor' ? r.creditor_name : r.debtor_name;
            return (
              <tr key={r.id} className="hover:bg-gray-50">
                <td className="px-3 py-2">
                  {r.role === 'debtor' && <Badge variant="danger">{t('company.enforcement.debtor')}</Badge>}
                  {r.role === 'creditor' && <Badge variant="success">{t('company.enforcement.creditor')}</Badge>}
                  {!r.role && <span className="text-gray-400">—</span>}
                </td>
                <td className="px-3 py-2">{counterparty ?? '—'}</td>
                <td className="px-3 py-2 font-mono text-xs hidden md:table-cell">{r.executory_doc_number ?? r.case_number ?? '—'}</td>
                <td className="px-3 py-2 hidden lg:table-cell">{r.court_name ?? '—'}</td>
                <td className="px-3 py-2 text-right tabular-nums">{r.amount != null ? formatCurrency(r.amount, r.currency) : '—'}</td>
                <td className="px-3 py-2 hidden md:table-cell">{formatDate(r.publication_date)}</td>
                <td className="px-3 py-2">
                  {r.source_url && (
                    <a href={r.source_url} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline text-xs">
                      {t('company.enforcement.source')}
                    </a>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function TenderTable({ tenders }: { tenders: NonNullable<ReturnType<typeof useTendersByBuyer>['data']>['data'] }) {
  const { t } = useTranslation();
  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.tender.title')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.tender.ocid')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.tender.status')}</th>
            <th className="px-3 py-2 text-right font-medium text-gray-500 hidden md:table-cell">{t('company.tender.value')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500 hidden lg:table-cell">{t('company.tender.method')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500 hidden lg:table-cell">{t('company.tender.date')}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {tenders.map((t_) => (
            <tr key={t_.id} className="hover:bg-gray-50">
              <td className="px-3 py-2 font-medium max-w-xs truncate">{t_.title}</td>
              <td className="px-3 py-2 font-mono text-xs">{t_.ocid}</td>
              <td className="px-3 py-2"><Badge variant={statusVariant(t_.status)}>{translateStatus(t, t_.status)}</Badge></td>
              <td className="px-3 py-2 text-right hidden md:table-cell">{formatCurrency(t_.value_amount, t_.value_currency ?? 'MDL')}</td>
              <td className="px-3 py-2 hidden lg:table-cell">{t_.procurement_method ?? '—'}</td>
              <td className="px-3 py-2 hidden lg:table-cell">{formatDate(t_.published_date)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AccreditationTable({ accreditations }: { accreditations: NonNullable<ReturnType<typeof useAccreditations>['data']>['data'] }) {
  const { t } = useTranslation();
  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.accreditation.organization')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.accreditation.certificate')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.accreditation.category')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.accreditation.standard')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500">{t('company.accreditation.status')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500 hidden md:table-cell">{t('company.accreditation.issueDate')}</th>
            <th className="px-3 py-2 text-left font-medium text-gray-500 hidden lg:table-cell">{t('company.accreditation.expiryDate')}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {accreditations.map((a) => (
            <tr key={a.id} className="hover:bg-gray-50">
              <td className="px-3 py-2 font-medium">{a.organization_name}</td>
              <td className="px-3 py-2 font-mono text-xs">{a.certificate_number}</td>
              <td className="px-3 py-2">{translateCategory(t, a.category)}</td>
              <td className="px-3 py-2">{a.standard}</td>
              <td className="px-3 py-2"><Badge variant={statusVariant(a.status)}>{translateStatus(t, a.status)}</Badge></td>
              <td className="px-3 py-2 hidden md:table-cell">{formatDate(a.issue_date)}</td>
              <td className="px-3 py-2 hidden lg:table-cell">{formatDate(a.expiry_date)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
