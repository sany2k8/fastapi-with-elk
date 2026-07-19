from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "fastapi-observability-elk"
    environment: str = "local"  # local | staging | production
    log_level: str = "INFO"
    log_json: bool = True  # JSON logs for Filebeat/ELK; set false for pretty console logs

    # Prometheus / metrics
    metrics_path: str = "/metrics"

    # Correlation ID
    correlation_id_header: str = "X-Request-ID"


@lru_cache
def get_settings() -> Settings:
    """Cached so Settings() is only parsed once per process."""
    return Settings()