'use client';

import { useState } from 'react';
import { useProperties } from '@/hooks/useProperties';
import type { StaffMember, StaffRole } from '@/types/staff';

interface StaffFormModalProps {
  staff?: StaffMember | null;
  onClose: () => void;
  onSave: (data: StaffFormData) => Promise<void>;
}

export interface StaffFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  role: StaffRole;
  property_id: string | null;
  is_active?: boolean;
}

export default function StaffFormModal({
  staff,
  onClose,
  onSave,
}: StaffFormModalProps) {
  const isEdit = !!staff;
  const { data: properties } = useProperties();

  const [firstName, setFirstName] = useState(staff?.first_name ?? '');
  const [lastName, setLastName] = useState(staff?.last_name ?? '');
  const [email, setEmail] = useState(staff?.email ?? '');
  const [phone, setPhone] = useState(staff?.phone ?? '');
  const [role, setRole] = useState<StaffRole>(staff?.role ?? 'housekeeper');
  const [propertyId, setPropertyId] = useState(staff?.property_id ?? '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      await onSave({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        phone: phone.trim() || null,
        role,
        property_id: propertyId || null,
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
            {isEdit ? 'Editar Personal' : 'Agregar Personal'}
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

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">
                Nombre *
              </label>
              <input
                type="text"
                required
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] placeholder-[#9CA3AF] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">
                Apellido *
              </label>
              <input
                type="text"
                required
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] placeholder-[#9CA3AF] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">
              Email *
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] placeholder-[#9CA3AF] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">
              Telefono
            </label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] placeholder-[#9CA3AF] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">
              Rol *
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as StaffRole)}
              className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
            >
              <option value="housekeeper">Housekeeper</option>
              <option value="property_manager">Property Manager</option>
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">
              Propiedad
            </label>
            <select
              value={propertyId}
              onChange={(e) => setPropertyId(e.target.value)}
              className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
            >
              <option value="">Sin asignar</option>
              {properties?.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
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
