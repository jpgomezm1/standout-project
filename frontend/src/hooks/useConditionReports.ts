import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE } from '@/lib/constants';
import type { ConditionReport } from '@/types/condition-report';

export function useConditionReports() {
  const { data, error, isLoading, mutate } = useSWR<ConditionReport[]>(
    `${API_BASE}/condition-reports`,
    fetcher,
  );

  return {
    data,
    isLoading,
    error,
    mutate,
  };
}

export function usePropertyConditionReports(propertyId: string | undefined) {
  const { data, error, isLoading, mutate } = useSWR<ConditionReport[]>(
    propertyId ? `${API_BASE}/properties/${propertyId}/condition-reports` : null,
    fetcher,
  );

  return {
    data,
    isLoading,
    error,
    mutate,
  };
}

export function useConditionReport(id: string | undefined) {
  const { data, error, isLoading, mutate } = useSWR<ConditionReport>(
    id ? `${API_BASE}/condition-reports/${id}` : null,
    fetcher,
  );

  return {
    data,
    isLoading,
    error,
    mutate,
  };
}
