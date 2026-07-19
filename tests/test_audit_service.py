"""
Tests for services/audit_service.py — targets RNF-06 (≥70% coverage on AuditoriaService).
All DB and cache calls are mocked; no real MongoDB or Redis connection required.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.audit_service import (
    compute_field_changes,
    create_audit_entry,
    get_historial,
    get_latest_snapshot,
    get_all_records,
    get_all_audit_entries,
    get_metadatos,
)
from database.models import SensibilidadEnum, AprobacionEnum


# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

SAMPLE_RECORD = {
    "identificacion_basica": {
        "id_registro": "REG-001",
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
    "id_registro": "REG-001",
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


# ---------------------------------------------------------------------------
# Async cursor stub — mimics Motor's chainable cursor API
# ---------------------------------------------------------------------------

class _Cursor:
    def __init__(self, docs: list):
        self._docs = docs

    def sort(self, *args, **kwargs):
        return self

    def skip(self, n: int):
        return self

    def limit(self, n: int):
        return self

    async def to_list(self, length):
        return self._docs


# ---------------------------------------------------------------------------
# Collection factory helpers
# ---------------------------------------------------------------------------

def _audit_col(find_one_return=None, docs=None):
    col = MagicMock()
    col.find_one = AsyncMock(return_value=find_one_return)
    col.insert_one = AsyncMock(return_value=MagicMock(inserted_id="mock_id_123"))
    col.count_documents = AsyncMock(return_value=len(docs) if docs else 0)
    col.find = MagicMock(return_value=_Cursor(docs or []))
    return col


def _records_col(find_one_return=None, docs=None):
    col = MagicMock()
    col.find_one = AsyncMock(return_value=find_one_return)
    col.update_one = AsyncMock(return_value=MagicMock())
    col.count_documents = AsyncMock(return_value=len(docs) if docs else 0)
    col.find = MagicMock(return_value=_Cursor(docs or []))
    return col


# ---------------------------------------------------------------------------
# compute_field_changes
# ---------------------------------------------------------------------------

class TestComputeFieldChanges:
    async def test_returns_empty_when_previous_is_none(self):
        result = await compute_field_changes(SAMPLE_RECORD, None)
        assert result == []

    async def test_returns_empty_when_previous_is_empty_dict(self):
        result = await compute_field_changes(SAMPLE_RECORD, {})
        assert result == []

    async def test_returns_empty_for_identical_records(self):
        data = {"campo": "valor", "numero": 42}
        result = await compute_field_changes(data, data.copy())
        assert result == []

    async def test_detects_changed_value(self):
        old = {"especie": "Tigre", "peso": 100}
        new = {"especie": "Jaguar", "peso": 100}
        changes = await compute_field_changes(new, old)
        assert len(changes) == 1
        assert changes[0].campo == "especie"
        assert changes[0].valor_anterior == "Tigre"
        assert changes[0].valor_nuevo == "Jaguar"

    async def test_detects_multiple_changed_values(self):
        old = {"especie": "Tigre", "peso": 100}
        new = {"especie": "Jaguar", "peso": 120}
        changes = await compute_field_changes(new, old)
        assert len(changes) == 2

    async def test_detects_added_field(self):
        old = {"especie": "Jaguar"}
        new = {"especie": "Jaguar", "habitat": "selva tropical"}
        changes = await compute_field_changes(new, old)
        campos = [c.campo for c in changes]
        assert "habitat" in campos

    async def test_added_field_has_none_as_previous(self):
        old = {"especie": "Jaguar"}
        new = {"especie": "Jaguar", "nuevo_campo": "valor"}
        changes = await compute_field_changes(new, old)
        added = next(c for c in changes if c.campo == "nuevo_campo")
        assert added.valor_anterior is None


# ---------------------------------------------------------------------------
# create_audit_entry
# ---------------------------------------------------------------------------

class TestCreateAuditEntry:
    @patch("services.audit_service.cache_delete", new_callable=AsyncMock)
    @patch("services.audit_service.get_records_collection")
    @patch("services.audit_service.get_audit_collection")
    async def test_first_entry_gets_version_1(self, mock_audit_fn, mock_records_fn, mock_cache_del):
        mock_audit_fn.return_value = _audit_col(find_one_return=None)
        mock_records_fn.return_value = _records_col()

        entry = await create_audit_entry(record=SAMPLE_RECORD, usuario="test@biohub.org")

        assert entry.version == 1
        assert entry.id_registro == "REG-001"

    @patch("services.audit_service.cache_delete", new_callable=AsyncMock)
    @patch("services.audit_service.get_records_collection")
    @patch("services.audit_service.get_audit_collection")
    async def test_increments_version_from_last(self, mock_audit_fn, mock_records_fn, mock_cache_del):
        mock_audit_fn.return_value = _audit_col(find_one_return={"version": 5})
        mock_records_fn.return_value = _records_col()

        entry = await create_audit_entry(record=SAMPLE_RECORD)

        assert entry.version == 6

    @patch("services.audit_service.cache_delete", new_callable=AsyncMock)
    @patch("services.audit_service.get_records_collection")
    @patch("services.audit_service.get_audit_collection")
    async def test_raises_when_id_registro_missing(self, mock_audit_fn, mock_records_fn, mock_cache_del):
        mock_audit_fn.return_value = _audit_col()
        mock_records_fn.return_value = _records_col()

        with pytest.raises(ValueError, match="id_registro is required"):
            await create_audit_entry(record={"identificacion_basica": {}})

    @patch("services.audit_service.cache_delete", new_callable=AsyncMock)
    @patch("services.audit_service.get_records_collection")
    @patch("services.audit_service.get_audit_collection")
    async def test_raises_when_identificacion_basica_absent(self, mock_audit_fn, mock_records_fn, mock_cache_del):
        mock_audit_fn.return_value = _audit_col()
        mock_records_fn.return_value = _records_col()

        with pytest.raises(ValueError):
            await create_audit_entry(record={})

    @patch("services.audit_service.cache_delete", new_callable=AsyncMock)
    @patch("services.audit_service.get_records_collection")
    @patch("services.audit_service.get_audit_collection")
    async def test_cache_invalidated_after_insert(self, mock_audit_fn, mock_records_fn, mock_cache_del):
        mock_audit_fn.return_value = _audit_col()
        mock_records_fn.return_value = _records_col()

        await create_audit_entry(record=SAMPLE_RECORD)

        calls = [str(c) for c in mock_cache_del.call_args_list]
        assert any("historial:REG-001" in c for c in calls)
        assert any("auditoria:REG-001" in c for c in calls)

    @patch("services.audit_service.cache_delete", new_callable=AsyncMock)
    @patch("services.audit_service.get_records_collection")
    @patch("services.audit_service.get_audit_collection")
    async def test_stores_usuario_and_motivo(self, mock_audit_fn, mock_records_fn, mock_cache_del):
        mock_audit_fn.return_value = _audit_col()
        mock_records_fn.return_value = _records_col()

        entry = await create_audit_entry(
            record=SAMPLE_RECORD,
            usuario="director@biohub.org",
            motivo="Corrección taxonómica",
        )

        assert entry.usuario == "director@biohub.org"
        assert entry.motivo == "Corrección taxonómica"

    @patch("services.audit_service.cache_delete", new_callable=AsyncMock)
    @patch("services.audit_service.get_records_collection")
    @patch("services.audit_service.get_audit_collection")
    async def test_stores_ip_origen(self, mock_audit_fn, mock_records_fn, mock_cache_del):
        mock_audit_fn.return_value = _audit_col()
        mock_records_fn.return_value = _records_col()

        entry = await create_audit_entry(record=SAMPLE_RECORD, ip_origen="10.0.0.5")

        assert entry.ip_origen == "10.0.0.5"

    @patch("services.audit_service.cache_delete", new_callable=AsyncMock)
    @patch("services.audit_service.get_records_collection")
    @patch("services.audit_service.get_audit_collection")
    async def test_stores_sensibilidad_and_estado(self, mock_audit_fn, mock_records_fn, mock_cache_del):
        mock_audit_fn.return_value = _audit_col()
        mock_records_fn.return_value = _records_col()

        entry = await create_audit_entry(
            record=SAMPLE_RECORD,
            sensibilidad=SensibilidadEnum.CONFIDENTIAL,
            estado_aprobacion=AprobacionEnum.APROBADO,
        )

        assert entry.sensibilidad == SensibilidadEnum.CONFIDENTIAL
        assert entry.estado_aprobacion == AprobacionEnum.APROBADO

    @patch("services.audit_service.cache_delete", new_callable=AsyncMock)
    @patch("services.audit_service.get_records_collection")
    @patch("services.audit_service.get_audit_collection")
    async def test_upserts_records_collection(self, mock_audit_fn, mock_records_fn, mock_cache_del):
        records_col = _records_col()
        mock_audit_fn.return_value = _audit_col()
        mock_records_fn.return_value = records_col

        await create_audit_entry(record=SAMPLE_RECORD)

        records_col.update_one.assert_called_once()
        filter_arg = records_col.update_one.call_args[0][0]
        assert filter_arg == {"id_registro": "REG-001"}

    @patch("services.audit_service.cache_delete", new_callable=AsyncMock)
    @patch("services.audit_service.get_records_collection")
    @patch("services.audit_service.get_audit_collection")
    async def test_computes_field_changes_against_previous(self, mock_audit_fn, mock_records_fn, mock_cache_del):
        mock_audit_fn.return_value = _audit_col()
        mock_records_fn.return_value = _records_col()

        previous = {**SAMPLE_RECORD, "nombre_cientifico": "Felis concolor"}
        entry = await create_audit_entry(record=SAMPLE_RECORD, previous=previous)

        assert isinstance(entry.campos_modificados, list)


# ---------------------------------------------------------------------------
# get_historial
# ---------------------------------------------------------------------------

class TestGetHistorial:
    @patch("services.audit_service.get_audit_collection")
    async def test_returns_list_of_audit_entries(self, mock_col_fn):
        mock_col_fn.return_value = _audit_col(docs=[AUDIT_DOC])

        result = await get_historial("REG-001")

        assert len(result) == 1
        assert result[0].id_registro == "REG-001"
        assert result[0].version == 1

    @patch("services.audit_service.get_audit_collection")
    async def test_returns_empty_list_when_no_history(self, mock_col_fn):
        mock_col_fn.return_value = _audit_col(docs=[])

        result = await get_historial("REG-999")

        assert result == []

    @patch("services.audit_service.get_audit_collection")
    async def test_returns_multiple_entries(self, mock_col_fn):
        doc_v2 = {**AUDIT_DOC, "version": 2}
        mock_col_fn.return_value = _audit_col(docs=[AUDIT_DOC, doc_v2])

        result = await get_historial("REG-001")

        assert len(result) == 2


# ---------------------------------------------------------------------------
# get_latest_snapshot
# ---------------------------------------------------------------------------

class TestGetLatestSnapshot:
    @patch("services.audit_service.get_records_collection")
    async def test_returns_data_dict(self, mock_col_fn):
        mock_col_fn.return_value = _records_col(
            find_one_return={"id_registro": "REG-001", "data": SAMPLE_RECORD}
        )

        result = await get_latest_snapshot("REG-001")

        assert result == SAMPLE_RECORD

    @patch("services.audit_service.get_records_collection")
    async def test_returns_none_when_record_not_found(self, mock_col_fn):
        mock_col_fn.return_value = _records_col(find_one_return=None)

        result = await get_latest_snapshot("REG-999")

        assert result is None

    @patch("services.audit_service.get_records_collection")
    async def test_returns_none_when_data_key_absent(self, mock_col_fn):
        mock_col_fn.return_value = _records_col(
            find_one_return={"id_registro": "REG-001"}
        )

        result = await get_latest_snapshot("REG-001")

        assert result is None


# ---------------------------------------------------------------------------
# get_all_records
# ---------------------------------------------------------------------------

class TestGetAllRecords:
    @patch("services.audit_service.get_records_collection")
    async def test_returns_total_and_snapshots(self, mock_col_fn):
        doc = {
            "id_registro": "REG-001",
            "version": 1,
            "timestamp": "2026-05-01T10:00:00",
            "data": SAMPLE_RECORD,
        }
        mock_col_fn.return_value = _records_col(docs=[doc])

        total, registros = await get_all_records(limit=10, offset=0)

        assert total == 1
        assert len(registros) == 1
        assert registros[0].id_registro == "REG-001"

    @patch("services.audit_service.get_records_collection")
    async def test_returns_empty_when_no_records(self, mock_col_fn):
        mock_col_fn.return_value = _records_col(docs=[])

        total, registros = await get_all_records()

        assert total == 0
        assert registros == []


# ---------------------------------------------------------------------------
# get_all_audit_entries
# ---------------------------------------------------------------------------

class TestGetAllAuditEntries:
    @patch("services.audit_service.get_audit_collection")
    async def test_returns_total_and_entries(self, mock_col_fn):
        mock_col_fn.return_value = _audit_col(docs=[AUDIT_DOC])

        total, entries = await get_all_audit_entries(limit=10, offset=0)

        assert total == 1
        assert len(entries) == 1
        assert entries[0].id_registro == "REG-001"

    @patch("services.audit_service.get_audit_collection")
    async def test_returns_empty_when_no_entries(self, mock_col_fn):
        mock_col_fn.return_value = _audit_col(docs=[])

        total, entries = await get_all_audit_entries()

        assert total == 0
        assert entries == []


# ---------------------------------------------------------------------------
# get_metadatos
# ---------------------------------------------------------------------------

class TestGetMetadatos:
    @patch("services.audit_service.get_records_collection")
    async def test_returns_both_sections(self, mock_col_fn):
        mock_col_fn.return_value = _records_col(
            find_one_return={"id_registro": "REG-001", "data": SAMPLE_RECORD}
        )

        result = await get_metadatos("REG-001")

        assert "identificacion_basica" in result
        assert "informacion_registro" in result

    @patch("services.audit_service.get_records_collection")
    async def test_identificacion_contains_id(self, mock_col_fn):
        mock_col_fn.return_value = _records_col(
            find_one_return={"id_registro": "REG-001", "data": SAMPLE_RECORD}
        )

        result = await get_metadatos("REG-001")

        assert result["identificacion_basica"]["id_registro"] == "REG-001"

    @patch("services.audit_service.get_records_collection")
    async def test_returns_none_when_no_snapshot(self, mock_col_fn):
        mock_col_fn.return_value = _records_col(find_one_return=None)

        result = await get_metadatos("REG-999")

        assert result is None

    @patch("services.audit_service.get_records_collection")
    async def test_returns_empty_dicts_when_keys_absent(self, mock_col_fn):
        record_without_sections = {"identificacion_basica": {"id_registro": "REG-001"}}
        mock_col_fn.return_value = _records_col(
            find_one_return={"id_registro": "REG-001", "data": record_without_sections}
        )

        result = await get_metadatos("REG-001")

        assert result["informacion_registro"] == {}
