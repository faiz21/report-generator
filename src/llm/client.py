from dataclasses import dataclass

import openai

from src.core.exceptions import LLMAPIError, LLMRateLimitError, LLMTimeoutError
from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class LLMResponse:
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str


class LLMClient:
    def __init__(self, api_key: str, base_url: str):
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    async def chat_completion(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        response_format: dict | None = None,
    ) -> LLMResponse:
        kwargs: dict = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if response_format is not None:
            kwargs["response_format"] = response_format

        try:
            response = await self.client.chat.completions.create(**kwargs)
        except openai.RateLimitError as e:
            logger.error("rate_limit_error", model=model, error=str(e))
            raise LLMRateLimitError(f"Rate limit exceeded for {model}: {e}") from e
        except openai.APITimeoutError as e:
            logger.error("timeout_error", model=model, error=str(e))
            raise LLMTimeoutError(f"Request timed out for {model}: {e}") from e
        except openai.APIError as e:
            logger.error("api_error", model=model, error=str(e))
            raise LLMAPIError(f"API error from {model}: {e}") from e

        choice = response.choices[0]
        usage = response.usage

        return LLMResponse(
            content=choice.message.content or "",
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
            model=response.model or model,
        )

    async def embed(
        self,
        model: str,
        texts: list[str],
    ) -> list[list[float]]:
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=texts,
            )
        except openai.APIError as e:
            logger.error("embedding_error", model=model, error=str(e))
            raise LLMAPIError(f"Embedding API error: {e}") from e

        return [item.embedding for item in response.data]
