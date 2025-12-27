from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class BookingBase(BaseModel):
    status: Optional[str] = "pending"


class BookingCreate(BookingBase):
    service_id: UUID
    appointment_time: datetime


class BookingResponse(BookingBase):
    id: UUID
    user_id: UUID
    created_at: datetime

    model_config = {
        "from_attributes": True  # replaces orm_mode=True in pydantic v2
    }
