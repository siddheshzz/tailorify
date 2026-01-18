from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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
    password: str = Field(..., min_length=8)
    user_type: UserRole = UserRole.CLIENT
    # is_active: bool

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that name is not just whitespace."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty or just whitespace")
        return v.strip()
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v and not v.strip():
            return None  # Convert empty string to None
        return v.strip() if v else None
    
    @field_validator("address")
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        """Validate address."""
        if v and not v.strip():
            return None  # Convert empty string to None
        return v.strip() if v else None



# -----------------------------------------
# Regular user: Update their own info ONLY
# -----------------------------------------
class UserUpdateSelf(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    password: Optional[str] = None  # user can change their password

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
