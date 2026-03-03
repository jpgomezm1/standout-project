import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE } from '@/lib/constants';
import type { StaffMember } from '@/types/staff';

export function useStaff() {
  const { data, error, isLoading, mutate } = useSWR<StaffMember[]>(
    `${API_BASE}/staff`,
    fetcher,
  );

  return {
    data,
    isLoading,
    error,
    mutate,
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
