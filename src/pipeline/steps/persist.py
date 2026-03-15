from src.core.constants import ProcessingStatus
from src.pipeline.context import PipelineContext
from src.pipeline.steps.base import PipelineStep


class PersistStep(PipelineStep):
    name = "persist"
    status_on_start = ProcessingStatus.PERSISTING_OUTPUTS
    status_on_complete = ProcessingStatus.PERSISTING_OUTPUTS

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        update_fields: dict = {}

        if ctx.refined_report:
            update_fields["raw_report"] = ctx.refined_report
        if ctx.raw_report_id:
            update_fields["raw_report_id"] = ctx.raw_report_id
        if ctx.raw_report_ja:
            update_fields["raw_report_jp"] = ctx.raw_report_ja
        if ctx.page_summary:
            update_fields["page_summary"] = (
                ctx.page_summary if isinstance(ctx.page_summary, str) else str(ctx.page_summary)
            )
        if ctx.content_score:
            update_fields["overall"] = ctx.content_score.get("overall")
            update_fields["outline_alignment"] = ctx.content_score.get("outline_alignment")
            update_fields["writing_alignment"] = ctx.content_score.get("writing_alignment")
            update_fields["analysis_score"] = ctx.content_score.get("analysis_score")
            update_fields["notes"] = ctx.content_score.get("notes")
        if ctx.extracted_data:
            update_fields["extracted_data"] = ctx.extracted_data
        if ctx.validation_report:
            update_fields["validation_report"] = ctx.validation_report
        if ctx.resolved_models:
            update_fields["content_generator_model"] = ctx.resolved_models.get("generator")

        if update_fields:
            await self.repo.update_page_outputs(ctx.page_id, **update_fields)

        return ctx
