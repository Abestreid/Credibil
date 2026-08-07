import { useCallback, useEffect, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import api from '@/lib/api';
import type {
  ApiResponse,
  Company,
  SearchResponse,
  AutocompleteResponse,
  DashboardResponse,
  FinancialReport,
  CourtCase,
  Tender,
  Accreditation,
  CompanyRelationships,
  PersonDetail,
  EnforcementProceeding,
  EnforcementSummary,
  MonitoredCompany,
  MonitoringChangeEvent,
  MonitoringNotification,
} from '@/types';

export function useSearchParamsState<T extends Record<string, string>>(
  defaults: T
): [T, (updates: Partial<T>) => void] {
  const [searchParams, setSearchParams] = useSearchParams();

  const state = {} as T;
  for (const key of Object.keys(defaults) as (keyof T)[]) {
    state[key] = (searchParams.get(key as string) || defaults[key]) as T[keyof T];
  }

  const setState = useCallback(
    (updates: Partial<T>) => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev);
        for (const [k, v] of Object.entries(updates)) {
          if (v === undefined || v === null || v === defaults[k as keyof T]) {
            next.delete(k);
          } else {
            next.set(k, String(v));
          }
        }
        return next;
      });
    },
    [setSearchParams, defaults]
  );

  return [state, setState];
}

export function useCompanySearch(query: string, page = 1, pageSize = 20, enabled = true) {
  return useQuery<SearchResponse>({
    queryKey: ['search', 'companies', query, page, pageSize],
    queryFn: async () => {
      const res = await api.get<SearchResponse>('/search/companies', {
        params: { q: query, page, page_size: pageSize },
      });
      return res.data;
    },
    enabled,
    staleTime: 30_000,
  });
}

export function useCrossSearch(query: string, page = 1, pageSize = 20, enabled = true) {
  return useQuery<SearchResponse>({
    queryKey: ['search', 'all', query, page, pageSize],
    queryFn: async () => {
      const res = await api.get<SearchResponse>('/search', {
        params: { q: query, page, page_size: pageSize },
      });
      return res.data;
    },
    enabled,
    staleTime: 30_000,
  });
}

export function useAutocomplete(query: string, enabled = true) {
  return useQuery<AutocompleteResponse>({
    queryKey: ['autocomplete', query],
    queryFn: async () => {
      const res = await api.get<AutocompleteResponse>('/search/autocomplete', {
        params: { q: query, limit: 8 },
      });
      return res.data;
    },
    enabled,
    staleTime: 10_000,
  });
}

export function useDebouncedValue<T>(value: T, delay = 250): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debounced;
}

export function useCompanies(params: { page?: number; per_page?: number; search?: string } = {}) {
  return useQuery({
    queryKey: ['companies', params],
    queryFn: async () => {
      const res = await api.get<ApiResponse<Company[]>>('/companies', { params });
      return res.data;
    },
  });
}

export function useCompany(id: string | undefined) {
  return useQuery({
    queryKey: ['company', id],
    queryFn: async () => {
      const res = await api.get<ApiResponse<Company>>(`/companies/${id}`);
      return res.data;
    },
    enabled: !!id,
  });
}

export function useDashboard(idno: string | undefined) {
  return useQuery({
    queryKey: ['dashboard', idno],
    queryFn: async () => {
      const res = await api.get<ApiResponse<DashboardResponse>>(`/analytics/dashboard/${idno}`);
      return res.data;
    },
    enabled: !!idno,
  });
}

export function useFinancialReports(idno: string | undefined) {
  return useQuery({
    queryKey: ['financial', idno],
    queryFn: async () => {
      const res = await api.get<ApiResponse<FinancialReport[]>>('/financial', { params: { idno, limit: 50 } });
      return res.data;
    },
    enabled: !!idno,
    staleTime: 0,
    refetchOnMount: true,
    refetchOnWindowFocus: true,
  });
}

export function useCourtCases(idno: string | undefined) {
  return useQuery({
    queryKey: ['court', idno],
    queryFn: async () => {
      const res = await api.get<ApiResponse<CourtCase[]>>('/court/cases', { params: { idno, limit: 50 } });
      return res.data;
    },
    enabled: !!idno,
  });
}

export function useCourtAnalytics(idno: string | undefined) {
  return useQuery({
    queryKey: ['court-analytics', idno],
    queryFn: async () => {
      const res = await api.get<ApiResponse<Record<string, unknown>>>('/court/analytics', { params: { idno } });
      return res.data;
    },
    enabled: !!idno,
  });
}

export function useEnforcement(idno: string | undefined, state: 'active' | 'archived') {
  return useQuery({
    queryKey: ['enforcement', idno, state],
    queryFn: async () => {
      const res = await api.get<ApiResponse<EnforcementProceeding[]>>('/enforcement/proceedings', {
        params: { idno, state, limit: 100 },
      });
      return res.data;
    },
    enabled: !!idno,
  });
}

export function useEnforcementSummary(idno: string | undefined) {
  return useQuery({
    queryKey: ['enforcement-summary', idno],
    queryFn: async () => {
      const res = await api.get<ApiResponse<EnforcementSummary>>('/enforcement/summary', {
        params: { idno },
      });
      return res.data;
    },
    enabled: !!idno,
  });
}

export function useTendersByBuyer(idno: string | undefined) {
  return useQuery({
    queryKey: ['tenders', 'buyer', idno],
    queryFn: async () => {
      const res = await api.get<ApiResponse<Tender[]>>(`/tenders/by-buyer/${idno}`, { params: { limit: 50 } });
      return res.data;
    },
    enabled: !!idno,
  });
}

export function useTenderAnalytics(idno: string | undefined) {
  return useQuery({
    queryKey: ['tender-analytics', idno],
    queryFn: async () => {
      const res = await api.get<ApiResponse<Record<string, unknown>>>('/tenders/analytics', { params: { idno } });
      return res.data;
    },
    enabled: !!idno,
  });
}

export function useAccreditations(params: { keyword?: string; category?: string; limit?: number } = {}) {
  return useQuery({
    queryKey: ['accreditations', params],
    queryFn: async () => {
      const res = await api.get<ApiResponse<Accreditation[]>>('/accreditations', { params });
      return res.data;
    },
  });
}

export function useSearchHealth() {
  return useQuery({
    queryKey: ['search-health'],
    queryFn: async () => {
      const res = await api.get<{ search_healthy: boolean }>('/search/health');
      return res.data;
    },
    refetchInterval: 30_000,
  });
}

export function useCompanyRelationships(idno: string | undefined) {
  return useQuery({
    queryKey: ['relationships', 'company', idno],
    queryFn: async () => {
      const res = await api.get<ApiResponse<CompanyRelationships>>(`/relationship/company/${idno}`);
      return res.data;
    },
    enabled: !!idno,
  });
}

export function usePersonDetail(personId: string | undefined) {
  return useQuery({
    queryKey: ['person', personId],
    queryFn: async () => {
      const res = await api.get<ApiResponse<PersonDetail>>(`/relationship/person/${personId}`);
      return res.data;
    },
    enabled: !!personId,
  });
}

export function useCheckTaxDebt(companyId: string | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const res = await api.post<{ status: string; task_id: string }>(
        `/companies/${companyId}/tax-debt`
      );
      return res.data;
    },
    onSuccess: () => {
      if (companyId) {
        queryClient.invalidateQueries({ queryKey: ['company', companyId] });
      }
    },
  });
}

// ---------------------------------------------------------------- monitoring
export function useMonitoredCompanies() {
  return useQuery({
    queryKey: ['monitoring', 'companies'],
    queryFn: async () => {
      const res = await api.get<ApiResponse<MonitoredCompany[]>>('/monitoring/companies');
      return res.data;
    },
  });
}

export function useAddMonitoring() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (idno: string) => {
      const res = await api.post<ApiResponse<MonitoredCompany>>('/monitoring/companies', { idno });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring'] });
    },
  });
}

export function useRemoveMonitoring() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (idno: string) => {
      const res = await api.delete<ApiResponse<{ removed: boolean }>>(`/monitoring/companies/${idno}`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring'] });
    },
  });
}

export function useCompanyChanges(idno: string | undefined) {
  return useQuery({
    queryKey: ['monitoring', 'changes', idno],
    queryFn: async () => {
      const res = await api.get<ApiResponse<MonitoringChangeEvent[]>>(
        `/monitoring/companies/${idno}/changes`,
        { params: { limit: 200 } },
      );
      return res.data;
    },
    enabled: !!idno,
  });
}

export function useNotifications(unreadOnly = false) {
  return useQuery({
    queryKey: ['monitoring', 'notifications', unreadOnly],
    queryFn: async () => {
      const res = await api.get<ApiResponse<MonitoringNotification[]>>('/monitoring/notifications', {
        params: { unread_only: unreadOnly, limit: 100 },
      });
      return res.data;
    },
  });
}

export function useUnreadCount() {
  return useQuery({
    queryKey: ['monitoring', 'unread'],
    queryFn: async () => {
      const res = await api.get<ApiResponse<{ unread: number }>>('/monitoring/notifications/unread-count');
      return res.data;
    },
    refetchInterval: 60_000,
  });
}

export function useMarkAllNotificationsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const res = await api.post<ApiResponse<{ marked: number }>>('/monitoring/notifications/read-all');
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring'] });
    },
  });
}

export function useMarkNotificationRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await api.post<ApiResponse<{ read: boolean }>>(`/monitoring/notifications/${id}/read`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring'] });
    },
  });
}
