import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class ReportPage(Base):
    __tablename__ = "report_pages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    report_page_template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    page_order: Mapped[int | None] = mapped_column(Integer)

    # Narrative outputs
    raw_report: Mapped[str | None] = mapped_column(Text)
    raw_report_id: Mapped[str | None] = mapped_column(Text)  # Indonesian
    raw_report_jp: Mapped[str | None] = mapped_column(Text)  # Japanese
    page_summary: Mapped[str | None] = mapped_column(Text)

    # Scores
    overall: Mapped[float | None] = mapped_column(Float)
    outline_alignment: Mapped[float | None] = mapped_column(Float)
    writing_alignment: Mapped[float | None] = mapped_column(Float)
    analysis_score: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[list | None] = mapped_column(JSON)

    # Structured UI JSON
    en_content: Mapped[dict | None] = mapped_column(JSON)
    id_content: Mapped[dict | None] = mapped_column(JSON)
    ja_content: Mapped[dict | None] = mapped_column(JSON)

    # --- New columns for pipeline tracking ---
    generation_status: Mapped[str | None] = mapped_column(String(50))
    json_status: Mapped[str | None] = mapped_column(String(50))
    generation_run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    json_run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    template_version: Mapped[str | None] = mapped_column(String(50))
    content_generator_model: Mapped[str | None] = mapped_column(String(200))
    extracted_data: Mapped[dict | None] = mapped_column(JSON)
    validation_report: Mapped[dict | None] = mapped_column(JSON)
    generation_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    generation_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error_code: Mapped[str | None] = mapped_column(String(100))
    last_error_message: Mapped[str | None] = mapped_column(Text)
