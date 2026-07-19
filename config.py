from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    mongodb_uri: Optional[str] = None  # Optional for serverless/fallback to in-memory
    mongodb_db_name: str = "biohub_db"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "registros-biologicos"
    use_mock_kafka: bool = True

    redis_url: Optional[str] = None

    env: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
