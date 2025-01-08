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
async def view_logs(request: Request, db: Session = Depends(get_db)):
    logs = db.query(CRUDLog).order_by(desc(CRUDLog.timestamp)).all()
    return templates.TemplateResponse("logs.html", {"request": request, "logs": logs})
