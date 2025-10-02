import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import api_router as api_v1_router
from app.core.settings import get_settings
from app.db.session import engine
from app.schemas.response import ErrorResponse, HealthResponse, RootResponse

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting up application...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    # Note: Database tables are managed by Alembic migrations
    # Run 'alembic upgrade head' to create/update tables

    yield

    # Shutdown: Clean up resources
    logger.info("👋 Shutting down application...")
    engine.dispose()
    logger.info("✅ Database connections closed")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A journaling and note-taking application",
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


# Exception handlers - registered before middleware for HTTP and validation errors
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions (404, 403, 401, etc.) and return standardized error response.
    """
    request_id = getattr(request.state, "request_id", "unknown")

    error_response = ErrorResponse(
        error=exc.__class__.__name__,
        message=str(exc.detail),
        status_code=exc.status_code,
        path=str(request.url.path),
        request_id=request_id[:8] if request_id != "unknown" else request_id,
    )

    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail} "
        f"Path: {request.url.path} [ID: {request_id[:8] if request_id != 'unknown' else request_id}]"
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors (422 Unprocessable Entity).
    """
    request_id = getattr(request.state, "request_id", "unknown")

    error_response = ErrorResponse(
        error="ValidationError",
        message="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        path=str(request.url.path),
        request_id=request_id[:8] if request_id != "unknown" else request_id,
        details=exc.errors(),
    )

    logger.warning(
        f"Validation Error: {request.url.path} [ID: {request_id[:8] if request_id != 'unknown' else request_id}] "
        f"Errors: {exc.errors()}"
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(),
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all HTTP requests with timing and response information.
    """
    # Generate request ID for tracing
    request_id = str(time.time())

    # Store request ID in request state so exception handlers can access it
    request.state.request_id = request_id

    # Start timing
    start_time = time.time()

    # Log incoming request
    logger.info(
        f"→ {request.method} {request.url.path} "
        f"[ID: {request_id[:8]}] "
        f"Client: {request.client.host if request.client else 'unknown'}"
    )

    # Process request - use try/except to catch and let exception handlers work
    try:
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"← {request.method} {request.url.path} "
            f"[ID: {request_id[:8]}] "
            f"Status: {response.status_code} "
            f"Duration: {duration:.3f}s"
        )

        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration:.3f}"

        return response

    except Exception:
        # Don't log here - let the exception propagate
        # The exception handlers will handle it and return proper response
        raise


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"], response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    """
    return HealthResponse(
        status="healthy",
        app=settings.APP_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )


# Root endpoint
@app.get("/", tags=["Root"], response_model=RootResponse)
async def root():
    """
    Root endpoint with API information.
    """
    return RootResponse(
        message=f"Welcome to {settings.APP_NAME} API",
        version=settings.VERSION,
        docs="/docs",
        redoc="/redoc",
        health="/health",
    )


# Include API routers
app.include_router(api_v1_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
