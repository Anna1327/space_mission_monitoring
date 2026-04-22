from fastapi import status, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
    }
)
def get_systems(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        _=Depends(get_current_client)
):
    """Получить список всех систем (с пагинацией)"""
    service = SystemService(db)
    return service.get_all(skip=skip, limit=limit)


@router.get(
    "/{system_id}",
    response_model=SystemResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Missing or invalid token"},
        404: {"description": "System not found"},
    }
)
def get_system(
        system_id: int,
        db: Session = Depends(get_db),
        _=Depends(get_current_client)
):
    """Получить систему по ID"""
    service = SystemService(db)
    system = service.get_by_id(system_id)
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
    }
)
def create_system(
        data: SystemCreate,
        db: Session = Depends(get_db),
        _=Depends(get_current_client)
):
    """Создать новую систему (двигатель, жизнеобеспечение, связь)"""
    if not data.name or not data.system_type:
        raise HTTPException(
            status_code=400,
            detail="name and system_type are required"
        )
    service = SystemService(db)
    return service.create(data)


@router.post(
    "/{system_id}/trigger/{event_type}",
    response_model=EventTriggerResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid event type or missing data"},
        401: {"description": "Missing or invalid token"},
        404: {"description": "System not found"},
    }
)
def trigger_event(
        system_id: int,
        event_type: str,
        db: Session = Depends(get_db),
        _=Depends(get_current_client)
):
    """
    Симулировать событие системы

    Поддерживаемые event_type:
    - failure (отказ)
    - warning (предупреждение)
    - recover (восстановление)
    """
    valid_events = ["failure", "warning", "recover"]
    if event_type not in valid_events:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid event_type. Must be one of: {', '.join(valid_events)}"
        )

    service = SystemService(db)
    system = service.get_by_id(system_id)
    if not system:
        raise HTTPException(
            status_code=404,
            detail=f"System with id {system_id} not found"
        )

    if event_type == "failure":
        system = service.update_status(system_id, "failed")
    elif event_type == "warning":
        system = service.update_status(system_id, "warning")
    elif event_type == "recover":
        system = service.update_status(system_id, "active")

    event_data = {
        "system_id": system_id,
        "event": f"system_{event_type}",
        "system_name": system.name,
        "system_type": system.system_type,
        "old_status": system.status,
        "new_status": system.status if event_type == "recover" else event_type
    }
    service.add_event(system_id, event_data)

    # TODO: broadcast via WebSocket
    return {"status": "triggered", "event": event_data}
