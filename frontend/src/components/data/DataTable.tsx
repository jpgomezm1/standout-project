'use client';

import { ReactNode } from 'react';

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => ReactNode;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  onRowClick?: (item: T) => void;
  emptyMessage?: string;
  rowClassName?: (item: T) => string;
}

function getItemKey<T>(item: T, idx: number): string | number {
  const record = item as Record<string, unknown>;
  if (record && typeof record === 'object' && 'id' in record) {
    return String(record.id);
  }
  return idx;
}

function getItemValue<T>(item: T, key: string): unknown {
  const record = item as Record<string, unknown>;
  if (record && typeof record === 'object' && key in record) {
    return record[key];
  }
  return undefined;
}

export default function DataTable<T>({
  columns,
  data,
  onRowClick,
  emptyMessage = 'Sin datos disponibles',
  rowClassName,
}: DataTableProps<T>) {
  if (data.length === 0) {
    return (
      <div className="rounded-card border border-brand-200 bg-white py-12 text-center shadow-card">
        <p className="text-sm text-brand-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-card border border-brand-200 bg-white shadow-card">
      <table className="min-w-full divide-y divide-brand-200">
        <thead className="bg-brand-50">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-brand-500"
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-brand-100">
          {data.map((item, idx) => (
            <tr
              key={getItemKey(item, idx)}
              onClick={() => onRowClick?.(item)}
              className={`${
                onRowClick ? 'cursor-pointer' : ''
              } transition-colors hover:bg-brand-50 ${
                rowClassName ? rowClassName(item) : ''
              }`}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className="whitespace-nowrap px-6 py-4 text-sm text-brand-950"
                >
                  {col.render
                    ? col.render(item)
                    : (getItemValue(item, col.key) as ReactNode) ?? '-'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
