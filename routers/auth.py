import hashlib
import hmac
import os
import secrets
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
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

HASH_ALGO = "pbkdf2_sha256"
HASH_ITERATIONS = 200_000

_redis_client: Redis | None = None


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), HASH_ITERATIONS
    )
    return f"{HASH_ALGO}${HASH_ITERATIONS}${salt}${dk.hex()}"


def _verify_password(plain: str, stored: str) -> bool:
    try:
        algo, iters, salt, hash_hex = stored.split("$")
        if algo != HASH_ALGO:
            return False
        dk = hashlib.pbkdf2_hmac(
            "sha256", plain.encode("utf-8"), bytes.fromhex(salt), int(iters)
        )
        return hmac.compare_digest(dk.hex(), hash_hex)
    except (ValueError, TypeError):
        return False


def _is_safe_next(path: str) -> bool:
    return bool(path) and path.startswith("/") and not path.startswith("//")


def get_redis() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            decode_responses=True,
            username=os.getenv("REDIS_USERNAME") or None,
            password=os.getenv("REDIS_PASSWORD") or None,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
    return _redis_client

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request, next: str = "/admin"):
    if not _is_safe_next(next):
        next = "/admin"
    return templates.TemplateResponse("login.html", {"request": request, "next": next})

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), next: str = Form("/admin"), db: Session = Depends(get_db)):
    if not _is_safe_next(next):
        next = "/admin"
    try:
        stored_password = get_redis().hget('users', username)
    except Exception:
        return RedirectResponse("/login?error=auth_unavailable", status_code=303)

    verified = False
    if stored_password:
        if stored_password.startswith(f"{HASH_ALGO}$"):
            verified = _verify_password(password, stored_password)
        else:
            # Legacy plaintext entry: constant-time compare, then upgrade to hash.
            verified = hmac.compare_digest(password, stored_password)
            if verified:
                try:
                    get_redis().hset('users', username, _hash_password(password))
                except Exception:
                    pass

    if verified:
        ip = request.client.host if request.client else None
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

        request.session.clear()
        request.session["authenticated"] = True
        request.session["username"] = username
        return RedirectResponse(next, status_code=303)
    # Generic error: do not reveal whether the username or password was wrong.
    return RedirectResponse(f"/login?error=invalid_credentials&next={next}", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)

@router.get("/success_redirect", response_class=HTMLResponse)
async def success_redirect(request: Request):
    return templates.TemplateResponse("success_redirect.html", {"request": request})

@router.get("/user_logs", response_class=HTMLResponse)
async def get_user_logs(request: Request, db: Session = Depends(get_db)):
    user_logs = db.query(UserLog).all()
    return templates.TemplateResponse("user_logs.html", {"request": request, "user_logs": user_logs})
