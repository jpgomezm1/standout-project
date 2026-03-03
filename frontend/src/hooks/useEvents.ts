import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE, POLLING_INTERVALS } from '@/lib/constants';
import type { OperationalEvent, EventType } from '@/types/event';

interface UseEventsOptions {
  property_id?: string;
  event_type?: EventType;
  since?: string;
  limit?: number;
}

function buildUrl(options?: UseEventsOptions): string {
  const params = new URLSearchParams();

  if (options?.property_id) params.set('property_id', options.property_id);
  if (options?.event_type) params.set('event_type', options.event_type);
  if (options?.since) params.set('since', options.since);
  if (options?.limit) params.set('limit', String(options.limit));

  const qs = params.toString();
  return `${API_BASE}/events${qs ? `?${qs}` : ''}`;
}

export function useEvents(options?: UseEventsOptions) {
  const { data, error, isLoading, mutate } = useSWR<OperationalEvent[]>(
    buildUrl(options),
    fetcher,
    { refreshInterval: POLLING_INTERVALS.EVENTS },
  );

  return {
    data,
    isLoading,
    error,
    mutate,
  };
}
