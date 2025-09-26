from fastapi import APIRouter, Header, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import verify_bearer_token_and_get_user
from app.db.session import get_db
from app.schemas.parking import (
    ParkingSpaceCreate,
    ParkingSpaceOut,
    ParkingSpaceUpdate,
    AvailabilityCreate,
    AvailabilityOut,
    ParkingSearchResult,
)
from app.db.repositories.parking_repo import (
    create_parking_space,
    get_parking_space,
    list_parking_spaces,
    update_parking_space,
    delete_parking_space,
    add_availability,
    list_availabilities,
    delete_availability,
    search_parking_spaces,
)
from app.core.storage import upload_fileobj_to_s3

from datetime import datetime

# Optional dependency; if missing, expect ISO8601
from dateutil import parser as dateutil_parser


router = APIRouter(prefix="/parking", tags=["parking"])


@router.post("/", response_model=ParkingSpaceOut)
def create_space(payload: ParkingSpaceCreate, Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    data = payload.dict()
    # convert photos list to comma-separated string for storage
    photos = data.pop("photos", None)
    if photos:
        data["photos"] = ",".join(photos)
    ps = create_parking_space(db, user.id, data=data)
    return ps


@router.get("/", response_model=List[ParkingSpaceOut])
def list_spaces(Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    spaces = list_parking_spaces(db, owner_id=user.id)
    return spaces


@router.get("/{parking_id}", response_model=ParkingSpaceOut)
def get_space(parking_id: int, Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    ps = get_parking_space(db, parking_id)
    if ps is None or ps.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    return ps


@router.put("/{parking_id}", response_model=ParkingSpaceOut)
def update_space(parking_id: int, payload: ParkingSpaceUpdate, Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    ps = get_parking_space(db, parking_id)
    if ps is None or ps.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    data = payload.dict(exclude_unset=True)
    photos = data.pop("photos", None)
    if photos is not None:
        data["photos"] = ",".join(photos)
    updated = update_parking_space(db, ps, data)
    return updated


@router.delete("/{parking_id}")
def delete_space(parking_id: int, Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    ps = get_parking_space(db, parking_id)
    if ps is None or ps.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    delete_parking_space(db, ps)
    return {"ok": True}


# Availability endpoints
@router.post("/{parking_id}/availability", response_model=AvailabilityOut)
def add_space_availability(parking_id: int, payload: AvailabilityCreate, Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    ps = get_parking_space(db, parking_id)
    if ps is None or ps.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    av = add_availability(db, parking_id, start=payload.start, end=payload.end)
    return av


@router.post("/{parking_id}/photos")
def upload_parking_photo(parking_id: int, file: UploadFile = File(...), Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    ps = get_parking_space(db, parking_id)
    if ps is None or ps.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    # Upload to S3 and append URL to photos
    url = upload_fileobj_to_s3(
        file.file, file.filename, content_type=file.content_type)
    # merge into existing photos CSV
    existing = ps.photos or ""
    if existing:
        new_photos = existing + "," + url
    else:
        new_photos = url
    ps.photos = new_photos
    db.commit()
    db.refresh(ps)
    return {"url": url}


@router.get("/{parking_id}/availability", response_model=List[AvailabilityOut])
def list_space_availability(parking_id: int, Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    # public read allowed for now
    return list_availabilities(db, parking_id)


@router.delete("/availability/{availability_id}")
def delete_space_availability(availability_id: int, Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    # ensure ownership by joining availability -> parking
    av = db.get(type(list_availabilities).__annotations__.get(
        'return', object), availability_id)
    # fallback simple query
    from app.db.models.parking import Availability
    av = db.get(Availability, availability_id)
    if av is None:
        raise HTTPException(status_code=404, detail="Not found")
    if av.parking_space.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    delete_availability(db, av)
    return {"ok": True}


@router.get("/search", response_model=List[ParkingSearchResult])
def search_parking(
    lat: float = Query(...),
    lng: float = Query(...),
    radius_m: float = Query(3000, ge=100, le=20000),
    start_time: str | None = Query(None),
    end_time: str | None = Query(None),
    max_price: float | None = Query(None),
    sort: str = Query("distance", pattern="^(distance|price)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):

    def parse_dt(value: str | None):
        if value is None:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            try:
                return dateutil_parser.isoparse(value)
            except Exception:
                raise HTTPException(
                    status_code=422, detail="Invalid datetime format")

    start_dt = parse_dt(start_time)
    end_dt = parse_dt(end_time)
    if (start_dt is None) ^ (end_dt is None):
        raise HTTPException(
            status_code=422, detail="Both start_time and end_time are required together")

    results = search_parking_spaces(
        db,
        center_lat=lat,
        center_lng=lng,
        radius_m=radius_m,
        start_time=start_dt,
        end_time=end_dt,
        max_price=max_price,
        sort=sort,
        limit=limit,
        offset=offset,
    )
    out: List[ParkingSearchResult] = []
    for ps, dist in results:
        out.append(
            ParkingSearchResult(
                id=ps.id,
                title=ps.title,
                address=ps.address,
                latitude=ps.latitude or 0.0,
                longitude=ps.longitude or 0.0,
                price_per_hour=ps.price_per_hour,
                distance_m=round(dist, 2),
            )
        )
    return out
