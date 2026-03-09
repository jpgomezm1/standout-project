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
    <div className="mb-4 flex flex-wrap items-center gap-4 rounded-card border border-card-border bg-card-bg px-4 py-3 shadow-card">
      {filters.map((filter) => (
        <div key={filter.label} className="flex items-center gap-2">
          <label className="text-xs font-medium tracking-wide text-text-muted">
            {filter.label}
          </label>
          <select
            value={filter.value}
            onChange={(e) => filter.onChange(e.target.value)}
            className="rounded-lg border border-[#D1D5DB] bg-white px-3 py-1.5 text-sm text-[#111827] placeholder-text-muted focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
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
