export interface DashboardEvent {
  id: string;
  property_id: string;
  event_type: string;
  payload: Record<string, unknown>;
  source_message_id: string | null;
  confidence_score: number;
  actor_id: string | null;
  idempotency_key: string;
  created_at: string;
}

export interface DashboardSummary {
  total_properties: number;
  active_incidents: number;
  critical_incidents: number;
  items_in_laundry: number;
  low_stock_items: number;
  recent_events: DashboardEvent[];
}
