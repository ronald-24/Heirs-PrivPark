from sqlalchemy.orm import Session
from sqlalchemy import select, delete, exists, and_, func
from typing import List, Tuple
from datetime import datetime
import math

from app.db.models.parking import ParkingSpace, Availability, ListingStatus


def create_parking_space(db: Session, owner_id: int, *, data: dict) -> ParkingSpace:
    ps = ParkingSpace(owner_id=owner_id, **data)
    db.add(ps)
    db.commit()
    db.refresh(ps)
    return ps


def get_parking_space(db: Session, parking_id: int) -> ParkingSpace | None:
    return db.execute(select(ParkingSpace).where(ParkingSpace.id == parking_id)).scalar_one_or_none()


def list_parking_spaces(db: Session, owner_id: int | None = None) -> List[ParkingSpace]:
    q = select(ParkingSpace)
    if owner_id is not None:
        q = q.where(ParkingSpace.owner_id == owner_id)
    return db.execute(q).scalars().all()


def update_parking_space(db: Session, parking: ParkingSpace, data: dict) -> ParkingSpace:
    for k, v in data.items():
        setattr(parking, k, v)
    db.commit()
    db.refresh(parking)
    return parking


def delete_parking_space(db: Session, parking: ParkingSpace) -> None:
    db.delete(parking)
    db.commit()


# Availability
def add_availability(db: Session, parking_space_id: int, start: datetime, end: datetime) -> Availability:
    av = Availability(parking_space_id=parking_space_id, start=start, end=end)
    db.add(av)
    db.commit()
    db.refresh(av)
    return av


def list_availabilities(db: Session, parking_space_id: int):
    return db.execute(select(Availability).where(Availability.parking_space_id == parking_space_id)).scalars().all()


def delete_availability(db: Session, availability: Availability) -> None:
    db.delete(availability)
    db.commit()


def admin_set_listing_status(
    db: Session,
    parking: ParkingSpace,
    *,
    status: ListingStatus | str,
    is_active: bool | None = None,
) -> ParkingSpace:
    if isinstance(status, str):
        status = ListingStatus(status)
    parking.status = status
    if is_active is not None:
        parking.is_active = is_active
    db.add(parking)
    db.commit()
    db.refresh(parking)
    return parking


def _haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in meters between two WGS84 points using Haversine."""
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * \
        math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def search_parking_spaces(
    db: Session,
    *,
    center_lat: float,
    center_lng: float,
    radius_m: float,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    max_price: float | None = None,
    sort: str = "distance",
    limit: int = 50,
    offset: int = 0,
) -> List[Tuple[ParkingSpace, float]]:
    """
    Returns a list of (ParkingSpace, distance_m) within radius, filtered by price and availability.
    Availability rule: if start_time/end_time provided, there must exist an Availability
    whose [start, end] fully covers the requested interval.
    """
    # Bounding box pre-filter in degrees
    # Approx degrees per meter
    delta_lat = radius_m / 111_320.0
    # Guard cos for poles
    cos_lat = math.cos(math.radians(center_lat))
    delta_lng = radius_m / (111_320.0 * (cos_lat if cos_lat != 0 else 1e-6))

    min_lat = center_lat - delta_lat
    max_lat = center_lat + delta_lat
    min_lng = center_lng - delta_lng
    max_lng = center_lng + delta_lng

    conditions = [
        ParkingSpace.latitude.is_not(None),
        ParkingSpace.longitude.is_not(None),
        ParkingSpace.latitude.between(min_lat, max_lat),
        ParkingSpace.longitude.between(min_lng, max_lng),
    ]
    if max_price is not None:
        conditions.append(ParkingSpace.price_per_hour <= max_price)

    if start_time is not None and end_time is not None:
        availability_exists = exists().where(
            and_(
                Availability.parking_space_id == ParkingSpace.id,
                Availability.start <= start_time,
                Availability.end >= end_time,
            )
        )
        conditions.append(availability_exists)

    q = select(ParkingSpace).where(and_(*conditions))
    candidates = db.execute(q).scalars().all()

    results: List[Tuple[ParkingSpace, float]] = []
    for ps in candidates:
        if ps.latitude is None or ps.longitude is None:
            continue
        d = _haversine_distance_m(
            center_lat, center_lng, ps.latitude, ps.longitude)
        if d <= radius_m:
            results.append((ps, d))

    if sort == "price":
        results.sort(key=lambda t: (t[0].price_per_hour or float("inf"), t[1]))
    else:
        results.sort(key=lambda t: t[1])

    # Pagination on the sorted results
    results = results[offset: offset + limit]
    return results
