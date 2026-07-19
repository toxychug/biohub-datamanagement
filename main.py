from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from database.connection import connect_to_mongo, close_mongo, is_using_in_memory
from database.db_seed import seed_sample_data
from cache.cache import init_cache, close_cache
from kafka_service.consumer import get_kafka_consumer
from kafka_service.mock_producer import router as mock_producer_router
from routers.auditoria import router as auditoria_router
from routers.aprobacion import router as aprobacion_router
from config import settings
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[*] Starting BioHub Change Management & Audit Service...")

    await connect_to_mongo()
    await init_cache()

    # Seed sample data if using in-memory database
    if is_using_in_memory():
        await seed_sample_data()

    # Start Kafka consumer
    kafka_consumer = await get_kafka_consumer()
    await kafka_consumer.start()

    print("[✓] Service started successfully")

    yield

    # Shutdown
    print("[*] Shutting down service...")
    await kafka_consumer.stop()
    await close_cache()
    await close_mongo()
    print("[✓] Service shutdown complete")


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

app.mount("/ui", StaticFiles(directory="static", html=True), name="ui")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from database.connection import is_mongodb_available, is_using_in_memory
    
    if is_using_in_memory():
        db_status = "in-memory (MongoDB unavailable)"
    elif is_mongodb_available():
        db_status = "connected"
    else:
        db_status = "disconnected"

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


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "BioHub Change Management & Audit",
        "version": "0.1.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
