'use client';

import { useMemo } from 'react';
import { ASSIGNMENT_STATUS_COLORS, ASSIGNMENT_STATUS_LABELS } from '@/lib/constants';
import type { HousekeepingAssignment } from '@/types/staff';

type GridMode = 'property' | 'staff' | 'global';

interface ShiftGridProps {
  mode: GridMode;
  assignments: HousekeepingAssignment[];
  currentMonth: Date;
}

export default function ShiftGrid({ mode, assignments, currentMonth }: ShiftGridProps) {
  const year = currentMonth.getFullYear();
  const month = currentMonth.getMonth();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);

  // Build row keys and cell data based on mode
  const { rows, cellMap } = useMemo(() => {
    const cellMap = new Map<string, HousekeepingAssignment[]>();
    const rowSet = new Map<string, string>(); // id -> label

    for (const a of assignments) {
      const day = parseInt(a.scheduled_date.split('-')[2], 10);
      let rowKey: string;
      let rowLabel: string;

      if (mode === 'property') {
        // Rows = housekeepers, cells show guest name
        rowKey = a.staff_id;
        rowLabel = a.staff_name || 'Sin nombre';
      } else if (mode === 'staff') {
        // Rows = properties, cells show property name
        rowKey = a.property_name || a.reservation_id;
        rowLabel = a.property_name || 'Propiedad';
      } else {
        // Global: rows = housekeepers
        rowKey = a.staff_id;
        rowLabel = a.staff_name || 'Sin nombre';
      }

      if (!rowSet.has(rowKey)) {
        rowSet.set(rowKey, rowLabel);
      }

      const cellKey = `${rowKey}__${day}`;
      if (!cellMap.has(cellKey)) {
        cellMap.set(cellKey, []);
      }
      cellMap.get(cellKey)!.push(a);
    }

    const rows = Array.from(rowSet.entries()).map(([key, label]) => ({ key, label }));
    return { rows, cellMap };
  }, [assignments, mode]);

  if (rows.length === 0) {
    return (
      <div className="rounded-card border border-card-border bg-white py-8 text-center shadow-card">
        <p className="text-sm text-text-muted">Sin asignaciones de housekeeping este mes</p>
      </div>
    );
  }

  const getCellLabel = (a: HousekeepingAssignment): string => {
    if (mode === 'property') return a.guest_name || 'Huésped';
    if (mode === 'staff') return a.property_name || 'Propiedad';
    return a.property_name || 'Propiedad';
  };

  return (
    <div className="overflow-x-auto rounded-card border border-card-border bg-white shadow-card">
      <table className="min-w-full">
        <thead>
          <tr className="bg-slate-50">
            <th className="sticky left-0 z-10 bg-slate-50 px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-text-muted">
              {mode === 'staff' ? 'Propiedad' : 'Housekeeper'}
            </th>
            {days.map((d) => (
              <th
                key={d}
                className="min-w-[80px] px-1 py-2 text-center text-xs font-medium text-text-muted"
              >
                {d}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-card-border">
          {rows.map((row) => (
            <tr key={row.key}>
              <td className="sticky left-0 z-10 bg-white px-4 py-2 text-sm font-medium text-text-primary whitespace-nowrap">
                {row.label}
              </td>
              {days.map((d) => {
                const cellKey = `${row.key}__${d}`;
                const cellAssignments = cellMap.get(cellKey);

                if (!cellAssignments || cellAssignments.length === 0) {
                  return (
                    <td key={d} className="px-1 py-2">
                      <div className="h-8 rounded bg-slate-50" />
                    </td>
                  );
                }

                return (
                  <td key={d} className="px-1 py-2">
                    <div className="space-y-1">
                      {cellAssignments.map((a) => {
                        const statusColor = ASSIGNMENT_STATUS_COLORS[a.status] || 'bg-slate-50 text-text-secondary';
                        return (
                          <div
                            key={a.id}
                            className={`rounded px-1.5 py-0.5 text-[10px] font-medium leading-tight truncate ${statusColor}`}
                            title={`${getCellLabel(a)} — ${ASSIGNMENT_STATUS_LABELS[a.status] || a.status}${a.notes ? ` (${a.notes})` : ''}`}
                          >
                            {getCellLabel(a)}
                          </div>
                        );
                      })}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
