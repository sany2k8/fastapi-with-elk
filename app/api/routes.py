from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import example

router = APIRouter()
health_router = APIRouter()


class ItemIn(BaseModel):
    name: str


@router.post("/items", tags=["items"])
async def create_item(payload: ItemIn):
    return await example.create_item(payload.name)


@router.get("/external", tags=["demo"])
async def hit_external_service():
    try:
        return await example.call_external_service()
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@health_router.get("/health", tags=["health"])
async def liveness():
    """Liveness probe: is the process up at all?"""
    return {"status": "ok"}


@health_router.get("/health/ready", tags=["health"])
async def readiness():
    """Readiness probe: is the app ready to serve traffic?

    Add real dependency checks here (DB ping, cache ping, ...) as your project grows.
    """
    return {"status": "ready"}