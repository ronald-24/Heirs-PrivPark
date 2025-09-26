from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class AvailabilityCreate(BaseModel):
    start: datetime
    end: datetime


class AvailabilityOut(AvailabilityCreate):
    id: int

    class Config:
        from_attributes = True


class ParkingSpaceBase(BaseModel):
    title: str
    description: str | None = None
    photos: List[str] | None = None
    price_per_hour: float | None = None
    rules: str | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class ParkingSpaceCreate(ParkingSpaceBase):
    pass


class ParkingSpaceUpdate(ParkingSpaceBase):
    pass


class ParkingSpaceOut(ParkingSpaceBase):
    id: int
    owner_id: int
    availabilities: List[AvailabilityOut] | None = None

    class Config:
        from_attributes = True
