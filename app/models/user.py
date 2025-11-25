# # from sqlalchemy import Column, Integer, String
# # from app.db.base import Base
# # from sqlalchemy.orm import relationship

# # class User(Base):
# #     __tablename__ = "users"

    

# #     id = Column(Integer, primary_key=True, index=True)
# #     email = Column(String, unique=True, index=True, nullable=False)
# #     full_name = Column(String, nullable=False)
# #     hashed_password = Column(String, nullable=False)
# #     bookings = relationship("Booking", back_populates="user")


# import uuid
# from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, func
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.sql import func as sql_func
# # from app.db.base import Base  # Use your actual Base import if applicable

# # For demonstration, we define a simple Base class
# Base = declarative_base() 

# class User(Base):
#     __tablename__ = "users"

#     # id: UUID, Primary Key, Unique identifier
#     # We use UUID from postgresql dialect and generate a default UUID on creation.
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
#     # email: String, Unique, Not Null, Login credential
#     email = Column(String, unique=True, nullable=False, index=True) 
    
#     # password_hash: String, Not Null, Bcrypt hashed
#     password_hash = Column(String, nullable=False)
    
#     # first_name: String, Not Null, Client's first name
#     first_name = Column(String, nullable=False)
    
#     # last_name: String, Not Null, Client's last name
#     last_name = Column(String, nullable=False)
    
#     # phone: String, Optional, Contact number (can be Null)
#     phone = Column(String, nullable=True) 
    
#     # address: String, Optional, Delivery address (can be Null)
#     address = Column(String, nullable=True)
    
#     # user_type: Enum, Not Null, 'client' or 'admin'
#     user_type = Column(
#         Enum('client', 'admin', name='user_type_enum'),
#         nullable=False
#     )
    
#     # created_at: DateTime, Not Null, Account creation timestamp
#     # func.now() sets the default to the database's current time on insertion
#     created_at = Column(DateTime(timezone=True), nullable=False, default=sql_func.now())
    
#     # updated_at: DateTime, Not Null, Last update timestamp
#     # server_default sets a default, and onupdate updates the timestamp on every change
#     updated_at = Column(
#         DateTime(timezone=True), 
#         nullable=False, 
#         default=sql_func.now(), 
#         onupdate=sql_func.now()
#     )
    
#     # is_active: Boolean, Not Null, Default: True
#     is_active = Column(Boolean, nullable=False, default=True)

#     def __repr__(self):
#         return f"<User(id={self.id}, email='{self.email}', type='{self.user_type}')>"



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

    def __repr__(self):
        return f"<User(email='{self.email}')>"