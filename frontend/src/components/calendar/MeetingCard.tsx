import { Clock } from 'lucide-react'
import { format } from 'date-fns'
import type { Meeting } from '../../types'
import { statusCardClasses, statusNameColor } from '../../lib/utils'

interface MeetingCardProps {
  meeting: Meeting
  onClick: (meeting: Meeting) => void
}

export function MeetingCard({ meeting, onClick }: MeetingCardProps) {
  const time = format(new Date(meeting.date), 'hh:mm aa')

  return (
    <button
      onClick={() => onClick(meeting)}
      className={`w-full text-left rounded-lg border px-2.5 py-1.5 text-xs transition-opacity hover:opacity-90 ${statusCardClasses(meeting.status)}`}
    >
      <p className={`truncate text-[11px] ${statusNameColor(meeting.status)}`}>
        {meeting.candidate_name}
      </p>
      <p className="truncate text-[10px] text-gray-500 mt-0.5">{meeting.position}</p>
      <div className="flex items-center gap-1 mt-1 text-[10px] text-gray-500">
        <Clock size={10} className="shrink-0" />
        <span>{time}</span>
      </div>
    </button>
  )
}
