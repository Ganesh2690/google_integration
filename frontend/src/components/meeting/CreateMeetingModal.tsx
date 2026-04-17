import { useEffect } from 'react'
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import type { Department, LocationType, Meeting } from '../../types'
import { createMeeting, updateMeeting } from '../../lib/api'
import { formatDepartment } from '../../lib/utils'

const DEPARTMENTS: Department[] = [
  'CARDIOLOGY',
  'LABORATORY',
  'NURSING',
  'PHARMACY',
  'RADIOLOGY',
  'ADMINISTRATION',
  'CLINICAL_COORDINATION',
]
const LOCATION_TYPES: { value: LocationType; label: string }[] = [
  { value: 'GOOGLE_MEET', label: 'Google Meet' },
  { value: 'ZOOM', label: 'Zoom' },
  { value: 'MS_TEAMS', label: 'MS Teams' },
  { value: 'PHYSICAL', label: 'Physical' },
]
const DURATIONS = [15, 30, 45, 60, 90]

const schema = z.object({
  candidate_name: z.string().min(1).max(120),
  candidate_email: z.string().email().optional().or(z.literal('')),
  position: z.string().min(1).max(120),
  department: z.enum([
    'CARDIOLOGY',
    'LABORATORY',
    'NURSING',
    'PHARMACY',
    'RADIOLOGY',
    'ADMINISTRATION',
    'CLINICAL_COORDINATION',
  ]),
  host_id: z.string().min(1),
  date: z.string().min(1, 'Date is required'),
  time: z.string().min(1, 'Time is required'),
  duration_mins: z.number().int().min(15).max(240),
  location_type: z.enum(['GOOGLE_MEET', 'ZOOM', 'MS_TEAMS', 'PHYSICAL']),
  location_detail: z.string().optional(),
  notes: z.string().optional(),
})

type FormValues = z.infer<typeof schema>

interface CreateMeetingModalProps {
  editMeeting?: Meeting
  interviewers: Array<{ id: string; name: string }>
  onClose: () => void
  onSuccess: () => void
}

export function CreateMeetingModal({
  editMeeting,
  interviewers,
  onClose,
  onSuccess,
}: CreateMeetingModalProps) {
  const queryClient = useQueryClient()
  const isEdit = !!editMeeting

  const defaultDate = editMeeting ? format(new Date(editMeeting.date), 'yyyy-MM-dd') : ''
  const defaultTime = editMeeting ? format(new Date(editMeeting.date), 'HH:mm') : ''

  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors },
    reset,
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      candidate_name: editMeeting?.candidate_name ?? '',
      candidate_email: editMeeting?.candidate_email ?? '',
      position: editMeeting?.position ?? '',
      department: (editMeeting?.department as Department) ?? 'NURSING',
      host_id: editMeeting?.host_id ?? (interviewers[0]?.id ?? ''),
      date: defaultDate,
      time: defaultTime,
      duration_mins: editMeeting?.duration_mins ?? 30,
      location_type: (editMeeting?.location_type as LocationType) ?? 'GOOGLE_MEET',
      location_detail: editMeeting?.location_detail ?? '',
      notes: editMeeting?.notes ?? '',
    },
  })

  const locationType = watch('location_type')

  useEffect(() => {
    reset({
      candidate_name: editMeeting?.candidate_name ?? '',
      candidate_email: editMeeting?.candidate_email ?? '',
      position: editMeeting?.position ?? '',
      department: (editMeeting?.department as Department) ?? 'NURSING',
      host_id: editMeeting?.host_id ?? (interviewers[0]?.id ?? ''),
      date: defaultDate,
      time: defaultTime,
      duration_mins: editMeeting?.duration_mins ?? 30,
      location_type: (editMeeting?.location_type as LocationType) ?? 'GOOGLE_MEET',
      location_detail: editMeeting?.location_detail ?? '',
      notes: editMeeting?.notes ?? '',
    })
  }, [editMeeting]) // eslint-disable-line react-hooks/exhaustive-deps

  const createMut = useMutation({
    mutationFn: (values: FormValues) => {
      const dateTime = new Date(`${values.date}T${values.time}:00Z`).toISOString()
      return createMeeting({
        candidate_name: values.candidate_name,
        candidate_email: values.candidate_email || undefined,
        position: values.position,
        department: values.department,
        host_id: values.host_id,
        date: dateTime,
        duration_mins: values.duration_mins,
        location_type: values.location_type,
        location_detail: values.location_detail || undefined,
        notes: values.notes || undefined,
        participants: [],
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] })
      onSuccess()
    },
  })

  const updateMut = useMutation({
    mutationFn: (values: FormValues) => {
      const dateTime = new Date(`${values.date}T${values.time}:00Z`).toISOString()
      return updateMeeting(editMeeting!.id, {
        candidate_name: values.candidate_name,
        candidate_email: values.candidate_email || undefined,
        position: values.position,
        department: values.department,
        host_id: values.host_id,
        date: dateTime,
        duration_mins: values.duration_mins,
        location_type: values.location_type,
        location_detail: values.location_detail || undefined,
        notes: values.notes || undefined,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['meetings'] })
      onSuccess()
    },
  })

  const onSubmit = (values: FormValues) => {
    if (isEdit) {
      updateMut.mutate(values)
    } else {
      createMut.mutate(values)
    }
  }

  const isPending = createMut.isPending || updateMut.isPending

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-modal w-full max-w-lg max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between px-6 pt-6 pb-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {isEdit ? 'Reschedule Interview' : 'Schedule Interview'}
            </h2>
            <p className="text-sm text-gray-500 mt-0.5">
              {isEdit ? 'Update the interview details.' : 'Fill in details to schedule an interview.'}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        <div className="border-t border-gray-100 mx-6" />

        <form onSubmit={handleSubmit(onSubmit)} className="px-6 py-4 space-y-4">
          {/* Candidate Name */}
          <Field label="Candidate Name" required error={errors.candidate_name?.message}>
            <input
              {...register('candidate_name')}
              placeholder="e.g. Maria Garcia"
              className={inputCls(!!errors.candidate_name)}
            />
          </Field>

          {/* Candidate Email */}
          <Field label="Candidate Email" error={errors.candidate_email?.message}>
            <input
              {...register('candidate_email')}
              type="email"
              placeholder="candidate@example.com"
              className={inputCls(!!errors.candidate_email)}
            />
          </Field>

          {/* Position */}
          <Field label="Position" required error={errors.position?.message}>
            <input
              {...register('position')}
              placeholder="e.g. Registered Nurse"
              className={inputCls(!!errors.position)}
            />
          </Field>

          {/* Department */}
          <Field label="Department" required error={errors.department?.message}>
            <select {...register('department')} className={inputCls(!!errors.department)}>
              {DEPARTMENTS.map((d) => (
                <option key={d} value={d}>
                  {formatDepartment(d)}
                </option>
              ))}
            </select>
          </Field>

          {/* Interviewer */}
          <Field label="Interviewer / Host" required error={errors.host_id?.message}>
            <select {...register('host_id')} className={inputCls(!!errors.host_id)}>
              {interviewers.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.name}
                </option>
              ))}
            </select>
          </Field>

          {/* Date & Time */}
          <div className="grid grid-cols-2 gap-3">
            <Field label="Date" required error={errors.date?.message}>
              <input
                {...register('date')}
                type="date"
                className={inputCls(!!errors.date)}
              />
            </Field>
            <Field label="Time" required error={errors.time?.message}>
              <input
                {...register('time')}
                type="time"
                className={inputCls(!!errors.time)}
              />
            </Field>
          </div>

          {/* Duration */}
          <Field label="Duration" error={errors.duration_mins?.message}>
            <Controller
              name="duration_mins"
              control={control}
              render={({ field }) => (
                <div className="flex gap-2 flex-wrap">
                  {DURATIONS.map((d) => (
                    <button
                      key={d}
                      type="button"
                      onClick={() => field.onChange(d)}
                      className={`px-3 py-1.5 text-sm rounded-lg border transition-colors ${
                        field.value === d
                          ? 'bg-brand-teal text-white border-brand-teal'
                          : 'border-gray-200 text-gray-600 hover:border-brand-teal hover:text-brand-teal'
                      }`}
                    >
                      {d} min
                    </button>
                  ))}
                </div>
              )}
            />
          </Field>

          {/* Location Type */}
          <Field label="Location Type" error={errors.location_type?.message}>
            <div className="flex flex-wrap gap-2">
              {LOCATION_TYPES.map(({ value, label }) => (
                <label key={value} className="flex items-center gap-1.5 cursor-pointer">
                  <input
                    {...register('location_type')}
                    type="radio"
                    value={value}
                    className="accent-brand-teal"
                  />
                  <span className="text-sm text-gray-700">{label}</span>
                </label>
              ))}
            </div>
          </Field>

          {/* Location Detail (physical only) */}
          {locationType === 'PHYSICAL' && (
            <Field label="Location Detail" error={errors.location_detail?.message}>
              <input
                {...register('location_detail')}
                placeholder="e.g. Room 204, Building A"
                className={inputCls(!!errors.location_detail)}
              />
            </Field>
          )}

          {/* Notes */}
          <Field label="Notes" error={errors.notes?.message}>
            <textarea
              {...register('notes')}
              rows={3}
              placeholder="Additional notes…"
              className={`${inputCls(false)} resize-none`}
            />
          </Field>

          {/* Footer */}
          <div className="flex justify-end gap-3 pt-2 border-t border-gray-100">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isPending}
              className="px-5 py-2.5 text-sm bg-brand-teal text-white font-medium rounded-lg hover:bg-brand-tealDk disabled:opacity-60 transition-colors"
            >
              {isPending ? 'Saving…' : isEdit ? 'Save Changes' : 'Save & Schedule'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function inputCls(hasError: boolean) {
  return `w-full px-3 py-2 text-sm border rounded-lg focus:outline-none focus:ring-2 transition-colors ${
    hasError
      ? 'border-rose-300 focus:ring-rose-200'
      : 'border-gray-200 focus:ring-brand-teal/30 focus:border-brand-teal'
  }`
}

function Field({
  label,
  required,
  error,
  children,
}: {
  label: string
  required?: boolean
  error?: string
  children: React.ReactNode
}) {
  return (
    <div>
      <label className="block text-xs font-medium text-gray-600 mb-1.5">
        {label}
        {required && <span className="text-rose-500 ml-0.5">*</span>}
      </label>
      {children}
      {error && <p className="text-xs text-rose-500 mt-1">{error}</p>}
    </div>
  )
}
