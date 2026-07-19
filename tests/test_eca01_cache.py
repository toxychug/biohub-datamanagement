"""
Tests for ECA-01 — Rendimiento bajo consulta masiva (caché).
Verifica que:
  1. cache_get devuelve el resultado sin ir a MongoDB (cache HIT).
  2. cache_get devuelve None y se consulta MongoDB (cache MISS).
  3. cache_set se llama con los datos correctos tras el MISS.
  4. cache_delete invalida AMBAS claves al insertar una entrada.
  5. Peticiones filtradas NO se cachean.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.audit_service import create_audit_entry, get_historial
from database.models import SensibilidadEnum, AprobacionEnum

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SAMPLE_RECORD = {
    "identificacion_basica": {
        "id_registro": "REG-ECA01",
        "nombre_cientifico": "Panthera onca",
        "nombre_comun": "Jaguar",
    },
    "informacion_registro": {
        "investigador": "researcher@biohub.org",
        "institucion": "Universidad Nacional",
        "fecha_registro": "2026-01-15",
    },
    "geolocalizacion": {
        "latitud": 5.52,
        "longitud": -74.1,
        "nivel_sensibilidad": "PUBLIC",
    },
}

AUDIT_DOC = {
    "id_registro": "REG-ECA01",
    "version": 1,
    "timestamp": "2026-05-01T10:00:00",
    "usuario": "researcher@biohub.org",
    "ip_origen": None,
    "campos_modificados": [],
    "motivo": "Registro inicial",
    "snapshot_completo": SAMPLE_RECORD,
    "sensibilidad": "PUBLIC",
    "estado_aprobacion": "PENDIENTE",
}


class _Cursor:
    def __init__(self, docs):
        self._docs = docs

    def sort(self, *a, **kw):
        return self

    def skip(self, n):
        return self

    def limit(self, n):
        return self

    async def to_list(self, length):
        return self._docs


def _audit_col(find_one_return=None, docs=None):
    col = MagicMock()
    col.find_one = AsyncMock(return_value=find_one_return)
    col.insert_one = AsyncMock(return_value=MagicMock(inserted_id="mock_id"))
    col.count_documents = AsyncMock(return_value=len(docs) if docs else 0)
    col.find = MagicMock(return_value=_Cursor(docs or []))
    return col


def _records_col():
    col = MagicMock()
    col.find_one = AsyncMock(return_value=None)
    col.update_one = AsyncMock(return_value=MagicMock())
    col.count_documents = AsyncMock(return_value=0)
    col.find = MagicMock(return_value=_Cursor([]))
    return col


# ---------------------------------------------------------------------------
# ECA-01 · Criterio 1: cache HIT evita consulta a MongoDB
# ---------------------------------------------------------------------------

class TestCacheHit:
    @patch("routers.auditoria.cache_get", new_callable=AsyncMock)
    @patch("routers.auditoria.cache_set", new_callable=AsyncMock)
    @patch("routers.auditoria.get_historial", new_callable=AsyncMock)
    async def test_cache_hit_skips_db_call(self, mock_get_historial, mock_cache_set, mock_cache_get):
        """Si cache_get devuelve datos, get_historial (MongoDB) NO debe invocarse."""
        mock_cache_get.return_value = [AUDIT_DOC]

        from routers.auditoria import get_historial_endpoint
        # Pasar None explícito — los Query() defaults no se resuelven fuera de FastAPI
        result = await get_historial_endpoint(
            id_registro="REG-ECA01",
            fecha_desde=None,
            fecha_hasta=None,
            tipo_cambio=None,
        )

        mock_get_historial.assert_not_called()
        mock_cache_set.assert_not_called()
        assert result == [AUDIT_DOC]

    @patch("routers.auditoria.cache_get", new_callable=AsyncMock)
    @patch("routers.auditoria.cache_set", new_callable=AsyncMock)
    @patch("routers.auditoria.get_historial", new_callable=AsyncMock)
    async def test_cache_miss_calls_db(self, mock_get_historial, mock_cache_set, mock_cache_get):
        """Si cache_get devuelve None, debe consultar MongoDB y guardar en caché."""
        from database.models import AuditEntry
        fake_entry = AuditEntry(**AUDIT_DOC)
        mock_cache_get.return_value = None
        mock_get_historial.return_value = [fake_entry]

        from routers.auditoria import get_historial_endpoint
        result = await get_historial_endpoint(
            id_registro="REG-ECA01",
            fecha_desde=None,
            fecha_hasta=None,
            tipo_cambio=None,
        )

        mock_get_historial.assert_called_once_with(
            "REG-ECA01",
            fecha_desde=None,
            fecha_hasta=None,
            tipo_cambio=None,
        )
        mock_cache_set.assert_called_once()
        assert len(result) == 1

    @patch("routers.auditoria.cache_get", new_callable=AsyncMock)
    @patch("routers.auditoria.cache_set", new_callable=AsyncMock)
    @patch("routers.auditoria.get_historial", new_callable=AsyncMock)
    async def test_filtered_request_bypasses_cache(self, mock_get_historial, mock_cache_set, mock_cache_get):
        """Peticiones con filtros NO deben leer ni escribir en caché."""
        from database.models import AuditEntry
        fake_entry = AuditEntry(**AUDIT_DOC)
        mock_get_historial.return_value = [fake_entry]

        from datetime import datetime
        from routers.auditoria import get_historial_endpoint
        await get_historial_endpoint(
            id_registro="REG-ECA01",
            fecha_desde=datetime(2026, 1, 1),
            fecha_hasta=None,
            tipo_cambio=None,
        )

        mock_cache_get.assert_not_called()
        mock_cache_set.assert_not_called()


# ---------------------------------------------------------------------------
# ECA-01 · Criterio 4: invalidación de caché al insertar
# ---------------------------------------------------------------------------

class TestCacheInvalidationOnInsert:
    @patch("services.audit_service.cache_delete", new_callable=AsyncMock)
    @patch("services.audit_service.get_records_collection")
    @patch("services.audit_service.get_audit_collection")
    async def test_both_cache_keys_deleted_on_insert(self, mock_audit_fn, mock_records_fn, mock_cache_del):
        """create_audit_entry debe invalidar historial:{id} y auditoria:{id}."""
        mock_audit_fn.return_value = _audit_col()
        mock_records_fn.return_value = _records_col()

        await create_audit_entry(record=SAMPLE_RECORD)

        deleted_keys = [call.args[0] for call in mock_cache_del.call_args_list]
        assert "historial:REG-ECA01" in deleted_keys
        assert "auditoria:REG-ECA01" in deleted_keys

    @patch("services.audit_service.cache_delete", new_callable=AsyncMock)
    @patch("services.audit_service.get_records_collection")
    @patch("services.audit_service.get_audit_collection")
    async def test_cache_delete_called_exactly_twice(self, mock_audit_fn, mock_records_fn, mock_cache_del):
        """Se deben invalidar exactamente 2 claves de caché por inserción."""
        mock_audit_fn.return_value = _audit_col()
        mock_records_fn.return_value = _records_col()

        await create_audit_entry(record=SAMPLE_RECORD)

        assert mock_cache_del.call_count == 2

    @patch("services.audit_service.cache_delete", new_callable=AsyncMock)
    @patch("services.audit_service.get_records_collection")
    @patch("services.audit_service.get_audit_collection")
    async def test_cache_invalidated_with_correct_id(self, mock_audit_fn, mock_records_fn, mock_cache_del):
        """Las claves invalidadas deben contener el id_registro correcto."""
        mock_audit_fn.return_value = _audit_col()
        mock_records_fn.return_value = _records_col()

        await create_audit_entry(record=SAMPLE_RECORD)

        for call in mock_cache_del.call_args_list:
            key = call.args[0]
            assert "REG-ECA01" in key, f"Clave inesperada: {key}"
