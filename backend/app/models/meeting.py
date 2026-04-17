from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MeetingStatus(StrEnum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"


class LocationType(StrEnum):
    GOOGLE_MEET = "GOOGLE_MEET"
    ZOOM = "ZOOM"
    MS_TEAMS = "MS_TEAMS"
    PHYSICAL = "PHYSICAL"


class Department(StrEnum):
    CARDIOLOGY = "CARDIOLOGY"
    LABORATORY = "LABORATORY"
    NURSING = "NURSING"
    PHARMACY = "PHARMACY"
    RADIOLOGY = "RADIOLOGY"
    ADMINISTRATION = "ADMINISTRATION"
    CLINICAL_COORDINATION = "CLINICAL_COORDINATION"


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    candidate_name: Mapped[str] = mapped_column(String(120), nullable=False)
    candidate_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    position: Mapped[str] = mapped_column(String(120), nullable=False)
    department: Mapped[Department] = mapped_column(SAEnum(Department), nullable=False)
    host_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    host: Mapped[User] = relationship("User", back_populates="meetings_hosted")
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_mins: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    location_type: Mapped[LocationType] = mapped_column(SAEnum(LocationType), nullable=False)
    location_detail: Mapped[str | None] = mapped_column(String(512), nullable=True)
    google_event_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meet_link: Mapped[str | None] = mapped_column(String(512), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    participants: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[MeetingStatus] = mapped_column(
        SAEnum(MeetingStatus), default=MeetingStatus.SCHEDULED, nullable=False
    )
    color_tag: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    audit_logs: Mapped[list[AuditLog]] = relationship(
        "AuditLog", back_populates="meeting", cascade="all, delete-orphan"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)  # RECRUITER | INTERVIEWER | ADMIN
    google_tokens: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # type: ignore[type-arg]

    meetings_hosted: Mapped[list[Meeting]] = relationship("Meeting", back_populates="host")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    meeting_id: Mapped[str] = mapped_column(
        String, ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False
    )
    meeting: Mapped[Meeting] = relationship("Meeting", back_populates="audit_logs")
    action: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # CREATED | UPDATED | RESCHEDULED | CANCELLED | COMPLETED
    actor_id: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)  # type: ignore[type-arg]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
