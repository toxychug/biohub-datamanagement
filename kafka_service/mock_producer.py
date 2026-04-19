from fastapi import APIRouter, HTTPException
from config import settings
from services.audit_service import create_audit_entry
from services.sensitivity_service import classify_sensitivity
from database.models import AprobacionEnum

router = APIRouter(prefix="/dev", tags=["development"])


@router.post("/simulate")
async def simulate_kafka_event(record: dict):
    """
    Simulate a Kafka event from Group 1 (only in development mode).
    Injects a biological record into the audit pipeline without using Kafka.
    """

    if settings.env != "development":
        raise HTTPException(
            status_code=403,
            detail="Mock Kafka producer only available in development mode"
        )

    try:
        sensibilidad = classify_sensitivity(record)

        audit_entry = await create_audit_entry(
            record=record,
            usuario=record.get("informacion_registro", {}).get("investigador", "system"),
            motivo=record.get("trazabilidad", {}).get("historial_cambios", [{}])[0].get("motivo", "Mock event"),
            sensibilidad=sensibilidad,
            estado_aprobacion=AprobacionEnum.PENDIENTE
        )

        return {
            "status": "ok",
            "id_registro": audit_entry.id_registro,
            "version": audit_entry.version,
            "timestamp": audit_entry.timestamp.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
