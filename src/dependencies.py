from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repository import Repository
from src.db.session import get_session
from src.llm.client import LLMClient
from src.llm.model_router import ModelRouter
from src.core.config import settings


async def get_repository(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[Repository, None]:
    yield Repository(session)


def get_llm_client() -> LLMClient:
    return LLMClient(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )


def get_model_router() -> ModelRouter:
    return ModelRouter(config_path=settings.models_config_path)
