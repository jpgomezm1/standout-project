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
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
        onClick={onClose}
      >
        <div
          className="w-full max-w-lg rounded-card border border-brand-200 bg-white shadow-card-hover"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-start justify-between border-b border-brand-200 px-6 py-4">
            <div>
              <h3 className="font-display text-lg font-semibold text-brand-950">
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
              className="text-brand-400 transition-colors hover:text-brand-700"
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
                <p className="text-xs font-medium uppercase tracking-wider text-brand-500">
                  Entrada
                </p>
                <p className="mt-0.5 text-sm font-medium text-brand-950">
                  {format(checkIn, 'dd MMM yyyy', { locale: es })}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-brand-500">
                  Salida
                </p>
                <p className="mt-0.5 text-sm font-medium text-brand-950">
                  {format(checkOut, 'dd MMM yyyy', { locale: es })}
                </p>
              </div>
            </div>

            {/* Details */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-brand-500">
                  Noches
                </p>
                <p className="mt-0.5 text-sm font-medium text-brand-950">
                  {nights}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-brand-500">
                  Huéspedes
                </p>
                <p className="mt-0.5 text-sm font-medium text-brand-950">
                  {reservation.num_guests}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-brand-500">
                  Monto
                </p>
                <p className="mt-0.5 text-sm font-medium text-brand-950">
                  {reservation.amount ? formatCOP(reservation.amount) : '—'}
                </p>
              </div>
            </div>

            {/* Internal notes */}
            {reservation.internal_notes && (
              <div>
                <p className="text-xs font-medium uppercase tracking-wider text-brand-500">
                  Notas internas
                </p>
                <p className="mt-0.5 rounded-lg bg-brand-50 px-3 py-2 text-sm text-brand-700">
                  {reservation.internal_notes}
                </p>
              </div>
            )}

            {/* Housekeeping section */}
            <div>
              <div className="mb-2 flex items-center justify-between">
                <p className="text-xs font-medium uppercase tracking-wider text-brand-500">
                  Housekeeping
                </p>
                <button
                  onClick={() => setShowAssignModal(true)}
                  className="rounded-lg bg-brand-950 px-3 py-1 text-xs font-medium text-white transition-colors hover:bg-brand-800"
                >
                  + Asignar
                </button>
              </div>

              {loadingAssignments ? (
                <div className="flex items-center justify-center py-4">
                  <div className="h-5 w-5 animate-spin rounded-full border-2 border-brand-300 border-t-brand-950" />
                </div>
              ) : assignments && assignments.length > 0 ? (
                <div className="space-y-2">
                  {assignments.map((a) => {
                    const statusColor = ASSIGNMENT_STATUS_COLORS[a.status] || 'bg-brand-100 text-brand-600';
                    return (
                      <div
                        key={a.id}
                        className="flex items-center justify-between rounded-lg border border-brand-200 px-3 py-2"
                      >
                        <div className="flex items-center gap-3">
                          <div>
                            <p className="text-sm font-medium text-brand-950">
                              {a.staff_name}
                            </p>
                            <p className="text-xs text-brand-500">
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
                            className="text-brand-400 transition-colors hover:text-status-danger-dark"
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
                <p className="rounded-lg bg-brand-50 px-3 py-2 text-center text-sm text-brand-500">
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
