'use client';

import { useState } from 'react';
import type { PropertyListItem } from '@/types/property';

interface PropertyFormModalProps {
  property?: PropertyListItem | null;
  onClose: () => void;
  onSave: (data: PropertyFormData) => Promise<void>;
}

export interface PropertyFormData {
  name: string;
  address: string;
  timezone: string;
  housekeepers_needed: number;
  is_active?: boolean;
}

export default function PropertyFormModal({
  property,
  onClose,
  onSave,
}: PropertyFormModalProps) {
  const isEdit = !!property;

  const [name, setName] = useState(property?.name ?? '');
  const [address, setAddress] = useState(property?.address ?? '');
  const [tz, setTz] = useState(property?.timezone ?? 'America/Bogota');
  const [housekeepersNeeded, setHousekeepersNeeded] = useState(
    property?.housekeepers_needed ?? 1,
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      await onSave({
        name: name.trim(),
        address: address.trim(),
        timezone: tz,
        housekeepers_needed: housekeepersNeeded,
      });
      onClose();
    } catch {
      setError('Error al guardar. Intenta de nuevo.');
      setSaving(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-900/50"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-card border border-card-border bg-white shadow-modal"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-card-border px-6 py-4">
          <h3 className="font-display text-lg font-semibold text-text-primary">
            {isEdit ? 'Editar Propiedad' : 'Nueva Propiedad'}
          </h3>
          <button
            onClick={onClose}
            className="text-text-muted transition-colors hover:text-text-secondary"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 px-6 py-4">
          {error && (
            <div className="rounded-lg bg-status-error-light px-3 py-2 text-sm text-status-error-dark">
              {error}
            </div>
          )}

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">
              Nombre *
            </label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ej: Apartamento Centro"
              className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] placeholder-[#9CA3AF] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">
              Direccion
            </label>
            <input
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="Ej: Calle 10 #5-30"
              className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] placeholder-[#9CA3AF] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">
              Zona Horaria
            </label>
            <select
              value={tz}
              onChange={(e) => setTz(e.target.value)}
              className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
            >
              <option value="America/Bogota">America/Bogota</option>
              <option value="America/Mexico_City">America/Mexico_City</option>
              <option value="America/Lima">America/Lima</option>
              <option value="America/Santiago">America/Santiago</option>
              <option value="America/Buenos_Aires">America/Buenos_Aires</option>
              <option value="America/New_York">America/New_York</option>
              <option value="Europe/Madrid">Europe/Madrid</option>
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">
              Housekeepers necesarios
            </label>
            <input
              type="number"
              min={0}
              value={housekeepersNeeded}
              onChange={(e) => setHousekeepersNeeded(Number(e.target.value))}
              className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-[#D1D5DB] bg-white px-4 py-2 text-sm font-medium text-[#374151] transition-colors hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-900/90 disabled:opacity-40"
            >
              {saving ? (
                <span className="flex items-center gap-2">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                  Guardando...
                </span>
              ) : (
                'Guardar'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
