from pathlib import Path

from src.core.exceptions import PromptError


class PromptLoader:
    def __init__(self, prompts_dir: str = "config/prompts"):
        self.prompts_dir = Path(prompts_dir)

    def load(self, task_type: str, prompt_name: str, **variables: str) -> str:
        prompt_path = self.prompts_dir / task_type / f"{prompt_name}.md"
        if not prompt_path.exists():
            raise PromptError(f"Prompt template not found: {prompt_path}")

        template = prompt_path.read_text()
        return self._render(template, variables)

    def load_raw(self, task_type: str, prompt_name: str) -> str:
        prompt_path = self.prompts_dir / task_type / f"{prompt_name}.md"
        if not prompt_path.exists():
            raise PromptError(f"Prompt template not found: {prompt_path}")
        return prompt_path.read_text()

    def _render(self, template: str, variables: dict[str, str]) -> str:
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result
