from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.models.meeting import Department, LocationType, MeetingStatus


class MeetingCreate(BaseModel):
    candidate_name: str = Field(min_length=1, max_length=120)
    candidate_email: EmailStr | None = None
    position: str = Field(min_length=1, max_length=120)
    department: Department
    host_id: str
    date: datetime
    duration_mins: int = Field(ge=15, le=240, default=30)
    location_type: LocationType
    location_detail: str | None = None
    notes: str | None = None
    participants: list[EmailStr] = []


class MeetingUpdate(BaseModel):
    candidate_name: str | None = Field(default=None, min_length=1, max_length=120)
    candidate_email: EmailStr | None = None
    position: str | None = Field(default=None, min_length=1, max_length=120)
    department: Department | None = None
    host_id: str | None = None
    date: datetime | None = None
    duration_mins: int | None = Field(default=None, ge=15, le=240)
    location_type: LocationType | None = None
    location_detail: str | None = None
    notes: str | None = None
    participants: list[EmailStr] | None = None
    regenerate_meet_link: bool = False


class MeetingRead(BaseModel):
    id: str
    candidate_name: str
    candidate_email: str | None
    position: str
    department: Department
    host_id: str
    date: datetime
    duration_mins: int
    location_type: LocationType
    location_detail: str | None
    google_event_id: str | None
    meet_link: str | None
    notes: str | None
    participants: list[str]
    status: MeetingStatus
    color_tag: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuditLogRead(BaseModel):
    id: str
    meeting_id: str
    action: str
    actor_id: str
    payload: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class MeetingListFilters(BaseModel):
    from_date: datetime | None = None
    to_date: datetime | None = None
    department: Department | None = None
    status: MeetingStatus | None = None
    host_id: str | None = None
