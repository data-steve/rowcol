from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from db import create_db_and_tables
from domains import router as domains_router
from runway.routes import router as runway_router
from runway.routes.auth import router as auth_router
from runway.routes.businesses import router as businesses_router  
from runway.routes.users import router as users_router
from runway.routes.digest import router as digest_router
from runway.middleware import setup_cors, AuthMiddleware, LoggingMiddleware, ErrorHandlingMiddleware
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Oodaloo Runway API",
    description="Cash runway management for single-business agencies",
    version="4.3.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
)

# Setup CORS
setup_cors(app)

# Add middleware (order matters - they're applied in reverse order)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="runway/templates")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logging.info("Oodaloo Runway API started successfully")

# Include routers
app.include_router(auth_router)
app.include_router(businesses_router)
app.include_router(users_router)
app.include_router(digest_router)
app.include_router(runway_router)  # Existing runway routes (onboarding, tray)
app.include_router(domains_router)  # Domain-specific internal routes

@app.get("/")
async def root():
    return {
        "message": "Oodaloo Runway API is running",
        "version": "4.3.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "4.3.0",
        "timestamp": "2025-01-27T00:00:00Z"
    }

@app.get("/templates/{template_name}")
async def serve_template(template_name: str, request: Request):
    return templates.TemplateResponse(f"{template_name}", {"request": request})
