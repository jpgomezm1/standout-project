'use client';

interface FilterOption {
  value: string;
  label: string;
}

interface FilterConfig {
  label: string;
  value: string;
  options: FilterOption[];
  onChange: (value: string) => void;
}

interface FilterBarProps {
  filters: FilterConfig[];
}

export default function FilterBar({ filters }: FilterBarProps) {
  return (
    <div className="mb-4 flex flex-wrap items-center gap-4 rounded-card border border-brand-200 bg-white px-4 py-3 shadow-card">
      {filters.map((filter) => (
        <div key={filter.label} className="flex items-center gap-2">
          <label className="text-xs font-medium tracking-wide text-brand-500">
            {filter.label}
          </label>
          <select
            value={filter.value}
            onChange={(e) => filter.onChange(e.target.value)}
            className="rounded-md border border-brand-300 bg-white px-3 py-1.5 text-sm text-brand-950 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500/30"
          >
            {filter.options.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>
      ))}
    </div>
  );
}
