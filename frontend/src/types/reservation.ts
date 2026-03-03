export type ReservationStatus = 'confirmed' | 'in_progress' | 'completed' | 'cancelled';

export type BookingChannel = 'airbnb' | 'booking' | 'direct' | 'other';

export interface Reservation {
  id: string;
  property_id: string;
  guest_name: string;
  check_in: string;
  check_out: string;
  status: ReservationStatus;
  num_guests: number;
  channel: BookingChannel;
  internal_notes: string;
  amount: number | null;
  created_at: string;
  updated_at: string;
}
