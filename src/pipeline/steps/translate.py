from src.core.constants import ArtifactType, ProcessingStatus, TaskType
from src.llm.response_parser import extract_json_from_response
from src.pipeline.context import PipelineContext
from src.pipeline.steps.base import PipelineStep


class TranslateStep(PipelineStep):
    name = "translate"
    status_on_start = ProcessingStatus.TRANSLATING
    status_on_complete = ProcessingStatus.TRANSLATED
    is_hard_failure = False  # Soft failure — pipeline continues

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        model = self.model_router.resolve(
            TaskType.TRANSLATOR, ctx.analysis_level, ctx.model_variant
        )
        defaults = self.model_router.get_defaults(TaskType.TRANSLATOR)
        ctx.resolved_models["translator"] = model

        system_prompt = (
            "You are a professional translator specializing in technical and business documents. "
            "Preserve all markdown formatting, tables, and heading structure exactly. "
            "Translate accurately while maintaining the professional tone."
        )

        user_message = (
            f"Translate the following report into Indonesian and Japanese.\n\n"
            f"## Source Report (English)\n{ctx.refined_report}\n\n"
            f"## Output Format\n"
            f"Respond in JSON with exactly two keys:\n"
            f'- "translation_id": the full report translated to Indonesian\n'
            f'- "translation_ja": the full report translated to Japanese\n\n'
            f"Both translations must preserve all markdown formatting."
        )

        response = await self.llm_client.chat_completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=defaults.get("temperature", 0.3),
            max_tokens=defaults.get("max_tokens"),
        )

        ctx.token_usage["translator"] = {
            "prompt_tokens": response.prompt_tokens,
            "completion_tokens": response.completion_tokens,
            "total_tokens": response.total_tokens,
        }

        parsed = extract_json_from_response(response.content)
        if isinstance(parsed, dict):
            ctx.raw_report_id = parsed.get("translation_id", "")
            ctx.raw_report_ja = parsed.get("translation_ja", "")

        # Save artifacts
        if ctx.raw_report_id:
            await self.repo.save_artifact(
                report_page_id=ctx.page_id,
                run_id=ctx.run_id,
                artifact_type=ArtifactType.TRANSLATION_ID,
                content_text=ctx.raw_report_id,
            )
        if ctx.raw_report_ja:
            await self.repo.save_artifact(
                report_page_id=ctx.page_id,
                run_id=ctx.run_id,
                artifact_type=ArtifactType.TRANSLATION_JA,
                content_text=ctx.raw_report_ja,
            )

        return ctx
