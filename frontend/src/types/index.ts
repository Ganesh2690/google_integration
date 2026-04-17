export type MeetingStatus = 'DRAFT' | 'SCHEDULED' | 'COMPLETED' | 'CANCELLED' | 'RESCHEDULED'

export type LocationType = 'GOOGLE_MEET' | 'ZOOM' | 'MS_TEAMS' | 'PHYSICAL'

export type Department =
  | 'CARDIOLOGY'
  | 'LABORATORY'
  | 'NURSING'
  | 'PHARMACY'
  | 'RADIOLOGY'
  | 'ADMINISTRATION'
  | 'CLINICAL_COORDINATION'

export interface Meeting {
  id: string
  candidate_name: string
  candidate_email: string | null
  position: string
  department: Department
  host_id: string
  date: string
  duration_mins: number
  location_type: LocationType
  location_detail: string | null
  google_event_id: string | null
  meet_link: string | null
  notes: string | null
  participants: string[]
  status: MeetingStatus
  color_tag: string | null
  created_at: string
  updated_at: string
}

export interface MeetingCreate {
  candidate_name: string
  candidate_email?: string
  position: string
  department: Department
  host_id: string
  date: string
  duration_mins: number
  location_type: LocationType
  location_detail?: string
  notes?: string
  participants: string[]
}

export interface MeetingUpdate {
  candidate_name?: string
  candidate_email?: string
  position?: string
  department?: Department
  host_id?: string
  date?: string
  duration_mins?: number
  location_type?: LocationType
  location_detail?: string
  notes?: string
  participants?: string[]
  regenerate_meet_link?: boolean
}

export interface User {
  id: string
  email: string
  name: string
  role: string
}

export interface AuditLog {
  id: string
  meeting_id: string
  action: string
  actor_id: string
  payload: Record<string, unknown>
  created_at: string
}
