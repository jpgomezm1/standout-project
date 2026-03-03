import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE } from '@/lib/constants';
import type { LaundryFlow } from '@/types/laundry';

export function useLaundry(propertyId: string | undefined) {
  const { data, error, isLoading, mutate } = useSWR<LaundryFlow[]>(
    propertyId ? `${API_BASE}/properties/${propertyId}/laundry` : null,
    fetcher,
  );

  return {
    data,
    isLoading,
    error,
    mutate,
  };
}
