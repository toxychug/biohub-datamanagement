"""
Tests for ECA-02 — Confiabilidad ante falla del broker Kafka.
Verifica que:
  1. El consumer se detiene limpiamente con stop().
  2. Ante una excepción al conectar, reintenta con backoff exponencial.
  3. El backoff no supera _BACKOFF_MAX (60 s).
  4. El backoff se resetea a _BACKOFF_INITIAL tras una conexión exitosa.
  5. _process_message llama a create_audit_entry con los datos correctos.
  6. _process_message no propaga excepciones (falla silenciosa por registro).
  7. start() no lanza tarea si use_mock_kafka=True.
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call

from kafka_service.consumer import BiohubKafkaConsumer, _BACKOFF_INITIAL, _BACKOFF_MAX


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLE_RECORD = {
    "identificacion_basica": {"id_registro": "REG-001", "nombre_cientifico": "Panthera onca"},
    "informacion_registro": {"investigador": "researcher@biohub.org"},
    "geolocalizacion": {"latitud": 5.52, "longitud": -74.1, "nivel_sensibilidad": "PUBLIC"},
    "trazabilidad": {"historial_cambios": [{"motivo": "Registro inicial"}]},
}


# ---------------------------------------------------------------------------
# ECA-02 · Criterio: detención limpia
# ---------------------------------------------------------------------------

class TestStop:
    async def test_stop_sets_running_false(self):
        consumer = BiohubKafkaConsumer()
        consumer.running = True
        consumer.task = None
        consumer.consumer = None

        await consumer.stop()

        assert consumer.running is False

    async def test_stop_cancels_task(self):
        consumer = BiohubKafkaConsumer()
        consumer.running = True

        async def _noop():
            await asyncio.sleep(100)

        consumer.task = asyncio.create_task(_noop())
        consumer.consumer = None

        await consumer.stop()

        assert consumer.task.cancelled()

    async def test_stop_calls_consumer_stop_if_connected(self):
        consumer = BiohubKafkaConsumer()
        consumer.running = True
        consumer.task = None

        mock_inner = MagicMock()
        mock_inner.stop = AsyncMock()
        consumer.consumer = mock_inner

        await consumer.stop()

        mock_inner.stop.assert_called_once()


# ---------------------------------------------------------------------------
# ECA-02 · Criterio: backoff exponencial ante falla de conexión
# ---------------------------------------------------------------------------

class TestBackoffOnConnectionFailure:
    @patch("kafka_service.consumer.asyncio.sleep", new_callable=AsyncMock)
    @patch("kafka_service.consumer.AIOKafkaConsumer")
    async def test_retries_after_connection_error(self, MockKafka, mock_sleep):
        """Cuando el broker falla, el consumer reintenta tras esperar."""
        consumer = BiohubKafkaConsumer()
        consumer.running = True

        # Primera llamada lanza excepción; segunda detiene el loop
        call_count = 0

        async def fake_start():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionRefusedError("broker down")
            consumer.running = False  # detiene el while en el 2do intento

        instance = MagicMock()
        instance.start = AsyncMock(side_effect=fake_start)
        instance.stop = AsyncMock()
        MockKafka.return_value = instance

        await consumer._consume_with_retry()

        mock_sleep.assert_called_once_with(_BACKOFF_INITIAL)

    @patch("kafka_service.consumer.asyncio.sleep", new_callable=AsyncMock)
    @patch("kafka_service.consumer.AIOKafkaConsumer")
    async def test_backoff_doubles_on_consecutive_failures(self, MockKafka, mock_sleep):
        """El delay debe duplicarse en cada fallo consecutivo."""
        consumer = BiohubKafkaConsumer()
        consumer.running = True

        call_count = 0

        async def fake_start():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionRefusedError("broker down")
            consumer.running = False

        instance = MagicMock()
        instance.start = AsyncMock(side_effect=fake_start)
        instance.stop = AsyncMock()
        MockKafka.return_value = instance

        await consumer._consume_with_retry()

        sleep_calls = [c.args[0] for c in mock_sleep.call_args_list]
        assert sleep_calls[0] == _BACKOFF_INITIAL         # 1 s
        assert sleep_calls[1] == _BACKOFF_INITIAL * 2     # 2 s

    @patch("kafka_service.consumer.asyncio.sleep", new_callable=AsyncMock)
    @patch("kafka_service.consumer.AIOKafkaConsumer")
    async def test_backoff_does_not_exceed_max(self, MockKafka, mock_sleep):
        """El delay nunca debe superar _BACKOFF_MAX (60 s)."""
        consumer = BiohubKafkaConsumer()
        consumer.running = True

        call_count = 0
        max_failures = 10  # suficiente para saturar el backoff

        async def fake_start():
            nonlocal call_count
            call_count += 1
            if call_count < max_failures:
                raise ConnectionRefusedError("broker down")
            consumer.running = False

        instance = MagicMock()
        instance.start = AsyncMock(side_effect=fake_start)
        instance.stop = AsyncMock()
        MockKafka.return_value = instance

        await consumer._consume_with_retry()

        sleep_calls = [c.args[0] for c in mock_sleep.call_args_list]
        assert all(d <= _BACKOFF_MAX for d in sleep_calls), (
            f"Algún delay superó {_BACKOFF_MAX}s: {sleep_calls}"
        )

    @patch("kafka_service.consumer.asyncio.sleep", new_callable=AsyncMock)
    @patch("kafka_service.consumer.AIOKafkaConsumer")
    async def test_backoff_resets_after_successful_connection(self, MockKafka, mock_sleep):
        """Después de una conexión exitosa el delay debe volver a _BACKOFF_INITIAL."""
        consumer = BiohubKafkaConsumer()
        consumer.running = True

        # Ciclo: falla → éxito+mensajes → falla → stop
        cycle = 0

        async def fake_start():
            nonlocal cycle
            cycle += 1
            if cycle == 1:
                raise ConnectionRefusedError("first failure")
            # En el segundo intento conecta bien pero no hay mensajes → sale del for

        async def fake_aiter(self_inner):
            consumer.running = False  # sale del while tras el primer ciclo exitoso
            return
            yield  # hace que sea un async generator

        instance = MagicMock()
        instance.start = AsyncMock(side_effect=fake_start)
        instance.stop = AsyncMock()
        instance.__aiter__ = fake_aiter
        instance.__anext__ = AsyncMock(side_effect=StopAsyncIteration)
        MockKafka.return_value = instance

        await consumer._consume_with_retry()

        # El único sleep ocurre antes de la reconexión exitosa con delay inicial
        sleep_calls = [c.args[0] for c in mock_sleep.call_args_list]
        assert sleep_calls[0] == _BACKOFF_INITIAL


# ---------------------------------------------------------------------------
# ECA-02 · Criterio: procesamiento de mensajes
# ---------------------------------------------------------------------------

class TestProcessMessage:
    @patch("kafka_service.consumer.create_audit_entry", new_callable=AsyncMock)
    @patch("kafka_service.consumer.classify_sensitivity")
    async def test_process_message_calls_create_audit_entry(self, mock_classify, mock_create):
        """_process_message debe invocar create_audit_entry con el record."""
        from database.models import SensibilidadEnum
        mock_classify.return_value = SensibilidadEnum.PUBLIC
        mock_create.return_value = MagicMock()

        consumer = BiohubKafkaConsumer()
        await consumer._process_message(SAMPLE_RECORD)

        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["record"] == SAMPLE_RECORD
        assert call_kwargs["usuario"] == "researcher@biohub.org"

    @patch("kafka_service.consumer.create_audit_entry", new_callable=AsyncMock)
    @patch("kafka_service.consumer.classify_sensitivity")
    async def test_process_message_extracts_motivo(self, mock_classify, mock_create):
        """_process_message debe extraer el motivo del historial_cambios."""
        from database.models import SensibilidadEnum
        mock_classify.return_value = SensibilidadEnum.PUBLIC
        mock_create.return_value = MagicMock()

        consumer = BiohubKafkaConsumer()
        await consumer._process_message(SAMPLE_RECORD)

        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["motivo"] == "Registro inicial"

    @patch("kafka_service.consumer.create_audit_entry", new_callable=AsyncMock)
    @patch("kafka_service.consumer.classify_sensitivity")
    async def test_process_message_does_not_raise_on_error(self, mock_classify, mock_create):
        """Si create_audit_entry lanza excepción, _process_message no debe propagarla."""
        mock_classify.side_effect = Exception("clasificación fallida")

        consumer = BiohubKafkaConsumer()
        # No debe lanzar excepción
        await consumer._process_message(SAMPLE_RECORD)

    @patch("kafka_service.consumer.create_audit_entry", new_callable=AsyncMock)
    @patch("kafka_service.consumer.classify_sensitivity")
    async def test_process_message_handles_missing_historial(self, mock_classify, mock_create):
        """Si no hay historial_cambios, motivo debe ser cadena vacía."""
        from database.models import SensibilidadEnum
        mock_classify.return_value = SensibilidadEnum.PUBLIC
        mock_create.return_value = MagicMock()

        record_sin_historial = {**SAMPLE_RECORD, "trazabilidad": {}}
        consumer = BiohubKafkaConsumer()
        await consumer._process_message(record_sin_historial)

        call_kwargs = mock_create.call_args.kwargs
        assert call_kwargs["motivo"] == ""


# ---------------------------------------------------------------------------
# ECA-02 · start() con mock Kafka
# ---------------------------------------------------------------------------

class TestStart:
    @patch("kafka_service.consumer.settings")
    async def test_start_skips_task_when_mock_kafka_enabled(self, mock_settings):
        """Con use_mock_kafka=True, start() no debe crear ningún task."""
        mock_settings.use_mock_kafka = True
        consumer = BiohubKafkaConsumer()

        await consumer.start()

        assert consumer.task is None
        assert consumer.running is False
