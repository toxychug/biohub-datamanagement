from database.models import SensibilidadEnum


def classify_sensitivity(record: dict) -> SensibilidadEnum:
    """Classify record sensitivity based on geolocalizacion.nivel_sensibilidad."""

    # Check geolocalizacion.nivel_sensibilidad first
    geolocalizacion = record.get("geolocalizacion", {})
    nivel = geolocalizacion.get("nivel_sensibilidad", "").upper()

    if nivel in ["RESTRICTED", "CONFIDENTIAL"]:
        return SensibilidadEnum(nivel)

    # Fallback to datos_consumo_externo.restricciones_acceso
    datos_consumo = record.get("datos_consumo_externo", {})
    restricciones = datos_consumo.get("restricciones_acceso", "").upper()

    if restricciones in ["RESTRICTED", "CONFIDENTIAL"]:
        return SensibilidadEnum(restricciones)

    # Default to PUBLIC
    return SensibilidadEnum.PUBLIC
