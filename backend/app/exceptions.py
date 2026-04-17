from __future__ import annotations


class DomainError(Exception):
    """Base domain error — maps to HTTP 400."""


class NotFoundError(DomainError):
    """Resource not found — maps to HTTP 404."""


class InvalidStateTransition(DomainError):
    """Illegal meeting status transition — maps to HTTP 409."""

    def __init__(self, current: str, target: str) -> None:
        super().__init__(f"Cannot transition meeting from '{current}' to '{target}'.")
        self.current = current
        self.target = target


class GoogleAPIError(Exception):
    """Upstream Google API failure — maps to HTTP 502."""

    def __init__(self, message: str, upstream: str = "") -> None:
        super().__init__(message)
        self.upstream = upstream
