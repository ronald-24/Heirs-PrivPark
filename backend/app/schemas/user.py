from pydantic import BaseModel


class UserBase(BaseModel):
    email: str | None = None
    display_name: str | None = None
    photo_url: str | None = None
    role: str | None = None


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    display_name: str | None = None
    photo_url: str | None = None
