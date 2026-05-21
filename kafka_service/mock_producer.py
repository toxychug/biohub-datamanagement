from fastapi import APIRouter, HTTPException, Body
from config import settings
from services.audit_service import create_audit_entry
from services.sensitivity_service import classify_sensitivity
from database.models import AprobacionEnum, SimulateResponse

router = APIRouter(prefix="/dev", tags=["development"])

_SIMULATE_EXAMPLE = {
    "identificacion_basica": {
        "id_registro": "REG-001",
        "nombre_cientifico": "Panthera onca",
        "nombre_comun": "Jaguar",
        "taxonomia": {
            "reino": "Animalia", "filo": "Chordata", "clase": "Mammalia",
            "orden": "Carnivora", "familia": "Felidae", "genero": "Panthera", "especie": "P. onca"
        },
        "estado_taxonomico": "Aceptado",
        "autoridad_taxonomica": "Linnaeus, 1758",
        "fecha_clasificacion": "2026-01-15"
    },
    "datos_hallazgo": {
        "fecha": "2026-04-19", "hora": "08:30:00", "tipo_registro": "Avistamiento",
        "metodo_observacion": "Fotográfico", "cantidad_individuos": 1, "comportamiento": "Caza"
    },
    "geolocalizacion": {
        "latitud": 1.2345, "longitud": -76.5432, "altitud": 320.0,
        "region": "Amazonas", "ecosistema": "Selva húmeda tropical",
        "precision": "Alta", "nivel_sensibilidad": "RESTRICTED"
    },
    "datos_ambientales": {
        "temperatura": 28.5, "humedad": 85.0, "ph_suelo": 6.2,
        "tipo_suelo": "Latosol", "clima": "Tropical húmedo",
        "precipitacion": 3200.0, "cobertura_vegetal": "Densa", "condiciones_entorno": "Óptimas"
    },
    "caracteristicas_fisicas": {
        "tamano": "Grande", "peso": "80kg", "coloracion": "Amarillo con manchas negras",
        "edad_aproximada": "Adulto", "sexo": "Macho", "estado_salud": "Saludable",
        "caracteristicas_distintivas": "Roseta característica en flanco derecho"
    },
    "evidencia": {
        "fotografias": ["foto_001.jpg"], "videos": [], "audios": [], "archivos_adjuntos": [],
        "metadatos": {"fecha_captura": "2026-04-19T08:30:00", "gps": "1.2345,-76.5432", "dispositivo": "Nikon D850"}
    },
    "estado_conservacion": {
        "categoria_amenaza": "NT", "nivel_riesgo": "Moderado",
        "listas_oficiales": ["IUCN"], "observaciones": "Población estable en la región"
    },
    "informacion_registro": {
        "investigador": "researcher@institute.org",
        "equipo_expedicion": "Equipo Amazonia Norte",
        "institucion": "Universidad Nacional de Colombia",
        "id_expedicion": "EXP-2026-001",
        "fecha_registro": "2026-04-19",
        "estado_registro": "ACTIVO"
    },
    "validacion_cientifica": {
        "director_aprobador": "", "estado_validacion": "PENDIENTE",
        "comentarios": "", "fecha_validacion": ""
    },
    "trazabilidad": {
        "version": 1,
        "historial_cambios": [
            {"usuario": "researcher@institute.org", "fecha": "2026-04-19",
             "cambio": "Registro inicial", "motivo": "Primera observación documentada"}
        ]
    },
    "datos_analiticos": {
        "incluido_mapa_calor": True, "frecuencia_avistamiento": 1,
        "tendencias": "Estable", "indicadores_ecologicos": ["Depredador apex"]
    },
    "datos_consumo_externo": {
        "anonimizado": False, "visible_publico": False,
        "version_api": "1.0", "restricciones_acceso": "Solo investigadores autorizados"
    }
}


@router.post(
    "/simulate",
    response_model=SimulateResponse,
    summary="Simular evento Kafka del Grupo 1 (solo desarrollo)",
    responses={
        403: {"description": "Solo disponible en modo desarrollo"},
        400: {"description": "Formato de registro biológico inválido"},
    },
)
async def simulate_kafka_event(
    record: dict = Body(..., description="Registro biológico en formato Grupo 1", example=_SIMULATE_EXAMPLE)
) -> SimulateResponse:
    """Inyecta un registro biológico directamente en el pipeline de auditoría sin pasar por Kafka. Solo disponible con ENV=development."""

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
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Error in mock producer:\n{error_msg}")
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
