from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["Pages"])

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Redirect ke dashboard (home utama)"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Halaman utama dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})
