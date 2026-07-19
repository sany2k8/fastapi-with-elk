from asgi_correlation_id import CorrelationIdMiddleware

from app.core.config import get_settings


def setup_correlation_id(app) -> None:
    settings = get_settings()
    app.add_middleware(CorrelationIdMiddleware, header_name=settings.correlation_id_header)