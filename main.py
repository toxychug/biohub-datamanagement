from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.connection import connect_to_mongo, close_mongo
from cache.cache import init_cache, close_cache
from kafka_service.consumer import get_kafka_consumer
from kafka_service.mock_producer import router as mock_producer_router
from routers.auditoria import router as auditoria_router
from routers.aprobacion import router as aprobacion_router
from database.models import HealthResponse, RootResponse
from config import settings
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[*] Starting BioHub Change Management & Audit Service...")

    await connect_to_mongo()
    await init_cache()

    kafka_consumer = None
    if not settings.use_mock_kafka:
        kafka_consumer = await get_kafka_consumer()
        await kafka_consumer.start()

    print("[OK] Service started successfully")

    yield

    print("[*] Shutting down service...")
    if kafka_consumer:
        await kafka_consumer.stop()
    await close_cache()
    await close_mongo()
    print("[OK] Service shutdown complete")


app = FastAPI(
    title="BioHub Change Management & Audit",
    description="Change Management & Audit microservice for BioHub (Group 2)",
    version="0.1.0",
    lifespan=lifespan
)

# Mount routers
app.include_router(auditoria_router)
app.include_router(aprobacion_router)

if settings.env == "development":
    app.include_router(mock_producer_router)


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Estado del servicio",
    tags=["monitoring"],
)
async def health_check() -> HealthResponse:
    """Retorna el estado de conexión de MongoDB, caché (Redis/memoria), Kafka y el entorno actual."""
    try:
        from database.connection import get_database
        db = get_database()
        await db.command("ping")
        db_status = "connected"
    except Exception as e:
        db_status = f"error"

    try:
        from cache.cache import _cache_client, _use_redis
        if _use_redis is True:
            cache_type = "redis"
        else:
            cache_type = "memory"
    except Exception:
        cache_type = "unknown"

    return {
        "status": "ok",
        "service": "biohub-change-management",
        "db": db_status,
        "cache": cache_type,
        "kafka": "mock" if settings.use_mock_kafka else "real",
        "environment": settings.env
    }


@app.get(
    "/",
    response_model=RootResponse,
    summary="Raíz del servicio",
    tags=["monitoring"],
)
async def root() -> RootResponse:
    """Retorna el nombre del servicio, versión y enlace a la documentación interactiva."""
    return {
        "service": "BioHub Change Management & Audit",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
