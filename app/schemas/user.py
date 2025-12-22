from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from uuid import UUID
from enum import Enum

class UserRole(str, Enum):
    CLIENT = "client"
    ADMIN = "admin"

# -----------------------------------------
# Base user schema (shared fields)
# -----------------------------------------
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    


# -----------------------------------------
# Admin-only: Create a new user
# -----------------------------------------
class UserCreate(UserBase):
    password:str = Field(..., min_length=8)
    user_type: UserRole = UserRole.CLIENT
    # is_active: bool


# -----------------------------------------
# Regular user: Update their own info ONLY
# -----------------------------------------
class UserUpdateSelf(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    password: Optional[str] = None   # user can change their password

    # user CANNOT edit:
    # - email
    # - user_type
    # - is_active


class UserResponse(UserBase):
    id: UUID
    user_type: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# -----------------------------------------
# Admin-only: Can update ANY user field
# -----------------------------------------
class UserUpdateAdmin(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    user_type: Optional[str] = None
    is_active: Optional[bool] = None


# -----------------------------------------
# Response model (API returns this)
# -----------------------------------------
# class UserResponse(BaseModel):
#     id: UUID
#     email: EmailStr
#     first_name: str
#     last_name: str
#     phone: Optional[str] = None
#     address: Optional[str] = None
#     user_type: str
#     is_active: bool
#     created_at: datetime
#     updated_at: datetime

#     model_config = {
#         "from_attributes": True
#     }

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

from uuid import UUID

class UserAuthPayload(BaseModel):
    id: str
    email: Optional[EmailStr] = None
    user_type: str