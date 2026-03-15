import uuid
from datetime import datetime

from pydantic import BaseModel

from src.core.constants import AnalysisLevel, ModelVariant


class GeneratePageRequest(BaseModel):
    analysis_level: AnalysisLevel = AnalysisLevel.OPTIMAL
    model_variant: ModelVariant = ModelVariant.A
    force_rerun: bool = False
    resume_from_step: str | None = None


class GenerateJsonRequest(BaseModel):
    analysis_level: AnalysisLevel = AnalysisLevel.OPTIMAL
    model_variant: ModelVariant = ModelVariant.A


class GenerateResponse(BaseModel):
    run_id: uuid.UUID
    status: str
    status_url: str


class BatchGenerateResponse(BaseModel):
    report_id: uuid.UUID
    batch_id: uuid.UUID
    queued_page_count: int


class PageStatusResponse(BaseModel):
    page_id: uuid.UUID
    generation_status: str | None
    json_status: str | None
    generation_run_id: uuid.UUID | None
    json_run_id: uuid.UUID | None
    generation_started_at: datetime | None
    generation_completed_at: datetime | None
    last_error_code: str | None
    last_error_message: str | None


class RunStatusResponse(BaseModel):
    run_id: uuid.UUID
    run_type: str
    status: str
    started_at: datetime
    ended_at: datetime | None
    last_completed_step: str | None
    error_step: str | None
    error_message: str | None
    resolved_models: dict | None
    token_usage: dict | None
