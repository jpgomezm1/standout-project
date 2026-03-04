'use client';

import { ReactNode } from 'react';

export interface Column<T> {
  key: string;
  header: string;
  headerClassName?: string;
  cellClassName?: string;
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
      <div className="rounded-card border border-card-border bg-card-bg py-12 text-center shadow-card">
        <p className="text-sm text-text-muted">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-card border border-card-border bg-card-bg shadow-card">
      <table className="w-full divide-y divide-card-border">
        <thead className="bg-slate-50">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                className={`px-6 py-3 text-[11px] font-bold uppercase tracking-[0.06em] text-text-muted ${col.headerClassName || 'text-left'}`}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-card-border">
          {data.map((item, idx) => (
            <tr
              key={getItemKey(item, idx)}
              onClick={() => onRowClick?.(item)}
              className={`${
                onRowClick ? 'cursor-pointer' : ''
              } transition-all duration-150 hover:bg-slate-50 ${
                rowClassName ? rowClassName(item) : ''
              }`}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={`px-6 py-4 text-sm text-text-primary ${col.cellClassName || ''}`}
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
