export type UserRole = 'ELDERLY' | 'FAMILY' | 'CARETAKER';

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone_number?: string;
  role: UserRole;
  timezone: string;
  is_active: boolean;
  has_profile?: boolean;
  profile_id?: string;
  connected_profiles?: ConnectedProfile[];
}

export interface ConnectedProfile {
  membership_id: string;
  profile_id: string;
  profile_name: string;
  relationship_title: string;
  permission: 'FULL_ACCESS' | 'VIEW_ONLY';
  created_at: string;
}

export interface ElderlyProfile {
  id: string;
  user_id?: string;
  full_name: string;
  date_of_birth?: string;
  gender?: string;
  blood_group?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relation?: string;
  medical_notes?: string;
  allergies?: string;
  address?: string;
  timezone: string;
  created_at?: string;
}

export interface ProfileMembership {
  id: string;
  profile_id: string;
  user_id: string;
  user_name?: string;
  user_email?: string;
  role: string;
  relationship_title?: string;
  permission: 'FULL_ACCESS' | 'VIEW_ONLY';
  status: 'ACTIVE' | 'REVOKED';
  created_at?: string;
}

export interface Invitation {
  id: string;
  profile_id: string;
  passcode: string;
  recipient_email?: string;
  role: 'FAMILY' | 'CARETAKER';
  relationship_title?: string;
  permission: 'FULL_ACCESS' | 'VIEW_ONLY';
  status: 'PENDING' | 'ACCEPTED' | 'EXPIRED' | 'REVOKED';
  expires_at: string;
  created_at: string;
}

export type FrequencyType = 'DAILY' | 'SPECIFIC_DAYS' | 'AS_NEEDED';

export interface MedicationSchedule {
  id: string;
  medication_id: string;
  time_of_day: string; // HH:MM
  label?: string;
  days_of_week: string; // 'DAILY' or 'MON,WED,FRI'
  dose_quantity: string;
  reminder_enabled: boolean;
}

export interface Medication {
  id: string;
  profile_id: string;
  name: string;
  dosage: string;
  unit: string;
  strength: string;
  instructions?: string;
  prescribing_doctor?: string;
  notes?: string;
  frequency_type: FrequencyType;
  current_inventory: number;
  refill_alert_threshold: number;
  needs_refill: boolean;
  start_date: string;
  end_date?: string;
  is_active: boolean;
  schedules?: MedicationSchedule[];
}

export type AdherenceStatus = 'UPCOMING' | 'TAKEN' | 'SKIPPED' | 'MISSED';

export interface MedicationLog {
  id: string;
  medication_id: string;
  medication_name: string;
  dosage: string;
  unit: string;
  instructions?: string;
  schedule_id: string;
  label?: string;
  scheduled_date: string;
  scheduled_time: string;
  status: AdherenceStatus;
  taken_at?: string;
  recorded_by_user_id?: string;
  recorded_by_name?: string;
  notes?: string;
}

export type AppointmentStatus = 'SCHEDULED' | 'COMPLETED' | 'CANCELLED';
export type AppointmentType = 'IN_PERSON' | 'VIRTUAL' | 'HOME_VISIT';

export interface Appointment {
  id: string;
  profile_id: string;
  created_by_user_id?: string;
  created_by_name?: string;
  doctor_name: string;
  specialty?: string;
  hospital_clinic?: string;
  location?: string;
  appointment_date: string;
  appointment_time: string;
  appointment_type: AppointmentType;
  notes?: string;
  status: AppointmentStatus;
}

export interface AdherenceStats {
  period_days: number;
  total_scheduled: number;
  taken: number;
  missed: number;
  skipped: number;
  upcoming: number;
  adherence_rate: number;
  daily_breakdown: {
    date: string;
    day_name: string;
    total: number;
    taken: number;
    missed: number;
    skipped: number;
  }[];
}

export interface AppNotification {
  id: string;
  type: string;
  channel: string;
  title: string;
  message: string;
  recipient_email: string;
  status: 'QUEUED' | 'SENT' | 'FAILED' | 'SIMULATED_NOT_CONFIGURED';
  error_message?: string;
  delivery_attempts: number;
  sent_at?: string;
  is_read: boolean;
  created_at: string;
}
