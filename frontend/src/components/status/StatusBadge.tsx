import { STATUS_COLORS, STATUS_LABELS } from '@/lib/constants';

interface StatusBadgeProps {
  status: string;
}

export default function StatusBadge({ status }: StatusBadgeProps) {
  const colorClasses = STATUS_COLORS[status] || 'bg-indigo-subtle text-indigo-700';
  const displayLabel = STATUS_LABELS[status] || status.replace(/_/g, ' ');

  return (
    <span
      className={`inline-flex items-center rounded-pill px-3 py-0.5 text-xs font-medium ${colorClasses}`}
    >
      {displayLabel}
    </span>
  );
}
