'use client';

import { useMemo } from 'react';
import {
  PieChart, Pie, Cell, Tooltip,
  ResponsiveContainer, Legend,
} from 'recharts';
import { useDashboard } from '@/hooks/useDashboard';
import { useIncidents } from '@/hooks/useIncidents';
import { useProperties } from '@/hooks/useProperties';
import { useInventory } from '@/hooks/useInventory';
import PageHeader from '@/components/layout/PageHeader';
import ErrorBanner from '@/components/shared/ErrorBanner';
import RelativeTime from '@/components/shared/RelativeTime';
import { EVENT_TYPE_LABELS, EVENT_TYPE_COLORS } from '@/lib/constants';
import type { DashboardEvent } from '@/types/dashboard';
import type { Incident } from '@/types/incident';

/* ── Design System tokens (inline hex for charts/inline styles) ── */

const DS = {
  indigo900: '#1E3A8A',
  indigo700: '#3B4FE0',
  indigo300: '#A5B4FC',
  indigoSubtle: '#EEF2FF',
  teal600: '#0D9488',
  tealSubtle: '#CCFBF1',
  green500: '#22C55E',
  green600: '#16A34A',
  greenSubtle: '#F0FDF4',
  dangerText: '#DC2626',
  dangerBg: '#FEF2F2',
  slate50: '#F8FAFC',
  slate100: '#F1F5F9',
  slate200: '#E2E8F0',
  slate400: '#94A3B8',
  slate600: '#475569',
  slate900: '#0F172A',
  purpleText: '#7C3AED',
  purpleBg: '#F5F3FF',
} as const;

/* ── helpers ── */

function getDotColor(eventType: string): string {
  if (eventType.includes('BROKEN') || eventType.includes('MISSING') || eventType.includes('LOST')) return DS.teal600;
  if (eventType.includes('SENT') || eventType.includes('IN_PROGRESS')) return DS.indigo700;
  if (eventType.includes('RESOLVED') || eventType.includes('RETURNED') || eventType.includes('REPLACED')) return DS.green600;
  if (eventType.includes('LOW_STOCK') || eventType.includes('ALERT')) return DS.teal600;
  return DS.slate400;
}

function getEventDescription(event: DashboardEvent): string {
  const payload = event.payload;
  if (payload.description && typeof payload.description === 'string') return payload.description;
  if (payload.item_name && typeof payload.item_name === 'string') return `Item: ${payload.item_name}`;
  return EVENT_TYPE_LABELS[event.event_type] || event.event_type;
}

/* ── chart data builders ── */

const PRIORITY_COLORS: Record<string, string> = {
  critical: DS.indigo900,
  high: DS.indigo900,
  medium: DS.indigo700,
  low: DS.indigo300,
};

const PRIORITY_LABELS: Record<string, string> = {
  critical: 'Critico',
  high: 'Alto',
  medium: 'Medio',
  low: 'Bajo',
};

const STATUS_COLORS: Record<string, string> = {
  open: DS.indigo900,
  acknowledged: DS.indigo300,
  in_progress: DS.indigo700,
  resolved: DS.green500,
};

const STATUS_LABELS: Record<string, string> = {
  open: 'Abierto',
  acknowledged: 'Reconocido',
  in_progress: 'En progreso',
  resolved: 'Resuelto',
};

function buildPriorityData(incidents: Incident[]) {
  const counts: Record<string, number> = { critical: 0, high: 0, medium: 0, low: 0 };
  incidents.forEach((i) => { counts[i.priority] = (counts[i.priority] || 0) + 1; });
  return Object.entries(counts)
    .filter(([, v]) => v > 0)
    .map(([key, value]) => ({ name: PRIORITY_LABELS[key], value, color: PRIORITY_COLORS[key] }));
}

function buildStatusData(incidents: Incident[]) {
  const counts: Record<string, number> = { open: 0, acknowledged: 0, in_progress: 0, resolved: 0 };
  incidents.forEach((i) => { counts[i.status] = (counts[i.status] || 0) + 1; });
  return Object.entries(counts)
    .filter(([, v]) => v > 0)
    .map(([key, value]) => ({ name: STATUS_LABELS[key], value, color: STATUS_COLORS[key] }));
}

/* ── KPI Card (design system: colored top border) ── */

interface KpiCardProps {
  label: string;
  value: number;
  accent: string;
  numberColor?: string;
  href?: string;
}

function KpiCard({ label, value, accent, numberColor, href }: KpiCardProps) {
  const card = (
    <div
      className={`card-interactive overflow-hidden rounded-xl bg-card-bg shadow-card ${href ? 'cursor-pointer' : ''}`}
      style={{ borderTop: `3px solid ${accent}` }}
    >
      <div className="px-6 py-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-text-muted">{label}</p>
        <p className="mt-2 text-3xl font-bold" style={{ color: numberColor || accent }}>{value}</p>
      </div>
    </div>
  );

  return href ? <a href={href}>{card}</a> : card;
}

/* ── Custom tooltip ── */

function ChartTooltip({ active, payload, label }: { active?: boolean; payload?: { value: number; name: string }[]; label?: string }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-lg bg-card-bg px-3 py-2 text-sm shadow-card" style={{ border: `1px solid ${DS.slate200}` }}>
      {label && <p className="font-medium text-text-primary">{label}</p>}
      {payload.map((p, i) => (
        <p key={i} className="text-text-secondary">{p.name}: {p.value}</p>
      ))}
    </div>
  );
}

/* ── page ── */

export default function DashboardPage() {
  const { data, isLoading, error, mutate } = useDashboard();
  const { data: incidents } = useIncidents();
  const { data: properties } = useProperties();
  const firstPropertyId = properties?.[0]?.id;
  const { data: inventory } = useInventory(firstPropertyId);

  const activeIncidents = useMemo(() => (incidents || []).filter((i) => i.status !== 'resolved'), [incidents]);
  const recentIncidents = useMemo(() => (incidents || []).slice(0, 10), [incidents]);
  const priorityData = useMemo(() => buildPriorityData(activeIncidents), [activeIncidents]);
  const statusData = useMemo(() => buildStatusData(recentIncidents), [recentIncidents]);
  const itemsBelowExpected = useMemo(
    () => (inventory || []).filter((item) => item.current_quantity < item.expected_quantity),
    [inventory],
  );

  return (
    <div>
      <PageHeader title="Dashboard" subtitle="Resumen operativo en tiempo real" />

      {error && (
        <div className="mb-4">
          <ErrorBanner message="Error al cargar el dashboard. Intenta de nuevo." onRetry={() => mutate()} />
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-28 animate-pulse rounded-xl bg-slate-200" />
          ))}
        </div>
      ) : data ? (
        <>
          {/* KPI Cards — design system colors */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
            <div className="animate-fade-up">
              <KpiCard label="Propiedades" value={data.total_properties} accent={DS.indigo300} href="/properties" />
            </div>
            <div className="animate-fade-up-delay-1">
              <KpiCard label="Incidentes Activos" value={data.active_incidents} accent={DS.dangerText} numberColor={DS.dangerText} href="/incidents" />
            </div>
            <div className="animate-fade-up-delay-2">
              <KpiCard label="Incidentes Criticos" value={data.critical_incidents} accent={DS.slate400} numberColor={DS.slate400} href="/incidents" />
            </div>
            <div className="animate-fade-up-delay-3">
              <KpiCard label="Items en Lavanderia" value={data.items_in_laundry} accent={DS.indigo700} numberColor={DS.indigo700} />
            </div>
            <div className="animate-fade-up-delay-4">
              <KpiCard label="Alertas de Stock" value={data.low_stock_items} accent={DS.teal600} numberColor={DS.teal600} />
            </div>
          </div>

          {/* Charts Row */}
          <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-3 animate-fade-up-delay-2">
            {/* Pie — Incidents by Priority */}
            <div className="overflow-hidden rounded-xl bg-card-bg shadow-card">
              <h3 className="px-6 pt-6 text-sm font-semibold text-text-primary">Incidentes por Prioridad</h3>
              {priorityData.length > 0 ? (
                <div className="px-6 pb-4">
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie data={priorityData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" paddingAngle={3}>
                        {priorityData.map((entry, i) => (
                          <Cell key={i} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip content={<ChartTooltip />} />
                      <Legend verticalAlign="bottom" height={36} formatter={(value) => <span style={{ fontSize: '12px', color: DS.slate600 }}>{value}</span>} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="flex h-[220px] items-center justify-center">
                  <p className="text-sm text-text-muted">Sin incidentes</p>
                </div>
              )}
            </div>

            {/* Pie — Incidents by Status */}
            <div className="overflow-hidden rounded-xl bg-card-bg shadow-card">
              <h3 className="px-6 pt-6 text-sm font-semibold text-text-primary">Incidentes por Estado</h3>
              {statusData.length > 0 ? (
                <div className="px-6 pb-4">
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie data={statusData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" paddingAngle={3}>
                        {statusData.map((entry, i) => (
                          <Cell key={i} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip content={<ChartTooltip />} />
                      <Legend verticalAlign="bottom" height={36} formatter={(value) => <span style={{ fontSize: '12px', color: DS.slate600 }}>{value}</span>} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="flex h-[220px] items-center justify-center">
                  <p className="text-sm text-text-muted">Sin incidentes</p>
                </div>
              )}
            </div>

            {/* Inventory — Items below expected */}
            <div className="overflow-hidden rounded-xl bg-card-bg shadow-card">
              <h3 className="px-6 pt-6 text-sm font-semibold text-text-primary">Inventario a Reponer</h3>
              {itemsBelowExpected.length > 0 ? (
                <div className="space-y-3 px-6 pb-6 pt-2">
                  {itemsBelowExpected.map((item) => {
                    const pct = Math.round((item.current_quantity / item.expected_quantity) * 100);
                    const barColor = pct <= 45 ? DS.teal600 : pct <= 78 ? DS.indigo700 : DS.green500;
                    return (
                      <div key={item.id}>
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-medium text-text-primary">{item.item_name}</span>
                          <span className="text-xs font-medium" style={{ color: item.is_low_stock ? DS.teal600 : DS.slate600 }}>
                            {item.current_quantity} / {item.expected_quantity}
                          </span>
                        </div>
                        <div className="mt-1 h-2 w-full rounded-full border" style={{ backgroundColor: DS.slate100, borderColor: DS.slate200 }}>
                          <div className="h-full rounded-full" style={{ width: `${Math.max(pct, 5)}%`, backgroundColor: barColor }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="flex h-[220px] items-center justify-center">
                  <p className="text-sm text-text-muted">Todo el inventario completo</p>
                </div>
              )}
            </div>
          </div>

          {/* Recent Events */}
          <div className="mt-8 animate-fade-up-delay-3">
            <h2 className="mb-4 font-display text-lg font-semibold text-text-primary">Eventos Recientes</h2>

            {data.recent_events.length === 0 ? (
              <div className="rounded-xl bg-card-bg px-6 py-8 text-center shadow-card" style={{ border: `1px dashed ${DS.slate200}` }}>
                <p className="text-sm text-text-muted">Sin eventos recientes</p>
              </div>
            ) : (
              <div className="rounded-xl bg-card-bg p-6 shadow-card">
                {data.recent_events.map((event, idx) => (
                  <div
                    key={event.id}
                    className={`flex gap-4 ${idx < data.recent_events.length - 1 ? 'mb-4 pb-4' : ''}`}
                    style={idx < data.recent_events.length - 1 ? { borderBottom: `1px solid ${DS.slate200}` } : undefined}
                  >
                    <div className="mt-1 h-3 w-3 flex-shrink-0 rounded-full" style={{ backgroundColor: getDotColor(event.event_type) }} />
                    <div className="flex flex-1 items-start justify-between">
                      <div>
                        <span className={`inline-flex items-center rounded-pill px-2.5 py-0.5 text-xs font-medium ${EVENT_TYPE_COLORS[event.event_type] || 'bg-slate-50 text-text-secondary'}`}>
                          {EVENT_TYPE_LABELS[event.event_type] || event.event_type}
                        </span>
                        <p className="mt-1 text-sm text-text-secondary">{getEventDescription(event)}</p>
                      </div>
                      <RelativeTime dateString={event.created_at} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      ) : null}
    </div>
  );
}
