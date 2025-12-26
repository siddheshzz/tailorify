from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class OrderImageBase(BaseModel):
    image_type: Literal["before", "after", "reference", "instruction"]


class OrderImageCreate(OrderImageBase):
    pass


class OrderImageResponse(OrderImageBase):
    id: UUID
    order_id: UUID
    uploaded_by: UUID
    s3_object_path: str
    s3_url: str
    uploaded_at: datetime

    class Config:
        orm_mode = True


class ImageUploadConfirmation(BaseModel):
    s3_object_path: str
    s3_url: str
    uploaded_by: UUID
    image_type: Literal["before", "after", "reference", "instruction"]
