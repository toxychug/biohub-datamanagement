from fastapi import APIRouter, HTTPException
from database.models import ApprovalAction, AprobacionEnum
from services.approval_service import get_approval_status, update_approval
from database.connection import get_records_collection
from cache.cache import cache_get, cache_set, cache_delete

router = APIRouter(prefix="/aprobacion", tags=["aprobacion"])


@router.get("/{id_registro}")
async def get_approval_status_endpoint(id_registro: str) -> dict:
    """Get the current approval status of a biological record."""

    # Try cache first
    cache_key = f"aprobacion:{id_registro}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        status = await get_approval_status(id_registro)

        if status is None:
            raise HTTPException(status_code=404, detail="No approval status found")

        result = {
            "id_registro": id_registro,
            "estado_aprobacion": status.value
        }

        # Cache for 300s
        await cache_set(cache_key, result, ttl=300)

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/actualizar")
async def update_approval_endpoint(action: ApprovalAction) -> dict:
    """Update the approval status of a biological record."""

    try:
        # Get current record snapshot
        records_col = get_records_collection()
        record_doc = await records_col.find_one({"id_registro": action.id_registro})

        if record_doc is None:
            raise HTTPException(status_code=404, detail="Record not found")

        snapshot = record_doc.get("data", {})

        # Update approval status
        audit_entry = await update_approval(action, snapshot)

        # Invalidate cache
        await cache_delete(f"aprobacion:{action.id_registro}")
        await cache_delete(f"historial:{action.id_registro}")

        return {
            "status": "ok",
            "id_registro": audit_entry.id_registro,
            "version": audit_entry.version,
            "nuevo_estado": audit_entry.estado_aprobacion.value,
            "timestamp": audit_entry.timestamp.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
