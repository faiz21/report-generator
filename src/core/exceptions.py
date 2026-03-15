class ReportGeneratorError(Exception):
    """Base exception for the report generator."""


class ConfigError(ReportGeneratorError):
    """Configuration loading or validation error."""


class ModelRoutingError(ReportGeneratorError):
    """Failed to resolve a model for the given task/level/variant."""


class PromptError(ReportGeneratorError):
    """Failed to load or render a prompt template."""


class LLMError(ReportGeneratorError):
    """Base exception for LLM-related errors."""


class LLMAPIError(LLMError):
    """LLM provider returned an API error."""


class LLMRateLimitError(LLMError):
    """LLM provider rate limit exceeded."""


class LLMTimeoutError(LLMError):
    """LLM request timed out."""


class LLMResponseParseError(LLMError):
    """Failed to parse LLM response as expected format."""


class SchemaValidationError(ReportGeneratorError):
    """LLM response did not conform to expected schema."""

    def __init__(self, message: str, raw_response: str | None = None):
        super().__init__(message)
        self.raw_response = raw_response


class PipelineError(ReportGeneratorError):
    """Error during pipeline execution."""

    def __init__(self, message: str, step_name: str | None = None):
        super().__init__(message)
        self.step_name = step_name


class PipelineStepError(PipelineError):
    """A specific pipeline step failed."""


class DatabaseError(ReportGeneratorError):
    """Database operation failed."""


class VectorStoreError(ReportGeneratorError):
    """Vector store operation failed."""
