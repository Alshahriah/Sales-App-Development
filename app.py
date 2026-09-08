import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from routers import auth, sales, dashboard, admin, logs, regions, misc
from database import init_db

from dotenv import load_dotenv
load_dotenv()

SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
if not SESSION_SECRET_KEY:
    raise RuntimeError(
        "SESSION_SECRET_KEY environment variable is required. "
        "Copy .env.example to .env and set a long random value."
    )

app = FastAPI(middleware=[Middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    same_site="lax",
    https_only=os.getenv("SESSION_HTTPS_ONLY", "false").lower() == "true",
)])

# Include the routers
app.include_router(auth.router)
app.include_router(sales.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(logs.router)
app.include_router(regions.router)
app.include_router(misc.router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

PUBLIC_PATHS = {"/login", "/token", "/signup", "/logout"}


def _is_safe_next(path: str) -> bool:
    # Only allow relative paths to prevent open redirects.
    return bool(path) and path.startswith("/") and not path.startswith("//")


@app.on_event("startup")
def _startup_init_db():
    init_db()


@app.middleware("http")
async def check_authentication(request: Request, call_next):
    path = request.url.path
    if (
        path in PUBLIC_PATHS
        or path == "/favicon.ico"
        or path.startswith("/static")
    ):
        return await call_next(request)
    if not request.session.get("authenticated"):
        next_url = path + ("?" + request.url.query if request.url.query else "")
        if not _is_safe_next(next_url):
            next_url = "/admin"
        return RedirectResponse(f"/login?next={next_url}")
    response = await call_next(request)
    return response
