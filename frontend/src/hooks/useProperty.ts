import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE } from '@/lib/constants';
import type { PropertySummary } from '@/types/property';

export function useProperty(propertyId: string | undefined) {
  const { data, error, isLoading, mutate } = useSWR<PropertySummary>(
    propertyId ? `${API_BASE}/properties/${propertyId}` : null,
    fetcher,
  );

  return {
    data,
    isLoading,
    error,
    mutate,
  };
}
