import json

from src.core.constants import ArtifactType, ProcessingStatus, TaskType
from src.llm.response_parser import extract_json_from_response, validate_score_range
from src.pipeline.context import PipelineContext
from src.pipeline.steps.base import PipelineStep


class AnalyzeStep(PipelineStep):
    name = "analyze"
    status_on_start = ProcessingStatus.ANALYZING
    status_on_complete = ProcessingStatus.ANALYSIS_COMPLETED

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        model = self.model_router.resolve(
            TaskType.ANALYZER, ctx.analysis_level, ctx.model_variant
        )
        defaults = self.model_router.get_defaults(TaskType.ANALYZER)
        ctx.resolved_models["analyzer"] = model

        system_prompt = (
            "You are an expert content analyst. Analyze the report and produce "
            "a structured evaluation including summary, quality scores, and "
            "extracted structured data."
        )

        user_parts = [
            f"# Analyze Report Page: {ctx.page_title}",
            f"\n## Refined Report\n{ctx.refined_report}",
        ]

        if ctx.user_instruction:
            user_parts.append(f"\n## Original Instructions\n{ctx.user_instruction}")

        extraction_hint = ""
        if ctx.normalized_schema:
            extraction_hint = (
                f"\n## Data Extraction Schema\n"
                f"Extract structured data conforming to:\n"
                f"```json\n{json.dumps(ctx.normalized_schema, indent=2)}\n```"
            )
            user_parts.append(extraction_hint)

        user_parts.append(
            "\n## Output Format\n"
            "Respond in JSON with these fields:\n"
            "- summary: key takeaway summary grouped by categories\n"
            "- content_score: object with:\n"
            "  - overall: 0-100\n"
            "  - outline_alignment: 0-100\n"
            "  - writing_alignment: 0-100\n"
            "  - analysis_score: 0-100\n"
            "  - notes: list of scoring notes (max 2)\n"
            "- extracted_data: structured data extracted from the report"
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

        ctx.token_usage["analyzer"] = {
            "prompt_tokens": response.prompt_tokens,
            "completion_tokens": response.completion_tokens,
            "total_tokens": response.total_tokens,
        }

        parsed = extract_json_from_response(response.content)
        if isinstance(parsed, dict):
            ctx.page_summary = parsed.get("summary", "")
            score = parsed.get("content_score", {})
            if isinstance(score, dict):
                # Server-side recalculation of overall score
                outline = validate_score_range(score.get("outline_alignment", 0))
                writing = validate_score_range(score.get("writing_alignment", 0))
                analysis = validate_score_range(score.get("analysis_score", 0))
                overall = round((outline + writing + analysis) / 3, 2)

                ctx.content_score = {
                    "overall": overall,
                    "outline_alignment": outline,
                    "writing_alignment": writing,
                    "analysis_score": analysis,
                    "notes": score.get("notes", [])[:2],
                }
            ctx.extracted_data = parsed.get("extracted_data", {})

        # Save artifacts
        await self.repo.save_artifact(
            report_page_id=ctx.page_id,
            run_id=ctx.run_id,
            artifact_type=ArtifactType.SUMMARY,
            content_text=ctx.page_summary if isinstance(ctx.page_summary, str) else json.dumps(ctx.page_summary),
        )
        await self.repo.save_artifact(
            report_page_id=ctx.page_id,
            run_id=ctx.run_id,
            artifact_type=ArtifactType.SCORE,
            content_json=ctx.content_score,
        )
        if ctx.extracted_data:
            await self.repo.save_artifact(
                report_page_id=ctx.page_id,
                run_id=ctx.run_id,
                artifact_type=ArtifactType.EXTRACTED_DATA,
                content_json=ctx.extracted_data,
            )

        return ctx
