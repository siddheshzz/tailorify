from app.models.base import Base, default_uuid, default_timestamp
from sqlalchemy import Column, String, Enum, ForeignKey, Numeric,DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Order(Base):
    __tablename__ = "orders"

    id = default_uuid()
    
    # # Foreign Keys
    client_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False, index=True)
    
    # Details
    status = Column(
        Enum('pending', 'in_progress', 'ready', 'completed', 'cancelled', name='order_status_enum'),
        nullable=False, default='pending'
    )
    description = Column(String, nullable=False)
    requested_date = default_timestamp()
    estimated_completion = default_timestamp()
    actual_completion = Column(DateTime(timezone=True), nullable=True)
    quoted_price = Column(Numeric(precision=10, scale=2), nullable=False)
    actual_price = Column(Numeric(precision=10, scale=2), nullable=True)
    notes = Column(String, nullable=True)
    priority = Column(
        Enum('normal', 'high', 'urgent', name='order_priority_enum'),
        nullable=True, default='normal'
    )

    # Timestamps
    created_at = default_timestamp()
    updated_at = default_timestamp(update=True)

    # Relationships (Bidirectional, referenced as strings)
    client = relationship("User", back_populates="orders")
    service = relationship("Service", back_populates="orders")
    images = relationship("OrderImage", back_populates="orders")
    

    def __repr__(self):
        return f"<Order(status='{self.status}', client_id='{self.client_id}')>"