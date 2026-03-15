import copy

from src.core.constants import ProcessingStatus
from src.pipeline.context import PipelineContext
from src.pipeline.steps.base import PipelineStep

KEYS_TO_REMOVE = {"$id", "$defs", "$schema"}


def normalize_schema(schema: dict) -> dict:
    """Recursively remove unwanted JSON Schema keywords and flatten allOf."""
    if not isinstance(schema, dict):
        return schema

    result = {}
    for key, value in schema.items():
        if key in KEYS_TO_REMOVE:
            continue
        if key == "allOf" and isinstance(value, list):
            # Flatten allOf into parent
            for item in value:
                if isinstance(item, dict):
                    result.update(normalize_schema(item))
            continue
        if isinstance(value, dict):
            result[key] = normalize_schema(value)
        elif isinstance(value, list):
            result[key] = [
                normalize_schema(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value

    return result


class NormalizeStep(PipelineStep):
    name = "normalize"
    status_on_start = ProcessingStatus.QUEUED
    status_on_complete = ProcessingStatus.QUEUED

    async def execute(self, ctx: PipelineContext) -> PipelineContext:
        if ctx.extraction_schema:
            ctx.normalized_schema = normalize_schema(copy.deepcopy(ctx.extraction_schema))
        if ctx.ui_json_schema:
            ctx.ui_json_schema = normalize_schema(copy.deepcopy(ctx.ui_json_schema))
        return ctx
