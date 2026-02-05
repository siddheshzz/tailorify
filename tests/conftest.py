import os

# ---------------------------------------------------------------------------
# Environment bootstrap — MUST execute before any app module is imported.
# app.core.config.Settings() is instantiated at module level and raises a
# ValidationError if required fields (SECRET_KEY, AWS_*, RESEND_*, …) are
# missing.  setdefault keeps any value already present (e.g. from CI .env).
# ---------------------------------------------------------------------------
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-aws-key")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-aws-secret")
os.environ.setdefault("AWS_REGION", "ap-south-1")
os.environ.setdefault("AWS_S3_BUCKET_NAME", "test-bucket")
os.environ.setdefault("RESEND_API_KEY", "test-resend-key")
os.environ.setdefault("RESEND_FROM_EMAIL", "test@resend.dev")
os.environ.setdefault("RESEND_FROM_NAME", "Test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("ENABLE_CACHING", "False")
os.environ.setdefault("ENABLE_EMAIL_NOTIFICATIONS", "False")
