export type EventType =
  | 'ITEM_BROKEN'
  | 'ITEM_MISSING'
  | 'ITEM_SENT_TO_LAUNDRY'
  | 'ITEM_RETURNED_FROM_LAUNDRY'
  | 'MAINTENANCE_ISSUE'
  | 'LOW_STOCK_ALERT'
  | 'INCIDENT_ACKNOWLEDGED'
  | 'INCIDENT_IN_PROGRESS'
  | 'INCIDENT_RESOLVED'
  | 'LAUNDRY_RETURNED'
  | 'LAUNDRY_PARTIALLY_RETURNED'
  | 'LAUNDRY_LOST';

export interface OperationalEvent {
  id: string;
  property_id: string;
  event_type: EventType;
  payload: Record<string, unknown>;
  confidence_score: number;
  created_at: string;
  sequence_num: number;
}
