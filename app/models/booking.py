import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    appointment_time = Column(DateTime(timezone=True), nullable=False)  # <-- add this
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # # Relationships (optional, but useful for joins)
    users = relationship("User", back_populates="bookings")
    service = relationship("Service", back_populates="bookings")
