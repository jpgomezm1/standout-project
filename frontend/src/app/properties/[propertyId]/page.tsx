'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useProperty } from '@/hooks/useProperty';
import { useIncidents } from '@/hooks/useIncidents';
import { useEvents } from '@/hooks/useEvents';
import { usePropertyStaff } from '@/hooks/useStaff';
import { usePropertyAssignments } from '@/hooks/useHousekeeping';
import { usePropertyConditionReports } from '@/hooks/useConditionReports';
import DataTable, { Column } from '@/components/data/DataTable';
import StatusBadge from '@/components/status/StatusBadge';
import SeverityIndicator from '@/components/status/SeverityIndicator';
import EventTimeline from '@/components/timeline/EventTimeline';
import CalendarHeader from '@/components/calendar/CalendarHeader';
import ShiftGrid from '@/components/housekeeping/ShiftGrid';
import ErrorBanner from '@/components/shared/ErrorBanner';
import { TableSkeleton } from '@/components/shared/Skeleton';
import Skeleton from '@/components/shared/Skeleton';
import RelativeTime from '@/components/shared/RelativeTime';
import type { Incident } from '@/types/incident';

/* ── helpers ─────────────────────────────────────────────── */

const PROPERTY_TYPE_LABELS: Record<string, string> = {
  penthouse: 'Penthouse',
  suite: 'Suite',
  apartment: 'Apartamento',
  studio: 'Studio',
  house: 'Casa',
  loft: 'Loft',
};

function getPropertyMeta(metadata: Record<string, unknown>) {
  return {
    type: PROPERTY_TYPE_LABELS[(metadata?.property_type as string) || ''] || null,
    city: (metadata?.city as string) || null,
    maxGuests: (metadata?.max_guests as number) || null,
  };
}

/* ── incident table columns ──────────────────────────────── */

const incidentColumns: Column<Incident>[] = [
  {
    key: 'title',
    header: 'Título',
    render: (i) => (
      <span className="font-medium text-text-primary">{i.title}</span>
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
    render: (i) => <StatusBadge status={i.status} />,
  },
  {
    key: 'created_at',
    header: 'Creado',
    render: (i) => <RelativeTime dateString={i.created_at} />,
  },
];

/* ── SVG icons (inline, heroicons outline) ───────────────── */

function CalendarIcon({ className = 'h-5 w-5' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5A2.25 2.25 0 0 1 5.25 9h13.5A2.25 2.25 0 0 1 21 11.25v7.5" />
    </svg>
  );
}

function BoxIcon({ className = 'h-5 w-5' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="m20.25 7.5-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125Z" />
    </svg>
  );
}

function ShirtIcon({ className = 'h-5 w-5' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 10.5V6a3.75 3.75 0 1 0-7.5 0v4.5m11.356-1.993 1.263 12c.07.665-.45 1.243-1.119 1.243H4.25a1.125 1.125 0 0 1-1.12-1.243l1.264-12A1.125 1.125 0 0 1 5.513 7.5h12.974c.576 0 1.059.435 1.119 1.007ZM8.625 10.5a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm7.5 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Z" />
    </svg>
  );
}

function ExclamationIcon({ className = 'h-5 w-5' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
    </svg>
  );
}

function AlertIcon({ className = 'h-5 w-5' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
    </svg>
  );
}

function UserIcon({ className = 'h-5 w-5' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
    </svg>
  );
}

function ChevronRightIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="h-4 w-4">
      <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
    </svg>
  );
}

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

function MapPinIcon({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z" />
    </svg>
  );
}

function UsersIcon({ className = 'h-4 w-4' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
    </svg>
  );
}

/* ── page ─────────────────────────────────────────────────── */

export default function PropertyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const propertyId = params.propertyId as string;
  const [hkMonth, setHkMonth] = useState(() => new Date());

  const { data: property, isLoading: propertyLoading, error: propertyError } = useProperty(propertyId);
  const { data: incidents, isLoading: incidentsLoading } = useIncidents({ property_id: propertyId, status: 'open' });
  const { data: events, isLoading: eventsLoading } = useEvents({ property_id: propertyId, limit: 15 });
  const { data: staffList, isLoading: staffLoading } = usePropertyStaff(propertyId);
  const { data: hkAssignments, isLoading: hkLoading } = usePropertyAssignments(propertyId, hkMonth);
  const { data: conditionReports, isLoading: crLoading } = usePropertyConditionReports(propertyId);

  const propertyManager = staffList?.find((s) => s.role === 'property_manager') || null;

  if (propertyError) {
    return (
      <div>
        <Link href="/properties" className="mb-4 inline-flex items-center gap-1 text-sm text-text-muted transition-colors hover:text-text-secondary">
          &larr; Propiedades
        </Link>
        <ErrorBanner message="Error al cargar los detalles de la propiedad." onRetry={() => router.refresh()} />
      </div>
    );
  }

  const meta = property ? getPropertyMeta(property.metadata) : null;

  return (
    <div className="space-y-6">
      {/* ── Breadcrumb ───────────────────────────────────── */}
      <Link
        href="/properties"
        className="inline-flex items-center gap-1 text-sm text-text-muted transition-colors hover:text-text-secondary"
      >
        &larr; Propiedades
      </Link>

      {/* ── Property Header ──────────────────────────────── */}
      {propertyLoading ? (
        <div className="rounded-card border border-card-border bg-white p-6 shadow-card">
          <Skeleton rows={3} className="h-5 w-72" />
        </div>
      ) : property ? (
        <div className="rounded-card border border-card-border bg-white p-6 shadow-card">
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3">
                <h1 className="font-display text-2xl font-semibold text-text-primary">
                  {property.name}
                </h1>
                <span
                  className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${
                    property.is_active
                      ? 'bg-badge-resolved-bg text-badge-resolved-text'
                      : 'bg-indigo-subtle text-text-secondary'
                  }`}
                >
                  {property.is_active ? 'Activa' : 'Inactiva'}
                </span>
              </div>

              {/* Metadata chips */}
              <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-text-muted">
                {property.address && (
                  <span className="inline-flex items-center gap-1">
                    <MapPinIcon />
                    {property.address}
                  </span>
                )}
                {meta?.type && (
                  <span className="inline-flex items-center gap-1 rounded-pill bg-indigo-subtle px-2.5 py-0.5 text-xs font-medium text-text-secondary">
                    {meta.type}
                  </span>
                )}
                {meta?.maxGuests && (
                  <span className="inline-flex items-center gap-1">
                    <UsersIcon />
                    Hasta {meta.maxGuests} huéspedes
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Current guest banner */}
          {property.current_guest && (
            <div className="mt-4 flex items-center gap-3 rounded-card bg-badge-resolved-bg px-4 py-3">
              <UserIcon className="h-5 w-5 text-badge-resolved-text" />
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-badge-resolved-text">
                  Huésped actual
                </p>
                <p className="text-sm font-semibold text-badge-resolved-text">
                  {property.current_guest}
                </p>
              </div>
            </div>
          )}
        </div>
      ) : null}

      {/* ── KPI Stats ────────────────────────────────────── */}
      {propertyLoading ? (
        <div className="grid grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="rounded-card border border-card-border bg-white p-5 shadow-card">
              <Skeleton rows={2} className="h-4 w-20" />
            </div>
          ))}
        </div>
      ) : property ? (
        <div className="grid grid-cols-4 gap-4">
          {/* Reservas próximas */}
          <Link
            href={`/properties/${propertyId}/reservations`}
            className="rounded-card border border-card-border bg-white p-5 shadow-card transition-all hover:border-indigo-300 hover:shadow-card-hover"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-card bg-indigo-subtle">
                <CalendarIcon className="h-5 w-5 text-indigo-300" />
              </div>
              <div>
                <p className="text-2xl font-semibold text-indigo-300">
                  {property.upcoming_reservations}
                </p>
                <p className="text-xs text-text-muted">Reservas próximas</p>
              </div>
            </div>
          </Link>

          {/* Incidentes activos */}
          <Link
            href="/incidents"
            className="rounded-card border border-card-border bg-white p-5 shadow-card transition-all hover:border-indigo-300 hover:shadow-card-hover"
          >
            <div className="flex items-center gap-3">
              <div className={`flex h-10 w-10 items-center justify-center rounded-card ${
                property.active_incidents > 0 ? 'bg-badge-danger-bg' : 'bg-indigo-subtle'
              }`}>
                <ExclamationIcon className={`h-5 w-5 ${
                  property.active_incidents > 0 ? 'text-badge-danger-text' : 'text-text-muted'
                }`} />
              </div>
              <div>
                <p className={`text-2xl font-semibold ${
                  property.active_incidents > 0 ? 'text-badge-danger-text' : 'text-text-primary'
                }`}>
                  {property.active_incidents}
                </p>
                <p className="text-xs text-text-muted">Incidentes activos</p>
              </div>
            </div>
          </Link>

          {/* Ítems en lavandería */}
          <Link
            href={`/properties/${propertyId}/laundry`}
            className="rounded-card border border-card-border bg-white p-5 shadow-card transition-all hover:border-indigo-300 hover:shadow-card-hover"
          >
            <div className="flex items-center gap-3">
              <div className={`flex h-10 w-10 items-center justify-center rounded-card ${
                property.items_in_laundry > 0 ? 'bg-badge-progress-bg' : 'bg-indigo-subtle'
              }`}>
                <ShirtIcon className={`h-5 w-5 ${
                  property.items_in_laundry > 0 ? 'text-badge-progress-text' : 'text-text-muted'
                }`} />
              </div>
              <div>
                <p className="text-2xl font-semibold text-text-primary">
                  {property.items_in_laundry}
                </p>
                <p className="text-xs text-text-muted">Ítems en lavandería</p>
              </div>
            </div>
          </Link>

          {/* Alertas de stock */}
          <Link
            href={`/properties/${propertyId}/inventory`}
            className="rounded-card border border-card-border bg-white p-5 shadow-card transition-all hover:border-indigo-300 hover:shadow-card-hover"
          >
            <div className="flex items-center gap-3">
              <div className={`flex h-10 w-10 items-center justify-center rounded-card ${
                property.low_stock_alerts > 0 ? 'bg-teal-subtle' : 'bg-indigo-subtle'
              }`}>
                <AlertIcon className={`h-5 w-5 ${
                  property.low_stock_alerts > 0 ? 'text-teal-600' : 'text-text-muted'
                }`} />
              </div>
              <div>
                <p className={`text-2xl font-semibold ${
                  property.low_stock_alerts > 0 ? 'text-teal-600' : 'text-text-primary'
                }`}>
                  {property.low_stock_alerts}
                </p>
                <p className="text-xs text-text-muted">Alertas de stock</p>
              </div>
            </div>
          </Link>
        </div>
      ) : null}

      {/* ── Equipo (Staff) ──────────────────────────────── */}
      {staffLoading ? (
        <div className="rounded-card border border-card-border bg-white p-6 shadow-card">
          <Skeleton rows={3} className="h-4 w-48" />
        </div>
      ) : (propertyManager || property) ? (
        <div className="rounded-card border border-card-border bg-white p-6 shadow-card">
          <div className="mb-4 flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-card bg-indigo-subtle">
              <UsersIcon className="h-4 w-4 text-text-secondary" />
            </div>
            <h2 className="font-display text-lg font-semibold text-text-primary">
              Equipo
            </h2>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {/* Property Manager */}
            {propertyManager && (
              <div className="rounded-card border border-card-border bg-slate-50 p-4">
                <p className="mb-2 text-xs font-medium uppercase tracking-wider text-text-muted">
                  Property Manager
                </p>
                <p className="font-medium text-text-primary">
                  {propertyManager.first_name} {propertyManager.last_name}
                </p>
                <div className="mt-2 space-y-1">
                  {propertyManager.phone && (
                    <p className="flex items-center gap-1.5 text-sm text-text-secondary">
                      <PhoneIcon className="h-3.5 w-3.5" />
                      {propertyManager.phone}
                    </p>
                  )}
                  <p className="flex items-center gap-1.5 text-sm text-text-secondary">
                    <EnvelopeIcon className="h-3.5 w-3.5" />
                    {propertyManager.email}
                  </p>
                </div>
              </div>
            )}

            {/* Housekeepers needed chip */}
            {property && (
              <div className="rounded-card border border-card-border bg-slate-50 p-4">
                <p className="mb-2 text-xs font-medium uppercase tracking-wider text-text-muted">
                  Housekeeping
                </p>
                <span className="inline-flex items-center rounded-pill bg-badge-progress-bg px-3 py-1 text-sm font-medium text-badge-progress-text">
                  {property.housekeepers_needed} housekeeper{property.housekeepers_needed !== 1 ? 's' : ''} necesaria{property.housekeepers_needed !== 1 ? 's' : ''}
                </span>
                <p className="mt-2 text-xs text-text-muted">
                  Se asignan del pool por disponibilidad
                </p>
              </div>
            )}
          </div>
        </div>
      ) : null}

      {/* ── Turnos de Housekeeping ───────────────────────── */}
      <div className="rounded-card border border-card-border bg-white p-6 shadow-card">
        <div className="mb-4 flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-card bg-badge-progress-bg">
            <CalendarIcon className="h-4 w-4 text-badge-progress-text" />
          </div>
          <h2 className="font-display text-lg font-semibold text-text-primary">
            Turnos de Housekeeping
          </h2>
        </div>
        <CalendarHeader
          currentMonth={hkMonth}
          onPrevMonth={() => setHkMonth((m) => new Date(m.getFullYear(), m.getMonth() - 1, 1))}
          onNextMonth={() => setHkMonth((m) => new Date(m.getFullYear(), m.getMonth() + 1, 1))}
        />
        {hkLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-card-border border-t-indigo-700" />
          </div>
        ) : (
          <ShiftGrid mode="property" assignments={hkAssignments || []} currentMonth={hkMonth} />
        )}
      </div>

      {/* ── Reportes de Condición ────────────────────────── */}
      <div className="rounded-card border border-card-border bg-white p-6 shadow-card">
        <div className="mb-4 flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-card bg-indigo-subtle">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="h-4 w-4 text-text-secondary">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15a2.25 2.25 0 0 1 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25Z" />
            </svg>
          </div>
          <h2 className="font-display text-lg font-semibold text-text-primary">
            Reportes de Condición
          </h2>
          {conditionReports && conditionReports.length > 0 && (
            <span className="inline-flex items-center rounded-pill bg-indigo-subtle px-2.5 py-0.5 text-xs font-medium text-text-secondary">
              {conditionReports.length}
            </span>
          )}
        </div>

        {crLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-card-border border-t-indigo-700" />
          </div>
        ) : conditionReports && conditionReports.length > 0 ? (
          <div className="space-y-3">
            {conditionReports.slice(0, 5).map((cr) => {
              const conditionStyles: Record<string, string> = {
                excellent: 'bg-badge-resolved-bg text-badge-resolved-text',
                good: 'bg-badge-progress-bg text-badge-progress-text',
                fair: 'bg-teal-subtle text-teal-600',
                poor: 'bg-badge-danger-bg text-badge-danger-text',
              };
              const conditionLabels: Record<string, string> = {
                excellent: 'Excelente',
                good: 'Buena',
                fair: 'Regular',
                poor: 'Mala',
              };
              return (
                <Link
                  key={cr.id}
                  href={`/condition-reports/${cr.id}`}
                  className="flex items-center justify-between rounded-card border border-card-border bg-slate-50 p-4 transition-all hover:border-indigo-300 hover:shadow-card-hover"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-text-primary">
                        {new Date(cr.created_at).toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' })}
                      </span>
                      <span className={`inline-flex items-center rounded-pill px-2 py-0.5 text-xs font-medium ${conditionStyles[cr.general_condition] || 'bg-indigo-subtle text-text-secondary'}`}>
                        {conditionLabels[cr.general_condition] || cr.general_condition}
                      </span>
                      {cr.events_created > 0 && (
                        <span className="inline-flex items-center rounded-pill bg-badge-danger-bg px-2 py-0.5 text-xs font-medium text-badge-danger-text">
                          {cr.events_created} evento{cr.events_created !== 1 ? 's' : ''}
                        </span>
                      )}
                    </div>
                    {cr.staff_name && (
                      <p className="mt-1 text-xs text-text-muted">Por: {cr.staff_name}</p>
                    )}
                    <p className="mt-1 line-clamp-1 text-xs text-text-muted">{cr.summary}</p>
                  </div>
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="h-4 w-4 text-text-muted">
                    <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                  </svg>
                </Link>
              );
            })}
          </div>
        ) : (
          <p className="py-4 text-center text-sm text-text-muted">
            Sin reportes de condición
          </p>
        )}
      </div>

      {/* ── Navigation Cards ─────────────────────────────── */}
      <div className="grid grid-cols-3 gap-4">
        <Link
          href={`/properties/${propertyId}/reservations`}
          className="group flex items-center gap-4 rounded-card border border-card-border bg-white p-5 shadow-card transition-all hover:border-indigo-300 hover:shadow-card-hover"
        >
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-card bg-slate-900 transition-transform group-hover:scale-105">
            <CalendarIcon className="h-6 w-6 text-white" />
          </div>
          <div className="flex-1">
            <p className="font-display text-sm font-semibold text-text-primary">Calendario</p>
            <p className="mt-0.5 text-xs text-text-muted">Reservas y disponibilidad</p>
          </div>
          <ChevronRightIcon />
        </Link>

        <Link
          href={`/properties/${propertyId}/inventory`}
          className="group flex items-center gap-4 rounded-card border border-card-border bg-white p-5 shadow-card transition-all hover:border-indigo-300 hover:shadow-card-hover"
        >
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-card bg-slate-900 transition-transform group-hover:scale-105">
            <BoxIcon className="h-6 w-6 text-white" />
          </div>
          <div className="flex-1">
            <p className="font-display text-sm font-semibold text-text-primary">Inventario</p>
            <p className="mt-0.5 text-xs text-text-muted">Stock y alertas de ítems</p>
          </div>
          <ChevronRightIcon />
        </Link>

        <Link
          href={`/properties/${propertyId}/laundry`}
          className="group flex items-center gap-4 rounded-card border border-card-border bg-white p-5 shadow-card transition-all hover:border-indigo-300 hover:shadow-card-hover"
        >
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-card bg-slate-900 transition-transform group-hover:scale-105">
            <ShirtIcon className="h-6 w-6 text-white" />
          </div>
          <div className="flex-1">
            <p className="font-display text-sm font-semibold text-text-primary">Lavandería</p>
            <p className="mt-0.5 text-xs text-text-muted">Flujos y devoluciones</p>
          </div>
          <ChevronRightIcon />
        </Link>
      </div>

      {/* ── Incidents + Events (two columns) ─────────────── */}
      <div className="grid grid-cols-5 gap-6">
        {/* Incidentes — wider */}
        <div className="col-span-3">
          <div className="mb-3 flex items-center gap-2">
            <h2 className="font-display text-lg font-semibold text-text-primary">
              Incidentes Activos
            </h2>
            {incidents && incidents.length > 0 && (
              <span className="inline-flex items-center rounded-pill bg-badge-danger-bg px-2.5 py-0.5 text-xs font-medium text-badge-danger-text">
                {incidents.length}
              </span>
            )}
          </div>
          {incidentsLoading ? (
            <TableSkeleton rows={3} cols={4} />
          ) : (
            <DataTable<Incident>
              columns={incidentColumns}
              data={incidents || []}
              emptyMessage="Sin incidentes activos"
            />
          )}
        </div>

        {/* Eventos recientes — narrower */}
        <div className="col-span-2">
          <h2 className="mb-3 font-display text-lg font-semibold text-text-primary">
            Eventos Recientes
          </h2>
          {eventsLoading ? (
            <div className="rounded-card border border-card-border bg-white p-6 shadow-card">
              <Skeleton rows={5} className="h-8 w-full" />
            </div>
          ) : (
            <EventTimeline events={events || []} />
          )}
        </div>
      </div>
    </div>
  );
}
