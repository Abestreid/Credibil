import { useTranslation } from 'react-i18next';

export function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const cls = size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-8 w-8' : 'h-6 w-6';
  return (
    <svg className={`animate-spin ${cls} text-primary-600`} fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}

export function LoadingState({ message }: { message?: string }) {
  const { t } = useTranslation();
  const text = message ?? t('common.loading');
  return (
    <div className="flex items-center justify-center py-12 gap-3">
      <Spinner />
      <span className="text-sm text-gray-500">{text}</span>
    </div>
  );
}

export function ErrorState({ message, retry }: { message: string; retry?: () => void }) {
  const { t } = useTranslation();
  return (
    <div className="text-center py-12">
      <p className="text-red-600 text-sm mb-3">{message}</p>
      {retry && (
        <button onClick={retry} className="text-sm text-primary-600 hover:underline">
          {t('common.tryAgain')}
        </button>
      )}
    </div>
  );
}

export function EmptyState({ message }: { message?: string }) {
  const { t } = useTranslation();
  const text = message ?? t('common.noData');
  return (
    <div className="text-center py-12">
      <p className="text-gray-500 text-sm">{text}</p>
    </div>
  );
}

export function Badge({ children, variant = 'default' }: { children: React.ReactNode; variant?: 'default' | 'success' | 'warning' | 'danger' | 'info' }) {
  const colors = {
    default: 'bg-gray-100 text-gray-700',
    success: 'bg-green-100 text-green-700',
    warning: 'bg-yellow-100 text-yellow-700',
    danger: 'bg-red-100 text-red-700',
    info: 'bg-blue-100 text-blue-700',
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colors[variant]}`}>
      {children}
    </span>
  );
}

export function formatCurrency(amount: number | null, currency = 'MDL') {
  if (amount == null) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency, maximumFractionDigits: 0 }).format(amount);
}

export function formatDate(date: string | null) {
  if (!date) return '—';
  return new Date(date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
}

export function statusVariant(status: string) {
  if (['active', 'completed', 'solved', 'favorable'].includes(status)) return 'success' as const;
  if (['pending', 'in_progress', 'ongoing', 'open'].includes(status)) return 'warning' as const;
  if (['inactive', 'suspended', 'rejected', 'unfavorable', 'closed'].includes(status)) return 'danger' as const;
  return 'default' as const;
}
