from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator, metrics

from app.core.config import get_settings

# --- Custom business metrics (use anywhere in service code) ---------------

ITEMS_CREATED = Counter(
    "items_created_total",
    "Number of items created via the API",
)

EXTERNAL_CALL_DURATION = Histogram(
    "external_service_call_duration_seconds",
    "Duration of calls to the (simulated) external service",
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)


# --- Standard HTTP metrics via prometheus-fastapi-instrumentator ----------


def setup_metrics(app) -> None:
    """Attach standard HTTP metrics and expose /metrics.

    metrics.default() already registers http_requests_total AND
    http_request_duration_seconds — do NOT also add metrics.requests() or
    metrics.latency(), that raises "Duplicated timeseries" at startup.
    """
    settings = get_settings()

    instrumentator = Instrumentator(
        should_group_status_codes=True,
        should_ignore_untemplated=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=[settings.metrics_path, "/health", "/health/ready"],
        inprogress_name="fastapi_inprogress",
        inprogress_labels=True,
    )

    instrumentator.add(
        metrics.default(
            latency_lowr_buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
        )
    )

    instrumentator.instrument(app).expose(
        app, endpoint=settings.metrics_path, include_in_schema=False
    )