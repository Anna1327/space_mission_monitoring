from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from app.core.database import get_db
from app.core.config import settings
from app.utils.websocket_manager import ws_manager
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


def get_redis():
    return Redis.from_url(settings.REDIS_URL)


@router.get(
    "/health/detailed",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        503: {"description": "Service unhealthy (database or redis down)"}
    }
)
def health_detailed(
        db: Session = Depends(get_db),
        redis: Redis = Depends(get_redis)
):
    """
        Детальная проверка состояния сервиса
        Возвращает статус каждого компонента (database, redis, websocket)
    """
    result = {"status": "healthy", "checks": {}}

    # Проверка БД
    try:
        db.execute(text("SELECT 1"))
        result["checks"]["database"] = "connected"
    except SQLAlchemyError as e:
        result["checks"]["database"] = f"failed: {str(e)}"
        result["status"] = "unhealthy"

    # Проверка Redis
    try:
        redis.ping()
        result["checks"]["redis"] = "connected"
    except RedisConnectionError as e:
        result["checks"]["redis"] = f"failed: {str(e)}"
        result["status"] = "unhealthy"

    # WebSocket
    result["checks"]["websocket"] = f"active_connections: {ws_manager.connection_count}"

    if result["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=result
        )

    return result
