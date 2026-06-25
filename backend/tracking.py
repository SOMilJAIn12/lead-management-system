"""
tracking.py
-----------
Email engagement tracking endpoints:

  GET /open/{lead_id}
      Called automatically by the recipient's email client when it loads
      the hidden 1x1 tracking pixel embedded in the email. Marks the lead's
      `email_opened` flag as True and records `opened_at`. Always returns a
      transparent PNG image (so the email client renders nothing visible,
      and so the request never looks broken even if the lead_id is unknown).

  GET /click/{lead_id}
      Called when the lead clicks the "learn more" link in the email. Marks
      `link_clicked` as True, records `clicked_at`, then redirects the
      browser to the final destination page.
"""
import base64
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import Response, RedirectResponse
from database import get_db

router = APIRouter()

# A verified, valid 1x1 fully-transparent PNG (RGBA), base64 encoded.
_TRANSPARENT_PIXEL_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGNgAAIA"
    "AAUAAXpeqz8AAAAASUVORK5CYII="
)
TRANSPARENT_PIXEL = base64.b64decode(_TRANSPARENT_PIXEL_B64)

# Where users land after clicking the tracked link in the email.
REDIRECT_TARGET = "https://example.com"


@router.get("/open/{lead_id}")
async def track_open(lead_id: str):
    """Mark an email as opened, then return a 1x1 transparent tracking pixel."""
    db = get_db()
    if db is not None:
        # Only set opened_at the first time, but this filter also makes the
        # update a no-op (harmless) for unknown lead_ids.
        await db.leads.update_one(
            {"_id": lead_id, "email_opened": {"$ne": True}},
            {"$set": {"email_opened": True, "opened_at": datetime.utcnow()}},
        )
    return Response(content=TRANSPARENT_PIXEL, media_type="image/png")


@router.get("/click/{lead_id}")
async def track_click(lead_id: str):
    """Mark a lead's tracked link as clicked, then redirect to the destination page."""
    db = get_db()
    if db is not None:
        await db.leads.update_one(
            {"_id": lead_id, "link_clicked": {"$ne": True}},
            {"$set": {"link_clicked": True, "clicked_at": datetime.utcnow()}},
        )
    return RedirectResponse(url=REDIRECT_TARGET)
