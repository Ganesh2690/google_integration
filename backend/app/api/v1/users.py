from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.meeting import User
from app.schemas.user import UserRead

router = APIRouter()


@router.get("/interviewers", response_model=list[UserRead])
async def list_interviewers(
    db: AsyncSession = Depends(get_db),
) -> list[UserRead]:
    result = await db.execute(
        select(User).where(User.role.in_(["INTERVIEWER", "ADMIN"])).order_by(User.name)
    )
    users = result.scalars().all()
    return [UserRead.model_validate(u) for u in users]
