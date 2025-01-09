from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from redis import Redis
from sqlalchemy.orm import Session
from database import get_db
from pytz import timezone
from datetime import datetime
from models import UserLog

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
r = Redis(host='redis-10517.c292.ap-southeast-1-1.ec2.redns.redis-cloud.com',port=10517,decode_responses=True,username="default",password="ejjWDDXsKPbXenk5YLNLOghtkVMZfF4K",)

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request, next: str = "/admin"):
    return templates.TemplateResponse("login.html", {"request": request, "next": next})

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), next: str = Form("/admin"), db: Session = Depends(get_db)):
    stored_password = r.hget('users', username)
    if stored_password and password == stored_password:
        ip = request.client.host
        user_agent = request.headers.get('user-agent')
        india_timezone = timezone('Asia/Kolkata')
        india_time = datetime.now(india_timezone)
        
        # Create a UserLog entry
        user_log = UserLog(
            username=username,
            ip_address=ip,
            user_agent=user_agent,
            login_time=datetime.utcnow(),
            india_time=india_time.strftime('%Y-%m-%d %H:%M:%S IST')
        )
        db.add(user_log)
        db.commit()
        
        response = RedirectResponse(next, status_code=303)
        response.set_cookie(key="authenticated", value="true")
        response.set_cookie(key="username", value=username)
        return response
    return RedirectResponse(f"/login?error=incorrect_password&next={next}", status_code=303)

@router.get("/success_redirect", response_class=HTMLResponse)
async def success_redirect(request: Request):
    return templates.TemplateResponse("success_redirect.html", {"request": request})

@router.get("/user_logs", response_class=HTMLResponse)
async def get_user_logs(request: Request, db: Session = Depends(get_db)):
    user_logs = db.query(UserLog).all()
    return templates.TemplateResponse("user_logs.html", {"request": request, "user_logs": user_logs})

