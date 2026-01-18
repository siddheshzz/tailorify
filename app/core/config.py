from typing import List, Literal, Union

from pydantic import AnyHttpUrl, field_validator,Field, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Metadata
    PROJECT_NAME: str = "Tailorify API"
    API_V1_STR: str = "/api/v1"
    APP_VERSION:str = "1.0.0"

    # Environment Logic
    ENVIRONMENT: str = "development"  # or "production"

    # Database
    # This will be validated to ensure it's a valid Postgres URL
    DATABASE_URL: str

    # CORS
    # Converts a string like "http://localhost:3000,https://app.com" into a list
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v

    # S3 / Minio Configuration
    # S3_BUCKET_NAME: str
    # S3_ACCESS_KEY: str
    # S3_SECRET_KEY: str
    # S3_REGION: str = "us-east-1"
    # S3_ENDPOINT_URL: str | None = None  # Crucial for Minio (local) vs real S3 (AWS)

    # S3_EXTERNAL_HOST:str
    # S3_REQUIRE_TLS:str
    # IS_PROXY_REQUIRED:str
    # S3_INTERNAL_URL:str

    # Storage Configuration
    STORAGE_BACKEND: Literal["minio", "s3"] = "s3"  # Switch between MinIO and S3

    # # MinIO Configuration (Local Development)
    # MINIO_ENDPOINT: str = "minio:9000"
    # MINIO_EXTERNAL_ENDPOINT: str = "localhost:9000"
    # MINIO_ACCESS_KEY: str = "minioadmin"
    # MINIO_SECRET_KEY: str = "minioadmin"
    # MINIO_BUCKET_NAME: str = "tailorify"
    # MINIO_SECURE: bool = False
    # MINIO_USE_PROXY: bool = True
    # MINIO_INTERNAL_URL: str = "http://minio:9000"

     # Cache TTL Settings (in seconds)
    CACHE_DEFAULT_TTL: int = 300  # 5 minutes
    CACHE_PRODUCTS_TTL: int = 600  # 10 minutes
    CACHE_SERVICES_TTL: int = 1800  # 30 minutes
    CACHE_USER_PROFILE_TTL: int = 900  # 15 minutes
    CACHE_ORDER_LIST_TTL: int = 180  # 3 minutes
    
    # ============================================
    # Celery Configuration
    # ============================================
    CELERY_BROKER_URL: str = ""  # Will default to REDIS_URL
    CELERY_RESULT_BACKEND: str = ""  # Will default to REDIS_URL
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 300  # 5 minutes max per task
    CELERY_TASK_SOFT_TIME_LIMIT: int = 270  # Soft limit at 4.5 minutes
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 4
    CELERY_WORKER_MAX_TASKS_PER_CHILD: int = 1000
    CELERY_TASK_ACKS_LATE: bool = True
    CELERY_RESULT_EXPIRES: int = 3600  # Results expire after 1 hour

    REDIS_URL: str = "redis://redis:6379/0"
    
    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def set_celery_broker(cls, v: str, info) -> str:
        """Use Redis URL if Celery broker not explicitly set."""
        if not v and info.data.get("REDIS_URL"):
            return info.data["REDIS_URL"]
        return v or ""
    
    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def set_celery_backend(cls, v: str, info) -> str:
        """Use Redis URL if Celery backend not explicitly set."""
        if not v and info.data.get("REDIS_URL"):
            return info.data["REDIS_URL"]
        return v or ""
    
    # ============================================
    # Email Configuration (Resend)
    # ============================================
    RESEND_API_KEY: str
    RESEND_FROM_EMAIL: str
    RESEND_FROM_NAME: str
    
    # Email Templates (Resend Template IDs)
    EMAIL_TEMPLATE_ORDER_CONFIRMATION: str = ""  # Optional: Template ID for order confirmation
    EMAIL_TEMPLATE_WELCOME: str = ""  # Optional: Template ID for welcome email
    EMAIL_TEMPLATE_CAMPAIGN: str = ""  # Optional: Template ID for campaigns
    

    # ============================================
    # Rate Limiting
    # ============================================
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_ENABLED: bool = True
    
    # ============================================
    # Logging Configuration
    # ============================================
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    LOG_FORMAT: str = "json"  # or "text"
    
    # ============================================
    # Feature Flags
    # ============================================
    ENABLE_CACHING: bool = True
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    ENABLE_ANALYTICS: bool = False


    # AWS S3 Configuration (Production)
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET_NAME: str

    # File Upload Settings
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB
    ALLOWED_IMAGE_TYPES: list = [
        "image/jpeg",
        "image/png",
        "image/jpg",
        "image/gif",
        "image/webp",
    ]
    PRESIGNED_URL_EXPIRY_MINUTES: int = 30  # 6 hours

    # Security (For JWT)
    SECRET_KEY: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days




    # Pydantic Settings Config
    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=True, extra="ignore"
    )


settings = Settings()  # type: ignore
