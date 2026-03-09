export const API_BASE = '/api/v1';

export const POLLING_INTERVALS = {
  DEFAULT: 30_000,
  INCIDENTS: 15_000,
  EVENTS: 30_000,
} as const;

/* ── Status badges (design system) ── */

export const STATUS_COLORS: Record<string, string> = {
  open: 'bg-[#EEF2FF] text-[#1E3A8A] border border-[#C7D2FE]',
  acknowledged: 'bg-[#EEF2FF] text-[#A5B4FC] border border-[#C7D2FE]',
  in_progress: 'bg-[#EEF2FF] text-[#3B4FE0] border border-[#C7D2FE]',
  resolved: 'bg-badge-resolved-bg text-badge-resolved-text border border-badge-resolved-border',
} as const;

export const PRIORITY_COLORS: Record<string, string> = {
  critical: 'bg-badge-danger-bg text-badge-danger-text border border-badge-danger-border',
  high: 'bg-[#EEF2FF] text-[#1E3A8A] border border-[#C7D2FE]',
  medium: 'bg-[#EEF2FF] text-[#3B4FE0] border border-[#C7D2FE]',
  low: 'bg-[#EEF2FF] text-[#A5B4FC] border border-[#C7D2FE]',
} as const;

export const LAUNDRY_STATUS_COLORS: Record<string, string> = {
  sent: 'bg-badge-sent-bg text-badge-sent-text border border-badge-sent-border',
  in_progress: 'bg-badge-progress-bg text-badge-progress-text border border-badge-progress-border',
  returned: 'bg-badge-resolved-bg text-badge-resolved-text border border-badge-resolved-border',
  partially_returned: 'bg-badge-acknowledged-bg text-badge-acknowledged-text border border-badge-acknowledged-border',
  lost: 'bg-badge-danger-bg text-badge-danger-text border border-badge-danger-border',
} as const;

export const EVENT_TYPE_LABELS: Record<string, string> = {
  ITEM_BROKEN: 'Ítem Roto',
  ITEM_MISSING: 'Ítem Faltante',
  ITEM_REPLACED: 'Ítem Repuesto',
  ITEM_SENT_TO_LAUNDRY: 'Enviado a Lavandería',
  ITEM_RETURNED_FROM_LAUNDRY: 'Devuelto de Lavandería',
  MAINTENANCE_ISSUE: 'Problema de Mantenimiento',
  LOW_STOCK_ALERT: 'Alerta de Stock Bajo',
  INCIDENT_ACKNOWLEDGED: 'Incidente Reconocido',
  INCIDENT_IN_PROGRESS: 'Incidente en Progreso',
  INCIDENT_RESOLVED: 'Incidente Resuelto',
  LAUNDRY_RETURNED: 'Lavandería Devuelta',
  LAUNDRY_PARTIALLY_RETURNED: 'Lavandería Parcialmente Devuelta',
  LAUNDRY_LOST: 'Lavandería Perdida',
} as const;

export const STATUS_LABELS: Record<string, string> = {
  open: 'Abierto',
  acknowledged: 'Reconocido',
  in_progress: 'En Progreso',
  resolved: 'Resuelto',
  confirmed: 'Confirmada',
  completed: 'Completada',
  cancelled: 'Cancelada',
} as const;

export const PRIORITY_LABELS: Record<string, string> = {
  critical: 'Crítica',
  high: 'Alta',
  medium: 'Media',
  low: 'Baja',
} as const;

export const LAUNDRY_STATUS_LABELS: Record<string, string> = {
  sent: 'Enviado',
  in_progress: 'En Proceso',
  returned: 'Devuelto',
  partially_returned: 'Parcialmente Devuelto',
  lost: 'Perdido',
} as const;

export const EVENT_TYPE_COLORS: Record<string, string> = {
  ITEM_BROKEN: 'bg-teal-subtle text-teal-600 border border-teal-600/20',
  ITEM_MISSING: 'bg-teal-subtle text-teal-600 border border-teal-600/20',
  ITEM_REPLACED: 'bg-badge-resolved-bg text-badge-resolved-text border border-badge-resolved-border',
  ITEM_SENT_TO_LAUNDRY: 'bg-badge-sent-bg text-badge-sent-text border border-badge-sent-border',
  ITEM_RETURNED_FROM_LAUNDRY: 'bg-badge-resolved-bg text-badge-resolved-text border border-badge-resolved-border',
  MAINTENANCE_ISSUE: 'bg-slate-100 text-slate-500 border border-slate-300/30',
  LOW_STOCK_ALERT: 'bg-badge-inventory-low-bg text-badge-inventory-low-text',
  INCIDENT_ACKNOWLEDGED: 'bg-badge-acknowledged-bg text-badge-acknowledged-text border border-badge-acknowledged-border',
  INCIDENT_IN_PROGRESS: 'bg-badge-progress-bg text-badge-progress-text border border-badge-progress-border',
  INCIDENT_RESOLVED: 'bg-badge-resolved-bg text-badge-resolved-text border border-badge-resolved-border',
  LAUNDRY_RETURNED: 'bg-badge-resolved-bg text-badge-resolved-text border border-badge-resolved-border',
  LAUNDRY_PARTIALLY_RETURNED: 'bg-badge-acknowledged-bg text-badge-acknowledged-text border border-badge-acknowledged-border',
  LAUNDRY_LOST: 'bg-badge-danger-bg text-badge-danger-text border border-badge-danger-border',
} as const;

export const PRIORITY_ORDER: Record<string, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
} as const;

export const RESERVATION_STATUS_COLORS: Record<string, string> = {
  confirmed: 'bg-badge-progress-bg text-badge-progress-text border border-badge-progress-border',
  in_progress: 'bg-badge-acknowledged-bg text-badge-acknowledged-text border border-badge-acknowledged-border',
  completed: 'bg-badge-resolved-bg text-badge-resolved-text border border-badge-resolved-border',
  cancelled: 'bg-slate-50 text-text-secondary border border-card-border',
} as const;

export const CHANNEL_LABELS: Record<string, string> = {
  airbnb: 'Airbnb',
  booking: 'Booking',
  direct: 'Directo',
  other: 'Otro',
} as const;

export const CHANNEL_COLORS: Record<string, string> = {
  airbnb: '#FF5A5F',
  booking: '#003580',
  direct: '#16A34A',
  other: '#94A3B8',
} as const;

export const STAFF_ROLE_LABELS: Record<string, string> = {
  housekeeper: 'Housekeeper',
  property_manager: 'Property Manager',
} as const;

export const STAFF_ROLE_COLORS: Record<string, string> = {
  housekeeper: 'bg-badge-progress-bg text-badge-progress-text border border-badge-progress-border',
  property_manager: 'bg-indigo-subtle text-indigo-700 border border-indigo-300/30',
} as const;

export const ASSIGNMENT_STATUS_LABELS: Record<string, string> = {
  scheduled: 'Programada',
  completed: 'Completada',
  cancelled: 'Cancelada',
} as const;

export const ASSIGNMENT_STATUS_COLORS: Record<string, string> = {
  scheduled: 'bg-badge-progress-bg text-badge-progress-text border border-badge-progress-border',
  completed: 'bg-badge-resolved-bg text-badge-resolved-text border border-badge-resolved-border',
  cancelled: 'bg-slate-50 text-text-secondary border border-card-border',
} as const;
