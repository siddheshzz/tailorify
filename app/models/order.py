from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal

from app.models.base import Base, default_timestamp, default_uuid


class Order(Base):
    __tablename__ = "orders"

    id = default_uuid()

    # # Foreign Keys
    client_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    service_id = Column(
        UUID(as_uuid=True), ForeignKey("services.id",ondelete="RESTRICT"), nullable=False, index=True
    )

    # Details
    status = Column(
        Enum(
            "pending",
            "in_progress",
            "ready",
            "completed",
            "cancelled",
            name="order_status_enum",
        ),
        nullable=False,
        default="pending",
    )
    description = Column(String, nullable=False)
    requested_date = default_timestamp()
    estimated_completion = default_timestamp()
    actual_completion = Column(DateTime(timezone=True), nullable=True)
    quoted_price = Column(Numeric(precision=10, scale=2), nullable=False)
    actual_price = Column(Numeric(precision=10, scale=2), nullable=True)
    notes = Column(String, nullable=True)
    priority = Column(
        Enum("normal", "high", "urgent", name="order_priority_enum"),
        nullable=True,
        default="normal",
    )

    # Timestamps
    created_at = default_timestamp()
    updated_at = default_timestamp(update=True)

    # Relationships (Bidirectional, referenced as strings)
    client = relationship("User", back_populates="orders",lazy="selectin")
    service = relationship("Service", back_populates="orders",lazy="selectin")
    images = relationship("OrderImage", back_populates="orders",cascade="all, delete-orphan",lazy="selectin")

    def __repr__(self):
        return f"<Order(status='{self.status}', client_id='{self.client_id}')>"
    @property
    def is_completed(self) -> bool:
        """Check if order is completed."""
        return bool(self.status == "completed")
    
    @property
    def is_active(self) -> bool:
        """Check if order is still active (not completed or cancelled)."""
        return self.status not in ["completed", "cancelled"]
    
    @property
    def final_price(self) :
        """Get final price (actual or quoted)."""
        return self.actual_price if self.actual_price else self.quoted_price
    
    def to_dict(self) -> dict:
        """Convert order to dictionary for caching."""
        return {
            "id": str(self.id),
            "client_id": str(self.client_id),
            "service_id": str(self.service_id),
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "quoted_price": str(self.quoted_price),
            "actual_price": str(self.actual_price) if self.actual_price else None,
            "requested_date": self.requested_date.isoformat() if self.requested_date else None,
            "estimated_completion": self.estimated_completion.isoformat() if self.estimated_completion else None,
            "actual_completion": self.actual_completion.isoformat() if self.actual_completion else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

