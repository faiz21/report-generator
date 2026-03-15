import json

from src.core.constants import ArtifactType, ProcessingStatus, TaskType
from src.pipeline.context import PipelineContext
from src.pipeline.steps.base import PipelineStep


class GenerateStep(PipelineStep):
    name = "generate_draft"
    status_on_start = ProcessingStatus.GENERATING_DRAFT
    status_on_complete = ProcessingStatus.DRAFT_GENERATED

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        # Resolve model
        model = self.model_router.resolve(
            TaskType.GENERATOR, ctx.analysis_level, ctx.model_variant
        )
        defaults = self.model_router.get_defaults(TaskType.GENERATOR)
        ctx.resolved_models["generator"] = model

        # Build system prompt
        system_prompt = ctx.system_prompt or "You are a professional report writer."

        # Build user message
        user_parts = []

        user_parts.append(f"# Page: {ctx.page_title}")
        user_parts.append(f"Plant: {ctx.plant_code} - {ctx.plant_name}")

        if ctx.user_instruction:
            user_parts.append(f"\n## Instructions\n{ctx.user_instruction}")

        if ctx.report_format:
            user_parts.append(f"\n## Required Report Format\n{ctx.report_format}")

        if ctx.dataset:
            user_parts.append(f"\n## Dataset\n{ctx.dataset}")

        if ctx.retrieved_context:
            user_parts.append("\n## Supporting Context (from knowledge base)")
            for i, chunk in enumerate(ctx.retrieved_context, 1):
                user_parts.append(f"\n### Context {i}\n{chunk}")

        if ctx.normalized_schema:
            user_parts.append(
                f"\n## Data to Extract\nAfter writing the report, ensure the following data can be extracted:\n{json.dumps(ctx.normalized_schema, indent=2)}"
            )

        user_message = "\n".join(user_parts)

        # Call LLM
        response = await self.llm_client.chat_completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=defaults.get("temperature", 0.7),
            max_tokens=defaults.get("max_tokens"),
        )

        ctx.raw_report = response.content
        ctx.token_usage["generator"] = {
            "prompt_tokens": response.prompt_tokens,
            "completion_tokens": response.completion_tokens,
            "total_tokens": response.total_tokens,
        }

        # Save artifact
        await self.repo.save_artifact(
            report_page_id=ctx.page_id,
            run_id=ctx.run_id,
            artifact_type=ArtifactType.DRAFT,
            content_text=ctx.raw_report,
        )

        return ctx
