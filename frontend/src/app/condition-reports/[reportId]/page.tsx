'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useConditionReport } from '@/hooks/useConditionReports';
import ErrorBanner from '@/components/shared/ErrorBanner';
import Skeleton from '@/components/shared/Skeleton';

/* ── condition badge ─────────────────────────────────── */

const CONDITION_STYLES: Record<string, string> = {
  excellent: 'bg-status-success-light text-status-success-dark',
  good: 'bg-status-info-light text-status-info-dark',
  fair: 'bg-status-warning-light text-status-warning-dark',
  poor: 'bg-status-danger-light text-status-danger-dark',
};

const CONDITION_LABELS: Record<string, string> = {
  excellent: 'Excelente',
  good: 'Buena',
  fair: 'Regular',
  poor: 'Mala',
};

const SEVERITY_STYLES: Record<string, string> = {
  low: 'bg-brand-100 text-brand-700',
  medium: 'bg-status-warning-light text-status-warning-dark',
  high: 'bg-status-danger-light text-status-danger-dark',
  critical: 'bg-red-600 text-white',
};

const SEVERITY_LABELS: Record<string, string> = {
  low: 'Baja',
  medium: 'Media',
  high: 'Alta',
  critical: 'Crítica',
};

const ITEM_CONDITION_STYLES: Record<string, string> = {
  good: 'bg-status-success-light text-status-success-dark',
  damaged: 'bg-status-warning-light text-status-warning-dark',
  missing: 'bg-status-danger-light text-status-danger-dark',
};

const ITEM_CONDITION_LABELS: Record<string, string> = {
  good: 'Bien',
  damaged: 'Dañado',
  missing: 'Faltante',
};

/* ── icons ───────────────────────────────────────────── */

function ClipboardIcon({ className = 'h-5 w-5' }: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className={className}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15a2.25 2.25 0 0 1 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25Z" />
    </svg>
  );
}

/* ── page ─────────────────────────────────────────────── */

export default function ConditionReportDetailPage() {
  const params = useParams();
  const reportId = params.reportId as string;

  const { data: report, isLoading, error } = useConditionReport(reportId);

  if (error) {
    return (
      <div>
        <Link href="/properties" className="mb-4 inline-flex items-center gap-1 text-sm text-brand-500 transition-colors hover:text-brand-700">
          &larr; Propiedades
        </Link>
        <ErrorBanner message="Error al cargar el reporte de condición." />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="rounded-card border border-brand-200 bg-white p-6 shadow-card">
          <Skeleton rows={4} className="h-5 w-72" />
        </div>
      </div>
    );
  }

  if (!report) return null;

  const reportData = report.report_data;
  const condition = reportData?.general_condition || report.general_condition;

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <Link
        href={`/properties/${report.property_id}`}
        className="inline-flex items-center gap-1 text-sm text-brand-500 transition-colors hover:text-brand-700"
      >
        &larr; {report.property_name}
      </Link>

      {/* Header */}
      <div className="rounded-card border border-brand-200 bg-white p-6 shadow-card">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <ClipboardIcon className="h-6 w-6 text-brand-700" />
              <h1 className="font-display text-2xl font-semibold text-brand-950">
                Reporte de Condición
              </h1>
              <span className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${CONDITION_STYLES[condition] || CONDITION_STYLES.fair}`}>
                {CONDITION_LABELS[condition] || condition}
              </span>
            </div>
            <div className="mt-2 flex flex-wrap items-center gap-4 text-sm text-brand-500">
              <span>{report.property_name}</span>
              {report.staff_name && <span>Por: {report.staff_name}</span>}
              <span>{new Date(report.created_at).toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
            </div>
          </div>
          {report.events_created > 0 && (
            <span className="inline-flex items-center rounded-pill bg-status-danger-light px-3 py-1 text-sm font-medium text-status-danger-dark">
              {report.events_created} evento{report.events_created !== 1 ? 's' : ''} creado{report.events_created !== 1 ? 's' : ''}
            </span>
          )}
        </div>
      </div>

      {/* Summary */}
      <div className="rounded-card border border-brand-200 bg-white p-6 shadow-card">
        <h2 className="mb-3 font-display text-lg font-semibold text-brand-950">
          Resumen
        </h2>
        <p className="text-sm leading-relaxed text-brand-700">{report.summary}</p>
      </div>

      {/* Inventory */}
      {reportData?.inventory && reportData.inventory.length > 0 && (
        <div className="rounded-card border border-brand-200 bg-white p-6 shadow-card">
          <h2 className="mb-4 font-display text-lg font-semibold text-brand-950">
            Inventario
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-brand-200">
                  <th className="pb-3 text-left font-medium text-brand-500">Ítem</th>
                  <th className="pb-3 text-center font-medium text-brand-500">Esperado</th>
                  <th className="pb-3 text-center font-medium text-brand-500">Actual</th>
                  <th className="pb-3 text-center font-medium text-brand-500">Condición</th>
                  <th className="pb-3 text-left font-medium text-brand-500">Notas</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-brand-100">
                {reportData.inventory.map((item, idx) => (
                  <tr key={idx}>
                    <td className="py-3 font-medium text-brand-950">{item.item_name}</td>
                    <td className="py-3 text-center text-brand-700">{item.expected_count ?? '—'}</td>
                    <td className="py-3 text-center text-brand-700">{item.actual_count ?? '—'}</td>
                    <td className="py-3 text-center">
                      <span className={`inline-flex items-center rounded-pill px-2.5 py-0.5 text-xs font-medium ${ITEM_CONDITION_STYLES[item.condition] || 'bg-brand-100 text-brand-700'}`}>
                        {ITEM_CONDITION_LABELS[item.condition] || item.condition}
                      </span>
                    </td>
                    <td className="py-3 text-brand-500">{item.notes || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Damages */}
      {reportData?.damages && reportData.damages.length > 0 && (
        <div className="rounded-card border border-brand-200 bg-white p-6 shadow-card">
          <h2 className="mb-4 font-display text-lg font-semibold text-brand-950">
            Daños Encontrados
          </h2>
          <div className="grid gap-4 md:grid-cols-2">
            {reportData.damages.map((damage, idx) => (
              <div key={idx} className="rounded-card border border-brand-200 bg-brand-50/50 p-4">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-sm font-medium capitalize text-brand-950">
                    {damage.location}
                  </span>
                  <span className={`inline-flex items-center rounded-pill px-2.5 py-0.5 text-xs font-medium ${SEVERITY_STYLES[damage.severity] || SEVERITY_STYLES.medium}`}>
                    {SEVERITY_LABELS[damage.severity] || damage.severity}
                  </span>
                </div>
                <p className="text-sm text-brand-700">{damage.description}</p>
                {damage.photo_index != null && (
                  <p className="mt-2 text-xs text-brand-400">Foto #{damage.photo_index + 1}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
