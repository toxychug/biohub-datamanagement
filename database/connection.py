from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from config import settings
from typing import Optional

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo():
    global _client, _db
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _db = _client[settings.mongodb_db_name]
    await _client.admin.command("ping")
    print(f"[✓] Connected to MongoDB: {settings.mongodb_db_name}")


async def close_mongo():
    global _client
    if _client is not None:
        _client.close()
        print("[✓] MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    if _db is None:
        raise RuntimeError("Database not connected. Call connect_to_mongo() first.")
    return _db


def get_audit_collection() -> AsyncIOMotorCollection:
    db = get_database()
    return db["audit_entries"]


def get_records_collection() -> AsyncIOMotorCollection:
    db = get_database()
    return db["biological_records"]
