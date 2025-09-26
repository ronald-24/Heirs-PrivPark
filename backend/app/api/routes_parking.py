from fastapi import APIRouter, Header, Depends, HTTPException, UploadFile, File
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
)
from app.core.storage import upload_fileobj_to_s3


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
