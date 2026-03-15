from src.core.constants import ProcessingStatus
from src.pipeline.context import PipelineContext
from src.pipeline.steps.base import PipelineStep


class AssembleStep(PipelineStep):
    name = "assemble"
    status_on_start = ProcessingStatus.QUEUED
    status_on_complete = ProcessingStatus.QUEUED

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        ctx.generation_context = {
            "page_title": ctx.page_title,
            "page_key": ctx.page_key,
            "plant_code": ctx.plant_code,
            "plant_name": ctx.plant_name,
            "plant_description": ctx.plant_description,
            "report_type": ctx.report_type,
            "dataset": ctx.dataset,
            "user_instruction": ctx.user_instruction,
            "report_format": ctx.report_format,
            "extraction_schema": ctx.normalized_schema or ctx.extraction_schema,
            "sample_data": ctx.sample_data,
            "analysis_level": ctx.analysis_level.value,
            "model_variant": ctx.model_variant.value,
        }
        return ctx
