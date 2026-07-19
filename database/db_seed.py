"""
Database seeder: Auto-loads sample data when starting in development mode
with in-memory database (when MongoDB is unavailable).
"""

from datetime import datetime
from database.in_memory_db import get_in_memory_db
from database.models import AuditEntry, SensibilidadEnum, AprobacionEnum, BiologicalRecordSnapshot
from config import settings


async def seed_sample_data():
    """Load sample seed data into the in-memory database."""
    
    if not settings.env == "development":
        return
    
    db = get_in_memory_db()
    
    # Sample records to seed
    sample_records = [
        {
            "id_registro": "REG-001",
            "nombre_cientifico": "Panthera onca",
            "nombre_comun": "Jaguar",
            "investigador": "m.garcia@unal.edu.co",
            "institucion": "Universidad Nacional de Colombia",
            "sensibilidad": "RESTRICTED"
        },
        {
            "id_registro": "REG-002",
            "nombre_cientifico": "Vultur gryphus",
            "nombre_comun": "Cóndor andino",
            "investigador": "j.martinez@unal.edu.co",
            "institucion": "Universidad Nacional de Colombia",
            "sensibilidad": "RESTRICTED"
        },
        {
            "id_registro": "REG-003",
            "nombre_cientifico": "Ara chloropterus",
            "nombre_comun": "Guacamaya verde",
            "investigador": "c.lopez@unal.edu.co",
            "institucion": "Universidad Nacional de Colombia",
            "sensibilidad": "PUBLIC"
        },
        {
            "id_registro": "REG-004",
            "nombre_cientifico": "Ateles fusciceps",
            "nombre_comun": "Mono araña",
            "investigador": "a.torres@unal.edu.co",
            "institucion": "Universidad Nacional de Colombia",
            "sensibilidad": "CONFIDENTIAL"
        },
        {
            "id_registro": "REG-005",
            "nombre_cientifico": "Boa constrictor",
            "nombre_comun": "Anaconda",
            "investigador": "m.garcia@unal.edu.co",
            "institucion": "Universidad Nacional de Colombia",
            "sensibilidad": "PUBLIC"
        }
    ]
    
    for record_data in sample_records:
        # Create audit entry
        audit_entry = AuditEntry(
            id_registro=record_data["id_registro"],
            version=1,
            timestamp=datetime.utcnow(),
            usuario=record_data["investigador"],
            motivo="Registro inicial de prueba",
            snapshot_completo={
                "identificacion_basica": {
                    "id_registro": record_data["id_registro"],
                    "nombre_cientifico": record_data["nombre_cientifico"],
                    "nombre_comun": record_data["nombre_comun"]
                },
                "informacion_registro": {
                    "investigador": record_data["investigador"],
                    "institucion": record_data["institucion"]
                },
                "geolocalizacion": {
                    "latitud": 5.5 + (float(record_data["id_registro"].split("-")[1]) * 0.1),
                    "longitud": -74.0 + (float(record_data["id_registro"].split("-")[1]) * 0.1),
                    "nivel_sensibilidad": record_data["sensibilidad"]
                }
            },
            sensibilidad=SensibilidadEnum[record_data["sensibilidad"]],
            estado_aprobacion=AprobacionEnum.PENDIENTE
        )
        
        # Insert audit entry
        await db.insert_audit_entry(audit_entry)
        
        # Create snapshot
        snapshot = BiologicalRecordSnapshot(
            id_registro=record_data["id_registro"],
            version=1,
            timestamp=datetime.utcnow(),
            data=audit_entry.snapshot_completo
        )
        
        # Insert snapshot
        await db.insert_or_update_record(snapshot)
    
    print(f"[✓] Seeded {len(sample_records)} sample records to in-memory database")
