"""
In-memory database fallback for when MongoDB is unavailable.
Used in development mode when MongoDB is down or for testing.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from database.models import AuditEntry, BiologicalRecordSnapshot


class InMemoryDatabase:
    """Simple in-memory database that mimics MongoDB behavior."""
    
    def __init__(self):
        self.audit_entries: Dict[str, List[AuditEntry]] = {}  # id_registro -> [entries]
        self.biological_records: Dict[str, BiologicalRecordSnapshot] = {}  # id_registro -> snapshot

    async def insert_audit_entry(self, entry: AuditEntry) -> str:
        """Insert an audit entry and return its ID."""
        if entry.id_registro not in self.audit_entries:
            self.audit_entries[entry.id_registro] = []
        self.audit_entries[entry.id_registro].append(entry)
        return entry.id_registro

    async def get_audit_history(self, id_registro: str, limit: int = 100) -> List[AuditEntry]:
        """Get audit history for a record (newest first)."""
        if id_registro not in self.audit_entries:
            return []
        entries = self.audit_entries[id_registro]
        return sorted(entries, key=lambda x: x.version, reverse=True)[:limit]

    async def get_latest_audit_entry(self, id_registro: str) -> Optional[AuditEntry]:
        """Get the latest audit entry for a record."""
        history = await self.get_audit_history(id_registro, limit=1)
        return history[0] if history else None

    async def insert_or_update_record(self, record: BiologicalRecordSnapshot) -> str:
        """Insert or update a biological record snapshot."""
        self.biological_records[record.id_registro] = record
        return record.id_registro

    async def get_record_snapshot(self, id_registro: str) -> Optional[BiologicalRecordSnapshot]:
        """Get the latest snapshot of a record."""
        return self.biological_records.get(id_registro)

    async def get_all_records(self, limit: int = 100, skip: int = 0) -> List[BiologicalRecordSnapshot]:
        """Get all records with pagination."""
        records = list(self.biological_records.values())
        return records[skip:skip + limit]

    async def count_records(self) -> int:
        """Count total records."""
        return len(self.biological_records)

    async def delete_all(self):
        """Clear all data (useful for testing)."""
        self.audit_entries.clear()
        self.biological_records.clear()

    def __repr__(self) -> str:
        return (
            f"InMemoryDatabase("
            f"audit_entries={len(self.audit_entries)}, "
            f"records={len(self.biological_records)})"
        )


# Global in-memory database instance
_in_memory_db: Optional[InMemoryDatabase] = None


def get_in_memory_db() -> InMemoryDatabase:
    """Get or create the in-memory database instance."""
    global _in_memory_db
    if _in_memory_db is None:
        _in_memory_db = InMemoryDatabase()
    return _in_memory_db
