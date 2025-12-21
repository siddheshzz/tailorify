from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Metadata
    PROJECT_NAME: str = "Tailorify API"
    API_V1_STR: str = "/api/v1"
    
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
    S3_BUCKET_NAME: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_REGION: str = "us-east-1"
    S3_ENDPOINT_URL: str | None = None  # Crucial for Minio (local) vs real S3 (AWS)

    S3_EXTERNAL_HOST:str
    S3_REQUIRE_TLS:str
    IS_PROXY_REQUIRED:str
    S3_INTERNAL_URL:str
    
    # Security (For JWT)
    SECRET_KEY: str = "SUPER_SECRET_CHANGE_ME_IN_PROD"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # Pydantic Settings Config
    model_config = SettingsConfigDict(
        env_file=".env", 
        case_sensitive=True, 
        extra="ignore"
    )

settings = Settings() # type: ignore

