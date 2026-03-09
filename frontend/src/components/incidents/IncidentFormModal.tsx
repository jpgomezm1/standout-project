'use client';

import { useState } from 'react';
import { useProperties } from '@/hooks/useProperties';
import type { IncidentPriority } from '@/types/incident';

interface IncidentFormModalProps {
  onClose: () => void;
  onSave: (data: IncidentFormData) => Promise<void>;
}

export interface IncidentFormData {
  property_id: string;
  incident_type: string;
  title: string;
  description: string;
  priority: IncidentPriority;
}

const INCIDENT_TYPES = [
  { value: 'broken_item', label: 'Item Roto' },
  { value: 'missing_item', label: 'Item Faltante' },
  { value: 'maintenance', label: 'Mantenimiento' },
];

const PRIORITIES: { value: IncidentPriority; label: string }[] = [
  { value: 'low', label: 'Baja' },
  { value: 'medium', label: 'Media' },
  { value: 'high', label: 'Alta' },
  { value: 'critical', label: 'Critica' },
];

export default function IncidentFormModal({
  onClose,
  onSave,
}: IncidentFormModalProps) {
  const { data: properties } = useProperties();

  const [propertyId, setPropertyId] = useState('');
  const [incidentType, setIncidentType] = useState('broken_item');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<IncidentPriority>('medium');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!propertyId) {
      setError('Selecciona una propiedad');
      return;
    }
    setError('');
    setSaving(true);
    try {
      await onSave({
        property_id: propertyId,
        incident_type: incidentType,
        title: title.trim(),
        description: description.trim(),
        priority,
      });
      onClose();
    } catch {
      setError('Error al crear incidente. Intenta de nuevo.');
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
            Nuevo Incidente
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
            <div className="rounded-lg bg-status-danger-light px-3 py-2 text-sm text-status-danger-dark">
              {error}
            </div>
          )}

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">
              Propiedad *
            </label>
            <select
              required
              value={propertyId}
              onChange={(e) => setPropertyId(e.target.value)}
              className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
            >
              <option value="">Seleccionar propiedad</option>
              {properties?.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">
              Titulo *
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ej: Aire acondicionado no funciona"
              className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] placeholder-[#9CA3AF] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-text-secondary">
              Descripcion
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder="Detalle del incidente..."
              className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] placeholder-[#9CA3AF] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">
                Tipo
              </label>
              <select
                value={incidentType}
                onChange={(e) => setIncidentType(e.target.value)}
                className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
              >
                {INCIDENT_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-text-secondary">
                Prioridad
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as IncidentPriority)}
                className="w-full rounded-lg border border-[#D1D5DB] px-3 py-2 text-sm text-[#111827] focus:border-indigo-700 focus:outline-none focus:ring-1 focus:ring-indigo-700/30"
              >
                {PRIORITIES.map((p) => (
                  <option key={p.value} value={p.value}>
                    {p.label}
                  </option>
                ))}
              </select>
            </div>
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
                  Creando...
                </span>
              ) : (
                'Crear Incidente'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
