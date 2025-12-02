from pydantic_settings import BaseSettings

class AppConfig(BaseSettings):
    S3_EXTERNAL_PORT: str
    S3_INTERNAL_PORT: str
    S3_BUCKET_NAME: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_REGION: str
    S3_REQUIRE_TLS: bool
    IS_PROXY_REQUIRED: bool
    S3_EXTERNAL_HOST: str
    S3_INTERNAL_URL: str

app_config: AppConfig = AppConfig() # type: ignore