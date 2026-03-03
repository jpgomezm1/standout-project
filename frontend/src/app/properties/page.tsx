'use client';

import { useRouter } from 'next/navigation';
import { useProperties } from '@/hooks/useProperties';
import PageHeader from '@/components/layout/PageHeader';
import DataTable, { Column } from '@/components/data/DataTable';
import ErrorBanner from '@/components/shared/ErrorBanner';
import { TableSkeleton } from '@/components/shared/Skeleton';
import type { PropertyListItem } from '@/types/property';

const columns: Column<PropertyListItem>[] = [
  {
    key: 'name',
    header: 'Nombre',
    render: (p) => (
      <span className="font-medium text-brand-950">{p.name}</span>
    ),
  },
  {
    key: 'is_active',
    header: 'Estado',
    render: (p) => (
      <span
        className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${
          p.is_active
            ? 'bg-status-success-light text-status-success-dark'
            : 'bg-brand-100 text-brand-600'
        }`}
      >
        {p.is_active ? 'Activa' : 'Inactiva'}
      </span>
    ),
  },
  {
    key: 'property_manager',
    header: 'PM',
    render: (p) => (
      <span className="text-sm text-brand-700">
        {p.property_manager || '—'}
      </span>
    ),
  },
  {
    key: 'housekeepers_needed',
    header: 'Housekeepers',
    render: (p) => (
      <span className="inline-flex items-center rounded-pill bg-status-info-light px-2.5 py-0.5 text-xs font-medium text-status-info-dark">
        {p.housekeepers_needed} necesarias
      </span>
    ),
  },
];

export default function PropertiesPage() {
  const router = useRouter();
  const { data: properties, isLoading, error, mutate } = useProperties();

  return (
    <div>
      <PageHeader
        title="Propiedades"
        subtitle="Vista general de todas las propiedades gestionadas"
      />

      {error && (
        <div className="mb-4">
          <ErrorBanner
            message="Error al cargar propiedades. Intenta de nuevo."
            onRetry={() => mutate()}
          />
        </div>
      )}

      {isLoading ? (
        <TableSkeleton rows={5} cols={4} />
      ) : (
        <DataTable<PropertyListItem>
          columns={columns}
          data={properties || []}
          onRowClick={(property) => router.push(`/properties/${property.id}`)}
          emptyMessage="No se encontraron propiedades"
        />
      )}
    </div>
  );
}
