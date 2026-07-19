import asyncio
import json
from aiokafka import AIOKafkaConsumer
from config import settings
from services.audit_service import create_audit_entry
from services.sensitivity_service import classify_sensitivity
from database.models import AprobacionEnum

_BACKOFF_INITIAL = 1
_BACKOFF_MAX = 60


class BiohubKafkaConsumer:
    def __init__(self):
        self.consumer = None
        self.running = False
        self.task = None

    async def start(self):
        """Launch the background consume-with-retry task (ECA-02)."""
        if settings.use_mock_kafka:
            print("[!] Mock Kafka enabled — skipping real consumer")
            return

        self.running = True
        self.task = asyncio.create_task(self._consume_with_retry())
        print(f"[OK] Kafka consumer task started for topic: {settings.kafka_topic}")

    async def _consume_with_retry(self):
        """Reconnect with exponential backoff whenever the broker is unreachable (ECA-02)."""
        delay = _BACKOFF_INITIAL

        while self.running:
            try:
                self.consumer = AIOKafkaConsumer(
                    settings.kafka_topic,
                    bootstrap_servers=settings.kafka_bootstrap_servers,
                    group_id="biohub-change-management",
                    auto_offset_reset="earliest",
                    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
                )
                await self.consumer.start()
                print(f"[OK] Kafka consumer connected to {settings.kafka_bootstrap_servers}")
                delay = _BACKOFF_INITIAL  # reset backoff on successful connection

                async for message in self.consumer:
                    await self._process_message(message.value)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[!] Kafka error: {e}. Reconnecting in {delay}s...")
                try:
                    if self.consumer:
                        await self.consumer.stop()
                except Exception:
                    pass
                finally:
                    self.consumer = None

                if self.running:
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, _BACKOFF_MAX)

    async def _process_message(self, record: dict):
        """Process a single Kafka message (biological record event)."""
        id_registro = record.get("identificacion_basica", {}).get("id_registro", "unknown")
        try:
            sensibilidad = classify_sensitivity(record)

            historial = record.get("trazabilidad", {}).get("historial_cambios", [])
            motivo = historial[0].get("motivo", "") if historial else ""

            await create_audit_entry(
                record=record,
                usuario=record.get("informacion_registro", {}).get("investigador", "unknown"),
                motivo=motivo,
                sensibilidad=sensibilidad,
                estado_aprobacion=AprobacionEnum.PENDIENTE
            )
            print(f"[OK] Processed record: {id_registro}")
        except Exception as e:
            print(f"[!] Error processing message {id_registro}: {e}")

    async def stop(self):
        """Stop consuming from Kafka."""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        if self.consumer:
            await self.consumer.stop()
        print("[OK] Kafka consumer stopped")


_kafka_consumer: BiohubKafkaConsumer = None


async def get_kafka_consumer() -> BiohubKafkaConsumer:
    global _kafka_consumer
    if not _kafka_consumer:
        _kafka_consumer = BiohubKafkaConsumer()
    return _kafka_consumer
