from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import health_router, router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.core.metrics import setup_metrics
from app.middleware.correlation import setup_correlation_id
from app.middleware.logging import RequestLoggingMiddleware

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_starting", environment=get_settings().environment)
    yield
    logger.info("app_shutting_down")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    # add_middleware is applied in reverse (last added = outermost), so the
    # correlation-ID middleware must be added AFTER the logging middleware to
    # wrap it — that way request_id is already set when access logs are written.
    app.add_middleware(RequestLoggingMiddleware)
    setup_correlation_id(app)

    setup_metrics(app)

    app.include_router(health_router)
    app.include_router(router, prefix="/api/v1")

    return app


app = create_app()