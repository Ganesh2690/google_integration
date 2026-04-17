from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.meeting import Department, MeetingStatus
from app.schemas.meeting import (
    AuditLogRead,
    MeetingCreate,
    MeetingListFilters,
    MeetingRead,
    MeetingUpdate,
)
from app.services.meeting_service import meeting_service

router = APIRouter()

# Use a fixed system actor for demo (replace with get_current_user in production)
SYSTEM_ACTOR = "system"


@router.get("", response_model=list[MeetingRead])
async def list_meetings(
    db: AsyncSession = Depends(get_db),
    from_date: datetime | None = Query(default=None, alias="from"),
    to_date: datetime | None = Query(default=None, alias="to"),
    department: Department | None = Query(default=None),
    status: MeetingStatus | None = Query(default=None),
    host_id: str | None = Query(default=None),
) -> list[MeetingRead]:
    filters = MeetingListFilters(
        from_date=from_date,
        to_date=to_date,
        department=department,
        status=status,
        host_id=host_id,
    )
    meetings = await meeting_service.list_meetings(db, filters)
    return [MeetingRead.model_validate(m) for m in meetings]


@router.post("", response_model=MeetingRead, status_code=201)
async def create_meeting(
    payload: MeetingCreate,
    db: AsyncSession = Depends(get_db),
) -> MeetingRead:
    meeting = await meeting_service.create_meeting(db, payload, actor_id=SYSTEM_ACTOR)
    return MeetingRead.model_validate(meeting)


@router.get("/{meeting_id}", response_model=MeetingRead)
async def get_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
) -> MeetingRead:
    meeting = await meeting_service.get_meeting(db, meeting_id)
    return MeetingRead.model_validate(meeting)


@router.patch("/{meeting_id}", response_model=MeetingRead)
async def update_meeting(
    meeting_id: str,
    payload: MeetingUpdate,
    db: AsyncSession = Depends(get_db),
) -> MeetingRead:
    meeting = await meeting_service.update_meeting(db, meeting_id, payload, actor_id=SYSTEM_ACTOR)
    return MeetingRead.model_validate(meeting)


@router.post("/{meeting_id}/cancel", response_model=MeetingRead)
async def cancel_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
) -> MeetingRead:
    meeting = await meeting_service.cancel_meeting(db, meeting_id, actor_id=SYSTEM_ACTOR)
    return MeetingRead.model_validate(meeting)


@router.post("/{meeting_id}/complete", response_model=MeetingRead)
async def complete_meeting(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
) -> MeetingRead:
    meeting = await meeting_service.complete_meeting(db, meeting_id, actor_id=SYSTEM_ACTOR)
    return MeetingRead.model_validate(meeting)


@router.get("/{meeting_id}/audit", response_model=list[AuditLogRead])
async def get_audit_log(
    meeting_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[AuditLogRead]:
    logs = await meeting_service.get_audit_log(db, meeting_id)
    return [AuditLogRead.model_validate(log) for log in logs]
