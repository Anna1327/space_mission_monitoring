from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import redis.asyncio as aioredis
from redis.exceptions import ConnectionError as RedisConnectionError
from app.core.database import get_db
from app.core.config import settings
from app.utils.websocket_manager import ws_manager
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


async def get_redis():
    client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.close()


@router.get(
    "/health/detailed",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        503: {"description": "Service unhealthy (database or redis down)"}
    },
    summary="Детальная проверка здоровья",
    description="Проверяет асинхронное состояние всех компонентов системы."
)
async def health_detailed(
        db: AsyncSession = Depends(get_db),
        redis: aioredis.Redis = Depends(get_redis)
):
    result = {"status": "healthy", "checks": {}}

    try:
        await db.execute(text("SELECT 1"))
        result["checks"]["database"] = "connected"
    except SQLAlchemyError as e:
        result["checks"]["database"] = f"failed: {str(e)}"
        result["status"] = "unhealthy"

    try:
        await redis.ping()
        result["checks"]["redis"] = "connected"
    except RedisConnectionError as e:
        result["checks"]["redis"] = f"failed: {str(e)}"
        result["status"] = "unhealthy"

    total_connections = sum(len(conns) for conns in ws_manager.subscriptions.values())
    result["checks"]["websocket"] = f"active_connections: {total_connections}"

    if result["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=result
        )

    return result
