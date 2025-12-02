from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class OrderBase(BaseModel):
    description: Optional[str] = None
    quoted_price: Optional[Decimal] = None
    actual_price: Optional[Decimal] = None
    notes: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

class OrderCreate(OrderBase):
    client_id: UUID
    service_id: UUID

# class OrderUpdateIMG(OrderBase):
#     im

class OrderResponse(OrderBase):
    id: UUID
    client_id: UUID
    service_id: UUID
    requested_date: datetime
    estimated_completion: datetime
    actual_completion: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True  # replaces orm_mode=True in pydantic v2
    }
