from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..assessment.router import router as assessment_router
from ..auth.router import router as auth_router
from ..content.router import router as content_router
from ..gamification import subscribers as _game_subscribers  # noqa: F401 — registers event handlers
from ..gamification.router import router as game_router
from ..core.config import get_settings
from ..core.db import create_all_dev
from ..core.errors import install_error_handlers
from ..learning.router import router as learning_router
from ..tutor.router import router as tutor_router
from ..seed import seed_if_empty


def create_app() -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if settings.is_dev:
            await create_all_dev()  # prod schema is Alembic-owned (DATABASE.md §12)
            if settings.auto_seed:
                await seed_if_empty()
        yield

    app = FastAPI(
        title="Neuraforge API",
        version="0.1.0",
        lifespan=lifespan,
        openapi_url=f"{settings.api_prefix}/openapi.json",
        docs_url=f"{settings.api_prefix}/docs",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    install_error_handlers(app)

    @app.get(f"{settings.api_prefix}/health", tags=["ops"])
    async def health() -> dict:
        return {"status": "ok", "env": settings.env}

    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(content_router, prefix=settings.api_prefix)
    app.include_router(learning_router, prefix=settings.api_prefix)
    app.include_router(game_router, prefix=settings.api_prefix)
    app.include_router(tutor_router, prefix=settings.api_prefix)
    app.include_router(assessment_router, prefix=settings.api_prefix)
    return app
