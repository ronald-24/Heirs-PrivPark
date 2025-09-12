from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api import api_router
from app.db.base import Base
from app.db.session import engine


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.project_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup() -> None:
        # Auto-create tables for MVP/dev to speed up first run
        Base.metadata.create_all(bind=engine)

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    # Include API router
    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_app()
