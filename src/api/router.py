from fastapi import APIRouter

from src.api.report_pages import router as pages_router
from src.api.reports import router as reports_router

api_router = APIRouter()
api_router.include_router(pages_router)
api_router.include_router(reports_router)
