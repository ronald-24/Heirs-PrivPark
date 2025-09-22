from fastapi import APIRouter, Header, Depends
from sqlalchemy.orm import Session

from app.api.deps import verify_bearer_token_and_get_user
from app.db.session import get_db
from app.schemas.user import UserOut, UserUpdate
from app.db.repositories.user_repo import upsert_from_claims


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    return user


@router.put("/me", response_model=UserOut)
def update_me(payload: UserUpdate, Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    user, claims = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    updated = upsert_from_claims(
        db,
        firebase_uid=claims["uid"],
        email=user.email,
        display_name=payload.display_name or user.display_name,
        photo_url=payload.photo_url or user.photo_url,
    )
    return updated
