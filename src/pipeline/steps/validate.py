from src.core.constants import ArtifactType, ProcessingStatus, TaskType
from src.llm.response_parser import extract_json_from_response
from src.pipeline.context import PipelineContext
from src.pipeline.steps.base import PipelineStep


class ValidateStep(PipelineStep):
    name = "validate_outline"
    status_on_start = ProcessingStatus.VALIDATING_OUTLINE
    status_on_complete = ProcessingStatus.VALIDATION_COMPLETED

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        model = self.model_router.resolve(
            TaskType.VALIDATOR, ctx.analysis_level, ctx.model_variant
        )
        defaults = self.model_router.get_defaults(TaskType.VALIDATOR)
        ctx.resolved_models["validator"] = model

        system_prompt = (
            "You are a critical report validator. Evaluate the report against "
            "the required structure, heading hierarchy, glossary consistency, "
            "tone, and completeness. Be specific about issues found."
        )

        user_parts = [
            f"# Validate Report Page: {ctx.page_title}",
            f"\n## Generated Report\n{ctx.raw_report}",
        ]

        if ctx.report_format:
            user_parts.append(f"\n## Required Format/Structure\n{ctx.report_format}")

        if ctx.user_instruction:
            user_parts.append(f"\n## Original Instructions\n{ctx.user_instruction}")

        user_parts.append(
            "\n## Output Format\n"
            "Respond in JSON with these fields:\n"
            "- compliant_elements: list of elements that are correct\n"
            "- issues_found: list of specific issues\n"
            "- required_fixes: list of required fixes\n"
            '- overall_status: "PASS" or "NEEDS_REVISION"'
        )

        response = await self.llm_client.chat_completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "\n".join(user_parts)},
            ],
            temperature=defaults.get("temperature", 0.3),
            max_tokens=defaults.get("max_tokens"),
        )

        ctx.token_usage["validator"] = {
            "prompt_tokens": response.prompt_tokens,
            "completion_tokens": response.completion_tokens,
            "total_tokens": response.total_tokens,
        }

        try:
            ctx.validation_report = extract_json_from_response(response.content)
        except Exception:
            ctx.validation_report = {
                "compliant_elements": [],
                "issues_found": [response.content],
                "required_fixes": [],
                "overall_status": "NEEDS_REVISION",
            }

        await self.repo.save_artifact(
            report_page_id=ctx.page_id,
            run_id=ctx.run_id,
            artifact_type=ArtifactType.VALIDATION,
            content_json=ctx.validation_report,
        )

        return ctx
