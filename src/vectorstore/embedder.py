from src.core.config import settings
from src.llm.client import LLMClient


class Embedder:
    def __init__(self, llm_client: LLMClient, model: str | None = None):
        self.llm_client = llm_client
        self.model = model or settings.embedding_model

    async def embed(self, texts: list[str], batch_size: int = 100) -> list[list[float]]:
        if not texts:
            return []

        all_embeddings: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            embeddings = await self.llm_client.embed(self.model, batch)
            all_embeddings.extend(embeddings)

        return all_embeddings
