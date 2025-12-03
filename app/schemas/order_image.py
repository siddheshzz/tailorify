from pydantic import BaseModel
from uuid import UUID
from typing import Literal
from datetime import datetime

class OrderImageBase(BaseModel):
    image_type: Literal['before', 'after', 'reference', 'instruction']


class OrderImageCreate(OrderImageBase):
    pass


class OrderImageResponse(OrderImageBase):
    id: UUID
    order_id: UUID
    uploaded_by: UUID
    s3_url: str
    uploaded_at: datetime

    class Config:
        orm_mode = True


class ImageUploadConfirmation(BaseModel):
    s3_object_path: str
    uploaded_by: UUID