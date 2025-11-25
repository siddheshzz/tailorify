from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


# -----------------------------------------
# Base user schema (shared fields)
# -----------------------------------------
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    user_type: str         # "client" | "admin"
    is_active: bool


# -----------------------------------------
# Admin-only: Create a new user
# -----------------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str                     # plain password (hash before DB)
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    user_type: str                    # admin can set
    is_active: Optional[bool] = True  # admin chooses


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
class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    user_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }
