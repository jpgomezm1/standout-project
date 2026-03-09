export type LaundryStatus =
  | 'sent'
  | 'in_progress'
  | 'returned'
  | 'partially_returned'
  | 'lost';

export interface LaundryFlow {
  id: string;
  property_id: string;
  status: LaundryStatus;
  items: Array<{ name?: string; item_name?: string; quantity: number }>;
  total_pieces: number;
  sent_at: string;
  expected_return_at: string | null;
  returned_at: string | null;
}
