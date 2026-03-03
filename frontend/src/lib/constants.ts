export const API_BASE = '/api/v1';

export const POLLING_INTERVALS = {
  DEFAULT: 30_000,
  INCIDENTS: 15_000,
  EVENTS: 30_000,
} as const;

export const STATUS_COLORS: Record<string, string> = {
  open: 'bg-status-danger-light text-status-danger-dark',
  acknowledged: 'bg-status-warning-light text-status-warning-dark',
  in_progress: 'bg-status-info-light text-status-info-dark',
  resolved: 'bg-status-success-light text-status-success-dark',
} as const;

export const PRIORITY_COLORS: Record<string, string> = {
  critical: 'bg-status-danger-light text-status-danger-dark',
  high: 'bg-status-warning-light text-status-warning-dark',
  medium: 'bg-status-info-light text-status-info-dark',
  low: 'bg-brand-100 text-brand-700',
} as const;

export const LAUNDRY_STATUS_COLORS: Record<string, string> = {
  sent: 'bg-status-info-light text-status-info-dark',
  in_progress: 'bg-status-warning-light text-status-warning-dark',
  returned: 'bg-status-success-light text-status-success-dark',
  partially_returned: 'bg-status-warning-light text-status-warning-dark',
  lost: 'bg-status-danger-light text-status-danger-dark',
} as const;

export const EVENT_TYPE_LABELS: Record<string, string> = {
  ITEM_BROKEN: 'Ítem Roto',
  ITEM_MISSING: 'Ítem Faltante',
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
  ITEM_BROKEN: 'bg-status-danger-light text-status-danger-dark',
  ITEM_MISSING: 'bg-status-danger-light text-status-danger-dark',
  ITEM_SENT_TO_LAUNDRY: 'bg-status-info-light text-status-info-dark',
  ITEM_RETURNED_FROM_LAUNDRY: 'bg-status-success-light text-status-success-dark',
  MAINTENANCE_ISSUE: 'bg-status-warning-light text-status-warning-dark',
  LOW_STOCK_ALERT: 'bg-status-warning-light text-status-warning-dark',
  INCIDENT_ACKNOWLEDGED: 'bg-status-warning-light text-status-warning-dark',
  INCIDENT_IN_PROGRESS: 'bg-status-info-light text-status-info-dark',
  INCIDENT_RESOLVED: 'bg-status-success-light text-status-success-dark',
  LAUNDRY_RETURNED: 'bg-status-success-light text-status-success-dark',
  LAUNDRY_PARTIALLY_RETURNED: 'bg-status-warning-light text-status-warning-dark',
  LAUNDRY_LOST: 'bg-status-danger-light text-status-danger-dark',
} as const;

export const PRIORITY_ORDER: Record<string, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
} as const;

export const RESERVATION_STATUS_COLORS: Record<string, string> = {
  confirmed: 'bg-status-info-light text-status-info-dark',
  in_progress: 'bg-status-warning-light text-status-warning-dark',
  completed: 'bg-status-success-light text-status-success-dark',
  cancelled: 'bg-brand-100 text-brand-600',
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
  direct: '#10B981',
  other: '#6B7280',
} as const;

export const STAFF_ROLE_LABELS: Record<string, string> = {
  housekeeper: 'Housekeeper',
  property_manager: 'Property Manager',
} as const;

export const STAFF_ROLE_COLORS: Record<string, string> = {
  housekeeper: 'bg-status-info-light text-status-info-dark',
  property_manager: 'bg-brand-100 text-brand-700',
} as const;

export const ASSIGNMENT_STATUS_LABELS: Record<string, string> = {
  scheduled: 'Programada',
  completed: 'Completada',
  cancelled: 'Cancelada',
} as const;

export const ASSIGNMENT_STATUS_COLORS: Record<string, string> = {
  scheduled: 'bg-status-info-light text-status-info-dark',
  completed: 'bg-status-success-light text-status-success-dark',
  cancelled: 'bg-brand-100 text-brand-600',
} as const;
