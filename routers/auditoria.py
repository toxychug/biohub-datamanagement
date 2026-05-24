from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Optional
from services.audit_service import get_historial, get_metadatos, get_all_records, get_all_audit_entries
from services.sensitivity_service import classify_sensitivity
from database.models import AuditEntry, SensibilidadEnum, MetadatosResponse, SensibilidadResponse, RegistrosListResponse, AuditListResponse
from services.audit_service import get_historial, get_metadatos, get_all_records
from services.sensitivity_service import classify_sensitivity
from database.models import AuditEntry, SensibilidadEnum, MetadatosResponse, SensibilidadResponse, RegistrosListResponse
from cache.cache import cache_get, cache_set

router = APIRouter(prefix="/auditoria", tags=["auditoria"])


@router.get(
    "/registros",
    response_model=RegistrosListResponse,
    summary="Obtener todos los registros biológicos",
    responses={
        500: {"description": "Error interno del servidor"},
    },
)
async def get_all_registros_endpoint(
    limit: int = Query(20, ge=1, le=100, description="Número máximo de registros a retornar"),
    offset: int = Query(0, ge=0, description="Número de registros a omitir (paginación)"),
) -> RegistrosListResponse:
    """Retorna el snapshot más reciente de todos los registros biológicos, ordenados por fecha descendente. Soporta paginación con `limit` y `offset`."""
    try:
        total, registros = await get_all_records(limit=limit, offset=offset)
        return RegistrosListResponse(total=total, limit=limit, offset=offset, registros=registros)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/entradas",
    response_model=AuditListResponse,
    summary="Obtener todos los documentos de auditoría",
    responses={
        500: {"description": "Error interno del servidor"},
    },
)
async def get_all_audit_entries_endpoint(
    limit: int = Query(20, ge=1, le=100, description="Número máximo de entradas a retornar"),
    offset: int = Query(0, ge=0, description="Número de entradas a omitir (paginación)"),
) -> AuditListResponse:
    """Retorna todos los documentos de auditoría de todos los registros, ordenados por fecha descendente. Soporta paginación con `limit` y `offset`."""
    try:
        total, entradas = await get_all_audit_entries(limit=limit, offset=offset)
        return AuditListResponse(total=total, limit=limit, offset=offset, entradas=entradas)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/historial/{id_registro}",
    response_model=List[AuditEntry],
    summary="Obtener historial de auditoría de un registro biológico",
    responses={
        404: {"description": "No se encontró historial para el ID de registro dado"},
        500: {"description": "Error interno del servidor"},
    },
)
async def get_historial_endpoint(
    id_registro: str = Path(..., description="Identificador único del registro biológico", example="REG-001")
) -> List[AuditEntry]:
    """Retorna el rastro de auditoría completo e inmutable de un registro biológico, ordenado por versión ascendente."""

    # Try cache first
    cache_key = f"historial:{id_registro}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        historial = await get_historial(id_registro)

        if historial is None or len(historial) == 0:
            raise HTTPException(status_code=404, detail="No audit history found")

        # Cache for 60s (changes frequently)
        await cache_set(cache_key, [entry.model_dump(mode="json") for entry in historial], ttl=60)

        return historial
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/metadatos/{id_registro}",
    response_model=MetadatosResponse,
    summary="Obtener metadatos de un registro biológico",
    responses={
        404: {"description": "No se encontraron metadatos para el ID de registro dado"},
        500: {"description": "Error interno del servidor"},
    },
)
async def get_metadatos_endpoint(
    id_registro: str = Path(..., description="Identificador único del registro biológico", example="REG-001")
) -> MetadatosResponse:
    """Retorna `identificacion_basica` e `informacion_registro` del snapshot más reciente del registro."""

    # Try cache first
    cache_key = f"metadatos:{id_registro}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        metadatos = await get_metadatos(id_registro)

        if metadatos is None:
            raise HTTPException(status_code=404, detail="No metadata found")

        # Cache for 300s
        await cache_set(cache_key, metadatos, ttl=300)

        return metadatos
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/sensibilidad/{id_registro}",
    response_model=SensibilidadResponse,
    summary="Obtener clasificación de sensibilidad de un registro biológico",
    responses={
        404: {"description": "No se encontró el registro para el ID dado"},
        500: {"description": "Error interno del servidor"},
    },
)
async def get_sensibilidad_endpoint(
    id_registro: str = Path(..., description="Identificador único del registro biológico", example="REG-001")
) -> SensibilidadResponse:
    """Clasifica el registro como PUBLIC, RESTRICTED o CONFIDENTIAL según el nivel de sensibilidad de la geolocalización."""

    # Try cache first
    cache_key = f"sensibilidad:{id_registro}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        metadatos = await get_metadatos(id_registro)

        if metadatos is None:
            raise HTTPException(status_code=404, detail="No record found")

        # Build full record from metadata and latest snapshot
        from database.connection import get_records_collection
        records_col = get_records_collection()
        record_doc = await records_col.find_one({"id_registro": id_registro})

        if record_doc is None:
            raise HTTPException(status_code=404, detail="No record found")

        sensibilidad = classify_sensitivity(record_doc.get("data", {}))

        result = {
            "id_registro": id_registro,
            "sensibilidad": sensibilidad.value
        }

        # Cache for 300s
        await cache_set(cache_key, result, ttl=300)

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
