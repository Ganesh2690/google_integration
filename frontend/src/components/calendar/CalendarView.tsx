import { useRef, useEffect } from 'react'
import type { RefObject } from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import type { EventContentArg } from '@fullcalendar/core'
import type { Meeting } from '../../types'
import { MeetingCard } from './MeetingCard'

type ViewType = 'dayGridMonth' | 'timeGridWeek' | 'timeGridDay'

interface CalendarViewProps {
  meetings: Meeting[]
  currentDate: Date
  view: ViewType
  onDateChange: (date: Date) => void
  onMeetingClick: (meeting: Meeting) => void
  calendarRef?: RefObject<FullCalendar>
}

export function CalendarView({
  meetings,
  currentDate,
  view,
  onDateChange,
  onMeetingClick,
  calendarRef,
}: CalendarViewProps) {
  const internalRef = useRef<FullCalendar>(null)
  const calRef = calendarRef ?? internalRef

  // Sync view changes imperatively
  useEffect(() => {
    calRef.current?.getApi().changeView(view)
  }, [view]) // eslint-disable-line react-hooks/exhaustive-deps

  const events = meetings.map((m) => ({
    id: m.id,
    title: m.candidate_name,
    start: m.date,
    extendedProps: { meeting: m },
  }))

  function renderEventContent(info: EventContentArg) {
    const meeting = info.event.extendedProps.meeting as Meeting
    return <MeetingCard meeting={meeting} onClick={onMeetingClick} />
  }

  // Sync FullCalendar when currentDate changes from toolbar
  const handleDatesSet = () => {
    const api = calRef.current?.getApi()
    if (api) {
      onDateChange(api.getDate())
    }
  }

  // Expose navigation to parent via imperative handle via callback
  // Parent calls calRef.current.getApi() via the passed ref prop
  return (
    <div className="fc-wrapper">
      <FullCalendar
        ref={calRef}
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView={view}
        initialDate={currentDate}
        events={events}
        eventContent={renderEventContent}
        headerToolbar={false}
        datesSet={handleDatesSet}
        height="auto"
        dayMaxEvents={3}
        moreLinkClick="popover"
        eventDisplay="block"
        nowIndicator
      />
    </div>
  )
}
