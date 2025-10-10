from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.user import User


def get_by_firebase_uid(db: Session, firebase_uid: str) -> User | None:
    return db.execute(select(User).where(User.firebase_uid == firebase_uid)).scalar_one_or_none()


def upsert_from_claims(
    db: Session,
    firebase_uid: str,
    email: str | None,
    display_name: str | None,
    photo_url: str | None,
    password: str | None,
) -> User:
    user = get_by_firebase_uid(db, firebase_uid)
    if user is None:
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            display_name=display_name,
            photo_url=photo_url,
            password=password,
        )
        db.add(user)
    else:
        user.email = email or user.email
        user.display_name = display_name or user.display_name
        user.photo_url = photo_url or user.photo_url
        user.password = password or user.password
    db.commit()
    db.refresh(user)
    return user


def list_users(db: Session, *, limit: int = 100, offset: int = 0) -> list[User]:
    q = select(User).limit(limit).offset(offset)
    return db.execute(q).scalars().all()


def admin_update_user(db: Session, *, user: User, role: str | None = None, is_active: bool | None = None) -> User:
    if role is not None:
        user.role = role
    if is_active is not None:
        user.is_active = is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
