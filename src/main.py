from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.core.logging import setup_logging

UI_DIR = Path(__file__).parent / "ui"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Report Generator",
        description="AI-powered report generation system for plant datasets",
        version="0.1.0",
        lifespan=lifespan,
    )

    # API routes
    from src.api.router import api_router
    app.include_router(api_router)

    # UI routes (HTML pages)
    from src.ui.routes import router as ui_router
    app.include_router(ui_router)

    # Static files (JS, CSS)
    app.mount("/static", StaticFiles(directory=str(UI_DIR / "static")), name="static")

    return app


app = create_app()
