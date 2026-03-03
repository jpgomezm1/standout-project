import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE, POLLING_INTERVALS } from '@/lib/constants';
import type { Incident, IncidentStatus, IncidentPriority } from '@/types/incident';

interface UseIncidentsOptions {
  property_id?: string;
  status?: IncidentStatus;
  priority?: IncidentPriority;
}

function buildUrl(options?: UseIncidentsOptions): string {
  const params = new URLSearchParams();

  if (options?.property_id) params.set('property_id', options.property_id);
  if (options?.status) params.set('status', options.status);
  if (options?.priority) params.set('priority', options.priority);

  const qs = params.toString();
  return `${API_BASE}/incidents${qs ? `?${qs}` : ''}`;
}

export function useIncidents(options?: UseIncidentsOptions) {
  const { data, error, isLoading, mutate } = useSWR<Incident[]>(
    buildUrl(options),
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
