from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI

from src.core.logging import setup_logging


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

    from src.api.router import api_router

    app.include_router(api_router)
    return app


app = create_app()
