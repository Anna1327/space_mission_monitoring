from fastapi import status, APIRouter, Depends, HTTPException, Query, Request
from app.core.limiter import limiter
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from ...core.database import get_db
from ...services.system_service import SystemService
from ...schemas.system import SystemCreate, SystemResponse, EventTriggerResponse
from ...api.deps import get_current_client

router = APIRouter(prefix="/systems", tags=["systems"])


@router.get(
    "/",
    response_model=List[SystemResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Missing or invalid token"},
    },
    summary="Получить список систем",
    description="""
    Возвращает список всех систем с поддержкой пагинации, сортировки и фильтрации (асинхронно).
    """,
    openapi_extra={
        "x-code-samples": [
            {
                "lang": "curl",
                "source": "curl -X GET 'http://localhost:8000/api/v1/systems?skip=10&limit=5' -H 'Authorization: Bearer <token>'"
            }
        ]
    }
)
async def get_systems(
    skip: int = Query(0, ge=0, description="Сколько пропустить", examples=[10]),
    limit: int = Query(100, ge=1, le=1000, description="Сколько взять (max 1000)", examples=[50]),
    sort_by: str = Query("id", description="Поле для сортировки (id, name, status, created_at)", examples=["created_at"]),
    order: str = Query("asc", description="Порядок сортировки (asc, desc)", examples=["desc"]),
    status_filter: str = Query(None, description="Фильтр по статусу (active, warning, failed)", examples=["active"]),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_client)
):
    """Получить список всех систем (с пагинацией, сортировкой и фильтрацией)"""
    service = SystemService(db)
    return await service.get_all(
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order,
        status_filter=status_filter
    )


@router.get(
    "/{system_id}",
    response_model=SystemResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Missing or invalid token"},
        404: {"description": "System not found"},
    },
    summary="Получить систему по ID",
    description="Возвращает полную информацию о системе по её идентификатору."
)
async def get_system(
        system_id: int,
        db: AsyncSession = Depends(get_db),
        _=Depends(get_current_client)
):
    """Получить систему по ID"""
    service = SystemService(db)
    system = await service.get_by_id(system_id)
    if not system:
        raise HTTPException(
            status_code=404,
            detail=f"System with id {system_id} not found"
        )
    return system


@router.post(
    "/",
    response_model=SystemResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Bad request: name and system_type are required"},
        401: {"description": "Missing or invalid token"},
    },
    summary="Создать новую систему",
    description="Создаёт новую систему (двигатель, жизнеобеспечение, связь).",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "name": "Starship Enterprise",
                        "system_type": "engine"
                    }
                }
            }
        }
    }
)
@limiter.limit("100/minute")
async def create_system(
        request: Request,
        data: SystemCreate,
        db: AsyncSession = Depends(get_db),
        _=Depends(get_current_client)
):
    """Создать новую систему (двигатель, жизнеобеспечение, связь)"""
    if not data.name or not data.system_type:
        raise HTTPException(
            status_code=400,
            detail="name and system_type are required"
        )
    service = SystemService(db)
    return await service.create(data)


@router.delete(
    "/{system_id}",
    response_model=SystemResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Missing or invalid token"},
        404: {"description": "System not found"},
    },
    summary="Удалить систему по ID",
    description="Удаляет систему по её идентификатору."
)
async def delete_system(
        system_id: int,
        db: AsyncSession = Depends(get_db),
        _=Depends(get_current_client)
):
    """Удалить систему по ID"""
    service = SystemService(db)
    deleted_system = await service.delete(system_id)
    if not deleted_system:
        raise HTTPException(
            status_code=404,
            detail=f"System with id {system_id} not found"
        )
    return deleted_system


@router.post(
    "/{system_id}/trigger/{event_type}",
    response_model=EventTriggerResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid event type or missing data"},
        401: {"description": "Missing or invalid token"},
        404: {"description": "System not found"},
    },
    summary="Симулировать событие системы",
    description="""
    Симулирует событие на системе асинхронно.
    """
)
async def trigger_event(
        system_id: int,
        event_type: str,
        db: AsyncSession = Depends(get_db),
        _=Depends(get_current_client)
):
    """
    Симулировать событие системы
    """
    valid_events = ["failure", "warning", "recover"]
    if event_type not in valid_events:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event_type. Must be one of: {', '.join(valid_events)}"
        )

    service = SystemService(db)
    system = await service.get_by_id(system_id)
    if not system:
        raise HTTPException(
            status_code=404,
            detail=f"System with id {system_id} not found"
        )

    if event_type == "failure":
        system = await service.update_status(system_id, "failed")
    elif event_type == "warning":
        system = await service.update_status(system_id, "warning")
    elif event_type == "recover":
        system = await service.update_status(system_id, "active")

    event_data = {
        "system_id": system_id,
        "event": f"system_{event_type}",
        "system_name": system.name,
        "system_type": system.system_type,
        "old_status": system.status,
        "new_status": system.status if event_type == "recover" else event_type
    }

    await service.add_event(system_id, event_data)

    from ...utils.websocket_manager import ws_manager
    await ws_manager.broadcast_to_system(system_id, event_data)
    return {"status": "triggered", "event": event_data}
