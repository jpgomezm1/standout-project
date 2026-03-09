import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { api } from '@/lib/api-client';
import { API_BASE } from '@/lib/constants';
import type { LaundryFlow } from '@/types/laundry';

export function useLaundry(propertyId: string | undefined) {
  const { data, error, isLoading, mutate } = useSWR<LaundryFlow[]>(
    propertyId ? `${API_BASE}/properties/${propertyId}/laundry` : null,
    fetcher,
  );

  const updateStatus = async (flowId: string, status: string) => {
    await api.patch(`/properties/${propertyId}/laundry/${flowId}`, { status });
    mutate();
  };

  return {
    data,
    isLoading,
    error,
    mutate,
    updateStatus,
  };
}
