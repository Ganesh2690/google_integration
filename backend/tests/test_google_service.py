from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import GoogleAPIError
from app.services.google_service import GoogleService


def _make_tokens() -> dict[str, str]:
    return {"access_token": "access", "refresh_token": "refresh"}


def test_create_event_returns_meet_link() -> None:
    service = GoogleService()
    tokens = _make_tokens()

    mock_event = {
        "id": "evt_123",
        "hangoutLink": "https://meet.google.com/test-link",
        "htmlLink": "https://calendar.google.com/test",
        "conferenceData": {"entryPoints": [{"uri": "https://meet.google.com/test-link"}]},
    }

    with patch.object(service, "_client") as mock_client:
        mock_service = MagicMock()
        mock_client.return_value = mock_service
        mock_service.events().insert().execute.return_value = mock_event

        result = service._create_event_sync(
            summary="Test",
            description="",
            start_iso="2026-03-24T09:00:00Z",
            end_iso="2026-03-24T09:30:00Z",
            attendees=["candidate@test.com"],
            tokens=tokens,
        )

    assert result["meet_link"] == "https://meet.google.com/test-link"
    assert result["event_id"] == "evt_123"


def test_create_event_raises_google_api_error() -> None:
    service = GoogleService()
    tokens = _make_tokens()

    with patch.object(service, "_client") as mock_client:
        mock_client.side_effect = Exception("API down")

        with pytest.raises(GoogleAPIError):
            service._create_event_sync(
                summary="Test",
                description="",
                start_iso="2026-03-24T09:00:00Z",
                end_iso="2026-03-24T09:30:00Z",
                attendees=[],
                tokens=tokens,
            )


def test_cancel_event_soft() -> None:
    service = GoogleService()
    tokens = _make_tokens()

    with (
        patch.object(service, "_client") as mock_client,
        patch("app.services.google_service.settings") as mock_settings,
    ):
        mock_settings.GOOGLE_CANCEL_MODE = "soft"
        mock_svc = MagicMock()
        mock_client.return_value = mock_svc
        mock_svc.events().patch().execute.return_value = {}

        service._cancel_event_sync("evt_123", tokens)

        mock_svc.events().patch.assert_called()
