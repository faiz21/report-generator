import uuid

from fastapi import APIRouter, BackgroundTasks, Depends

from src.api.schemas import (
    GenerateJsonRequest,
    GeneratePageRequest,
    GenerateResponse,
    PageStatusResponse,
)
from src.db.repository import Repository
from src.dependencies import get_llm_client, get_model_router, get_repository
from src.llm.client import LLMClient
from src.llm.model_router import ModelRouter
from src.services.page_generation import PageGenerationService
from src.services.json_generation import JsonGenerationService

router = APIRouter(prefix="/api/report-pages", tags=["report-pages"])


@router.post("/{page_id}/generate", response_model=GenerateResponse)
async def generate_page(
    page_id: uuid.UUID,
    request: GeneratePageRequest,
    background_tasks: BackgroundTasks,
    repo: Repository = Depends(get_repository),
    llm_client: LLMClient = Depends(get_llm_client),
    model_router: ModelRouter = Depends(get_model_router),
):
    service = PageGenerationService(repo=repo, llm_client=llm_client, model_router=model_router)
    run = await service.create_run(page_id)

    background_tasks.add_task(
        service.generate_page,
        page_id=page_id,
        run_id=run.id,
        analysis_level=request.analysis_level,
        model_variant=request.model_variant,
        resume_from_step=request.resume_from_step,
    )

    return GenerateResponse(
        run_id=run.id,
        status="queued",
        status_url=f"/api/report-pages/{page_id}/status",
    )


@router.post("/{page_id}/generate-json", response_model=GenerateResponse)
async def generate_json(
    page_id: uuid.UUID,
    request: GenerateJsonRequest,
    background_tasks: BackgroundTasks,
    repo: Repository = Depends(get_repository),
    llm_client: LLMClient = Depends(get_llm_client),
    model_router: ModelRouter = Depends(get_model_router),
):
    service = JsonGenerationService(repo=repo, llm_client=llm_client, model_router=model_router)
    run = await service.create_run(page_id)

    background_tasks.add_task(
        service.generate_json,
        page_id=page_id,
        run_id=run.id,
        analysis_level=request.analysis_level,
        model_variant=request.model_variant,
    )

    return GenerateResponse(
        run_id=run.id,
        status="queued",
        status_url=f"/api/report-pages/{page_id}/status",
    )


@router.get("/{page_id}/status", response_model=PageStatusResponse)
async def get_page_status(
    page_id: uuid.UUID,
    repo: Repository = Depends(get_repository),
):
    page = await repo.get_report_page(page_id)
    if page is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Report page not found")

    return PageStatusResponse(
        page_id=page.id,
        generation_status=page.generation_status,
        json_status=page.json_status,
        generation_run_id=page.generation_run_id,
        json_run_id=page.json_run_id,
        generation_started_at=page.generation_started_at,
        generation_completed_at=page.generation_completed_at,
        last_error_code=page.last_error_code,
        last_error_message=page.last_error_message,
    )
