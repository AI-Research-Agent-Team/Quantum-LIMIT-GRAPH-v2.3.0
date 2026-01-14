"""
Quantum LIMIT-GRAPH API
FastAPI application for evaluation, leaderboard, and metrics management
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

# Import routes
from api.routes import evaluation, leaderboard, metrics, agents, webhooks
from api.middleware.logging import LoggingMiddleware
from api.middleware.rate_limit import RateLimitMiddleware
from database.connection import init_db, close_db
from monitoring.metrics_collector import setup_metrics

# Version info
API_VERSION = "2.3.0"
API_TITLE = "Quantum LIMIT-GRAPH API"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    print("🚀 Starting Quantum LIMIT-GRAPH API...")
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Setup metrics
    setup_metrics()
    print("✅ Metrics configured")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Quantum LIMIT-GRAPH API...")
    await close_db()
    print("✅ Database connections closed")

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="""
    # Quantum LIMIT-GRAPH API
    
    Multilingual quantum research agent benchmark API for AgentBeats.
    
    ## Features
    
    - 🎯 **Evaluation API**: Submit and retrieve evaluation results
    - 🏆 **Leaderboard API**: Real-time agent rankings
    - 📊 **Metrics API**: Performance analytics
    - 🤖 **Agent Management**: Register and manage agents
    - 🔗 **Webhooks**: AgentBeats integration
    
    ## Authentication
    
    API key required for most endpoints. Include in header:
    ```
    X-API-Key: your-api-key
    ```
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Prometheus instrumentation
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Include routers
app.include_router(
    evaluation.router,
    prefix="/api/v1/evaluations",
    tags=["Evaluations"]
)

app.include_router(
    leaderboard.router,
    prefix="/api/v1/leaderboard",
    tags=["Leaderboard"]
)

app.include_router(
    metrics.router,
    prefix="/api/v1/metrics",
    tags=["Metrics"]
)

app.include_router(
    agents.router,
    prefix="/api/v1/agents",
    tags=["Agents"]
)

app.include_router(
    webhooks.router,
    prefix="/api/v1/webhooks",
    tags=["Webhooks"]
)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "operational",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "evaluations": "/api/v1/evaluations",
            "leaderboard": "/api/v1/leaderboard",
            "metrics": "/api/v1/metrics",
            "agents": "/api/v1/agents",
            "webhooks": "/api/v1/webhooks"
        }
    }

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    from database.connection import check_db_health
    from api.services.cache_service import check_redis_health
    
    db_healthy = await check_db_health()
    redis_healthy = await check_redis_health()
    
    return {
        "status": "healthy" if db_healthy and redis_healthy else "degraded",
        "version": API_VERSION,
        "services": {
            "database": "up" if db_healthy else "down",
            "redis": "up" if redis_healthy else "down"
        }
    }

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    import traceback
    from monitoring.logger import logger
    
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG") else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8080")),
        reload=os.getenv("DEBUG", "false").lower() == "true",
        log_level="info"
    )
