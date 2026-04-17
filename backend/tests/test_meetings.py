from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting import MeetingStatus, User


async def _seed_host(db: AsyncSession) -> User:
    user = User(
        id=str(uuid.uuid4()),
        email=f"host_{uuid.uuid4().hex[:6]}@test.com",
        name="Test Interviewer",
        role="INTERVIEWER",
        google_tokens=None,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


MEETING_PAYLOAD = {
    "candidate_name": "Alice Example",
    "candidate_email": "alice@example.com",
    "position": "Nurse",
    "department": "NURSING",
    "date": "2026-03-24T09:00:00Z",
    "duration_mins": 30,
    "location_type": "GOOGLE_MEET",
    "participants": [],
}


@pytest.mark.asyncio
async def test_create_meeting_no_google(client: AsyncClient, db_session: AsyncSession) -> None:
    host = await _seed_host(db_session)
    payload = {**MEETING_PAYLOAD, "host_id": host.id}

    response = await client.post("/api/v1/meetings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["candidate_name"] == "Alice Example"
    assert data["status"] == MeetingStatus.SCHEDULED.value
    assert data["meet_link"] is None  # no Google tokens seeded


@pytest.mark.asyncio
async def test_create_meeting_with_mock_google(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    host = User(
        id=str(uuid.uuid4()),
        email=f"host_{uuid.uuid4().hex[:6]}@test.com",
        name="Google Host",
        role="INTERVIEWER",
        google_tokens={"access_token": "tok", "refresh_token": "ref"},
    )
    db_session.add(host)
    await db_session.commit()
    await db_session.refresh(host)

    payload = {**MEETING_PAYLOAD, "host_id": host.id}

    mock_result = {
        "event_id": "google_event_123",
        "meet_link": "https://meet.google.com/abc-defg-hij",
        "html_link": "https://calendar.google.com/event/abc",
    }

    with patch(
        "app.services.meeting_service.google_service.create_event_with_meet",
        new=AsyncMock(return_value=mock_result),
    ):
        response = await client.post("/api/v1/meetings", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["meet_link"] == "https://meet.google.com/abc-defg-hij"
    assert data["google_event_id"] == "google_event_123"


@pytest.mark.asyncio
async def test_list_meetings(client: AsyncClient, db_session: AsyncSession) -> None:
    response = await client.get("/api/v1/meetings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_cancel_meeting(client: AsyncClient, db_session: AsyncSession) -> None:
    host = await _seed_host(db_session)
    payload = {**MEETING_PAYLOAD, "host_id": host.id}

    create_resp = await client.post("/api/v1/meetings", json=payload)
    meeting_id = create_resp.json()["id"]

    cancel_resp = await client.post(f"/api/v1/meetings/{meeting_id}/cancel")
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == MeetingStatus.CANCELLED.value


@pytest.mark.asyncio
async def test_complete_meeting(client: AsyncClient, db_session: AsyncSession) -> None:
    host = await _seed_host(db_session)
    payload = {**MEETING_PAYLOAD, "host_id": host.id}

    create_resp = await client.post("/api/v1/meetings", json=payload)
    meeting_id = create_resp.json()["id"]

    complete_resp = await client.post(f"/api/v1/meetings/{meeting_id}/complete")
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == MeetingStatus.COMPLETED.value


@pytest.mark.asyncio
async def test_invalid_state_transition(client: AsyncClient, db_session: AsyncSession) -> None:
    host = await _seed_host(db_session)
    payload = {**MEETING_PAYLOAD, "host_id": host.id}

    create_resp = await client.post("/api/v1/meetings", json=payload)
    meeting_id = create_resp.json()["id"]

    # Complete it
    await client.post(f"/api/v1/meetings/{meeting_id}/complete")

    # Try to cancel a completed meeting — should be 409
    cancel_resp = await client.post(f"/api/v1/meetings/{meeting_id}/cancel")
    assert cancel_resp.status_code == 409


@pytest.mark.asyncio
async def test_get_audit_log(client: AsyncClient, db_session: AsyncSession) -> None:
    host = await _seed_host(db_session)
    payload = {**MEETING_PAYLOAD, "host_id": host.id}

    create_resp = await client.post("/api/v1/meetings", json=payload)
    meeting_id = create_resp.json()["id"]

    audit_resp = await client.get(f"/api/v1/meetings/{meeting_id}/audit")
    assert audit_resp.status_code == 200
    logs = audit_resp.json()
    assert len(logs) >= 1
    assert logs[0]["action"] == "CREATED"


@pytest.mark.asyncio
async def test_404_on_missing_meeting(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/meetings/nonexistent-id")
    assert resp.status_code == 404
