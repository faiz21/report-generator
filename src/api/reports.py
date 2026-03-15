import uuid

from fastapi import APIRouter, BackgroundTasks, Depends

from src.api.schemas import BatchGenerateResponse, GenerateJsonRequest, GeneratePageRequest
from src.db.repository import Repository
from src.dependencies import get_llm_client, get_model_router, get_repository
from src.llm.client import LLMClient
from src.llm.model_router import ModelRouter
from src.services.page_generation import PageGenerationService
from src.services.json_generation import JsonGenerationService

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{report_id}/pages")
async def list_report_pages(
    report_id: uuid.UUID,
    repo: Repository = Depends(get_repository),
):
    """List all pages for a specific report."""
    pages = await repo.get_report_pages_by_report(report_id)
    return [
        {
            "id": str(p.id),
            "report_id": str(p.report_id),
            "page_order": p.page_order,
            "generation_status": p.generation_status,
            "json_status": p.json_status,
            "overall": p.overall,
            "generation_completed_at": p.generation_completed_at.isoformat() if p.generation_completed_at else None,
        }
        for p in pages
    ]


@router.post("/{report_id}/generate-pages", response_model=BatchGenerateResponse)
async def generate_all_pages(
    report_id: uuid.UUID,
    request: GeneratePageRequest,
    background_tasks: BackgroundTasks,
    repo: Repository = Depends(get_repository),
    llm_client: LLMClient = Depends(get_llm_client),
    model_router: ModelRouter = Depends(get_model_router),
):
    service = PageGenerationService(repo=repo, llm_client=llm_client, model_router=model_router)
    pages = await repo.get_report_pages_by_report(report_id)
    batch_id = uuid.uuid4()

    for page in pages:
        run = await service.create_run(page.id)
        background_tasks.add_task(
            service.generate_page,
            page_id=page.id,
            run_id=run.id,
            analysis_level=request.analysis_level,
            model_variant=request.model_variant,
        )

    return BatchGenerateResponse(
        report_id=report_id,
        batch_id=batch_id,
        queued_page_count=len(pages),
    )


@router.post("/{report_id}/generate-json", response_model=BatchGenerateResponse)
async def generate_all_json(
    report_id: uuid.UUID,
    request: GenerateJsonRequest,
    background_tasks: BackgroundTasks,
    repo: Repository = Depends(get_repository),
    llm_client: LLMClient = Depends(get_llm_client),
    model_router: ModelRouter = Depends(get_model_router),
):
    service = JsonGenerationService(repo=repo, llm_client=llm_client, model_router=model_router)
    pages = await repo.get_report_pages_by_report(report_id)
    batch_id = uuid.uuid4()

    for page in pages:
        run = await service.create_run(page.id)
        background_tasks.add_task(
            service.generate_json,
            page_id=page.id,
            run_id=run.id,
            analysis_level=request.analysis_level,
            model_variant=request.model_variant,
        )

    return BatchGenerateResponse(
        report_id=report_id,
        batch_id=batch_id,
        queued_page_count=len(pages),
    )
