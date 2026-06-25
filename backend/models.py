"""
models.py
---------
Defines the `Lead` model: the internal representation of a lead document as
stored in MongoDB.

We deliberately generate our own `id` (a UUID string) instead of relying on
MongoDB's ObjectId, and store it directly as `_id`. This keeps the id a
plain string everywhere (API responses, tracking URLs like /open/{lead_id},
email links, frontend state) without ever having to serialize/deserialize
ObjectId.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid


class Lead(BaseModel):
    """Represents a single lead captured through the lead form."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    email: EmailStr
    phone: str
    company: Optional[str] = None
    requirement: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

    # Email engagement tracking
    email_sent: bool = False
    email_opened: bool = False
    opened_at: Optional[datetime] = None
    link_clicked: bool = False
    clicked_at: Optional[datetime] = None

    # AI classifier output
    category: str = "General"
    priority: str = "Medium"

    def to_mongo(self) -> dict:
        """Convert this model into a dict ready to insert into MongoDB (id -> _id)."""
        doc = self.dict()
        doc["_id"] = doc.pop("id")
        return doc

    @staticmethod
    def from_mongo(doc: dict) -> "Lead":
        """Build a Lead instance back from a raw MongoDB document (_id -> id)."""
        doc = dict(doc)
        doc["id"] = doc.pop("_id")
        return Lead(**doc)
