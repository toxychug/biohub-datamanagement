import asyncio
import json
from aiokafka import AIOKafkaConsumer
from config import settings
from services.audit_service import create_audit_entry
from services.sensitivity_service import classify_sensitivity
from database.models import AprobacionEnum


class BiohubKafkaConsumer:
    def __init__(self):
        self.consumer = None
        self.running = False
        self.task = None

    async def start(self):
        """Start consuming from Kafka broker."""
        if settings.use_mock_kafka:
            print("[!] Mock Kafka enabled — skipping real consumer")
            return

        try:
            self.consumer = AIOKafkaConsumer(
                settings.kafka_topic,
                bootstrap_servers=settings.kafka_bootstrap_servers,
                group_id="biohub-change-management",
                auto_offset_reset="earliest",
                value_deserializer=lambda m: json.loads(m.decode("utf-8"))
            )
            await self.consumer.start()
            self.running = True
            print(f"[✓] Kafka consumer started on topic: {settings.kafka_topic}")

            # Start consuming in background
            self.task = asyncio.create_task(self._consume_messages())
        except Exception as e:
            print(f"[!] Kafka connection failed: {e}")

    async def _consume_messages(self):
        """Consume messages from Kafka topic."""
        try:
            async for message in self.consumer:
                await self._process_message(message.value)
        except Exception as e:
            print(f"[!] Kafka consumer error: {e}")
            self.running = False

    async def _process_message(self, record: dict):
        """Process a single Kafka message (biological record event)."""
        try:
            sensibilidad = classify_sensitivity(record)

            await create_audit_entry(
                record=record,
                usuario=record.get("informacion_registro", {}).get("investigador", "unknown"),
                motivo=record.get("trazabilidad", {}).get("historial_cambios", [{}])[0].get("motivo", ""),
                sensibilidad=sensibilidad,
                estado_aprobacion=AprobacionEnum.PENDIENTE
            )
            print(f"[✓] Processed record: {record.get('identificacion_basica', {}).get('id_registro', 'unknown')}")
        except Exception as e:
            print(f"[!] Error processing message: {e}")

    async def stop(self):
        """Stop consuming from Kafka."""
        if self.consumer:
            self.running = False
            if self.task:
                self.task.cancel()
            await self.consumer.stop()
            print("[✓] Kafka consumer stopped")


_kafka_consumer: BiohubKafkaConsumer = None


async def get_kafka_consumer() -> BiohubKafkaConsumer:
    global _kafka_consumer
    if not _kafka_consumer:
        _kafka_consumer = BiohubKafkaConsumer()
    return _kafka_consumer
