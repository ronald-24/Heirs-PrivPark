from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from typing import List
from datetime import datetime

from app.db.models.parking import ParkingSpace, Availability


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
