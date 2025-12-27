from sqlalchemy import Boolean, Column, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.models.base import Base, default_timestamp, default_uuid


class Service(Base):
    __tablename__ = "services"

    id = default_uuid()
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    base_price = Column(Numeric(precision=10, scale=2), nullable=False)
    category = Column(String, nullable=True)
    estimated_days = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=True, default=True)
    created_at = default_timestamp()

    # Relationships (referenced as a string)
    orders = relationship("Order", back_populates="service")
    bookings = relationship("Booking", back_populates="service")

    def __repr__(self):
        return f"<Service(name='{self.name}')>"
