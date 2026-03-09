import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE, POLLING_INTERVALS } from '@/lib/constants';
import type { DashboardSummary } from '@/types/dashboard';

export function useDashboard() {
  const { data, error, isLoading, mutate } = useSWR<DashboardSummary>(
    `${API_BASE}/dashboard/summary`,
    fetcher,
    { refreshInterval: POLLING_INTERVALS.INCIDENTS },
  );

  return {
    data,
    isLoading,
    error,
    mutate,
  };
}
