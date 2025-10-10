from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel


class IssueReportBase(BaseModel):
    subject: str
    description: str


class IssueReportCreate(IssueReportBase):
    booking_id: int | None = None
    parking_space_id: int | None = None


class IssueReportUpdate(BaseModel):
    subject: str | None = None
    description: str | None = None


class AdminIssueReportUpdate(BaseModel):
    status: str | None = None
    admin_notes: str | None = None


class IssueReportOut(IssueReportBase):
    id: int
    created_by_user_id: int
    booking_id: int | None
    parking_space_id: int | None
    status: str
    admin_notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
