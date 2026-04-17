from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.meeting import Department, LocationType, Meeting, MeetingStatus, User

SEED_USERS = [
    {
        "id": "user-recruiter-1",
        "email": "recruiter@apollohospitals.com",
        "name": "Sarah Recruiter",
        "role": "RECRUITER",
        "google_tokens": None,
    },
    {
        "id": "user-interviewer-1",
        "email": "dr.johnson@apollohospitals.com",
        "name": "Dr. Robert Johnson",
        "role": "INTERVIEWER",
        "google_tokens": None,
    },
    {
        "id": "user-interviewer-2",
        "email": "dr.williams@apollohospitals.com",
        "name": "Dr. Linda Williams",
        "role": "INTERVIEWER",
        "google_tokens": None,
    },
    {
        "id": "user-interviewer-3",
        "email": "dr.martinez@apollohospitals.com",
        "name": "Dr. Carlos Martinez",
        "role": "INTERVIEWER",
        "google_tokens": None,
    },
    {
        "id": "user-admin-1",
        "email": "admin@apollohospitals.com",
        "name": "Admin User",
        "role": "ADMIN",
        "google_tokens": None,
    },
]

# Seed meetings on late-March 2026 dates matching the UI screenshots
SEED_MEETINGS = [
    {
        "candidate_name": "Michael Thompson",
        "candidate_email": "m.thompson@email.com",
        "position": "Lab Technician",
        "department": Department.LABORATORY,
        "host_id": "user-interviewer-1",
        "date": datetime(2026, 3, 3, 9, 0, tzinfo=timezone.utc),
        "duration_mins": 45,
        "location_type": LocationType.GOOGLE_MEET,
        "meet_link": "https://meet.google.com/abc-defg-hij",
        "google_event_id": "seed_event_001",
        "status": MeetingStatus.SCHEDULED,
        "color_tag": "#e2e8f0",
        "notes": "Review lab technician certification.",
        "participants": ["hr@apollohospitals.com"],
    },
    {
        "candidate_name": "Amanda Foster",
        "candidate_email": "a.foster@email.com",
        "position": "Clinical Coordinator",
        "department": Department.CLINICAL_COORDINATION,
        "host_id": "user-interviewer-2",
        "date": datetime(2026, 3, 5, 10, 30, tzinfo=timezone.utc),
        "duration_mins": 60,
        "location_type": LocationType.GOOGLE_MEET,
        "meet_link": "https://meet.google.com/klm-nopq-rst",
        "google_event_id": "seed_event_002",
        "status": MeetingStatus.COMPLETED,
        "color_tag": "#d1fae5",
        "notes": "Discuss coordination experience.",
        "participants": [],
    },
    {
        "candidate_name": "Sarah Mitchell",
        "candidate_email": "s.mitchell@email.com",
        "position": "Registered Nurse",
        "department": Department.NURSING,
        "host_id": "user-interviewer-1",
        "date": datetime(2026, 3, 8, 14, 0, tzinfo=timezone.utc),
        "duration_mins": 30,
        "location_type": LocationType.GOOGLE_MEET,
        "meet_link": "https://meet.google.com/uvw-xyza-bcd",
        "google_event_id": "seed_event_003",
        "status": MeetingStatus.SCHEDULED,
        "color_tag": "#e2e8f0",
        "notes": None,
        "participants": [],
    },
    {
        "candidate_name": "John Davis",
        "candidate_email": "j.davis@email.com",
        "position": "Lab Technician",
        "department": Department.LABORATORY,
        "host_id": "user-interviewer-3",
        "date": datetime(2026, 3, 10, 11, 0, tzinfo=timezone.utc),
        "duration_mins": 45,
        "location_type": LocationType.PHYSICAL,
        "location_detail": "Room 204, Apollo Hospitals Houston",
        "meet_link": None,
        "google_event_id": None,
        "status": MeetingStatus.CANCELLED,
        "color_tag": "#fee2e2",
        "notes": "Candidate requested cancellation.",
        "participants": [],
    },
    {
        "candidate_name": "Emily Chen",
        "candidate_email": "e.chen@email.com",
        "position": "Medical Assistant",
        "department": Department.ADMINISTRATION,
        "host_id": "user-interviewer-2",
        "date": datetime(2026, 3, 12, 9, 30, tzinfo=timezone.utc),
        "duration_mins": 30,
        "location_type": LocationType.GOOGLE_MEET,
        "meet_link": "https://meet.google.com/efg-hijk-lmn",
        "google_event_id": "seed_event_005",
        "status": MeetingStatus.SCHEDULED,
        "color_tag": "#e2e8f0",
        "notes": None,
        "participants": ["hr@apollohospitals.com"],
    },
    {
        "candidate_name": "David Park",
        "candidate_email": "d.park@email.com",
        "position": "Pharmacist",
        "department": Department.PHARMACY,
        "host_id": "user-interviewer-1",
        "date": datetime(2026, 3, 14, 15, 0, tzinfo=timezone.utc),
        "duration_mins": 60,
        "location_type": LocationType.GOOGLE_MEET,
        "meet_link": "https://meet.google.com/opq-rstu-vwx",
        "google_event_id": "seed_event_006",
        "status": MeetingStatus.RESCHEDULED,
        "color_tag": "#fef3c7",
        "notes": "Rescheduled from March 10.",
        "participants": [],
    },
    {
        "candidate_name": "Jessica Lee",
        "candidate_email": "j.lee@email.com",
        "position": "Registered Nurse",
        "department": Department.NURSING,
        "host_id": "user-interviewer-3",
        "date": datetime(2026, 3, 17, 10, 0, tzinfo=timezone.utc),
        "duration_mins": 30,
        "location_type": LocationType.GOOGLE_MEET,
        "meet_link": "https://meet.google.com/yza-bcde-fgh",
        "google_event_id": "seed_event_007",
        "status": MeetingStatus.SCHEDULED,
        "color_tag": "#e2e8f0",
        "notes": None,
        "participants": [],
    },
    {
        "candidate_name": "Robert Kim",
        "candidate_email": "r.kim@email.com",
        "position": "Physician",
        "department": Department.CARDIOLOGY,
        "host_id": "user-interviewer-1",
        "date": datetime(2026, 3, 19, 13, 0, tzinfo=timezone.utc),
        "duration_mins": 90,
        "location_type": LocationType.GOOGLE_MEET,
        "meet_link": "https://meet.google.com/ijk-lmno-pqr",
        "google_event_id": "seed_event_008",
        "status": MeetingStatus.COMPLETED,
        "color_tag": "#d1fae5",
        "notes": "Strong candidate for cardiology.",
        "participants": ["chief@apollohospitals.com"],
    },
    {
        "candidate_name": "Maria Garcia",
        "candidate_email": "m.garcia@email.com",
        "position": "Medical Assistant",
        "department": Department.RADIOLOGY,
        "host_id": "user-interviewer-2",
        "date": datetime(2026, 3, 21, 9, 0, tzinfo=timezone.utc),
        "duration_mins": 30,
        "location_type": LocationType.GOOGLE_MEET,
        "meet_link": "https://meet.google.com/stu-vwxy-zab",
        "google_event_id": "seed_event_009",
        "status": MeetingStatus.SCHEDULED,
        "color_tag": "#e2e8f0",
        "notes": None,
        "participants": [],
    },
    {
        "candidate_name": "James Wilson",
        "candidate_email": "j.wilson@email.com",
        "position": "Radiologist",
        "department": Department.RADIOLOGY,
        "host_id": "user-interviewer-3",
        "date": datetime(2026, 3, 24, 11, 30, tzinfo=timezone.utc),
        "duration_mins": 60,
        "location_type": LocationType.GOOGLE_MEET,
        "meet_link": "https://meet.google.com/cde-fghi-jkl",
        "google_event_id": "seed_event_010",
        "status": MeetingStatus.SCHEDULED,
        "color_tag": "#e2e8f0",
        "notes": "Final round interview.",
        "participants": ["hr@apollohospitals.com"],
    },
    {
        "candidate_name": "Linda Nguyen",
        "candidate_email": "l.nguyen@email.com",
        "position": "Clinical Coordinator",
        "department": Department.CLINICAL_COORDINATION,
        "host_id": "user-interviewer-1",
        "date": datetime(2026, 3, 26, 14, 30, tzinfo=timezone.utc),
        "duration_mins": 45,
        "location_type": LocationType.GOOGLE_MEET,
        "meet_link": "https://meet.google.com/mno-pqrs-tuv",
        "google_event_id": "seed_event_011",
        "status": MeetingStatus.SCHEDULED,
        "color_tag": "#e2e8f0",
        "notes": None,
        "participants": [],
    },
    {
        "candidate_name": "Kevin Brown",
        "candidate_email": "k.brown@email.com",
        "position": "Nurse Practitioner",
        "department": Department.NURSING,
        "host_id": "user-interviewer-2",
        "date": datetime(2026, 3, 28, 10, 0, tzinfo=timezone.utc),
        "duration_mins": 60,
        "location_type": LocationType.GOOGLE_MEET,
        "meet_link": "https://meet.google.com/wxy-zabc-def",
        "google_event_id": "seed_event_012",
        "status": MeetingStatus.SCHEDULED,
        "color_tag": "#e2e8f0",
        "notes": "NP license verification required.",
        "participants": [],
    },
]


async def seed_database(session: AsyncSession) -> None:
    from sqlalchemy import select

    # Seed users
    for user_data in SEED_USERS:
        result = await session.execute(select(User).where(User.id == user_data["id"]))
        if result.scalar_one_or_none() is None:
            user = User(**user_data)
            session.add(user)

    await session.commit()

    # Seed meetings
    for meeting_data in SEED_MEETINGS:
        m_id = f"meeting-seed-{uuid.uuid4().hex[:8]}"
        data = {**meeting_data, "id": m_id}
        data.setdefault("location_detail", None)
        meeting = Meeting(**data)
        session.add(meeting)

    await session.commit()
    print("Database seeded successfully.")


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await seed_database(session)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
