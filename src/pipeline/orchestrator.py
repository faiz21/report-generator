from datetime import datetime, timezone

from src.core.constants import ProcessingStatus
from src.core.logging import get_logger
from src.db.repository import Repository
from src.pipeline.context import PipelineContext
from src.pipeline.steps.base import PipelineStep

logger = get_logger(__name__)


class PipelineOrchestrator:
    def __init__(self, steps: list[PipelineStep], repo: Repository):
        self.steps = steps
        self.repo = repo

    async def run(
        self, ctx: PipelineContext, resume_from: str | None = None
    ) -> PipelineContext:
        skip = resume_from is not None
        started_at = datetime.now(timezone.utc)

        await self.repo.update_page_status(
            ctx.page_id,
            ProcessingStatus.QUEUED,
            generation_run_id=ctx.run_id,
            generation_started_at=started_at,
        )

        for step in self.steps:
            # Skip steps until we reach the resume point
            if skip:
                if step.name == resume_from:
                    skip = False
                else:
                    continue

            ctx.current_step = step.name
            logger.info(
                "pipeline_step_start",
                step=step.name,
                page_id=str(ctx.page_id),
                run_id=str(ctx.run_id),
            )

            # Update page status
            await self.repo.update_page_status(ctx.page_id, step.status_on_start)

            try:
                ctx = await step.execute(ctx)
                ctx.completed_steps.append(step.name)

                # Update run with last completed step
                await self.repo.update_run(
                    ctx.run_id, last_completed_step=step.name
                )

                logger.info(
                    "pipeline_step_complete",
                    step=step.name,
                    page_id=str(ctx.page_id),
                )

            except Exception as e:
                error_info = {
                    "step": step.name,
                    "error": str(e),
                    "type": type(e).__name__,
                }
                ctx.errors.append(error_info)

                logger.error(
                    "pipeline_step_failed",
                    step=step.name,
                    page_id=str(ctx.page_id),
                    error=str(e),
                )

                # Update run with error info
                await self.repo.update_run(
                    ctx.run_id,
                    error_step=step.name,
                    error_message=str(e),
                )

                if step.is_hard_failure:
                    # Abort pipeline
                    await self.repo.update_page_status(
                        ctx.page_id,
                        ProcessingStatus.FAILED,
                        last_error_code=type(e).__name__,
                        last_error_message=str(e),
                    )
                    await self.repo.complete_run(
                        ctx.run_id,
                        status="failed",
                        resolved_models=ctx.resolved_models,
                        token_usage=ctx.token_usage,
                        error_payload={"errors": ctx.errors},
                    )
                    return ctx
                else:
                    # Soft failure — mark partial and continue
                    await self.repo.update_page_status(
                        ctx.page_id,
                        ProcessingStatus.PARTIAL_FAILED,
                        last_error_code=type(e).__name__,
                        last_error_message=str(e),
                    )

        # All steps completed (possibly with partial failures)
        final_status = (
            ProcessingStatus.PARTIAL_FAILED
            if ctx.errors
            else ProcessingStatus.COMPLETED
        )
        await self.repo.update_page_status(
            ctx.page_id,
            final_status,
            generation_completed_at=datetime.now(timezone.utc),
        )
        await self.repo.complete_run(
            ctx.run_id,
            status=final_status.value,
            resolved_models=ctx.resolved_models,
            token_usage=ctx.token_usage,
            error_payload={"errors": ctx.errors} if ctx.errors else None,
        )

        return ctx

    async def run_single_step(
        self, ctx: PipelineContext, step_name: str
    ) -> PipelineContext:
        for step in self.steps:
            if step.name == step_name:
                ctx.current_step = step.name
                await self.repo.update_page_status(ctx.page_id, step.status_on_start)
                ctx = await step.execute(ctx)
                ctx.completed_steps.append(step.name)
                return ctx

        raise ValueError(f"Step '{step_name}' not found in pipeline")
