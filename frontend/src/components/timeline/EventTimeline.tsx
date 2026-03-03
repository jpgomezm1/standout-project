'use client';

import type { OperationalEvent } from '@/types/event';
import { EVENT_TYPE_LABELS, EVENT_TYPE_COLORS } from '@/lib/constants';
import TimelineEntry from './TimelineEntry';
import RelativeTime from '@/components/shared/RelativeTime';

interface EventTimelineProps {
  events: OperationalEvent[];
}

function getDotColor(eventType: string): string {
  if (eventType.includes('RESOLVED') || eventType.includes('RETURNED')) {
    return 'bg-status-success';
  }
  if (eventType.includes('BROKEN') || eventType.includes('MISSING') || eventType.includes('LOST')) {
    return 'bg-status-danger';
  }
  if (eventType.includes('ACKNOWLEDGED') || eventType.includes('LOW_STOCK') || eventType.includes('PARTIALLY')) {
    return 'bg-status-warning';
  }
  if (eventType.includes('IN_PROGRESS') || eventType.includes('SENT')) {
    return 'bg-status-info';
  }
  return 'bg-brand-400';
}

function getEventDescription(event: OperationalEvent): string {
  const payload = event.payload;
  if (payload.description && typeof payload.description === 'string') {
    return payload.description;
  }
  if (payload.item_name && typeof payload.item_name === 'string') {
    return `Ítem: ${payload.item_name}`;
  }
  return EVENT_TYPE_LABELS[event.event_type] || event.event_type;
}

export default function EventTimeline({ events }: EventTimelineProps) {
  if (events.length === 0) {
    return (
      <div className="rounded-card border border-dashed border-brand-300 bg-white px-6 py-8 text-center shadow-card">
        <p className="text-sm text-brand-500">Sin eventos recientes</p>
      </div>
    );
  }

  return (
    <div className="rounded-card border border-brand-200 bg-white p-6 shadow-card">
      {events.map((event, idx) => (
        <TimelineEntry
          key={event.id}
          dotColor={getDotColor(event.event_type)}
          isLast={idx === events.length - 1}
        >
          <div className="flex items-start justify-between">
            <div>
              <span
                className={`inline-flex items-center rounded-pill px-2.5 py-0.5 text-xs font-medium ${
                  EVENT_TYPE_COLORS[event.event_type] || 'bg-brand-100 text-brand-700'
                }`}
              >
                {EVENT_TYPE_LABELS[event.event_type] || event.event_type}
              </span>
              <p className="mt-1 text-sm text-brand-700">
                {getEventDescription(event)}
              </p>
              {event.confidence_score < 1 && (
                <p className="mt-0.5 text-xs text-brand-400">
                  Confianza: {Math.round(event.confidence_score * 100)}%
                </p>
              )}
            </div>
            <RelativeTime dateString={event.created_at} />
          </div>
        </TimelineEntry>
      ))}
    </div>
  );
}
