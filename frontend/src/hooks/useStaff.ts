import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE } from '@/lib/constants';
import { api } from '@/lib/api-client';
import type { StaffMember } from '@/types/staff';
import type { StaffFormData } from '@/components/staff/StaffFormModal';

export function useStaff() {
  const { data, error, isLoading, mutate } = useSWR<StaffMember[]>(
    `${API_BASE}/staff`,
    fetcher,
  );

  const createStaff = async (payload: StaffFormData) => {
    await api.post<StaffMember>('/staff', payload);
    await mutate();
  };

  const updateStaff = async (id: string, payload: Partial<StaffFormData>) => {
    await api.patch<StaffMember>(`/staff/${id}`, payload);
    await mutate();
  };

  return {
    data,
    isLoading,
    error,
    mutate,
    createStaff,
    updateStaff,
  };
}

export function usePropertyStaff(propertyId: string | undefined) {
  const { data, error, isLoading, mutate } = useSWR<StaffMember[]>(
    propertyId ? `${API_BASE}/properties/${propertyId}/staff` : null,
    fetcher,
  );

  return {
    data,
    isLoading,
    error,
    mutate,
  };
}
