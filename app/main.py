from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models
from app.api.v1.endpoints import booking, order, service, user
from app.core.config import settings


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    yield


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


@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Standard AWS/Cloud Health Check"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }


@app.get("/")
def read_root():
    return {"message": "Tailor Backend Running"}
