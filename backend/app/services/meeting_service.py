from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.exceptions import InvalidStateTransition, NotFoundError
from app.models.meeting import AuditLog, Meeting, MeetingStatus, User
from app.schemas.meeting import MeetingCreate, MeetingListFilters, MeetingUpdate
from app.services.google_service import google_service

logger = get_logger(__name__)

ALLOWED_TRANSITIONS: dict[MeetingStatus, set[MeetingStatus]] = {
    MeetingStatus.SCHEDULED: {
        MeetingStatus.COMPLETED,
        MeetingStatus.CANCELLED,
        MeetingStatus.RESCHEDULED,
    },
    MeetingStatus.RESCHEDULED: {MeetingStatus.SCHEDULED},
    MeetingStatus.COMPLETED: set(),
    MeetingStatus.CANCELLED: set(),
    MeetingStatus.DRAFT: {MeetingStatus.SCHEDULED, MeetingStatus.CANCELLED},
}


def _assert_transition(current: MeetingStatus, target: MeetingStatus) -> None:
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise InvalidStateTransition(current.value, target.value)


class MeetingService:
    async def list_meetings(self, db: AsyncSession, filters: MeetingListFilters) -> list[Meeting]:
        stmt = select(Meeting).options(selectinload(Meeting.host))
        if filters.from_date:
            stmt = stmt.where(Meeting.date >= filters.from_date)
        if filters.to_date:
            stmt = stmt.where(Meeting.date <= filters.to_date)
        if filters.department:
            stmt = stmt.where(Meeting.department == filters.department)
        if filters.status:
            stmt = stmt.where(Meeting.status == filters.status)
        if filters.host_id:
            stmt = stmt.where(Meeting.host_id == filters.host_id)
        stmt = stmt.order_by(Meeting.date)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_meeting(self, db: AsyncSession, meeting_id: str) -> Meeting:
        stmt = (
            select(Meeting)
            .options(selectinload(Meeting.host), selectinload(Meeting.audit_logs))
            .where(Meeting.id == meeting_id)
        )
        result = await db.execute(stmt)
        meeting = result.scalar_one_or_none()
        if meeting is None:
            raise NotFoundError(f"Meeting '{meeting_id}' not found.")
        return meeting

    async def create_meeting(
        self, db: AsyncSession, payload: MeetingCreate, actor_id: str
    ) -> Meeting:
        meeting_id = str(uuid.uuid4())

        # Resolve host tokens for Google Calendar
        host_tokens = await self._get_host_tokens(db, payload.host_id)

        meet_link: str | None = None
        google_event_id: str | None = None

        from app.models.meeting import LocationType

        if payload.location_type == LocationType.GOOGLE_MEET and host_tokens:
            end_dt = payload.date + timedelta(minutes=payload.duration_mins)
            try:
                result = await google_service.create_event_with_meet(
                    summary=f"Interview: {payload.candidate_name} - {payload.position}",
                    description=payload.notes or "",
                    start_iso=payload.date.isoformat(),
                    end_iso=end_dt.isoformat(),
                    attendees=list(payload.participants)
                    + ([payload.candidate_email] if payload.candidate_email else []),
                    tokens=host_tokens,
                )
                meet_link = result["meet_link"]
                google_event_id = result["event_id"]
            except Exception as exc:
                logger.warning("google_meet_creation_skipped", reason=str(exc))

        meeting = Meeting(
            id=meeting_id,
            candidate_name=payload.candidate_name,
            candidate_email=str(payload.candidate_email) if payload.candidate_email else None,
            position=payload.position,
            department=payload.department,
            host_id=payload.host_id,
            date=payload.date,
            duration_mins=payload.duration_mins,
            location_type=payload.location_type,
            location_detail=payload.location_detail,
            notes=payload.notes,
            participants=[str(p) for p in payload.participants],
            status=MeetingStatus.SCHEDULED,
            meet_link=meet_link,
            google_event_id=google_event_id,
        )
        db.add(meeting)
        await self._write_audit(db, meeting_id, "CREATED", actor_id, payload.model_dump())
        await db.commit()
        await db.refresh(meeting)
        return meeting

    async def update_meeting(
        self,
        db: AsyncSession,
        meeting_id: str,
        payload: MeetingUpdate,
        actor_id: str,
    ) -> Meeting:
        meeting = await self.get_meeting(db, meeting_id)
        update_data = payload.model_dump(exclude_unset=True, exclude={"regenerate_meet_link"})

        for field, value in update_data.items():
            if field == "participants" and value is not None:
                setattr(meeting, field, [str(p) for p in value])
            elif field == "candidate_email" and value is not None:
                setattr(meeting, field, str(value))
            else:
                setattr(meeting, field, value)

        meeting.updated_at = datetime.now(timezone.utc)

        # Sync to Google if event exists
        if meeting.google_event_id and meeting.host:
            host_tokens = meeting.host.google_tokens
            if host_tokens:
                patch: dict[str, Any] = {}
                if payload.date:
                    end_dt = payload.date + timedelta(minutes=meeting.duration_mins)
                    patch["start"] = {"dateTime": payload.date.isoformat(), "timeZone": "UTC"}
                    patch["end"] = {"dateTime": end_dt.isoformat(), "timeZone": "UTC"}
                if patch:
                    try:
                        await google_service.update_event(
                            meeting.google_event_id, patch, host_tokens
                        )
                    except Exception as exc:
                        logger.warning("google_update_skipped", reason=str(exc))

        await self._write_audit(db, meeting_id, "UPDATED", actor_id, update_data)
        await db.commit()
        await db.refresh(meeting)
        return meeting

    async def cancel_meeting(self, db: AsyncSession, meeting_id: str, actor_id: str) -> Meeting:
        meeting = await self.get_meeting(db, meeting_id)
        _assert_transition(meeting.status, MeetingStatus.CANCELLED)
        meeting.status = MeetingStatus.CANCELLED
        meeting.updated_at = datetime.now(timezone.utc)

        if meeting.google_event_id and meeting.host and meeting.host.google_tokens:
            try:
                await google_service.cancel_event(
                    meeting.google_event_id, meeting.host.google_tokens
                )
            except Exception as exc:
                logger.warning("google_cancel_skipped", reason=str(exc))

        await self._write_audit(db, meeting_id, "CANCELLED", actor_id, {})
        await db.commit()
        await db.refresh(meeting)
        return meeting

    async def complete_meeting(self, db: AsyncSession, meeting_id: str, actor_id: str) -> Meeting:
        meeting = await self.get_meeting(db, meeting_id)
        _assert_transition(meeting.status, MeetingStatus.COMPLETED)
        meeting.status = MeetingStatus.COMPLETED
        meeting.updated_at = datetime.now(timezone.utc)
        await self._write_audit(db, meeting_id, "COMPLETED", actor_id, {})
        await db.commit()
        await db.refresh(meeting)
        return meeting

    async def reschedule_meeting(
        self,
        db: AsyncSession,
        meeting_id: str,
        payload: MeetingUpdate,
        actor_id: str,
    ) -> Meeting:
        meeting = await self.get_meeting(db, meeting_id)
        _assert_transition(meeting.status, MeetingStatus.RESCHEDULED)
        meeting.status = MeetingStatus.RESCHEDULED

        update_data = payload.model_dump(exclude_unset=True, exclude={"regenerate_meet_link"})
        for field, value in update_data.items():
            if field == "participants" and value is not None:
                setattr(meeting, field, [str(p) for p in value])
            else:
                setattr(meeting, field, value)

        meeting.updated_at = datetime.now(timezone.utc)

        if meeting.google_event_id and meeting.host and meeting.host.google_tokens:
            if payload.date:
                end_dt = payload.date + timedelta(minutes=meeting.duration_mins)
                patch: dict[str, Any] = {
                    "start": {"dateTime": payload.date.isoformat(), "timeZone": "UTC"},
                    "end": {"dateTime": end_dt.isoformat(), "timeZone": "UTC"},
                }
                try:
                    await google_service.update_event(
                        meeting.google_event_id, patch, meeting.host.google_tokens
                    )
                except Exception as exc:
                    logger.warning("google_reschedule_skipped", reason=str(exc))

        await self._write_audit(db, meeting_id, "RESCHEDULED", actor_id, update_data)
        await db.commit()
        await db.refresh(meeting)
        return meeting

    async def get_audit_log(self, db: AsyncSession, meeting_id: str) -> list[AuditLog]:
        await self.get_meeting(db, meeting_id)  # raises NotFoundError if missing
        stmt = (
            select(AuditLog)
            .where(AuditLog.meeting_id == meeting_id)
            .order_by(AuditLog.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def _get_host_tokens(self, db: AsyncSession, host_id: str) -> dict[str, Any] | None:
        result = await db.execute(select(User).where(User.id == host_id))
        user = result.scalar_one_or_none()
        if user and user.google_tokens:
            return dict(user.google_tokens)
        return None

    async def _write_audit(
        self,
        db: AsyncSession,
        meeting_id: str,
        action: str,
        actor_id: str,
        payload: dict[str, Any],
    ) -> None:
        # Serialize payload safely
        safe_payload: dict[str, Any] = {}
        for k, v in payload.items():
            try:
                import json

                json.dumps(v)
                safe_payload[k] = v
            except (TypeError, ValueError):
                safe_payload[k] = str(v)

        log = AuditLog(
            id=str(uuid.uuid4()),
            meeting_id=meeting_id,
            action=action,
            actor_id=actor_id,
            payload=safe_payload,
            created_at=datetime.now(timezone.utc),
        )
        db.add(log)


meeting_service = MeetingService()
