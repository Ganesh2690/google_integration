import axios from 'axios'
import type { Meeting, MeetingCreate, MeetingUpdate, User } from '../types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api/v1',
  headers: { 'Content-Type': 'application/json' },
})

// Auth token injection
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Meetings
export const fetchMeetings = async (params?: {
  from?: string
  to?: string
  department?: string
  status?: string
  host_id?: string
}): Promise<Meeting[]> => {
  const { data } = await api.get<Meeting[]>('/meetings', { params })
  return data
}

export const fetchMeeting = async (id: string): Promise<Meeting> => {
  const { data } = await api.get<Meeting>(`/meetings/${id}`)
  return data
}

export const createMeeting = async (payload: MeetingCreate): Promise<Meeting> => {
  const { data } = await api.post<Meeting>('/meetings', payload)
  return data
}

export const updateMeeting = async (id: string, payload: MeetingUpdate): Promise<Meeting> => {
  const { data } = await api.patch<Meeting>(`/meetings/${id}`, payload)
  return data
}

export const cancelMeeting = async (id: string): Promise<Meeting> => {
  const { data } = await api.post<Meeting>(`/meetings/${id}/cancel`)
  return data
}

export const completeMeeting = async (id: string): Promise<Meeting> => {
  const { data } = await api.post<Meeting>(`/meetings/${id}/complete`)
  return data
}

// Users
export const fetchInterviewers = async (): Promise<User[]> => {
  const { data } = await api.get<User[]>('/users/interviewers')
  return data
}

// Departments
export const fetchDepartments = async (): Promise<string[]> => {
  const { data } = await api.get<string[]>('/departments')
  return data
}

export default api
