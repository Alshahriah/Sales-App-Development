from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, password: str = Form(...)):
    if password == "yolobunda":  # Set your password here
        response = RedirectResponse("/success_redirect", status_code=303)
        response.set_cookie(key="authenticated", value="true")
        return response
    return RedirectResponse("/login?error=incorrect_password", status_code=303)

@router.get("/success_redirect", response_class=HTMLResponse)
async def success_redirect(request: Request):
    return templates.TemplateResponse("success_redirect.html", {"request": request})
