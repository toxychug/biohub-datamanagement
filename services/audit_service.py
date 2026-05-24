from database.connection import get_audit_collection, get_records_collection
from database.models import AuditEntry, FieldChange, SensibilidadEnum, AprobacionEnum
from datetime import datetime
from typing import Optional, List, Any
from deepdiff import DeepDiff


async def compute_field_changes(current: dict, previous: Optional[dict]) -> List[FieldChange]:
    """Compute the differences between two record versions."""
    if previous is None or len(previous) == 0:
        return []

    try:
        diff = DeepDiff(previous, current, ignore_order=True)
    except Exception:
        return []

    changes = []

    try:
        for key, value in diff.get("values_changed", {}).items():
            campo = key.replace("root['", "").replace("']", "").replace("']['", ".")
            old_val = value.get("old_value")
            new_val = value.get("new_value")
            changes.append(FieldChange(campo=campo, valor_anterior=old_val, valor_nuevo=new_val))

        for key in diff.get("dictionary_item_added", []):
            campo = key.replace("root['", "").replace("']", "").replace("']['", ".")
            changes.append(FieldChange(campo=campo, valor_anterior=None, valor_nuevo=current.get(campo)))
    except Exception:
        pass

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

    try:
        audit_col = get_audit_collection()

        id_registro = record.get("identificacion_basica", {}).get("id_registro", "unknown")
        if not id_registro or id_registro == "unknown":
            raise ValueError("id_registro is required in identificacion_basica")

        # Get current version number
        last_version = await audit_col.find_one(
            {"id_registro": id_registro},
            sort=[("version", -1)]
        )
        version = (last_version["version"] + 1) if last_version is not None else 1

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
        audit_dict = {
            "id_registro": audit_entry.id_registro,
            "version": audit_entry.version,
            "timestamp": audit_entry.timestamp.isoformat(),
            "usuario": audit_entry.usuario,
            "ip_origen": audit_entry.ip_origen,
            "campos_modificados": [{"campo": c.campo, "valor_anterior": c.valor_anterior, "valor_nuevo": c.valor_nuevo} for c in audit_entry.campos_modificados],
            "motivo": audit_entry.motivo,
            "snapshot_completo": audit_entry.snapshot_completo,
            "sensibilidad": audit_entry.sensibilidad.value,
            "estado_aprobacion": audit_entry.estado_aprobacion.value
        }
        result = await audit_col.insert_one(audit_dict)
        print(f"[✓] Inserted audit entry: {result.inserted_id}")

        # Upsert into biological_records collection (latest snapshot)
        records_col = get_records_collection()
        await records_col.update_one(
            {"id_registro": id_registro},
            {
                "$set": {
                    "id_registro": id_registro,
                    "version": version,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": record
                }
            },
            upsert=True
        )
        print(f"[✓] Upserted biological record: {id_registro}")

        return audit_entry
    except Exception as e:
        print(f"[ERROR] create_audit_entry failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


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


async def get_all_records(limit: int = 20, offset: int = 0):
    """Get all biological records (latest snapshot per record) with pagination."""
    records_col = get_records_collection()

    total = await records_col.count_documents({})
    cursor = records_col.find({}).sort("timestamp", -1).skip(offset).limit(limit)
    docs = await cursor.to_list(None)

    from database.models import BiologicalRecordSnapshot
    registros = [BiologicalRecordSnapshot(**{k: v for k, v in doc.items() if k != "_id"}) for doc in docs]

    return total, registros


async def get_all_audit_entries(limit: int = 20, offset: int = 0) -> tuple[int, List[AuditEntry]]:
    """Get all audit entries across all records with pagination."""
    audit_col = get_audit_collection()

    total = await audit_col.count_documents({})
    cursor = audit_col.find({}).sort("timestamp", -1).skip(offset).limit(limit)
    docs = await cursor.to_list(None)

    entries = [AuditEntry(**{k: v for k, v in doc.items() if k != "_id"}) for doc in docs]
    return total, entries


async def get_metadatos(id_registro: str) -> Optional[dict]:
    """Get metadata (identificacion_basica + informacion_registro) from latest snapshot."""
    snapshot = await get_latest_snapshot(id_registro)

    if not snapshot:
        return None

    return {
        "identificacion_basica": snapshot.get("identificacion_basica", {}),
        "informacion_registro": snapshot.get("informacion_registro", {})
    }
