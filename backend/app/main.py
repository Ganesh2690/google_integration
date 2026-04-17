from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.exceptions import DomainError, GoogleAPIError, InvalidStateTransition, NotFoundError


def create_app() -> FastAPI:
    configure_logging()

    application = FastAPI(
        title="ClinReady Interview Calendar API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix="/api/v1")

    @application.exception_handler(DomainError)
    async def domain_error_handler(_req: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @application.exception_handler(NotFoundError)
    async def not_found_handler(_req: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @application.exception_handler(InvalidStateTransition)
    async def state_transition_handler(_req: Request, exc: InvalidStateTransition) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @application.exception_handler(GoogleAPIError)
    async def google_api_handler(_req: Request, exc: GoogleAPIError) -> JSONResponse:
        return JSONResponse(
            status_code=502,
            content={"error": str(exc), "upstream": exc.upstream},
        )

    return application


app = create_app()
