from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import verify_bearer_token_and_get_user
from app.core.security import require_role
from app.db.session import get_db
from app.db.repositories.user_repo import list_users, admin_update_user
from app.db.repositories.parking_repo import get_parking_space, admin_set_listing_status
from app.db.repositories.issue_report_repo import (
    list_issue_reports,
    get_issue_report,
    admin_update_issue_report,
)
from app.schemas.user import AdminUserUpdate, AdminUserListOut
from app.schemas.parking import ParkingSpaceOut
from app.schemas.issue_report import AdminIssueReportUpdate, IssueReportOut


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[AdminUserListOut])
def admin_list_users(
    Authorization: str | None = Header(default=None), db: Session = Depends(get_db)
):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    require_role("admin", user.role)
    return list_users(db)


@router.put("/users/{user_id}", response_model=AdminUserListOut)
def admin_update_user_info(
    user_id: int,
    payload: AdminUserUpdate,
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    current_user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    require_role("admin", current_user.role)
    from app.db.models import User
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u = admin_update_user(db, user=u, role=payload.role,
                          is_active=payload.is_active)
    return u


@router.put("/listings/{parking_id}/status", response_model=ParkingSpaceOut)
def admin_update_listing_status(
    parking_id: int,
    status: str,
    is_active: bool | None = None,
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    require_role("admin", user.role)
    ps = get_parking_space(db, parking_id)
    if not ps:
        raise HTTPException(status_code=404, detail="Parking not found")
    ps = admin_set_listing_status(db, ps, status=status, is_active=is_active)
    return ps


@router.get("/issue-reports", response_model=list[IssueReportOut])
def admin_list_issue_reports(
    Authorization: str | None = Header(default=None), db: Session = Depends(get_db)
):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    require_role("admin", user.role)
    return list_issue_reports(db)


@router.put("/issue-reports/{issue_report_id}", response_model=IssueReportOut)
def admin_update_issue_report_status(
    issue_report_id: int,
    payload: AdminIssueReportUpdate,
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    require_role("admin", user.role)
    ir = get_issue_report(db, issue_report_id)
    if not ir:
        raise HTTPException(status_code=404, detail="Issue report not found")
    ir = admin_update_issue_report(db, ir, status=payload.status,
                                   admin_notes=payload.admin_notes)
    return ir
