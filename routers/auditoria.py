from fastapi import APIRouter, HTTPException
from typing import List, Optional
from services.audit_service import get_historial, get_metadatos
from services.sensitivity_service import classify_sensitivity
from database.models import AuditEntry, SensibilidadEnum
from cache.cache import cache_get, cache_set

router = APIRouter(prefix="/auditoria", tags=["auditoria"])


@router.get("/historial/{id_registro}")
async def get_historial_endpoint(id_registro: str) -> List[AuditEntry]:
    """Get complete audit history for a biological record."""

    # Try cache first
    cache_key = f"historial:{id_registro}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    try:
        historial = await get_historial(id_registro)

        if not historial:
            raise HTTPException(status_code=404, detail="No audit history found")

        # Cache for 60s (changes frequently)
        await cache_set(cache_key, [entry.dict(default=str) for entry in historial], ttl=60)

        return historial
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metadatos/{id_registro}")
async def get_metadatos_endpoint(id_registro: str) -> dict:
    """Get metadata (identificacion_basica + informacion_registro) from latest snapshot."""

    # Try cache first
    cache_key = f"metadatos:{id_registro}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    try:
        metadatos = await get_metadatos(id_registro)

        if not metadatos:
            raise HTTPException(status_code=404, detail="No metadata found")

        # Cache for 300s
        await cache_set(cache_key, metadatos, ttl=300)

        return metadatos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sensibilidad/{id_registro}")
async def get_sensibilidad_endpoint(id_registro: str) -> dict:
    """Get sensitivity classification for a biological record."""

    # Try cache first
    cache_key = f"sensibilidad:{id_registro}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    try:
        metadatos = await get_metadatos(id_registro)

        if not metadatos:
            raise HTTPException(status_code=404, detail="No record found")

        # Build full record from metadata and latest snapshot
        from database.connection import get_records_collection
        records_col = get_records_collection()
        record_doc = await records_col.find_one({"id_registro": id_registro})

        if not record_doc:
            raise HTTPException(status_code=404, detail="No record found")

        sensibilidad = classify_sensitivity(record_doc.get("data", {}))

        result = {
            "id_registro": id_registro,
            "sensibilidad": sensibilidad.value
        }

        # Cache for 300s
        await cache_set(cache_key, result, ttl=300)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
