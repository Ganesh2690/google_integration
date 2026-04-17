from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import auth, departments, meetings, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
