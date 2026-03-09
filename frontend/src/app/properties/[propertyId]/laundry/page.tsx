'use client';

import { useState, useRef, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useProperty } from '@/hooks/useProperty';
import { useLaundry } from '@/hooks/useLaundry';
import { useToast } from '@/components/shared/Toast';
import PageHeader from '@/components/layout/PageHeader';
import DataTable, { Column } from '@/components/data/DataTable';
import FilterBar from '@/components/data/FilterBar';
import ErrorBanner from '@/components/shared/ErrorBanner';
import { TableSkeleton } from '@/components/shared/Skeleton';
import { LAUNDRY_STATUS_COLORS, LAUNDRY_STATUS_LABELS } from '@/lib/constants';
import type { LaundryFlow, LaundryStatus } from '@/types/laundry';

const STATUS_OPTIONS: Array<{ value: string; label: string }> = [
  { value: '', label: 'Todos los Estados' },
  { value: 'sent', label: 'Enviado' },
  { value: 'in_progress', label: 'En Proceso' },
  { value: 'returned', label: 'Devuelto' },
  { value: 'partially_returned', label: 'Parcialmente Devuelto' },
  { value: 'lost', label: 'Perdido' },
];

const ALL_STATUSES: Array<{ value: string; label: string }> = [
  { value: 'sent', label: 'Enviado' },
  { value: 'in_progress', label: 'En Proceso' },
  { value: 'returned', label: 'Devuelto' },
  { value: 'partially_returned', label: 'Parcialmente Devuelto' },
  { value: 'lost', label: 'Perdido' },
];

function StatusDropdown({
  flowId,
  currentStatus,
  onChangeStatus,
}: {
  flowId: string;
  currentStatus: string;
  onChangeStatus: (flowId: string, status: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const btnRef = useRef<HTMLButtonElement>(null);
  const [pos, setPos] = useState({ top: 0, left: 0 });

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleOpen = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (btnRef.current) {
      const rect = btnRef.current.getBoundingClientRect();
      setPos({ top: rect.bottom + 4, left: rect.left });
    }
    setOpen(!open);
  };

  const colorClasses = LAUNDRY_STATUS_COLORS[currentStatus] || 'bg-indigo-subtle text-indigo-700';
  const displayLabel = LAUNDRY_STATUS_LABELS[currentStatus] || currentStatus;

  return (
    <div ref={ref} className="inline-block">
      <button
        ref={btnRef}
        onClick={handleOpen}
        className={`inline-flex items-center gap-1.5 rounded-pill px-3 py-0.5 text-xs font-medium cursor-pointer transition hover:opacity-80 ${colorClasses}`}
      >
        {displayLabel}
        <svg className="h-3 w-3 opacity-60" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
        </svg>
      </button>

      {open && (
        <div
          className="fixed z-50 w-48 rounded-card border border-card-border bg-white py-1 shadow-modal"
          style={{ top: pos.top, left: pos.left }}
        >
          {ALL_STATUSES.map((s) => (
            <button
              key={s.value}
              onClick={(e) => {
                e.stopPropagation();
                if (s.value !== currentStatus) onChangeStatus(flowId, s.value);
                setOpen(false);
              }}
              className={`flex w-full items-center gap-2 px-3 py-2 text-left text-sm transition hover:bg-slate-50 ${
                s.value === currentStatus ? 'font-medium text-indigo-700' : 'text-text-primary'
              }`}
            >
              <span className={`inline-block h-2 w-2 rounded-full ${LAUNDRY_STATUS_COLORS[s.value]?.split(' ')[1] || 'bg-slate-400'}`} />
              {s.label}
              {s.value === currentStatus && (
                <svg className="ml-auto h-4 w-4 text-indigo-700" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

export default function LaundryPage() {
  const params = useParams();
  const propertyId = params.propertyId as string;
  const [statusFilter, setStatusFilter] = useState('');
  const { toast } = useToast();

  const { data: property } = useProperty(propertyId);
  const { data: laundryFlows, isLoading, error, mutate, updateStatus } = useLaundry(propertyId);

  const propertyName = property?.name || 'Propiedad';

  const filteredFlows = laundryFlows
    ? statusFilter
      ? laundryFlows.filter((flow) => flow.status === (statusFilter as LaundryStatus))
      : laundryFlows
    : [];

  const handleStatusChange = async (flowId: string, newStatus: string) => {
    try {
      await updateStatus(flowId, newStatus);
      toast(`Estado actualizado a "${LAUNDRY_STATUS_LABELS[newStatus] || newStatus}"`);
    } catch {
      toast('Error al actualizar estado', 'error');
    }
  };

  const columns: Column<LaundryFlow>[] = [
    {
      key: 'items',
      header: 'Ítems',
      render: (flow) => (
        <span className="text-sm text-text-primary">
          {flow.items.map((item) => `${item.name || item.item_name} (${item.quantity})`).join(', ')}
        </span>
      ),
    },
    {
      key: 'total_pieces',
      header: 'Total Piezas',
      render: (flow) => (
        <span className="text-sm font-medium text-text-primary">{flow.total_pieces}</span>
      ),
    },
    {
      key: 'status',
      header: 'Estado',
      render: (flow) => (
        <StatusDropdown
          flowId={flow.id}
          currentStatus={flow.status}
          onChangeStatus={handleStatusChange}
        />
      ),
    },
    {
      key: 'sent_at',
      header: 'Fecha Envío',
      render: (flow) => (
        <span className="text-sm text-text-secondary">
          {new Date(flow.sent_at).toLocaleDateString('es-CO')}
        </span>
      ),
    },
    {
      key: 'returned_at',
      header: 'Fecha Devolución',
      render: (flow) => (
        <span className="text-sm text-text-secondary">
          {flow.returned_at
            ? new Date(flow.returned_at).toLocaleDateString('es-CO')
            : '-'}
        </span>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title={`Lavandería - ${propertyName}`}
        subtitle="Seguimiento de flujos de lavandería y devoluciones"
        actions={
          <Link
            href={`/properties/${propertyId}`}
            className="rounded-pill border border-card-border bg-white px-4 py-2 text-sm font-medium text-text-secondary transition-colors hover:border-indigo-300 hover:shadow-card"
          >
            Volver a Propiedad
          </Link>
        }
      />

      <FilterBar
        filters={[
          {
            label: 'Estado',
            value: statusFilter,
            options: STATUS_OPTIONS,
            onChange: setStatusFilter,
          },
        ]}
      />

      {error && (
        <div className="mb-4">
          <ErrorBanner
            message="Error al cargar datos de lavandería."
            onRetry={() => mutate()}
          />
        </div>
      )}

      {isLoading ? (
        <TableSkeleton rows={5} cols={5} />
      ) : (
        <DataTable<LaundryFlow>
          columns={columns}
          data={filteredFlows}
          emptyMessage="No se encontraron flujos de lavandería"
        />
      )}
    </div>
  );
}
