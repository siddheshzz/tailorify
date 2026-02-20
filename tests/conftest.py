import os

# ---------------------------------------------------------------------------
# Environment bootstrap — MUST execute before any app module is imported.
# app.core.config.Settings() is instantiated at module level and raises a
# ValidationError if required fields (SECRET_KEY, AWS_*, RESEND_*, …) are
# missing or empty. In CI, secrets may be set to empty strings rather than
# being unset, so we check for falsy values and force-override them.
# ---------------------------------------------------------------------------


def _set_if_empty(key: str, default: str) -> None:
    """Set env var if missing or empty (handles CI blank secrets)."""
    if not os.environ.get(key):
        os.environ[key] = default


_set_if_empty("SECRET_KEY", "test-secret-key-for-pytest")
_set_if_empty("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
_set_if_empty("AWS_ACCESS_KEY_ID", "test-aws-key")
_set_if_empty("AWS_SECRET_ACCESS_KEY", "test-aws-secret")
_set_if_empty("AWS_REGION", "ap-south-1")
_set_if_empty("AWS_S3_BUCKET_NAME", "test-bucket")
_set_if_empty("RESEND_API_KEY", "test-resend-key")
_set_if_empty("RESEND_FROM_EMAIL", "test@resend.dev")
_set_if_empty("RESEND_FROM_NAME", "Test")
_set_if_empty("REDIS_URL", "redis://localhost:6379/0")
_set_if_empty("ENABLE_CACHING", "False")
_set_if_empty("ENABLE_EMAIL_NOTIFICATIONS", "False")
