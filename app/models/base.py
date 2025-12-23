import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func as sql_func
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, DeclarativeBase

# The Declarative Base: All models must inherit from this
class Base(DeclarativeBase):
    """The shared Base class for all models"""
    pass

# Utility functions for common columns (optional, but good practice)
def default_uuid():
    return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

def default_timestamp(update=False):
    if update:
        return Column(DateTime(timezone=True), nullable=False, default=sql_func.now(), onupdate=sql_func.now())
    return Column(DateTime(timezone=True), nullable=False, default=sql_func.now())