from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BookingBase(BaseModel):
    service_id: int
    status: Optional[str] = "pending"

class BookingCreate(BookingBase):
    service_id:int
    appointment_time: datetime



class BookingResponse(BookingBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
