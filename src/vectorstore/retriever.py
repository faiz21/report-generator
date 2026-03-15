from supabase import create_client

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class VectorRetriever:
    def __init__(self, embedder=None):
        self.client = create_client(settings.supabase_url, settings.supabase_key)
        self.embedder = embedder

    async def retrieve(
        self,
        query: str,
        filters: dict | None = None,
        top_k: int = 5,
    ) -> list[str]:
        if not self.embedder:
            logger.warning("retriever_skip", reason="no embedder configured")
            return []

        # Embed the query
        query_embeddings = await self.embedder.embed([query])
        if not query_embeddings:
            return []

        query_embedding = query_embeddings[0]

        # Call Supabase RPC for similarity search
        params = {
            "query_embedding": query_embedding,
            "match_count": top_k,
        }
        if filters:
            params["filter_metadata"] = filters

        try:
            result = self.client.rpc("match_documents", params).execute()
            if result.data:
                return [row.get("content", "") for row in result.data]
        except Exception as e:
            logger.error("retrieval_failed", error=str(e))

        return []
