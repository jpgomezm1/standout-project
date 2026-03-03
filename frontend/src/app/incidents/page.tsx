'use client';

import { useState } from 'react';
import { useIncidents } from '@/hooks/useIncidents';
import { useProperties } from '@/hooks/useProperties';
import PageHeader from '@/components/layout/PageHeader';
import DataTable, { Column } from '@/components/data/DataTable';
import FilterBar from '@/components/data/FilterBar';
import StatusBadge from '@/components/status/StatusBadge';
import SeverityIndicator from '@/components/status/SeverityIndicator';
import ErrorBanner from '@/components/shared/ErrorBanner';
import { TableSkeleton } from '@/components/shared/Skeleton';
import RelativeTime from '@/components/shared/RelativeTime';
import { PRIORITY_ORDER } from '@/lib/constants';
import type { Incident, IncidentStatus, IncidentPriority } from '@/types/incident';

const columns: Column<Incident>[] = [
  {
    key: 'title',
    header: 'Título',
    render: (i) => (
      <span className="font-medium text-brand-950">{i.title}</span>
    ),
  },
  {
    key: 'property_id',
    header: 'Propiedad',
    render: (i) => (
      <span className="text-sm text-brand-600">{i.property_id}</span>
    ),
  },
  {
    key: 'incident_type',
    header: 'Tipo',
    render: (i) => (
      <span className="text-sm text-brand-600">{i.incident_type}</span>
    ),
  },
  {
    key: 'priority',
    header: 'Prioridad',
    render: (i) => <SeverityIndicator priority={i.priority} />,
  },
  {
    key: 'status',
    header: 'Estado',
    render: (i) => <StatusBadge status={i.status} />,
  },
  {
    key: 'created_at',
    header: 'Creado',
    render: (i) => <RelativeTime dateString={i.created_at} />,
  },
];

const STATUS_OPTIONS = [
  { value: '', label: 'Todos los Estados' },
  { value: 'open', label: 'Abierto' },
  { value: 'acknowledged', label: 'Reconocido' },
  { value: 'in_progress', label: 'En Progreso' },
  { value: 'resolved', label: 'Resuelto' },
];

const PRIORITY_OPTIONS = [
  { value: '', label: 'Todas las Prioridades' },
  { value: 'critical', label: 'Crítica' },
  { value: 'high', label: 'Alta' },
  { value: 'medium', label: 'Media' },
  { value: 'low', label: 'Baja' },
];

export default function IncidentsPage() {
  const [propertyFilter, setPropertyFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');

  const { data: properties } = useProperties();

  const { data: incidents, isLoading, error, mutate } = useIncidents({
    property_id: propertyFilter || undefined,
    status: (statusFilter as IncidentStatus) || undefined,
    priority: (priorityFilter as IncidentPriority) || undefined,
  });

  const propertyOptions = [
    { value: '', label: 'Todas las Propiedades' },
    ...(properties || []).map((p) => ({ value: p.id, label: p.name })),
  ];

  const sortedIncidents = incidents
    ? [...incidents].sort(
        (a, b) =>
          (PRIORITY_ORDER[a.priority] ?? 99) - (PRIORITY_ORDER[b.priority] ?? 99),
      )
    : [];

  const [expandedId, setExpandedId] = useState<string | null>(null);

  return (
    <div>
      <PageHeader
        title="Incidentes"
        subtitle="Monitoreo de incidentes en todas las propiedades"
      />

      <FilterBar
        filters={[
          {
            label: 'Propiedad',
            value: propertyFilter,
            options: propertyOptions,
            onChange: setPropertyFilter,
          },
          {
            label: 'Estado',
            value: statusFilter,
            options: STATUS_OPTIONS,
            onChange: setStatusFilter,
          },
          {
            label: 'Prioridad',
            value: priorityFilter,
            options: PRIORITY_OPTIONS,
            onChange: setPriorityFilter,
          },
        ]}
      />

      {error && (
        <div className="mb-4">
          <ErrorBanner
            message="Error al cargar incidentes."
            onRetry={() => mutate()}
          />
        </div>
      )}

      {isLoading ? (
        <TableSkeleton rows={6} cols={6} />
      ) : (
        <>
          <DataTable<Incident>
            columns={columns}
            data={sortedIncidents}
            onRowClick={(incident) =>
              setExpandedId(expandedId === incident.id ? null : incident.id)
            }
            emptyMessage="No se encontraron incidentes"
          />

          {expandedId && (
            <div className="mt-2 rounded-card border border-brand-200 bg-white p-6 shadow-card">
              {(() => {
                const incident = sortedIncidents.find((i) => i.id === expandedId);
                if (!incident) return null;
                return (
                  <div>
                    <div className="mb-3 flex items-center gap-3">
                      <h3 className="font-display text-lg font-semibold text-brand-950">
                        {incident.title}
                      </h3>
                      <SeverityIndicator priority={incident.priority} />
                      <StatusBadge status={incident.status} />
                    </div>
                    <p className="mb-4 text-sm text-brand-700">
                      {incident.description}
                    </p>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-brand-500">Tipo:</span>{' '}
                        <span className="text-brand-950">{incident.incident_type}</span>
                      </div>
                      <div>
                        <span className="font-medium text-brand-500">Reportado por:</span>{' '}
                        <span className="text-brand-950">{incident.reported_by || 'N/A'}</span>
                      </div>
                      <div>
                        <span className="font-medium text-brand-500">Asignado a:</span>{' '}
                        <span className="text-brand-950">{incident.assigned_to || 'Sin asignar'}</span>
                      </div>
                      <div>
                        <span className="font-medium text-brand-500">Creado:</span>{' '}
                        <span className="text-brand-950">
                          {new Date(incident.created_at).toLocaleString('es-CO')}
                        </span>
                      </div>
                      {incident.resolved_at && (
                        <div>
                          <span className="font-medium text-brand-500">Resuelto:</span>{' '}
                          <span className="text-brand-950">
                            {new Date(incident.resolved_at).toLocaleString('es-CO')}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })()}
            </div>
          )}
        </>
      )}
    </div>
  );
}
