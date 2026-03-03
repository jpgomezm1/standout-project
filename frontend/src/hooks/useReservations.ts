import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE, POLLING_INTERVALS } from '@/lib/constants';
import type { Reservation, ReservationStatus } from '@/types/reservation';

interface UseReservationsOptions {
  status?: ReservationStatus;
  from_date?: string;
  to_date?: string;
}

function buildUrl(propertyId: string, options?: UseReservationsOptions): string {
  const params = new URLSearchParams();

  if (options?.status) params.set('status', options.status);
  if (options?.from_date) params.set('from_date', options.from_date);
  if (options?.to_date) params.set('to_date', options.to_date);

  const qs = params.toString();
  return `${API_BASE}/properties/${propertyId}/reservations${qs ? `?${qs}` : ''}`;
}

export function useReservations(propertyId: string, options?: UseReservationsOptions) {
  const { data, error, isLoading, mutate } = useSWR<Reservation[]>(
    propertyId ? buildUrl(propertyId, options) : null,
    fetcher,
    { refreshInterval: POLLING_INTERVALS.DEFAULT },
  );

  return {
    data,
    isLoading,
    error,
    mutate,
  };
}
