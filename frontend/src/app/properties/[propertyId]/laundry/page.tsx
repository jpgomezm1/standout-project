'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useProperty } from '@/hooks/useProperty';
import { useLaundry } from '@/hooks/useLaundry';
import PageHeader from '@/components/layout/PageHeader';
import DataTable, { Column } from '@/components/data/DataTable';
import FilterBar from '@/components/data/FilterBar';
import ErrorBanner from '@/components/shared/ErrorBanner';
import { TableSkeleton } from '@/components/shared/Skeleton';
import { LAUNDRY_STATUS_COLORS, LAUNDRY_STATUS_LABELS } from '@/lib/constants';
import type { LaundryFlow, LaundryStatus } from '@/types/laundry';

const columns: Column<LaundryFlow>[] = [
  {
    key: 'items',
    header: 'Ítems',
    render: (flow) => (
      <span className="text-sm text-brand-950">
        {flow.items.map((item) => `${item.item_name} (${item.quantity})`).join(', ')}
      </span>
    ),
  },
  {
    key: 'total_pieces',
    header: 'Total Piezas',
    render: (flow) => (
      <span className="text-sm font-medium text-brand-950">{flow.total_pieces}</span>
    ),
  },
  {
    key: 'status',
    header: 'Estado',
    render: (flow) => {
      const colorClasses = LAUNDRY_STATUS_COLORS[flow.status] || 'bg-brand-100 text-brand-700';
      const displayLabel = LAUNDRY_STATUS_LABELS[flow.status] || flow.status.replace(/_/g, ' ');
      return (
        <span
          className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${colorClasses}`}
        >
          {displayLabel}
        </span>
      );
    },
  },
  {
    key: 'sent_at',
    header: 'Fecha Envío',
    render: (flow) => (
      <span className="text-sm text-brand-600">
        {new Date(flow.sent_at).toLocaleDateString('es-CO')}
      </span>
    ),
  },
  {
    key: 'expected_return_at',
    header: 'Fecha Devolución',
    render: (flow) => (
      <span className="text-sm text-brand-600">
        {flow.returned_at
          ? new Date(flow.returned_at).toLocaleDateString('es-CO')
          : flow.expected_return_at
            ? new Date(flow.expected_return_at).toLocaleDateString('es-CO')
            : '-'}
      </span>
    ),
  },
];

const STATUS_OPTIONS: Array<{ value: string; label: string }> = [
  { value: '', label: 'Todos los Estados' },
  { value: 'sent', label: 'Enviado' },
  { value: 'in_progress', label: 'En Proceso' },
  { value: 'returned', label: 'Devuelto' },
  { value: 'partially_returned', label: 'Parcialmente Devuelto' },
  { value: 'lost', label: 'Perdido' },
];

export default function LaundryPage() {
  const params = useParams();
  const propertyId = params.propertyId as string;
  const [statusFilter, setStatusFilter] = useState('');

  const { data: property } = useProperty(propertyId);
  const { data: laundryFlows, isLoading, error, mutate } = useLaundry(propertyId);

  const propertyName = property?.name || 'Propiedad';

  const filteredFlows = laundryFlows
    ? statusFilter
      ? laundryFlows.filter((flow) => flow.status === (statusFilter as LaundryStatus))
      : laundryFlows
    : [];

  return (
    <div>
      <PageHeader
        title={`Lavandería - ${propertyName}`}
        subtitle="Seguimiento de flujos de lavandería y devoluciones"
        actions={
          <Link
            href={`/properties/${propertyId}`}
            className="rounded-pill border border-brand-300 bg-white px-4 py-2 text-sm font-medium text-brand-700 transition-colors hover:border-brand-500 hover:shadow-card"
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
