from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow  # type: ignore[import-untyped]
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.models.meeting import User
from app.schemas.user import TokenResponse

router = APIRouter()

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
    "openid",
    "email",
    "profile",
]


def _build_flow() -> Flow:
    return Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )


@router.get("/google")
async def google_oauth_start() -> RedirectResponse:
    flow = _build_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )
    return RedirectResponse(url=auth_url)


@router.get("/google/callback", response_model=TokenResponse)
async def google_oauth_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    code = request.query_params.get("code")
    if not code:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Missing authorization code")

    flow = _build_flow()
    flow.fetch_token(code=code)
    credentials = flow.credentials

    import httpx

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {credentials.token}"},
        )
    userinfo = resp.json()

    email = userinfo["email"]
    name = userinfo.get("name", email)

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    tokens = {
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
    }

    if user is None:
        import uuid

        user = User(
            id=str(uuid.uuid4()),
            email=email,
            name=name,
            role="RECRUITER",
            google_tokens=tokens,
        )
        db.add(user)
    else:
        user.google_tokens = tokens

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(subject=user.id, extra={"email": user.email})
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    from fastapi import HTTPException

    from app.core.security import decode_access_token

    body = await request.json()
    old_token = body.get("token", "")
    try:
        payload = decode_access_token(old_token)
        user_id: str = payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token") from None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token = create_access_token(subject=user.id, extra={"email": user.email})
    return TokenResponse(access_token=access_token)
