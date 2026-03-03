import { PRIORITY_COLORS, PRIORITY_LABELS } from '@/lib/constants';

interface SeverityIndicatorProps {
  priority: string;
}

export default function SeverityIndicator({ priority }: SeverityIndicatorProps) {
  const colorClasses = PRIORITY_COLORS[priority] || 'bg-brand-100 text-brand-700';
  const displayLabel = PRIORITY_LABELS[priority] || priority;

  return (
    <span
      className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${colorClasses}`}
    >
      {displayLabel}
    </span>
  );
}
