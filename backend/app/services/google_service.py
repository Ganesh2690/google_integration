from __future__ import annotations

import uuid
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from starlette.concurrency import run_in_threadpool
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger
from app.exceptions import GoogleAPIError

logger = get_logger(__name__)


class GoogleService:
    def _client(self, tokens: dict[str, Any]) -> Any:
        creds = Credentials(  # type: ignore[no-untyped-call]
            token=tokens.get("access_token"),
            refresh_token=tokens.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
        )
        return build("calendar", "v3", credentials=creds, cache_discovery=False)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
    def _create_event_sync(
        self,
        *,
        summary: str,
        description: str,
        start_iso: str,
        end_iso: str,
        attendees: list[str],
        tokens: dict[str, Any],
    ) -> dict[str, str]:
        try:
            service = self._client(tokens)
            body: dict[str, Any] = {
                "summary": summary,
                "description": description,
                "start": {"dateTime": start_iso, "timeZone": "UTC"},
                "end": {"dateTime": end_iso, "timeZone": "UTC"},
                "attendees": [{"email": e} for e in attendees],
                "conferenceData": {
                    "createRequest": {
                        "requestId": str(uuid.uuid4()),
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    }
                },
            }
            event = (
                service.events()
                .insert(
                    calendarId="primary",
                    body=body,
                    conferenceDataVersion=1,
                    sendUpdates="all",
                )
                .execute()
            )
            meet_link: str = (
                event.get("hangoutLink") or event["conferenceData"]["entryPoints"][0]["uri"]
            )
            return {
                "event_id": event["id"],
                "meet_link": meet_link,
                "html_link": event.get("htmlLink", ""),
            }
        except Exception as exc:
            logger.error("google_create_event_failed", error=str(exc))
            raise GoogleAPIError("Failed to create Google Calendar event", str(exc)) from exc

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def _update_event_sync(
        self,
        event_id: str,
        patch: dict[str, Any],
        tokens: dict[str, Any],
    ) -> None:
        try:
            service = self._client(tokens)
            service.events().patch(
                calendarId="primary",
                eventId=event_id,
                body=patch,
                sendUpdates="all",
            ).execute()
        except Exception as exc:
            logger.error("google_update_event_failed", error=str(exc))
            raise GoogleAPIError("Failed to update Google Calendar event", str(exc)) from exc

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def _cancel_event_sync(self, event_id: str, tokens: dict[str, Any]) -> None:
        try:
            service = self._client(tokens)
            if settings.GOOGLE_CANCEL_MODE == "delete":
                service.events().delete(
                    calendarId="primary",
                    eventId=event_id,
                    sendUpdates="all",
                ).execute()
            else:
                service.events().patch(
                    calendarId="primary",
                    eventId=event_id,
                    body={"status": "cancelled"},
                    sendUpdates="all",
                ).execute()
        except Exception as exc:
            logger.error("google_cancel_event_failed", error=str(exc))
            raise GoogleAPIError("Failed to cancel Google Calendar event", str(exc)) from exc

    async def create_event_with_meet(
        self,
        *,
        summary: str,
        description: str,
        start_iso: str,
        end_iso: str,
        attendees: list[str],
        tokens: dict[str, Any],
    ) -> dict[str, str]:
        return await run_in_threadpool(
            self._create_event_sync,
            summary=summary,
            description=description,
            start_iso=start_iso,
            end_iso=end_iso,
            attendees=attendees,
            tokens=tokens,
        )

    async def update_event(
        self,
        event_id: str,
        patch: dict[str, Any],
        tokens: dict[str, Any],
    ) -> None:
        await run_in_threadpool(self._update_event_sync, event_id, patch, tokens)

    async def cancel_event(self, event_id: str, tokens: dict[str, Any]) -> None:
        await run_in_threadpool(self._cancel_event_sync, event_id, tokens)


google_service = GoogleService()
