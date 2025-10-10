from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import verify_bearer_token_and_get_user
from app.db.session import get_db
from app.db.repositories.issue_report_repo import (
    create_issue_report,
    get_issue_report,
    update_issue_report,
)
from app.schemas.issue_report import IssueReportCreate, IssueReportUpdate, IssueReportOut


router = APIRouter(prefix="/issue-reports", tags=["issue-reports"])


@router.post("/", response_model=IssueReportOut)
def create_user_issue_report(
    payload: IssueReportCreate,
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    ir = create_issue_report(
        db,
        created_by_user_id=user.id,
        subject=payload.subject,
        description=payload.description,
        booking_id=payload.booking_id,
        parking_space_id=payload.parking_space_id,
    )
    return ir


@router.put("/{issue_report_id}", response_model=IssueReportOut)
def update_user_issue_report(
    issue_report_id: int,
    payload: IssueReportUpdate,
    Authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user, _ = verify_bearer_token_and_get_user(
        authorization=Authorization, db=db)
    ir = get_issue_report(db, issue_report_id)
    if not ir or ir.created_by_user_id != user.id:
        raise HTTPException(status_code=404, detail="Issue report not found")
    ir = update_issue_report(db, ir, subject=payload.subject,
                             description=payload.description)
    return ir
