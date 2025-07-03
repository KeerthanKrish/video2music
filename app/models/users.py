"""User-related Pydantic models."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user model with common fields."""

    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model."""

    password: str


class UserResponse(UserBase):
    """User response model for API responses."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class User(UserResponse):
    """Complete user model with all fields."""

    hashed_password: str 