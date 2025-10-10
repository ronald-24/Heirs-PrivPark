from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    email: str | None = None
    display_name: str | None = None
    photo_url: str | None = None
    role: str | None = None
    is_active: bool | None = None


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    display_name: str | None = None
    photo_url: str | None = None


class AdminUserUpdate(BaseModel):
    role: str | None = None
    is_active: bool | None = None


class AdminUserListOut(BaseModel):
    id: int
    email: str | None = None
    display_name: str | None = None
    role: str
    is_active: bool
    created_at: datetime | None = None

    class Config:
        from_attributes = True
