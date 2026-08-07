export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  status: string;
  tenant_id: string | null;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface Company {
  id: string;
  idno: string;
  name_ro: string;
  name_ru: string;
  registration_date: string | null;
  status: string;
  legal_form: string;
  legal_address: string | null;
  postal_code: string | null;
  caem: string | null;
  caem_description: string | null;
  cuatm: string | null;
  cuiio: string | null;
  cfp: string | null;
  cfoj: string | null;
  business_category: string | null;
  tax_debt: number | null;
  tax_debt_fetched_at: string | null;
  founder_count: number;
  director_count: number;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface PaginationMeta {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  meta?: PaginationMeta;
  request_id?: string;
}

export interface SearchHit {
  id: string;
  entity_type: 'company' | 'person';
  data: Record<string, unknown>;
  highlights: Record<string, string>;
  match_type?: string;
  matched_field?: string;
  match_reason?: string;
}

export interface SearchPaginationMeta {
  page: number;
  page_size: number;
  total_hits: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface SearchResponse {
  hits: SearchHit[];
  meta: SearchPaginationMeta;
  processing_time_ms: number;
  query: string;
}

export interface AutocompleteSuggestion {
  id: string;
  entity_type: 'company' | 'person';
  data: Record<string, unknown>;
  match_type?: string;
  match_reason?: string;
}

export interface AutocompleteResponse {
  suggestions: AutocompleteSuggestion[];
  processing_time_ms: number;
}

export interface DashboardResponse {
  summary: {
    idno: string;
    name_ro: string | null;
    name_ru: string | null;
    status: string | null;
    legal_form: string | null;
    caem: string | null;
    caem_description: string | null;
    legal_address: string | null;
    registration_date: string | null;
    founder_count: number;
    director_count: number;
    tax_debt: number | null;
  } | null;
  financial: {
    company_idno: string;
    company_name: string | null;
    years_analyzed: number[];
    growth: { current_year: number; revenue_growth_pct: number | null; profit_growth_pct: number | null }[];
    margins: { year: number; gross_margin_pct: number | null; net_margin_pct: number | null }[];
    liquidity: { year: number; current_ratio: number | null; debt_to_equity_ratio: number | null }[];
    employee_dynamics: { year: number; employees_count: number | null; yoy_change_pct: number | null }[];
    revenue_chart: { year: number; value: number }[];
    profit_chart: { year: number; value: number }[];
    assets_chart: { year: number; value: number }[];
    employees_chart: { year: number; value: number }[];
  } | null;
  court_statistics: Record<string, unknown>;
  court_judges: Record<string, unknown>[];
  court_distribution: Record<string, unknown>[];
  court_timeline: Record<string, unknown>[];
  tender_statistics: Record<string, unknown>;
  tender_awards: Record<string, unknown>;
  tender_win_rate: Record<string, unknown>;
  tender_methods: Record<string, unknown>[];
  tender_timeline: Record<string, unknown>[];
  relationship_graph: {
    nodes: { id: string; label: string; node_type: string; idno?: string }[];
    edges: { source: string; target: string; relationship_type: string; is_active: boolean }[];
    total_nodes: number;
    total_edges: number;
  };
  timeline: { date: string; event_type: string; title: string; description: string | null; source: string | null }[];
  risk_indicators: { category: string; level: string; score: number | null; factors: string[]; details: string | null }[];
  sanctions: { is_sanctioned: boolean; sanctions_count: number; active_sanctions: number; sanction_types: string[]; lists: string[] };
}

export interface FinancialReport {
  id: string;
  company_idno: string;
  year: number;
  period: string;
  company_name: string | null;
  // P&L summary
  revenue: number | null;
  expenses: number | null;
  profit: number | null;
  // Balance sheet summary
  total_assets: number | null;
  total_liabilities: number | null;
  equity: number | null;
  // P&L detail
  cost_of_goods_sold: number | null;
  distribution_expenses: number | null;
  admin_expenses: number | null;
  other_operating_expenses: number | null;
  financial_income: number | null;
  financial_expenses: number | null;
  income_tax: number | null;
  // Balance sheet detail
  current_assets: number | null;
  fixed_assets: number | null;
  inventories: number | null;
  trade_receivables: number | null;
  cash_and_banks: number | null;
  short_term_debt: number | null;
  long_term_debt: number | null;
  share_capital: number | null;
  // Cash flow
  operating_cash_flow: number | null;
  investing_cash_flow: number | null;
  financing_cash_flow: number | null;
  // Misc
  employees_count: number | null;
  created_at: string;
  updated_at: string;
}

export interface CourtCase {
  id: string;
  case_number: string;
  case_type: string;
  court_name: string;
  court_type: string;
  status: string;
  plaintiff_name: string | null;
  defendant_name: string | null;
  judge_name: string | null;
  registration_date: string | null;
  decision_date: string | null;
  created_at: string;
}

export interface MonitoredCompany {
  id: string;
  idno: string;
  company_id: string | null;
  company_name: string | null;
  is_active: boolean;
  created_at: string | null;
  last_checked_at: string | null;
  last_change_at: string | null;
}

export interface MonitoringChangeEvent {
  id: string;
  idno: string;
  category: string;
  field: string;
  description: string;
  old_value: string | null;
  new_value: string | null;
  detected_at: string | null;
}

export interface MonitoringNotification {
  id: string;
  idno: string;
  company_name: string | null;
  change_count: number;
  categories: string[];
  summary: string | null;
  is_read: boolean;
  created_at: string | null;
}

export interface EnforcementProceeding {
  id: string;
  somation_id: number;
  debtor_name: string | null;
  debtor_idno: string | null;
  debtor_idno_masked: string | null;
  creditor_name: string | null;
  creditor_idno: string | null;
  executory_doc_number: string | null;
  court_name: string | null;
  case_number: string | null;
  amount: number | null;
  currency: string;
  publication_date: string | null;
  state: 'active' | 'archived';
  source_url: string | null;
  role: 'debtor' | 'creditor' | null;
}

export interface EnforcementSummary {
  idno: string;
  total: number;
  active: number;
  archived: number;
  as_debtor: number;
  as_creditor: number;
}

export interface Tender {
  id: string;
  ocid: string;
  title: string;
  status: string;
  procurement_method: string | null;
  buyer_name: string | null;
  buyer_idno: string | null;
  value_amount: number | null;
  value_currency: string | null;
  published_date: string | null;
  created_at: string;
}

export interface Accreditation {
  id: string;
  organization_name: string;
  director_name: string | null;
  certificate_number: string;
  category: string;
  standard: string;
  status: string;
  issue_date: string | null;
  expiry_date: string | null;
  scope: string | null;
  country_code: string;
  created_at: string | null;
}

export interface ConnectedCompany {
  company_idno: string;
  company_name: string | null;
  company_status: string | null;
  company_id: string | null;
  roles: string[];
  ownership_percentage?: number | null;
  director_role?: string | null;
  is_current?: boolean;
}

export interface RelationshipPerson {
  person_id: string;
  person_name: string;
  person_idnp: string | null;
  roles_in_current: string[];
  connected_companies: ConnectedCompany[];
  total_companies: number;
  active_companies: number;
  liquidated_companies: number;
}

export interface CompanyRelationships {
  company: { id: string; idno: string; name_ro: string | null; status: string | null } | null;
  persons: RelationshipPerson[];
  total_persons: number;
  total_relationships: number;
}

export interface PersonDetail {
  person: { id: string; full_name: string; idnp: string | null; person_type: string; nationality: string | null };
  connected_companies: ConnectedCompany[];
  total_companies: number;
  active_companies: number;
  liquidated_companies: number;
}
