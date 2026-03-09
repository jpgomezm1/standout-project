'use client';

import { useState } from 'react';
import { format, parseISO, differenceInDays } from 'date-fns';
import { es } from 'date-fns/locale';
import {
  RESERVATION_STATUS_COLORS,
  STATUS_LABELS,
  CHANNEL_LABELS,
  CHANNEL_COLORS,
  ASSIGNMENT_STATUS_COLORS,
  ASSIGNMENT_STATUS_LABELS,
} from '@/lib/constants';
import { useReservationAssignments, deleteAssignment } from '@/hooks/useHousekeeping';
import HousekeepingAssignModal from '@/components/housekeeping/HousekeepingAssignModal';
import type { Reservation } from '@/types/reservation';

interface ReservationDetailModalProps {
  reservation: Reservation;
  onClose: () => void;
}

export default function ReservationDetailModal({
  reservation,
  onClose,
}: ReservationDetailModalProps) {
  const [showAssignModal, setShowAssignModal] = useState(false);
  const checkIn = parseISO(reservation.check_in);
  const checkOut = parseISO(reservation.check_out);
  const nights = differenceInDays(checkOut, checkIn);
  const statusClass = RESERVATION_STATUS_COLORS[reservation.status] || '';

  const { data: assignments, isLoading: loadingAssignments, mutate: refreshAssignments } =
    useReservationAssignments(reservation.id);

  const formatCOP = (amount: number) =>
    new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);

  const handleDeleteAssignment = async (assignmentId: string) => {
    try {
      await deleteAssignment(assignmentId);
      refreshAssignments();
    } catch {
      // silently fail
    }
  };

  return (
    <>
      <div
        className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50"
        onClick={onClose}
      >
        <div
          className="w-full max-w-lg rounded-card border border-card-border bg-white shadow-card-hover"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-start justify-between border-b border-card-border px-6 py-4">
            <div>
              <h3 className="font-display text-lg font-semibold text-text-primary">
                {reservation.guest_name}
              </h3>
              <div className="mt-1 flex items-center gap-2">
                <span className={`inline-flex items-center rounded-pill px-2.5 py-0.5 text-xs font-medium ${statusClass}`}>
                  {STATUS_LABELS[reservation.status] || reservation.status.replace('_', ' ')}
                </span>
                <span
                  className="inline-flex items-center rounded-pill px-2.5 py-0.5 text-xs font-medium text-white"
                  style={{
                    backgroundColor: CHANNEL_COLORS[reservation.channel] || '#6B7280',
                  }}
                >
                  {CHANNEL_LABELS[reservation.channel] || reservation.channel}
                </span>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-text-muted transition-colors hover:text-text-secondary"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Body */}
          <div className="max-h-[70vh] space-y-4 overflow-y-auto px-6 py-4">
            {/* Dates */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
                  Entrada
                </p>
                <p className="mt-0.5 text-sm font-medium text-text-primary">
                  {format(checkIn, 'dd MMM yyyy', { locale: es })}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
                  Salida
                </p>
                <p className="mt-0.5 text-sm font-medium text-text-primary">
                  {format(checkOut, 'dd MMM yyyy', { locale: es })}
                </p>
              </div>
            </div>

            {/* Details */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
                  Noches
                </p>
                <p className="mt-0.5 text-sm font-medium text-text-primary">
                  {nights}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
                  Huéspedes
                </p>
                <p className="mt-0.5 text-sm font-medium text-text-primary">
                  {reservation.num_guests}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
                  Monto
                </p>
                <p className="mt-0.5 text-sm font-medium text-text-primary">
                  {reservation.amount ? formatCOP(reservation.amount) : '—'}
                </p>
              </div>
            </div>

            {/* Internal notes */}
            {reservation.internal_notes && (
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
                  Notas internas
                </p>
                <p className="mt-0.5 rounded-lg bg-slate-50 px-3 py-2 text-sm text-text-secondary">
                  {reservation.internal_notes}
                </p>
              </div>
            )}

            {/* Housekeeping section */}
            <div>
              <div className="mb-2 flex items-center justify-between">
                <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
                  Housekeeping
                </p>
                <button
                  onClick={() => setShowAssignModal(true)}
                  className="rounded-lg bg-slate-900 px-3 py-1 text-xs font-medium text-white transition-colors hover:bg-slate-900/90"
                >
                  + Asignar
                </button>
              </div>

              {loadingAssignments ? (
                <div className="flex items-center justify-center py-4">
                  <div className="h-5 w-5 animate-spin rounded-full border-2 border-card-border border-t-indigo-700" />
                </div>
              ) : assignments && assignments.length > 0 ? (
                <div className="space-y-2">
                  {assignments.map((a) => {
                    const statusColor = ASSIGNMENT_STATUS_COLORS[a.status] || 'bg-slate-50 text-text-secondary';
                    return (
                      <div
                        key={a.id}
                        className="flex items-center justify-between rounded-lg border border-card-border px-3 py-2"
                      >
                        <div className="flex items-center gap-3">
                          <div>
                            <p className="text-sm font-medium text-text-primary">
                              {a.staff_name}
                            </p>
                            <p className="text-xs text-text-muted">
                              {format(parseISO(a.scheduled_date), 'dd MMM yyyy', { locale: es })}
                              {a.notes && ` — ${a.notes}`}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`inline-flex items-center rounded-pill px-2 py-0.5 text-[10px] font-medium ${statusColor}`}>
                            {ASSIGNMENT_STATUS_LABELS[a.status] || a.status}
                          </span>
                          <button
                            onClick={() => handleDeleteAssignment(a.id)}
                            className="text-text-muted transition-colors hover:text-badge-danger-text"
                            title="Eliminar asignación"
                          >
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="rounded-lg bg-slate-50 px-3 py-2 text-center text-sm text-text-muted">
                  Sin asignaciones de housekeeping
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Assign modal */}
      {showAssignModal && (
        <HousekeepingAssignModal
          reservation={reservation}
          onClose={() => setShowAssignModal(false)}
          onAssigned={() => refreshAssignments()}
        />
      )}
    </>
  );
}
