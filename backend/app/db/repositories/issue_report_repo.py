from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models import IssueReport, IssueStatus


def create_issue_report(
    db: Session,
    *,
    created_by_user_id: int,
    subject: str,
    description: str,
    booking_id: int | None = None,
    parking_space_id: int | None = None,
) -> IssueReport:
    ir = IssueReport(
        created_by_user_id=created_by_user_id,
        subject=subject,
        description=description,
        booking_id=booking_id,
        parking_space_id=parking_space_id,
        status=IssueStatus.open,
    )
    db.add(ir)
    db.commit()
    db.refresh(ir)
    return ir


def list_issue_reports(db: Session, *, status: IssueStatus | None = None, limit: int = 100, offset: int = 0) -> list[IssueReport]:
    q = select(IssueReport).order_by(
        IssueReport.created_at.desc()).limit(limit).offset(offset)
    if status is not None:
        q = q.where(IssueReport.status == status)
    return db.execute(q).scalars().all()


def get_issue_report(db: Session, issue_report_id: int) -> IssueReport | None:
    return db.execute(select(IssueReport).where(IssueReport.id == issue_report_id)).scalar_one_or_none()


def update_issue_report(db: Session, ir: IssueReport, *, subject: str | None = None, description: str | None = None) -> IssueReport:
    if subject is not None:
        ir.subject = subject
    if description is not None:
        ir.description = description
    db.add(ir)
    db.commit()
    db.refresh(ir)
    return ir


def admin_update_issue_report(db: Session, ir: IssueReport, *, status: IssueStatus | str | None = None, admin_notes: str | None = None) -> IssueReport:
    if isinstance(status, str):
        status = IssueStatus(status)
    if status is not None:
        ir.status = status
    if admin_notes is not None:
        ir.admin_notes = admin_notes
    db.add(ir)
    db.commit()
    db.refresh(ir)
    return ir
