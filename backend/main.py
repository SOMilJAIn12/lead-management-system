"""
main.py
-------
FastAPI application entrypoint for the Automated Lead Management & Email
Tracking System.

Wires together:
  - MongoDB connection (database.py) via a lifespan handler
  - CORS for the Vite dev server
  - POST /lead        - capture a lead, classify it, persist it, email it
  - GET  /leads       - list all leads (optionally filtered by `search`)
  - GET  /dashboard   - aggregate stats for the dashboard cards/charts
  - /open and /click  - tracking endpoints (tracking.py)
"""
import os
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import connect_to_mongo, close_mongo_connection, get_db
from models import Lead
from schemas import LeadCreate, LeadResponse, DashboardStats
from email_service import send_lead_email
from ai_classifier import classify_lead
from tracking import router as tracking_router

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("main")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: open the MongoDB connection once and reuse it for every request.
    await connect_to_mongo()
    yield
    # Shutdown: close the connection cleanly.
    await close_mongo_connection()


app = FastAPI(
    title="Automated Lead Management & Email Tracking System",
    description="Lead capture, MongoDB storage, automated tracked emails, and a dashboard.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allow the React (Vite) dev server to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the /open/{lead_id} and /click/{lead_id} tracking endpoints.
app.include_router(tracking_router, tags=["tracking"])


def lead_to_response(doc: dict) -> dict:
    """Convert a raw MongoDB lead document (_id-based) into the API response shape (id-based)."""
    doc = dict(doc)
    doc["id"] = doc.pop("_id")
    return doc


@app.get("/")
async def root():
    """Simple health check / landing route for the API."""
    return {"status": "ok", "service": "Lead Management API"}


@app.post("/lead", response_model=LeadResponse)
async def create_lead(payload: LeadCreate):
    """
    Capture a new lead.

    Flow:
      1. Pydantic (LeadCreate) validates required fields automatically.
      2. The keyword-based AI classifier assigns a category + priority.
      3. The lead is saved to MongoDB.
      4. A personalized, tracked thank-you email is sent (best-effort -
         if sending fails, the lead is still saved and returned).
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    # --- AI Bonus: classify the lead from its requirement text ---
    category, priority = classify_lead(payload.requirement)

    lead = Lead(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        company=payload.company,
        requirement=payload.requirement,
        category=category,
        priority=priority,
    )

    doc = lead.to_mongo()

    try:
        await db.leads.insert_one(doc)
    except Exception as e:
        logger.error(f"Failed to insert lead into MongoDB: {e}")
        raise HTTPException(status_code=500, detail="Failed to save lead") from e

    # --- Send the personalized tracked email (best-effort) ---
    try:
        sent = send_lead_email(
            full_name=lead.full_name,
            to_email=lead.email,
            requirement=lead.requirement,
            lead_id=lead.id,
        )
    except Exception as e:
        logger.error(f"Unexpected error while sending email: {e}")
        sent = False

    if sent:
        await db.leads.update_one({"_id": lead.id}, {"$set": {"email_sent": True}})
        doc["email_sent"] = True

    return lead_to_response(doc)


@app.get("/leads", response_model=List[LeadResponse])
async def list_leads(search: Optional[str] = None):
    """
    Return all leads, most recent first.
    Optional `search` query param does a case-insensitive match across
    name, email, company, and requirement (powers the dashboard search box).
    """
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    query = {}
    if search:
        regex = {"$regex": search, "$options": "i"}
        query = {
            "$or": [
                {"full_name": regex},
                {"email": regex},
                {"company": regex},
                {"requirement": regex},
                {"category": regex},
                {"priority": regex},
            ]
        }

    cursor = db.leads.find(query).sort("submitted_at", -1)
    leads = [lead_to_response(doc) async for doc in cursor]
    return leads


@app.get("/dashboard", response_model=DashboardStats)
async def dashboard():
    """Aggregate stats powering the dashboard cards and charts."""
    db = get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    total_leads = await db.leads.count_documents({})
    emails_sent = await db.leads.count_documents({"email_sent": True})
    emails_opened = await db.leads.count_documents({"email_opened": True})
    link_clicks = await db.leads.count_documents({"link_clicked": True})

    open_rate = round((emails_opened / emails_sent) * 100, 2) if emails_sent else 0.0
    click_rate = round((link_clicks / emails_opened) * 100, 2) if emails_opened else 0.0

    category_breakdown = {}
    async for doc in db.leads.aggregate([{"$group": {"_id": "$category", "count": {"$sum": 1}}}]):
        category_breakdown[doc["_id"] or "General"] = doc["count"]

    priority_breakdown = {}
    async for doc in db.leads.aggregate([{"$group": {"_id": "$priority", "count": {"$sum": 1}}}]):
        priority_breakdown[doc["_id"] or "Medium"] = doc["count"]

    return DashboardStats(
        total_leads=total_leads,
        emails_sent=emails_sent,
        emails_opened=emails_opened,
        open_rate=open_rate,
        link_clicks=link_clicks,
        click_rate=click_rate,
        category_breakdown=category_breakdown,
        priority_breakdown=priority_breakdown,
    )
