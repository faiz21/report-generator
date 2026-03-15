from src.core.config import load_yaml_config
from src.core.constants import AnalysisLevel, ModelVariant, TaskType
from src.core.exceptions import ModelRoutingError


class ModelRouter:
    def __init__(self, config_path: str = "config/models.yaml"):
        config = load_yaml_config(config_path)
        self._models: dict = config.get("models", {})
        self._defaults: dict = config.get("defaults", {})

    def resolve(
        self,
        task_type: TaskType,
        analysis_level: AnalysisLevel,
        model_variant: ModelVariant,
    ) -> str:
        task_config = self._models.get(task_type.value)
        if task_config is None:
            raise ModelRoutingError(f"No model config for task type: {task_type}")

        level_config = task_config.get(analysis_level.value)
        if level_config is None:
            raise ModelRoutingError(
                f"No model config for analysis level '{analysis_level}' under task '{task_type}'"
            )

        model_id = level_config.get(model_variant.value)
        if model_id is None:
            raise ModelRoutingError(
                f"No model for variant '{model_variant}' at level '{analysis_level}' for task '{task_type}'"
            )

        return model_id

    def get_defaults(self, task_type: TaskType) -> dict:
        return self._defaults.get(task_type.value, {})
