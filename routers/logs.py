from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db
from models import Sale, CRUDLog, UpdateStatusRequest, Region
from pathlib import Path
from fastapi.templating import Jinja2Templates

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/logs", response_class=HTMLResponse)
async def get_logs(request: Request, page: int = 1, per_page: int = 20, db: Session = Depends(get_db)):
    total_logs = db.query(CRUDLog).count()
    logs = db.query(CRUDLog).order_by(CRUDLog.timestamp.desc()).offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total_logs + per_page - 1) // per_page
    return templates.TemplateResponse("logs.html", {"request": request, "logs": logs, "page": page, "total_pages": total_pages, "per_page": per_page})
