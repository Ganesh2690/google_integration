from __future__ import annotations

from fastapi import APIRouter

from app.models.meeting import Department

router = APIRouter()


@router.get("")
async def list_departments() -> list[str]:
    return [d.value for d in Department]
