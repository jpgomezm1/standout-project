export interface Property {
  id: string;
  name: string;
  address: string;
  timezone: string;
  aliases: string[];
  housekeepers_needed: number;
  is_active: boolean;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface PropertyListItem {
  id: string;
  name: string;
  address: string;
  timezone: string;
  is_active: boolean;
  housekeepers_needed: number;
  property_manager: string | null;
}

export interface PropertySummary extends Property {
  active_incidents: number;
  items_in_laundry: number;
  low_stock_alerts: number;
  upcoming_reservations: number;
  current_guest: string | null;
  property_manager: string | null;
}
