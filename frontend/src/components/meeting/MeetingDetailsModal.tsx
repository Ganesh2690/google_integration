import { useState } from 'react'
import { X, User, Briefcase, Users, Calendar, Clock, MapPin, Video, Copy, ExternalLink } from 'lucide-react'
import { format } from 'date-fns'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { Meeting, MeetingUpdate } from '../../types'
import { statusPillClasses, formatDepartment, formatLocationLabel } from '../../lib/utils'
import { cancelMeeting, completeMeeting, updateMeeting } from '../../lib/api'
import { CreateMeetingModal } from './CreateMeetingModal'

interface MeetingDetailsModalProps {
  meeting: Meeting
  interviewers: Array<{ id: string; name: string }>
  onClose: () => void
}

export function MeetingDetailsModal({ meeting, interviewers, onClose }: MeetingDetailsModalProps) {
  const [showCancelConfirm, setShowCancelConfirm] = useState(false)
  const [showReschedule, setShowReschedule] = useState(false)
  const [copied, setCopied] = useState(false)
  const queryClient = useQueryClient()

  const hostName = interviewers.find((u) => u.id === meeting.host_id)?.name ?? meeting.host_id

  const cancelMut = useMutation({
    mutationFn: () => cancelMeeting(meeting.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] })
      onClose()
    },
  })

  const completeMut = useMutation({
    mutationFn: () => completeMeeting(meeting.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] })
      onClose()
    },
  })

  const confirmMut = useMutation({
    mutationFn: () =>
      updateMeeting(meeting.id, { status: 'SCHEDULED' } as unknown as MeetingUpdate),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] })
      onClose()
    },
  })

  const handleCopyLink = async () => {
    if (meeting.meet_link) {
      await navigator.clipboard.writeText(meeting.meet_link)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const meetingDate = new Date(meeting.date)
  const locationLabel = formatLocationLabel(meeting.location_type, meeting.location_detail)
  const hasMeetLink = !!meeting.meet_link

  if (showReschedule) {
    return (
      <CreateMeetingModal
        editMeeting={meeting}
        interviewers={interviewers}
        onClose={() => setShowReschedule(false)}
        onSuccess={() => {
          setShowReschedule(false)
          onClose()
        }}
      />
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-modal w-full max-w-md max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between px-6 pt-6 pb-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Interview Details</h2>
            <p className="text-sm text-gray-500 mt-0.5">View and manage details of the interview.</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Status badges */}
        <div className="flex items-center gap-2 px-6 pb-4">
          <span
            className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${statusPillClasses(meeting.status)}`}
          >
            {meeting.status.charAt(0) + meeting.status.slice(1).toLowerCase()}
          </span>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600 border border-gray-200">
            <Video size={12} />
            Video
          </span>
        </div>

        <div className="border-t border-gray-100 mx-6" />

        {/* Candidate Information */}
        <div className="px-6 pt-4 pb-2">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
            Candidate Information
          </p>
          <div className="space-y-3">
            <InfoRow icon={User} label="Candidate Name" value={meeting.candidate_name} />
            <InfoRow icon={Briefcase} label="Position" value={meeting.position} />
            <InfoRow icon={Users} label="Department" value={formatDepartment(meeting.department)} />
          </div>
        </div>

        <div className="border-t border-gray-100 mx-6 my-2" />

        {/* Schedule */}
        <div className="px-6 pt-2 pb-4">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
            Schedule
          </p>
          <div className="space-y-3">
            <InfoRow
              icon={Calendar}
              label="Date"
              value={format(meetingDate, 'MMMM d, yyyy')}
            />
            <InfoRow
              icon={Clock}
              label="Time"
              value={format(meetingDate, 'hh:mm aa')}
            />
            <InfoRow icon={MapPin} label="Location" value={locationLabel} />
            <InfoRow icon={User} label="Interviewer" value={hostName} />

            {/* Meeting link */}
            {hasMeetLink && (
              <div className="flex items-start gap-3">
                <Video size={16} className="text-gray-400 shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-gray-500 mb-1.5">Meeting Link</p>
                  <div className="rounded-lg border border-gray-200 bg-gray-50 overflow-hidden">
                    <div className="flex items-center gap-2 px-3 py-2">
                      <a
                        href={meeting.meet_link ?? '#'}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 text-xs text-brand-teal break-all hover:underline"
                      >
                        {meeting.meet_link}
                      </a>
                      <button
                        onClick={handleCopyLink}
                        className="shrink-0 p-1 rounded hover:bg-gray-200 transition-colors"
                        title="Copy link"
                      >
                        <Copy size={12} className="text-gray-500" />
                      </button>
                    </div>
                    {copied && (
                      <p className="text-xs text-emerald-600 px-3 pb-1">Copied!</p>
                    )}
                  </div>

                  {meeting.status === 'SCHEDULED' && (
                    <a
                      href={meeting.meet_link ?? '#'}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-2 flex w-full items-center justify-center gap-2 bg-brand-teal hover:bg-brand-tealDk text-white text-sm font-medium py-2.5 px-4 rounded-lg transition-colors"
                    >
                      <ExternalLink size={14} />
                      Join Video Meeting
                    </a>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Cancel confirm dialog */}
        {showCancelConfirm && (
          <div className="mx-6 mb-4 p-4 bg-rose-50 border border-rose-200 rounded-xl">
            <p className="text-sm font-medium text-rose-800 mb-1">Cancel this interview?</p>
            <p className="text-xs text-rose-600 mb-3">This action cannot be undone.</p>
            <div className="flex gap-2">
              <button
                onClick={() => setShowCancelConfirm(false)}
                className="flex-1 py-1.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                No, keep it
              </button>
              <button
                onClick={() => cancelMut.mutate()}
                disabled={cancelMut.isPending}
                className="flex-1 py-1.5 text-sm bg-rose-600 text-white rounded-lg hover:bg-rose-700 disabled:opacity-60 transition-colors"
              >
                {cancelMut.isPending ? 'Cancelling…' : 'Yes, cancel'}
              </button>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 px-6 py-4 border-t border-gray-100">
          {meeting.status === 'SCHEDULED' || meeting.status === 'RESCHEDULED' ? (
            <>
              <button
                onClick={onClose}
                className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => setShowReschedule(true)}
                className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Reschedule
              </button>
              <button
                onClick={() => setShowCancelConfirm(true)}
                className="px-4 py-2 text-sm border border-rose-200 text-rose-600 rounded-lg hover:bg-rose-50 transition-colors"
              >
                Cancel Interview
              </button>
              <button
                onClick={() => completeMut.mutate()}
                disabled={completeMut.isPending}
                className="px-4 py-2 text-sm border border-emerald-200 text-emerald-700 rounded-lg hover:bg-emerald-50 disabled:opacity-60 transition-colors"
              >
                Mark Completed
              </button>
              <button
                onClick={() => confirmMut.mutate()}
                disabled={confirmMut.isPending}
                className="px-4 py-2 text-sm bg-brand-teal text-white rounded-lg hover:bg-brand-tealDk disabled:opacity-60 transition-colors"
              >
                {confirmMut.isPending ? 'Saving…' : 'Confirm Interview'}
              </button>
            </>
          ) : (
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

function InfoRow({
  icon: Icon,
  label,
  value,
}: {
  icon: React.ElementType
  label: string
  value: string
}) {
  return (
    <div className="flex items-start gap-3">
      <Icon size={16} className="text-gray-400 shrink-0 mt-0.5" />
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-sm font-medium text-gray-900">{value}</p>
      </div>
    </div>
  )
}
