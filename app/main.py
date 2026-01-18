from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models
from app.api.v1.endpoints import booking, order, service, user
from app.core.config import settings
# from app.worker import sample_task
from app.core.cache import cache
import logging


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    try:
        await cache.connect()
        logger.info("Redis cache connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
    
    logger.info(f"Tailorify Backend started in {settings.ENVIRONMENT} mode")
    
    yield

    # Shutdown
    logger.info("Shutting down Tailorify Backend...")
    
    # Close Redis connection
    await cache.close()
    logger.info("Redis cache connection closed")
    
    # Close database connection
    logger.info("Database connection closed")
    
    logger.info("Tailorify Backend shutdown complete")




app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan_handler,
    docs_url="/docs"
    if settings.ENVIRONMENT == "development"
    else None,  # Optional: hide docs in prod
)

# origins = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(user.router, prefix="/api/v1/user", tags=["User"])
app.include_router(service.router, prefix="/api/v1/service", tags=["Service"])
app.include_router(order.router, prefix="/api/v1/order", tags=["Order"])
app.include_router(booking.router, prefix="/api/v1/booking", tags=["Booking"])
# app.include_router(admin_campaigns.router, prefix=settings.API_V1_STR)

# @app.post("/run-task")
# async def run_task(name: str):
#     # .delay() sends the message to Redis immediately
#     task = sample_task.delay(name)
#     return {"task_id": task.id}



@app.get("/health", tags=["Monitoring"])
async def health_check():
    # """Standard AWS/Cloud Health Check"""
    # return {
    #     "status": "healthy",
    #     "environment": settings.ENVIRONMENT,
    #     "version": "1.0.0",
    # }

    health_status = {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "services": {
            "api": "operational",
            "cache": "unknown",
            "database": "unknown"
        }
    }
    
    # Check Redis connection
    try:
        if cache.is_connected:
            health_status["services"]["cache"] = "operational"
        else:
            health_status["services"]["cache"] = "disconnected"
    except Exception as e:
        health_status["services"]["cache"] = f"error: {str(e)}"
    
    # Determine overall status
    if any(status != "operational" for status in health_status["services"].values()):
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/")
def read_root():
    return {"message": "Tailor Backend Running"}
