from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from infra.database import create_db_and_tables
# from domains import router as domains_router
from runway import router as runway_router
from infra.auth import setup_cors, AuthMiddleware, LoggingMiddleware, ErrorHandlingMiddleware
from infra.qbo.qbo_sync_scheduler import start_qbo_sync_scheduler, start_qbo_sync_worker, stop_qbo_sync_scheduler
import logging
import os
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    logging.info("Oodaloo Runway API started successfully")
    
    # Start QBO sync scheduler and worker
    try:
        # Start sync scheduler in background
        asyncio.create_task(start_qbo_sync_scheduler())
        # Start job worker in background
        asyncio.create_task(start_qbo_sync_worker())
        logging.info("QBO sync scheduler and worker started")
    except Exception as e:
        logging.error(f"Failed to start QBO sync scheduler: {e}")
    
    yield
    
    # Shutdown
    try:
        stop_qbo_sync_scheduler()
        logging.info("QBO sync scheduler stopped")
    except Exception as e:
        logging.error(f"Error stopping QBO sync scheduler: {e}")

app = FastAPI(
    title="Oodaloo Runway API",
    description="Cash runway management for single-business agencies",
    version="4.3.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
    lifespan=lifespan,
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

# Include routers - clean cascading import pattern
app.include_router(runway_router)  # All runway product APIs
# app.include_router(domains_router)  # All domain-specific internal APIs - REMOVED to ensure only runway/ is exposed

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

@app.get("/health/sync")
async def sync_health_check():
    """Health check for QBO sync system."""
    try:
        from infra.qbo.qbo_sync_scheduler import get_qbo_sync_scheduler
        scheduler = get_qbo_sync_scheduler()
        stats = scheduler.get_sync_stats()
        
        return {
            "status": "healthy",
            "qbo_sync_stats": stats,
            "timestamp": "2025-01-27T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": "2025-01-27T00:00:00Z"
        }

@app.get("/templates/{template_name}")
async def serve_template(template_name: str, request: Request):
    return templates.TemplateResponse(f"{template_name}", {"request": request})
