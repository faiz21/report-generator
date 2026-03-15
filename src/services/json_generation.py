import uuid

from src.core.constants import AnalysisLevel, JsonStatus, ModelVariant, RunType, TaskType
from src.core.logging import get_logger
from src.db.repository import Repository
from src.llm.client import LLMClient
from src.llm.model_router import ModelRouter
from src.llm.response_parser import extract_json_from_response
from src.models.report_page_run import ReportPageRun

logger = get_logger(__name__)


class JsonGenerationService:
    def __init__(
        self,
        repo: Repository,
        llm_client: LLMClient,
        model_router: ModelRouter,
    ):
        self.repo = repo
        self.llm_client = llm_client
        self.model_router = model_router

    async def create_run(self, page_id: uuid.UUID) -> ReportPageRun:
        return await self.repo.create_run(page_id, RunType.JSON_EXTRACTION)

    async def generate_json(
        self,
        page_id: uuid.UUID,
        run_id: uuid.UUID,
        analysis_level: AnalysisLevel,
        model_variant: ModelVariant,
    ) -> None:
        page = await self.repo.get_report_page(page_id)
        if page is None:
            logger.error("page_not_found", page_id=str(page_id))
            await self.repo.complete_run(run_id, status="failed")
            return

        await self.repo.update_page_status(
            page_id, JsonStatus.GENERATING.value, json_run_id=run_id
        )

        model = self.model_router.resolve(
            TaskType.JSON_GENERATOR, analysis_level, model_variant
        )
        defaults = self.model_router.get_defaults(TaskType.JSON_GENERATOR)

        # Load template schema if available
        template = page.report_metadata if hasattr(page, "report_metadata") else {}
        ui_schema = template.get("ui_json_schema", {}) if isinstance(template, dict) else {}

        try:
            # Generate EN JSON from English report
            en_json = await self._extract_json_for_language(
                model, defaults, page.raw_report or "", ui_schema, "English"
            )

            # Generate ID JSON from Indonesian report
            id_json = await self._extract_json_for_language(
                model, defaults, page.raw_report_id or "", ui_schema, "Indonesian"
            )

            # Generate JA JSON from Japanese report
            ja_json = await self._extract_json_for_language(
                model, defaults, page.raw_report_jp or "", ui_schema, "Japanese"
            )

            # Persist
            await self.repo.update_page_outputs(
                page_id,
                en_content=en_json,
                id_content=id_json,
                ja_content=ja_json,
                json_status=JsonStatus.PERSISTED.value,
            )

            # Save artifacts
            from src.core.constants import ArtifactType

            for artifact_type, content in [
                (ArtifactType.EN_JSON, en_json),
                (ArtifactType.ID_JSON, id_json),
                (ArtifactType.JA_JSON, ja_json),
            ]:
                await self.repo.save_artifact(
                    report_page_id=page_id,
                    run_id=run_id,
                    artifact_type=artifact_type,
                    content_json=content,
                )

            await self.repo.complete_run(run_id, status="completed")

        except Exception as e:
            logger.error("json_generation_failed", page_id=str(page_id), error=str(e))
            await self.repo.update_page_status(
                page_id,
                JsonStatus.FAILED.value,
                last_error_code=type(e).__name__,
                last_error_message=str(e),
            )
            await self.repo.complete_run(
                run_id,
                status="failed",
                error_payload={"error": str(e)},
            )

    async def _extract_json_for_language(
        self,
        model: str,
        defaults: dict,
        source_report: str,
        ui_schema: dict,
        language: str,
    ) -> dict:
        if not source_report:
            return {}

        import json

        system_prompt = (
            "You are a structured data extraction specialist. "
            "Extract structured JSON content from the report for UI rendering. "
            "Output valid JSON only."
        )

        user_parts = [
            f"# Extract Structured {language} Content",
            f"\n## Source Report ({language})\n{source_report}",
        ]

        if ui_schema:
            user_parts.append(
                f"\n## Required JSON Schema\n```json\n{json.dumps(ui_schema, indent=2)}\n```"
            )

        user_parts.append(
            "\n## Task\n"
            "Extract the report content into a structured JSON object that conforms "
            "to the schema above. Output only the JSON object."
        )

        response = await self.llm_client.chat_completion(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "\n".join(user_parts)},
            ],
            temperature=defaults.get("temperature", 0.2),
            max_tokens=defaults.get("max_tokens"),
        )

        return extract_json_from_response(response.content)
