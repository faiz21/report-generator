import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.report_page import ReportPage
from src.models.report_page_artifact import ReportPageArtifact
from src.models.report_page_run import ReportPageRun


class Repository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # --- ReportPage ---

    async def get_report_page(self, page_id: uuid.UUID) -> ReportPage | None:
        result = await self.session.execute(
            select(ReportPage).where(ReportPage.id == page_id)
        )
        return result.scalar_one_or_none()

    async def get_report_pages_by_report(self, report_id: uuid.UUID) -> list[ReportPage]:
        result = await self.session.execute(
            select(ReportPage)
            .where(ReportPage.report_id == report_id)
            .order_by(ReportPage.page_order)
        )
        return list(result.scalars().all())

    async def update_page_status(
        self, page_id: uuid.UUID, status: str, **extra_fields: object
    ) -> None:
        values: dict = {"generation_status": status, **extra_fields}
        await self.session.execute(
            update(ReportPage).where(ReportPage.id == page_id).values(**values)
        )
        await self.session.commit()

    async def update_page_outputs(self, page_id: uuid.UUID, **fields: object) -> None:
        await self.session.execute(
            update(ReportPage).where(ReportPage.id == page_id).values(**fields)
        )
        await self.session.commit()

    # --- ReportPageRun ---

    async def create_run(
        self,
        report_page_id: uuid.UUID,
        run_type: str,
        input_snapshot: dict | None = None,
    ) -> ReportPageRun:
        run = ReportPageRun(
            id=uuid.uuid4(),
            report_page_id=report_page_id,
            run_type=run_type,
            status="running",
            input_snapshot=input_snapshot,
        )
        self.session.add(run)
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def update_run(self, run_id: uuid.UUID, **fields: object) -> None:
        await self.session.execute(
            update(ReportPageRun).where(ReportPageRun.id == run_id).values(**fields)
        )
        await self.session.commit()

    async def complete_run(
        self,
        run_id: uuid.UUID,
        status: str,
        resolved_models: dict | None = None,
        token_usage: dict | None = None,
        error_payload: dict | None = None,
    ) -> None:
        values: dict = {
            "status": status,
            "ended_at": datetime.now(timezone.utc),
        }
        if resolved_models is not None:
            values["resolved_models"] = resolved_models
        if token_usage is not None:
            values["token_usage"] = token_usage
        if error_payload is not None:
            values["error_payload"] = error_payload
        await self.session.execute(
            update(ReportPageRun).where(ReportPageRun.id == run_id).values(**values)
        )
        await self.session.commit()

    # --- ReportPageArtifact ---

    async def save_artifact(
        self,
        report_page_id: uuid.UUID,
        run_id: uuid.UUID,
        artifact_type: str,
        content_text: str | None = None,
        content_json: dict | None = None,
    ) -> ReportPageArtifact:
        # Get next version number for this artifact type
        result = await self.session.execute(
            select(ReportPageArtifact.artifact_version)
            .where(
                ReportPageArtifact.report_page_id == report_page_id,
                ReportPageArtifact.artifact_type == artifact_type,
            )
            .order_by(ReportPageArtifact.artifact_version.desc())
            .limit(1)
        )
        latest = result.scalar_one_or_none()
        next_version = (latest or 0) + 1

        artifact = ReportPageArtifact(
            id=uuid.uuid4(),
            report_page_id=report_page_id,
            run_id=run_id,
            artifact_type=artifact_type,
            artifact_version=next_version,
            content_text=content_text,
            content_json=content_json,
        )
        self.session.add(artifact)
        await self.session.commit()
        await self.session.refresh(artifact)
        return artifact
