import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE } from '@/lib/constants';
import type { HousekeepingAssignment, StaffMember } from '@/types/staff';

/** Assignments for a single reservation */
export function useReservationAssignments(reservationId: string | undefined) {
  const { data, error, isLoading, mutate } = useSWR<HousekeepingAssignment[]>(
    reservationId
      ? `${API_BASE}/reservations/${reservationId}/housekeeping`
      : null,
    fetcher,
  );
  return { data, isLoading, error, mutate };
}

/** Assignments for a property in a month */
export function usePropertyAssignments(propertyId: string | undefined, month: Date) {
  const start = `${month.getFullYear()}-${String(month.getMonth() + 1).padStart(2, '0')}-01`;
  const lastDay = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate();
  const end = `${month.getFullYear()}-${String(month.getMonth() + 1).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;

  const { data, error, isLoading, mutate } = useSWR<HousekeepingAssignment[]>(
    propertyId
      ? `${API_BASE}/properties/${propertyId}/housekeeping-assignments?start=${start}&end=${end}`
      : null,
    fetcher,
  );
  return { data, isLoading, error, mutate };
}

/** Assignments for a staff member in a month */
export function useStaffAssignments(staffId: string | undefined, month: Date) {
  const start = `${month.getFullYear()}-${String(month.getMonth() + 1).padStart(2, '0')}-01`;
  const lastDay = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate();
  const end = `${month.getFullYear()}-${String(month.getMonth() + 1).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;

  const { data, error, isLoading, mutate } = useSWR<HousekeepingAssignment[]>(
    staffId
      ? `${API_BASE}/staff/${staffId}/housekeeping-assignments?start=${start}&end=${end}`
      : null,
    fetcher,
  );
  return { data, isLoading, error, mutate };
}

/** All assignments in a month (global view) */
export function useGlobalAssignments(month: Date) {
  const start = `${month.getFullYear()}-${String(month.getMonth() + 1).padStart(2, '0')}-01`;
  const lastDay = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate();
  const end = `${month.getFullYear()}-${String(month.getMonth() + 1).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;

  const { data, error, isLoading, mutate } = useSWR<HousekeepingAssignment[]>(
    `${API_BASE}/housekeeping-assignments?start=${start}&end=${end}`,
    fetcher,
  );
  return { data, isLoading, error, mutate };
}

/** Available housekeepers on a specific date */
export function useAvailableHousekeepers(date: string | undefined) {
  const { data, error, isLoading } = useSWR<StaffMember[]>(
    date ? `${API_BASE}/housekeeping-assignments/available?date=${date}` : null,
    fetcher,
  );
  return { data, isLoading, error };
}

/** Create a manual housekeeping assignment */
export async function createAssignment(body: {
  reservation_id: string;
  staff_id: string;
  scheduled_date: string;
  notes?: string;
}) {
  const res = await fetch(`${API_BASE}/housekeeping-assignments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error('Failed to create housekeeping assignment');
  }
  return res.json();
}

/** Delete a housekeeping assignment */
export async function deleteAssignment(assignmentId: string) {
  const res = await fetch(
    `${API_BASE}/housekeeping-assignments/${assignmentId}`,
    { method: 'DELETE' },
  );
  if (!res.ok) {
    throw new Error('Failed to delete housekeeping assignment');
  }
}
