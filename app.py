from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from routers import auth, sales, dashboard, admin, logs, regions, misc

app = FastAPI(middleware=[Middleware(SessionMiddleware, secret_key="secret")])

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

@app.middleware("http")
async def check_authentication(request: Request, call_next):
    if request.url.path not in ["/login", "/token", "/signup"]:
        if request.cookies.get("authenticated") != "true":
            next_url = request.url.path + "?" + request.url.query if request.url.query else request.url.path
            return RedirectResponse(f"/login?next={next_url}")
    response = await call_next(request)
    return response
