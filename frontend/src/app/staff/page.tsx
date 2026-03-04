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
import { useToast } from '@/components/shared/Toast';
import StaffFormModal from '@/components/staff/StaffFormModal';
import type { StaffFormData } from '@/components/staff/StaffFormModal';
import type { StaffMember } from '@/types/staff';

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

function PencilIcon({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
    </svg>
  );
}

function PlusIcon({ className = 'h-5 w-5' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
    </svg>
  );
}

/* -- page ------------------------------------------------------------- */

export default function StaffPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { data: staff, isLoading, error, mutate, createStaff, updateStaff } = useStaff();
  const [globalMonth, setGlobalMonth] = useState(() => new Date());
  const { data: globalAssignments, isLoading: globalLoading } = useGlobalAssignments(globalMonth);

  const [showModal, setShowModal] = useState(false);
  const [editingStaff, setEditingStaff] = useState<StaffMember | null>(null);

  const propertyManagers = staff?.filter((s) => s.role === 'property_manager') || [];
  const housekeepers = staff?.filter((s) => s.role === 'housekeeper') || [];

  const handleCreate = () => {
    setEditingStaff(null);
    setShowModal(true);
  };

  const handleEdit = (member: StaffMember) => {
    setEditingStaff(member);
    setShowModal(true);
  };

  const handleToggleActive = async (member: StaffMember) => {
    await updateStaff(member.id, { is_active: !member.is_active });
    toast(member.is_active ? 'Personal desactivado' : 'Personal activado');
  };

  const handleSave = async (data: StaffFormData) => {
    if (editingStaff) {
      await updateStaff(editingStaff.id, data);
      toast('Personal actualizado');
    } else {
      await createStaff(data);
      toast('Personal creado exitosamente');
    }
  };

  /* -- Action column shared by both tables ---- */
  const actionsColumn: Column<StaffMember> = {
    key: 'actions',
    header: 'Acciones',
    render: (s) => (
      <div className="flex items-center gap-2">
        <button
          onClick={(e) => { e.stopPropagation(); handleEdit(s); }}
          title="Editar"
          className="rounded-lg p-1.5 text-text-muted transition-colors hover:bg-indigo-subtle hover:text-indigo-700"
        >
          <PencilIcon />
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); handleToggleActive(s); }}
          title={s.is_active ? 'Desactivar' : 'Activar'}
          className={`rounded-lg px-2.5 py-1 text-xs font-medium transition-colors ${
            s.is_active
              ? 'text-badge-danger-text hover:bg-badge-danger-bg'
              : 'text-badge-resolved-text hover:bg-badge-resolved-bg'
          }`}
        >
          {s.is_active ? 'Desactivar' : 'Activar'}
        </button>
      </div>
    ),
  };

  /* -- columns for Property Managers ------------------------------------ */
  const pmColumns: Column<StaffMember>[] = [
    {
      key: 'name',
      header: 'Nombre',
      render: (s) => (
        <span className="font-medium text-text-primary">
          {s.first_name} {s.last_name}
        </span>
      ),
    },
    {
      key: 'email',
      header: 'Email',
      render: (s) => (
        <span className="text-sm text-text-secondary">{s.email}</span>
      ),
    },
    {
      key: 'phone',
      header: 'Telefono',
      render: (s) => (
        <span className="text-sm text-text-secondary">{s.phone || '\u2014'}</span>
      ),
    },
    {
      key: 'is_active',
      header: 'Estado',
      render: (s) => (
        <span
          className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${
            s.is_active
              ? 'bg-badge-resolved-bg text-badge-resolved-text border border-badge-resolved-border'
              : 'bg-slate-50 text-text-secondary border border-card-border'
          }`}
        >
          {s.is_active ? 'Activo' : 'Inactivo'}
        </span>
      ),
    },
    actionsColumn,
  ];

  /* -- columns for Housekeepers ----------------------------------------- */
  const hkColumns: Column<StaffMember>[] = [
    {
      key: 'name',
      header: 'Nombre',
      render: (s) => (
        <span className="font-medium text-text-primary">
          {s.first_name} {s.last_name}
        </span>
      ),
    },
    {
      key: 'email',
      header: 'Email',
      render: (s) => (
        <span className="text-sm text-text-secondary">{s.email}</span>
      ),
    },
    {
      key: 'phone',
      header: 'Telefono',
      render: (s) => (
        <span className="text-sm text-text-secondary">{s.phone || '\u2014'}</span>
      ),
    },
    {
      key: 'is_active',
      header: 'Estado',
      render: (s) => (
        <span
          className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${
            s.is_active
              ? 'bg-badge-resolved-bg text-badge-resolved-text border border-badge-resolved-border'
              : 'bg-slate-50 text-text-secondary border border-card-border'
          }`}
        >
          {s.is_active ? 'Activo' : 'Inactivo'}
        </span>
      ),
    },
    actionsColumn,
  ];

  return (
    <div className="space-y-8">
      <PageHeader
        title="Personal"
        subtitle="Gestion de Property Managers y pool de Housekeepers"
        actions={
          <button
            onClick={handleCreate}
            className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-900/90"
          >
            <PlusIcon className="h-4 w-4" />
            Agregar Personal
          </button>
        }
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
          <div className="flex h-8 w-8 items-center justify-center rounded-card bg-indigo-subtle">
            <UsersIcon className="h-4 w-4 text-indigo-700" />
          </div>
          <h2 className="font-display text-lg font-semibold text-text-primary">
            Property Managers
          </h2>
          {!isLoading && (
            <span className="inline-flex items-center rounded-pill bg-indigo-subtle px-2.5 py-0.5 text-xs font-medium text-indigo-700">
              {propertyManagers.length}
            </span>
          )}
        </div>
        {isLoading ? (
          <TableSkeleton rows={2} cols={5} />
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
          <div className="flex h-8 w-8 items-center justify-center rounded-card bg-badge-progress-bg">
            <UsersIcon className="h-4 w-4 text-badge-progress-text" />
          </div>
          <h2 className="font-display text-lg font-semibold text-text-primary">
            Pool de Housekeepers
          </h2>
          {!isLoading && (
            <span className="inline-flex items-center rounded-pill bg-badge-progress-bg px-2.5 py-0.5 text-xs font-medium text-badge-progress-text">
              {housekeepers.length}
            </span>
          )}
        </div>
        {isLoading ? (
          <TableSkeleton rows={4} cols={5} />
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
          <div className="flex h-8 w-8 items-center justify-center rounded-card bg-badge-progress-bg">
            <CalendarIcon className="h-4 w-4 text-badge-progress-text" />
          </div>
          <h2 className="font-display text-lg font-semibold text-text-primary">
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
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-card-border border-t-indigo-700" />
          </div>
        ) : (
          <ShiftGrid mode="global" assignments={globalAssignments || []} currentMonth={globalMonth} />
        )}
      </div>

      {/* Staff Form Modal */}
      {showModal && (
        <StaffFormModal
          staff={editingStaff}
          onClose={() => setShowModal(false)}
          onSave={handleSave}
        />
      )}
    </div>
  );
}
