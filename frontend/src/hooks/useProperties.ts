import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE, POLLING_INTERVALS } from '@/lib/constants';
import type { PropertyListItem } from '@/types/property';

export function useProperties() {
  const { data, error, isLoading, mutate } = useSWR<PropertyListItem[]>(
    `${API_BASE}/properties`,
    fetcher,
    { refreshInterval: POLLING_INTERVALS.DEFAULT },
  );

  return {
    data,
    isLoading,
    error,
    mutate,
  };
}
