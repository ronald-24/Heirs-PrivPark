from fastapi import APIRouter, Header, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import verify_bearer_token_and_get_user
from app.db.session import get_db
from app.schemas.user import UserOut


router = APIRouter(prefix="/auth", tags=["auth"])


class TokenResponse(BaseModel):
    user_id: int
    firebase_uid: str
    email: str | None
    message: str


@router.post("/verify-token", response_model=TokenResponse)
def verify_token(Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    """Vérifie un token Firebase et retourne les informations utilisateur"""
    user, claims = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    return TokenResponse(
        user_id=user.id,
        firebase_uid=claims.get("uid"),
        email=claims.get("email"),
        message="Token valide"
    )





@router.get("/me", response_model=UserOut)
def get_current_user(Authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    """Récupère les informations de l'utilisateur connecté"""
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    return user
