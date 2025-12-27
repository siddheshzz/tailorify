from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    base_price: float
    category: str
    estimated_days: int
    image_url: Optional[str] = None
    is_active: Optional[bool] = True


class ServiceCreate(ServiceBase):
    pass


class ServiceResponse(ServiceBase):
    id: UUID

    model_config = {
        "from_attributes": True  # replaces orm_mode=True in pydantic v2
    }


class ServiceUpdate(ServiceBase):
    pass
