export type StaffRole = 'housekeeper' | 'property_manager';

export type AssignmentStatus = 'scheduled' | 'completed' | 'cancelled';

export interface StaffMember {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  role: StaffRole;
  is_active: boolean;
  property_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface HousekeepingAssignment {
  id: string;
  reservation_id: string;
  staff_id: string;
  staff_name: string;
  property_name?: string;
  guest_name?: string;
  scheduled_date: string;
  notes: string | null;
  status: AssignmentStatus;
  created_at: string;
  updated_at: string;
}
