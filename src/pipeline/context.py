import uuid
from dataclasses import dataclass, field

from src.core.constants import AnalysisLevel, ModelVariant


@dataclass
class PipelineContext:
    # Identifiers
    page_id: uuid.UUID
    report_id: uuid.UUID
    run_id: uuid.UUID

    # Routing config
    analysis_level: AnalysisLevel
    model_variant: ModelVariant

    # Input data
    dataset: str = ""
    page_template: dict = field(default_factory=dict)
    report_metadata: dict = field(default_factory=dict)

    # Prompt assets from template
    system_prompt: str = ""
    user_instruction: str = ""
    report_format: str = ""
    extraction_schema: dict = field(default_factory=dict)
    sample_data: dict = field(default_factory=dict)
    ui_json_schema: dict = field(default_factory=dict)

    # Plant info
    plant_code: str = ""
    plant_name: str = ""
    plant_description: str = ""

    # Page info
    page_title: str = ""
    page_key: str = ""
    page_order: int = 0
    report_type: str = ""

    # Accumulated during pipeline
    normalized_schema: dict = field(default_factory=dict)
    generation_context: dict = field(default_factory=dict)
    retrieved_context: list[str] = field(default_factory=list)
    raw_report: str = ""
    validation_report: dict = field(default_factory=dict)
    refined_report: str = ""
    raw_report_id: str = ""  # Indonesian
    raw_report_ja: str = ""  # Japanese
    page_summary: str = ""
    content_score: dict = field(default_factory=dict)
    extracted_data: dict = field(default_factory=dict)

    # Tracking
    resolved_models: dict = field(default_factory=dict)
    token_usage: dict = field(default_factory=dict)
    current_step: str = ""
    completed_steps: list[str] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
