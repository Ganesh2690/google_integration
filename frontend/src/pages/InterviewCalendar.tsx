import { useState, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ChevronLeft, ChevronRight, Download, Plus } from 'lucide-react'
import { format, addMonths, subMonths, addWeeks, subWeeks, addDays, subDays } from 'date-fns'
import type FullCalendar from '@fullcalendar/react'
import { fetchMeetings, fetchInterviewers, fetchDepartments } from '../lib/api'
import type { Department, Meeting, MeetingStatus } from '../types'
import { CalendarView } from '../components/calendar/CalendarView'
import { FilterBar } from '../components/calendar/FilterBar'
import { MeetingDetailsModal } from '../components/meeting/MeetingDetailsModal'
import { CreateMeetingModal } from '../components/meeting/CreateMeetingModal'
import { cn } from '../lib/utils'

type ViewMode = 'dayGridMonth' | 'timeGridWeek' | 'timeGridDay'

const VIEW_LABELS: { key: ViewMode; label: string }[] = [
  { key: 'dayGridMonth', label: 'Month' },
  { key: 'timeGridWeek', label: 'Week' },
  { key: 'timeGridDay', label: 'Day' },
]

export function InterviewCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date(2026, 2, 24)) // March 24 2026
  const [view, setView] = useState<ViewMode>('dayGridMonth')
  const [departmentFilter, setDepartmentFilter] = useState<Department | ''>('')
  const [statusFilter, setStatusFilter] = useState<MeetingStatus | ''>('')
  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const calRef = useRef<FullCalendar>(null)

  const { data: meetings = [] } = useQuery({
    queryKey: ['meetings', departmentFilter, statusFilter],
    queryFn: () =>
      fetchMeetings({
        department: departmentFilter || undefined,
        status: statusFilter || undefined,
      }),
  })

  const { data: interviewers = [] } = useQuery({
    queryKey: ['interviewers'],
    queryFn: fetchInterviewers,
  })

  const { data: departments = [] } = useQuery({
    queryKey: ['departments'],
    queryFn: fetchDepartments,
  })

  const navigatePrev = () => {
    const api = calRef.current?.getApi()
    if (api) {
      api.prev()
      setCurrentDate(api.getDate())
    } else {
      if (view === 'dayGridMonth') setCurrentDate((d) => subMonths(d, 1))
      else if (view === 'timeGridWeek') setCurrentDate((d) => subWeeks(d, 1))
      else setCurrentDate((d) => subDays(d, 1))
    }
  }

  const navigateNext = () => {
    const api = calRef.current?.getApi()
    if (api) {
      api.next()
      setCurrentDate(api.getDate())
    } else {
      if (view === 'dayGridMonth') setCurrentDate((d) => addMonths(d, 1))
      else if (view === 'timeGridWeek') setCurrentDate((d) => addWeeks(d, 1))
      else setCurrentDate((d) => addDays(d, 1))
    }
  }

  const navigateToday = () => {
    const api = calRef.current?.getApi()
    if (api) {
      api.today()
      setCurrentDate(api.getDate())
    } else {
      setCurrentDate(new Date())
    }
  }

  const handleViewChange = (v: ViewMode) => {
    setView(v)
    const api = calRef.current?.getApi()
    if (api) api.changeView(v)
  }

  const currentLabel =
    view === 'dayGridMonth'
      ? format(currentDate, 'MMMM yyyy')
      : view === 'timeGridWeek'
      ? `${format(currentDate, 'MMM d')} – Week`
      : format(currentDate, 'EEEE, MMM d yyyy')

  const handleExport = () => {
    const lines = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//ClinReady//Interview Calendar//EN',
      ...meetings.flatMap((m) => [
        'BEGIN:VEVENT',
        `DTSTART:${m.date.replace(/[-:]/g, '').replace('.000Z', 'Z')}`,
        `SUMMARY:${m.candidate_name} - ${m.position}`,
        `DESCRIPTION:${m.department} | ${m.status}`,
        'END:VEVENT',
      ]),
      'END:VCALENDAR',
    ]
    const blob = new Blob([lines.join('\r\n')], { type: 'text/calendar' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'interviews.ics'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex flex-col min-h-full">
      {/* Teal Banner */}
      <div className="bg-[#0E7C86] px-6 py-5">
        <p className="text-sm text-teal-200 mb-1">
          <span className="opacity-75">Home</span>
          <span className="opacity-75 mx-1">/</span>
          <span className="font-medium text-white">Interview Calendar</span>
        </p>
        <h1 className="text-2xl font-bold text-white">Interview Calender</h1>
        <p className="text-sm text-teal-100 mt-0.5">Manage and track candidate interviews</p>
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-3 px-6 py-3 bg-white border-b border-gray-200 flex-wrap">
        {/* Navigation */}
        <div className="flex items-center gap-1">
          <button
            onClick={navigatePrev}
            className="p-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
          >
            <ChevronLeft size={16} className="text-gray-600" />
          </button>
          <button
            onClick={navigateToday}
            className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Today
          </button>
          <button
            onClick={navigateNext}
            className="p-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
          >
            <ChevronRight size={16} className="text-gray-600" />
          </button>
          <h2 className="ml-3 text-lg font-semibold text-gray-900">{currentLabel}</h2>
        </div>

        {/* Filters */}
        <FilterBar
          department={departmentFilter}
          status={statusFilter}
          departments={departments}
          onDepartmentChange={setDepartmentFilter}
          onStatusChange={setStatusFilter}
        />

        {/* Right side */}
        <div className="flex items-center gap-2 ml-auto">
          {/* View toggles */}
          <div className="flex rounded-lg border border-gray-200 overflow-hidden">
            {VIEW_LABELS.map(({ key, label }) => (
              <button
                key={key}
                onClick={() => handleViewChange(key)}
                className={cn(
                  'px-3 py-1.5 text-sm font-medium transition-colors',
                  view === key
                    ? 'bg-gray-900 text-white'
                    : 'bg-white text-gray-600 hover:bg-gray-50'
                )}
              >
                {label}
              </button>
            ))}
          </div>

          <button
            onClick={handleExport}
            className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
            title="Export ICS"
          >
            <Download size={16} className="text-gray-600" />
          </button>

          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-brand-teal text-white text-sm font-medium rounded-lg hover:bg-brand-tealDk transition-colors"
          >
            <Plus size={16} />
            Create Meeting
          </button>
        </div>
      </div>

      {/* Calendar */}
      <div className="flex-1 bg-white px-6 py-4">
        <CalendarView
          calendarRef={calRef}
          meetings={meetings}
          currentDate={currentDate}
          view={view}
          onDateChange={setCurrentDate}
          onMeetingClick={setSelectedMeeting}
        />
      </div>

      {/* Footer */}
      <footer className="py-4 text-center text-sm text-gray-500 border-t border-gray-100">
        2026 © <span className="text-brand-teal font-medium">ClinReady</span>, All Rights Reserved
      </footer>

      {/* Modals */}
      {selectedMeeting && (
        <MeetingDetailsModal
          meeting={selectedMeeting}
          interviewers={interviewers}
          onClose={() => setSelectedMeeting(null)}
        />
      )}

      {showCreateModal && (
        <CreateMeetingModal
          interviewers={interviewers}
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => setShowCreateModal(false)}
        />
      )}
    </div>
  )
}
