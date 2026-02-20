from sqlalchemy import Boolean, Column, Enum, String
from sqlalchemy.orm import relationship

from app.models.base import Base, default_timestamp, default_uuid

class UserType(Enum):
    """User type enumeration."""
    CLIENT = "client"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    # Use the helper function for id
    id = default_uuid()

    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    # Just an example
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    # user_type = Column(Enum("client", "admin", name="user_type_enum"), nullable=False)
    user_type = Column(
        Enum("client", "admin", name="user_type_enum"),
        nullable=False,
        default=UserType.CLIENT,
        index=True,
        comment="User type (client/admin) - REQUIRED with default"
    )
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = default_timestamp()
    updated_at = default_timestamp(update=True)

    # Relationships to other models (referenced as strings)
    orders = relationship("Order", back_populates="client",cascade="all, delete-orphan",lazy="selectin")
    uploaded_images = relationship("OrderImage", back_populates="uploader",
        cascade="all, delete-orphan",
        lazy="selectin")
    bookings = relationship("Booking", back_populates="users",cascade="all, delete-orphan",
        lazy="selectin")

    def __repr__(self):
        return f"<User(email='{self.email}')> "

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return bool(self.user_type == "admin")
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for caching."""
        return {
            "id": str(self.id),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone,
            "address": self.address,
            "user_type": self.user_type.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at is True else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at is True else None,
        }