import asyncio
import random
import time

from app.core.logging import get_logger
from app.core.metrics import EXTERNAL_CALL_DURATION, ITEMS_CREATED

logger = get_logger(__name__)


async def create_item(name: str) -> dict:
    logger.info("creating_item", item_name=name)
    ITEMS_CREATED.inc()
    return {"id": random.randint(1000, 9999), "name": name}


async def call_external_service() -> dict:
    """Simulates a flaky downstream call, timed as a business metric."""
    start = time.perf_counter()
    await asyncio.sleep(random.uniform(0.05, 0.4))
    duration = time.perf_counter() - start
    EXTERNAL_CALL_DURATION.observe(duration)

    if random.random() < 0.1:
        logger.error("external_service_failed", duration_ms=round(duration * 1000, 2))
        raise RuntimeError("external service timed out")

    logger.info("external_service_ok", duration_ms=round(duration * 1000, 2))
    return {"latency_ms": round(duration * 1000, 2)}