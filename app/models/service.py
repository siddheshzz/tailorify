# # from sqlalchemy import Column, Integer, String, Text, Float
# # from sqlalchemy.orm import relationship
# # from app.db.base import Base

# # class Service(Base):
# #     __tablename__ = "service"

# #     id = Column(Integer, primary_key=True, index=True)
# #     name = Column(String(100), unique=True, nullable=False, index=True)
# #     description = Column(Text, nullable=True)
# #     price = Column(Float, nullable=False, default=0.0)



# import uuid
# from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.sql import func as sql_func
# # from app.db.base import Base  # Use your actual Base import

# # Assuming Base is defined elsewhere, e.g., Base = declarative_base() 
# class Base:
#     pass

# class Service(Base):
#     __tablename__ = "services"

#     # id: UUID, Primary Key, Unique identifier
#     # UUID(as_uuid=True) for Python UUID objects, default=uuid.uuid4 to generate ID
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
#     # name: String, Not Null, Service name (e.g., "Hemming")
#     name = Column(String, nullable=False, index=True)
    
#     # description: String, Optional, Detailed description
#     description = Column(String, nullable=True) 
    
#     # base_price: Decimal, Not Null, Starting price
#     # Numeric is often preferred for financial data to ensure precision
#     base_price = Column(Numeric(precision=10, scale=2), nullable=False)
    
#     # category: String, Not Null, Category (alteration, custom, repair, etc.)
#     category = Column(String, nullable=False)
    
#     # estimated_days: Integer, Not Null, Turnaround time
#     estimated_days = Column(Integer, nullable=False)
    
#     # image_url: String, Optional, Service image stored in S3
#     image_url = Column(String, nullable=True) 
    
#     # is_active: Boolean, Not Null, Default: True
#     is_active = Column(Boolean, nullable=False, default=True)
    
#     # created_at: DateTime, Not Null, Creation timestamp
#     # default=sql_func.now() sets the time in the database upon creation
#     created_at = Column(DateTime(timezone=True), nullable=False, default=sql_func.now())
    
#     def __repr__(self):
#         return f"<Service(id='{self.id}', name='{self.name}', price={self.base_price})>"

from app.db.base import Base, default_uuid, default_timestamp
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

    def __repr__(self):
        return f"<Service(name='{self.name}')>"