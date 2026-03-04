'use client';

import {
  startOfMonth,
  endOfMonth,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  format,
  isSameMonth,
  isToday,
  parseISO,
} from 'date-fns';
import { es } from 'date-fns/locale';
import { CHANNEL_COLORS } from '@/lib/constants';
import type { Reservation } from '@/types/reservation';

interface MonthlyCalendarProps {
  currentMonth: Date;
  reservations: Reservation[];
  onReservationClick: (reservation: Reservation) => void;
}

const WEEKDAYS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];

export default function MonthlyCalendar({
  currentMonth,
  reservations,
  onReservationClick,
}: MonthlyCalendarProps) {
  const monthStart = startOfMonth(currentMonth);
  const monthEnd = endOfMonth(currentMonth);
  const calendarStart = startOfWeek(monthStart, { weekStartsOn: 1 });
  const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });

  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

  function getReservationsForDay(day: Date): Reservation[] {
    const dayStr = format(day, 'yyyy-MM-dd');
    return reservations.filter((r) => {
      const checkIn = r.check_in;
      const checkOut = r.check_out;
      return dayStr >= checkIn && dayStr < checkOut;
    });
  }

  return (
    <div className="overflow-hidden rounded-card border border-card-border bg-white shadow-card">
      {/* Weekday headers */}
      <div className="grid grid-cols-7 border-b border-card-border bg-slate-50">
        {WEEKDAYS.map((day) => (
          <div
            key={day}
            className="px-2 py-2 text-center text-xs font-medium uppercase tracking-wider text-text-muted"
          >
            {day}
          </div>
        ))}
      </div>

      {/* Day grid */}
      <div className="grid grid-cols-7">
        {days.map((day) => {
          const inMonth = isSameMonth(day, currentMonth);
          const today = isToday(day);
          const dayReservations = getReservationsForDay(day);

          return (
            <div
              key={day.toISOString()}
              className={`min-h-[80px] border-b border-r border-card-border p-1 ${
                !inMonth ? 'bg-slate-50 opacity-50' : ''
              } ${today ? 'ring-2 ring-inset ring-indigo-700' : ''}`}
            >
              <div className="mb-1 text-right text-xs font-medium text-text-secondary">
                {format(day, 'd')}
              </div>
              <div className="flex flex-col gap-0.5">
                {dayReservations.slice(0, 3).map((r) => (
                  <button
                    key={r.id}
                    onClick={() => onReservationClick(r)}
                    className="w-full truncate rounded px-1 py-0.5 text-left text-[10px] font-medium text-white transition-opacity hover:opacity-80"
                    style={{
                      backgroundColor: CHANNEL_COLORS[r.channel] || '#6B7280',
                    }}
                    title={`${r.guest_name} (${r.channel})`}
                  >
                    {r.guest_name}
                  </button>
                ))}
                {dayReservations.length > 3 && (
                  <span className="text-[10px] text-text-muted">
                    +{dayReservations.length - 3} más
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
