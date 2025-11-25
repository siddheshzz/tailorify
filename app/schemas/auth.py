from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    first_name : str
    last_name  : str
    phone : Optional[str] = None
    address : Optional[str] = None
    user_type : Literal['client', 'admin']


class UserCreate(UserBase):
    password :str

class User(UserBase):
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # class Config:
    #     # This setting is necessary for Pydantic to read data directly from
    #     # SQLAlchemy models (which use dot notation for attribute access).
    #     from_attributes = True # Pydantic v2
    #     # or orm_mode = True # Pydantic v1
    model_config = {
        "from_attributes": True  # replaces orm_mode=True in pydantic v2
    }

    

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
