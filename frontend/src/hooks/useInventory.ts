import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE } from '@/lib/constants';
import type { InventoryItem } from '@/types/inventory';

export function useInventory(propertyId: string | undefined) {
  const { data, error, isLoading, mutate } = useSWR<InventoryItem[]>(
    propertyId ? `${API_BASE}/properties/${propertyId}/inventory` : null,
    fetcher,
  );

  return {
    data,
    isLoading,
    error,
    mutate,
  };
}
