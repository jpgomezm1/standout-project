'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { useIncidents } from '@/hooks/useIncidents';
import { useProperties } from '@/hooks/useProperties';
import { api } from '@/lib/api-client';
import PageHeader from '@/components/layout/PageHeader';
import DataTable, { Column } from '@/components/data/DataTable';
import FilterBar from '@/components/data/FilterBar';
import SeverityIndicator from '@/components/status/SeverityIndicator';
import ErrorBanner from '@/components/shared/ErrorBanner';
import { TableSkeleton } from '@/components/shared/Skeleton';
import { useToast } from '@/components/shared/Toast';
import RelativeTime from '@/components/shared/RelativeTime';
import { PRIORITY_ORDER, STATUS_COLORS, STATUS_LABELS } from '@/lib/constants';
import IncidentFormModal from '@/components/incidents/IncidentFormModal';
import type { IncidentFormData } from '@/components/incidents/IncidentFormModal';
import type { Incident, IncidentStatus, IncidentPriority } from '@/types/incident';

const INCIDENT_TYPE_LABELS: Record<string, string> = {
  broken_item: 'Ítem Roto',
  missing_item: 'Ítem Faltante',
  maintenance: 'Mantenimiento',
};

const ALL_INCIDENT_STATUSES: Array<{ value: string; label: string }> = [
  { value: 'open', label: 'Abierto' },
  { value: 'acknowledged', label: 'Reconocido' },
  { value: 'in_progress', label: 'En Progreso' },
  { value: 'resolved', label: 'Resuelto' },
];

function IncidentStatusDropdown({
  incidentId,
  currentStatus,
  onChangeStatus,
}: {
  incidentId: string;
  currentStatus: string;
  onChangeStatus: (incidentId: string, status: IncidentStatus) => void;
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

  const colorClasses = STATUS_COLORS[currentStatus] || 'bg-indigo-subtle text-indigo-700';
  const displayLabel = STATUS_LABELS[currentStatus] || currentStatus;

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
          {ALL_INCIDENT_STATUSES.map((s) => (
            <button
              key={s.value}
              onClick={(e) => {
                e.stopPropagation();
                if (s.value !== currentStatus) onChangeStatus(incidentId, s.value as IncidentStatus);
                setOpen(false);
              }}
              className={`flex w-full items-center gap-2 px-3 py-2 text-left text-sm transition hover:bg-slate-50 ${
                s.value === currentStatus ? 'font-medium text-indigo-700' : 'text-text-primary'
              }`}
            >
              <span className={`inline-block h-2 w-2 rounded-full ${STATUS_COLORS[s.value]?.split(' ')[1] || 'bg-slate-400'}`} />
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

function buildColumns(properties: { id: string; name: string }[], onChangeStatus: (id: string, status: IncidentStatus) => void): Column<Incident>[] {
  const propertyMap = new Map(properties.map((p) => [p.id, p.name]));

  return [
    {
      key: 'title',
      header: 'Título',
      render: (i) => (
        <span className="font-medium text-text-primary">{i.title}</span>
      ),
    },
    {
      key: 'property_id',
      header: 'Propiedad',
      render: (i) => (
        <span className="text-sm text-text-secondary">{propertyMap.get(i.property_id) ?? i.property_id}</span>
      ),
    },
    {
      key: 'incident_type',
      header: 'Tipo',
      render: (i) => (
        <span className="text-sm text-text-secondary">{INCIDENT_TYPE_LABELS[i.incident_type] ?? i.incident_type}</span>
      ),
    },
    {
      key: 'priority',
      header: 'Prioridad',
      headerClassName: 'text-center',
      cellClassName: 'text-center',
      render: (i) => <SeverityIndicator priority={i.priority} />,
    },
    {
      key: 'status',
      header: 'Estado',
      headerClassName: 'text-center',
      cellClassName: 'text-center',
      render: (i) => (
        <IncidentStatusDropdown
          incidentId={i.id}
          currentStatus={i.status}
          onChangeStatus={onChangeStatus}
        />
      ),
    },
    {
      key: 'created_at',
      header: 'Creado',
      render: (i) => <RelativeTime dateString={i.created_at} />,
    },
  ];
}

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

  const { toast } = useToast();
  const { data: properties } = useProperties();

  const { data: incidents, isLoading, error, mutate } = useIncidents({
    property_id: propertyFilter || undefined,
    status: (statusFilter as IncidentStatus) || undefined,
    priority: (priorityFilter as IncidentPriority) || undefined,
  });

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [updating, setUpdating] = useState(false);

  const propertyOptions = [
    { value: '', label: 'Todas las Propiedades' },
    ...(properties || []).map((p) => ({ value: p.id, label: p.name })),
  ];

  const handleStatusChange = useCallback(async (incidentId: string, newStatus: IncidentStatus) => {
    setUpdating(true);
    try {
      await api.patch(`/incidents/${incidentId}`, { status: newStatus });
      await mutate();
      const STATUS_TOAST: Record<string, string> = {
        acknowledged: 'Incidente reconocido',
        in_progress: 'Incidente en progreso',
        resolved: 'Incidente resuelto',
      };
      toast(STATUS_TOAST[newStatus] || 'Estado actualizado');
    } catch (err) {
      console.error('Error updating incident status:', err);
      toast('Error al actualizar estado', 'error');
    } finally {
      setUpdating(false);
    }
  }, [mutate, toast]);

  const columns = buildColumns(properties || [], handleStatusChange);

  const sortedIncidents = incidents
    ? [...incidents].sort(
        (a, b) =>
          (PRIORITY_ORDER[a.priority] ?? 99) - (PRIORITY_ORDER[b.priority] ?? 99),
      )
    : [];

  const handleCreateIncident = async (data: IncidentFormData) => {
    await api.post('/incidents', data);
    await mutate();
    toast('Incidente creado exitosamente');
  };

  return (
    <div>
      <PageHeader
        title="Incidentes"
        subtitle="Monitoreo de incidentes en todas las propiedades"
        actions={
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-900/90"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-4 w-4">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            Nuevo Incidente
          </button>
        }
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
            <div className="mt-2 rounded-card border border-card-border bg-white p-6 shadow-card">
              {(() => {
                const incident = sortedIncidents.find((i) => i.id === expandedId);
                if (!incident) return null;
                return (
                  <div>
                    <div className="mb-3 flex items-center gap-3">
                      <h3 className="font-display text-lg font-semibold text-text-primary">
                        {incident.title}
                      </h3>
                      <SeverityIndicator priority={incident.priority} />
                      <span className={`inline-flex rounded-pill px-3 py-0.5 text-xs font-medium ${STATUS_COLORS[incident.status] || ''}`}>
                        {STATUS_LABELS[incident.status] || incident.status}
                      </span>
                    </div>
                    <p className="mb-4 text-sm text-text-secondary">
                      {incident.description}
                    </p>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-text-muted">Tipo:</span>{' '}
                        <span className="text-text-primary">{INCIDENT_TYPE_LABELS[incident.incident_type] ?? incident.incident_type}</span>
                      </div>
                      <div>
                        <span className="font-medium text-text-muted">Reportado por:</span>{' '}
                        <span className="text-text-primary">{incident.reported_by || 'N/A'}</span>
                      </div>
                      <div>
                        <span className="font-medium text-text-muted">Asignado a:</span>{' '}
                        <span className="text-text-primary">{incident.assigned_to || 'Sin asignar'}</span>
                      </div>
                      <div>
                        <span className="font-medium text-text-muted">Creado:</span>{' '}
                        <span className="text-text-primary">
                          {new Date(incident.created_at).toLocaleString('es-CO')}
                        </span>
                      </div>
                      {incident.resolved_at && (
                        <div>
                          <span className="font-medium text-text-muted">Resuelto:</span>{' '}
                          <span className="text-text-primary">
                            {new Date(incident.resolved_at).toLocaleString('es-CO')}
                          </span>
                        </div>
                      )}
                    </div>

                    {incident.status !== 'resolved' && (
                      <div className="mt-4 flex gap-3 border-t border-card-border pt-4">
                        <span className="text-sm font-medium text-text-muted self-center">Cambiar estado:</span>
                        {incident.status === 'open' && (
                          <button
                            disabled={updating}
                            onClick={() => handleStatusChange(incident.id, 'acknowledged')}
                            className="rounded-lg bg-badge-acknowledged-bg px-3 py-1.5 text-sm font-medium text-badge-acknowledged-text transition hover:opacity-80 disabled:opacity-50"
                          >
                            Reconocer
                          </button>
                        )}
                        {(incident.status === 'open' || incident.status === 'acknowledged') && (
                          <button
                            disabled={updating}
                            onClick={() => handleStatusChange(incident.id, 'in_progress')}
                            className="rounded-lg bg-badge-progress-bg px-3 py-1.5 text-sm font-medium text-badge-progress-text transition hover:opacity-80 disabled:opacity-50"
                          >
                            En Progreso
                          </button>
                        )}
                        <button
                          disabled={updating}
                          onClick={() => handleStatusChange(incident.id, 'resolved')}
                          className="rounded-lg bg-badge-resolved-bg px-3 py-1.5 text-sm font-medium text-badge-resolved-text transition hover:opacity-80 disabled:opacity-50"
                        >
                          Resolver
                        </button>
                      </div>
                    )}
                  </div>
                );
              })()}
            </div>
          )}
        </>
      )}

      {showCreateModal && (
        <IncidentFormModal
          onClose={() => setShowCreateModal(false)}
          onSave={handleCreateIncident}
        />
      )}
    </div>
  );
}
