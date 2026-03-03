'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import useSWR from 'swr';
import { fetcher } from '@/lib/fetcher';
import { API_BASE } from '@/lib/constants';
import { useStaffAssignments } from '@/hooks/useHousekeeping';
import CalendarHeader from '@/components/calendar/CalendarHeader';
import ShiftGrid from '@/components/housekeeping/ShiftGrid';
import Skeleton from '@/components/shared/Skeleton';
import ErrorBanner from '@/components/shared/ErrorBanner';
import type { StaffMember } from '@/types/staff';

function PhoneIcon({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 0 0 2.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 0 1-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 0 0-1.091-.852H4.5A2.25 2.25 0 0 0 2.25 4.5v2.25Z" />
    </svg>
  );
}

function EnvelopeIcon({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75" />
    </svg>
  );
}

export default function StaffDetailPage() {
  const params = useParams();
  const staffId = params.staffId as string;
  const [month, setMonth] = useState(() => new Date());

  const { data: staffMember, isLoading: staffLoading, error: staffError } = useSWR<StaffMember>(
    `${API_BASE}/staff/${staffId}`,
    fetcher,
  );
  const { data: assignments, isLoading: assignmentsLoading } = useStaffAssignments(staffId, month);

  if (staffError) {
    return (
      <div>
        <Link href="/staff" className="mb-4 inline-flex items-center gap-1 text-sm text-brand-500 transition-colors hover:text-brand-700">
          &larr; Personal
        </Link>
        <ErrorBanner message="Error al cargar detalles del personal." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <Link
        href="/staff"
        className="inline-flex items-center gap-1 text-sm text-brand-500 transition-colors hover:text-brand-700"
      >
        &larr; Personal
      </Link>

      {/* Header */}
      {staffLoading ? (
        <div className="rounded-card border border-brand-200 bg-white p-6 shadow-card">
          <Skeleton rows={2} className="h-5 w-64" />
        </div>
      ) : staffMember ? (
        <div className="rounded-card border border-brand-200 bg-white p-6 shadow-card">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-status-info-light">
              <span className="text-lg font-semibold text-status-info-dark">
                {staffMember.first_name[0]}{staffMember.last_name[0]}
              </span>
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="font-display text-2xl font-semibold text-brand-950">
                  {staffMember.first_name} {staffMember.last_name}
                </h1>
                <span
                  className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${
                    staffMember.is_active
                      ? 'bg-status-success-light text-status-success-dark'
                      : 'bg-brand-100 text-brand-600'
                  }`}
                >
                  {staffMember.is_active ? 'Activa' : 'Inactiva'}
                </span>
              </div>
              <div className="mt-1 flex items-center gap-4 text-sm text-brand-600">
                <span className="flex items-center gap-1.5">
                  <EnvelopeIcon className="h-3.5 w-3.5" />
                  {staffMember.email}
                </span>
                {staffMember.phone && (
                  <span className="flex items-center gap-1.5">
                    <PhoneIcon className="h-3.5 w-3.5" />
                    {staffMember.phone}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : null}

      {/* Shift Grid */}
      <div>
        <h2 className="mb-3 font-display text-lg font-semibold text-brand-950">
          Agenda de Turnos
        </h2>
        <CalendarHeader
          currentMonth={month}
          onPrevMonth={() => setMonth((m) => new Date(m.getFullYear(), m.getMonth() - 1, 1))}
          onNextMonth={() => setMonth((m) => new Date(m.getFullYear(), m.getMonth() + 1, 1))}
        />
        {assignmentsLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand-300 border-t-brand-950" />
          </div>
        ) : (
          <ShiftGrid mode="staff" assignments={assignments || []} currentMonth={month} />
        )}
      </div>
    </div>
  );
}
