from supabase import create_client

from src.core.config import settings
from src.core.exceptions import VectorStoreError
from src.core.logging import get_logger

logger = get_logger(__name__)


class VectorStore:
    def __init__(self):
        self.client = create_client(settings.supabase_url, settings.supabase_key)

    async def upsert(
        self,
        chunks: list[str],
        embeddings: list[list[float]],
        metadata: dict,
    ) -> None:
        if not chunks:
            return

        page_id = metadata.get("report_page_id", "")
        doc_type = metadata.get("doc_type", "")

        # Delete existing chunks for this page + doc_type to avoid duplicates
        try:
            self.client.table("document_chunks").delete().eq(
                "report_page_id", page_id
            ).eq("doc_type", doc_type).execute()
        except Exception as e:
            logger.warning("vector_delete_failed", error=str(e))

        # Insert new chunks
        records = []
        for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            record = {
                "content": chunk_text,
                "embedding": embedding,
                "chunk_index": i,
                **metadata,
            }
            records.append(record)

        try:
            self.client.table("document_chunks").insert(records).execute()
        except Exception as e:
            raise VectorStoreError(f"Failed to insert vector chunks: {e}") from e

        logger.info(
            "vector_upsert_complete",
            page_id=page_id,
            doc_type=doc_type,
            chunk_count=len(records),
        )
