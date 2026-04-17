import { Filter, ChevronDown } from 'lucide-react'
import type { Department, MeetingStatus } from '../../types'
import { formatDepartment } from '../../lib/utils'

interface FilterBarProps {
  department: Department | ''
  status: MeetingStatus | ''
  departments: string[]
  onDepartmentChange: (val: Department | '') => void
  onStatusChange: (val: MeetingStatus | '') => void
}

const STATUSES: MeetingStatus[] = ['SCHEDULED', 'COMPLETED', 'CANCELLED', 'RESCHEDULED']

export function FilterBar({
  department,
  status,
  departments,
  onDepartmentChange,
  onStatusChange,
}: FilterBarProps) {
  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1.5 text-sm text-gray-500">
        <Filter size={14} />
        <span className="font-medium">Filters:</span>
      </div>

      {/* Department filter */}
      <div className="relative">
        <select
          value={department}
          onChange={(e) => onDepartmentChange(e.target.value as Department | '')}
          className="appearance-none pl-3 pr-7 py-1.5 text-sm bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-teal/30 focus:border-brand-teal cursor-pointer"
        >
          <option value="">All Departments</option>
          {departments.map((d) => (
            <option key={d} value={d}>
              {formatDepartment(d)}
            </option>
          ))}
        </select>
        <ChevronDown
          size={14}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
        />
      </div>

      {/* Status filter */}
      <div className="relative">
        <select
          value={status}
          onChange={(e) => onStatusChange(e.target.value as MeetingStatus | '')}
          className="appearance-none pl-3 pr-7 py-1.5 text-sm bg-white border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-teal/30 focus:border-brand-teal cursor-pointer"
        >
          <option value="">All Statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s.charAt(0) + s.slice(1).toLowerCase()}
            </option>
          ))}
        </select>
        <ChevronDown
          size={14}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
        />
      </div>
    </div>
  )
}
