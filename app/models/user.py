

from app.models.base import Base, default_uuid, default_timestamp
from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    # Use the helper function for id
    id = default_uuid()
    
    email = Column(String, unique=True, nullable=False, index=True) 
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True) 
    address = Column(String, nullable=True)
    user_type = Column(
        Enum('client', 'admin', name='user_type_enum'),
        nullable=False
    )
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = default_timestamp()
    updated_at = default_timestamp(update=True)
    
    # Relationships to other models (referenced as strings)
    orders = relationship("Order", back_populates="client")
    uploaded_images = relationship("OrderImage", back_populates="uploader")
    bookings = relationship("Booking", back_populates="user")

    def __repr__(self):
        return f"<User(email='{self.email}')>"