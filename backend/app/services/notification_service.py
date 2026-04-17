from __future__ import annotations

from app.core.logging import get_logger

logger = get_logger(__name__)


async def send_meeting_notification(
    *,
    to_email: str,
    subject: str,
    body: str,
) -> None:
    """Placeholder — integrate fastapi-mail when SMTP is configured."""
    logger.info("notification_skipped", to=to_email, subject=subject)
