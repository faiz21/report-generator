import uuid

from src.core.constants import AnalysisLevel, ModelVariant, RunType
from src.core.logging import get_logger
from src.db.repository import Repository
from src.llm.client import LLMClient
from src.llm.model_router import ModelRouter
from src.models.report_page_run import ReportPageRun
from src.pipeline.context import PipelineContext
from src.pipeline.orchestrator import PipelineOrchestrator
from src.pipeline.steps.analyze import AnalyzeStep
from src.pipeline.steps.assemble import AssembleStep
from src.pipeline.steps.generate import GenerateStep
from src.pipeline.steps.normalize import NormalizeStep
from src.pipeline.steps.persist import PersistStep
from src.pipeline.steps.refine import RefineStep
from src.pipeline.steps.translate import TranslateStep
from src.pipeline.steps.validate import ValidateStep
from src.pipeline.steps.vectorize_report import VectorizeReportStep
from src.pipeline.steps.vectorize_summary import VectorizeSummaryStep

logger = get_logger(__name__)


class PageGenerationService:
    def __init__(
        self,
        repo: Repository,
        llm_client: LLMClient,
        model_router: ModelRouter,
        chunker=None,
        embedder=None,
        vector_store=None,
    ):
        self.repo = repo
        self.llm_client = llm_client
        self.model_router = model_router
        self.chunker = chunker
        self.embedder = embedder
        self.vector_store = vector_store

    async def create_run(self, page_id: uuid.UUID) -> ReportPageRun:
        return await self.repo.create_run(page_id, RunType.GENERATION)

    async def generate_page(
        self,
        page_id: uuid.UUID,
        run_id: uuid.UUID,
        analysis_level: AnalysisLevel,
        model_variant: ModelVariant,
        resume_from_step: str | None = None,
    ) -> None:
        page = await self.repo.get_report_page(page_id)
        if page is None:
            logger.error("page_not_found", page_id=str(page_id))
            await self.repo.complete_run(run_id, status="failed", error_payload={"error": "Page not found"})
            return

        # Build pipeline context from page data
        template = page.report_metadata if hasattr(page, "report_metadata") else {}
        ctx = PipelineContext(
            page_id=page.id,
            report_id=page.report_id,
            run_id=run_id,
            analysis_level=analysis_level,
            model_variant=model_variant,
            dataset=getattr(page, "dataset", "") or "",
            page_template=template,
            system_prompt=template.get("system_prompt", "") if isinstance(template, dict) else "",
            user_instruction=template.get("user_instruction", "") if isinstance(template, dict) else "",
            report_format=template.get("report_format", "") if isinstance(template, dict) else "",
            extraction_schema=template.get("extraction_schema", {}) if isinstance(template, dict) else {},
            sample_data=template.get("sample_data", {}) if isinstance(template, dict) else {},
            plant_code=template.get("plant_code", "") if isinstance(template, dict) else "",
            plant_name=template.get("plant_name", "") if isinstance(template, dict) else "",
            page_title=template.get("page_title", "") if isinstance(template, dict) else "",
            page_key=template.get("page_key", "") if isinstance(template, dict) else "",
            page_order=page.page_order or 0,
            report_type=template.get("report_type", "") if isinstance(template, dict) else "",
        )

        # Build step instances
        step_args = {
            "llm_client": self.llm_client,
            "model_router": self.model_router,
            "repo": self.repo,
        }

        steps = [
            NormalizeStep(**step_args),
            AssembleStep(**step_args),
            GenerateStep(**step_args),
            ValidateStep(**step_args),
            RefineStep(**step_args),
            TranslateStep(**step_args),
            AnalyzeStep(**step_args),
            PersistStep(**step_args),
            VectorizeReportStep(
                **step_args,
                chunker=self.chunker,
                embedder=self.embedder,
                vector_store=self.vector_store,
            ),
            VectorizeSummaryStep(
                **step_args,
                chunker=self.chunker,
                embedder=self.embedder,
                vector_store=self.vector_store,
            ),
        ]

        orchestrator = PipelineOrchestrator(steps=steps, repo=self.repo)
        await orchestrator.run(ctx, resume_from=resume_from_step)
