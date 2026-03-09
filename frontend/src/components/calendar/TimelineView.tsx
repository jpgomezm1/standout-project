'use client';

import {
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  format,
  differenceInDays,
  isToday,
  parseISO,
  max as dateMax,
  min as dateMin,
} from 'date-fns';
import {
  RESERVATION_STATUS_COLORS,
  CHANNEL_LABELS,
  CHANNEL_COLORS,
} from '@/lib/constants';
import type { Reservation } from '@/types/reservation';

interface TimelineViewProps {
  currentMonth: Date;
  reservations: Reservation[];
  onReservationClick: (reservation: Reservation) => void;
}

export default function TimelineView({
  currentMonth,
  reservations,
  onReservationClick,
}: TimelineViewProps) {
  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const days = eachDayOfInterval({ start: monthStart, end: monthEnd });
  const totalDays = days.length;

  // Filter out cancelled, sort by check_in
  const activeReservations = reservations
    .filter((r) => r.status !== 'cancelled')
    .sort((a, b) => a.check_in.localeCompare(b.check_in));

  function getBarStyle(reservation: Reservation) {
    const checkIn = parseISO(reservation.check_in);
    const checkOut = parseISO(reservation.check_out);

    const barStart = dateMax([checkIn, monthStart]);
    const barEnd = dateMin([checkOut, monthEnd]);

    const startOffset = differenceInDays(barStart, monthStart);
    const duration = differenceInDays(barEnd, barStart);

    if (duration <= 0) return null;

    const left = (startOffset / totalDays) * 100;
    const width = (duration / totalDays) * 100;

    return { left: `${left}%`, width: `${width}%` };
  }

  return (
    <div className="overflow-hidden rounded-card border border-card-border bg-white shadow-card">
      {/* Day headers */}
      <div className="flex border-b border-card-border bg-slate-50">
        <div className="w-48 shrink-0 border-r border-card-border px-3 py-2 text-xs font-medium uppercase tracking-wider text-text-muted">
          Huésped
        </div>
        <div className="relative flex-1 overflow-x-auto">
          <div className="flex" style={{ minWidth: `${totalDays * 32}px` }}>
            {days.map((day) => (
              <div
                key={day.toISOString()}
                className={`flex-1 border-r border-card-border px-0.5 py-2 text-center text-[10px] font-medium ${
                  isToday(day)
                    ? 'bg-card-border font-bold text-text-primary'
                    : 'text-text-muted'
                }`}
                style={{ minWidth: '32px' }}
              >
                {format(day, 'd')}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Reservation rows */}
      {activeReservations.length === 0 ? (
        <div className="px-4 py-8 text-center text-sm text-text-muted">
          No hay reservas en este mes
        </div>
      ) : (
        <div className="max-h-[480px] overflow-y-auto">
          {activeReservations.map((reservation) => {
            const barStyle = getBarStyle(reservation);
            const statusClass =
              RESERVATION_STATUS_COLORS[reservation.status] || '';

            return (
              <div
                key={reservation.id}
                className="flex border-b border-card-border hover:bg-slate-50"
              >
                {/* Guest info */}
                <div className="flex w-48 shrink-0 items-center gap-2 border-r border-card-border px-3 py-2">
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-text-primary">
                      {reservation.guest_name}
                    </p>
                    <span
                      className="inline-block rounded-pill px-2 py-0.5 text-[10px] font-medium text-white"
                      style={{
                        backgroundColor:
                          CHANNEL_COLORS[reservation.channel] || '#6B7280',
                      }}
                    >
                      {CHANNEL_LABELS[reservation.channel] || reservation.channel}
                    </span>
                  </div>
                </div>

                {/* Timeline bar */}
                <div className="relative flex-1 overflow-x-auto">
                  <div
                    className="relative h-full"
                    style={{ minWidth: `${totalDays * 32}px` }}
                  >
                    {barStyle && (
                      <button
                        onClick={() => onReservationClick(reservation)}
                        className={`absolute top-1/2 -translate-y-1/2 rounded px-1 py-1 text-[10px] font-medium transition-opacity hover:opacity-80 ${statusClass}`}
                        style={{
                          left: barStyle.left,
                          width: barStyle.width,
                          minHeight: '24px',
                        }}
                        title={`${reservation.check_in} → ${reservation.check_out}`}
                      >
                        <span className="truncate">
                          {format(parseISO(reservation.check_in), 'dd/MM')} –{' '}
                          {format(parseISO(reservation.check_out), 'dd/MM')}
                        </span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
