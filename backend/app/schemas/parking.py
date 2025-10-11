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
    is_active: bool | None = None
    status: str | None = None


class ParkingSpaceCreate(ParkingSpaceBase):
    pass


class ParkingSpaceUpdate(ParkingSpaceBase):
    pass


class ParkingSpaceOut(ParkingSpaceBase):
    id: int
    owner_id: int
    created_at: datetime | None = None
    availabilities: List[AvailabilityOut] | None = None

    class Config:
        from_attributes = True


class ParkingSearchResult(BaseModel):
    id: int
    title: str
    address: str | None = None
    latitude: float
    longitude: float
    price_per_hour: float | None = None
    distance_m: float


class ParkingSearchQuery(BaseModel):
    lat: float
    lng: float
    radius_m: float = Field(3000, ge=100, le=20000)
    start_time: datetime | None = None
    end_time: datetime | None = None
    max_price: float | None = None
    sort: str = Field("distance", pattern="^(distance|price)$")
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)
