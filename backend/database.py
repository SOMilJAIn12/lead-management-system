"""
database.py
------------
Handles the MongoDB connection lifecycle using Motor (the async MongoDB driver).

The connection is created once on application startup (see `connect_to_mongo`,
called from main.py's lifespan handler) and reused for every request via
`get_db()`. This avoids opening a new connection per-request, which is slow
and wasteful.
"""
import os
import logging
from typing import Optional
import motor.motor_asyncio
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("database")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "lead_management")

# Module-level handles, populated by connect_to_mongo() at startup.
_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
_db: Optional[motor.motor_asyncio.AsyncIOMotorDatabase] = None


async def connect_to_mongo():
    """Open the MongoDB connection and ensure useful indexes exist."""
    global _client, _db
    _client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
    _db = _client[DB_NAME]

    # Indexes speed up the dashboard search box and sorting by submission time.
    await _db.leads.create_index("email")
    await _db.leads.create_index("submitted_at")
    await _db.leads.create_index("full_name")
    logger.info(f"Connected to MongoDB at {MONGO_URI}, database '{DB_NAME}'")


async def close_mongo_connection():
    """Close the MongoDB connection on application shutdown."""
    global _client
    if _client is not None:
        _client.close()
        logger.info("MongoDB connection closed")


def get_db():
    """
    Return the active database handle.
    Used inside route handlers / routers instead of importing `_db` directly,
    since `_db` is only assigned after `connect_to_mongo()` runs at startup.
    """
    return _db
