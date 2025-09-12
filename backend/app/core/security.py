# Placeholder for future role/scopes utilities

from fastapi import HTTPException, status


def require_role(role: str, user_role: str | None):
    if user_role != role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Insufficient permissions")
