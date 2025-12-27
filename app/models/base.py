import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


# The Declarative Base: All models must inherit from this
class Base(DeclarativeBase):
    """The shared Base class for all models"""

    pass


# Utility functions for common columns (optional, but good practice)
def default_uuid():
    # return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    return Column(
        UUID(as_uuid=True),
        primary_key=True,
        # Note: we pass the function 'uuid.uuid4', NOT 'uuid.uuid4()'
        default=uuid.uuid4,
    )


def default_timestamp(update=False):
    if update:
        return Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            # This provides a Python-side default using the modern UTC way
            default=lambda: datetime.now(timezone.utc),
        )
    return Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        # This provides a Python-side default using the modern UTC way
        default=lambda: datetime.now(timezone.utc),
    )
