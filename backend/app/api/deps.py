from typing import Annotated
from fastapi import Depends, HTTPException, status
from firebase_admin import auth as fb_auth, credentials, initialize_app
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.db.repositories.user_repo import upsert_from_claims


_firebase_initialized = False


def _init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return
    settings = get_settings()
    if not settings.firebase_credentials_path:
        raise RuntimeError("FIREBASE_CREDENTIALS_PATH not configured")
    cred = credentials.Certificate(settings.firebase_credentials_path)
    initialize_app(cred, {'projectId': settings.firebase_project_id}
                   if settings.firebase_project_id else None)
    _firebase_initialized = True


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
):
    # This dependency expects to be used with OAuth2 password bearer, but here
    # we will extract ID token inside route via Authorization header for simplicity.
    raise NotImplementedError


def verify_bearer_token_and_get_user(
    db: Annotated[Session, Depends(get_db)],
    authorization: str | None = None,
):
    _init_firebase()
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    id_token = authorization.split(" ", 1)[1]
    try:
        decoded = fb_auth.verify_id_token(id_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    firebase_uid = decoded.get("uid")
    email = decoded.get("email")
    name = decoded.get("name")
    picture = decoded.get("picture")

    user = upsert_from_claims(
        db, firebase_uid=firebase_uid, email=email, display_name=name, photo_url=picture)
    return user, decoded
