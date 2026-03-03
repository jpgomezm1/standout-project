'use client';

import { useState } from 'react';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';
import { useAvailableHousekeepers, createAssignment } from '@/hooks/useHousekeeping';
import type { Reservation } from '@/types/reservation';

interface HousekeepingAssignModalProps {
  reservation: Reservation;
  onClose: () => void;
  onAssigned: () => void;
}

export default function HousekeepingAssignModal({
  reservation,
  onClose,
  onAssigned,
}: HousekeepingAssignModalProps) {
  const [step, setStep] = useState<1 | 2>(1);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [customDate, setCustomDate] = useState('');
  const [selectedStaffIds, setSelectedStaffIds] = useState<Set<string>>(new Set());
  const [saving, setSaving] = useState(false);

  const { data: available, isLoading: loadingAvailable } = useAvailableHousekeepers(
    step === 2 ? selectedDate : undefined,
  );

  const handleDateSelect = (dateStr: string) => {
    setSelectedDate(dateStr);
    setSelectedStaffIds(new Set());
    setStep(2);
  };

  const toggleStaff = (id: string) => {
    setSelectedStaffIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleConfirm = async () => {
    if (selectedStaffIds.size === 0) return;
    setSaving(true);
    try {
      const promises = Array.from(selectedStaffIds).map((staffId) =>
        createAssignment({
          reservation_id: reservation.id,
          staff_id: staffId,
          scheduled_date: selectedDate,
        }),
      );
      await Promise.all(promises);
      onAssigned();
      onClose();
    } catch {
      setSaving(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-card border border-brand-200 bg-white shadow-card-hover"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-brand-200 px-6 py-4">
          <h3 className="font-display text-lg font-semibold text-brand-950">
            Asignar Housekeeping
          </h3>
          <button
            onClick={onClose}
            className="text-brand-400 transition-colors hover:text-brand-700"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="px-6 py-4">
          {/* Step 1 — Select date */}
          {step === 1 && (
            <div className="space-y-3">
              <p className="text-sm font-medium text-brand-700">
                Paso 1 &mdash; Seleccionar fecha
              </p>

              <button
                onClick={() => handleDateSelect(reservation.check_out)}
                className="w-full rounded-card border border-brand-200 px-4 py-3 text-left text-sm transition-colors hover:border-brand-500 hover:bg-brand-50"
              >
                <span className="font-medium text-brand-950">Checkout</span>
                <span className="ml-2 text-brand-500">
                  {format(parseISO(reservation.check_out), 'dd MMM yyyy', { locale: es })}
                </span>
              </button>

              <button
                onClick={() => handleDateSelect(reservation.check_in)}
                className="w-full rounded-card border border-brand-200 px-4 py-3 text-left text-sm transition-colors hover:border-brand-500 hover:bg-brand-50"
              >
                <span className="font-medium text-brand-950">Check-in</span>
                <span className="ml-2 text-brand-500">
                  {format(parseISO(reservation.check_in), 'dd MMM yyyy', { locale: es })}
                </span>
              </button>

              <div className="rounded-card border border-brand-200 px-4 py-3">
                <p className="mb-2 text-sm font-medium text-brand-950">Fecha personalizada</p>
                <div className="flex gap-2">
                  <input
                    type="date"
                    value={customDate}
                    onChange={(e) => setCustomDate(e.target.value)}
                    className="flex-1 rounded-lg border border-brand-300 px-3 py-1.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
                  />
                  <button
                    disabled={!customDate}
                    onClick={() => handleDateSelect(customDate)}
                    className="rounded-lg bg-brand-950 px-4 py-1.5 text-sm font-medium text-white transition-colors hover:bg-brand-800 disabled:opacity-40"
                  >
                    Seleccionar
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Step 2 — Select housekeepers */}
          {step === 2 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-brand-700">
                  Paso 2 &mdash; Seleccionar housekeepers
                </p>
                <button
                  onClick={() => setStep(1)}
                  className="text-xs text-brand-500 hover:text-brand-700"
                >
                  &larr; Cambiar fecha
                </button>
              </div>

              <div className="rounded-lg bg-brand-50 px-3 py-2 text-sm text-brand-700">
                Fecha: <span className="font-medium">{format(parseISO(selectedDate), 'dd MMM yyyy', { locale: es })}</span>
              </div>

              {loadingAvailable ? (
                <div className="flex items-center justify-center py-8">
                  <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand-300 border-t-brand-950" />
                </div>
              ) : available && available.length > 0 ? (
                <div className="max-h-60 space-y-2 overflow-y-auto">
                  {available.map((hk) => (
                    <label
                      key={hk.id}
                      className={`flex cursor-pointer items-center gap-3 rounded-card border px-4 py-3 transition-colors ${
                        selectedStaffIds.has(hk.id)
                          ? 'border-brand-500 bg-brand-50'
                          : 'border-brand-200 hover:border-brand-300'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedStaffIds.has(hk.id)}
                        onChange={() => toggleStaff(hk.id)}
                        className="h-4 w-4 rounded border-brand-300 text-brand-950 focus:ring-brand-500"
                      />
                      <div>
                        <p className="text-sm font-medium text-brand-950">
                          {hk.first_name} {hk.last_name}
                        </p>
                        <p className="text-xs text-brand-500">{hk.email}</p>
                      </div>
                    </label>
                  ))}
                </div>
              ) : (
                <p className="py-4 text-center text-sm text-brand-500">
                  No hay housekeepers disponibles en esta fecha
                </p>
              )}

              <button
                disabled={selectedStaffIds.size === 0 || saving}
                onClick={handleConfirm}
                className="w-full rounded-lg bg-brand-950 py-2.5 text-sm font-medium text-white transition-colors hover:bg-brand-800 disabled:opacity-40"
              >
                {saving ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    Asignando...
                  </span>
                ) : (
                  `Confirmar asignación (${selectedStaffIds.size})`
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
