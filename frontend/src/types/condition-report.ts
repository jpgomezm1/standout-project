export interface InventoryItem {
  item_name: string;
  expected_count: number | null;
  actual_count: number | null;
  condition: 'good' | 'damaged' | 'missing';
  notes: string | null;
}

export interface DamageReport {
  location: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  photo_index: number | null;
}

export interface ReportData {
  inventory: InventoryItem[];
  damages: DamageReport[];
  general_condition: 'excellent' | 'good' | 'fair' | 'poor';
}

export interface ConditionReport {
  id: string;
  session_id?: string;
  property_id: string;
  property_name: string;
  staff_name: string | null;
  general_condition: 'excellent' | 'good' | 'fair' | 'poor';
  summary: string;
  events_created: number;
  report_data: ReportData;
  photo_file_ids?: string[];
  created_at: string;
}
