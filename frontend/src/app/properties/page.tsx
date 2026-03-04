'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useProperties } from '@/hooks/useProperties';
import PageHeader from '@/components/layout/PageHeader';
import DataTable, { Column } from '@/components/data/DataTable';
import ErrorBanner from '@/components/shared/ErrorBanner';
import { TableSkeleton } from '@/components/shared/Skeleton';
import { useToast } from '@/components/shared/Toast';
import PropertyFormModal from '@/components/properties/PropertyFormModal';
import type { PropertyFormData } from '@/components/properties/PropertyFormModal';
import type { PropertyListItem } from '@/types/property';

function PlusIcon({ className = 'h-5 w-5' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
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

export default function PropertiesPage() {
  const router = useRouter();
  const { toast } = useToast();
  const { data: properties, isLoading, error, mutate, createProperty, updateProperty } = useProperties();

  const [search, setSearch] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingProperty, setEditingProperty] = useState<PropertyListItem | null>(null);

  const filteredProperties = (properties || []).filter((p) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return p.name.toLowerCase().includes(q) || p.address.toLowerCase().includes(q);
  });

  const handleCreate = () => {
    setEditingProperty(null);
    setShowModal(true);
  };

  const handleEdit = (property: PropertyListItem) => {
    setEditingProperty(property);
    setShowModal(true);
  };

  const handleSave = async (data: PropertyFormData) => {
    if (editingProperty) {
      await updateProperty(editingProperty.id, data);
      toast('Propiedad actualizada');
    } else {
      await createProperty(data);
      toast('Propiedad creada exitosamente');
    }
  };

  const columns: Column<PropertyListItem>[] = [
    {
      key: 'name',
      header: 'Nombre',
      render: (p) => (
        <span className="font-medium text-text-primary">{p.name}</span>
      ),
    },
    {
      key: 'is_active',
      header: 'Estado',
      render: (p) => (
        <span
          className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${
            p.is_active
              ? 'bg-badge-resolved-bg text-badge-resolved-text border border-badge-resolved-border'
              : 'bg-slate-50 text-text-secondary border border-card-border'
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
        <span className="text-sm text-text-secondary">
          {p.property_manager || '\u2014'}
        </span>
      ),
    },
    {
      key: 'housekeepers_needed',
      header: 'Housekeepers',
      render: (p) => (
        <span className="inline-flex items-center rounded-pill bg-badge-progress-bg px-2.5 py-0.5 text-xs font-medium text-badge-progress-text border border-badge-progress-border">
          {p.housekeepers_needed} necesarias
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Acciones',
      render: (p) => (
        <button
          onClick={(e) => { e.stopPropagation(); handleEdit(p); }}
          title="Editar"
          className="rounded-lg p-1.5 text-text-muted transition-colors hover:bg-slate-50 hover:text-text-secondary"
        >
          <PencilIcon />
        </button>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Propiedades"
        subtitle="Vista general de todas las propiedades gestionadas"
        actions={
          <button
            onClick={handleCreate}
            className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-900/90"
          >
            <PlusIcon className="h-4 w-4" />
            Nueva Propiedad
          </button>
        }
      />

      {/* Search */}
      <div className="mb-4">
        <div className="relative max-w-sm">
          <svg
            className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-text-muted"
            xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
          <input
            type="text"
            placeholder="Buscar por nombre o direccion..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-lg border border-[#D1D5DB] py-2 pl-9 pr-3 text-sm focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
          />
        </div>
      </div>

      {error && (
        <div className="mb-4">
          <ErrorBanner
            message="Error al cargar propiedades. Intenta de nuevo."
            onRetry={() => mutate()}
          />
        </div>
      )}

      {isLoading ? (
        <TableSkeleton rows={5} cols={5} />
      ) : (
        <DataTable<PropertyListItem>
          columns={columns}
          data={filteredProperties}
          onRowClick={(property) => router.push(`/properties/${property.id}`)}
          emptyMessage={search ? 'No se encontraron propiedades con esa busqueda' : 'No se encontraron propiedades'}
        />
      )}

      {showModal && (
        <PropertyFormModal
          property={editingProperty}
          onClose={() => setShowModal(false)}
          onSave={handleSave}
        />
      )}
    </div>
  );
}
