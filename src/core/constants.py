from enum import StrEnum


class ProcessingStatus(StrEnum):
    QUEUED = "queued"
    GENERATING_DRAFT = "generating_draft"
    DRAFT_GENERATED = "draft_generated"
    VALIDATING_OUTLINE = "validating_outline"
    VALIDATION_COMPLETED = "validation_completed"
    REFINING_CONTENT = "refining_content"
    CONTENT_REFINED = "content_refined"
    TRANSLATING = "translating"
    TRANSLATED = "translated"
    ANALYZING = "analyzing"
    ANALYSIS_COMPLETED = "analysis_completed"
    PERSISTING_OUTPUTS = "persisting_outputs"
    VECTORIZING = "vectorizing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_FAILED = "partial_failed"


class JsonStatus(StrEnum):
    PENDING = "json_pending"
    GENERATING = "json_generating"
    VALIDATING = "json_validating"
    PERSISTED = "json_persisted"
    FAILED = "json_failed"


class TaskType(StrEnum):
    GENERATOR = "generator"
    VALIDATOR = "validator"
    REFINER = "refiner"
    TRANSLATOR = "translator"
    ANALYZER = "analyzer"
    JSON_GENERATOR = "json_generator"


class AnalysisLevel(StrEnum):
    COST_EFFECTIVE = "COST_EFFECTIVE"
    OPTIMAL = "OPTIMAL"
    TOP_GRADE = "TOP_GRADE"


class ModelVariant(StrEnum):
    A = "A"
    B = "B"
    C = "C"


class RunType(StrEnum):
    GENERATION = "generation"
    JSON_EXTRACTION = "json_extraction"
    RERUN_STEP = "rerun_step"


class ArtifactType(StrEnum):
    DRAFT = "draft"
    VALIDATION = "validation"
    REFINED = "refined"
    TRANSLATION_ID = "translation_id"
    TRANSLATION_JA = "translation_ja"
    SUMMARY = "summary"
    SCORE = "score"
    EXTRACTED_DATA = "extracted_data"
    EN_JSON = "en_json"
    ID_JSON = "id_json"
    JA_JSON = "ja_json"


class DocType(StrEnum):
    REPORT = "report"
    SUMMARY = "summary"


class FailureCategory(StrEnum):
    PROMPT_BUILD_FAILURE = "prompt_build_failure"
    MODEL_RESOLUTION_FAILURE = "model_resolution_failure"
    LLM_TIMEOUT = "llm_timeout"
    INVALID_JSON_RESPONSE = "invalid_json_response"
    SCHEMA_VALIDATION_FAILURE = "schema_validation_failure"
    DATABASE_WRITE_FAILURE = "database_write_failure"
    VECTOR_INSERT_FAILURE = "vector_insert_failure"
    RETRIEVAL_FAILURE = "retrieval_failure"
