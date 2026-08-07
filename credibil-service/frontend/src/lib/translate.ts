import { TFunction } from 'i18next';

const STATUS_MAP: Record<string, string> = {
  active: 'statuses.active',
  inactive: 'statuses.inactive',
  liquidated: 'statuses.liquidated',
  dissolved: 'statuses.dissolved',
  pending: 'statuses.pending',
  suspended: 'statuses.suspended',
  closed: 'statuses.closed',
  open: 'statuses.open',
  completed: 'statuses.completed',
  ongoing: 'statuses.ongoing',
  in_progress: 'statuses.in_progress',
  rejected: 'statuses.rejected',
  favorable: 'statuses.favorable',
  unfavorable: 'statuses.unfavorable',
  filed: 'statuses.filed',
  dismissed: 'statuses.dismissed',
  awarded: 'statuses.awarded',
  cancelled: 'statuses.cancelled',
  published: 'statuses.published',
  evaluated: 'statuses.evaluated',
  planned: 'statuses.planned',
  revoked: 'statuses.revoked',
  expired: 'statuses.expired',
};

const ROLE_MAP: Record<string, string> = {
  director: 'roles.director',
  founder: 'roles.founder',
  shareholder: 'roles.shareholder',
  owner: 'roles.owner',
  administrator: 'roles.administrator',
};

const CATEGORY_MAP: Record<string, string> = {
  micro: 'categories.micro',
  small: 'categories.small',
  medium: 'categories.medium',
  large: 'categories.large',
};

const LEGAL_FORM_MAP: Record<string, string> = {
  SRL: 'legalForms.SRL',
  SA: 'legalForms.SA',
  OTHER: 'legalForms.OTHER',
  IF: 'legalForms.IF',
  II: 'legalForms.II',
};

const PERSON_TYPE_MAP: Record<string, string> = {
  natural: 'personTypes.natural',
  legal: 'personTypes.legal',
  individual: 'personTypes.individual',
};

const RISK_LEVEL_MAP: Record<string, string> = {
  low: 'riskLevels.low',
  medium: 'riskLevels.medium',
  high: 'riskLevels.high',
  critical: 'riskLevels.critical',
};

const COURT_TYPE_MAP: Record<string, string> = {
  civil: 'courtTypes.civil',
  criminal: 'courtTypes.criminal',
  administrative: 'courtTypes.administrative',
  commercial: 'courtTypes.commercial',
};

export function translateStatus(t: TFunction, status: string | null | undefined): string {
  if (!status) return '—';
  const key = STATUS_MAP[status.toLowerCase()];
  return key ? t(key) : status.charAt(0).toUpperCase() + status.slice(1);
}

export function translateRole(t: TFunction, role: string | null | undefined): string {
  if (!role) return '—';
  const key = ROLE_MAP[role.toLowerCase()];
  return key ? t(key) : role.charAt(0).toUpperCase() + role.slice(1);
}

export function roleBadgeVariant(role: string | null | undefined): 'default' | 'success' | 'info' | 'danger' | 'warning' {
  if (!role) return 'default';
  const r = role.toLowerCase();
  if (r === 'founder' || r === 'shareholder' || r === 'owner') return 'success';
  if (r === 'director' || r === 'administrator' || r === 'administrator provizoriu' || r === 'direcţie de conducere') return 'info';
  if (r === 'lichidator' || r === 'administrator al procesului de insolvabilitate' || r === 'administrator din oficiu') return 'danger';
  return 'default';
}

export function translateCategory(t: TFunction, category: string | null | undefined): string {
  if (!category) return '—';
  const key = CATEGORY_MAP[category.toLowerCase()];
  return key ? t(key) : category.charAt(0).toUpperCase() + category.slice(1);
}

export function translateLegalForm(t: TFunction, form: string | null | undefined): string {
  if (!form) return '—';
  const key = LEGAL_FORM_MAP[form];
  return key ? t(key) : form;
}

export function translatePersonType(t: TFunction, type: string | null | undefined): string {
  if (!type) return '—';
  const key = PERSON_TYPE_MAP[type.toLowerCase()];
  return key ? t(key) : type.charAt(0).toUpperCase() + type.slice(1);
}

export function translateRiskLevel(t: TFunction, level: string | null | undefined): string {
  if (!level) return '—';
  const key = RISK_LEVEL_MAP[level.toLowerCase()];
  return key ? t(key) : level.charAt(0).toUpperCase() + level.slice(1);
}

export function translateCourtType(t: TFunction, type: string | null | undefined): string {
  if (!type) return '—';
  const key = COURT_TYPE_MAP[type.toLowerCase()];
  return key ? t(key) : type.charAt(0).toUpperCase() + type.slice(1);
}
