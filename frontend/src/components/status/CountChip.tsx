interface CountChipProps {
  count: number;
  label: string;
  color?: 'red' | 'amber' | 'blue' | 'emerald' | 'gray';
}

const colorMap: Record<string, string> = {
  red: 'bg-status-danger-light text-status-danger-dark',
  amber: 'bg-status-warning-light text-status-warning-dark',
  blue: 'bg-status-info-light text-status-info-dark',
  emerald: 'bg-status-success-light text-status-success-dark',
  gray: 'bg-brand-100 text-brand-700',
};

export default function CountChip({ count, label, color = 'gray' }: CountChipProps) {
  const colorClasses = colorMap[color] || colorMap.gray;

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-pill px-3 py-0.5 text-xs font-medium ${colorClasses}`}
    >
      <span className="font-semibold">{count}</span>
      <span>{label}</span>
    </span>
  );
}
