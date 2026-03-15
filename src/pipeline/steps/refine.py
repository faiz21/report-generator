import json

from src.core.constants import ArtifactType, ProcessingStatus, TaskType
from src.pipeline.context import PipelineContext
from src.pipeline.steps.base import PipelineStep


class RefineStep(PipelineStep):
    name = "refine_content"
    status_on_start = ProcessingStatus.REFINING_CONTENT
    status_on_complete = ProcessingStatus.CONTENT_REFINED

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        # If validation passed, skip refinement
        status = ctx.validation_report.get("overall_status", "")
        if status == "PASS":
            ctx.refined_report = ctx.raw_report
            await self.repo.save_artifact(
                report_page_id=ctx.page_id,
                run_id=ctx.run_id,
                artifact_type=ArtifactType.REFINED,
                content_text=ctx.refined_report,
            )
            return ctx

        model = self.model_router.resolve(
            TaskType.REFINER, ctx.analysis_level, ctx.model_variant
        )
        defaults = self.model_router.get_defaults(TaskType.REFINER)
        ctx.resolved_models["refiner"] = model

        # Use the page's system prompt to maintain voice consistency
        system_prompt = ctx.system_prompt or "You are a professional report writer."

        user_parts = [
            f"# Refine Report Page: {ctx.page_title}",
            f"\n## Original Report\n{ctx.raw_report}",
            f"\n## Validation Feedback\n{json.dumps(ctx.validation_report, indent=2)}",
        ]

        if ctx.report_format:
            user_parts.append(f"\n## Required Format\n{ctx.report_format}")

        user_parts.append(
            "\n## Task\n"
            "Revise the report to address all required fixes from the validation feedback. "
            "Preserve compliant elements. Maintain the same voice and formatting standards. "
            "Output the complete revised report in markdown."
        )

        response = await self.llm_client.chat_completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "\n".join(user_parts)},
            ],
            temperature=defaults.get("temperature", 0.5),
            max_tokens=defaults.get("max_tokens"),
        )

        ctx.refined_report = response.content
        ctx.token_usage["refiner"] = {
            "prompt_tokens": response.prompt_tokens,
            "completion_tokens": response.completion_tokens,
            "total_tokens": response.total_tokens,
        }

        await self.repo.save_artifact(
            report_page_id=ctx.page_id,
            run_id=ctx.run_id,
            artifact_type=ArtifactType.REFINED,
            content_text=ctx.refined_report,
        )

        return ctx
