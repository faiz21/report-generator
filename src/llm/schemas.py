from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    compliant_elements: list[str] = Field(default_factory=list)
    issues_found: list[str] = Field(default_factory=list)
    required_fixes: list[str] = Field(default_factory=list)
    overall_status: str = "PASS"  # "PASS" or "NEEDS_REVISION"


class ContentScore(BaseModel):
    overall: float = 0
    outline_alignment: float = 0
    writing_alignment: float = 0
    analysis_score: float = 0
    notes: list[str] = Field(default_factory=list)


class AnalyzerResult(BaseModel):
    summary: str = ""
    content_score: ContentScore = Field(default_factory=ContentScore)
    extracted_data: dict = Field(default_factory=dict)


class TranslationResult(BaseModel):
    translation_id: str = ""  # Indonesian
    translation_ja: str = ""  # Japanese


class TrilingualJsonResult(BaseModel):
    en_json: dict = Field(default_factory=dict)
    id_json: dict = Field(default_factory=dict)
    ja_json: dict = Field(default_factory=dict)
