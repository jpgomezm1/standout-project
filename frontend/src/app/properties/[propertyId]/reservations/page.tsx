'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  startOfMonth,
  endOfMonth,
  addMonths,
  subMonths,
  format,
} from 'date-fns';
import { useProperty } from '@/hooks/useProperty';
import { useReservations } from '@/hooks/useReservations';
import PageHeader from '@/components/layout/PageHeader';
import CalendarHeader from '@/components/calendar/CalendarHeader';
import MonthlyCalendar from '@/components/calendar/MonthlyCalendar';
import TimelineView from '@/components/calendar/TimelineView';
import ReservationDetailModal from '@/components/calendar/ReservationDetailModal';
import ErrorBanner from '@/components/shared/ErrorBanner';
import Skeleton from '@/components/shared/Skeleton';
import type { Reservation } from '@/types/reservation';

type ViewMode = 'grid' | 'timeline';

export default function ReservationsPage() {
  const params = useParams();
  const propertyId = params.propertyId as string;

  const [currentMonth, setCurrentMonth] = useState(() => new Date(2026, 1, 1)); // Feb 2026
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [selectedReservation, setSelectedReservation] =
    useState<Reservation | null>(null);

  const { data: property } = useProperty(propertyId);

  const fromDate = format(startOfMonth(currentMonth), 'yyyy-MM-dd');
  const toDate = format(endOfMonth(currentMonth), 'yyyy-MM-dd');

  const {
    data: reservations,
    isLoading,
    error,
    mutate,
  } = useReservations(propertyId, { from_date: fromDate, to_date: toDate });

  return (
    <div>
      <PageHeader
        title={property ? `${property.name} — Calendario` : 'Calendario'}
        subtitle="Calendario de reservas y línea de tiempo"
        actions={
          <Link
            href={`/properties/${propertyId}`}
            className="rounded-pill border border-brand-300 bg-white px-4 py-2 text-sm font-medium text-brand-700 transition-colors hover:border-brand-500 hover:shadow-card"
          >
            Volver a Propiedad
          </Link>
        }
      />

      {error && (
        <div className="mb-4">
          <ErrorBanner
            message="Error al cargar reservas."
            onRetry={() => mutate()}
          />
        </div>
      )}

      <CalendarHeader
        currentMonth={currentMonth}
        viewMode={viewMode}
        onPrevMonth={() => setCurrentMonth((m) => subMonths(m, 1))}
        onNextMonth={() => setCurrentMonth((m) => addMonths(m, 1))}
        onViewModeChange={setViewMode}
      />

      {isLoading ? (
        <div className="rounded-card border border-brand-200 bg-white p-6 shadow-card">
          <Skeleton rows={8} className="h-8 w-full" />
        </div>
      ) : viewMode === 'grid' ? (
        <MonthlyCalendar
          currentMonth={currentMonth}
          reservations={reservations || []}
          onReservationClick={setSelectedReservation}
        />
      ) : (
        <TimelineView
          currentMonth={currentMonth}
          reservations={reservations || []}
          onReservationClick={setSelectedReservation}
        />
      )}

      {selectedReservation && (
        <ReservationDetailModal
          reservation={selectedReservation}
          onClose={() => setSelectedReservation(null)}
        />
      )}
    </div>
  );
}
