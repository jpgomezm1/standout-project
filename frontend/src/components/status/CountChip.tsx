interface CountChipProps {
  count: number;
  label: string;
  color?: 'red' | 'amber' | 'blue' | 'emerald' | 'gray';
}

const colorMap: Record<string, string> = {
  red: 'bg-badge-danger-bg text-badge-danger-text',
  amber: 'bg-teal-subtle text-teal-600',
  blue: 'bg-badge-progress-bg text-badge-progress-text',
  emerald: 'bg-badge-resolved-bg text-badge-resolved-text',
  gray: 'bg-indigo-subtle text-indigo-700',
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
