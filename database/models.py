from pydantic import BaseModel, Field
from typing import Any, List, Optional
from datetime import datetime
from enum import Enum


class SensibilidadEnum(str, Enum):
    PUBLIC = "PUBLIC"
    RESTRICTED = "RESTRICTED"
    CONFIDENTIAL = "CONFIDENTIAL"


class AprobacionEnum(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_REVISION = "EN_REVISION"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


class FieldChange(BaseModel):
    campo: str
    valor_anterior: Any = None
    valor_nuevo: Any = None


class AuditEntry(BaseModel):
    id_registro: str
    version: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    usuario: str
    ip_origen: Optional[str] = None
    campos_modificados: List[FieldChange] = []
    motivo: str = ""
    snapshot_completo: dict
    sensibilidad: SensibilidadEnum = SensibilidadEnum.PUBLIC
    estado_aprobacion: AprobacionEnum = AprobacionEnum.PENDIENTE

    class Config:
        json_schema_extra = {
            "example": {
                "id_registro": "REG-001",
                "version": 1,
                "timestamp": "2026-04-19T10:30:00Z",
                "usuario": "researcher@institute.org",
                "ip_origen": "192.168.1.100",
                "campos_modificados": [
                    {
                        "campo": "geolocalizacion.latitud",
                        "valor_anterior": None,
                        "valor_nuevo": 5.52
                    }
                ],
                "motivo": "Registro inicial de hallazgo",
                "snapshot_completo": {},
                "sensibilidad": "RESTRICTED",
                "estado_aprobacion": "PENDIENTE"
            }
        }


class ApprovalAction(BaseModel):
    id_registro: str
    nuevo_estado: AprobacionEnum
    director_aprobador: str
    comentarios: Optional[str] = None


class BiologicalRecordSnapshot(BaseModel):
    id_registro: str
    version: int
    timestamp: datetime
    data: dict
