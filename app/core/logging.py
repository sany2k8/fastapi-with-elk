import logging
import sys

import structlog
from asgi_correlation_id.context import correlation_id

from app.core.config import get_settings


def add_correlation_id(logger, method_name, event_dict):
    """structlog processor: inject the current request's correlation ID, if any."""
    request_id = correlation_id.get()
    if request_id:
        event_dict["request_id"] = request_id
    return event_dict


def add_service_context(logger, method_name, event_dict):
    """Stamp every log line with service/env metadata — useful once more than
    one service's logs live in the same Elasticsearch cluster."""
    settings = get_settings()
    event_dict["service"] = settings.app_name
    event_dict["environment"] = settings.environment
    return event_dict


def configure_logging() -> None:
    settings = get_settings()

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        add_correlation_id,
        add_service_context,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.log_json:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=shared_processors + [structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(settings.log_level)

    # Route uvicorn's own logs through the same JSON pipeline
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers = [handler]
        uv_logger.propagate = False


def get_logger(name: str = __name__):
    return structlog.get_logger(name)
