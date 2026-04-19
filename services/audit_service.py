from database.connection import get_audit_collection, get_records_collection
from database.models import AuditEntry, FieldChange, SensibilidadEnum, AprobacionEnum
from datetime import datetime
from typing import Optional, List, Any
from deepdiff import DeepDiff


async def compute_field_changes(current: dict, previous: Optional[dict]) -> List[FieldChange]:
    """Compute the differences between two record versions."""
    if not previous:
        return []

    try:
        diff = DeepDiff(previous, current, ignore_order=True)
    except Exception:
        return []

    changes = []

    for key, value in diff.get("values_changed", {}).items():
        campo = key.replace("root['", "").replace("']", "").replace("']['", ".")
        old_val = value.get("old_value")
        new_val = value.get("new_value")
        changes.append(FieldChange(campo=campo, valor_anterior=old_val, valor_nuevo=new_val))

    for key in diff.get("dictionary_item_added", []):
        campo = key.replace("root['", "").replace("']", "").replace("']['", ".")
        changes.append(FieldChange(campo=campo, valor_anterior=None, valor_nuevo=current.get(campo)))

    return changes


async def create_audit_entry(
    record: dict,
    previous: Optional[dict] = None,
    usuario: str = "system",
    ip_origen: Optional[str] = None,
    motivo: str = "",
    sensibilidad: SensibilidadEnum = SensibilidadEnum.PUBLIC,
    estado_aprobacion: AprobacionEnum = AprobacionEnum.PENDIENTE
) -> AuditEntry:
    """Create an immutable audit entry for a biological record change."""

    audit_col = get_audit_collection()

    id_registro = record.get("identificacion_basica", {}).get("id_registro", "unknown")

    # Get current version number
    last_version = await audit_col.find_one(
        {"id_registro": id_registro},
        sort=[("version", -1)]
    )
    version = (last_version["version"] + 1) if last_version else 1

    # Compute field changes
    campos_modificados = await compute_field_changes(record, previous)

    # Create audit entry
    audit_entry = AuditEntry(
        id_registro=id_registro,
        version=version,
        timestamp=datetime.utcnow(),
        usuario=usuario,
        ip_origen=ip_origen,
        campos_modificados=campos_modificados,
        motivo=motivo,
        snapshot_completo=record,
        sensibilidad=sensibilidad,
        estado_aprobacion=estado_aprobacion
    )

    # Insert into audit collection
    await audit_col.insert_one(audit_entry.dict())

    # Upsert into biological_records collection (latest snapshot)
    records_col = get_records_collection()
    await records_col.update_one(
        {"id_registro": id_registro},
        {
            "$set": {
                "id_registro": id_registro,
                "version": version,
                "timestamp": datetime.utcnow(),
                "data": record
            }
        },
        upsert=True
    )

    return audit_entry


async def get_historial(id_registro: str) -> List[AuditEntry]:
    """Get complete audit history for a biological record."""
    audit_col = get_audit_collection()

    entries = await audit_col.find(
        {"id_registro": id_registro}
    ).sort([("version", 1)]).to_list(None)

    return [AuditEntry(**entry) for entry in entries]


async def get_latest_snapshot(id_registro: str) -> Optional[dict]:
    """Get the most recent complete snapshot of a biological record."""
    records_col = get_records_collection()

    record = await records_col.find_one({"id_registro": id_registro})

    if record:
        return record.get("data")
    return None


async def get_metadatos(id_registro: str) -> Optional[dict]:
    """Get metadata (identificacion_basica + informacion_registro) from latest snapshot."""
    snapshot = await get_latest_snapshot(id_registro)

    if not snapshot:
        return None

    return {
        "identificacion_basica": snapshot.get("identificacion_basica", {}),
        "informacion_registro": snapshot.get("informacion_registro", {})
    }
