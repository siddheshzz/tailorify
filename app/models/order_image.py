from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, default_timestamp, default_uuid


class OrderImage(Base):
    __tablename__ = "order_images"

    id = default_uuid()

    # Foreign Keys
    order_id = Column(
        UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, index=True
    )
    uploaded_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    # Details
    s3_url: Mapped[str] = mapped_column(String)
    s3_object_path: Mapped[str] = mapped_column(String)
    image_type = Column(
        Enum("before", "after", "reference", "instruction", name="image_type_enum"),
        nullable=False,
    )

    # Timestamps
    uploaded_at = default_timestamp()

    # Relationships
    orders = relationship("Order", back_populates="images")
    uploader = relationship("User", back_populates="uploaded_images")

    def __repr__(self):
        return f"<OrderImage(order_id='{self.order_id}', type='{self.image_type}')>"
