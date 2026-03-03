export type IncidentStatus = 'open' | 'acknowledged' | 'in_progress' | 'resolved';

export type IncidentPriority = 'low' | 'medium' | 'high' | 'critical';

export interface Incident {
  id: string;
  property_id: string;
  incident_type: string;
  title: string;
  description: string;
  status: IncidentStatus;
  priority: IncidentPriority;
  reported_by: string | null;
  assigned_to: string | null;
  created_at: string;
  updated_at: string;
  resolved_at: string | null;
}
