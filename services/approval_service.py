from database.connection import get_audit_collection
from database.models import ApprovalAction, AprobacionEnum, AuditEntry
from typing import Optional
from datetime import datetime


async def get_approval_status(id_registro: str) -> Optional[AprobacionEnum]:
    """Get the current approval status of a biological record."""

    audit_col = get_audit_collection()

    latest = await audit_col.find_one(
        {"id_registro": id_registro},
        sort=[("version", -1)]
    )

    if latest is not None:
        return AprobacionEnum(latest.get("estado_aprobacion", "PENDIENTE"))

    return None


async def update_approval(action: ApprovalAction, snapshot: dict) -> AuditEntry:
    """Update approval status by creating a new immutable audit entry."""

    from services.audit_service import create_audit_entry
    from services.sensitivity_service import classify_sensitivity
    from database.models import TipoCambioEnum

    # Create new audit entry with updated approval state
    audit_entry = await create_audit_entry(
        record=snapshot,
        previous=snapshot,
        usuario=action.director_aprobador,
        motivo=f"Aprobación: {action.comentarios or 'Sin comentarios'}",
        sensibilidad=classify_sensitivity(snapshot),
        estado_aprobacion=action.nuevo_estado,
        tipo_cambio=TipoCambioEnum.CAMBIO_ESTADO,
    )

    return audit_entry
