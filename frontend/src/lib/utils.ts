import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import type { MeetingStatus } from '../types'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function statusCardClasses(status: MeetingStatus): string {
  switch (status) {
    case 'SCHEDULED':
      return 'bg-slate-100 text-slate-800 border-slate-200'
    case 'COMPLETED':
      return 'bg-emerald-100 text-emerald-800 border-emerald-200'
    case 'CANCELLED':
      return 'bg-rose-100 text-rose-800 border-rose-200'
    case 'RESCHEDULED':
      return 'bg-blue-100 text-blue-800 border-blue-200'
    case 'DRAFT':
      return 'bg-gray-100 text-gray-700 border-gray-200'
    default:
      return 'bg-slate-100 text-slate-800 border-slate-200'
  }
}

export function statusNameColor(status: MeetingStatus): string {
  switch (status) {
    case 'SCHEDULED':
      return 'text-slate-800 font-semibold'
    case 'COMPLETED':
      return 'text-emerald-800 font-semibold'
    case 'CANCELLED':
      return 'text-rose-700 font-semibold'
    case 'RESCHEDULED':
      return 'text-blue-700 font-semibold'
    default:
      return 'text-slate-800 font-semibold'
  }
}

export function statusPillClasses(status: MeetingStatus): string {
  switch (status) {
    case 'SCHEDULED':
      return 'bg-blue-100 text-blue-700 border border-blue-200'
    case 'COMPLETED':
      return 'bg-emerald-100 text-emerald-700 border border-emerald-200'
    case 'CANCELLED':
      return 'bg-rose-100 text-rose-700 border border-rose-200'
    case 'RESCHEDULED':
      return 'bg-amber-100 text-amber-700 border border-amber-200'
    default:
      return 'bg-gray-100 text-gray-600 border border-gray-200'
  }
}

export function formatDepartment(dept: string): string {
  return dept
    .split('_')
    .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
    .join(' ')
}

export function formatLocationLabel(locationType: string, locationDetail?: string | null): string {
  switch (locationType) {
    case 'GOOGLE_MEET':
      return locationDetail ?? 'Google Meet'
    case 'ZOOM':
      return locationDetail ?? 'Zoom Meeting'
    case 'MS_TEAMS':
      return locationDetail ?? 'Microsoft Teams'
    case 'PHYSICAL':
      return locationDetail ?? 'Physical Location'
    default:
      return locationDetail ?? locationType
  }
}
