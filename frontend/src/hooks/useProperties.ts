import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE, POLLING_INTERVALS } from '@/lib/constants';
import { api } from '@/lib/api-client';
import type { PropertyListItem } from '@/types/property';
import type { PropertyFormData } from '@/components/properties/PropertyFormModal';

export function useProperties() {
  const { data, error, isLoading, mutate } = useSWR<PropertyListItem[]>(
    `${API_BASE}/properties`,
    fetcher,
    { refreshInterval: POLLING_INTERVALS.DEFAULT },
  );

  const createProperty = async (payload: PropertyFormData) => {
    await api.post('/properties', payload);
    await mutate();
  };

  const updateProperty = async (id: string, payload: Partial<PropertyFormData>) => {
    await api.patch(`/properties/${id}`, payload);
    await mutate();
  };

  return {
    data,
    isLoading,
    error,
    mutate,
    createProperty,
    updateProperty,
  };
}
