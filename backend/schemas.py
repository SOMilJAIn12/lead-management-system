"""
schemas.py
----------
Pydantic schemas used at the API boundary:
  - LeadCreate: validated shape of incoming POST /lead requests
  - LeadResponse: shape returned to the frontend for a single lead
  - DashboardStats: shape returned by GET /dashboard
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict
from datetime import datetime


class LeadCreate(BaseModel):
    """Incoming payload from the Lead Capture Form."""

    full_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(..., min_length=7, max_length=20)
    company: Optional[str] = Field(default=None, max_length=120)
    requirement: str = Field(..., min_length=5)

    @validator("full_name")
    def full_name_not_blank(cls, v):
        if not v.strip():
            raise ValueError("Full name cannot be blank")
        return v.strip()

    @validator("phone")
    def phone_basic_check(cls, v):
        digits = "".join(ch for ch in v if ch.isdigit())
        if len(digits) < 7:
            raise ValueError("Phone number must contain at least 7 digits")
        return v.strip()

    @validator("company")
    def company_strip(cls, v):
        return v.strip() if v else v

    @validator("requirement")
    def requirement_not_blank(cls, v):
        if not v.strip():
            raise ValueError("Requirement cannot be blank")
        return v.strip()


class LeadResponse(BaseModel):
    """Shape of a lead as returned by the API (POST /lead, GET /leads)."""

    id: str
    full_name: str
    email: EmailStr
    phone: str
    company: Optional[str] = None
    requirement: str
    submitted_at: datetime
    email_sent: bool
    email_opened: bool
    opened_at: Optional[datetime] = None
    link_clicked: bool
    clicked_at: Optional[datetime] = None
    category: str
    priority: str


class DashboardStats(BaseModel):
    """Shape returned by GET /dashboard."""

    total_leads: int
    emails_sent: int
    emails_opened: int
    open_rate: float
    link_clicks: int
    click_rate: float
    category_breakdown: Dict[str, int]
    priority_breakdown: Dict[str, int]
