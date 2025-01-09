from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from redis import Redis

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
r = Redis(host='redis-10517.c292.ap-southeast-1-1.ec2.redns.redis-cloud.com',port=10517,decode_responses=True,username="default",password="ejjWDDXsKPbXenk5YLNLOghtkVMZfF4K",)

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request, next: str = "/admin"):
    return templates.TemplateResponse("login.html", {"request": request, "next": next})

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), next: str = Form("/admin")):
    stored_password = r.hget('users', username)
    if stored_password and password == stored_password:
        response = RedirectResponse(next, status_code=303)
        response.set_cookie(key="authenticated", value="true")
        return response
    return RedirectResponse(f"/login?error=incorrect_password&next={next}", status_code=303)


@router.get("/success_redirect", response_class=HTMLResponse)
async def success_redirect(request: Request):
    return templates.TemplateResponse("success_redirect.html", {"request": request})
