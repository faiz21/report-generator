from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(tags=["ui"])

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/pages/{page_id}", response_class=HTMLResponse)
async def page_detail(request: Request, page_id: str):
    return templates.TemplateResponse("page_detail.html", {"request": request, "page_id": page_id})


@router.get("/reports/{report_id}", response_class=HTMLResponse)
async def report_detail(request: Request, report_id: str):
    return templates.TemplateResponse("report_detail.html", {"request": request, "report_id": report_id})
