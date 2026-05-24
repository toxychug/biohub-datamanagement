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


# --- Response models for OpenAPI documentation ---

class HealthResponse(BaseModel):
    status: str
    service: str
    db: str
    cache: str
    kafka: str
    environment: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "service": "biohub-change-management",
                "db": "connected",
                "cache": "memory",
                "kafka": "mock",
                "environment": "development"
            }
        }


class RootResponse(BaseModel):
    service: str
    version: str
    docs: str

    class Config:
        json_schema_extra = {
            "example": {
                "service": "BioHub Change Management & Audit",
                "version": "0.1.0",
                "docs": "/docs"
            }
        }


class MetadatosResponse(BaseModel):
    identificacion_basica: dict
    informacion_registro: dict

    class Config:
        json_schema_extra = {
            "example": {
                "identificacion_basica": {
                    "id_registro": "REG-001",
                    "nombre_cientifico": "Panthera onca",
                    "nombre_comun": "Jaguar",
                    "taxonomia": {
                        "reino": "Animalia", "filo": "Chordata", "clase": "Mammalia",
                        "orden": "Carnivora", "familia": "Felidae",
                        "genero": "Panthera", "especie": "P. onca"
                    },
                    "estado_taxonomico": "Aceptado",
                    "autoridad_taxonomica": "Linnaeus, 1758",
                    "fecha_clasificacion": "2026-01-15"
                },
                "informacion_registro": {
                    "investigador": "researcher@institute.org",
                    "equipo_expedicion": "Equipo Amazonia Norte",
                    "institucion": "Universidad Nacional de Colombia",
                    "id_expedicion": "EXP-2026-001",
                    "fecha_registro": "2026-04-19",
                    "estado_registro": "ACTIVO"
                }
            }
        }


class SensibilidadResponse(BaseModel):
    id_registro: str
    sensibilidad: SensibilidadEnum

    class Config:
        json_schema_extra = {
            "example": {
                "id_registro": "REG-001",
                "sensibilidad": "RESTRICTED"
            }
        }


class AprobacionResponse(BaseModel):
    id_registro: str
    estado_aprobacion: AprobacionEnum

    class Config:
        json_schema_extra = {
            "example": {
                "id_registro": "REG-001",
                "estado_aprobacion": "PENDIENTE"
            }
        }


class AprobacionUpdateResponse(BaseModel):
    status: str
    id_registro: str
    version: int
    nuevo_estado: str
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "id_registro": "REG-001",
                "version": 2,
                "nuevo_estado": "APROBADO",
                "timestamp": "2026-04-19T10:30:00"
            }
        }


class SimulateResponse(BaseModel):
    status: str
    id_registro: str
    version: int
    timestamp: str

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "id_registro": "REG-001",
                "version": 1,
                "timestamp": "2026-04-19T10:30:00"
            }
        }


class RegistrosListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    registros: List[BiologicalRecordSnapshot]


class AuditListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    entradas: List[AuditEntry]
