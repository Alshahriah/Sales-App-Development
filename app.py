from fastapi import FastAPI
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
