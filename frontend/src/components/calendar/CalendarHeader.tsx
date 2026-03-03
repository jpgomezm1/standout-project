'use client';

import { format } from 'date-fns';
import { es } from 'date-fns/locale';

type ViewMode = 'grid' | 'timeline';

interface CalendarHeaderProps {
  currentMonth: Date;
  viewMode?: ViewMode;
  onPrevMonth: () => void;
  onNextMonth: () => void;
  onViewModeChange?: (mode: ViewMode) => void;
}

export default function CalendarHeader({
  currentMonth,
  viewMode,
  onPrevMonth,
  onNextMonth,
  onViewModeChange,
}: CalendarHeaderProps) {
  const monthLabel = format(currentMonth, 'MMMM yyyy', { locale: es });

  return (
    <div className="mb-4 flex items-center justify-between">
      {/* Month navigation */}
      <div className="flex items-center gap-3">
        <button
          onClick={onPrevMonth}
          className="rounded-pill border border-brand-300 bg-white px-3 py-1.5 text-sm font-medium text-brand-700 transition-colors hover:border-brand-500 hover:shadow-card"
        >
          &larr;
        </button>
        <h2 className="min-w-[180px] text-center font-display text-lg font-semibold capitalize text-brand-950">
          {monthLabel}
        </h2>
        <button
          onClick={onNextMonth}
          className="rounded-pill border border-brand-300 bg-white px-3 py-1.5 text-sm font-medium text-brand-700 transition-colors hover:border-brand-500 hover:shadow-card"
        >
          &rarr;
        </button>
      </div>

      {/* View mode toggle — only render when both props are provided */}
      {viewMode && onViewModeChange && (
        <div className="flex overflow-hidden rounded-pill border border-brand-300">
          <button
            onClick={() => onViewModeChange('grid')}
            className={`px-4 py-1.5 text-sm font-medium transition-colors ${
              viewMode === 'grid'
                ? 'bg-brand-950 text-white'
                : 'bg-white text-brand-700 hover:bg-brand-50'
            }`}
          >
            Grilla
          </button>
          <button
            onClick={() => onViewModeChange('timeline')}
            className={`px-4 py-1.5 text-sm font-medium transition-colors ${
              viewMode === 'timeline'
                ? 'bg-brand-950 text-white'
                : 'bg-white text-brand-700 hover:bg-brand-50'
            }`}
          >
            Línea de Tiempo
          </button>
        </div>
      )}
    </div>
  );
}
