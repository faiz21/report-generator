import json
import re

from src.core.exceptions import LLMResponseParseError, SchemaValidationError


def extract_json_from_response(response: str) -> dict | list:
    """Extract JSON from an LLM response that may contain markdown code blocks or extra text."""
    # Try direct parse first
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", response, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding JSON object/array in the response
    for pattern in [r"\{[\s\S]*\}", r"\[[\s\S]*\]"]:
        match = re.search(pattern, response)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                continue

    raise LLMResponseParseError(f"Could not extract JSON from response: {response[:200]}...")


def validate_required_keys(data: dict, required_keys: list[str], context: str = "") -> None:
    """Validate that all required keys are present in the parsed data."""
    missing = [key for key in required_keys if key not in data]
    if missing:
        raise SchemaValidationError(
            f"Missing required keys {missing} in {context or 'response'}",
            raw_response=json.dumps(data),
        )


def validate_score_range(value: float | int, min_val: float = 0, max_val: float = 100) -> float:
    """Validate that a score is within expected range."""
    try:
        score = float(value)
    except (ValueError, TypeError) as e:
        raise SchemaValidationError(f"Invalid score value: {value}") from e

    return max(min_val, min(max_val, score))
