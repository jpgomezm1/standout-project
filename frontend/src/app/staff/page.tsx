'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useStaff } from '@/hooks/useStaff';
import { useGlobalAssignments } from '@/hooks/useHousekeeping';
import PageHeader from '@/components/layout/PageHeader';
import DataTable, { Column } from '@/components/data/DataTable';
import CalendarHeader from '@/components/calendar/CalendarHeader';
import ShiftGrid from '@/components/housekeeping/ShiftGrid';
import ErrorBanner from '@/components/shared/ErrorBanner';
import { TableSkeleton } from '@/components/shared/Skeleton';
import type { StaffMember } from '@/types/staff';

/* -- columns for Property Managers ------------------------------------ */

const pmColumns: Column<StaffMember>[] = [
  {
    key: 'name',
    header: 'Nombre',
    render: (s) => (
      <span className="font-medium text-brand-950">
        {s.first_name} {s.last_name}
      </span>
    ),
  },
  {
    key: 'email',
    header: 'Email',
    render: (s) => (
      <span className="text-sm text-brand-600">{s.email}</span>
    ),
  },
  {
    key: 'phone',
    header: 'Teléfono',
    render: (s) => (
      <span className="text-sm text-brand-600">{s.phone || '—'}</span>
    ),
  },
  {
    key: 'is_active',
    header: 'Estado',
    render: (s) => (
      <span
        className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${
          s.is_active
            ? 'bg-status-success-light text-status-success-dark'
            : 'bg-brand-100 text-brand-600'
        }`}
      >
        {s.is_active ? 'Activo' : 'Inactivo'}
      </span>
    ),
  },
];

/* -- columns for Housekeepers ----------------------------------------- */

const hkColumns: Column<StaffMember>[] = [
  {
    key: 'name',
    header: 'Nombre',
    render: (s) => (
      <span className="font-medium text-brand-950">
        {s.first_name} {s.last_name}
      </span>
    ),
  },
  {
    key: 'email',
    header: 'Email',
    render: (s) => (
      <span className="text-sm text-brand-600">{s.email}</span>
    ),
  },
  {
    key: 'phone',
    header: 'Teléfono',
    render: (s) => (
      <span className="text-sm text-brand-600">{s.phone || '—'}</span>
    ),
  },
  {
    key: 'is_active',
    header: 'Estado',
    render: (s) => (
      <span
        className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${
          s.is_active
            ? 'bg-status-success-light text-status-success-dark'
            : 'bg-brand-100 text-brand-600'
        }`}
      >
        {s.is_active ? 'Activo' : 'Inactivo'}
      </span>
    ),
  },
];

/* -- SVG Icons -------------------------------------------------------- */

function UsersIcon({ className = 'h-5 w-5' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
    </svg>
  );
}

function CalendarIcon({ className = 'h-5 w-5' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5" />
    </svg>
  );
}

/* -- page ------------------------------------------------------------- */

export default function StaffPage() {
  const router = useRouter();
  const { data: staff, isLoading, error, mutate } = useStaff();
  const [globalMonth, setGlobalMonth] = useState(() => new Date());
  const { data: globalAssignments, isLoading: globalLoading } = useGlobalAssignments(globalMonth);

  const propertyManagers = staff?.filter((s) => s.role === 'property_manager') || [];
  const housekeepers = staff?.filter((s) => s.role === 'housekeeper') || [];

  return (
    <div className="space-y-8">
      <PageHeader
        title="Personal"
        subtitle="Gestión de Property Managers y pool de Housekeepers"
      />

      {error && (
        <div className="mb-4">
          <ErrorBanner
            message="Error al cargar personal. Intenta de nuevo."
            onRetry={() => mutate()}
          />
        </div>
      )}

      {/* Property Managers section */}
      <div>
        <div className="mb-3 flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-card bg-brand-100">
            <UsersIcon className="h-4 w-4 text-brand-700" />
          </div>
          <h2 className="font-display text-lg font-semibold text-brand-950">
            Property Managers
          </h2>
          {!isLoading && (
            <span className="inline-flex items-center rounded-pill bg-brand-100 px-2.5 py-0.5 text-xs font-medium text-brand-700">
              {propertyManagers.length}
            </span>
          )}
        </div>
        {isLoading ? (
          <TableSkeleton rows={2} cols={4} />
        ) : (
          <DataTable<StaffMember>
            columns={pmColumns}
            data={propertyManagers}
            emptyMessage="No hay Property Managers registrados"
          />
        )}
      </div>

      {/* Housekeepers Pool section */}
      <div>
        <div className="mb-3 flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-card bg-status-info-light">
            <UsersIcon className="h-4 w-4 text-status-info-dark" />
          </div>
          <h2 className="font-display text-lg font-semibold text-brand-950">
            Pool de Housekeepers
          </h2>
          {!isLoading && (
            <span className="inline-flex items-center rounded-pill bg-status-info-light px-2.5 py-0.5 text-xs font-medium text-status-info-dark">
              {housekeepers.length}
            </span>
          )}
        </div>
        {isLoading ? (
          <TableSkeleton rows={4} cols={4} />
        ) : (
          <DataTable<StaffMember>
            columns={hkColumns}
            data={housekeepers}
            onRowClick={(hk) => router.push(`/staff/${hk.id}`)}
            emptyMessage="No hay Housekeepers registrados"
          />
        )}
      </div>

      {/* Global Shift Grid */}
      <div>
        <div className="mb-3 flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-card bg-status-info-light">
            <CalendarIcon className="h-4 w-4 text-status-info-dark" />
          </div>
          <h2 className="font-display text-lg font-semibold text-brand-950">
            Parrilla Global de Turnos
          </h2>
        </div>
        <CalendarHeader
          currentMonth={globalMonth}
          onPrevMonth={() => setGlobalMonth((m) => new Date(m.getFullYear(), m.getMonth() - 1, 1))}
          onNextMonth={() => setGlobalMonth((m) => new Date(m.getFullYear(), m.getMonth() + 1, 1))}
        />
        {globalLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand-300 border-t-brand-950" />
          </div>
        ) : (
          <ShiftGrid mode="global" assignments={globalAssignments || []} currentMonth={globalMonth} />
        )}
      </div>
    </div>
  );
}
