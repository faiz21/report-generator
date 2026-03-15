from src.core.constants import DocType, ProcessingStatus
from src.core.logging import get_logger
from src.pipeline.context import PipelineContext
from src.pipeline.steps.base import PipelineStep

logger = get_logger(__name__)


class VectorizeReportStep(PipelineStep):
    name = "vectorize_report"
    status_on_start = ProcessingStatus.VECTORIZING
    status_on_complete = ProcessingStatus.VECTORIZING
    is_hard_failure = False  # Soft failure

    def __init__(self, *args, chunker=None, embedder=None, vector_store=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        if not ctx.refined_report:
            logger.warning("vectorize_report_skip", reason="no refined report")
            return ctx

        if not self.chunker or not self.embedder or not self.vector_store:
            logger.warning("vectorize_report_skip", reason="vector services not configured")
            return ctx

        metadata = {
            "plant_code": ctx.plant_code,
            "plant_name": ctx.plant_name,
            "report_type": ctx.report_type,
            "page_type": ctx.page_template.get("page_type", ""),
            "page_key": ctx.page_key,
            "doc_type": DocType.REPORT,
            "report_page_id": str(ctx.page_id),
            "run_id": str(ctx.run_id),
        }

        chunks = self.chunker.chunk(ctx.refined_report)
        embeddings = await self.embedder.embed(chunks)
        await self.vector_store.upsert(
            chunks=chunks,
            embeddings=embeddings,
            metadata=metadata,
        )

        logger.info(
            "vectorize_report_complete",
            page_id=str(ctx.page_id),
            chunk_count=len(chunks),
        )

        return ctx
