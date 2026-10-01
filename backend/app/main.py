from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.exceptions import AppException
from backend.app.core.logging import logger
from backend.app.api.v1.router import api_router
from backend.app.db.session import async_engine
from backend.app.db.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Autonomous AI Video Generation Platform...")
    # Auto-create tables in development / test if not existing
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schemas verified.")

    import asyncio
    from backend.app.services.scheduling_service import scheduling_service

    async def _scheduler_runner():
        while True:
            try:
                await asyncio.sleep(60)
                await scheduling_service.check_and_trigger_due_tasks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")

    scheduler_task = asyncio.create_task(_scheduler_runner())

    yield

    logger.info("Shutting down platform engine...")
    scheduler_task.cancel()
    await async_engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Autonomous multi-tenant short-form video generation & publishing platform orchestrated by LangGraph.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled server error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred processing your request.",
                "details": str(exc) if settings.DEBUG else {},
                "retryable": False
            }
        }
    )

# Health checks
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "mock_mode": settings.MOCK_EXTERNAL_APIS}

@app.get("/ready", tags=["Health"])
async def readiness_check():
    return {"status": "ready"}

# Register API v1
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
