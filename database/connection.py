from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from config import settings
from typing import Optional, Union
from database.in_memory_db import get_in_memory_db

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None
_is_mongodb_available: bool = False
_use_in_memory: bool = False


async def connect_to_mongo():
    """
    Connect to MongoDB with fallback to in-memory database.
    If MongoDB fails, the app continues with in-memory storage in development mode.
    """
    global _client, _db, _is_mongodb_available, _use_in_memory
    
    try:
        _client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
        _db = _client[settings.mongodb_db_name]
        
        # Test the connection
        await _client.admin.command("ping")
        _is_mongodb_available = True
        _use_in_memory = False
        print(f"[✓] Connected to MongoDB: {settings.mongodb_db_name}")
        
    except Exception as e:
        print(f"[!] MongoDB connection failed: {e}")
        print("[*] Falling back to in-memory database (development mode)")
        
        _client = None
        _db = None
        _is_mongodb_available = False
        _use_in_memory = True
        
        if settings.env != "development":
            raise RuntimeError(
                "MongoDB connection failed and not in development mode. "
                "Cannot use in-memory fallback in production."
            )


async def close_mongo():
    global _client
    if _client is not None:
        _client.close()
        print("[✓] MongoDB connection closed")


def is_mongodb_available() -> bool:
    """Check if MongoDB is currently available."""
    return _is_mongodb_available


def is_using_in_memory() -> bool:
    """Check if using in-memory database."""
    return _use_in_memory


def get_database() -> Union[AsyncIOMotorDatabase, dict]:
    """
    Get database instance (MongoDB or in-memory).
    Returns AsyncIOMotorDatabase for MongoDB or a dict-like object for in-memory.
    """
    if _is_mongodb_available and _db is not None:
        return _db
    elif _use_in_memory:
        return get_in_memory_db()
    else:
        raise RuntimeError("Database not connected. Call connect_to_mongo() first.")


def get_audit_collection() -> Union[AsyncIOMotorCollection, object]:
    """Get audit entries collection (MongoDB or in-memory)."""
    db = get_database()
    
    if _is_mongodb_available:
        return db["audit_entries"]
    else:
        # Return a wrapper for in-memory database
        return InMemoryCollectionWrapper(db, "audit_entries")


def get_records_collection() -> Union[AsyncIOMotorCollection, object]:
    """Get biological records collection (MongoDB or in-memory)."""
    db = get_database()
    
    if _is_mongodb_available:
        return db["biological_records"]
    else:
        # Return a wrapper for in-memory database
        return InMemoryCollectionWrapper(db, "biological_records")


class InMemoryCollectionWrapper:
    """Wrapper to make in-memory database compatible with Motor collection interface."""
    
    def __init__(self, in_memory_db, collection_name: str):
        self.db = in_memory_db
        self.collection_name = collection_name
    
    async def insert_one(self, document):
        """Insert a document."""
        if self.collection_name == "audit_entries":
            return await self.db.insert_audit_entry(document)
        elif self.collection_name == "biological_records":
            return await self.db.insert_or_update_record(document)
    
    async def find(self, filter_dict, **kwargs):
        """Find documents (simplified for in-memory)."""
        return InMemoryFindCursor(self.db, self.collection_name, filter_dict, **kwargs)
    
    async def find_one(self, filter_dict):
        """Find a single document."""
        if self.collection_name == "audit_entries":
            id_registro = filter_dict.get("id_registro")
            if id_registro:
                entries = await self.db.get_audit_history(id_registro, limit=1)
                return entries[0] if entries else None
        elif self.collection_name == "biological_records":
            id_registro = filter_dict.get("id_registro")
            if id_registro:
                return await self.db.get_record_snapshot(id_registro)
        return None
    
    async def update_one(self, filter_dict, update_dict):
        """Update a document (simplified)."""
        if self.collection_name == "biological_records":
            id_registro = filter_dict.get("id_registro")
            if id_registro and "$set" in update_dict:
                record = await self.db.get_record_snapshot(id_registro)
                if record:
                    # Update the record
                    for key, value in update_dict["$set"].items():
                        setattr(record, key, value)
                    return {"modifiedCount": 1}
        return {"modifiedCount": 0}
    
    async def count_documents(self, filter_dict=None):
        """Count documents."""
        if self.collection_name == "biological_records":
            return await self.db.count_records()
        elif self.collection_name == "audit_entries":
            return len(self.db.audit_entries)
        return 0


class InMemoryFindCursor:
    """Cursor for in-memory find operations."""
    
    def __init__(self, db, collection_name: str, filter_dict: dict, **kwargs):
        self.db = db
        self.collection_name = collection_name
        self.filter = filter_dict
        self.kwargs = kwargs
        self._documents = []
        self._executed = False
    
    async def _execute(self):
        """Execute the query."""
        if not self._executed:
            if self.collection_name == "biological_records":
                self._documents = await self.db.get_all_records(
                    limit=self.kwargs.get("limit", 100),
                    skip=self.kwargs.get("skip", 0)
                )
            elif self.collection_name == "audit_entries":
                # Get all audit entries across all records
                all_entries = []
                for entries in self.db.audit_entries.values():
                    all_entries.extend(entries)
                # Sort by timestamp descending
                all_entries.sort(key=lambda x: x.timestamp, reverse=True)
                self._documents = all_entries
            self._executed = True
    
    async def to_list(self, length=None):
        """Get all documents as list."""
        await self._execute()
        if length:
            return self._documents[:length]
        return self._documents
    
    def __aiter__(self):
        """Async iterator support."""
        return self
    
    async def __anext__(self):
        """Get next document."""
        await self._execute()
        if not hasattr(self, '_index'):
            self._index = 0
        if self._index >= len(self._documents):
            raise StopAsyncIteration
        doc = self._documents[self._index]
        self._index += 1
        return doc
