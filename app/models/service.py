
from app.models.base import Base, default_uuid, default_timestamp
from sqlalchemy import Column, String, Integer, Boolean, Numeric
from sqlalchemy.orm import relationship

class Service(Base):
    __tablename__ = "services"

    id = default_uuid()
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True) 
    base_price = Column(Numeric(precision=10, scale=2), nullable=False)
    category = Column(String, nullable=False)
    estimated_days = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True) 
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = default_timestamp()
    
    # Relationships (referenced as a string)
    orders = relationship("Order", back_populates="service")
    bookings = relationship("Booking", back_populates="service")

    def __repr__(self):
        return f"<Service(name='{self.name}')>"